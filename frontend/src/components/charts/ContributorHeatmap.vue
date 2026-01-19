<script setup lang="ts">
/**
 * ContributorHeatmap - GitHub 风格贡献热力图
 * 展示项目过去一年的活跃度分布
 */
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

interface Props {
  data?: Record<string, number>  // 日期 -> 活跃度值
  year?: number
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  year: new Date().getFullYear(),
  title: '贡献活跃度'
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

// 生成过去一年的日期数据
function generateYearData(): [string, number][] {
  const data: [string, number][] = []
  const end = new Date()
  const start = new Date(end.getFullYear() - 1, end.getMonth(), end.getDate())
  
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const dateStr = d.toISOString().split('T')[0]
    // 如果有真实数据则使用，否则生成模拟数据
    const value = props.data?.[dateStr] ?? Math.floor(Math.random() * 10)
    data.push([dateStr, value])
  }
  
  return data
}

// 颜色等级（类似 GitHub）
const colorLevels = [
  '#161b22', // 0 - 无活动
  '#0e4429', // 1-2
  '#006d32', // 3-5
  '#26a641', // 6-8
  '#39d353', // 9+
]

function getColor(value: number): string {
  if (value === 0) return colorLevels[0]
  if (value <= 2) return colorLevels[1]
  if (value <= 5) return colorLevels[2]
  if (value <= 8) return colorLevels[3]
  return colorLevels[4]
}

const chartOptions = computed(() => {
  const yearData = generateYearData()
  
  return {
    backgroundColor: 'transparent',
    title: {
      text: props.title,
      left: 'center',
      top: 0,
      textStyle: {
        color: '#94a3b8',
        fontSize: 14,
        fontWeight: 500
      }
    },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(139, 92, 246, 0.3)',
      borderWidth: 1,
      padding: [8, 12],
      textStyle: {
        color: '#fff',
        fontSize: 12
      },
      formatter: (params: any) => {
        const date = params.data[0]
        const value = params.data[1]
        return `<div style="font-weight: 500">${date}</div>
                <div style="color: #94a3b8; margin-top: 4px">${value} 次活动</div>`
      }
    },
    visualMap: {
      show: false,
      min: 0,
      max: 10,
      inRange: {
        color: colorLevels
      }
    },
    calendar: {
      top: 40,
      left: 40,
      right: 20,
      bottom: 10,
      cellSize: ['auto', 13],
      range: [
        `${props.year - 1}-${String(new Date().getMonth() + 1).padStart(2, '0')}-01`,
        `${props.year}-${String(new Date().getMonth() + 1).padStart(2, '0')}-${new Date().getDate()}`
      ],
      itemStyle: {
        borderWidth: 2,
        borderColor: '#0f172a'
      },
      yearLabel: { show: false },
      monthLabel: {
        color: '#64748b',
        fontSize: 10,
        nameMap: 'ZH'
      },
      dayLabel: {
        color: '#64748b',
        fontSize: 10,
        firstDay: 1,
        nameMap: ['日', '一', '二', '三', '四', '五', '六']
      },
      splitLine: {
        show: false
      }
    },
    series: [{
      type: 'heatmap',
      coordinateSystem: 'calendar',
      data: yearData,
      emphasis: {
        itemStyle: {
          borderColor: '#8b5cf6',
          borderWidth: 1
        }
      }
    }]
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
  <div class="relative">
    <div ref="chartRef" class="w-full h-40"></div>
    
    <!-- 图例 -->
    <div class="flex items-center justify-end gap-1 mt-2 text-xs text-slate-500">
      <span>少</span>
      <div 
        v-for="(color, index) in colorLevels" 
        :key="index"
        :style="{ backgroundColor: color }"
        class="w-3 h-3 rounded-sm"
      ></div>
      <span>多</span>
    </div>
  </div>
</template>

