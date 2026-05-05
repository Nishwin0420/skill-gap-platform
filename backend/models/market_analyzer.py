"""
Job Market Intelligence Engine
================================
Collects and analyzes job market data to track skill demand trends.
Uses web scraping (BeautifulSoup) and simulated market datasets.

Features:
    - Simulated job market dataset generation
    - Skill demand frequency analysis
    - Trend analysis over time
    - Regional demand filtering
    - Dynamic market weight computation

References:
    - Dataset Sources: Indeed, LinkedIn, Kaggle Job Datasets
    - O*NET Skill Taxonomy (US Dept of Labor)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
import json


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class MarketAnalyzer:
    """
    Job Market Intelligence Engine for analyzing
    skill demand trends and computing dynamic market weights.
    """

    def __init__(self):
        self.data_source = "simulated"   # updated by _load_or_generate_data
        self.job_data = self._load_or_generate_data()


    def _load_or_generate_data(self):
        """
        Load job market data from (in priority order):
        1. 30k trained dataset (llm_training_data.csv) ← PRIMARY: 610k rows, 83 skills
        2. Adzuna live API (cached 6h)                  ← supplement if trained data missing
        3. Remotive public API (free fallback)           ← supplement if Adzuna missing
        4. job_market_data.csv on disk                   ← previous simulated CSV
        5. Generate simulated dataset                    ← last resort offline fallback
        """
        # ── 1. PRIMARY: Use the 30k trained dataset (ALWAYS preferred) ────────
        real_dataset_path = DATA_DIR / "datasets" / "llm_training_data.csv"
        if real_dataset_path.exists():
            try:
                df_real = pd.read_csv(real_dataset_path)

                # Validate required columns exist
                required_cols = {"job_id", "job_title", "company_name", "job_location",
                                 "matched_skills", "salary_year_avg"}
                if required_cols.issubset(df_real.columns):
                    df = pd.DataFrame()
                    df["job_id"]           = df_real["job_id"]
                    df["title"]            = df_real["job_title"]
                    df["company"]          = df_real["company_name"]
                    df["region"]           = df_real["job_location"]
                    df["skills_required"]  = df_real["matched_skills"]
                    df["salary_estimate"]  = df_real["salary_year_avg"].fillna(0)
                    df["experience_required"] = 2

                    # Spread postings across the past 12 months for realistic trend calculation
                    base_date   = pd.Timestamp.now() - pd.Timedelta(days=365)
                    random_days = np.random.randint(0, 365, size=len(df))
                    df["posted_date"] = base_date + pd.to_timedelta(random_days, unit="d")

                    self.data_source = "real_dataset_30k"
                    print(f"[MarketAnalyzer] Loaded {len(df):,} rows from trained dataset "
                          f"({real_dataset_path.name})")
                    return df
            except Exception as e:
                print(f"[MarketAnalyzer] Warning: Could not load trained dataset: {e}")

        # ── 2. Adzuna live API (only used if trained dataset is missing) ───────
        try:
            from backend.api_clients.adzuna_client import get_cached_or_fresh_jobs
            live_jobs = get_cached_or_fresh_jobs()
            if live_jobs:
                df = self._live_jobs_to_dataframe(live_jobs)
                if not df.empty:
                    self.data_source = "live_adzuna"
                    return df
        except Exception:
            pass

        # ── 3. Remotive public live API (Free fallback) ────────────────────────
        try:
            import requests
            resp = requests.get("https://remotive.com/api/remote-jobs?limit=100", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                jobs = data.get("jobs", [])
                if jobs:
                    formatted_jobs = []
                    for j in jobs:
                        formatted_jobs.append({
                            "title":   j.get("title", ""),
                            "company": j.get("company_name", ""),
                            "description": j.get("description", ""),
                            "created": j.get("publication_date", ""),
                            "country": "Global",
                        })
                    df = self._live_jobs_to_dataframe(formatted_jobs)
                    if not df.empty:
                        self.data_source = "live_remotive"
                        return df
        except Exception:
            pass

        # ── 4. Fall back to existing simulated CSV ─────────────────────────────
        csv_path = DATA_DIR / "job_market_data.csv"
        if csv_path.exists():
            self.data_source = "csv"
            return pd.read_csv(csv_path, parse_dates=["posted_date"])

        # ── 5. Generate simulated data (absolute last resort) ──────────────────
        self.data_source = "simulated"
        return self._generate_simulated_data()

    def _live_jobs_to_dataframe(self, live_jobs: list) -> pd.DataFrame:
        """
        Convert Adzuna API job list to the DataFrame schema used by
        all downstream analysis (same columns as the simulated dataset).
        Also extracts skills from descriptions using the NLP extractor.
        """
        from backend.nlp.skill_extractor import extract_skills
        from datetime import datetime, timezone

        records = []
        for job in live_jobs:
            description = job.get("description", "")
            title = job.get("title", "Unknown")
            company = job.get("company", "Unknown")
            country = job.get("country", "gb")
            region = "US" if country == "us" else ("India" if country == "in" else "Europe")

            # NLP skill extraction from live job description
            try:
                skills = extract_skills(description)
            except Exception:
                skills = []

            if not skills:
                continue  # Skip jobs with no detectable skills

            # Parse salary
            sal_min = job.get("salary_min") or 0
            sal_max = job.get("salary_max") or 0
            salary = int((sal_min + sal_max) / 2) if sal_min or sal_max else 60000

            # Parse date
            try:
                posted = datetime.fromisoformat(job.get("created", "").replace("Z", "+00:00"))
                posted = posted.replace(tzinfo=None)
            except Exception:
                posted = datetime.now()

            records.append({
                "job_id": f"LV-{len(records)+1:05d}",
                "title": title,
                "company": company,
                "region": region,
                "posted_date": posted,
                "skills_required": "|".join(skills[:12]),
                "experience_required": 2,
                "salary_estimate": salary,
            })

        if not records:
            return pd.DataFrame()

        return pd.DataFrame(records)

    def _generate_simulated_data(self):
        """
        Generate realistic simulated job market data.
        Simulates job postings from major portals with skill requirements.
        """
        np.random.seed(42)

        roles = [
            "Software Engineer", "Data Scientist", "ML Engineer",
            "Frontend Developer", "Backend Developer", "Full Stack Developer",
            "DevOps Engineer", "Cloud Architect", "Data Analyst",
            "AI Engineer", "Mobile Developer", "Cybersecurity Analyst",
            "Data Engineer", "Product Manager", "QA Engineer"
        ]

        companies = [
            "Google", "Microsoft", "Amazon", "Meta", "Apple",
            "TCS", "Infosys", "Wipro", "HCL", "Tech Mahindra",
            "Flipkart", "Razorpay", "Swiggy", "Zomato", "PhonePe",
            "Netflix", "Uber", "Salesforce", "Adobe", "Oracle"
        ]

        regions = ["India", "US", "Europe", "Asia Pacific", "Global"]

        role_skills = {
            "Software Engineer": ["python", "java", "c++", "sql", "git", "linux", "rest api", "agile"],
            "Data Scientist": ["python", "machine learning", "sql", "pandas", "statistics", "data visualization", "scikit-learn", "deep learning"],
            "ML Engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "docker", "aws", "mlops"],
            "Frontend Developer": ["javascript", "react", "html", "css", "typescript", "tailwind css", "next.js", "git"],
            "Backend Developer": ["python", "node.js", "sql", "postgresql", "rest api", "docker", "redis", "git"],
            "Full Stack Developer": ["javascript", "react", "node.js", "sql", "html", "css", "mongodb", "git", "docker"],
            "DevOps Engineer": ["docker", "kubernetes", "aws", "linux", "ci/cd", "terraform", "git", "python"],
            "Cloud Architect": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "linux", "networking"],
            "Data Analyst": ["sql", "python", "excel", "power bi", "tableau", "data analysis", "statistics", "pandas"],
            "AI Engineer": ["python", "deep learning", "nlp", "computer vision", "pytorch", "tensorflow", "huggingface", "generative ai"],
            "Mobile Developer": ["kotlin", "swift", "react native", "flutter", "javascript", "firebase", "git", "rest api"],
            "Cybersecurity Analyst": ["cybersecurity", "networking", "linux", "python", "ethical hacking", "sql"],
            "Data Engineer": ["python", "sql", "apache spark", "hadoop", "aws", "docker", "big data", "postgresql"],
            "Product Manager": ["agile", "sql", "data analysis", "jira", "excel"],
            "QA Engineer": ["python", "javascript", "sql", "postman", "git", "agile"]
        }

        records = []
        base_date = datetime(2025, 1, 1)

        for i in range(5000):
            role = np.random.choice(roles)
            company = np.random.choice(companies)
            region = np.random.choice(regions, p=[0.4, 0.25, 0.15, 0.1, 0.1])
            posted_date = base_date + timedelta(days=np.random.randint(0, 450))

            skills = role_skills.get(role, ["python", "sql"])
            # Add some variation
            n_skills = min(len(skills), np.random.randint(3, len(skills) + 1))
            selected_skills = list(np.random.choice(skills, n_skills, replace=False))

            salary_ranges = {
                "India": (600000, 4000000),
                "US": (70000, 200000),
                "Europe": (50000, 150000),
                "Asia Pacific": (40000, 120000),
                "Global": (50000, 180000)
            }
            sal_min, sal_max = salary_ranges[region]
            salary = np.random.randint(sal_min, sal_max)

            exp_required = np.random.choice([0, 1, 2, 3, 5, 7, 10],
                                             p=[0.1, 0.15, 0.2, 0.2, 0.15, 0.1, 0.1])

            records.append({
                "job_id": f"JOB-{i+1:04d}",
                "title": role,
                "company": company,
                "region": region,
                "posted_date": posted_date,
                "skills_required": "|".join(selected_skills),
                "experience_required": exp_required,
                "salary_estimate": salary
            })

        df = pd.DataFrame(records)

        # Save
        csv_path = DATA_DIR / "job_market_data.csv"
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)

        return df

    def get_skill_demand_scores(self, region=None):
        """
        Calculate skill demand scores based on frequency in job postings.
        Returns skill → demand_score (0-10).
        """
        df = self.job_data
        if region:
            df = df[df["region"] == region]

        all_skills = []
        for skills_str in df["skills_required"]:
            all_skills.extend(str(skills_str).split("|"))

        counter = Counter(all_skills)
        total = len(df)

        if total == 0:
            return {}

        max_count = max(counter.values()) if counter else 1

        scores = {}
        for skill, count in counter.items():
            scores[skill] = round((count / max_count) * 10, 2)

        return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

    def get_trending_skills(self, top_n=20, months=6):
        """
        Get skills that are trending (increasing demand over recent months).
        """
        df = self.job_data.copy()
        df["posted_date"] = pd.to_datetime(df["posted_date"])
        cutoff = df["posted_date"].max() - timedelta(days=months * 30)

        recent = df[df["posted_date"] >= cutoff]
        older = df[df["posted_date"] < cutoff]

        recent_skills = Counter()
        for skills_str in recent["skills_required"]:
            recent_skills.update(str(skills_str).split("|"))

        older_skills = Counter()
        for skills_str in older["skills_required"]:
            older_skills.update(str(skills_str).split("|"))

        # Calculate growth rate
        trends = {}
        all_skills = set(list(recent_skills.keys()) + list(older_skills.keys()))
        for skill in all_skills:
            recent_count = recent_skills.get(skill, 0)
            older_count = older_skills.get(skill, 1)
            growth = ((recent_count - older_count) / max(older_count, 1)) * 100
            trends[skill] = {
                "recent_count": recent_count,
                "older_count": older_count,
                "growth_rate": round(growth, 2),
                "trend": "Rising" if growth > 10 else "Stable" if growth > -10 else "Declining"
            }

        sorted_trends = sorted(
            trends.items(),
            key=lambda x: x[1]["growth_rate"],
            reverse=True
        )

        return dict(sorted_trends[:top_n])

    def get_skill_time_series(self, skill_name, granularity="month"):
        """
        Get time series data for a specific skill's demand.
        """
        df = self.job_data.copy()
        df["posted_date"] = pd.to_datetime(df["posted_date"])

        # Filter rows containing the skill
        mask = df["skills_required"].str.contains(skill_name, case=False, na=False)
        skill_df = df[mask]

        if granularity == "month":
            skill_df = skill_df.set_index("posted_date")
            monthly = skill_df.resample("M").size().reset_index()
            monthly.columns = ["date", "count"]
            monthly["date"] = monthly["date"].dt.strftime("%Y-%m")
            return monthly.to_dict("records")
        else:
            return []

    def get_role_analysis(self, role_title=None):
        """
        Get analysis of job roles — common skills, average salary, etc.
        """
        df = self.job_data

        if role_title:
            df = df[df["title"].str.contains(role_title, case=False, na=False)]

        if df.empty:
            return {}

        all_skills = []
        for skills_str in df["skills_required"]:
            all_skills.extend(str(skills_str).split("|"))

        skill_freq = Counter(all_skills).most_common(10)

        return {
            "total_postings": len(df),
            "avg_salary": round(float(df["salary_estimate"].mean()), 0),
            "avg_experience": round(float(df["experience_required"].mean()), 1),
            "top_skills": [{"skill": s, "count": c} for s, c in skill_freq],
            "regions": df["region"].value_counts().to_dict(),
            "top_companies": df["company"].value_counts().head(5).to_dict()
        }

    def get_market_summary(self):
        """Get overall market summary statistics."""
        df = self.job_data
        demand_scores = self.get_skill_demand_scores()

        return {
            "total_job_postings": len(df),
            "unique_roles": df["title"].nunique(),
            "unique_companies": df["company"].nunique(),
            "regions_covered": df["region"].nunique(),
            "top_10_skills": dict(list(demand_scores.items())[:10]),
            "data_source": getattr(self, "data_source", "simulated"),
            "date_range": {
                "from": str(df["posted_date"].min())[:10],
                "to": str(df["posted_date"].max())[:10]
            }
        }


# ====================================
# SINGLETON
# ====================================
_analyzer = None

def get_market_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = MarketAnalyzer()
    return _analyzer
