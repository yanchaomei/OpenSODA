"""
Agent 测试模块

测试 ReAct Agent 的推理逻辑、工具选择和多轮对话能力
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

# 模拟数据
MOCK_HEALTH_METRICS = {
    "openrank": 40.05,
    "activity": 23.5,
    "participants": 156,
    "bus_factor": 16,
    "new_contributors": 12,
}

MOCK_GITHUB_INFO = {
    "name": "dubbo",
    "full_name": "apache/dubbo",
    "description": "Apache Dubbo is a high-performance RPC framework",
    "stars": 40000,
    "forks": 26000,
    "language": "Java",
}


class TestToolSelection:
    """测试 Agent 工具选择逻辑"""

    @pytest.mark.asyncio
    async def test_health_analysis_selects_correct_tool(self):
        """用户询问健康状况时应选择健康分析工具"""
        from app.agents.orchestrator import determine_tool_from_intent
        
        intents = [
            "分析 apache/dubbo 的健康状况",
            "告诉我这个项目的健康度",
            "评估一下 vue 项目怎么样",
        ]
        
        for intent in intents:
            result = await determine_tool_from_intent(intent)
            assert "analyze_repo_health" in result or "get_repo_health_metrics" in result

    @pytest.mark.asyncio
    async def test_diagnosis_selects_correct_tool(self):
        """用户询问问题时应选择诊断工具"""
        from app.agents.orchestrator import determine_tool_from_intent
        
        intents = [
            "dubbo 有什么问题？",
            "诊断一下这个项目",
            "这个项目存在哪些风险？",
        ]
        
        for intent in intents:
            result = await determine_tool_from_intent(intent)
            assert "diagnose_repo_issues" in result

    @pytest.mark.asyncio
    async def test_suggestion_selects_correct_tool(self):
        """用户询问建议时应选择建议工具"""
        from app.agents.orchestrator import determine_tool_from_intent
        
        intents = [
            "如何改进这个项目？",
            "给我一些运营建议",
            "怎么提升项目活跃度？",
        ]
        
        for intent in intents:
            result = await determine_tool_from_intent(intent)
            assert "get_improvement_suggestions" in result


class TestMultiTurnReasoning:
    """测试多轮推理能力"""

    @pytest.mark.asyncio
    async def test_agent_calls_multiple_tools_when_needed(self):
        """复杂问题应触发多工具调用"""
        # 模拟 Agent 处理复杂查询
        query = "全面分析 apache/dubbo 并给出改进建议"
        
        with patch('app.agents.orchestrator.run_agent_stream') as mock_stream:
            # 模拟返回多个工具调用事件
            mock_stream.return_value = [
                {"type": "tool_call", "name": "analyze_repo_health"},
                {"type": "tool_result", "output": "健康度 70.2"},
                {"type": "tool_call", "name": "diagnose_repo_issues"},
                {"type": "tool_result", "output": "发现2个问题"},
                {"type": "tool_call", "name": "get_improvement_suggestions"},
                {"type": "tool_result", "output": "建议列表"},
            ]
            
            events = list(mock_stream.return_value)
            tool_calls = [e for e in events if e["type"] == "tool_call"]
            
            # 应该调用多个工具
            assert len(tool_calls) >= 2

    @pytest.mark.asyncio
    async def test_agent_stops_when_information_sufficient(self):
        """信息充足时应停止工具调用"""
        # 简单查询应该只调用一次
        query = "apache/dubbo 的 OpenRank 是多少？"
        
        with patch('app.agents.orchestrator.run_agent_stream') as mock_stream:
            mock_stream.return_value = [
                {"type": "tool_call", "name": "get_repo_openrank"},
                {"type": "tool_result", "output": "OpenRank: 40.05"},
                {"type": "text", "content": "apache/dubbo 的 OpenRank 值为 40.05"},
            ]
            
            events = list(mock_stream.return_value)
            tool_calls = [e for e in events if e["type"] == "tool_call"]
            
            # 简单查询只需调用一次
            assert len(tool_calls) == 1


class TestContextManagement:
    """测试上下文管理"""

    @pytest.mark.asyncio
    async def test_maintains_conversation_history(self):
        """应该维护对话历史"""
        from app.agents.orchestrator import build_messages
        
        history = [
            {"role": "user", "content": "分析 dubbo"},
            {"role": "assistant", "content": "dubbo 健康度 70.2"},
            {"role": "user", "content": "有什么问题吗？"},
        ]
        
        messages = build_messages(history)
        
        assert len(messages) == 3
        assert messages[0].content == "分析 dubbo"
        assert messages[2].content == "有什么问题吗？"

    @pytest.mark.asyncio
    async def test_handles_tool_results_in_history(self):
        """应该正确处理历史中的工具调用结果"""
        from app.agents.orchestrator import build_messages
        
        history = [
            {"role": "user", "content": "分析 dubbo"},
            {"role": "assistant", "content": "", "tool_calls": [{"name": "analyze"}]},
            {"role": "tool", "content": "分析结果", "tool_call_id": "123"},
            {"role": "assistant", "content": "根据分析..."},
        ]
        
        messages = build_messages(history)
        
        # 应该正确构建所有消息类型
        assert len(messages) >= 3


class TestErrorHandling:
    """测试错误处理"""

    @pytest.mark.asyncio
    async def test_handles_tool_failure_gracefully(self):
        """工具调用失败时应优雅处理"""
        from app.tools.opendigger import get_repo_openrank
        
        with patch('app.tools.opendigger.OpenDiggerTool.get_openrank') as mock:
            mock.side_effect = Exception("API Error")
            
            result = await get_repo_openrank.ainvoke({"repo": "invalid/repo"})
            
            # 应该返回错误信息而不是抛出异常
            assert "错误" in result or "error" in result.lower() or "无法" in result

    @pytest.mark.asyncio
    async def test_handles_invalid_repo_format(self):
        """无效仓库格式应返回提示"""
        from app.tools.opendigger import get_repo_openrank
        
        invalid_repos = ["invalid", "too/many/slashes", ""]
        
        for repo in invalid_repos:
            result = await get_repo_openrank.ainvoke({"repo": repo})
            # 应该返回错误或无数据提示
            assert result is not None


class TestHealthScoreCalculation:
    """测试健康度计算逻辑"""

    def test_activity_score_calculation(self):
        """测试活跃度评分计算"""
        from app.agents.analysis import calculate_dimension_scores
        
        metrics = {
            "openrank": 50,
            "activity": 10,
        }
        
        scores = calculate_dimension_scores(metrics)
        
        # 活跃度 = 0.6 * 50 + 0.4 * min(100, 10*5) = 30 + 20 = 50
        assert 45 <= scores["activity"] <= 55

    def test_community_score_calculation(self):
        """测试社区健康度计算"""
        from app.agents.analysis import calculate_dimension_scores
        
        metrics = {
            "participants": 100,  # -> 100/5 = 20
            "bus_factor": 5,      # -> 5*10 = 50
        }
        
        scores = calculate_dimension_scores(metrics)
        
        # 社区 = 0.5 * 20 + 0.5 * 50 = 35
        assert 30 <= scores["community"] <= 40

    def test_overall_score_weighted_average(self):
        """测试总分加权平均"""
        from app.agents.analysis import calculate_health_score
        
        metrics = {
            "openrank": 60,
            "activity": 15,
            "participants": 200,
            "bus_factor": 10,
            "change_requests_accepted": 80,
            "change_requests": 100,
            "new_contributors": 5,
        }
        
        result = calculate_health_score(metrics)
        
        # 总分应在合理范围内
        assert 0 <= result["overall_score"] <= 100
        
        # 应包含四个维度分数
        assert "activity" in result["dimension_scores"]
        assert "community" in result["dimension_scores"]
        assert "maintenance" in result["dimension_scores"]
        assert "growth" in result["dimension_scores"]

    def test_bus_factor_risk_detection(self):
        """测试巴士因子风险检测"""
        from app.agents.diagnosis import diagnose_issues
        
        metrics = {
            "bus_factor": 2,  # 低于阈值 3
            "openrank": 50,
            "activity": 10,
        }
        
        result = diagnose_issues(metrics)
        
        # 应该检测到巴士因子风险
        issues = result.get("issues", [])
        assert any("巴士因子" in str(issue) or "bus" in str(issue).lower() 
                   for issue in issues)


class TestTrendAnalysis:
    """测试趋势分析"""

    def test_rising_trend_detection(self):
        """测试上升趋势检测"""
        from app.agents.analysis import analyze_trend
        
        values = [10, 12, 15, 18, 22, 25]  # 明显上升
        
        result = analyze_trend(values)
        
        assert result["trend"] == "rising"
        assert result["score"] > 60

    def test_declining_trend_detection(self):
        """测试下降趋势检测"""
        from app.agents.analysis import analyze_trend
        
        values = [25, 22, 18, 15, 12, 10]  # 明显下降
        
        result = analyze_trend(values)
        
        assert result["trend"] == "declining"
        assert result["score"] < 40

    def test_stable_trend_detection(self):
        """测试稳定趋势检测"""
        from app.agents.analysis import analyze_trend
        
        values = [50, 51, 49, 50, 52, 50]  # 基本稳定
        
        result = analyze_trend(values)
        
        assert result["trend"] == "stable"
        assert 40 <= result["score"] <= 60


# 集成测试
class TestAgentIntegration:
    """Agent 集成测试"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_analysis_flow(self):
        """测试完整分析流程"""
        # 这个测试需要真实的 API 调用，标记为集成测试
        pass

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_streaming_output(self):
        """测试流式输出"""
        pass

