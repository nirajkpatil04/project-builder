import React, { useState, useEffect } from 'react';
import {
  FolderGit2, Download, Printer, Trash2, ExternalLink,
  Calendar, CheckCircle, ArrowRight, Layers
} from 'lucide-react';
import { api } from '../api';
import BlueprintViewer from './BlueprintViewer';

export default function Dashboard({ user, onRequireAuth }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState(null);
  const [error, setError] = useState(null);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await api.getProjects();
      setProjects(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchProjects();
    }
  }, [user]);

  const handleOpenProject = async (id) => {
    try {
      setLoading(true);
      const detail = await api.getProject(id);
      setSelectedProject(detail);
    } catch (err) {
      alert(err.message || 'Failed to load project details');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProject = async (id, title) => {
    if (!window.confirm(`Are you sure you want to delete "${title}"?`)) return;
    try {
      await api.deleteProject(id);
      setProjects(projects.filter((p) => p.id !== id));
      if (selectedProject?.id === id) {
        setSelectedProject(null);
      }
    } catch (err) {
      alert(err.message || 'Failed to delete project');
    }
  };

  if (!user) {
    return (
      <div className="container" style={{ paddingTop: '60px', textAlign: 'center' }}>
        <div className="glass-card" style={{ padding: '48px', maxWidth: '540px', margin: '0 auto' }}>
          <FolderGit2 size={48} color="var(--accent-cyan)" style={{ margin: '0 auto 16px' }} />
          <h2 style={{ marginBottom: '12px' }}>Student Workspace</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Please sign in to view and manage your saved blueprints, track roadmaps, and receive mentor reviews.
          </p>
          <button onClick={onRequireAuth} className="btn btn-primary">
            Sign In / Register
          </button>
        </div>
      </div>
    );
  }

  if (selectedProject) {
    return (
      <div className="container" style={{ paddingTop: '24px' }}>
        <BlueprintViewer
          blueprint={selectedProject.blueprint}
          profile={selectedProject.profile}
          user={user}
          onBack={() => setSelectedProject(null)}
          onSaveSuccess={fetchProjects}
          onRequireAuth={onRequireAuth}
        />
      </div>
    );
  }

  return (
    <div className="container" style={{ paddingTop: '28px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '2rem' }}>My Saved Projects</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            Track progress, export blueprints, or share with your project guide.
          </p>
        </div>
      </div>

      {error && (
        <div style={{
          background: 'rgba(244, 63, 94, 0.15)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          borderRadius: 'var(--radius-md)',
          padding: '14px',
          color: '#fda4af',
          marginBottom: '24px',
        }}>
          {error}
        </div>
      )}

      {loading ? (
        <div className="glass-card" style={{ padding: '48px', textAlign: 'center' }}>
          <p style={{ color: 'var(--text-secondary)' }}>Loading your saved projects...</p>
        </div>
      ) : projects.length === 0 ? (
        <div className="glass-card" style={{ padding: '56px', textAlign: 'center', maxWidth: '640px', margin: '40px auto' }}>
          <FolderGit2 size={48} color="var(--accent-primary)" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>No saved projects yet</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Use the Path Builder wizard to generate a comprehensive AI project blueprint, then save it to your workspace.
          </p>
        </div>
      ) : (
        <div className="grid-2" style={{ gap: '20px' }}>
          {projects.map((p) => (
            <div
              key={p.id}
              className="glass-card"
              style={{
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span className={`badge badge-${p.level}`}>
                    {p.level.toUpperCase()} PATH
                  </span>
                  <span className={`badge ${
                    p.status === 'approved' ? 'badge-beginner' : p.status === 'revisions_needed' ? 'badge-amber' : 'badge-cyan'
                  }`}>
                    {p.status}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.25rem', marginBottom: '8px', color: 'var(--text-primary)' }}>
                  {p.title}
                </h3>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
                  Saved on {new Date(p.created_at).toLocaleDateString()} &bull; Owner: {p.owner_name}
                </div>

                {/* Progress bar */}
                <div style={{ marginBottom: '20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Roadmap Progress</span>
                    <strong style={{ color: 'var(--accent-emerald)' }}>{p.progress_pct}%</strong>
                  </div>
                  <div style={{
                    width: '100%',
                    height: '6px',
                    background: 'var(--bg-primary)',
                    borderRadius: 'var(--radius-sm)',
                    overflow: 'hidden',
                  }}>
                    <div style={{
                      width: `${p.progress_pct}%`,
                      height: '100%',
                      background: 'var(--gradient-brand)',
                    }} />
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div style={{
                display: 'flex',
                gap: '8px',
                borderTop: '1px solid var(--border-subtle)',
                paddingTop: '16px',
                flexWrap: 'wrap',
              }}>
                <button
                  onClick={() => handleOpenProject(p.id)}
                  className="btn btn-primary btn-sm"
                  style={{ flex: 1 }}
                >
                  <span>Open Blueprint</span>
                  <ArrowRight size={14} />
                </button>
                <a
                  href={api.getMarkdownExportUrl(p.id)}
                  download
                  className="btn btn-secondary btn-sm"
                  title="Download Markdown"
                >
                  <Download size={14} />
                </a>
                <a
                  href={api.getHtmlExportUrl(p.id)}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary btn-sm"
                  title="Print / Save PDF"
                >
                  <Printer size={14} />
                </a>
                <button
                  onClick={() => handleDeleteProject(p.id, p.title)}
                  className="btn btn-secondary btn-sm"
                  style={{ color: 'var(--accent-rose)' }}
                  title="Delete Project"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
