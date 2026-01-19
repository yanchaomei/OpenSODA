<script setup lang="ts">
/**
 * ShareCard - 分析报告分享功能
 * 支持复制链接、生成图片、导出报告
 */
import { ref, computed } from 'vue'

interface Props {
  repo: string
  healthScore: number
  metrics?: Record<string, any>
}

const props = defineProps<Props>()

const showShareMenu = ref(false)
const copied = ref(false)
const generating = ref(false)

// 生成分享链接
const shareUrl = computed(() => {
  return `${window.location.origin}/analysis/${props.repo}`
})

// 生成分享文本
const shareText = computed(() => {
  return `🔍 我刚用 OpenSource Copilot 分析了 ${props.repo}！\n\n` +
    `📊 健康度评分：${props.healthScore}/100\n` +
    `📈 OpenRank：${props.metrics?.openrank?.toFixed(1) || 'N/A'}\n\n` +
    `查看详细报告 👉 ${shareUrl.value}`
})

// 复制链接
async function copyLink() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (e) {
    console.error('Failed to copy:', e)
  }
}

// 复制分享文本
async function copyShareText() {
  try {
    await navigator.clipboard.writeText(shareText.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (e) {
    console.error('Failed to copy:', e)
  }
}

// 分享到 Twitter
function shareToTwitter() {
  const text = encodeURIComponent(`🔍 ${props.repo} 的开源健康度评分：${props.healthScore}/100\n\n使用 OpenSource Copilot 智能分析 👉`)
  const url = encodeURIComponent(shareUrl.value)
  window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank')
}

// 生成分享图片（简化版：截图提示）
async function generateImage() {
  generating.value = true
  
  // 模拟生成过程
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  // 提示用户使用截图
  alert('💡 小提示：使用系统截图功能 (Cmd+Shift+4 / Win+Shift+S) 可以快速生成分享图片！')
  
  generating.value = false
}

// 下载 JSON 数据
function downloadJson() {
  const data = {
    repo: props.repo,
    healthScore: props.healthScore,
    metrics: props.metrics,
    analyzedAt: new Date().toISOString(),
    generatedBy: 'OpenSource Copilot'
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${props.repo.replace('/', '_')}_analysis.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="relative">
    <!-- 分享按钮 -->
    <button
      @click="showShareMenu = !showShareMenu"
      class="px-4 py-2 glass text-slate-300 rounded-xl hover:text-white hover:border-accent/30 transition-all flex items-center gap-2"
    >
      <span>🔗</span>
      <span>分享</span>
    </button>
    
    <!-- 分享菜单 -->
    <Transition name="menu">
      <div
        v-if="showShareMenu"
        class="absolute right-0 top-full mt-2 w-64 glass-dark rounded-xl shadow-2xl overflow-hidden z-50"
      >
        <!-- 复制链接 -->
        <button
          @click="copyLink"
          class="w-full px-4 py-3 flex items-center gap-3 hover:bg-surface-light/30 transition-colors text-left"
        >
          <span class="text-lg">{{ copied ? '✅' : '📋' }}</span>
          <div>
            <div class="text-white text-sm">{{ copied ? '已复制!' : '复制链接' }}</div>
            <div class="text-xs text-slate-500 truncate">{{ shareUrl }}</div>
          </div>
        </button>
        
        <!-- 复制文本 -->
        <button
          @click="copyShareText"
          class="w-full px-4 py-3 flex items-center gap-3 hover:bg-surface-light/30 transition-colors text-left"
        >
          <span class="text-lg">📝</span>
          <div>
            <div class="text-white text-sm">复制分享文本</div>
            <div class="text-xs text-slate-500">包含评分和链接</div>
          </div>
        </button>
        
        <div class="border-t border-white/10"></div>
        
        <!-- 分享到 Twitter -->
        <button
          @click="shareToTwitter"
          class="w-full px-4 py-3 flex items-center gap-3 hover:bg-surface-light/30 transition-colors text-left"
        >
          <span class="text-lg">🐦</span>
          <div>
            <div class="text-white text-sm">分享到 Twitter</div>
            <div class="text-xs text-slate-500">发布推文</div>
          </div>
        </button>
        
        <!-- 生成图片 -->
        <button
          @click="generateImage"
          :disabled="generating"
          class="w-full px-4 py-3 flex items-center gap-3 hover:bg-surface-light/30 transition-colors text-left disabled:opacity-50"
        >
          <span class="text-lg">{{ generating ? '⏳' : '🖼️' }}</span>
          <div>
            <div class="text-white text-sm">{{ generating ? '生成中...' : '生成图片' }}</div>
            <div class="text-xs text-slate-500">适合社交媒体</div>
          </div>
        </button>
        
        <div class="border-t border-white/10"></div>
        
        <!-- 下载数据 -->
        <button
          @click="downloadJson"
          class="w-full px-4 py-3 flex items-center gap-3 hover:bg-surface-light/30 transition-colors text-left"
        >
          <span class="text-lg">📦</span>
          <div>
            <div class="text-white text-sm">下载 JSON</div>
            <div class="text-xs text-slate-500">原始数据导出</div>
          </div>
        </button>
      </div>
    </Transition>
    
    <!-- 点击外部关闭 -->
    <div
      v-if="showShareMenu"
      class="fixed inset-0 z-40"
      @click="showShareMenu = false"
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

