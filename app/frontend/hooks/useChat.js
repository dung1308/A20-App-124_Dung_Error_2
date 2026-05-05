import { useState } from 'react';
import { api } from '../services/api';

export const useChat = (userId) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  const sendMessage = async (text) => {
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const data = await api.postChat({ 
        user_id: userId, 
        message: text,
        session_id: sessionId 
      });
      const aiMsg = { role: 'assistant', content: data.response, agent: data.intent };
      setMessages(prev => [...prev, aiMsg]);
      if (data.session_id) setSessionId(data.session_id);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Lỗi kết nối AI.' }]);
    } finally {
      setLoading(false);
    }
  };

  const clearMessages = () => setMessages([]);

  return { messages, sendMessage, clearMessages, loading };
};