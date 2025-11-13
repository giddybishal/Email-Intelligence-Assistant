import { createContext } from "react"
import type { ReactNode } from "react"

interface ChatContextType{
  getReply: (msg: string) => Promise<string>
}

interface ChatProviderProps{
  children: ReactNode
}

export const ChatContext = createContext<ChatContextType | null>(null)

export function ChatProvider({ children } : ChatProviderProps) {
  const BACKEND_URL = "http://127.0.0.1:8000"

  async function getReply(msg: string): Promise<string> {
    try{
      const res = await fetch(`${BACKEND_URL}/query`,{
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: msg }),
      })
      if (res.ok){
        const data = await res.json()
        return data ?? 'No response'
      } else{
        const errData = await res.json()
        alert(errData.detail || "Failed to send the message")
        return 'There was an error'
      }
    } catch (err){
      console.error("Error sending message:", err)
      return 'There was an error'
    }
  }

  return (
    <ChatContext.Provider value={{ getReply }}>
      {children}
    </ChatContext.Provider>
  );
}
