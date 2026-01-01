<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import ChatInput from '@/components/chat/ChatInput.vue'

const route = useRoute()
const chatStore = useChatStore()
const messagesContainer = ref<HTMLElement | null>(null)

// 快捷问题分类
const quickCategories = [
  {
    title: '🔍 项目分析',
    questions: [
      { text: '分析 apache/dubbo', icon: '📊' },
      { text: '分析 vuejs/vue 的健康度', icon: '💚' },
      { text: '帮我分析 X-lab2017/open-digger', icon: '🔬' },
    ]
  },
  {
    title: '💡 运营建议',
    questions: [
      { text: '如何提升开源项目的 OpenRank 值？', icon: '📈' },
      { text: '如何吸引更多贡献者参与项目？', icon: '👥' },
      { text: '什么是巴士因子？为什么重要？', icon: '🚌' },
    ]
  },
  {
    title: '🛠️ 工具使用',
    questions: [
      { text: '查找 kubernetes/kubernetes 适合新手的 Issue', icon: '🎯' },
      { text: '获取 facebook/react 的贡献者列表', icon: '👨‍💻' },
      { text: '查看 microsoft/vscode 的活跃度趋势', icon: '📉' },
    ]
  }
]

function sendQuickQuestion(question: string) {
  chatStore.sendMessage(question)
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 监听消息变化，自动滚动
watch(
  () => chatStore.messages.length,
  () => scrollToBottom()
)

// 监听流式内容变化
watch(
  () => chatStore.messages[chatStore.messages.length - 1]?.content,
  () => scrollToBottom()
)

// 监听工具调用变化
watch(
  () => chatStore.messages[chatStore.messages.length - 1]?.toolCalls?.length,
  () => scrollToBottom(),
  { deep: true }
)

onMounted(() => {
  // 检查是否有查询参数
  const query = route.query.q as string
  if (query) {
    chatStore.sendMessage(query)
  }
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- 顶部状态栏 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-accent to-primary-500 flex items-center justify-center text-xl shadow-lg">
          🤖
        </div>
        <div>
          <h1 class="text-lg font-bold text-white">OpenSource Copilot</h1>
          <p class="text-xs text-slate-400">基于 ReAct 的多工具 Agent</p>
        </div>
      </div>
      
      <div class="flex items-center gap-2">
        <!-- 当前仓库标签 -->
        <div v-if="chatStore.currentRepo" class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface border border-white/10">
          <span class="text-xs text-slate-400">当前:</span>
          <span class="text-sm text-white font-mono">{{ chatStore.currentRepo }}</span>
          <button 
            @click="chatStore.setRepo('')"
            class="text-slate-500 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>
        
        <!-- 清空对话 -->
        <button
          v-if="chatStore.hasMessages"
          @click="chatStore.clearMessages()"
          class="px-3 py-1.5 text-sm text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
        >
          清空对话
        </button>
      </div>
    </div>
    
    <!-- 消息列表 -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto space-y-6 pb-4 pr-2"
    >
      <!-- 欢迎消息 -->
      <div v-if="!chatStore.hasMessages" class="py-8">
        <!-- Agent 介绍 -->
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-accent/20 to-primary-500/20 border border-accent/30 mb-4">
            <span class="text-4xl">🤖</span>
          </div>
          <h2 class="text-2xl font-bold text-white mb-2">
            你好，我是 OpenSource Copilot
          </h2>
          <p class="text-slate-400 max-w-lg mx-auto">
            我是一个基于 <span class="text-accent-light">ReAct</span> 模式的智能 Agent，
            能够调用多种工具来分析开源项目、诊断问题并提供建议。
          </p>
        </div>
        
        <!-- Agent 能力展示 -->
        <div class="glass p-4 mb-8 max-w-2xl mx-auto">
          <h3 class="text-sm font-medium text-slate-300 mb-3">🛠️ 我可以使用的工具：</h3>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div class="flex items-center gap-2 text-slate-400">
              <span class="w-6 h-6 rounded bg-accent/20 flex items-center justify-center text-xs">📊</span>
              <span>项目健康度分析</span>
            </div>
            <div class="flex items-center gap-2 text-slate-400">
              <span class="w-6 h-6 rounded bg-accent/20 flex items-center justify-center text-xs">🔍</span>
              <span>问题诊断</span>
            </div>
            <div class="flex items-center gap-2 text-slate-400">
              <span class="w-6 h-6 rounded bg-accent/20 flex items-center justify-center text-xs">💡</span>
              <span>改进建议生成</span>
            </div>
            <div class="flex items-center gap-2 text-slate-400">
              <span class="w-6 h-6 rounded bg-accent/20 flex items-center justify-center text-xs">📈</span>
              <span>OpenRank 查询</span>
            </div>
            <div class="flex items-center gap-2 text-slate-400">
              <span class="w-6 h-6 rounded bg-accent/20 flex items-center justify-center text-xs">👥</span>
              <span>贡献者分析</span>
            </div>
            <div class="flex items-center gap-2 text-slate-400">
              <span class="w-6 h-6 rounded bg-accent/20 flex items-center justify-center text-xs">🎯</span>
              <span>新手 Issue 查找</span>
            </div>
            <div class="flex items-center gap-2 text-slate-400">
              <span class="w-6 h-6 rounded bg-accent/20 flex items-center justify-center text-xs">📉</span>
              <span>活跃度趋势</span>
            </div>
            <div class="flex items-center gap-2 text-slate-400">
              <span class="w-6 h-6 rounded bg-accent/20 flex items-center justify-center text-xs">📚</span>
              <span>知识库检索</span>
            </div>
          </div>
        </div>
        
        <!-- 快捷问题 -->
        <div class="space-y-6 max-w-3xl mx-auto">
          <div v-for="category in quickCategories" :key="category.title">
            <h3 class="text-sm font-medium text-slate-400 mb-3">{{ category.title }}</h3>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="question in category.questions"
                :key="question.text"
                @click="sendQuickQuestion(question.text)"
                class="flex items-center gap-2 px-4 py-2 bg-surface border border-white/10 rounded-xl text-sm text-slate-300 hover:border-accent/50 hover:text-white hover:bg-surface-light/50 transition-all"
              >
                <span>{{ question.icon }}</span>
                <span>{{ question.text }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 消息列表 -->
      <TransitionGroup name="message">
        <ChatMessage
          v-for="message in chatStore.messages"
          :key="message.id"
          :message="message"
        />
      </TransitionGroup>
      
      <!-- 加载指示器 -->
      <div v-if="chatStore.isLoading && !chatStore.messages[chatStore.messages.length - 1]?.content" class="flex items-start gap-4">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-accent to-primary-500 flex items-center justify-center text-lg">
          🤖
        </div>
        <div class="chat-bubble-assistant">
          <div class="flex items-center gap-2">
            <div class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span class="text-sm text-slate-400">{{ chatStore.messages[chatStore.messages.length - 1]?.agentStatus || '正在思考...' }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <ChatInput
      @send="(msg) => chatStore.sendMessage(msg)"
      :disabled="chatStore.isLoading"
    />
  </div>
</template>

<style scoped>
.message-enter-active {
  transition: all 0.3s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
</style>
