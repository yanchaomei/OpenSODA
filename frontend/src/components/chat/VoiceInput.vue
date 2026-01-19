<script setup lang="ts">
/**
 * VoiceInput - 语音输入组件
 * 使用 Web Speech API 实现语音转文字
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'

const emit = defineEmits<{
  (e: 'transcript', text: string): void
  (e: 'error', message: string): void
}>()

const isListening = ref(false)
const isSupported = ref(false)
const transcript = ref('')
const volume = ref(0)

let recognition: any = null
let audioContext: AudioContext | null = null
let analyser: AnalyserNode | null = null
let animationId: number | null = null

// 检查浏览器支持
onMounted(() => {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (SpeechRecognition) {
    isSupported.value = true
    recognition = new SpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = true
    recognition.lang = 'zh-CN'
    
    recognition.onstart = () => {
      isListening.value = true
      startVolumeAnalysis()
    }
    
    recognition.onend = () => {
      isListening.value = false
      stopVolumeAnalysis()
      if (transcript.value) {
        emit('transcript', transcript.value)
        transcript.value = ''
      }
    }
    
    recognition.onresult = (event: any) => {
      let finalTranscript = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript
        }
      }
      if (finalTranscript) {
        transcript.value = finalTranscript
      }
    }
    
    recognition.onerror = (event: any) => {
      isListening.value = false
      stopVolumeAnalysis()
      if (event.error === 'not-allowed') {
        emit('error', '请允许麦克风访问权限')
      } else if (event.error === 'no-speech') {
        emit('error', '未检测到语音输入')
      } else {
        emit('error', `语音识别错误: ${event.error}`)
      }
    }
  }
})

onUnmounted(() => {
  stopListening()
  stopVolumeAnalysis()
})

// 音量分析
async function startVolumeAnalysis() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    audioContext = new AudioContext()
    analyser = audioContext.createAnalyser()
    const source = audioContext.createMediaStreamSource(stream)
    source.connect(analyser)
    analyser.fftSize = 256
    
    const dataArray = new Uint8Array(analyser.frequencyBinCount)
    
    function updateVolume() {
      if (!analyser) return
      analyser.getByteFrequencyData(dataArray)
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length
      volume.value = Math.min(average / 128, 1)
      animationId = requestAnimationFrame(updateVolume)
    }
    
    updateVolume()
  } catch (e) {
    console.error('Failed to start volume analysis:', e)
  }
}

function stopVolumeAnalysis() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  if (audioContext) {
    audioContext.close()
    audioContext = null
  }
  volume.value = 0
}

function toggleListening() {
  if (!isSupported.value) {
    emit('error', '您的浏览器不支持语音输入')
    return
  }
  
  if (isListening.value) {
    stopListening()
  } else {
    startListening()
  }
}

function startListening() {
  if (recognition) {
    try {
      recognition.start()
    } catch (e) {
      console.error('Failed to start recognition:', e)
    }
  }
}

function stopListening() {
  if (recognition) {
    recognition.stop()
  }
}

// 波形条高度
const waveHeights = computed(() => {
  if (!isListening.value) return [20, 30, 25, 35, 20]
  const base = 20
  const multiplier = volume.value * 60
  return [
    base + Math.sin(Date.now() / 100) * multiplier,
    base + Math.sin(Date.now() / 100 + 1) * multiplier,
    base + Math.sin(Date.now() / 100 + 2) * multiplier,
    base + Math.sin(Date.now() / 100 + 3) * multiplier,
    base + Math.sin(Date.now() / 100 + 4) * multiplier,
  ]
})
</script>

<template>
  <div class="relative">
    <!-- 主按钮 -->
    <button
      @click="toggleListening"
      :disabled="!isSupported"
      :class="[
        'relative w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300',
        isListening
          ? 'bg-gradient-to-r from-red-500 to-rose-500 shadow-lg shadow-red-500/30 scale-110'
          : 'bg-surface-light/50 hover:bg-surface-light text-slate-400 hover:text-white',
        !isSupported && 'opacity-50 cursor-not-allowed'
      ]"
      :title="isSupported ? (isListening ? '点击停止' : '语音输入') : '浏览器不支持语音输入'"
    >
      <!-- 麦克风图标 -->
      <svg v-if="!isListening" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
      </svg>
      
      <!-- 波形动画 -->
      <div v-else class="flex items-center gap-0.5 h-5">
        <div
          v-for="(_, i) in 5"
          :key="i"
          class="w-1 bg-white rounded-full transition-all duration-75"
          :style="{ height: `${waveHeights[i]}px` }"
        ></div>
      </div>
      
      <!-- 录音中光晕 -->
      <div
        v-if="isListening"
        class="absolute inset-0 rounded-xl animate-ping bg-red-500/30"
      ></div>
    </button>
    
    <!-- 实时转写文字 -->
    <Transition name="fade">
      <div
        v-if="isListening && transcript"
        class="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 px-4 py-2 bg-surface-dark/95 backdrop-blur rounded-xl text-white text-sm whitespace-nowrap shadow-xl border border-white/10"
      >
        <span class="text-accent-light">🎤</span>
        {{ transcript }}
      </div>
    </Transition>
    
    <!-- 提示文字 -->
    <div
      v-if="isListening"
      class="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs text-red-400 whitespace-nowrap"
    >
      正在录音...
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translate(-50%, 10px);
}
</style>

