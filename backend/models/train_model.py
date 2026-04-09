"""
Model Training Pipeline
========================
Generates synthetic employment data, trains ML models, and saves them.

Models trained:
    1. Random Forest Classifier — Readiness level classification
    2. XGBoost Regressor — Employability score prediction (0-100)
    3. KNN — Similar profile matching

References:
    - Kumar et al. (2023) — Skill Gap Analysis: A Machine Learning Approach
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, accuracy_score, mean_absolute_error,
    r2_score, confusion_matrix
)
import joblib
import warnings
warnings.filterwarnings("ignore")

try:
    from xgboost import XGBRegressor
    HAS_XGBOOST = True
except ImportError:
    from sklearn.ensemble import GradientBoostingRegressor as XGBRegressor
    HAS_XGBOOST = False

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "data" / "trained_models"
DATASETS_DIR = BASE_DIR / "data" / "datasets"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATASETS_DIR.mkdir(parents=True, exist_ok=True)


def generate_synthetic_data(n_samples=5000):
    """
    Generate synthetic employment/skill dataset for model training.
    
    Features:
        - skill_match_pct (0-1)
        - market_demand_score (0-1)
        - experience_normalized (0-1)
        - num_in_demand_normalized (0-1)
        - skill_diversity (0-1)
        - gap_severity (0-1)
        - missing_weight_normalized (0-1)
        - matched_weight_normalized (0-1)
    
    Targets:
        - employability_score (0-100)
        - readiness_level (categorical)
    """
    np.random.seed(42)
    
    # Generate features with realistic distributions
    skill_match = np.random.beta(5, 3, n_samples)  # Skewed toward higher match
    market_demand = np.random.beta(4, 4, n_samples)
    experience = np.random.beta(3, 5, n_samples)
    in_demand = np.random.beta(4, 5, n_samples)
    diversity = np.random.beta(3, 6, n_samples)
    gap_severity = skill_match * 0.7 + np.random.normal(0, 0.1, n_samples)
    gap_severity = np.clip(gap_severity, 0, 1)
    missing_weight = 1 - skill_match * 0.6 - np.random.normal(0, 0.1, n_samples)
    missing_weight = np.clip(missing_weight, 0, 1)
    matched_weight = skill_match * 0.8 + np.random.normal(0, 0.1, n_samples)
    matched_weight = np.clip(matched_weight, 0, 1)
    
    # Generate employability score (target) with realistic formula + noise
    score = (
        skill_match * 35 +
        market_demand * 15 +
        experience * 15 +
        in_demand * 10 +
        diversity * 5 +
        gap_severity * 10 +
        missing_weight * 5 +
        matched_weight * 5 +
        np.random.normal(0, 3, n_samples)  # noise
    )
    score = np.clip(score, 0, 100)
    
    # Generate readiness level based on score
    readiness = np.where(
        score >= 80, "Highly Competitive",
        np.where(score >= 60, "Competitive",
                 np.where(score >= 40, "Developing", "Not Ready"))
    )
    
    # Create DataFrame
    df = pd.DataFrame({
        "skill_match_pct": skill_match,
        "market_demand_score": market_demand,
        "experience_normalized": experience,
        "num_in_demand_normalized": in_demand,
        "skill_diversity": diversity,
        "gap_severity": gap_severity,
        "missing_weight_normalized": missing_weight,
        "matched_weight_normalized": matched_weight,
        "employability_score": score,
        "readiness_level": readiness
    })
    
    # Save to CSV
    csv_path = DATASETS_DIR / "synthetic_employment.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Generated {n_samples} samples → {csv_path}")
    
    return df


def train_models(df=None):
    """
    Train all ML models and save to disk.
    """
    if df is None:
        csv_path = DATASETS_DIR / "synthetic_employment.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
        else:
            print("No dataset found. Generating synthetic data...")
            df = generate_synthetic_data()
    
    feature_cols = [
        "skill_match_pct", "market_demand_score", "experience_normalized",
        "num_in_demand_normalized", "skill_diversity", "gap_severity",
        "missing_weight_normalized", "matched_weight_normalized"
    ]
    
    X = df[feature_cols].values
    y_score = df["employability_score"].values
    y_level = df["readiness_level"].values
    
    # Split data
    X_train, X_test, y_score_train, y_score_test = train_test_split(
        X, y_score, test_size=0.2, random_state=42
    )
    _, _, y_level_train, y_level_test = train_test_split(
        X, y_level, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("\n" + "="*60)
    print("🧠 MODEL TRAINING PIPELINE")
    print("="*60)
    
    # ==========================================
    # 1. Random Forest Classifier (Readiness Level)
    # ==========================================
    print("\n📊 Training Random Forest Classifier...")
    
    rf_params = {
        "n_estimators": [100, 200],
        "max_depth": [10, 15, 20],
        "min_samples_split": [3, 5],
    }
    
    rf = GridSearchCV(
        RandomForestClassifier(random_state=42),
        rf_params,
        cv=5,
        scoring="accuracy",
        n_jobs=-1
    )
    rf.fit(X_train_scaled, y_level_train)
    
    rf_best = rf.best_estimator_
    rf_pred = rf_best.predict(X_test_scaled)
    rf_accuracy = accuracy_score(y_level_test, rf_pred)
    
    print(f"   Best params: {rf.best_params_}")
    print(f"   Accuracy: {rf_accuracy:.4f}")
    print(f"\n   Classification Report:")
    print(classification_report(y_level_test, rf_pred, zero_division=0))
    
    # Cross-validation
    cv_scores = cross_val_score(rf_best, X_train_scaled, y_level_train, cv=5)
    print(f"   CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # Feature importance
    print(f"\n   Feature Importance:")
    for name, imp in sorted(
        zip(feature_cols, rf_best.feature_importances_),
        key=lambda x: x[1], reverse=True
    ):
        print(f"     {name:35s}: {imp:.4f}")
    
    # Save
    joblib.dump(rf_best, MODELS_DIR / "random_forest_classifier.pkl")
    print(f"\n   ✅ Saved → random_forest_classifier.pkl")
    
    # ==========================================
    # 2. XGBoost Regressor (Employability Score)
    # ==========================================
    print("\n📊 Training XGBoost Regressor...")
    
    if HAS_XGBOOST:
        xgb = XGBRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbosity=0
        )
    else:
        xgb = XGBRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42
        )
    
    xgb.fit(X_train_scaled, y_score_train)
    xgb_pred = xgb.predict(X_test_scaled)
    
    mae = mean_absolute_error(y_score_test, xgb_pred)
    r2 = r2_score(y_score_test, xgb_pred)
    
    print(f"   MAE: {mae:.4f}")
    print(f"   R² Score: {r2:.4f}")
    
    # Save
    joblib.dump(xgb, MODELS_DIR / "xgboost_regressor.pkl")
    print(f"   ✅ Saved → xgboost_regressor.pkl")
    
    # ==========================================
    # 3. KNN (Similar Profile Matching)
    # ==========================================
    print("\n📊 Training KNN Model...")
    
    knn = KNeighborsClassifier(
        n_neighbors=7,
        weights="distance",
        metric="euclidean"
    )
    knn.fit(X_train_scaled, y_level_train)
    knn_pred = knn.predict(X_test_scaled)
    knn_accuracy = accuracy_score(y_level_test, knn_pred)
    
    print(f"   Accuracy: {knn_accuracy:.4f}")
    
    # Save
    joblib.dump(knn, MODELS_DIR / "knn_model.pkl")
    print(f"   ✅ Saved → knn_model.pkl")
    
    # ==========================================
    # Save Scaler
    # ==========================================
    joblib.dump(scaler, MODELS_DIR / "feature_scaler.pkl")
    print(f"\n   ✅ Saved → feature_scaler.pkl")
    
    # ==========================================
    # Summary
    # ==========================================
    print("\n" + "="*60)
    print("📋 TRAINING SUMMARY")
    print("="*60)
    print(f"   Random Forest Accuracy:  {rf_accuracy:.4f}")
    print(f"   XGBoost MAE:             {mae:.4f}")
    print(f"   XGBoost R²:              {r2:.4f}")
    print(f"   KNN Accuracy:            {knn_accuracy:.4f}")
    print(f"\n   Models saved to: {MODELS_DIR}")
    print("="*60)
    
    return {
        "rf_accuracy": rf_accuracy,
        "xgb_mae": mae,
        "xgb_r2": r2,
        "knn_accuracy": knn_accuracy
    }


if __name__ == "__main__":
    print("🚀 Starting Model Training Pipeline...")
    df = generate_synthetic_data(n_samples=5000)
    metrics = train_models(df)
