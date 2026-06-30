<template>
  <div class="max-w-2xl mx-auto px-4 py-6">
    <h1 class="text-3xl font-bold mb-8 text-center text-gray-800 dark:text-white">Wordle Game</h1>

    <!-- Login / Register -->
    <div v-if="!userStore.token" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200">{{ isRegister ? 'Register' : 'Login' }}</h2>
      <div class="space-y-4">
        <input v-model="nickname" placeholder="Nickname" class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-400 outline-none" />
        <input v-model="password" type="password" placeholder="Password" class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-400 outline-none" />
        <p v-if="errorMsg" class="text-red-500 text-sm">{{ errorMsg }}</p>
        <div class="flex gap-2">
          <button @click="isRegister ? doRegister() : doLogin()" :disabled="loading" class="flex-1 bg-blue-500 text-white py-2.5 rounded-lg hover:bg-blue-600 disabled:opacity-50 font-medium">
            {{ loading ? 'Loading...' : (isRegister ? 'Register' : 'Login') }}
          </button>
        </div>
        <p class="text-sm text-center text-gray-500">
          {{ isRegister ? 'Already have an account?' : "Don't have an account?" }}
          <a href="#" @click.prevent="isRegister = !isRegister" class="text-blue-500 hover:underline">
            {{ isRegister ? 'Login' : 'Register' }}
          </a>
        </p>
      </div>
    </div>

    <!-- Authenticated Home -->
    <div v-else class="space-y-6">

      <!-- User Info -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 flex items-center justify-between">
        <div>
          <p class="font-semibold text-gray-800 dark:text-gray-200">{{ userStore.user?.nickname }}</p>
          <p class="text-sm text-gray-500">Total: {{ userStore.user?.total_games ?? 0 }} | Wins: {{ userStore.user?.wins ?? 0 }}</p>
        </div>
        <button @click="userStore.logout()" class="text-sm text-red-500 hover:underline">Logout</button>
      </div>

      <!-- Create Room -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-lg font-semibold mb-4 text-gray-700 dark:text-gray-200">Create Room</h2>
        <div class="space-y-3">
          <input v-model="roomName" placeholder="Room name" class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-400 outline-none" />
          <WordBankSelector v-model="selectedBank" />
          <div class="flex gap-2">
            <select v-model="selectedLength" class="flex-1 px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200">
              <option v-for="n in 8" :key="n" :value="n + 2">{{ n + 2 }} letters</option>
            </select>
            <select v-model="maxPlayers" class="w-28 px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200">
              <option v-for="n in [2, 4, 6, 8, 10]" :key="n" :value="n">{{ n }} players</option>
            </select>
          </div>
          <p v-if="createError" class="text-red-500 text-sm">{{ createError }}</p>
          <button @click="doCreateRoom" :disabled="creating" class="w-full bg-green-500 text-white py-2.5 rounded-lg hover:bg-green-600 disabled:opacity-50 font-medium">
            {{ creating ? 'Creating...' : 'Create Room' }}
          </button>
        </div>
      </div>

      <!-- Join Room -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-lg font-semibold mb-4 text-gray-700 dark:text-gray-200">Join Room</h2>
        <p v-if="joinError" class="text-red-500 text-sm mb-2">{{ joinError }}</p>
        <div class="flex gap-2">
          <input v-model="joinCode" placeholder="Enter room code (e.g. AB3XY9)" maxlength="6" class="flex-1 px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 uppercase focus:ring-2 focus:ring-blue-400 outline-none" />
          <button @click="doJoinRoom" :disabled="joining" class="bg-blue-500 text-white px-6 py-2.5 rounded-lg hover:bg-blue-600 disabled:opacity-50 font-medium">
            {{ joining ? 'Joining...' : 'Join' }}
          </button>
        </div>
      </div>

      <!-- Room List -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-lg font-semibold mb-4 text-gray-700 dark:text-gray-200">
          Room List
          <span v-if="rooms.length > 0" class="text-sm font-normal text-gray-500">({{ rooms.length }})</span>
        </h2>
        <div v-if="loadingRooms" class="text-center py-4 text-gray-500">Loading...</div>
        <div v-else-if="rooms.length === 0" class="text-center py-4 text-gray-400">No rooms available. Create one!</div>
        <div v-else class="space-y-2">
          <div v-for="room in rooms" :key="room.id" class="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition">
            <div class="flex-1 min-w-0">
              <div class="font-medium text-gray-800 dark:text-gray-200 truncate">{{ room.name }}</div>
              <div class="text-xs text-gray-500">
                Code: {{ room.code }} | Bank: {{ room.word_bank }} | {{ room.word_length }} letters | {{ room.player_count }}/{{ room.max_players }} players
              </div>
            </div>
            <button @click="doJoinByRoomId(room.id)" class="ml-2 bg-blue-500 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-blue-600">
              Join
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import WordBankSelector from '@/components/WordBankSelector.vue'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()

// Auth
const nickname = ref('')
const password = ref('')
const isRegister = ref(false)
const loading = ref(false)
const errorMsg = ref('')

// Create Room
const roomName = ref('')
const selectedBank = ref('CET4')
const selectedLength = ref(5)
const maxPlayers = ref(6)
const creating = ref(false)
const createError = ref('')

// Join Room
const joinCode = ref('')
const joining = ref(false)
const joinError = ref('')

// Room List
const rooms = ref<any[]>([])
const loadingRooms = ref(false)

async function doRegister() {
  if (!nickname.value || !password.value) { errorMsg.value = 'Please fill in all fields'; return }
  loading.value = true; errorMsg.value = ''
  try {
    const resp = await axios.post('/api/users/register', { nickname: nickname.value, password: password.value })
    userStore.setAuth(resp.data.access_token, resp.data.user)
    await loadRooms()
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || 'Register failed'
  } finally { loading.value = false }
}

async function doLogin() {
  if (!nickname.value || !password.value) { errorMsg.value = 'Please fill in all fields'; return }
  loading.value = true; errorMsg.value = ''
  try {
    const resp = await axios.post('/api/users/login', { nickname: nickname.value, password: password.value })
    userStore.setAuth(resp.data.access_token, resp.data.user)
    await loadRooms()
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || 'Login failed'
  } finally { loading.value = false }
}

async function doCreateRoom() {
  if (!roomName.value) { createError.value = 'Please enter a room name'; return }
  creating.value = true; createError.value = ''
  try {
    const token = userStore.token
    const resp = await axios.post('/api/rooms', {
      name: roomName.value,
      word_bank: selectedBank.value,
      word_length: selectedLength.value,
      max_players: maxPlayers.value,
      max_guesses: selectedLength.value + 1,
    }, { headers: { Authorization: 'Bearer ' + token } })
    router.push('/room/' + resp.data.code)
  } catch (err: any) {
    createError.value = err.response?.data?.detail || 'Create room failed'
  } finally { creating.value = false }
}

async function doJoinRoom() {
  if (!joinCode.value) { joinError.value = 'Please enter a room code'; return }
  joining.value = true; joinError.value = ''
  try {
    const resp = await axios.post('/api/rooms/' + joinCode.value.toUpperCase() + '/join', {}, {
      headers: { Authorization: 'Bearer ' + userStore.token },
    })
    router.push('/room/' + resp.data.code)
  } catch (err: any) {
    joinError.value = err.response?.data?.detail || 'Join failed'
  } finally { joining.value = false }
}

async function doJoinByRoomId(roomId: string) {
  try {
    const resp = await axios.post('/api/rooms/' + roomId + '/join', {}, {
      headers: { Authorization: 'Bearer ' + userStore.token },
    })
    router.push('/room/' + resp.data.code)
  } catch (err: any) {
    joinError.value = err.response?.data?.detail || 'Join failed'
  }
}

async function loadRooms() {
  if (!userStore.token) return
  loadingRooms.value = true
  try {
    const resp = await axios.get('/api/rooms', { headers: { Authorization: 'Bearer ' + userStore.token } })
    rooms.value = resp.data.items || []
  } catch { rooms.value = [] }
  finally { loadingRooms.value = false }
}

onMounted(() => {
  if (userStore.token) loadRooms()
})
</script>
