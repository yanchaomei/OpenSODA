"""
Analysis Agent - 分析 Agent

负责获取项目数据和计算指标
"""
from typing import Dict, Any, Optional
from app.tools.opendigger import OpenDiggerTool
from app.tools.github import GitHubTool
from app.tools.dataease import generate_health_score_chart, generate_trend_chart


async def run_analysis(repo: str) -> Dict[str, Any]:
    """
    运行项目分析
    
    Args:
        repo: 仓库路径，如 "apache/dubbo"
        
    Returns:
        分析结果，包含指标、健康度评分等
    """
    opendigger = OpenDiggerTool()
    github = GitHubTool()
    
    try:
        # 并行获取数据
        import asyncio
        
        metrics_task = opendigger.get_repo_metrics(repo)
        github_info_task = github.get_repo_info(repo)
        contributors_task = opendigger.get_contributors_stats(repo)
        issue_stats_task = opendigger.get_issue_stats(repo)
        pr_stats_task = opendigger.get_pr_stats(repo)
        
        results = await asyncio.gather(
            metrics_task,
            github_info_task,
            contributors_task,
            issue_stats_task,
            pr_stats_task,
            return_exceptions=True
        )
        
        metrics = results[0] if not isinstance(results[0], Exception) else {}
        repo_info = results[1] if not isinstance(results[1], Exception) else {}
        contributors = results[2] if not isinstance(results[2], Exception) else {}
        issue_stats = results[3] if not isinstance(results[3], Exception) else {}
        pr_stats = results[4] if not isinstance(results[4], Exception) else {}
        
        # 合并所有指标
        all_metrics = {
            **metrics,
            **contributors,
            **issue_stats,
            **pr_stats
        }
        
        # 计算健康度评分
        health_score = calculate_health_score(all_metrics, repo_info)
        
        # 生成趋势数据
        trends = await get_trend_data(opendigger, repo)
        
        # 生成图表配置
        charts = generate_charts(health_score, trends, all_metrics)
        
        return {
            "repo": repo,
            "repo_info": repo_info,
            "metrics": all_metrics,
            "health_score": health_score,
            "trends": trends,
            "charts": charts
        }
    
    finally:
        await opendigger.close()
        await github.close()


def _safe_number(value: Any, default: float = 0) -> float:
    """安全地将值转换为数字"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        # 如果是字典，尝试获取最新值
        if value:
            try:
                sorted_keys = sorted(value.keys())
                return float(value[sorted_keys[-1]]) if sorted_keys else default
            except (ValueError, TypeError):
                return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def calculate_health_score(metrics: Dict[str, Any], repo_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算仓库健康度评分
    
    评分维度（各项 0-100）：
    - activity: 活跃度（基于 OpenRank、Activity 指标）
    - community: 社区健康度（基于贡献者数量、多样性、巴士因子）
    - maintenance: 维护响应度（基于 Issue 响应时间、PR 合并率）
    - growth: 增长趋势（基于 Star/Fork 增长、新贡献者）
    """
    # 活跃度评分 - 安全类型转换
    openrank = _safe_number(metrics.get("openrank", 0))
    activity = _safe_number(metrics.get("activity", 0))
    
    # OpenRank 归一化（假设 100 为顶级项目）
    openrank_score = min(100, openrank * 1)
    activity_score = min(100, activity * 5)
    activity_final = openrank_score * 0.6 + activity_score * 0.4
    
    # 社区健康度评分 - 安全类型转换
    participants = _safe_number(metrics.get("total_participants", 0))
    bus_factor = _safe_number(metrics.get("bus_factor", 1), default=1)
    
    # 参与者数量评分（500+ 满分）
    participants_score = min(100, participants / 5) if participants else 0
    # 巴士因子评分（10+ 满分）
    bus_factor_score = min(100, bus_factor * 10)
    community_final = participants_score * 0.5 + bus_factor_score * 0.5
    
    # 维护响应度评分 - 安全类型转换
    merge_rate = _safe_number(metrics.get("merge_rate", 0.5), default=0.5)
    response_time = _safe_number(metrics.get("avg_response_time"))
    
    merge_rate_score = merge_rate * 100
    # 响应时间评分（24小时内满分，7天为0）
    if response_time > 0:
        response_score = max(0, 100 - (response_time / 168) * 100)
    else:
        response_score = 50  # 默认中等
    maintenance_final = merge_rate_score * 0.5 + response_score * 0.5
    
    # 增长趋势评分 - 安全类型转换
    new_contributors = _safe_number(metrics.get("new_contributors", 0))
    stars = _safe_number(repo_info.get("stars", 0)) if repo_info else 0
    
    # 新贡献者评分（月均10+ 满分）
    new_contrib_score = min(100, new_contributors * 10)
    # Star 数评分（10000+ 满分）
    stars_score = min(100, stars / 100) if stars > 0 else 50
    growth_final = new_contrib_score * 0.6 + stars_score * 0.4
    
    # 总体评分（加权平均）
    overall = (
        activity_final * 0.3 +
        community_final * 0.25 +
        maintenance_final * 0.25 +
        growth_final * 0.2
    )
    
    # 生成评分解释
    summary, highlights, concerns = generate_score_interpretation(
        overall, activity_final, community_final, maintenance_final, growth_final, metrics
    )
    
    return {
        "overall": round(overall, 1),
        "activity": round(activity_final, 1),
        "community": round(community_final, 1),
        "maintenance": round(maintenance_final, 1),
        "growth": round(growth_final, 1),
        "summary": summary,
        "highlights": highlights,
        "concerns": concerns
    }


def generate_score_interpretation(
    overall: float,
    activity: float,
    community: float,
    maintenance: float,
    growth: float,
    metrics: Dict[str, Any]
) -> tuple:
    """生成评分解释"""
    
    # 总体评价
    if overall >= 80:
        summary = "项目整体健康状况优秀，社区运营良好"
    elif overall >= 60:
        summary = "项目健康状况良好，有一些可以改进的地方"
    elif overall >= 40:
        summary = "项目健康状况一般，建议重点关注薄弱环节"
    else:
        summary = "项目健康状况需要关注，建议采取改进措施"
    
    # 亮点
    highlights = []
    if activity >= 70:
        highlights.append(f"项目活跃度高，OpenRank 值为 {metrics.get('openrank', 'N/A')}")
    if community >= 70:
        highlights.append(f"社区健康，有 {metrics.get('total_participants', 'N/A')} 位参与者")
    if maintenance >= 70:
        highlights.append("维护响应迅速，Issue/PR 处理及时")
    if growth >= 70:
        highlights.append("项目保持良好增长态势")
    
    if not highlights:
        highlights.append("项目正在稳定发展中")
    
    # 关注点
    concerns = []
    if activity < 50:
        concerns.append("活跃度较低，建议增加社区活动")
    if community < 50:
        concerns.append("贡献者生态需要加强，建议吸引更多参与者")
    if maintenance < 50:
        concerns.append("维护响应可以更快，建议优化 Issue/PR 处理流程")
    if growth < 50:
        concerns.append("增长趋势放缓，建议加强推广和社区运营")
    
    # 特殊风险检查
    bus_factor = metrics.get("bus_factor", 0)
    if bus_factor and bus_factor < 3:
        concerns.append(f"巴士因子仅为 {bus_factor}，项目过于依赖少数贡献者")
    
    return summary, highlights, concerns


async def get_trend_data(tool: OpenDiggerTool, repo: str) -> Dict[str, Any]:
    """获取趋势数据"""
    import asyncio
    
    tasks = [
        tool.get_trend_data(repo, "openrank", 12),
        tool.get_trend_data(repo, "activity", 12),
        tool.get_trend_data(repo, "stars", 12),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        "openrank": results[0] if not isinstance(results[0], Exception) else [],
        "activity": results[1] if not isinstance(results[1], Exception) else [],
        "stars": results[2] if not isinstance(results[2], Exception) else [],
    }


def generate_charts(
    health_score: Dict[str, Any],
    trends: Dict[str, Any],
    metrics: Dict[str, Any]
) -> list:
    """生成图表配置"""
    charts = []
    
    # 健康度雷达图
    health_chart = generate_health_score_chart(health_score)
    charts.append({
        "id": "health_radar",
        "type": "radar",
        "title": "社区健康度",
        "config": health_chart
    })
    
    # OpenRank 趋势图
    if trends.get("openrank"):
        openrank_chart = generate_trend_chart(trends["openrank"], "OpenRank")
        charts.append({
            "id": "openrank_trend",
            "type": "line",
            "title": "OpenRank 趋势",
            "config": openrank_chart
        })
    
    # 活跃度趋势图
    if trends.get("activity"):
        activity_chart = generate_trend_chart(trends["activity"], "活跃度")
        charts.append({
            "id": "activity_trend",
            "type": "line",
            "title": "活跃度趋势",
            "config": activity_chart
        })
    
    return charts

