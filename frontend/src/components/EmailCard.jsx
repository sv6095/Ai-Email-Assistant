import { Mail, AlertCircle, Briefcase, User, Megaphone } from 'lucide-react';
import { cn } from '@/lib/utils';

const categoryConfig = {
  urgent: { icon: AlertCircle, color: 'text-destructive', bg: 'bg-destructive/10' },
  work: { icon: Briefcase, color: 'text-primary', bg: 'bg-primary/10' },
  personal: { icon: User, color: 'text-success', bg: 'bg-success/10' },
  promotions: { icon: Megaphone, color: 'text-warning', bg: 'bg-warning/10' },
};

const getTimeAgo = (date) => {
  if (!date) return 'Unknown time';
  
  const dateObj = date instanceof Date ? date : new Date(date);
  
  // Check if date is valid
  if (isNaN(dateObj.getTime())) {
    return 'Unknown time';
  }
  
  const seconds = Math.floor((new Date().getTime() - dateObj.getTime()) / 1000);
  
  // Handle negative seconds (future dates)
  if (seconds < 0) return 'Just now';

  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};

export const EmailCard = ({ email, index }) => {
  const category = email.category ? categoryConfig[email.category] : null;
  const CategoryIcon = category?.icon || Mail;
  const timeAgo = getTimeAgo(email.timestamp || email.date);

  return (
    <div className="bg-secondary/50 rounded-xl p-4 border border-border hover:border-primary/30 transition-colors">
      <div className="flex items-start gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-muted-foreground w-5">#{index}</span>
          <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center', category?.bg || 'bg-muted')}>
            <CategoryIcon className={cn('w-4 h-4', category?.color || 'text-muted-foreground')} />
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <span className="font-medium text-foreground truncate">{email.sender?.name || email.sender}</span>
            <span className="text-xs text-muted-foreground flex-shrink-0">{timeAgo}</span>
          </div>
          <p className="text-xs text-muted-foreground truncate mb-2">
            {email.sender?.email || (typeof email.sender === 'string' ? email.sender : '')}
          </p>
          <h4 className="font-medium text-sm text-foreground mb-2 line-clamp-1">{email.subject}</h4>

          {email.summary && (
            <div className="bg-background/50 rounded-lg p-2 border border-border/50 mb-2">
              <p className="text-xs text-muted-foreground mb-1 font-medium">AI Summary:</p>
              <p className="text-sm text-foreground/80">{email.summary}</p>
            </div>
          )}

          {email.replyText && (
            <div className="bg-primary/10 rounded-lg p-2 border border-primary/20">
              <p className="text-xs text-primary mb-1 font-medium">Suggested Reply:</p>
              <p className="text-sm text-foreground/90 whitespace-pre-wrap">{email.replyText}</p>
            </div>
          )}
        </div>

        {!email.isRead && (
          <div className="w-2 h-2 rounded-full bg-primary flex-shrink-0 mt-1" />
        )}
      </div>
    </div>
  );
};
