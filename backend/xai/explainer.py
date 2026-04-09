"""
Explainable AI (XAI) Module
============================
Provides transparent explanations for AI/ML predictions using
SHAP and rule-based explanation generation.

Features:
    - SHAP feature importance (when models are available)
    - Rule-based explanation fallback
    - Market evidence for recommendations
    - Confidence scores and reasoning chains
    - Decision transparency

References:
    - Zhang & Liu (2024) — AI-Driven Career Recommendation Systems
    - SHAP (SHapley Additive exPlanations) - Lundberg & Lee (2017)
"""

import numpy as np
import joblib
from pathlib import Path
from backend.nlp.skill_normalizer import get_normalizer

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

MODELS_DIR = Path(__file__).resolve().parent.parent / "data" / "trained_models"


class ExplainableAI:
    """
    Explainable AI module providing transparent reasoning
    for skill gap analysis and employability predictions.
    Uses SHAP (SHapley Additive exPlanations) when available.
    """

    def __init__(self):
        self.normalizer = get_normalizer()
        self.rf_model = None
        self._load_models()

    def _load_models(self):
        """Load trained models for SHAP analysis."""
        try:
            rf_path = MODELS_DIR / "random_forest_classifier.pkl"
            if rf_path.exists():
                self.rf_model = joblib.load(rf_path)
        except Exception:
            pass

    def generate_shap_explanation(self, features, feature_names):
        """
        Generate SHAP values for a prediction using TreeExplainer.
        Returns SHAP values per feature for waterfall/force plots.
        """
        if not HAS_SHAP or self.rf_model is None:
            return self._fallback_shap(features, feature_names)

        try:
            explainer = shap.TreeExplainer(self.rf_model)
            shap_values = explainer.shap_values(features)

            # For multi-class, pick the predicted class
            if isinstance(shap_values, list):
                pred_class = self.rf_model.predict(features)[0]
                class_idx = list(self.rf_model.classes_).index(pred_class)
                values = shap_values[class_idx][0]
            else:
                values = shap_values[0]

            shap_result = {
                "method": "SHAP TreeExplainer",
                "base_value": float(explainer.expected_value[0]) if isinstance(
                    explainer.expected_value, (list, np.ndarray)
                ) else float(explainer.expected_value),
                "features": []
            }

            for name, val, shap_val in zip(feature_names, features.flatten(), values):
                shap_result["features"].append({
                    "name": name,
                    "value": round(float(val), 4),
                    "shap_value": round(float(shap_val), 4),
                    "impact": "positive" if shap_val > 0 else "negative",
                    "magnitude": abs(round(float(shap_val), 4))
                })

            shap_result["features"].sort(key=lambda x: x["magnitude"], reverse=True)
            return shap_result

        except Exception as e:
            return self._fallback_shap(features, feature_names)

    def _fallback_shap(self, features, feature_names):
        """Fallback SHAP-like explanation when SHAP library not available."""
        f = features.flatten()
        weights = [0.30, 0.15, 0.12, 0.10, 0.08, 0.12, 0.07, 0.06]
        
        result = {
            "method": "Approximated Feature Importance",
            "base_value": 0.5,
            "features": []
        }
        
        for name, val, w in zip(feature_names, f, weights):
            impact = round(float((val - 0.5) * w), 4)
            result["features"].append({
                "name": name,
                "value": round(float(val), 4),
                "shap_value": impact,
                "impact": "positive" if impact > 0 else "negative",
                "magnitude": abs(impact)
            })
        
        result["features"].sort(key=lambda x: x["magnitude"], reverse=True)
        return result

    def explain_prediction(self, prediction_result, gap_analysis, user_skills, job_skills):
        """
        Generate comprehensive explanation for an employability prediction.

        Args:
            prediction_result: Output from EmployabilityPredictor
            gap_analysis: Output from SkillGapEngine
            user_skills: User's skills list
            job_skills: Required job skills list

        Returns:
            Dict with explanations, evidence, and recommendations
        """
        score = prediction_result.get("employability_score", 50)
        level = prediction_result.get("readiness_level", "Developing")

        explanation = {
            "summary": self._generate_summary(score, level, gap_analysis),
            "score_breakdown": self._explain_score_breakdown(
                prediction_result, gap_analysis
            ),
            "feature_impact": self._explain_feature_impact(prediction_result),
            "skill_analysis": self._explain_skill_analysis(
                user_skills, job_skills, gap_analysis
            ),
            "market_evidence": self._gather_market_evidence(
                gap_analysis.get("missing_skills", [])
            ),
            "strengths": self._identify_strengths(user_skills, job_skills),
            "improvement_areas": self._identify_improvements(gap_analysis),
            "recommendation_reasons": self._generate_recommendation_reasons(
                gap_analysis
            ),
            "confidence_assessment": self._assess_confidence(prediction_result),
            "actionable_insights": self._generate_actionable_insights(
                score, gap_analysis
            )
        }

        return explanation

    def _generate_summary(self, score, level, gap_analysis):
        """Generate human-readable summary of the prediction."""
        match_pct = gap_analysis.get("match_percentage", 0)
        missing_count = gap_analysis.get("total_missing", 0)
        matched_count = gap_analysis.get("total_matched", 0)

        summary = f"Your employability score is {score:.0f}/100 ({level}). "

        if match_pct >= 80:
            summary += (f"You match {match_pct:.0f}% of the required skills, "
                       f"demonstrating strong alignment with the job requirements. ")
        elif match_pct >= 60:
            summary += (f"You match {match_pct:.0f}% of the required skills. "
                       f"With {missing_count} missing skill(s), you're on a good track "
                       f"but need targeted improvement. ")
        elif match_pct >= 40:
            summary += (f"You match {match_pct:.0f}% of the required skills. "
                       f"There are {missing_count} skill gaps that need attention "
                       f"to improve your candidacy. ")
        else:
            summary += (f"You currently match only {match_pct:.0f}% of requirements. "
                       f"Significant skill development in {missing_count} areas "
                       f"is recommended. ")

        return summary

    def _explain_score_breakdown(self, prediction, gap_analysis):
        """Explain how the score was calculated."""
        feature_names = prediction.get("feature_names", [])
        feature_values = prediction.get("feature_values", [])

        breakdown = []
        weights = {
            "Skill Match %": 35,
            "Market Demand Score": 15,
            "Experience Level": 15,
            "In-Demand Skills Count": 10,
            "Skill Diversity": 5,
            "Gap Severity": 10,
            "Missing Skills Impact": 5,
            "Matched Skills Value": 5
        }

        for name, value in zip(feature_names, feature_values):
            weight = weights.get(name, 10)
            contribution = round(value * weight, 2)
            breakdown.append({
                "factor": name,
                "value": round(value, 3),
                "weight_percentage": weight,
                "contribution": contribution,
                "rating": (
                    "Strong" if value >= 0.7 else
                    "Moderate" if value >= 0.4 else
                    "Weak"
                )
            })

        return sorted(breakdown, key=lambda x: x["contribution"], reverse=True)

    def _explain_feature_impact(self, prediction):
        """Explain which features had the most impact on the prediction."""
        importance = prediction.get("feature_importance", {})
        if not importance:
            return []

        impacts = []
        for feature, imp_score in sorted(
            importance.items(), key=lambda x: x[1], reverse=True
        ):
            direction = "positive" if imp_score > 0 else "neutral"
            impacts.append({
                "feature": feature,
                "importance_score": imp_score,
                "impact_level": (
                    "High" if imp_score > 0.2 else
                    "Medium" if imp_score > 0.1 else
                    "Low"
                ),
                "direction": direction
            })

        return impacts

    def _explain_skill_analysis(self, user_skills, job_skills, gap_analysis):
        """Provide detailed explanation of skill-by-skill analysis."""
        matched = gap_analysis.get("matched_skills", [])
        missing = gap_analysis.get("missing_skills", [])

        analysis = {
            "matched_explanation": [],
            "missing_explanation": [],
            "extra_skills_note": ""
        }

        for skill in matched:
            weight = self.normalizer.get_market_weight(skill)
            analysis["matched_explanation"].append({
                "skill": skill,
                "market_weight": weight,
                "note": f"✅ {skill.title()} is in demand (weight: {weight}/10) and you have this skill."
            })

        for skill in missing[:5]:
            weight = self.normalizer.get_market_weight(skill)
            difficulty = self.normalizer.get_skill_difficulty(skill)
            hours = self.normalizer.get_estimated_hours(skill)
            analysis["missing_explanation"].append({
                "skill": skill,
                "market_weight": weight,
                "difficulty": difficulty,
                "estimated_hours": hours,
                "note": (f"❌ {skill.title()} is required (demand: {weight}/10, "
                        f"difficulty: {difficulty}). Estimated {hours}hrs to learn.")
            })

        extra = gap_analysis.get("extra_skills", [])
        if extra:
            analysis["extra_skills_note"] = (
                f"You have {len(extra)} additional skills not required for this role: "
                f"{', '.join(extra[:5])}. These show breadth but won't impact the match score."
            )

        return analysis

    def _gather_market_evidence(self, missing_skills):
        """Attach market data supporting skill recommendations."""
        evidence = []
        for skill in missing_skills[:5]:
            weight = self.normalizer.get_market_weight(skill)
            evidence.append({
                "skill": skill,
                "demand_score": weight,
                "evidence": (
                    f"{skill.title()} appears frequently in job postings "
                    f"with a demand score of {weight}/10."
                ),
                "priority": "High" if weight >= 8 else "Medium" if weight >= 5 else "Low"
            })
        return evidence

    def _identify_strengths(self, user_skills, job_skills):
        """Identify user's strongest areas."""
        strengths = []
        matched = set(user_skills) & set(job_skills)

        for skill in matched:
            weight = self.normalizer.get_market_weight(skill)
            if weight >= 7:
                strengths.append({
                    "skill": skill,
                    "market_weight": weight,
                    "significance": "This is a high-demand skill that strengthens your profile."
                })

        # Diversity strength
        diversity = self.normalizer.calculate_skill_diversity(list(user_skills))
        if diversity > 0.3:
            strengths.append({
                "skill": "Skill Diversity",
                "market_weight": round(diversity * 10, 1),
                "significance": f"Your skills span {round(diversity*100)}% of categories, showing versatility."
            })

        return strengths

    def _identify_improvements(self, gap_analysis):
        """Identify key areas for improvement."""
        improvements = []
        category_gaps = gap_analysis.get("category_analysis", {})

        for cat, data in category_gaps.items():
            if data["coverage"] < 50 and data["missing"]:
                improvements.append({
                    "area": cat.replace("_", " ").title(),
                    "coverage": data["coverage"],
                    "missing_skills": data["missing"],
                    "recommendation": (
                        f"Your coverage in {cat.replace('_', ' ').title()} is "
                        f"{data['coverage']}%. Focus on: {', '.join(data['missing'][:3])}"
                    )
                })

        return sorted(improvements, key=lambda x: x["coverage"])

    def _generate_recommendation_reasons(self, gap_analysis):
        """Generate clear reasons for each recommendation."""
        reasons = []
        priority_ranking = gap_analysis.get("priority_ranking", [])

        for item in priority_ranking[:5]:
            skill = item["skill"]
            weight = item["market_weight"]
            unlock = item.get("unlocks_count", 0)

            reason = f"Learn {skill.title()} because: "
            reason_parts = []

            if weight >= 8:
                reason_parts.append(f"very high market demand ({weight}/10)")
            elif weight >= 5:
                reason_parts.append(f"moderate market demand ({weight}/10)")

            if unlock > 0:
                reason_parts.append(f"it unlocks {unlock} other skills")

            if item.get("difficulty") == "beginner":
                reason_parts.append("it's beginner-friendly")

            reason += ", ".join(reason_parts) + "."

            reasons.append({
                "skill": skill,
                "reason": reason,
                "priority": item.get("priority_score", 0)
            })

        return reasons

    def _assess_confidence(self, prediction):
        """Assess overall confidence in the prediction."""
        confidence = prediction.get("readiness_confidence", 0.7)

        return {
            "overall_confidence": round(confidence * 100, 1),
            "confidence_level": (
                "High" if confidence >= 0.8 else
                "Medium" if confidence >= 0.6 else
                "Low"
            ),
            "note": (
                "Prediction is based on ML model with cross-validated accuracy. "
                "Results improve with more detailed skill data."
            )
        }

    def _generate_actionable_insights(self, score, gap_analysis):
        """Generate specific, actionable next steps."""
        insights = []
        missing = gap_analysis.get("missing_skills", [])

        if score < 40:
            insights.append("🎯 Start with foundational skills before advanced ones.")
            if missing:
                insights.append(f"📚 Priority 1: Learn {missing[0]} — highest impact on your score.")
        elif score < 60:
            if missing:
                insights.append(f"📚 Learning {', '.join(missing[:2])} could boost your score by ~15-20 points.")
            insights.append("💡 Consider building a portfolio project using your existing skills.")
        elif score < 80:
            insights.append("🚀 You're competitive! Focus on advanced skills to stand out.")
            if missing:
                insights.append(f"⭐ Mastering {missing[0]} would make you highly competitive.")
        else:
            insights.append("🏆 Excellent profile! Focus on deepening expertise.")
            insights.append("📝 Highlight your skills in resume with specific project examples.")

        insights.append("📊 Keep tracking market trends — skill demand changes quarterly.")

        return insights


# ====================================
# SINGLETON
# ====================================
_explainer = None

def get_explainer():
    global _explainer
    if _explainer is None:
        _explainer = ExplainableAI()
    return _explainer
