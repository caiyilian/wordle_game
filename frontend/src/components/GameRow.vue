<template>
  <div class="flex gap-1.5 justify-center">
    <GameCell
      v-for="i in wordLength"
      :key="i"
      :letter="letters[i - 1] || ''"
      :color="(colors && colors[i - 1]) || null"
      :delay="isCurrent ? 0 : (i - 1) * 150"
    />
  </div>
</template>

<script setup lang="ts">
import type { ColorResult } from '@/types/game'

defineProps<{
  wordLength: number
  letters: string[]
  colors?: ColorResult[] | null
  isCurrent?: boolean
}>()
</script>