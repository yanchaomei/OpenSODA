<script setup lang="ts">
/**
 * TimelineChart - 项目里程碑时间线
 * 展示项目的重要事件和版本发布
 */
import { computed, ref } from 'vue'

interface TimelineEvent {
  date: string
  title: string
  description?: string
  type: 'release' | 'milestone' | 'event' | 'commit'
  version?: string
}

interface Props {
  events: TimelineEvent[]
  maxItems?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxItems: 6
})

const displayedEvents = computed(() => {
  return props.events.slice(0, props.maxItems)
})

function getEventIcon(type: string): string {
  switch (type) {
    case 'release': return '🏷️'
    case 'milestone': return '🎯'
    case 'event': return '📌'
    case 'commit': return '💾'
    default: return '📍'
  }
}

function getEventColor(type: string): string {
  switch (type) {
    case 'release': return 'from-emerald-500 to-green-600'
    case 'milestone': return 'from-accent to-primary-500'
    case 'event': return 'from-cyan-500 to-blue-500'
    case 'commit': return 'from-slate-500 to-slate-600'
    default: return 'from-slate-500 to-slate-600'
  }
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>

<template>
  <div class="relative">
    <!-- 时间线 -->
    <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-accent/50 via-primary-500/30 to-transparent"></div>
    
    <!-- 事件列表 -->
    <div class="space-y-6 pl-10">
      <div 
        v-for="(event, index) in displayedEvents" 
        :key="index"
        class="relative group"
        :style="{ animationDelay: `${index * 100}ms` }"
      >
        <!-- 节点 -->
        <div 
          :class="[
            'absolute -left-10 w-8 h-8 rounded-full flex items-center justify-center',
            'bg-gradient-to-br shadow-lg transition-transform group-hover:scale-110',
            getEventColor(event.type)
          ]"
        >
          <span class="text-sm">{{ getEventIcon(event.type) }}</span>
        </div>
        
        <!-- 内容卡片 -->
        <div class="p-4 bg-surface-light/20 rounded-xl border border-white/5 hover:border-accent/30 transition-all">
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-2">
              <h4 class="text-white font-medium">{{ event.title }}</h4>
              <span 
                v-if="event.version" 
                class="px-2 py-0.5 bg-accent/20 text-accent-light text-xs rounded-full"
              >
                {{ event.version }}
              </span>
            </div>
            <span class="text-xs text-slate-500">{{ formatDate(event.date) }}</span>
          </div>
          <p v-if="event.description" class="text-sm text-slate-400">
            {{ event.description }}
          </p>
        </div>
      </div>
    </div>
    
    <!-- 查看更多 -->
    <div v-if="events.length > maxItems" class="pl-10 mt-4">
      <button class="text-sm text-accent-light hover:text-accent transition-colors">
        查看全部 {{ events.length }} 条记录 →
      </button>
    </div>
  </div>
</template>

<style scoped>
@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.group {
  animation: fadeInLeft 0.5s ease-out forwards;
  opacity: 0;
}
</style>

