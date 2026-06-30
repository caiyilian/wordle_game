<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="$emit('close')">
      <div class="modal bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 max-w-sm w-full mx-4 text-center"
           :class="isWin ? 'ring-2 ring-wordle-green' : 'ring-2 ring-wordle-gray'">
        <!-- Emoji -->
        <div class="text-5xl mb-4">{{ isWin ? '🎉' : '😞' }}</div>

        <!-- Title -->
        <h2 class="text-2xl font-bold mb-2 text-gray-800 dark:text-gray-100">
          {{ isWin ? 'Congratulations!' : 'Game Over' }}
        </h2>

        <!-- Answer -->
        <div class="mb-4">
          <p class="text-sm text-gray-500 mb-1">The word was</p>
          <p class="text-3xl font-bold tracking-wider uppercase text-gray-800 dark:text-gray-100">{{ answer }}</p>
          <p v-if="meaning" class="text-sm text-gray-500 mt-1">{{ meaning }}</p>
        </div>

        <!-- Stats -->
        <div class="flex justify-center gap-6 mb-6">
          <div class="text-center">
            <p class="text-2xl font-bold text-gray-800 dark:text-gray-100">{{ guessCount }}</p>
            <p class="text-xs text-gray-500">Guesses</p>
          </div>
          <div class="text-center" v-if="isWin">
            <p class="text-2xl font-bold text-wordle-green">{{ isPerfect ? '1' : guessCount }}</p>
            <p class="text-xs text-gray-500">Attempts</p>
          </div>
        </div>

        <!-- Guess grid mini -->
        <div class="flex flex-col items-center gap-1 mb-6">
          <div v-for="g in miniGuesses" :key="g.number" class="flex gap-1">
            <div v-for="(c, i) in g.colors" :key="i"
                 class="w-4 h-4 rounded-sm"
                 :class="colorClass(c)"></div>
          </div>
        </div>

        <!-- Buttons -->
        <div class="flex gap-3">
          <button @click="$emit('close')"
                  class="flex-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 py-2.5 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600">
            Close
          </button>
          <button @click="$emit('playAgain')"
                  class="flex-1 bg-green-500 text-white py-2.5 rounded-lg font-medium hover:bg-green-600">
            Play Again
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import type { ColorResult } from '@/types/game'

const props = defineProps<{
  isWin: boolean
  answer: string
  meaning?: string
  guessCount: number
  guesses: Array<{ word: string; colors: ColorResult[]; number: number }>
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'playAgain'): void
}>()

const isPerfect = computed(() => props.guessCount === 1)

const miniGuesses = computed(() => props.guesses.slice(0, 6))

function colorClass(c: ColorResult): string {
  if (c === 'green') return 'bg-wordle-green'
  if (c === 'yellow') return 'bg-wordle-yellow'
  return 'bg-wordle-gray'
}

onMounted(() => {
  if (props.isWin) {
    import('canvas-confetti').then(({ default: confetti }) => {
      confetti({
        particleCount: 150,
        spread: 80,
        origin: { y: 0.6 },
      })
    })
  }
})
</script>

<style scoped>
.modal {
  animation: modalIn 0.3s ease-out;
}
@keyframes modalIn {
  0% { transform: scale(0.8); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
</style>