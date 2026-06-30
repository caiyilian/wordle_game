import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface UserInfo {
  id: string
  nickname: string
  avatar_url?: string | null
  total_games: number
  wins: number
  current_streak: number
  max_streak: number
  guess_distribution: Record<string, number>
  created_at: string
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(null)
  const user = ref<UserInfo | null>(null)

  function setAuth(t: string, u: UserInfo) {
    token.value = t
    user.value = u
  }

  function logout() {
    token.value = null
    user.value = null
  }

  return { token, user, setAuth, logout }
}, {
  persist: {
    key: 'wordle_user_store',
    storage: localStorage,
    pick: ['token', 'user'],
  },
})