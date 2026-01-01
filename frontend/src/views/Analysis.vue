<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import HealthRadar from '@/components/charts/HealthRadar.vue'
import TrendChart from '@/components/charts/TrendChart.vue'
import MetricCard from '@/components/analysis/MetricCard.vue'

const route = useRoute()
const router = useRouter()
const analysisStore = useAnalysisStore()

const repoInput = ref('')

const repo = computed(() => {
  const params = route.params.repo
  if (Array.isArray(params)) {
    return params.join('/')
  }
  return params || ''
})

async function analyzeRepo() {
  if (repoInput.value.trim()) {
    router.push(`/analysis/${repoInput.value}`)
  }
}

async function loadAnalysis() {
  if (repo.value) {
    try {
      await analysisStore.analyzeRepo(repo.value)
    } catch (e) {
      console.error('Analysis failed:', e)
    }
  }
}

onMounted(() => {
  if (repo.value) {
    repoInput.value = repo.value
    loadAnalysis()
  }
})

watch(repo, (newRepo) => {
  if (newRepo) {
    repoInput.value = newRepo
    loadAnalysis()
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- 搜索框 -->
    <div class="glass p-6">
      <div class="flex gap-4">
        <input
          v-model="repoInput"
          @keyup.enter="analyzeRepo"
          type="text"
          placeholder="输入仓库地址，如 apache/dubbo 或 https://github.com/apache/dubbo"
          class="flex-1 bg-surface border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-accent/50"
        />
        <button
          @click="analyzeRepo"
          :disabled="analysisStore.isLoading"
          class="px-6 py-3 bg-accent text-white font-semibold rounded-xl hover:bg-accent-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ analysisStore.isLoading ? '分析中...' : '开始分析' }}
        </button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="analysisStore.isLoading" class="text-center py-12">
      <div class="loading-dots mb-4 justify-center">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <p class="text-slate-400">正在分析 {{ repo }}...</p>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="analysisStore.error" class="glass p-6 text-center">
      <div class="text-4xl mb-4">😢</div>
      <p class="text-red-400">{{ analysisStore.error }}</p>
    </div>
    
    <!-- 分析结果 -->
    <template v-else-if="analysisStore.currentAnalysis">
      <!-- 项目信息头 -->
      <div class="glass p-6">
        <div class="flex items-start justify-between">
          <div>
            <h2 class="text-2xl font-bold text-white mb-2">
              {{ analysisStore.currentAnalysis.repo }}
            </h2>
            <p class="text-slate-400">
              {{ analysisStore.currentAnalysis.repoInfo?.description || '暂无描述' }}
            </p>
            <div class="flex items-center gap-4 mt-4 text-sm text-slate-400">
              <span>⭐ {{ analysisStore.currentAnalysis.repoInfo?.stars?.toLocaleString() || 0 }}</span>
              <span>🍴 {{ analysisStore.currentAnalysis.repoInfo?.forks?.toLocaleString() || 0 }}</span>
              <span>📝 {{ analysisStore.currentAnalysis.repoInfo?.language || '未知' }}</span>
            </div>
          </div>
          <div class="text-right">
            <div
              :class="[
                'text-5xl font-bold',
                analysisStore.getScoreClass(analysisStore.currentAnalysis.healthScore.overall)
              ]"
            >
              {{ analysisStore.currentAnalysis.healthScore.overall }}
            </div>
            <div class="text-slate-400 mt-1">
              {{ analysisStore.getScoreLabel(analysisStore.currentAnalysis.healthScore.overall) }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- 健康度摘要 -->
      <div class="glass p-6">
        <h3 class="text-lg font-semibold text-white mb-4">健康度评估</h3>
        <p class="text-slate-300 mb-4">
          {{ analysisStore.currentAnalysis.healthScore.summary }}
        </p>
        
        <!-- 亮点 -->
        <div v-if="analysisStore.currentAnalysis.healthScore.highlights?.length" class="mb-4">
          <h4 class="text-sm text-slate-400 mb-2">✅ 亮点</h4>
          <ul class="space-y-1">
            <li
              v-for="highlight in analysisStore.currentAnalysis.healthScore.highlights"
              :key="highlight"
              class="text-green-400 text-sm"
            >
              • {{ highlight }}
            </li>
          </ul>
        </div>
        
        <!-- 关注点 -->
        <div v-if="analysisStore.currentAnalysis.healthScore.concerns?.length">
          <h4 class="text-sm text-slate-400 mb-2">⚠️ 需关注</h4>
          <ul class="space-y-1">
            <li
              v-for="concern in analysisStore.currentAnalysis.healthScore.concerns"
              :key="concern"
              class="text-yellow-400 text-sm"
            >
              • {{ concern }}
            </li>
          </ul>
        </div>
      </div>
      
      <!-- 指标卡片 -->
      <div class="grid grid-cols-4 gap-4">
        <MetricCard
          title="活跃度"
          :value="analysisStore.currentAnalysis.healthScore.activity"
          :max="100"
          icon="🔥"
        />
        <MetricCard
          title="社区健康度"
          :value="analysisStore.currentAnalysis.healthScore.community"
          :max="100"
          icon="👥"
        />
        <MetricCard
          title="维护响应度"
          :value="analysisStore.currentAnalysis.healthScore.maintenance"
          :max="100"
          icon="🔧"
        />
        <MetricCard
          title="增长趋势"
          :value="analysisStore.currentAnalysis.healthScore.growth"
          :max="100"
          icon="📈"
        />
      </div>
      
      <!-- 图表 -->
      <div class="grid grid-cols-2 gap-6">
        <div class="glass p-6">
          <h3 class="text-lg font-semibold text-white mb-4">健康度雷达</h3>
          <HealthRadar :health-score="analysisStore.currentAnalysis.healthScore" />
        </div>
        <div class="glass p-6">
          <h3 class="text-lg font-semibold text-white mb-4">OpenRank 趋势</h3>
          <TrendChart
            v-if="analysisStore.currentAnalysis.trends?.openrank"
            :data="analysisStore.currentAnalysis.trends.openrank"
            metric-name="OpenRank"
          />
          <div v-else class="h-64 flex items-center justify-center text-slate-500">
            暂无趋势数据
          </div>
        </div>
      </div>
      
      <!-- 详细指标 -->
      <div class="glass p-6">
        <h3 class="text-lg font-semibold text-white mb-4">详细指标</h3>
        <div class="grid grid-cols-3 gap-4">
          <div class="p-4 bg-surface-light/30 rounded-lg">
            <div class="text-sm text-slate-400 mb-1">OpenRank</div>
            <div class="text-2xl font-bold text-white">
              {{ analysisStore.currentAnalysis.metrics.openrank?.toFixed(2) || 'N/A' }}
            </div>
          </div>
          <div class="p-4 bg-surface-light/30 rounded-lg">
            <div class="text-sm text-slate-400 mb-1">参与者数</div>
            <div class="text-2xl font-bold text-white">
              {{ analysisStore.currentAnalysis.metrics.total_participants || 'N/A' }}
            </div>
          </div>
          <div class="p-4 bg-surface-light/30 rounded-lg">
            <div class="text-sm text-slate-400 mb-1">巴士因子</div>
            <div class="text-2xl font-bold text-white">
              {{ analysisStore.currentAnalysis.metrics.bus_factor || 'N/A' }}
            </div>
          </div>
          <div class="p-4 bg-surface-light/30 rounded-lg">
            <div class="text-sm text-slate-400 mb-1">PR 合并率</div>
            <div class="text-2xl font-bold text-white">
              {{ analysisStore.currentAnalysis.metrics.merge_rate 
                ? (analysisStore.currentAnalysis.metrics.merge_rate * 100).toFixed(1) + '%' 
                : 'N/A' }}
            </div>
          </div>
          <div class="p-4 bg-surface-light/30 rounded-lg">
            <div class="text-sm text-slate-400 mb-1">新贡献者</div>
            <div class="text-2xl font-bold text-white">
              {{ analysisStore.currentAnalysis.metrics.new_contributors || 'N/A' }}
            </div>
          </div>
          <div class="p-4 bg-surface-light/30 rounded-lg">
            <div class="text-sm text-slate-400 mb-1">活跃度</div>
            <div class="text-2xl font-bold text-white">
              {{ analysisStore.currentAnalysis.metrics.activity?.toFixed(2) || 'N/A' }}
            </div>
          </div>
        </div>
      </div>
    </template>
    
    <!-- 空状态 -->
    <div v-else class="text-center py-16">
      <div class="text-6xl mb-6">🔍</div>
      <h2 class="text-2xl font-bold text-white mb-4">分析开源项目</h2>
      <p class="text-slate-400">
        输入 GitHub 仓库地址，获取项目健康度分析报告
      </p>
    </div>
  </div>
</template>

