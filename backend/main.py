"""
AI-Based Decision Intelligence System
========================================
Main FastAPI Application

An intelligent platform that analyzes real-world job market data,
student skill profiles, and industry demand trends to identify
skill gaps, predict employability, and generate personalized learning paths.

Technology Stack:
    - FastAPI (Backend Framework)
    - scikit-learn, XGBoost (ML Models)
    - spaCy, HuggingFace Transformers (NLP)
    - SHAP, LIME (Explainable AI)
    - networkx (Graph Algorithms)
    - SQLAlchemy (Database ORM)
    - BeautifulSoup4 (Web Scraping)

References:
    - Kumar et al. (2023) — Skill Gap Analysis: A Machine Learning Approach
    - Zhang & Liu (2024) — AI-Driven Career Recommendation Systems
    - Ahmed et al. (2023) — NLP for Skill Extraction from Job Descriptions
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env file (local dev only — production uses platform env vars)
try:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass  # python-dotenv not required in production

from backend.api.routes_analysis import router as analysis_router
from backend.api.routes_market import router as market_router
from backend.api.routes_dashboard import router as dashboard_router
from backend.api.routes_innovation import router as innovation_router
from backend.config import (
    API_TITLE, API_DESCRIPTION, API_VERSION, CORS_ORIGINS
)

# ====================================
# APP INITIALIZATION
# ====================================
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ====================================
# CORS MIDDLEWARE
# ====================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================
# INCLUDE ROUTERS
# ====================================
app.include_router(analysis_router)
app.include_router(market_router)
app.include_router(dashboard_router)
app.include_router(innovation_router)


# ====================================
# STARTUP EVENTS
# ====================================
@app.on_event("startup")
async def on_startup():
    """Run background tasks on server startup."""
    # Feature 4: Live skill taxonomy auto-update (background thread)
    try:
        from backend.api_clients.skill_taxonomy_updater import start_background_update
        start_background_update()
    except Exception as e:
        print(f"[Startup] Taxonomy updater skipped: {e}")

# ====================================
# ROOT ENDPOINT
# ====================================
@app.get("/")
def root():
    return {
        "message": "✅ AI Skill Gap & Employability Intelligence Platform is running",
        "version": API_VERSION,
        "endpoints": {
            "analysis": ["/api/analyze", "/api/analyze-full", "/api/extract-skills"],
            "market": ["/api/market-trends", "/api/market-summary", "/api/role-analysis"],
            "dashboard": ["/api/dashboard-stats", "/api/analysis-history", "/api/placement-stats"],
            "explainability": ["/api/xai/explain/{id}"],
            "ontology": ["/api/skill-ontology"],
            "learning": ["/api/generate-learning-path"],
            "innovation": [
                "/api/forecast/top-skills",
                "/api/forecast/emerging",
                "/api/ats-score",
                "/api/interview-prep",
                "/api/comparative-analysis",
                "/api/history"
            ]
        },
        "documentation": "/docs",
        "modules": [
            "Job Market Intelligence Engine",
            "Skill Profiling & Normalization (NLP)",
            "Skill Gap Detection Engine",
            "Employability Score Prediction (ML)",
            "Learning Path Generator (DAG)",
            "Explainable AI (XAI)"
        ]
    }


@app.get("/health")
def health():
    return {"status": "OK", "version": API_VERSION}