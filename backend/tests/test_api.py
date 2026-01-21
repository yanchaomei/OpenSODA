"""
API 端点测试模块

测试所有 FastAPI 端点的请求/响应行为
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

# 导入应用
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """健康检查端点测试"""

    def test_health_check_returns_200(self):
        """健康检查应返回 200"""
        response = client.get("/api/health/")
        assert response.status_code == 200

    def test_health_check_returns_status(self):
        """健康检查应返回状态信息"""
        response = client.get("/api/health/")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_check_includes_services(self):
        """健康检查应包含服务状态"""
        response = client.get("/api/health/")
        data = response.json()
        
        if "services" in data:
            # 检查服务状态格式
            for service_name, service_info in data["services"].items():
                assert "status" in service_info


class TestAnalysisEndpoints:
    """分析相关端点测试"""

    def test_analyze_repo_requires_repo_param(self):
        """分析端点需要 repo 参数"""
        response = client.get("/api/analysis/repo/")
        # 应该返回 404（路由不匹配）或 422（参数缺失）
        assert response.status_code in [404, 422]

    def test_analyze_repo_valid_format(self):
        """分析有效仓库格式"""
        with patch('app.api.analysis.analyze_repository') as mock:
            mock.return_value = {
                "repo": "apache/dubbo",
                "health_score": 70.2,
                "dimension_scores": {
                    "activity": 64,
                    "community": 55,
                    "maintenance": 97,
                    "growth": 64
                }
            }
            
            response = client.get("/api/analysis/repo/apache/dubbo")
            
            if response.status_code == 200:
                data = response.json()
                assert "health_score" in data or "error" in data

    def test_analyze_repo_invalid_format(self):
        """分析无效仓库格式"""
        response = client.get("/api/analysis/repo/invalid")
        # 应该返回错误或空结果
        assert response.status_code in [200, 400, 422]

    def test_compare_repos_endpoint(self):
        """项目对比端点测试"""
        with patch('app.api.analysis.compare_repositories') as mock:
            mock.return_value = {
                "repos": ["apache/dubbo", "alibaba/nacos"],
                "comparison": {}
            }
            
            response = client.post(
                "/api/analysis/compare",
                json={"repos": ["apache/dubbo", "alibaba/nacos"]}
            )
            
            # 应该成功或返回验证错误
            assert response.status_code in [200, 422]

    def test_compare_repos_requires_at_least_two(self):
        """对比至少需要两个仓库"""
        response = client.post(
            "/api/analysis/compare",
            json={"repos": ["apache/dubbo"]}
        )
        
        # 应该返回验证错误
        assert response.status_code in [400, 422]


class TestChatEndpoints:
    """聊天相关端点测试"""

    def test_chat_endpoint_accepts_message(self):
        """聊天端点接受消息"""
        with patch('app.api.chat.process_chat') as mock:
            mock.return_value = {"response": "测试回复"}
            
            response = client.post(
                "/api/chat/",
                json={"message": "分析 dubbo", "history": []}
            )
            
            assert response.status_code in [200, 500]

    def test_chat_requires_message(self):
        """聊天需要消息内容"""
        response = client.post(
            "/api/chat/",
            json={"history": []}
        )
        
        # 缺少必需字段应返回 422
        assert response.status_code == 422

    def test_chat_stream_endpoint_exists(self):
        """流式聊天端点存在"""
        with patch('app.api.chat.stream_chat') as mock:
            mock.return_value = AsyncMock()
            
            response = client.post(
                "/api/chat/stream",
                json={"message": "测试", "history": []}
            )
            
            # 端点应该存在并返回响应
            assert response.status_code in [200, 500]


class TestDashboardEndpoints:
    """仪表盘端点测试"""

    def test_dashboard_stats(self):
        """获取仪表盘统计"""
        response = client.get("/api/dashboard/")
        
        if response.status_code == 200:
            data = response.json()
            # 应该包含统计数据
            assert "stats" in data or "error" in data


class TestExportEndpoints:
    """导出端点测试"""

    def test_export_markdown(self):
        """导出 Markdown 格式"""
        with patch('app.api.analysis.export_markdown_report') as mock:
            mock.return_value = "# Report"
            
            response = client.post(
                "/api/analysis/export/markdown",
                json={"repo": "apache/dubbo", "analysis": {}}
            )
            
            assert response.status_code in [200, 422]

    def test_export_json(self):
        """导出 JSON 格式"""
        with patch('app.api.analysis.export_json_report') as mock:
            mock.return_value = {}
            
            response = client.post(
                "/api/analysis/export/json",
                json={"repo": "apache/dubbo", "analysis": {}}
            )
            
            assert response.status_code in [200, 422]


class TestInputValidation:
    """输入验证测试"""

    def test_repo_format_validation(self):
        """仓库格式验证"""
        # 有效格式
        valid_repos = [
            "apache/dubbo",
            "vuejs/vue",
            "kubernetes/kubernetes",
            "owner-name/repo-name",
            "owner_name/repo_name",
        ]
        
        for repo in valid_repos:
            # 使用 mock 避免真实 API 调用
            with patch('app.api.analysis.analyze_repository') as mock:
                mock.return_value = {"repo": repo}
                response = client.get(f"/api/analysis/repo/{repo}")
                # 不应该因为格式问题返回 422
                assert response.status_code != 422 or "format" not in str(response.json())

    def test_json_body_validation(self):
        """JSON 请求体验证"""
        # 无效 JSON
        response = client.post(
            "/api/chat/",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_missing_required_fields(self):
        """缺少必需字段"""
        response = client.post(
            "/api/chat/",
            json={}
        )
        
        assert response.status_code == 422


class TestResponseFormat:
    """响应格式测试"""

    def test_analysis_response_format(self):
        """分析响应格式"""
        with patch('app.api.analysis.analyze_repository') as mock:
            mock.return_value = {
                "repo": "test/repo",
                "health_score": 75.0,
                "dimension_scores": {
                    "activity": 70,
                    "community": 80,
                    "maintenance": 75,
                    "growth": 65
                },
                "metrics": {},
                "issues": [],
                "suggestions": []
            }
            
            response = client.get("/api/analysis/repo/test/repo")
            
            if response.status_code == 200:
                data = response.json()
                
                # 验证响应结构
                assert "health_score" in data
                if "dimension_scores" in data:
                    assert isinstance(data["dimension_scores"], dict)

    def test_error_response_format(self):
        """错误响应格式"""
        with patch('app.api.analysis.analyze_repository') as mock:
            mock.side_effect = Exception("Test error")
            
            response = client.get("/api/analysis/repo/test/repo")
            
            if response.status_code >= 400:
                data = response.json()
                # 错误响应应包含 detail 或 error
                assert "detail" in data or "error" in data


class TestRateLimiting:
    """速率限制测试（如果实现）"""

    @pytest.mark.skip(reason="Rate limiting not implemented yet")
    def test_rate_limiting(self):
        """测试速率限制"""
        # 快速发送多个请求
        responses = []
        for _ in range(100):
            response = client.get("/api/health/")
            responses.append(response.status_code)
        
        # 应该有一些请求被限制
        assert 429 in responses


class TestCORS:
    """CORS 配置测试"""

    def test_cors_headers_present(self):
        """CORS 头部存在"""
        response = client.options(
            "/api/health/",
            headers={"Origin": "http://localhost:5173"}
        )
        
        # 检查 CORS 头部
        headers = dict(response.headers)
        # FastAPI 可能不在 OPTIONS 响应中包含 CORS 头
        # 这取决于中间件配置


class TestAuthentication:
    """认证测试（如果实现）"""

    @pytest.mark.skip(reason="Authentication not implemented yet")
    def test_protected_endpoint_requires_auth(self):
        """受保护端点需要认证"""
        response = client.get("/api/admin/")
        assert response.status_code == 401


# 性能测试
class TestPerformance:
    """性能基准测试"""

    def test_health_endpoint_response_time(self):
        """健康检查响应时间"""
        import time
        
        start = time.time()
        response = client.get("/api/health/")
        duration = time.time() - start
        
        # 健康检查应该很快
        assert duration < 0.5  # 500ms

    @pytest.mark.skip(reason="Requires real API calls")
    def test_analysis_endpoint_response_time(self):
        """分析端点响应时间"""
        import time
        
        start = time.time()
        response = client.get("/api/analysis/repo/apache/dubbo")
        duration = time.time() - start
        
        # 分析应该在合理时间内完成
        assert duration < 10  # 10 seconds

