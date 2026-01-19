<script setup lang="ts">
/**
 * OnboardingTour - 首次使用引导流程
 * 引导新用户了解核心功能
 */
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 本地存储 key
const STORAGE_KEY = 'opensoda-onboarding-completed'

// 是否显示引导
const showTour = ref(false)
const currentStep = ref(0)

// 引导步骤
const steps = [
  {
    id: 'welcome',
    title: '欢迎使用 OpenSource Copilot!',
    description: '我是一个基于 AI Agent 的开源社区智能运营助手，能够帮助你分析、诊断和优化开源项目。',
    icon: '👋',
    action: null
  },
  {
    id: 'chat',
    title: '智能对话',
    description: '你可以用自然语言与我对话。比如问我："分析一下 apache/dubbo 的健康状况"，我会自动调用工具获取数据并生成报告。',
    icon: '💬',
    action: '试试对话'
  },
  {
    id: 'analysis',
    title: '项目分析',
    description: '输入任意 GitHub 仓库地址，即可获取包含 OpenRank、健康度评分、改进建议的完整分析报告。',
    icon: '📊',
    action: '开始分析'
  },
  {
    id: 'compare',
    title: '项目对比',
    description: '同时对比多个开源项目，通过可视化图表发现它们的差异和各自的优势。',
    icon: '⚖️',
    action: '对比项目'
  },
  {
    id: 'shortcuts',
    title: '快捷操作',
    description: '按 ⌘K / Ctrl+K 可以快速打开命令面板，输入项目名称直接搜索分析。',
    icon: '⌨️',
    action: null
  }
]

const currentStepData = computed(() => steps[currentStep.value])
const isLastStep = computed(() => currentStep.value === steps.length - 1)
const progress = computed(() => ((currentStep.value + 1) / steps.length) * 100)

// 检查是否需要显示引导
onMounted(() => {
  const completed = localStorage.getItem(STORAGE_KEY)
  if (!completed) {
    // 首次访问，延迟显示引导
    setTimeout(() => {
      showTour.value = true
    }, 1000)
  }
})

function nextStep() {
  if (isLastStep.value) {
    completeTour()
  } else {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function skipTour() {
  completeTour()
}

function completeTour() {
  showTour.value = false
  localStorage.setItem(STORAGE_KEY, 'true')
}

function executeAction() {
  const step = currentStepData.value
  completeTour()
  
  switch (step.id) {
    case 'chat':
      router.push('/chat')
      break
    case 'analysis':
      router.push('/analysis/apache/dubbo')
      break
    case 'compare':
      router.push('/compare')
      break
  }
}

// 重新开始引导（可通过设置调用）
function restartTour() {
  localStorage.removeItem(STORAGE_KEY)
  currentStep.value = 0
  showTour.value = true
}

// 暴露方法供外部调用
defineExpose({ restartTour })
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="showTour"
        class="fixed inset-0 z-[100] flex items-center justify-center"
      >
        <!-- 遮罩 -->
        <div class="absolute inset-0 bg-black/70 backdrop-blur-sm"></div>
        
        <!-- 引导卡片 -->
        <div class="relative w-full max-w-lg mx-4 animate-scale-in">
          <!-- 进度条 -->
          <div class="absolute -top-2 left-0 right-0 h-1 bg-surface-light/30 rounded-full overflow-hidden">
            <div 
              class="h-full bg-gradient-to-r from-accent to-primary-500 transition-all duration-500"
              :style="{ width: `${progress}%` }"
            ></div>
          </div>
          
          <!-- 卡片内容 -->
          <div class="glass-dark rounded-2xl p-8 shadow-2xl">
            <!-- 图标 -->
            <div class="flex justify-center mb-6">
              <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent/20 to-primary-500/20 flex items-center justify-center animate-float">
                <span class="text-5xl">{{ currentStepData.icon }}</span>
              </div>
            </div>
            
            <!-- 标题 -->
            <h2 class="text-2xl font-bold text-white text-center mb-3">
              {{ currentStepData.title }}
            </h2>
            
            <!-- 描述 -->
            <p class="text-slate-400 text-center leading-relaxed mb-8">
              {{ currentStepData.description }}
            </p>
            
            <!-- 步骤指示器 -->
            <div class="flex justify-center gap-2 mb-6">
              <button
                v-for="(step, index) in steps"
                :key="step.id"
                @click="currentStep = index"
                :class="[
                  'w-2 h-2 rounded-full transition-all',
                  index === currentStep 
                    ? 'w-6 bg-accent' 
                    : index < currentStep 
                      ? 'bg-accent/50' 
                      : 'bg-surface-light/50'
                ]"
              ></button>
            </div>
            
            <!-- 操作按钮 -->
            <div class="flex items-center justify-between">
              <button
                @click="skipTour"
                class="text-sm text-slate-500 hover:text-white transition-colors"
              >
                跳过引导
              </button>
              
              <div class="flex gap-3">
                <button
                  v-if="currentStep > 0"
                  @click="prevStep"
                  class="px-4 py-2 glass text-slate-300 rounded-xl hover:text-white transition-colors"
                >
                  上一步
                </button>
                
                <button
                  v-if="currentStepData.action"
                  @click="executeAction"
                  class="px-5 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium rounded-xl hover:opacity-90 transition-opacity"
                >
                  {{ currentStepData.action }}
                </button>
                
                <button
                  @click="nextStep"
                  class="px-5 py-2 bg-gradient-to-r from-accent to-primary-500 text-white font-medium rounded-xl hover:opacity-90 transition-opacity"
                >
                  {{ isLastStep ? '开始使用' : '下一步' }}
                </button>
              </div>
            </div>
          </div>
          
          <!-- 步骤数 -->
          <div class="absolute -bottom-8 left-1/2 -translate-x-1/2 text-sm text-slate-500">
            {{ currentStep + 1 }} / {{ steps.length }}
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.animate-scale-in {
  animation: scaleIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

.glass-dark {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>

