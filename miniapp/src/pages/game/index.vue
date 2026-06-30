<template>
  <view class="container">
    <view class="header">
      <text class="room-title">Room: {{ roomStore.roomCode }}</text>
      <view class="status-row">
        <text class="players">Players: {{ roomStore.players.join(', ') || 'Waiting...' }}</text>
        <text v-if="wsConnected" class="connected">● Connected</text>
        <text v-else class="disconnected">● Disconnected</text>
      </view>
    </view>

    <!-- Game Board -->
    <GameBoard
      :guesses="gameStore.guesses"
      :current-row="gameStore.currentRow"
      :word-length="gameStore.wordLength"
      :max-guesses="gameStore.maxGuesses"
    />

    <!-- Keyboard -->
    <VirtualKeyboard
      :keyboard-colors="gameStore.keyboardColors"
      @keypress="onKey"
    />

    <!-- Chat -->
    <ChatPanel
      :messages="chatMessages"
      :can-send="wsConnected"
      @send="onChatSend"
    />
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { useRoomStore } from '@/store/room'
import { useGameStore } from '@/store/game'
import { wsClient, type WSMessageHandlers } from '@/api/websocket'
import GameBoard from '@/components/GameBoard.vue'
import VirtualKeyboard from '@/components/VirtualKeyboard.vue'
import ChatPanel from '@/components/ChatPanel.vue'

const userStore = useUserStore()
const roomStore = useRoomStore()
const gameStore = useGameStore()

const wsConnected = ref(false)
const chatMessages = ref<Array<{id: number; type?: string; content: string; nickname?: string}>>([])

function addChatMsg(type: string, content: string, nickname?: string) {
  chatMessages.value.push({ id: Date.now(), type, content, nickname })
}

const handlers: WSMessageHandlers = {
  onGuessResult(data) {
    gameStore.submitGuess(data.colors, data.user_id)
    addChatMsg('system', (data.nickname || 'Someone') + ' guessed ' + data.word)
  },
  onGameOver(data) {
    gameStore.endGame(data)
    addChatMsg('system', 'Game over! Answer: ' + data.answer + '. Winner: ' + (data.winner_nickname || 'Nobody'))
  },
  onGameStart(data) {
    gameStore.startGame(data)
    addChatMsg('system', 'Game started! Guess the ' + data.word_length + '-letter word!')
  },
  onPlayerJoined(data) {
    roomStore.addPlayer(data.nickname)
    addChatMsg('system', data.nickname + ' joined')
  },
  onPlayerLeft(data) {
    roomStore.removePlayer(data.nickname)
    addChatMsg('system', data.nickname + ' left')
  },
  onChat(data) {
    addChatMsg('chat', data.message, data.nickname)
  },
  onConnected() {
    wsConnected.value = true
  },
  onDisconnected() {
    wsConnected.value = false
  },
  onError(data) {
    addChatMsg('system', 'Error: ' + (data.message || 'Unknown'))
  },
}

let roomCode = ''

onLoad((options) => {
  roomCode = options?.code || ''
  roomStore.roomCode = roomCode

  // Get room info
  const token = userStore.token
  if (!token || !roomCode) {
    uni.navigateTo({ url: '/pages/index/index' })
    return
  }

  uni.request({
    url: 'http://localhost:8000/api/rooms/' + roomCode,
    header: { Authorization: 'Bearer ' + token },
    success(res: any) {
      if (res.statusCode === 200) {
        const data = res.data
        roomStore.setRoom(data)
        gameStore.wordLength = data.word_length
        gameStore.maxGuesses = data.max_guesses
      }
    },
    complete() {
      // Connect WebSocket
      wsClient.connect(roomCode, token, handlers)
    }
  })
})

onUnmounted(() => {
  wsClient.disconnect()
})

function onKey(key: string) {
  if (!wsConnected.value) return
  if (key === 'ENTER') {
    if (gameStore.currentRow.length === gameStore.wordLength) {
      wsClient.send('guess', { word: gameStore.currentRow })
    }
  } else if (key === 'BACKSPACE') {
    gameStore.removeLetter()
  } else {
    gameStore.addLetter(key)
  }
}

function onChatSend(text: string) {
  wsClient.send('chat', { message: text })
}
</script>

<style scoped>
.container {
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.header {
  text-align: center;
}
.room-title {
  font-size: 32rpx;
  font-weight: bold;
}
.status-row {
  display: flex;
  justify-content: center;
  gap: 16rpx;
  font-size: 24rpx;
  margin-top: 8rpx;
}
.connected { color: #22c55e; }
.disconnected { color: #ef4444; }
.players { color: #6b7280; }
</style>
