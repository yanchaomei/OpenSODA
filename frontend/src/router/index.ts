import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue'),
    meta: { title: '智能对话' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '数据仪表盘' }
  },
  {
    path: '/analysis/:repo*',
    name: 'Analysis',
    component: () => import('@/views/Analysis.vue'),
    meta: { title: '项目分析' }
  },
  {
    path: '/compare',
    name: 'Compare',
    component: () => import('@/views/Compare.vue'),
    meta: { title: '项目对比' }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue'),
    meta: { title: '分析历史' }
  },
  {
    path: '/batch',
    name: 'BatchAnalysis',
    component: () => import('@/views/BatchAnalysis.vue'),
    meta: { title: '批量分析' }
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: () => import('@/views/Monitor.vue'),
    meta: { title: '项目监控' }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
    meta: { title: '关于项目' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || 'OpenSource Copilot'} - 开源社区智能运营助手`
  next()
})

export default router

