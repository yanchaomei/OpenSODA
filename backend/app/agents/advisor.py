"""
Advisor Agent - 建议 Agent

负责生成运营建议和最佳实践
"""
from typing import Dict, Any, List, Optional
from app.tools.maxkb import search_opensource_knowledge
from app.tools.dataease import generate_health_score_chart


async def run_advisor(
    diagnosis: Dict[str, Any],
    metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    运行建议生成
    
    Args:
        diagnosis: 诊断结果
        metrics: 项目指标
        
    Returns:
        建议列表和图表
    """
    recommendations = []
    charts = []
    
    issues = diagnosis.get("issues", [])
    risks = diagnosis.get("risks", [])
    details = diagnosis.get("details", {})
    
    # 根据诊断结果生成建议
    
    # 活跃度相关建议
    if details.get("activity", {}).get("score", 100) < 60:
        activity_recs = generate_activity_recommendations(
            details.get("activity", {}),
            metrics
        )
        recommendations.extend(activity_recs)
    
    # 社区相关建议
    if details.get("community", {}).get("score", 100) < 60:
        community_recs = generate_community_recommendations(
            details.get("community", {}),
            metrics
        )
        recommendations.extend(community_recs)
    
    # 维护相关建议
    if details.get("maintenance", {}).get("score", 100) < 60:
        maintenance_recs = generate_maintenance_recommendations(
            details.get("maintenance", {}),
            metrics
        )
        recommendations.extend(maintenance_recs)
    
    # 增长相关建议
    if details.get("growth", {}).get("score", 100) < 60:
        growth_recs = generate_growth_recommendations(
            details.get("growth", {}),
            metrics
        )
        recommendations.extend(growth_recs)
    
    # 如果没有特别问题，给出通用建议
    if not recommendations:
        recommendations = generate_general_recommendations(metrics)
    
    # 按优先级排序
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))
    
    return {
        "recommendations": recommendations,
        "charts": charts
    }


def generate_activity_recommendations(
    activity_details: Dict[str, Any],
    metrics: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """生成活跃度相关建议"""
    recommendations = []
    
    openrank = activity_details.get("metrics", {}).get("openrank", 0)
    
    if openrank < 10:
        recommendations.append({
            "category": "activity",
            "title": "提升项目影响力",
            "description": "当前 OpenRank 值较低，建议通过多种方式提升项目曝光度和参与度",
            "priority": "high",
            "actions": [
                "在技术社区（如掘金、思否、知乎）发布项目介绍文章",
                "制作项目演示视频或教程",
                "积极参与相关技术话题讨论",
                "寻找合作项目，建立生态联系"
            ],
            "reference": "https://opensource.guide/building-community/"
        })
    
    recommendations.append({
        "category": "activity",
        "title": "定期发布更新",
        "description": "保持项目活跃的关键是持续迭代",
        "priority": "medium",
        "actions": [
            "制定发版计划，定期发布新版本",
            "及时修复 Bug 和处理安全问题",
            "定期更新文档和示例"
        ]
    })
    
    return recommendations


def generate_community_recommendations(
    community_details: Dict[str, Any],
    metrics: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """生成社区相关建议"""
    recommendations = []
    
    bus_factor = community_details.get("metrics", {}).get("bus_factor", 0)
    new_contributors = community_details.get("metrics", {}).get("new_contributors", 0)
    
    # 巴士因子低
    if bus_factor < 3:
        recommendations.append({
            "category": "community",
            "title": "培养更多核心贡献者",
            "description": f"当前巴士因子仅为 {bus_factor}，项目过于依赖少数人",
            "priority": "high",
            "actions": [
                "识别活跃的贡献者，主动邀请他们承担更多职责",
                "完善开发文档，降低贡献门槛",
                "建立 Mentor 机制，指导新贡献者",
                "逐步下放代码审查和合并权限"
            ],
            "reference": "https://opensource.guide/leadership-and-governance/"
        })
    
    # 新贡献者少
    if new_contributors < 2:
        recommendations.append({
            "category": "community",
            "title": "吸引新贡献者",
            "description": "新贡献者是社区持续发展的动力",
            "priority": "high",
            "actions": [
                "创建 'good first issue' 标签，标记适合新手的任务",
                "编写详细的 CONTRIBUTING.md 贡献指南",
                "对首次贡献的 PR 给予积极反馈和鼓励",
                "举办 Hackathon 或贡献者活动"
            ]
        })
    
    recommendations.append({
        "category": "community",
        "title": "建立社区沟通渠道",
        "description": "良好的沟通能增强社区凝聚力",
        "priority": "medium",
        "actions": [
            "创建 Discord/Slack 群组方便实时交流",
            "定期举办社区会议或直播",
            "建立邮件列表讨论重要决策",
            "在 README 中明确标注沟通渠道"
        ]
    })
    
    return recommendations


def generate_maintenance_recommendations(
    maintenance_details: Dict[str, Any],
    metrics: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """生成维护相关建议"""
    recommendations = []
    
    merge_rate = maintenance_details.get("metrics", {}).get("merge_rate", 0)
    response_time = maintenance_details.get("metrics", {}).get("response_time")
    
    # PR 合并率低
    if merge_rate < 0.5:
        recommendations.append({
            "category": "maintenance",
            "title": "优化 PR 处理流程",
            "description": f"当前 PR 合并率为 {merge_rate:.1%}，建议优化处理效率",
            "priority": "high",
            "actions": [
                "设置 CI/CD 自动化检查，加速代码审查",
                "明确 PR 规范，使用 PR 模板",
                "定期清理过期的 PR",
                "考虑增加 Reviewer 数量"
            ]
        })
    
    # 响应时间慢
    if response_time and response_time > 72:
        recommendations.append({
            "category": "maintenance",
            "title": "提升 Issue 响应速度",
            "description": f"当前平均响应时间为 {response_time/24:.1f} 天，可以更快",
            "priority": "medium",
            "actions": [
                "使用 Issue 模板规范问题报告",
                "设置 Bot 自动回复和分类",
                "建立值班机制，确保及时响应",
                "将常见问题整理到 FAQ 文档"
            ]
        })
    
    recommendations.append({
        "category": "maintenance",
        "title": "完善自动化流程",
        "description": "自动化能提升维护效率",
        "priority": "low",
        "actions": [
            "配置 GitHub Actions 进行自动测试",
            "使用 Dependabot 自动更新依赖",
            "设置自动发布流程",
            "添加代码质量检查（如 SonarQube）"
        ]
    })
    
    return recommendations


def generate_growth_recommendations(
    growth_details: Dict[str, Any],
    metrics: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """生成增长相关建议"""
    recommendations = []
    
    recommendations.append({
        "category": "growth",
        "title": "加强项目推广",
        "description": "让更多人了解和使用项目",
        "priority": "medium",
        "actions": [
            "撰写技术博客介绍项目特性和使用场景",
            "在技术大会上演讲或做 Workshop",
            "与相关项目建立合作关系",
            "优化 README 和文档，降低上手门槛"
        ]
    })
    
    recommendations.append({
        "category": "growth",
        "title": "建立用户反馈机制",
        "description": "了解用户需求才能持续增长",
        "priority": "low",
        "actions": [
            "定期收集用户反馈",
            "分析 Issue 中的常见需求",
            "建立功能投票机制",
            "发布用户调研问卷"
        ]
    })
    
    return recommendations


def generate_general_recommendations(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """生成通用建议（项目状况良好时）"""
    return [
        {
            "category": "general",
            "title": "保持良好势头",
            "description": "项目健康状况良好，继续保持当前的运营策略",
            "priority": "low",
            "actions": [
                "持续关注社区动态",
                "定期回顾和优化流程",
                "保持文档更新"
            ]
        },
        {
            "category": "general",
            "title": "探索新机会",
            "description": "在稳定的基础上寻求突破",
            "priority": "low",
            "actions": [
                "探索新的应用场景",
                "考虑参与开源基金会",
                "建立更广泛的生态合作"
            ]
        }
    ]


def get_knowledge_for_issue(issue: str) -> Optional[str]:
    """从知识库获取相关建议"""
    return search_opensource_knowledge(issue)

