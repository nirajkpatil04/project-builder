"""Blueprint generator.

Transforms an Idea + Level + Student Profile into an exhaustive, production-grade
project blueprint covering all 22 required engineering disciplines and practical
final-year project requirements (architecture, modules, database design, roadmap,
Git workflow, documentation, testing, presentation, viva questions, and Mermaid diagrams).
"""
from __future__ import annotations

import math
from typing import Any

from .catalog import (
    AI_DOMAINS,
    APPLICATION_AREAS,
    BRANCHES,
    LEVEL_LABELS,
    is_electromechanical_branch,
    is_physical_branch,
)
from .ideas import IDEA_INDEX, Idea
from .stacks import (
    AREAS,
    DOMAIN_ADDONS,
    HARDWARE_STACK,
    INTEREST_INTEGRATIONS,
    PHYSICAL_AREAS,
    PHYSICAL_STACK,
    STACK,
)
from .viva import LEVEL_EXTRA, VIVA_BANK


def _build_mermaid_architecture(idea: Idea, level: str) -> str:
    """Generates a valid Mermaid flowchart diagram tailored to the idea and tier."""
    is_hw = idea["type"] in ("hardware", "hybrid")
    domains = set(idea["domains"])

    lines = ["graph TD", "    subgraph ClientLayer[\"1. Client & Presentation Layer\"]"]
    lines.append("        UI[\"Frontend Web App (React / PWA)\"]")
    if is_hw:
        lines.append("        HW[\"IoT Device / Edge Sensor (ESP32/RPi)\"]")
    if "cv" in domains:
        lines.append("        Cam[\"Camera / Video Feed / File Input\"]")
    lines.append("    end")

    lines.append("    subgraph GatewayLayer[\"2. API & Security Layer\"]")
    lines.append("        API[\"FastAPI Backend Gateway\"]")
    lines.append("        Auth[\"Auth & RBAC (JWT / bcrypt)\"]")
    lines.append("        RateLimiter[\"Rate Limiting & Input Sanitization\"]")
    lines.append("    end")

    lines.append("    subgraph CoreLayer[\"3. Application & Intelligence Layer\"]")
    lines.append("        BizLogic[\"Business Logic Services\"]")
    if "cv" in domains:
        lines.append("        Preproc[\"Preprocessing & Augmentation (OpenCV/Albumentations)\"]")
    if "nlp" in domains or "genai" in domains:
        lines.append("        Tokenize[\"Text Normalization & Tokenizer\"]")
    if level == "beginner":
        lines.append("        ModelEngine[\"AI Inference Engine (ONNX / Joblib / PyTorch)\"]")
    elif level == "intermediate":
        lines.append("        ModelEngine[\"Optimized Model Engine (ONNX / TorchScript)\"]")
        lines.append("        WorkerQueue[\"Async Task Worker (Celery / Background Tasks)\"]")
    else:
        lines.append("        ModelEngine[\"High-Throughput Model Serving (vLLM / Triton / TensorRT)\"]")
        lines.append("        VectorDB[\"Vector Store & Knowledge Index (pgvector / Chroma)\"]")
        lines.append("        WorkerQueue[\"Distributed Event Bus (Kafka / Redis Queue)\"]")
    lines.append("    end")

    lines.append("    subgraph DataLayer[\"4. Persistence & Storage Layer\"]")
    lines.append("        RelDB[(\"Relational DB (PostgreSQL / SQLite)\")]")
    lines.append("        FileStore[(\"Object / Media Storage (S3 / Local Dir)\")]")
    if level in ("intermediate", "advanced"):
        lines.append("        CacheStore[(\"In-Memory Cache (Redis)\")]")
    lines.append("    end")

    # Wire up connections
    lines.append("    UI -->|HTTPS / REST API| API")
    if is_hw:
        lines.append("    HW -->|MQTT / HTTP Telemetry| API")
    if "cv" in domains:
        lines.append("    Cam --> UI")
    lines.append("    API --> Auth")
    lines.append("    API --> RateLimiter")
    lines.append("    RateLimiter --> BizLogic")
    if "cv" in domains:
        lines.append("    BizLogic --> Preproc")
        lines.append("    Preproc --> ModelEngine")
    elif "nlp" in domains or "genai" in domains:
        lines.append("    BizLogic --> Tokenize")
        lines.append("    Tokenize --> ModelEngine")
    else:
        lines.append("    BizLogic --> ModelEngine")

    if level in ("intermediate", "advanced"):
        lines.append("    BizLogic --> WorkerQueue")
        lines.append("    WorkerQueue --> ModelEngine")
        lines.append("    BizLogic <--> CacheStore")

    lines.append("    BizLogic <--> RelDB")
    lines.append("    BizLogic <--> FileStore")
    if "genai" in domains and level == "advanced":
        lines.append("    ModelEngine <--> VectorDB")

    return "\n".join(lines)


def _build_mermaid_physical_architecture(idea: Idea, level: str, is_mechatronic: bool) -> str:
    """Generates an authentic mechanical assembly, kinematic, and power-flow Mermaid diagram."""
    lines = [
        "graph TD",
        "    subgraph PowerDrive[\"1. Actuation & Power Transmission Layer\"]",
        "        Motor[\"Drive Prime Mover (BLDC Motor / NEMA 23 Stepper / AC Gearmotor)\"]",
        "        Coupler[\"Flexible Spider Jaw Coupler (Zero-Backlash)\"]",
        "        Reduction[\"Speed Reduction Gearbox / Timing Belt Pulley (4:1)\"]",
        "    end",
        "    subgraph Kinematics[\"2. Kinematic Conversion & Motion Guidance\"]",
        "        LeadScrew[\"Precision Ball Screw (SFU1605) / Rack & Pinion\"]",
        "        LinearGuide[\"Hardened Linear Guide Rails & Bearings (MGN12 / HGR20)\"]",
        "        LinkageArm[\"Fabricated Kinematic Linkage (Al 6061-T6 / AISI 1018)\"]",
        "    end",
        "    subgraph Structure[\"3. Structural Frame & Mounting Assembly\"]",
        "        ChassisFrame[\"Rigid Tubular Spaceframe / ISMC Steel Channel Frame\"]",
        "        BearingHousing[\"CNC Milled Reamed Bearing Housings (ISO 286 H7)\"]",
        "        Worktable[\"Payload Worktable / End-Effector Tooling\"]",
        "    end",
    ]
    if is_mechatronic:
        lines.extend([
            "    subgraph Instrumentation[\"4. Mechatronic Control & Sensor Instrumentation\"]",
            "        MCU[\"Microcontroller (Arduino Mega 2560 / ESP32-WROOM-32)\"]",
            "        Driver[\"Opto-Isolated Motor Driver (TB6600 / 24V H-Bridge)\"]",
            "        Telemetry[\"Sensors: HX711 Load Cell + Rotary Optical Encoder\"]",
            "        Failsafe[\"Hardware E-Stop & Endstop Limit Switches (NC Loop)\"]",
            "    end",
            "    MCU --> Driver",
            "    Driver --> Motor",
            "    Telemetry -.->|Positional / Force Feedback| MCU",
            "    Failsafe -->|Emergency Trip Trigger| MCU",
        ])
    lines.extend([
        "    Motor --> Coupler",
        "    Coupler --> Reduction",
        "    Reduction --> LeadScrew",
        "    LeadScrew --> LinearGuide",
        "    LinearGuide --> LinkageArm",
        "    LinkageArm --> Worktable",
        "    ChassisFrame -.->|Structural Foundation| BearingHousing",
        "    BearingHousing -.-> LinearGuide",
    ])
    return "\n".join(lines)


def _build_cad_modeling_section(idea: Idea, level: str) -> dict[str, Any]:
    """Generates CAD 3D modeling, kinematics, degrees of freedom, and drawing specs."""
    return {
        "primary_cad_tool": "SolidWorks 2024 / CATIA V5 / Autodesk Fusion 360",
        "modeling_approach": "Parametric Top-Down Assembly with Master Model Skeleton Architecture",
        "assemblies": [
            {
                "subassembly_name": "Base Structural Frame & Chassis Assembly",
                "components_count": 14,
                "primary_material": "Aluminium 6061-T6 / Mild Steel AISI 1018 Channel",
                "mating_constraints": "Coincident floor anchor planes, concentric bolt holes, rigid weldment mates",
            },
            {
                "subassembly_name": "Kinematic Motion & Transmission Assembly",
                "components_count": 9,
                "primary_material": "Induction Hardened Ground Steel Shafts (CK45) & SFU1605 Ball Screw",
                "mating_constraints": "Screw mates (5mm pitch lead), concentric bearing journals, tangent cam/follower",
            },
            {
                "subassembly_name": "Working End-Effector / Tooling Carriage",
                "components_count": 7,
                "primary_material": "Aluminium 6061-T6 Milled Bracket + Polyurethane Dampers",
                "mating_constraints": "Parallel linear guide rails, limit distance stroke mates (0 to 250 mm)",
            },
        ],
        "kinematic_analysis": {
            "degrees_of_freedom": "1-DOF constrained linear stroke (Gruebler criterion m = 6*(N-1-J) + sum(fi) = 1)",
            "motion_study": "SolidWorks Motion simulation verifying peak linear velocity of 120 mm/s and acceleration of 0.8 m/s²",
            "collision_check": "Zero static or dynamic interference detected across 100% stroke travel envelope",
        },
        "drawing_standards": "ISO 128 / ASME Y14.5 compliant A3 drawing sheets with Third Angle projection and title block",
    }


def _build_fea_cfd_section(idea: Idea, level: str) -> dict[str, Any]:
    """Generates finite element analysis (FEA) and computational fluid dynamics (CFD) simulation data."""
    is_aero = any(d in idea.get("branches", []) for d in ("aero", "aeronautical", "auto")) or "cfd" in idea.get("domains", [])
    fea_data: dict[str, Any] = {
        "simulation_software": "ANSYS Workbench 2024 R1 (Static Structural & Modal Harmonic Response)",
        "meshing_methodology": "Adaptive Quadratic Tetrahedral & Hexahedral elements (SOLID187/SOLID186)",
        "mesh_metrics": {
            "total_nodes": 148520,
            "total_elements": 92340,
            "element_quality_average": 0.84,
            "mesh_convergence": "Refined across 4 iterations until peak stress variance was strictly < 2.8%",
        },
        "boundary_conditions": {
            "fixtures": "Fixed structural support at base mounting holes (all 6 degrees of freedom locked)",
            "applied_loads": "Dynamic design working load applied at center of span with 1.5x impact multiplier",
        },
        "stress_results": {
            "max_von_mises_stress_mpa": 112.4,
            "material_yield_strength_mpa": 276.0,  # Al 6061-T6 baseline
            "calculated_factor_of_safety": 2.45,
            "max_deformation_mm": 0.38,
            "critical_hotspot": "Fillet radius transition between vertical upright and horizontal bearing pedestal",
        },
        "modal_frequency_analysis": {
            "mode_1_natural_frequency_hz": 142.6,
            "operating_excitation_frequency_hz": 40.0,
            "resonance_margin_pct": 256.5,
            "resonance_risk": "Zero resonance hazard (natural frequency well above operating motor harmonics)",
        },
    }
    if is_aero:
        fea_data["cfd_analysis"] = {
            "cfd_tool": "ANSYS Fluent (k-epsilon Realizable Turbulence Model)",
            "inlet_velocity_ms": 15.0,
            "calculated_drag_coefficient_cd": 0.32,
            "lift_drag_ratio": 4.8,
            "boundary_layer_resolution": "y+ <= 3.5 along aerodynamic boundary surfaces",
            "findings": "Streamline separation point delayed by 28 mm using tapered trailing edge profile",
        }
    return fea_data


def _build_material_selection_section(idea: Idea, level: str) -> dict[str, Any]:
    """Generates material property matrices and Ashby selection trade-offs with Indian pricing."""
    return {
        "selection_framework": "Ashby Performance Index Optimization maximizing specific yield strength (sigma_y / rho)",
        "selected_materials": [
            {
                "material_name": "Aluminium 6061-T6",
                "application": "Structural linkage arms, carriage plate, CNC milled bracket mounts",
                "density_g_cm3": 2.70,
                "yield_strength_mpa": 276,
                "ultimate_tensile_strength_mpa": 310,
                "elastic_modulus_gpa": 68.9,
                "hardness": "95 HB (Brinell)",
                "approx_cost_inr_per_kg": 380,
                "advantages": "Excellent strength-to-weight ratio, superior corrosion resistance, high machinability rating",
            },
            {
                "material_name": "Mild Steel AISI 1018 / EN8",
                "application": "Drive shafts, heavy-duty base chassis frame, keyed couplings",
                "density_g_cm3": 7.85,
                "yield_strength_mpa": 365,
                "ultimate_tensile_strength_mpa": 440,
                "elastic_modulus_gpa": 205.0,
                "hardness": "126 HB / Induction hardenable to 55 HRC",
                "approx_cost_inr_per_kg": 85,
                "advantages": "High toughness, high fatigue endurance limit, cost-effective Indian market availability",
            },
            {
                "material_name": "3K Twill Carbon Fiber Composite / PETG 3D Polymer",
                "application": "Lightweight covers, aerodynamic fairings, sensor brackets",
                "density_g_cm3": 1.55,
                "yield_strength_mpa": 600,
                "ultimate_tensile_strength_mpa": 850,
                "elastic_modulus_gpa": 70.0,
                "hardness": "Shore 80D",
                "approx_cost_inr_per_kg": 1800,
                "advantages": "Extreme directional stiffness, near-zero thermal expansion, rapid prototyping turnaround",
            },
        ],
        "procurement_guidance": "Sourced through certified Indian industrial metal stockists with Mill Test Certificates (MTR).",
    }


def _build_fabrication_plan_section(idea: Idea, level: str) -> dict[str, Any]:
    """Generates workshop manufacturing operations sequence, tooling, and safety protocols."""
    return {
        "manufacturing_processes": [
            {
                "step_number": 1,
                "operation": "Raw Stock Preparation & Cut-off",
                "machine": "Horizontal Metal Band Saw / Hydraulic Shearing Machine",
                "parameters": "Cutting speed 45 m/min with flood soluble oil coolant",
                "output": "Stock billets cut to +2.0 mm over length allowance",
            },
            {
                "step_number": 2,
                "operation": "Cylindrical Turning & Facing",
                "machine": "Precision Centre Lathe (HMT / Enterprise)",
                "parameters": "Spindle speed 650 RPM, feed rate 0.12 mm/rev, carbide TNMG insert",
                "output": "Turned stepped shafts with bearing journals finished to Ra <= 0.8 um",
            },
            {
                "step_number": 3,
                "operation": "CNC 3-Axis Milling & Reaming",
                "machine": "CNC Vertical Machining Centre (VMC)",
                "parameters": "Spindle 2400 RPM, flood coolant, solid carbide reamer for H7 bearing bores",
                "output": "Reamed bearing housings conforming strictly to ISO 286 H7 (+0.021/-0.000 mm)",
            },
            {
                "step_number": 4,
                "operation": "Frame Fabrication & TIG/MIG Welding",
                "machine": "TIG (GTAW) 200A Welding Machine with 100% Argon Shielding Gas",
                "parameters": "Welding current 110-130A, ER70S-6 filler wire, continuous argon back purge",
                "output": "Rigid tubular chassis / base frame with zero angular thermal distortion",
            },
            {
                "step_number": 5,
                "operation": "Surface Finishing & Corrosion Protection",
                "machine": "Degreasing Bath + Sulphuric Acid Anodizing / Powder Coating Booth",
                "parameters": "25-micron hard anodize for aluminium; red-oxide primer + epoxy powder coat for steel",
                "output": "Scratch-resistant, corrosion-proof industrial finish",
            },
        ],
        "workshop_safety": [
            "Mandatory PPE: Safety goggles, steel-toe boots, ear protection, and leather welding apron",
            "Emergency stop push buttons installed within immediate reach of lathe and milling workstations",
            "Continuous exhaust fume extraction active during all TIG/MIG welding operations",
        ],
    }


def _build_mechanical_bom_section(idea: Idea, level: str) -> list[dict[str, Any]]:
    """Generates an authentic Mechanical Bill of Materials with Indian market pricing in INR."""
    bom = [
        {"item": "Deep Groove Ball Bearings (SKF 6204-2RS / 608RS, 4 nos)", "category": "Bearings", "approx_price_inr": 850, "indian_source": "Authorized SKF / FAG Bearings Distributor"},
        {"item": "Precision Ground Linear Shafts (Hard Chrome Plated CK45, Dia 16mm x 1000mm, 2 nos)", "category": "Shafts & Guides", "approx_price_inr": 1700, "indian_source": "Robu.in / local machinery mart"},
        {"item": "Precision Rolled Ball Screw (SFU1605 with anti-backlash ball nut, 400mm length)", "category": "Actuators & Screws", "approx_price_inr": 2400, "indian_source": "Industrial CNC Automation Hub"},
        {"item": "Flexible Aluminum Spider Jaw Shaft Couplers (8mm to 12mm, 2 nos)", "category": "Couplers", "approx_price_inr": 560, "indian_source": "Robotics India / local tooling shop"},
        {"item": "Helical / Spur Drive Gears (EN8 Case Hardened, Module 1.5, 20T & 80T pair)", "category": "Power Transmission", "approx_price_inr": 1600, "indian_source": "Precision Gear Works, Coimbatore / Pune"},
        {"item": "High-Torque NEMA 23 Stepper Motor (2.5 Nm, 3.0A) or 48V BLDC Geared Drive", "category": "Actuation Prime Mover", "approx_price_inr": 2800, "indian_source": "RoboCraze / Quartz Components"},
        {"item": "Structural Fasteners Pack (ISO 4762 Grade 8.8 / 10.9 Allen Socket Screws + Nyloc Nuts)", "category": "Fasteners & Hardware", "approx_price_inr": 450, "indian_source": "Unbrako / TVS Fastener Retailers"},
        {"item": "Raw Material Stock Billet (Aluminium 6061-T6 plates + AISI 1018 mild steel tubes)", "category": "Raw Metals Stock", "approx_price_inr": 2200, "indian_source": "Local City Metal Industrial Estate"},
    ]
    return bom


def _build_gdt_tolerances_section(idea: Idea, level: str) -> dict[str, Any]:
    """Generates Geometric Dimensioning and Tolerancing (GD&T) specifications and testing standards."""
    return {
        "tolerance_fits": [
            {"fit_type": "Bearing Outer Ring in Housing", "iso_fit": "H7/h6", "clearance_type": "Transition / Light Push Fit", "tolerance_range_mm": "+0.000 to +0.021 mm"},
            {"fit_type": "Shaft Journal in Bearing Inner Ring", "iso_fit": "H7/g6", "clearance_type": "Precision Running Slide Fit", "tolerance_range_mm": "-0.007 to -0.016 mm"},
            {"fit_type": "Keyway Width & Drive Key Fit", "iso_fit": "P9/h9", "clearance_type": "Interference Drive Key Fit", "tolerance_range_mm": "-0.012 to -0.042 mm"},
        ],
        "geometric_tolerances": [
            {"feature": "Shaft Bearing Journal Diameter", "symbol": "Cylindricity", "tolerance_value_mm": 0.015, "datum": "Datum Axis A-B"},
            {"feature": "Base Mounting Worktable Surface", "symbol": "Flatness", "tolerance_value_mm": 0.040, "datum": "Primary Base Surface"},
            {"feature": "Vertical Guide Column Axis", "symbol": "Perpendicularity", "tolerance_value_mm": 0.025, "datum": "Datum Plane A"},
            {"feature": "Driven Shaft Pulley Shoulder", "symbol": "Circular Runout", "tolerance_value_mm": 0.020, "datum": "Datum Axis A"},
        ],
        "physical_testing_standards": [
            "ASTM E8 / IS 1608: Tensile testing of welded chassis and linkage coupon specimens",
            "ASTM E10 / ASTM E18: Brinell and Rockwell surface hardness testing of hardened shaft journals",
            "IS 13917 / ISO 1940-1: Grade G2.5 dynamic balancing of rotating drive shafts and flywheels",
            "ASTM D3359: Cross-hatch adhesion inspection for anti-corrosion powder coating",
        ],
    }


def _build_embedded_sensors_section(idea: Idea, level: str, is_mechatronic: bool) -> dict[str, Any] | None:
    """Conditionally includes embedded systems and sensors without forcing artificial AI requirements."""
    if not is_mechatronic:
        return None
    return {
        "subsystem_type": "Electromechanical / Mechatronic Control & Sensor Instrumentation",
        "microcontroller": "Arduino Mega 2560 R3 / ESP32-WROOM-32 (Industrial Opto-Isolated I/O)",
        "sensors": [
            {"sensor_name": "HX711 Strain Gauge Load Cell (50 kg)", "measurement": "Applied axial thrust / clamping force feedback", "interface": "2-Wire Serial (PD_SCK & DOUT)"},
            {"sensor_name": "Optical Rotary Incremental Encoder (600 P/R)", "measurement": "Real-time shaft position and rotational RPM", "interface": "Quadrature Channel A/B Interrupts"},
            {"sensor_name": "Industrial Microswitch Limit Endstops (NC)", "measurement": "Home datum calibration and hardware overtravel trip", "interface": "Normally-Closed Hardware Interlock"},
        ],
        "motor_drivers": [
            {"driver_model": "TB6600 4A Stepper Driver / Cytron 20A DC Driver", "specs": "9-42V DC input, opto-isolated step/direction signaling, adjustable microstepping"},
        ],
        "power_supply": "24V 10A (240W) SMPS Industrial Power Supply with overload trip and thermal shutdown",
        "design_note": "Included strictly for mechatronic closed-loop actuation and physical telemetry without forcing AI or cloud dependencies.",
    }


def _build_mermaid_er(idea: Idea) -> str:
    """Generates a valid Mermaid ER Diagram from the idea's declared entity relationships."""
    lines = ["erDiagram"]

    # Entities and attributes
    for table_name, comment, cols in idea.get("entities", []):
        lines.append(f"    {table_name.upper()} {{")
        for col in cols:
            col_name, col_type, col_meta = col[0], col[1], col[2] if len(col) > 2 else ""
            clean_type = col_type.split("(")[0].replace(" ", "_")
            meta = ""
            if "PK" in col_meta:
                meta = "PK"
            elif "FK" in col_meta:
                meta = "FK"
            lines.append(f"        {clean_type} {col_name} {meta}".rstrip())
        lines.append("    }")

    # Infer relationships from FK declarations
    relationships: set[str] = set()
    for table_name, _, cols in idea.get("entities", []):
        for col in cols:
            col_meta = col[2] if len(col) > 2 else ""
            if "FK" in col_meta:
                parts = col_meta.split()
                for p in parts:
                    if "." in p:
                        target_table = p.split(".")[0].upper()
                        source_table = table_name.upper()
                        rel = f"    {target_table} ||--o{{ {source_table} : references"
                        relationships.add(rel)

    for rel in sorted(relationships):
        lines.append(rel)

    return "\n".join(lines)


def _generate_modules(idea: Idea, level: str) -> list[dict[str, Any]]:
    """Builds modular system components with clear contracts."""
    modules = [
        {
            "id": "MOD-1",
            "name": "Authentication & User Management Module",
            "description": "Handles secure student/faculty signup, token creation, role permissions and session lifecycle.",
            "inputs": "Credentials, registration forms, JWT tokens",
            "outputs": "Authorized sessions, user profiles, role verification signals",
            "technologies": ["FastAPI Security", "PyJWT", "bcrypt", "Pydantic"],
            "responsibilities": [
                "Credential hashing with salt and validation",
                "Role-based access gating (Student, Faculty / Mentor, Admin)",
                "Session renewal and secure credential rotation",
            ],
        },
        {
            "id": "MOD-2",
            "name": "Data Ingestion & Preprocessing Pipeline",
            "description": "Receives raw user inputs (images, audio, sensors, text), runs validation, noise-filtering, and converts to model tensors.",
            "inputs": "Uploaded media files, live camera streams, or IoT telemetry frames",
            "outputs": "Cleaned, scaled, normalized numerical feature tensors ready for inference",
            "technologies": ["OpenCV", "Pillow", "NumPy", "Pandas", "Albumentations"],
            "responsibilities": [
                "Format verification, dimension resizing and range normalization",
                "Noise reduction and anomaly filtering",
                "Data caching and batch preparation",
            ],
        },
        {
            "id": "MOD-3",
            "name": "Core Machine Learning / AI Engine",
            "description": f"Executes inference using the fine-tuned {idea.get('model', 'AI')} architecture with confidence calibration.",
            "inputs": "Preprocessed tensors or prompt tokens",
            "outputs": "Classification labels, regression values, bounding boxes, or generated text with explainability scores",
            "technologies": ["PyTorch / TensorFlow", "ONNX Runtime", "scikit-learn", "Hugging Face"],
            "responsibilities": [
                "Singleton model loading on application startup",
                "Forward pass execution with thread-safe inference",
                "Extraction of explainability heatmaps (Grad-CAM/SHAP) or token citations",
            ],
        },
        {
            "id": "MOD-4",
            "name": "Business Logic & Analytics Core",
            "description": "Applies domain business rules, computes risk scores/aggregates, and stores historical operational logs.",
            "inputs": "Model prediction outputs, user contextual parameters",
            "outputs": "Actionable recommendations, alerts, aggregated statistics, database records",
            "technologies": ["Python Services", "SQLAlchemy 2.0", "FastAPI"],
            "responsibilities": [
                "Mapping raw model classes to actionable human-readable advice",
                "Threshold evaluation and triggering automated alert notifications",
                "Historical trend aggregation for analytics dashboards",
            ],
        },
        {
            "id": "MOD-5",
            "name": "API Service & Integration Layer",
            "description": "Exposes standardized RESTful endpoints, provides auto-documented OpenAPI contracts, and integrates third-party services.",
            "inputs": "Client HTTP/WebSocket requests, external webhooks",
            "outputs": "Structured JSON responses, downloadable exports (PDF/CSV), streaming events",
            "technologies": ["FastAPI", "Swagger/OpenAPI", "HTTPX", "ReportLab"],
            "responsibilities": [
                "Strict request/response validation through Pydantic schemas",
                "Error handling with standard RFC 7807 problem details",
                "Third-party external API integration with retry policies",
            ],
        },
        {
            "id": "MOD-6",
            "name": "Interactive Client Presentation UI",
            "description": "Modern responsive interface for students/mentors to interact with predictions, explore visual analytics, and manage records.",
            "inputs": "User mouse/keyboard/camera interactions, WebSocket updates",
            "outputs": "Rendered graphs, real-time feedback, interactive dashboards, accessible forms",
            "technologies": ["React", "Vite", "Chart.js / Lucide", "CSS Grid/Flexbox"],
            "responsibilities": [
                "Intuitive file upload with instant client-side preview",
                "Real-time rendering of confidence meters and explainability overlays",
                "Responsive design for both desktop and mobile screens",
            ],
        },
    ]

    if idea["type"] in ("hardware", "hybrid"):
        modules.insert(1, {
            "id": "MOD-HW",
            "name": "Hardware Acquisition & Edge Telemetry Module",
            "description": "Reads physical sensors, runs initial edge filtering, and transmits packets over serial or MQTT/HTTP.",
            "inputs": "Physical environmental signals (voltage, resistance, I2C/SPI signals)",
            "outputs": "Serialized JSON sensor frames with timestamps and checksums",
            "technologies": ["C++ / MicroPython", "ESP32 / Arduino", "FreeRTOS", "MQTT PubSubClient"],
            "responsibilities": [
                "Analog-to-digital conversion and sensor calibration curves",
                "Local hardware watchdog timers and auto-reconnect logic",
                "Safe actuator triggering (relays, servos, buzzers) with failsafes",
            ],
        })

    return modules


def _generate_technologies_grid(idea: Idea, level: str) -> dict[str, Any]:
    """Generates complete technology definitions across all 22 required areas."""
    grid = {}
    domains = set(idea["domains"])

    for key, label in AREAS:
        area_info = dict(STACK[key][level])

        # Add domain-specific enhancements
        addons = []
        if key in DOMAIN_ADDONS:
            for d in domains:
                if d in DOMAIN_ADDONS[key]:
                    addons.extend(DOMAIN_ADDONS[key][d])
        if addons:
            area_info["tools"] = area_info["tools"] + addons

        # Add interest-specific third-party integrations
        if key == "third_party":
            for interest in idea.get("interests", []):
                if interest in INTEREST_INTEGRATIONS:
                    area_info["tools"] = list(set(area_info["tools"] + INTEREST_INTEGRATIONS[interest]))

        grid[key] = {
            "area_id": key,
            "area_label": label,
            "tools": area_info["tools"],
            "rationale": area_info["why"],
            "best_practices": area_info["practices"],
        }

    # If hardware/hybrid, include hardware stack
    if idea["type"] in ("hardware", "hybrid"):
        hw_info = HARDWARE_STACK[level]
        grid["hardware"] = {
            "area_id": "hardware",
            "area_label": "Hardware & Embedded Systems",
            "tools": hw_info["tools"],
            "rationale": hw_info["why"],
            "best_practices": hw_info["practices"],
        }

    return grid


def _generate_roadmap(months: int, team_size: int, level: str) -> list[dict[str, Any]]:
    """Builds a realistic phase-by-phase sprint roadmap tailored to project duration and team size."""
    phases_count = min(6, max(3, months))
    phase_names = [
        ("Phase 1: Research, Problem Definition & Environment Setup", 0.15),
        ("Phase 2: Dataset Collection, Data Preprocessing & Baseline AI", 0.25),
        ("Phase 3: Backend API, Database Architecture & Core Services", 0.20),
        ("Phase 4: Frontend Development, User Experience & Integration", 0.20),
        ("Phase 5: Model Optimization, Verification & Comprehensive Testing", 0.10),
        ("Phase 6: Cloud Deployment, Documentation & Viva Preparation", 0.10),
    ]

    total_weeks = months * 4
    roadmap = []
    task_counter = 1

    tasks_pool = [
        # Phase 1
        [
            ("Formulate Problem Statement & IEEE literature review of 10+ papers", 20, "Approved project synopsis & paper survey matrix"),
            ("Design System Architecture, Component block diagrams & DFDs", 16, "Architecture specification document"),
            ("Initialize Git Repository with branching rules, CI templates and README", 10, "Working GitHub repo with README and .gitignore"),
        ],
        # Phase 2
        [
            ("Collect, clean and annotate domain dataset with train/val/test splits", 32, "Verified clean dataset with exploratory data analysis notebook"),
            ("Build baseline machine learning model and benchmark baseline accuracy", 24, "Baseline evaluation report (precision, recall, F1, confusion matrix)"),
            ("Train core deep learning / AI architecture with data augmentation", 36, "Exported model weights (.onnx / .pt) and training loss curves"),
        ],
        # Phase 3
        [
            ("Implement SQLAlchemy relational schema and SQLite/PostgreSQL migrations", 18, "Database tables initialized with sample seed data"),
            ("Develop FastAPI endpoints for authentication, file handling and predictions", 28, "Interactive Swagger docs testing all CRUD & prediction routes"),
            ("Implement background task queue and error handling middleware", 20, "Tested async worker processing without blocking HTTP request thread"),
        ],
        # Phase 4
        [
            ("Build responsive client interface using React, Vite and CSS design system", 30, "Pixel-perfect modern dashboard matching design specification"),
            ("Integrate frontend with backend REST API and handle async states (loading/error)", 22, "Full end-to-end user journey functional in browser"),
            ("Implement data visualization widgets (charts, confidence meters, logs)", 18, "Visual analytics views for prediction history and metrics"),
        ],
        # Phase 5
        [
            ("Perform unit testing (pytest) and API integration tests with coverage report", 24, "Automated test suite achieving ≥ 75% code coverage"),
            ("Conduct model robustness tests (outlier inputs, noise, adversarial edge cases)", 18, "Model reliability and failure-mode analysis report"),
            ("Security audit: input validation, SQL injection tests, CORS & rate limit audit", 14, "Security hardening checklist and OWASP compliance sheet"),
        ],
        # Phase 6
        [
            ("Containerize application with Docker & Docker Compose and test local deploy", 18, "Multi-container compose file running app with zero config"),
            ("Write final IEEE format project report (Chapters 1 to 8) and project book", 36, "Completed, bind-ready final year project thesis PDF"),
            ("Design 12-slide final presentation deck and conduct mock viva Q&A drill", 16, "Presentation slides and rehearsed demo video recording"),
        ]
    ]

    current_week = 1
    for p_idx in range(phases_count):
        p_title, p_weight = phase_names[p_idx]
        p_weeks = max(1, round(total_weeks * p_weight))
        end_week = min(total_weeks, current_week + p_weeks - 1)

        phase_tasks = []
        for t_title, base_hours, deliverable in tasks_pool[p_idx]:
            # Scale effort based on team size & level
            scaled_hours = round(base_hours * (1.0 if team_size <= 2 else 1.3) * (0.8 if level == "beginner" else (1.0 if level == "intermediate" else 1.25)))
            t_id = f"p{p_idx + 1}-t{task_counter}"
            phase_tasks.append({
                "id": t_id,
                "title": t_title,
                "estimated_hours": scaled_hours,
                "deliverable": deliverable,
            })
            task_counter += 1

        roadmap.append({
            "phase_number": p_idx + 1,
            "title": p_title,
            "duration": f"Weeks {current_week} – {end_week}",
            "weeks_count": p_weeks,
            "tasks": phase_tasks,
        })
        current_week = end_week + 1

    return roadmap


def _generate_testing_plan(idea: Idea, level: str) -> list[dict[str, Any]]:
    """Generates structured test cases covering all verification facets."""
    return [
        {
            "id": "TC-01",
            "category": "Authentication",
            "scenario": "User registration with weak password or invalid email",
            "test_input": "Email without '@', password with only lowercase characters",
            "expected_output": "HTTP 422 Unprocessable Entity with explicit validation message; no user created",
            "type": "Unit & API Test",
        },
        {
            "id": "TC-02",
            "category": "Data Preprocessing",
            "scenario": "Handling corrupted or unsupported file upload",
            "test_input": "0-byte file or disguised .exe renamed as .png / .csv",
            "expected_output": "HTTP 400 Bad Request: 'Invalid file format or corrupted payload'; clean failure",
            "type": "Integration Test",
        },
        {
            "id": "TC-03",
            "category": "AI Model Inference",
            "scenario": "Prediction on standard valid input",
            "test_input": "Standard normalized input tensor from test set",
            "expected_output": f"HTTP 200 with prediction label, confidence score in range [0.0, 1.0], response time < 500ms",
            "type": "Performance & Functional",
        },
        {
            "id": "TC-04",
            "category": "Model Generalization",
            "scenario": "Evaluation on unseen out-of-distribution / edge case sample",
            "test_input": "Low-contrast, blurry or noisy input sample",
            "expected_output": "System signals low confidence (< threshold) and recommends manual verification instead of wrong assertion",
            "type": "AI Safety & Robustness",
        },
        {
            "id": "TC-05",
            "category": "Database Integrity",
            "scenario": "Concurrent write requests for same entity",
            "test_input": "Multiple simultaneous POST requests simulating 20 concurrent users",
            "expected_output": "Zero database deadlocks; all writes persisted consistently with unique IDs",
            "type": "Concurrency Test",
        },
        {
            "id": "TC-06",
            "category": "Security & Authorization",
            "scenario": "Student user attempting to invoke mentor/admin review endpoint",
            "test_input": "Bearer token belonging to user with 'student' role",
            "expected_output": "HTTP 403 Forbidden: 'Insufficient permissions for this action'",
            "type": "Security & RBAC",
        },
    ]


def _generate_presentation_slides(idea: Idea, level: str) -> list[dict[str, Any]]:
    """Builds a 10-12 slide final-year project presentation guide."""
    tier_title = idea["tiers"][level][0]
    return [
        {
            "slide_number": 1,
            "title": "Title & Team Introduction",
            "key_points": [
                f"Project Title: {tier_title}",
                f"Domain: {', '.join(AI_DOMAINS.get(d, d) for d in idea['domains'])}",
                "Names of Team Members, Register Numbers, Branch & Batch",
                "Name of Project Guide / Supervisor and College Department",
            ],
            "visual_recommendation": "High-impact title slide with crisp branding and college logo.",
        },
        {
            "slide_number": 2,
            "title": "Problem Statement & Motivation",
            "key_points": [
                f"Core Challenge: {idea['problem']}",
                f"Primary Beneficiaries: {idea['users']}",
                "Quantifiable impact: Why this project matters right now in the real world.",
            ],
            "visual_recommendation": "Problem diagram or real-world photograph illustrating the issue.",
        },
        {
            "slide_number": 3,
            "title": "Literature Review & Existing Systems",
            "key_points": [
                "Summary of 3–4 standard existing approaches or published papers.",
                "Limitations of existing methods: high cost, low accuracy, high latency, poor accessibility.",
                "Tabular comparison contrasting existing systems against our proposed work.",
            ],
            "visual_recommendation": "Comparative feature matrix with checkmarks and crosses.",
        },
        {
            "slide_number": 4,
            "title": "Project Objectives & Scope",
            "key_points": idea["objectives"] + [f"Scope Level: {LEVEL_LABELS[level]} tier implementation"],
            "visual_recommendation": "Numbered objective cards with bold highlight metrics.",
        },
        {
            "slide_number": 5,
            "title": "System Architecture & Block Diagram",
            "key_points": [
                "End-to-end architectural flow: Client → API Gateway → AI Engine → Database.",
                "Modularity and clean separation of concerns.",
                "How data flows from input capture to user action.",
            ],
            "visual_recommendation": "The Mermaid System Architecture diagram generated in this blueprint.",
        },
        {
            "slide_number": 6,
            "title": "Dataset & Preprocessing Pipeline",
            "key_points": [
                f"Dataset: {idea.get('dataset', 'Domain specific dataset')}",
                "Preprocessing techniques: Cleaning, normalization, resizing, augmentation.",
                "Train / Validation / Test split strategy ensuring no data leakage.",
            ],
            "visual_recommendation": "Sample input images/data rows and class distribution bar chart.",
        },
        {
            "slide_number": 7,
            "title": "AI / ML Model Design & Training",
            "key_points": [
                f"Chosen Architecture: {idea.get('model', 'Machine Learning model')}",
                "Training parameters: Loss function, optimizer, learning rate, epochs, batch size.",
                "Key technical choices: Transfer learning / fine-tuning rationale.",
            ],
            "visual_recommendation": "Neural network layer diagram or training loss/accuracy curve.",
        },
        {
            "slide_number": 8,
            "title": "Key Modules & Implementation Highlights",
            "key_points": [
                "Backend services and REST API endpoints built with FastAPI.",
                "Interactive user interface developed in React.",
                "Security measures: Password hashing, JWT tokens and input validation.",
            ],
            "visual_recommendation": "Code snippets of key algorithms or database schema diagram.",
        },
        {
            "slide_number": 9,
            "title": "Experimental Results & Performance Evaluation",
            "key_points": [
                "Quantitative metrics: Accuracy, Precision, Recall, F1-Score, ROC-AUC, Latency.",
                "Confusion matrix and ablation study results.",
                "Verification against real-world sample tests.",
            ],
            "visual_recommendation": "Confusion matrix heatmap and bar chart comparing model iterations.",
        },
        {
            "slide_number": 10,
            "title": "Live Demonstration Walkthrough",
            "key_points": [
                "Live end-to-end execution of a typical user scenario.",
                "Highlight handling of edge cases and instant visual feedback.",
                "Display of generated reports / export features.",
            ],
            "visual_recommendation": "Screenshots of application UI with annotation callouts.",
        },
        {
            "slide_number": 11,
            "title": "Conclusion, Limitations & Future Scope",
            "key_points": [
                "Summary of achieved milestones against original objectives.",
                "Known current limitations (edge cases, hardware constraints).",
                "Future work: Mobile app release, edge device deployment, regional language support.",
            ],
            "visual_recommendation": "Two-column slide: 'What was achieved' vs 'Future enhancements'.",
        },
        {
            "slide_number": 12,
            "title": "References & Questions (Q&A)",
            "key_points": [
                "Key research papers (IEEE, ACM, Springer citations).",
                "Official datasets and documentation links.",
                "Open for questions from external examiners and evaluators.",
            ],
            "visual_recommendation": "Formal reference list and contact details.",
        },
    ]


def _generate_viva_qa(idea: Idea, level: str) -> list[dict[str, str]]:
    """Assembles a curated list of viva questions combining idea-specific and category questions."""
    curated = []

    # 1. Idea-specific questions (most valuable!)
    for q, a in idea.get("viva", []):
        curated.append({"category": "Domain Specific", "question": q, "answer": a})

    # 2. Project & architecture questions
    for q, a in VIVA_BANK.get("project", [])[:3]:
        curated.append({"category": "Project Defense", "question": q, "answer": a})

    # 3. Domain questions (cv, nlp, ml, dl, etc.)
    for d in idea.get("domains", []):
        if d in VIVA_BANK:
            for q, a in VIVA_BANK[d][:2]:
                curated.append({"category": f"AI / {d.upper()}", "question": q, "answer": a})

    # 4. Full stack & engineering questions
    for cat in ("database", "backend", "security", "testing"):
        if cat in VIVA_BANK:
            q, a = VIVA_BANK[cat][0]
            curated.append({"category": cat.capitalize(), "question": q, "answer": a})

    # 5. Advanced extras if applicable
    if level == "advanced" and "advanced" in LEVEL_EXTRA:
        for q, a in LEVEL_EXTRA["advanced"][:2]:
            curated.append({"category": "Advanced System Design", "question": q, "answer": a})

    return curated


def _generate_physical_modules(idea: Idea, level: str, is_mechatronic: bool) -> list[dict[str, Any]]:
    """Builds physical engineering sub-assemblies and functional hardware modules."""
    modules = [
        {
            "id": "MOD-1",
            "name": "Structural Frame, Chassis & Foundation Mounting",
            "description": "Defines rigid chassis geometry, foundation mounting points, and structural member profiles (ISMC steel / 6061 aluminium extrusion).",
            "inputs": "Envelope packaging constraints, payload mass, static load ratings",
            "outputs": "Rigid welded/fastened chassis frame with calculated deflection < 0.5 mm",
            "technologies": ["SolidWorks 2024", "ISMC Steel Channels", "Al 6061-T6", "TIG/MIG Welding"],
            "responsibilities": [
                "Packaging envelope and center-of-gravity calculation",
                "Weldment cut list and joint notch angle preparation",
                "Anti-vibration rubber isolation pad mounting",
            ],
        },
        {
            "id": "MOD-2",
            "name": "Power Transmission & Kinematic Mechanism",
            "description": "Converts motor rotation into linear or angular work output via gear reduction, precision ball screws, or 4-bar linkages.",
            "inputs": "Motor torque curves, target travel speed, output stroke range",
            "outputs": "Multiplied mechanical torque and smooth kinematic trajectory with minimal backlash",
            "technologies": ["Precision Ball Screw SFU1605", "Helical Gear Train", "SKF Deep Groove Bearings", "Flexible Jaw Couplers"],
            "responsibilities": [
                "Reduction ratio calculation matching required payload inertia",
                "Shaft step fillet design with stress concentration mitigation",
                "Axial pre-load adjustment eliminating kinematic backlash",
            ],
        },
        {
            "id": "MOD-3",
            "name": "CAD 3D Modeling, FEA Simulation & Stress Analysis",
            "description": "High-fidelity parametric solid modeling and finite element structural simulation verifying factor of safety under peak dynamic load.",
            "inputs": "Working peak dynamic load, boundary constraint anchors, material properties",
            "outputs": "von Mises stress contour maps, mesh convergence plots, certified Factor of Safety >= 2.5",
            "technologies": ["SolidWorks CAD", "ANSYS Workbench Static Structural", "Adaptive Tetrahedral Meshing"],
            "responsibilities": [
                "Full 3D parametric CAD assembly with mates and collision checks",
                "Quadratic finite element meshing with refinement at critical fillet radii",
                "Verification that maximum equivalent stress <= 50% of material yield strength",
            ],
        },
        {
            "id": "MOD-4",
            "name": "Material Procurement & Subtractive/Additive Fabrication",
            "description": "Execution of workshop manufacturing operations including CNC milling, centre lathe turning, cutting, and 3D printing.",
            "inputs": "Engineering drawing sheets, raw stock billets, CAM toolpaths",
            "outputs": "Finished components conforming to dimensional tolerances and surface roughness specs",
            "technologies": ["CNC 3-Axis Milling", "Centre Lathe", "Fiber Laser Sheet Cutting", "FDM 3D Printing"],
            "responsibilities": [
                "Spindle speeds and feeds calculation based on workpiece metallurgy",
                "Precision boring and turning of bearing journals",
                "Deburring, surface degreasing, and anti-corrosion primer coating",
            ],
        },
        {
            "id": "MOD-5",
            "name": "GD&T Quality Inspection, Metrology & Physical Testing",
            "description": "Validation of machined fits against ISO 286 tolerance limits and experimental load-deflection testing.",
            "inputs": "Fabricated prototype, dial indicators, vernier calipers, calibrated test loads",
            "outputs": "Inspection verification sheet, static load deflection curves, runout measurement log",
            "technologies": ["Digital Vernier & Micrometer", "Dial Indicator with Magnetic Base", "ASTM E8 Tensile Standards"],
            "responsibilities": [
                "Shaft-bearing fit tolerance verification (ISO 286 H7/g6 and H7/p6)",
                "Shaft total indicator reading (TIR) runout measurement <= 0.03 mm",
                "Experimental proof load test verifying zero permanent plastic deformation",
            ],
        },
    ]
    if is_mechatronic:
        modules.insert(3, {
            "id": "MOD-ELEC",
            "name": "Mechatronic Controls, Actuation & Sensor Instrumentation",
            "description": "Embedded controller interfacing for motor driver pulsing, closed-loop position/strain feedback, and emergency trip interlocks.",
            "inputs": "24V DC power, operator control inputs, limit switch trigger states",
            "outputs": "PWM/Step pulses to motor drivers, real-time load/position sensor data",
            "technologies": ["Arduino Mega / ESP32", "TB6600 Stepper Driver", "HX711 Strain Gauge Amplifier", "Optical Encoder"],
            "responsibilities": [
                "Opto-isolated stepper motor pulse generation",
                "Load cell calibration curve for real-time force measurement",
                "Failsafe hardware emergency stop and software travel limit trips",
            ],
        })
    return modules


def _generate_physical_technologies_grid(idea: Idea, level: str, is_mechatronic: bool) -> dict[str, Any]:
    """Generates complete technology definitions across all 22 physical engineering disciplines."""
    grid = {}
    for key, label in PHYSICAL_AREAS:
        if key == "embedded_mechatronics" and not is_mechatronic:
            continue
        area_info = dict(PHYSICAL_STACK[key][level])
        grid[key] = {
            "area_id": key,
            "area_label": label,
            "tools": area_info["tools"],
            "rationale": area_info["why"],
            "best_practices": area_info["practices"],
        }
    return grid


def _generate_physical_roadmap(months: int, team_size: int, level: str) -> list[dict[str, Any]]:
    """Builds a realistic 6-phase physical fabrication and testing lifecycle roadmap."""
    phases_count = min(6, max(3, months))
    phase_names = [
        ("Phase 1: Problem Definition, Literature Survey & Mechanism Synthesis", 0.15),
        ("Phase 2: 3D CAD Modeling, Kinematic Motion & Assembly Mating", 0.20),
        ("Phase 3: FEA Structural Stress Analysis, CFD & Factor of Safety Optimization", 0.20),
        ("Phase 4: Material Procurement & Workshop CNC/Machining Fabrication", 0.20),
        ("Phase 5: Sub-Assembly, GD&T Inspection & Physical Prototype Testing", 0.15),
        ("Phase 6: Final Technical Documentation, Drawing Sheets & Viva Defense", 0.10),
    ]

    total_weeks = months * 4
    roadmap = []
    task_counter = 1

    tasks_pool = [
        # Phase 1
        [
            ("Formulate mechanical problem statement and survey 10+ ASME/IEEE research papers", 18, "Approved project synopsis & mechanisms survey matrix"),
            ("Analytical kinematic synthesis and degree-of-freedom (Gruebler) calculations", 16, "Kinematic synthesis document with motion equations"),
            ("Define packaging envelope, operational load specs and Factor of Safety targets", 12, "Design requirements specification (DRS) document"),
        ],
        # Phase 2
        [
            ("Develop parametric 3D CAD parts in SolidWorks/CATIA with standard mate constraints", 30, "Parametric 3D solid model file package (.SLDPRT / .STEP)"),
            ("Perform SolidWorks motion study to simulate stroke, linkage clearance and interference", 22, "Kinematic motion study video and collision-free clearance report"),
            ("Compile detailed Mechanical Bill of Materials (BOM) with commercial vendor catalog parts", 16, "Procurement-ready BOM with Indian market pricing"),
        ],
        # Phase 3
        [
            ("Set up ANSYS Workbench static structural model with fixed constraints and working loads", 24, "Initialized FEA model with applied boundary conditions"),
            ("Execute quadratic tetrahedral mesh refinement at critical fillet radii and hole notches", 20, "Mesh convergence curve verifying stress stability within 3%"),
            ("Evaluate von Mises equivalent stress, deformation contours and certify FOS >= 2.5", 22, "FEA stress report with safety factor certificate and CFD if applicable"),
        ],
        # Phase 4
        [
            ("Procure standardized raw stock materials (Al 6061, AISI 1018 steel) and catalog bearings", 18, "Verified material stock and vendor delivery sign-off"),
            ("Perform centre lathe cylindrical turning, facing, boring and CNC milling operations", 32, "Machined precision drive shafts, bearing housings and brackets"),
            ("Execute TIG/MIG welding of tubular chassis or sheet metal laser cutting and press brake bending", 28, "Fabricated primary structural frame ready for assembly"),
        ],
        # Phase 5
        [
            ("Perform GD&T dimensional inspection using vernier, micrometer and bore gauge (ISO 286)", 18, "Inspection dimensional quality sign-off report"),
            ("Assemble sub-assemblies with Grade 8.8 fasteners, Nyloc nuts and SKF bearings", 24, "Fully assembled physical mechanical prototype"),
            ("Execute static proof load test and measure elastic deflection under dial indicator", 20, "Experimental load-deflection test curve correlating with FEA"),
        ],
        # Phase 6
        [
            ("Draft production engineering drawing sheets (ISO 128 / ASME Y14.5) with full GD&T", 24, "Complete A3 drawing sheets set with title blocks and exploded views"),
            ("Write IEEE/AICTE standard final-year engineering thesis chapters 1 through 8", 32, "Bind-ready final year engineering capstone project report PDF"),
            ("Prepare 12-slide presentation deck and conduct mock viva voce defense drill", 16, "Final slide deck and rehearsed mechanical defense walkthrough"),
        ]
    ]

    current_week = 1
    for p_idx in range(phases_count):
        p_title, p_weight = phase_names[p_idx]
        p_weeks = max(1, round(total_weeks * p_weight))
        end_week = min(total_weeks, current_week + p_weeks - 1)

        phase_tasks = []
        for t_title, base_hours, deliverable in tasks_pool[p_idx]:
            scaled_hours = round(base_hours * (1.0 if team_size <= 2 else 1.3) * (0.8 if level == "beginner" else (1.0 if level == "intermediate" else 1.25)))
            t_id = f"p{p_idx + 1}-t{task_counter}"
            phase_tasks.append({
                "id": t_id,
                "title": t_title,
                "estimated_hours": scaled_hours,
                "deliverable": deliverable,
            })
            task_counter += 1

        roadmap.append({
            "phase_number": p_idx + 1,
            "title": p_title,
            "duration": f"Weeks {current_week} – {end_week}",
            "weeks_count": p_weeks,
            "tasks": phase_tasks,
        })
        current_week = end_week + 1

    return roadmap


def _generate_physical_testing_plan(idea: Idea, level: str) -> list[dict[str, Any]]:
    """Generates structured physical verification and metrology test cases."""
    return [
        {
            "id": "TC-01",
            "category": "Metrology & Dimensions",
            "scenario": "Shaft journal diameter and bearing housing bore fit inspection",
            "test_input": "Precision external micrometer (0-25mm) and internal dial bore gauge calibrated to 20 deg C",
            "expected_output": "Shaft conforms to ISO 286 g6 (-0.007 to -0.016 mm); Housing conforms to H7 (+0.000 to +0.021 mm); zero loose wobble",
            "type": "Metrology & Fit Verification",
        },
        {
            "id": "TC-02",
            "category": "Structural Proof Load",
            "scenario": "Static loading under 1.5x maximum rated operating payload",
            "test_input": "Calibrated deadweights / hydraulic test jack applied at center-span load position",
            "expected_output": "Total deflection under dial indicator <= 0.45 mm; returns to absolute 0.00 mm upon load release (pure elastic regime; no yield)",
            "type": "Proof Load & Elastic Deflection Test",
        },
        {
            "id": "TC-03",
            "category": "FEA Stress Correlation",
            "scenario": "Stress concentration verification at critical mounting fillet under peak working load",
            "test_input": "Quarter-bridge strain gauge rosette bonded to peak FEA stress hotspot connected to DAQ",
            "expected_output": "Measured physical micro-strain matches ANSYS FEA predicted strain within 8% variance; calculated stress <= 50% yield",
            "type": "Experimental Stress Analysis",
        },
        {
            "id": "TC-04",
            "category": "Dynamics & Runout",
            "scenario": "Total indicator reading (TIR) shaft radial runout and dynamic balance at operating RPM",
            "test_input": "Magnetic base dial indicator touching ground shaft journal rotated manually and under motor spin",
            "expected_output": "Radial runout TIR <= 0.025 mm; smooth operation conforming to ISO 1940 Grade G2.5 dynamic balance threshold",
            "type": "Rotational Dynamics & Runout",
        },
        {
            "id": "TC-05",
            "category": "Joint Integrity (NDT)",
            "scenario": "Weld joint integrity inspection on chassis tubular frame joints",
            "test_input": "Solvent-removable dye penetrant (PT) test kit with cleaner, red penetrant dye, and white developer spray",
            "expected_output": "Zero linear cracks, zero porosity bleeds, and full throat thickness penetration along all structural welds",
            "type": "Non-Destructive Testing (NDT)",
        },
        {
            "id": "TC-06",
            "category": "Endurance & Thermal",
            "scenario": "Continuous 2-hour uninterrupted duty cycle under full design load",
            "test_input": "Continuous motor running with ambient temperature monitoring using infrared thermometer",
            "expected_output": "Bearing housing temperature <= 60 deg C; motor temperature <= 75 deg C; zero fastener loosening or mechanical binding",
            "type": "Thermal & Continuous Duty Endurance",
        },
    ]


def _generate_physical_viva_qa(idea: Idea, level: str) -> list[dict[str, str]]:
    """Assembles curated viva voce defense questions for physical & mechanical engineering."""
    curated = []
    # 1. Idea-specific questions
    for q, a in idea.get("viva", []):
        curated.append({"category": "Domain Specific", "question": q, "answer": a})

    # 2. Core physical engineering questions
    physical_bank = [
        ("Why did you select the von Mises yield criterion rather than Tresca for your FEA stress analysis?",
         "von Mises (Maximum Distortion Energy Theory) is the standard and most accurate failure criterion for ductile metals (like Al 6061-T6 and mild steel) under multi-axial stress states. Tresca is slightly more conservative, but von Mises correlates most reliably with experimental plastic yielding in isotropic alloys."),
        ("Explain how you determined the Factor of Safety (FOS) of 2.5 in your design.",
         "Factor of Safety accounts for uncertainties in raw material tensile consistency, dynamic shock loads during operation, and manufacturing tolerances. For capstone mechanisms with human proximity, standard engineering practice (e.g. Shigley's Mechanical Engineering Design) recommends an FOS between 2.0 and 3.0 relative to yield strength (sigma_y)."),
        ("How did you calculate the motor torque and reduction ratio required for the drive mechanism?",
         "Total torque required at the drive shaft includes static breakaway friction torque plus acceleration torque: T_total = T_friction + (J_total * alpha). We determined total inertia J_total reflected to the motor shaft divided by the gear ratio squared (i^2). A 4:1 reduction allowed our chosen motor to operate within its peak efficiency speed band."),
        ("Why did you choose an ISO 286 H7/g6 tolerance fit for the precision shaft and bearing housing?",
         "H7 provides a reamed hole with a tight upper tolerance (+0.021 mm on 20 mm bore) and zero negative tolerance. A g6 shaft ensures a precision clearance slide fit (-0.007 to -0.016 mm), allowing smooth assembly and axial thermal expansion without radial looseness or bearing chatter."),
        ("How did you mitigate stress concentrations (notch effect) at diameter transitions on your shafts?",
         "Abrupt sharp steps cause high theoretical stress concentration factors (Kt > 2.5). We specified generous transition fillet radii (r/d >= 0.15) with precision grinding and polished surface finish (Ra <= 0.8 um), reducing Kt to < 1.4 and significantly increasing cyclic fatigue endurance limit."),
        ("What trade-offs led to selecting Aluminium 6061-T6 over Mild Steel AISI 1018?",
         "Aluminium 6061-T6 has roughly one-third the density of steel (2.7 g/cm3 vs 7.85 g/cm3) while delivering a yield strength of 276 MPa, giving it a much higher specific strength (sigma_y / rho). This reduces moving mass and motor power requirements, while mild steel was reserved for high-impact structural mounts and pins."),
    ]
    for q, a in physical_bank:
        curated.append({"category": "Mechanical & Structural Defense", "question": q, "answer": a})
    return curated


def generate_blueprint(idea_key: str, level: str, profile: dict[str, Any]) -> dict[str, Any]:
    """Branch-Adaptive blueprint compiler.

    Detects branch specialization (Physical & Fabrication-First for core branches
    such as Mechanical, Automobile, Production, Aerospace, and Civil; Software/AI
    for Computer and Emerging technologies) and compiles deep, authentic engineering blueprints.
    """
    idea = IDEA_INDEX.get(idea_key)
    if not idea:
        raise ValueError(f"Unknown idea key: {idea_key}")

    tier_title, tier_summary, tier_features = idea["tiers"][level]
    student_branch = profile.get("branch", "")
    is_physical = is_physical_branch(student_branch) or idea.get("type") in ("physical", "mechanical")
    is_mechatronic = is_electromechanical_branch(student_branch) or "robotics" in idea.get("domains", []) or idea.get("type") in ("hybrid", "hardware")

    # Compute hardware BOM if present
    hardware_bom = []
    if idea.get("hardware"):
        for item, price, min_lvl in idea["hardware"]:
            included = True
            if min_lvl == "advanced" and level in ("beginner", "intermediate"):
                included = False
            elif min_lvl == "intermediate" and level == "beginner":
                included = False
            hardware_bom.append({
                "component": item,
                "approx_price_inr": price,
                "required_level": min_lvl,
                "included_in_this_tier": included,
            })

    blueprint: dict[str, Any] = {
        "idea_key": idea["key"],
        "title": idea["title"],
        "tagline": idea["tagline"],
        "level": level,
        "level_label": LEVEL_LABELS[level],
        "tier_title": tier_title,
        "tier_summary": tier_summary,
        "tier_features": tier_features,
        "domains": [{"value": d, "label": AI_DOMAINS.get(d, d)} for d in idea["domains"]],
        "type": idea["type"],
        "difficulty": idea["difficulty"],
        "target_users": idea["users"],
        "estimated_cost_inr": idea["cost"][level],
        "is_physical_engineering": is_physical,
        "discipline_type": "physical" if is_physical else "software",
    }

    # 1. Problem Statement
    if is_physical:
        blueprint["problem_statement"] = {
            "background": f"In core engineering capstones, addressing physical design, kinematic synthesis, and structural integrity for {idea['title'].lower()} is critical across manufacturing and mobility sectors.",
            "core_problem": idea["problem"],
            "target_beneficiaries": idea["users"],
            "objectives": idea["objectives"],
            "success_metrics": [
                "Achieve Factor of Safety (FOS) >= 2.4 under peak operational dynamic load in ANSYS FEA",
                "Ensure dimensional accuracy strictly conforming to ISO 286 tolerance limits (H7/g6)",
                "Verify structural elastic deflection under dial indicator <= 0.50 mm with zero permanent plastic yield",
                "Deliver a fully functioning physical prototype validated through standardized experimental proof load tests",
            ],
        }
    else:
        blueprint["problem_statement"] = {
            "background": f"In recent years, the challenge of addressing {idea['title'].lower()} has become increasingly vital across the {', '.join(APPLICATION_AREAS.get(i, i) for i in idea.get('interests', ['industry']))} sectors.",
            "core_problem": idea["problem"],
            "target_beneficiaries": idea["users"],
            "objectives": idea["objectives"],
            "success_metrics": [
                "Achieve classification / prediction accuracy exceeding the defined baseline (≥ 90%)",
                "Keep client-to-server end-to-end latency below 800 milliseconds",
                "Deliver a responsive, zero-error user experience across web and mobile viewports",
                "Ensure complete data persistence, role safety, and defensible auditability",
            ],
        }

    # Branch-Adaptive Core Sections
    if is_physical:
        # Physical & Fabrication-First Engineering Blueprint
        blueprint["cad_modeling"] = _build_cad_modeling_section(idea, level)
        blueprint["fea_cfd_simulation"] = _build_fea_cfd_section(idea, level)
        blueprint["material_selection"] = _build_material_selection_section(idea, level)
        blueprint["fabrication_plan"] = _build_fabrication_plan_section(idea, level)
        blueprint["mechanical_bom"] = _build_mechanical_bom_section(idea, level)
        blueprint["gdt_and_tolerances"] = _build_gdt_tolerances_section(idea, level)
        blueprint["embedded_sensors"] = _build_embedded_sensors_section(idea, level, is_mechatronic)
        blueprint["technologies"] = _generate_physical_technologies_grid(idea, level, is_mechatronic)
        blueprint["modules"] = _generate_physical_modules(idea, level, is_mechatronic)
        blueprint["hardware_bom"] = hardware_bom if hardware_bom else blueprint["mechanical_bom"]
        blueprint["roadmap"] = _generate_physical_roadmap(profile.get("months", 4), profile.get("team_size", 2), level)
        blueprint["testing"] = {
            "strategy": "Physical & Structural Quality Assurance: Metrology Verification -> Static Proof Load Deflection -> Strain FEA Correlation -> Dynamic Runout & Vibration -> Weld PT NDT -> Thermal Endurance",
            "test_cases": _generate_physical_testing_plan(idea, level),
            "coverage_target_pct": 95,
        }
        blueprint["viva_questions"] = _generate_physical_viva_qa(idea, level)
        blueprint["architecture"] = {
            "pattern": "Kinematic Power Transmission with Rigid Structural Spaceframe",
            "overview": (
                f"The physical engineering assembly is designed with a high torsional-stiffness structural frame, "
                f"converting motor prime mover torque into precise linear and angular displacement via hardened transmission elements. "
                f"Components are optimized using ANSYS FEA stress analysis to guarantee a minimum Factor of Safety >= 2.4 under peak dynamic load."
            ),
            "mermaid_diagram": _build_mermaid_physical_architecture(idea, level, is_mechatronic),
            "data_flow_steps": [
                "1. Motor prime mover generates rotational mechanical torque transferred via a zero-backlash flexible spider jaw coupler.",
                "2. Speed reduction stage multiplies torque and drives the precision ball screw / gear transmission.",
                "3. Motion conversion mechanism guides the working carriage smoothly along hardened linear guide rails.",
                "4. Structural foundation frame absorbs dynamic reaction forces and mitigates cyclic deflection.",
                "5. Sensors (load cell / optical encoder) provide closed-loop positional and force feedback to controller (if electromechanical).",
            ],
        }
        blueprint["database_design"] = {
            "engine": "Parametric Engineering Drawing Repository & Fastener CAD Library",
            "schema_strategy": "Standardized Part Numbering System with Revision Tracking (ISO 10209)",
            "mermaid_er_diagram": _build_mermaid_er(idea),
            "tables": [
                {
                    "name": table_name,
                    "description": comment,
                    "columns": [{"name": c[0], "type": c[1], "constraints": c[2] if len(c) > 2 else ""} for c in cols],
                }
                for table_name, comment, cols in idea.get("entities", [])
            ],
        }
        blueprint["git_workflow"] = {
            "model": "Hardware & CAD Version Control (GitHub / GrabCAD Workbench Flow)",
            "branching_rules": [
                "main: Approved production drawing sheets (.SLDDRW / .DWG / .PDF) and certified CAM toolpaths.",
                "design-review: Sub-assembly models undergoing FEA verification and tolerance stack-up checks.",
                "cad/<subassembly>: Feature branches for individual part modeling (e.g. cad/chassis-tubes, cad/spindle-shaft).",
                "cam/<machine-code>: CAM CNC toolpaths and G-code validation branches.",
            ],
            "commit_convention": "Conventional CAD/Engineering Commits (e.g., 'feat: add M6 threaded holes to motor mount', 'fix: increase fillet radius to 3mm for FEA stress reduction')",
            "pull_request_guidelines": [
                "Each PR must include CAD step files, 2D PDF drawing sheets, and interference check logs.",
                "At least 1 teammate engineering review sign-off is required before merging.",
                "FEA stress and Factor of Safety verification must pass without yield.",
            ],
        }
        blueprint["documentation"] = {
            "report_format": "AICTE & IEEE Standard Mechanical/Physical Final Year Project Report Format",
            "chapters": [
                {"number": 1, "title": "Introduction & Physical Project Objectives", "contents": "Background, Industrial Need, Problem Definition, Scope, Organization of the Thesis"},
                {"number": 2, "title": "Literature Survey of Mechanical Mechanisms", "contents": "Survey of existing mechanical mechanisms, patents, research gap, comparative matrix"},
                {"number": 3, "title": "Design Requirements & Kinematic Synthesis", "contents": "Degrees of freedom (Gruebler criterion), linkage synthesis, motor torque sizing calculations"},
                {"number": 4, "title": "3D CAD Modeling & Dynamic Assembly Mating", "contents": "SolidWorks / CATIA 3D solid model, assembly mates, interference detection, bill of materials"},
                {"number": 5, "title": "Finite Element Analysis (FEA) & CFD Simulation", "contents": "ANSYS static structural mesh convergence, von Mises stress contours, Factor of Safety >= 2.5, modal vibration analysis"},
                {"number": 6, "title": "Material Selection & Workshop Fabrication", "contents": "Ashby material selection trade-offs, CNC milling, lathe turning, TIG welding, 3D printing"},
                {"number": 7, "title": "GD&T Tolerances, Metrology & Physical Testing", "contents": "ISO 286 tolerance fits (H7/g6), dial indicator deflection measurements, proof load testing, dye penetrant NDT"},
                {"number": 8, "title": "Cost Estimation, Conclusion & Defense", "contents": "Complete mechanical bill of materials with Indian pricing (INR), future scope, viva defense preparation"},
            ],
            "srs_outline": "Design Requirements Specification (DRS / ISO 128 Compliant)",
            "readme_template": (
                f"# {tier_title}\n\n"
                f"> {tier_summary}\n\n"
                f"## CAD & Fabrication Quick Start\n"
                f"```bash\n"
                f"# Clone CAD repository & drawings\n"
                f"git clone https://github.com/your-team/{idea['key']}.git\n"
                f"cd {idea['key']}\n\n"
                f"# CAD Assembly: Open assemblies/main_assembly.SLDASM in SolidWorks 2024\n"
                f"# FEA Simulation: Open ansys/structural_static.wbpj in ANSYS Workbench\n"
                f"# Drawings: Production-ready drawing sheets available in docs/drawings_A3.pdf\n"
                f"```\n"
            ),
        }
    else:
        # Software & AI Engineering Blueprint
        blueprint["architecture"] = {
            "pattern": "Layered Service-Oriented Monolith with Asynchronous AI Execution",
            "overview": (
                f"The system is designed with a strict separation between presentation, application logic, "
                f"AI intelligence, and data persistence. Client interactions trigger REST requests through FastAPI, "
                f"which routes them through authentication and sanitization layers before passing feature tensors "
                f"to the dedicated {idea.get('model', 'AI')} model engine."
            ),
            "mermaid_diagram": _build_mermaid_architecture(idea, level),
            "data_flow_steps": [
                "1. User or IoT edge device captures raw data (media, text, or sensor readings) and transmits it over HTTPS/MQTT.",
                "2. API Gateway validates request schema, authenticates user JWT token, and checks rate limits.",
                "3. Preprocessing service extracts clean numerical features and normalizes dimensions.",
                "4. Inference engine executes the pre-loaded neural network model and generates predictions with confidence scores.",
                "5. Post-processing maps raw outputs to domain recommendations, logs transaction into database, and returns JSON response.",
            ],
        }
        blueprint["technologies"] = _generate_technologies_grid(idea, level)
        blueprint["hardware_bom"] = hardware_bom
        blueprint["modules"] = _generate_modules(idea, level)
        blueprint["database_design"] = {
            "engine": "PostgreSQL (Production) / SQLite (Development)",
            "schema_strategy": "Normalized Relational 3NF with JSON fields for unstructured AI metadata",
            "mermaid_er_diagram": _build_mermaid_er(idea),
            "tables": [
                {
                    "name": table_name,
                    "description": comment,
                    "columns": [{"name": c[0], "type": c[1], "constraints": c[2] if len(c) > 2 else ""} for c in cols],
                }
                for table_name, comment, cols in idea.get("entities", [])
            ],
        }
        blueprint["roadmap"] = _generate_roadmap(profile.get("months", 4), profile.get("team_size", 2), level)
        blueprint["git_workflow"] = {
            "model": "GitHub Flow (Feature Branch Workflow)",
            "branching_rules": [
                "main: Always production-ready, protected branch, requires pull-request approval and passing tests to merge.",
                "dev: Integration staging branch where all feature branches converge.",
                "feature/<module-name>: Individual contributor branches (e.g. feature/auth-jwt, feature/yolo-inference).",
                "fix/<issue-number>: Hotfixes for addressing specific bugs.",
            ],
            "commit_convention": "Conventional Commits (e.g., 'feat: add leaf disease classification route', 'fix: resolve cors header in dev')",
            "pull_request_guidelines": [
                "Each PR must address one focused responsibility.",
                "PR description must detail changes, test results, and attach a screenshot/log.",
                "At least 1 teammate code-review approval is required before merging.",
                "Automated CI linting and pytest suite must pass with zero failures.",
            ],
        }
        blueprint["documentation"] = {
            "report_format": "IEEE Standard Final Year Project Report Format",
            "chapters": [
                {"number": 1, "title": "Introduction", "contents": "Background, Problem Definition, Purpose, Scope, Organization of the Report"},
                {"number": 2, "title": "Literature Survey", "contents": "Critical review of existing papers, comparative matrix of existing systems, research gap"},
                {"number": 3, "title": "System Requirement Analysis", "contents": "Functional requirements, non-functional requirements, hardware & software specifications"},
                {"number": 4, "title": "System Design & Architecture", "contents": "System architecture, DFDs (Level 0, 1, 2), UML diagrams (Use Case, Sequence, Class), Database ER diagram"},
                {"number": 5, "title": "Implementation & Algorithms", "contents": "Dataset preprocessing, AI/ML model architecture & training equations, Backend API implementation, Frontend components"},
                {"number": 6, "title": "Testing & Results Analysis", "contents": "Unit, Integration and System test cases, Model evaluation metrics, Confusion matrix, ROC curves, Comparison with baselines"},
                {"number": 7, "title": "Conclusion & Future Enhancements", "contents": "Summary of achievements, limitations of current work, future directions for scaling"},
                {"number": 8, "title": "References & Appendices", "contents": "IEEE bibliography, sample code listings, user manual screenshots"},
            ],
            "srs_outline": "Software Requirements Specification (IEEE 830 standard compliant)",
            "readme_template": (
                f"# {tier_title}\n\n"
                f"> {tier_summary}\n\n"
                f"## Quick Start\n"
                f"```bash\n"
                f"# Clone repository\n"
                f"git clone https://github.com/your-username/{idea['key']}.git\n"
                f"cd {idea['key']}\n\n"
                f"# Backend setup\n"
                f"cd backend\n"
                f"python -m venv .venv\n"
                f"source .venv/bin/activate  # or .\\.venv\\Scripts\\activate on Windows\n"
                f"pip install -r requirements.txt\n"
                f"uvicorn app.main:app --reload\n\n"
                f"# Frontend setup (in a new terminal)\n"
                f"cd ../frontend\n"
                f"npm install\n"
                f"npm run dev\n"
                f"```\n"
            ),
        }
        blueprint["testing"] = {
            "strategy": "Comprehensive Pyramid Testing: Unit tests → Integration tests → AI Evaluation → Security & Concurrency",
            "test_cases": _generate_testing_plan(idea, level),
            "coverage_target_pct": 80,
        }
        blueprint["viva_questions"] = _generate_viva_qa(idea, level)

    # Presentation Pitch Deck (common structure with domain-adaptive slides)
    blueprint["presentation"] = {
        "deck_outline": _generate_presentation_slides(idea, level),
        "presentation_tips": [
            "Open with a 30-second relatable real-world hook before showing any technical details.",
            "Always demonstrate the physical prototype or live system rather than relying only on slides.",
            "Be prepared to defend your choice of material, factor of safety, or core algorithm with quantitative numbers.",
            "Ensure every team member speaks about their dedicated engineering subsystem during evaluation.",
        ],
    }

    return blueprint
