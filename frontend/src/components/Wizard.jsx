import React, { useState, useEffect } from 'react';
import {
  ArrowRight, CheckCircle2, Clock, Users,
  Wallet, Layers, ChevronRight, SlidersHorizontal, FileText
} from 'lucide-react';
import { api } from '../api';
import BlueprintViewer from './BlueprintViewer';
import { INDIAN_BRANCH_CATEGORIES } from './AuthModal';

export default function Wizard({ user, onRequireAuth, onSaveSuccess }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [options, setOptions] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [selectedIdeaKey, setSelectedIdeaKey] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState('intermediate');
  const [blueprintData, setBlueprintData] = useState(null);
  const [error, setError] = useState(null);

  // Student Profile state
  const [goal, setGoal] = useState('Crop disease detection from plant leaf photos using deep learning');
  const [branch, setBranch] = useState(user?.branch || 'mech');
  const [skill, setSkill] = useState('intermediate');
  const [budget, setBudget] = useState('low');
  const [preference, setPreference] = useState('software');
  const [difficulty, setDifficulty] = useState('moderate');
  const [months, setMonths] = useState(4);
  const [teamSize, setTeamSize] = useState(2);
  const [selectedInterests, setSelectedInterests] = useState(['agriculture']);

  useEffect(() => {
    if (user?.branch) {
      setBranch(user.branch);
    }
  }, [user]);

  useEffect(() => {
    api.getOptions()
      .then((data) => setOptions(data))
      .catch((err) => console.warn('Failed to load options catalog:', err));
  }, []);

  const handleToggleInterest = (val) => {
    if (selectedInterests.includes(val)) {
      setSelectedInterests(selectedInterests.filter((i) => i !== val));
    } else {
      if (selectedInterests.length < 5) {
        setSelectedInterests([...selectedInterests, val]);
      }
    }
  };

  const handleFindPaths = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const profile = {
      goal,
      branch,
      skill,
      budget,
      preference,
      difficulty,
      months: Number(months),
      team_size: Number(teamSize),
      interests: selectedInterests,
    };

    try {
      const res = await api.getSuggestions(profile, 4);
      setSuggestions(res.suggestions || []);
      setStep(2);
    } catch (err) {
      setError(err.message || 'Failed to fetch project path suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBlueprint = async (ideaKey, level) => {
    setLoading(true);
    setError(null);
    setSelectedIdeaKey(ideaKey);
    setSelectedLevel(level);

    const profile = {
      goal,
      branch,
      skill,
      budget,
      preference,
      difficulty,
      months: Number(months),
      team_size: Number(teamSize),
      interests: selectedInterests,
    };

    try {
      const res = await api.generateBlueprint(profile, ideaKey, level, true);
      setBlueprintData(res);
      setStep(3);
    } catch (err) {
      setError(err.message || 'Failed to compile project blueprint');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ paddingTop: '24px' }}>
      {/* STEP 1: PARAMETER SPECIFICATION FORM */}
      {step === 1 && (
        <div className="glass-card" style={{ padding: '32px', maxWidth: '920px', margin: '0 auto' }}>
          <div style={{ marginBottom: '28px' }}>
            <span className="badge badge-cyan" style={{ marginBottom: '8px' }}>
              Project Specification
            </span>
            <h1 style={{ fontSize: '1.8rem', marginBottom: '8px' }}>
              Final-Year Engineering Project Builder
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              Specify your engineering discipline, technical constraints, budget, and timeline to generate
              structured project paths (Beginner -&gt; Intermediate -&gt; Advanced) with full technical specifications.
            </p>
          </div>

          {error && (
            <div style={{
              background: 'rgba(220, 38, 38, 0.15)',
              border: '1px solid rgba(220, 38, 38, 0.3)',
              borderRadius: 'var(--radius-sm)',
              padding: '12px',
              color: '#fca5a5',
              marginBottom: '20px',
              fontSize: '0.88rem',
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleFindPaths}>
            {/* Project Goal */}
            <div className="form-group">
              <label className="form-label">
                Problem Statement or Technical Objective
              </label>
              <textarea
                rows={3}
                required
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="Example: Real-time driver drowsiness detection using facial landmarks and an embedded alert module"
                className="form-control"
                style={{ resize: 'vertical' }}
              />
            </div>

            {/* Grid Parameters */}
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Department / Branch</label>
                <select
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  className="form-control"
                >
                  {(options?.branch_categories || INDIAN_BRANCH_CATEGORIES).map((cat) => (
                    <optgroup key={cat.category} label={`━━ ${cat.category} ━━`}>
                      {cat.branches.map((b) => (
                        <option key={b.value} value={b.value}>
                          {b.label}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Team Current Competency</label>
                <select
                  value={skill}
                  onChange={(e) => setSkill(e.target.value)}
                  className="form-control"
                >
                  <option value="beginner">Beginner: Core programming, new to advanced frameworks</option>
                  <option value="intermediate">Intermediate: Prior experience building web apps or models</option>
                  <option value="advanced">Advanced: Full-stack, neural network training and systems</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Budget Limit (Hardware + Cloud)</label>
                <select
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  className="form-control"
                >
                  <option value="zero">Zero Cost: Under Rs. 500 (Software Only)</option>
                  <option value="low">Low Budget: Rs. 500 - Rs. 3,000</option>
                  <option value="medium">Medium Budget: Rs. 3,000 - Rs. 12,000</option>
                  <option value="high">High Budget: Rs. 12,000+</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">System Architecture Preference</label>
                <select
                  value={preference}
                  onChange={(e) => setPreference(e.target.value)}
                  className="form-control"
                >
                  <option value="software">Software Only (Web / Desktop / API)</option>
                  <option value="hardware">Hardware Focused (Microcontroller / Sensors)</option>
                  <option value="hybrid">Hybrid (Edge IoT Device + Cloud Backend)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Target Difficulty</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="form-control"
                >
                  <option value="easy">Standard: Straightforward to implement and verify</option>
                  <option value="moderate">Moderate: Balanced engineering challenge with solid viva scope</option>
                  <option value="challenging">High: Research-grade and production-level complexity</option>
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div className="form-group">
                  <label className="form-label">Duration (Months)</label>
                  <select
                    value={months}
                    onChange={(e) => setMonths(Number(e.target.value))}
                    className="form-control"
                  >
                    {[1, 2, 3, 4, 5, 6, 8, 10, 12].map((m) => (
                      <option key={m} value={m}>{m} Months</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Team Size</label>
                  <select
                    value={teamSize}
                    onChange={(e) => setTeamSize(Number(e.target.value))}
                    className="form-control"
                  >
                    {[1, 2, 3, 4, 5, 6].map((s) => (
                      <option key={s} value={s}>{s} Student{s > 1 ? 's' : ''}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Application Sectors */}
            <div className="form-group" style={{ marginBottom: '24px' }}>
              <label className="form-label">Application Domain Tags (Select up to 4)</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
                {[
                  { id: 'agriculture', label: 'Agriculture' },
                  { id: 'healthcare', label: 'Healthcare' },
                  { id: 'education', label: 'Education' },
                  { id: 'smart-city', label: 'Smart City & Transport' },
                  { id: 'security', label: 'Security & Surveillance' },
                  { id: 'accessibility', label: 'Accessibility' },
                  { id: 'environment', label: 'Environment' },
                  { id: 'finance', label: 'Finance' },
                  { id: 'energy', label: 'Energy' },
                  { id: 'manufacturing', label: 'Manufacturing' },
                  { id: 'developer-tools', label: 'Developer Systems' },
                ].map((item) => {
                  const isSelected = selectedInterests.includes(item.id);
                  return (
                    <button
                      type="button"
                      key={item.id}
                      onClick={() => handleToggleInterest(item.id)}
                      className={`btn btn-sm ${isSelected ? 'btn-primary' : 'btn-secondary'}`}
                    >
                      {item.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary btn-lg"
              style={{ width: '100%' }}
            >
              {loading ? (
                <span>Evaluating Constraints...</span>
              ) : (
                <>
                  <span>Generate Recommended Paths</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>
        </div>
      )}

      {/* STEP 2: PATH RECOMMENDATIONS */}
      {step === 2 && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <div>
              <button
                onClick={() => setStep(1)}
                className="btn btn-secondary btn-sm"
                style={{ marginBottom: '6px' }}
              >
                <ChevronRight size={14} style={{ transform: 'rotate(180deg)' }} />
                <span>Adjust Parameters</span>
              </button>
              <h1 style={{ fontSize: '1.6rem' }}>
                Compatible Project Paths
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                Progression scopes from Beginner to Advanced. Select the tier appropriate for your team.
              </p>
            </div>
          </div>

          {loading && (
            <div className="glass-card" style={{ padding: '36px', textAlign: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '6px' }}>Compiling Engineering Blueprint</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
                Generating architecture, 22 technical dimensions, database schemas, roadmap, and defense specifications.
              </p>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {suggestions.map((idea) => (
              <div
                key={idea.key}
                className="glass-card"
                style={{ padding: '24px' }}
              >
                <div style={{ marginBottom: '14px' }}>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '6px' }}>
                    <span className="badge badge-cyan">
                      Fit: {idea.type.toUpperCase()}
                    </span>
                    {idea.domains?.map((d) => (
                      <span key={d.value} className="badge badge-intermediate">
                        {d.label}
                      </span>
                    ))}
                  </div>
                  <h2 style={{ fontSize: '1.4rem', marginBottom: '4px' }}>{idea.title}</h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>{idea.tagline}</p>
                </div>

                {/* Match Reasons */}
                {idea.reasons?.length > 0 && (
                  <div style={{
                    background: 'var(--bg-secondary)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '10px 14px',
                    marginBottom: '20px',
                    borderLeft: '3px solid var(--accent-primary)',
                  }}>
                    <strong style={{ fontSize: '0.8rem', color: 'var(--text-primary)', textTransform: 'uppercase' }}>
                      Profile Alignment:
                    </strong>
                    <ul style={{ paddingLeft: '16px', fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                      {idea.reasons.map((r, i) => (
                        <li key={i}>{r}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 3 Tiers */}
                <div className="grid-3">
                  {idea.path?.map((tier) => (
                    <div
                      key={tier.level}
                      style={{
                        background: 'var(--bg-secondary)',
                        border: tier.recommended ? '1px solid var(--accent-primary)' : '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '16px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                          <span className={`badge badge-${tier.level}`}>{tier.level_label}</span>
                          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                            Cost: Rs. {tier.cost_inr?.toLocaleString()}
                          </span>
                        </div>
                        <h4 style={{ fontSize: '0.98rem', marginBottom: '6px', color: 'var(--text-primary)' }}>
                          {tier.title}
                        </h4>
                        <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                          {tier.summary}
                        </p>

                        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '8px', marginBottom: '12px' }}>
                          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                            Included Scope:
                          </span>
                          <ul style={{ paddingLeft: '14px', fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                            {tier.features?.map((f, i) => (
                              <li key={i} style={{ marginBottom: '2px' }}>{f}</li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      <div>
                        {tier.feasibility && (
                          <div style={{
                            fontSize: '0.75rem',
                            color: tier.feasibility.label === 'Risky' ? 'var(--accent-rose)' : 'var(--accent-emerald)',
                            marginBottom: '10px',
                            fontWeight: 600,
                          }}>
                            Effort: {tier.feasibility.effort_person_weeks} person-weeks ({tier.feasibility.label})
                          </div>
                        )}
                        <button
                          onClick={() => handleGenerateBlueprint(idea.key, tier.level)}
                          disabled={loading}
                          className={`btn ${tier.recommended ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                          style={{ width: '100%' }}
                        >
                          <span>Select {tier.level_label}</span>
                          <ArrowRight size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* STEP 3: FULL BLUEPRINT RENDER */}
      {step === 3 && blueprintData && (
        <BlueprintViewer
          blueprint={blueprintData.blueprint}
          profile={blueprintData.profile}
          user={user}
          onBack={() => setStep(2)}
          onSaveSuccess={onSaveSuccess}
          onRequireAuth={onRequireAuth}
        />
      )}
    </div>
  );
}
