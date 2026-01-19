<script setup lang="ts">
/**
 * About - 关于页面
 * 展示系统架构、技术栈、团队信息
 */
import { ref } from 'vue'
import SankeyFlow from '@/components/charts/SankeyFlow.vue'
import AgentNetwork from '@/components/chat/AgentNetwork.vue'

const activeTab = ref<'architecture' | 'features' | 'tech'>('architecture')

// Agent 网络数据
const agentNodes = [
  { id: 'user', name: '用户', type: 'tool' as const, status: 'idle' as const },
  { id: 'orchestrator', name: 'ReAct 协调器', type: 'orchestrator' as const, status: 'working' as const },
  { id: 'analysis', name: '分析 Agent', type: 'analysis' as const, status: 'idle' as const },
  { id: 'diagnosis', name: '诊断 Agent', type: 'diagnosis' as const, status: 'idle' as const },
  { id: 'opendigger', name: 'OpenDigger', type: 'tool' as const, status: 'idle' as const },
  { id: 'github', name: 'GitHub API', type: 'tool' as const, status: 'idle' as const },
  { id: 'llm', name: 'LLM', type: 'llm' as const, status: 'idle' as const },
]

const agentLinks = [
  { source: 'user', target: 'orchestrator', type: 'data' as const },
  { source: 'orchestrator', target: 'llm', type: 'control' as const },
  { source: 'orchestrator', target: 'analysis', type: 'control' as const },
  { source: 'orchestrator', target: 'diagnosis', type: 'control' as const },
  { source: 'analysis', target: 'opendigger', type: 'data' as const },
  { source: 'analysis', target: 'github', type: 'data' as const },
  { source: 'diagnosis', target: 'opendigger', type: 'data' as const },
  { source: 'llm', target: 'orchestrator', type: 'result' as const },
]

const techStack = [
  {
    category: '前端技术',
    items: [
      { name: 'Vue 3', desc: '渐进式框架', icon: '💚' },
      { name: 'TypeScript', desc: '类型安全', icon: '🔷' },
      { name: 'Pinia', desc: '状态管理', icon: '🍍' },
      { name: 'ECharts', desc: '数据可视化', icon: '📊' },
      { name: 'TailwindCSS', desc: '原子化 CSS', icon: '🎨' },
    ]
  },
  {
    category: '后端技术',
    items: [
      { name: 'FastAPI', desc: '高性能 API', icon: '⚡' },
      { name: 'LangGraph', desc: 'Agent 框架', icon: '🤖' },
      { name: 'Pydantic', desc: '数据验证', icon: '✅' },
      { name: 'Redis', desc: '缓存加速', icon: '🚀' },
      { name: 'WebSocket', desc: '实时通信', icon: '🔌' },
    ]
  },
  {
    category: '数据来源',
    items: [
      { name: 'OpenDigger', desc: '开源指标', icon: '📈' },
      { name: 'GitHub API', desc: '仓库数据', icon: '🐙' },
      { name: 'OpenAI', desc: 'LLM 推理', icon: '🧠' },
    ]
  }
]

const features = [
  {
    title: 'ReAct Agent 架构',
    desc: '基于 Reasoning + Acting 范式，实现自主思考与工具调用的闭环',
    icon: '🧠',
    details: ['思考链可视化', '多轮对话记忆', '工具调用追踪']
  },
  {
    title: '多维度健康评估',
    desc: '融合 OpenRank、活跃度、社区、维护、增长等多维指标',
    icon: '📊',
    details: ['5 大核心维度', '权重可配置', '历史趋势分析']
  },
  {
    title: '智能诊断建议',
    desc: '自动识别项目问题，生成针对性的改进建议',
    icon: '💡',
    details: ['问题自动检测', '优先级排序', '可操作建议']
  },
  {
    title: '流式响应体验',
    desc: '实时展示 Agent 思考过程，提供沉浸式交互体验',
    icon: '⚡',
    details: ['SSE 流式输出', '打字机效果', '思维链展示']
  },
  {
    title: '专业数据可视化',
    desc: '雷达图、趋势图、热力图等多种图表专业呈现',
    icon: '🎨',
    details: ['ECharts 图表', '响应式布局', '交互动画']
  },
  {
    title: '项目监控告警',
    desc: '持续监控项目健康度，阈值告警及时通知',
    icon: '🔔',
    details: ['定时检查', '阈值配置', '浏览器通知']
  }
]
</script>

<template>
  <div class="space-y-8">
    <!-- 页面标题 -->
    <div class="text-center py-8">
      <div class="inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-gradient-to-br from-accent via-primary-500 to-cyan-500 mb-6 shadow-2xl shadow-accent/30 animate-float">
        <span class="text-5xl">🤖</span>
      </div>
      <h1 class="text-4xl font-bold text-white mb-4">
        OpenSource Copilot
      </h1>
      <p class="text-xl text-slate-400 max-w-2xl mx-auto">
        基于 <span class="text-accent-light font-semibold">ReAct Agent</span> 架构的
        开源社区智能运营助手
      </p>
      <div class="flex items-center justify-center gap-4 mt-6">
        <span class="px-4 py-2 glass rounded-full text-sm text-slate-300">
          🏆 OpenSODA 2025 决赛作品
        </span>
        <span class="px-4 py-2 glass rounded-full text-sm text-slate-300">
          ⭐ MIT License
        </span>
      </div>
    </div>
    
    <!-- Tab 切换 -->
    <div class="flex justify-center">
      <div class="glass p-1 rounded-xl flex gap-1">
        <button
          v-for="tab in [
            { id: 'architecture', label: '系统架构', icon: '🏗️' },
            { id: 'features', label: '核心功能', icon: '✨' },
            { id: 'tech', label: '技术栈', icon: '🛠️' }
          ]"
          :key="tab.id"
          @click="activeTab = tab.id as any"
          :class="[
            'px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2',
            activeTab === tab.id 
              ? 'bg-accent text-white shadow-lg shadow-accent/30' 
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          ]"
        >
          <span>{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </button>
      </div>
    </div>
    
    <!-- 系统架构 -->
    <div v-show="activeTab === 'architecture'" class="space-y-6">
      <!-- 架构图 -->
      <div class="glass p-6 rounded-2xl">
        <h2 class="text-xl font-semibold text-white mb-6 flex items-center gap-2">
          <span class="text-2xl">🏗️</span>
          系统架构图
        </h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- 层级架构 -->
          <div class="space-y-4">
            <h3 class="text-lg font-medium text-white mb-4">分层架构</h3>
            
            <!-- 用户层 -->
            <div class="p-4 rounded-xl bg-gradient-to-r from-cyan-500/20 to-cyan-600/10 border border-cyan-500/30">
              <div class="text-cyan-400 font-semibold mb-2">🖥️ 表现层</div>
              <div class="flex flex-wrap gap-2">
                <span class="px-3 py-1 bg-cyan-500/20 rounded text-xs text-cyan-300">Vue 3 SPA</span>
                <span class="px-3 py-1 bg-cyan-500/20 rounded text-xs text-cyan-300">ECharts</span>
                <span class="px-3 py-1 bg-cyan-500/20 rounded text-xs text-cyan-300">WebSocket</span>
              </div>
            </div>
            
            <!-- API 层 -->
            <div class="p-4 rounded-xl bg-gradient-to-r from-violet-500/20 to-violet-600/10 border border-violet-500/30">
              <div class="text-violet-400 font-semibold mb-2">🔌 接口层</div>
              <div class="flex flex-wrap gap-2">
                <span class="px-3 py-1 bg-violet-500/20 rounded text-xs text-violet-300">FastAPI</span>
                <span class="px-3 py-1 bg-violet-500/20 rounded text-xs text-violet-300">REST API</span>
                <span class="px-3 py-1 bg-violet-500/20 rounded text-xs text-violet-300">SSE</span>
              </div>
            </div>
            
            <!-- Agent 层 -->
            <div class="p-4 rounded-xl bg-gradient-to-r from-amber-500/20 to-amber-600/10 border border-amber-500/30">
              <div class="text-amber-400 font-semibold mb-2">🤖 Agent 层</div>
              <div class="flex flex-wrap gap-2">
                <span class="px-3 py-1 bg-amber-500/20 rounded text-xs text-amber-300">LangGraph</span>
                <span class="px-3 py-1 bg-amber-500/20 rounded text-xs text-amber-300">ReAct</span>
                <span class="px-3 py-1 bg-amber-500/20 rounded text-xs text-amber-300">Tools</span>
              </div>
            </div>
            
            <!-- 数据层 -->
            <div class="p-4 rounded-xl bg-gradient-to-r from-emerald-500/20 to-emerald-600/10 border border-emerald-500/30">
              <div class="text-emerald-400 font-semibold mb-2">💾 数据层</div>
              <div class="flex flex-wrap gap-2">
                <span class="px-3 py-1 bg-emerald-500/20 rounded text-xs text-emerald-300">OpenDigger</span>
                <span class="px-3 py-1 bg-emerald-500/20 rounded text-xs text-emerald-300">GitHub API</span>
                <span class="px-3 py-1 bg-emerald-500/20 rounded text-xs text-emerald-300">Redis Cache</span>
              </div>
            </div>
          </div>
          
          <!-- Agent 网络 -->
          <div>
            <h3 class="text-lg font-medium text-white mb-4">Agent 协作网络</h3>
            <div class="bg-surface-light/20 rounded-xl p-4">
              <AgentNetwork :agents="agentNodes" :links="agentLinks" />
            </div>
          </div>
        </div>
      </div>
      
      <!-- 数据流向 -->
      <div class="glass p-6 rounded-2xl">
        <h2 class="text-xl font-semibold text-white mb-6 flex items-center gap-2">
          <span class="text-2xl">🔄</span>
          数据流向
        </h2>
        <SankeyFlow title="" />
      </div>
    </div>
    
    <!-- 核心功能 -->
    <div v-show="activeTab === 'features'" class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="(feature, index) in features" 
          :key="feature.title"
          class="glass p-6 rounded-2xl hover:border-accent/30 border border-transparent transition-all duration-300 group"
          :style="{ animationDelay: `${index * 100}ms` }"
        >
          <div class="flex items-center gap-4 mb-4">
            <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-accent/20 to-primary-500/20 flex items-center justify-center text-3xl group-hover:scale-110 transition-transform border border-accent/30">
              {{ feature.icon }}
            </div>
            <div>
              <h3 class="text-lg font-semibold text-white">{{ feature.title }}</h3>
            </div>
          </div>
          <p class="text-slate-400 text-sm mb-4">{{ feature.desc }}</p>
          <div class="flex flex-wrap gap-2">
            <span 
              v-for="detail in feature.details" 
              :key="detail"
              class="text-xs px-2 py-1 bg-surface-light/30 rounded text-slate-400"
            >
              {{ detail }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 技术栈 -->
    <div v-show="activeTab === 'tech'" class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div 
          v-for="stack in techStack" 
          :key="stack.category"
          class="glass p-6 rounded-2xl"
        >
          <h3 class="text-lg font-semibold text-white mb-4">{{ stack.category }}</h3>
          <div class="space-y-3">
            <div 
              v-for="item in stack.items" 
              :key="item.name"
              class="flex items-center gap-3 p-3 bg-surface-light/20 rounded-xl hover:bg-surface-light/40 transition-colors"
            >
              <span class="text-2xl">{{ item.icon }}</span>
              <div>
                <div class="text-white font-medium">{{ item.name }}</div>
                <div class="text-xs text-slate-400">{{ item.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部信息 -->
    <div class="text-center py-8 border-t border-white/5">
      <p class="text-slate-500 text-sm">
        Made with ❤️ for OpenSODA 2025 Competition
      </p>
      <div class="flex items-center justify-center gap-4 mt-4">
        <a href="https://github.com" target="_blank" class="text-slate-400 hover:text-white transition-colors">
          GitHub
        </a>
        <span class="text-slate-600">•</span>
        <a href="#" class="text-slate-400 hover:text-white transition-colors">
          文档
        </a>
        <span class="text-slate-600">•</span>
        <a href="#" class="text-slate-400 hover:text-white transition-colors">
          API
        </a>
      </div>
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
</style>

