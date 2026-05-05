"""
Employability Score Prediction Module
======================================
ML-based employability prediction using trained models:
    - Random Forest Classifier (readiness level)
    - XGBoost Regressor (employability score 0-100)
    - KNN (similar profile matching)

Features:
    - Multi-factor feature engineering
    - Model loading from trained artifacts
    - Fallback to rule-based prediction

References:
    - Kumar et al. (2023) — Skill Gap Analysis: A Machine Learning Approach
    - scikit-learn documentation
"""

import numpy as np
import joblib
from pathlib import Path
from backend.nlp.skill_normalizer import get_normalizer

# Import Advanced AI Models
try:
    from backend.models.salary_dnn_predictor import predict_salary
    from backend.models.career_trajectory_model import get_career_predictions
    from backend.models.skill_graph_engine import get_bridge_recommendations
except ImportError:
    pass

# LLM integration (optional — only loaded if fine-tuned model exists on disk)
_llm_pipeline = None
_LLM_MODEL_DIR = Path(__file__).resolve().parent.parent / "data" / "trained_models" / "llm_employability"


def _get_llm_pipeline():
    """Lazy-load the fine-tuned DistilBERT model if it exists on disk."""
    global _llm_pipeline
    if _llm_pipeline is not None:
        return _llm_pipeline
    if not _LLM_MODEL_DIR.exists():
        return None
    try:
        from transformers import pipeline as hf_pipeline
        _llm_pipeline = hf_pipeline(
            "text-classification",
            model=str(_LLM_MODEL_DIR),
            tokenizer=str(_LLM_MODEL_DIR),
            truncation=True,
            max_length=256,
        )
        print("[EmployabilityPredictor] [OK] Fine-tuned LLM loaded from disk.")
    except Exception as e:
        print(f"[EmployabilityPredictor] LLM load skipped: {e}")
        _llm_pipeline = None
    return _llm_pipeline

MODELS_DIR = Path(__file__).resolve().parent.parent / "data" / "trained_models"


class EmployabilityPredictor:
    """
    ML-based employability prediction using Random Forest, XGBoost, and KNN.
    """

    def __init__(self):
        self.normalizer = get_normalizer()
        self.rf_model = None
        self.xgb_model = None
        self.knn_model = None
        self.scaler = None
        self._load_models()

    def _load_models(self):
        """Load trained models from disk."""
        try:
            rf_path = MODELS_DIR / "random_forest_classifier.pkl"
            xgb_path = MODELS_DIR / "xgboost_regressor.pkl"
            knn_path = MODELS_DIR / "knn_model.pkl"
            scaler_path = MODELS_DIR / "feature_scaler.pkl"

            if rf_path.exists():
                self.rf_model = joblib.load(rf_path)
            if xgb_path.exists():
                self.xgb_model = joblib.load(xgb_path)
            if knn_path.exists():
                self.knn_model = joblib.load(knn_path)
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
        except Exception as e:
            print(f"Warning: Could not load ML models: {e}")

    def engineer_features(self, user_skills, job_skills, experience, gap_analysis):
        """
        Engineer features for ML prediction.

        Feature vector (8 dimensions):
            1. skill_match_pct — Percentage of matched skills
            2. market_demand_score — Average market weight of matched skills
            3. experience_normalized — Experience years (capped at 20)
            4. num_in_demand — Count of high-demand skills user has
            5. skill_diversity — Category diversity score (0-1)
            6. gap_severity_score — Numerical gap severity
            7. missing_skill_weight — Total weight of missing skills
            8. matched_skill_weight — Total weight of matched skills
        """
        normalizer = self.normalizer
        matched = gap_analysis.get("matched_skills", [])
        missing = gap_analysis.get("missing_skills", [])

        # Feature 1: Skill match percentage
        skill_match_pct = gap_analysis.get("match_percentage", 0) / 100

        # Feature 2: Average market demand of matched skills
        if matched:
            market_demand_score = np.mean([
                normalizer.get_market_weight(s) for s in matched
            ]) / 10
        else:
            market_demand_score = 0.0

        # Feature 3: Experience normalized (0-1)
        experience_normalized = min(experience / 20, 1.0)

        # Feature 4: Number of high-demand skills (weight >= 8)
        num_in_demand = sum(
            1 for s in user_skills
            if normalizer.get_market_weight(s) >= 8
        )
        num_in_demand_normalized = min(num_in_demand / 10, 1.0)

        # Feature 5: Skill diversity
        skill_diversity = normalizer.calculate_skill_diversity(user_skills)

        # Feature 6: Gap severity score
        severity_map = {"Low": 0.9, "Medium": 0.6, "High": 0.3, "Critical": 0.1}
        gap_severity = severity_map.get(
            gap_analysis.get("gap_severity", "High"), 0.3
        )

        # Feature 7: Missing skill weight (normalized)
        missing_weight = sum(
            normalizer.get_market_weight(s) for s in missing
        )
        missing_weight_normalized = 1 - min(missing_weight / 50, 1.0)

        # Feature 8: Matched skill weight (normalized)
        matched_weight = sum(
            normalizer.get_market_weight(s) for s in matched
        )
        matched_weight_normalized = min(matched_weight / 50, 1.0)

        return np.array([
            skill_match_pct,
            market_demand_score,
            experience_normalized,
            num_in_demand_normalized,
            skill_diversity,
            gap_severity,
            missing_weight_normalized,
            matched_weight_normalized
        ]).reshape(1, -1)

    def predict(self, user_skills, job_skills, experience, gap_analysis):
        """
        Predict employability score and readiness level.

        Returns:
            Dict with score, readiness_level, confidence, feature_importance
        """
        features = self.engineer_features(
            user_skills, job_skills, experience, gap_analysis
        )

        # Scale features if scaler available
        if self.scaler is not None:
            features_scaled = self.scaler.transform(features)
        else:
            features_scaled = features

        result = {}

        # XGBoost regression — employability score
        if self.xgb_model is not None:
            try:
                score = float(self.xgb_model.predict(features_scaled)[0])
                result["employability_score"] = round(np.clip(score, 0, 100), 2)
            except Exception:
                result["employability_score"] = self._fallback_score(features)
        else:
            result["employability_score"] = self._fallback_score(features)

        # Random Forest classification — readiness level
        if self.rf_model is not None:
            try:
                level = self.rf_model.predict(features_scaled)[0]
                proba = self.rf_model.predict_proba(features_scaled)[0]
                result["readiness_level"] = str(level)
                result["readiness_confidence"] = round(float(max(proba)), 3)
                result["readiness_probabilities"] = {
                    str(cls): round(float(p), 3)
                    for cls, p in zip(self.rf_model.classes_, proba)
                }
            except Exception:
                result["readiness_level"] = self._fallback_readiness(
                    result.get("employability_score", 50)
                )
                result["readiness_confidence"] = 0.7
        else:
            result["readiness_level"] = self._fallback_readiness(
                result.get("employability_score", 50)
            )
            result["readiness_confidence"] = 0.7

        # KNN — similar profile match
        if self.knn_model is not None:
            try:
                distances, indices = self.knn_model.kneighbors(features_scaled)
                result["similar_profiles"] = {
                    "average_distance": round(float(np.mean(distances)), 3),
                    "closest_match_distance": round(float(distances[0][0]), 3)
                }
            except Exception:
                pass

        # Feature importance labels
        result["feature_names"] = [
            "Skill Match %",
            "Market Demand Score",
            "Experience Level",
            "In-Demand Skills Count",
            "Skill Diversity",
            "Gap Severity",
            "Missing Skills Impact",
            "Matched Skills Value"
        ]
        result["feature_values"] = features.flatten().tolist()

        # Feature importance from RF model
        if self.rf_model is not None and hasattr(self.rf_model, "feature_importances_"):
            result["feature_importance"] = dict(zip(
                result["feature_names"],
                [round(float(x), 4) for x in self.rf_model.feature_importances_]
            ))

        # ── LLM Enrichment (silent fallback) ──────────────────────
        # If the fine-tuned DistilBERT model exists, use it to enrich
        # the prediction with a semantic demand signal from real job text.
        try:
            llm = _get_llm_pipeline()
            if llm is not None and user_skills:
                skill_text = ", ".join(user_skills[:30])
                llm_result = llm(skill_text)[0]
                result["llm_demand_label"] = llm_result["label"]
                result["llm_demand_confidence"] = round(llm_result["score"], 3)
                # Blend LLM signal into employability score (20% weight)
                llm_boost = {"High Demand": 10, "Medium Demand": 0, "Low Demand": -10}
                boost = llm_boost.get(llm_result["label"], 0) * llm_result["score"]
                blended = round(
                    np.clip(result.get("employability_score", 50) + boost, 0, 100), 2
                )
                result["employability_score_llm_blended"] = blended
                result["llm_model"] = "distilbert-base-uncased (fine-tuned on real job data)"
        except Exception:
            pass  # LLM enrichment is completely optional — never break existing flow

        # ── Advanced AI Model Integration ─────────────────────
        try:
            # 1. Salary DNN
            salary_pred = predict_salary(features.flatten().tolist()[:7])
            if salary_pred:
                result["predicted_salary_usd"] = round(salary_pred, 2)
            
            # 2. Career Trajectory (Markov Chain)
            # Infer current role from highest match or target_role if passed
            # Here we default to "Software Engineer" as a fallback base
            base_role = "Software Engineer"
            result["career_trajectory_forecast"] = get_career_predictions(base_role)
            
            # 3. Skill Graph Engine (Node2Vec)
            missing_skills = gap_analysis.get("missing_skills", [])
            if missing_skills and user_skills:
                bridge_skills = get_bridge_recommendations(user_skills, missing_skills)
                result["bridge_skills_recommended"] = bridge_skills
                
        except Exception as e:
            print(f"[EmployabilityPredictor] Advanced AI enrichment skipped: {e}")

        return result

    def _fallback_score(self, features):
        """Rule-based fallback when ML models are not loaded."""
        f = features.flatten()
        # Weighted combination of features
        score = (
            f[0] * 35 +    # skill match
            f[1] * 15 +    # market demand
            f[2] * 15 +    # experience
            f[3] * 10 +    # in-demand skills
            f[4] * 5 +     # diversity
            f[5] * 10 +    # gap severity
            f[6] * 5 +     # missing weight
            f[7] * 5       # matched weight
        )
        return round(np.clip(score, 0, 100), 2)

    def _fallback_readiness(self, score):
        """Rule-based fallback for readiness classification."""
        if score >= 80:
            return "Highly Competitive"
        elif score >= 60:
            return "Competitive"
        elif score >= 40:
            return "Developing"
        else:
            return "Not Ready"

    def generate_detailed_report(self, user_skills, job_skills, experience, gap_analysis):
        """
        Generate comprehensive employability report.
        """
        prediction = self.predict(user_skills, job_skills, experience, gap_analysis)

        score = prediction.get("employability_score", 50)

        report = {
            **prediction,
            "technical_score": gap_analysis.get("match_percentage", 0),
            "experience_score": round(min(experience * 10, 100), 2),
            "skill_gap_severity": gap_analysis.get("gap_severity", "Medium"),
            "overall_rating": self._get_rating(score),
            "job_suitability": "Suitable" if score >= 55 else "Not Suitable",
            "improvement_potential": self._estimate_improvement(
                gap_analysis.get("missing_skills", [])
            ),
            "recommended_focus_areas": self._get_focus_areas(
                gap_analysis.get("category_analysis", {})
            )
        }

        return report

    def _get_rating(self, score):
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 55:
            return "Fair"
        else:
            return "Needs Improvement"

    def _estimate_improvement(self, missing_skills):
        """Estimate potential score improvement if missing skills are learned."""
        if not missing_skills:
            return {"potential_increase": 0, "skills_to_learn": 0}

        top_3_weight = sum(
            self.normalizer.get_market_weight(s)
            for s in missing_skills[:3]
        )

        return {
            "potential_increase": round(min(top_3_weight * 3, 30), 1),
            "skills_to_learn": min(len(missing_skills), 5),
            "top_skills_to_learn": missing_skills[:3]
        }

    def _get_focus_areas(self, category_analysis):
        """Identify weakest skill categories to focus on."""
        weak_areas = []
        for cat, data in category_analysis.items():
            if data["coverage"] < 50 and data["missing"]:
                weak_areas.append({
                    "category": cat,
                    "coverage": data["coverage"],
                    "missing_count": len(data["missing"])
                })

        return sorted(weak_areas, key=lambda x: x["coverage"])


# ====================================
# SINGLETON
# ====================================
_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = EmployabilityPredictor()
    return _predictor
