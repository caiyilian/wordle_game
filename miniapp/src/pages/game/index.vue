<template>
  <view class="container">
    <text class="room-title">Room: {{ roomCode }}</text>
    <view class="board">
      <view v-for="(row, ri) in displayRows" :key="ri" class="row">
        <view v-for="(cell, ci) in row" :key="ci" class="cell" :class="'color-' + (cell.color || 'empty')">
          <text>{{ cell.letter }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const roomCode = ref('')
const guesses = ref<any[]>([])
const currentRow = ref('')
const wordLength = ref(5)
const maxGuesses = ref(6)

const displayRows = computed(() => {
  const rows = []
  for (let i = 0; i < maxGuesses.value; i++) {
    if (i < guesses.value.length) {
      const g = guesses.value[i]
      rows.push(g.word.split('').map((l: string, j: number) => ({ letter: l, color: g.colors[j] })))
    } else if (i === guesses.value.length) {
      rows.push(currentRow.value.padEnd(wordLength.value, ' ').split('').map(l => ({ letter: l, color: null })))
    } else {
      rows.push(Array(wordLength.value).fill(null).map(() => ({ letter: '', color: null })))
    }
  }
  return rows
})

import { computed } from 'vue'

onMounted(() => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1] as any
  roomCode.value = page.$page?.options?.code || ''
})
</script>

<style scoped>
.container { padding: 20rpx; }
.room-title { font-size: 32rpx; font-weight: bold; text-align: center; margin-bottom: 40rpx; }
.board { display: flex; flex-direction: column; align-items: center; gap: 8rpx; }
.row { display: flex; gap: 8rpx; }
.cell { width: 80rpx; height: 80rpx; border: 2rpx solid #ddd; display: flex; align-items: center; justify-content: center; font-size: 36rpx; font-weight: bold; border-radius: 8rpx; }
.color-green { background: #86a373; color: white; border-color: #86a373; }
.color-yellow { background: #c6b66d; color: white; border-color: #c6b66d; }
.color-gray { background: #7b7b7c; color: white; border-color: #7b7b7c; }
.color-empty { background: white; }
</style>