import api from './index'

export const analysisApi = {
  /**
   * 分析单个仓库
   */
  async analyzeRepo(repo: string) {
    const [owner, repoName] = repo.split('/')
    return api.get(`/analysis/repo/${owner}/${repoName}`)
  },

  /**
   * 对比多个仓库
   */
  async compareRepos(repos: string[]) {
    return api.post('/analysis/compare', repos)
  },

  /**
   * 获取趋势项目
   */
  async getTrendingRepos(language?: string, period: string = 'weekly') {
    return api.get('/analysis/trending', {
      params: { language, period }
    })
  }
}

