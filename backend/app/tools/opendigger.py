"""
OpenDigger API 工具封装
OpenDigger: https://github.com/X-lab2017/open-digger

提供开源项目的各种指标数据获取能力
"""
import httpx
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
from app.core.config import settings


class OpenDiggerTool:
    """
    OpenDigger API 工具类
    
    OpenDigger 数据格式说明:
    - 数据以 JSON 文件形式存储在 CDN
    - URL格式: https://oss.x-lab.info/open_digger/github/{owner}/{repo}/{metric}.json
    - 返回数据通常是按月份索引的时序数据
    """
    
    BASE_URL = "https://oss.x-lab.info/open_digger/github"
    
    # 可用的指标列表
    AVAILABLE_METRICS = [
        "openrank",           # OpenRank 值
        "activity",           # 活跃度
        "attention",          # 关注度
        "stars",              # Star 数
        "technical_fork",     # Fork 数
        "participants",       # 参与者数
        "new_contributors",   # 新贡献者数
        "bus_factor",         # 巴士因子
        "issues_new",         # 新 Issue 数
        "issues_closed",      # 关闭 Issue 数
        "issue_comments",     # Issue 评论数
        "issue_response_time",     # Issue 响应时间
        "issue_resolution_duration", # Issue 解决时长
        "change_requests",    # PR 数
        "change_requests_accepted", # 合并 PR 数
        "change_requests_reviews",  # PR Review 数
        "code_change_lines_add",    # 代码添加行数
        "code_change_lines_remove", # 代码删除行数
        "code_change_lines_sum",    # 代码变更行数
    ]
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_metric(self, repo: str, metric: str) -> Optional[Dict[str, Any]]:
        """
        获取单个指标数据
        
        Args:
            repo: 仓库路径，如 "apache/dubbo"
            metric: 指标名称，如 "openrank"
            
        Returns:
            指标数据字典，按月份索引
        """
        url = f"{self.BASE_URL}/{repo}/{metric}.json"
        
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch {metric} for {repo}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching {metric} for {repo}: {e}")
            return None
    
    async def get_repo_metrics(self, repo: str) -> Dict[str, Any]:
        """
        获取仓库的综合指标数据
        
        Args:
            repo: 仓库路径，如 "apache/dubbo"
            
        Returns:
            包含各项指标的字典
        """
        # 核心指标
        core_metrics = [
            "openrank",
            "activity", 
            "attention",
            "stars",
            "participants",
            "new_contributors",
            "bus_factor",
        ]
        
        result = {"repo": repo}
        
        for metric in core_metrics:
            data = await self.get_metric(repo, metric)
            if data:
                # 获取最新值（最后一个月的数据）
                latest_value = self._get_latest_value(data)
                result[metric] = latest_value
                # 保留历史数据
                result[f"{metric}_history"] = data
        
        return result
    
    async def get_openrank(self, repo: str) -> Optional[float]:
        """获取仓库的 OpenRank 值"""
        data = await self.get_metric(repo, "openrank")
        if data:
            return self._get_latest_value(data)
        return None
    
    async def get_activity(self, repo: str) -> Optional[float]:
        """获取仓库的活跃度"""
        data = await self.get_metric(repo, "activity")
        if data:
            return self._get_latest_value(data)
        return None
    
    async def get_contributors_stats(self, repo: str) -> Dict[str, Any]:
        """获取贡献者统计"""
        participants = await self.get_metric(repo, "participants")
        new_contributors = await self.get_metric(repo, "new_contributors")
        bus_factor = await self.get_metric(repo, "bus_factor")
        
        return {
            "total_participants": self._get_latest_value(participants) if participants else 0,
            "new_contributors": self._get_latest_value(new_contributors) if new_contributors else 0,
            "bus_factor": self._get_latest_value(bus_factor) if bus_factor else 0,
        }
    
    async def get_issue_stats(self, repo: str) -> Dict[str, Any]:
        """获取 Issue 统计"""
        issues_new = await self.get_metric(repo, "issues_new")
        issues_closed = await self.get_metric(repo, "issues_closed")
        response_time = await self.get_metric(repo, "issue_response_time")
        resolution_time = await self.get_metric(repo, "issue_resolution_duration")
        
        return {
            "new_issues": self._get_latest_value(issues_new) if issues_new else 0,
            "closed_issues": self._get_latest_value(issues_closed) if issues_closed else 0,
            "avg_response_time": self._get_latest_value(response_time) if response_time else None,
            "avg_resolution_time": self._get_latest_value(resolution_time) if resolution_time else None,
        }
    
    async def get_pr_stats(self, repo: str) -> Dict[str, Any]:
        """获取 PR 统计"""
        prs = await self.get_metric(repo, "change_requests")
        prs_merged = await self.get_metric(repo, "change_requests_accepted")
        pr_reviews = await self.get_metric(repo, "change_requests_reviews")
        
        prs_count = self._get_latest_value(prs) if prs else 0
        merged_count = self._get_latest_value(prs_merged) if prs_merged else 0
        
        return {
            "total_prs": prs_count,
            "merged_prs": merged_count,
            "merge_rate": merged_count / prs_count if prs_count > 0 else 0,
            "reviews": self._get_latest_value(pr_reviews) if pr_reviews else 0,
        }
    
    async def get_trend_data(self, repo: str, metric: str, months: int = 12) -> List[Dict[str, Any]]:
        """
        获取指标的趋势数据
        
        Args:
            repo: 仓库路径
            metric: 指标名称
            months: 获取最近多少个月的数据
            
        Returns:
            按时间排序的趋势数据列表
        """
        data = await self.get_metric(repo, metric)
        if not data:
            return []
        
        # 按月份排序并取最近N个月
        sorted_items = sorted(data.items(), key=lambda x: x[0])
        recent_items = sorted_items[-months:] if len(sorted_items) > months else sorted_items
        
        return [{"month": k, "value": v} for k, v in recent_items]
    
    def _get_latest_value(self, data: Dict[str, Any]) -> Any:
        """
        从时序数据中获取最新值
        OpenDigger 数据格式为 {"2024-01": value, "2024-02": value, ...}
        """
        if not data:
            return None
        
        # 按月份排序，取最新的值
        sorted_keys = sorted(data.keys())
        if sorted_keys:
            return data[sorted_keys[-1]]
        return None
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


# LangChain Tool 装饰器版本，供 Agent 使用
@tool
async def get_repo_openrank(repo: str) -> str:
    """
    获取开源仓库的 OpenRank 值。OpenRank 是衡量开源项目影响力的核心指标。
    
    Args:
        repo: 仓库路径，格式为 "owner/repo"，例如 "apache/dubbo"
        
    Returns:
        仓库的 OpenRank 值和简要解读
    """
    tool_instance = OpenDiggerTool()
    try:
        openrank = await tool_instance.get_openrank(repo)
        if openrank is not None:
            # 提供简单的解读
            if openrank > 100:
                level = "极高，是顶级开源项目"
            elif openrank > 50:
                level = "很高，是知名开源项目"
            elif openrank > 20:
                level = "较高，是活跃的开源项目"
            elif openrank > 5:
                level = "中等，有一定影响力"
            else:
                level = "较低，需要提升影响力"
            
            return f"仓库 {repo} 的 OpenRank 值为 {openrank:.2f}，影响力{level}。"
        else:
            return f"未能获取仓库 {repo} 的 OpenRank 数据，请检查仓库路径是否正确。"
    finally:
        await tool_instance.close()


@tool
async def get_repo_health_metrics(repo: str) -> str:
    """
    获取开源仓库的健康度指标，包括活跃度、关注度、贡献者等多维度数据。
    
    Args:
        repo: 仓库路径，格式为 "owner/repo"，例如 "apache/dubbo"
        
    Returns:
        仓库的综合健康度指标
    """
    tool_instance = OpenDiggerTool()
    try:
        metrics = await tool_instance.get_repo_metrics(repo)
        
        summary_parts = [f"仓库 {repo} 的健康度指标："]
        
        if metrics.get("openrank"):
            summary_parts.append(f"- OpenRank: {metrics['openrank']:.2f}")
        if metrics.get("activity"):
            summary_parts.append(f"- 活跃度: {metrics['activity']:.2f}")
        if metrics.get("attention"):
            summary_parts.append(f"- 关注度: {metrics['attention']:.2f}")
        if metrics.get("participants"):
            summary_parts.append(f"- 参与者数: {metrics['participants']}")
        if metrics.get("bus_factor"):
            summary_parts.append(f"- 巴士因子: {metrics['bus_factor']}")
        
        return "\n".join(summary_parts)
    finally:
        await tool_instance.close()


@tool
async def get_repo_contributors_info(repo: str) -> str:
    """
    获取开源仓库的贡献者相关信息，包括贡献者数量、新增贡献者、巴士因子等。
    
    Args:
        repo: 仓库路径，格式为 "owner/repo"
        
    Returns:
        贡献者相关统计信息
    """
    tool_instance = OpenDiggerTool()
    try:
        stats = await tool_instance.get_contributors_stats(repo)
        
        result = f"""仓库 {repo} 的贡献者统计：
- 总参与者数: {stats['total_participants']}
- 新增贡献者: {stats['new_contributors']}
- 巴士因子: {stats['bus_factor']}

巴士因子说明：表示项目核心贡献者的数量，数值越高表示项目越不依赖单一开发者。"""
        
        return result
    finally:
        await tool_instance.close()


@tool
async def get_repo_activity_trend(repo: str, months: int = 6) -> str:
    """
    获取开源仓库的活跃度趋势数据。
    
    Args:
        repo: 仓库路径，格式为 "owner/repo"
        months: 获取最近多少个月的数据，默认6个月
        
    Returns:
        活跃度趋势数据
    """
    tool_instance = OpenDiggerTool()
    try:
        trend = await tool_instance.get_trend_data(repo, "activity", months)
        
        if not trend:
            return f"未能获取仓库 {repo} 的活跃度趋势数据"
        
        result = f"仓库 {repo} 最近 {len(trend)} 个月的活跃度趋势：\n"
        for item in trend:
            result += f"- {item['month']}: {item['value']:.2f}\n"
        
        # 计算趋势
        if len(trend) >= 2:
            first_val = trend[0]['value']
            last_val = trend[-1]['value']
            if last_val > first_val:
                result += f"\n趋势分析: 活跃度呈上升趋势，增长了 {((last_val - first_val) / first_val * 100):.1f}%"
            elif last_val < first_val:
                result += f"\n趋势分析: 活跃度呈下降趋势，下降了 {((first_val - last_val) / first_val * 100):.1f}%"
            else:
                result += "\n趋势分析: 活跃度保持稳定"
        
        return result
    finally:
        await tool_instance.close()

