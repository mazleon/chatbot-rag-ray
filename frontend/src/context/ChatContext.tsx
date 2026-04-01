import { createContext, useContext, useReducer, type ReactNode } from 'react'
import type { Message } from '../types'
import { api } from '../services/api'

interface Session {
  id: string;
  title: string;
  messages: Message[];
  documents: string[];
}

interface ChatState {
  sessions: Session[];
  currentSessionId: string;
  isSidebarOpen: boolean;
  isLoading: boolean;
  error: string | null;
}

type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_MESSAGES' }
  | { type: 'NEW_SESSION'; payload: string }
  | { type: 'SWITCH_SESSION'; payload: string }
  | { type: 'RENAME_SESSION'; payload: { id: string; title: string } }
  | { type: 'ADD_DOCUMENT'; payload: { sessionId: string; filename: string } }
  | { type: 'DELETE_SESSION'; payload: string }
  | { type: 'TOGGLE_SIDEBAR' }

function createNewProject(id: string = crypto.randomUUID()): Session {
  return { id, title: 'New Project', messages: [], documents: [] };
}

const initialSession = createNewProject();

const initialState: ChatState = {
  sessions: [initialSession],
  currentSessionId: initialSession.id,
  isSidebarOpen: true,
  isLoading: false,
  error: null,
}

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'ADD_MESSAGE': {
      const updatedSessions = state.sessions.map(s => {
        if (s.id !== state.currentSessionId) return s;
        // Generate title from first user message if it's still 'New Project'
        const newTitle = (s.messages.length === 0 && action.payload.role === 'user') 
          ? action.payload.content.slice(0, 30) + (action.payload.content.length > 30 ? '...' : '')
          : s.title;
        return { ...s, title: newTitle, messages: [...s.messages, action.payload] };
      });
      return { ...state, sessions: updatedSessions, error: null };
    }
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'CLEAR_MESSAGES': {
      const updatedSessions = state.sessions.map(s => 
        s.id === state.currentSessionId ? { ...s, messages: [] } : s
      );
      return { ...state, sessions: updatedSessions, error: null };
    }
    case 'NEW_SESSION': {
      const newSession = createNewProject(action.payload);
      return { ...state, sessions: [newSession, ...state.sessions], currentSessionId: newSession.id, error: null };
    }
    case 'SWITCH_SESSION':
      return { ...state, currentSessionId: action.payload, error: null };
    case 'DELETE_SESSION': {
      const filtered = state.sessions.filter(s => s.id !== action.payload);
      if (filtered.length === 0) {
        const fresh = createNewProject();
        return { ...state, sessions: [fresh], currentSessionId: fresh.id };
      }
      return { 
        ...state, 
        sessions: filtered, 
        currentSessionId: state.currentSessionId === action.payload ? filtered[0].id : state.currentSessionId 
      };
    }
    case 'ADD_DOCUMENT': {
      const updatedSessions = state.sessions.map(s => 
        s.id === action.payload.sessionId ? { ...s, documents: [...s.documents, action.payload.filename] } : s
      );
      return { ...state, sessions: updatedSessions };
    }
    case 'TOGGLE_SIDEBAR':
      return { ...state, isSidebarOpen: !state.isSidebarOpen };
    default:
      return state;
  }
}

interface ChatContextType {
  state: ChatState;
  currentSession: Session;
  sendMessage: (content: string) => Promise<void>;
  clearChat: () => void;
  newSession: () => void;
  switchSession: (id: string) => void;
  deleteSession: (id: string) => void;
  toggleSidebar: () => void;
  uploadDocument: (file: File) => Promise<void>;
}

const ChatContext = createContext<ChatContextType | null>(null)

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, initialState)
  
  const currentSession = state.sessions.find(s => s.id === state.currentSessionId) || state.sessions[0];

  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    }
    dispatch({ type: 'ADD_MESSAGE', payload: userMessage })
    dispatch({ type: 'SET_LOADING', payload: true })

    try {
      const response = await api.chat({
        session_id: state.currentSessionId,
        message: content,
      })

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        intent: response.intent,
        sources: response.sources,
      }
      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to send message'
      dispatch({ type: 'SET_ERROR', payload: message })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const uploadDocument = async (file: File) => {
    dispatch({ type: 'SET_LOADING', payload: true })
    try {
      console.log('[ChatContext] Uploading document:', file.name)
      const result = await api.uploadDocument(file)
      console.log('[ChatContext] Upload result:', result)
      
      dispatch({ type: 'ADD_DOCUMENT', payload: { sessionId: state.currentSessionId, filename: file.name } })
      console.log('[ChatContext] Added document to session:', state.currentSessionId)
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Successfully ingested **${file.name}**. ${result.chunks_created} chunks added to Knowledge Base.`,
        timestamp: new Date().toISOString(),
      }
      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage })
      console.log('[ChatContext] Added confirmation message')
    } catch (err) {
      console.error('[ChatContext] Ingestion failed:', err)
      const errorMsg = err instanceof Error ? err.message : 'Failed to ingest document'
      dispatch({ type: 'SET_ERROR', payload: errorMsg })
      
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Failed to upload **${file.name}**: ${errorMsg}`,
        timestamp: new Date().toISOString(),
      }
      dispatch({ type: 'ADD_MESSAGE', payload: errorMessage })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const clearChat = () => dispatch({ type: 'CLEAR_MESSAGES' })
  const newSession = () => dispatch({ type: 'NEW_SESSION', payload: crypto.randomUUID() })
  const switchSession = (id: string) => dispatch({ type: 'SWITCH_SESSION', payload: id })
  const deleteSession = (id: string) => dispatch({ type: 'DELETE_SESSION', payload: id })
  const toggleSidebar = () => dispatch({ type: 'TOGGLE_SIDEBAR' })

  return (
    <ChatContext.Provider value={{ state, currentSession, sendMessage, clearChat, newSession, switchSession, deleteSession, toggleSidebar, uploadDocument }}>
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const context = useContext(ChatContext)
  if (!context) throw new Error('useChat must be used within ChatProvider')
  return context
}