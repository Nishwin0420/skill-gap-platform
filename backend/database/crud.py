"""
CRUD Operations Module
=======================
Database CRUD (Create, Read, Update, Delete) operations
for the AI Skill Gap Intelligence Platform.
"""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database.db_setup import (
    User, Skill, UserSkill, JobListing,
    AnalysisHistory, MarketTrend, LearningPath, SkillCategory,
    SessionLocal
)


# ====================================
# USER OPERATIONS
# ====================================
def create_user(db: Session, name, email=None, role="student",
                experience=0, target_role=None, region="India"):
    user = User(
        name=name, email=email, role=role,
        experience_years=experience, target_role=target_role, region=region
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip=0, limit=100):
    return db.query(User).offset(skip).limit(limit).all()


# ====================================
# ANALYSIS HISTORY
# ====================================
def save_analysis(db: Session, user_id=None, resume_skills=None,
                  job_skills=None, result=None):
    """Save a complete analysis result to history."""
    analysis = AnalysisHistory(
        user_id=user_id,
        resume_skills=json.dumps(resume_skills) if resume_skills else None,
        job_skills=json.dumps(job_skills) if job_skills else None,
        match_percentage=result.get("match_percentage", 0) if result else 0,
        employability_score=result.get("employability_score", 0) if result else 0,
        readiness_level=result.get("readiness_level", "") if result else "",
        gap_severity=result.get("gap_severity", "") if result else "",
        missing_skills=json.dumps(
            result.get("missing_skills", [])
        ) if result else None,
        analysis_result=json.dumps(result) if result else None
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_analysis_history(db: Session, user_id=None, limit=20):
    query = db.query(AnalysisHistory)
    if user_id:
        query = query.filter(AnalysisHistory.user_id == user_id)
    return query.order_by(AnalysisHistory.created_at.desc()).limit(limit).all()


def get_analysis_by_id(db: Session, analysis_id: int):
    return db.query(AnalysisHistory).filter(
        AnalysisHistory.id == analysis_id
    ).first()


# ====================================
# MARKET TRENDS
# ====================================
def save_market_trend(db: Session, skill_name, demand_score, region="Global"):
    trend = MarketTrend(
        skill_name=skill_name,
        demand_score=demand_score,
        region=region
    )
    db.add(trend)
    db.commit()
    return trend


# ====================================
# LEARNING PATHS
# ====================================
def save_learning_path(db: Session, user_id=None, target_role=None,
                       path_data=None, total_hours=0, total_skills=0):
    path = LearningPath(
        user_id=user_id,
        target_role=target_role,
        path_data=json.dumps(path_data) if path_data else None,
        total_hours=total_hours,
        total_skills=total_skills
    )
    db.add(path)
    db.commit()
    db.refresh(path)
    return path


# ====================================
# DASHBOARD STATS
# ====================================
def get_dashboard_stats(db: Session):
    """Get aggregate statistics for the dashboard."""
    total_analyses = db.query(AnalysisHistory).count()
    total_users = db.query(User).count()

    # Average scores
    analyses = db.query(AnalysisHistory).all()
    if analyses:
        avg_match = sum(a.match_percentage for a in analyses) / len(analyses)
        avg_score = sum(a.employability_score for a in analyses) / len(analyses)
    else:
        avg_match = 0
        avg_score = 0

    return {
        "total_analyses": total_analyses,
        "total_users": total_users,
        "average_match_percentage": round(avg_match, 2),
        "average_employability_score": round(avg_score, 2)
    }


# ====================================
# HISTORY QUERIES
# ====================================
def get_all_analyses(db: Session, limit=50):
    """Get all analyses for history page, ordered by most recent."""
    return (
        db.query(AnalysisHistory)
        .order_by(AnalysisHistory.created_at.desc())
        .limit(limit)
        .all()
    )


def get_all_learning_paths(db: Session, limit=50):
    """Get all generated learning paths for history browsing."""
    return (
        db.query(LearningPath)
        .order_by(LearningPath.created_at.desc())
        .limit(limit)
        .all()
    )


# ====================================
# COHORT BENCHMARKING
# ====================================
def get_cohort_scores(db: Session, target_role: str = None, limit: int = 500):
    """
    Retrieve historical employability scores for benchmarking.
    If target_role is provided, filters by role stored in analysis_result JSON.
    Returns a list of employability_score floats for percentile calculation.
    """
    import json as _json

    query = db.query(AnalysisHistory).order_by(
        AnalysisHistory.created_at.desc()
    ).limit(limit)

    all_records = query.all()
    scores = []

    for record in all_records:
        # Always include the raw score
        if record.employability_score and record.employability_score > 0:
            # Optional role filter from stored JSON
            if target_role:
                try:
                    result_data = _json.loads(record.analysis_result or "{}")
                    stored_role = result_data.get("target_role", "")
                    if stored_role and stored_role.lower() != target_role.lower():
                        continue
                except Exception:
                    pass  # If parsing fails, include the record anyway

            scores.append(round(float(record.employability_score), 2))

    return scores
