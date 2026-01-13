<script setup lang="ts">
import { ref, computed, watch } from 'vue'

/**
 * Agent 思考过程可视化组件
 * 展示 ReAct Agent 的思考链和工具调用流程
 */
const props = defineProps<{
  status?: string
  toolCalls?: Array<{
    name: string
    displayName?: string
    input?: any
    output?: string
    status: 'pending' | 'running' | 'completed' | 'error'
  }>
  isActive: boolean
}>()

// 当前阶段
const currentPhase = computed(() => {
  if (!props.isActive) return 'idle'
  if (props.status?.includes('思考')) return 'thinking'
  if (props.status?.includes('推理')) return 'reasoning'
  if (props.toolCalls?.some(t => t.status === 'running')) return 'executing'
  if (props.toolCalls?.every(t => t.status === 'completed')) return 'responding'
  return 'thinking'
})

// 阶段描述
const phaseDescriptions = {
  idle: '等待输入',
  thinking: '理解用户意图',
  reasoning: '决定调用工具',
  executing: '执行工具调用',
  responding: '生成回复'
}

// 工具图标映射
const toolIcons: Record<string, string> = {
  'analyze_repo_health': '📊',
  'diagnose_repo_issues': '🔍',
  'get_improvement_suggestions': '💡',
  'get_repo_openrank': '📈',
  'get_repo_health_metrics': '📊',
  'get_repo_contributors_info': '👥',
  'get_repo_activity_trend': '📉',
  'get_github_repo_info': '🔗',
  'get_github_contributors': '👨‍💻',
  'find_good_first_issues': '🎯',
  'search_opensource_knowledge': '📚',
}

function getToolIcon(name: string): string {
  return toolIcons[name] || '🔧'
}

// 展开/收起工具详情
const expandedTools = ref<Set<number>>(new Set())

function toggleToolExpand(index: number) {
  if (expandedTools.value.has(index)) {
    expandedTools.value.delete(index)
  } else {
    expandedTools.value.add(index)
  }
}
</script>

<template>
  <div v-if="isActive" class="agent-thinking-wrapper">
    <!-- 主容器 -->
    <div class="glass-dark rounded-2xl overflow-hidden border border-accent/20">
      <!-- 顶部状态栏 -->
      <div class="px-4 py-3 bg-gradient-to-r from-accent/20 to-primary-500/20 border-b border-white/5">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <!-- 动态图标 -->
            <div class="relative">
              <div 
                :class="[
                  'w-8 h-8 rounded-lg flex items-center justify-center',
                  currentPhase === 'thinking' ? 'bg-yellow-500/20' :
                  currentPhase === 'reasoning' ? 'bg-blue-500/20' :
                  currentPhase === 'executing' ? 'bg-purple-500/20' :
                  currentPhase === 'responding' ? 'bg-green-500/20' :
                  'bg-slate-500/20'
                ]"
              >
                <span class="text-lg">
                  {{ currentPhase === 'thinking' ? '🤔' :
                     currentPhase === 'reasoning' ? '🧠' :
                     currentPhase === 'executing' ? '⚙️' :
                     currentPhase === 'responding' ? '💬' : '⏳' }}
                </span>
              </div>
              <!-- 脉冲动画 -->
              <div 
                class="absolute inset-0 rounded-lg animate-ping opacity-30"
                :class="[
                  currentPhase === 'executing' ? 'bg-purple-500' :
                  currentPhase === 'thinking' ? 'bg-yellow-500' :
                  'bg-accent'
                ]"
              ></div>
            </div>
            
            <div>
              <div class="text-sm font-medium text-white">
                ReAct Agent
              </div>
              <div class="text-xs text-slate-400">
                {{ phaseDescriptions[currentPhase] || status }}
              </div>
            </div>
          </div>
          
          <!-- 状态机指示器 -->
          <div class="flex items-center gap-1.5">
            <div 
              v-for="phase in ['thinking', 'reasoning', 'executing', 'responding']" 
              :key="phase"
              :class="[
                'w-2 h-2 rounded-full transition-all duration-300',
                currentPhase === phase ? 'bg-accent scale-125' :
                ['thinking', 'reasoning', 'executing', 'responding'].indexOf(phase) < 
                ['thinking', 'reasoning', 'executing', 'responding'].indexOf(currentPhase) 
                  ? 'bg-green-500' : 'bg-slate-600'
              ]"
              :title="phaseDescriptions[phase as keyof typeof phaseDescriptions]"
            ></div>
          </div>
        </div>
      </div>
      
      <!-- 状态机流程图 -->
      <div class="px-4 py-3 border-b border-white/5">
        <div class="flex items-center justify-between text-xs">
          <!-- START -->
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center">
              <div class="w-2 h-2 rounded-full bg-green-500"></div>
            </div>
            <span class="text-slate-500">START</span>
          </div>
          
          <!-- 箭头 -->
          <div class="flex-1 flex items-center px-2">
            <div class="flex-1 h-0.5 bg-gradient-to-r from-green-500/50 to-accent/50"></div>
            <svg class="w-3 h-3 text-accent/50 -ml-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </div>
          
          <!-- Agent Node -->
          <div 
            :class="[
              'px-3 py-1.5 rounded-lg font-medium transition-all',
              currentPhase === 'thinking' || currentPhase === 'reasoning' 
                ? 'bg-accent/30 text-accent-light ring-2 ring-accent/50' 
                : 'bg-surface-light/50 text-slate-400'
            ]"
          >
            🤖 Agent
          </div>
          
          <!-- 条件分支 -->
          <div class="flex-1 flex items-center px-2">
            <svg class="w-3 h-3 text-accent/50 mr-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
            <div class="flex-1 h-0.5 bg-gradient-to-r from-accent/50 to-purple-500/50"></div>
          </div>
          
          <!-- Tools Node -->
          <div 
            :class="[
              'px-3 py-1.5 rounded-lg font-medium transition-all',
              currentPhase === 'executing' 
                ? 'bg-purple-500/30 text-purple-300 ring-2 ring-purple-500/50' 
                : 'bg-surface-light/50 text-slate-400'
            ]"
          >
            🔧 Tools
          </div>
          
          <!-- 箭头 -->
          <div class="flex-1 flex items-center px-2">
            <svg class="w-3 h-3 text-purple-500/50 mr-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
            <div class="flex-1 h-0.5 bg-gradient-to-r from-purple-500/50 to-red-500/50"></div>
          </div>
          
          <!-- END -->
          <div class="flex items-center gap-2">
            <span class="text-slate-500">END</span>
            <div 
              :class="[
                'w-6 h-6 rounded-full flex items-center justify-center transition-all',
                currentPhase === 'responding' ? 'bg-red-500/30' : 'bg-red-500/10'
              ]"
            >
              <div 
                :class="[
                  'w-2 h-2 rounded-full transition-all',
                  currentPhase === 'responding' ? 'bg-red-500' : 'bg-red-500/50'
                ]"
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 工具调用详情 -->
      <div v-if="toolCalls?.length" class="p-4 space-y-2">
        <div class="text-xs text-slate-500 mb-3 flex items-center gap-2">
          <span>📝</span>
          <span>工具调用记录 ({{ toolCalls.filter(t => t.status === 'completed').length }}/{{ toolCalls.length }})</span>
        </div>
        
        <TransitionGroup name="tool-list">
          <div 
            v-for="(tool, index) in toolCalls" 
            :key="`${tool.name}-${index}`"
            class="tool-card-enhanced"
          >
            <!-- 工具头部 -->
            <div 
              class="flex items-center gap-3 cursor-pointer"
              @click="toggleToolExpand(index)"
            >
              <!-- 状态指示器 -->
              <div 
                :class="[
                  'w-10 h-10 rounded-xl flex items-center justify-center text-lg transition-all',
                  tool.status === 'completed' ? 'bg-green-500/20 shadow-lg shadow-green-500/20' :
                  tool.status === 'running' ? 'bg-accent/20 shadow-lg shadow-accent/20' :
                  tool.status === 'error' ? 'bg-red-500/20 shadow-lg shadow-red-500/20' :
                  'bg-slate-700/50'
                ]"
              >
                <span v-if="tool.status === 'running'" class="animate-spin">⚙️</span>
                <span v-else-if="tool.status === 'completed'">{{ getToolIcon(tool.name) }}</span>
                <span v-else-if="tool.status === 'error'">❌</span>
                <span v-else>⏳</span>
              </div>
              
              <!-- 工具信息 -->
              <div class="flex-1 min-w-0">
                <div class="text-sm text-white font-medium truncate">
                  {{ tool.displayName || tool.name }}
                </div>
                <div class="text-xs text-slate-500 mt-0.5">
                  {{ tool.status === 'completed' ? '执行完成' : 
                     tool.status === 'running' ? '执行中...' :
                     tool.status === 'error' ? '执行失败' : '等待执行' }}
                </div>
              </div>
              
              <!-- 展开图标 -->
              <svg 
                :class="[
                  'w-5 h-5 text-slate-500 transition-transform',
                  expandedTools.has(index) ? 'rotate-180' : ''
                ]" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
            
            <!-- 展开详情 -->
            <Transition name="expand">
              <div v-if="expandedTools.has(index)" class="mt-3 pt-3 border-t border-white/5">
                <!-- 输入参数 -->
                <div v-if="tool.input" class="mb-2">
                  <div class="text-xs text-slate-500 mb-1">📥 输入参数:</div>
                  <code class="block text-xs text-slate-300 bg-surface-dark px-3 py-2 rounded-lg overflow-x-auto">
                    {{ typeof tool.input === 'object' ? JSON.stringify(tool.input, null, 2) : tool.input }}
                  </code>
                </div>
                
                <!-- 输出结果 -->
                <div v-if="tool.output">
                  <div class="text-xs text-slate-500 mb-1">📤 返回结果:</div>
                  <div class="text-xs text-slate-300 bg-surface-dark px-3 py-2 rounded-lg max-h-40 overflow-y-auto">
                    {{ tool.output.slice(0, 500) }}{{ tool.output.length > 500 ? '...' : '' }}
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </TransitionGroup>
      </div>
      
      <!-- 无工具调用时的思考动画 -->
      <div v-else class="p-4">
        <div class="flex items-center gap-4">
          <!-- 大脑波形动画 -->
          <div class="brain-waves">
            <div class="brain-wave" style="--delay: 0s"></div>
            <div class="brain-wave" style="--delay: 0.15s"></div>
            <div class="brain-wave" style="--delay: 0.3s"></div>
            <div class="brain-wave" style="--delay: 0.45s"></div>
            <div class="brain-wave" style="--delay: 0.6s"></div>
          </div>
          
          <div class="flex-1">
            <div class="text-sm text-white mb-1">{{ status || '正在分析...' }}</div>
            <div class="text-xs text-slate-500">
              Agent 正在理解您的问题并决定下一步行动
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 工具卡片增强 */
.tool-card-enhanced {
  @apply p-3 rounded-xl bg-surface-light/20 border border-white/5;
  @apply transition-all duration-300;
}

.tool-card-enhanced:hover {
  @apply bg-surface-light/30 border-accent/20;
}

/* 工具列表动画 */
.tool-list-enter-active {
  animation: tool-slide-in 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.tool-list-leave-active {
  animation: tool-slide-out 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes tool-slide-in {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes tool-slide-out {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
  }
}

/* 展开/收起动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 300px;
}

/* 大脑波形动画 */
.brain-waves {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 32px;
  padding: 0 8px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 8px;
}

.brain-wave {
  width: 4px;
  height: 8px;
  background: linear-gradient(to top, #8b5cf6, #06b6d4);
  border-radius: 2px;
  animation: wave-pulse 1.2s ease-in-out infinite;
  animation-delay: var(--delay, 0s);
}

@keyframes wave-pulse {
  0%, 100% {
    height: 8px;
    opacity: 0.5;
  }
  50% {
    height: 24px;
    opacity: 1;
  }
}
</style>
