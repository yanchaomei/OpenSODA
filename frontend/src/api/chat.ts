import api from './index'

interface ChatMessage {
  role: string
  content: string
}

interface StreamCallbacks {
  onText: (text: string) => void
  onToolStart?: (tool: string, displayName: string, input: any) => void
  onToolEnd?: (tool: string, output: string) => void
  onMetrics?: (metrics: any) => void
  onHealthScore?: (healthScore: any) => void
  onCharts?: (charts: any[]) => void
  onRecommendations?: (recommendations: any[]) => void
  onStatus?: (step: string, message: string) => void
  onComplete: () => void
  onError: (error: string) => void
}

export const chatApi = {
  /**
   * 普通聊天 API
   */
  async chat(message: string, repo?: string, history?: ChatMessage[]) {
    return api.post('/chat/', {
      message,
      repo,
      history: history || []
    })
  },

  /**
   * 流式聊天 API - 支持 Agent 工具调用展示
   */
  async streamChat(
    message: string,
    repo: string | undefined,
    history: ChatMessage[],
    callbacks: StreamCallbacks
  ) {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message,
        repo,
        history
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('No reader available')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          callbacks.onComplete()
          break
        }

        buffer += decoder.decode(value, { stream: true })
        
        // 解析 SSE 数据
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            
            if (data === '[DONE]') {
              callbacks.onComplete()
              return
            }

            try {
              const parsed = JSON.parse(data)
              
              switch (parsed.type) {
                case 'text':
                  callbacks.onText(parsed.content)
                  break
                  
                case 'tool_start':
                  callbacks.onToolStart?.(
                    parsed.tool,
                    parsed.tool_display || parsed.tool,
                    parsed.input
                  )
                  callbacks.onStatus?.('tool', parsed.message)
                  break
                  
                case 'tool_end':
                  callbacks.onToolEnd?.(parsed.tool, parsed.output)
                  break
                  
                case 'metrics':
                  callbacks.onMetrics?.(parsed.data)
                  break
                  
                case 'health_score':
                  callbacks.onHealthScore?.(parsed.data)
                  break
                  
                case 'charts':
                  callbacks.onCharts?.(parsed.data)
                  break
                  
                case 'recommendations':
                  callbacks.onRecommendations?.(parsed.data)
                  break
                  
                case 'diagnosis':
                  // 诊断数据
                  break
                  
                case 'status':
                  callbacks.onStatus?.(parsed.step, parsed.message)
                  break
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', data)
            }
          }
        }
      }
    } catch (error: any) {
      callbacks.onError(error.message)
    } finally {
      reader.releaseLock()
    }
  },

  /**
   * WebSocket 聊天
   */
  createWebSocket(): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/chat/ws`)
    return ws
  }
}
