import { Bot, User as UserIcon } from 'lucide-react';
import { EmailCard } from './EmailCard';
import { EmailGroupSummary } from './EmailGroupSummary';
import { cn } from '@/lib/utils';

export const ChatMessage = ({ message, onAction }) => {
  const isUser = message.type === 'user';
  const isSystem = message.type === 'system';

  const hasGroupedEmails = Array.isArray(message.groupedEmails) && message.groupedEmails.length > 0;
  const shouldRenderEmails = !hasGroupedEmails && message.emails && message.emails.length > 0;

  const getButtonVariantClasses = (actionType) => {
    if (actionType === 'delete') {
      return 'bg-destructive text-destructive-foreground hover:bg-destructive/90';
    }
    if (actionType === 'cancel') {
      return 'border border-border bg-transparent hover:bg-accent hover:text-accent-foreground';
    }
    return 'bg-primary text-primary-foreground hover:bg-primary/90';
  };

  return (
    <div
      className={cn(
        'flex gap-3 animate-fade-in',
        isUser && 'flex-row-reverse',
        isSystem && 'justify-center'
      )}
    >
      {/* Avatar */}
      {!isSystem && (
        <div
          className={cn(
            'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
            isUser ? 'bg-primary' : 'bg-secondary'
          )}
        >
          {isUser ? (
            <UserIcon className="w-4 h-4 text-primary-foreground" />
          ) : (
            <Bot className="w-4 h-4 text-foreground" />
          )}
        </div>
      )}

      {/* Message Content */}
      <div
        className={cn(
          'rounded-2xl px-4 py-3',
          isUser && 'bg-bubble-user max-w-[80%]',
          message.type === 'assistant' && 'bg-bubble-ai border border-border max-w-[80%]',
          isSystem && 'bg-bubble-system border border-border max-w-2xl'
        )}
      >
        <div className={cn('prose prose-invert prose-sm max-w-none', isSystem && 'text-left')}>
          {message.content.split('\n').map((line, i) => {
            const isEmpty = !line.trim();
            if (isEmpty) return <br key={i} />;
            
            return (
              <p key={i} className={cn('mb-2 last:mb-0 text-foreground leading-relaxed', isSystem && line.startsWith('**') && 'mt-3 first:mt-0')}>
                {line.split(/(\*\*.*?\*\*)/).map((part, j) => {
                  if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={j} className="font-semibold text-primary">{part.slice(2, -2)}</strong>;
                  }
                  return <span key={j}>{part}</span>;
                })}
              </p>
            );
          })}
        </div>

        {/* Smart Inbox Grouping */}
        {hasGroupedEmails && (
          <div className="mt-4 space-y-4">
            {message.groupedEmails.map((group) => (
              <EmailGroupSummary key={group.category} group={group} />
            ))}
          </div>
        )}

        {/* Email Cards */}
        {shouldRenderEmails && (
          <div className="mt-4 space-y-3">
            {message.emails.map((email, index) => (
              <EmailCard key={email.id || index} email={email} index={index + 1} />
            ))}
          </div>
        )}

        {/* Action Buttons */}
        {message.actions && message.actions.length > 0 && (
          <div className="mt-4 flex gap-2 flex-wrap">
            {message.actions.map((action) => (
              <button
                key={action.id}
                onClick={() => onAction?.(action)}
                disabled={action.disabled}
                className={cn(
                  'px-3 py-1.5 text-sm font-medium rounded-lg transition-colors',
                  'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
                  'disabled:opacity-50 disabled:cursor-not-allowed',
                  getButtonVariantClasses(action.type)
                )}
              >
                {action.label}
              </button>
            ))}
          </div>
        )}

        {/* Timestamp */}
        {message.timestamp && (
          <p className="text-[10px] text-muted-foreground mt-2">
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>
    </div>
  );
};
