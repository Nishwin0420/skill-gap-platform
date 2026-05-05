"""
LeetCode Live API Client
==========================
Fetches real-time LeetCode stats using the unofficial public GraphQL endpoint.
No API key required — uses the same endpoint as the LeetCode website.
Falls back gracefully on any error or rate limit.
"""

import requests
from typing import Dict, Optional

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"
TIMEOUT = 6  # seconds


def fetch_leetcode_profile(username: str) -> Optional[Dict]:
    """
    Fetch live LeetCode stats for a given username.

    Returns:
        Dict with problems solved breakdown and rating — or None on failure.
    """
    if not username or not username.strip():
        return None

    username = username.strip()

    query = """
    query userPublicProfile($username: String!) {
      matchedUser(username: $username) {
        username
        submitStats: submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
            submissions
          }
        }
        profile {
          ranking
          reputation
          starRating
        }
      }
    }
    """

    try:
        response = requests.post(
            LEETCODE_GRAPHQL,
            json={"query": query, "variables": {"username": username}},
            headers={
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com",
                "User-Agent": "Mozilla/5.0",
            },
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            return None

        data = response.json()
        user = data.get("data", {}).get("matchedUser")
        if not user:
            return None  # User not found

        # Parse submission stats
        stats = {
            item["difficulty"]: item["count"]
            for item in user.get("submitStats", {}).get("acSubmissionNum", [])
        }

        easy = stats.get("Easy", 0)
        medium = stats.get("Medium", 0)
        hard = stats.get("Hard", 0)
        total = easy + medium + hard

        # Weighted score: Hard = 3x, Medium = 2x, Easy = 1x
        weighted = easy + medium * 2 + hard * 3
        # Max realistic: 600 easy + 400 medium*2 + 200 hard*3 = ~2000
        score = min(100.0, (weighted / 1800) * 100)

        profile = user.get("profile", {})

        return {
            "platform": "LeetCode",
            "username": username,
            "problems_solved": total,
            "easy": easy,
            "medium": medium,
            "hard": hard,
            "ranking": profile.get("ranking", 0),
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
