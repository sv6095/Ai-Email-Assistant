import { useState, useRef, useEffect } from 'react';
import { LogOut, Mail, Settings } from 'lucide-react';

export const Header = ({ user, onLogout }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen]);

  return (
    <header className="header">
      <div className="header-left">
        <div className="header-logo">
          <Mail className="header-logo-icon" />
        </div>
        <div>
          <h1 className="header-title">MailAI Assistant</h1>
          <p className="header-subtitle">Connected to Gmail</p>
        </div>
      </div>
      <div className="header-dropdown" ref={dropdownRef}>
        <button
          className="header-user-button"
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        >
          <div className="header-avatar">
            {user.avatar ? (
              <img src={user.avatar} alt={user.name} className="header-avatar-image" />
            ) : (
              <div className="header-avatar-fallback">
                {user.name?.charAt(0) || 'U'}
              </div>
            )}
          </div>
          <span className="header-user-name">{user.name}</span>
        </button>
        {isDropdownOpen && (
          <div className="header-dropdown-content">
            <div className="header-dropdown-header">
              <p className="header-dropdown-name">{user.name}</p>
              <p className="header-dropdown-email">{user.email}</p>
            </div>
            <div className="header-dropdown-separator"></div>
            <button className="header-dropdown-item">
              <Settings className="header-dropdown-icon" />
              Settings
            </button>
            <div className="header-dropdown-separator"></div>
            <button
              className="header-dropdown-item header-dropdown-item-destructive"
              onClick={onLogout}
            >
              <LogOut className="header-dropdown-icon" />
              Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
