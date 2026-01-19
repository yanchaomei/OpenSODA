<script setup lang="ts">
import { RouterView } from 'vue-router'
import Sidebar from './components/layout/Sidebar.vue'
import Header from './components/layout/Header.vue'
import KeyboardShortcuts from './components/common/KeyboardShortcuts.vue'
import OnboardingTour from './components/common/OnboardingTour.vue'
import ParticleBackground from './components/common/ParticleBackground.vue'
</script>

<template>
  <div class="relative flex h-screen overflow-hidden">
    <!-- 粒子动画背景 -->
    <ParticleBackground />
    
    <!-- 侧边栏 -->
    <Sidebar class="relative z-10" />
    
    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col overflow-hidden relative z-10">
      <!-- 顶部导航 -->
      <Header />
      
      <!-- 页面内容 -->
      <main class="flex-1 overflow-auto p-6">
        <RouterView v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </RouterView>
      </main>
    </div>
    
    <!-- 全局键盘快捷键 -->
    <KeyboardShortcuts />
    
    <!-- 首次使用引导 -->
    <OnboardingTour />
  </div>
</template>

<style scoped>
/* 页面切换动画 */
.page-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

