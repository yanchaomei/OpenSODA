/**
 * ECharts 统一主题配置
 * OpenSource Copilot 专用深色主题
 */

export const CHART_COLORS = {
  // 主色调
  primary: '#8b5cf6',    // 紫色
  secondary: '#06b6d4',  // 青色
  accent: '#a78bfa',     // 浅紫
  
  // 状态色
  success: '#10b981',    // 绿色
  warning: '#f59e0b',    // 橙色
  error: '#ef4444',      // 红色
  info: '#3b82f6',       // 蓝色
  
  // 评分色阶
  scoreExcellent: '#10b981',  // >= 80
  scoreGood: '#22c55e',       // >= 60
  scoreFair: '#eab308',       // >= 40
  scorePoor: '#ef4444',       // < 40
  
  // 背景和边框
  background: '#0f172a',
  surface: '#1e293b',
  border: 'rgba(255, 255, 255, 0.1)',
  
  // 文字
  textPrimary: '#f8fafc',
  textSecondary: '#94a3b8',
  textMuted: '#64748b',
}

// 系列颜色
export const SERIES_COLORS = [
  '#8b5cf6', // purple
  '#06b6d4', // cyan
  '#10b981', // emerald
  '#f59e0b', // amber
  '#ec4899', // pink
  '#3b82f6', // blue
  '#14b8a6', // teal
  '#f97316', // orange
]

// 评分颜色获取
export function getScoreColor(score: number): string {
  if (score >= 80) return CHART_COLORS.scoreExcellent
  if (score >= 60) return CHART_COLORS.scoreGood
  if (score >= 40) return CHART_COLORS.scoreFair
  return CHART_COLORS.scorePoor
}

// 通用 ECharts 配置
export const CHART_COMMON_OPTIONS = {
  // 背景透明
  backgroundColor: 'transparent',
  
  // 动画配置
  animation: true,
  animationDuration: 800,
  animationEasing: 'cubicOut',
  
  // 网格配置
  grid: {
    left: '3%',
    right: '3%',
    top: '10%',
    bottom: '10%',
    containLabel: true
  },
  
  // 提示框配置
  tooltip: {
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderColor: 'rgba(139, 92, 246, 0.3)',
    borderWidth: 1,
    padding: [12, 16],
    textStyle: {
      color: '#fff',
      fontSize: 13
    },
    extraCssText: 'box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);'
  },
  
  // 坐标轴通用样式
  axisStyle: {
    axisLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    },
    axisTick: {
      show: false
    },
    axisLabel: {
      color: '#64748b',
      fontSize: 11
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.05)'
      }
    }
  },
  
  // 图例配置
  legend: {
    textStyle: {
      color: '#94a3b8',
      fontSize: 12
    },
    icon: 'circle',
    itemWidth: 10,
    itemHeight: 10,
    itemGap: 20
  }
}

// 雷达图配置
export const RADAR_OPTIONS = {
  shape: 'polygon',
  splitNumber: 4,
  axisName: {
    color: '#94a3b8',
    fontSize: 12,
    fontWeight: 500
  },
  splitLine: {
    lineStyle: {
      color: [
        'rgba(139, 92, 246, 0.1)',
        'rgba(139, 92, 246, 0.15)',
        'rgba(139, 92, 246, 0.2)',
        'rgba(139, 92, 246, 0.25)'
      ]
    }
  },
  splitArea: {
    show: true,
    areaStyle: {
      color: [
        'rgba(139, 92, 246, 0.02)',
        'rgba(139, 92, 246, 0.04)',
        'rgba(139, 92, 246, 0.06)',
        'rgba(139, 92, 246, 0.08)'
      ]
    }
  },
  axisLine: {
    lineStyle: {
      color: 'rgba(139, 92, 246, 0.2)'
    }
  }
}

// 折线图配置
export const LINE_OPTIONS = {
  smooth: true,
  showSymbol: false,
  lineStyle: {
    width: 2
  },
  areaStyle: {
    opacity: 0.3
  },
  emphasis: {
    focus: 'series'
  }
}

// 柱状图配置
export const BAR_OPTIONS = {
  barWidth: '60%',
  barMaxWidth: 50,
  itemStyle: {
    borderRadius: [4, 4, 0, 0]
  },
  emphasis: {
    itemStyle: {
      shadowBlur: 10,
      shadowColor: 'rgba(0, 0, 0, 0.3)'
    }
  }
}

export default {
  CHART_COLORS,
  SERIES_COLORS,
  getScoreColor,
  CHART_COMMON_OPTIONS,
  RADAR_OPTIONS,
  LINE_OPTIONS,
  BAR_OPTIONS
}

