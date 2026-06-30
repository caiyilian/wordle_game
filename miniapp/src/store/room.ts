import { defineStore } from 'pinia'
import { ref } from 'vue'

interface RoomData {
  id: string
  code: string
  name: string
  word_bank: string
  word_length: number
  max_guesses: number
  max_players: number
  status: string
  created_by: string
}

export const useRoomStore = defineStore('room', () => {
  const roomCode = ref('')
  const roomId = ref('')
  const wordBank = ref('CET4')
  const wordLength = ref(5)
  const maxGuesses = ref(6)
  const maxPlayers = ref(8)
  const players = ref<string[]>([])
  const status = ref('waiting')
  const roomName = ref('')

  function setRoom(data: RoomData) {
    roomCode.value = data.code
    roomId.value = data.id
    wordBank.value = data.word_bank
    wordLength.value = data.word_length
    maxGuesses.value = data.max_guesses
    maxPlayers.value = data.max_players
    status.value = data.status
    roomName.value = data.name
  }

  function addPlayer(nickname: string) {
    if (!players.value.includes(nickname)) {
      players.value.push(nickname)
    }
  }

  function removePlayer(nickname: string) {
    players.value = players.value.filter(p => p !== nickname)
  }

  function setStatus(s: string) {
    status.value = s
  }

  function reset() {
    roomCode.value = ''
    roomId.value = ''
    players.value = []
    status.value = 'waiting'
    roomName.value = ''
  }

  return { roomCode, roomId, wordBank, wordLength, maxGuesses, maxPlayers, players, status, roomName, setRoom, addPlayer, removePlayer, setStatus, reset }
})
