"""
数据模型定义
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, TypedDict
from datetime import datetime


class RepoInfo(BaseModel):
    """仓库基本信息"""
    owner: str
    name: str
    full_name: str  # owner/name
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MetricsData(BaseModel):
    """指标数据"""
    openrank: Optional[float] = None
    activity: Optional[float] = None
    attention: Optional[float] = None
    bus_factor: Optional[int] = None
    
    # 时序数据
    openrank_history: Optional[List[float]] = None
    activity_history: Optional[List[float]] = None
    stars_history: Optional[List[int]] = None
    
    # 贡献者相关
    contributors_count: Optional[int] = None
    new_contributors: Optional[int] = None
    
    # Issue/PR相关
    issue_response_time: Optional[float] = None  # 小时
    pr_merge_time: Optional[float] = None  # 小时
    
    # 原始数据
    raw_data: Optional[Dict[str, Any]] = None


class HealthScore(BaseModel):
    """健康度评分"""
    overall: float  # 总体评分 0-100
    activity: float  # 活跃度
    community: float  # 社区健康度
    maintenance: float  # 维护响应度
    growth: float  # 增长趋势
    
    # 评分解释
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None
    concerns: Optional[List[str]] = None


class DiagnosisResult(BaseModel):
    """诊断结果"""
    issues: List[str]  # 发现的问题
    risks: List[str]  # 潜在风险
    severity: str  # low, medium, high
    details: Optional[Dict[str, Any]] = None


class Recommendation(BaseModel):
    """建议"""
    category: str  # community, code, process, etc.
    title: str
    description: str
    priority: str  # low, medium, high
    actions: List[str]  # 具体行动项
    reference: Optional[str] = None  # 参考链接


class ChatMessage(TypedDict):
    """聊天消息"""
    role: str
    content: str


class AgentState(TypedDict):
    """Agent状态 - 用于LangGraph"""
    messages: List[ChatMessage]
    repo: Optional[str]
    repo_info: Optional[Dict[str, Any]]
    metrics: Optional[Dict[str, Any]]
    health_score: Optional[Dict[str, Any]]
    diagnosis: Optional[Dict[str, Any]]
    recommendations: Optional[List[Dict[str, Any]]]
    charts: Optional[List[Dict[str, Any]]]
    current_step: str
    error: Optional[str]

