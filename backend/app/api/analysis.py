"""
Analysis API - 分析接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

router = APIRouter()


class RepoAnalysisRequest(BaseModel):
    """仓库分析请求"""
    repo: str  # 格式: owner/repo，如 "apache/dubbo"
    metrics: Optional[List[str]] = None  # 可选指定要获取的指标


class HealthScore(BaseModel):
    """健康度评分"""
    overall: float  # 总体评分 0-100
    activity: float  # 活跃度
    community: float  # 社区健康度
    maintenance: float  # 维护响应度
    growth: float  # 增长趋势


class ContributorStats(BaseModel):
    """贡献者统计"""
    total: int
    active: int  # 近30天活跃
    new: int  # 近30天新增
    core: int  # 核心贡献者


class RepoAnalysisResponse(BaseModel):
    """仓库分析响应"""
    repo: str
    health_score: HealthScore
    openrank: Optional[float] = None
    activity: Optional[float] = None
    attention: Optional[float] = None
    contributors: Optional[ContributorStats] = None
    metrics: Optional[Dict[str, Any]] = None
    trends: Optional[Dict[str, List[float]]] = None


@router.get("/repo/{owner}/{repo}", response_model=RepoAnalysisResponse)
async def analyze_repo(owner: str, repo: str):
    """
    分析单个仓库的健康度
    """
    from app.tools.opendigger import OpenDiggerTool
    
    repo_path = f"{owner}/{repo}"
    tool = OpenDiggerTool()
    
    try:
        # 获取各项指标
        metrics = await tool.get_repo_metrics(repo_path)
        
        # 计算健康度评分
        health_score = calculate_health_score(metrics)
        
        return RepoAnalysisResponse(
            repo=repo_path,
            health_score=health_score,
            openrank=metrics.get("openrank"),
            activity=metrics.get("activity"),
            attention=metrics.get("attention"),
            metrics=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_repos(repos: List[str]):
    """
    对比多个仓库的指标
    """
    from app.tools.opendigger import OpenDiggerTool
    
    tool = OpenDiggerTool()
    results = []
    
    for repo in repos:
        try:
            metrics = await tool.get_repo_metrics(repo)
            health_score = calculate_health_score(metrics)
            results.append({
                "repo": repo,
                "health_score": health_score,
                "metrics": metrics
            })
        except Exception as e:
            results.append({
                "repo": repo,
                "error": str(e)
            })
    
    return {"comparisons": results}


@router.get("/trending")
async def get_trending_repos(
    language: Optional[str] = None,
    period: str = "weekly"
):
    """
    获取趋势项目
    """
    # TODO: 实现趋势项目获取
    return {
        "period": period,
        "language": language,
        "repos": []
    }


def calculate_health_score(metrics: Dict[str, Any]) -> HealthScore:
    """
    计算仓库健康度评分
    
    评分维度:
    - activity: 活跃度 (基于 OpenRank, activity 指标)
    - community: 社区健康度 (基于贡献者数量、多样性)
    - maintenance: 维护响应度 (Issue响应时间、PR合并时间)
    - growth: 增长趋势 (Star、Fork增长率)
    """
    # 获取原始指标
    openrank = metrics.get("openrank", 0)
    activity = metrics.get("activity", 0)
    attention = metrics.get("attention", 0)
    
    # 归一化计算各维度分数 (0-100)
    activity_score = min(100, (openrank or 0) * 10 + (activity or 0) * 5)
    community_score = min(100, attention * 2) if attention else 50
    maintenance_score = 70  # 默认值，后续根据响应时间计算
    growth_score = 60  # 默认值，后续根据增长率计算
    
    # 计算总体评分 (加权平均)
    overall = (
        activity_score * 0.3 +
        community_score * 0.25 +
        maintenance_score * 0.25 +
        growth_score * 0.2
    )
    
    return HealthScore(
        overall=round(overall, 1),
        activity=round(activity_score, 1),
        community=round(community_score, 1),
        maintenance=round(maintenance_score, 1),
        growth=round(growth_score, 1)
    )

