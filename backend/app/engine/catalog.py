"""Option catalogues exposed to the frontend wizard."""
from __future__ import annotations

# Comprehensive official Indian Engineering Branch Catalog (AICTE & State Technical Universities)
BRANCH_CATEGORIES: dict[str, dict[str, str]] = {
    "Mechanical & Manufacturing": {
        "mech": "Mechanical Engineering",
        "auto": "Automobile Engineering",
        "aero": "Aerospace Engineering",
        "aeronautical": "Aeronautical Engineering",
        "mechatronics": "Mechatronics Engineering",
        "prod_ind": "Production & Industrial Engineering",
        "mfg": "Manufacturing Engineering",
        "marine": "Marine Engineering",
        "mining": "Mining Engineering",
        "metallurgy": "Metallurgy & Materials Engineering",
    },
    "Computer & Emerging Technologies": {
        "cse": "Computer Science & Engineering (CSE)",
        "it": "Information Technology (IT)",
        "aids": "Artificial Intelligence & Data Science (AI & DS)",
        "aiml": "Artificial Intelligence & Machine Learning (AI & ML)",
        "cyber": "Cyber Security",
        "iot": "Internet of Things (IoT)",
        "swe": "Software Engineering",
        "cloud": "Cloud Computing",
    },
    "Electrical & Electronics": {
        "ece": "Electronics & Communication (ECE)",
        "eee": "Electrical & Electronics (EEE)",
        "eie": "Electronics & Instrumentation (EIE)",
        "vlsi": "VLSI Design",
        "robotics_auto": "Robotics & Automation",
        "telecom": "Telecommunication Engineering",
    },
    "Civil & Infrastructure": {
        "civil": "Civil Engineering",
        "environmental": "Environmental Engineering",
        "construction_tech": "Construction Technology",
        "structural": "Structural Engineering",
        "transportation": "Transportation Engineering",
        "geoinformatics": "Geo-informatics",
    },
    "Chemical, Bio & Allied": {
        "chem": "Chemical Engineering",
        "biotech": "Biotechnology",
        "biomed": "Biomedical Engineering",
        "petroleum": "Petroleum Engineering",
        "petrochem": "Petrochemical Engineering",
        "food_tech": "Food Technology",
        "agri_eng": "Agricultural Engineering",
        "textile": "Textile Engineering",
    },
}

# Flat lookup dictionary for all 38 branches
BRANCHES: dict[str, str] = {
    code: name
    for category in BRANCH_CATEGORIES.values()
    for code, name in category.items()
}

# Physical & Fabrication-Heavy disciplines that prioritize CAD, FEA, Materials & Manufacturing
PHYSICAL_ENGINEERING_BRANCHES = {
    # Mechanical & Manufacturing
    "mech", "auto", "aero", "aeronautical", "mechatronics",
    "prod_ind", "mfg", "marine", "mining", "metallurgy",
    # Civil & Infrastructure
    "civil", "construction_tech", "structural", "transportation", "environmental", "geoinformatics",
    # Physical/Chemical allied
    "petroleum", "petrochem", "textile", "agri_eng",
}

# Electromechanical / Mechatronics branches where embedded systems/sensors are native
ELECTROMECHANICAL_BRANCHES = {
    "mechatronics", "robotics_auto", "auto", "aero", "aeronautical", "mech", "eie", "iot", "biomed",
}


def is_physical_branch(branch: str | None) -> bool:
    """Returns True if the branch is a physical, fabrication, or hardware-first engineering discipline."""
    if not branch:
        return False
    b = branch.lower()
    return b in PHYSICAL_ENGINEERING_BRANCHES


def is_electromechanical_branch(branch: str | None) -> bool:
    """Returns True if the branch integrates mechanical hardware with embedded sensors/controllers."""
    if not branch:
        return False
    b = branch.lower()
    return b in ELECTROMECHANICAL_BRANCHES


def get_branch_category(branch: str | None) -> str:
    """Returns the top-level AICTE category name for a given branch code."""
    if not branch:
        return "Computer & Emerging Technologies"
    b = branch.lower()
    for cat_name, cat_branches in BRANCH_CATEGORIES.items():
        if b in cat_branches:
            return cat_name
    return "Computer & Emerging Technologies"

SKILLS = {
    "beginner": "Beginner: Basic programming background",
    "intermediate": "Intermediate: Experience with apps and basic ML models",
    "advanced": "Advanced: Comfortable with full-stack and deep learning",
}

BUDGETS = {
    "zero": "Under ₹500 (Software only)",
    "low": "₹500 to ₹3,000",
    "medium": "₹3,000 to ₹12,000",
    "high": "₹12,000+",
}
BUDGET_CAP = {"zero": 500, "low": 3000, "medium": 12000, "high": 10**9}

PREFERENCES = {
    "software": "Software only",
    "hardware": "Hardware / IoT focused",
    "hybrid": "Hybrid (software + hardware)",
}

DIFFICULTIES = {
    "easy": "Easy: Safe and feasible to complete",
    "moderate": "Moderate: Balanced engineering challenge",
    "challenging": "Challenging: Competitive capstone project",
}

LEVEL_LABELS = {"beginner": "Beginner", "intermediate": "Intermediate", "advanced": "Advanced"}

APPLICATION_AREAS = {
    "healthcare": "Healthcare",
    "agriculture": "Agriculture",
    "education": "Education",
    "finance": "Finance & FinTech",
    "smart-city": "Smart City",
    "environment": "Environment",
    "transport": "Transport & Safety",
    "accessibility": "Accessibility",
    "retail": "Retail",
    "manufacturing": "Manufacturing",
    "energy": "Energy",
    "security": "Security",
    "careers": "Careers & Jobs",
}

AI_DOMAINS = {
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "cv": "Computer Vision",
    "nlp": "NLP",
    "genai": "Generative AI / LLM",
    "iot": "IoT & Embedded",
    "data": "Data Engineering & Analytics",
    "robotics": "Robotics",
}


def options_payload() -> dict:
    def as_list(d: dict) -> list[dict]:
        return [{"value": k, "label": v} for k, v in d.items()]

    categories_list = [
        {
            "category": cat_name,
            "branches": [{"value": k, "label": v} for k, v in cat_dict.items()],
        }
        for cat_name, cat_dict in BRANCH_CATEGORIES.items()
    ]

    return {
        "branches": as_list(BRANCHES),
        "branch_categories": categories_list,
        "skills": as_list(SKILLS),
        "budgets": as_list(BUDGETS),
        "preferences": as_list(PREFERENCES),
        "difficulties": as_list(DIFFICULTIES),
        "application_areas": as_list(APPLICATION_AREAS),
        "ai_domains": as_list(AI_DOMAINS),
        "months": [1, 2, 3, 4, 5, 6, 8, 10, 12],
        "team_sizes": [1, 2, 3, 4, 5, 6],
    }
