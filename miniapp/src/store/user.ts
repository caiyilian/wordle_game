import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const nickname = ref('')
  const userId = ref('')
  const avatarUrl = ref('')

  const isLoggedIn = computed(() => !!token.value)

  function loadFromStorage() {
    const saved = uni.getStorageSync('token')
    if (saved) token.value = saved
    const savedNickname = uni.getStorageSync('nickname')
    if (savedNickname) nickname.value = savedNickname
    const savedId = uni.getStorageSync('userId')
    if (savedId) userId.value = savedId
  }

  function setToken(t: string) {
    token.value = t
    uni.setStorageSync('token', t)
  }

  function setUser(user: { id: string; nickname: string; avatar_url?: string }) {
    userId.value = user.id
    nickname.value = user.nickname
    avatarUrl.value = user.avatar_url || ''
    uni.setStorageSync('nickname', user.nickname)
    uni.setStorageSync('userId', user.id)
  }

  async function login(nick: string, password: string) {
    const res = await uni.request({
      url: 'http://localhost:8000/api/users/login',
      method: 'POST',
      data: { nickname: nick, password },
    })
    const data = res.data as any
    if (res.statusCode === 200 && data.access_token) {
      setToken(data.access_token)
      setUser(data.user)
      return true
    }
    return false
  }

  async function register(nick: string, password: string) {
    const res = await uni.request({
      url: 'http://localhost:8000/api/users/register',
      method: 'POST',
      data: { nickname: nick, password },
    })
    const data = res.data as any
    if (res.statusCode === 201 && data.access_token) {
      setToken(data.access_token)
      setUser(data.user)
      return true
    }
    return false
  }

  function logout() {
    token.value = ''
    nickname.value = ''
    userId.value = ''
    avatarUrl.value = ''
    uni.removeStorageSync('token')
    uni.removeStorageSync('nickname')
    uni.removeStorageSync('userId')
  }

  loadFromStorage()

  return { token, nickname, userId, avatarUrl, isLoggedIn, login, register, logout, setToken, setUser, loadFromStorage }
})
