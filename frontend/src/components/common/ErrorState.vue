<script setup lang="ts">
/**
 * ErrorState - 友好的错误状态组件
 * 提供清晰的错误信息和重试选项
 */
interface Props {
  title?: string
  message: string
  type?: 'error' | 'warning' | 'info' | 'network'
  showRetry?: boolean
  showHome?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '出错了',
  type: 'error',
  showRetry: true,
  showHome: false
})

const emit = defineEmits<{
  (e: 'retry'): void
}>()

const icons = {
  error: '😢',
  warning: '⚠️',
  info: 'ℹ️',
  network: '🌐'
}

const colors = {
  error: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    text: 'text-red-400',
    button: 'from-red-500 to-rose-600'
  },
  warning: {
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/30',
    text: 'text-yellow-400',
    button: 'from-yellow-500 to-amber-600'
  },
  info: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    text: 'text-blue-400',
    button: 'from-blue-500 to-indigo-600'
  },
  network: {
    bg: 'bg-slate-500/10',
    border: 'border-slate-500/30',
    text: 'text-slate-400',
    button: 'from-slate-500 to-slate-600'
  }
}

const currentColors = colors[props.type]
</script>

<template>
  <div :class="[
    'p-8 rounded-2xl border text-center',
    currentColors.bg,
    currentColors.border
  ]">
    <!-- 图标 -->
    <div class="text-6xl mb-4">
      {{ icons[type] }}
    </div>
    
    <!-- 标题 -->
    <h3 :class="['text-xl font-semibold mb-2', currentColors.text]">
      {{ title }}
    </h3>
    
    <!-- 错误信息 -->
    <p class="text-slate-400 mb-6 max-w-md mx-auto">
      {{ message }}
    </p>
    
    <!-- 操作按钮 -->
    <div class="flex items-center justify-center gap-3">
      <button
        v-if="showRetry"
        @click="emit('retry')"
        :class="[
          'px-6 py-2.5 bg-gradient-to-r text-white font-medium rounded-xl',
          'hover:opacity-90 transition-all shadow-lg',
          currentColors.button
        ]"
      >
        🔄 重试
      </button>
      
      <router-link
        v-if="showHome"
        to="/"
        class="px-6 py-2.5 glass text-white font-medium rounded-xl hover:bg-white/10 transition-all"
      >
        🏠 返回首页
      </router-link>
    </div>
    
    <!-- 帮助提示 -->
    <div class="mt-6 text-sm text-slate-500">
      <p v-if="type === 'network'">
        请检查网络连接后重试
      </p>
      <p v-else-if="type === 'error'">
        如果问题持续存在，请联系管理员
      </p>
    </div>
  </div>
</template>

