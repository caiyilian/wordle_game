import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface UserInfo {
  id: string
  nickname: string
  avatar_url?: string
  total_games: number
  wins: number
  current_streak: number
  max_streak: number
  guess_distribution: Record<string, number>
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<UserInfo | null>(JSON.parse(localStorage.getItem('user') || 'null'))

  function setAuth(t: string, u: UserInfo) {
    token.value = t
    user.value = u
    localStorage.setItem('token', t)
    localStorage.setItem('user', JSON.stringify(u))
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, setAuth, logout }
})