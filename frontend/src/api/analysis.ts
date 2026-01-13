import api from './index'

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

export interface CompareResult {
  repo: string
  health_score?: HealthScore
  metrics?: Record<string, any>
  rank?: number
  error?: string
}

export interface CompareResponse {
  comparisons: CompareResult[]
  summary: {
    total_repos: number
    valid_repos: number
    average_score: number
    best_overall: { repo: string; score: number }
    best_activity: { repo: string; score: number }
    best_community: { repo: string; score: number }
    best_maintenance: { repo: string; score: number }
    best_growth: { repo: string; score: number }
    dimensions: string[]
  }
  winner?: string
  compared_at: string
}

export interface TrendingRepo {
  repo: string
  openrank: number
  category: string
}

export const analysisApi = {
  /**
   * 分析单个仓库
   * 注意: axios 拦截器已返回 response.data，此处直接返回
   */
  async analyzeRepo(repo: string) {
    const [owner, repoName] = repo.split('/')
    return api.get(`/analysis/repo/${owner}/${repoName}`)
  },

  /**
   * 对比多个仓库
   */
  async compareRepos(repos: string[]): Promise<CompareResponse> {
    return api.post('/analysis/compare', { repos })
  },

  /**
   * 导出为 Markdown
   */
  async exportMarkdown(repos: string[]): Promise<Blob> {
    return api.post('/analysis/export/markdown', { repos }, {
      responseType: 'blob'
    })
  },

  /**
   * 导出为 JSON
   */
  async exportJson(repos: string[]): Promise<Blob> {
    return api.post('/analysis/export/json', { repos }, {
      responseType: 'blob'
    })
  },

  /**
   * 获取趋势项目
   */
  async getTrendingRepos(language?: string, period: string = 'weekly'): Promise<{
    period: string
    language: string | null
    repos: TrendingRepo[]
    updated_at: string
  }> {
    return api.get('/analysis/trending', {
      params: { language, period }
    })
  },

  /**
   * 获取分析历史
   */
  async getHistory(limit: number = 20) {
    return api.get('/analysis/history', {
      params: { limit }
    })
  }
}
