"""
Dashboard API Routes
=====================
Endpoints for dashboard statistics and placement analytics.
"""

from fastapi import APIRouter
from backend.database.db_setup import SessionLocal
from backend.database.crud import get_dashboard_stats, get_analysis_history
from backend.models.market_analyzer import get_market_analyzer

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/dashboard-stats")
def dashboard_stats():
    """Get aggregated dashboard statistics."""
    db = SessionLocal()
    try:
        stats = get_dashboard_stats(db)
        analyzer = get_market_analyzer()
        market = analyzer.get_market_summary()

        all_trends = analyzer.get_skill_demand_scores()
        return {
            "platform_stats": stats,
            "market_overview": market,
            "recent_trends": all_trends,          # full list — frontend controls slice
            "top_trends": dict(list(all_trends.items())[:10]),  # precomputed top-10
            "total_skills_tracked": len(all_trends),
        }
    finally:
        db.close()


@router.get("/analysis-history")
def analysis_history(limit: int = 20):
    """Get recent analysis history."""
    db = SessionLocal()
    try:
        analyses = get_analysis_history(db, limit=limit)
        return {
            "analyses": [
                {
                    "id": a.id,
                    "match_percentage": a.match_percentage,
                    "employability_score": a.employability_score,
                    "readiness_level": a.readiness_level,
                    "gap_severity": a.gap_severity,
                    "created_at": str(a.created_at)
                }
                for a in analyses
            ],
            "total": len(analyses)
        }
    finally:
        db.close()


@router.get("/placement-stats")
def placement_stats():
    """
    Placement analytics for college stakeholder view.
    Shows aggregate skill gap trends and employability statistics.
    """
    db = SessionLocal()
    try:
        analyses = get_analysis_history(db, limit=100)
        analyzer = get_market_analyzer()

        if analyses:
            avg_match = sum(a.match_percentage for a in analyses) / len(analyses)
            avg_score = sum(a.employability_score for a in analyses) / len(analyses)

            readiness_dist = {}
            for a in analyses:
                level = a.readiness_level or "Unknown"
                readiness_dist[level] = readiness_dist.get(level, 0) + 1

            severity_dist = {}
            for a in analyses:
                sev = a.gap_severity or "Unknown"
                severity_dist[sev] = severity_dist.get(sev, 0) + 1
        else:
            avg_match = 0
            avg_score = 0
            readiness_dist = {}
            severity_dist = {}

        return {
            "total_assessments": len(analyses),
            "average_match_percentage": round(avg_match, 2),
            "average_employability_score": round(avg_score, 2),
            "readiness_distribution": readiness_dist,
            "gap_severity_distribution": severity_dist,
            "top_demanded_skills": dict(
                list(analyzer.get_skill_demand_scores().items())[:15]
            ),
            "stakeholder": "college"
        }
    finally:
        db.close()
