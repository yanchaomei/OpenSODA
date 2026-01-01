<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { HealthScore } from '@/stores/analysis'

const props = defineProps<{
  healthScore: HealthScore
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const chartOptions = computed(() => ({
  backgroundColor: 'transparent',
  radar: {
    indicator: [
      { name: '活跃度', max: 100 },
      { name: '社区健康度', max: 100 },
      { name: '维护响应度', max: 100 },
      { name: '增长趋势', max: 100 }
    ],
    shape: 'polygon',
    splitNumber: 4,
    axisName: {
      color: '#94a3b8'
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    },
    splitArea: {
      show: true,
      areaStyle: {
        color: ['rgba(139, 92, 246, 0.05)', 'rgba(139, 92, 246, 0.1)']
      }
    },
    axisLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    }
  },
  series: [{
    type: 'radar',
    data: [{
      value: [
        props.healthScore.activity,
        props.healthScore.community,
        props.healthScore.maintenance,
        props.healthScore.growth
      ],
      name: `总分: ${props.healthScore.overall}`,
      areaStyle: {
        color: 'rgba(139, 92, 246, 0.3)'
      },
      lineStyle: {
        color: '#8b5cf6',
        width: 2
      },
      itemStyle: {
        color: '#8b5cf6'
      }
    }]
  }],
  tooltip: {
    trigger: 'item'
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

watch(() => props.healthScore, () => {
  updateChart()
}, { deep: true })
</script>

<template>
  <div ref="chartRef" class="w-full h-64"></div>
</template>

