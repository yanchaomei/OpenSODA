import axios from 'axios'

// 获取 API 基础 URL（生产环境使用环境变量，开发环境使用代理）
const getBaseUrl = () => {
  // Vercel 生产环境会通过 rewrites 处理 /api 请求
  return '/api'
}

const api = axios.create({
  baseURL: getBaseUrl(),
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 导出 API 基础 URL 供其他模块使用
export const API_BASE_URL = getBaseUrl()

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    console.error('API Error:', message)
    return Promise.reject(new Error(message))
  }
)

export default api

