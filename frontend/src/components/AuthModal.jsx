import React, { useState } from 'react';
import { X, Lock, Mail, User, GraduationCap, ArrowRight, Building, BookMarked, CheckCircle2 } from 'lucide-react';
import { api, setAuthToken, setStoredUser } from '../api';

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
  // Current Step: 'auth' (Step 1) | 'onboarding' (Step 2)
  const [step, setStep] = useState('auth');
  const [isRegister, setIsRegister] = useState(false);

  // Step 1: Primary Credentials
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

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

  // Step 1 Option 2: Google SSO Authentication
  const handleGoogleSignIn = async () => {
    setError(null);
    setLoading(true);

    try {
      // In a production browser environment, invoke Google OAuth token flow
      // Prompt user for Google email if none entered yet
      let googleEmail = email && email.includes('@') ? email : prompt('Enter your Google Account email (e.g. yourname@gmail.com):', 'student.aicte@gmail.com');
      if (!googleEmail) {
        setLoading(false);
        return;
      }

      const googleName = googleEmail.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      const data = await api.googleAuth({
        email: googleEmail,
        name: googleName,
      });

      setAuthToken(data.access_token);
      setStoredUser(data.user);

      if (!data.user.has_completed_onboarding) {
        // Split name into first and last name if available
        const parts = googleName.split(' ');
        if (parts.length > 0) setFirstName(parts[0]);
        if (parts.length > 1) setLastName(parts.slice(1).join(' '));
        setCurrentUserData(data.user);
        setStep('onboarding');
      } else {
        onAuthSuccess(data.user);
        onClose();
      }
    } catch (err) {
      setError(err.message || 'Google SSO failed');
    } finally {
      setLoading(false);
    }
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
