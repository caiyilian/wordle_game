const API_BASE = 'http://localhost:8000'

const TOKEN_KEY = 'token'

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface LoginResponse {
  token: string
  user: UserInfo
}

export interface UserInfo {
  id: number
  nickname: string
  avatar?: string
  created_at: string
}

export interface RoomData {
  room_code: string
  word_length: number
  max_players: number
  status: 'waiting' | 'playing' | 'finished'
  creator_id: number
  players: PlayerInfo[]
  created_at: string
}

export interface PlayerInfo {
  id: number
  nickname: string
  avatar?: string
  is_creator: boolean
  is_ready: boolean
  score: number
}

export interface LeaderboardEntry {
  rank: number
  user_id: number
  nickname: string
  avatar?: string
  score: number
  games_played: number
  win_rate: number
}

export interface UserStats {
  user_id: number
  nickname: string
  total_games: number
  wins: number
  win_rate: number
  total_score: number
  best_streak: number
  current_streak: number
}

export interface RecentGame {
  id: number
  room_code: string
  word: string
  word_length: number
  guesses: number
  won: boolean
  score: number
  created_at: string
}

export interface CreateRoomData {
  word_length?: number
  max_players?: number
}

export interface JoinRoomData {
  room_code: string
}

export interface LoginData {
  nickname: string
  password: string
}

export interface RegisterData {
  nickname: string
  password: string
}

export interface LeaderboardType {
  type?: 'score' | 'win_rate' | 'streak'
}

function getToken(): string | null {
  return uni.getStorageSync(TOKEN_KEY)
}

function setToken(token: string): void {
  uni.setStorageSync(TOKEN_KEY, token)
}

function removeToken(): void {
  uni.removeStorageSync(TOKEN_KEY)
}

async function request<T = unknown>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  url: string,
  data?: unknown,
  params?: Record<string, unknown>
): Promise<ApiResponse<T>> {
  const token = getToken()
  const header: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (token) {
    header.Authorization = `Bearer ${token}`
  }

  const queryString = params
    ? '?' + new URLSearchParams(params as Record<string, string>).toString()
    : ''

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}${url}${queryString}`,
      method,
      header,
      data,
      dataType: 'json',
      success: (res) => {
        const response = res.data as ApiResponse<T>
        if (res.statusCode >= 200 && res.statusCode < 300) {
          if (response.code === 0 || response.code === 200) {
            resolve(response)
          } else {
            if (response.code === 401) {
              removeToken()
              uni.navigateTo({ url: '/pages/login/login' })
            }
            reject(new Error(response.message || 'Request failed'))
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${res.errMsg}`))
        }
      },
      fail: (err) => {
        reject(new Error(err.errMsg || 'Network error'))
      },
    })
  })
}

export async function get<T = unknown>(url: string, params?: Record<string, unknown>): Promise<ApiResponse<T>> {
  return request('GET', url, undefined, params)
}

export async function post<T = unknown>(url: string, data?: unknown): Promise<ApiResponse<T>> {
  return request('POST', url, data)
}

export async function put<T = unknown>(url: string, data?: unknown): Promise<ApiResponse<T>> {
  return request('PUT', url, data)
}

export async function del<T = unknown>(url: string): Promise<ApiResponse<T>> {
  return request('DELETE', url)
}

export async function login(nickname: string, password: string): Promise<ApiResponse<LoginResponse>> {
  const res = await post<LoginResponse>('/api/auth/login', { nickname, password })
  if (res.data?.token) {
    setToken(res.data.token)
  }
  return res
}

export async function register(nickname: string, password: string): Promise<ApiResponse<LoginResponse>> {
  const res = await post<LoginResponse>('/api/auth/register', { nickname, password })
  if (res.data?.token) {
    setToken(res.data.token)
  }
  return res
}

export async function logout(): Promise<ApiResponse<null>> {
  const res = await post<null>('/api/auth/logout')
  removeToken()
  return res
}

export async function createRoom(data: CreateRoomData): Promise<ApiResponse<RoomData>> {
  return post<RoomData>('/api/rooms', data)
}

export async function joinRoom(roomCode: string): Promise<ApiResponse<RoomData>> {
  return post<RoomData>('/api/rooms/join', { room_code: roomCode })
}

export async function getRoomInfo(roomCode: string): Promise<ApiResponse<RoomData>> {
  return get<RoomData>(`/api/rooms/${roomCode}`)
}

export async function getLeaderboard(type?: LeaderboardType['type']): Promise<ApiResponse<LeaderboardEntry[]>> {
  return get<LeaderboardEntry[]>('/api/leaderboard', { type })
}

export async function getUserStats(): Promise<ApiResponse<UserStats>> {
  return get<UserStats>('/api/user/stats')
}

export async function getRecentGames(): Promise<ApiResponse<RecentGame[]>> {
  return get<RecentGame[]>('/api/user/games/recent')
}

export function getStoredToken(): string | null {
  return getToken()
}

export function clearToken(): void {
  removeToken()
}