"""
Skill Decay & Freshness Analyzer
==================================
Models the "half-life" of skills based on how recently they appear
in a resume's experience section.

Algorithm:
  strength = base_strength * (decay_rate ^ years_since_last_use)
  decay_rate = 0.85  (15% strength lost per year of inactivity)

Classifications:
  >= 70  -> Fresh   (active/recent use)
  >= 45  -> Fading  (used 1-3 years ago)
  < 45   -> Decaying (used 4+ years ago or not found in experience)
"""

import re
from datetime import datetime
from typing import List, Dict, Optional


class SkillDecayAnalyzer:
    """
    Analyzes skill freshness based on date extraction from resume
    experience text and a decay half-life model.
    """

    DECAY_RATE = 0.85          # 15% decay per year of inactivity
    FRESH_THRESHOLD = 70       # >= 70 -> Fresh
    FADING_THRESHOLD = 45      # >= 45 -> Fading, else Decaying
    BASE_STRENGTH = 100.0      # Start score when skill is mentioned

    # Regex patterns for year extraction (4-digit years 1990-2029)
    YEAR_PATTERNS = [
        r'\b(20[0-2]\d)\b',            # 2000-2029
        r'\b(199\d)\b',                # 1990-1999
        r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,]+?(20[0-2]\d|199\d)',
        r'(20[0-2]\d|199\d)\s*[-–]\s*(20[0-2]\d|199\d|present|current|now)',
    ]

    def _extract_years_from_text(self, text: str) -> List[int]:
        """Extract all 4-digit years from text."""
        years = []
        text_lower = text.lower()
        for pattern in self.YEAR_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    for m in match:
                        try:
                            y = int(m)
                            if 1990 <= y <= datetime.now().year:
                                years.append(y)
                        except (ValueError, TypeError):
                            pass
                else:
                    try:
                        y = int(match)
                        if 1990 <= y <= datetime.now().year:
                            years.append(y)
                    except (ValueError, TypeError):
                        pass
        return sorted(set(years))

    def _find_last_used_year(self, skill: str, experience_text: str) -> Optional[int]:
        """
        Find the most recent year associated with a skill mention in experience text.
        Looks at the surrounding ±300 chars around each mention.
        """
        if not experience_text:
            return None

        skill_lower = skill.lower()
        text_lower = experience_text.lower()
        best_year = None

        idx = 0
        while True:
            pos = text_lower.find(skill_lower, idx)
            if pos == -1:
                break
            # Extract surrounding window
            window_start = max(0, pos - 300)
            window_end = min(len(text_lower), pos + 300)
            window = experience_text[window_start:window_end]
            local_years = self._extract_years_from_text(window)
            if local_years:
                candidate = max(local_years)
                if best_year is None or candidate > best_year:
                    best_year = candidate
            idx = pos + 1

        return best_year

    def _compute_freshness_score(self, last_used_year: Optional[int]) -> float:
        """Apply half-life decay formula based on years since last use."""
        current_year = datetime.now().year
        if last_used_year is None:
            # Skill not found in experience — assume older
            return round(self.BASE_STRENGTH * (self.DECAY_RATE ** 5), 1)

        years_since = max(0, current_year - last_used_year)
        score = self.BASE_STRENGTH * (self.DECAY_RATE ** years_since)
        return round(score, 1)

    def _classify(self, score: float) -> Dict:
        """Return freshness label, icon and CSS color hint."""
        if score >= self.FRESH_THRESHOLD:
            return {"label": "Fresh", "icon": "🟢", "color": "emerald", "priority": 3}
        elif score >= self.FADING_THRESHOLD:
            return {"label": "Fading", "icon": "🟡", "color": "amber", "priority": 2}
        else:
            return {"label": "Decaying", "icon": "🔴", "color": "red", "priority": 1}

    def analyze(
        self,
        matched_skills: List[str],
        experience_text: str,
        projects_text: str = "",
    ) -> Dict:
        """
        Analyze the freshness of all matched (known) skills.

        Args:
            matched_skills: Skills the user already has (matched with JD)
            experience_text: Parsed resume experience section
            projects_text: Parsed resume projects section (bonus context)

        Returns:
            Dict with per-skill decay data + summary stats
        """
        combined_text = f"{experience_text} {projects_text}"
        skill_results = []

        for skill in matched_skills:
            last_year = self._find_last_used_year(skill, combined_text)
            score = self._compute_freshness_score(last_year)
            classification = self._classify(score)

            skill_results.append({
                "skill": skill,
                "freshness_score": score,
                "last_used_year": last_year,
                "years_since_use": (
                    datetime.now().year - last_year if last_year else "unknown"
                ),
                **classification,
            })

        # Sort: Decaying first (needs attention), then Fading, then Fresh
        skill_results.sort(key=lambda x: x["priority"])

        # Summary stats
        total = len(skill_results)
        fresh_count = sum(1 for s in skill_results if s["label"] == "Fresh")
        fading_count = sum(1 for s in skill_results if s["label"] == "Fading")
        decaying_count = sum(1 for s in skill_results if s["label"] == "Decaying")

        avg_freshness = (
            round(sum(s["freshness_score"] for s in skill_results) / total, 1)
            if total > 0 else 0
        )

        decaying_skills = [s["skill"] for s in skill_results if s["label"] == "Decaying"]
        fading_skills = [s["skill"] for s in skill_results if s["label"] == "Fading"]

        return {
            "skill_freshness": skill_results,
            "summary": {
                "total_skills_analyzed": total,
                "fresh": fresh_count,
                "fading": fading_count,
                "decaying": decaying_count,
                "avg_freshness_score": avg_freshness,
                "decaying_skills": decaying_skills,
                "fading_skills": fading_skills,
                "needs_refresher": decaying_skills + fading_skills,
            },
        }


# ====================================
# SINGLETON
# ====================================
_decay_analyzer = None


def get_decay_analyzer() -> SkillDecayAnalyzer:
    global _decay_analyzer
    if _decay_analyzer is None:
        _decay_analyzer = SkillDecayAnalyzer()
    return _decay_analyzer
