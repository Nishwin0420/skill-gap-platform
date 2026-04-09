"""
Skill Demand Forecasting Engine
=================================
Uses ARIMA-style trend analysis to predict future skill demand.
Projects which skills will be in demand 3-6 months from now.

Features:
    - Time-series trend extrapolation
    - Growth rate forecasting
    - Emerging skills detection
    - Risk identification for declining skills

References:
    - Box-Jenkins ARIMA methodology
    - Kumar et al. (2023) — Skill Gap Analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class SkillForecaster:
    """
    Predicts future skill demand using time-series trend analysis.
    """

    def __init__(self):
        self.job_data = self._load_data()

    def _load_data(self):
        csv_path = DATA_DIR / "job_market_data.csv"
        if csv_path.exists():
            return pd.read_csv(csv_path, parse_dates=["posted_date"])
        return pd.DataFrame()

    def forecast_skill_demand(self, skill_name, months_ahead=6):
        """
        Forecast demand for a specific skill over the next N months.
        Uses linear trend extrapolation with growth rate.
        """
        if self.job_data.empty:
            return []

        df = self.job_data.copy()
        df["posted_date"] = pd.to_datetime(df["posted_date"])
        mask = df["skills_required"].str.contains(skill_name, case=False, na=False)
        skill_df = df[mask]

        if skill_df.empty:
            return []

        # Monthly counts
        skill_df = skill_df.set_index("posted_date")
        monthly = skill_df.resample("M").size().reset_index()
        monthly.columns = ["date", "count"]

        if len(monthly) < 2:
            return []

        # Calculate trend using linear regression
        x = np.arange(len(monthly))
        y = monthly["count"].values
        coeffs = np.polyfit(x, y, 1)
        slope, intercept = coeffs

        # Forecast future months
        forecasts = []
        last_date = monthly["date"].max()

        for i in range(1, months_ahead + 1):
            future_date = last_date + pd.DateOffset(months=i)
            future_x = len(monthly) + i - 1
            predicted = max(0, round(slope * future_x + intercept))

            forecasts.append({
                "date": future_date.strftime("%Y-%m"),
                "predicted_demand": predicted,
                "confidence": max(0.5, round(1 - (i * 0.08), 2)),
                "trend": "Rising" if slope > 0.5 else "Stable" if slope > -0.5 else "Declining"
            })

        return {
            "skill": skill_name,
            "historical": [
                {"date": row["date"].strftime("%Y-%m"), "count": int(row["count"])}
                for _, row in monthly.iterrows()
            ],
            "forecast": forecasts,
            "trend_slope": round(float(slope), 3),
            "growth_rate": round(float(slope / max(y.mean(), 1) * 100), 2),
            "trend_direction": "Rising" if slope > 0.5 else "Stable" if slope > -0.5 else "Declining"
        }

    def get_emerging_skills(self, top_n=10):
        """
        Identify skills with the fastest growth rate.
        These are emerging skills to watch.
        """
        if self.job_data.empty:
            return []

        df = self.job_data.copy()
        df["posted_date"] = pd.to_datetime(df["posted_date"])
        median_date = df["posted_date"].median()

        recent = df[df["posted_date"] >= median_date]
        older = df[df["posted_date"] < median_date]

        recent_skills = Counter()
        for skills_str in recent["skills_required"]:
            recent_skills.update(str(skills_str).split("|"))

        older_skills = Counter()
        for skills_str in older["skills_required"]:
            older_skills.update(str(skills_str).split("|"))

        growth_rates = {}
        for skill in set(list(recent_skills.keys()) + list(older_skills.keys())):
            r = recent_skills.get(skill, 0)
            o = older_skills.get(skill, 1)
            growth = ((r - o) / max(o, 1)) * 100
            growth_rates[skill] = {
                "growth_rate": round(growth, 2),
                "recent_count": r,
                "older_count": o,
                "status": "Emerging" if growth > 30 else "Growing" if growth > 10 else "Stable" if growth > -10 else "Declining"
            }

        sorted_skills = sorted(growth_rates.items(), key=lambda x: x[1]["growth_rate"], reverse=True)
        return [{"skill": k, **v} for k, v in sorted_skills[:top_n]]

    def get_declining_skills(self, top_n=5):
        """Identify skills with decreasing demand — risk skills."""
        emerging = self.get_emerging_skills(top_n=200)
        declining = [s for s in emerging if s["status"] == "Declining"]
        return declining[:top_n]

    def forecast_all_top_skills(self, top_n=10, months_ahead=6):
        """Forecast demand for the top N most popular skills."""
        if self.job_data.empty:
            return []

        all_skills = []
        for skills_str in self.job_data["skills_required"]:
            all_skills.extend(str(skills_str).split("|"))

        top_skills = [s for s, _ in Counter(all_skills).most_common(top_n)]

        forecasts = []
        for skill in top_skills:
            result = self.forecast_skill_demand(skill, months_ahead)
            if result:
                forecasts.append({
                    "skill": skill,
                    "current_demand": result["historical"][-1]["count"] if result["historical"] else 0,
                    "forecast_6m": result["forecast"][-1]["predicted_demand"] if result["forecast"] else 0,
                    "growth_rate": result["growth_rate"],
                    "trend": result["trend_direction"]
                })

        return sorted(forecasts, key=lambda x: x["growth_rate"], reverse=True)


# ====================================
# SINGLETON
# ====================================
_forecaster = None

def get_forecaster():
    global _forecaster
    if _forecaster is None:
        _forecaster = SkillForecaster()
    return _forecaster
