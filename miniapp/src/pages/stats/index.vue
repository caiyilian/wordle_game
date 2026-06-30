<template>
  <view class="container">
    <text class="page-title">Statistics</text>

    <view class="stats-grid">
      <view class="stat-card"><text class="stat-value">{{ stats.totalGames }}</text><text class="stat-label">Total Games</text></view>
      <view class="stat-card"><text class="stat-value">{{ stats.winRate }}%</text><text class="stat-label">Win Rate</text></view>
      <view class="stat-card"><text class="stat-value">{{ stats.streak }}</text><text class="stat-label">Streak</text></view>
      <view class="stat-card"><text class="stat-value">{{ stats.maxStreak }}</text><text class="stat-label">Best Streak</text></view>
    </view>

    <view class="section">
      <text class="section-title">Guess Distribution</text>
      <view v-if="Object.keys(distribution).length > 0" class="dist-list">
        <view v-for="(count, guessNum) in distribution" :key="guessNum" class="dist-row">
          <text class="dist-label">{{ guessNum }}</text>
          <view class="dist-bar">
            <view class="dist-fill" :style="{ width: barWidth(count as number) + '%' }">
              <text class="dist-count">{{ count }}</text>
            </view>
          </view>
        </view>
      </view>
      <text v-else class="empty-text">No data yet. Play some games!</text>
    </view>

    <view class="section">
      <text class="section-title">Leaderboard</text>
      <view class="tabs">
        <text v-for="tab in tabs" :key="tab.key" class="tab" :class="tab.key === activeTab ? 'tab-active' : ''" @click="switchTab(tab.key)">{{ tab.label }}</text>
      </view>
      <view v-if="leaders.length === 0" class="empty-text">Loading...</view>
      <view v-else class="leader-list">
        <view v-for="(entry, i) in leaders" :key="i" class="leader-row">
          <text class="rank">#{{ i + 1 }}</text>
          <text class="nickname">{{ entry.nickname }}</text>
          <text class="score">{{ entry[activeTab] }}{{ activeTab === 'win_rate' ? '%' : '' }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

interface Stats {
  totalGames: number
  wins: number
  winRate: number
  streak: number
  maxStreak: number
  guessDistribution: Record<string, number>
}

const stats = ref<Stats>({ totalGames: 0, wins: 0, winRate: 0, streak: 0, maxStreak: 0, guessDistribution: {} })
const distribution = computed(() => stats.value.guessDistribution)
const leaders = ref<any[]>([])
const activeTab = ref('win_rate')
const tabs = [
  { key: 'win_rate', label: 'Win Rate' },
  { key: 'streak', label: 'Streak' },
  { key: 'avg_guesses', label: 'Avg Guesses' },
]

function barWidth(count: number): number {
  const maxVal = Math.max(...Object.values(distribution.value).map(Number), 1)
  return (count / maxVal) * 100
}

function loadLeaderboard() {
  const token = userStore.token
  if (!token) return
  uni.request({
    url: 'http://localhost:8000/api/leaderboard?type=' + activeTab.value,
    header: { Authorization: 'Bearer ' + token },
    success(res: any) {
      if (res.statusCode === 200) {
        leaders.value = res.data || []
      }
    }
  })
}

function switchTab(tab: string) {
  activeTab.value = tab
  loadLeaderboard()
}

onMounted(() => {
  const token = userStore.token
  if (!token) return
  // Load stats
  uni.request({
    url: 'http://localhost:8000/api/users/me/stats',
    header: { Authorization: 'Bearer ' + token },
    success(res: any) {
      if (res.statusCode === 200) {
        const d = res.data
        stats.value = {
          totalGames: d.total_games || 0,
          wins: d.wins || 0,
          winRate: d.win_rate || 0,
          streak: d.current_streak || 0,
          maxStreak: d.max_streak || 0,
          guessDistribution: d.guess_distribution || {},
        }
      }
    }
  })
  loadLeaderboard()
})
</script>

<style scoped>
.container { padding: 30rpx; }
.page-title { font-size: 40rpx; font-weight: bold; text-align: center; margin-bottom: 40rpx; }
.stats-grid { display: flex; flex-wrap: wrap; gap: 16rpx; margin-bottom: 40rpx; }
.stat-card { flex: 1; min-width: 120rpx; background: white; border-radius: 16rpx; padding: 24rpx; text-align: center; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.08); }
.stat-value { font-size: 40rpx; font-weight: bold; color: #4a90d9; display: block; }
.stat-label { font-size: 22rpx; color: #9ca3af; margin-top: 8rpx; display: block; }
.section { background: white; border-radius: 16rpx; padding: 24rpx; margin-bottom: 20rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.08); }
.section-title { font-size: 30rpx; font-weight: 600; margin-bottom: 20rpx; display: block; }
.dist-list { display: flex; flex-direction: column; gap: 8rpx; }
.dist-row { display: flex; align-items: center; gap: 12rpx; }
.dist-label { width: 40rpx; text-align: right; font-size: 24rpx; color: #6b7280; }
.dist-bar { flex: 1; height: 36rpx; background: #f3f4f6; border-radius: 8rpx; overflow: hidden; }
.dist-fill { height: 100%; background: #86a373; border-radius: 8rpx; display: flex; align-items: center; padding-left: 12rpx; }
.dist-count { font-size: 20rpx; color: white; font-weight: bold; }
.empty-text { color: #9ca3af; font-size: 24rpx; text-align: center; padding: 24rpx; }
.tabs { display: flex; gap: 8rpx; margin-bottom: 20rpx; }
.tab { flex: 1; text-align: center; padding: 12rpx; font-size: 24rpx; background: #f3f4f6; border-radius: 8rpx; }
.tab-active { background: #4a90d9; color: white; }
.leader-list { display: flex; flex-direction: column; gap: 4rpx; }
.leader-row { display: flex; align-items: center; padding: 16rpx; border-radius: 8rpx; background: #f9fafb; }
.rank { width: 60rpx; font-weight: bold; font-size: 24rpx; color: #6b7280; }
.nickname { flex: 1; font-size: 26rpx; }
.score { font-weight: bold; font-size: 26rpx; color: #374151; }
</style>
