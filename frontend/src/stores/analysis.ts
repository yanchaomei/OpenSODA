import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { analysisApi, type CompareResponse } from '@/api/analysis'

export interface HealthScore {
  overall: number
  activity: number
  community: number
  maintenance: number
  growth: number
  summary?: string
  highlights?: string[]
  concerns?: string[]
}

export interface RepoAnalysis {
  repo: string
  repoInfo?: Record<string, any>
  metrics: Record<string, any>
  healthScore: HealthScore
  trends?: Record<string, any[]>
  charts?: any[]
  diagnosis?: {
    issues: string[]
    risks: string[]
    severity: string
  }
  recommendations?: any[]
  analyzedAt?: string
}

// 本地存储 key
const HISTORY_STORAGE_KEY = 'opensource_copilot_history'

export const useAnalysisStore = defineStore('analysis', () => {
  const currentAnalysis = ref<RepoAnalysis | null>(null)
  const recentAnalyses = ref<RepoAnalysis[]>([])
  const compareResult = ref<CompareResponse | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  const hasAnalysis = computed(() => currentAnalysis.value !== null)
  
  // 从本地存储加载历史记录
  function loadHistory() {
    try {
      const saved = localStorage.getItem(HISTORY_STORAGE_KEY)
      if (saved) {
        recentAnalyses.value = JSON.parse(saved)
      }
    } catch (e) {
      console.error('Failed to load history:', e)
    }
  }
  
  // 保存历史记录到本地存储
  function saveHistory() {
    try {
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(recentAnalyses.value))
    } catch (e) {
      console.error('Failed to save history:', e)
    }
  }
  
  // 监听变化自动保存
  watch(recentAnalyses, saveHistory, { deep: true })
  
  // 初始化时加载历史
  loadHistory()
  
  async function analyzeRepo(repo: string) {
    isLoading.value = true
    error.value = null
    
    try {
      const result = await analysisApi.analyzeRepo(repo)
      
      const analysis: RepoAnalysis = {
        repo: result?.repo || repo,
        repoInfo: result?.repo_info || {},
        metrics: result?.metrics || {},
        healthScore: {
          overall: result?.health_score?.overall || 0,
          activity: result?.health_score?.activity || 0,
          community: result?.health_score?.community || 0,
          maintenance: result?.health_score?.maintenance || 0,
          growth: result?.health_score?.growth || 0,
          summary: result?.health_score?.summary,
          highlights: result?.health_score?.highlights,
          concerns: result?.health_score?.concerns
        },
        trends: result?.trends,
        charts: result?.charts,
        analyzedAt: result?.analyzed_at || new Date().toISOString()
      }
      
      currentAnalysis.value = analysis
      
      // 添加到最近分析列表
      const existingIndex = recentAnalyses.value.findIndex(a => a.repo === repo)
      if (existingIndex >= 0) {
        recentAnalyses.value[existingIndex] = analysis
      } else {
        recentAnalyses.value.unshift(analysis)
        // 保留最近10个
        if (recentAnalyses.value.length > 10) {
          recentAnalyses.value.pop()
        }
      }
      
      return analysis
    } catch (e: any) {
      error.value = e.message || '分析失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }
  
  async function compareRepos(repos: string[]) {
    isLoading.value = true
    error.value = null
    
    try {
      compareResult.value = await analysisApi.compareRepos(repos)
      return compareResult.value
    } catch (e: any) {
      error.value = e.message || '对比分析失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }
  
  function clearCurrentAnalysis() {
    currentAnalysis.value = null
  }
  
  function clearHistory() {
    recentAnalyses.value = []
    saveHistory()
  }
  
  function removeFromHistory(repo: string) {
    const index = recentAnalyses.value.findIndex(a => a.repo === repo)
    if (index >= 0) {
      recentAnalyses.value.splice(index, 1)
    }
  }
  
  function getScoreClass(score: number): string {
    if (score >= 80) return 'score-excellent'
    if (score >= 60) return 'score-good'
    if (score >= 40) return 'score-fair'
    if (score >= 20) return 'score-poor'
    return 'score-critical'
  }
  
  function getScoreLabel(score: number): string {
    if (score >= 80) return '优秀'
    if (score >= 60) return '良好'
    if (score >= 40) return '一般'
    if (score >= 20) return '较差'
    return '需关注'
  }
  
  function getScoreColor(score: number): string {
    if (score >= 80) return '#10b981' // emerald
    if (score >= 60) return '#22c55e' // green
    if (score >= 40) return '#eab308' // yellow
    return '#ef4444' // red
  }
  
  return {
    currentAnalysis,
    recentAnalyses,
    compareResult,
    isLoading,
    error,
    hasAnalysis,
    analyzeRepo,
    compareRepos,
    clearCurrentAnalysis,
    clearHistory,
    removeFromHistory,
    getScoreClass,
    getScoreLabel,
    getScoreColor
  }
})

