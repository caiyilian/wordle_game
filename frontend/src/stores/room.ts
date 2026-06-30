import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface RoomInfo {
  id: string
  code: string
  name: string
  wordBank: string
  wordLength: number
  status: string
  maxPlayers: number
  maxGuesses: number
  playerCount: number
}

export const useRoomStore = defineStore('room', () => {
  const currentRoom = ref<RoomInfo | null>(null)
  const players = ref<string[]>([])

  function setRoom(room: RoomInfo) {
    currentRoom.value = room
  }

  return { currentRoom, players, setRoom }
}, {
  persist: {
    key: 'wordle_room_store',
    storage: localStorage,
    pick: ['currentRoom'],
  },
})