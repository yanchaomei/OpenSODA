"""
Orchestrator Agent - 主控 Agent (ReAct 模式)

使用 ReAct (Reasoning + Acting) 模式，让 Agent 具备：
1. 思考（Thought）- 分析用户需求
2. 行动（Action）- 调用工具获取信息
3. 观察（Observation）- 处理工具返回结果
4. 循环直到能够回答用户问题
"""
from typing import Dict, Any, List, Optional, AsyncGenerator, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, START, MessagesState
from langgraph.prebuilt import ToolNode
import json

from app.core.config import settings
from app.tools.opendigger import (
    OpenDiggerTool,
    get_repo_openrank,
    get_repo_health_metrics,
    get_repo_contributors_info,
    get_repo_activity_trend
)
from app.tools.github import (
    GitHubTool,
    get_github_repo_info,
    get_github_contributors,
    find_good_first_issues
)
from app.tools.maxkb import search_opensource_knowledge


# ============= 定义 Agent 工具 =============

@tool
async def analyze_repo_health(repo: str) -> str:
    """
    全面分析开源仓库的健康状况，包括 OpenRank、活跃度、贡献者等多维度指标。
    这是分析项目的主要入口工具。
    
    Args:
        repo: 仓库路径，格式为 "owner/repo"，例如 "apache/dubbo"
        
    Returns:
        仓库的健康度分析报告
    """
    from app.agents.analysis import run_analysis
    
    try:
        result = await run_analysis(repo)
        
        health = result.get("health_score", {})
        metrics = result.get("metrics", {})
        
        report = f"""
## 📊 {repo} 健康度分析报告

### 综合评分: {health.get('overall', 'N/A')}/100

| 维度 | 评分 |
|------|------|
| 🔥 活跃度 | {health.get('activity', 'N/A')} |
| 👥 社区健康 | {health.get('community', 'N/A')} |
| 🔧 维护响应 | {health.get('maintenance', 'N/A')} |
| 📈 增长趋势 | {health.get('growth', 'N/A')} |

### 关键指标
- **OpenRank**: {metrics.get('openrank', 'N/A')}
- **活跃度**: {metrics.get('activity', 'N/A')}
- **参与者数**: {metrics.get('total_participants', 'N/A')}
- **巴士因子**: {metrics.get('bus_factor', 'N/A')}

### 评估摘要
{health.get('summary', '暂无摘要')}
"""
        
        if health.get('highlights'):
            report += "\n### ✅ 亮点\n"
            for h in health['highlights']:
                report += f"- {h}\n"
        
        if health.get('concerns'):
            report += "\n### ⚠️ 需关注\n"
            for c in health['concerns']:
                report += f"- {c}\n"
        
        return report
    except Exception as e:
        return f"分析仓库 {repo} 时出错: {str(e)}"


@tool
async def diagnose_repo_issues(repo: str) -> str:
    """
    诊断开源仓库存在的问题和潜在风险。
    在分析健康度后使用此工具获取详细的问题诊断。
    
    Args:
        repo: 仓库路径，格式为 "owner/repo"
        
    Returns:
        问题诊断报告
    """
    from app.agents.analysis import run_analysis
    from app.agents.diagnosis import run_diagnosis
    
    try:
        analysis = await run_analysis(repo)
        diagnosis = await run_diagnosis(
            analysis.get("metrics", {}),
            analysis.get("health_score", {})
        )
        
        severity_emoji = {
            "high": "🔴",
            "medium": "🟡", 
            "low": "🟢"
        }
        
        report = f"""
## 🔍 {repo} 问题诊断报告

**严重程度**: {severity_emoji.get(diagnosis.get('severity', 'low'), '⚪')} {diagnosis.get('severity', 'unknown').upper()}

### 发现的问题
"""
        for issue in diagnosis.get('issues', []):
            report += f"- ❌ {issue}\n"
        
        if not diagnosis.get('issues'):
            report += "- ✅ 暂未发现明显问题\n"
        
        report += "\n### 潜在风险\n"
        for risk in diagnosis.get('risks', []):
            report += f"- ⚠️ {risk}\n"
        
        if not diagnosis.get('risks'):
            report += "- ✅ 暂未发现潜在风险\n"
        
        return report
    except Exception as e:
        return f"诊断仓库 {repo} 时出错: {str(e)}"


@tool
async def get_improvement_suggestions(repo: str) -> str:
    """
    获取针对开源仓库的改进建议。
    基于诊断结果提供可执行的优化建议。
    
    Args:
        repo: 仓库路径，格式为 "owner/repo"
        
    Returns:
        改进建议列表
    """
    from app.agents.analysis import run_analysis
    from app.agents.diagnosis import run_diagnosis
    from app.agents.advisor import run_advisor
    
    try:
        analysis = await run_analysis(repo)
        diagnosis = await run_diagnosis(
            analysis.get("metrics", {}),
            analysis.get("health_score", {})
        )
        advice = await run_advisor(diagnosis, analysis.get("metrics", {}))
        
        report = f"## 💡 {repo} 改进建议\n\n"
        
        for rec in advice.get('recommendations', []):
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            report += f"### {priority_emoji.get(rec.get('priority', 'low'), '⚪')} {rec.get('title', '建议')}\n"
            report += f"{rec.get('description', '')}\n\n"
            
            if rec.get('actions'):
                report += "**具体行动:**\n"
                for action in rec['actions']:
                    report += f"- {action}\n"
            report += "\n"
        
        return report if advice.get('recommendations') else f"仓库 {repo} 目前状况良好，暂无特别建议。"
    except Exception as e:
        return f"获取建议时出错: {str(e)}"


@tool
def compare_repos(repos: str) -> str:
    """
    对比多个开源仓库的健康度指标。
    
    Args:
        repos: 用逗号分隔的仓库列表，如 "apache/dubbo,vuejs/vue,facebook/react"
        
    Returns:
        对比分析结果
    """
    # 这是一个同步工具的示例，实际实现需要异步
    return f"将对比以下仓库: {repos}（功能开发中）"


# ============= Agent 配置 =============

# 所有可用工具
AGENT_TOOLS = [
    analyze_repo_health,
    diagnose_repo_issues,
    get_improvement_suggestions,
    get_repo_openrank,
    get_repo_health_metrics,
    get_repo_contributors_info,
    get_repo_activity_trend,
    get_github_repo_info,
    get_github_contributors,
    find_good_first_issues,
    search_opensource_knowledge,
]


SYSTEM_PROMPT = """你是 OpenSource Copilot，一个专业的开源社区智能运营助手。

## 你的能力
你可以使用以下工具来帮助用户：

1. **analyze_repo_health** - 全面分析仓库健康度（推荐首选）
2. **diagnose_repo_issues** - 诊断仓库存在的问题
3. **get_improvement_suggestions** - 获取改进建议
4. **get_repo_openrank** - 获取 OpenRank 值
5. **get_repo_health_metrics** - 获取健康度指标
6. **get_repo_contributors_info** - 获取贡献者信息
7. **get_repo_activity_trend** - 获取活跃度趋势
8. **get_github_repo_info** - 获取 GitHub 仓库基本信息
9. **get_github_contributors** - 获取贡献者列表
10. **find_good_first_issues** - 查找适合新手的 Issue
11. **search_opensource_knowledge** - 搜索开源运营知识库

## 工作流程
1. 理解用户需求
2. 选择合适的工具获取信息
3. 分析工具返回的数据
4. 给出专业、有价值的回答

## 回答要求
- 使用中文回答
- 回答要专业但友好
- 提供具体的数据支撑
- 给出可执行的建议

当用户提到仓库时，优先使用 analyze_repo_health 获取全面分析，然后根据需要使用其他工具补充信息。
"""


def create_agent():
    """创建 ReAct Agent"""
    
    # 创建 LLM
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=0.7,
    )
    
    # 绑定工具
    llm_with_tools = llm.bind_tools(AGENT_TOOLS)
    
    return llm_with_tools


def should_continue(state: MessagesState) -> Literal["tools", "end"]:
    """判断是否继续调用工具"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # 如果有工具调用，继续执行工具
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # 否则结束
    return "end"


async def call_model(state: MessagesState) -> Dict[str, Any]:
    """调用模型"""
    messages = state["messages"]
    
    # 添加系统提示
    full_messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    llm = create_agent()
    response = await llm.ainvoke(full_messages)
    
    return {"messages": [response]}


def build_agent_graph():
    """构建 Agent 图"""
    
    # 创建工具节点
    tool_node = ToolNode(AGENT_TOOLS)
    
    # 创建图
    workflow = StateGraph(MessagesState)
    
    # 添加节点
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    
    # 添加边
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()


# 全局 Agent 图
_agent_graph = None


def get_agent_graph():
    """获取 Agent 图"""
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = build_agent_graph()
    return _agent_graph


async def run_agent(
    message: str,
    repo: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    运行 Agent
    """
    graph = get_agent_graph()
    
    # 构建消息
    messages = []
    if history:
        for h in history:
            if h.get("role") == "user":
                messages.append(HumanMessage(content=h["content"]))
            elif h.get("role") == "assistant":
                messages.append(AIMessage(content=h["content"]))
    
    # 如果指定了仓库，在消息中添加上下文
    if repo and repo not in message:
        message = f"[当前分析仓库: {repo}]\n\n{message}"
    
    messages.append(HumanMessage(content=message))
    
    # 运行
    result = await graph.ainvoke({"messages": messages})
    
    # 提取最终响应
    final_message = result["messages"][-1]
    
    return {
        "response": final_message.content,
        "messages": result["messages"]
    }


async def run_agent_stream(
    message: str,
    repo: Optional[str] = None,
    history: Optional[List] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    流式运行 Agent，实时返回思考和行动过程
    """
    graph = get_agent_graph()
    
    # 构建消息
    messages = []
    if history:
        for h in history:
            # 支持 dict 和 Pydantic model 两种格式
            role = h.get("role") if isinstance(h, dict) else getattr(h, "role", None)
            content = h.get("content", "") if isinstance(h, dict) else getattr(h, "content", "")
            
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
    
    if repo and repo not in message:
        message = f"[当前分析仓库: {repo}]\n\n{message}"
    
    messages.append(HumanMessage(content=message))
    
    yield {"type": "status", "step": "thinking", "message": "🤔 正在思考..."}
    
    # 工具名称映射
    tool_names_cn = {
        "analyze_repo_health": "📊 分析仓库健康度",
        "diagnose_repo_issues": "🔍 诊断问题",
        "get_improvement_suggestions": "💡 获取建议",
        "get_repo_openrank": "📈 获取 OpenRank",
        "get_repo_health_metrics": "📊 获取健康指标",
        "get_repo_contributors_info": "👥 获取贡献者信息",
        "get_repo_activity_trend": "📉 获取活跃度趋势",
        "get_github_repo_info": "🔗 获取 GitHub 信息",
        "get_github_contributors": "👥 获取贡献者列表",
        "find_good_first_issues": "🎯 查找新手 Issue",
        "search_opensource_knowledge": "📚 搜索知识库",
    }
    
    # 收集工具调用结果
    tool_results = []
    final_text = ""
    
    try:
        # 流式执行
        async for event in graph.astream_events({"messages": messages}, version="v2"):
            kind = event["event"]
            
            if kind == "on_chat_model_start":
                yield {"type": "status", "step": "reasoning", "message": "💭 正在推理..."}
            
            elif kind == "on_chat_model_stream":
                # 流式输出文本
                chunk = event["data"].get("chunk")
                if chunk:
                    content = None
                    # 尝试多种方式获取内容
                    if hasattr(chunk, "content") and chunk.content:
                        content = chunk.content
                    elif isinstance(chunk, dict) and chunk.get("content"):
                        content = chunk["content"]
                    elif hasattr(chunk, "text") and chunk.text:
                        content = chunk.text
                    
                    if content:
                        final_text += content
                        yield {"type": "text", "content": content}
            
            elif kind == "on_chat_model_end":
                # 模型调用结束，获取最终输出
                output = event["data"].get("output")
                if output and hasattr(output, "content") and output.content and not final_text:
                    final_text = output.content
                    yield {"type": "text", "content": output.content}
            
            elif kind == "on_tool_start":
                tool_name = event["name"]
                tool_input = event["data"].get("input", {})
                display_name = tool_names_cn.get(tool_name, tool_name)
                
                yield {
                    "type": "tool_start",
                    "tool": tool_name,
                    "tool_display": display_name,
                    "input": tool_input,
                    "message": f"🔧 正在调用工具: {display_name}"
                }
            
            elif kind == "on_tool_end":
                tool_name = event["name"]
                output = event["data"].get("output", "")
                output_str = str(output)
                
                # 提取工具返回的内容
                if hasattr(output, 'content'):
                    output_str = output.content
                
                tool_results.append({
                    "tool": tool_name,
                    "output": output_str
                })
                
                yield {
                    "type": "tool_end",
                    "tool": tool_name,
                    "output": output_str[:500] + "..." if len(output_str) > 500 else output_str,
                    "message": f"✅ 工具调用完成"
                }
            
            elif kind == "on_chain_end":
                # 检查最终输出
                output = event["data"].get("output", {})
                if isinstance(output, dict) and "messages" in output:
                    last_msg = output["messages"][-1] if output["messages"] else None
                    if last_msg and hasattr(last_msg, "content") and last_msg.content and not final_text:
                        final_text = last_msg.content
                        yield {"type": "text", "content": last_msg.content}
        
        # 如果有工具调用结果但没有生成文本，直接返回工具结果
        if tool_results and not final_text.strip():
            # 找最详细的工具输出作为回复
            for result in tool_results:
                if "健康度分析报告" in result["output"] or "诊断报告" in result["output"]:
                    yield {"type": "text", "content": result["output"]}
                    final_text = result["output"]
                    break
            else:
                # 否则组合所有结果
                combined = "\n\n".join([r["output"] for r in tool_results])
                yield {"type": "text", "content": combined}
                final_text = combined
        
        # 如果完全没有输出，返回默认消息
        if not final_text.strip() and not tool_results:
            yield {"type": "text", "content": "你好！我是 OpenSource Copilot，一个开源社区智能运营助手。请告诉我你想分析哪个开源项目，例如：\"分析 apache/dubbo 的健康状况\""}
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Agent stream error: {error_detail}")
        yield {"type": "error", "message": f"处理时发生错误: {str(e)}"}
        yield {"type": "text", "content": f"抱歉，处理您的请求时发生了错误：{str(e)}\n\n请尝试重新提问，例如：\"分析 apache/dubbo\""}
    
    yield {"type": "status", "step": "complete", "message": "✨ 处理完成"}
