<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  value: number
  max: number
  icon: string
}>()

const percentage = computed(() => Math.min(100, (props.value / props.max) * 100))

const colorClass = computed(() => {
  if (props.value >= 80) return 'from-emerald-500 to-green-400'
  if (props.value >= 60) return 'from-green-500 to-lime-400'
  if (props.value >= 40) return 'from-yellow-500 to-amber-400'
  if (props.value >= 20) return 'from-orange-500 to-amber-400'
  return 'from-red-500 to-orange-400'
})

const textColorClass = computed(() => {
  if (props.value >= 80) return 'text-emerald-400'
  if (props.value >= 60) return 'text-green-400'
  if (props.value >= 40) return 'text-yellow-400'
  if (props.value >= 20) return 'text-orange-400'
  return 'text-red-400'
})
</script>

<template>
  <div class="glass p-5">
    <div class="flex items-center justify-between mb-3">
      <span class="text-2xl">{{ icon }}</span>
      <span :class="['text-2xl font-bold', textColorClass]">{{ value.toFixed(1) }}</span>
    </div>
    
    <div class="mb-2">
      <div class="h-2 bg-surface-dark rounded-full overflow-hidden">
        <div
          :class="['h-full rounded-full bg-gradient-to-r transition-all duration-500', colorClass]"
          :style="{ width: `${percentage}%` }"
        ></div>
      </div>
    </div>
    
    <div class="text-sm text-slate-400">{{ title }}</div>
  </div>
</template>

