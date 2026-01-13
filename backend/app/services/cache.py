"""
缓存服务模块
提供内存缓存和可选的 Redis 缓存支持
"""
import json
import hashlib
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import asyncio
from collections import OrderedDict

from app.core.config import settings


class LRUCache:
    """
    LRU (Least Recently Used) 内存缓存实现
    当 Redis 不可用时作为后备缓存
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        初始化 LRU 缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认过期时间（秒）
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict = OrderedDict()
        self._expiry: dict = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        async with self._lock:
            if key not in self._cache:
                return None
            
            # 检查是否过期
            if key in self._expiry and datetime.now() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                return None
            
            # 移动到末尾（最近使用）
            self._cache.move_to_end(key)
            return self._cache[key]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        async with self._lock:
            ttl = ttl or self.default_ttl
            
            # 如果已存在，更新并移动到末尾
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                # 如果达到最大容量，删除最旧的条目
                while len(self._cache) >= self.max_size:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                    if oldest_key in self._expiry:
                        del self._expiry[oldest_key]
            
            self._cache[key] = value
            self._expiry[key] = datetime.now() + timedelta(seconds=ttl)
            return True
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._expiry:
                    del self._expiry[key]
                return True
            return False
    
    async def clear(self) -> None:
        """清空所有缓存"""
        async with self._lock:
            self._cache.clear()
            self._expiry.clear()
    
    async def stats(self) -> dict:
        """获取缓存统计信息"""
        return {
            "type": "memory",
            "size": len(self._cache),
            "max_size": self.max_size,
            "default_ttl": self.default_ttl
        }


class RedisCache:
    """
    Redis 缓存实现
    提供持久化和分布式缓存能力
    """
    
    def __init__(self, redis_url: str, default_ttl: int = 3600, prefix: str = "osc:"):
        """
        初始化 Redis 缓存
        
        Args:
            redis_url: Redis 连接 URL
            default_ttl: 默认过期时间（秒）
            prefix: 键前缀
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.prefix = prefix
        self._redis = None
        self._available = False
    
    async def _get_redis(self):
        """获取 Redis 连接"""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self.redis_url, decode_responses=True)
                await self._redis.ping()
                self._available = True
            except Exception as e:
                print(f"Redis connection failed: {e}")
                self._available = False
                self._redis = None
        return self._redis
    
    def _make_key(self, key: str) -> str:
        """生成带前缀的键"""
        return f"{self.prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        redis = await self._get_redis()
        if not redis:
            return None
        
        try:
            value = await redis.get(self._make_key(key))
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        redis = await self._get_redis()
        if not redis:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            await redis.setex(
                self._make_key(key),
                ttl,
                json.dumps(value, ensure_ascii=False)
            )
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        redis = await self._get_redis()
        if not redis:
            return False
        
        try:
            await redis.delete(self._make_key(key))
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    async def clear(self) -> None:
        """清空所有缓存（仅删除带前缀的键）"""
        redis = await self._get_redis()
        if not redis:
            return
        
        try:
            cursor = 0
            while True:
                cursor, keys = await redis.scan(cursor, match=f"{self.prefix}*", count=100)
                if keys:
                    await redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            print(f"Redis clear error: {e}")
    
    async def stats(self) -> dict:
        """获取缓存统计信息"""
        redis = await self._get_redis()
        if not redis:
            return {"type": "redis", "available": False}
        
        try:
            info = await redis.info("memory")
            dbsize = await redis.dbsize()
            return {
                "type": "redis",
                "available": True,
                "used_memory": info.get("used_memory_human", "unknown"),
                "keys": dbsize,
                "default_ttl": self.default_ttl
            }
        except Exception as e:
            return {"type": "redis", "available": False, "error": str(e)}


class CacheService:
    """
    统一缓存服务
    自动选择可用的缓存后端（Redis 或内存）
    """
    
    def __init__(self):
        """初始化缓存服务"""
        self._memory_cache = LRUCache(max_size=500, default_ttl=1800)  # 30分钟
        self._redis_cache: Optional[RedisCache] = None
        
        # 尝试初始化 Redis 缓存
        redis_url = getattr(settings, 'REDIS_URL', None)
        if redis_url:
            self._redis_cache = RedisCache(redis_url, default_ttl=3600)
        
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0
        }
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        # 优先从 Redis 获取
        if self._redis_cache:
            value = await self._redis_cache.get(key)
            if value is not None:
                self._stats["hits"] += 1
                return value
        
        # 回退到内存缓存
        value = await self._memory_cache.get(key)
        if value is not None:
            self._stats["hits"] += 1
            return value
        
        self._stats["misses"] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        self._stats["sets"] += 1
        
        # 同时写入两个缓存
        results = []
        
        results.append(await self._memory_cache.set(key, value, ttl))
        
        if self._redis_cache:
            results.append(await self._redis_cache.set(key, value, ttl))
        
        return any(results)
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        results = []
        
        results.append(await self._memory_cache.delete(key))
        
        if self._redis_cache:
            results.append(await self._redis_cache.delete(key))
        
        return any(results)
    
    async def clear(self) -> None:
        """清空所有缓存"""
        await self._memory_cache.clear()
        
        if self._redis_cache:
            await self._redis_cache.clear()
    
    async def stats(self) -> dict:
        """获取缓存统计"""
        memory_stats = await self._memory_cache.stats()
        redis_stats = await self._redis_cache.stats() if self._redis_cache else None
        
        return {
            "memory": memory_stats,
            "redis": redis_stats,
            "performance": {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "sets": self._stats["sets"],
                "hit_rate": (
                    self._stats["hits"] / (self._stats["hits"] + self._stats["misses"])
                    if (self._stats["hits"] + self._stats["misses"]) > 0 else 0
                )
            }
        }


# 全局缓存实例
_cache_service: Optional[CacheService] = None


def get_cache() -> CacheService:
    """获取全局缓存服务实例"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def cached(ttl: int = 1800, key_prefix: str = ""):
    """
    缓存装饰器
    
    Args:
        ttl: 缓存过期时间（秒），默认30分钟
        key_prefix: 缓存键前缀
    
    Usage:
        @cached(ttl=3600, key_prefix="opendigger")
        async def get_repo_metrics(repo: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # 生成缓存键
            key_data = json.dumps({
                "func": func.__name__,
                "prefix": key_prefix,
                "args": [str(a) for a in args],
                "kwargs": {k: str(v) for k, v in kwargs.items()}
            }, sort_keys=True)
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            if key_prefix:
                cache_key = f"{key_prefix}:{cache_key}"
            
            # 尝试从缓存获取
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            await cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# 导出
__all__ = [
    "CacheService",
    "get_cache",
    "cached",
    "LRUCache",
    "RedisCache"
]

