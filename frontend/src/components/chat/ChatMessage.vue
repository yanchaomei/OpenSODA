<script setup lang="ts">
import { computed, ref } from 'vue'
import { marked } from 'marked'
import type { Message } from '@/stores/chat'

const props = defineProps<{
  message: Message
}>()

const isUser = computed(() => props.message.role === 'user')
const showToolDetails = ref(false)

const formattedContent = computed(() => {
  if (!props.message.content) return ''
  return marked(props.message.content, { breaks: true })
})

const formattedTime = computed(() => {
  return new Date(props.message.timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
})

const hasToolCalls = computed(() => {
  return props.message.toolCalls && props.message.toolCalls.length > 0
})
</script>

<template>
  <div :class="['flex gap-4', isUser ? 'flex-row-reverse' : '']">
    <!-- 头像 -->
    <div
      :class="[
        'w-10 h-10 rounded-xl flex items-center justify-center text-lg flex-shrink-0',
        isUser ? 'bg-primary-500/20' : 'bg-gradient-to-br from-accent to-primary-500'
      ]"
    >
      {{ isUser ? '👤' : '🤖' }}
    </div>
    
    <!-- 消息内容 -->
    <div :class="['flex flex-col max-w-[75%]', isUser ? 'items-end' : 'items-start']">
      <!-- Agent 状态标签 -->
      <div v-if="!isUser && message.agentStatus" class="mb-2">
        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-accent/20 text-accent-light border border-accent/30">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
          </span>
          {{ message.agentStatus }}
        </span>
      </div>
      
      <!-- 工具调用展示 -->
      <div v-if="hasToolCalls" class="w-full mb-3 space-y-2">
        <div
          v-for="(toolCall, index) in message.toolCalls"
          :key="index"
          class="glass-dark rounded-lg overflow-hidden"
        >
          <!-- 工具调用头部 -->
          <div 
            class="flex items-center justify-between px-3 py-2 bg-surface-light/30 cursor-pointer hover:bg-surface-light/50 transition-colors"
            @click="showToolDetails = !showToolDetails"
          >
            <div class="flex items-center gap-2">
              <span class="text-lg">{{ toolCall.status === 'running' ? '⏳' : toolCall.status === 'completed' ? '✅' : '🔧' }}</span>
              <span class="text-sm font-medium text-white">{{ toolCall.displayName || toolCall.name }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span v-if="toolCall.status === 'running'" class="text-xs text-accent-light animate-pulse">执行中...</span>
              <span v-else-if="toolCall.status === 'completed'" class="text-xs text-green-400">已完成</span>
              <svg 
                :class="['w-4 h-4 text-slate-400 transition-transform', showToolDetails ? 'rotate-180' : '']" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          
          <!-- 工具调用详情 -->
          <transition name="expand">
            <div v-if="showToolDetails" class="px-3 py-2 border-t border-white/5">
              <div v-if="toolCall.input" class="mb-2">
                <div class="text-xs text-slate-500 mb-1">输入参数:</div>
                <code class="text-xs text-slate-300 bg-surface-dark px-2 py-1 rounded block">
                  {{ typeof toolCall.input === 'object' ? JSON.stringify(toolCall.input, null, 2) : toolCall.input }}
                </code>
              </div>
              <div v-if="toolCall.output">
                <div class="text-xs text-slate-500 mb-1">返回结果:</div>
                <div class="text-xs text-slate-300 bg-surface-dark px-2 py-1 rounded max-h-32 overflow-y-auto">
                  {{ toolCall.output.slice(0, 300) }}{{ toolCall.output.length > 300 ? '...' : '' }}
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
      
      <!-- 消息气泡 -->
      <div
        v-if="message.content"
        :class="[isUser ? 'chat-bubble-user' : 'chat-bubble-assistant']"
      >
        <div class="markdown-body" v-html="formattedContent"></div>
        <span v-if="message.isStreaming" class="typing-cursor"></span>
      </div>
      
      <!-- 时间戳 -->
      <span class="text-xs text-slate-500 mt-1">{{ formattedTime }}</span>
      
      <!-- 附加数据卡片 -->
      <div v-if="!isUser && (message.metrics || message.recommendations)" class="mt-4 space-y-4 w-full">
        <!-- 健康度评分卡片 -->
        <div v-if="message.healthScore" class="glass p-4">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-sm font-medium text-white">📊 健康度评分</h4>
            <span 
              :class="[
                'text-2xl font-bold',
                message.healthScore.overall >= 80 ? 'text-emerald-400' :
                message.healthScore.overall >= 60 ? 'text-green-400' :
                message.healthScore.overall >= 40 ? 'text-yellow-400' : 'text-red-400'
              ]"
            >
              {{ message.healthScore.overall }}
            </span>
          </div>
          <div class="grid grid-cols-4 gap-2 text-center">
            <div>
              <div class="text-lg font-semibold text-white">{{ message.healthScore.activity }}</div>
              <div class="text-xs text-slate-500">活跃度</div>
            </div>
            <div>
              <div class="text-lg font-semibold text-white">{{ message.healthScore.community }}</div>
              <div class="text-xs text-slate-500">社区</div>
            </div>
            <div>
              <div class="text-lg font-semibold text-white">{{ message.healthScore.maintenance }}</div>
              <div class="text-xs text-slate-500">维护</div>
            </div>
            <div>
              <div class="text-lg font-semibold text-white">{{ message.healthScore.growth }}</div>
              <div class="text-xs text-slate-500">增长</div>
            </div>
          </div>
        </div>
        
        <!-- 指标卡片 -->
        <div v-if="message.metrics" class="glass p-4">
          <h4 class="text-sm font-medium text-slate-400 mb-3">📈 关键指标</h4>
          <div class="grid grid-cols-3 gap-3">
            <div v-if="message.metrics.openrank" class="text-center p-2 bg-surface-light/30 rounded-lg">
              <div class="text-lg font-bold text-accent-light">{{ message.metrics.openrank?.toFixed(2) }}</div>
              <div class="text-xs text-slate-500">OpenRank</div>
            </div>
            <div v-if="message.metrics.activity" class="text-center p-2 bg-surface-light/30 rounded-lg">
              <div class="text-lg font-bold text-primary-400">{{ message.metrics.activity?.toFixed(2) }}</div>
              <div class="text-xs text-slate-500">活跃度</div>
            </div>
            <div v-if="message.metrics.bus_factor" class="text-center p-2 bg-surface-light/30 rounded-lg">
              <div class="text-lg font-bold text-green-400">{{ message.metrics.bus_factor }}</div>
              <div class="text-xs text-slate-500">巴士因子</div>
            </div>
          </div>
        </div>
        
        <!-- 建议列表 -->
        <div v-if="message.recommendations?.length" class="glass p-4">
          <h4 class="text-sm font-medium text-slate-400 mb-3">💡 改进建议</h4>
          <ul class="space-y-2">
            <li
              v-for="(rec, index) in message.recommendations.slice(0, 3)"
              :key="index"
              class="flex items-start gap-2 p-2 bg-surface-light/20 rounded-lg"
            >
              <span
                :class="[
                  'flex-shrink-0 px-2 py-0.5 rounded text-xs font-medium',
                  rec.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                  rec.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-green-500/20 text-green-400'
                ]"
              >
                {{ rec.priority === 'high' ? '高' : rec.priority === 'medium' ? '中' : '低' }}
              </span>
              <div>
                <div class="text-sm text-white font-medium">{{ rec.title }}</div>
                <div class="text-xs text-slate-400 mt-0.5">{{ rec.description }}</div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 200px;
}
</style>
