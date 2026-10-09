import React, { useState, useEffect } from 'react';
import { useUser } from '@clerk/react';
import Navbar from './components/Navbar';
import Wizard from './components/Wizard';
import Dashboard from './components/Dashboard';
import MentorPortal from './components/MentorPortal';
import AuthModal from './components/AuthModal';
import TermsModal from './components/TermsModal';
import { api, getStoredUser, setAuthToken, setStoredUser } from './api';

const hasClerk = Boolean(
  import.meta.env.VITE_CLERK_PUBLISHABLE_KEY ||
  'pk_test_ZmluZS1saW9uZXNzLTMxMDcuY2xlcmsuYWNjb3VudHMuZGV2JA'
);

function ClerkSessionSync({ onUserSynced }) {
  const { isLoaded, isSignedIn, user: clerkUser } = useUser();

  useEffect(() => {
    if (isLoaded && isSignedIn && clerkUser) {
      const email = clerkUser.primaryEmailAddress?.emailAddress;
      const name = clerkUser.fullName || email?.split('@')[0];
      if (email) {
        api.googleAuth({ email, name })
          .then((data) => {
            setAuthToken(data.access_token);
            setStoredUser(data.user);
            onUserSynced(data.user);
          })
          .catch((err) => {
            console.warn('Could not sync Clerk user with backend:', err);
          });
      }
    }
  }, [isLoaded, isSignedIn, clerkUser]);

  return null;
}

export default function App() {
  const [activeTab, setActiveTab] = useState('wizard');
  const [user, setUser] = useState(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isTermsOpen, setIsTermsOpen] = useState(false);

  useEffect(() => {
    // Check local session
    const stored = getStoredUser();
    if (stored) {
      setUser(stored);
      // Validate token with backend in background
      api.getMe()
        .then((fresh) => {
          setUser(fresh);
          setStoredUser(fresh);
        })
        .catch(() => {
          // Token expired or invalid
          setAuthToken(null);
          setStoredUser(null);
          setUser(null);
        });
    }
  }, []);

  const handleLogout = () => {
    setAuthToken(null);
    setStoredUser(null);
    setUser(null);
    setActiveTab('wizard');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {hasClerk && <ClerkSessionSync onUserSynced={setUser} />}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
        onOpenTerms={() => setIsTermsOpen(true)}
      />

      <main style={{ flex: 1 }}>
        {activeTab === 'wizard' && (
          <Wizard
            user={user}
            onRequireAuth={() => setIsAuthOpen(true)}
            onSaveSuccess={() => {}}
          />
        )}

        {activeTab === 'dashboard' && (
          <Dashboard
            user={user}
            onRequireAuth={() => setIsAuthOpen(true)}
          />
        )}

        {activeTab === 'mentor' && (
          <MentorPortal
            user={user}
            onRequireAuth={() => setIsAuthOpen(true)}
          />
        )}
      </main>

      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        background: 'var(--bg-primary)',
        padding: '24px 0',
        marginTop: '60px',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: '0.85rem',
      }}>
        <div className="container">
          <p>
            Project Builder &bull; Autonomous Architecture &amp; Engineering Blueprint Platform for Final-Year Projects.
          </p>
          <p style={{ marginTop: '4px', fontSize: '0.78rem' }}>
            Supports all 22 engineering disciplines, MLOps, IEEE documentation, Git workflows, and viva voce defense.
          </p>
          <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'center', gap: '16px', alignItems: 'center' }}>
            <button
              onClick={() => setIsTermsOpen(true)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--accent-cyan)',
                fontSize: '0.78rem',
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              Terms &amp; Conditions
            </button>
            <span style={{ color: 'var(--text-muted)' }}>&bull;</span>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Custom Domain: projectbuilder.dev
            </span>
          </div>
        </div>
      </footer>

      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={(newUser) => setUser(newUser)}
      />

      <TermsModal
        isOpen={isTermsOpen}
        onClose={() => setIsTermsOpen(false)}
      />
    </div>
  );
}
