<script setup lang="ts">
import { ref } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'
import HealthRadar from '@/components/charts/HealthRadar.vue'

const analysisStore = useAnalysisStore()

const repos = ref(['', ''])
const isLoading = ref(false)
const results = ref<any[]>([])

function addRepo() {
  if (repos.value.length < 5) {
    repos.value.push('')
  }
}

function removeRepo(index: number) {
  if (repos.value.length > 2) {
    repos.value.splice(index, 1)
  }
}

async function compare() {
  const validRepos = repos.value.filter(r => r.trim())
  if (validRepos.length < 2) {
    alert('请至少输入两个仓库进行对比')
    return
  }
  
  isLoading.value = true
  results.value = []
  
  try {
    for (const repo of validRepos) {
      try {
        const result = await analysisStore.analyzeRepo(repo)
        results.value.push(result)
      } catch (e) {
        results.value.push({ repo, error: '分析失败' })
      }
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- 输入区域 -->
    <div class="glass p-6">
      <h2 class="text-xl font-semibold text-white mb-4">项目对比</h2>
      
      <div class="space-y-3">
        <div
          v-for="(repo, index) in repos"
          :key="index"
          class="flex gap-3"
        >
          <input
            v-model="repos[index]"
            type="text"
            :placeholder="`仓库 ${index + 1}，如 apache/dubbo`"
            class="flex-1 bg-surface border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-accent/50"
          />
          <button
            v-if="repos.length > 2"
            @click="removeRepo(index)"
            class="px-4 py-3 bg-red-500/20 text-red-400 rounded-xl hover:bg-red-500/30 transition-colors"
          >
            删除
          </button>
        </div>
      </div>
      
      <div class="flex gap-4 mt-4">
        <button
          v-if="repos.length < 5"
          @click="addRepo"
          class="px-4 py-2 bg-surface-light text-slate-300 rounded-xl hover:bg-surface transition-colors"
        >
          + 添加仓库
        </button>
        <button
          @click="compare"
          :disabled="isLoading"
          class="px-6 py-2 bg-accent text-white font-semibold rounded-xl hover:bg-accent-dark disabled:opacity-50 transition-colors"
        >
          {{ isLoading ? '对比中...' : '开始对比' }}
        </button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="loading-dots mb-4 justify-center">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <p class="text-slate-400">正在分析项目...</p>
    </div>
    
    <!-- 对比结果 -->
    <div v-else-if="results.length > 0" class="space-y-6">
      <!-- 总览表格 -->
      <div class="glass p-6 overflow-x-auto">
        <h3 class="text-lg font-semibold text-white mb-4">对比总览</h3>
        
        <table class="w-full">
          <thead>
            <tr class="border-b border-white/10">
              <th class="text-left py-3 px-4 text-slate-400 font-medium">指标</th>
              <th
                v-for="result in results"
                :key="result.repo"
                class="text-center py-3 px-4 text-white font-medium"
              >
                {{ result.repo }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b border-white/5">
              <td class="py-3 px-4 text-slate-300">总体评分</td>
              <td
                v-for="result in results"
                :key="result.repo"
                class="text-center py-3 px-4"
              >
                <span
                  v-if="!result.error"
                  :class="['text-2xl font-bold', analysisStore.getScoreClass(result.healthScore.overall)]"
                >
                  {{ result.healthScore.overall }}
                </span>
                <span v-else class="text-red-400">-</span>
              </td>
            </tr>
            <tr class="border-b border-white/5">
              <td class="py-3 px-4 text-slate-300">活跃度</td>
              <td
                v-for="result in results"
                :key="result.repo"
                class="text-center py-3 px-4 text-white"
              >
                {{ result.healthScore?.activity ?? '-' }}
              </td>
            </tr>
            <tr class="border-b border-white/5">
              <td class="py-3 px-4 text-slate-300">社区健康度</td>
              <td
                v-for="result in results"
                :key="result.repo"
                class="text-center py-3 px-4 text-white"
              >
                {{ result.healthScore?.community ?? '-' }}
              </td>
            </tr>
            <tr class="border-b border-white/5">
              <td class="py-3 px-4 text-slate-300">维护响应度</td>
              <td
                v-for="result in results"
                :key="result.repo"
                class="text-center py-3 px-4 text-white"
              >
                {{ result.healthScore?.maintenance ?? '-' }}
              </td>
            </tr>
            <tr class="border-b border-white/5">
              <td class="py-3 px-4 text-slate-300">增长趋势</td>
              <td
                v-for="result in results"
                :key="result.repo"
                class="text-center py-3 px-4 text-white"
              >
                {{ result.healthScore?.growth ?? '-' }}
              </td>
            </tr>
            <tr class="border-b border-white/5">
              <td class="py-3 px-4 text-slate-300">OpenRank</td>
              <td
                v-for="result in results"
                :key="result.repo"
                class="text-center py-3 px-4 text-white"
              >
                {{ result.metrics?.openrank?.toFixed(2) ?? '-' }}
              </td>
            </tr>
            <tr>
              <td class="py-3 px-4 text-slate-300">巴士因子</td>
              <td
                v-for="result in results"
                :key="result.repo"
                class="text-center py-3 px-4 text-white"
              >
                {{ result.metrics?.bus_factor ?? '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 雷达图对比 -->
      <div class="grid grid-cols-2 gap-6">
        <div
          v-for="result in results.filter(r => !r.error)"
          :key="result.repo"
          class="glass p-6"
        >
          <h3 class="text-lg font-semibold text-white mb-4">{{ result.repo }}</h3>
          <HealthRadar :health-score="result.healthScore" />
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div v-else class="text-center py-16">
      <div class="text-6xl mb-6">⚖️</div>
      <h2 class="text-2xl font-bold text-white mb-4">项目对比分析</h2>
      <p class="text-slate-400">
        输入多个仓库地址，对比它们的健康度指标
      </p>
    </div>
  </div>
</template>

