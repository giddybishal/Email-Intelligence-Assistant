import { useContext, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

import { ChatContext } from "@/contexts/ChatContext";

export default function ChatUI() {
  const context = useContext(ChatContext)
  if (!context) throw new Error("ChatWindow must be used within ChatProvider")

  const { getReply } = context

  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hello! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");

    const contextReply = await getReply(input)
    const reply = { role: "assistant", content: contextReply};
    setMessages((m) => [...m, reply])
  };

  return (
    <Card className="w-full max-w-3xl mx-auto flex flex-col h-[80vh]">
      <CardContent className="flex flex-col flex-1 p-0 max-h-full">
        <ScrollArea className="flex-1 p-4 space-y-4 max-h-[90%]">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-2 ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {msg.role === "assistant" && (
                <Avatar>
                  <AvatarFallback>AI</AvatarFallback>
                </Avatar>
              )}
              <div
                className={`rounded-2xl px-4 py-2 max-w-[80%] text-sm ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                }`}
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
              </div>
              {msg.role === "user" && (
                <Avatar>
                  <AvatarFallback>U</AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}
        </ScrollArea>

        <div className="border-t p-3 flex gap-2 items-end">
          <Textarea
            placeholder="Type your message..."
            className="flex-1 resize-none"
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
          />
          <Button onClick={sendMessage}>Send</Button>
        </div>
      </CardContent>
    </Card>
  );
}
