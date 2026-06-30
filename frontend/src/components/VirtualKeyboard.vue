<template>
  <div class="w-full max-w-lg mx-auto select-none">
    <div v-for="(row, ri) in KEYBOARD_ROWS" :key="ri" class="flex justify-center gap-1 mb-1">
      <button
        v-for="key in row"
        :key="key"
        class="key font-semibold rounded"
        :class="keyClass(key)"
        @click="handleClick(key)"
      >
        <span v-if="key === 'BACKSPACE'" class="text-sm">⌫</span>
        <span v-else-if="key === 'ENTER'" class="text-xs">ENTER</span>
        <span v-else>{{ key }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useGameStore } from '@/stores/game'
import { useKeyboard } from '@/composables/useKeyboard'
import { KEYBOARD_ROWS } from '@/utils/constants'

const emit = defineEmits<{
  (e: 'letter', key: string): void
  (e: 'enter'): void
  (e: 'backspace'): void
}>()

const gameStore = useGameStore()

function handleClick(key: string) {
  if (key === 'ENTER') emit('enter')
  else if (key === 'BACKSPACE') emit('backspace')
  else emit('letter', key)
}

function keyClass(key: string): string {
  const base = 'h-12 sm:h-14 px-1 sm:px-3 text-lg transition-colors duration-200 active:scale-95'
  if (key === 'ENTER' || key === 'BACKSPACE') {
    return base + ' flex-1 max-w-[3.5rem] sm:max-w-[4rem] bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-400 dark:hover:bg-gray-500'
  }
  const color = gameStore.keyStates[key]
  if (color === 'green') return base + ' w-8 sm:w-10 bg-wordle-green text-white'
  if (color === 'yellow') return base + ' w-8 sm:w-10 bg-wordle-yellow text-white'
  if (color === 'gray') return base + ' w-8 sm:w-10 bg-wordle-gray text-white'
  return base + ' w-8 sm:w-10 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-500'
}

useKeyboard((key: string) => { handleClick(key) })
</script>

<style scoped>
.key {
  touch-action: manipulation;
}
</style>
