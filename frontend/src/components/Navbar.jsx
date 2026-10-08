import React from 'react';
import { Layers, FolderGit2, ShieldCheck, LogIn, LogOut, BookOpen, FileCheck } from 'lucide-react';
import { getAuthToken } from '../api';

export default function Navbar({
  activeTab,
  setActiveTab,
  user,
  onOpenAuth,
  onLogout,
  onOpenTerms
}) {
  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      background: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border-subtle)',
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '64px',
      }}>
        {/* Logo */}
        <div
          onClick={() => setActiveTab('wizard')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            cursor: 'pointer',
          }}
        >
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--accent-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Layers size={18} color="white" />
          </div>
          <div>
            <span style={{
              fontSize: '1.15rem',
              fontWeight: 700,
              letterSpacing: '-0.02em',
              color: 'var(--text-primary)',
            }}>
              Project Builder
            </span>
            <span style={{
              display: 'block',
              fontSize: '0.7rem',
              color: 'var(--text-muted)',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
            }}>
              Engineering Capstone Architecture
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', gap: '6px' }}>
          <button
            onClick={() => setActiveTab('wizard')}
            className={`btn btn-sm ${activeTab === 'wizard' ? 'btn-primary' : 'btn-secondary'}`}
          >
            <span>Path Builder</span>
          </button>

          {user && (
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`btn btn-sm ${activeTab === 'dashboard' ? 'btn-primary' : 'btn-secondary'}`}
            >
              <FolderGit2 size={15} />
              <span>My Projects</span>
            </button>
          )}

          {user && (user.role === 'mentor' || user.role === 'admin') && (
            <button
              onClick={() => setActiveTab('mentor')}
              className={`btn btn-sm ${activeTab === 'mentor' ? 'btn-primary' : 'btn-secondary'}`}
            >
              <ShieldCheck size={15} />
              <span>{user.role === 'admin' ? 'Admin Panel' : 'Faculty Review'}</span>
            </button>
          )}

          {user && user.role === 'admin' && (
            <a
              href={`http://localhost:8000/docs?token=${getAuthToken() || ''}`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-sm btn-secondary"
              title="FastAPI Interactive Specifications (Admin Only)"
            >
              <BookOpen size={15} />
              <span>Admin API Docs</span>
            </a>
          )}

          <button
            onClick={onOpenTerms}
            className="btn btn-sm btn-secondary"
            title="Terms & Conditions"
          >
            <FileCheck size={15} />
            <span>T&amp;C</span>
          </button>
        </nav>

        {/* Auth CTA */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {user.full_name}
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '4px' }}>
                  <span className={`badge ${
                    user.role === 'admin' ? 'badge-advanced' : user.role === 'mentor' ? 'badge-cyan' : 'badge-beginner'
                  }`}>
                    {user.role}
                  </span>
                  {user.branch && (
                    <span className="badge badge-intermediate" style={{ textTransform: 'uppercase' }}>
                      {user.branch}
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={onLogout}
                className="btn btn-secondary btn-sm"
                title="Sign out"
              >
                <LogOut size={15} />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="btn btn-primary btn-sm"
            >
              <LogIn size={15} />
              <span>Sign In / Register</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
