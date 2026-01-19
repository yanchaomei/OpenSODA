<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const menuItems = [
  { path: '/', icon: '🏠', label: '首页' },
  { path: '/chat', icon: '💬', label: '智能对话' },
  { path: '/dashboard', icon: '📊', label: '数据仪表盘' },
  { path: '/analysis', icon: '🔍', label: '项目分析' },
  { path: '/compare', icon: '⚖️', label: '项目对比' },
  { path: '/batch', icon: '📦', label: '批量分析' },
  { path: '/monitor', icon: '🔔', label: '项目监控' },
  { path: '/history', icon: '📜', label: '分析历史' },
  { path: '/about', icon: '💡', label: '关于项目' },
]

const currentPath = computed(() => route.path)

function navigateTo(path: string) {
  router.push(path)
}
</script>

<template>
  <aside class="w-64 bg-surface-dark border-r border-white/5 flex flex-col">
    <!-- Logo -->
    <div class="p-6 border-b border-white/5">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-accent to-primary-500 flex items-center justify-center text-xl">
          🤖
        </div>
        <div>
          <h1 class="text-lg font-bold text-white">OpenSource</h1>
          <p class="text-xs text-slate-400">Copilot</p>
        </div>
      </div>
    </div>
    
    <!-- 导航菜单 -->
    <nav class="flex-1 p-4">
      <ul class="space-y-2">
        <li v-for="item in menuItems" :key="item.path">
          <button
            @click="navigateTo(item.path)"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
              currentPath === item.path || (item.path !== '/' && currentPath.startsWith(item.path))
                ? 'bg-accent/20 text-accent-light border border-accent/30'
                : 'text-slate-400 hover:bg-white/5 hover:text-white'
            ]"
          >
            <span class="text-lg">{{ item.icon }}</span>
            <span class="font-medium">{{ item.label }}</span>
          </button>
        </li>
      </ul>
    </nav>
    
    <!-- 底部信息 -->
    <div class="p-4 border-t border-white/5">
      <div class="glass-dark p-4 text-center">
        <p class="text-xs text-slate-400 mb-2">Powered by</p>
        <div class="flex items-center justify-center gap-2 text-sm">
          <span class="text-primary-400">OpenDigger</span>
          <span class="text-slate-500">+</span>
          <span class="text-accent-light">LangGraph</span>
        </div>
      </div>
    </div>
  </aside>
</template>

