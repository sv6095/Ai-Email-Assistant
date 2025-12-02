import { useState } from 'react';
import { Send } from 'lucide-react';
import { cn } from '@/lib/utils';

export const ChatInput = ({ onSend, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="p-4 border-t border-border bg-card/50 backdrop-blur-sm">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-end gap-2 bg-input rounded-2xl border border-border focus-within:border-primary transition-colors p-2">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command... (e.g., 'Show my emails')"
            disabled={disabled}
            rows={1}
            className={cn(
              'flex-1 bg-transparent text-foreground placeholder:text-muted-foreground resize-none',
              'focus:outline-none px-3 py-2 text-sm leading-relaxed',
              'min-h-[44px] max-h-32'
            )}
            style={{
              height: 'auto',
              overflow: 'hidden',
            }}
            onInput={(e) => {
              const target = e.target;
              target.style.height = 'auto';
              target.style.height = `${Math.min(target.scrollHeight, 128)}px`;
            }}
          />
          
          <div className="flex items-center gap-1 pb-1">
            <button
              onClick={handleSend}
              disabled={!message.trim() || disabled}
              className="w-9 h-9 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <div className="mt-2 flex items-center justify-center gap-4 text-xs text-muted-foreground">
          <span>Try: "Show my emails"</span>
          <span>•</span>
          <span>"Reply to email 1"</span>
          <span>•</span>
          <span>"Delete email from Netflix"</span>
        </div>
      </div>
    </div>
  );
};

