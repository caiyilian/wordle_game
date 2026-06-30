<template>
  <div class="space-y-1.5">
    <GameRow
      v-for="row in maxGuesses"
      :key="row"
      :word-length="wordLength"
      :letters="getLetters(row)"
      :colors="getColors(row)"
      :is-current="isCurrentRow(row)"
      :revealing="revealingRow === row"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useGameStore } from '@/stores/game'
import type { ColorResult } from '@/types/game'
import GameRow from './GameRow.vue'

const gameStore = useGameStore()

const wordLength = computed(() => gameStore.state.wordLength)
const maxGuesses = computed(() => gameStore.state.maxGuesses)
const revealingRow = ref(0)

// Detect new guess → trigger reveal animation
watch(() => gameStore.state.guesses.length, (newLen, oldLen) => {
  if (newLen > (oldLen || 0)) {
    revealingRow.value = newLen
    // Clear after animation completes (delay per cell × wordLength)
    setTimeout(() => { revealingRow.value = 0 }, gameStore.state.wordLength * 300 + 400)
  }
})

function getLetters(rowIdx: number): string[] {
  const idx = rowIdx - 1
  const guess = gameStore.state.guesses[idx]
  if (guess) return guess.word.split('')
  if (idx === gameStore.state.guesses.length) return gameStore.currentRow.split('')
  return []
}

function getColors(rowIdx: number): ColorResult[] | null {
  const idx = rowIdx - 1
  const guess = gameStore.state.guesses[idx]
  if (guess) return guess.colors
  return null
}

function isCurrentRow(rowIdx: number): boolean {
  return rowIdx - 1 === gameStore.state.guesses.length
}
</script>