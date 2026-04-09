"""
Innovation API Routes
======================
Endpoints for innovative features:
- Skill Demand Forecasting (ARIMA-style)
- Resume ATS Scoring
- Interview Preparation
- Comparative Analytics
- Analysis History (multi-user)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from backend.models.skill_forecaster import get_forecaster
from backend.models.ats_scorer import get_ats_scorer
from backend.models.interview_prep import get_interview_prep
from backend.models.skill_gap_engine import get_gap_engine
from backend.models.employability_predictor import get_predictor
from backend.nlp.skill_normalizer import get_normalizer
from backend.database.db_setup import SessionLocal
from backend.database.crud import get_all_analyses

router = APIRouter(prefix="/api", tags=["Innovation"])


# ====================================
# REQUEST MODELS
# ====================================
class ATSScoreRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    job_skills: List[str] = []


class InterviewPrepRequest(BaseModel):
    user_skills: List[str]
    job_skills: List[str]
    target_role: Optional[str] = None


class ComparativeRequest(BaseModel):
    user_skills: List[str]
    experience: float = 0
    target_role: Optional[str] = None


class ForecastRequest(BaseModel):
    skill: str
    months_ahead: int = Field(default=6, ge=1, le=12)


# ====================================
# SKILL DEMAND FORECASTING
# ====================================
@router.get("/forecast/top-skills")
def forecast_top_skills():
    """
    Get demand forecast for top skills over the next 6 months.
    Uses linear trend extrapolation from job market data.
    """
    forecaster = get_forecaster()
    forecasts = forecaster.forecast_all_top_skills(top_n=10, months_ahead=6)
    return {
        "forecasts": forecasts,
        "method": "Linear Trend Extrapolation",
        "period": "6 months"
    }


@router.post("/forecast/skill")
def forecast_specific_skill(data: ForecastRequest):
    """Forecast demand for a specific skill."""
    forecaster = get_forecaster()
    result = forecaster.forecast_skill_demand(data.skill, data.months_ahead)
    if not result:
        return {"skill": data.skill, "forecast": [], "message": "Insufficient data"}
    return result


@router.get("/forecast/emerging")
def get_emerging_skills():
    """Identify skills with the fastest growth — emerging skills to watch."""
    forecaster = get_forecaster()
    emerging = forecaster.get_emerging_skills(top_n=10)
    declining = forecaster.get_declining_skills(top_n=5)
    return {
        "emerging_skills": emerging,
        "declining_skills": declining,
        "analysis_date": datetime.utcnow().isoformat()
    }


# ====================================
# RESUME ATS SCORING
# ====================================
@router.post("/ats-score")
def score_resume_ats(data: ATSScoreRequest):
    """
    Score a resume for ATS (Applicant Tracking System) compatibility.
    Returns score, grade, breakdown, and improvement suggestions.
    """
    scorer = get_ats_scorer()
    result = scorer.score_resume(data.resume_text, data.job_skills)
    return result


# ====================================
# INTERVIEW PREPARATION
# ====================================
@router.post("/interview-prep")
def generate_interview_prep(data: InterviewPrepRequest):
    """
    Generate personalized interview preparation materials.
    Returns role-specific questions, tips, and study plan.
    """
    prep_gen = get_interview_prep()
    result = prep_gen.generate_prep(
        data.user_skills, data.job_skills, data.target_role
    )
    return result


# ====================================
# COMPARATIVE ANALYTICS
# ====================================
@router.post("/comparative-analysis")
def comparative_analysis(data: ComparativeRequest):
    """
    Compare user profile against role benchmarks.
    Shows how they stack up against typical candidates.
    """
    normalizer = get_normalizer()
    gap_engine = get_gap_engine()
    predictor = get_predictor()

    # Role benchmarks
    role_benchmarks = {
        "Machine Learning Engineer": {
            "required_skills": ["python", "machine learning", "deep learning", "tensorflow", "sql", "docker", "git"],
            "avg_experience": 3.0,
            "avg_score": 65,
        },
        "Full Stack Developer": {
            "required_skills": ["javascript", "react", "node.js", "python", "sql", "docker", "git", "html", "css"],
            "avg_experience": 2.5,
            "avg_score": 60,
        },
        "Data Scientist": {
            "required_skills": ["python", "machine learning", "sql", "data analysis", "statistics", "pandas", "deep learning"],
            "avg_experience": 2.5,
            "avg_score": 62,
        },
        "DevOps Engineer": {
            "required_skills": ["docker", "kubernetes", "aws", "linux", "git", "python", "jenkins", "terraform"],
            "avg_experience": 3.0,
            "avg_score": 58,
        },
        "Backend Developer": {
            "required_skills": ["python", "sql", "docker", "rest api", "git", "postgresql", "redis"],
            "avg_experience": 2.0,
            "avg_score": 63,
        },
    }

    results = {}
    for role, benchmark in role_benchmarks.items():
        gap = gap_engine.analyze_gap(data.user_skills, benchmark["required_skills"])
        prediction = predictor.generate_detailed_report(
            data.user_skills, benchmark["required_skills"], data.experience, gap
        )
        score = prediction.get("employability_score", 0)

        results[role] = {
            "match_percentage": gap["match_percentage"],
            "your_score": round(score, 1),
            "benchmark_score": benchmark["avg_score"],
            "diff_from_benchmark": round(score - benchmark["avg_score"], 1),
            "above_average": score > benchmark["avg_score"],
            "matched_skills": gap["matched_skills"],
            "missing_skills": gap["missing_skills"],
            "gap_severity": gap["gap_severity"],
        }

    # Sort by match
    sorted_roles = sorted(results.items(), key=lambda x: x[1]["match_percentage"], reverse=True)

    return {
        "comparisons": dict(sorted_roles),
        "best_fit_role": sorted_roles[0][0] if sorted_roles else None,
        "user_skills": data.user_skills,
        "experience": data.experience,
        "total_roles_analyzed": len(results)
    }


# ====================================
# ANALYSIS HISTORY (MULTI-USER)
# ====================================
@router.get("/history")
def get_analysis_history(limit: int = 50):
    """
    Get past analysis history for viewing in History dashboard.
    Returns all stored analyses with key metrics.
    """
    import json as json_mod

    db = SessionLocal()
    try:
        analyses = get_all_analyses(db, limit=limit)
        history = []
        for a in analyses:
            # Parse JSON-stored skill lists
            resume_skills = []
            job_skills = []
            missing_skills = []

            if a.resume_skills:
                try:
                    resume_skills = json_mod.loads(a.resume_skills)
                except (json_mod.JSONDecodeError, TypeError):
                    resume_skills = [s.strip() for s in a.resume_skills.split(",") if s.strip()]

            if a.job_skills:
                try:
                    job_skills = json_mod.loads(a.job_skills)
                except (json_mod.JSONDecodeError, TypeError):
                    job_skills = [s.strip() for s in a.job_skills.split(",") if s.strip()]

            if a.missing_skills:
                try:
                    missing_skills = json_mod.loads(a.missing_skills)
                except (json_mod.JSONDecodeError, TypeError):
                    missing_skills = []

            history.append({
                "id": a.id,
                "resume_skills": resume_skills,
                "job_skills": job_skills,
                "missing_skills": missing_skills,
                "match_percentage": a.match_percentage,
                "employability_score": a.employability_score,
                "readiness_level": a.readiness_level,
                "gap_severity": a.gap_severity,
                "created_at": str(a.created_at) if a.created_at else None,
                "target_role": getattr(a, "target_role", "N/A"),
            })
        return {
            "total_analyses": len(history),
            "history": history,
            "aggregated_stats": _aggregate_history(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


def _aggregate_history(history):
    """Calculate aggregate statistics from history."""
    if not history:
        return {
            "avg_match": 0, "avg_score": 0, "avg_gap": "N/A",
            "total_analyses": 0, "most_common_missing": []
        }

    scores = [h["employability_score"] for h in history if h["employability_score"]]
    matches = [h["match_percentage"] for h in history if h["match_percentage"]]

    # Most common missing skills
    all_missing = []
    for h in history:
        all_missing.extend(h.get("missing_skills", []))

    from collections import Counter
    common_missing = [s for s, _ in Counter(all_missing).most_common(10)]

    return {
        "avg_match": round(sum(matches) / len(matches), 1) if matches else 0,
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "total_analyses": len(history),
        "most_common_missing": common_missing,
        "highest_score": max(scores) if scores else 0,
        "lowest_score": min(scores) if scores else 0,
    }
