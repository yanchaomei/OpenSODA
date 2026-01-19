<script setup lang="ts">
/**
 * AgentNetwork - 多 Agent 协作网络可视化
 * 展示 Agent 之间的协作关系和工作流程
 */
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'

interface AgentNode {
  id: string
  name: string
  type: 'orchestrator' | 'analysis' | 'diagnosis' | 'tool' | 'llm'
  status: 'idle' | 'working' | 'done'
}

interface AgentLink {
  source: string
  target: string
  type?: 'data' | 'control' | 'result'
}

interface Props {
  agents: AgentNode[]
  links: AgentLink[]
  activeAgent?: string
}

const props = withDefaults(defineProps<Props>(), {
  activeAgent: undefined
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

// Agent 类型对应的颜色和图标
const agentConfig: Record<string, { color: string; symbol: string }> = {
  orchestrator: { color: '#8b5cf6', symbol: 'diamond' },
  analysis: { color: '#06b6d4', symbol: 'circle' },
  diagnosis: { color: '#10b981', symbol: 'circle' },
  tool: { color: '#f59e0b', symbol: 'rect' },
  llm: { color: '#ec4899', symbol: 'triangle' }
}

const chartOptions = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderColor: 'rgba(139, 92, 246, 0.3)',
    borderWidth: 1,
    textStyle: { color: '#fff', fontSize: 12 },
    formatter: (params: any) => {
      if (params.dataType === 'node') {
        return `<strong>${params.name}</strong><br/>类型: ${params.data.agentType}<br/>状态: ${params.data.status}`
      }
      return `${params.data.source} → ${params.data.target}`
    }
  },
  animationDuration: 1500,
  animationEasingUpdate: 'quinticInOut',
  series: [{
    type: 'graph',
    layout: 'force',
    roam: true,
    draggable: true,
    data: props.agents.map(agent => {
      const config = agentConfig[agent.type] || agentConfig.tool
      const isActive = agent.id === props.activeAgent || agent.status === 'working'
      return {
        id: agent.id,
        name: agent.name,
        agentType: agent.type,
        status: agent.status,
        symbolSize: agent.type === 'orchestrator' ? 60 : 45,
        symbol: config.symbol,
        itemStyle: {
          color: isActive ? config.color : `${config.color}66`,
          borderColor: isActive ? '#fff' : `${config.color}88`,
          borderWidth: isActive ? 3 : 1,
          shadowBlur: isActive ? 20 : 0,
          shadowColor: isActive ? config.color : 'transparent'
        },
        label: {
          show: true,
          position: 'bottom',
          distance: 8,
          color: isActive ? '#fff' : '#94a3b8',
          fontSize: 11,
          fontWeight: isActive ? 'bold' : 'normal'
        }
      }
    }),
    links: props.links.map(link => ({
      source: link.source,
      target: link.target,
      lineStyle: {
        width: 2,
        color: link.type === 'result' ? '#10b981' : 
               link.type === 'control' ? '#8b5cf6' : '#06b6d4',
        opacity: 0.6,
        curveness: 0.2,
        type: link.type === 'data' ? 'solid' : 'dashed'
      },
      symbol: ['none', 'arrow'],
      symbolSize: [0, 10]
    })),
    force: {
      repulsion: 300,
      edgeLength: [100, 200],
      gravity: 0.1
    },
    emphasis: {
      focus: 'adjacency',
      lineStyle: { width: 4, opacity: 1 }
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

watch([() => props.agents, () => props.links, () => props.activeAgent], () => {
  updateChart()
}, { deep: true })
</script>

<template>
  <div class="relative">
    <div ref="chartRef" class="w-full h-64"></div>
    
    <!-- 图例 -->
    <div class="absolute bottom-2 left-2 flex flex-wrap gap-3 text-xs">
      <div class="flex items-center gap-1.5">
        <div class="w-3 h-3 rotate-45 bg-violet-500"></div>
        <span class="text-slate-400">协调器</span>
      </div>
      <div class="flex items-center gap-1.5">
        <div class="w-3 h-3 rounded-full bg-cyan-500"></div>
        <span class="text-slate-400">分析 Agent</span>
      </div>
      <div class="flex items-center gap-1.5">
        <div class="w-3 h-3 bg-amber-500"></div>
        <span class="text-slate-400">工具</span>
      </div>
      <div class="flex items-center gap-1.5">
        <div class="w-2 h-3 border-l-4 border-t-4 border-pink-500 border-b-4 border-transparent" style="border-right: 4px solid transparent;"></div>
        <span class="text-slate-400">LLM</span>
      </div>
    </div>
  </div>
</template>

