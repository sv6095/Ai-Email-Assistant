import { useState, useCallback } from 'react';

const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

export const useChat = (user) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  const initializeChat = useCallback((user) => {
    if (!user) return;

    const welcomeMessage = {
      id: generateId(),
      type: 'system',
      content: `Welcome, ${user.name}! I'm your AI email assistant.`,
      timestamp: new Date(),
    };

    const featuresMessage = {
      id: generateId(),
      type: 'system',
      content: `Here's what I can help you with:

**Check Your Recent Emails**
Quickly see your latest 5 emails with sender, subject, and a short summary. Just ask me to show your emails!

**Reply to Emails**
I can draft professional responses to any email in your inbox. Tell me which email you'd like to reply to.

**Delete Emails**
Remove emails you don't need. You can delete by sender (like "Delete the latest email from Bob") or by subject keyword (like "Delete emails with subject 'Invoice'").

How can I help you manage your inbox today?`,
      timestamp: new Date(),
    };

    setMessages([welcomeMessage, featuresMessage]);
  }, []);

  const appendAssistantMessage = useCallback((response) => {
    const assistantMessage = {
      id: response.id || generateId(),
      type: 'assistant',
      content: response.content || response.message || 'I received your message.',
      emails: response.emails || [],
      actions: response.actions || [],
      timestamp: response.timestamp ? new Date(response.timestamp) : new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);
  }, []);

  const sendMessage = useCallback(async (content) => {
    if (!content.trim()) return;

    // Add user message
    const userMessage = {
      id: generateId(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const { chatService } = await import('@/services/chat');
      const response = await chatService.sendMessage(content.trim());
      appendAssistantMessage(response);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: generateId(),
        type: 'system',
        content: `Sorry, I encountered an error. ${error.message || 'Please try again.'}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [appendAssistantMessage]);

  const handleAction = useCallback(async (action) => {
    if (!action) return;
    setIsTyping(true);

    try {
      const { chatService } = await import('@/services/chat');
      const payload = {
        type: action.type,
        emailId: action.emailId,
        payload: action.payload,
      };
      const response = await chatService.handleAction(payload);
      appendAssistantMessage(response);
    } catch (error) {
      console.error('Error handling action:', error);
      
      const errorMessage = {
        id: generateId(),
        type: 'system',
        content: `Sorry, I encountered an error processing that action. ${error.message || 'Please try again.'}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [appendAssistantMessage]);

  return {
    messages,
    isTyping,
    sendMessage,
    handleAction,
    initializeChat,
  };
};

