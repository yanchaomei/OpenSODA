<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

interface TrendData {
  month: string
  value: number
}

const props = withDefaults(defineProps<{
  data: TrendData[]
  metricName?: string
  color?: string
  showArea?: boolean
  showMarker?: boolean
  height?: number
}>(), {
  metricName: '指标',
  color: '#8b5cf6',
  showArea: true,
  showMarker: true,
  height: 256
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

// 计算趋势
const trend = computed(() => {
  if (props.data.length < 2) return 'stable'
  const firstHalf = props.data.slice(0, Math.floor(props.data.length / 2))
  const secondHalf = props.data.slice(Math.floor(props.data.length / 2))
  
  const avgFirst = firstHalf.reduce((a, b) => a + b.value, 0) / firstHalf.length
  const avgSecond = secondHalf.reduce((a, b) => a + b.value, 0) / secondHalf.length
  
  const change = (avgSecond - avgFirst) / avgFirst
  if (change > 0.1) return 'rising'
  if (change < -0.1) return 'declining'
  return 'stable'
})

const trendColor = computed(() => {
  if (trend.value === 'rising') return '#10b981'
  if (trend.value === 'declining') return '#ef4444'
  return '#eab308'
})

const chartOptions = computed(() => {
  const maxValue = Math.max(...props.data.map(d => d.value))
  const minValue = Math.min(...props.data.map(d => d.value))
  
  return {
    backgroundColor: 'transparent',
    animation: true,
    animationDuration: 1000,
    animationEasing: 'cubicOut',
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: props.data.map(d => d.month),
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        formatter: (value: string) => {
          // 简化月份显示
          return value.replace(/^\d{4}-/, '')
        }
      },
      axisTick: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      min: Math.floor(minValue * 0.9),
      axisLine: {
        show: false
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 11
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.05)',
          type: 'dashed'
        }
      }
    },
    series: [{
      name: props.metricName,
      type: 'line',
      data: props.data.map(d => d.value),
      smooth: 0.3,
      lineStyle: {
        color: props.color,
        width: 3,
        shadowColor: props.color,
        shadowBlur: 10,
        shadowOffsetY: 5
      },
      areaStyle: props.showArea ? {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: `${props.color}40` },
          { offset: 0.5, color: `${props.color}20` },
          { offset: 1, color: `${props.color}05` }
        ])
      } : undefined,
      itemStyle: {
        color: props.color,
        borderColor: '#1e293b',
        borderWidth: 2
      },
      symbol: props.showMarker ? 'circle' : 'none',
      symbolSize: 8,
      emphasis: {
        focus: 'series',
        itemStyle: {
          shadowBlur: 20,
          shadowColor: props.color
        }
      },
      markPoint: props.showMarker ? {
        symbol: 'pin',
        symbolSize: 50,
        data: [
          { type: 'max', name: '最高' },
          { type: 'min', name: '最低' }
        ],
        label: {
          color: '#fff',
          fontSize: 10
        },
        itemStyle: {
          color: props.color
        }
      } : undefined,
      markLine: {
        silent: true,
        lineStyle: {
          color: 'rgba(139, 92, 246, 0.3)',
          type: 'dashed'
        },
        data: [
          { type: 'average', name: '平均值' }
        ],
        label: {
          color: '#94a3b8',
          fontSize: 10
        }
      }
    }],
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(139, 92, 246, 0.3)',
      borderWidth: 1,
      padding: [12, 16],
      textStyle: {
        color: '#fff',
        fontSize: 13
      },
      axisPointer: {
        type: 'cross',
        lineStyle: {
          color: 'rgba(139, 92, 246, 0.3)'
        },
        crossStyle: {
          color: 'rgba(139, 92, 246, 0.3)'
        }
      },
      formatter: (params: any) => {
        const data = params[0]
        return `
          <div style="font-weight: 600; margin-bottom: 4px; color: #94a3b8">
            ${data.axisValue}
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 10px; height: 10px; background: ${props.color}; border-radius: 50%;"></span>
            <span>${props.metricName}:</span>
            <span style="font-weight: 600; color: ${props.color}">${data.value.toFixed(2)}</span>
          </div>
        `
      }
    },
    dataZoom: props.data.length > 12 ? [{
      type: 'inside',
      start: 50,
      end: 100
    }] : undefined
  }
})

function initChart() {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    chart.setOption(chartOptions.value)
    
    resizeObserver = new ResizeObserver(() => {
      chart?.resize()
    })
    resizeObserver.observe(chartRef.value)
  }
}

function updateChart() {
  if (chart) {
    chart.setOption(chartOptions.value, true)
  }
}

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
})

watch(() => props.data, () => {
  updateChart()
}, { deep: true })
</script>

<template>
  <div class="relative">
    <!-- 趋势标签 -->
    <div class="absolute top-0 right-0 z-10">
      <span 
        :class="[
          'px-2 py-1 rounded text-xs font-medium',
          trend === 'rising' ? 'bg-emerald-500/20 text-emerald-400' :
          trend === 'declining' ? 'bg-red-500/20 text-red-400' :
          'bg-yellow-500/20 text-yellow-400'
        ]"
      >
        {{ trend === 'rising' ? '📈 上升' : trend === 'declining' ? '📉 下降' : '➡️ 稳定' }}
      </span>
    </div>
    
    <div 
      ref="chartRef" 
      class="w-full"
      :style="{ height: `${height}px` }"
    ></div>
  </div>
</template>
