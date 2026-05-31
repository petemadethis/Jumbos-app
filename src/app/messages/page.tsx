'use client';

import { useState, useEffect } from 'react';
import { apiFetch } from '@/lib/api';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';

export default function MessagesPage() {
  const [conversations, setConversations] = useState<any[]>([]);
  const [selectedChat, setSelectedChat] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConversations = async () => {
      const data = await apiFetch<any[]>('/messages/');
      if (data) {
        // Group by user logic would go here in a real app
        setConversations(data);
      }
      setLoading(false);
    };
    fetchConversations();
  }, []);

  const fetchChatThread = async (userId: string) => {
    const data = await apiFetch<any[]>(`/messages/conversation/${userId}`);
    if (data) setMessages(data);
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedChat) return;
    
    const res = await apiFetch<any>('/messages/send', {
      method: 'POST',
      body: JSON.stringify({
        recipient_id: selectedChat.id,
        body: newMessage,
        subject: 'Direct Message'
      }),
    });

    if (res) {
      setMessages([...messages, res]);
      setNewMessage('');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 h-[calc(100vh-80px)]">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden flex h-full">
        {/* Sidebar */}
        <div className="w-1/3 border-r border-slate-200 flex flex-col">
          <div className="p-6 border-b border-slate-200 bg-slate-50">
            <h1 className="text-2xl font-bold text-primary">Messages</h1>
          </div>
          <div className="flex-grow overflow-y-auto divide-y divide-slate-100">
            {loading ? (
              <div className="p-10 text-center text-slate-400">Loading chats...</div>
            ) : conversations.length > 0 ? (
              conversations.map((chat) => (
                <div 
                  key={chat.id}
                  onClick={() => {
                    setSelectedChat(chat.other_user);
                    fetchChatThread(chat.other_user.id);
                  }}
                  className={`p-6 cursor-pointer hover:bg-slate-50 transition-colors ${
                    selectedChat?.id === chat.other_user.id ? 'bg-secondary/5 border-r-4 border-secondary' : ''
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-slate-200 overflow-hidden">
                      <img src={chat.other_user.image_url || 'https://via.placeholder.com/100'} alt="" />
                    </div>
                    <div className="flex-grow">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-bold text-primary">{chat.other_user.full_name}</span>
                        <span className="text-xs text-slate-400">12:45 PM</span>
                      </div>
                      <p className="text-sm text-slate-500 truncate">{chat.body}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-10 text-center text-slate-400 italic">No conversations yet.</div>
            )}
          </div>
        </div>

        {/* Chat Window */}
        <div className="flex-grow flex flex-col bg-slate-50/30">
          {selectedChat ? (
            <>
              {/* Header */}
              <div className="p-6 bg-white border-b border-slate-200 flex items-center gap-4 shadow-sm">
                <div className="w-10 h-10 rounded-full bg-slate-200 overflow-hidden">
                  <img src={selectedChat.image_url || 'https://via.placeholder.com/100'} alt="" />
                </div>
                <div>
                  <h2 className="font-bold text-primary">{selectedChat.full_name}</h2>
                  <p className="text-xs text-secondary font-bold uppercase">{selectedChat.role}</p>
                </div>
              </div>

              {/* Body */}
              <div className="flex-grow overflow-y-auto p-8 space-y-6">
                {messages.map((msg) => (
                  <div 
                    key={msg.id} 
                    className={`flex ${msg.sender_id === selectedChat.id ? 'justify-start' : 'justify-end'}`}
                  >
                    <div 
                      className={`max-w-[70%] p-4 rounded-2xl shadow-sm ${
                        msg.sender_id === selectedChat.id 
                        ? 'bg-white text-slate-700 rounded-tl-none border border-slate-100' 
                        : 'bg-primary text-white rounded-tr-none'
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{msg.body}</p>
                      <span className={`text-[10px] block mt-2 opacity-50 ${msg.sender_id === selectedChat.id ? 'text-slate-400' : 'text-white'}`}>
                        {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Input */}
              <div className="p-6 bg-white border-t border-slate-200">
                <div className="flex gap-4">
                  <textarea 
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Write a message..." 
                    className="flex-grow p-4 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-secondary focus:bg-white transition-all resize-none h-24"
                  />
                  <div className="flex flex-col justify-end">
                    <Button 
                      onClick={handleSendMessage}
                      disabled={!newMessage.trim()}
                      className="px-8 py-4"
                    >
                      Send
                    </Button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-grow flex items-center justify-center text-slate-400 flex-col gap-4">
              <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <p className="text-xl font-medium">Select a conversation to start messaging</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
