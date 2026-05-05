"""
Markov Chain Career Trajectory Forecaster
==========================================
Uses a stochastic transition matrix (Markov Model) to predict the
next most logical career moves a candidate should make based on
historical skill transitions and current role.

Generates: backend/data/trained_models/career_markov.pkl
"""

import json
import pickle
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "data" / "trained_models" / "career_markov.pkl"

# Simulate transition probabilities between roles
CAREER_GRAPH = {
    "Junior Developer": {
        "Software Engineer": 0.60,
        "Frontend Developer": 0.20,
        "Backend Developer": 0.15,
        "Data Analyst": 0.05
    },
    "Software Engineer": {
        "Senior Software Engineer": 0.50,
        "Lead Developer": 0.20,
        "DevOps Engineer": 0.15,
        "Cloud Architect": 0.15
    },
    "Frontend Developer": {
        "Senior Frontend Developer": 0.60,
        "Full Stack Developer": 0.30,
        "UI/UX Designer": 0.10
    },
    "Backend Developer": {
        "Senior Backend Developer": 0.50,
        "Full Stack Developer": 0.30,
        "Data Engineer": 0.20
    },
    "Data Analyst": {
        "Data Scientist": 0.50,
        "Data Engineer": 0.30,
        "Machine Learning Engineer": 0.20
    },
    "Data Scientist": {
        "Senior Data Scientist": 0.60,
        "Machine Learning Engineer": 0.30,
        "AI Architect": 0.10
    },
    "Machine Learning Engineer": {
        "Senior ML Engineer": 0.50,
        "AI Architect": 0.40,
        "Data Engineering Lead": 0.10
    },
    "Senior Software Engineer": {
        "Lead Developer": 0.40,
        "Software Architect": 0.40,
        "Engineering Manager": 0.20
    },
    "Full Stack Developer": {
        "Senior Full Stack Developer": 0.60,
        "Lead Developer": 0.20,
        "Software Architect": 0.20
    }
}

class CareerMarkovModel:
    def __init__(self, transition_dict):
        self.transitions = transition_dict
        
    def predict_next_roles(self, current_role, top_n=3):
        if not current_role:
            return []
            
        # Try to find an exact or partial match
        match = None
        for role in self.transitions.keys():
            if role.lower() in current_role.lower() or current_role.lower() in role.lower():
                match = role
                break
                
        if not match:
            # Fallback default recommendations
            return [
                {"role": "Senior " + current_role, "probability": 0.60},
                {"role": "Lead " + current_role, "probability": 0.30}
            ]
            
        options = self.transitions[match]
        # Sort by probability descending
        sorted_opts = sorted(options.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for role, prob in sorted_opts[:top_n]:
            results.append({"role": role, "probability": prob})
            
        return results

def build_model():
    print("=" * 50)
    print("[MARKOV] Building Career Forecaster")
    print("=" * 50)
    
    model = CareerMarkovModel(CAREER_GRAPH)
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
        
    print(f"[OK] Markov Model saved to: {MODEL_PATH}")

def get_career_predictions(current_role):
    if not MODEL_PATH.exists():
        return []
        
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
        
    return model.predict_next_roles(current_role)

if __name__ == "__main__":
    build_model()
