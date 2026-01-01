"""
MaxKB 知识库工具封装
MaxKB: https://github.com/1Panel-dev/MaxKB

提供知识库检索和问答能力
"""
import httpx
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
from app.core.config import settings


class MaxKBTool:
    """
    MaxKB 知识库工具类
    
    MaxKB 是一个基于大语言模型的知识库问答系统
    支持文档上传、知识检索和智能问答
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or settings.MAXKB_BASE_URL
        self.api_key = api_key or settings.MAXKB_API_KEY
        
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=60.0
        )
    
    async def search_knowledge(
        self,
        query: str,
        dataset_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        在知识库中搜索相关内容
        
        Args:
            query: 搜索查询
            dataset_id: 数据集ID（可选）
            top_k: 返回结果数量
            
        Returns:
            相关知识片段列表
        """
        url = f"{self.base_url}/api/dataset/search"
        
        payload = {
            "query": query,
            "top_k": top_k
        }
        if dataset_id:
            payload["dataset_id"] = dataset_id
        
        try:
            response = await self.client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                print(f"MaxKB search error: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error searching MaxKB: {e}")
            return []
    
    async def ask_question(
        self,
        question: str,
        application_id: Optional[str] = None,
        history: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """
        向知识库提问
        
        Args:
            question: 问题
            application_id: 应用ID
            history: 对话历史
            
        Returns:
            回答内容
        """
        url = f"{self.base_url}/api/application/chat"
        
        payload = {
            "message": question,
            "history": history or []
        }
        if application_id:
            payload["application_id"] = application_id
        
        try:
            response = await self.client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("content")
            else:
                print(f"MaxKB chat error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error chatting with MaxKB: {e}")
            return None
    
    async def list_datasets(self) -> List[Dict[str, Any]]:
        """
        列出所有数据集
        
        Returns:
            数据集列表
        """
        url = f"{self.base_url}/api/dataset"
        
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []
        except Exception as e:
            print(f"Error listing datasets: {e}")
            return []
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


# 预置的开源运营知识库内容（当 MaxKB 未配置时使用）
OPENSOURCE_KNOWLEDGE_BASE = {
    "community_health": """
开源社区健康度评估要点：
1. 活跃度指标：定期的代码提交、Issue 讨论、PR 合并
2. 多样性：贡献者来自不同组织、地区
3. 响应速度：Issue 和 PR 的响应时间
4. 文档完善度：README、贡献指南、API 文档
5. 治理透明度：决策过程公开、规则明确
""",
    "contributor_growth": """
如何提升开源项目贡献者数量：
1. 标记 "good first issue" 吸引新手
2. 编写详细的贡献指南 (CONTRIBUTING.md)
3. 及时回复和合并 PR，给予正向反馈
4. 建立社区沟通渠道（Discord、Slack、微信群）
5. 定期举办贡献者活动和 Hackathon
6. 公开感谢贡献者（Contributors 列表、Release Notes）
""",
    "issue_management": """
Issue 管理最佳实践：
1. 使用 Issue 模板规范问题报告
2. 及时分类和打标签
3. 设置 SLA 目标（如 48 小时内首次回复）
4. 定期清理过期 Issue
5. 将常见问题整理到 FAQ 或文档
""",
    "pr_review": """
PR Review 最佳实践：
1. 建立代码审查规范
2. 使用自动化 CI/CD 检查
3. 避免 PR 积压，设置合并时间目标
4. 给予建设性反馈
5. 对于大型 PR，建议拆分
""",
    "openrank_explanation": """
OpenRank 指标解读：
OpenRank 是 X-lab 提出的开源项目影响力评估算法，基于协作网络的 PageRank 变体。

核心特点：
1. 考虑贡献者的质量和多样性
2. 时间衰减因子，近期活动权重更高
3. 综合考虑 Issue、PR、Review、Commit 等多种贡献
4. 全球开源项目可比较

OpenRank 值参考：
- > 100: 顶级开源项目（如 Linux、Kubernetes）
- 50-100: 知名开源项目
- 20-50: 活跃的中型项目
- 5-20: 有一定影响力的项目
- < 5: 小型或新兴项目
""",
    "bus_factor": """
巴士因子 (Bus Factor) 解读：
巴士因子表示项目中有多少核心贡献者，如果这些人"被巴士撞了"项目就会陷入困境。

健康标准：
- 巴士因子 ≥ 3: 健康，风险较低
- 巴士因子 = 2: 需要关注，应培养更多核心贡献者
- 巴士因子 = 1: 高风险，严重依赖单一贡献者

提升建议：
1. 积极培养新的核心贡献者
2. 完善文档，降低知识门槛
3. 代码审查时让更多人参与
4. 分散维护职责
"""
}


@tool
def search_opensource_knowledge(query: str) -> str:
    """
    在开源运营知识库中搜索相关最佳实践和建议。
    
    Args:
        query: 搜索关键词，如 "如何提升贡献者数量"、"OpenRank 是什么"
        
    Returns:
        相关的知识内容和建议
    """
    query_lower = query.lower()
    
    results = []
    
    # 简单的关键词匹配
    keyword_mapping = {
        "community_health": ["健康", "健康度", "社区健康", "health"],
        "contributor_growth": ["贡献者", "contributor", "增长", "提升", "吸引"],
        "issue_management": ["issue", "问题管理", "issues"],
        "pr_review": ["pr", "pull request", "代码审查", "review", "合并"],
        "openrank_explanation": ["openrank", "影响力", "评分"],
        "bus_factor": ["巴士因子", "bus factor", "核心贡献者", "风险"],
    }
    
    for key, keywords in keyword_mapping.items():
        if any(kw in query_lower for kw in keywords):
            results.append(OPENSOURCE_KNOWLEDGE_BASE[key])
    
    if results:
        return "\n\n---\n\n".join(results)
    else:
        # 返回一般性建议
        return """
没有找到精确匹配的知识，以下是一些通用的开源运营建议：

1. 保持项目活跃：定期发布、及时响应社区反馈
2. 完善文档：让新人更容易上手
3. 建立社区：创建沟通渠道，培养贡献者
4. 透明治理：公开决策过程，建立信任
5. 持续改进：关注指标变化，及时调整策略
"""


@tool
async def ask_maxkb(question: str) -> str:
    """
    向 MaxKB 知识库提问，获取开源运营相关的专业建议。
    
    Args:
        question: 问题内容
        
    Returns:
        来自知识库的回答
    """
    tool_instance = MaxKBTool()
    try:
        # 首先尝试调用 MaxKB
        answer = await tool_instance.ask_question(question)
        
        if answer:
            return answer
        else:
            # 如果 MaxKB 不可用，使用本地知识库
            return search_opensource_knowledge(question)
    finally:
        await tool_instance.close()

