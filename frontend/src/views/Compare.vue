<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { analysisApi, type CompareResponse, type CompareResult } from '@/api/analysis'
import HealthRadar from '@/components/charts/HealthRadar.vue'
import * as echarts from 'echarts'

// 状态
const repos = ref(['apache/dubbo', 'vuejs/vue'])
const isLoading = ref(false)
const compareResult = ref<CompareResponse | null>(null)
const error = ref<string | null>(null)
const barChartRef = ref<HTMLElement | null>(null)
const radarChartRef = ref<HTMLElement | null>(null)

// 计算属性
const validResults = computed(() => 
  compareResult.value?.comparisons.filter(r => !r.error) || []
)

const hasResults = computed(() => validResults.value.length > 0)

// 预设仓库
const presetRepos = [
  { name: 'apache/dubbo', label: 'Apache Dubbo' },
  { name: 'vuejs/vue', label: 'Vue.js' },
  { name: 'facebook/react', label: 'React' },
  { name: 'kubernetes/kubernetes', label: 'Kubernetes' },
  { name: 'microsoft/vscode', label: 'VS Code' },
  { name: 'golang/go', label: 'Go' },
  { name: 'tensorflow/tensorflow', label: 'TensorFlow' },
  { name: 'X-lab2017/open-digger', label: 'OpenDigger' },
]

// 方法
function addRepo() {
  if (repos.value.length < 5) {
    repos.value.push('')
  }
}

function removeRepo(index: number) {
  if (repos.value.length > 2) {
    repos.value.splice(index, 1)
  }
}

function selectPreset(repoName: string, index: number) {
  repos.value[index] = repoName
}

async function compare() {
  const validRepos = repos.value.filter(r => r.trim())
  if (validRepos.length < 2) {
    error.value = '请至少输入两个仓库进行对比'
    return
  }
  
  isLoading.value = true
  error.value = null
  compareResult.value = null
  
  try {
    compareResult.value = await analysisApi.compareRepos(validRepos)
    
    // 渲染图表
    setTimeout(() => {
      renderBarChart()
      renderRadarChart()
    }, 100)
  } catch (e: any) {
    error.value = e.message || '对比分析失败'
  } finally {
    isLoading.value = false
  }
}

function renderBarChart() {
  if (!barChartRef.value || !hasResults.value) return
  
  const chart = echarts.init(barChartRef.value)
  
  const dimensions = ['活跃度', '社区健康', '维护响应', '增长趋势', '总体评分']
  const series = validResults.value.map((result, index) => ({
    name: result.repo,
    type: 'bar',
    data: [
      result.health_score?.activity || 0,
      result.health_score?.community || 0,
      result.health_score?.maintenance || 0,
      result.health_score?.growth || 0,
      result.health_score?.overall || 0,
    ],
    itemStyle: {
      borderRadius: [4, 4, 0, 0],
    },
    emphasis: {
      focus: 'series'
    }
  }))
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(139, 92, 246, 0.3)',
      textStyle: {
        color: '#fff'
      }
    },
    legend: {
      data: validResults.value.map(r => r.repo),
      textStyle: {
        color: '#94a3b8'
      },
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dimensions,
      axisLine: {
        lineStyle: {
          color: 'rgba(255,255,255,0.1)'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLine: {
        lineStyle: {
          color: 'rgba(255,255,255,0.1)'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255,255,255,0.05)'
        }
      }
    },
    color: ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'],
    series
  }
  
  chart.setOption(option)
  
  // 响应式
  window.addEventListener('resize', () => chart.resize())
}

function renderRadarChart() {
  if (!radarChartRef.value || !hasResults.value) return
  
  const chart = echarts.init(radarChartRef.value)
  
  const indicator = [
    { name: '活跃度', max: 100 },
    { name: '社区健康', max: 100 },
    { name: '维护响应', max: 100 },
    { name: '增长趋势', max: 100 },
  ]
  
  const series = validResults.value.map((result, index) => ({
    value: [
      result.health_score?.activity || 0,
      result.health_score?.community || 0,
      result.health_score?.maintenance || 0,
      result.health_score?.growth || 0,
    ],
    name: result.repo,
    areaStyle: {
      opacity: 0.2
    }
  }))
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(139, 92, 246, 0.3)',
      textStyle: {
        color: '#fff'
      }
    },
    legend: {
      data: validResults.value.map(r => r.repo),
      textStyle: {
        color: '#94a3b8'
      },
      bottom: 0
    },
    radar: {
      indicator,
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: '#94a3b8'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255,255,255,0.1)'
        }
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(139, 92, 246, 0.02)', 'rgba(139, 92, 246, 0.04)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(255,255,255,0.1)'
        }
      }
    },
    color: ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'],
    series: [{
      type: 'radar',
      data: series
    }]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

async function exportMarkdown() {
  const validRepos = repos.value.filter(r => r.trim())
  try {
    const blob = await analysisApi.exportMarkdown(validRepos)
    downloadBlob(blob, `compare_report_${Date.now()}.md`)
  } catch (e) {
    error.value = '导出失败'
  }
}

async function exportJson() {
  const validRepos = repos.value.filter(r => r.trim())
  try {
    const blob = await analysisApi.exportJson(validRepos)
    downloadBlob(blob, `compare_report_${Date.now()}.json`)
  } catch (e) {
    error.value = '导出失败'
  }
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function getScoreClass(score: number): string {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-green-400'
  if (score >= 40) return 'text-yellow-400'
  return 'text-red-400'
}

function getRankEmoji(rank: number): string {
  if (rank === 1) return '🥇'
  if (rank === 2) return '🥈'
  if (rank === 3) return '🥉'
  return `#${rank}`
}
</script>

<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-3">
          <span class="text-3xl">⚖️</span>
          项目对比分析
        </h1>
        <p class="text-slate-400 mt-1">对比多个开源项目的健康度指标，发现最佳实践</p>
      </div>
      
      <!-- 导出按钮 -->
      <div v-if="hasResults" class="flex gap-2">
        <button
          @click="exportMarkdown"
          class="px-4 py-2 bg-surface border border-white/10 text-slate-300 rounded-xl hover:border-accent/50 hover:text-white transition-all flex items-center gap-2"
        >
          <span>📄</span>
          导出 Markdown
        </button>
        <button
          @click="exportJson"
          class="px-4 py-2 bg-surface border border-white/10 text-slate-300 rounded-xl hover:border-accent/50 hover:text-white transition-all flex items-center gap-2"
        >
          <span>📦</span>
          导出 JSON
        </button>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="glass p-6 rounded-2xl">
      <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <span>📝</span>
        选择要对比的项目
      </h2>
      
      <div class="space-y-4">
        <div
          v-for="(repo, index) in repos"
          :key="index"
          class="flex gap-3 items-start"
        >
          <div class="flex-1">
            <div class="relative">
              <input
                v-model="repos[index]"
                type="text"
                :placeholder="`仓库 ${index + 1}，如 apache/dubbo`"
                class="w-full bg-surface border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-accent/50 pr-12"
              />
              <span class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500">
                {{ index + 1 }}
              </span>
            </div>
            
            <!-- 预设快捷选择 -->
            <div class="flex flex-wrap gap-2 mt-2">
              <button
                v-for="preset in presetRepos.slice(0, 4)"
                :key="preset.name"
                @click="selectPreset(preset.name, index)"
                class="px-2 py-1 text-xs bg-surface-light/50 text-slate-400 rounded-lg hover:bg-accent/20 hover:text-accent-light transition-colors"
              >
                {{ preset.label }}
              </button>
            </div>
          </div>
          
          <button
            v-if="repos.length > 2"
            @click="removeRepo(index)"
            class="px-4 py-3 bg-red-500/10 text-red-400 rounded-xl hover:bg-red-500/20 transition-colors"
            title="删除"
          >
            ✕
          </button>
        </div>
      </div>
      
      <div class="flex gap-4 mt-6">
        <button
          v-if="repos.length < 5"
          @click="addRepo"
          class="px-4 py-2.5 bg-surface-light text-slate-300 rounded-xl hover:bg-surface hover:text-white transition-colors flex items-center gap-2"
        >
          <span>+</span>
          添加仓库
        </button>
        <button
          @click="compare"
          :disabled="isLoading"
          class="px-6 py-2.5 bg-gradient-to-r from-accent to-primary-500 text-white font-semibold rounded-xl hover:opacity-90 disabled:opacity-50 transition-all shadow-lg shadow-accent/25 flex items-center gap-2"
        >
          <span v-if="isLoading" class="animate-spin">⏳</span>
          <span v-else>🔍</span>
          {{ isLoading ? '分析中...' : '开始对比' }}
        </button>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="error" class="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
        {{ error }}
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="text-center py-16">
      <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-accent/20 mb-4">
        <span class="text-4xl animate-bounce">⚖️</span>
      </div>
      <div class="loading-dots mb-4 justify-center">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <p class="text-slate-400">正在分析项目数据...</p>
      <p class="text-sm text-slate-500 mt-2">从 OpenDigger 获取指标中</p>
    </div>
    
    <!-- 对比结果 -->
    <template v-else-if="hasResults">
      <!-- 冠军卡片 -->
      <div v-if="compareResult?.winner" class="glass p-6 rounded-2xl bg-gradient-to-r from-accent/10 to-primary-500/10 border border-accent/30">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="text-5xl">🏆</div>
            <div>
              <div class="text-sm text-accent-light mb-1">综合评分最高</div>
              <h3 class="text-2xl font-bold text-white">{{ compareResult.winner }}</h3>
            </div>
          </div>
          <div class="text-right">
            <div class="text-4xl font-bold text-accent-light">
              {{ compareResult.summary.best_overall.score }}
            </div>
            <div class="text-sm text-slate-400">总体评分</div>
          </div>
        </div>
      </div>
      
      <!-- 汇总统计 -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div class="glass p-4 rounded-xl text-center">
          <div class="text-2xl font-bold text-white">{{ compareResult?.summary.valid_repos }}</div>
          <div class="text-sm text-slate-400">对比项目</div>
        </div>
        <div class="glass p-4 rounded-xl text-center">
          <div class="text-2xl font-bold text-accent-light">{{ compareResult?.summary.average_score }}</div>
          <div class="text-sm text-slate-400">平均评分</div>
        </div>
        <div class="glass p-4 rounded-xl text-center">
          <div class="text-lg font-bold text-emerald-400 truncate">{{ compareResult?.summary.best_activity.repo.split('/')[1] }}</div>
          <div class="text-sm text-slate-400">活跃度最佳</div>
        </div>
        <div class="glass p-4 rounded-xl text-center">
          <div class="text-lg font-bold text-cyan-400 truncate">{{ compareResult?.summary.best_community.repo.split('/')[1] }}</div>
          <div class="text-sm text-slate-400">社区最佳</div>
        </div>
        <div class="glass p-4 rounded-xl text-center">
          <div class="text-lg font-bold text-yellow-400 truncate">{{ compareResult?.summary.best_growth.repo.split('/')[1] }}</div>
          <div class="text-sm text-slate-400">增长最佳</div>
        </div>
      </div>
      
      <!-- 图表区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 柱状图对比 -->
        <div class="glass p-6 rounded-2xl">
          <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span>📊</span>
            维度对比
          </h3>
          <div ref="barChartRef" class="w-full h-80"></div>
        </div>
        
        <!-- 雷达图对比 -->
        <div class="glass p-6 rounded-2xl">
          <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span>🎯</span>
            雷达图对比
          </h3>
          <div ref="radarChartRef" class="w-full h-80"></div>
        </div>
      </div>
      
      <!-- 详细对比表格 -->
      <div class="glass p-6 rounded-2xl overflow-x-auto">
        <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span>📋</span>
          详细数据对比
        </h3>
        
        <table class="w-full min-w-[600px]">
          <thead>
            <tr class="border-b border-white/10">
              <th class="text-left py-3 px-4 text-slate-400 font-medium">排名</th>
              <th class="text-left py-3 px-4 text-slate-400 font-medium">项目</th>
              <th class="text-center py-3 px-4 text-slate-400 font-medium">总体评分</th>
              <th class="text-center py-3 px-4 text-slate-400 font-medium">活跃度</th>
              <th class="text-center py-3 px-4 text-slate-400 font-medium">社区健康</th>
              <th class="text-center py-3 px-4 text-slate-400 font-medium">维护响应</th>
              <th class="text-center py-3 px-4 text-slate-400 font-medium">增长趋势</th>
              <th class="text-center py-3 px-4 text-slate-400 font-medium">OpenRank</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="result in validResults"
              :key="result.repo"
              class="border-b border-white/5 hover:bg-surface-light/30 transition-colors"
            >
              <td class="py-4 px-4">
                <span class="text-2xl">{{ getRankEmoji(result.rank || 0) }}</span>
              </td>
              <td class="py-4 px-4">
                <div class="font-medium text-white">{{ result.repo }}</div>
                <div class="text-xs text-slate-500 mt-1">
                  {{ result.health_score?.summary?.slice(0, 30) }}...
                </div>
              </td>
              <td class="text-center py-4 px-4">
                <span :class="['text-2xl font-bold', getScoreClass(result.health_score?.overall || 0)]">
                  {{ result.health_score?.overall }}
                </span>
              </td>
              <td class="text-center py-4 px-4 text-white">
                {{ result.health_score?.activity }}
              </td>
              <td class="text-center py-4 px-4 text-white">
                {{ result.health_score?.community }}
              </td>
              <td class="text-center py-4 px-4 text-white">
                {{ result.health_score?.maintenance }}
              </td>
              <td class="text-center py-4 px-4 text-white">
                {{ result.health_score?.growth }}
              </td>
              <td class="text-center py-4 px-4">
                <span class="text-accent-light font-semibold">
                  {{ result.metrics?.openrank?.toFixed(1) || 'N/A' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 各项目详细卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="result in validResults"
          :key="result.repo"
          class="glass p-6 rounded-2xl"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <span class="text-2xl">{{ getRankEmoji(result.rank || 0) }}</span>
              <div>
                <h4 class="text-white font-semibold">{{ result.repo.split('/')[1] }}</h4>
                <div class="text-xs text-slate-500">{{ result.repo }}</div>
              </div>
            </div>
            <div :class="['text-3xl font-bold', getScoreClass(result.health_score?.overall || 0)]">
              {{ result.health_score?.overall }}
            </div>
          </div>
          
          <!-- 迷你雷达图 -->
          <HealthRadar 
            :health-score="{
              overall: result.health_score?.overall || 0,
              activity: result.health_score?.activity || 0,
              community: result.health_score?.community || 0,
              maintenance: result.health_score?.maintenance || 0,
              growth: result.health_score?.growth || 0
            }" 
          />
          
          <!-- 亮点和关注点 -->
          <div class="mt-4 space-y-2">
            <div v-if="result.health_score?.highlights?.length" class="space-y-1">
              <div v-for="h in result.health_score.highlights.slice(0, 2)" :key="h" class="text-xs text-green-400 flex items-center gap-1">
                <span>✓</span> {{ h }}
              </div>
            </div>
            <div v-if="result.health_score?.concerns?.length" class="space-y-1">
              <div v-for="c in result.health_score.concerns.slice(0, 2)" :key="c" class="text-xs text-yellow-400 flex items-center gap-1">
                <span>⚠</span> {{ c }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
    
    <!-- 空状态 -->
    <div v-else class="text-center py-20">
      <div class="inline-flex items-center justify-center w-24 h-24 rounded-2xl bg-gradient-to-br from-accent/20 to-primary-500/20 border border-accent/30 mb-6">
        <span class="text-5xl">⚖️</span>
      </div>
      <h2 class="text-2xl font-bold text-white mb-4">项目对比分析</h2>
      <p class="text-slate-400 max-w-md mx-auto mb-8">
        输入2-5个开源项目仓库地址，全方位对比它们的健康度指标，
        找出最佳实践和改进空间。
      </p>
      <div class="flex flex-wrap justify-center gap-3">
        <span class="px-3 py-1.5 bg-surface border border-white/10 rounded-lg text-sm text-slate-400">
          📊 多维度评分对比
        </span>
        <span class="px-3 py-1.5 bg-surface border border-white/10 rounded-lg text-sm text-slate-400">
          📈 趋势图表展示
        </span>
        <span class="px-3 py-1.5 bg-surface border border-white/10 rounded-lg text-sm text-slate-400">
          📄 报告导出功能
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.loading-dots {
  display: flex;
  gap: 4px;
}
.loading-dots span {
  width: 8px;
  height: 8px;
  background: #8b5cf6;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
