import { useRef, useEffect } from 'react';
import { Bot, User as UserIcon, MessageSquare } from 'lucide-react';
import { cn } from '@/lib/utils';

export const ConversationThread = ({ messages, isOpen, onClose }) => {
  const threadEndRef = useRef(null);

  useEffect(() => {
    if (isOpen && threadEndRef.current) {
      threadEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  // Filter out system messages for cleaner thread view
  const threadMessages = messages.filter(msg => msg.type !== 'system');

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  // Group messages by date
  const groupedMessages = [];
  let currentDate = null;
  
  threadMessages.forEach((message) => {
    const messageDate = message.timestamp ? formatDate(message.timestamp) : '';
    if (messageDate !== currentDate) {
      currentDate = messageDate;
      groupedMessages.push({ type: 'date', date: currentDate });
    }
    groupedMessages.push(message);
  });

  return (
    <div
      className={cn(
        'fixed top-16 right-0 h-[calc(100vh-4rem)] w-full md:w-96 bg-card border-l border-border',
        'transform transition-transform duration-300 ease-in-out z-40',
        'flex flex-col shadow-xl',
        isOpen ? 'translate-x-0' : 'translate-x-full'
      )}
    >
      {/* Header */}
      <div className="h-16 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-primary" />
          <h2 className="font-semibold text-foreground">Conversation Thread</h2>
        </div>
        <button
          onClick={onClose}
          className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
          aria-label="Close thread"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Thread Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {threadMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <MessageSquare className="w-12 h-12 mb-3 opacity-50" />
            <p className="text-sm">No conversation yet</p>
            <p className="text-xs mt-1">Start chatting to see the thread</p>
          </div>
        ) : (
          <>
            {groupedMessages.map((item, index) => {
              if (item.type === 'date') {
                return (
                  <div
                    key={`date-${index}`}
                    className="flex items-center justify-center py-2"
                  >
                    <span className="text-xs text-muted-foreground bg-card px-3 py-1 rounded-full border border-border">
                      {item.date}
                    </span>
                  </div>
                );
              }

              const message = item;
              const isUser = message.type === 'user';
              const isAssistant = message.type === 'assistant';

              return (
                <div
                  key={message.id}
                  className={cn(
                    'flex gap-3 animate-fade-in',
                    isUser && 'flex-row-reverse'
                  )}
                >
                  {/* Avatar */}
                  <div
                    className={cn(
                      'w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0',
                      isUser ? 'bg-primary' : 'bg-secondary'
                    )}
                  >
                    {isUser ? (
                      <UserIcon className="w-3.5 h-3.5 text-primary-foreground" />
                    ) : (
                      <Bot className="w-3.5 h-3.5 text-foreground" />
                    )}
                  </div>

                  {/* Message Content */}
                  <div className={cn('flex-1 min-w-0', isUser && 'flex flex-col items-end')}>
                    <div
                      className={cn(
                        'rounded-lg px-3 py-2 max-w-[85%]',
                        isUser && 'bg-primary text-primary-foreground',
                        isAssistant && 'bg-secondary border border-border'
                      )}
                    >
                      <p className="text-sm text-foreground leading-relaxed break-words">
                        {message.content}
                      </p>
                    </div>
                    
                    {/* Timestamp */}
                    {message.timestamp && (
                      <span className="text-[10px] text-muted-foreground mt-1 px-1">
                        {formatTime(message.timestamp)}
                      </span>
                    )}

                    {/* Status indicators for assistant messages */}
                    {isAssistant && message.emails && message.emails.length > 0 && (
                      <div className="mt-1 text-[10px] text-muted-foreground px-1">
                        {message.emails.length} email{message.emails.length !== 1 ? 's' : ''} shown
                      </div>
                    )}

                    {isAssistant && message.actions && message.actions.length > 0 && (
                      <div className="mt-1 text-[10px] text-muted-foreground px-1">
                        {message.actions.length} action{message.actions.length !== 1 ? 's' : ''} available
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
            <div ref={threadEndRef} />
          </>
        )}
      </div>
    </div>
  );
};

