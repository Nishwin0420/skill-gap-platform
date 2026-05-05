# Skill‑Gap Platform — Career Intelligence Suite

> AI‑powered platform that analyzes resumes, detects skill gaps, predicts employability scores, and generates personalized learning paths — trained on **610k+ real job postings**.

[![CI – Build & Lint](https://github.com/<YOUR_GITHUB_USERNAME>/skill-gap-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/<YOUR_GITHUB_USERNAME>/skill-gap-platform/actions/workflows/ci.yml)

---

## ✨ Features

| Module | Description |
|---|---|
| **Skill Analyzer** | NLP‑based skill extraction from resume (spaCy + HuggingFace) |
| **Skill Gap Detection** | Weighted gap analysis vs. job role requirements |
| **Employability Score** | ML models (Random Forest, XGBoost, KNN) → 0–100 score |
| **Learning Path** | DAG‑based optimal learning sequence (networkx) |
| **Market Trends** | Real‑time demand scores for 87+ skills |
| **Interview Prep** | Role‑specific question bank + curated preparation tips |
| **Explainable AI** | SHAP‑based feature importance + narrative XAI |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Node.js ≥ 20
- Python 3.11
- PostgreSQL (or SQLite for local dev — automatic fallback)

### 1. Clone & Install

```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/skill-gap-platform.git
cd skill-gap-platform

# Backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Frontend
cd frontend
npm install
```

### 2. Configure Environment

```bash
# Root level
cp .env.example .env
# Fill in DATABASE_URL, GROQ_API_KEY, CLERK keys etc.

# Frontend
cp frontend/.env.example frontend/.env
# Set REACT_APP_BACKEND_URL=http://localhost:8000
```

### 3. Run

```bash
# Terminal 1 — Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm start
```

Open **http://localhost:3000**

---

## 🌐 Production Deployment

### Frontend → Vercel
1. Import this repo on [vercel.com](https://vercel.com).
2. Set **Root Directory** = `frontend`.
3. Set env var `REACT_APP_BACKEND_URL` to your Railway backend URL.
4. Deploy.

### Backend → Railway
1. Create a new project on [railway.app](https://railway.app).
2. Import this repo; Railway auto‑detects `railway.json` + `nixpacks.toml`.
3. Add env vars: `DATABASE_URL`, `GROQ_API_KEY`, `CLERK_SECRET_KEY`, `ALLOWED_ORIGINS`.
4. Deploy — Railway gives you an `https://*.up.railway.app` URL.

See `.env.example` for the full list of required environment variables.

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Tailwind CSS, Framer Motion, Recharts, react‑icons |
| **Backend** | FastAPI, uvicorn, SQLAlchemy, pydantic |
| **NLP** | spaCy (en_core_web_sm), HuggingFace Transformers, sentence‑transformers |
| **ML** | scikit‑learn (RF, KNN), XGBoost, SHAP |
| **Graph** | networkx (DAG learning paths) |
| **Database** | PostgreSQL (Neon/Railway) — SQLite fallback for local dev |
| **Auth** | Clerk |
| **LLM** | Groq (Llama‑3 / Mixtral) |

---

## 📁 Project Structure

```
skill-gap-platform/
├── backend/
│   ├── api/              # FastAPI route handlers
│   ├── api_clients/      # External API integrations (Groq, Adzuna, GitHub)
│   ├── auth/             # Clerk JWT validation
│   ├── data/             # Skill ontology, O*NET datasets
│   ├── models/           # ML model definitions and scoring
│   ├── utils/            # Helper functions
│   ├── config.py         # Centralized configuration + CORS
│   └── main.py           # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── components/   # All React UI pages and panels
│   │   ├── config/       # API base URL config
│   │   └── utils/        # toTitleCase + other helpers
│   ├── vercel.json        # Vercel deployment config
│   └── package.json
├── .env.example           # Required environment variables template
├── requirements.txt       # Python dependencies
├── railway.json           # Railway deployment config
├── nixpacks.toml          # Railway build steps
├── Procfile               # Heroku‑style fallback start command
└── .github/workflows/ci.yml  # GitHub Actions CI
```

---

## 📄 License

MIT — See [LICENSE](LICENSE)
