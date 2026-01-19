<script setup lang="ts">
/**
 * ThemeSwitcher - 主题切换器
 * 支持暗色/亮色/系统主题切换
 */
import { ref, onMounted, watch } from 'vue'

type Theme = 'dark' | 'light' | 'system'

const currentTheme = ref<Theme>('dark')
const showMenu = ref(false)

const themes = [
  { id: 'dark' as Theme, name: '深色', icon: '🌙' },
  { id: 'light' as Theme, name: '浅色', icon: '☀️' },
  { id: 'system' as Theme, name: '跟随系统', icon: '💻' },
]

function getSystemTheme(): 'dark' | 'light' {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyTheme(theme: Theme) {
  const effectiveTheme = theme === 'system' ? getSystemTheme() : theme
  
  if (effectiveTheme === 'light') {
    document.documentElement.classList.add('light-theme')
    document.documentElement.classList.remove('dark-theme')
  } else {
    document.documentElement.classList.add('dark-theme')
    document.documentElement.classList.remove('light-theme')
  }
}

function setTheme(theme: Theme) {
  currentTheme.value = theme
  localStorage.setItem('theme', theme)
  applyTheme(theme)
  showMenu.value = false
}

onMounted(() => {
  const saved = localStorage.getItem('theme') as Theme | null
  if (saved) {
    currentTheme.value = saved
    applyTheme(saved)
  }
  
  // 监听系统主题变化
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (currentTheme.value === 'system') {
      applyTheme('system')
    }
  })
})

const currentThemeData = () => themes.find(t => t.id === currentTheme.value)
</script>

<template>
  <div class="relative">
    <!-- 切换按钮 -->
    <button
      @click="showMenu = !showMenu"
      class="w-10 h-10 rounded-xl glass flex items-center justify-center text-lg hover:bg-surface-light/50 transition-all"
      title="切换主题"
    >
      {{ currentThemeData()?.icon }}
    </button>
    
    <!-- 下拉菜单 -->
    <Transition name="menu">
      <div
        v-if="showMenu"
        class="absolute right-0 top-full mt-2 w-40 glass-dark rounded-xl overflow-hidden shadow-2xl z-50"
      >
        <button
          v-for="theme in themes"
          :key="theme.id"
          @click="setTheme(theme.id)"
          :class="[
            'w-full px-4 py-3 flex items-center gap-3 hover:bg-surface-light/30 transition-colors text-left',
            currentTheme === theme.id ? 'bg-accent/10 text-accent-light' : 'text-slate-300'
          ]"
        >
          <span class="text-lg">{{ theme.icon }}</span>
          <span>{{ theme.name }}</span>
          <span v-if="currentTheme === theme.id" class="ml-auto text-accent">✓</span>
        </button>
      </div>
    </Transition>
    
    <!-- 点击外部关闭 -->
    <div
      v-if="showMenu"
      class="fixed inset-0 z-40"
      @click="showMenu = false"
    ></div>
  </div>
</template>

<style scoped>
.menu-enter-active,
.menu-leave-active {
  transition: all 0.2s ease;
}

.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.glass-dark {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>

