import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../../hooks/useChat';

// For demo purposes, this is hardcoded. 
// In production, use an environment variable like import.meta.env.VITE_USE_MOCK === 'true'
const IS_DEMO_MODE = true;

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
    if (!input.trim()) return;
    sendMessage(input);
    setInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="chat-box">
      {IS_DEMO_MODE && (
        <div style={{ 
          backgroundColor: '#fffbeb', 
          color: '#92400e', 
          fontSize: '11px', 
          textAlign: 'center', 
          padding: '4px 8px', 
          borderBottom: '1px solid #fde68a',
          fontWeight: '500',
          letterSpacing: '0.025em'
        }}>
          Demo Mode: Results are simulated
        </div>
      )}
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>{m.content}</div>
        ))}
        {loading && (
          <div className="msg assistant typing" style={{ color: '#6b7280', fontSize: '0.85em', marginTop: '4px', fontStyle: 'italic' }}>
            VinUni Bot đang soạn câu trả lời...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <input 
        value={input} 
        onChange={e => setInput(e.target.value)} 
        onKeyPress={handleKeyPress}
        placeholder="Hỏi thêm về ngành học..." 
      />
      <button onClick={handleSend} disabled={loading}>Gửi</button>
    </div>
  );
};
export default ChatBox;