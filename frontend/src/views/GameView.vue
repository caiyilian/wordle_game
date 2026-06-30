<template>
  <div class="max-w-4xl mx-auto px-4 py-4">
    <div class="flex flex-col lg:flex-row gap-6">
      <!-- Left: Game Board + Keyboard -->
      <div class="flex-1">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 mb-4">
          <!-- Room Header -->
          <div class="flex justify-between items-center mb-4">
            <div>
              <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-200">
                Room: {{ roomCode }}
                <span class="text-sm text-gray-500 ml-2 font-normal">{{ wordBank }}</span>
              </h2>
              <div class="text-xs text-gray-500">
                Players: {{ players.join(', ') || 'Waiting...' }}
                <span v-if="wsConnected" class="text-green-500 ml-2">● Connected</span>
                <span v-else class="text-red-500 ml-2">● Disconnected</span>
              </div>
            </div>
            <div class="flex gap-2">
              <button v-if="isRoomOwner && gameStore.state.status === 'waiting'"
                      @click="startGame"
                      class="bg-green-500 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-green-600">
                Start Game
              </button>
              <button @click="leaveRoom"
                      class="bg-red-500 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-red-600">
                Leave
              </button>
            </div>
          </div>

          <!-- Game Board -->
          <div v-if="gameStore.state.status !== 'waiting'" class="flex flex-col items-center gap-1.5 mb-4">
            <GameBoard />
          </div>
          <div v-else class="text-center py-16 text-gray-400">
            <p class="text-lg mb-2">Waiting for host to start the game...</p>
            <p class="text-sm">Share code: <strong class="text-gray-600 dark:text-gray-300">{{ roomCode }}</strong></p>
          </div>

          <!-- Virtual Keyboard -->
          <div v-if="gameStore.state.status !== 'waiting'" class="mt-4">
            <VirtualKeyboard @letter="onKeyLetter" @enter="onKeyEnter" @backspace="onKeyBackspace" />
          </div>
        </div>
      </div>

      <!-- Right: Chat Panel -->
      <div class="lg:w-72 hidden lg:block">
        <ChatPanel
          :messages="chatMessages"
          :can-send="wsConnected"
          @send="onChatSend"
        />
      </div>
    </div>

    <!-- Mobile chat toggle -->
    <button v-if="!showMobileChat" @click="showMobileChat = true"
            class="lg:hidden fixed bottom-4 right-4 bg-blue-500 text-white w-12 h-12 rounded-full shadow-lg flex items-center justify-center text-xl z-40">
      💬
    </button>

    <!-- Mobile chat drawer -->
    <Teleport to="body">
      <div v-if="showMobileChat" class="lg:hidden fixed inset-0 z-50 bg-black/40" @click="showMobileChat = false">
        <div class="absolute bottom-0 left-0 right-0 bg-white dark:bg-gray-800 rounded-t-2xl p-4 max-h-[60vh] overflow-auto"
             @click.stop>
          <div class="flex justify-between items-center mb-3">
            <h3 class="font-semibold text-gray-700 dark:text-gray-200">Chat</h3>
            <button @click="showMobileChat = false" class="text-gray-500 text-lg">✕</button>
          </div>
          <ChatPanel
            :messages="chatMessages"
            :can-send="wsConnected"
            @send="onChatSend"
          />
        </div>
      </div>
    </Teleport>

    <!-- Result Modal -->
    <ResultModal
      v-if="showResult && gameStore.state.answer"
      :is-win="gameStore.state.winnerId === userStore.user?.id"
      :answer="gameStore.state.answer"
      :meaning="gameStore.state.meaning"
      :guess-count="gameStore.state.guesses.length"
      :guesses="gameStore.state.guesses as any"
      @close="showResult = false"
      @play-again="startGame"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watchEffect, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useGameStore } from '@/stores/game'
import { useWebSocket } from '@/composables/useWebSocket'
import GameBoard from '@/components/GameBoard.vue'
import VirtualKeyboard from '@/components/VirtualKeyboard.vue'
import ChatPanel from '@/components/ChatPanel.vue'
import ResultModal from '@/components/ResultModal.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const gameStore = useGameStore()

const roomCode = ref(route.params.id as string)
const wordBank = ref('CET4')
const players = ref<string[]>([])
const chatMessages = ref<Array<{id: number; type?: string; userId?: string; nickname?: string; content: string}>>([])

// WebSocket
const wsConnected = ref(false)
const showResult = ref(false)
const showMobileChat = ref(false)

const { connected, connect, disconnect, send } = useWebSocket(roomCode.value, userStore.token || '', {
  onGuessResult(data: any) {
    gameStore.submitGuess(data.colors)
    addChatMsg('system', data.nickname + ' guessed ' + data.word)
  },
  onGameOver(data: any) {
    gameStore.state.status = 'finished'
    gameStore.state.answer = data.answer
    gameStore.state.meaning = data.meaning
    gameStore.state.winnerId = data.winner_id
    const winner = data.winner_id === userStore.user?.id ? 'You' : (data.winner_nickname || 'Someone')
    addChatMsg('system', 'Game over! Answer: ' + data.answer + ' (' + data.meaning + ') Winner: ' + winner)
    showResult.value = true
  },
  onGameStart(data: any) {
    gameStore.state.status = 'playing'
    gameStore.state.wordLength = data.word_length
    gameStore.state.maxGuesses = data.max_guesses
    gameStore.reset()
    wordBank.value = data.word_bank || wordBank.value
    addChatMsg('system', 'Game started! Guess the ' + data.word_length + '-letter word!')
  },
  onPlayerJoined(data: any) {
    if (!players.value.includes(data.nickname)) {
      players.value.push(data.nickname)
    }
    addChatMsg('system', data.nickname + ' joined the room')
  },
  onPlayerLeft(data: any) {
    players.value = players.value.filter((p: string) => p !== data.nickname)
    addChatMsg('system', data.nickname + ' left the room')
  },
  onChat(data: any) {
    addChatMsg('chat', data.message, data.nickname, data.user_id)
  },
  onPong() {
    wsConnected.value = true
  },
  onError(data: any) {
    addChatMsg('system', 'Error: ' + (data.message || 'unknown error'))
  },
})

watchEffect(() => {
  wsConnected.value = connected.value
})

const roomOwner = ref<string>('')

function addChatMsg(type: string, content: string, nickname?: string, userId?: string) {
  chatMessages.value.push({ id: Date.now(), type, content, nickname, userId })
}

const isRoomOwner = computed(() => {
  return userStore.user?.id && roomOwner.value && userStore.user.id === roomOwner.value
})

function startGame() {
  send('start_game')
  addChatMsg('system', 'Starting game...')
}

function onKeyLetter(key: string) {
  gameStore.addLetter(key)
}

function onKeyEnter() {
  if (gameStore.currentRow.length !== gameStore.state.wordLength) return
  send('guess', { word: gameStore.currentRow.toLowerCase() })
}

function onKeyBackspace() {
  gameStore.removeLetter()
}

function onChatSend(text: string) {
  if (!wsConnected.value) return
  send('chat', { message: text })
}

function leaveRoom() {
  disconnect()
  gameStore.reset()
  router.push('/')
}

function handleKeydown(e: KeyboardEvent) {
  const key = e.key.toUpperCase()
  if (!wsConnected.value) return
  if (key === 'BACKSPACE') onKeyBackspace()
  else if (key === 'ENTER') {
    // Don't capture Enter when typing in chat input
    if (document.activeElement?.tagName !== 'INPUT') onKeyEnter()
  }
  else if (/^[A-Z]$/.test(key) && gameStore.state.status === 'playing') onKeyLetter(key)
}

onMounted(async () => {
  if (!userStore.token) {
    router.push('/')
    return
  }
  // Get room info
  try {
    const axios = (await import('axios')).default
    const info = await axios.get('/api/rooms/' + roomCode.value, {
      headers: { Authorization: 'Bearer ' + userStore.token }
    })
    wordBank.value = info.data.word_bank
    gameStore.state.wordLength = info.data.word_length
    gameStore.state.maxGuesses = info.data.max_guesses
    roomOwner.value = info.data.created_by
    // Join room
    await axios.post('/api/rooms/' + roomCode.value + '/join', {}, {
      headers: { Authorization: 'Bearer ' + userStore.token }
    })
  } catch { /* already joined */ }
  // Connect WebSocket
  connect()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  disconnect()
})
</script>
