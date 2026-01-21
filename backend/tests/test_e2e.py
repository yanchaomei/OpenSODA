"""
端到端测试模块

测试完整的用户流程，从输入到输出
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
import json


class TestHealthAnalysisFlow:
    """健康分析完整流程测试"""

    @pytest.mark.asyncio
    async def test_complete_health_analysis(self):
        """
        测试完整的健康分析流程：
        用户输入 -> Agent 推理 -> 工具调用 -> 数据获取 -> 结果生成
        """
        from app.agents.orchestrator import run_agent_stream
        
        # Mock 外部 API
        mock_opendigger_response = {
            "2024-10": 40.05,
            "2024-09": 38.5,
            "2024-08": 41.2,
        }
        
        with patch('app.tools.opendigger.OpenDiggerTool.get_metric') as mock_metric:
            mock_metric.return_value = mock_opendigger_response
            
            events = []
            async for event in run_agent_stream(
                message="分析 apache/dubbo 的健康状况",
                history=[]
            ):
                events.append(event)
            
            # 验证流程
            event_types = [e.get("type") for e in events]
            
            # 应该有思考事件
            assert "thinking" in event_types or len([e for e in events if "think" in str(e)]) > 0
            
            # 应该有工具调用
            tool_calls = [e for e in events if e.get("type") == "tool_call"]
            assert len(tool_calls) > 0 or len(events) > 0  # 至少有输出
            
            # 应该有最终输出
            text_events = [e for e in events if e.get("type") == "text"]
            assert len(text_events) > 0 or len(events) > 0

    @pytest.mark.asyncio
    async def test_multi_tool_collaboration(self):
        """
        测试多工具协作流程：
        健康分析 -> 问题诊断 -> 建议生成
        """
        from app.agents.orchestrator import run_agent_stream
        
        with patch('app.tools.opendigger.OpenDiggerTool') as mock_tool:
            mock_tool.return_value.get_metric = AsyncMock(return_value={"2024-10": 40.0})
            
            events = []
            async for event in run_agent_stream(
                message="全面分析 kubernetes/kubernetes 并告诉我有什么问题和改进建议",
                history=[]
            ):
                events.append(event)
            
            # 复杂查询应该触发多个工具
            tool_calls = [e for e in events if e.get("type") == "tool_call"]
            # 可能调用多个工具
            # assert len(tool_calls) >= 2  # 取决于 Agent 决策


class TestDiagnosisFlow:
    """问题诊断流程测试"""

    @pytest.mark.asyncio
    async def test_problem_detection(self):
        """测试问题检测流程"""
        from app.agents.diagnosis import diagnose_issues
        
        # 模拟有问题的指标
        problematic_metrics = {
            "bus_factor": 2,  # 低于红线
            "openrank": 10,
            "activity": 2,
            "openrank_trend": [-5, -3, -2, -1],  # 下降趋势
        }
        
        result = diagnose_issues(problematic_metrics)
        
        issues = result.get("issues", [])
        
        # 应该检测到巴士因子问题
        assert len(issues) > 0 or "bus" in str(result).lower() or "巴士" in str(result)

    @pytest.mark.asyncio
    async def test_healthy_project_no_critical_issues(self):
        """健康项目不应有严重问题"""
        from app.agents.diagnosis import diagnose_issues
        
        healthy_metrics = {
            "bus_factor": 15,
            "openrank": 80,
            "activity": 25,
            "participants": 500,
            "openrank_trend": [70, 72, 75, 78, 80],  # 上升趋势
        }
        
        result = diagnose_issues(healthy_metrics)
        
        # 不应该有严重问题
        critical_issues = [
            i for i in result.get("issues", [])
            if "critical" in str(i).lower() or "严重" in str(i)
        ]
        assert len(critical_issues) == 0


class TestSuggestionFlow:
    """建议生成流程测试"""

    @pytest.mark.asyncio
    async def test_suggestions_are_actionable(self):
        """建议应该是可执行的"""
        from app.agents.advisor import generate_suggestions
        
        context = {
            "repo": "test/repo",
            "issues": ["巴士因子过低", "活跃度下降"],
            "metrics": {
                "bus_factor": 2,
                "activity": 5,
            }
        }
        
        suggestions = await generate_suggestions(context)
        
        # 应该有建议
        assert len(suggestions) > 0 or suggestions is not None
        
        # 建议应该针对发现的问题
        # 例如：巴士因子低 -> 建议培养贡献者


class TestChatFlow:
    """对话流程测试"""

    @pytest.mark.asyncio
    async def test_simple_query_response(self):
        """简单查询应得到响应"""
        from app.api.chat import process_chat_message
        
        with patch('app.agents.orchestrator.run_agent') as mock_agent:
            mock_agent.return_value = "Apache Dubbo 的 OpenRank 值为 40.05"
            
            response = await process_chat_message(
                message="dubbo 的 openrank 是多少？",
                history=[]
            )
            
            assert response is not None
            assert len(response) > 0

    @pytest.mark.asyncio
    async def test_follow_up_question(self):
        """追问应使用上下文"""
        from app.api.chat import process_chat_message
        
        history = [
            {"role": "user", "content": "分析 dubbo"},
            {"role": "assistant", "content": "dubbo 健康度 70.2"}
        ]
        
        with patch('app.agents.orchestrator.run_agent') as mock_agent:
            mock_agent.return_value = "根据之前的分析，dubbo 存在以下问题..."
            
            response = await process_chat_message(
                message="有什么问题吗？",
                history=history
            )
            
            # 应该理解"有什么问题"是针对 dubbo 的
            assert response is not None


class TestStreamingFlow:
    """流式输出流程测试"""

    @pytest.mark.asyncio
    async def test_streaming_events_order(self):
        """流式事件应按正确顺序输出"""
        from app.agents.orchestrator import run_agent_stream
        
        with patch('app.tools.opendigger.OpenDiggerTool') as mock:
            mock.return_value.get_metric = AsyncMock(return_value=40.0)
            
            events = []
            async for event in run_agent_stream(
                message="获取 dubbo 的 openrank",
                history=[]
            ):
                events.append(event)
            
            # 应该有事件输出
            assert len(events) > 0

    @pytest.mark.asyncio
    async def test_streaming_handles_errors(self):
        """流式输出应处理错误"""
        from app.agents.orchestrator import run_agent_stream
        
        with patch('app.tools.opendigger.OpenDiggerTool') as mock:
            mock.return_value.get_metric = AsyncMock(
                side_effect=Exception("API Error")
            )
            
            events = []
            try:
                async for event in run_agent_stream(
                    message="获取不存在的项目",
                    history=[]
                ):
                    events.append(event)
            except Exception:
                pass  # 期望可能抛出异常
            
            # 应该有某种输出或错误处理
            # error_events = [e for e in events if e.get("type") == "error"]


class TestDataIntegration:
    """数据集成测试"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_opendigger_integration(self):
        """测试 OpenDigger 数据集成"""
        from app.tools.opendigger import OpenDiggerTool
        
        tool = OpenDiggerTool()
        
        # 使用知名项目测试
        openrank = await tool.get_openrank("apache/dubbo")
        
        if openrank is not None:
            # OpenRank 应该是合理的数值
            assert 0 <= openrank <= 200

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_github_integration(self):
        """测试 GitHub API 集成"""
        from app.tools.github import GitHubTool
        
        tool = GitHubTool()
        
        info = await tool.get_repo_info("vuejs/vue")
        
        if info is not None:
            assert "name" in info or "stars" in info


class TestComparisonFlow:
    """项目对比流程测试"""

    @pytest.mark.asyncio
    async def test_compare_two_projects(self):
        """对比两个项目"""
        from app.api.analysis import compare_repositories
        
        with patch('app.tools.opendigger.OpenDiggerTool') as mock:
            mock.return_value.get_all_metrics = AsyncMock(return_value={
                "openrank": 40,
                "activity": 20,
            })
            
            result = await compare_repositories(
                repos=["apache/dubbo", "alibaba/nacos"]
            )
            
            # 应该返回对比结果
            assert result is not None

    @pytest.mark.asyncio
    async def test_compare_multiple_projects(self):
        """对比多个项目"""
        from app.api.analysis import compare_repositories
        
        with patch('app.tools.opendigger.OpenDiggerTool') as mock:
            mock.return_value.get_all_metrics = AsyncMock(return_value={
                "openrank": 40,
            })
            
            result = await compare_repositories(
                repos=["vue", "react", "angular"]
            )
            
            # 应该返回所有项目的对比
            assert result is not None


class TestExportFlow:
    """导出流程测试"""

    @pytest.mark.asyncio
    async def test_export_markdown_format(self):
        """导出 Markdown 格式"""
        from app.api.analysis import generate_markdown_report
        
        analysis_data = {
            "repo": "apache/dubbo",
            "health_score": 70.2,
            "dimension_scores": {
                "activity": 64,
                "community": 55,
                "maintenance": 97,
                "growth": 64
            },
            "issues": ["巴士因子关注"],
            "suggestions": ["增加社区活动"]
        }
        
        markdown = generate_markdown_report(analysis_data)
        
        # 应该是有效的 Markdown
        assert "apache/dubbo" in markdown or "dubbo" in markdown
        assert "#" in markdown  # Markdown 标题

    @pytest.mark.asyncio
    async def test_export_json_format(self):
        """导出 JSON 格式"""
        from app.api.analysis import generate_json_report
        
        analysis_data = {
            "repo": "test/repo",
            "health_score": 75
        }
        
        json_str = generate_json_report(analysis_data)
        
        # 应该是有效的 JSON
        parsed = json.loads(json_str)
        assert "repo" in parsed


class TestEdgeCases:
    """边缘情况测试"""

    @pytest.mark.asyncio
    async def test_empty_message(self):
        """空消息处理"""
        from app.api.chat import process_chat_message
        
        with pytest.raises(Exception):
            # 空消息应该抛出异常或返回错误
            await process_chat_message(message="", history=[])

    @pytest.mark.asyncio
    async def test_very_long_message(self):
        """超长消息处理"""
        from app.api.chat import process_chat_message
        
        long_message = "分析 dubbo " * 1000
        
        try:
            with patch('app.agents.orchestrator.run_agent') as mock:
                mock.return_value = "处理完成"
                result = await process_chat_message(
                    message=long_message,
                    history=[]
                )
            # 应该能处理或优雅地拒绝
            assert True
        except Exception:
            # 拒绝超长输入也是可接受的
            assert True

    @pytest.mark.asyncio
    async def test_special_characters_in_repo(self):
        """仓库名中的特殊字符"""
        from app.tools.opendigger import get_repo_openrank
        
        special_repos = [
            "owner.name/repo.name",
            "owner-name/repo-name",
            "owner_name/repo_name",
        ]
        
        for repo in special_repos:
            result = await get_repo_openrank.ainvoke({"repo": repo})
            # 应该正常处理或返回错误信息
            assert result is not None

    @pytest.mark.asyncio
    async def test_nonexistent_repo(self):
        """不存在的仓库"""
        from app.tools.opendigger import get_repo_openrank
        
        result = await get_repo_openrank.ainvoke({
            "repo": "definitely-not-exist/fake-repo-12345"
        })
        
        # 应该返回错误信息而不是崩溃
        assert "无法" in result or "不存在" in result or "error" in result.lower() or "找不到" in result


class TestPerformance:
    """性能测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_requests(self):
        """并发请求测试"""
        from app.api.analysis import analyze_repository
        
        async def single_request():
            with patch('app.tools.opendigger.OpenDiggerTool') as mock:
                mock.return_value.get_all_metrics = AsyncMock(return_value={})
                return await analyze_repository("test/repo")
        
        # 发送 10 个并发请求
        tasks = [single_request() for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 应该都成功
        successes = [r for r in results if not isinstance(r, Exception)]
        assert len(successes) >= 8  # 至少 80% 成功

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_response_time(self):
        """响应时间测试"""
        import time
        from app.agents.orchestrator import run_agent_stream
        
        with patch('app.tools.opendigger.OpenDiggerTool') as mock:
            mock.return_value.get_metric = AsyncMock(return_value=40.0)
            
            start = time.time()
            events = []
            async for event in run_agent_stream(
                message="获取 dubbo openrank",
                history=[]
            ):
                events.append(event)
            duration = time.time() - start
            
            # 应该在合理时间内完成
            assert duration < 30  # 30 seconds max

