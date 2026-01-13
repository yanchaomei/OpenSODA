<script setup lang="ts">
/**
 * 骨架屏组件
 * 用于页面加载时的占位展示
 */
withDefaults(defineProps<{
  variant?: 'text' | 'title' | 'avatar' | 'card' | 'chart' | 'custom'
  width?: string
  height?: string
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full'
  animate?: boolean
}>(), {
  variant: 'text',
  rounded: 'md',
  animate: true
})
</script>

<template>
  <div 
    :class="[
      'skeleton',
      {
        'animate-none': !animate,
        'rounded-none': rounded === 'none',
        'rounded-sm': rounded === 'sm',
        'rounded-md': rounded === 'md',
        'rounded-lg': rounded === 'lg',
        'rounded-xl': rounded === 'xl',
        'rounded-full': rounded === 'full',
      }
    ]"
    :style="{
      width: width || (variant === 'avatar' ? '48px' : variant === 'title' ? '75%' : '100%'),
      height: height || (
        variant === 'text' ? '16px' :
        variant === 'title' ? '24px' :
        variant === 'avatar' ? '48px' :
        variant === 'card' ? '128px' :
        variant === 'chart' ? '256px' :
        '16px'
      )
    }"
  />
</template>

