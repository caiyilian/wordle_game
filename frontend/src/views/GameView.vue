<template>
  <div class="max-w-4xl mx-auto">
    <div class="flex flex-col lg:flex-row gap-6">
      <div class="flex-1">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-4">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold">Room: {{ roomCode }}</h2>
            <span class="text-sm text-gray-500">{{ wordBank }} - {{ wordLength }} letters</span>
          </div>
          
          <div class="flex flex-col items-center gap-1 mb-4">
            <div v-for="(row, rowIndex) in displayRows" :key="rowIndex" class="flex gap-1">
              <div v-for="(cell, cellIndex) in row" :key="cellIndex"
                   class="w-12 h-12 border-2 flex items-center justify-center text-xl font-bold uppercase transition-colors duration-200"
                   :class="getCellClass(cell.color, rowIndex === currentRowIndex, cellIndex)">
                {{ cell.letter }}
              </div>
            </div>
          </div>
          
          <div class="flex flex-col items-center gap-1">
            <div v-for="(row, rIdx) in keyboardRows" :key="rIdx" class="flex gap-1">
              <button v-for="key in row" :key="key" @click="handleKey(key)"
                      class="px-3 py-2 rounded text-sm font-bold transition-all active:scale-95"
                      :class="getKeyClass(key)">
                {{ key === 'BACKSPACE' ? '\u232B' : key === 'ENTER' ? '\u2713' : key }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="lg:w-72 bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <h3 class="font-semibold mb-3">Chat</h3>
        <div ref="chatRef" class="h-64 overflow-y-auto space-y-2 mb-3 text-sm">
          <div v-for="msg in chatMessages" :key="msg.id" class="p-2 rounded bg-gray-50 dark:bg-gray-700">
            <span class="font-medium">{{ msg.nickname || msg.userId }}:</span>
            <span class="text-gray-600 dark:text-gray-300"> {{ msg.content }}</span>
          </div>
        </div>
        <div class="flex gap-2">
          <input v-model="chatInput" @keyup.enter="sendChat" placeholder="Type a message..."
                 class="flex-1 px-3 py-1 border rounded text-sm dark:bg-gray-700 dark:border-gray-600" />
          <button @click="sendChat" class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600">Send</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useGameStore } from '@/stores/game'
import { KEYBOARD_ROWS } from '@/utils/constants'

const route = useRoute()
const userStore = useUserStore()
const gameStore = useGameStore()

const roomCode = ref(route.params.id as string)
const wordBank = ref('CET4')
const wordLength = ref(5)
const currentRowIndex = ref(0)
const chatMessages = ref<any[]>([])
const chatInput = ref('')
const chatRef = ref<HTMLElement>()

const keyboardRows = KEYBOARD_ROWS

const displayRows = computed(() => {
  const rows: any[][] = []
  for (let i = 0; i < 6; i++) {
    if (i < gameStore.state.guesses.length) {
      const guess = gameStore.state.guesses[i]
      rows.push(guess.word.split('').map((letter: string, j: number) => ({
        letter,
        color: guess.colors[j],
      })))
    } else if (i === gameStore.state.guesses.length) {
      const current = gameStore.currentRow.padEnd(wordLength.value, '_').split('')
      rows.push(current.map((l: string) => ({ letter: l, color: null as any })))
    } else {
      rows.push(Array(wordLength.value).fill(null).map(() => ({ letter: '', color: null as any })))
    }
  }
  return rows
})

function getCellClass(color: string | null, isActive: boolean, index: number) {
  if (!color) return isActive ? 'border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-700 text-gray-800 dark:text-white animate-pulse' : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700'
  const base = 'text-white'
  if (color === 'green') return base + ' bg-wordle-green'
  if (color === 'yellow') return base + ' bg-wordle-yellow'
  return base + ' bg-wordle-gray'
}

function getKeyClass(key: string) {
  const state = gameStore.keyStates[key]
  if (state === 'green') return 'bg-wordle-green text-white'
  if (state === 'yellow') return 'bg-wordle-yellow text-white'
  if (state === 'gray') return 'bg-wordle-gray text-white'
  return 'bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-500'
}

function handleKey(key: string) {
  if (key === 'BACKSPACE') gameStore.removeLetter()
  else if (key === 'ENTER') submitGuess()
  else gameStore.addLetter(key)
}

function submitGuess() {
  if (gameStore.currentRow.length !== wordLength.value) return
  gameStore.submitGuess([])
  currentRowIndex.value++
}

async function sendChat() {
  if (!chatInput.value.trim()) return
  chatMessages.value.push({
    id: Date.now(),
    nickname: userStore.user?.nickname,
    content: chatInput.value,
  })
  chatInput.value = ''
  await nextTick()
  chatRef.value?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  if (userStore.token) {
    console.log('Connected to room:', roomCode.value)
  }
})
</script>
