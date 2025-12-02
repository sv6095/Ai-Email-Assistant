// Auth service - login/logout helpers
import { api } from './api';

export const auth = {
  login: () => {
    // Redirect to backend login endpoint, which will redirect to Google OAuth
    const loginUrl = `${api.baseURL}/auth/login`;
    console.log('Redirecting to:', loginUrl);
    window.location.href = loginUrl;
  },
  
  logout: async (token) => {
    const response = await api.post('/auth/logout', { token });
    return response.json();
  },
  
  getCurrentUser: async () => {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    const response = await fetch(`${api.baseURL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (!response.ok) return null;
    return response.json();
  },
};

