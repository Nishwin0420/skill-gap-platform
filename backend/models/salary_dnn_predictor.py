"""
PyTorch Deep Neural Network (DNN) Predictor
============================================
A Multi-Layer Perceptron (MLP) built in PyTorch to predict
candidate Salary Potential based on non-linear skill and market features.

Generates: backend/data/trained_models/salary_dnn.pt
"""

import json
import numpy as np
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "data" / "trained_models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODELS_DIR / "salary_dnn.pt"
SCALER_PATH = MODELS_DIR / "salary_scaler.pkl"

# ==========================================
# 1. DNN Architecture
# ==========================================
class SalaryDNN(nn.Module):
    def __init__(self, input_dim):
        super(SalaryDNN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(64, 32),
            nn.ReLU(),
            
            nn.Linear(32, 1)  # Output: Predicted Salary
        )

    def forward(self, x):
        return self.network(x)

# ==========================================
# 2. Training Script
# ==========================================
def train_dnn():
    print("=" * 50)
    print("[DNN] PyTorch Salary Predictor Training")
    print("=" * 50)
    
    # Features: [Skill Match %, Market Demand Score, Experience Level, In-Demand Skills Count, Skill Diversity, Gap Severity, Employability Score]
    # We will simulate 10,000 synthetic data points based on typical market dynamics
    num_samples = 10000
    input_dim = 7
    
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Generate Synthetic Features
    match_pct = np.random.uniform(10, 100, num_samples)
    demand_score = np.random.uniform(20, 100, num_samples)
    exp_years = np.random.uniform(0, 15, num_samples)
    skill_count = np.random.randint(2, 25, num_samples)
    diversity = np.random.uniform(1, 5, num_samples)
    gap_severity = np.random.uniform(0, 1, num_samples)
    employability = (match_pct * 0.4) + (demand_score * 0.3) + (exp_years * 5)
    
    X = np.column_stack((match_pct, demand_score, exp_years, skill_count, diversity, gap_severity, employability))
    
    # Generate Synthetic Target (Salary in USD)
    # Base: 50k + (Exp * 5k) + (Demand * 300) + (Match * 200) + Non-linear synergy
    base_salary = 50000 + (exp_years * 5000) + (demand_score * 300) + (match_pct * 200)
    synergy_bonus = (exp_years * demand_score * 5)  # Non-linear feature
    Y = base_salary + synergy_bonus + np.random.normal(0, 5000, num_samples)
    
    # Scale Data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Convert to PyTorch Tensors
    X_tensor = torch.FloatTensor(X_scaled)
    Y_tensor = torch.FloatTensor(Y).view(-1, 1)
    
    # Model Setup
    model = SalaryDNN(input_dim=input_dim)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-5)
    
    # Training Loop
    epochs = 300
    print("Training Progress:")
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        predictions = model(X_tensor)
        loss = criterion(predictions, Y_tensor)
        
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 50 == 0:
            print(f"  Epoch [{epoch+1}/{epochs}] | MSE Loss: {loss.item():,.2f}")
    
    # Save Model & Scaler
    torch.save(model.state_dict(), MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"\n[OK] DNN weights saved to: {MODEL_PATH}")
    print(f"[OK] Scaler saved to: {SCALER_PATH}")

# ==========================================
# 3. Inference Wrapper
# ==========================================
def predict_salary(features_array):
    """
    Args:
        features_array: list of 7 floats corresponding to the input features.
    Returns:
        float: Predicted salary
    """
    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        return None
        
    scaler = joblib.load(SCALER_PATH)
    model = SalaryDNN(input_dim=7)
    model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
    model.eval()
    
    X_scaled = scaler.transform(np.array(features_array).reshape(1, -1))
    X_tensor = torch.FloatTensor(X_scaled)
    
    with torch.no_grad():
        pred = model(X_tensor)
        
    return float(pred.item())

if __name__ == "__main__":
    train_dnn()
