const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  async postMatch(payload) {
    const response = await fetch(`${API_BASE_URL}/api/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error('Failed to fetch recommendations');
    return response.json();
  },

  async postChat(payload) {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error('Chat service unavailable');
    return response.json();
  },

  async sendMessage(userId, message, sessionId = null) {
    try {
      return await this.postChat({ user_id: userId, message, session_id: sessionId });
    } catch (error) {
      console.error("api.sendMessage failed:", error);
      throw error;
    }
  },

  async startSession() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error('Service unavailable');
      return await response.json();
    } catch (error) {
      console.error("api.startSession failed:", error);
      throw error;
    }
  },

  async getHistory(userId) {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/history`);
    if (!response.ok) return { history: [] };
    return response.json();
  }
};