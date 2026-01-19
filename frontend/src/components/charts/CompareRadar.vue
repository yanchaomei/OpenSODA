<script setup lang="ts">
/**
 * CompareRadar - 多项目对比雷达图
 * 支持叠加展示多个项目的健康度对比
 */
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

interface ProjectScore {
  name: string
  color?: string
  scores: {
    activity: number
    community: number
    maintenance: number
    growth: number
  }
}

interface Props {
  projects: ProjectScore[]
  showLegend?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  showLegend: true,
  size: 'md'
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

// 预定义颜色
const COLORS = [
  '#8b5cf6', // purple
  '#06b6d4', // cyan
  '#10b981', // emerald
  '#f59e0b', // amber
  '#ef4444', // red
  '#ec4899', // pink
]

const chartOptions = computed(() => {
  const seriesData = props.projects.map((project, index) => ({
    name: project.name,
    type: 'radar' as const,
    symbol: 'circle',
    symbolSize: 6,
    data: [{
      value: [
        project.scores.activity,
        project.scores.community,
        project.scores.maintenance,
        project.scores.growth
      ],
      name: project.name,
      areaStyle: {
        color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
          { offset: 0, color: `${project.color || COLORS[index % COLORS.length]}40` },
          { offset: 1, color: `${project.color || COLORS[index % COLORS.length]}10` }
        ])
      },
      lineStyle: {
        color: project.color || COLORS[index % COLORS.length],
        width: 2
      },
      itemStyle: {
        color: project.color || COLORS[index % COLORS.length],
        borderColor: '#fff',
        borderWidth: 2
      }
    }]
  }))

  return {
    backgroundColor: 'transparent',
    animation: true,
    animationDuration: 1000,
    animationEasing: 'cubicOut',
    legend: props.showLegend ? {
      data: props.projects.map(p => p.name),
      bottom: 0,
      textStyle: {
        color: '#94a3b8',
        fontSize: 12
      },
      icon: 'circle',
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 20
    } : undefined,
    radar: {
      indicator: [
        { name: '活跃度', max: 100 },
        { name: '社区健康', max: 100 },
        { name: '维护响应', max: 100 },
        { name: '增长趋势', max: 100 }
      ],
      shape: 'polygon',
      splitNumber: 4,
      center: ['50%', props.showLegend ? '45%' : '50%'],
      radius: props.size === 'sm' ? '55%' : props.size === 'lg' ? '70%' : '60%',
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
    },
    series: seriesData,
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
        const color = params.color
        return `
          <div style="font-weight: 600; margin-bottom: 8px; color: ${color}">
            ${data.name}
          </div>
          <div style="display: grid; gap: 4px; font-size: 12px;">
            <div>活跃度: <span style="color: #fff; font-weight: 500">${data.value[0]}</span></div>
            <div>社区健康: <span style="color: #fff; font-weight: 500">${data.value[1]}</span></div>
            <div>维护响应: <span style="color: #fff; font-weight: 500">${data.value[2]}</span></div>
            <div>增长趋势: <span style="color: #fff; font-weight: 500">${data.value[3]}</span></div>
          </div>
        `
      }
    }
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

watch(() => props.projects, () => {
  updateChart()
}, { deep: true })
</script>

<template>
  <div 
    ref="chartRef" 
    :class="[
      'w-full',
      size === 'sm' ? 'h-48' : size === 'lg' ? 'h-96' : 'h-72'
    ]"
  ></div>
</template>

