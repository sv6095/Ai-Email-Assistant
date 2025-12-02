import { useState, useEffect } from 'react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import { auth } from './services/auth';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication status
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        const user = await auth.getCurrentUser();
        setIsAuthenticated(!!user);
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  // Handle routing based on pathname
  const pathname = window.location.pathname;

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }

  // If on dashboard route, show dashboard (it will handle its own auth check)
  if (pathname === '/dashboard' || pathname.startsWith('/dashboard')) {
    return <Dashboard />;
  }

  // Otherwise show login
  return <Login onLogin={() => setIsAuthenticated(true)} />;
}

export default App
