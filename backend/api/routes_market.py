"""
Market Intelligence API Routes
================================
Endpoints for job market trends, skill demand analysis, and role insights.
"""

from fastapi import APIRouter
from typing import Optional

from backend.models.market_analyzer import get_market_analyzer

router = APIRouter(prefix="/api", tags=["Market Intelligence"])


@router.get("/market-trends")
def get_market_trends(region: Optional[str] = None, top_n: int = 150):
    """
    Get current skill demand trends from job market data.
    Optionally filter by region (India, US, Europe, etc.)
    """
    analyzer = get_market_analyzer()

    demand_scores = analyzer.get_skill_demand_scores(region=region)
    trending = analyzer.get_trending_skills(top_n=top_n)
    summary = analyzer.get_market_summary()

    return {
        "demand_scores": dict(list(demand_scores.items())[:top_n]),
        "trending_skills": trending,
        "market_summary": summary,
        "region_filter": region or "All Regions"
    }


@router.get("/market-trends/{skill}")
def get_skill_trend(skill: str):
    """Get demand history for a specific skill."""
    analyzer = get_market_analyzer()

    time_series = analyzer.get_skill_time_series(skill)
    demand_scores = analyzer.get_skill_demand_scores()

    return {
        "skill": skill,
        "current_demand_score": demand_scores.get(skill.lower(), 0),
        "time_series": time_series,
        "total_data_points": len(time_series)
    }


@router.get("/role-analysis")
def get_role_analysis(role: Optional[str] = None):
    """Get job role analysis with required skills and salary data."""
    analyzer = get_market_analyzer()
    analysis = analyzer.get_role_analysis(role)

    return {
        "role": role or "All Roles",
        "analysis": analysis
    }


@router.get("/market-summary")
def get_market_summary():
    """Get overall market intelligence summary."""
    analyzer = get_market_analyzer()
    return analyzer.get_market_summary()
