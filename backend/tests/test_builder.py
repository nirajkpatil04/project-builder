"""Unit and integration tests for Project Builder backend."""
import uuid
import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.engine.catalog import options_payload
from app.engine.generator import generate_blueprint
from app.engine.recommender import suggest
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_builder_options():
    res = client.get("/api/builder/options")
    assert res.status_code == 200
    data = res.json()
    assert "branches" in data
    assert "skills" in data
    assert "budgets" in data
    assert "preferences" in data
    assert "difficulties" in data


def test_recommender_suggestions():
    profile = {
        "goal": "I want to build a leaf crop disease detection app using computer vision",
        "branch": "cse",
        "skill": "beginner",
        "budget": "zero",
        "preference": "software",
        "difficulty": "moderate",
        "months": 4,
        "team_size": 2,
        "interests": ["agriculture"],
    }
    results = suggest(profile, limit=3)
    assert len(results) >= 1
    top = results[0]
    assert "title" in top
    assert "score" in top
    assert len(top["path"]) == 3  # beginner, intermediate, advanced


def test_generate_blueprint():
    profile = {
        "goal": "Crop disease leaf recognition",
        "branch": "cse",
        "skill": "beginner",
        "budget": "zero",
        "preference": "software",
        "difficulty": "moderate",
        "months": 4,
        "team_size": 2,
        "interests": ["agriculture"],
    }
    bp = generate_blueprint("crop-disease-detection", "beginner", profile)
    assert bp["idea_key"] == "crop-disease-detection"
    assert "problem_statement" in bp
    assert "architecture" in bp
    assert "mermaid_diagram" in bp["architecture"]
    assert "graph TD" in bp["architecture"]["mermaid_diagram"]
    assert "technologies" in bp
    # Check all 22 engineering disciplines are present in the technologies output!
    assert "backend" in bp["technologies"]
    assert "frontend" in bp["technologies"]
    assert "database" in bp["technologies"]
    assert "api" in bp["technologies"]
    assert "auth" in bp["technologies"]
    assert "ai_ml" in bp["technologies"]
    assert "deep_learning" in bp["technologies"]
    assert "genai" in bp["technologies"]
    assert "cv" in bp["technologies"]
    assert "nlp" in bp["technologies"]
    assert "training" in bp["technologies"]
    assert "inference" in bp["technologies"]
    assert "cloud" in bp["technologies"]
    assert "devops" in bp["technologies"]
    assert "security" in bp["technologies"]
    assert "testing" in bp["technologies"]
    assert "performance" in bp["technologies"]
    assert "git" in bp["technologies"]
    assert "system_design" in bp["technologies"]
    assert "storage" in bp["technologies"]
    assert "third_party" in bp["technologies"]
    assert "monitoring" in bp["technologies"]
    # Check modules, db design, roadmap, git workflow, testing, viva
    assert len(bp["modules"]) >= 5
    assert "mermaid_er_diagram" in bp["database_design"]
    assert len(bp["roadmap"]) >= 3
    assert "git_workflow" in bp
    assert "documentation" in bp
    assert "testing" in bp
    assert "presentation" in bp
    assert len(bp["viva_questions"]) >= 5


def test_auth_and_project_lifecycle():
    # 1. Register student
    reg_payload = {
        "email": "teststudent@college.edu",
        "full_name": "Rohan Sharma",
        "password": "Password123",
        "branch": "cse",
    }
    res = client.post("/api/auth/register", json=reg_payload)
    if res.status_code == 409:
        # already registered in previous run, login instead
        login_res = client.post(
            "/api/auth/login",
            json={"email": "teststudent@college.edu", "password": "Password123"},
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
    else:
        assert res.status_code == 201
        token = res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get profile
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "teststudent@college.edu"

    # 3. Request suggestions
    sug_res = client.post(
        "/api/builder/suggest",
        headers=headers,
        json={
            "profile": {
                "goal": "Face recognition attendance system for classroom",
                "branch": "cse",
                "skill": "beginner",
                "budget": "low",
                "preference": "software",
                "difficulty": "easy",
                "months": 3,
                "team_size": 2,
                "interests": ["education"],
            },
            "limit": 2,
        },
    )
    assert sug_res.status_code == 200
    suggestions = sug_res.json()["suggestions"]
    assert len(suggestions) > 0

    # 4. Generate blueprint
    gen_res = client.post(
        "/api/builder/generate",
        headers=headers,
        json={
            "profile": {
                "goal": "Face recognition attendance system",
                "branch": "cse",
                "skill": "beginner",
                "budget": "low",
                "preference": "software",
                "difficulty": "easy",
                "months": 3,
                "team_size": 2,
                "interests": ["education"],
            },
            "idea_key": suggestions[0]["key"],
            "level": "beginner",
            "use_llm": False,
        },
    )
    assert gen_res.status_code == 200
    blueprint = gen_res.json()["blueprint"]

    # 5. Save project
    save_res = client.post(
        "/api/projects",
        headers=headers,
        json={"blueprint": blueprint, "profile": gen_res.json()["profile"]},
    )
    assert save_res.status_code == 201
    project_id = save_res.json()["id"]

    # 6. Check list
    list_res = client.get("/api/projects", headers=headers)
    assert list_res.status_code == 200
    assert any(p["id"] == project_id for p in list_res.json())

    # 7. Check detail & export
    detail_res = client.get(f"/api/projects/{project_id}", headers=headers)
    assert detail_res.status_code == 200

    md_res = client.get(f"/api/projects/{project_id}/export/markdown", headers=headers)
    assert md_res.status_code == 200
    assert "Problem Statement" in md_res.text

    html_res = client.get(f"/api/projects/{project_id}/export/html", headers=headers)
    assert html_res.status_code == 200
    assert "<html" in html_res.text


def test_physical_engineering_blueprint():
    """REQUIREMENT 1: Physical & Fabrication-First Engineering for Mechanical and allied branches."""
    profile = {
        "goal": "Design, FEA stress optimization, and CNC fabrication of an automated gantry mechanism",
        "branch": "mech",
        "skill": "intermediate",
        "budget": "medium",
        "preference": "hardware",
        "difficulty": "challenging",
        "months": 6,
        "team_size": 3,
        "interests": ["manufacturing"],
    }
    bp = generate_blueprint("automated-sheet-metal-bending", "intermediate", profile)

    # 1. Branch adaptive flag
    assert bp["is_physical_engineering"] is True
    assert bp["discipline_type"] == "physical"

    # 2. CAD 3D Modeling & Kinematics
    assert "cad_modeling" in bp
    assert "SolidWorks" in bp["cad_modeling"]["primary_cad_tool"]
    assert len(bp["cad_modeling"]["assemblies"]) >= 2
    assert "kinematic_analysis" in bp["cad_modeling"]

    # 3. FEA & CFD Stress Analysis
    assert "fea_cfd_simulation" in bp
    stress = bp["fea_cfd_simulation"]["stress_results"]
    assert stress["calculated_factor_of_safety"] >= 2.0
    assert stress["max_von_mises_stress_mpa"] > 0
    assert "modal_frequency_analysis" in bp["fea_cfd_simulation"]

    # 4. Material Selection with Indian Pricing
    assert "material_selection" in bp
    mats = bp["material_selection"]["selected_materials"]
    assert len(mats) >= 2
    assert any("Aluminium" in m["material_name"] for m in mats)
    assert any(m["approx_cost_inr_per_kg"] > 0 for m in mats)

    # 5. Workshop Fabrication & Manufacturing Plan
    assert "fabrication_plan" in bp
    ops = bp["fabrication_plan"]["manufacturing_processes"]
    assert len(ops) >= 4
    assert any("Turning" in o["operation"] or "Milling" in o["operation"] for o in ops)
    assert len(bp["fabrication_plan"]["workshop_safety"]) >= 2

    # 6. Mechanical BOM with Indian market pricing
    assert "mechanical_bom" in bp
    bom = bp["mechanical_bom"]
    assert len(bom) >= 5
    for item in bom:
        assert item["approx_price_inr"] > 0
        assert "indian_source" in item

    # 7. GD&T and Tolerances
    assert "gdt_and_tolerances" in bp
    assert len(bp["gdt_and_tolerances"]["tolerance_fits"]) >= 2
    assert len(bp["gdt_and_tolerances"]["physical_testing_standards"]) >= 2

    # 8. Testing Plan is Physical Quality Assurance
    assert "Physical" in bp["testing"]["strategy"]
    assert any("Metrology" in tc["category"] or "Static Load" in tc["category"] for tc in bp["testing"]["test_cases"])

    # 9. Verify Exporter handles physical blueprints
    from app.services.exporter import export_markdown, export_printable_html
    md_out = export_markdown("Automated Gantry", bp)
    assert "CAD 3D Modeling" in md_out
    assert "FEA & CFD Simulation" in md_out
    assert "Mechanical Bill of Materials" in md_out
    assert "GD&T, Tolerances" in md_out

    html_out = export_printable_html("Automated Gantry", bp)
    assert "CAD 3D Modeling" in html_out
    assert "FEA &amp; CFD Stress Analysis" in html_out or "FEA & CFD" in html_out


def test_indian_branch_catalog_38_branches():
    """REQUIREMENT 2: Comprehensive Catalog of 38 Indian Engineering Branches grouped by AICTE categories."""
    res = client.get("/api/builder/options")
    assert res.status_code == 200
    data = res.json()

    # Flat catalog of 38 branches
    assert len(data["branches"]) == 38

    # 5 AICTE Categories
    categories = data["branch_categories"]
    assert len(categories) == 5
    cat_names = {c["category"] for c in categories}
    assert "Mechanical & Manufacturing" in cat_names
    assert "Computer & Emerging Technologies" in cat_names
    assert "Electrical & Electronics" in cat_names
    assert "Civil & Infrastructure" in cat_names
    assert "Chemical, Bio & Allied" in cat_names

    # Check key branches exist
    flat_keys = {b["value"] for b in data["branches"]}
    for expected in ["mech", "auto", "aero", "aeronautical", "mechatronics", "prod_ind", "cse", "aids", "aiml", "ece", "eee", "civil", "chem", "biotech"]:
        assert expected in flat_keys


def test_admin_only_docs_protection():
    """REQUIREMENT 3: API Documentation (/docs, /redoc, /openapi.json) locked down to Admin only."""
    # 1. Unauthenticated access -> 403 Forbidden
    res_docs = client.get("/docs")
    assert res_docs.status_code == 403

    res_redoc = client.get("/redoc")
    assert res_redoc.status_code == 403

    res_openapi = client.get("/openapi.json")
    assert res_openapi.status_code == 403

    # 2. Student access -> 403 Forbidden
    student_login = client.post(
        "/api/auth/login",
        json={"email": "teststudent@college.edu", "password": "Password123"},
    )
    assert student_login.status_code == 200
    student_token = student_login.json()["access_token"]

    student_docs = client.get(f"/docs?token={student_token}")
    assert student_docs.status_code == 403

    # 3. Platform Admin access -> 200 OK
    admin_login = client.post(
        "/api/auth/login",
        json={"email": "admin@projectbuilder.dev", "password": "Admin@12345"},
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    assert admin_login.json()["user"]["role"] == "admin"

    admin_docs = client.get(f"/docs?token={admin_token}")
    assert admin_docs.status_code == 200
    assert "swagger-ui" in admin_docs.text

    admin_openapi = client.get(f"/openapi.json?token={admin_token}")
    assert admin_openapi.status_code == 200
    assert "openapi" in admin_openapi.json()


def test_google_sso_and_multistep_onboarding():
    """REQUIREMENT 4 & 5: Google SSO (Step 1) and Profile Setup Onboarding (Step 2)."""
    test_email = f"sso.student.{uuid.uuid4().hex[:6]}@engineering.edu"
    google_res = client.post(
        "/api/auth/google",
        json={"email": test_email, "name": "Aditya Patil"},
    )
    assert google_res.status_code == 200
    data = google_res.json()
    assert data["user"]["has_completed_onboarding"] is False
    assert data["user"]["role"] == "student"

    sso_token = data["access_token"]
    headers = {"Authorization": f"Bearer {sso_token}"}

    # 2. Step 2 Onboarding completion
    onboard_res = client.post(
        "/api/auth/onboarding",
        headers=headers,
        json={
            "first_name": "Aditya",
            "last_name": "Patil",
            "branch": "mech",
            "college": "COEP Technological University, Pune",
            "semester": "Final Year (8th Sem)",
        },
    )
    assert onboard_res.status_code == 200
    onboarded_user = onboard_res.json()["user"]
    assert onboarded_user["has_completed_onboarding"] is True
    assert onboarded_user["branch"] == "mech"
    assert onboarded_user["college"] == "COEP Technological University, Pune"
    assert onboarded_user["full_name"] == "Aditya Patil"

