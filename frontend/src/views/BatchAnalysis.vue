<script setup lang="ts">
/**
 * BatchAnalysis - 批量分析页面
 * 同时分析多个项目，生成综合报告
 */
import { ref, computed } from 'vue'
import { analysisApi } from '@/api/analysis'
import HealthRadar from '@/components/charts/HealthRadar.vue'

interface BatchResult {
  repo: string
  status: 'pending' | 'loading' | 'success' | 'error'
  data?: any
  error?: string
}

const reposInput = ref('')
const results = ref<BatchResult[]>([])
const isAnalyzing = ref(false)
const exportFormat = ref<'markdown' | 'json' | 'csv'>('markdown')

// 解析输入的仓库列表
const reposList = computed(() => {
  return reposInput.value
    .split(/[\n,;]/)
    .map(r => r.trim())
    .filter(r => r && r.includes('/'))
})

// 统计信息
const stats = computed(() => {
  const completed = results.value.filter(r => r.status === 'success')
  const failed = results.value.filter(r => r.status === 'error')
  const avgScore = completed.length > 0
    ? Math.round(completed.reduce((sum, r) => sum + (r.data?.health_score?.overall || 0), 0) / completed.length)
    : 0
  
  return {
    total: results.value.length,
    completed: completed.length,
    failed: failed.length,
    avgScore
  }
})

// 开始批量分析
async function startBatchAnalysis() {
  if (reposList.value.length === 0) return
  
  isAnalyzing.value = true
  results.value = reposList.value.map(repo => ({
    repo,
    status: 'pending'
  }))
  
  // 并发分析（限制并发数为 3）
  const concurrency = 3
  const queue = [...reposList.value]
  
  async function processRepo(repo: string) {
    const index = results.value.findIndex(r => r.repo === repo)
    if (index === -1) return
    
    results.value[index].status = 'loading'
    
    try {
      const data = await analysisApi.analyzeRepo(repo)
      results.value[index] = {
        repo,
        status: 'success',
        data
      }
    } catch (e: any) {
      results.value[index] = {
        repo,
        status: 'error',
        error: e.message || '分析失败'
      }
    }
  }
  
  // 分批处理
  while (queue.length > 0) {
    const batch = queue.splice(0, concurrency)
    await Promise.all(batch.map(processRepo))
  }
  
  isAnalyzing.value = false
}

// 导出报告
function exportReport() {
  const successResults = results.value.filter(r => r.status === 'success')
  
  if (exportFormat.value === 'json') {
    const data = successResults.map(r => ({
      repo: r.repo,
      healthScore: r.data?.health_score,
      metrics: r.data?.metrics
    }))
    downloadFile(JSON.stringify(data, null, 2), 'batch_analysis.json', 'application/json')
  } else if (exportFormat.value === 'csv') {
    const headers = ['Repo', 'Overall', 'Activity', 'Community', 'Maintenance', 'Growth', 'OpenRank']
    const rows = successResults.map(r => [
      r.repo,
      r.data?.health_score?.overall || 'N/A',
      r.data?.health_score?.activity || 'N/A',
      r.data?.health_score?.community || 'N/A',
      r.data?.health_score?.maintenance || 'N/A',
      r.data?.health_score?.growth || 'N/A',
      r.data?.metrics?.openrank?.toFixed(2) || 'N/A'
    ])
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n')
    downloadFile(csv, 'batch_analysis.csv', 'text/csv')
  } else {
    let md = '# 批量分析报告\n\n'
    md += `生成时间: ${new Date().toLocaleString()}\n\n`
    md += `## 统计摘要\n\n`
    md += `- 分析项目数: ${stats.value.total}\n`
    md += `- 成功: ${stats.value.completed}\n`
    md += `- 失败: ${stats.value.failed}\n`
    md += `- 平均健康分: ${stats.value.avgScore}\n\n`
    md += `## 详细结果\n\n`
    md += `| 项目 | 总分 | 活跃度 | 社区 | 维护 | 增长 | OpenRank |\n`
    md += `|------|------|--------|------|------|------|----------|\n`
    successResults.forEach(r => {
      md += `| ${r.repo} | ${r.data?.health_score?.overall || 'N/A'} | ${r.data?.health_score?.activity || 'N/A'} | ${r.data?.health_score?.community || 'N/A'} | ${r.data?.health_score?.maintenance || 'N/A'} | ${r.data?.health_score?.growth || 'N/A'} | ${r.data?.metrics?.openrank?.toFixed(2) || 'N/A'} |\n`
    })
    downloadFile(md, 'batch_analysis.md', 'text/markdown')
  }
}

function downloadFile(content: string, filename: string, type: string) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function getScoreColor(score: number): string {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-green-400'
  if (score >= 40) return 'text-yellow-400'
  return 'text-red-400'
}

function getStatusIcon(status: string): string {
  switch (status) {
    case 'pending': return '⏳'
    case 'loading': return '🔄'
    case 'success': return '✅'
    case 'error': return '❌'
    default: return '❓'
  }
}

// 预设项目组
const presets = [
  {
    name: 'Apache 顶级项目',
    repos: ['apache/spark', 'apache/kafka', 'apache/dubbo', 'apache/flink', 'apache/hadoop']
  },
  {
    name: '前端框架',
    repos: ['vuejs/vue', 'facebook/react', 'angular/angular', 'sveltejs/svelte']
  },
  {
    name: 'AI/ML 项目',
    repos: ['tensorflow/tensorflow', 'pytorch/pytorch', 'huggingface/transformers', 'langchain-ai/langchain']
  },
  {
    name: '云原生',
    repos: ['kubernetes/kubernetes', 'docker/docker-ce', 'containerd/containerd', 'prometheus/prometheus']
  }
]

function applyPreset(preset: typeof presets[0]) {
  reposInput.value = preset.repos.join('\n')
}
</script>

<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-2xl font-bold text-white flex items-center gap-3">
        <span class="text-3xl">📦</span>
        批量分析
      </h1>
      <p class="text-slate-400 mt-1">同时分析多个开源项目，生成综合报告</p>
    </div>
    
    <!-- 输入区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 glass p-6 rounded-2xl">
        <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span>📝</span>
          输入项目列表
        </h2>
        
        <textarea
          v-model="reposInput"
          rows="8"
          placeholder="输入仓库地址，每行一个，如：
apache/dubbo
vuejs/vue
facebook/react"
          class="w-full bg-surface border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-accent/50 font-mono text-sm resize-none"
        ></textarea>
        
        <div class="flex items-center justify-between mt-4">
          <div class="text-sm text-slate-500">
            已识别 <span class="text-accent-light font-semibold">{{ reposList.length }}</span> 个项目
          </div>
          <button
            @click="startBatchAnalysis"
            :disabled="isAnalyzing || reposList.length === 0"
            class="px-6 py-2.5 bg-gradient-to-r from-accent to-primary-500 text-white font-semibold rounded-xl hover:opacity-90 disabled:opacity-50 transition-all shadow-lg shadow-accent/25 flex items-center gap-2"
          >
            <span v-if="isAnalyzing" class="animate-spin">⏳</span>
            <span v-else>🚀</span>
            {{ isAnalyzing ? '分析中...' : '开始批量分析' }}
          </button>
        </div>
      </div>
      
      <!-- 预设项目组 -->
      <div class="glass p-6 rounded-2xl">
        <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span>📁</span>
          预设项目组
        </h2>
        
        <div class="space-y-3">
          <button
            v-for="preset in presets"
            :key="preset.name"
            @click="applyPreset(preset)"
            class="w-full p-3 bg-surface-light/20 rounded-xl text-left hover:bg-accent/10 hover:border-accent/30 border border-transparent transition-all group"
          >
            <div class="text-white font-medium group-hover:text-accent-light transition-colors">
              {{ preset.name }}
            </div>
            <div class="text-xs text-slate-500 mt-1">
              {{ preset.repos.length }} 个项目
            </div>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 分析进度 -->
    <div v-if="results.length > 0" class="glass p-6 rounded-2xl">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-white flex items-center gap-2">
          <span>📊</span>
          分析结果
        </h2>
        
        <!-- 导出按钮 -->
        <div v-if="stats.completed > 0" class="flex items-center gap-3">
          <select
            v-model="exportFormat"
            class="bg-surface border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white"
          >
            <option value="markdown">Markdown</option>
            <option value="json">JSON</option>
            <option value="csv">CSV</option>
          </select>
          <button
            @click="exportReport"
            class="px-4 py-1.5 glass text-slate-300 rounded-lg hover:text-white hover:border-accent/30 transition-all flex items-center gap-2"
          >
            <span>📥</span>
            导出报告
          </button>
        </div>
      </div>
      
      <!-- 统计摘要 -->
      <div class="grid grid-cols-4 gap-4 mb-6">
        <div class="p-4 bg-surface-light/20 rounded-xl text-center">
          <div class="text-2xl font-bold text-white">{{ stats.total }}</div>
          <div class="text-sm text-slate-400">总项目数</div>
        </div>
        <div class="p-4 bg-surface-light/20 rounded-xl text-center">
          <div class="text-2xl font-bold text-emerald-400">{{ stats.completed }}</div>
          <div class="text-sm text-slate-400">分析成功</div>
        </div>
        <div class="p-4 bg-surface-light/20 rounded-xl text-center">
          <div class="text-2xl font-bold text-red-400">{{ stats.failed }}</div>
          <div class="text-sm text-slate-400">分析失败</div>
        </div>
        <div class="p-4 bg-surface-light/20 rounded-xl text-center">
          <div :class="['text-2xl font-bold', getScoreColor(stats.avgScore)]">{{ stats.avgScore }}</div>
          <div class="text-sm text-slate-400">平均健康分</div>
        </div>
      </div>
      
      <!-- 结果列表 -->
      <div class="space-y-3">
        <div
          v-for="result in results"
          :key="result.repo"
          :class="[
            'p-4 rounded-xl border transition-all',
            result.status === 'loading' ? 'bg-accent/5 border-accent/30' :
            result.status === 'success' ? 'bg-surface-light/20 border-white/5' :
            result.status === 'error' ? 'bg-red-500/5 border-red-500/30' :
            'bg-surface-light/10 border-white/5'
          ]"
        >
          <div class="flex items-center gap-4">
            <span class="text-xl">{{ getStatusIcon(result.status) }}</span>
            <div class="flex-1 min-w-0">
              <div class="text-white font-medium">{{ result.repo }}</div>
              <div v-if="result.error" class="text-sm text-red-400 mt-1">{{ result.error }}</div>
              <div v-else-if="result.data?.health_score?.summary" class="text-sm text-slate-400 mt-1 truncate">
                {{ result.data.health_score.summary }}
              </div>
            </div>
            <div v-if="result.status === 'success'" class="flex items-center gap-6">
              <div :class="['text-3xl font-bold', getScoreColor(result.data?.health_score?.overall || 0)]">
                {{ result.data?.health_score?.overall }}
              </div>
              <div class="w-24 h-24">
                <HealthRadar
                  v-if="result.data?.health_score"
                  :health-score="result.data.health_score"
                  size="sm"
                  :show-label="false"
                />
              </div>
            </div>
            <div v-else-if="result.status === 'loading'" class="animate-spin text-2xl">
              🔄
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div v-else class="text-center py-20">
      <div class="inline-flex items-center justify-center w-24 h-24 rounded-2xl bg-gradient-to-br from-accent/20 to-primary-500/20 border border-accent/30 mb-6">
        <span class="text-5xl">📦</span>
      </div>
      <h2 class="text-2xl font-bold text-white mb-4">批量分析多个项目</h2>
      <p class="text-slate-400 max-w-md mx-auto">
        输入多个 GitHub 仓库地址，一次性分析它们的健康度，<br>
        生成综合对比报告。
      </p>
    </div>
  </div>
</template>

