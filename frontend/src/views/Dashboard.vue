<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const systemHealth = ref<any>(null)
const loading = ref(true)
const recentProjects = ref([
  { name: 'apache/dubbo', score: 70.2, trend: 'up' },
  { name: 'vuejs/vue', score: 85.5, trend: 'stable' },
  { name: 'facebook/react', score: 92.1, trend: 'up' },
])

// Agent 能力卡片
const agentCapabilities = [
  {
    icon: '🔍',
    title: '项目分析',
    description: '全面分析开源项目的健康状况，包括活跃度、社区、维护等多个维度',
    action: '开始分析',
    query: '帮我分析一个开源项目的健康状况'
  },
  {
    icon: '🩺',
    title: '问题诊断',
    description: '识别项目存在的问题和潜在风险，提供专业的诊断报告',
    action: '诊断问题',
    query: '诊断项目存在的问题'
  },
  {
    icon: '💡',
    title: '智能建议',
    description: '基于分析结果提供可执行的改进建议，助力社区运营',
    action: '获取建议',
    query: '给我一些开源项目运营的建议'
  },
  {
    icon: '📊',
    title: '数据洞察',
    description: '深入挖掘 OpenRank、贡献者、活跃度等关键指标',
    action: '查看数据',
    query: '查看项目的关键数据指标'
  }
]

// 热门仓库
const hotRepos = [
  { name: 'kubernetes/kubernetes', openrank: 892.5, category: '云原生' },
  { name: 'tensorflow/tensorflow', openrank: 567.3, category: 'AI/ML' },
  { name: 'microsoft/vscode', openrank: 445.2, category: '开发工具' },
  { name: 'apache/spark', openrank: 234.8, category: '大数据' },
  { name: 'golang/go', openrank: 198.5, category: '编程语言' },
]

onMounted(async () => {
  try {
    const response = await api.get('/health/')
    systemHealth.value = response.data
  } catch (e) {
    console.error('Failed to fetch health:', e)
  } finally {
    loading.value = false
  }
})

function startChat(query: string) {
  router.push({ name: 'Chat', query: { q: query } })
}

function analyzeRepo(repo: string) {
  router.push({ name: 'Chat', query: { q: `分析 ${repo} 的健康状况` } })
}
</script>

<template>
  <div class="space-y-8">
    <!-- 欢迎区域 -->
    <div class="glass rounded-2xl p-8 relative overflow-hidden">
      <!-- 背景装饰 -->
      <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-accent/20 to-transparent rounded-full blur-3xl"></div>
      <div class="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-primary-500/20 to-transparent rounded-full blur-3xl"></div>
      
      <div class="relative z-10">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent to-primary-500 flex items-center justify-center text-3xl shadow-lg shadow-accent/30">
            🤖
          </div>
          <div>
            <h1 class="text-2xl font-bold text-white">OpenSource Copilot</h1>
            <p class="text-slate-400">基于 ReAct Agent 的开源社区智能运营助手</p>
          </div>
        </div>
        
        <p class="text-slate-300 max-w-2xl mb-6">
          我是一个能够<span class="text-accent-light font-medium">思考</span>、
          <span class="text-accent-light font-medium">调用工具</span>、
          <span class="text-accent-light font-medium">分析数据</span>的智能 Agent。
          告诉我你想分析的开源项目，我会帮你进行全面的健康度评估。
        </p>
        
        <div class="flex gap-3">
          <button 
            @click="startChat('帮我分析一个开源项目')"
            class="px-6 py-3 bg-gradient-to-r from-accent to-primary-500 text-white font-medium rounded-xl hover:opacity-90 transition-all shadow-lg shadow-accent/25"
          >
            🚀 开始对话
          </button>
          <button 
            @click="$router.push('/analysis')"
            class="px-6 py-3 glass text-white font-medium rounded-xl hover:bg-surface-light/50 transition-all"
          >
            📊 快速分析
          </button>
        </div>
      </div>
    </div>
    
    <!-- Agent 能力展示 -->
    <div>
      <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <span>🛠️</span>
        <span>Agent 能力</span>
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div 
          v-for="cap in agentCapabilities" 
          :key="cap.title"
          class="glass p-5 rounded-xl hover:border-accent/50 border border-transparent transition-all cursor-pointer group"
          @click="startChat(cap.query)"
        >
          <div class="text-3xl mb-3">{{ cap.icon }}</div>
          <h3 class="text-white font-medium mb-2">{{ cap.title }}</h3>
          <p class="text-sm text-slate-400 mb-4">{{ cap.description }}</p>
          <div class="text-sm text-accent-light group-hover:underline">
            {{ cap.action }} →
          </div>
        </div>
      </div>
    </div>
    
    <!-- 热门项目 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 热门仓库 -->
      <div class="glass rounded-xl p-6">
        <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span>🔥</span>
          <span>热门开源项目</span>
        </h2>
        <div class="space-y-3">
          <div 
            v-for="(repo, index) in hotRepos" 
            :key="repo.name"
            class="flex items-center gap-4 p-3 rounded-lg hover:bg-surface-light/30 transition-colors cursor-pointer"
            @click="analyzeRepo(repo.name)"
          >
            <span class="w-6 h-6 flex items-center justify-center text-sm font-bold text-slate-500">
              {{ index + 1 }}
            </span>
            <div class="flex-1 min-w-0">
              <div class="text-white font-medium truncate">{{ repo.name }}</div>
              <div class="text-xs text-slate-500">{{ repo.category }}</div>
            </div>
            <div class="text-right">
              <div class="text-accent-light font-semibold">{{ repo.openrank }}</div>
              <div class="text-xs text-slate-500">OpenRank</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 系统状态 -->
      <div class="glass rounded-xl p-6">
        <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span>💚</span>
          <span>系统状态</span>
        </h2>
        
        <div v-if="loading" class="flex items-center justify-center py-8">
          <div class="loading-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
        
        <div v-else-if="systemHealth" class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-surface-light/30 rounded-lg">
            <div class="flex items-center gap-3">
              <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
              <span class="text-white">Agent 服务</span>
            </div>
            <span class="text-green-400 text-sm">运行中</span>
          </div>
          
          <div 
            v-for="service in systemHealth.services" 
            :key="service.name"
            class="flex items-center justify-between p-3 bg-surface-light/30 rounded-lg"
          >
            <div class="flex items-center gap-3">
              <div 
                :class="[
                  'w-3 h-3 rounded-full',
                  service.status === 'healthy' ? 'bg-green-500' : 
                  service.status === 'unknown' ? 'bg-yellow-500' : 'bg-red-500'
                ]"
              ></div>
              <span class="text-white capitalize">{{ service.name }}</span>
            </div>
            <span 
              :class="[
                'text-sm',
                service.status === 'healthy' ? 'text-green-400' : 
                service.status === 'unknown' ? 'text-yellow-400' : 'text-red-400'
              ]"
            >
              {{ service.latency_ms ? `${service.latency_ms}ms` : service.status }}
            </span>
          </div>
        </div>
        
        <div v-else class="text-center py-8 text-slate-500">
          无法获取系统状态
        </div>
      </div>
    </div>
    
    <!-- 使用提示 -->
    <div class="glass rounded-xl p-6">
      <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <span>💬</span>
        <span>使用示例</span>
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          class="p-4 bg-surface-light/30 rounded-lg cursor-pointer hover:bg-surface-light/50 transition-colors"
          @click="startChat('分析 apache/dubbo 的社区健康状况')"
        >
          <div class="text-white mb-2">"分析 apache/dubbo 的社区健康状况"</div>
          <div class="text-xs text-slate-500">→ 获取完整的项目健康度报告</div>
        </div>
        <div 
          class="p-4 bg-surface-light/30 rounded-lg cursor-pointer hover:bg-surface-light/50 transition-colors"
          @click="startChat('vuejs/vue 有什么问题需要关注？')"
        >
          <div class="text-white mb-2">"vuejs/vue 有什么问题需要关注？"</div>
          <div class="text-xs text-slate-500">→ 诊断潜在问题和风险</div>
        </div>
        <div 
          class="p-4 bg-surface-light/30 rounded-lg cursor-pointer hover:bg-surface-light/50 transition-colors"
          @click="startChat('如何提升开源项目的 OpenRank？')"
        >
          <div class="text-white mb-2">"如何提升开源项目的 OpenRank？"</div>
          <div class="text-xs text-slate-500">→ 获取专业的运营建议</div>
        </div>
      </div>
    </div>
  </div>
</template>
