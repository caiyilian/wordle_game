export interface WSMessage<T = unknown> {
  type: string
  data: T
  timestamp: number
}

export interface GuessResultData {
  guess: string
  result: ('correct' | 'present' | 'absent')[]
  is_correct: boolean
  remaining_attempts: number
}

export interface GameOverData {
  won: boolean
  word: string
  winner_id?: number
  winner_nickname?: string
  score_changes: Record<number, number>
}

export interface GameStartData {
  word_length: number
  max_attempts: number
  players: PlayerInfo[]
}

export interface PlayerJoinedData {
  player: PlayerInfo
  players: PlayerInfo[]
}

export interface PlayerLeftData {
  player_id: number
  players: PlayerInfo[]
}

export interface ChatData {
  player_id: number
  player_nickname: string
  message: string
  timestamp: number
}

export interface ErrorData {
  code: number
  message: string
}

export interface PlayerInfo {
  id: number
  nickname: string
  avatar?: string
  is_creator: boolean
  is_ready: boolean
  score: number
}

export type WSMessageType =
  | 'guess_result'
  | 'game_over'
  | 'game_start'
  | 'player_joined'
  | 'player_left'
  | 'chat'
  | 'error'
  | 'ping'
  | 'pong'
  | 'join_room'
  | 'leave_room'
  | 'guess'
  | 'chat_message'
  | 'ready'
  | 'start_game'

export interface WSHandlers {
  onGuessResult?: (data: GuessResultData) => void
  onGameOver?: (data: GameOverData) => void
  onGameStart?: (data: GameStartData) => void
  onPlayerJoined?: (data: PlayerJoinedData) => void
  onPlayerLeft?: (data: PlayerLeftData) => void
  onChat?: (data: ChatData) => void
  onError?: (data: ErrorData) => void
  onConnected?: () => void
  onDisconnected?: (reason?: string) => void
}

const WS_BASE = 'ws://localhost:8000'
const HEARTBEAT_INTERVAL = 30000
const MAX_RECONNECT_DELAY = 8000
const INITIAL_RECONNECT_DELAY = 1000

export class WebSocketClient {
  private socket: UniApp.SocketTask | null = null
  private handlers: WSHandlers = {}
  private roomId: string = ''
  private token: string = ''
  private reconnectAttempts = 0
  private reconnectTimer: number | null = null
  private heartbeatTimer: number | null = null
  private isIntentionallyClosed = false
  private messageQueue: Array<{ type: string; data?: unknown }> = []

  connect(roomId: string, token: string, handlers: WSHandlers): Promise<void> {
    this.roomId = roomId
    this.token = token
    this.handlers = handlers
    this.isIntentionallyClosed = false
    this.reconnectAttempts = 0

    return new Promise((resolve, reject) => {
      this.createConnection()
        .then(resolve)
        .catch(reject)
    })
  }

  private createConnection(): Promise<void> {
    return new Promise((resolve, reject) => {
      const url = `${WS_BASE}/ws/room/${this.roomId}?token=${encodeURIComponent(this.token)}`

      this.socket = uni.connectSocket({
        url,
        header: {
          Authorization: `Bearer ${this.token}`,
        },
        success: () => {
          console.log('[WebSocket] Connection initiated')
        },
        fail: (err) => {
          console.error('[WebSocket] Connection failed:', err)
          this.scheduleReconnect()
          reject(new Error(err.errMsg || 'WebSocket connection failed'))
        },
      })

      this.socket.onOpen(() => {
        console.log('[WebSocket] Connected')
        this.reconnectAttempts = 0
        this.startHeartbeat()
        this.flushMessageQueue()
        this.handlers.onConnected?.()
        resolve()
      })

      this.socket.onMessage((res) => {
        this.handleMessage(res.data)
      })

      this.socket.onClose((res) => {
        console.log('[WebSocket] Closed:', res.code, res.reason)
        this.stopHeartbeat()
        if (!this.isIntentionallyClosed) {
          this.handlers.onDisconnected?.(res.reason)
          this.scheduleReconnect()
        } else {
          this.handlers.onDisconnected?.('Intentional disconnect')
        }
      })

      this.socket.onError((err) => {
        console.error('[WebSocket] Error:', err)
        this.handlers.onError?.({ code: -1, message: err.errMsg || 'WebSocket error' })
      })
    })
  }

  private handleMessage(data: string | ArrayBuffer): void {
    try {
      const message: WSMessage = JSON.parse(data as string)
      console.log('[WebSocket] Received:', message.type)

      switch (message.type) {
        case 'guess_result':
          this.handlers.onGuessResult?.(message.data as GuessResultData)
          break
        case 'game_over':
          this.handlers.onGameOver?.(message.data as GameOverData)
          break
        case 'game_start':
          this.handlers.onGameStart?.(message.data as GameStartData)
          break
        case 'player_joined':
          this.handlers.onPlayerJoined?.(message.data as PlayerJoinedData)
          break
        case 'player_left':
          this.handlers.onPlayerLeft?.(message.data as PlayerLeftData)
          break
        case 'chat':
          this.handlers.onChat?.(message.data as ChatData)
          break
        case 'error':
          this.handlers.onError?.(message.data as ErrorData)
          break
        case 'pong':
          break
        default:
          console.log('[WebSocket] Unknown message type:', message.type)
      }
    } catch (err) {
      console.error('[WebSocket] Failed to parse message:', err)
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat()
    this.heartbeatTimer = setInterval(() => {
      this.send('ping')
    }, HEARTBEAT_INTERVAL) as unknown as number
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  private scheduleReconnect(): void {
    if (this.isIntentionallyClosed) return

    const delay = Math.min(
      INITIAL_RECONNECT_DELAY * Math.pow(2, this.reconnectAttempts),
      MAX_RECONNECT_DELAY
    )

    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1})`)

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++
      this.createConnection().catch(() => {
        this.scheduleReconnect()
      })
    }, delay) as unknown as number
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.isConnected) {
      const msg = this.messageQueue.shift()
      if (msg) {
        this.sendRaw(msg.type, msg.data)
      }
    }
  }

  private sendRaw(type: string, data?: unknown): void {
    if (!this.socket || !this.isConnected) {
      this.messageQueue.push({ type, data })
      return
    }

    const message: WSMessage = {
      type,
      data: data ?? {},
      timestamp: Date.now(),
    }

    this.socket.send({
      data: JSON.stringify(message),
      fail: (err) => {
        console.error('[WebSocket] Send failed:', err)
        this.messageQueue.unshift({ type, data })
      },
    })
  }

  send(type: string, data?: unknown): void {
    this.sendRaw(type, data)
  }

  disconnect(): void {
    this.isIntentionallyClosed = true
    this.stopHeartbeat()

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.socket) {
      this.socket.close()
      this.socket = null
    }

    this.messageQueue = []
    this.reconnectAttempts = 0
  }

  get isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === 1
  }
}

export const wsClient = new WebSocketClient()