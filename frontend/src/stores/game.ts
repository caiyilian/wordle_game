import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ColorResult, GuessResult, GameState } from '@/types/game'

export const useGameStore = defineStore('game', () => {
  const state = ref<GameState>({
    wordLength: 5,
    maxGuesses: 6,
    wordBank: 'CET4',
    guesses: [],
    status: 'waiting',
  })

  const currentRow = ref('')
  const keyStates = ref<Record<string, ColorResult>>({})

  function addLetter(letter: string) {
    if (currentRow.value.length < state.value.wordLength) {
      currentRow.value += letter
    }
  }

  function removeLetter() {
    currentRow.value = currentRow.value.slice(0, -1)
  }

  function submitGuess(colors: ColorResult[]) {
    const guessWord = currentRow.value.toLowerCase()
    if (guessWord.length !== state.value.wordLength) return

    state.value.guesses.push({
      word: guessWord,
      colors,
      number: state.value.guesses.length + 1,
      userId: '',
    })

    // Update keyboard colors - only upgrade (gray -> yellow -> green)
    for (let i = 0; i < colors.length; i++) {
      const letter = guessWord[i].toUpperCase()
      const current = keyStates.value[letter]
      const priority: Record<string, number> = { gray: 0, yellow: 1, green: 2 }
      if (current === undefined || priority[colors[i]] > priority[current]) {
        keyStates.value[letter] = colors[i]
      }
    }

    currentRow.value = ''
  }

  function reset() {
    state.value = {
      wordLength: 5,
      maxGuesses: 6,
      wordBank: 'CET4',
      guesses: [],
      status: 'waiting',
    }
    currentRow.value = ''
    keyStates.value = {}
  }

  return { state, currentRow, keyStates, addLetter, removeLetter, submitGuess, reset }
}, {
  persist: {
    key: 'wordle_game_store',
    storage: localStorage,
    pick: ['state', 'currentRow', 'keyStates'],
  },
})