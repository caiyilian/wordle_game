<template>
  <view class="chat-panel">
    <scroll-view class="chat-messages" scroll-y :scroll-into-view="scrollTarget" :style="{ maxHeight: '40vh' }">
      <view v-for="(msg, i) in messages" :key="msg.id || i" :id="'msg-' + i" class="chat-msg" :class="'msg-' + (msg.type || 'chat')">
        <text v-if="msg.nickname" class="msg-nickname">{{ msg.nickname }}:</text>
        <text class="msg-content">{{ msg.content }}</text>
      </view>
    </scroll-view>
    <view class="chat-input-row">
      <input v-model="inputText" class="chat-input" :disabled="!canSend" placeholder="Type a message..." @confirm="sendMsg" />
      <button class="chat-send-btn" :disabled="!inputText.trim() || !canSend" @click="sendMsg">Send</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

interface ChatMessage {
  id?: number
  type?: string
  content: string
  nickname?: string
  userId?: string
}

const props = defineProps<{
  messages: ChatMessage[]
  canSend: boolean
}>()

const emit = defineEmits<{
  (e: 'send', text: string): void
}>()

const inputText = ref('')
const scrollTarget = ref('')

function sendMsg() {
  const text = inputText.value.trim()
  if (!text || !props.canSend) return
  emit('send', text)
  inputText.value = ''
  nextTick(() => {
    scrollTarget.value = 'msg-' + (props.messages.length - 1)
  })
}
</script>

<style scoped lang="scss">
.chat-panel {
  display: flex;
  flex-direction: column;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  overflow: hidden;
  background: white;
}
.chat-messages {
  flex: 1;
  padding: 16rpx;
}
.chat-msg {
  padding: 6rpx 0;
  font-size: 26rpx;
  line-height: 1.4;
}
.msg-system {
  color: #9ca3af;
  font-style: italic;
}
.msg-chat {
  color: #374151;
}
.msg-nickname {
  font-weight: bold;
  color: #4a90d9;
  margin-right: 8rpx;
}
.chat-input-row {
  display: flex;
  border-top: 2rpx solid #e5e7eb;
  padding: 10rpx;
  gap: 10rpx;
}
.chat-input {
  flex: 1;
  height: 64rpx;
  border: 2rpx solid #d1d5db;
  border-radius: 12rpx;
  padding: 0 16rpx;
  font-size: 26rpx;
}
.chat-send-btn {
  height: 64rpx;
  background: #4a90d9;
  color: white;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 26rpx;
  display: flex;
  align-items: center;
}
</style>
