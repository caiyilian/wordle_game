<template>
  <view class="game-cell" :class="colorClass" :style="cellStyle">
    <view class="cell-inner" :class="flipClass">
      <text class="letter">{{ letter }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
interface Props {
  letter: string
  color: 'green' | 'yellow' | 'gray' | null
}

const props = defineProps<Props>()

const colorClass = computed(() => {
  if (!props.color) return 'empty'
  return props.color
})

const flipClass = computed(() => {
  if (!props.color) return ''
  return 'flip'
})

const cellStyle = computed(() => {
  const colors: Record<string, string> = {
    green: '#86a373',
    yellow: '#c6b66d',
    gray: '#7b7b7c',
    empty: 'transparent'
  }
  const bgColor = props.color ? colors[props.color] : colors.empty
  const borderColor = props.color ? 'transparent' : '#ddd'
  return {
    backgroundColor: bgColor,
    borderColor: borderColor
  } as Record<string, string>
})
</script>

<style scoped lang="scss">
.game-cell {
  width: 80rpx;
  height: 80rpx;
  border: 2rpx solid #ddd;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 4rpx;
  perspective: 800rpx;
  background-color: white;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.game-cell.empty {
  background-color: white;
  border-color: #ddd;
}

.game-cell.green {
  background-color: #86a373;
  border-color: transparent;
}

.game-cell.yellow {
  background-color: #c6b66d;
  border-color: transparent;
}

.game-cell.gray {
  background-color: #7b7b7c;
  border-color: transparent;
}

.cell-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.cell-inner.flip {
  animation: flip 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.letter {
  font-size: 36rpx;
  font-weight: 600;
  color: white;
  text-transform: uppercase;
  backface-visibility: hidden;
}

@keyframes flip {
  0% {
    transform: rotateX(0deg);
  }
  50% {
    transform: rotateX(-90deg);
  }
  100% {
    transform: rotateX(0deg);
  }
}
</style>