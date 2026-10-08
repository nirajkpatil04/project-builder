import React, { useState, useEffect } from 'react';
import {
  ShieldCheck, MessageSquare, Check, AlertCircle, User,
  FileText, ExternalLink, RefreshCw, BarChart3, Users
} from 'lucide-react';
import { api } from '../api';

export default function MentorPortal({ user, onRequireAuth }) {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [stats, setStats] = useState(null);
  const [usersList, setUsersList] = useState([]);
  const [activeSubTab, setActiveSubTab] = useState('projects');
  const [loading, setLoading] = useState(true);

  // Review submission state
  const [reviewDecision, setReviewDecision] = useState('approved');
  const [reviewComment, setReviewComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);
  const [reviewSuccess, setReviewSuccess] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [projData, statsData] = await Promise.all([
        api.getProjects(),
        api.getStats().catch(() => null),
      ]);
      setProjects(projData || []);
      setStats(statsData);

      if (user?.role === 'admin') {
        const uList = await api.getUsers().catch(() => []);
        setUsersList(uList || []);
      }
    } catch (err) {
      console.warn('Failed to load mentor portal data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user && (user.role === 'mentor' || user.role === 'admin')) {
      fetchData();
    }
  }, [user]);

  const handleOpenProject = async (id) => {
    try {
      const detail = await api.getProject(id);
      setSelectedProject(detail);
      setReviewComment('');
    } catch (err) {
      alert(err.message || 'Failed to open project');
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (!selectedProject || !reviewComment.trim()) return;
    setSubmittingReview(true);
    try {
      await api.submitReview(selectedProject.id, reviewDecision, reviewComment);
      setReviewSuccess(true);
      const updated = await api.getProject(selectedProject.id);
      setSelectedProject(updated);
      fetchData();
      setTimeout(() => setReviewSuccess(false), 3000);
    } catch (err) {
      alert(err.message || 'Failed to submit review');
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await api.updateUserStatus(userId, newRole, null);
      fetchData();
    } catch (err) {
      alert(err.message || 'Failed to update user role');
    }
  };

  if (!user || (user.role !== 'mentor' && user.role !== 'admin')) {
    return (
      <div className="container" style={{ paddingTop: '60px', textAlign: 'center' }}>
        <div className="glass-card" style={{ padding: '36px', maxWidth: '520px', margin: '0 auto' }}>
          <ShieldCheck size={36} color="var(--accent-rose)" style={{ margin: '0 auto 12px' }} />
          <h2>Faculty Review Portal</h2>
          <p style={{ color: 'var(--text-secondary)', margin: '12px 0 20px', fontSize: '0.9rem' }}>
            This section is reserved for department evaluators and faculty mentors.
            Please sign in with a Mentor or Admin account.
          </p>
          <button onClick={onRequireAuth} className="btn btn-primary btn-sm">
            Sign In with Faculty Account
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ paddingTop: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <span className="badge badge-cyan" style={{ marginBottom: '4px' }}>
            {user.role === 'admin' ? 'System Administrator' : 'Faculty Mentor'}
          </span>
          <h1 style={{ fontSize: '1.6rem' }}>
            {user.role === 'admin' ? 'Department Administration' : 'Project Guidance & Evaluation Panel'}
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Review student capstone projects, provide technical critiques, and approve milestone roadmaps.
          </p>
        </div>
        <button onClick={fetchData} className="btn btn-secondary btn-sm">
          <RefreshCw size={14} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Sub-tabs for admin */}
      {user.role === 'admin' && (
        <div style={{ display: 'flex', gap: '6px', marginBottom: '20px' }}>
          <button
            onClick={() => setActiveSubTab('projects')}
            className={`btn btn-sm ${activeSubTab === 'projects' ? 'btn-primary' : 'btn-secondary'}`}
          >
            <FileText size={14} />
            <span>Student Projects ({projects.length})</span>
          </button>
          <button
            onClick={() => setActiveSubTab('stats')}
            className={`btn btn-sm ${activeSubTab === 'stats' ? 'btn-primary' : 'btn-secondary'}`}
          >
            <BarChart3 size={14} />
            <span>Database Statistics</span>
          </button>
          <button
            onClick={() => setActiveSubTab('users')}
            className={`btn btn-sm ${activeSubTab === 'users' ? 'btn-primary' : 'btn-secondary'}`}
          >
            <Users size={14} />
            <span>User Directory ({usersList.length})</span>
          </button>
        </div>
      )}

      {/* SUB-TAB 1: PROJECTS QUEUE */}
      {activeSubTab === 'projects' && (
        <div className="grid-2" style={{ gap: '20px' }}>
          {/* Project List */}
          <div>
            <h3 style={{ fontSize: '1.05rem', marginBottom: '12px' }}>Student Submissions</h3>
            {loading ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>Loading project submissions...</p>
            ) : projects.length === 0 ? (
              <div className="glass-card" style={{ padding: '24px', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>No student projects submitted yet.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {projects.map((p) => {
                  const isSelected = selectedProject?.id === p.id;
                  return (
                    <div
                      key={p.id}
                      onClick={() => handleOpenProject(p.id)}
                      className="glass-card"
                      style={{
                        padding: '14px 16px',
                        cursor: 'pointer',
                        borderColor: isSelected ? 'var(--accent-primary)' : 'var(--border-subtle)',
                        background: isSelected ? 'var(--bg-tertiary)' : 'var(--bg-card)',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                        <span className={`badge badge-${p.level}`}>{p.level}</span>
                        <span className={`badge ${
                          p.status === 'approved' ? 'badge-beginner' : p.status === 'revisions_needed' ? 'badge-amber' : 'badge-cyan'
                        }`}>
                          {p.status}
                        </span>
                      </div>
                      <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '3px' }}>
                        {p.title}
                      </h4>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        Student: {p.owner_name} &bull; Progress: {p.progress_pct}%
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Project Detail & Review Form */}
          <div>
            {selectedProject ? (
              <div className="glass-card" style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <h3 style={{ fontSize: '1.05rem', color: 'var(--text-primary)' }}>Reviewing Project #{selectedProject.id}</h3>
                  <a
                    href={api.getHtmlExportUrl(selectedProject.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-secondary btn-sm"
                  >
                    <ExternalLink size={14} />
                    <span>View Blueprint Document</span>
                  </a>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: 'var(--radius-sm)', marginBottom: '16px' }}>
                  <h4 style={{ fontSize: '0.98rem', marginBottom: '4px' }}>{selectedProject.title}</h4>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    {selectedProject.blueprint?.problem_statement?.core_problem}
                  </p>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    Architecture: {selectedProject.blueprint?.architecture?.pattern}
                  </div>
                </div>

                {/* Review Form */}
                <form onSubmit={handleSubmitReview}>
                  <div className="form-group">
                    <label className="form-label">Evaluation Status</label>
                    <select
                      value={reviewDecision}
                      onChange={(e) => setReviewDecision(e.target.value)}
                      className="form-control"
                    >
                      <option value="approved">Approved: Proceed with Implementation</option>
                      <option value="changes_requested">Changes Requested: Requires Technical Refinement</option>
                      <option value="comment">Advisory Note</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Faculty Feedback and Technical Critique</label>
                    <textarea
                      rows={3}
                      required
                      value={reviewComment}
                      onChange={(e) => setReviewComment(e.target.value)}
                      placeholder="Specify technical critique, viva questions to expect, or architecture changes..."
                      className="form-control"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={submittingReview}
                    className="btn btn-primary btn-sm"
                    style={{ width: '100%' }}
                  >
                    {reviewSuccess ? (
                      <>
                        <Check size={14} />
                        <span>Feedback Recorded</span>
                      </>
                    ) : (
                      <>
                        <MessageSquare size={14} />
                        <span>{submittingReview ? 'Submitting...' : 'Record Evaluation'}</span>
                      </>
                    )}
                  </button>
                </form>

                {/* Existing Reviews History */}
                {selectedProject.reviews?.length > 0 && (
                  <div style={{ marginTop: '20px', paddingTop: '14px', borderTop: '1px solid var(--border-subtle)' }}>
                    <h4 style={{ fontSize: '0.88rem', marginBottom: '10px', color: 'var(--text-secondary)' }}>Logged Review History</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      {selectedProject.reviews.map((r) => (
                        <div key={r.id} style={{ background: 'var(--bg-tertiary)', padding: '8px 12px', borderRadius: 'var(--radius-sm)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '2px' }}>
                            <strong style={{ color: 'var(--text-primary)' }}>{r.reviewer_name}</strong>
                            <span className="badge badge-intermediate">{r.decision}</span>
                          </div>
                          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{r.comment}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="glass-card" style={{ padding: '36px', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>Select a project from the left queue to inspect and submit feedback.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SUB-TAB 2: ANALYTICS (ADMIN) */}
      {activeSubTab === 'stats' && stats && (
        <div>
          <div className="grid-3" style={{ gap: '16px', marginBottom: '24px' }}>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
                {stats.total_projects}
              </div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Total Projects Stored</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                {stats.total_users}
              </div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Active Accounts</div>
            </div>
            <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent-emerald)' }}>
                {stats.total_reviews}
              </div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Faculty Reviews Logged</div>
            </div>
          </div>
        </div>
      )}

      {/* SUB-TAB 3: USER DIRECTORY (ADMIN) */}
      {activeSubTab === 'users' && (
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '1.05rem', marginBottom: '14px' }}>User Role Management</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ background: 'var(--bg-secondary)', textAlign: 'left' }}>
                <th style={{ padding: '8px 12px', borderBottom: '1px solid var(--border-subtle)' }}>User</th>
                <th style={{ padding: '8px 12px', borderBottom: '1px solid var(--border-subtle)' }}>Email</th>
                <th style={{ padding: '8px 12px', borderBottom: '1px solid var(--border-subtle)' }}>Branch</th>
                <th style={{ padding: '8px 12px', borderBottom: '1px solid var(--border-subtle)' }}>Role</th>
                <th style={{ padding: '8px 12px', borderBottom: '1px solid var(--border-subtle)' }}>Modify Role</th>
              </tr>
            </thead>
            <tbody>
              {usersList.map((u) => (
                <tr key={u.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '8px 12px', fontWeight: 600 }}>{u.full_name}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--text-secondary)' }}>{u.email}</td>
                  <td style={{ padding: '8px 12px' }}><span className="badge badge-intermediate">{u.branch || 'N/A'}</span></td>
                  <td style={{ padding: '8px 12px' }}>
                    <span className={`badge ${
                      u.role === 'admin' ? 'badge-advanced' : u.role === 'mentor' ? 'badge-cyan' : 'badge-beginner'
                    }`}>
                      {u.role}
                    </span>
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      className="form-control"
                      style={{ padding: '4px 8px', fontSize: '0.8rem', width: 'auto' }}
                    >
                      <option value="student">Student</option>
                      <option value="mentor">Mentor</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
