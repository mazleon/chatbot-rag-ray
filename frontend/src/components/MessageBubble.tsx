import { clsx } from 'clsx'
import type { Message } from '../types'
import { Streamdown } from 'streamdown'
import { code } from '@streamdown/code'
import { Zap, Copy, Check, Terminal } from 'lucide-react'
import { useState } from 'react'

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const CodeBlock = ({ node, inline, className, children, ...props }: any) => {
    const match = /language-(\w+)/.exec(className || '')
    const lang = match ? match[1] : ''
    
    if (inline) {
      return (
        <code className="bg-white/5 rounded-md px-1.5 py-0.5 text-pink-400 font-mono text-[0.9em]" {...props}>
          {children}
        </code>
      )
    }

    return (
      <div className="group relative my-6 rounded-xl overflow-hidden border border-white/10 bg-[#0d1117] shadow-2xl">
        <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/10">
          <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground uppercase tracking-wider">
            <Terminal className="h-3.5 w-3.5" />
            {lang || 'code'}
          </div>
          <button 
            onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
            className="p-1 hover:bg-white/10 rounded-md transition-colors text-muted-foreground hover:text-foreground"
          >
            <Copy className="h-3.5 w-3.5" />
          </button>
        </div>
        <pre className="p-4 overflow-x-auto text-[13px] leading-relaxed scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
          <code className={clsx(className, "font-mono")}>
            {children}
          </code>
        </pre>
      </div>
    )
  }

  return (
    <div className={clsx('group flex w-full animate-fade-in-up', isUser ? 'justify-end' : 'justify-start')}>
      {isUser ? (
        <div className="bg-[#2f2f2f] text-foreground px-5 py-2.5 rounded-2xl max-w-[75%] text-[15px] leading-relaxed shadow-sm">
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
      ) : (
        <div className="flex gap-4 w-full max-w-[85%]">
          <div className="flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-xl border border-white/10 bg-[#1e1e1e] text-primary shadow-sm mt-1 transition-transform group-hover:scale-105">
            <Zap className="h-5 w-5 fill-primary/20" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="prose prose-slate dark:prose-invert max-w-none 
              prose-p:leading-[1.8] prose-p:mb-5 prose-p:text-foreground/90 last:prose-p:mb-0
              prose-headings:text-foreground prose-headings:font-bold prose-headings:tracking-tight
              prose-h1:text-2xl prose-h1:mt-8 prose-h1:mb-4
              prose-h2:text-xl prose-h2:mt-7 prose-h2:mb-3
              prose-h3:text-lg prose-h3:mt-6 prose-h3:mb-2
              prose-strong:text-foreground prose-strong:font-semibold
              prose-ul:list-disc prose-ul:marker:text-primary/60 prose-ul:pl-6 prose-ul:mb-5
              prose-ol:list-decimal prose-ol:marker:text-primary/60 prose-ol:pl-6 prose-ol:mb-5
              prose-li:my-1.5 prose-li:pl-1
              prose-blockquote:border-l-4 prose-blockquote:border-primary/30 prose-blockquote:bg-primary/5 prose-blockquote:py-1 prose-blockquote:px-4 prose-blockquote:rounded-r-lg prose-blockquote:italic
              prose-table:border-collapse prose-table:w-full prose-table:my-6
              prose-th:bg-white/5 prose-th:p-3 prose-th:text-left prose-th:border prose-th:border-white/10
              prose-td:p-3 prose-td:border prose-td:border-white/10
              text-[15px] antialiased">
              <Streamdown 
                plugins={{ code }}
                components={{
                  code: CodeBlock
                }}
              >
                {message.content}
              </Streamdown>
            </div>
            
            <div className="mt-4 flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
              {message.intent && (
                <div className="inline-flex items-center rounded-full bg-primary/10 border border-primary/20 px-2.5 py-0.5 text-[9px] font-bold text-primary uppercase tracking-widest leading-none">
                  {message.intent}
                </div>
              )}
              <button 
                onClick={handleCopy}
                className="flex items-center gap-1.5 text-[11px] text-muted-foreground hover:text-foreground transition-colors"
                title="Copy response"
              >
                {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}