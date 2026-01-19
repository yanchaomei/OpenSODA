<script setup lang="ts">
/**
 * AnalysisSkeleton - 分析页面加载骨架屏
 * 专业的加载占位组件，提升用户体验
 */
</script>

<template>
  <div class="space-y-6 animate-pulse">
    <!-- 头部信息骨架 -->
    <div class="glass p-6 rounded-xl">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="h-8 w-64 bg-surface-light/30 rounded-lg mb-3"></div>
          <div class="h-4 w-96 bg-surface-light/20 rounded mb-4"></div>
          <div class="flex gap-4">
            <div class="h-4 w-20 bg-surface-light/20 rounded"></div>
            <div class="h-4 w-20 bg-surface-light/20 rounded"></div>
            <div class="h-4 w-20 bg-surface-light/20 rounded"></div>
          </div>
        </div>
        <div class="text-right">
          <div class="h-16 w-24 bg-surface-light/30 rounded-lg mb-2"></div>
          <div class="h-4 w-16 bg-surface-light/20 rounded ml-auto"></div>
        </div>
      </div>
    </div>
    
    <!-- AI 总结骨架 -->
    <div class="glass p-6 rounded-xl">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-8 h-8 bg-surface-light/30 rounded-lg"></div>
        <div class="h-5 w-32 bg-surface-light/30 rounded"></div>
      </div>
      <div class="space-y-2">
        <div class="h-4 w-full bg-surface-light/20 rounded"></div>
        <div class="h-4 w-5/6 bg-surface-light/20 rounded"></div>
        <div class="h-4 w-4/6 bg-surface-light/20 rounded"></div>
      </div>
    </div>
    
    <!-- 指标卡片骨架 -->
    <div class="grid grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="glass p-5 rounded-xl">
        <div class="flex items-center justify-between mb-3">
          <div class="h-4 w-16 bg-surface-light/20 rounded"></div>
          <div class="w-8 h-8 bg-surface-light/30 rounded-lg"></div>
        </div>
        <div class="h-8 w-20 bg-surface-light/30 rounded-lg mb-2"></div>
        <div class="h-2 w-full bg-surface-light/20 rounded-full"></div>
      </div>
    </div>
    
    <!-- 图表骨架 -->
    <div class="grid grid-cols-2 gap-6">
      <div class="glass p-6 rounded-xl">
        <div class="h-5 w-32 bg-surface-light/30 rounded mb-4"></div>
        <div class="h-64 bg-surface-light/10 rounded-lg flex items-center justify-center">
          <div class="w-32 h-32 rounded-full bg-surface-light/20"></div>
        </div>
      </div>
      <div class="glass p-6 rounded-xl">
        <div class="h-5 w-32 bg-surface-light/30 rounded mb-4"></div>
        <div class="h-64 bg-surface-light/10 rounded-lg flex items-end justify-around p-4">
          <div v-for="i in 6" :key="i" :style="{ height: `${20 + i * 12}%` }" class="w-8 bg-surface-light/20 rounded-t"></div>
        </div>
      </div>
    </div>
    
    <!-- 详细指标骨架 -->
    <div class="glass p-6 rounded-xl">
      <div class="h-5 w-24 bg-surface-light/30 rounded mb-4"></div>
      <div class="grid grid-cols-3 gap-4">
        <div v-for="i in 6" :key="i" class="p-4 bg-surface-light/10 rounded-lg">
          <div class="h-3 w-16 bg-surface-light/20 rounded mb-2"></div>
          <div class="h-7 w-20 bg-surface-light/30 rounded"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.animate-pulse > div {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.03) 25%,
    rgba(255, 255, 255, 0.08) 50%,
    rgba(255, 255, 255, 0.03) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 2s ease-in-out infinite;
}
</style>

