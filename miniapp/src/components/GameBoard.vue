<template>
  <scroll-view class="game-board" scroll-y :style="{ maxHeight: '60vh' }">
    <view class="board-container">
      <GameRow
        v-for="(row, rowIndex) in displayRows"
        :key="rowIndex"
        :letters="row.letters"
        :colors="row.colors"
      />
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import GameRow from './GameRow.vue'

interface Guess {
  word: string
  colors: ('green' | 'yellow' | 'gray')[]
}

interface Props {
  guesses: Guess[]
  currentRow: string
  wordLength: number
  maxGuesses: number
}

const props = defineProps<Props>()

const displayRows = computed(() => {
  const rows: { letters: string[]; colors: ('green' | 'yellow' | 'gray' | null)[] }[] = []
  
  // Add past guesses
  for (const guess of props.guesses) {
    rows.push({
      letters: guess.word.split(''),
      colors: guess.colors
    })
  }
  
  // Add current row being typed
  const currentLetters = props.currentRow.split('').map(l => l || '')
  while (currentLetters.length < props.wordLength) {
    currentLetters.push('')
  }
  rows.push({
    letters: currentLetters,
    colors: Array(props.wordLength).fill(null)
  })
  
  // Add empty rows for remaining guesses
  const remainingRows = props.maxGuesses - props.guesses.length - 1
  for (let i = 0; i < remainingRows; i++) {
    rows.push({
      letters: Array(props.wordLength).fill(''),
      colors: Array(props.wordLength).fill(null)
    })
  }
  
  return rows
})
</script>

<style scoped lang="scss">
.game-board {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 20rpx 0;
}

.board-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}
</style>