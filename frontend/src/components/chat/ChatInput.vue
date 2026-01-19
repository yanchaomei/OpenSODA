<script setup lang="ts">
import { ref, computed } from 'vue'
import VoiceInput from './VoiceInput.vue'

const props = defineProps<{
  disabled?: boolean
  placeholder?: string
}>()

const emit = defineEmits<{
  send: [message: string]
}>()

const message = ref('')
const isFocused = ref(false)
const voiceError = ref('')

const canSend = computed(() => message.value.trim().length > 0 && !props.disabled)

function handleSend() {
  if (!canSend.value) return
  emit('send', message.value.trim())
  message.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

// 语音输入结果
function handleVoiceTranscript(text: string) {
  message.value = text
  voiceError.value = ''
  // 自动发送
  setTimeout(() => {
    if (message.value === text) {
      handleSend()
    }
  }, 500)
}

function handleVoiceError(error: string) {
  voiceError.value = error
  setTimeout(() => {
    voiceError.value = ''
  }, 3000)
}

// 快捷命令
const quickCommands = [
  { icon: '📊', text: '分析', hint: '分析 [仓库]' },
  { icon: '🔍', text: '诊断', hint: '诊断 [仓库] 的问题' },
  { icon: '💡', text: '建议', hint: '给 [仓库] 一些改进建议' },
  { icon: '📈', text: '趋势', hint: '查看 [仓库] 的活跃度趋势' },
]

function insertCommand(hint: string) {
  message.value = hint
}
</script>

<template>
  <div class="chat-input-wrapper">
    <!-- 快捷命令提示 -->
    <div v-if="isFocused && !message" class="quick-commands">
      <button
        v-for="cmd in quickCommands"
        :key="cmd.text"
        @click="insertCommand(cmd.hint)"
        class="quick-cmd-btn"
      >
        <span>{{ cmd.icon }}</span>
        <span>{{ cmd.text }}</span>
      </button>
    </div>
    
    <!-- 输入框容器 -->
    <div 
      :class="[
        'input-container glass',
        isFocused ? 'ring-2 ring-accent/50' : '',
        disabled ? 'opacity-50' : ''
      ]"
    >
      <!-- Agent 指示器 -->
      <div class="flex items-center gap-2 px-4 py-2 border-b border-white/5">
        <div class="flex items-center gap-1.5">
          <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span class="text-xs text-slate-500">Agent 就绪</span>
        </div>
        <div class="flex-1"></div>
        <div class="text-xs text-slate-600">支持 Markdown 格式</div>
      </div>
      
      <!-- 输入区域 -->
      <div class="flex items-end gap-3 p-3">
        <textarea
          v-model="message"
          :placeholder="placeholder || '输入消息与 Agent 对话，例如：分析 apache/dubbo 的健康状况'"
          :disabled="disabled"
          @focus="isFocused = true"
          @blur="isFocused = false"
          @keydown="handleKeydown"
          rows="1"
          class="chat-textarea"
        />
        
        <!-- 语音输入 -->
        <VoiceInput
          @transcript="handleVoiceTranscript"
          @error="handleVoiceError"
        />
        
        <!-- 发送按钮 -->
        <button
          @click="handleSend"
          :disabled="!canSend"
          :class="[
            'send-btn',
            canSend ? 'send-btn-active' : 'send-btn-disabled'
          ]"
        >
          <svg v-if="disabled" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
      
      <!-- 语音错误提示 -->
      <Transition name="slide">
        <div v-if="voiceError" class="px-4 py-2 bg-red-500/10 text-red-400 text-sm border-t border-red-500/20">
          {{ voiceError }}
        </div>
      </Transition>
    </div>
    
    <!-- 底部提示 -->
    <div class="flex items-center justify-center gap-4 mt-2 text-xs text-slate-600">
      <span>💡 提示：输入仓库路径如 <code class="px-1 py-0.5 bg-surface rounded">owner/repo</code> 进行分析</span>
    </div>
  </div>
</template>

<style scoped>
.chat-input-wrapper {
  @apply relative;
}

.quick-commands {
  @apply absolute bottom-full left-0 right-0 mb-2 flex gap-2 justify-center;
  animation: slide-up 0.2s ease-out;
}

.quick-cmd-btn {
  @apply flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm;
  @apply bg-surface border border-white/10 text-slate-400;
  @apply hover:border-accent/50 hover:text-white hover:bg-surface-light/50;
  @apply transition-all duration-200;
}

.input-container {
  @apply rounded-2xl overflow-hidden transition-all duration-200;
  @apply border border-white/10;
}

.chat-textarea {
  @apply flex-1 bg-transparent text-white placeholder-slate-500;
  @apply resize-none outline-none text-sm;
  @apply min-h-[40px] max-h-[200px];
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.1) transparent;
}

.send-btn {
  @apply p-2.5 rounded-xl transition-all duration-200 flex-shrink-0;
}

.send-btn-active {
  @apply bg-gradient-to-r from-accent to-primary-500 text-white;
  @apply hover:opacity-90 hover:scale-105;
  @apply shadow-lg shadow-accent/25;
}

.send-btn-disabled {
  @apply bg-surface-light text-slate-500 cursor-not-allowed;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
