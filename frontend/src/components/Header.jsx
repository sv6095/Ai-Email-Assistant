import { useState, useRef, useEffect } from 'react';
import { LogOut, Mail, Settings, MessageSquare } from 'lucide-react';
import { cn } from '@/lib/utils';

export const Header = ({ user, onLogout, onToggleThread }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [avatarError, setAvatarError] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isDropdownOpen]);

  // Reset avatar error when avatar URL changes
  useEffect(() => {
    setAvatarError(false);
  }, [user?.avatar]);

  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center">
          <Mail className="w-4 h-4 text-primary-foreground" />
        </div>
        <div>
          <h1 className="font-semibold text-foreground">MailAI Assistant</h1>
          <p className="text-xs text-muted-foreground">Connected to Gmail</p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {/* Thread Toggle Button */}
        {onToggleThread && (
          <button
            onClick={onToggleThread}
            className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-secondary transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            aria-label="Toggle conversation thread"
          >
            <MessageSquare className="w-4 h-4 text-foreground" />
            <span className="text-sm font-medium text-foreground hidden sm:inline">Thread</span>
          </button>
        )}
        <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          className="flex items-center gap-2 h-auto p-2 rounded-lg hover:bg-secondary transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          <div className="w-8 h-8 rounded-full overflow-hidden bg-primary flex items-center justify-center flex-shrink-0">
            {user?.avatar && !avatarError ? (
              <img
                src={user.avatar}
                alt={user?.name || 'User'}
                className="w-full h-full object-cover"
                onError={() => setAvatarError(true)}
                onLoad={() => setAvatarError(false)}
              />
            ) : (
              <span className="text-sm font-medium text-primary-foreground">
                {user?.name?.charAt(0)?.toUpperCase() || 'U'}
              </span>
            )}
          </div>
          <span className="text-sm font-medium text-foreground hidden sm:inline">
            {user?.name || 'User'}
          </span>
        </button>

        {isDropdownOpen && (
          <div className="absolute right-0 mt-2 w-56 bg-card border border-border rounded-lg shadow-lg z-50 animate-fade-in">
            <div className="px-2 py-1.5 border-b border-border">
              <p className="text-sm font-medium text-foreground">{user?.name || 'User'}</p>
              <p className="text-xs text-muted-foreground">{user?.email || ''}</p>
            </div>

            <div className="py-1">
              <button
                onClick={() => {
                  setIsDropdownOpen(false);
                  // Settings action can be added here
                }}
                className="w-full flex items-center px-2 py-1.5 text-sm text-foreground hover:bg-accent hover:text-accent-foreground transition-colors cursor-pointer"
              >
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </button>
            </div>

            <div className="border-t border-border"></div>

            <div className="py-1">
              <button
                onClick={() => {
                  setIsDropdownOpen(false);
                  onLogout();
                }}
                className="w-full flex items-center px-2 py-1.5 text-sm text-destructive hover:bg-destructive/10 transition-colors cursor-pointer focus:text-destructive"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign out
              </button>
            </div>
          </div>
        )}
        </div>
      </div>
    </header>
  );
};
