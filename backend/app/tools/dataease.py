"""
DataEase 可视化工具封装
DataEase: https://github.com/dataease/dataease

提供数据可视化能力
"""
import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings


class DataEaseTool:
    """
    DataEase 可视化工具类
    
    DataEase 是开源的数据可视化分析工具
    支持多种图表类型和仪表盘
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or settings.DATAEASE_BASE_URL
        self.api_key = api_key or settings.DATAEASE_API_KEY
        
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=30.0
        )
    
    async def create_chart(
        self,
        chart_type: str,
        data: List[Dict[str, Any]],
        title: str = "",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建图表
        
        Args:
            chart_type: 图表类型（line, bar, pie, radar 等）
            data: 图表数据
            title: 图表标题
            options: 额外配置选项
            
        Returns:
            图表配置
        """
        # 如果 DataEase 可用，调用 API 创建图表
        # 这里返回 ECharts 兼容的配置，供前端渲染
        
        return self._generate_echarts_config(chart_type, data, title, options)
    
    def _generate_echarts_config(
        self,
        chart_type: str,
        data: List[Dict[str, Any]],
        title: str = "",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成 ECharts 图表配置
        
        返回的配置可以直接用于 ECharts 渲染
        """
        config = {
            "title": {
                "text": title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis" if chart_type in ["line", "bar"] else "item"
            },
            "legend": {
                "bottom": 10
            }
        }
        
        if chart_type == "line":
            config.update(self._line_chart_config(data, options))
        elif chart_type == "bar":
            config.update(self._bar_chart_config(data, options))
        elif chart_type == "pie":
            config.update(self._pie_chart_config(data, options))
        elif chart_type == "radar":
            config.update(self._radar_chart_config(data, options))
        elif chart_type == "gauge":
            config.update(self._gauge_chart_config(data, options))
        
        return config
    
    def _line_chart_config(self, data: List[Dict], options: Optional[Dict] = None) -> Dict:
        """折线图配置"""
        # 假设 data 格式: [{"name": "系列名", "data": [{"x": "x值", "y": y值}, ...]}]
        
        x_data = []
        series = []
        
        for series_data in data:
            series_name = series_data.get("name", "")
            points = series_data.get("data", [])
            
            if not x_data and points:
                x_data = [p.get("x", p.get("month", "")) for p in points]
            
            series.append({
                "name": series_name,
                "type": "line",
                "data": [p.get("y", p.get("value", 0)) for p in points],
                "smooth": True
            })
        
        return {
            "xAxis": {
                "type": "category",
                "data": x_data
            },
            "yAxis": {
                "type": "value"
            },
            "series": series
        }
    
    def _bar_chart_config(self, data: List[Dict], options: Optional[Dict] = None) -> Dict:
        """柱状图配置"""
        x_data = []
        series = []
        
        for series_data in data:
            series_name = series_data.get("name", "")
            points = series_data.get("data", [])
            
            if not x_data and points:
                x_data = [p.get("x", p.get("label", "")) for p in points]
            
            series.append({
                "name": series_name,
                "type": "bar",
                "data": [p.get("y", p.get("value", 0)) for p in points]
            })
        
        return {
            "xAxis": {
                "type": "category",
                "data": x_data
            },
            "yAxis": {
                "type": "value"
            },
            "series": series
        }
    
    def _pie_chart_config(self, data: List[Dict], options: Optional[Dict] = None) -> Dict:
        """饼图配置"""
        # 假设 data 格式: [{"name": "项目名", "value": 数值}, ...]
        
        return {
            "series": [{
                "type": "pie",
                "radius": ["40%", "70%"],
                "data": data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }]
        }
    
    def _radar_chart_config(self, data: List[Dict], options: Optional[Dict] = None) -> Dict:
        """雷达图配置 - 适合展示健康度多维度"""
        indicators = options.get("indicators", []) if options else []
        
        return {
            "radar": {
                "indicator": indicators
            },
            "series": [{
                "type": "radar",
                "data": data
            }]
        }
    
    def _gauge_chart_config(self, data: List[Dict], options: Optional[Dict] = None) -> Dict:
        """仪表盘配置 - 适合展示单一指标"""
        value = data[0].get("value", 0) if data else 0
        name = data[0].get("name", "") if data else ""
        
        return {
            "series": [{
                "type": "gauge",
                "detail": {
                    "formatter": "{value}"
                },
                "data": [{
                    "value": value,
                    "name": name
                }]
            }]
        }
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


def generate_health_score_chart(health_score: Dict[str, float]) -> Dict[str, Any]:
    """
    生成健康度雷达图配置
    
    Args:
        health_score: 健康度评分字典
            {
                "overall": 总分,
                "activity": 活跃度,
                "community": 社区健康度,
                "maintenance": 维护响应度,
                "growth": 增长趋势
            }
    
    Returns:
        ECharts 雷达图配置
    """
    return {
        "title": {
            "text": "社区健康度评估",
            "left": "center"
        },
        "radar": {
            "indicator": [
                {"name": "活跃度", "max": 100},
                {"name": "社区健康度", "max": 100},
                {"name": "维护响应度", "max": 100},
                {"name": "增长趋势", "max": 100}
            ]
        },
        "series": [{
            "type": "radar",
            "data": [{
                "value": [
                    health_score.get("activity", 0),
                    health_score.get("community", 0),
                    health_score.get("maintenance", 0),
                    health_score.get("growth", 0)
                ],
                "name": f"总分: {health_score.get('overall', 0):.1f}"
            }],
            "areaStyle": {
                "opacity": 0.3
            }
        }]
    }


def generate_trend_chart(trend_data: List[Dict], metric_name: str = "指标") -> Dict[str, Any]:
    """
    生成趋势折线图配置
    
    Args:
        trend_data: 趋势数据 [{"month": "2024-01", "value": 10.5}, ...]
        metric_name: 指标名称
        
    Returns:
        ECharts 折线图配置
    """
    return {
        "title": {
            "text": f"{metric_name}趋势",
            "left": "center"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "xAxis": {
            "type": "category",
            "data": [item.get("month", "") for item in trend_data]
        },
        "yAxis": {
            "type": "value"
        },
        "series": [{
            "name": metric_name,
            "type": "line",
            "data": [item.get("value", 0) for item in trend_data],
            "smooth": True,
            "areaStyle": {
                "opacity": 0.3
            }
        }]
    }


def generate_contributors_chart(contributors: List[Dict]) -> Dict[str, Any]:
    """
    生成贡献者分布图
    
    Args:
        contributors: 贡献者列表 [{"login": "user1", "contributions": 100}, ...]
        
    Returns:
        ECharts 柱状图配置
    """
    # 取 Top 10
    top_contributors = sorted(
        contributors,
        key=lambda x: x.get("contributions", 0),
        reverse=True
    )[:10]
    
    return {
        "title": {
            "text": "Top 10 贡献者",
            "left": "center"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "xAxis": {
            "type": "category",
            "data": [c.get("login", "") for c in top_contributors],
            "axisLabel": {
                "rotate": 45
            }
        },
        "yAxis": {
            "type": "value",
            "name": "贡献次数"
        },
        "series": [{
            "type": "bar",
            "data": [c.get("contributions", 0) for c in top_contributors],
            "itemStyle": {
                "color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "#83bff6"},
                        {"offset": 1, "color": "#188df0"}
                    ]
                }
            }
        }]
    }

