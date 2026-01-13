<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { HealthScore } from '@/stores/analysis'

const props = withDefaults(defineProps<{
  healthScore: HealthScore
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  animated?: boolean
}>(), {
  size: 'md',
  showLabel: true,
  animated: true
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

// 根据分数获取颜色
function getScoreColor(score: number): string {
  if (score >= 80) return '#10b981' // emerald
  if (score >= 60) return '#22c55e' // green
  if (score >= 40) return '#eab308' // yellow
  return '#ef4444' // red
}

const mainColor = computed(() => getScoreColor(props.healthScore.overall))

const chartOptions = computed(() => ({
  backgroundColor: 'transparent',
  animation: props.animated,
  animationDuration: 800,
  animationEasing: 'cubicOut',
  radar: {
    indicator: [
      { name: '活跃度', max: 100 },
      { name: '社区健康', max: 100 },
      { name: '维护响应', max: 100 },
      { name: '增长趋势', max: 100 }
    ],
    shape: 'polygon',
    splitNumber: 4,
    center: ['50%', '55%'],
    radius: props.size === 'sm' ? '60%' : props.size === 'lg' ? '75%' : '70%',
    axisName: {
      color: '#94a3b8',
      fontSize: props.size === 'sm' ? 10 : 12,
      fontWeight: 500,
      formatter: (name: string, indicator: any) => {
        if (!props.showLabel) return ''
        const value = getValueByName(name)
        return `{name|${name}}\n{value|${value}}`
      },
      rich: {
        name: {
          color: '#94a3b8',
          fontSize: props.size === 'sm' ? 10 : 12,
          lineHeight: 18
        },
        value: {
          color: mainColor.value,
          fontSize: props.size === 'sm' ? 12 : 14,
          fontWeight: 'bold',
          lineHeight: 20
        }
      }
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
  },
  series: [{
    type: 'radar',
    symbol: 'circle',
    symbolSize: 6,
    data: [{
      value: [
        props.healthScore.activity,
        props.healthScore.community,
        props.healthScore.maintenance,
        props.healthScore.growth
      ],
      name: `总分: ${props.healthScore.overall}`,
      areaStyle: {
        color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
          { offset: 0, color: `${mainColor.value}40` },
          { offset: 1, color: `${mainColor.value}10` }
        ])
      },
      lineStyle: {
        color: mainColor.value,
        width: 2,
        shadowColor: mainColor.value,
        shadowBlur: 10
      },
      itemStyle: {
        color: mainColor.value,
        borderColor: '#fff',
        borderWidth: 2,
        shadowColor: mainColor.value,
        shadowBlur: 8
      }
    }],
    emphasis: {
      itemStyle: {
        shadowBlur: 20
      }
    }
  }],
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderColor: 'rgba(139, 92, 246, 0.3)',
    borderWidth: 1,
    padding: [12, 16],
    textStyle: {
      color: '#fff',
      fontSize: 13
    },
    formatter: (params: any) => {
      const data = params.data
      return `
        <div style="font-weight: 600; margin-bottom: 8px; color: ${mainColor.value}">
          ${data.name}
        </div>
        <div style="display: grid; gap: 4px;">
          <div>活跃度: <span style="color: #fff; font-weight: 500">${data.value[0]}</span></div>
          <div>社区健康: <span style="color: #fff; font-weight: 500">${data.value[1]}</span></div>
          <div>维护响应: <span style="color: #fff; font-weight: 500">${data.value[2]}</span></div>
          <div>增长趋势: <span style="color: #fff; font-weight: 500">${data.value[3]}</span></div>
        </div>
      `
    }
  }
}))

function getValueByName(name: string): number {
  switch (name) {
    case '活跃度': return props.healthScore.activity
    case '社区健康': return props.healthScore.community
    case '维护响应': return props.healthScore.maintenance
    case '增长趋势': return props.healthScore.growth
    default: return 0
  }
}

function initChart() {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    chart.setOption(chartOptions.value)
    
    // 使用 ResizeObserver 监听容器大小变化
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

watch(() => props.healthScore, () => {
  updateChart()
}, { deep: true })
</script>

<template>
  <div 
    ref="chartRef" 
    :class="[
      'w-full',
      size === 'sm' ? 'h-48' : size === 'lg' ? 'h-80' : 'h-64'
    ]"
  ></div>
</template>
