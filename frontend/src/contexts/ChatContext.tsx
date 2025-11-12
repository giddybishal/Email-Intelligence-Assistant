import { createContext, useEffect, useState } from "react";
import type { ReactNode } from "react";

interface ChatContextType {
  messages: { role: string; content: string }[];
  sendMessage: (message: string) => void;
}

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatContext = createContext<ChatContextType | null>(null);

export function ChatProvider({ children }: ChatProviderProps) {
  const [reply, setReply] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const BACKEND_URL = "http://127.0.0.1:8000";

  async function getReply(msg: string) {
    try {
      setIsLoading(true);
      const res = await fetch(`${BACKEND_URL}/query`, {
        method: "POST",
        body: msg,
      });
      if (res.status === 200) {
        const data = await res.json();
        setReply(data);
        console.log(data);
      } else {
        const errData = await res.json();
        alert(errData.detail || "Failed to send the message");
      }
    } catch (err) {
      console.error("Error sending message:", err);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <ChatProvider.Provider value={{ getReply, isLoading, setIsLoading }}>
      {children}
    </ChatProvider.Provider>
  );
}
