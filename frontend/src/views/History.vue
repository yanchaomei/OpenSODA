<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'

const router = useRouter()
const analysisStore = useAnalysisStore()

const hasHistory = computed(() => analysisStore.recentAnalyses.length > 0)

function viewAnalysis(repo: string) {
  router.push({ name: 'Analysis', query: { repo } })
}

function compareSelected() {
  const repos = analysisStore.recentAnalyses.slice(0, 5).map(a => a.repo)
  if (repos.length >= 2) {
    router.push({ name: 'Compare', query: { repos: repos.join(',') } })
  }
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getScoreClass(score: number): string {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-green-400'
  if (score >= 40) return 'text-yellow-400'
  return 'text-red-400'
}

function getScoreBg(score: number): string {
  if (score >= 80) return 'bg-emerald-500/20 border-emerald-500/30'
  if (score >= 60) return 'bg-green-500/20 border-green-500/30'
  if (score >= 40) return 'bg-yellow-500/20 border-yellow-500/30'
  return 'bg-red-500/20 border-red-500/30'
}
</script>

<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-3">
          <span class="text-3xl">📜</span>
          分析历史
        </h1>
        <p class="text-slate-400 mt-1">查看历史分析记录，快速回顾项目状态</p>
      </div>
      
      <div class="flex gap-3">
        <button
          v-if="hasHistory && analysisStore.recentAnalyses.length >= 2"
          @click="compareSelected"
          class="px-4 py-2 bg-surface border border-white/10 text-slate-300 rounded-xl hover:border-accent/50 hover:text-white transition-all flex items-center gap-2"
        >
          <span>⚖️</span>
          对比全部
        </button>
        <button
          v-if="hasHistory"
          @click="analysisStore.clearHistory()"
          class="px-4 py-2 bg-red-500/10 text-red-400 rounded-xl hover:bg-red-500/20 transition-colors flex items-center gap-2"
        >
          <span>🗑️</span>
          清空历史
        </button>
      </div>
    </div>
    
    <!-- 历史列表 -->
    <div v-if="hasHistory" class="space-y-4">
      <TransitionGroup name="list">
        <div
          v-for="analysis in analysisStore.recentAnalyses"
          :key="analysis.repo"
          class="glass p-6 rounded-2xl hover:border-accent/30 border border-transparent transition-all cursor-pointer group"
          @click="viewAnalysis(analysis.repo)"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <!-- 评分徽章 -->
              <div 
                :class="[
                  'w-16 h-16 rounded-xl flex items-center justify-center border',
                  getScoreBg(analysis.healthScore.overall)
                ]"
              >
                <span :class="['text-2xl font-bold', getScoreClass(analysis.healthScore.overall)]">
                  {{ analysis.healthScore.overall }}
                </span>
              </div>
              
              <div>
                <h3 class="text-lg font-semibold text-white group-hover:text-accent-light transition-colors">
                  {{ analysis.repo }}
                </h3>
                <p class="text-sm text-slate-500 mt-1">
                  {{ analysis.healthScore.summary?.slice(0, 50) }}...
                </p>
                <div class="flex items-center gap-4 mt-2 text-xs text-slate-500">
                  <span>📅 {{ formatDate(analysis.analyzedAt) }}</span>
                  <span v-if="analysis.metrics?.openrank">
                    📈 OpenRank: {{ analysis.metrics.openrank.toFixed(1) }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="flex items-center gap-4">
              <!-- 维度评分 -->
              <div class="hidden md:flex gap-3">
                <div class="text-center">
                  <div class="text-sm font-semibold text-white">{{ analysis.healthScore.activity }}</div>
                  <div class="text-xs text-slate-500">活跃度</div>
                </div>
                <div class="text-center">
                  <div class="text-sm font-semibold text-white">{{ analysis.healthScore.community }}</div>
                  <div class="text-xs text-slate-500">社区</div>
                </div>
                <div class="text-center">
                  <div class="text-sm font-semibold text-white">{{ analysis.healthScore.maintenance }}</div>
                  <div class="text-xs text-slate-500">维护</div>
                </div>
                <div class="text-center">
                  <div class="text-sm font-semibold text-white">{{ analysis.healthScore.growth }}</div>
                  <div class="text-xs text-slate-500">增长</div>
                </div>
              </div>
              
              <!-- 操作按钮 -->
              <div class="flex gap-2">
                <button
                  @click.stop="viewAnalysis(analysis.repo)"
                  class="px-3 py-1.5 bg-accent/20 text-accent-light rounded-lg hover:bg-accent/30 transition-colors text-sm"
                >
                  查看详情
                </button>
                <button
                  @click.stop="analysisStore.removeFromHistory(analysis.repo)"
                  class="px-3 py-1.5 bg-surface-light text-slate-400 rounded-lg hover:bg-red-500/20 hover:text-red-400 transition-colors text-sm"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
          
          <!-- 亮点/关注点 -->
          <div v-if="analysis.healthScore.highlights?.length || analysis.healthScore.concerns?.length" class="mt-4 pt-4 border-t border-white/5 flex flex-wrap gap-2">
            <span
              v-for="h in (analysis.healthScore.highlights || []).slice(0, 2)"
              :key="h"
              class="px-2 py-1 bg-green-500/10 text-green-400 rounded text-xs"
            >
              ✓ {{ h.slice(0, 30) }}
            </span>
            <span
              v-for="c in (analysis.healthScore.concerns || []).slice(0, 2)"
              :key="c"
              class="px-2 py-1 bg-yellow-500/10 text-yellow-400 rounded text-xs"
            >
              ⚠ {{ c.slice(0, 30) }}
            </span>
          </div>
        </div>
      </TransitionGroup>
    </div>
    
    <!-- 空状态 -->
    <div v-else class="text-center py-20">
      <div class="inline-flex items-center justify-center w-24 h-24 rounded-2xl bg-gradient-to-br from-slate-700/50 to-slate-800/50 border border-white/10 mb-6">
        <span class="text-5xl opacity-50">📜</span>
      </div>
      <h2 class="text-2xl font-bold text-white mb-4">暂无分析历史</h2>
      <p class="text-slate-400 max-w-md mx-auto mb-8">
        分析过的项目会自动保存在这里，方便您随时回顾和对比。
      </p>
      <div class="flex justify-center gap-4">
        <router-link
          to="/chat"
          class="px-6 py-3 bg-gradient-to-r from-accent to-primary-500 text-white font-medium rounded-xl hover:opacity-90 transition-all shadow-lg shadow-accent/25"
        >
          💬 开始对话分析
        </router-link>
        <router-link
          to="/analysis"
          class="px-6 py-3 glass text-white font-medium rounded-xl hover:bg-surface-light/50 transition-all"
        >
          📊 快速分析
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>

