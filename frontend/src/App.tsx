import { ChatProvider } from './context/ChatContext'
import { ChatWindow } from './components/ChatWindow'
import { Sidebar } from './components/Sidebar'

function App() {
  return (
    <ChatProvider>
      <div className="flex h-screen w-screen overflow-hidden bg-background selection:bg-foreground selection:text-background">
        <Sidebar />
        <main className="flex-1 min-w-0">
          <ChatWindow />
        </main>
      </div>
    </ChatProvider>
  )
}

export default App