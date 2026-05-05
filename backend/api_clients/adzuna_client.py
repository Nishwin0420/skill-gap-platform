"""
Adzuna Live Job Market API Client
====================================
Fetches live job postings from Adzuna API and caches results for 6 hours.
Requires ADZUNA_APP_ID and ADZUNA_APP_KEY environment variables.

Free tier: 500 calls/day
Cache: 6-hour TTL to avoid burning quota on every page load.
Fallback: Returns None if keys missing or API fails.
"""

import os
import json
import time
import requests
from typing import Optional, Dict, List
from pathlib import Path

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"
CACHE_FILE = Path(__file__).resolve().parent.parent / "data" / "live_market_cache.json"
CACHE_TTL_SECONDS = 6 * 3600  # 6 hours
TIMEOUT = 8  # seconds


# Target roles and countries to fetch
FETCH_ROLES = [
    "data scientist", "machine learning engineer", "software engineer",
    "full stack developer", "devops engineer", "data analyst",
    "backend developer", "frontend developer", "ai engineer"
]

FETCH_COUNTRIES = ["gb", "us"]  # UK + US — both supported on free tier


def _is_cache_valid() -> bool:
    """Check if cached data is still fresh (< 6 hours old)."""
    if not CACHE_FILE.exists():
        return False
    age = time.time() - CACHE_FILE.stat().st_mtime
    return age < CACHE_TTL_SECONDS


def _load_cache() -> Optional[Dict]:
    """Load cached market data."""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _save_cache(data: Dict) -> None:
    """Persist market data to cache file."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass


def fetch_live_jobs(max_per_role: int = 20) -> Optional[List[Dict]]:
    """
    Fetch live job postings from Adzuna API.

    Returns:
        List of job dicts (title, company, location, description, salary) or None.
    """
    app_id = os.getenv("ADZUNA_APP_ID", "").strip()
    app_key = os.getenv("ADZUNA_APP_KEY", "").strip()

    if not app_key:
        return None  # No credentials → caller uses simulated data

    all_jobs: List[Dict] = []

    for country in FETCH_COUNTRIES:
        for role in FETCH_ROLES:
            try:
                url = f"{ADZUNA_BASE}/{country}/search/1"
                params = {
                    "app_id": app_id,
                    "app_key": app_key,
                    "results_per_page": max_per_role,
                    "what": role,
                    "content-type": "application/json",
                }
                resp = requests.get(url, params=params, timeout=TIMEOUT)
                if resp.status_code != 200:
                    continue

                data = resp.json()
                for job in data.get("results", []):
                    all_jobs.append({
                        "title": job.get("title", ""),
                        "company": job.get("company", {}).get("display_name", ""),
                        "location": job.get("location", {}).get("display_name", ""),
                        "description": job.get("description", ""),
                        "salary_min": job.get("salary_min"),
                        "salary_max": job.get("salary_max"),
                        "category": job.get("category", {}).get("label", ""),
                        "created": job.get("created", ""),
                        "country": country,
                        "search_role": role,
                    })

            except Exception:
                continue  # Skip failed role — partial data is fine

    if not all_jobs:
        return None

    return all_jobs


def get_cached_or_fresh_jobs() -> Optional[List[Dict]]:
    """
    Return cached live jobs if fresh, else fetch new data.
    If Adzuna credentials are missing, returns None immediately.
    """
    app_key = os.getenv("ADZUNA_APP_KEY", "").strip()
    if not app_key:
        return None

    # Return cache if valid
    if _is_cache_valid():
        cached = _load_cache()
        if cached and isinstance(cached, list):
            return cached

    # Fetch fresh data
    fresh = fetch_live_jobs()
    if fresh:
        _save_cache(fresh)
    return fresh
