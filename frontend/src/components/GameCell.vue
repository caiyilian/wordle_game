<template>
  <div
    class="cell w-14 h-14 sm:w-16 sm:h-16 border-2 flex items-center justify-center text-2xl font-bold rounded select-none"
    :class="[cellClasses, { revealing: revealing }]"
    :style="{ animationDelay: (revealing ? delay : 0) + 'ms' }"
  >
    <span class="cell-letter">{{ letter.toUpperCase() }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ColorResult } from '@/types/game'

const props = defineProps<{
  letter: string
  color: ColorResult | null
  delay?: number
  revealing?: boolean
}>()

const cellClasses = computed(() => {
  if (props.revealing && props.color === 'green') return 'bg-wordle-green text-white border-wordle-green flip-green'
  if (props.revealing && props.color === 'yellow') return 'bg-wordle-yellow text-white border-wordle-yellow flip-yellow'
  if (props.revealing && props.color === 'gray') return 'bg-wordle-gray text-white border-wordle-gray flip-gray'
  if (props.color === 'green') return 'bg-wordle-green text-white border-wordle-green'
  if (props.color === 'yellow') return 'bg-wordle-yellow text-white border-wordle-yellow'
  if (props.color === 'gray') return 'bg-wordle-gray text-white border-wordle-gray'
  if (props.letter) return 'border-gray-400 dark:border-gray-500 text-gray-800 dark:text-gray-200 bg-white dark:bg-gray-800'
  return 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800'
})
</script>

<style scoped>
.cell {
  perspective: 1000px;
}
.cell-letter {
  display: inline-block;
}
.revealing {
  animation: flip 0.4s ease-in-out forwards;
}
.revealing .cell-letter {
  animation: fadeColor 0.4s ease-in-out forwards;
}

@keyframes flip {
  0% { transform: rotateX(0deg); }
  49% { transform: rotateX(-90deg); }
  50% { transform: rotateX(-90deg); }
  100% { transform: rotateX(0deg); }
}

@keyframes fadeColor {
  0%, 49% { opacity: 0; }
  50% { opacity: 0; }
  100% { opacity: 1; }
}

/* Initial pop animation for non-revealing cells */
.cell:not(.revealing) {
  animation: pop 0.2s ease-out;
}
@keyframes pop {
  0% { transform: scale(0.8); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
</style>
