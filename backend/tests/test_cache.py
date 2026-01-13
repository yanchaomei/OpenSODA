"""
缓存服务测试用例

测试 LRU 内存缓存和缓存装饰器
"""
import pytest
import asyncio
from app.services.cache import LRUCache, CacheService, get_cache, cached


class TestLRUCache:
    """LRU 缓存测试"""
    
    @pytest.fixture
    def cache(self):
        """创建测试用缓存实例"""
        return LRUCache(max_size=5, default_ttl=60)
    
    @pytest.mark.asyncio
    async def test_basic_set_and_get(self, cache):
        """测试基本的设置和获取"""
        await cache.set("key1", "value1")
        
        result = await cache.get("key1")
        
        assert result == "value1"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache):
        """测试获取不存在的键"""
        result = await cache.get("nonexistent")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache):
        """测试 LRU 淘汰策略"""
        # 填满缓存
        for i in range(5):
            await cache.set(f"key{i}", f"value{i}")
        
        # 添加第6个元素，应该淘汰最早的
        await cache.set("key5", "value5")
        
        # key0 应该被淘汰
        assert await cache.get("key0") is None
        # key1-key5 应该存在
        assert await cache.get("key1") == "value1"
        assert await cache.get("key5") == "value5"
    
    @pytest.mark.asyncio
    async def test_access_updates_lru_order(self, cache):
        """测试访问更新 LRU 顺序"""
        # 填满缓存
        for i in range(5):
            await cache.set(f"key{i}", f"value{i}")
        
        # 访问 key0，使其变成最近使用
        await cache.get("key0")
        
        # 添加新元素，应该淘汰 key1（现在是最旧的）
        await cache.set("key5", "value5")
        
        # key0 应该还在（因为刚被访问）
        assert await cache.get("key0") == "value0"
        # key1 应该被淘汰
        assert await cache.get("key1") is None
    
    @pytest.mark.asyncio
    async def test_delete(self, cache):
        """测试删除"""
        await cache.set("key1", "value1")
        
        result = await cache.delete("key1")
        
        assert result is True
        assert await cache.get("key1") is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, cache):
        """测试删除不存在的键"""
        result = await cache.delete("nonexistent")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_clear(self, cache):
        """测试清空缓存"""
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        
        await cache.clear()
        
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
    
    @pytest.mark.asyncio
    async def test_ttl_expiration(self):
        """测试 TTL 过期"""
        cache = LRUCache(max_size=5, default_ttl=1)  # 1秒过期
        
        await cache.set("key1", "value1")
        
        # 立即获取应该成功
        assert await cache.get("key1") == "value1"
        
        # 等待过期
        await asyncio.sleep(1.1)
        
        # 过期后应该返回 None
        assert await cache.get("key1") is None
    
    @pytest.mark.asyncio
    async def test_custom_ttl(self, cache):
        """测试自定义 TTL"""
        await cache.set("short", "value", ttl=1)
        await cache.set("long", "value", ttl=100)
        
        await asyncio.sleep(1.1)
        
        # 短 TTL 应该过期
        assert await cache.get("short") is None
        # 长 TTL 应该还在
        assert await cache.get("long") == "value"
    
    @pytest.mark.asyncio
    async def test_stats(self, cache):
        """测试缓存统计"""
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        
        stats = await cache.stats()
        
        assert stats["type"] == "memory"
        assert stats["size"] == 2
        assert stats["max_size"] == 5
    
    @pytest.mark.asyncio
    async def test_complex_values(self, cache):
        """测试复杂值类型"""
        complex_value = {
            "list": [1, 2, 3],
            "nested": {"a": "b"},
            "number": 42
        }
        
        await cache.set("complex", complex_value)
        
        result = await cache.get("complex")
        
        assert result == complex_value


class TestCachedDecorator:
    """缓存装饰器测试"""
    
    @pytest.mark.asyncio
    async def test_cached_function(self):
        """测试缓存装饰器"""
        call_count = 0
        
        @cached(ttl=60, key_prefix="test")
        async def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # 第一次调用
        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # 第二次调用（相同参数）应该使用缓存
        result2 = await expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # 没有增加
        
        # 不同参数应该重新计算
        result3 = await expensive_function(10)
        assert result3 == 20
        assert call_count == 2


class TestCacheService:
    """缓存服务测试"""
    
    @pytest.mark.asyncio
    async def test_get_cache_singleton(self):
        """测试缓存服务单例"""
        cache1 = get_cache()
        cache2 = get_cache()
        
        assert cache1 is cache2
    
    @pytest.mark.asyncio
    async def test_cache_service_basic_operations(self):
        """测试缓存服务基本操作"""
        cache = get_cache()
        
        await cache.set("service_test", "value")
        result = await cache.get("service_test")
        
        assert result == "value"
        
        # 清理
        await cache.delete("service_test")
    
    @pytest.mark.asyncio
    async def test_cache_service_stats(self):
        """测试缓存服务统计"""
        cache = get_cache()
        
        # 执行一些操作来产生统计数据
        await cache.set("stats_test", "value")
        await cache.get("stats_test")
        await cache.get("nonexistent")
        
        stats = await cache.stats()
        
        assert "memory" in stats
        assert "performance" in stats
        assert "hits" in stats["performance"]
        assert "misses" in stats["performance"]
        
        # 清理
        await cache.delete("stats_test")


# 如果直接运行测试文件
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

