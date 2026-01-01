<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const repoInput = ref('')

const features = [
  {
    icon: '📊',
    title: '健康度分析',
    description: '基于 OpenRank 等多维度指标，全面评估开源项目的健康状况'
  },
  {
    icon: '🔍',
    title: '问题诊断',
    description: '智能识别社区运营中的问题和潜在风险'
  },
  {
    icon: '💡',
    title: '运营建议',
    description: '基于最佳实践，提供可执行的改进建议'
  },
  {
    icon: '🤖',
    title: 'AI 对话',
    description: '自然语言交互，随时获取专业的开源运营指导'
  }
]

const quickActions = [
  { label: '分析 apache/dubbo', repo: 'apache/dubbo' },
  { label: '分析 vuejs/vue', repo: 'vuejs/vue' },
  { label: '分析 facebook/react', repo: 'facebook/react' },
]

function startAnalysis() {
  if (repoInput.value.trim()) {
    router.push(`/analysis/${repoInput.value}`)
  }
}

function quickAnalyze(repo: string) {
  router.push(`/analysis/${repo}`)
}

function goToChat() {
  router.push('/chat')
}
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <!-- Hero Section -->
    <div class="text-center mb-16 animate-fade-in">
      <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 border border-accent/20 text-accent-light text-sm mb-6">
        <span>🎯</span>
        <span>OpenSODA 2025 参赛作品</span>
      </div>
      
      <h1 class="text-5xl font-bold text-white mb-6">
        <span class="bg-gradient-to-r from-primary-400 via-accent to-primary-400 bg-clip-text text-transparent">
          OpenSource Copilot
        </span>
      </h1>
      
      <p class="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
        基于多 Agent 架构的开源社区智能运营助手<br/>
        帮助项目维护者进行社区健康度诊断、贡献者分析和运营决策
      </p>
      
      <!-- 快速开始 -->
      <div class="flex flex-col items-center gap-4">
        <div class="flex gap-4 w-full max-w-xl">
          <input
            v-model="repoInput"
            @keyup.enter="startAnalysis"
            type="text"
            placeholder="输入仓库地址，如 apache/dubbo"
            class="flex-1 bg-surface border border-white/10 rounded-xl px-5 py-4 text-white placeholder-slate-500 focus:outline-none focus:border-accent/50 focus:ring-2 focus:ring-accent/20 transition-all"
          />
          <button
            @click="startAnalysis"
            class="px-8 py-4 bg-gradient-to-r from-accent to-primary-500 text-white font-semibold rounded-xl hover:opacity-90 transition-opacity"
          >
            开始分析
          </button>
        </div>
        
        <div class="flex items-center gap-2 text-sm text-slate-500">
          <span>快速体验：</span>
          <button
            v-for="action in quickActions"
            :key="action.repo"
            @click="quickAnalyze(action.repo)"
            class="px-3 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          >
            {{ action.label }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Features Grid -->
    <div class="grid grid-cols-2 gap-6 mb-16">
      <div
        v-for="feature in features"
        :key="feature.title"
        class="glass p-6 hover:border-accent/30 transition-colors animate-slide-up"
      >
        <div class="text-3xl mb-4">{{ feature.icon }}</div>
        <h3 class="text-lg font-semibold text-white mb-2">{{ feature.title }}</h3>
        <p class="text-slate-400">{{ feature.description }}</p>
      </div>
    </div>
    
    <!-- CTA Section -->
    <div class="glass p-8 text-center">
      <h2 class="text-2xl font-bold text-white mb-4">有问题？直接问我！</h2>
      <p class="text-slate-400 mb-6">
        支持自然语言对话，随时获取开源运营相关的专业建议
      </p>
      <button
        @click="goToChat"
        class="inline-flex items-center gap-2 px-6 py-3 bg-surface-light text-white rounded-xl hover:bg-surface transition-colors"
      >
        <span>💬</span>
        <span>开始对话</span>
      </button>
    </div>
    
    <!-- Tech Stack -->
    <div class="mt-16 text-center">
      <p class="text-sm text-slate-500 mb-4">技术栈</p>
      <div class="flex items-center justify-center gap-8 text-slate-400">
        <div class="flex items-center gap-2">
          <span>🔧</span>
          <span>OpenDigger</span>
        </div>
        <div class="flex items-center gap-2">
          <span>🤖</span>
          <span>LangGraph</span>
        </div>
        <div class="flex items-center gap-2">
          <span>📚</span>
          <span>MaxKB</span>
        </div>
        <div class="flex items-center gap-2">
          <span>📊</span>
          <span>DataEase</span>
        </div>
      </div>
    </div>
  </div>
</template>

