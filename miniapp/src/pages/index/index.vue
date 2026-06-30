<template>
  <view class="container">
    <text class="title">Wordle Game</text>

    <view v-if="!token" class="auth-section">
      <input v-model="nickname" placeholder="Nickname" class="input" />
      <input v-model="password" type="password" placeholder="Password" class="input" />
      <button @click="login" class="btn btn-primary">Login</button>
      <button @click="register" class="btn btn-secondary">Register</button>
      <button @click="wechatLogin" class="btn btn-wechat">WeChat Login</button>
    </view>

    <view v-else class="game-section">
      <button @click="createRoom" class="btn btn-primary">Create Room</button>
      <view class="join-section">
        <input v-model="roomCode" placeholder="Room Code" class="input" />
        <button @click="joinRoom" class="btn btn-secondary">Join</button>
      </view>
      <button @click="goStats" class="btn btn-stats">My Statistics</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const token = ref('')
const nickname = ref('')
const password = ref('')
const roomCode = ref('')

const API_BASE = 'http://localhost:8000'

onMounted(() => {
  const saved = uni.getStorageSync('token')
  if (saved) token.value = saved
})

async function login() {
  const res = await uni.request({
    url: API_BASE + '/api/users/login',
    method: 'POST',
    data: { nickname: nickname.value, password: password.value },
  })
  if (res.statusCode === 200) {
    const data = res.data as any
    token.value = data.access_token
    uni.setStorageSync('token', data.access_token)
    uni.setStorageSync('nickname', data.user?.nickname || nickname.value)
  }
}

async function register() {
  const res = await uni.request({
    url: API_BASE + '/api/users/register',
    method: 'POST',
    data: { nickname: nickname.value, password: password.value },
  })
  if (res.statusCode === 201) {
    const data = res.data as any
    token.value = data.access_token
    uni.setStorageSync('token', data.access_token)
    uni.setStorageSync('nickname', data.user?.nickname || nickname.value)
  }
}

function wechatLogin() {
  uni.showToast({ title: 'WeChat login coming soon', icon: 'none' })
}

async function createRoom() {
  const res = await uni.request({
    url: API_BASE + '/api/rooms',
    method: 'POST',
    header: { Authorization: 'Bearer ' + token.value },
    data: { name: 'My Room', word_bank: 'CET4', word_length: 5, max_players: 6 },
  })
  if (res.statusCode === 201) {
    const data = res.data as any
    uni.navigateTo({ url: '/pages/game/index?code=' + data.code })
  }
}

async function joinRoom() {
  uni.navigateTo({ url: '/pages/game/index?code=' + roomCode.value })
}

function goStats() {
  uni.navigateTo({ url: '/pages/stats/index' })
}
</script>

<style scoped>
.container { padding: 40rpx; }
.title { font-size: 48rpx; font-weight: bold; text-align: center; margin-bottom: 60rpx; }
.auth-section, .game-section { display: flex; flex-direction: column; gap: 20rpx; }
.input { border: 2rpx solid #ddd; border-radius: 12rpx; padding: 20rpx; font-size: 28rpx; }
.btn { padding: 24rpx; border-radius: 12rpx; font-size: 28rpx; text-align: center; }
.btn-primary { background: #4a90d9; color: white; }
.btn-secondary { background: #67c23a; color: white; }
.btn-wechat { background: #07c160; color: white; }
.btn-stats { background: #8b5cf6; color: white; }
.join-section { display: flex; gap: 20rpx; }
.join-section .input { flex: 1; }
</style>