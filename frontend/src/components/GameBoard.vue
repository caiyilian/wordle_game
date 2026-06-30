<template>
  <div class="space-y-1.5">
    <GameRow
      v-for="row in maxGuesses"
      :key="row"
      :word-length="wordLength"
      :letters="getLetters(row)"
      :colors="getColors(row)"
      :is-current="isCurrentRow(row)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useGameStore } from '@/stores/game'
import type { ColorResult } from '@/types/game'
import GameRow from './GameRow.vue'

const gameStore = useGameStore()

const wordLength = computed(() => gameStore.state.wordLength)
const maxGuesses = computed(() => gameStore.state.maxGuesses)

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