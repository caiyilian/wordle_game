<template>
  <view class="keyboard">
    <view v-for="(row, ri) in keys" :key="ri" class="keyboard-row">
      <view
        v-for="key in row"
        :key="key"
        class="key"
        :class="[
          key === 'ENTER' || key === 'BACKSPACE' ? 'key-special' : '',
          keyboardColors[key.toLowerCase()] ? 'key-' + keyboardColors[key.toLowerCase()] : ''
        ]"
        @click="$emit('keypress', key)"
      >
        <text v-if="key === 'BACKSPACE'">⌫</text>
        <text v-else-if="key === 'ENTER'">↵</text>
        <text v-else>{{ key }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
defineProps<{
  keyboardColors: Record<string, string>
  disabled?: boolean
}>()

defineEmits<{
  (e: 'keypress', key: string): void
}>()

const keys = [
  ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
  ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
  ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'BACKSPACE'],
]
</script>

<style scoped lang="scss">
.keyboard {
  width: 100%;
  max-width: 600rpx;
  margin: 0 auto;
  padding: 10rpx 0;
}
.keyboard-row {
  display: flex;
  justify-content: center;
  gap: 6rpx;
  margin-bottom: 6rpx;
}
.key {
  min-width: 50rpx;
  height: 64rpx;
  background: #d3d6da;
  border-radius: 6rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: bold;
  padding: 0 8rpx;
  color: #1a1a1a;
}
.key-special {
  min-width: 72rpx;
  font-size: 20rpx;
  background: #818384;
  color: white;
}
.key-green {
  background: #86a373 !important;
  color: white !important;
}
.key-yellow {
  background: #c6b66d !important;
  color: white !important;
}
.key-gray {
  background: #7b7b7c !important;
  color: white !important;
}
</style>
