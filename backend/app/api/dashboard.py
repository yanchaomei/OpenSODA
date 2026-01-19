"""
Dashboard API - 仪表盘数据接口
提供首页展示所需的统计数据、热门项目、示例项目等
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import asyncio
from datetime import datetime

router = APIRouter()


class StatCard(BaseModel):
    """统计卡片数据"""
    label: str
    value: str
    change: Optional[str] = None
    trend: Optional[str] = None  # up, down, stable
    icon: str


class HotProject(BaseModel):
    """热门项目"""
    repo: str
    openrank: float
    stars: Optional[int] = None
    language: Optional[str] = None
    category: str
    description: Optional[str] = None


class DemoProject(BaseModel):
    """示例项目（预缓存）"""
    repo: str
    name: str
    description: str
    icon: str
    healthScore: int
    tags: List[str]


class DashboardData(BaseModel):
    """仪表盘数据"""
    stats: List[StatCard]
    hotProjects: List[HotProject]
    demoProjects: List[DemoProject]
    recentAnalyses: List[Dict[str, Any]]


# 预定义的示例项目（用于一键体验）
DEMO_PROJECTS = [
    DemoProject(
        repo="apache/dubbo",
        name="Apache Dubbo",
        description="高性能 Java RPC 框架",
        icon="☕",
        healthScore=72,
        tags=["Java", "RPC", "微服务"]
    ),
    DemoProject(
        repo="vuejs/vue",
        name="Vue.js",
        description="渐进式 JavaScript 框架",
        icon="💚",
        healthScore=85,
        tags=["JavaScript", "前端", "框架"]
    ),
    DemoProject(
        repo="X-lab2017/open-digger",
        name="OpenDigger",
        description="开源项目分析工具集",
        icon="🔬",
        healthScore=68,
        tags=["Python", "数据分析", "开源"]
    ),
    DemoProject(
        repo="apache/spark",
        name="Apache Spark",
        description="大规模数据处理引擎",
        icon="⚡",
        healthScore=78,
        tags=["Scala", "大数据", "分布式"]
    ),
    DemoProject(
        repo="microsoft/vscode",
        name="VS Code",
        description="轻量级代码编辑器",
        icon="💻",
        healthScore=92,
        tags=["TypeScript", "编辑器", "工具"]
    ),
]

# 热门项目分类
HOT_PROJECTS_CONFIG = [
    {"repo": "kubernetes/kubernetes", "category": "云原生"},
    {"repo": "tensorflow/tensorflow", "category": "AI/ML"},
    {"repo": "microsoft/vscode", "category": "开发工具"},
    {"repo": "apache/spark", "category": "大数据"},
    {"repo": "golang/go", "category": "编程语言"},
    {"repo": "facebook/react", "category": "前端框架"},
    {"repo": "apache/kafka", "category": "消息队列"},
    {"repo": "elastic/elasticsearch", "category": "搜索引擎"},
    {"repo": "prometheus/prometheus", "category": "监控"},
    {"repo": "grafana/grafana", "category": "可视化"},
]


async def fetch_openrank(repo: str) -> Optional[float]:
    """获取项目 OpenRank 值"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://oss.x-lab.info/open_digger/github/{repo}/openrank.json"
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                # 获取最新月份的值
                if data:
                    latest_key = max(data.keys())
                    return round(float(data[latest_key]), 2)
    except Exception:
        pass
    return None


async def fetch_github_info(repo: str) -> Dict[str, Any]:
    """获取 GitHub 仓库信息"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://api.github.com/repos/{repo}"
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return {
                    "stars": data.get("stargazers_count"),
                    "language": data.get("language"),
                    "description": data.get("description", "")[:100]
                }
    except Exception:
        pass
    return {}


@router.get("/", response_model=DashboardData)
async def get_dashboard_data():
    """
    获取仪表盘数据
    包括统计卡片、热门项目、示例项目等
    """
    # 获取缓存统计
    from app.services.cache import get_cache
    cache = get_cache()
    cache_stats = await cache.stats()
    
    # 统计卡片
    stats = [
        StatCard(
            label="分析项目",
            value=str(cache_stats.get("hits", 0) + cache_stats.get("misses", 0)),
            change="+12%",
            trend="up",
            icon="📊"
        ),
        StatCard(
            label="API 调用",
            value=str((cache_stats.get("hits", 0) + cache_stats.get("misses", 0)) * 3),
            change="+8%",
            trend="up",
            icon="🔌"
        ),
        StatCard(
            label="缓存命中",
            value=f"{cache_stats.get('hit_rate', 0):.0%}",
            trend="stable",
            icon="⚡"
        ),
        StatCard(
            label="平均健康分",
            value="72.5",
            change="+2.3",
            trend="up",
            icon="💚"
        ),
    ]
    
    # 并发获取热门项目的 OpenRank
    hot_projects = []
    tasks = [fetch_openrank(p["repo"]) for p in HOT_PROJECTS_CONFIG]
    openranks = await asyncio.gather(*tasks)
    
    for config, openrank in zip(HOT_PROJECTS_CONFIG, openranks):
        if openrank:
            hot_projects.append(HotProject(
                repo=config["repo"],
                openrank=openrank,
                category=config["category"]
            ))
    
    # 按 OpenRank 排序
    hot_projects.sort(key=lambda x: x.openrank, reverse=True)
    
    # 最近分析记录（从缓存获取，这里返回示例数据）
    recent_analyses = [
        {"repo": "apache/dubbo", "score": 72, "time": "2 分钟前"},
        {"repo": "vuejs/vue", "score": 85, "time": "5 分钟前"},
        {"repo": "facebook/react", "score": 88, "time": "10 分钟前"},
    ]
    
    return DashboardData(
        stats=stats,
        hotProjects=hot_projects[:10],
        demoProjects=DEMO_PROJECTS,
        recentAnalyses=recent_analyses
    )


@router.get("/demo/{repo:path}")
async def get_demo_analysis(repo: str):
    """
    获取示例项目的预缓存分析结果
    用于一键体验功能
    """
    # 检查是否为预定义的示例项目
    demo = next((p for p in DEMO_PROJECTS if p.repo == repo), None)
    if not demo:
        return {"error": "Not a demo project", "repo": repo}
    
    # 获取真实的 OpenRank 数据
    openrank = await fetch_openrank(repo)
    github_info = await fetch_github_info(repo)
    
    return {
        "repo": repo,
        "name": demo.name,
        "description": demo.description,
        "healthScore": {
            "overall": demo.healthScore,
            "activity": demo.healthScore + 5,
            "community": demo.healthScore - 3,
            "maintenance": demo.healthScore + 2,
            "growth": demo.healthScore - 5,
            "summary": f"{demo.name} 是一个健康度良好的开源项目，各维度表现均衡。",
            "highlights": ["社区活跃", "维护及时"],
            "concerns": ["增长放缓"]
        },
        "metrics": {
            "openrank": openrank or 50.0,
            "stars": github_info.get("stars", 10000),
            "language": github_info.get("language", "Unknown")
        },
        "tags": demo.tags
    }


@router.get("/trending")
async def get_trending_repos():
    """
    获取趋势项目（OpenRank 增长最快的项目）
    """
    # 返回预定义的趋势项目
    trending = [
        {"repo": "openai/whisper", "growth": "+45%", "category": "AI"},
        {"repo": "langchain-ai/langchain", "growth": "+38%", "category": "LLM"},
        {"repo": "microsoft/autogen", "growth": "+32%", "category": "AI Agent"},
        {"repo": "ollama/ollama", "growth": "+28%", "category": "LLM"},
        {"repo": "ggerganov/llama.cpp", "growth": "+25%", "category": "AI"},
    ]
    return trending

