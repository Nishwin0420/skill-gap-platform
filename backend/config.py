"""
Configuration module for the AI-Based Decision Intelligence System.
Centralizes all configuration, paths, and environment variables.
"""

import os
from pathlib import Path

# ================================
# BASE PATHS
# ================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "trained_models"
DATASETS_DIR = DATA_DIR / "datasets"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
DATASETS_DIR.mkdir(exist_ok=True)

# ================================
# DATABASE
# ================================
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR.parent / 'skillgap.db'}"

# ================================
# API CONFIGURATION
# ================================
API_TITLE = "AI Skill Gap & Employability Intelligence Platform"
API_DESCRIPTION = """
An AI-Based Decision Intelligence System that analyzes real-world job market data,
student skill profiles, and industry demand trends to identify skill gaps,
predict employability, and generate personalized learning paths.

## Core Modules
- **Job Market Intelligence Engine** — Real-time market trend analysis
- **Skill Profiling & Normalization** — NLP-based skill extraction (HuggingFace + spaCy)
- **Skill Gap Detection Engine** — Weighted gap analysis with priority ranking
- **Employability Score Prediction** — ML models (Random Forest, XGBoost, KNN)
- **Learning Path Generator** — DAG-based personalized learning sequences
- **Explainable AI (XAI)** — SHAP/LIME transparent recommendations
"""
API_VERSION = "2.0.0"

# ================================
# NLP CONFIGURATION
# ================================
SPACY_MODEL = "en_core_web_sm"
HUGGINGFACE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TFIDF_MAX_FEATURES = 5000

# ================================
# ML MODEL CONFIGURATION
# ================================
RANDOM_FOREST_PARAMS = {
    "n_estimators": 200,
    "max_depth": 15,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "random_state": 42
}

XGBOOST_PARAMS = {
    "n_estimators": 200,
    "max_depth": 8,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42
}

KNN_PARAMS = {
    "n_neighbors": 7,
    "weights": "distance",
    "metric": "euclidean"
}

# ================================
# EMPLOYABILITY THRESHOLDS
# ================================
READINESS_LEVELS = {
    "Highly Competitive": (80, 100),
    "Competitive": (60, 79),
    "Developing": (40, 59),
    "Not Ready": (0, 39)
}

# ================================
# SKILL CATEGORIES (O*NET aligned)
# ================================
SKILL_CATEGORIES = [
    "Programming Languages",
    "Web Development",
    "Data Science & Analytics",
    "Machine Learning & AI",
    "Cloud & DevOps",
    "Databases",
    "Mobile Development",
    "Cybersecurity",
    "Soft Skills",
    "Tools & Platforms"
]

# ================================
# CORS ORIGINS
# ================================
# In production: set ALLOWED_ORIGINS env var to your Vercel URL(s)
# e.g. ALLOWED_ORIGINS=https://skill-gap-platform.vercel.app
# All *.vercel.app preview URLs are always allowed automatically.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "")
if _raw_origins:
    CORS_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]
else:
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

# Always append Vercel preview wildcard origins
CORS_ORIGINS += [
    "https://*.vercel.app",
]

