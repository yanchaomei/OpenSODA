<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import HealthRadar from '@/components/charts/HealthRadar.vue'
import TrendChart from '@/components/charts/TrendChart.vue'
import MetricCard from '@/components/analysis/MetricCard.vue'
import AISummaryCard from '@/components/analysis/AISummaryCard.vue'
import ShareCard from '@/components/analysis/ShareCard.vue'
import AnalysisSkeleton from '@/components/common/AnalysisSkeleton.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import ContributorHeatmap from '@/components/charts/ContributorHeatmap.vue'

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

// 推荐对比的项目
const recommendedCompare = computed(() => {
  if (!analysisStore.currentAnalysis) return []
  const current = analysisStore.currentAnalysis.repo
  const recommendations = [
    { repo: 'vuejs/vue', reason: '前端框架' },
    { repo: 'facebook/react', reason: '前端框架' },
    { repo: 'apache/dubbo', reason: 'Java 生态' },
    { repo: 'kubernetes/kubernetes', reason: '云原生' },
    { repo: 'tensorflow/tensorflow', reason: 'AI/ML' },
  ]
  return recommendations.filter(r => r.repo !== current).slice(0, 3)
})

async function analyzeRepo() {
  if (repoInput.value.trim()) {
    // 解析输入，支持完整 GitHub URL
    let repoPath = repoInput.value.trim()
    if (repoPath.includes('github.com/')) {
      repoPath = repoPath.split('github.com/')[1].replace(/\/$/, '')
    }
    router.push(`/analysis/${repoPath}`)
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

function goToCompare(compareRepo: string) {
  router.push({
    path: '/compare',
    query: { repos: [repo.value, compareRepo].join(',') }
  })
}

function retry() {
  loadAnalysis()
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
    <div class="glass p-6 rounded-2xl">
      <div class="flex gap-4">
        <div class="flex-1 relative">
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">🔍</span>
          <input
            v-model="repoInput"
            @keyup.enter="analyzeRepo"
            type="text"
            placeholder="输入仓库地址，如 apache/dubbo 或 https://github.com/apache/dubbo"
            class="w-full bg-surface border border-white/10 rounded-xl pl-12 pr-4 py-3.5 text-white placeholder-slate-500 focus:outline-none focus:border-accent/50 transition-colors"
          />
        </div>
        <button
          @click="analyzeRepo"
          :disabled="analysisStore.isLoading"
          class="px-8 py-3.5 bg-gradient-to-r from-accent to-primary-500 text-white font-semibold rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-accent/25 flex items-center gap-2"
        >
          <span v-if="analysisStore.isLoading" class="animate-spin">⏳</span>
          <span v-else>🚀</span>
          {{ analysisStore.isLoading ? '分析中...' : '开始分析' }}
        </button>
      </div>
      
      <!-- 快捷示例 -->
      <div class="flex items-center gap-2 mt-3">
        <span class="text-xs text-slate-500">快速试试:</span>
        <button
          v-for="demo in ['apache/dubbo', 'vuejs/vue', 'X-lab2017/open-digger']"
          :key="demo"
          @click="repoInput = demo; analyzeRepo()"
          class="px-2 py-1 text-xs bg-surface-light/30 text-slate-400 rounded-lg hover:bg-accent/20 hover:text-accent-light transition-colors"
        >
          {{ demo }}
        </button>
      </div>
    </div>
    
    <!-- 加载状态 - 骨架屏 -->
    <AnalysisSkeleton v-if="analysisStore.isLoading" />
    
    <!-- 错误状态 -->
    <ErrorState
      v-else-if="analysisStore.error"
      :message="analysisStore.error"
      type="error"
      @retry="retry"
    />
    
    <!-- 分析结果 -->
    <template v-else-if="analysisStore.currentAnalysis">
      <!-- 项目信息头 + 分享按钮 -->
      <div class="glass p-6 rounded-2xl">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h2 class="text-2xl font-bold text-white">
                {{ analysisStore.currentAnalysis.repo }}
              </h2>
              <a 
                :href="`https://github.com/${analysisStore.currentAnalysis.repo}`"
                target="_blank"
                class="text-slate-400 hover:text-white transition-colors"
              >
                ↗
              </a>
            </div>
            <p class="text-slate-400 mb-4">
              {{ analysisStore.currentAnalysis.repoInfo?.description || '暂无描述' }}
            </p>
            <div class="flex items-center gap-6 text-sm">
              <span class="flex items-center gap-1.5 text-slate-400">
                <span>⭐</span>
                <span class="text-white font-medium">{{ analysisStore.currentAnalysis.repoInfo?.stars?.toLocaleString() || 0 }}</span>
              </span>
              <span class="flex items-center gap-1.5 text-slate-400">
                <span>🍴</span>
                <span class="text-white font-medium">{{ analysisStore.currentAnalysis.repoInfo?.forks?.toLocaleString() || 0 }}</span>
              </span>
              <span class="flex items-center gap-1.5 text-slate-400">
                <span>📝</span>
                <span class="text-white font-medium">{{ analysisStore.currentAnalysis.repoInfo?.language || '未知' }}</span>
              </span>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <!-- 分享按钮 -->
            <ShareCard
              :repo="analysisStore.currentAnalysis.repo"
              :health-score="analysisStore.currentAnalysis.healthScore.overall"
              :metrics="analysisStore.currentAnalysis.metrics"
            />
            
            <!-- 健康度评分 -->
            <div class="text-center">
              <div
                :class="[
                  'text-5xl font-bold',
                  analysisStore.getScoreClass(analysisStore.currentAnalysis.healthScore.overall)
                ]"
              >
                {{ analysisStore.currentAnalysis.healthScore.overall }}
              </div>
              <div class="text-slate-400 mt-1 text-sm">
                {{ analysisStore.getScoreLabel(analysisStore.currentAnalysis.healthScore.overall) }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- AI 摘要卡片 -->
      <AISummaryCard
        :repo="analysisStore.currentAnalysis.repo"
        :health-score="analysisStore.currentAnalysis.healthScore.overall"
        :summary="analysisStore.currentAnalysis.healthScore.summary"
        :highlights="analysisStore.currentAnalysis.healthScore.highlights"
        :concerns="analysisStore.currentAnalysis.healthScore.concerns"
      />
      
      <!-- 指标卡片 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
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
      
      <!-- 图表区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="glass p-6 rounded-2xl">
          <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span>🎯</span>
            健康度雷达
          </h3>
          <HealthRadar :health-score="analysisStore.currentAnalysis.healthScore" size="lg" />
        </div>
        <div class="glass p-6 rounded-2xl">
          <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span>📈</span>
            OpenRank 趋势
          </h3>
          <TrendChart
            v-if="analysisStore.currentAnalysis.trends?.openrank"
            :data="analysisStore.currentAnalysis.trends.openrank"
            metric-name="OpenRank"
          />
          <div v-else class="h-64 flex items-center justify-center text-slate-500">
            <div class="text-center">
              <span class="text-4xl mb-2 block">📊</span>
              <p>暂无趋势数据</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 贡献热力图 -->
      <div class="glass p-6 rounded-2xl">
        <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span>🔥</span>
          贡献活跃度热力图
        </h3>
        <ContributorHeatmap title="" />
      </div>
      
      <!-- 详细指标 -->
      <div class="glass p-6 rounded-2xl">
        <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span>📋</span>
          详细指标
        </h3>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div class="p-4 bg-surface-light/20 rounded-xl text-center">
            <div class="text-sm text-slate-400 mb-1">OpenRank</div>
            <div class="text-2xl font-bold text-accent-light">
              {{ analysisStore.currentAnalysis.metrics.openrank?.toFixed(1) || 'N/A' }}
            </div>
          </div>
          <div class="p-4 bg-surface-light/20 rounded-xl text-center">
            <div class="text-sm text-slate-400 mb-1">参与者</div>
            <div class="text-2xl font-bold text-white">
              {{ analysisStore.currentAnalysis.metrics.total_participants || 'N/A' }}
            </div>
          </div>
          <div class="p-4 bg-surface-light/20 rounded-xl text-center">
            <div class="text-sm text-slate-400 mb-1">巴士因子</div>
            <div class="text-2xl font-bold text-white">
              {{ analysisStore.currentAnalysis.metrics.bus_factor || 'N/A' }}
            </div>
          </div>
          <div class="p-4 bg-surface-light/20 rounded-xl text-center">
            <div class="text-sm text-slate-400 mb-1">PR 合并率</div>
            <div class="text-2xl font-bold text-white">
              {{ analysisStore.currentAnalysis.metrics.merge_rate 
                ? (analysisStore.currentAnalysis.metrics.merge_rate * 100).toFixed(0) + '%' 
                : 'N/A' }}
            </div>
          </div>
          <div class="p-4 bg-surface-light/20 rounded-xl text-center">
            <div class="text-sm text-slate-400 mb-1">新贡献者</div>
            <div class="text-2xl font-bold text-white">
              {{ analysisStore.currentAnalysis.metrics.new_contributors || 'N/A' }}
            </div>
          </div>
          <div class="p-4 bg-surface-light/20 rounded-xl text-center">
            <div class="text-sm text-slate-400 mb-1">活跃度</div>
            <div class="text-2xl font-bold text-white">
              {{ analysisStore.currentAnalysis.metrics.activity?.toFixed(1) || 'N/A' }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- 推荐对比 -->
      <div class="glass p-6 rounded-2xl">
        <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span>⚖️</span>
          推荐对比
        </h3>
        <div class="flex flex-wrap gap-3">
          <button
            v-for="rec in recommendedCompare"
            :key="rec.repo"
            @click="goToCompare(rec.repo)"
            class="px-4 py-2.5 bg-surface-light/20 rounded-xl hover:bg-accent/20 hover:border-accent/30 border border-transparent transition-all flex items-center gap-2"
          >
            <span class="text-white">{{ rec.repo }}</span>
            <span class="text-xs text-slate-500">{{ rec.reason }}</span>
          </button>
          <router-link
            to="/compare"
            class="px-4 py-2.5 text-accent-light hover:text-accent transition-colors flex items-center gap-1"
          >
            更多对比 →
          </router-link>
        </div>
      </div>
    </template>
    
    <!-- 空状态 -->
    <div v-else class="text-center py-20">
      <div class="inline-flex items-center justify-center w-24 h-24 rounded-2xl bg-gradient-to-br from-accent/20 to-primary-500/20 border border-accent/30 mb-6">
        <span class="text-5xl">🔍</span>
      </div>
      <h2 class="text-2xl font-bold text-white mb-4">分析开源项目</h2>
      <p class="text-slate-400 max-w-md mx-auto mb-8">
        输入 GitHub 仓库地址，获取基于 OpenDigger 数据的<br>
        全面健康度分析报告
      </p>
      <div class="flex flex-wrap justify-center gap-3">
        <span class="px-3 py-1.5 bg-surface border border-white/10 rounded-lg text-sm text-slate-400">
          🏥 健康度评估
        </span>
        <span class="px-3 py-1.5 bg-surface border border-white/10 rounded-lg text-sm text-slate-400">
          📊 多维度指标
        </span>
        <span class="px-3 py-1.5 bg-surface border border-white/10 rounded-lg text-sm text-slate-400">
          💡 AI 建议
        </span>
      </div>
    </div>
  </div>
</template>
