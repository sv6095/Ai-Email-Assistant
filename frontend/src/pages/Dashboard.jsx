import { useState, useEffect, useRef } from 'react';
import { Header } from '../components/Header';
import { ChatMessage } from '../components/ChatMessage';
import { ChatInput } from '../components/ChatInput';
import { TypingIndicator } from '../components/TypingIndicator';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { ConversationThread } from '../components/ConversationThread';
import { useChat } from '../hooks/useChat';
import { auth } from '../services/auth';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isThreadOpen, setIsThreadOpen] = useState(false);
  const { messages, isTyping, sendMessage, handleAction: executeAction, initializeChat } = useChat(user);
  const messagesEndRef = useRef(null);
  const [confirmState, setConfirmState] = useState({
    open: false,
    action: null,
    title: '',
    description: '',
    confirmLabel: 'Confirm',
    cancelLabel: 'Cancel',
  });

  useEffect(() => {
    // Check for token in URL (from OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      localStorage.setItem('token', token);
      // Clean up URL
      window.history.replaceState({}, document.title, '/dashboard');
    }

    // Load user data
    const loadUser = async () => {
      const userData = await auth.getCurrentUser();
      if (userData) {
        const userObj = {
          name: userData.name,
          email: userData.email,
          avatar: userData.picture,
        };
        setUser(userObj);
        initializeChat(userObj);
      } else {
        // No valid token, redirect to login
        window.location.href = '/login';
      }
      setLoading(false);
    };

    loadUser();
  }, [initializeChat]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleLogout = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        await auth.logout(token);
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-background">
        <div className="text-foreground">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return (
    <div className="h-screen flex flex-col bg-background relative">
      <Header 
        user={user} 
        onLogout={handleLogout}
        onToggleThread={() => setIsThreadOpen(!isThreadOpen)}
      />
      
      {/* Backdrop overlay when thread is open on mobile */}
      {isThreadOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setIsThreadOpen(false)}
        />
      )}
      
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto py-6 px-4 space-y-6">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onAction={(action) => {
                if (!action) return;
                if (action.requiresConfirmation) {
                  setConfirmState({
                    open: true,
                    action,
                    title: action.confirmTitle || 'Are you sure?',
                    description: action.confirmDescription || 'Please confirm this action.',
                    confirmLabel: action.confirmLabel || 'Confirm',
                    cancelLabel: action.cancelLabel || 'Cancel',
                  });
                } else {
                  executeAction(action);
                }
              }}
            />
          ))}
          
          {isTyping && <TypingIndicator />}
          
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      <ChatInput onSend={sendMessage} disabled={isTyping} />

      <ConfirmDialog
        open={confirmState.open}
        onOpenChange={(open) => {
          if (!open) {
            setConfirmState((prev) => ({ ...prev, open: false, action: null }));
          }
        }}
        title={confirmState.title}
        description={confirmState.description}
        confirmLabel={confirmState.confirmLabel}
        cancelLabel={confirmState.cancelLabel}
        onConfirm={() => {
          if (confirmState.action) {
            executeAction(confirmState.action);
          }
          setConfirmState((prev) => ({ ...prev, open: false, action: null }));
        }}
        onCancel={() => setConfirmState((prev) => ({ ...prev, open: false, action: null }))}
        variant={confirmState.action?.type === 'delete' ? 'destructive' : 'default'}
      />

      {/* Conversation Thread Sidebar */}
      <ConversationThread
        messages={messages}
        isOpen={isThreadOpen}
        onClose={() => setIsThreadOpen(false)}
      />
    </div>
  );
}
