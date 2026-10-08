"""Project blueprint export service (Markdown & printable HTML).

Supports both Software/AI and Branch-Adaptive Physical & Fabrication-First Engineering blueprints.
"""
from __future__ import annotations

import html
from typing import Any


def export_markdown(project_title: str, blueprint: dict[str, Any]) -> str:
    """Formats the entire blueprint as an IEEE/AICTE-aligned Markdown document."""
    is_physical = bool(blueprint.get("is_physical_engineering"))

    lines = [
        f"# {blueprint.get('title', project_title)}",
        f"**Tier:** {blueprint.get('level_label', '').upper()}: {blueprint.get('tier_title', '')}  ",
        f"**Tagline:** {blueprint.get('tagline', '')}  ",
        f"**Estimated Cost:** ₹{blueprint.get('estimated_cost_inr', 0):,}  ",
        f"**Target Users:** {blueprint.get('target_users', '')}  ",
        f"**Discipline:** {'Physical & Fabrication Engineering' if is_physical else 'Software & AI Systems'}  ",
        "\n---\n",
    ]

    # 1. Problem Statement
    ps = blueprint.get("problem_statement", {})
    lines.append("## 1. Problem Statement & Objectives\n")
    lines.append(f"### Background\n{ps.get('background', '')}\n")
    lines.append(f"### Core Problem\n{ps.get('core_problem', '')}\n")
    lines.append("### Project Objectives")
    for obj in ps.get("objectives", []):
        lines.append(f"- {obj}")
    lines.append("\n### Measurable Success Metrics")
    for sm in ps.get("success_metrics", []):
        lines.append(f"- {sm}")
    lines.append("\n---\n")

    # 2. Architecture
    arch = blueprint.get("architecture", {})
    arch_title = "Kinematic & Structural Architecture" if is_physical else "System Architecture"
    lines.append(f"## 2. {arch_title}\n")
    lines.append(f"**Pattern:** {arch.get('pattern', '')}\n")
    lines.append(f"{arch.get('overview', '')}\n")
    lines.append("### Architecture Diagram (Mermaid)")
    lines.append("```mermaid")
    lines.append(arch.get("mermaid_diagram", ""))
    lines.append("```\n")
    lines.append("### End-to-End Operational Flow")
    for step in arch.get("data_flow_steps", []):
        lines.append(f"- {step}")
    lines.append("\n---\n")

    # 3. Technology Stack
    stack_title = "Physical Engineering Disciplines & Tech Stack" if is_physical else "Technology Stack (22 Dimensions)"
    lines.append(f"## 3. {stack_title}\n")
    lines.append("| Dimension | Tools & Frameworks | Rationale |")
    lines.append("| :--- | :--- | :--- |")
    techs = blueprint.get("technologies", {})
    for _, tdata in techs.items():
        tools_str = ", ".join(tdata.get("tools", []))
        lines.append(f"| **{tdata.get('area_label')}** | {tools_str} | {tdata.get('rationale')} |")
    lines.append("\n---\n")

    if is_physical:
        # 4. CAD 3D Modeling & Kinematics
        cad = blueprint.get("cad_modeling", {})
        lines.append("## 4. CAD 3D Modeling & Kinematics\n")
        lines.append(f"**Primary CAD Suite:** {cad.get('primary_cad_tool')}\n")
        lines.append(f"**Modeling Approach:** {cad.get('modeling_approach')}\n")
        lines.append(f"**Drawing Standards:** {cad.get('drawing_standards')}\n")
        lines.append("### Assembly Breakdown")
        lines.append("| Subassembly | Parts Count | Primary Material | Mating Constraints |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for sub in cad.get("assemblies", []):
            lines.append(f"| **{sub.get('subassembly_name')}** | {sub.get('components_count')} | {sub.get('primary_material')} | {sub.get('mating_constraints')} |")
        lines.append("")
        kin = cad.get("kinematic_analysis", {})
        if kin:
            lines.append("### Kinematic Analysis")
            lines.append(f"- **Degrees of Freedom:** {kin.get('degrees_of_freedom')}")
            lines.append(f"- **Motion Study:** {kin.get('motion_study')}")
            lines.append(f"- **Collision & Interference:** {kin.get('collision_check')}")
            lines.append("")
        lines.append("---\n")

        # 5. FEA / CFD Simulation & Stress Analysis
        fea = blueprint.get("fea_cfd_simulation", {})
        lines.append("## 5. FEA & CFD Simulation & Stress Analysis\n")
        lines.append(f"**Simulation Software:** {fea.get('simulation_software')}\n")
        lines.append(f"**Meshing Methodology:** {fea.get('meshing_methodology')}\n")
        mesh_m = fea.get("mesh_metrics", {})
        if mesh_m:
            lines.append("### Mesh Convergence Metrics")
            lines.append(f"- **Total Nodes:** {mesh_m.get('total_nodes'):,}")
            lines.append(f"- **Total Elements:** {mesh_m.get('total_elements'):,}")
            lines.append(f"- **Average Quality:** {mesh_m.get('element_quality_average')}")
            lines.append(f"- **Convergence Verification:** {mesh_m.get('mesh_convergence')}")
            lines.append("")
        b_cond = fea.get("boundary_conditions", {})
        if b_cond:
            lines.append("### Boundary Conditions")
            lines.append(f"- **Fixtures:** {b_cond.get('fixtures')}")
            lines.append(f"- **Applied Loads:** {b_cond.get('applied_loads')}")
            lines.append("")
        stress = fea.get("stress_results", {})
        if stress:
            lines.append("### Structural Stress & Factor of Safety")
            lines.append(f"- **Peak von Mises Stress:** {stress.get('max_von_mises_stress_mpa')} MPa")
            lines.append(f"- **Material Yield Strength:** {stress.get('material_yield_strength_mpa')} MPa")
            lines.append(f"- **Calculated Factor of Safety (FOS):** **{stress.get('calculated_factor_of_safety')}**")
            lines.append(f"- **Max Elastic Deformation:** {stress.get('max_deformation_mm')} mm")
            lines.append(f"- **Critical Hotspot:** {stress.get('critical_hotspot')}")
            lines.append("")
        modal = fea.get("modal_frequency_analysis", {})
        if modal:
            lines.append("### Modal & Harmonic Vibration")
            lines.append(f"- **Mode 1 Natural Frequency:** {modal.get('mode_1_natural_frequency_hz')} Hz")
            lines.append(f"- **Operating Harmonics:** {modal.get('operating_excitation_frequency_hz')} Hz")
            lines.append(f"- **Safety Margin:** {modal.get('resonance_margin_pct')}% ({modal.get('resonance_risk')})")
            lines.append("")
        cfd = fea.get("cfd_analysis", {})
        if cfd:
            lines.append("### Computational Fluid Dynamics (CFD)")
            lines.append(f"- **CFD Tool:** {cfd.get('cfd_tool')}")
            lines.append(f"- **Inlet Velocity:** {cfd.get('inlet_velocity_ms')} m/s")
            lines.append(f"- **Drag Coefficient (Cd):** {cfd.get('calculated_drag_coefficient_cd')}")
            lines.append(f"- **Lift/Drag Ratio:** {cfd.get('lift_drag_ratio')}")
            lines.append(f"- **Boundary Layer:** {cfd.get('boundary_layer_resolution')}")
            lines.append(f"- **Key Findings:** {cfd.get('findings')}")
            lines.append("")
        lines.append("---\n")

        # 6. Material Selection & Properties
        mat = blueprint.get("material_selection", {})
        lines.append("## 6. Material Selection & Mechanical Properties\n")
        lines.append(f"**Optimization Framework:** {mat.get('selection_framework')}\n")
        lines.append("| Material | Application | Density (g/cm³) | Yield (MPa) | UTS (MPa) | Modulus (GPa) | Price (₹/kg) | Key Advantages |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for m in mat.get("selected_materials", []):
            lines.append(f"| **{m.get('material_name')}** | {m.get('application')} | {m.get('density_g_cm3')} | {m.get('yield_strength_mpa')} | {m.get('ultimate_tensile_strength_mpa')} | {m.get('elastic_modulus_gpa')} | ₹{m.get('approx_cost_inr_per_kg')} | {m.get('advantages')} |")
        lines.append(f"\n*Procurement:* {mat.get('procurement_guidance')}\n")
        lines.append("---\n")

        # 7. Fabrication & Manufacturing Plan
        fab = blueprint.get("fabrication_plan", {})
        lines.append("## 7. Workshop Fabrication & Manufacturing Plan\n")
        lines.append("| Step | Operation | Machine / Tooling | Process Parameters | Finished Output |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for op in fab.get("manufacturing_processes", []):
            lines.append(f"| {op.get('step_number')} | **{op.get('operation')}** | {op.get('machine')} | {op.get('parameters')} | {op.get('output')} |")
        lines.append("\n### Workshop Safety Protocols")
        for s in fab.get("workshop_safety", []):
            lines.append(f"- {s}")
        lines.append("\n---\n")

        # 8. Mechanical Bill of Materials (BOM)
        bom = blueprint.get("mechanical_bom", [])
        lines.append("## 8. Mechanical Bill of Materials (BOM - Indian Market)\n")
        lines.append("| Component / Hardware Item | Category | Approx. Price (₹ INR) | Indian Sourcing Channel |")
        lines.append("| :--- | :--- | :--- | :--- |")
        total_bom = 0
        for item in bom:
            price = item.get("approx_price_inr", 0)
            total_bom += price
            lines.append(f"| **{item.get('item')}** | {item.get('category')} | ₹{price:,} | {item.get('indian_source')} |")
        lines.append(f"\n**Total Hardware BOM Estimate:** ₹{total_bom:,}\n")
        lines.append("---\n")

        # 9. GD&T and Tolerances
        gdt = blueprint.get("gdt_and_tolerances", {})
        lines.append("## 9. GD&T, Tolerances & Testing Standards\n")
        lines.append("### ISO 286 Fit Specifications")
        lines.append("| Application Mating Pair | ISO Fit Class | Clearance Category | Permissible Limits |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for tf in gdt.get("tolerance_fits", []):
            lines.append(f"| {tf.get('fit_type')} | `{tf.get('iso_fit')}` | {tf.get('clearance_type')} | {tf.get('tolerance_range_mm')} |")
        lines.append("\n### Geometric Tolerances")
        lines.append("| Feature | Geometric Symbol | Tolerance Limit | Datum Reference |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for gt in gdt.get("geometric_tolerances", []):
            lines.append(f"| {gt.get('feature')} | {gt.get('symbol')} | {gt.get('tolerance_value_mm')} mm | {gt.get('datum')} |")
        lines.append("\n### Physical Testing & Verification Standards")
        for st in gdt.get("physical_testing_standards", []):
            lines.append(f"- {st}")
        lines.append("\n---\n")

        # 10. Embedded Sensors (if mechatronic)
        sensors = blueprint.get("embedded_sensors")
        if sensors:
            lines.append("## 10. Embedded Systems & Sensor Instrumentation\n")
            lines.append(f"**Microcontroller:** {sensors.get('microcontroller')}\n")
            lines.append(f"**Motor Driver:** {', '.join(d.get('driver_model') for d in sensors.get('motor_drivers', []))}\n")
            lines.append(f"**Power Unit:** {sensors.get('power_supply')}\n")
            lines.append("### Sensor List")
            for sen in sensors.get("sensors", []):
                lines.append(f"- **{sen.get('sensor_name')}**: {sen.get('measurement')} (Interface: {sen.get('interface')})")
            lines.append(f"\n*{sensors.get('design_note')}*\n")
            lines.append("---\n")

        # 11. Modules
        lines.append("## 11. Subsystem Engineering Modules\n")
        for mod in blueprint.get("modules", []):
            lines.append(f"### {mod.get('id')}: {mod.get('name')}")
            lines.append(f"{mod.get('description')}\n")
            lines.append(f"- **Inputs:** {mod.get('inputs')}")
            lines.append(f"- **Outputs:** {mod.get('outputs')}")
            lines.append(f"- **Subsystem Disciplines:** {', '.join(mod.get('technologies', []))}")
            lines.append("- **Key Engineering Responsibilities:**")
            for resp in mod.get("responsibilities", []):
                lines.append(f"  - {resp}")
            lines.append("")
        lines.append("---\n")

    else:
        # Software & AI Sections
        # 4. Modules
        lines.append("## 4. System Modules Breakdown\n")
        for mod in blueprint.get("modules", []):
            lines.append(f"### {mod.get('id')}: {mod.get('name')}")
            lines.append(f"{mod.get('description')}\n")
            lines.append(f"- **Inputs:** {mod.get('inputs')}")
            lines.append(f"- **Outputs:** {mod.get('outputs')}")
            lines.append(f"- **Technologies:** {', '.join(mod.get('technologies', []))}")
            lines.append("- **Key Responsibilities:**")
            for resp in mod.get("responsibilities", []):
                lines.append(f"  - {resp}")
            lines.append("")
        lines.append("---\n")

        # 5. Database Design
        db = blueprint.get("database_design", {})
        lines.append("## 5. Database Schema & ER Design\n")
        lines.append(f"**Database Engine:** {db.get('engine')}\n")
        lines.append(f"**Schema Strategy:** {db.get('schema_strategy')}\n")
        lines.append("### Entity-Relationship Diagram (Mermaid)")
        lines.append("```mermaid")
        lines.append(db.get("mermaid_er_diagram", ""))
        lines.append("```\n")
        lines.append("### Tables Specification")
        for table in db.get("tables", []):
            lines.append(f"\n#### Table: `{table.get('name')}` ({table.get('description')})")
            lines.append("| Column | Type | Constraints |")
            lines.append("| :--- | :--- | :--- |")
            for col in table.get("columns", []):
                lines.append(f"| `{col.get('name')}` | `{col.get('type')}` | {col.get('constraints')} |")
        lines.append("\n---\n")

    # Common: Roadmap
    step_num = 12 if is_physical else 6
    lines.append(f"## {step_num}. Fabrication & Development Roadmap\n" if is_physical else f"## {step_num}. Sprint Roadmap & Milestones\n")
    for phase in blueprint.get("roadmap", []):
        lines.append(f"### {phase.get('title')} ({phase.get('duration')})")
        lines.append("| ID | Task Description | Est. Person-Hours | Deliverable |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for task in phase.get("tasks", []):
            lines.append(f"| `{task.get('id')}` | {task.get('title')} | {task.get('estimated_hours')} hrs | {task.get('deliverable')} |")
        lines.append("")
    lines.append("---\n")

    # Common: Testing Plan
    step_num += 1
    test_plan = blueprint.get("testing", {})
    lines.append(f"## {step_num}. Testing Strategy & Test Verification\n")
    lines.append(f"**Strategy:** {test_plan.get('strategy')}\n")
    lines.append("| Test ID | Category | Scenario | Expected Output | Type |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for tc in test_plan.get("test_cases", []):
        lines.append(f"| `{tc.get('id')}` | {tc.get('category')} | {tc.get('scenario')} | {tc.get('expected_output')} | {tc.get('type')} |")
    lines.append("\n---\n")

    # Common: Viva Questions
    step_num += 1
    lines.append(f"## {step_num}. Viva Voce & Technical Defense Guide\n")
    for idx, vq in enumerate(blueprint.get("viva_questions", []), 1):
        lines.append(f"**Q{idx} ({vq.get('category')}):** {vq.get('question')}")
        lines.append(f"> **Answer:** {vq.get('answer')}\n")

    return "\n".join(lines)


def export_printable_html(project_title: str, blueprint: dict[str, Any]) -> str:
    """Formats the blueprint into an elegant, print-ready HTML document for immediate printing or PDF saving."""
    is_physical = bool(blueprint.get("is_physical_engineering"))
    title_escaped = html.escape(blueprint.get("title", project_title))
    tier_title = html.escape(blueprint.get("tier_title", ""))
    tagline = html.escape(blueprint.get("tagline", ""))

    tech_rows = []
    for t in blueprint.get("technologies", {}).values():
        label = html.escape(t.get("area_label", ""))
        tools = html.escape(", ".join(t.get("tools", [])))
        why = html.escape(t.get("rationale", ""))
        tech_rows.append(f"<tr><td><strong>{label}</strong></td><td>{tools}</td><td>{why}</td></tr>")

    module_blocks = []
    for m in blueprint.get("modules", []):
        m_id = html.escape(m.get("id", ""))
        m_name = html.escape(m.get("name", ""))
        m_desc = html.escape(m.get("description", ""))
        m_tech = html.escape(", ".join(m.get("technologies", [])))
        module_blocks.append(f"<h3>{m_id}: {m_name}</h3><p>{m_desc}</p><p><strong>{'Disciplines' if is_physical else 'Tech'}:</strong> {m_tech}</p>")

    roadmap_blocks = []
    for p in blueprint.get("roadmap", []):
        p_title = html.escape(p.get("title", ""))
        p_dur = html.escape(p.get("duration", ""))
        task_items = []
        for t in p.get("tasks", []):
            t_title = html.escape(t.get("title", ""))
            t_hrs = t.get("estimated_hours", 0)
            t_del = html.escape(t.get("deliverable", ""))
            task_items.append(f"<li><strong>{t_title}</strong> ({t_hrs}h) &mdash; <em>Deliverable: {t_del}</em></li>")
        roadmap_blocks.append(f"<h3>{p_title} ({p_dur})</h3><ul>{''.join(task_items)}</ul>")

    viva_blocks = []
    for v in blueprint.get("viva_questions", []):
        q = html.escape(v.get("question", ""))
        cat = html.escape(v.get("category", ""))
        ans = html.escape(v.get("answer", ""))
        viva_blocks.append(f"<p><strong>Q: {q}</strong> ({cat})</p><blockquote>{ans}</blockquote>")

    physical_blocks = []
    if is_physical:
        # CAD
        cad = blueprint.get("cad_modeling", {})
        cad_subs = "".join(
            f"<tr><td><strong>{html.escape(s.get('subassembly_name', ''))}</strong></td><td>{s.get('components_count', 0)}</td><td>{html.escape(s.get('primary_material', ''))}</td><td>{html.escape(s.get('mating_constraints', ''))}</td></tr>"
            for s in cad.get("assemblies", [])
        )
        physical_blocks.append(f"""
        <h2>4. CAD 3D Modeling & Kinematics</h2>
        <p><strong>Primary CAD Tool:</strong> {html.escape(cad.get('primary_cad_tool', ''))} | <strong>Approach:</strong> {html.escape(cad.get('modeling_approach', ''))}</p>
        <table>
          <thead><tr><th>Subassembly</th><th>Parts</th><th>Primary Material</th><th>Mating Constraints</th></tr></thead>
          <tbody>{cad_subs}</tbody>
        </table>
        """)

        # FEA
        fea = blueprint.get("fea_cfd_simulation", {})
        stress = fea.get("stress_results", {})
        physical_blocks.append(f"""
        <h2>5. FEA & CFD Stress Analysis</h2>
        <p><strong>Software:</strong> {html.escape(fea.get('simulation_software', ''))}</p>
        <p><strong>von Mises Stress:</strong> {stress.get('max_von_mises_stress_mpa', 0)} MPa | <strong>Yield:</strong> {stress.get('material_yield_strength_mpa', 0)} MPa | <strong>Factor of Safety:</strong> <strong style="color: #2b6cb0;">{stress.get('calculated_factor_of_safety', 0)}</strong> | <strong>Max Deflection:</strong> {stress.get('max_deformation_mm', 0)} mm</p>
        """)

        # Materials
        mat = blueprint.get("material_selection", {})
        mat_rows = "".join(
            f"<tr><td><strong>{html.escape(m.get('material_name', ''))}</strong></td><td>{html.escape(m.get('application', ''))}</td><td>{m.get('density_g_cm3', 0)}</td><td>{m.get('yield_strength_mpa', 0)}</td><td>{m.get('ultimate_tensile_strength_mpa', 0)}</td><td>₹{m.get('approx_cost_inr_per_kg', 0)}</td></tr>"
            for m in mat.get("selected_materials", [])
        )
        physical_blocks.append(f"""
        <h2>6. Material Selection & Properties</h2>
        <table>
          <thead><tr><th>Material</th><th>Application</th><th>Density (g/cm³)</th><th>Yield (MPa)</th><th>UTS (MPa)</th><th>Price (₹/kg)</th></tr></thead>
          <tbody>{mat_rows}</tbody>
        </table>
        """)

        # Mechanical BOM
        bom = blueprint.get("mechanical_bom", [])
        bom_rows = "".join(
            f"<tr><td><strong>{html.escape(b.get('item', ''))}</strong></td><td>{html.escape(b.get('category', ''))}</td><td>₹{b.get('approx_price_inr', 0):,}</td><td>{html.escape(b.get('indian_source', ''))}</td></tr>"
            for b in bom
        )
        physical_blocks.append(f"""
        <h2>7. Mechanical Bill of Materials (BOM)</h2>
        <table>
          <thead><tr><th>Component</th><th>Category</th><th>Price (₹ INR)</th><th>Indian Sourcing</th></tr></thead>
          <tbody>{bom_rows}</tbody>
        </table>
        """)

    doc_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title_escaped} - Project Blueprint</title>
  <style>
    @media print {{
      body {{ font-size: 11pt; }}
      .page-break {{ page-break-before: always; }}
      .no-print {{ display: none !important; }}
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.5;
      color: #1a202c;
      max-width: 900px;
      margin: 0 auto;
      padding: 40px 20px;
    }}
    h1 {{ color: #2b6cb0; margin-bottom: 4px; font-size: 24pt; }}
    h2 {{ color: #2d3748; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-top: 32px; }}
    h3 {{ color: #4a5568; margin-top: 20px; }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      background: #ebf8ff;
      color: #2b6cb0;
      border-radius: 9999px;
      font-size: 10pt;
      font-weight: 600;
      text-transform: uppercase;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
      font-size: 10pt;
    }}
    th, td {{
      border: 1px solid #cbd5e0;
      padding: 8px 12px;
      text-align: left;
    }}
    th {{ background: #f7fafc; font-weight: 600; }}
    blockquote {{
      margin: 8px 0 16px;
      padding: 8px 16px;
      background: #edf2f7;
      border-left: 4px solid #4299e1;
      font-style: italic;
    }}
    .print-btn {{
      position: fixed;
      top: 20px;
      right: 20px;
      background: #3182ce;
      color: white;
      border: none;
      padding: 10px 18px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: bold;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
  </style>
</head>
<body>
  <button class="print-btn no-print" onclick="window.print()">Print / Save as PDF</button>

  <span class="badge">{html.escape(blueprint.get("level_label", "").upper())} PATH</span>
  <h1>{title_escaped}</h1>
  <p style="font-size: 13pt; color: #4a5568; margin-top: 0;"><em>{tier_title}</em> &mdash; {tagline}</p>
  <p><strong>Estimated Cost:</strong> ₹{blueprint.get("estimated_cost_inr", 0):,} | <strong>Target Users:</strong> {html.escape(blueprint.get("target_users", ""))}</p>

  <h2>1. Problem Statement & Objectives</h2>
  <p><strong>Background:</strong> {html.escape(blueprint.get("problem_statement", {}).get("background", ""))}</p>
  <p><strong>Core Problem:</strong> {html.escape(blueprint.get("problem_statement", {}).get("core_problem", ""))}</p>
  <h3>Key Objectives</h3>
  <ul>
    {"".join(f"<li>{html.escape(o)}</li>" for o in blueprint.get("problem_statement", {}).get("objectives", []))}
  </ul>

  <div class="page-break"></div>
  <h2>2. System Architecture</h2>
  <p><strong>Pattern:</strong> {html.escape(blueprint.get("architecture", {}).get("pattern", ""))}</p>
  <p>{html.escape(blueprint.get("architecture", {}).get("overview", ""))}</p>

  <h2>3. Engineering Disciplines & Stack</h2>
  <table>
    <thead><tr><th>Area</th><th>Tools & Technologies</th><th>Architectural Rationale</th></tr></thead>
    <tbody>
      {"".join(tech_rows)}
    </tbody>
  </table>

  {"".join(physical_blocks)}

  <div class="page-break"></div>
  <h2>Subsystem Modules</h2>
  {"".join(module_blocks)}

  <div class="page-break"></div>
  <h2>Fabrication & Sprint Roadmap</h2>
  {"".join(roadmap_blocks)}

  <div class="page-break"></div>
  <h2>Viva Voce Defense Guide</h2>
  {"".join(viva_blocks)}

</body>
</html>
"""
    return doc_html
