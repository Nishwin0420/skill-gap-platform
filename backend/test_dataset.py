from pathlib import Path
import pandas as pd

DATA_DIR = Path("backend/data").resolve()
real_dataset_path = DATA_DIR / "datasets" / "llm_training_data.csv"

try:
    print(f"Path exists: {real_dataset_path.exists()}")
    df_real = pd.read_csv(real_dataset_path)
    print(f"Loaded {len(df_real)} rows.")
    
    df = pd.DataFrame()
    df["job_id"] = df_real["job_id"]
    df["title"] = df_real["job_title"]
    df["company"] = df_real["company_name"]
    df["region"] = df_real["job_location"]
    df["skills_required"] = df_real["matched_skills"]
    df["salary_estimate"] = df_real["salary_year_avg"].fillna(0)
    df["experience_required"] = 2
    df["posted_date"] = pd.Timestamp.now() - pd.Timedelta(days=30)
    
    print("Mapping successful!")
except Exception as e:
    import traceback
    traceback.print_exc()
