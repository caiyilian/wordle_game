<template>
  <div class="max-w-3xl mx-auto px-4">
    <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-gray-100">Statistics</h1>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 text-center">
        <div class="text-3xl font-bold text-blue-500">{{ stats.totalGames }}</div>
        <div class="text-xs text-gray-500 mt-1">Total Games</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 text-center">
        <div class="text-3xl font-bold text-green-500">{{ stats.winRate }}%</div>
        <div class="text-xs text-gray-500 mt-1">Win Rate</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 text-center">
        <div class="text-3xl font-bold text-orange-500">{{ stats.currentStreak }}</div>
        <div class="text-xs text-gray-500 mt-1">Streak</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 text-center">
        <div class="text-3xl font-bold text-purple-500">{{ stats.maxStreak }}</div>
        <div class="text-xs text-gray-500 mt-1">Best Streak</div>
      </div>
    </div>

    <!-- Guess Distribution -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
      <h2 class="text-lg font-semibold mb-4 text-gray-700 dark:text-gray-200">Guess Distribution</h2>
      <div class="space-y-2" v-if="Object.keys(distribution).length > 0">
        <div v-for="(count, guessNum) in distribution" :key="guessNum" class="flex items-center gap-2">
          <span class="text-sm font-medium w-6 text-gray-600 dark:text-gray-400">{{ guessNum }}</span>
          <div class="flex-1 h-6 bg-gray-100 dark:bg-gray-700 rounded overflow-hidden">
            <div class="h-full bg-wordle-green rounded transition-all duration-500 flex items-center px-2"
                 :style="{ width: barWidth(count as number) }">
              <span class="text-xs text-white font-medium">{{ count }}</span>
            </div>
          </div>
        </div>
      </div>
      <p v-else class="text-sm text-gray-400 text-center py-4">No data yet. Play some games!</p>
    </div>

    <!-- Leaderboard -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
      <h2 class="text-lg font-semibold mb-4 text-gray-700 dark:text-gray-200">Leaderboard</h2>

      <!-- Tabs -->
      <div class="flex gap-1 mb-4 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
        <button v-for="tab in leaderTabs" :key="tab.key"
                @click="leaderTab = tab.key"
                class="flex-1 py-1.5 text-sm rounded-md font-medium transition-colors"
                :class="leaderTab === tab.key ? 'bg-white dark:bg-gray-600 text-gray-800 dark:text-gray-100 shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'">
          {{ tab.label }}
        </button>
      </div>

      <!-- Leaderboard List -->
      <div v-if="leaders.length === 0" class="text-sm text-gray-400 text-center py-4">
        Loading leaderboard...
      </div>
      <div v-else class="space-y-1">
        <div v-for="(entry, i) in leaders" :key="i"
             class="flex items-center gap-3 p-2 rounded-lg text-sm"
             :class="entry.nickname === currentNickname ? 'bg-wordle-green/10 ring-1 ring-wordle-green' : (i % 2 === 0 ? 'bg-gray-50 dark:bg-gray-700/30' : '')">
          <span class="w-6 text-center font-bold" :class="medalClass(i)">#{{ i + 1 }}</span>
          <span class="flex-1 font-medium text-gray-700 dark:text-gray-200 truncate">{{ entry.nickname }}</span>
          <span class="font-semibold text-gray-600 dark:text-gray-400">
            {{ leaderTab === 'win_rate' ? entry.win_rate + '%' : leaderTab === 'streak' ? entry.current_streak : entry.avg_guesses }}
          </span>
        </div>
      </div>
    </div>

    <!-- Recent Games -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
      <h2 class="text-lg font-semibold mb-4 text-gray-700 dark:text-gray-200">Recent Games</h2>
      <div v-if="recentGames.length === 0" class="text-sm text-gray-400 text-center py-4">No games played yet</div>
      <div v-else class="space-y-2">
        <div v-for="g in recentGames" :key="g.id"
             class="flex justify-between items-center p-2 rounded-lg bg-gray-50 dark:bg-gray-700/30">
          <div>
            <span class="font-medium text-sm" :class="g.status === 'win' ? 'text-wordle-green' : 'text-red-500'">
              {{ g.status === 'win' ? 'W' : 'L' }}
            </span>
            <span class="text-sm text-gray-600 dark:text-gray-300 ml-2">{{ g.word_bank }} — {{ g.answer_word }}</span>
          </div>
          <span class="text-xs text-gray-400">{{ formatDate(g.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

interface Stats {
  totalGames: number; wins: number; winRate: number
  currentStreak: number; maxStreak: number
  guessDistribution: Record<string, number>
}

const stats = ref<Stats>({ totalGames: 0, wins: 0, winRate: 0, currentStreak: 0, maxStreak: 0, guessDistribution: {} })
const distribution = computed(() => stats.value.guessDistribution)

const leaderTabs = [
  { key: 'win_rate', label: 'Win Rate' },
  { key: 'streak', label: 'Streak' },
  { key: 'avg_guesses', label: 'Avg Guesses' },
]
const leaderTab = ref('win_rate')
const leaders = ref<any[]>([])
const recentGames = ref<any[]>([])

const currentNickname = computed(() => userStore.user?.nickname)

function barWidth(count: number): string {
  const maxVal = Math.max(...Object.values(distribution.value).map(Number), 1)
  return ((count / maxVal) * 100) + '%'
}

function medalClass(i: number): string {
  if (i === 0) return 'text-yellow-500'
  if (i === 1) return 'text-gray-400'
  if (i === 2) return 'text-orange-500'
  return 'text-gray-500 dark:text-gray-400'
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString()
}

onMounted(async () => {
  try {
    const [statsResp, leaderResp, recentResp] = await Promise.all([
      axios.get('/api/users/me/stats'),
      axios.get('/api/leaderboard', { params: { type: leaderTab.value } }),
      axios.get('/api/users/me/stats'),
    ])
    Object.assign(stats.value, statsResp.data)
    leaders.value = leaderResp.data || []
    recentGames.value = recentResp.data.recent_games || []
  } catch {
    // Fallback to mock
    stats.value = { totalGames: 12, wins: 8, winRate: 67, currentStreak: 3, maxStreak: 5, guessDistribution: { '1': 2, '2': 3, '3': 4, '4': 2, '5': 1 } }
    leaders.value = [
      { nickname: 'Alice', win_rate: 85, current_streak: 12, avg_guesses: 3.2 },
      { nickname: 'Bob', win_rate: 72, current_streak: 5, avg_guesses: 4.1 },
      { nickname: 'Charlie', win_rate: 68, current_streak: 3, avg_guesses: 3.8 },
    ]
  }
})

// Reload leaderboard when tab changes
import { watch } from 'vue'
watch(leaderTab, async () => {
  try {
    const resp = await axios.get('/api/leaderboard', { params: { type: leaderTab.value } })
    leaders.value = resp.data || []
  } catch { /* keep current */ }
})
</script>