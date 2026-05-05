"""
GitHub Live API Client
========================
Fetches real-time repository and contribution data from the GitHub REST API.
No API key required for public repos (60 req/hr unauthenticated).
Falls back gracefully on any error.
"""

import requests
from typing import Dict, Optional

GITHUB_API = "https://api.github.com"
TIMEOUT = 5  # seconds — never block analysis


def fetch_github_profile(username: str) -> Optional[Dict]:
    """
    Fetch live GitHub profile stats for a given username.

    Returns:
        Dict with repos, languages, contributions, stars — or None on failure.
    """
    if not username or not username.strip():
        return None

    import os
    github_token = os.getenv("GITHUB_TOKEN", "").strip()

    username = username.strip()
    session = requests.Session()
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
        
    session.headers.update(headers)

    try:
        # 1. User profile
        user_resp = session.get(f"{GITHUB_API}/users/{username}", timeout=TIMEOUT)
        if user_resp.status_code != 200:
            return None
        user_data = user_resp.json()

        public_repos = user_data.get("public_repos", 0)
        followers = user_data.get("followers", 0)

        # 2. Repositories (up to 100)
        repos_resp = session.get(
            f"{GITHUB_API}/users/{username}/repos",
            params={"per_page": 100, "sort": "updated"},
            timeout=TIMEOUT
        )
        repos = repos_resp.json() if repos_resp.status_code == 200 else []

        # Aggregate languages and stars
        language_counts: Dict[str, int] = {}
        total_stars = 0
        for repo in repos:
            lang = repo.get("language")
            if lang:
                language_counts[lang] = language_counts.get(lang, 0) + 1
            total_stars += repo.get("stargazers_count", 0)

        # Sort languages by frequency
        top_languages = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)

        # Compute a normalized score (0-100)
        # Formula: weighted combo of repos, stars, followers
        import math
        score = min(100.0, (
            math.log1p(public_repos) * 12 +
            math.log1p(total_stars) * 8 +
            math.log1p(followers) * 5
        ))

        return {
            "platform": "GitHub",
            "username": username,
            "public_repos": public_repos,
            "total_stars": total_stars,
            "followers": followers,
            "top_languages": [{"language": l, "repo_count": c} for l, c in top_languages[:8]],
            "normalized_score": round(score, 1),
            "level": _score_to_level(score),
            "estimated": False,          # ← live data flag
        }

    except Exception:
        return None  # Let caller fall back to estimate


def _score_to_level(score: float) -> str:
    if score >= 80: return "Expert"
    if score >= 60: return "Advanced"
    if score >= 40: return "Intermediate"
    return "Beginner"
