<template>
  <div
    class="cell w-14 h-14 sm:w-16 sm:h-16 border-2 flex items-center justify-center text-2xl font-bold rounded select-none transition-colors duration-300"
    :class="cellClasses"
    :style="{ animationDelay: delay + 'ms' }"
  >
    {{ letter.toUpperCase() }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ColorResult } from '@/types/game'

const props = defineProps<{
  letter: string
  color: ColorResult | null
  delay?: number
}>()

const cellClasses = computed(() => {
  if (props.color === 'green') return 'bg-wordle-green text-white border-wordle-green'
  if (props.color === 'yellow') return 'bg-wordle-yellow text-white border-wordle-yellow'
  if (props.color === 'gray') return 'bg-wordle-gray text-white border-wordle-gray'
  if (props.letter) return 'border-gray-400 dark:border-gray-500 text-gray-800 dark:text-gray-200 bg-white dark:bg-gray-800'
  return 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800'
})
</script>

<style scoped>
.cell {
  animation: pop 0.2s ease-out;
}
@keyframes pop {
  0% { transform: scale(0.8); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
</style>
