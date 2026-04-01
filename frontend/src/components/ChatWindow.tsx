import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import { ChatInput } from './ChatInput'
import { useChat } from '../context/ChatContext'
import { ChevronDown, Share, MoreHorizontal, PanelLeftOpen, Zap } from 'lucide-react'
import type { Message } from '../types'

export function ChatWindow() {
  const { state, currentSession, sendMessage, toggleSidebar } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentSession.messages])

  return (
    <div className="flex h-full flex-col relative w-full items-center overflow-hidden">
      <header className="w-full flex justify-between items-center px-4 py-3 z-10 sticky top-0 items-center">
        <div className="flex items-center gap-2">
          {!state.isSidebarOpen && (
             <button 
                onClick={toggleSidebar}
                className="flex h-10 w-10 items-center justify-center rounded-lg hover:bg-sidebar-hover text-muted-foreground transition-colors mr-2"
             >
                <PanelLeftOpen className="h-5 w-5" />
             </button>
          )}
          <button className="flex items-center gap-1 text-[18px] font-semibold hover:bg-sidebar-hover px-3 py-2 rounded-xl transition-colors text-foreground min-w-0">
            <span className="truncate">Ray Advertising</span> <ChevronDown className="h-4 w-4 text-muted-foreground ml-1 shrink-0" />
          </button>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 text-[14px] font-medium text-foreground hover:bg-sidebar-hover px-3 py-2 rounded-xl transition-colors border border-white/10">
            <Share className="h-4 w-4" /> Share
          </button>
          <button className="flex h-9 w-9 items-center justify-center rounded-full hover:bg-sidebar-hover transition-colors text-muted-foreground hover:text-foreground">
            <MoreHorizontal className="h-5 w-5" />
          </button>
        </div>
      </header>

      <main className="flex w-full flex-1 flex-col overflow-y-auto px-4 pb-48 pt-6">
        {currentSession.messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center animate-fade-in-up mt-[-10vh]">
            <div className="mb-6 flex h-[72px] w-[72px] items-center justify-center rounded-2xl border border-white/10 bg-background text-primary shadow-sm shrink-0">
               <Zap className="h-10 w-10 fill-primary/20" />
            </div>
            <h2 className="font-display mb-3 text-3xl font-semibold tracking-tight text-foreground">How can I help you today?</h2>
            <p className="text-muted-foreground text-center max-w-md">Ray Advertising AI helps you create, manage, and optimize your marketing campaigns with ease.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-6 w-full max-w-3xl mx-auto">
            {currentSession.messages.map((msg: Message) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {state.error && (
              <div className="animate-fade-in-up border border-destructive bg-destructive/5 p-4 text-[15px] rounded-lg text-destructive w-full">
                <div className="flex items-center gap-2 font-medium">
                  <span className="flex h-5 w-5 items-center justify-center bg-destructive text-destructive-foreground rounded-full text-xs">!</span>
                  System Error
                </div>
                <p className="mt-2 ml-7">{state.error}</p>
              </div>
            )}
            {state.isLoading && (
              <div className="flex w-full gap-5 animate-fade-in-up flex-row pb-12 w-full max-w-3xl mx-auto">
                <div className="h-8 w-8 rounded-full border border-white/10 shrink-0 flex items-center justify-center bg-white/5">
                  <div className="h-4 w-4 bg-foreground/50 rounded-full animate-pulse" />
                </div>
                <div className="w-full flex items-center h-8">
                  <span className="w-2 h-2 rounded-full bg-foreground/60 animate-bounce" />
                  <span className="w-2 h-2 rounded-full bg-foreground/60 animate-bounce ml-1 [animation-delay:0.2s]" />
                  <span className="w-2 h-2 rounded-full bg-foreground/60 animate-bounce ml-1 [animation-delay:0.4s]" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} className="h-8" />
          </div>
        )}
      </main>

      <div className="absolute bottom-0 w-full pt-8 pb-3 bg-gradient-to-t from-background via-background to-transparent z-10 mx-auto px-4 w-full flex justify-center">
         <div className="w-full max-w-3xl flex justify-center">
            <ChatInput onSubmit={sendMessage} disabled={state.isLoading} />
         </div>
      </div>
    </div>
  )
}