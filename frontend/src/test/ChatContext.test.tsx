import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ChatProvider, useChat } from '../context/ChatContext'
import { ChatWindow } from '../components/ChatWindow'

const TestComponent = () => {
  const { sendMessage, state, currentSession } = useChat()
  return (
    <div>
      <button onClick={() => sendMessage('test')}>Send</button>
      <span data-testid="loading">{state.isLoading ? 'loading' : 'idle'}</span>
      <span data-testid="messages">{currentSession.messages.length}</span>
    </div>
  )
}

describe('ChatContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('provides initial state', () => {
    render(
      <ChatProvider>
        <TestComponent />
      </ChatProvider>
    )

    expect(screen.getByTestId('loading')).toHaveTextContent('idle')
    expect(screen.getByTestId('messages')).toHaveTextContent('0')
  })
})

describe('ChatWindow', () => {
  it('renders empty state', () => {
    render(
      <ChatProvider>
        <ChatWindow />
      </ChatProvider>
    )

    expect(screen.getByText('Secure your legacy.')).toBeInTheDocument()
  })

  it('renders header with correct title', () => {
    render(
      <ChatProvider>
        <ChatWindow />
      </ChatProvider>
    )

    expect(screen.getByText('Life Insurance Agent')).toBeInTheDocument()
  })
})