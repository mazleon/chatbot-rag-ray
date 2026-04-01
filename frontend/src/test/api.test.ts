import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { api, ApiError } from '../services/api'

declare global {
  function fetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response>
}

describe('API Service', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  describe('chat', () => {
    it('makes successful request', async () => {
      const mockResponse = {
        session_id: 'test-123',
        message: 'Hello from API',
        intent: 'greeting',
      }

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      } as Response)

      const result = await api.chat({
        session_id: 'test-123',
        message: 'Hello',
      })

      expect(result).toEqual(mockResponse)
      expect(fetch).toHaveBeenCalledWith(
        '/api/v1/chat',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ session_id: 'test-123', message: 'Hello' }),
        })
      )
    })

    it('throws ApiError on failure', async () => {
      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Internal error' }),
      } as Response)

      await expect(
        api.chat({ session_id: 'test', message: 'test' })
      ).rejects.toThrow(ApiError)
    })
  })

  describe('health', () => {
    it('returns health status', async () => {
      const mockResponse = {
        status: 'healthy',
        version: '1.0.0',
        environment: 'development',
      }

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      } as Response)

      const result = await api.health()

      expect(result).toEqual(mockResponse)
    })
  })

  describe('ApiError', () => {
    it('creates error with status and message', () => {
      const error = new ApiError(404, 'Not found')
      
      expect(error.status).toBe(404)
      expect(error.message).toBe('Not found')
      expect(error.name).toBe('ApiError')
    })
  })
})