import { useRef, useState } from 'react'
import { Trash2, FolderPlus, Upload, FileText, Search, SquarePen, PanelLeftClose } from 'lucide-react'
import { useChat } from '../context/ChatContext'
import { clsx } from 'clsx'

export function Sidebar() {
  const { state, currentSession, newSession, switchSession, deleteSession, uploadDocument, toggleSidebar } = useChat()
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  if (!state.isSidebarOpen) return null;

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    try {
      await uploadDocument(file)
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  return (
    <div className="flex w-[260px] shrink-0 flex-col bg-sidebar h-full text-[14px] border-r border-white/5">
      <div className="flex items-center justify-between px-3 py-3">
        <button 
          onClick={toggleSidebar}
          className="flex h-10 w-10 items-center justify-center rounded-lg hover:bg-sidebar-hover text-muted-foreground transition-colors"
        >
          <PanelLeftClose className="h-5 w-5" />
        </button>
        <button
          onClick={newSession}
          className="flex h-10 w-10 items-center justify-center rounded-lg hover:bg-sidebar-hover text-foreground transition-colors"
        >
          <SquarePen className="h-5 w-5" />
        </button>
      </div>

      <div className="flex flex-col px-3 gap-1">
        <button onClick={newSession} className="flex items-center gap-2 rounded-lg px-2 py-2 text-foreground hover:bg-sidebar-hover transition-colors">
          <div className="flex items-center justify-center w-6 h-6"><SquarePen className="h-4 w-4" /></div>
          <span>New chat</span>
        </button>
        <button className="flex items-center gap-2 rounded-lg px-2 py-2 text-foreground hover:bg-sidebar-hover transition-colors">
          <div className="flex items-center justify-center w-6 h-6"><Search className="h-4 w-4" /></div>
          <span>Search chats</span>
        </button>
        <button className="flex items-center gap-2 rounded-lg px-2 py-2 text-foreground hover:bg-sidebar-hover transition-colors">
          <div className="flex items-center justify-center w-6 h-6"><FolderPlus className="h-4 w-4" /></div>
          <span>New project</span>
        </button>
      </div>

      <div className="mt-6 flex-1 overflow-y-auto px-3">
        <h3 className="mb-2 px-2 text-[11px] font-bold text-muted-foreground uppercase tracking-widest">Projects</h3>
        <div className="space-y-0.5">
          {state.sessions.map(session => (
            <div
              key={session.id}
              className={clsx(
                "group relative flex w-full cursor-pointer items-center justify-between rounded-lg px-2 py-2 transition-colors",
                currentSession.id === session.id
                  ? "bg-sidebar-hover text-foreground"
                  : "text-foreground hover:bg-sidebar-hover"
              )}
              onClick={() => switchSession(session.id)}
            >
              <div className="flex items-center truncate w-full pr-6">
                <span className="truncate">{session.title}</span>
              </div>
              {state.sessions.length > 1 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteSession(session.id)
                  }}
                  className={clsx("absolute right-2 text-muted-foreground hover:text-foreground", currentSession.id === session.id ? 'block' : 'hidden group-hover:block')}
                  title="Delete project"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="mt-8">
            <h3 className="mb-2 px-2 text-[11px] font-bold text-muted-foreground uppercase tracking-widest">Knowledge Base</h3>
            <div className="px-2">
               <input 
                  type="file" 
                  ref={fileInputRef} 
                  className="hidden" 
                  accept=".pdf,.txt,.docx,.md"
                  onChange={handleFileUpload}
               />
               <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className="flex w-full items-center gap-2 rounded-lg py-2 text-muted-foreground transition-colors hover:text-foreground mb-3"
               >
                  {isUploading ? (
                    <span className="animate-pulse">Ingesting...</span>
                  ) : (
                    <>
                      <div className="flex items-center justify-center w-6 h-6"><Upload className="h-4 w-4" /></div>
                      Upload Documents
                    </>
                  )}
               </button>
               
               {currentSession.documents.length > 0 && (
                 <div className="space-y-1">
                   {currentSession.documents.map((doc, i) => (
                      <div key={i} className="flex items-center gap-2 rounded-md bg-sidebar-hover px-2 py-1.5 text-xs text-foreground">
                        <FileText className="h-3 w-3 text-muted-foreground" />
                        <span className="truncate">{doc}</span>
                      </div>
                   ))}
                 </div>
               )}
            </div>
        </div>
      </div>

      <div className="p-3">
        <button className="flex w-full items-center gap-2 rounded-lg p-2 text-foreground hover:bg-sidebar-hover transition-colors">
          <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center font-bold text-xs text-primary">UI</div>
          <div className="flex flex-col items-start leading-tight">
            <span className="font-semibold text-[14px]">User Name</span>
            <span className="text-[12px] text-muted-foreground">Free</span>
          </div>
        </button>
      </div>

    </div>
  )
}
