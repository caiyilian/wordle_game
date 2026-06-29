import { ref, onUnmounted } from 'vue'

interface WSListeners {
  onGuessResult?: (data: any) => void
  onGameOver?: (data: any) => void
  onChat?: (data: any) => void
  onPlayerJoined?: (data: any) => void
  onPlayerLeft?: (data: any) => void
  onGameStart?: (data: any) => void
  onHint?: (data: any) => void
  onPong?: () => void
  onError?: (data: any) => void
}

export function useWebSocket(roomId: string, token: string, listeners: WSListeners = {}) {
  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let heartbeatTimer: ReturnType<typeof setTimeout> | null = null

  function connect() {
    const wsUrl = `ws://localhost:8000/ws/${roomId}?token=${token}`
    const socket = new WebSocket(wsUrl)
    
    socket.onopen = () => {
      connected.value = true
      startHeartbeat()
    }
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleEvent(data)
    }
    
    socket.onclose = () => {
      connected.value = false
      stopHeartbeat()
      scheduleReconnect()
    }
    
    socket.onerror = () => {
      connected.value = false
    }
    
    ws.value = socket
  }

  function handleEvent(data: any) {
    switch (data.type) {
      case 'guess_result': listeners.onGuessResult?.(data); break
      case 'game_over': listeners.onGameOver?.(data); break
      case 'chat': listeners.onChat?.(data); break
      case 'player_joined': listeners.onPlayerJoined?.(data); break
      case 'player_left': listeners.onPlayerLeft?.(data); break
      case 'game_start': listeners.onGameStart?.(data); break
      case 'hint': listeners.onHint?.(data); break
      case 'pong': listeners.onPong?.(); break
      case 'error': listeners.onError?.(data); break
    }
  }

  function send(type: string, payload: any = {}) {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify({ type, ...payload }))
    }
  }

  function startHeartbeat() {
    heartbeatTimer = setInterval(() => {
      send('ping')
    }, 30000)
  }

  function stopHeartbeat() {
    if (heartbeatTimer) clearInterval(heartbeatTimer)
  }

  function scheduleReconnect() {
    if (reconnectTimer) return
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      connect()
    }, 3000)
  }

  function disconnect() {
    stopHeartbeat()
    if (reconnectTimer) clearTimeout(reconnectTimer)
    ws.value?.close()
    ws.value = null
    connected.value = false
  }

  onUnmounted(disconnect)

  return { connected, connect, disconnect, send }
}