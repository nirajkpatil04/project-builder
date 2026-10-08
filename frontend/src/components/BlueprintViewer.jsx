import React, { useState } from 'react';
import {
  FileText, Cpu, Layers, Database, Calendar, GitBranch,
  BookOpen, CheckSquare, Presentation, HelpCircle, Download,
  Printer, Save, Check, ArrowLeft, ExternalLink, ShieldAlert,
  Server, Lock, BrainCircuit, Activity, Wrench, Package,
  SlidersHorizontal, CheckCircle2, AlertTriangle, ShieldCheck
} from 'lucide-react';
import MermaidViewer from './MermaidViewer';
import { api } from '../api';

export default function BlueprintViewer({
  blueprint,
  profile,
  user,
  onBack,
  onSaveSuccess,
  onRequireAuth
}) {
  const [activeTab, setActiveTab] = useState('overview');
  const [completedTasks, setCompletedTasks] = useState(new Set());
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [expandedViva, setExpandedViva] = useState(0);

  if (!blueprint) return null;

  const isPhysical = Boolean(blueprint?.is_physical_engineering);

  const toggleTask = (taskId) => {
    const next = new Set(completedTasks);
    if (next.has(taskId)) {
      next.delete(taskId);
    } else {
      next.add(taskId);
    }
    setCompletedTasks(next);
  };

  const handleSave = async () => {
    if (!user) {
      onRequireAuth();
      return;
    }
    setSaving(true);
    try {
      await api.saveProject(blueprint, profile);
      setSavedSuccess(true);
      if (onSaveSuccess) onSaveSuccess();
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert(err.message || 'Failed to save project');
    } finally {
      setSaving(false);
    }
  };

  const handleDownloadMarkdown = () => {
    let md = `# ${blueprint.title}\n\n`;
    md += `**Tier:** ${blueprint.level_label} - ${blueprint.tier_title}\n`;
    md += `**Tagline:** ${blueprint.tagline}\n`;
    md += `**Estimated Cost:** ₹${blueprint.estimated_cost_inr?.toLocaleString()}\n`;
    md += `**Discipline:** ${isPhysical ? 'Physical & Fabrication Engineering' : 'Software & AI Systems'}\n\n`;
    md += `## 1. Problem Statement\n${blueprint.problem_statement?.core_problem}\n\n`;
    md += `## 2. Architecture Pattern\n${blueprint.architecture?.pattern}\n\n`;
    md += `\`\`\`mermaid\n${blueprint.architecture?.mermaid_diagram}\n\`\`\`\n\n`;

    if (isPhysical && blueprint.cad_modeling) {
      md += `## 3. CAD 3D Modeling\n`;
      md += `- Primary Tool: ${blueprint.cad_modeling.primary_cad_tool}\n`;
      md += `- Approach: ${blueprint.cad_modeling.modeling_approach}\n\n`;
    }

    if (isPhysical && blueprint.mechanical_bom) {
      md += `## 4. Mechanical BOM\n`;
      blueprint.mechanical_bom.forEach(b => {
        md += `- ${b.item} (${b.category}): ₹${b.approx_price_inr} [${b.indian_source}]\n`;
      });
      md += `\n`;
    }

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${blueprint.idea_key}_blueprint.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  const physicalTabs = [
    { id: 'overview', label: '1. Overview & Problem', icon: FileText },
    { id: 'architecture', label: '2. Kinematics & Structure', icon: Cpu },
    { id: 'cad', label: '3. CAD 3D Modeling', icon: Layers },
    { id: 'fea', label: '4. FEA & CFD Simulation', icon: Activity },
    { id: 'materials', label: '5. Materials & Properties', icon: Package },
    { id: 'fabrication', label: '6. Fabrication Plan', icon: Wrench },
    { id: 'bom', label: '7. Mechanical BOM (₹)', icon: SlidersHorizontal },
    { id: 'gdt', label: '8. GD&T & Tolerances', icon: CheckSquare },
    ...(blueprint.embedded_sensors ? [{ id: 'sensors', label: '9. Embedded Sensors', icon: Cpu }] : []),
    { id: 'technologies', label: '10. Physical Disciplines', icon: Server },
    { id: 'roadmap', label: '11. Workshop Roadmap', icon: Calendar },
    { id: 'documentation', label: '12. Thesis Documentation', icon: BookOpen },
    { id: 'testing', label: '13. Physical Testing', icon: CheckSquare },
    { id: 'presentation', label: '14. Pitch Deck', icon: Presentation },
    { id: 'viva', label: '15. Viva Voce Defense', icon: HelpCircle },
  ];

  const softwareTabs = [
    { id: 'overview', label: '1. Overview & Problem', icon: FileText },
    { id: 'architecture', label: '2. Architecture & Flow', icon: Cpu },
    { id: 'technologies', label: '3. 22 Tech Dimensions', icon: Server },
    { id: 'modules', label: '4. System Modules', icon: Layers },
    { id: 'database', label: '5. Database & ER', icon: Database },
    { id: 'roadmap', label: '6. Roadmap & Progress', icon: Calendar },
    { id: 'git', label: '7. Git Workflow', icon: GitBranch },
    { id: 'documentation', label: '8. IEEE Docs Guide', icon: BookOpen },
    { id: 'testing', label: '9. Testing Strategy', icon: CheckSquare },
    { id: 'presentation', label: '10. Pitch Deck', icon: Presentation },
    { id: 'viva', label: '11. Viva Defense', icon: HelpCircle },
  ];

  const tabs = isPhysical ? physicalTabs : softwareTabs;

  return (
    <div style={{ paddingBottom: '60px' }}>
      {/* Top Banner & Action Controls */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '20px' }}>
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '14px',
        }}>
          <div>
            <button
              onClick={onBack}
              className="btn btn-secondary btn-sm"
              style={{ marginBottom: '10px' }}
            >
              <ArrowLeft size={14} />
              <span>Back to Selection</span>
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '6px' }}>
              <span className={`badge badge-${blueprint.level}`}>
                {blueprint.level_label} Tier
              </span>
              <span className={`badge ${isPhysical ? 'badge-amber' : 'badge-cyan'}`}>
                {isPhysical ? 'PHYSICAL & FABRICATION' : blueprint.type?.toUpperCase()}
              </span>
              {isPhysical && (
                <span className="badge badge-emerald">
                  FABRICATION-FIRST
                </span>
              )}
            </div>
            <h1 style={{ fontSize: '1.6rem', marginBottom: '4px' }}>{blueprint.title}</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', maxWidth: '850px' }}>
              <strong style={{ color: 'var(--text-primary)' }}>{blueprint.tier_title}:</strong> {blueprint.tagline}
            </p>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              onClick={handleSave}
              disabled={saving}
              className="btn btn-primary btn-sm"
            >
              {savedSuccess ? <Check size={14} color="white" /> : <Save size={14} />}
              <span>{savedSuccess ? 'Saved' : saving ? 'Saving...' : 'Save Blueprint'}</span>
            </button>
            <button
              onClick={handleDownloadMarkdown}
              className="btn btn-secondary btn-sm"
            >
              <Download size={14} />
              <span>Export .MD</span>
            </button>
            <button
              onClick={handlePrint}
              className="btn btn-secondary btn-sm"
            >
              <Printer size={14} />
              <span>Print / PDF</span>
            </button>
          </div>
        </div>
      </div>

      {/* Sub-Tabs Bar */}
      <div style={{
        display: 'flex',
        overflowX: 'auto',
        gap: '4px',
        paddingBottom: '6px',
        marginBottom: '20px',
        borderBottom: '1px solid var(--border-subtle)',
      }}>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`btn btn-sm ${isActive ? 'btn-primary' : 'btn-secondary'}`}
              style={{
                padding: '6px 12px',
                fontSize: '0.82rem',
                whiteSpace: 'nowrap',
              }}
            >
              <Icon size={14} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: OVERVIEW & PROBLEM STATEMENT */}
      {activeTab === 'overview' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          {blueprint.mentor_advice && (
            <div style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-highlight)',
              borderRadius: 'var(--radius-sm)',
              padding: '16px',
              marginBottom: '24px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <BrainCircuit size={16} color="var(--accent-cyan)" />
                <h3 style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>Technical Advisory Note</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6' }}>
                {blueprint.mentor_advice}
              </p>
              {blueprint.examiner_focus_areas?.length > 0 && (
                <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)' }}>
                  <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--accent-amber)', textTransform: 'uppercase' }}>
                    Evaluation Checklist:
                  </span>
                  <ul style={{ marginTop: '4px', paddingLeft: '16px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    {blueprint.examiner_focus_areas.map((tip, idx) => (
                      <li key={idx} style={{ marginBottom: '3px' }}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <h2 style={{ fontSize: '1.3rem', marginBottom: '14px' }}>1. Problem Statement &amp; Objectives</h2>
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '6px' }}>Context</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
              {blueprint.problem_statement?.background}
            </p>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '6px' }}>Engineering Problem</h3>
            <p style={{ color: 'var(--text-primary)', fontSize: '0.92rem', background: 'var(--bg-secondary)', padding: '12px 16px', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--accent-primary)' }}>
              {blueprint.problem_statement?.core_problem}
            </p>
          </div>

          <div className="grid-2">
            <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
              <h3 style={{ fontSize: '0.95rem', color: 'var(--accent-emerald)', marginBottom: '8px' }}>Project Objectives</h3>
              <ul style={{ paddingLeft: '16px', color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
                {blueprint.problem_statement?.objectives?.map((obj, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{obj}</li>
                ))}
              </ul>
            </div>

            <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
              <h3 style={{ fontSize: '0.95rem', color: 'var(--accent-amber)', marginBottom: '8px' }}>Measurable Targets</h3>
              <ul style={{ paddingLeft: '16px', color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
                {blueprint.problem_statement?.success_metrics?.map((metric, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{metric}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: ARCHITECTURE & MERMAID */}
      {activeTab === 'architecture' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>
            2. {isPhysical ? 'Kinematic Transmission & Structural Architecture' : 'System Architecture & Data Flow'}
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '12px', fontSize: '0.9rem' }}>
            <strong>Pattern:</strong> {blueprint.architecture?.pattern}
          </p>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '20px', fontSize: '0.9rem' }}>
            {blueprint.architecture?.overview}
          </p>

          <MermaidViewer
            chartCode={blueprint.architecture?.mermaid_diagram}
            title={isPhysical ? "Mechanical Kinematic & Structural Diagram" : "System Architecture Diagram"}
          />

          <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginTop: '24px', marginBottom: '10px' }}>
            {isPhysical ? 'End-to-End Operational Kinematic Flow' : 'Data Flow Walkthrough'}
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {blueprint.architecture?.data_flow_steps?.map((step, i) => (
              <div key={i} style={{
                background: 'var(--bg-secondary)',
                padding: '10px 14px',
                borderRadius: 'var(--radius-sm)',
                borderLeft: '2px solid var(--accent-cyan)',
                color: 'var(--text-secondary)',
                fontSize: '0.88rem',
              }}>
                {step}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB: CAD 3D MODELING & KINEMATICS (Physical Only) */}
      {activeTab === 'cad' && isPhysical && blueprint.cad_modeling && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>3. CAD 3D Modeling &amp; Kinematics</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '16px', fontSize: '0.88rem' }}>
            Primary Suite: <strong style={{ color: 'var(--accent-cyan)' }}>{blueprint.cad_modeling.primary_cad_tool}</strong> | Strategy: {blueprint.cad_modeling.modeling_approach}
          </p>

          <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '10px' }}>Subassembly Mating Hierarchy</h3>
          <div style={{ overflowX: 'auto', marginBottom: '24px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
              <thead>
                <tr style={{ background: 'var(--bg-secondary)', textAlign: 'left' }}>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Subassembly</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Parts Count</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Primary Material</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Mating Constraints</th>
                </tr>
              </thead>
              <tbody>
                {blueprint.cad_modeling.assemblies?.map((sub, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--text-primary)' }}>{sub.subassembly_name}</td>
                    <td style={{ padding: '10px' }}><span className="badge badge-intermediate">{sub.components_count} parts</span></td>
                    <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>{sub.primary_material}</td>
                    <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>{sub.mating_constraints}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {blueprint.cad_modeling.kinematic_analysis && (
            <div style={{ background: 'var(--bg-secondary)', padding: '18px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <h3 style={{ fontSize: '1rem', color: 'var(--accent-emerald)', marginBottom: '10px' }}>Kinematic Synthesis &amp; Degree of Freedom</h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                <strong style={{ color: 'var(--text-primary)' }}>Degrees of Freedom:</strong> {blueprint.cad_modeling.kinematic_analysis.degrees_of_freedom}
              </p>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                <strong style={{ color: 'var(--text-primary)' }}>Motion Simulation:</strong> {blueprint.cad_modeling.kinematic_analysis.motion_study}
              </p>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                <strong style={{ color: 'var(--text-primary)' }}>Interference Check:</strong> {blueprint.cad_modeling.kinematic_analysis.collision_check}
              </p>
              <div style={{ marginTop: '10px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Drafting Standard: {blueprint.cad_modeling.drawing_standards}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB: FEA & CFD SIMULATION (Physical Only) */}
      {activeTab === 'fea' && isPhysical && blueprint.fea_cfd_simulation && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>4. FEA &amp; CFD Stress Simulation</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '20px', fontSize: '0.88rem' }}>
            Solver: <strong style={{ color: 'var(--accent-cyan)' }}>{blueprint.fea_cfd_simulation.simulation_software}</strong> | Mesh: {blueprint.fea_cfd_simulation.meshing_methodology}
          </p>

          {/* Stress Results Highlight Grid */}
          {blueprint.fea_cfd_simulation.stress_results && (
            <div className="grid-2" style={{ gap: '16px', marginBottom: '24px' }}>
              <div style={{ background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.25)', padding: '18px', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', textTransform: 'uppercase', fontWeight: 600 }}>Factor of Safety (FOS)</span>
                <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#38bdf8', margin: '6px 0' }}>
                  {blueprint.fea_cfd_simulation.stress_results.calculated_factor_of_safety}
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Certified safe for cyclic dynamic loading (AICTE guideline: FOS ≥ 2.0).
                </p>
              </div>

              <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', padding: '18px', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--accent-emerald)', textTransform: 'uppercase', fontWeight: 600 }}>von Mises Stress vs Yield</span>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', margin: '6px 0' }}>
                  {blueprint.fea_cfd_simulation.stress_results.max_von_mises_stress_mpa} MPa <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>/ {blueprint.fea_cfd_simulation.stress_results.material_yield_strength_mpa} MPa</span>
                </div>
                <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
                  Max elastic deflection: {blueprint.fea_cfd_simulation.stress_results.max_deformation_mm} mm. Hotspot: {blueprint.fea_cfd_simulation.stress_results.critical_hotspot}.
                </p>
              </div>
            </div>
          )}

          {/* Modal Vibration & CFD */}
          <div className="grid-2" style={{ gap: '16px' }}>
            {blueprint.fea_cfd_simulation.modal_frequency_analysis && (
              <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
                <h3 style={{ fontSize: '0.95rem', color: 'var(--accent-amber)', marginBottom: '8px' }}>Modal Dynamic Frequency</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  <strong>Mode 1 Natural Freq:</strong> {blueprint.fea_cfd_simulation.modal_frequency_analysis.mode_1_natural_frequency_hz} Hz
                </p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  <strong>Operating Harmonics:</strong> {blueprint.fea_cfd_simulation.modal_frequency_analysis.operating_excitation_frequency_hz} Hz
                </p>
                <p style={{ fontSize: '0.85rem', color: 'var(--accent-emerald)' }}>
                  {blueprint.fea_cfd_simulation.modal_frequency_analysis.resonance_risk}
                </p>
              </div>
            )}

            {blueprint.fea_cfd_simulation.cfd_analysis && (
              <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
                <h3 style={{ fontSize: '0.95rem', color: 'var(--accent-cyan)', marginBottom: '8px' }}>CFD Aerodynamic Simulation</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  <strong>Tool:</strong> {blueprint.fea_cfd_simulation.cfd_analysis.cfd_tool} (Velocity: {blueprint.fea_cfd_simulation.cfd_analysis.inlet_velocity_ms} m/s)
                </p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  <strong>Drag Coeff (Cd):</strong> {blueprint.fea_cfd_simulation.cfd_analysis.calculated_drag_coefficient_cd} (L/D: {blueprint.fea_cfd_simulation.cfd_analysis.lift_drag_ratio})
                </p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {blueprint.fea_cfd_simulation.cfd_analysis.findings}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB: MATERIALS & PROPERTIES (Physical Only) */}
      {activeTab === 'materials' && isPhysical && blueprint.material_selection && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>5. Material Selection &amp; Properties</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.88rem' }}>
            Selection Framework: {blueprint.material_selection.selection_framework}
          </p>

          <div style={{ overflowX: 'auto', marginBottom: '20px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.86rem' }}>
              <thead>
                <tr style={{ background: 'var(--bg-secondary)', textAlign: 'left' }}>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Material</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Application</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Density (g/cm³)</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Yield (MPa)</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Modulus (GPa)</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Indian Cost (₹/kg)</th>
                </tr>
              </thead>
              <tbody>
                {blueprint.material_selection.selected_materials?.map((m, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--text-primary)' }}>{m.material_name}</td>
                    <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>{m.application}</td>
                    <td style={{ padding: '10px' }}>{m.density_g_cm3}</td>
                    <td style={{ padding: '10px', color: 'var(--accent-cyan)' }}>{m.yield_strength_mpa}</td>
                    <td style={{ padding: '10px' }}>{m.elastic_modulus_gpa}</td>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--accent-emerald)' }}>₹{m.approx_cost_inr_per_kg}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: 'var(--radius-sm)', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
            <strong>Procurement Guidance:</strong> {blueprint.material_selection.procurement_guidance}
          </div>
        </div>
      )}

      {/* TAB: FABRICATION PLAN (Physical Only) */}
      {activeTab === 'fabrication' && isPhysical && blueprint.fabrication_plan && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>6. Workshop Fabrication &amp; Manufacturing Plan</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.88rem' }}>
            Sequential machining operations, CNC tooling parameters, and workshop safety protocols.
          </p>

          <div style={{ overflowX: 'auto', marginBottom: '24px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.86rem' }}>
              <thead>
                <tr style={{ background: 'var(--bg-secondary)', textAlign: 'left' }}>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>#</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Operation</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Machine / Tooling</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Machining Parameters</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Finished Output</th>
                </tr>
              </thead>
              <tbody>
                {blueprint.fabrication_plan.manufacturing_processes?.map((op) => (
                  <tr key={op.step_number} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '10px', color: 'var(--accent-cyan)', fontWeight: 600 }}>{op.step_number}</td>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--text-primary)' }}>{op.operation}</td>
                    <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>{op.machine}</td>
                    <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>{op.parameters}</td>
                    <td style={{ padding: '10px', color: 'var(--accent-emerald)' }}>{op.output}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <ShieldAlert size={18} color="var(--accent-rose)" />
              <h3 style={{ fontSize: '0.95rem', color: '#fda4af' }}>Workshop Safety Standards</h3>
            </div>
            <ul style={{ paddingLeft: '20px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              {blueprint.fabrication_plan.workshop_safety?.map((s, idx) => (
                <li key={idx} style={{ marginBottom: '4px' }}>{s}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* TAB: MECHANICAL BOM (Physical Only) */}
      {activeTab === 'bom' && isPhysical && blueprint.mechanical_bom && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>7. Mechanical Bill of Materials (BOM)</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.88rem' }}>
            Complete hardware procurement list with authentic Indian market pricing in ₹ INR.
          </p>

          <div style={{ overflowX: 'auto', marginBottom: '20px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
              <thead>
                <tr style={{ background: 'var(--bg-secondary)', textAlign: 'left' }}>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Component / Hardware Item</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Category</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Price (₹ INR)</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Indian Sourcing Channel</th>
                </tr>
              </thead>
              <tbody>
                {blueprint.mechanical_bom.map((item, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--text-primary)' }}>{item.item}</td>
                    <td style={{ padding: '10px' }}><span className="badge badge-intermediate">{item.category}</span></td>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--accent-cyan)' }}>₹{item.approx_price_inr?.toLocaleString()}</td>
                    <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>{item.indian_source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '12px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
            <span style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--accent-emerald)' }}>
              Total Hardware BOM: ₹{blueprint.mechanical_bom.reduce((acc, curr) => acc + (curr.approx_price_inr || 0), 0).toLocaleString()}
            </span>
          </div>
        </div>
      )}

      {/* TAB: GD&T & TOLERANCES (Physical Only) */}
      {activeTab === 'gdt' && isPhysical && blueprint.gdt_and_tolerances && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>8. GD&amp;T &amp; ISO Tolerance Standards</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.88rem' }}>
            ISO 286 limit fits, geometric tolerances, and certified ASTM / IS inspection standards.
          </p>

          <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '10px' }}>ISO 286 Fit Specifications</h3>
          <div style={{ overflowX: 'auto', marginBottom: '24px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.86rem' }}>
              <thead>
                <tr style={{ background: 'var(--bg-secondary)', textAlign: 'left' }}>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Mating Pair</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>ISO Fit</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Clearance Category</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Permissible Limits</th>
                </tr>
              </thead>
              <tbody>
                {blueprint.gdt_and_tolerances.tolerance_fits?.map((tf, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--text-primary)' }}>{tf.fit_type}</td>
                    <td style={{ padding: '10px', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>{tf.iso_fit}</td>
                    <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>{tf.clearance_type}</td>
                    <td style={{ padding: '10px', color: 'var(--accent-emerald)' }}>{tf.tolerance_range_mm}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid-2" style={{ gap: '16px' }}>
            <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
              <h3 style={{ fontSize: '0.95rem', color: 'var(--accent-amber)', marginBottom: '8px' }}>Geometric Tolerancing</h3>
              {blueprint.gdt_and_tolerances.geometric_tolerances?.map((gt, idx) => (
                <div key={idx} style={{ marginBottom: '8px', fontSize: '0.85rem' }}>
                  <strong style={{ color: 'var(--text-primary)' }}>{gt.feature}:</strong> {gt.symbol} ({gt.tolerance_value_mm} mm) [{gt.datum}]
                </div>
              ))}
            </div>

            <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
              <h3 style={{ fontSize: '0.95rem', color: 'var(--accent-emerald)', marginBottom: '8px' }}>Physical Inspection Standards</h3>
              <ul style={{ paddingLeft: '16px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                {blueprint.gdt_and_tolerances.physical_testing_standards?.map((st, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{st}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* TAB: EMBEDDED SENSORS (Physical Only, conditional) */}
      {activeTab === 'sensors' && isPhysical && blueprint.embedded_sensors && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>9. Embedded Systems &amp; Sensor Instrumentation</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.88rem' }}>
            Controller: <strong style={{ color: 'var(--accent-cyan)' }}>{blueprint.embedded_sensors.microcontroller}</strong> | Power: {blueprint.embedded_sensors.power_supply}
          </p>

          <div style={{ overflowX: 'auto', marginBottom: '20px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
              <thead>
                <tr style={{ background: 'var(--bg-secondary)', textAlign: 'left' }}>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Sensor Model</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Physical Measurement</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid var(--border-subtle)' }}>Interface / Wiring</th>
                </tr>
              </thead>
              <tbody>
                {blueprint.embedded_sensors.sensors?.map((sen, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--text-primary)' }}>{sen.sensor_name}</td>
                    <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>{sen.measurement}</td>
                    <td style={{ padding: '10px', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>{sen.interface}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: 'var(--radius-sm)', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
            <em>{blueprint.embedded_sensors.design_note}</em>
          </div>
        </div>
      )}

      {/* TAB: 22 ENGINEERING DISCIPLINES / TECH */}
      {activeTab === 'technologies' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ fontSize: '1.3rem', marginBottom: '4px' }}>
              {isPhysical ? '10. Physical Engineering Disciplines' : '3. Technology Stack: 22 Engineering Disciplines'}
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
              Rigorous technical decisions and tooling specifications across all engineering dimensions.
            </p>
          </div>

          <div className="grid-2">
            {Object.entries(blueprint.technologies || {}).map(([key, item]) => (
              <div key={key} style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '16px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <h3 style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>{item.area_label}</h3>
                  <span className="badge badge-cyan">{key.toUpperCase()}</span>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '8px' }}>
                  {item.tools?.map((tool, i) => (
                    <span key={i} style={{
                      background: 'var(--bg-tertiary)',
                      color: 'var(--text-primary)',
                      padding: '2px 6px',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.78rem',
                      fontFamily: 'var(--font-mono)',
                    }}>
                      {tool}
                    </span>
                  ))}
                </div>
                <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  <strong style={{ color: 'var(--text-primary)' }}>Rationale:</strong> {item.rationale}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB: SYSTEM MODULES (Software Only) */}
      {activeTab === 'modules' && !isPhysical && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>4. System Modules Breakdown</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
            {blueprint.modules?.map((mod) => (
              <div key={mod.id} style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '18px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)' }}>{mod.id}: {mod.name}</h3>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    {mod.technologies?.map((tech, i) => (
                      <span key={i} className="badge badge-intermediate">{tech}</span>
                    ))}
                  </div>
                </div>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '12px', fontSize: '0.88rem' }}>{mod.description}</p>
                <div className="grid-2" style={{ gap: '10px', background: 'var(--bg-tertiary)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Inputs:</span>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>{mod.inputs}</p>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Outputs:</span>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>{mod.outputs}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB: DATABASE (Software Only) */}
      {activeTab === 'database' && !isPhysical && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>5. Database Schema &amp; ER Design</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '14px', fontSize: '0.88rem' }}>
            Engine: {blueprint.database_design?.engine} | Strategy: {blueprint.database_design?.schema_strategy}
          </p>
          <MermaidViewer
            chartCode={blueprint.database_design?.mermaid_er_diagram}
            title="Entity-Relationship Diagram"
          />
        </div>
      )}

      {/* TAB: ROADMAP (Common) */}
      {activeTab === 'roadmap' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>
            {isPhysical ? '11. Workshop Roadmap & Fabrication Milestones' : '6. Sprint Roadmap & Progress'}
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
            {blueprint.roadmap?.map((phase, pIdx) => (
              <div key={pIdx} style={{ background: 'var(--bg-secondary)', padding: '18px', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)' }}>{phase.title}</h3>
                  <span className="badge badge-cyan">{phase.duration}</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {phase.tasks?.map((t) => (
                    <div
                      key={t.id}
                      onClick={() => toggleTask(t.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '10px 14px',
                        background: completedTasks.has(t.id) ? 'rgba(34, 197, 94, 0.1)' : 'var(--bg-tertiary)',
                        borderRadius: 'var(--radius-sm)',
                        cursor: 'pointer',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div style={{
                          width: '18px',
                          height: '18px',
                          borderRadius: '4px',
                          border: '2px solid',
                          borderColor: completedTasks.has(t.id) ? 'var(--accent-emerald)' : 'var(--text-muted)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          background: completedTasks.has(t.id) ? 'var(--accent-emerald)' : 'transparent',
                        }}>
                          {completedTasks.has(t.id) && <Check size={12} color="white" />}
                        </div>
                        <span style={{ fontSize: '0.88rem', color: 'var(--text-primary)', textDecoration: completedTasks.has(t.id) ? 'line-through' : 'none' }}>
                          {t.title}
                        </span>
                      </div>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        {t.estimated_hours}h
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB: DOCUMENTATION */}
      {activeTab === 'documentation' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>Documentation &amp; Thesis Chapters</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.88rem' }}>
            Format: {blueprint.documentation?.report_format}
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {blueprint.documentation?.chapters?.map((ch) => (
              <div key={ch.number} style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
                <strong style={{ color: 'var(--accent-cyan)' }}>Chapter {ch.number}: {ch.title}</strong>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>{ch.contents}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB: TESTING */}
      {activeTab === 'testing' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>Testing Strategy &amp; Verification Cases</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.88rem' }}>
            Strategy: {blueprint.testing?.strategy}
          </p>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ background: 'var(--bg-secondary)', textAlign: 'left' }}>
                  <th style={{ padding: '8px' }}>Test ID</th>
                  <th style={{ padding: '8px' }}>Category</th>
                  <th style={{ padding: '8px' }}>Scenario</th>
                  <th style={{ padding: '8px' }}>Expected Output</th>
                </tr>
              </thead>
              <tbody>
                {blueprint.testing?.test_cases?.map((tc) => (
                  <tr key={tc.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '8px', color: 'var(--accent-cyan)' }}>{tc.id}</td>
                    <td style={{ padding: '8px' }}><span className="badge badge-intermediate">{tc.category}</span></td>
                    <td style={{ padding: '8px', color: 'var(--text-primary)' }}>{tc.scenario}</td>
                    <td style={{ padding: '8px', color: 'var(--accent-emerald)' }}>{tc.expected_output}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB: PRESENTATION PITCH DECK */}
      {activeTab === 'presentation' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>Presentation &amp; Defense Slide Deck</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
            {blueprint.presentation?.deck_outline?.map((slide) => (
              <div key={slide.slide_number} style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <h3 style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>
                    Slide {slide.slide_number}: {slide.title}
                  </h3>
                  <span className="badge badge-cyan">{slide.visual_recommendation}</span>
                </div>
                <ul style={{ paddingLeft: '16px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  {slide.key_points?.map((pt, i) => (
                    <li key={i}>{pt}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB: VIVA VOE DEFENSE */}
      {activeTab === 'viva' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>Viva Voce &amp; Technical Defense Guide</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '18px', fontSize: '0.88rem' }}>
            Technical questions asked by examiners with model answers.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {blueprint.viva_questions?.map((vq, idx) => {
              const isExpanded = expandedViva === idx;
              return (
                <div key={idx} style={{ background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', overflow: 'hidden' }}>
                  <div
                    onClick={() => setExpandedViva(isExpanded ? -1 : idx)}
                    style={{ padding: '12px 16px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span className="badge badge-amber">{vq.category}</span>
                      <strong style={{ color: 'var(--text-primary)', fontSize: '0.88rem' }}>Q{idx + 1}: {vq.question}</strong>
                    </div>
                    <span style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>{isExpanded ? '−' : '+'}</span>
                  </div>
                  {isExpanded && (
                    <div style={{ padding: '14px 16px', borderTop: '1px solid var(--border-subtle)', background: 'rgba(0, 0, 0, 0.2)', color: 'var(--text-secondary)', fontSize: '0.86rem', lineHeight: '1.5' }}>
                      <strong style={{ color: 'var(--accent-emerald)', display: 'block', marginBottom: '4px' }}>Defense Model Answer:</strong>
                      {vq.answer}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
