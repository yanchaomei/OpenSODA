<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()

// 状态
const loading = ref(true)
const dashboardData = ref<any>(null)
const systemHealth = ref<any>(null)
const currentTime = ref(new Date())

// 动画计数器
const animatedStats = ref<Record<string, number>>({})

// 定时更新时间
setInterval(() => {
  currentTime.value = new Date()
}, 1000)

// 格式化时间
const formattedTime = computed(() => {
  return currentTime.value.toLocaleString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
})

const formattedDate = computed(() => {
  return currentTime.value.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 数字动画
function animateNumber(key: string, target: number, duration: number = 1000) {
  const start = animatedStats.value[key] || 0
  const increment = (target - start) / (duration / 16)
  const animate = () => {
    const current = animatedStats.value[key] || 0
    if (Math.abs(current - target) > Math.abs(increment)) {
      animatedStats.value[key] = current + increment
      requestAnimationFrame(animate)
    } else {
      animatedStats.value[key] = target
    }
  }
  animate()
}

onMounted(async () => {
  try {
    // 并发请求
    const [dashboardRes, healthRes] = await Promise.all([
      api.get('/dashboard/'),
      api.get('/health/')
    ])
    
    dashboardData.value = dashboardRes
    systemHealth.value = healthRes
    
    // 启动数字动画
    if (dashboardData.value?.stats) {
      dashboardData.value.stats.forEach((stat: any, index: number) => {
        const numValue = parseFloat(stat.value.replace(/[^0-9.]/g, '')) || 0
        setTimeout(() => {
          animateNumber(`stat-${index}`, numValue, 1500)
        }, index * 200)
      })
    }
  } catch (e) {
    console.error('Failed to fetch dashboard data:', e)
  } finally {
    loading.value = false
  }
})

function startChat(query: string) {
  router.push({ name: 'Chat', query: { q: query } })
}

function analyzeRepo(repo: string) {
  router.push(`/analysis/${repo}`)
}

function goToDemo(demo: any) {
  router.push(`/analysis/${demo.repo}`)
}

// 获取健康度颜色
function getScoreColor(score: number): string {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-green-400'
  if (score >= 40) return 'text-yellow-400'
  return 'text-red-400'
}

function getTrendIcon(trend: string): string {
  switch (trend) {
    case 'up': return '↑'
    case 'down': return '↓'
    default: return '→'
  }
}

function getTrendColor(trend: string): string {
  switch (trend) {
    case 'up': return 'text-emerald-400'
    case 'down': return 'text-red-400'
    default: return 'text-slate-400'
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- 顶部欢迎区域 -->
    <div class="glass rounded-2xl p-8 relative overflow-hidden">
      <!-- 装饰背景 -->
      <div class="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-accent/20 via-primary-500/10 to-transparent rounded-full blur-3xl"></div>
      <div class="absolute bottom-0 left-0 w-64 h-64 bg-gradient-to-tr from-cyan-500/20 to-transparent rounded-full blur-3xl"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-radial from-accent/5 to-transparent rounded-full"></div>
      
      <div class="relative z-10 flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent via-primary-500 to-cyan-500 flex items-center justify-center text-4xl shadow-2xl shadow-accent/30 animate-float">
              🤖
            </div>
            <div>
              <h1 class="text-3xl font-bold text-white mb-1">
                OpenSource Copilot
              </h1>
              <p class="text-slate-400">基于 ReAct Agent 的开源社区智能运营助手</p>
            </div>
          </div>
          
          <p class="text-slate-300 max-w-2xl mb-6 text-lg leading-relaxed">
            我能够<span class="text-accent-light font-semibold">自主思考</span>、
            <span class="text-cyan-400 font-semibold">调用工具</span>、
            <span class="text-emerald-400 font-semibold">分析数据</span>，
            为您提供全面的开源项目健康度评估与运营建议。
          </p>
          
          <div class="flex gap-3">
            <button 
              @click="startChat('帮我分析一个开源项目')"
              class="group px-6 py-3 bg-gradient-to-r from-accent to-primary-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-accent/30 transition-all duration-300 hover:-translate-y-0.5"
            >
              <span class="flex items-center gap-2">
                🚀 开始对话
                <span class="group-hover:translate-x-1 transition-transform">→</span>
              </span>
            </button>
            <button 
              @click="$router.push('/compare')"
              class="px-6 py-3 glass text-white font-medium rounded-xl hover:bg-white/10 transition-all border border-white/10 hover:border-accent/30"
            >
              ⚖️ 项目对比
            </button>
          </div>
        </div>
        
        <!-- 时间显示 -->
        <div class="text-right hidden lg:block">
          <div class="text-4xl font-mono font-bold text-white/90 tracking-wider">
            {{ formattedTime }}
          </div>
          <div class="text-sm text-slate-400 mt-1">
            {{ formattedDate }}
          </div>
          <div class="mt-4 flex items-center gap-2 justify-end">
            <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span class="text-xs text-emerald-400">系统运行中</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <template v-if="loading">
        <div v-for="i in 4" :key="i" class="glass p-5 rounded-xl">
          <div class="skeleton h-4 w-20 mb-3"></div>
          <div class="skeleton h-8 w-24 mb-2"></div>
          <div class="skeleton h-3 w-16"></div>
        </div>
      </template>
      <template v-else-if="dashboardData?.stats">
        <div 
          v-for="(stat, index) in dashboardData.stats" 
          :key="stat.label"
          class="glass p-5 rounded-xl hover:border-accent/30 border border-transparent transition-all duration-300 group cursor-default"
          :style="{ animationDelay: `${index * 100}ms` }"
        >
          <div class="flex items-start justify-between">
            <div>
              <div class="text-slate-400 text-sm mb-1">{{ stat.label }}</div>
              <div class="text-3xl font-bold text-white tabular-nums">
                {{ typeof animatedStats[`stat-${index}`] === 'number' 
                  ? (stat.value.includes('%') 
                    ? animatedStats[`stat-${index}`].toFixed(0) + '%'
                    : Math.round(animatedStats[`stat-${index}`]))
                  : stat.value }}
              </div>
            </div>
            <div class="text-3xl opacity-50 group-hover:opacity-100 group-hover:scale-110 transition-all">
              {{ stat.icon }}
            </div>
          </div>
          <div v-if="stat.change" class="mt-2 flex items-center gap-1">
            <span :class="getTrendColor(stat.trend)">
              {{ getTrendIcon(stat.trend) }} {{ stat.change }}
            </span>
            <span class="text-xs text-slate-500">较上周</span>
          </div>
        </div>
      </template>
    </div>
    
    <!-- 一键体验区域 -->
    <div class="glass rounded-xl p-6">
      <div class="flex items-center justify-between mb-5">
        <h2 class="text-lg font-semibold text-white flex items-center gap-2">
          <span class="text-2xl">⚡</span>
          <span>一键体验</span>
          <span class="text-xs px-2 py-1 bg-accent/20 text-accent-light rounded-full">推荐</span>
        </h2>
        <span class="text-sm text-slate-500">预置热门项目，点击即可查看分析结果</span>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <template v-if="loading">
          <div v-for="i in 5" :key="i" class="skeleton h-36 rounded-xl"></div>
        </template>
        <template v-else-if="dashboardData?.demoProjects">
          <div 
            v-for="(demo, index) in dashboardData.demoProjects" 
            :key="demo.repo"
            @click="goToDemo(demo)"
            class="group p-4 bg-surface-light/20 rounded-xl border border-white/5 hover:border-accent/40 cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-accent/10"
            :style="{ animationDelay: `${index * 50}ms` }"
          >
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-accent/20 to-primary-500/20 flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
                {{ demo.icon }}
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-white font-medium truncate">{{ demo.name }}</div>
                <div class="text-xs text-slate-500 truncate">{{ demo.repo }}</div>
              </div>
            </div>
            <p class="text-xs text-slate-400 mb-3 line-clamp-2">{{ demo.description }}</p>
            <div class="flex items-center justify-between">
              <div class="flex gap-1 flex-wrap">
                <span 
                  v-for="tag in demo.tags.slice(0, 2)" 
                  :key="tag"
                  class="text-xs px-2 py-0.5 bg-white/5 rounded text-slate-400"
                >
                  {{ tag }}
                </span>
              </div>
              <div :class="['text-lg font-bold', getScoreColor(demo.healthScore)]">
                {{ demo.healthScore }}
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
    
    <!-- 双列布局 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 热门项目排行 -->
      <div class="glass rounded-xl p-6">
        <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span class="text-xl">🔥</span>
          <span>OpenRank 排行榜</span>
        </h2>
        
        <div v-if="loading" class="space-y-3">
          <div v-for="i in 5" :key="i" class="flex items-center gap-4 p-3">
            <div class="skeleton w-6 h-6 rounded"></div>
            <div class="flex-1">
              <div class="skeleton h-4 w-32 mb-1"></div>
              <div class="skeleton h-3 w-16"></div>
            </div>
            <div class="skeleton h-6 w-16"></div>
          </div>
        </div>
        
        <div v-else-if="dashboardData?.hotProjects" class="space-y-1">
          <div 
            v-for="(project, index) in dashboardData.hotProjects.slice(0, 8)" 
            :key="project.repo"
            @click="analyzeRepo(project.repo)"
            class="flex items-center gap-4 p-3 rounded-lg hover:bg-surface-light/30 transition-all cursor-pointer group"
          >
            <span 
              :class="[
                'w-6 h-6 flex items-center justify-center text-sm font-bold rounded',
                index < 3 ? 'bg-gradient-to-br from-amber-500 to-orange-500 text-white' : 'text-slate-500'
              ]"
            >
              {{ index + 1 }}
            </span>
            <div class="flex-1 min-w-0">
              <div class="text-white font-medium truncate group-hover:text-accent-light transition-colors">
                {{ project.repo }}
              </div>
              <div class="text-xs text-slate-500">{{ project.category }}</div>
            </div>
            <div class="text-right">
              <div class="text-accent-light font-semibold tabular-nums">
                {{ project.openrank.toFixed(1) }}
              </div>
              <div class="text-xs text-slate-500">OpenRank</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 系统状态 & Agent 能力 -->
      <div class="space-y-6">
        <!-- 系统状态 -->
        <div class="glass rounded-xl p-6">
          <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span class="text-xl">💚</span>
            <span>系统状态</span>
          </h2>
          
          <div v-if="loading" class="space-y-3">
            <div v-for="i in 3" :key="i" class="flex items-center gap-3 p-3">
              <div class="skeleton w-3 h-3 rounded-full"></div>
              <div class="skeleton h-4 flex-1"></div>
            </div>
          </div>
          
          <div v-else-if="systemHealth" class="space-y-2">
            <div class="flex items-center justify-between p-3 bg-surface-light/20 rounded-lg">
              <div class="flex items-center gap-3">
                <div class="w-3 h-3 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/50 animate-pulse"></div>
                <span class="text-white">Agent 服务</span>
              </div>
              <span class="text-emerald-400 text-sm font-medium">运行中</span>
            </div>
            
            <div 
              v-for="(service, name) in systemHealth.services" 
              :key="name"
              class="flex items-center justify-between p-3 bg-surface-light/20 rounded-lg"
            >
              <div class="flex items-center gap-3">
                <div 
                  :class="[
                    'w-3 h-3 rounded-full',
                    service.status === 'healthy' ? 'bg-emerald-500 shadow-emerald-500/50' : 
                    service.status === 'unknown' ? 'bg-yellow-500 shadow-yellow-500/50' : 'bg-red-500 shadow-red-500/50',
                    'shadow-lg'
                  ]"
                ></div>
                <span class="text-white capitalize">{{ name }}</span>
              </div>
              <span 
                :class="[
                  'text-sm',
                  service.status === 'healthy' ? 'text-emerald-400' : 
                  service.status === 'unknown' ? 'text-yellow-400' : 'text-red-400'
                ]"
              >
                {{ service.latency_ms ? `${service.latency_ms}ms` : service.status }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- Agent 能力 -->
        <div class="glass rounded-xl p-6">
          <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span class="text-xl">🛠️</span>
            <span>Agent 工具链</span>
          </h2>
          
          <div class="grid grid-cols-2 gap-2">
            <div 
              v-for="tool in [
                { icon: '📊', name: '健康度分析' },
                { icon: '🔍', name: '问题诊断' },
                { icon: '💡', name: '建议生成' },
                { icon: '📈', name: 'OpenRank' },
                { icon: '👥', name: '贡献者分析' },
                { icon: '🎯', name: '新手 Issue' },
              ]"
              :key="tool.name"
              class="flex items-center gap-2 p-2 bg-surface-light/20 rounded-lg text-sm"
            >
              <span class="text-lg">{{ tool.icon }}</span>
              <span class="text-slate-300">{{ tool.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 使用示例 -->
    <div class="glass rounded-xl p-6">
      <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <span class="text-xl">💬</span>
        <span>试试这样问我</span>
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          v-for="example in [
            { text: '分析 apache/dubbo 的社区健康状况', desc: '获取完整的项目健康度报告' },
            { text: 'vuejs/vue 有什么问题需要关注？', desc: '诊断潜在问题和风险' },
            { text: '如何提升开源项目的 OpenRank？', desc: '获取专业的运营建议' },
          ]"
          :key="example.text"
          @click="startChat(example.text)"
          class="p-4 bg-surface-light/20 rounded-xl cursor-pointer hover:bg-surface-light/40 hover:border-accent/30 border border-transparent transition-all group"
        >
          <div class="text-white mb-2 group-hover:text-accent-light transition-colors">
            "{{ example.text }}"
          </div>
          <div class="text-xs text-slate-500 flex items-center gap-1">
            <span>→</span>
            <span>{{ example.desc }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 技术标签 -->
    <div class="flex flex-wrap items-center justify-center gap-3 py-4">
      <span 
        v-for="tech in ['LangGraph', 'ReAct Agent', 'OpenDigger', 'FastAPI', 'Vue 3', 'ECharts']"
        :key="tech"
        class="px-3 py-1.5 bg-surface-light/30 rounded-full text-sm text-slate-400 border border-white/5"
      >
        {{ tech }}
      </span>
    </div>
  </div>
</template>

<style scoped>
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bg-gradient-radial {
  background: radial-gradient(circle, var(--tw-gradient-from) 0%, var(--tw-gradient-to) 70%);
}

.tabular-nums {
  font-variant-numeric: tabular-nums;
}
</style>
