import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface GuessEntry {
  word: string
  colors: ('green' | 'yellow' | 'gray')[]
  user_id: string
}

export const useGameStore = defineStore('game', () => {
  const guesses = ref<GuessEntry[]>([])
  const currentRow = ref('')
  const keyboardColors = ref<Record<string, string>>({})
  const status = ref<'waiting' | 'playing' | 'finished'>('waiting')
  const answer = ref('')
  const meaning = ref('')
  const winnerId = ref('')
  const wordLength = ref(5)
  const maxGuesses = ref(6)

  const isMyTurn = computed(() => status.value === 'playing')

  const canGuess = computed(() => status.value === 'playing' && currentRow.value.length === wordLength.value)

  function startGame(data: { word_length: number; max_guesses: number; word_bank?: string }) {
    status.value = 'playing'
    wordLength.value = data.word_length
    maxGuesses.value = data.max_guesses
    guesses.value = []
    currentRow.value = ''
  }

  function submitGuess(colors: ('green' | 'yellow' | 'gray')[], userId: string) {
    guesses.value.push({
      word: currentRow.value,
      colors,
      user_id: userId,
    })
    // Update keyboard colors (green > yellow > gray, never downgrade)
    for (let i = 0; i < currentRow.value.length; i++) {
      const letter = currentRow.value[i].toLowerCase()
      const existing = keyboardColors.value[letter]
      const newColor = colors[i]
      const priority: Record<string, number> = { green: 3, yellow: 2, gray: 1 }
      if (!existing || (priority[newColor] || 0) > (priority[existing] || 0)) {
        keyboardColors.value[letter] = newColor
      }
    }
    currentRow.value = ''
  }

  function addLetter(key: string) {
    if (currentRow.value.length < wordLength.value && status.value === 'playing') {
      currentRow.value += key.toLowerCase()
    }
  }

  function removeLetter() {
    if (currentRow.value.length > 0) {
      currentRow.value = currentRow.value.slice(0, -1)
    }
  }

  function endGame(data: { status: string; answer: string; meaning: string; winner_id?: string }) {
    status.value = 'finished'
    answer.value = data.answer
    meaning.value = data.meaning
    winnerId.value = data.winner_id || ''
  }

  function reset() {
    guesses.value = []
    currentRow.value = ''
    keyboardColors.value = {}
    status.value = 'waiting'
    answer.value = ''
    meaning.value = ''
    winnerId.value = ''
  }

  return { guesses, currentRow, keyboardColors, status, answer, meaning, winnerId, wordLength, maxGuesses, isMyTurn, canGuess, startGame, submitGuess, addLetter, removeLetter, endGame, reset }
})
