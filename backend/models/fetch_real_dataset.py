"""
Real Dataset Fetcher
=====================
Downloads ~787,000 real-world job postings from HuggingFace Hub.
Source: lukebarousse/data_jobs -- data aggregated from LinkedIn, Glassdoor, Indeed.
NO Kaggle. NO synthetic data.

Filters jobs to those containing skills from our skill_ontology.json (150+ skills).
Outputs: backend/data/datasets/llm_training_data.csv  (~400-600 MB)

Usage:
    python -m backend.models.fetch_real_dataset
"""

import json
import csv
import sys
import time
from pathlib import Path

try:
    from datasets import load_dataset
except ImportError:
    print("ERROR: 'datasets' package not found. Run: pip install datasets")
    sys.exit(1)

# ============================================================
# PATHS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
ONTOLOGY_PATH = BASE_DIR / "data" / "skill_ontology.json"
OUTPUT_DIR = BASE_DIR / "data" / "datasets"
OUTPUT_PATH = OUTPUT_DIR / "llm_training_data.csv"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# STEP 1 -- Load 150+ skills from ontology
# ============================================================
def load_skills_from_ontology():
    """Extract all canonical skill names + synonyms from skill_ontology.json."""
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        ontology = json.load(f)

    skills = {}
    for cat_data in ontology.get("categories", {}).values():
        for key, skill_info in cat_data.get("skills", {}).items():
            canonical = skill_info.get("canonical", key).lower()
            synonyms = [s.lower() for s in skill_info.get("synonyms", [])]
            all_terms = [canonical] + synonyms
            skills[canonical] = {
                "canonical": canonical,
                "terms": all_terms,
                "market_weight": skill_info.get("market_weight", 5),
                "category": skill_info.get("category", "general"),
                "difficulty": skill_info.get("difficulty", "intermediate"),
            }

    print(f"  [OK] Loaded {len(skills)} canonical skills from ontology")
    return skills


# ============================================================
# STEP 2 -- Extract skills present in a text blob
# ============================================================
def extract_skills_from_text(text: str, all_skills: dict) -> list:
    """Fast substring matching of all skill terms in a job description text."""
    if not text:
        return []
    text_lower = text.lower()
    found = []
    for canonical, info in all_skills.items():
        for term in info["terms"]:
            if term in text_lower:
                found.append(canonical)
                break
    return found


# ============================================================
# STEP 3 -- Score a job posting (proxy employability score)
# ============================================================
def compute_proxy_score(matched_skills: list, all_skills: dict) -> float:
    """
    Compute a proxy 'skill demand score' for a job posting.
    Higher score = more high-weight skills required.
    Normalized 0-100.
    """
    if not matched_skills:
        return 0.0
    total_weight = sum(all_skills[s]["market_weight"] for s in matched_skills if s in all_skills)
    max_possible = 10 * len(matched_skills)
    return round((total_weight / max(max_possible, 1)) * 100, 2)


# ============================================================
# MAIN -- Download & Process Dataset
# ============================================================
def main():
    print("=" * 65)
    print("[FETCHER] REAL DATASET FETCHER -- lukebarousse/data_jobs")
    print("   Source: LinkedIn / Glassdoor / Indeed (via HuggingFace)")
    print("   Target: 5-10 Lakhs samples with 150+ skills")
    print("=" * 65)

    # Load ontology skills
    print("\n[Step 1] Loading skill ontology...")
    all_skills = load_skills_from_ontology()
    skill_names = list(all_skills.keys())
    print(f"  Total skills to match: {len(skill_names)}")

    # Download dataset from HuggingFace
    print("\n[Step 2] Downloading real job postings from HuggingFace...")
    print("  Dataset: lukebarousse/data_jobs")
    print("  Source: LinkedIn, Glassdoor, Indeed aggregated job postings")
    print("  This may take 2-10 minutes depending on your internet speed...\n")

    t0 = time.time()
    try:
        ds = load_dataset(
            "lukebarousse/data_jobs",
            split="train",
        )
        elapsed = round(time.time() - t0, 1)
        print(f"  [OK] Downloaded {len(ds):,} job postings in {elapsed}s")
    except Exception as e:
        print(f"  [FAIL] Failed to download dataset: {e}")
        print("  Please check your internet connection and try again.")
        sys.exit(1)

    # Process and filter
    print(f"\n[Step 3] Processing & filtering job postings...")
    print(f"  Matching against {len(all_skills)} skills from ontology...")

    written = 0
    skipped = 0
    min_skills = 3   # Only keep postings with at least 3 matching skills

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "job_id", "job_title", "company_name", "job_location",
            "job_description_text", "matched_skills", "num_skills",
            "skill_categories", "proxy_demand_score", "salary_year_avg",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, row in enumerate(ds):
            if i % 50000 == 0 and i > 0:
                pct = round((i / len(ds)) * 100, 1)
                print(f"  Progress: {i:,} / {len(ds):,} ({pct}%) -- Written: {written:,}")

            text_parts = []
            for field in ["job_title", "job_description", "job_skills"]:
                val = row.get(field, "") or ""
                text_parts.append(str(val))
            full_text = " ".join(text_parts)

            matched = extract_skills_from_text(full_text, all_skills)
            if len(matched) < min_skills:
                skipped += 1
                continue

            categories = list(set(
                all_skills[s]["category"] for s in matched if s in all_skills
            ))

            score = compute_proxy_score(matched, all_skills)
            salary = row.get("salary_year_avg", None)

            writer.writerow({
                "job_id": i,
                "job_title": str(row.get("job_title", "") or "")[:200],
                "company_name": str(row.get("company_name", "") or "")[:200],
                "job_location": str(row.get("job_location", "") or "")[:200],
                "job_description_text": full_text[:2000],
                "matched_skills": "|".join(matched),
                "num_skills": len(matched),
                "skill_categories": "|".join(categories),
                "proxy_demand_score": score,
                "salary_year_avg": salary,
            })
            written += 1

    file_mb = round(OUTPUT_PATH.stat().st_size / (1024 * 1024), 1)
    total_elapsed = round(time.time() - t0, 1)
    print(f"\n{'=' * 65}")
    print("[OK] DATASET GENERATION COMPLETE")
    print(f"{'=' * 65}")
    print(f"  Total input rows:    {len(ds):,}")
    print(f"  Rows written:        {written:,}")
    print(f"  Rows filtered out:   {skipped:,}")
    print(f"  Output file:         {OUTPUT_PATH}")
    print(f"  File size:           {file_mb} MB")
    print(f"  Time taken:          {total_elapsed}s")
    print(f"  Unique skills used:  {len(all_skills)}")
    print(f"{'=' * 65}")
    print("\n>> Next step: Run  python -m backend.models.train_llm")


if __name__ == "__main__":
    main()
