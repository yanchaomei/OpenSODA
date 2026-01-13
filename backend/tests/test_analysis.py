"""
Analysis API 测试用例

测试健康度评估算法和 API 接口
"""
import pytest
from fastapi.testclient import TestClient
from app.api.analysis import calculate_health_score, HealthScore


class TestHealthScoreCalculation:
    """健康度评分计算测试"""
    
    def test_calculate_health_score_basic(self):
        """测试基本健康度计算"""
        metrics = {
            "openrank": 50.0,
            "activity": 15.0,
            "attention": 100.0,
            "participants": 50,
            "bus_factor": 10,
            "new_contributors": 5,
            "stars": 1000
        }
        
        score = calculate_health_score(metrics)
        
        assert isinstance(score, HealthScore)
        assert 0 <= score.overall <= 100
        assert 0 <= score.activity <= 100
        assert 0 <= score.community <= 100
        assert 0 <= score.maintenance <= 100
        assert 0 <= score.growth <= 100
    
    def test_calculate_health_score_empty_metrics(self):
        """测试空指标处理"""
        metrics = {}
        
        score = calculate_health_score(metrics)
        
        # 应该返回默认值而不是崩溃
        assert isinstance(score, HealthScore)
        assert score.overall >= 0
    
    def test_calculate_health_score_partial_metrics(self):
        """测试部分指标处理"""
        metrics = {
            "openrank": 30.0,
            # 其他指标缺失
        }
        
        score = calculate_health_score(metrics)
        
        assert isinstance(score, HealthScore)
        assert score.activity > 0  # OpenRank 应该贡献活跃度分数
    
    def test_calculate_health_score_with_trends(self):
        """测试带趋势数据的计算"""
        metrics = {
            "openrank": 40.0,
            "activity": 10.0,
            "participants": 30,
            "bus_factor": 5
        }
        trends = {
            "openrank": [35.0, 36.0, 38.0, 40.0]  # 上升趋势
        }
        
        score = calculate_health_score(metrics, trends)
        
        assert score.growth >= 60  # 上升趋势应该提高增长分数
    
    def test_calculate_health_score_declining_trend(self):
        """测试下降趋势"""
        metrics = {
            "openrank": 30.0,
            "activity": 8.0,
            "participants": 20,
            "bus_factor": 3
        }
        trends = {
            "openrank": [45.0, 42.0, 38.0, 30.0]  # 下降趋势
        }
        
        score = calculate_health_score(metrics, trends)
        
        # 下降趋势应该降低增长分数
        assert score.growth < 70
    
    def test_calculate_health_score_high_openrank(self):
        """测试高 OpenRank 项目"""
        metrics = {
            "openrank": 100.0,
            "activity": 30.0,
            "attention": 500.0,
            "participants": 200,
            "bus_factor": 20,
            "new_contributors": 20,
            "stars": 50000
        }
        
        score = calculate_health_score(metrics)
        
        assert score.overall >= 70  # 高质量项目应该有较高总分
        assert score.activity >= 80
    
    def test_health_score_summary_generation(self):
        """测试评估摘要生成"""
        metrics = {
            "openrank": 80.0,
            "activity": 25.0,
            "participants": 100,
            "bus_factor": 15
        }
        
        score = calculate_health_score(metrics)
        
        assert score.summary is not None
        assert len(score.summary) > 0
    
    def test_health_score_highlights_and_concerns(self):
        """测试亮点和关注点生成"""
        # 高质量项目应该有亮点
        high_quality_metrics = {
            "openrank": 60.0,
            "activity": 25.0,
            "participants": 150,
            "bus_factor": 12
        }
        
        score = calculate_health_score(high_quality_metrics)
        
        assert score.highlights is not None
        assert len(score.highlights) > 0
        
        # 低质量项目应该有关注点
        low_quality_metrics = {
            "openrank": 2.0,
            "activity": 1.0,
            "participants": 5,
            "bus_factor": 1
        }
        
        score = calculate_health_score(low_quality_metrics)
        
        assert score.concerns is not None
        assert len(score.concerns) > 0


class TestHealthScoreWeights:
    """健康度权重测试"""
    
    def test_activity_weight(self):
        """测试活跃度权重 (30%)"""
        # 只改变活跃度相关指标
        base_metrics = {
            "openrank": 0,
            "activity": 0,
            "attention": 50,
            "participants": 25,
            "bus_factor": 5
        }
        
        high_activity_metrics = {
            **base_metrics,
            "openrank": 100.0,
            "activity": 20.0
        }
        
        base_score = calculate_health_score(base_metrics)
        high_score = calculate_health_score(high_activity_metrics)
        
        # 活跃度提升应该显著影响总分
        assert high_score.overall > base_score.overall
        assert high_score.activity > base_score.activity
    
    def test_community_weight(self):
        """测试社区健康度权重 (25%)"""
        base_metrics = {
            "openrank": 30,
            "activity": 10,
            "participants": 0,
            "bus_factor": 0
        }
        
        high_community_metrics = {
            **base_metrics,
            "participants": 100,
            "bus_factor": 15
        }
        
        base_score = calculate_health_score(base_metrics)
        high_score = calculate_health_score(high_community_metrics)
        
        assert high_score.community > base_score.community


class TestEdgeCases:
    """边界情况测试"""
    
    def test_none_values_handling(self):
        """测试 None 值处理"""
        metrics = {
            "openrank": None,
            "activity": None,
            "participants": None,
            "bus_factor": None
        }
        
        # 不应该抛出异常
        score = calculate_health_score(metrics)
        assert isinstance(score, HealthScore)
    
    def test_dict_values_handling(self):
        """测试字典类型值处理 (时序数据)"""
        metrics = {
            "openrank": {"2024-01": 30, "2024-02": 35, "2024-03": 40},
            "activity": {"2024-01": 10, "2024-02": 12, "2024-03": 15}
        }
        
        # 应该自动提取最新值
        score = calculate_health_score(metrics)
        assert isinstance(score, HealthScore)
    
    def test_negative_values(self):
        """测试负值处理"""
        metrics = {
            "openrank": -10,  # 不应该出现，但要能处理
            "activity": -5
        }
        
        score = calculate_health_score(metrics)
        # 应该将负值处理为 0
        assert score.activity >= 0


# 如果直接运行测试文件
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

