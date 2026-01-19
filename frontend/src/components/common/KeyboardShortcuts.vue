<script setup lang="ts">
/**
 * KeyboardShortcuts - 全局键盘快捷键支持
 * 提供 Ctrl+K 快速搜索等功能
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showCommandPalette = ref(false)
const searchQuery = ref('')
const searchInputRef = ref<HTMLInputElement | null>(null)

// 快捷操作列表
const commands = [
  { id: 'search', name: '搜索项目', shortcut: '/', icon: '🔍', action: () => router.push('/analysis') },
  { id: 'chat', name: '开始对话', shortcut: 'C', icon: '💬', action: () => router.push('/chat') },
  { id: 'compare', name: '项目对比', shortcut: 'P', icon: '⚖️', action: () => router.push('/compare') },
  { id: 'home', name: '返回首页', shortcut: 'H', icon: '🏠', action: () => router.push('/') },
  { id: 'history', name: '历史记录', shortcut: 'Y', icon: '📜', action: () => router.push('/history') },
]

// 热门项目快捷分析
const quickAnalysis = [
  { repo: 'apache/dubbo', name: 'Apache Dubbo' },
  { repo: 'vuejs/vue', name: 'Vue.js' },
  { repo: 'X-lab2017/open-digger', name: 'OpenDigger' },
  { repo: 'facebook/react', name: 'React' },
]

function handleKeyDown(e: KeyboardEvent) {
  // Ctrl/Cmd + K 打开命令面板
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    showCommandPalette.value = !showCommandPalette.value
    if (showCommandPalette.value) {
      setTimeout(() => searchInputRef.value?.focus(), 100)
    }
  }
  
  // ESC 关闭
  if (e.key === 'Escape') {
    showCommandPalette.value = false
    searchQuery.value = ''
  }
}

function executeCommand(command: typeof commands[0]) {
  command.action()
  showCommandPalette.value = false
  searchQuery.value = ''
}

function analyzeQuick(repo: string) {
  router.push(`/analysis/${repo}`)
  showCommandPalette.value = false
  searchQuery.value = ''
}

function searchRepo() {
  if (searchQuery.value.includes('/')) {
    router.push(`/analysis/${searchQuery.value}`)
  } else {
    router.push({ name: 'Chat', query: { q: `分析 ${searchQuery.value}` } })
  }
  showCommandPalette.value = false
  searchQuery.value = ''
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<template>
  <!-- 快捷键提示（右下角） -->
  <div class="fixed bottom-4 right-4 z-40">
    <button
      @click="showCommandPalette = true"
      class="px-3 py-2 glass text-slate-400 text-sm rounded-lg hover:text-white hover:border-accent/30 transition-all flex items-center gap-2"
    >
      <span>⌘</span>
      <span>K</span>
    </button>
  </div>
  
  <!-- 命令面板 -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="showCommandPalette"
        class="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
      >
        <!-- 遮罩 -->
        <div
          class="absolute inset-0 bg-black/60 backdrop-blur-sm"
          @click="showCommandPalette = false"
        ></div>
        
        <!-- 面板 -->
        <div class="relative w-full max-w-xl mx-4 glass-dark rounded-2xl shadow-2xl shadow-black/50 overflow-hidden animate-scale-in">
          <!-- 搜索框 -->
          <div class="p-4 border-b border-white/10">
            <div class="flex items-center gap-3">
              <span class="text-xl">🔍</span>
              <input
                ref="searchInputRef"
                v-model="searchQuery"
                type="text"
                placeholder="搜索项目或输入命令..."
                class="flex-1 bg-transparent text-white placeholder-slate-500 focus:outline-none text-lg"
                @keyup.enter="searchRepo"
              />
              <kbd class="px-2 py-1 bg-surface-light/50 text-slate-400 text-xs rounded">ESC</kbd>
            </div>
          </div>
          
          <!-- 快速分析 -->
          <div v-if="!searchQuery" class="p-4 border-b border-white/10">
            <div class="text-xs text-slate-500 mb-3">快速分析</div>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="item in quickAnalysis"
                :key="item.repo"
                @click="analyzeQuick(item.repo)"
                class="p-3 bg-surface-light/20 rounded-xl text-left hover:bg-surface-light/40 transition-colors group"
              >
                <div class="text-white group-hover:text-accent-light transition-colors">{{ item.name }}</div>
                <div class="text-xs text-slate-500">{{ item.repo }}</div>
              </button>
            </div>
          </div>
          
          <!-- 命令列表 -->
          <div class="p-2 max-h-80 overflow-y-auto">
            <div class="text-xs text-slate-500 px-3 py-2">快捷命令</div>
            <div
              v-for="cmd in commands"
              :key="cmd.id"
              @click="executeCommand(cmd)"
              class="flex items-center gap-3 px-3 py-3 hover:bg-surface-light/30 rounded-xl cursor-pointer transition-colors group"
            >
              <span class="text-xl">{{ cmd.icon }}</span>
              <span class="flex-1 text-white group-hover:text-accent-light transition-colors">
                {{ cmd.name }}
              </span>
              <kbd class="px-2 py-1 bg-surface-light/50 text-slate-400 text-xs rounded">
                {{ cmd.shortcut }}
              </kbd>
            </div>
          </div>
          
          <!-- 底部提示 -->
          <div class="p-3 bg-surface-light/20 flex items-center justify-between text-xs text-slate-500">
            <span>↵ 执行 · ↑↓ 导航 · ESC 关闭</span>
            <span>OpenSource Copilot</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.animate-scale-in {
  animation: scaleIn 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.glass-dark {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>

