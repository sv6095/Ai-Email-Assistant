// Chat service - handles chat API calls
import { api } from './api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

export const chatService = {
  sendMessage: async (message) => {
    const response = await fetch(`${api.baseURL}/chat/message`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to send message');
    }

    return response.json();
  },

  handleAction: async (action) => {
    const response = await fetch(`${api.baseURL}/chat/action`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(action),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to handle action');
    }

    return response.json();
  },
};

