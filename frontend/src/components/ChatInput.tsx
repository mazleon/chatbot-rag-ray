import { useState, useRef, useEffect, type FormEvent, KeyboardEvent } from 'react'
import { Plus, Loader2, Mic, ArrowUp } from 'lucide-react'
import { clsx } from 'clsx'

interface ChatInputProps {
  onSubmit: (message: string) => Promise<void>
  disabled?: boolean
}

export function ChatInput({ onSubmit, disabled }: ChatInputProps) {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [input])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading || disabled) return

    setIsLoading(true)
    try {
      await onSubmit(input.trim())
      setInput('')
      textareaRef.current?.focus()
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="w-full flex flex-col items-center">
      <form onSubmit={handleSubmit} className="relative flex w-full max-w-3xl items-end gap-2 rounded-[24px] bg-[#2f2f2f] px-2 py-2 pr-3">
        <button
          type="button"
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-muted-foreground transition-colors hover:bg-white/10 hover:text-foreground ml-1 mb-[2px]"
        >
          <Plus className="h-5 w-5" />
        </button>
        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything"
            disabled={disabled || isLoading}
            rows={1}
            className="w-full resize-none bg-transparent py-[10px] px-0 text-[16px] leading-[1.5] placeholder:text-muted-foreground focus:outline-none disabled:opacity-50 text-foreground"
            style={{ minHeight: '44px', maxHeight: '200px' }}
          />
        </div>
        <div className="flex shrink-0 items-center gap-2 mb-[2px] pl-1">
          <button
            type="button"
            className="flex h-8 w-8 items-center justify-center rounded-full text-muted-foreground transition-colors hover:bg-white/10 hover:text-foreground"
          >
            <Mic className="h-4 w-4" />
          </button>
          <button
            type="submit"
            disabled={!input.trim() || isLoading || disabled}
            className={clsx(
              'flex h-8 w-8 items-center justify-center rounded-full transition-all active:scale-95 text-white',
              input.trim() && !isLoading && !disabled
                ? 'bg-primary'
                : 'bg-[#676767] text-[#171717]'
            )}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin text-white" />
            ) : (
              <ArrowUp className="h-5 w-5" />
            )}
          </button>
        </div>
      </form>
      <div className="mt-3 text-center text-[12px] text-muted-foreground">
        Ray Advertising can make mistakes. Check important info.
      </div>
    </div>
  )
}