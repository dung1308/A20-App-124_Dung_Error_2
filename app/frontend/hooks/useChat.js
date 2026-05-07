import { useState, useCallback, useEffect } from 'react';
import { api } from '../services/api';

/**
 * useChat Hook
 * Manages chat state and API synchronization for the AI Mentor.
 * 
 * @param {string} userId - The identifier for the current student.
 * @param {string} storageKey - Optional key to persist messages in localStorage.
 * @returns {Object} { messages, setMessages, sendMessage, clearChat, loading }
 */
export const useChat = (userId, storageKey = null) => {
  const [messages, setMessages] = useState(() => {
    if (storageKey) {
      const saved = localStorage.getItem(storageKey);
      return saved ? JSON.parse(saved) : [];
    }
    return [];
  });
  const [loading, setLoading] = useState(false);

  // Persist to localStorage if key provided
  useEffect(() => {
    if (storageKey) {
      localStorage.setItem(storageKey, JSON.stringify(messages));
    }
  }, [messages, storageKey]);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || loading) return;

    // 1. Update UI with user message immediately
    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      // 2. Format history for the LLM context (role and content only)
      // Filter out meta-fields (like 'type' or 'data') not recognized by the backend schema
      const history = messages
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m => ({
          role: String(m.role),
          content: String(m.content || "")
        }));

      // 3. Dispatch to backend using the aliased ChatRequest schema
      const payload = {
        userId: userId || "anonymous",
        text: text,
        history: history
      };

      const response = await api.postChat(payload);

      // 4. Update UI with assistant response and metadata
      if (response && response.response) {
        const assistantMsg = { 
          role: 'assistant', 
          content: response.response,
          type: response.major ? 'recommendation' : null,
          data: response.major || null
        };
        setMessages((prev) => [...prev, assistantMsg]);
      }
    } catch (error) {
      console.error("useChat Error:", error);
      setMessages((prev) => [...prev, { role: 'assistant', content: "Xin lỗi, tôi gặp trục trặc khi kết nối. Bạn có thể thử lại sau nhé." }]);
    } finally {
      setLoading(false);
    }
  }, [userId, messages, loading]);

  const clearChat = useCallback(() => {
    setMessages([]);
    if (storageKey) {
      localStorage.removeItem(storageKey);
    }
  }, [storageKey]);

  return { messages, setMessages, sendMessage, clearChat, loading };
};