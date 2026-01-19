<script setup lang="ts">
/**
 * SankeyFlow - 桑基图组件
 * 展示 Agent 数据流向和处理过程
 */
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'

interface Node {
  name: string
}

interface Link {
  source: string
  target: string
  value: number
}

interface Props {
  nodes?: Node[]
  links?: Link[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  nodes: () => [
    { name: '用户查询' },
    { name: 'ReAct Agent' },
    { name: 'OpenDigger API' },
    { name: 'GitHub API' },
    { name: '缓存' },
    { name: '数据分析' },
    { name: '健康评分' },
    { name: '问题诊断' },
    { name: '建议生成' },
    { name: 'LLM 推理' },
    { name: '响应生成' },
    { name: '用户展示' }
  ],
  links: () => [
    { source: '用户查询', target: 'ReAct Agent', value: 100 },
    { source: 'ReAct Agent', target: 'LLM 推理', value: 90 },
    { source: 'ReAct Agent', target: 'OpenDigger API', value: 60 },
    { source: 'ReAct Agent', target: 'GitHub API', value: 40 },
    { source: 'OpenDigger API', target: '缓存', value: 30 },
    { source: 'OpenDigger API', target: '数据分析', value: 30 },
    { source: 'GitHub API', target: '缓存', value: 20 },
    { source: 'GitHub API', target: '数据分析', value: 20 },
    { source: '缓存', target: '数据分析', value: 50 },
    { source: '数据分析', target: '健康评分', value: 40 },
    { source: '数据分析', target: '问题诊断', value: 30 },
    { source: '数据分析', target: '建议生成', value: 30 },
    { source: 'LLM 推理', target: '响应生成', value: 90 },
    { source: '健康评分', target: '响应生成', value: 40 },
    { source: '问题诊断', target: '响应生成', value: 30 },
    { source: '建议生成', target: '响应生成', value: 30 },
    { source: '响应生成', target: '用户展示', value: 100 }
  ]
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const chartOptions = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    triggerOn: 'mousemove',
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderColor: 'rgba(139, 92, 246, 0.3)',
    borderWidth: 1,
    textStyle: { color: '#fff', fontSize: 12 }
  },
  series: [{
    type: 'sankey',
    layout: 'none',
    emphasis: {
      focus: 'adjacency'
    },
    nodeAlign: 'justify',
    data: props.nodes,
    links: props.links,
    lineStyle: {
      color: 'gradient',
      curveness: 0.5
    },
    itemStyle: {
      color: '#8b5cf6',
      borderColor: '#1e293b',
      borderWidth: 1
    },
    label: {
      color: '#e2e8f0',
      fontSize: 11
    }
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

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
})

watch([() => props.nodes, () => props.links], () => {
  if (chart) {
    chart.setOption(chartOptions.value, true)
  }
}, { deep: true })
</script>

<template>
  <div>
    <h4 v-if="title" class="text-sm text-slate-400 mb-2">{{ title }}</h4>
    <div ref="chartRef" class="w-full h-80"></div>
  </div>
</template>

