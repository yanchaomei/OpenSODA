<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(defineProps<{
  score: number
  title?: string
  size?: 'sm' | 'md' | 'lg'
}>(), {
  title: '健康度',
  size: 'md'
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

function getScoreColor(score: number): string {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#22c55e'
  if (score >= 40) return '#eab308'
  return '#ef4444'
}

function getScoreLabel(score: number): string {
  if (score >= 80) return '优秀'
  if (score >= 60) return '良好'
  if (score >= 40) return '一般'
  return '需关注'
}

const color = computed(() => getScoreColor(props.score))
const label = computed(() => getScoreLabel(props.score))

const chartOptions = computed(() => ({
  backgroundColor: 'transparent',
  animation: true,
  animationDuration: 1500,
  animationEasing: 'cubicOut',
  series: [
    {
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      center: ['50%', '60%'],
      radius: '90%',
      min: 0,
      max: 100,
      splitNumber: 5,
      axisLine: {
        lineStyle: {
          width: props.size === 'sm' ? 15 : 20,
          color: [
            [0.4, '#ef4444'],
            [0.6, '#eab308'],
            [0.8, '#22c55e'],
            [1, '#10b981']
          ]
        }
      },
      pointer: {
        icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
        length: '60%',
        width: props.size === 'sm' ? 6 : 8,
        offsetCenter: [0, '-10%'],
        itemStyle: {
          color: 'auto'
        }
      },
      axisTick: {
        length: props.size === 'sm' ? 8 : 12,
        lineStyle: {
          color: 'auto',
          width: 2
        }
      },
      splitLine: {
        length: props.size === 'sm' ? 15 : 20,
        lineStyle: {
          color: 'auto',
          width: 3
        }
      },
      axisLabel: {
        color: '#94a3b8',
        fontSize: props.size === 'sm' ? 10 : 12,
        distance: props.size === 'sm' ? -40 : -50,
        formatter: (value: number) => {
          if (value === 0) return '0'
          if (value === 100) return '100'
          return ''
        }
      },
      title: {
        offsetCenter: [0, '30%'],
        fontSize: props.size === 'sm' ? 12 : 14,
        color: '#94a3b8'
      },
      detail: {
        valueAnimation: true,
        fontSize: props.size === 'sm' ? 28 : 36,
        fontWeight: 'bold',
        offsetCenter: [0, '0%'],
        formatter: (value: number) => `${value.toFixed(0)}`,
        color: color.value
      },
      data: [{
        value: props.score,
        name: props.title
      }]
    },
    // 外环装饰
    {
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      center: ['50%', '60%'],
      radius: '100%',
      min: 0,
      max: 100,
      axisLine: {
        lineStyle: {
          width: 2,
          color: [[1, 'rgba(139, 92, 246, 0.2)']]
        }
      },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { show: false }
    }
  ]
}))

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

watch(() => props.score, () => {
  updateChart()
})
</script>

<template>
  <div class="relative">
    <div 
      ref="chartRef" 
      :class="[
        'w-full',
        size === 'sm' ? 'h-40' : size === 'lg' ? 'h-64' : 'h-52'
      ]"
    ></div>
    
    <!-- 标签 -->
    <div class="absolute bottom-2 left-1/2 -translate-x-1/2">
      <span 
        :class="[
          'px-3 py-1 rounded-full text-sm font-medium',
          score >= 80 ? 'bg-emerald-500/20 text-emerald-400' :
          score >= 60 ? 'bg-green-500/20 text-green-400' :
          score >= 40 ? 'bg-yellow-500/20 text-yellow-400' :
          'bg-red-500/20 text-red-400'
        ]"
      >
        {{ label }}
      </span>
    </div>
  </div>
</template>

