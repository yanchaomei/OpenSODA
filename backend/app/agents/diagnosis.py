"""
Diagnosis Agent - 诊断 Agent

负责识别问题、定位瓶颈、评估风险
"""
from typing import Dict, Any, List, Optional


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


async def run_diagnosis(
    metrics: Dict[str, Any],
    health_score: Dict[str, Any]
) -> Dict[str, Any]:
    """
    运行诊断分析
    
    Args:
        metrics: 项目指标数据
        health_score: 健康度评分
        
    Returns:
        诊断结果，包含问题、风险、严重程度
    """
    issues = []
    risks = []
    severity = "low"
    details = {}
    
    # 活跃度诊断
    activity_issues = diagnose_activity(metrics, health_score)
    issues.extend(activity_issues["issues"])
    risks.extend(activity_issues["risks"])
    details["activity"] = activity_issues
    
    # 社区诊断
    community_issues = diagnose_community(metrics, health_score)
    issues.extend(community_issues["issues"])
    risks.extend(community_issues["risks"])
    details["community"] = community_issues
    
    # 维护诊断
    maintenance_issues = diagnose_maintenance(metrics, health_score)
    issues.extend(maintenance_issues["issues"])
    risks.extend(maintenance_issues["risks"])
    details["maintenance"] = maintenance_issues
    
    # 增长诊断
    growth_issues = diagnose_growth(metrics, health_score)
    issues.extend(growth_issues["issues"])
    risks.extend(growth_issues["risks"])
    details["growth"] = growth_issues
    
    # 确定整体严重程度
    if len(issues) >= 5 or any("严重" in i or "高风险" in i for i in issues):
        severity = "high"
    elif len(issues) >= 3:
        severity = "medium"
    else:
        severity = "low"
    
    return {
        "issues": issues,
        "risks": risks,
        "severity": severity,
        "details": details,
        "summary": generate_diagnosis_summary(issues, risks, severity)
    }


def diagnose_activity(metrics: Dict[str, Any], health_score: Dict[str, Any]) -> Dict[str, Any]:
    """诊断活跃度相关问题"""
    issues = []
    risks = []
    
    openrank = _safe_number(metrics.get("openrank", 0))
    activity = _safe_number(metrics.get("activity", 0))
    activity_score = _safe_number(health_score.get("activity", 50), default=50)
    
    # 检查 OpenRank
    if openrank < 5:
        issues.append("OpenRank 值较低，项目影响力有限")
        risks.append("项目可能难以吸引新贡献者")
    elif openrank < 20:
        risks.append("OpenRank 处于中等水平，有提升空间")
    
    # 检查活跃度
    if activity < 5:
        issues.append("月度活跃度较低，社区参与不活跃")
    
    # 检查趋势
    openrank_history = metrics.get("openrank_history", {})
    if openrank_history:
        trend = analyze_trend(openrank_history)
        if trend == "declining":
            issues.append("OpenRank 呈下降趋势，需要关注")
            risks.append("如果趋势持续，项目影响力会进一步下降")
    
    return {
        "issues": issues,
        "risks": risks,
        "score": activity_score,
        "metrics": {
            "openrank": openrank,
            "activity": activity
        }
    }


def diagnose_community(metrics: Dict[str, Any], health_score: Dict[str, Any]) -> Dict[str, Any]:
    """诊断社区健康相关问题"""
    issues = []
    risks = []
    
    participants = _safe_number(metrics.get("total_participants", 0))
    bus_factor = _safe_number(metrics.get("bus_factor", 0))
    new_contributors = _safe_number(metrics.get("new_contributors", 0))
    community_score = _safe_number(health_score.get("community", 50), default=50)
    
    # 检查巴士因子
    if bus_factor < 2:
        issues.append(f"巴士因子仅为 {int(bus_factor)}，项目严重依赖单一贡献者")
        risks.append("核心贡献者离开可能导致项目停滞")
    elif bus_factor < 3:
        risks.append(f"巴士因子为 {int(bus_factor)}，建议培养更多核心贡献者")
    
    # 检查参与者数量
    if participants < 10:
        issues.append("参与者数量较少，社区规模有限")
    elif participants < 50:
        risks.append("社区规模中等，有增长空间")
    
    # 检查新贡献者
    if new_contributors == 0:
        issues.append("近期没有新贡献者加入")
        risks.append("社区可能对新人不够友好")
    elif new_contributors < 2:
        risks.append("新贡献者增长缓慢")
    
    return {
        "issues": issues,
        "risks": risks,
        "score": community_score,
        "metrics": {
            "participants": participants,
            "bus_factor": bus_factor,
            "new_contributors": new_contributors
        }
    }


def diagnose_maintenance(metrics: Dict[str, Any], health_score: Dict[str, Any]) -> Dict[str, Any]:
    """诊断维护响应相关问题"""
    issues = []
    risks = []
    
    merge_rate = _safe_number(metrics.get("merge_rate", 0))
    response_time = _safe_number(metrics.get("avg_response_time")) or None  # 小时
    resolution_time = _safe_number(metrics.get("avg_resolution_time")) or None  # 小时
    maintenance_score = _safe_number(health_score.get("maintenance", 50), default=50)
    
    # 检查 PR 合并率
    if merge_rate < 0.3:
        issues.append(f"PR 合并率较低 ({merge_rate:.1%})，可能存在积压")
        risks.append("贡献者可能因 PR 长期未处理而流失")
    elif merge_rate < 0.5:
        risks.append(f"PR 合并率为 {merge_rate:.1%}，有优化空间")
    
    # 检查 Issue 响应时间
    if response_time is not None:
        if response_time > 168:  # 超过一周
            issues.append(f"Issue 平均响应时间超过 {response_time/24:.1f} 天，响应较慢")
        elif response_time > 72:  # 超过3天
            risks.append(f"Issue 平均响应时间为 {response_time/24:.1f} 天，可以更快")
    
    # 检查 Issue 解决时间
    if resolution_time is not None:
        if resolution_time > 720:  # 超过一个月
            issues.append("Issue 平均解决时间超过一个月")
    
    return {
        "issues": issues,
        "risks": risks,
        "score": maintenance_score,
        "metrics": {
            "merge_rate": merge_rate,
            "response_time": response_time,
            "resolution_time": resolution_time
        }
    }


def diagnose_growth(metrics: Dict[str, Any], health_score: Dict[str, Any]) -> Dict[str, Any]:
    """诊断增长趋势相关问题"""
    issues = []
    risks = []
    
    new_contributors = _safe_number(metrics.get("new_contributors", 0))
    growth_score = _safe_number(health_score.get("growth", 50), default=50)
    
    # 检查新贡献者增长
    if new_contributors == 0:
        issues.append("近期没有新贡献者，增长停滞")
    
    # 检查 Star 趋势
    stars_history = metrics.get("stars_history", {})
    if stars_history:
        trend = analyze_trend(stars_history)
        if trend == "declining":
            risks.append("Star 增长放缓，项目关注度下降")
    
    # 检查活跃度趋势
    activity_history = metrics.get("activity_history", {})
    if activity_history:
        trend = analyze_trend(activity_history)
        if trend == "declining":
            issues.append("活跃度呈下降趋势")
            risks.append("如果趋势持续，项目可能逐渐沉寂")
    
    return {
        "issues": issues,
        "risks": risks,
        "score": growth_score,
        "metrics": {
            "new_contributors": new_contributors
        }
    }


def analyze_trend(history: Dict[str, Any]) -> str:
    """
    分析趋势方向
    
    Returns:
        "rising", "stable", "declining"
    """
    if not history or len(history) < 3:
        return "stable"
    
    # 获取时间排序的值
    sorted_items = sorted(history.items())
    values = [v for k, v in sorted_items if isinstance(v, (int, float))]
    
    if len(values) < 3:
        return "stable"
    
    # 比较前半段和后半段的平均值
    mid = len(values) // 2
    first_half_avg = sum(values[:mid]) / mid if mid > 0 else 0
    second_half_avg = sum(values[mid:]) / (len(values) - mid) if len(values) > mid else 0
    
    if first_half_avg == 0:
        return "stable"
    
    change_rate = (second_half_avg - first_half_avg) / first_half_avg
    
    if change_rate > 0.1:
        return "rising"
    elif change_rate < -0.1:
        return "declining"
    else:
        return "stable"


def generate_diagnosis_summary(issues: List[str], risks: List[str], severity: str) -> str:
    """生成诊断摘要"""
    if severity == "high":
        intro = "项目存在多个需要重点关注的问题："
    elif severity == "medium":
        intro = "项目整体状况尚可，但存在一些需要改进的地方："
    else:
        intro = "项目健康状况良好，以下是一些可选的优化建议："
    
    summary_parts = [intro]
    
    if issues:
        summary_parts.append(f"\n发现 {len(issues)} 个问题：")
        for i, issue in enumerate(issues[:5], 1):  # 最多显示5个
            summary_parts.append(f"  {i}. {issue}")
    
    if risks:
        summary_parts.append(f"\n潜在风险 {len(risks)} 项：")
        for i, risk in enumerate(risks[:3], 1):  # 最多显示3个
            summary_parts.append(f"  {i}. {risk}")
    
    return "\n".join(summary_parts)

