<script setup lang="ts">
/**
 * Monitor - 项目监控页面
 * 监控多个项目的健康度变化，设置告警阈值
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import TrendChart from '@/components/charts/TrendChart.vue'

interface MonitoredRepo {
  id: string
  repo: string
  thresholds: {
    healthScore: number
    activity: number
    openrank: number
  }
  lastCheck?: Date
  currentScore?: number
  alerts: Alert[]
  enabled: boolean
}

interface Alert {
  id: string
  type: 'warning' | 'critical'
  metric: string
  message: string
  value: number
  threshold: number
  timestamp: Date
}

const monitors = ref<MonitoredRepo[]>([])
const showAddModal = ref(false)
const newRepo = ref('')
const checkInterval = ref(60) // minutes
let intervalId: number | null = null

// 统计
const stats = computed(() => {
  const enabled = monitors.value.filter(m => m.enabled).length
  const totalAlerts = monitors.value.reduce((sum, m) => sum + m.alerts.length, 0)
  const criticalAlerts = monitors.value.reduce(
    (sum, m) => sum + m.alerts.filter(a => a.type === 'critical').length, 0
  )
  return { total: monitors.value.length, enabled, totalAlerts, criticalAlerts }
})

// 加载监控配置
onMounted(() => {
  const saved = localStorage.getItem('monitors')
  if (saved) {
    monitors.value = JSON.parse(saved)
  } else {
    // 默认监控一些项目
    monitors.value = [
      {
        id: '1',
        repo: 'apache/dubbo',
        thresholds: { healthScore: 60, activity: 50, openrank: 50 },
        enabled: true,
        alerts: [],
        currentScore: 75
      },
      {
        id: '2',
        repo: 'vuejs/vue',
        thresholds: { healthScore: 70, activity: 60, openrank: 100 },
        enabled: true,
        alerts: [],
        currentScore: 88
      }
    ]
  }
  
  // 模拟定时检查
  startMonitoring()
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})

function startMonitoring() {
  // 实际项目中这里会定时调用 API 检查
  intervalId = window.setInterval(() => {
    checkAllMonitors()
  }, checkInterval.value * 60 * 1000) // 转换为毫秒
}

function checkAllMonitors() {
  monitors.value.forEach(monitor => {
    if (monitor.enabled) {
      checkMonitor(monitor)
    }
  })
}

function checkMonitor(monitor: MonitoredRepo) {
  // 模拟检查（实际会调用 API）
  const score = Math.floor(Math.random() * 30) + 50
  monitor.currentScore = score
  monitor.lastCheck = new Date()
  
  // 检查阈值
  if (score < monitor.thresholds.healthScore) {
    addAlert(monitor, 'healthScore', score, monitor.thresholds.healthScore)
  }
  
  saveMonitors()
}

function addAlert(monitor: MonitoredRepo, metric: string, value: number, threshold: number) {
  const alert: Alert = {
    id: Date.now().toString(),
    type: value < threshold * 0.7 ? 'critical' : 'warning',
    metric,
    message: `${monitor.repo} 的 ${metric} 低于阈值`,
    value,
    threshold,
    timestamp: new Date()
  }
  monitor.alerts.unshift(alert)
  
  // 保留最近 10 条告警
  if (monitor.alerts.length > 10) {
    monitor.alerts = monitor.alerts.slice(0, 10)
  }
  
  // 浏览器通知
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification('OpenSource Copilot 告警', {
      body: alert.message,
      icon: '/favicon.ico'
    })
  }
}

function addMonitor() {
  if (!newRepo.value.includes('/')) return
  
  const monitor: MonitoredRepo = {
    id: Date.now().toString(),
    repo: newRepo.value.trim(),
    thresholds: { healthScore: 60, activity: 50, openrank: 50 },
    enabled: true,
    alerts: []
  }
  
  monitors.value.push(monitor)
  saveMonitors()
  newRepo.value = ''
  showAddModal.value = false
}

function removeMonitor(id: string) {
  monitors.value = monitors.value.filter(m => m.id !== id)
  saveMonitors()
}

function toggleMonitor(id: string) {
  const monitor = monitors.value.find(m => m.id === id)
  if (monitor) {
    monitor.enabled = !monitor.enabled
    saveMonitors()
  }
}

function clearAlerts(id: string) {
  const monitor = monitors.value.find(m => m.id === id)
  if (monitor) {
    monitor.alerts = []
    saveMonitors()
  }
}

function saveMonitors() {
  localStorage.setItem('monitors', JSON.stringify(monitors.value))
}

function requestNotificationPermission() {
  if ('Notification' in window) {
    Notification.requestPermission()
  }
}

function getScoreColor(score?: number): string {
  if (!score) return 'text-slate-400'
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-green-400'
  if (score >= 40) return 'text-yellow-400'
  return 'text-red-400'
}

function formatTime(date?: Date): string {
  if (!date) return '从未'
  const d = new Date(date)
  return d.toLocaleString('zh-CN', { 
    month: 'short', 
    day: 'numeric', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 模拟趋势数据
const trendData = computed(() => ({
  months: ['1月', '2月', '3月', '4月', '5月', '6月'],
  openrank: [65, 70, 68, 75, 72, 78],
  activity: [55, 60, 58, 65, 70, 68]
}))
</script>

<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-3">
          <span class="text-3xl">🔔</span>
          项目监控
        </h1>
        <p class="text-slate-400 mt-1">实时监控项目健康度，设置告警阈值</p>
      </div>
      
      <div class="flex items-center gap-3">
        <button
          @click="requestNotificationPermission"
          class="px-4 py-2 glass text-slate-300 rounded-xl hover:text-white hover:border-accent/30 transition-all flex items-center gap-2"
        >
          <span>🔔</span>
          启用通知
        </button>
        <button
          @click="showAddModal = true"
          class="px-6 py-2.5 bg-gradient-to-r from-accent to-primary-500 text-white font-semibold rounded-xl hover:opacity-90 transition-all shadow-lg shadow-accent/25 flex items-center gap-2"
        >
          <span>➕</span>
          添加监控
        </button>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <div class="grid grid-cols-4 gap-4">
      <div class="glass p-5 rounded-xl">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-600/20 flex items-center justify-center text-2xl border border-blue-500/30">
            📋
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ stats.total }}</div>
            <div class="text-sm text-slate-400">监控项目</div>
          </div>
        </div>
      </div>
      <div class="glass p-5 rounded-xl">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500/20 to-green-600/20 flex items-center justify-center text-2xl border border-green-500/30">
            ✅
          </div>
          <div>
            <div class="text-2xl font-bold text-emerald-400">{{ stats.enabled }}</div>
            <div class="text-sm text-slate-400">启用中</div>
          </div>
        </div>
      </div>
      <div class="glass p-5 rounded-xl">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 flex items-center justify-center text-2xl border border-yellow-500/30">
            ⚠️
          </div>
          <div>
            <div class="text-2xl font-bold text-yellow-400">{{ stats.totalAlerts }}</div>
            <div class="text-sm text-slate-400">告警总数</div>
          </div>
        </div>
      </div>
      <div class="glass p-5 rounded-xl">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500/20 to-red-600/20 flex items-center justify-center text-2xl border border-red-500/30">
            🚨
          </div>
          <div>
            <div class="text-2xl font-bold text-red-400">{{ stats.criticalAlerts }}</div>
            <div class="text-sm text-slate-400">严重告警</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 监控列表 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div
        v-for="monitor in monitors"
        :key="monitor.id"
        :class="[
          'glass p-6 rounded-2xl transition-all',
          !monitor.enabled && 'opacity-50'
        ]"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div :class="['w-3 h-3 rounded-full', monitor.enabled ? 'bg-green-500 animate-pulse' : 'bg-slate-500']"></div>
            <h3 class="text-lg font-semibold text-white">{{ monitor.repo }}</h3>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="toggleMonitor(monitor.id)"
              :class="[
                'p-2 rounded-lg transition-colors',
                monitor.enabled ? 'text-green-400 hover:bg-green-500/10' : 'text-slate-400 hover:bg-white/5'
              ]"
              :title="monitor.enabled ? '暂停监控' : '启用监控'"
            >
              {{ monitor.enabled ? '⏸️' : '▶️' }}
            </button>
            <button
              @click="removeMonitor(monitor.id)"
              class="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
              title="删除监控"
            >
              🗑️
            </button>
          </div>
        </div>
        
        <!-- 当前状态 -->
        <div class="grid grid-cols-3 gap-4 mb-4">
          <div class="p-3 bg-surface-light/20 rounded-xl text-center">
            <div :class="['text-2xl font-bold', getScoreColor(monitor.currentScore)]">
              {{ monitor.currentScore || '--' }}
            </div>
            <div class="text-xs text-slate-400">健康分</div>
          </div>
          <div class="p-3 bg-surface-light/20 rounded-xl text-center">
            <div class="text-lg text-white">{{ monitor.thresholds.healthScore }}</div>
            <div class="text-xs text-slate-400">阈值</div>
          </div>
          <div class="p-3 bg-surface-light/20 rounded-xl text-center">
            <div class="text-sm text-slate-300">{{ formatTime(monitor.lastCheck) }}</div>
            <div class="text-xs text-slate-400">上次检查</div>
          </div>
        </div>
        
        <!-- 告警列表 -->
        <div v-if="monitor.alerts.length > 0" class="mt-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-slate-400">最近告警</span>
            <button
              @click="clearAlerts(monitor.id)"
              class="text-xs text-slate-500 hover:text-white transition-colors"
            >
              清除
            </button>
          </div>
          <div class="space-y-2 max-h-32 overflow-auto">
            <div
              v-for="alert in monitor.alerts.slice(0, 3)"
              :key="alert.id"
              :class="[
                'p-2 rounded-lg text-sm flex items-center gap-2',
                alert.type === 'critical' ? 'bg-red-500/10 text-red-400' : 'bg-yellow-500/10 text-yellow-400'
              ]"
            >
              <span>{{ alert.type === 'critical' ? '🚨' : '⚠️' }}</span>
              <span class="flex-1 truncate">{{ alert.message }}</span>
              <span class="text-xs opacity-60">{{ formatTime(alert.timestamp) }}</span>
            </div>
          </div>
        </div>
        
        <div v-else class="mt-4 text-center py-4 bg-surface-light/10 rounded-xl">
          <span class="text-slate-500 text-sm">✅ 暂无告警</span>
        </div>
      </div>
    </div>
    
    <!-- 趋势图表 -->
    <div class="glass p-6 rounded-2xl">
      <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <span>📈</span>
        整体趋势
      </h2>
      <TrendChart :data="trendData" title="" />
    </div>
    
    <!-- 空状态 -->
    <div v-if="monitors.length === 0" class="text-center py-20">
      <div class="inline-flex items-center justify-center w-24 h-24 rounded-2xl bg-gradient-to-br from-accent/20 to-primary-500/20 border border-accent/30 mb-6">
        <span class="text-5xl">🔔</span>
      </div>
      <h2 class="text-2xl font-bold text-white mb-4">开始监控项目</h2>
      <p class="text-slate-400 max-w-md mx-auto mb-6">
        添加需要监控的项目，设置告警阈值，<br>
        当项目健康度下降时及时收到通知。
      </p>
      <button
        @click="showAddModal = true"
        class="px-6 py-3 bg-gradient-to-r from-accent to-primary-500 text-white font-semibold rounded-xl hover:opacity-90 transition-all shadow-lg shadow-accent/25"
      >
        添加第一个监控
      </button>
    </div>
    
    <!-- 添加监控弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showAddModal" class="fixed inset-0 z-50 flex items-center justify-center">
          <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showAddModal = false"></div>
          <div class="relative glass-dark p-8 rounded-2xl w-full max-w-md mx-4 shadow-2xl">
            <h3 class="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <span>➕</span>
              添加项目监控
            </h3>
            
            <div class="space-y-4">
              <div>
                <label class="text-sm text-slate-400 mb-2 block">仓库地址</label>
                <input
                  v-model="newRepo"
                  type="text"
                  placeholder="owner/repo"
                  class="w-full bg-surface border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-accent/50"
                />
              </div>
              
              <div class="flex justify-end gap-3 mt-6">
                <button
                  @click="showAddModal = false"
                  class="px-5 py-2.5 text-slate-400 hover:text-white transition-colors"
                >
                  取消
                </button>
                <button
                  @click="addMonitor"
                  :disabled="!newRepo.includes('/')"
                  class="px-6 py-2.5 bg-gradient-to-r from-accent to-primary-500 text-white font-semibold rounded-xl hover:opacity-90 disabled:opacity-50 transition-all"
                >
                  添加
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.glass-dark {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.95) translateY(10px);
}
</style>

