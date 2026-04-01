import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MessageBubble } from '../components/MessageBubble'

describe('MessageBubble', () => {
  it('renders user message correctly', () => {
    render(
      <MessageBubble
        message={{
          id: '1',
          role: 'user',
          content: 'Hello AI',
          timestamp: new Date().toISOString(),
        }}
      />
    )

    expect(screen.getByText('Hello AI')).toBeInTheDocument()
    expect(screen.getByText('Y')).toBeInTheDocument()
  })

  it('renders assistant message correctly', () => {
    render(
      <MessageBubble
        message={{
          id: '2',
          role: 'assistant',
          content: 'Hello human!',
          timestamp: new Date().toISOString(),
          intent: 'greeting',
        }}
      />
    )

    expect(screen.getByText('Hello human!')).toBeInTheDocument()
    expect(screen.getByText('AI')).toBeInTheDocument()
    expect(screen.getByText('Intent: greeting')).toBeInTheDocument()
  })

  it('does not show intent for user messages', () => {
    render(
      <MessageBubble
        message={{
          id: '3',
          role: 'user',
          content: 'What is term insurance?',
          timestamp: new Date().toISOString(),
          intent: 'policy_info',
        }}
      />
    )

    expect(screen.queryByText(/Intent:/)).not.toBeInTheDocument()
  })
})