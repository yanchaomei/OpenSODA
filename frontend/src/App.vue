<script setup lang="ts">
import { RouterView } from 'vue-router'
import Sidebar from './components/layout/Sidebar.vue'
import Header from './components/layout/Header.vue'
</script>

<template>
  <div class="flex h-screen overflow-hidden">
    <!-- 侧边栏 -->
    <Sidebar />
    
    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- 顶部导航 -->
      <Header />
      
      <!-- 页面内容 -->
      <main class="flex-1 overflow-auto p-6">
        <RouterView v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

