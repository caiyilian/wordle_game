<template>
  <view class="game-row">
    <GameCell
      v-for="(letter, index) in letters"
      :key="index"
      :letter="letter"
      :color="colors ? colors[index] : null"
    />
  </view>
</template>

<script setup lang="ts">
import GameCell from './GameCell.vue'

interface Props {
  letters: string[]
  colors: ('green' | 'yellow' | 'gray' | null)[] | null
}

defineProps<Props>()
</script>

<style scoped lang="scss">
.game-row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}
</style>