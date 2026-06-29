<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold mb-8 text-center">个人统计</h1>
    
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 text-center">
        <div class="text-3xl font-bold text-blue-500">{{ stats.totalGames }}</div>
        <div class="text-sm text-gray-500">总局数</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 text-center">
        <div class="text-3xl font-bold text-green-500">{{ stats.winRate }}%</div>
        <div class="text-sm text-gray-500">胜率</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 text-center">
        <div class="text-3xl font-bold text-orange-500">{{ stats.currentStreak }}</div>
        <div class="text-sm text-gray-500">当前连胜</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 text-center">
        <div class="text-3xl font-bold text-purple-500">{{ stats.maxStreak }}</div>
        <div class="text-sm text-gray-500">最长连胜</div>
      </div>
    </div>
    
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">猜词分布</h2>
      <div class="flex items-end gap-2 h-32">
        <div v-for="(count, guesses) in distribution" :key="guesses" class="flex-1 flex flex-col items-center">
          <span class="text-xs mb-1">{{ count }}</span>
          <div class="w-full bg-blue-500 rounded-t" :style="{ height: Math.max(count * 20, 4) + 'px' }"></div>
          <span class="text-xs mt-1">{{ guesses }}次</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

interface Stats {
  totalGames: number
  wins: number
  winRate: number
  currentStreak: number
  maxStreak: number
  guessDistribution: Record<string, number>
}

const stats = ref<Stats>({
  totalGames: 0, wins: 0, winRate: 0,
  currentStreak: 0, maxStreak: 0, guessDistribution: {},
})

const distribution = computed(() => stats.value.guessDistribution)

onMounted(async () => {
  try {
    const resp = await axios.get('/api/users/me/stats')
    Object.assign(stats.value, resp.data)
  } catch {
    // Use mock data for demo
    stats.value = {
      totalGames: 12, wins: 8, winRate: 66.7,
      currentStreak: 3, maxStreak: 5,
      guessDistribution: { '1': 2, '2': 3, '3': 2, '4': 1 },
    }
  }
})
</script>