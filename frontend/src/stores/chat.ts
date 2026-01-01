import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatApi } from '@/api/chat'

export interface ToolCall {
  name: string
  displayName?: string
  input?: any
  output?: string
  status: 'pending' | 'running' | 'completed' | 'error'
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metrics?: Record<string, any>
  healthScore?: {
    overall: number
    activity: number
    community: number
    maintenance: number
    growth: number
  }
  charts?: any[]
  recommendations?: any[]
  toolCalls?: ToolCall[]
  agentStatus?: string
  isStreaming?: boolean
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const currentRepo = ref<string | null>(null)
  const streamingContent = ref('')
  
  const hasMessages = computed(() => messages.value.length > 0)
  
  function addMessage(message: Omit<Message, 'id' | 'timestamp'>) {
    const newMessage: Message = {
      ...message,
      id: crypto.randomUUID(),
      timestamp: new Date()
    }
    messages.value.push(newMessage)
    return newMessage
  }
  
  function updateLastMessage(updates: Partial<Message>) {
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage && lastMessage.role === 'assistant') {
      Object.assign(lastMessage, updates)
    }
  }
  
  function addToolCall(toolCall: ToolCall) {
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage && lastMessage.role === 'assistant') {
      if (!lastMessage.toolCalls) {
        lastMessage.toolCalls = []
      }
      lastMessage.toolCalls.push(toolCall)
    }
  }
  
  function updateToolCall(toolName: string, updates: Partial<ToolCall>) {
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage?.toolCalls) {
      const toolCall = lastMessage.toolCalls.find(t => t.name === toolName)
      if (toolCall) {
        Object.assign(toolCall, updates)
      }
    }
  }
  
  async function sendMessage(content: string, repo?: string) {
    if (isLoading.value) return
    
    // 添加用户消息
    addMessage({ role: 'user', content })
    
    // 如果指定了仓库，更新当前仓库
    if (repo) {
      currentRepo.value = repo
    }
    
    // 创建助手消息占位
    addMessage({ 
      role: 'assistant', 
      content: '', 
      isStreaming: true,
      agentStatus: '🤔 正在思考...'
    })
    
    isLoading.value = true
    streamingContent.value = ''
    
    try {
      // 构建历史消息
      const history = messages.value.slice(0, -1).map(m => ({
        role: m.role,
        content: m.content
      }))
      
      // 使用流式 API
      await chatApi.streamChat(
        content,
        currentRepo.value || undefined,
        history,
        {
          onText: (text) => {
            streamingContent.value += text
            updateLastMessage({ 
              content: streamingContent.value, 
              isStreaming: true,
              agentStatus: undefined
            })
          },
          onToolStart: (tool, displayName, input) => {
            addToolCall({
              name: tool,
              displayName: displayName,
              input: input,
              status: 'running'
            })
            updateLastMessage({ agentStatus: `🔧 ${displayName}` })
          },
          onToolEnd: (tool, output) => {
            updateToolCall(tool, {
              output: output,
              status: 'completed'
            })
          },
          onStatus: (step, message) => {
            updateLastMessage({ agentStatus: message })
          },
          onMetrics: (metrics) => {
            updateLastMessage({ metrics })
          },
          onHealthScore: (healthScore) => {
            updateLastMessage({ healthScore })
          },
          onCharts: (charts) => {
            updateLastMessage({ charts })
          },
          onRecommendations: (recommendations) => {
            updateLastMessage({ recommendations })
          },
          onComplete: () => {
            updateLastMessage({ 
              content: streamingContent.value, 
              isStreaming: false,
              agentStatus: undefined
            })
          },
          onError: (error) => {
            console.error('Stream error:', error)
            updateLastMessage({ 
              content: streamingContent.value || `抱歉，发生错误：${error}`, 
              isStreaming: false,
              agentStatus: undefined
            })
          }
        }
      )
    } catch (error: any) {
      console.error('Chat error:', error)
      updateLastMessage({ 
        content: `抱歉，发生错误：${error.message}`, 
        isStreaming: false,
        agentStatus: undefined
      })
    } finally {
      isLoading.value = false
    }
  }
  
  function clearMessages() {
    messages.value = []
    currentRepo.value = null
    streamingContent.value = ''
  }
  
  function setRepo(repo: string) {
    currentRepo.value = repo
  }
  
  return {
    messages,
    isLoading,
    currentRepo,
    hasMessages,
    addMessage,
    sendMessage,
    clearMessages,
    setRepo
  }
})
