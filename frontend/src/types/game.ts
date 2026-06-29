export type ColorResult = 'green' | 'yellow' | 'gray'

export interface GuessResult {
  word: string
  colors: ColorResult[]
  number: number
  userId: string
}

export interface GameState {
  wordLength: number
  maxGuesses: number
  wordBank: string
  guesses: GuessResult[]
  status: 'waiting' | 'playing' | 'finished'
  answer?: string
  meaning?: string
  winnerId?: string
}

export interface RoomState {
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

export interface ChatMessage {
  userId: string
  nickname?: string
  message: string
  timestamp?: string
}