<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

interface MetricData {
  name: string
  value: number
  color?: string
}

const props = withDefaults(defineProps<{
  data: MetricData[]
  title?: string
  maxValue?: number
  horizontal?: boolean
}>(), {
  title: '',
  maxValue: 100,
  horizontal: true
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const defaultColors = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']

const chartOptions = computed(() => {
  const sortedData = [...props.data].sort((a, b) => b.value - a.value)
  
  return {
    backgroundColor: 'transparent',
    animation: true,
    animationDuration: 800,
    animationEasing: 'cubicOut',
    grid: {
      left: props.horizontal ? '5%' : '3%',
      right: '5%',
      bottom: '5%',
      top: props.title ? '15%' : '5%',
      containLabel: true
    },
    title: props.title ? {
      text: props.title,
      left: 'center',
      textStyle: {
        color: '#fff',
        fontSize: 14,
        fontWeight: 500
      }
    } : undefined,
    xAxis: props.horizontal ? {
      type: 'value',
      max: props.maxValue,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false },
      splitLine: { show: false }
    } : {
      type: 'category',
      data: sortedData.map(d => d.name),
      axisLine: {
        lineStyle: { color: 'rgba(255,255,255,0.1)' }
      },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 11,
        rotate: sortedData.length > 5 ? 30 : 0
      },
      axisTick: { show: false }
    },
    yAxis: props.horizontal ? {
      type: 'category',
      data: sortedData.map(d => d.name),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 12
      }
    } : {
      type: 'value',
      max: props.maxValue,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 11
      },
      splitLine: {
        lineStyle: { color: 'rgba(255,255,255,0.05)' }
      }
    },
    series: [{
      type: 'bar',
      data: sortedData.map((d, i) => ({
        value: d.value,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(
            props.horizontal ? 0 : 0,
            props.horizontal ? 0 : 1,
            props.horizontal ? 1 : 0,
            props.horizontal ? 0 : 0,
            [
              { offset: 0, color: d.color || defaultColors[i % defaultColors.length] },
              { offset: 1, color: `${d.color || defaultColors[i % defaultColors.length]}80` }
            ]
          ),
          borderRadius: props.horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0]
        }
      })),
      barWidth: props.horizontal ? 20 : '60%',
      label: {
        show: true,
        position: props.horizontal ? 'right' : 'top',
        color: '#fff',
        fontSize: 12,
        fontWeight: 'bold',
        formatter: (params: any) => params.value.toFixed(1)
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(139, 92, 246, 0.5)'
        }
      }
    }],
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(139, 92, 246, 0.3)',
      borderWidth: 1,
      textStyle: {
        color: '#fff',
        fontSize: 13
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

watch(() => props.data, () => {
  updateChart()
}, { deep: true })
</script>

<template>
  <div 
    ref="chartRef" 
    class="w-full"
    :style="{ height: horizontal ? `${Math.max(200, data.length * 40)}px` : '256px' }"
  ></div>
</template>

