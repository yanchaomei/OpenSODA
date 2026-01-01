<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

interface TrendData {
  month: string
  value: number
}

const props = defineProps<{
  data: TrendData[]
  metricName?: string
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const chartOptions = computed(() => ({
  backgroundColor: 'transparent',
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: props.data.map(d => d.month),
    axisLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    },
    axisLabel: {
      color: '#64748b',
      fontSize: 10
    }
  },
  yAxis: {
    type: 'value',
    axisLine: {
      show: false
    },
    axisLabel: {
      color: '#64748b'
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.05)'
      }
    }
  },
  series: [{
    name: props.metricName || '指标',
    type: 'line',
    data: props.data.map(d => d.value),
    smooth: true,
    lineStyle: {
      color: '#0ea5e9',
      width: 3
    },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(14, 165, 233, 0.3)' },
        { offset: 1, color: 'rgba(14, 165, 233, 0.05)' }
      ])
    },
    itemStyle: {
      color: '#0ea5e9'
    },
    emphasis: {
      focus: 'series'
    }
  }],
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(30, 41, 59, 0.9)',
    borderColor: 'rgba(255, 255, 255, 0.1)',
    textStyle: {
      color: '#fff'
    }
  }
}))

function initChart() {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    chart.setOption(chartOptions.value)
  }
}

function updateChart() {
  if (chart) {
    chart.setOption(chartOptions.value)
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chart?.resize())
})

watch(() => props.data, () => {
  updateChart()
}, { deep: true })
</script>

<template>
  <div ref="chartRef" class="w-full h-64"></div>
</template>

