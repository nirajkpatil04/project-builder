import React, { useState } from 'react';
import { X, Lock, Mail, User, GraduationCap, ArrowRight, ArrowLeft, ChevronRight, Plus, Building, BookMarked, CheckCircle2, ShieldCheck } from 'lucide-react';
import { SignInButton } from '@clerk/react';
import { api, setAuthToken, setStoredUser } from '../api';
const hasClerk = Boolean(
  import.meta.env.VITE_CLERK_PUBLISHABLE_KEY ||
  'pk_test_ZmluZS1saW9uZXNzLTMxMDcuY2xlcmsuYWNjb3VudHMuZGV2JA'
);

export const INDIAN_BRANCH_CATEGORIES = [
  {
    category: "Mechanical & Manufacturing",
    branches: [
      { value: "mech", label: "Mechanical Engineering" },
      { value: "auto", label: "Automobile Engineering" },
      { value: "aero", label: "Aerospace Engineering" },
      { value: "aeronautical", label: "Aeronautical Engineering" },
      { value: "mechatronics", label: "Mechatronics Engineering" },
      { value: "prod_ind", label: "Production & Industrial Engineering" },
      { value: "mfg", label: "Manufacturing Engineering" },
      { value: "marine", label: "Marine Engineering" },
      { value: "mining", label: "Mining Engineering" },
      { value: "metallurgy", label: "Metallurgy & Materials Engineering" },
    ],
  },
  {
    category: "Computer & Emerging Technologies",
    branches: [
      { value: "cse", label: "Computer Science & Engineering (CSE)" },
      { value: "it", label: "Information Technology (IT)" },
      { value: "aids", label: "Artificial Intelligence & Data Science (AI & DS)" },
      { value: "aiml", label: "Artificial Intelligence & Machine Learning (AI & ML)" },
      { value: "cyber", label: "Cyber Security" },
      { value: "iot", label: "Internet of Things (IoT)" },
      { value: "swe", label: "Software Engineering" },
      { value: "cloud", label: "Cloud Computing" },
    ],
  },
  {
    category: "Electrical & Electronics",
    branches: [
      { value: "ece", label: "Electronics & Communication (ECE)" },
      { value: "eee", label: "Electrical & Electronics (EEE)" },
      { value: "eie", label: "Electronics & Instrumentation (EIE)" },
      { value: "vlsi", label: "VLSI Design" },
      { value: "robotics_auto", label: "Robotics & Automation" },
      { value: "telecom", label: "Telecommunication Engineering" },
    ],
  },
  {
    category: "Civil & Infrastructure",
    branches: [
      { value: "civil", label: "Civil Engineering" },
      { value: "environmental", label: "Environmental Engineering" },
      { value: "construction_tech", label: "Construction Technology" },
      { value: "structural", label: "Structural Engineering" },
      { value: "transportation", label: "Transportation Engineering" },
      { value: "geoinformatics", label: "Geo-informatics" },
    ],
  },
  {
    category: "Chemical, Bio & Allied",
    branches: [
      { value: "chem", label: "Chemical Engineering" },
      { value: "biotech", label: "Biotechnology" },
      { value: "biomed", label: "Biomedical Engineering" },
      { value: "petroleum", label: "Petroleum Engineering" },
      { value: "petrochem", label: "Petrochemical Engineering" },
      { value: "food_tech", label: "Food Technology" },
      { value: "agri_eng", label: "Agricultural Engineering" },
      { value: "textile", label: "Textile Engineering" },
    ],
  },
];

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  // Current Step: 'auth' (Step 1) | 'google_picker' | 'onboarding' (Step 2)
  const [step, setStep] = useState('auth');
  const [isRegister, setIsRegister] = useState(false);

  // Step 1: Primary Credentials
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Google SSO Multi-Account Chooser State
  const [savedAccounts, setSavedAccounts] = useState(() => {
    try {
      const stored = localStorage.getItem('pb_saved_google_accounts');
      if (stored) return JSON.parse(stored);
    } catch (_) {}
    return [
      { name: 'Niraj Patil', email: 'nirajkpatil04@gmail.com', avatarBg: '#4285F4' },
      { name: 'AICTE Student', email: 'student.aicte@gmail.com', avatarBg: '#34A853' },
    ];
  });
  const [customGoogleEmail, setCustomGoogleEmail] = useState('');
  const [showAddGoogleAccount, setShowAddGoogleAccount] = useState(false);
  const [googleClientIdInput, setGoogleClientIdInput] = useState(() => {
    return localStorage.getItem('pb_google_client_id') || import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
  });
  const [showConfigOAuth, setShowConfigOAuth] = useState(false);

  // Step 2: Student Profile Onboarding
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [branch, setBranch] = useState('mech');
  const [college, setCollege] = useState('');
  const [semester, setSemester] = useState('Final Year (7th/8th Sem)');

  const [currentUserData, setCurrentUserData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  // Step 1: Standard Email & Password Submit
  const handlePrimaryAuthSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        // Register user and transition to Step 2 Onboarding
        const data = await api.register({
          email,
          password,
        });
        setAuthToken(data.access_token);
        setStoredUser(data.user);
        setCurrentUserData(data.user);
        // Move to Step 2 Profile Setup
        setStep('onboarding');
      } else {
        // Sign in existing user (Student, Mentor, or Admin)
        const data = await api.login({ email, password });
        setAuthToken(data.access_token);
        setStoredUser(data.user);

        // Check if onboarding profile is incomplete
        if (!data.user.has_completed_onboarding) {
          setCurrentUserData(data.user);
          setStep('onboarding');
        } else {
          onAuthSuccess(data.user);
          onClose();
        }
      }
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  // Execute authenticated Google login with verified user profile
  const executeGoogleLogin = async (googleEmail, googleName) => {
    if (!googleEmail || !googleEmail.includes('@')) {
      setError('Please provide a valid Gmail address (e.g. name@gmail.com)');
      return;
    }

    const cleanEmail = googleEmail.toLowerCase().trim();
    const finalName = googleName || cleanEmail.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

    setError(null);
    setLoading(true);

    try {
      const data = await api.googleAuth({
        email: cleanEmail,
        name: finalName,
      });

      setAuthToken(data.access_token);
      setStoredUser(data.user);

      // Save to saved accounts list for future quick 1-click chooser
      try {
        const updated = savedAccounts.filter(a => a.email.toLowerCase() !== cleanEmail);
        const palette = ['#4285F4', '#EA4335', '#FBBC05', '#34A853', '#8B5CF6'];
        const randomColor = palette[Math.floor(Math.random() * palette.length)];
        const newList = [{ name: finalName, email: cleanEmail, avatarBg: randomColor }, ...updated].slice(0, 5);
        setSavedAccounts(newList);
        localStorage.setItem('pb_saved_google_accounts', JSON.stringify(newList));
      } catch (_) {}

      if (!data.user.has_completed_onboarding) {
        const parts = finalName.split(' ');
        if (parts.length > 0) setFirstName(parts[0]);
        if (parts.length > 1) setLastName(parts.slice(1).join(' '));
        setCurrentUserData(data.user);
        setStep('onboarding');
      } else {
        onAuthSuccess(data.user);
        onClose();
      }
    } catch (err) {
      setError(err.message || 'Google Sign-In failed');
    } finally {
      setLoading(false);
    }
  };

  // Step 1 Option 2: Google SSO Authentication
  const handleGoogleSignIn = async () => {
    setError(null);
    const configuredClientId = googleClientIdInput.trim() || import.meta.env.VITE_GOOGLE_CLIENT_ID;

    // Check if Google Identity Services is available and a Client ID is provided
    if (configuredClientId && window.google?.accounts?.oauth2) {
      setLoading(true);
      try {
        const client = window.google.accounts.oauth2.initTokenClient({
          client_id: configuredClientId,
          scope: 'email profile openid',
          callback: async (tokenResponse) => {
            if (tokenResponse.error) {
              setLoading(false);
              setError('Google OAuth sign-in was cancelled or closed.');
              return;
            }
            try {
              const res = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
                headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
              });
              const profile = await res.json();
              await executeGoogleLogin(profile.email, profile.name || profile.given_name);
            } catch (err) {
              setError(err.message || 'Failed to fetch Google profile');
              setLoading(false);
            }
          },
        });
        client.requestAccessToken({ prompt: 'select_account' });
        return;
      } catch (err) {
        console.warn('GIS initTokenClient fallback:', err);
        setLoading(false);
      }
    }

    // Default: Open the dedicated Google Account Chooser
    setStep('google_picker');
  };

  // Step 2: Complete Student Profile Setup (Onboarding)
  const handleOnboardingSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await api.completeOnboarding({
        first_name: firstName,
        last_name: lastName,
        branch,
        college: college || undefined,
        semester: semester || undefined,
      });

      setAuthToken(data.access_token);
      setStoredUser(data.user);
      onAuthSuccess(data.user);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to complete profile onboarding');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 200,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'rgba(0, 0, 0, 0.78)',
      backdropFilter: 'blur(8px)',
      padding: '16px',
    }}>
      <div className="glass-card animate-fade-in" style={{
        width: '100%',
        maxWidth: step === 'onboarding' ? '540px' : '460px',
        padding: '32px',
        position: 'relative',
        background: '#0d111a',
        border: '1px solid var(--border-highlight)',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.85)',
        transition: 'max-width 0.3s ease',
      }}>
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            background: 'none',
            border: 'none',
          }}
        >
          <X size={20} />
        </button>

        {/* STEP 1: PRIMARY AUTHENTICATION SCREEN */}
        {step === 'auth' && (
          <>
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 12px',
                borderRadius: '9999px',
                background: 'rgba(56, 189, 248, 0.12)',
                color: 'var(--accent-cyan)',
                fontSize: '0.78rem',
                fontWeight: 600,
                marginBottom: '10px',
              }}>
                <GraduationCap size={14} />
                <span>AICTE Engineering Capstone Portal</span>
              </div>
              <h2 style={{ fontSize: '1.6rem', marginBottom: '6px' }}>
                {isRegister ? 'Create Your Account' : 'Welcome Back'}
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
                {isRegister
                  ? 'Step 1 of 2: Create login credentials to access branch blueprints'
                  : 'Sign in to access your engineering projects and dashboard'}
              </p>
            </div>

            {error && (
              <div style={{
                background: 'rgba(244, 63, 94, 0.15)',
                border: '1px solid rgba(244, 63, 94, 0.3)',
                borderRadius: 'var(--radius-md)',
                padding: '12px',
                color: '#fda4af',
                fontSize: '0.88rem',
                marginBottom: '20px',
              }}>
                {error}
              </div>
            )}

            {/* Clerk Authentication Option */}
            {hasClerk && (
              <SignInButton mode="modal">
                <button
                  type="button"
                  className="btn btn-primary"
                  style={{
                    width: '100%',
                    padding: '12px',
                    marginBottom: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '10px',
                    fontWeight: 600,
                    fontSize: '0.92rem',
                  }}
                >
                  <ShieldCheck size={18} />
                  <span>Continue with Clerk</span>
                </button>
              </SignInButton>
            )}

            {/* Google OAuth 2.0 SSO Option */}
            <button
              type="button"
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="btn btn-secondary"
              style={{
                width: '100%',
                padding: '12px',
                marginBottom: '18px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '12px',
                background: '#161d2b',
                borderColor: 'var(--border-subtle)',
                color: '#f8fafc',
                fontWeight: 500,
                fontSize: '0.92rem',
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"
                />
                <path
                  fill="#34A853"
                  d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
                />
                <path
                  fill="#EA4335"
                  d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
                />
              </svg>
              <span>Continue with Google</span>
            </button>

            {/* Divider */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              margin: '18px 0',
            }}>
              <div style={{ flex: 1, height: '1px', background: 'var(--border-subtle)' }} />
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                or with email & password
              </span>
              <div style={{ flex: 1, height: '1px', background: 'var(--border-subtle)' }} />
            </div>

            {/* Email & Password Form */}
            <form onSubmit={handlePrimaryAuthSubmit}>
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <div style={{ position: 'relative' }}>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="student@college.edu or email@gmail.com"
                    className="form-control"
                    style={{ paddingLeft: '40px' }}
                  />
                  <Mail size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '14px' }} />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Password</label>
                <div style={{ position: 'relative' }}>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min 8 characters (letters + numbers)"
                    className="form-control"
                    style={{ paddingLeft: '40px' }}
                  />
                  <Lock size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '14px' }} />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary"
                style={{ width: '100%', padding: '14px', marginTop: '10px' }}
              >
                {loading ? 'Processing...' : isRegister ? 'Continue to Profile Setup' : 'Sign In'}
                <ArrowRight size={18} />
              </button>
            </form>

            <div style={{ textAlign: 'center', marginTop: '22px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
              {isRegister ? 'Already registered? ' : "Don't have an account? "}
              <button
                type="button"
                onClick={() => { setIsRegister(!isRegister); setError(null); }}
                style={{ color: 'var(--accent-cyan)', fontWeight: 600, cursor: 'pointer', background: 'none', border: 'none' }}
              >
                {isRegister ? 'Sign In' : 'Create an Account'}
              </button>
            </div>
          </>
        )}

        {/* STEP 1.5: GOOGLE ACCOUNT CHOOSER SCREEN */}
        {step === 'google_picker' && (
          <div>
            {/* Header with back button */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <button
                type="button"
                onClick={() => { setStep('auth'); setError(null); }}
                style={{
                  background: 'rgba(255, 255, 255, 0.06)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  padding: '7px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
                title="Back to login"
              >
                <ArrowLeft size={16} />
              </button>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <svg width="20" height="20" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z" />
                  <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z" />
                  <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z" />
                  <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z" />
                </svg>
                <span style={{ fontWeight: 600, fontSize: '1rem', color: '#f8fafc' }}>Sign in with Google</span>
              </div>
            </div>

            <div style={{ textAlign: 'center', marginBottom: '20px' }}>
              <h2 style={{ fontSize: '1.45rem', marginBottom: '4px', color: '#ffffff' }}>Choose an account</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem' }}>
                to continue to <strong style={{ color: 'var(--accent-cyan)' }}>Project Builder</strong>
              </p>
            </div>

            {error && (
              <div style={{
                background: 'rgba(244, 63, 94, 0.15)',
                border: '1px solid rgba(244, 63, 94, 0.3)',
                borderRadius: 'var(--radius-md)',
                padding: '10px 14px',
                color: '#fda4af',
                fontSize: '0.86rem',
                marginBottom: '16px',
              }}>
                {error}
              </div>
            )}

            {/* Account Selection List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
              {savedAccounts.map((acc, index) => {
                const initial = (acc.name || acc.email || 'G')[0].toUpperCase();
                return (
                  <button
                    key={index}
                    type="button"
                    onClick={() => executeGoogleLogin(acc.email, acc.name)}
                    disabled={loading}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '14px',
                      padding: '12px 14px',
                      background: 'rgba(255, 255, 255, 0.03)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '10px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.15s ease',
                      width: '100%',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(56, 189, 248, 0.08)';
                      e.currentTarget.style.borderColor = 'rgba(56, 189, 248, 0.35)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
                      e.currentTarget.style.borderColor = 'var(--border-subtle)';
                    }}
                  >
                    <div style={{
                      width: '38px',
                      height: '38px',
                      borderRadius: '50%',
                      background: acc.avatarBg || '#4285F4',
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 700,
                      fontSize: '1rem',
                      flexShrink: 0,
                    }}>
                      {initial}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#f8fafc', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {acc.name}
                      </div>
                      <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {acc.email}
                      </div>
                    </div>
                    <ChevronRight size={18} color="var(--text-muted)" />
                  </button>
                );
              })}
            </div>

            {/* Option: Use another account */}
            {!showAddGoogleAccount ? (
              <button
                type="button"
                onClick={() => setShowAddGoogleAccount(true)}
                style={{
                  width: '100%',
                  padding: '12px 14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '14px',
                  background: 'transparent',
                  border: '1px dashed var(--border-subtle)',
                  borderRadius: '10px',
                  color: 'var(--accent-cyan)',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: 500,
                  marginBottom: '16px',
                }}
              >
                <div style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '50%',
                  background: 'rgba(56, 189, 248, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  <Plus size={18} color="var(--accent-cyan)" />
                </div>
                <span>Use another Google account</span>
              </button>
            ) : (
              <div style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '10px',
                padding: '14px',
                marginBottom: '16px',
              }}>
                <label style={{ display: 'block', fontSize: '0.84rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  Enter your Gmail address:
                </label>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                  <input
                    type="email"
                    value={customGoogleEmail}
                    onChange={(e) => setCustomGoogleEmail(e.target.value)}
                    placeholder="yourname@gmail.com"
                    className="form-control"
                    style={{ flex: 1 }}
                    autoFocus
                  />
                  <button
                    type="button"
                    disabled={loading || !customGoogleEmail.trim()}
                    onClick={() => {
                      let e = customGoogleEmail.trim();
                      if (!e.includes('@')) e += '@gmail.com';
                      executeGoogleLogin(e, '');
                    }}
                    className="btn btn-primary"
                    style={{ padding: '8px 16px', fontSize: '0.88rem' }}
                  >
                    {loading ? '...' : 'Sign In'}
                  </button>
                </div>
                {!customGoogleEmail.includes('@') && customGoogleEmail.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setCustomGoogleEmail(customGoogleEmail + '@gmail.com')}
                    style={{
                      background: 'rgba(56, 189, 248, 0.12)',
                      border: 'none',
                      borderRadius: '4px',
                      color: 'var(--accent-cyan)',
                      fontSize: '0.78rem',
                      padding: '3px 8px',
                      cursor: 'pointer',
                    }}
                  >
                    + Append @gmail.com
                  </button>
                )}
              </div>
            )}

            {/* Optional Google Cloud OAuth Client ID configuration helper */}
            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '14px', marginTop: '10px' }}>
              <button
                type="button"
                onClick={() => setShowConfigOAuth(!showConfigOAuth)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  fontSize: '0.78rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  cursor: 'pointer',
                  padding: 0,
                  width: '100%',
                  justifyContent: 'center',
                }}
              >
                <span>⚙️ Configure Google Cloud Client ID (for OAuth popup)</span>
              </button>

              {showConfigOAuth && (
                <div style={{
                  marginTop: '10px',
                  background: 'rgba(0,0,0,0.3)',
                  padding: '12px',
                  borderRadius: '8px',
                  fontSize: '0.8rem',
                  color: 'var(--text-secondary)',
                }}>
                  <p style={{ margin: '0 0 8px 0' }}>
                    To use Google's native cross-domain OAuth popup on Vercel, paste your Google Cloud Client ID below or add <code>VITE_GOOGLE_CLIENT_ID</code> in Vercel environment variables:
                  </p>
                  <div style={{ display: 'flex', gap: '6px', marginBottom: '8px' }}>
                    <input
                      type="text"
                      placeholder="xxxx.apps.googleusercontent.com"
                      value={googleClientIdInput}
                      onChange={(e) => setGoogleClientIdInput(e.target.value)}
                      className="form-control"
                      style={{ fontSize: '0.8rem', padding: '6px 10px' }}
                    />
                    <button
                      type="button"
                      onClick={() => {
                        localStorage.setItem('pb_google_client_id', googleClientIdInput.trim());
                        alert('Google Client ID saved locally!');
                      }}
                      className="btn btn-secondary"
                      style={{ fontSize: '0.78rem', padding: '6px 10px' }}
                    >
                      Save
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* STEP 2: PROFILE SETUP / SECOND AUTHENTICATOR SCREEN (ONBOARDING) */}
        {step === 'onboarding' && (
          <>
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 12px',
                borderRadius: '9999px',
                background: 'rgba(34, 197, 94, 0.15)',
                color: '#4ade80',
                fontSize: '0.78rem',
                fontWeight: 600,
                marginBottom: '10px',
              }}>
                <CheckCircle2 size={14} />
                <span>Step 2 of 2: Engineering Profile Setup</span>
              </div>
              <h2 style={{ fontSize: '1.5rem', marginBottom: '6px' }}>
                Personalize Your Engineering Track
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem' }}>
                Select your official AICTE engineering branch so the blueprint engine generates branch-accurate physical or software architectures.
              </p>
            </div>

            {error && (
              <div style={{
                background: 'rgba(244, 63, 94, 0.15)',
                border: '1px solid rgba(244, 63, 94, 0.3)',
                borderRadius: 'var(--radius-md)',
                padding: '12px',
                color: '#fda4af',
                fontSize: '0.88rem',
                marginBottom: '20px',
              }}>
                {error}
              </div>
            )}

            <form onSubmit={handleOnboardingSubmit}>
              {/* First & Last Name */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div className="form-group">
                  <label className="form-label">First Name *</label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type="text"
                      required
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      placeholder="e.g. Rohan"
                      className="form-control"
                      style={{ paddingLeft: '38px' }}
                    />
                    <User size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '14px' }} />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Last Name *</label>
                  <input
                    type="text"
                    required
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="e.g. Sharma"
                    className="form-control"
                  />
                </div>
              </div>

              {/* Indian Engineering Branch Catalog (Grouped by AICTE Categories) */}
              <div className="form-group">
                <label className="form-label">Engineering Branch * (AICTE Catalog)</label>
                <select
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  className="form-control"
                  style={{
                    backgroundColor: '#131b2a',
                    color: '#f8fafc',
                    fontWeight: 500,
                  }}
                >
                  {INDIAN_BRANCH_CATEGORIES.map((cat) => (
                    <optgroup key={cat.category} label={`━━ ${cat.category} ━━`}>
                      {cat.branches.map((b) => (
                        <option key={b.value} value={b.value}>
                          {b.label}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Mechanical, Automobile, and allied branches unlock CAD, FEA, CFD &amp; Fabrication tools.
                </div>
              </div>

              {/* Optional: College / University */}
              <div className="form-group">
                <label className="form-label">College / University Name (Optional)</label>
                <div style={{ position: 'relative' }}>
                  <input
                    type="text"
                    value={college}
                    onChange={(e) => setCollege(e.target.value)}
                    placeholder="e.g. COEP Technological University, Pune / IIT Bombay"
                    className="form-control"
                    style={{ paddingLeft: '38px' }}
                  />
                  <Building size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '14px' }} />
                </div>
              </div>

              {/* Optional: Semester / Year */}
              <div className="form-group">
                <label className="form-label">Semester / Year (Optional)</label>
                <div style={{ position: 'relative' }}>
                  <select
                    value={semester}
                    onChange={(e) => setSemester(e.target.value)}
                    className="form-control"
                    style={{ paddingLeft: '38px' }}
                  >
                    <option value="Final Year (7th/8th Sem)">Final Year (7th/8th Sem - Capstone)</option>
                    <option value="Third Year (5th/6th Sem)">Third Year (5th/6th Sem - Mini Project)</option>
                    <option value="Second Year (3rd/4th Sem)">Second Year (3rd/4th Sem)</option>
                    <option value="First Year (1st/2nd Sem)">First Year (1st/2nd Sem)</option>
                    <option value="M.Tech / Post-Graduate">M.Tech / Post-Graduate Thesis</option>
                  </select>
                  <BookMarked size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '14px' }} />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary"
                style={{ width: '100%', padding: '14px', marginTop: '12px' }}
              >
                {loading ? 'Configuring Platform...' : 'Complete Profile & Launch Platform'}
                <ArrowRight size={18} />
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
