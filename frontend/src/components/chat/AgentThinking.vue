<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const props = defineProps<{
  status?: string
  toolCalls?: Array<{
    name: string
    displayName?: string
    input?: any
    output?: string
    status: 'pending' | 'running' | 'completed' | 'error'
  }>
  isActive: boolean
}>()

const thoughts = ref<string[]>([])
const currentThought = ref('')

// 模拟思考过程
const thinkingPhrases = [
  '分析用户意图...',
  '确定需要调用的工具...',
  '准备参数...',
  '执行工具调用...',
  '处理返回结果...',
  '整理最终回复...'
]

let thoughtIndex = 0

watch(() => props.status, (newStatus) => {
  if (newStatus?.includes('思考')) {
    currentThought.value = thinkingPhrases[0]
  } else if (newStatus?.includes('推理')) {
    currentThought.value = thinkingPhrases[1]
  }
})

watch(() => props.toolCalls?.length, () => {
  if (props.toolCalls?.length) {
    currentThought.value = thinkingPhrases[3]
  }
})
</script>

<template>
  <div v-if="isActive" class="agent-thinking-container">
    <!-- 思维链可视化 -->
    <div class="glass-dark rounded-xl p-4 mb-4 border border-accent/30">
      <div class="flex items-center gap-2 mb-3">
        <div class="relative">
          <div class="w-3 h-3 bg-accent rounded-full animate-pulse"></div>
          <div class="absolute inset-0 w-3 h-3 bg-accent rounded-full animate-ping"></div>
        </div>
        <span class="text-sm font-medium text-accent-light">Agent 思维链</span>
      </div>
      
      <!-- 当前状态 -->
      <div v-if="status" class="flex items-center gap-2 text-white mb-3">
        <span class="text-lg">{{ status.charAt(0) }}</span>
        <span class="text-sm">{{ status.slice(1) }}</span>
      </div>
      
      <!-- 工具调用流程 -->
      <div v-if="toolCalls?.length" class="space-y-2">
        <div class="text-xs text-slate-500 mb-2">工具调用链:</div>
        <div 
          v-for="(tool, index) in toolCalls" 
          :key="index"
          class="flex items-center gap-3"
        >
          <!-- 连接线 -->
          <div class="flex flex-col items-center">
            <div 
              :class="[
                'w-8 h-8 rounded-lg flex items-center justify-center text-sm',
                tool.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                tool.status === 'running' ? 'bg-accent/20 text-accent-light animate-pulse' :
                'bg-slate-700/50 text-slate-500'
              ]"
            >
              {{ tool.status === 'completed' ? '✓' : tool.status === 'running' ? '⟳' : index + 1 }}
            </div>
            <div v-if="index < (toolCalls?.length || 0) - 1" class="w-0.5 h-4 bg-slate-700"></div>
          </div>
          
          <!-- 工具信息 -->
          <div class="flex-1">
            <div class="text-sm text-white font-medium">{{ tool.displayName || tool.name }}</div>
            <div v-if="tool.input" class="text-xs text-slate-500 mt-0.5">
              参数: {{ typeof tool.input === 'object' ? JSON.stringify(tool.input) : tool.input }}
            </div>
          </div>
          
          <!-- 状态 -->
          <div 
            :class="[
              'text-xs px-2 py-1 rounded',
              tool.status === 'completed' ? 'bg-green-500/20 text-green-400' :
              tool.status === 'running' ? 'bg-accent/20 text-accent-light' :
              'bg-slate-700/50 text-slate-500'
            ]"
          >
            {{ tool.status === 'completed' ? '完成' : tool.status === 'running' ? '执行中' : '等待' }}
          </div>
        </div>
      </div>
      
      <!-- 无工具调用时的加载动画 -->
      <div v-else class="flex items-center gap-3">
        <div class="loading-brain">
          <div class="brain-wave"></div>
          <div class="brain-wave"></div>
          <div class="brain-wave"></div>
        </div>
        <span class="text-sm text-slate-400">{{ currentThought || '正在处理...' }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.loading-brain {
  display: flex;
  gap: 2px;
  align-items: flex-end;
  height: 20px;
}

.brain-wave {
  width: 4px;
  background: linear-gradient(to top, var(--color-accent), var(--color-primary-500));
  border-radius: 2px;
  animation: brain-pulse 1s ease-in-out infinite;
}

.brain-wave:nth-child(1) {
  height: 8px;
  animation-delay: 0s;
}

.brain-wave:nth-child(2) {
  height: 16px;
  animation-delay: 0.2s;
}

.brain-wave:nth-child(3) {
  height: 12px;
  animation-delay: 0.4s;
}

@keyframes brain-pulse {
  0%, 100% {
    transform: scaleY(1);
    opacity: 0.7;
  }
  50% {
    transform: scaleY(1.5);
    opacity: 1;
  }
}
</style>

