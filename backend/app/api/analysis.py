"""
Analysis API - 分析接口
提供项目健康度分析、对比、导出等功能
"""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import io

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
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None
    concerns: Optional[List[str]] = None


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
    trends: Optional[Dict[str, Any]] = None  # 包含 openrank/activity (List[float]) 和 months (List[str])
    analyzed_at: Optional[str] = None


class CompareRequest(BaseModel):
    """对比请求"""
    repos: List[str]


class CompareResult(BaseModel):
    """单个仓库对比结果"""
    repo: str
    health_score: Optional[HealthScore] = None
    metrics: Optional[Dict[str, Any]] = None
    rank: Optional[int] = None
    error: Optional[str] = None


class CompareResponse(BaseModel):
    """对比响应"""
    comparisons: List[CompareResult]
    summary: Dict[str, Any]
    winner: Optional[str] = None
    compared_at: str


@router.get("/repo/{owner}/{repo}", response_model=RepoAnalysisResponse)
async def analyze_repo(owner: str, repo: str):
    """
    分析单个仓库的健康度
    
    Args:
        owner: 仓库所有者
        repo: 仓库名称
    
    Returns:
        RepoAnalysisResponse: 包含健康度评分、各项指标的分析结果
    """
    from app.tools.opendigger import OpenDiggerTool
    from app.tools.github import GitHubTool
    
    repo_path = f"{owner}/{repo}"
    opendigger = OpenDiggerTool()
    github = GitHubTool()
    
    try:
        # 并行获取数据
        metrics = await opendigger.get_repo_metrics(repo_path)
        
        # 尝试获取 GitHub 基本信息
        try:
            github_info = await github.get_repo_info(repo_path)
            metrics['stars'] = github_info.get('stargazers_count', 0)
            metrics['forks'] = github_info.get('forks_count', 0)
            metrics['open_issues'] = github_info.get('open_issues_count', 0)
        except:
            pass
        
        # 获取趋势数据
        trends = {}
        try:
            openrank_trend = await opendigger.get_trend_data(repo_path, "openrank", 12)
            activity_trend = await opendigger.get_trend_data(repo_path, "activity", 12)
            trends['openrank'] = [t['value'] for t in openrank_trend]
            trends['activity'] = [t['value'] for t in activity_trend]
            trends['months'] = [t['month'] for t in openrank_trend]
        except:
            pass
        
        # 计算健康度评分
        health_score = calculate_health_score(metrics, trends)
        
        return RepoAnalysisResponse(
            repo=repo_path,
            health_score=health_score,
            openrank=metrics.get("openrank"),
            activity=metrics.get("activity"),
            attention=metrics.get("attention"),
            metrics=metrics,
            trends=trends,
            analyzed_at=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await opendigger.close()


@router.post("/compare", response_model=CompareResponse)
async def compare_repos(request: CompareRequest):
    """
    对比多个仓库的指标
    
    Args:
        request: 包含仓库列表的请求
    
    Returns:
        CompareResponse: 对比结果，包含排名和汇总
    """
    from app.tools.opendigger import OpenDiggerTool
    
    repos = request.repos
    if len(repos) < 2:
        raise HTTPException(status_code=400, detail="至少需要两个仓库进行对比")
    if len(repos) > 5:
        raise HTTPException(status_code=400, detail="最多支持5个仓库对比")
    
    tool = OpenDiggerTool()
    results: List[CompareResult] = []
    
    try:
        for repo in repos:
            try:
                metrics = await tool.get_repo_metrics(repo)
                
                # 获取趋势数据计算健康度
                trends = {}
                try:
                    openrank_trend = await tool.get_trend_data(repo, "openrank", 6)
                    trends['openrank'] = [t['value'] for t in openrank_trend]
                except:
                    pass
                
                health_score = calculate_health_score(metrics, trends)
                
                results.append(CompareResult(
                    repo=repo,
                    health_score=health_score,
                    metrics=metrics
                ))
            except Exception as e:
                results.append(CompareResult(
                    repo=repo,
                    error=str(e)
                ))
        
        # 排名 (按总体评分)
        valid_results = [r for r in results if r.health_score is not None]
        valid_results.sort(key=lambda x: x.health_score.overall, reverse=True)
        
        for i, result in enumerate(valid_results):
            result.rank = i + 1
        
        # 生成汇总
        summary = generate_comparison_summary(results)
        winner = valid_results[0].repo if valid_results else None
        
        return CompareResponse(
            comparisons=results,
            summary=summary,
            winner=winner,
            compared_at=datetime.now().isoformat()
        )
    finally:
        await tool.close()


@router.post("/export/markdown")
async def export_markdown(request: CompareRequest):
    """
    导出分析结果为 Markdown 格式
    """
    from app.tools.opendigger import OpenDiggerTool
    
    tool = OpenDiggerTool()
    
    try:
        repos = request.repos
        
        # 生成 Markdown 报告
        md_content = f"""# 开源项目健康度分析报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
        
        for repo in repos:
            try:
                metrics = await tool.get_repo_metrics(repo)
                trends = {}
                try:
                    openrank_trend = await tool.get_trend_data(repo, "openrank", 6)
                    trends['openrank'] = [t['value'] for t in openrank_trend]
                except:
                    pass
                    
                health = calculate_health_score(metrics, trends)
                
                md_content += f"""## 📊 {repo}

### 健康度评分

| 维度 | 评分 |
|------|------|
| **总体评分** | {health.overall}/100 |
| 活跃度 | {health.activity} |
| 社区健康 | {health.community} |
| 维护响应 | {health.maintenance} |
| 增长趋势 | {health.growth} |

### 关键指标

- **OpenRank**: {metrics.get('openrank', 'N/A')}
- **活跃度**: {metrics.get('activity', 'N/A')}
- **参与者数**: {metrics.get('participants', 'N/A')}
- **巴士因子**: {metrics.get('bus_factor', 'N/A')}

"""
                if health.highlights:
                    md_content += "### ✅ 亮点\n\n"
                    for h in health.highlights:
                        md_content += f"- {h}\n"
                    md_content += "\n"
                
                if health.concerns:
                    md_content += "### ⚠️ 需关注\n\n"
                    for c in health.concerns:
                        md_content += f"- {c}\n"
                    md_content += "\n"
                
                md_content += "---\n\n"
                
            except Exception as e:
                md_content += f"""## ❌ {repo}

分析失败: {str(e)}

---

"""
        
        md_content += f"""
## 关于本报告

本报告由 **OpenSource Copilot** 自动生成，基于 OpenDigger 数据分析。

- 数据来源: [OpenDigger](https://github.com/X-lab2017/open-digger)
- 评分算法: 多维度加权健康度评估模型
"""
        
        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename=analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            }
        )
    finally:
        await tool.close()


@router.post("/export/json")
async def export_json(request: CompareRequest):
    """
    导出分析结果为 JSON 格式
    """
    compare_result = await compare_repos(request)
    
    json_content = json.dumps(
        compare_result.dict(),
        indent=2,
        ensure_ascii=False
    )
    
    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }
    )


@router.get("/trending")
async def get_trending_repos(
    language: Optional[str] = None,
    period: str = "weekly"
):
    """
    获取趋势项目 (基于 OpenRank 排名)
    """
    # 预设的热门项目列表
    trending_repos = [
        {"repo": "kubernetes/kubernetes", "openrank": 892.5, "category": "云原生"},
        {"repo": "tensorflow/tensorflow", "openrank": 567.3, "category": "AI/ML"},
        {"repo": "microsoft/vscode", "openrank": 445.2, "category": "开发工具"},
        {"repo": "apache/spark", "openrank": 234.8, "category": "大数据"},
        {"repo": "golang/go", "openrank": 198.5, "category": "编程语言"},
        {"repo": "facebook/react", "openrank": 356.7, "category": "前端框架"},
        {"repo": "vuejs/vue", "openrank": 289.4, "category": "前端框架"},
        {"repo": "apache/dubbo", "openrank": 156.2, "category": "微服务"},
        {"repo": "openai/openai-python", "openrank": 134.8, "category": "AI/ML"},
        {"repo": "langchain-ai/langchain", "openrank": 245.6, "category": "AI/ML"},
    ]
    
    return {
        "period": period,
        "language": language,
        "repos": trending_repos,
        "updated_at": datetime.now().isoformat()
    }


@router.get("/history")
async def get_analysis_history(limit: int = 20):
    """
    获取分析历史 (从缓存/数据库)
    
    Note: 当前版本使用内存存储，重启后会清空
    """
    # TODO: 实现持久化存储
    return {
        "history": [],
        "total": 0
    }


def calculate_health_score(metrics: Dict[str, Any], trends: Dict[str, Any] = None) -> HealthScore:
    """
    计算仓库健康度评分
    
    评分维度 (权重):
    - activity (30%): 活跃度 (基于 OpenRank, activity 指标)
    - community (25%): 社区健康度 (基于贡献者数量、巴士因子)
    - maintenance (25%): 维护响应度 (Issue响应时间、PR合并率)
    - growth (20%): 增长趋势 (OpenRank 趋势)
    
    算法:
    - S_activity = 0.6 × min(100, OpenRank) + 0.4 × min(100, Activity × 5)
    - S_community = 0.5 × min(100, Participants/5) + 0.5 × min(100, BusFactor × 10)
    - S_maintenance = 默认70，后续根据响应时间调整
    - S_growth = 基于趋势数据计算
    """
    trends = trends or {}
    
    # 安全获取指标值
    def safe_float(val, default=0):
        if val is None:
            return default
        if isinstance(val, dict):
            # 可能是时序数据，取最新值
            if val:
                return list(val.values())[-1] if val else default
            return default
        try:
            return float(val)
        except:
            return default
    
    openrank = safe_float(metrics.get("openrank"), 0)
    activity = safe_float(metrics.get("activity"), 0)
    attention = safe_float(metrics.get("attention"), 0)
    participants = safe_float(metrics.get("participants"), 0)
    bus_factor = safe_float(metrics.get("bus_factor"), 1)
    new_contributors = safe_float(metrics.get("new_contributors"), 0)
    stars = safe_float(metrics.get("stars"), 0)
    
    # 计算活跃度得分
    activity_score = 0.6 * min(100, openrank) + 0.4 * min(100, activity * 5)
    
    # 计算社区健康度得分
    community_score = 0.5 * min(100, participants / 5) + 0.5 * min(100, bus_factor * 10)
    
    # 计算维护响应度得分 (默认值，后续可以根据实际数据调整)
    maintenance_score = 70
    if attention > 50:
        maintenance_score = min(90, 70 + attention / 10)
    
    # 计算增长趋势得分
    growth_score = 60  # 默认值
    openrank_trend = trends.get('openrank', [])
    if len(openrank_trend) >= 2:
        first_half = openrank_trend[:len(openrank_trend)//2]
        second_half = openrank_trend[len(openrank_trend)//2:]
        
        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0
        
        if avg_first > 0:
            change_rate = (avg_second - avg_first) / avg_first
            if change_rate > 0.1:
                growth_score = min(100, 70 + change_rate * 100)
            elif change_rate < -0.1:
                growth_score = max(30, 60 + change_rate * 100)
    
    # 加入新贡献者和 Star 的影响
    growth_score = 0.6 * growth_score + 0.2 * min(100, new_contributors * 10) + 0.2 * min(100, stars / 100)
    
    # 计算总体评分 (加权平均)
    overall = (
        activity_score * 0.3 +
        community_score * 0.25 +
        maintenance_score * 0.25 +
        growth_score * 0.2
    )
    
    # 生成评估摘要
    summary = generate_summary(overall, activity_score, community_score, maintenance_score, growth_score)
    highlights, concerns = generate_insights(
        openrank, activity, participants, bus_factor, 
        activity_score, community_score, maintenance_score, growth_score
    )
    
    return HealthScore(
        overall=round(overall, 1),
        activity=round(activity_score, 1),
        community=round(community_score, 1),
        maintenance=round(maintenance_score, 1),
        growth=round(growth_score, 1),
        summary=summary,
        highlights=highlights,
        concerns=concerns
    )


def generate_summary(overall: float, activity: float, community: float, 
                    maintenance: float, growth: float) -> str:
    """生成评估摘要"""
    if overall >= 80:
        return "项目整体健康度优秀，各维度表现均衡，是一个非常活跃且成熟的开源项目。"
    elif overall >= 60:
        return "项目整体健康度良好，核心指标稳定，建议关注部分需要改进的维度。"
    elif overall >= 40:
        return "项目健康度一般，存在一些需要关注的问题，建议采取措施改进。"
    else:
        return "项目健康度较低，需要重点关注并采取改进措施。"


def generate_insights(openrank: float, activity: float, participants: float, 
                     bus_factor: float, activity_score: float, community_score: float,
                     maintenance_score: float, growth_score: float) -> tuple:
    """生成亮点和关注点"""
    highlights = []
    concerns = []
    
    # 亮点
    if openrank > 50:
        highlights.append(f"OpenRank 值 {openrank:.1f}，影响力较高")
    if activity > 20:
        highlights.append(f"活跃度 {activity:.1f}，社区非常活跃")
    if participants > 100:
        highlights.append(f"参与者 {int(participants)} 人，社区规模可观")
    if bus_factor > 5:
        highlights.append(f"巴士因子 {int(bus_factor)}，项目不过度依赖单一开发者")
    if activity_score >= 80:
        highlights.append("活跃度维度表现优秀")
    if community_score >= 80:
        highlights.append("社区健康度表现优秀")
    
    # 关注点
    if openrank < 5:
        concerns.append("OpenRank 值较低，建议提升项目影响力")
    if bus_factor < 3:
        concerns.append(f"巴士因子仅为 {int(bus_factor)}，项目可能过度依赖少数开发者")
    if participants < 10:
        concerns.append("参与者数量较少，建议吸引更多贡献者")
    if activity_score < 40:
        concerns.append("活跃度偏低，建议增加项目活动")
    if growth_score < 40:
        concerns.append("增长趋势放缓，建议关注项目发展方向")
    
    return highlights[:3], concerns[:3]


def generate_comparison_summary(results: List[CompareResult]) -> Dict[str, Any]:
    """生成对比汇总"""
    valid_results = [r for r in results if r.health_score is not None]
    
    if not valid_results:
        return {"message": "没有可用的对比数据"}
    
    # 各维度最佳
    best_overall = max(valid_results, key=lambda x: x.health_score.overall)
    best_activity = max(valid_results, key=lambda x: x.health_score.activity)
    best_community = max(valid_results, key=lambda x: x.health_score.community)
    best_maintenance = max(valid_results, key=lambda x: x.health_score.maintenance)
    best_growth = max(valid_results, key=lambda x: x.health_score.growth)
    
    # 平均分
    avg_overall = sum(r.health_score.overall for r in valid_results) / len(valid_results)
    
    return {
        "total_repos": len(results),
        "valid_repos": len(valid_results),
        "average_score": round(avg_overall, 1),
        "best_overall": {"repo": best_overall.repo, "score": best_overall.health_score.overall},
        "best_activity": {"repo": best_activity.repo, "score": best_activity.health_score.activity},
        "best_community": {"repo": best_community.repo, "score": best_community.health_score.community},
        "best_maintenance": {"repo": best_maintenance.repo, "score": best_maintenance.health_score.maintenance},
        "best_growth": {"repo": best_growth.repo, "score": best_growth.health_score.growth},
        "dimensions": ["活跃度", "社区健康", "维护响应", "增长趋势"]
    }
