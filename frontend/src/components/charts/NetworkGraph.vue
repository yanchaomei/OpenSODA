<script setup lang="ts">
/**
 * NetworkGraph - 贡献者网络关系图
 * 展示贡献者之间的协作关系
 */
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'

interface Node {
  id: string
  name: string
  value: number
  category?: number
}

interface Link {
  source: string
  target: string
  value?: number
}

interface Props {
  nodes: Node[]
  links: Link[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: ''
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const categories = [
  { name: '核心贡献者', itemStyle: { color: '#8b5cf6' } },
  { name: '活跃贡献者', itemStyle: { color: '#06b6d4' } },
  { name: '普通贡献者', itemStyle: { color: '#10b981' } },
]

const chartOptions = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderColor: 'rgba(139, 92, 246, 0.3)',
    borderWidth: 1,
    textStyle: {
      color: '#fff',
      fontSize: 12
    }
  },
  legend: {
    data: categories.map(c => c.name),
    textStyle: {
      color: '#94a3b8',
      fontSize: 11
    },
    bottom: 0,
    icon: 'circle',
    itemWidth: 8,
    itemHeight: 8
  },
  animationDuration: 1500,
  animationEasingUpdate: 'quinticInOut',
  series: [{
    type: 'graph',
    layout: 'force',
    data: props.nodes.map(node => ({
      ...node,
      symbolSize: Math.min(Math.max(node.value * 2, 15), 50),
      label: {
        show: node.value > 20,
        position: 'right',
        formatter: '{b}',
        fontSize: 10,
        color: '#94a3b8'
      },
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 1,
        shadowBlur: 10,
        shadowColor: 'rgba(139, 92, 246, 0.3)'
      }
    })),
    links: props.links.map(link => ({
      ...link,
      lineStyle: {
        width: Math.max((link.value || 1) / 2, 0.5),
        curveness: 0.3,
        opacity: 0.4
      }
    })),
    categories,
    roam: true,
    draggable: true,
    force: {
      repulsion: 200,
      edgeLength: [50, 200],
      gravity: 0.1
    },
    emphasis: {
      focus: 'adjacency',
      lineStyle: {
        width: 3,
        opacity: 1
      },
      itemStyle: {
        shadowBlur: 20
      }
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

watch([() => props.nodes, () => props.links], () => {
  updateChart()
}, { deep: true })
</script>

<template>
  <div>
    <h4 v-if="title" class="text-sm text-slate-400 mb-2">{{ title }}</h4>
    <div ref="chartRef" class="w-full h-80"></div>
  </div>
</template>

