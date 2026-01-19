<script setup lang="ts">
/**
 * AISummaryCard - AI 一句话总结卡片
 * 展示 AI 生成的项目概要和关键洞察
 */
import { computed, ref } from 'vue'

interface Props {
  repo: string
  healthScore: number
  summary?: string
  highlights?: string[]
  concerns?: string[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const expanded = ref(false)

// 根据健康度生成 AI 风格的一句话总结
const aiSummary = computed(() => {
  if (props.summary) return props.summary
  
  const score = props.healthScore
  const repoName = props.repo.split('/')[1]
  
  if (score >= 80) {
    return `${repoName} 是一个非常健康的开源项目，社区活跃、维护良好，值得关注和参与。`
  } else if (score >= 60) {
    return `${repoName} 整体状况良好，有一定的改进空间，建议关注社区增长和响应速度。`
  } else if (score >= 40) {
    return `${repoName} 存在一些需要关注的问题，建议重点优化社区运营和代码维护。`
  } else {
    return `${repoName} 当前健康度较低，建议尽快采取措施改善项目活跃度和社区参与。`
  }
})

// 健康度表情
const healthEmoji = computed(() => {
  const score = props.healthScore
  if (score >= 80) return '🌟'
  if (score >= 60) return '👍'
  if (score >= 40) return '🤔'
  return '⚠️'
})

// 健康度标签
const healthLabel = computed(() => {
  const score = props.healthScore
  if (score >= 80) return '优秀'
  if (score >= 60) return '良好'
  if (score >= 40) return '一般'
  return '需关注'
})

// 健康度颜色
const healthColor = computed(() => {
  const score = props.healthScore
  if (score >= 80) return 'from-emerald-500 to-green-600'
  if (score >= 60) return 'from-green-500 to-teal-600'
  if (score >= 40) return 'from-yellow-500 to-amber-600'
  return 'from-red-500 to-rose-600'
})
</script>

<template>
  <div class="glass p-6 rounded-2xl relative overflow-hidden">
    <!-- 装饰背景 -->
    <div class="absolute -top-20 -right-20 w-40 h-40 bg-gradient-to-br from-accent/10 to-transparent rounded-full blur-2xl"></div>
    
    <div class="relative z-10">
      <!-- 头部 -->
      <div class="flex items-start justify-between mb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-accent/20 to-primary-500/20 flex items-center justify-center">
            <span class="text-xl">🤖</span>
          </div>
          <div>
            <h3 class="text-white font-semibold flex items-center gap-2">
              AI 分析摘要
              <span class="text-xs px-2 py-0.5 bg-accent/20 text-accent-light rounded-full">智能生成</span>
            </h3>
            <p class="text-xs text-slate-500">基于 OpenDigger 数据 + GPT 分析</p>
          </div>
        </div>
        
        <!-- 健康度徽章 -->
        <div :class="[
          'px-4 py-2 rounded-xl bg-gradient-to-r text-white font-semibold flex items-center gap-2',
          healthColor
        ]">
          <span>{{ healthEmoji }}</span>
          <span>{{ healthLabel }}</span>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="space-y-3">
        <div class="h-4 w-full bg-surface-light/30 rounded animate-pulse"></div>
        <div class="h-4 w-5/6 bg-surface-light/30 rounded animate-pulse"></div>
        <div class="h-4 w-4/6 bg-surface-light/30 rounded animate-pulse"></div>
      </div>
      
      <!-- AI 总结内容 -->
      <template v-else>
        <p class="text-slate-300 text-lg leading-relaxed mb-4">
          {{ aiSummary }}
        </p>
        
        <!-- 关键洞察 -->
        <div v-if="expanded || (highlights?.length || concerns?.length)" 
             :class="{ 'max-h-0 overflow-hidden': !expanded && (highlights?.length || concerns?.length) }"
        >
          <div class="grid grid-cols-2 gap-4 pt-4 border-t border-white/10">
            <!-- 亮点 -->
            <div v-if="highlights?.length">
              <h4 class="text-sm text-slate-400 mb-2 flex items-center gap-1">
                <span>✅</span> 亮点
              </h4>
              <ul class="space-y-1">
                <li v-for="h in highlights.slice(0, 3)" :key="h" class="text-sm text-green-400 flex items-start gap-2">
                  <span class="mt-1">•</span>
                  <span>{{ h }}</span>
                </li>
              </ul>
            </div>
            
            <!-- 关注点 -->
            <div v-if="concerns?.length">
              <h4 class="text-sm text-slate-400 mb-2 flex items-center gap-1">
                <span>⚠️</span> 待改进
              </h4>
              <ul class="space-y-1">
                <li v-for="c in concerns.slice(0, 3)" :key="c" class="text-sm text-yellow-400 flex items-start gap-2">
                  <span class="mt-1">•</span>
                  <span>{{ c }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- 展开/收起按钮 -->
        <button
          v-if="highlights?.length || concerns?.length"
          @click="expanded = !expanded"
          class="mt-4 text-sm text-accent-light hover:text-accent transition-colors flex items-center gap-1"
        >
          {{ expanded ? '收起详情' : '查看详情' }}
          <span :class="{ 'rotate-180': expanded }" class="transition-transform">↓</span>
        </button>
      </template>
    </div>
  </div>
</template>

