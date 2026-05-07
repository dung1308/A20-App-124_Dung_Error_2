import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../../hooks/useChat';

// For demo purposes, this is hardcoded. 
// In production, use an environment variable like import.meta.env.VITE_USE_MOCK === 'true'
const IS_DEMO_MODE = import.meta.env.VITE_USE_MOCK === 'true' || true;

const ChatBox = ({ userId }) => {
  const [input, setInput] = useState('');
  const { messages, sendMessage, loading } = useChat(userId);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = () => {
    if (!input.trim() || loading) return;
    sendMessage(input);
    setInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[500px] bg-slate-50 rounded-2xl overflow-hidden border border-slate-200">
      {IS_DEMO_MODE && (
        <div className="bg-amber-50 text-amber-800 text-[10px] text-center py-1 font-bold uppercase tracking-wider border-b border-amber-100">
          Demo Mode: Phản hồi được mô phỏng
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-scrollbar bg-slate-50/50">
        {messages.length === 0 && !loading && (
          <div className="text-center py-10">
            <span className="material-symbols-outlined text-slate-300 text-5xl mb-2">forum</span>
            <p className="text-slate-400 text-sm">Hãy đặt câu hỏi về các ngành học bạn quan tâm!</p>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
              m.role === 'user' 
                ? 'bg-[#003466] text-white rounded-tr-none' 
                : 'bg-white text-slate-800 border border-slate-100 rounded-tl-none'
            }`}>
              {m.content}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-100 p-3 rounded-2xl rounded-tl-none shadow-sm flex gap-1 items-center">
              <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce"></div>
              <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              <span className="text-[11px] text-slate-400 ml-2 italic">VinUni Bot đang soạn câu trả lời...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Section */}
      <div className="p-3 bg-white border-t border-slate-200">
        <div className="relative flex items-center gap-2">
          <input 
            className="flex-1 pl-4 pr-12 py-3 bg-slate-100 border-transparent focus:border-[#003466] focus:bg-white focus:ring-4 focus:ring-[#003466]/5 rounded-xl transition-all outline-none text-sm"
            placeholder="Hỏi thêm về ngành học, sự nghiệp..." 
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <button 
            onClick={handleSend} 
            disabled={!input.trim() || loading}
            className="absolute right-2 w-9 h-9 bg-[#003466] text-white rounded-lg flex items-center justify-center shadow-lg shadow-blue-900/20 active:scale-95 transition-all disabled:opacity-30"
          >
            <span className="material-symbols-outlined text-[20px]">send</span>
          </button>
        </div>
      </div>
    </div>
  );
};
export default ChatBox;