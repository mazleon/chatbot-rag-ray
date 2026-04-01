import type { ChatRequest, ChatResponse } from '../types'

const API_BASE = '/api/v1'

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`
  
  console.log(`[API] ${options.method || 'GET'} ${url}`)
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    console.log(`[API] Response status: ${response.status}`)
    
    if (!response.ok) {
      let errorDetail = 'Unknown error'
      try {
        const errorData = await response.json()
        errorDetail = errorData.detail || JSON.stringify(errorData)
      } catch {
        errorDetail = await response.text() || `HTTP ${response.status}`
      }
      console.error(`[API] Error response:`, errorDetail)
      throw new ApiError(response.status, errorDetail)
    }

    const data = await response.json()
    console.log(`[API] Response received:`, data.message?.substring(0, 50) || 'OK')
    return data
  } catch (err) {
    if (err instanceof ApiError) throw err
    console.error(`[API] Network error:`, err)
    throw new ApiError(0, err instanceof Error ? err.message : 'Network request failed')
  }
}

export const api = {
  async chat(chatRequest: ChatRequest): Promise<ChatResponse> {
    console.log('[API] Sending chat request:', chatRequest)
    return request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(chatRequest),
    })
  },

  async health() {
    return request<{ status: string; version: string; environment: string }>('/health')
  },

  async getSessionHistory(sessionId: string) {
    return request<{ session_id: string; messages: unknown[]; message_count: number }>(
      `/sessions/${sessionId}/history`
    )
  },

  async deleteSession(sessionId: string) {
    return request<{ status: string; session_id: string }>(`/sessions/${sessionId}`, {
      method: 'DELETE',
    })
  },

  async ingest(documents: string[]) {
    return request<{ status: string; chunks_created: number; message: string }>('/ingest', {
      method: 'POST',
      body: JSON.stringify({ documents }),
    })
  },

  async uploadDocument(file: File) {
    const base64Content = await new Promise<string>((resolve) => {
      const reader = new FileReader()
      reader.onload = () => {
        const result = reader.result as string
        const base64 = result.split(',')[1]
        resolve(base64)
      }
      reader.readAsDataURL(file)
    })

    return request<{ status: string; chunks_created: number; message: string }>('/upload', {
      method: 'POST',
      body: JSON.stringify({
        filename: file.name,
        content: base64Content,
      }),
    })
  },
}

export { ApiError }