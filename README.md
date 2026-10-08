# Project Builder 🚀
### Autonomous Final-Year Engineering Project & MLOps Architecture Generator

> Transforms a student's goal, branch, skill level, budget, and constraints into a complete 3-tier engineering path (**Beginner → Intermediate → Advanced**) with exhaustive blueprints covering all 22 required engineering disciplines, live Mermaid diagrams, sprint roadmaps, IEEE report chapters, and viva defense preparation.

---

## 🌟 Key Features

1. **Intelligent Path Recommender (ML + Rule-Based Engine)**
   - Inputs: Engineering branch (CSE, IT, AIDS, ECE, EEE, Mech, Civil, BioMed), team skill level, hardware budget cap, software/hardware/hybrid preference, difficulty level, time available (1–12 months), team size (1–6), application domains, and free-text goal.
   - Evaluates match scores using TF-IDF text similarity and capacity load planning.
   - Generates progressive paths: **Beginner → Intermediate → Advanced** with effort estimation.

2. **Full Coverage of All 22 Engineering Dimensions**
   Every generated blueprint covers every required dimension:
   - **Backend** (FastAPI, async services, layered architecture)
   - **Frontend** (React + Vite, design systems, PWA)
   - **Database** (PostgreSQL/SQLite, 3NF schema, indexes)
   - **API & Integration** (RESTful OpenAPI 3, MQTT, WebSockets)
   - **Authentication & Authorization** (JWT, bcrypt, RBAC for Students/Mentors/Admins)
   - **AI / Machine Learning** (Feature engineering, baselines, SHAP/LIME explainability)
   - **Deep Learning** (PyTorch, transfer learning, mixed precision, ablations)
   - **Generative AI / LLM** (RAG, vector databases, LangChain, prompt guardrails)
   - **Computer Vision** (OpenCV, YOLOv8, MediaPipe, Grad-CAM heatmaps)
   - **NLP** (Transformers, BERT/IndicBERT, Tokenizers, NER)
   - **AI Model Training & Fine-tuning** (Colab GPU, Optuna tuning, LoRA/PEFT, DVC)
   - **AI Model Deployment & Inference** (ONNX Runtime, TFLite, latency budgets)
   - **Cloud & Deployment** (Docker, Cloud Run, AWS EC2/S3, Render)
   - **DevOps** (Docker Compose, GitHub Actions CI/CD)
   - **Web Security** (OWASP compliance, input sanitization, CORS, rate limits)
   - **Testing** (pytest, pyramid testing, test cases table, model edge-cases)
   - **Performance Optimization** (Redis caching, batching, DB indexes, p95 latency)
   - **Version Control (Git/GitHub)** (GitHub flow, branch rules, conventional commits)
   - **System Design & Architecture** (Interactive Mermaid diagram, data flow walkthrough)
   - **File & Cloud Storage** (Path-traversal safe storage, S3 compatibility)
   - **Third-Party Integrations** (Weather, Maps, SMS/WhatsApp, Translation)
   - **Monitoring & Maintenance** (Health endpoints, drift alerts, audit logs)
   - *Hardware BOM* (Bill of Materials with component pricing for IoT/hardware projects)

3. **Interactive Visualizations**
   - Live **Mermaid Architecture Diagram** with flow from client to model engine.
   - Live **Mermaid ER Diagram** with foreign-key entity relationships.

4. **Academic & Examination Readiness**
   - **IEEE Standard 8-Chapter Report Guide** (Abstract, Intro, Literature Review, System Analysis, System Design, Implementation, Testing & Results, Conclusion & Future Work).
   - **Ready-Made README.md Template**.
   - **12-Slide Final Presentation Deck Guide** with slide-by-slide speaker notes.
   - **Curated Viva Voce Defense Q&A** with model answers across domains and examiners' trap questions.

5. **Student & Faculty Workspace**
   - User Accounts (Student, Faculty Mentor, Administrator).
   - Saved Projects Dashboard with interactive sprint roadmap task checklist.
   - One-click export to **IEEE Markdown (.md)** and **Printable HTML / PDF**.
   - Faculty Mentor Review Portal: approve submissions, request changes, or leave viva warnings.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.12+ / FastAPI, SQLAlchemy 2.0, SQLite (or PostgreSQL), PyJWT, bcrypt, Pydantic 2.
- **Frontend:** React, Vite, Vanilla CSS design system (dark glassmorphism, Outfit & Inter typography), Mermaid.js, Lucide Icons.
- **Hybrid AI Engine:**
  - Built-in offline deterministic engine with 22 curated ideas and 66 project tiers.
  - Optional LLM integration (Gemini / OpenAI) via environment variables for personalized mentor advice and custom viva tips.

---

## ⚡ Quick Start

### 1. Run the Backend (FastAPI)
```bash
cd backend
# Create virtual environment (if not already created)
python -m venv .venv
.\.venv\Scripts\activate   # Windows (or: source .venv/bin/activate on Linux/Mac)

# Install dependencies
pip install -r requirements.txt

# Run FastAPI dev server
uvicorn app.main:app --reload --port 8000
```
- API is running at: `http://127.0.0.1:8000`
- Interactive Swagger docs: `http://127.0.0.1:8000/docs`

### 2. Run the Frontend (Vite + React)
```bash
cd ../frontend
npm install
npm run dev
```
- Frontend application is live at: `http://127.0.0.1:5173`

---

## 🔐 Default Demo Accounts

| Role | Email | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin@projectbuilder.dev` | `Admin@12345` |
| **Faculty Mentor** | `mentor@projectbuilder.dev` | `Mentor@12345` |
| **Student** | Any self-registered account, or create one in 5 seconds via the UI modal |

*(Quick one-click demo login buttons are also available in the Sign In modal!)*

---

## 🧪 Running Automated Tests
```bash
cd backend
.\.venv\Scripts\pytest -v
```
All 5 comprehensive test suites verify health, recommendation scoring, blueprint compilation across all 22 disciplines, and user authentication.
