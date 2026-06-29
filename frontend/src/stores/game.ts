import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { GuessResult, GameState } from '@/types/game'

export const useGameStore = defineStore('game', () => {
  const state = ref<GameState>({
    wordLength: 5,
    maxGuesses: 6,
    wordBank: 'CET4',
    guesses: [],
    status: 'waiting',
  })

  const currentRow = ref('')
  const keyStates = ref<Record<string, string>>({})

  function addLetter(letter: string) {
    if (currentRow.value.length < state.value.wordLength) {
      currentRow.value += letter
    }
  }

  function removeLetter() {
    currentRow.value = currentRow.value.slice(0, -1)
  }

  function submitGuess(colors: string[]) {
    state.value.guesses.push({
      word: currentRow.value.toLowerCase(),
      colors: colors as any,
      number: state.value.guesses.length + 1,
      userId: '',
    })
    currentRow.value = ''
    // Update key states
    const guess = currentRow.value || state.value.guesses[state.value.guesses.length - 1].word
    // Simplified key state update
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
})