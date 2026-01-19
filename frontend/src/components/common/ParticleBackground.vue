<script setup lang="ts">
/**
 * ParticleBackground - 粒子动画背景
 * 科技感十足的动态背景效果
 */
import { ref, onMounted, onUnmounted } from 'vue'

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
  color: string
  alpha: number
}

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationId: number | null = null
let particles: Particle[] = []
let mouseX = 0
let mouseY = 0
let isMouseOver = false

const PARTICLE_COUNT = 80
const CONNECTION_DISTANCE = 150
const MOUSE_RADIUS = 200

const colors = [
  'rgba(139, 92, 246, 1)',   // purple
  'rgba(6, 182, 212, 1)',    // cyan
  'rgba(16, 185, 129, 1)',   // emerald
  'rgba(59, 130, 246, 1)',   // blue
]

function createParticle(width: number, height: number): Particle {
  return {
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * 0.5,
    vy: (Math.random() - 0.5) * 0.5,
    radius: Math.random() * 2 + 1,
    color: colors[Math.floor(Math.random() * colors.length)],
    alpha: Math.random() * 0.5 + 0.2
  }
}

function init() {
  const canvas = canvasRef.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // 设置画布大小
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  resize()
  window.addEventListener('resize', resize)
  
  // 创建粒子
  particles = []
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push(createParticle(canvas.width, canvas.height))
  }
  
  // 鼠标事件
  const handleMouseMove = (e: MouseEvent) => {
    mouseX = e.clientX
    mouseY = e.clientY
    isMouseOver = true
  }
  
  const handleMouseLeave = () => {
    isMouseOver = false
  }
  
  canvas.addEventListener('mousemove', handleMouseMove)
  canvas.addEventListener('mouseleave', handleMouseLeave)
  
  // 动画循环
  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // 更新和绘制粒子
    particles.forEach((particle, i) => {
      // 鼠标交互
      if (isMouseOver) {
        const dx = mouseX - particle.x
        const dy = mouseY - particle.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        
        if (dist < MOUSE_RADIUS) {
          const force = (MOUSE_RADIUS - dist) / MOUSE_RADIUS
          particle.vx -= (dx / dist) * force * 0.02
          particle.vy -= (dy / dist) * force * 0.02
        }
      }
      
      // 更新位置
      particle.x += particle.vx
      particle.y += particle.vy
      
      // 边界反弹
      if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1
      if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1
      
      // 绘制粒子
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2)
      ctx.fillStyle = particle.color.replace('1)', `${particle.alpha})`)
      ctx.fill()
      
      // 绘制连线
      particles.slice(i + 1).forEach(other => {
        const dx = particle.x - other.x
        const dy = particle.y - other.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        
        if (dist < CONNECTION_DISTANCE) {
          const alpha = (1 - dist / CONNECTION_DISTANCE) * 0.2
          ctx.beginPath()
          ctx.moveTo(particle.x, particle.y)
          ctx.lineTo(other.x, other.y)
          ctx.strokeStyle = `rgba(139, 92, 246, ${alpha})`
          ctx.lineWidth = 0.5
          ctx.stroke()
        }
      })
      
      // 鼠标连线
      if (isMouseOver) {
        const dx = mouseX - particle.x
        const dy = mouseY - particle.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        
        if (dist < MOUSE_RADIUS) {
          const alpha = (1 - dist / MOUSE_RADIUS) * 0.5
          ctx.beginPath()
          ctx.moveTo(particle.x, particle.y)
          ctx.lineTo(mouseX, mouseY)
          ctx.strokeStyle = `rgba(6, 182, 212, ${alpha})`
          ctx.lineWidth = 1
          ctx.stroke()
        }
      }
    })
    
    animationId = requestAnimationFrame(animate)
  }
  
  animate()
}

onMounted(() => {
  init()
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<template>
  <canvas
    ref="canvasRef"
    class="fixed inset-0 pointer-events-auto z-0"
    style="opacity: 0.6"
  ></canvas>
</template>

