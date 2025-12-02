import { EmailCard } from './EmailCard';

export const EmailGroupSummary = ({ group }) => {
  if (!group) return null;
  
  const topEmails = (group.emails || []).slice(0, 3);
  const remainingCount = Math.max(0, (group.count || 0) - topEmails.length);
  
  return (
    <div className="border border-border rounded-xl bg-background/60 p-3">
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Smart Inbox Group</p>
          <h4 className="text-base font-semibold text-foreground">{group.category}</h4>
        </div>
        <span className="text-xs font-medium text-muted-foreground bg-muted px-2 py-1 rounded-lg">
          {group.count || 0} email{group.count === 1 ? '' : 's'}
        </span>
      </div>

      {group.highlights && group.highlights.length > 0 && (
        <ul className="mt-3 text-sm text-muted-foreground space-y-1 list-disc pl-5">
          {group.highlights.map((highlight, idx) => (
            <li key={`${group.category}-highlight-${idx}`}>{highlight}</li>
          ))}
        </ul>
      )}

      {topEmails.length > 0 && (
        <div className="mt-4 space-y-2">
          {topEmails.map((email, idx) => (
            <EmailCard key={email.id || `${group.category}-${idx}`} email={email} index={idx + 1} />
          ))}
        </div>
      )}

      {remainingCount > 0 && (
        <p className="text-xs text-muted-foreground mt-3">
          + {remainingCount} more email{remainingCount === 1 ? '' : 's'} in {group.category}
        </p>
      )}
    </div>
  );
};

