export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  intent?: string
  sources?: Array<{ text: string; score: number }>
}

export interface ChatRequest {
  session_id: string
  message: string
  context?: Record<string, unknown>
}

export interface ChatResponse {
  session_id: string
  message: string
  intent?: string
  sources?: Array<{ text: string; score: number }>
}

export interface Session {
  id: string
  created_at: string
  last_message_at: string
}