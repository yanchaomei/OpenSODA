<script setup lang="ts">
/**
 * WordCloud - 词云图组件
 * 展示项目关键词、技术栈等
 */
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'

interface WordItem {
  name: string
  value: number
}

interface Props {
  words: WordItem[]
  title?: string
  shape?: 'circle' | 'cardioid' | 'diamond' | 'triangle' | 'star'
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  shape: 'circle'
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const colors = [
  '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899',
  '#3b82f6', '#14b8a6', '#f97316', '#a855f7', '#22c55e'
]

const chartOptions = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    show: true,
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderColor: 'rgba(139, 92, 246, 0.3)',
    borderWidth: 1,
    textStyle: {
      color: '#fff',
      fontSize: 12
    },
    formatter: (params: any) => `${params.name}: ${params.value}`
  },
  series: [{
    type: 'wordCloud',
    shape: props.shape,
    left: 'center',
    top: 'center',
    width: '90%',
    height: '90%',
    sizeRange: [14, 50],
    rotationRange: [-45, 45],
    rotationStep: 15,
    gridSize: 8,
    drawOutOfBound: false,
    layoutAnimation: true,
    textStyle: {
      fontFamily: 'system-ui, sans-serif',
      fontWeight: 'bold',
      color: () => colors[Math.floor(Math.random() * colors.length)]
    },
    emphasis: {
      focus: 'self',
      textStyle: {
        textShadowBlur: 10,
        textShadowColor: 'rgba(139, 92, 246, 0.5)'
      }
    },
    data: props.words.map(w => ({
      name: w.name,
      value: w.value,
      textStyle: {
        color: colors[Math.floor(Math.random() * colors.length)]
      }
    }))
  }]
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

watch(() => props.words, () => {
  updateChart()
}, { deep: true })
</script>

<template>
  <div>
    <h4 v-if="title" class="text-sm text-slate-400 mb-2">{{ title }}</h4>
    <div ref="chartRef" class="w-full h-64"></div>
  </div>
</template>

