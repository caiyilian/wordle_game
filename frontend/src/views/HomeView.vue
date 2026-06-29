<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold mb-8 text-center">Welcome to Wordle</h1>
    
    <div v-if="!userStore.token" class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">Login / Register</h2>
      <div class="space-y-4">
        <input v-model="nickname" placeholder="Nickname" class="w-full px-4 py-2 border rounded dark:bg-gray-700 dark:border-gray-600" />
        <input v-model="password" type="password" placeholder="Password" class="w-full px-4 py-2 border rounded dark:bg-gray-700 dark:border-gray-600" />
        <div class="flex gap-2">
          <button @click="register" class="flex-1 bg-blue-500 text-white py-2 rounded hover:bg-blue-600">Register</button>
          <button @click="login" class="flex-1 bg-green-500 text-white py-2 rounded hover:bg-green-600">Login</button>
        </div>
      </div>
    </div>

    <div v-else class="space-y-6">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Create Room</h2>
        <div class="space-y-3">
          <input v-model="roomName" placeholder="Room Name" class="w-full px-4 py-2 border rounded dark:bg-gray-700 dark:border-gray-600" />
          <select v-model="selectedBank" class="w-full px-4 py-2 border rounded dark:bg-gray-700 dark:border-gray-600">
            <option value="CET4">CET4</option>
            <option value="CET6">CET6</option>
            <option value="考研">考研</option>
            <option value="TOEFL">TOEFL</option>
            <option value="GRE">GRE</option>
          </select>
          <select v-model="selectedLength" class="w-full px-4 py-2 border rounded dark:bg-gray-700 dark:border-gray-600">
            <option :value="3">3 letters</option>
            <option :value="4">4 letters</option>
            <option :value="5">5 letters</option>
            <option :value="6">6 letters</option>
          </select>
          <button @click="createRoom" class="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600">Create Room</button>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Join Room</h2>
        <div class="flex gap-2">
          <input v-model="joinCode" placeholder="Enter room code" class="flex-1 px-4 py-2 border rounded dark:bg-gray-700 dark:border-gray-600" />
          <button @click="joinRoom" class="bg-green-500 text-white px-6 rounded hover:bg-green-600">Join</button>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Room List</h2>
        <div v-if="rooms.length === 0" class="text-gray-500">No rooms available</div>
        <div v-else class="space-y-2">
          <div v-for="room in rooms" :key="room.id" class="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <div>
              <span class="font-medium">{{ room.name }}</span>
              <span class="text-sm text-gray-500 ml-2">({{ room.code }})</span>
            </div>
            <button @click="joinByRoomId(room.id)" class="text-blue-500 hover:underline">Join</button>
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
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()

const nickname = ref('')
const password = ref('')
const roomName = ref('')
const selectedBank = ref('CET4')
const selectedLength = ref(5)
const joinCode = ref('')
const rooms = ref<any[]>([])

async function register() {
  const resp = await axios.post('/api/users/register', { nickname: nickname.value, password: password.value })
  userStore.setAuth(resp.data.access_token, resp.data.user)
}

async function login() {
  const resp = await axios.post('/api/users/login', { nickname: nickname.value, password: password.value })
  userStore.setAuth(resp.data.access_token, resp.data.user)
}

async function createRoom() {
  const resp = await axios.post('/api/rooms', {
    name: roomName.value,
    word_bank: selectedBank.value,
    word_length: selectedLength.value,
    max_players: 8,
  }, { headers: { Authorization: 'Bearer ' + userStore.token } })
  router.push('/room/' + resp.data.code)
}

async function joinRoom() {
  const resp = await axios.post('/api/rooms/' + joinCode.value + '/join', {}, {
    headers: { Authorization: 'Bearer ' + userStore.token },
  })
  router.push('/room/' + resp.data.code)
}

async function joinByRoomId(roomId: string) {
  const resp = await axios.post('/api/rooms/' + roomId + '/join', {}, {
    headers: { Authorization: 'Bearer ' + userStore.token },
  })
  router.push('/room/' + resp.data.code)
}

onMounted(async () => {
  if (userStore.token) {
    const resp = await axios.get('/api/rooms', { headers: { Authorization: 'Bearer ' + userStore.token } })
    rooms.value = resp.data.items
  }
})
</script>
