import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { analysisApi } from '@/api/analysis'

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
}

export const useAnalysisStore = defineStore('analysis', () => {
  const currentAnalysis = ref<RepoAnalysis | null>(null)
  const recentAnalyses = ref<RepoAnalysis[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  const hasAnalysis = computed(() => currentAnalysis.value !== null)
  
  async function analyzeRepo(repo: string) {
    isLoading.value = true
    error.value = null
    
    try {
      const result = await analysisApi.analyzeRepo(repo)
      
      const analysis: RepoAnalysis = {
        repo,
        repoInfo: result.repo_info,
        metrics: result.metrics || {},
        healthScore: {
          overall: result.health_score?.overall || 0,
          activity: result.health_score?.activity || 0,
          community: result.health_score?.community || 0,
          maintenance: result.health_score?.maintenance || 0,
          growth: result.health_score?.growth || 0,
          summary: result.health_score?.summary,
          highlights: result.health_score?.highlights,
          concerns: result.health_score?.concerns
        },
        trends: result.trends,
        charts: result.charts
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
  
  function clearCurrentAnalysis() {
    currentAnalysis.value = null
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
  
  return {
    currentAnalysis,
    recentAnalyses,
    isLoading,
    error,
    hasAnalysis,
    analyzeRepo,
    clearCurrentAnalysis,
    getScoreClass,
    getScoreLabel
  }
})

