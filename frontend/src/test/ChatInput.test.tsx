import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatInput } from '../components/ChatInput'

describe('ChatInput', () => {
  it('renders input and button', () => {
    const mockSubmit = vi.fn()
    render(<ChatInput onSubmit={mockSubmit} disabled={false} />)

    expect(screen.getByPlaceholderText('Ask about life insurance...')).toBeInTheDocument()
  })

  it('calls onSubmit when form is submitted', async () => {
    const user = userEvent.setup()
    const mockSubmit = vi.fn().mockResolvedValue(undefined)
    render(<ChatInput onSubmit={mockSubmit} disabled={false} />)

    const input = screen.getByPlaceholderText('Ask about life insurance...')
    await user.type(input, 'Hello world')
    await user.keyboard('{Enter}')

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith('Hello world')
    })
  })

  it('does not submit empty message', async () => {
    const user = userEvent.setup()
    const mockSubmit = vi.fn()
    render(<ChatInput onSubmit={mockSubmit} disabled={false} />)

    await user.keyboard('{Enter}')

    expect(mockSubmit).not.toHaveBeenCalled()
  })

  it('does not submit when disabled', async () => {
    const user = userEvent.setup()
    const mockSubmit = vi.fn()
    render(<ChatInput onSubmit={mockSubmit} disabled={true} />)

    const input = screen.getByPlaceholderText('Ask about life insurance...')
    await user.type(input, 'Hello')
    await user.keyboard('{Enter}')

    expect(mockSubmit).not.toHaveBeenCalled()
  })

  it('clears input after successful submission', async () => {
    const user = userEvent.setup()
    const mockSubmit = vi.fn().mockResolvedValue(undefined)
    render(<ChatInput onSubmit={mockSubmit} disabled={false} />)

    const input = screen.getByPlaceholderText('Ask about life insurance...')
    await user.type(input, 'Test message')
    await user.keyboard('{Enter}')

    await waitFor(() => {
      expect(input).toHaveValue('')
    })
  })
})