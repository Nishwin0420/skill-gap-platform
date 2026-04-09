"""
Skill Gap Detection Engine
===========================
Identifies missing skills by comparing user profiles with job requirements,
weighted by market demand. Uses K-Means clustering and cosine similarity.

Key Features:
    - Weighted gap analysis (market demand driven)
    - Priority ranking algorithm
    - Skill clustering using K-Means
    - Cosine similarity for skill vector comparison

References:
    - Kumar et al. (2023) — Skill Gap Analysis: A Machine Learning Approach
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from backend.nlp.skill_normalizer import get_normalizer


class SkillGapEngine:
    """
    Advanced Skill Gap Detection Engine with market-demand weighting,
    priority ranking, and skill clustering.
    """

    def __init__(self):
        self.normalizer = get_normalizer()

    def analyze_gap(self, user_skills, job_skills):
        """
        Perform comprehensive skill gap analysis.

        Args:
            user_skills: List of user's skills (normalized)
            job_skills: List of required job skills (normalized)

        Returns:
            Dict with matched, missing, match_percentage, priority ranking
        """
        user_set = set(s.lower() for s in user_skills)
        job_set = set(s.lower() for s in job_skills)

        matched = list(user_set & job_set)
        missing = list(job_set - user_set)
        extra = list(user_set - job_set)

        # Calculate weighted match percentage
        total_weight = sum(
            self.normalizer.get_market_weight(s) for s in job_set
        )
        matched_weight = sum(
            self.normalizer.get_market_weight(s) for s in matched
        )
        match_percentage = (matched_weight / total_weight * 100) if total_weight > 0 else 0

        # Priority-rank missing skills
        priority_ranked = self._rank_missing_skills(missing, job_skills)

        # Skill vector similarity
        vector_similarity = self._compute_skill_vector_similarity(
            user_skills, job_skills
        )

        # Gap severity classification
        gap_severity = self._classify_gap_severity(
            match_percentage, len(missing), len(job_skills)
        )

        # Category-wise gap analysis
        category_gaps = self._analyze_category_gaps(user_skills, job_skills)

        return {
            "matched_skills": sorted(matched),
            "missing_skills": [item["skill"] for item in priority_ranked],
            "extra_skills": sorted(extra),
            "match_percentage": round(match_percentage, 2),
            "vector_similarity": vector_similarity,
            "gap_severity": gap_severity,
            "priority_ranking": priority_ranked,
            "category_analysis": category_gaps,
            "total_required": len(job_set),
            "total_matched": len(matched),
            "total_missing": len(missing)
        }

    def _rank_missing_skills(self, missing_skills, job_skills):
        """
        Rank missing skills by priority using multi-factor scoring:
        1. Market demand weight (40%)
        2. Number of dependent skills it unlocks (30%)
        3. Difficulty level inverse (20%) — easier skills ranked higher
        4. Frequency in job requirements (10%)
        """
        ranked = []

        for skill in missing_skills:
            market_weight = self.normalizer.get_market_weight(skill)
            difficulty = self.normalizer.get_skill_difficulty(skill)
            prereqs = self.normalizer.get_skill_prerequisites(skill)

            # Difficulty scoring (beginner=3, intermediate=2, advanced=1)
            difficulty_scores = {"beginner": 3, "intermediate": 2, "advanced": 1}
            diff_score = difficulty_scores.get(difficulty, 2)

            # Count how many other skills depend on this one
            unlock_count = self._count_dependents(skill)

            # Priority score (higher = learn first)
            priority_score = (
                market_weight * 0.4 +
                unlock_count * 0.3 * 3 +
                diff_score * 0.2 * 3 +
                1.0 * 0.1 * 10  # base frequency
            )

            ranked.append({
                "skill": skill,
                "priority_score": round(priority_score, 2),
                "market_weight": market_weight,
                "difficulty": difficulty,
                "estimated_hours": self.normalizer.get_estimated_hours(skill),
                "category": self.normalizer.get_skill_category(skill),
                "prerequisites": prereqs,
                "unlocks_count": unlock_count
            })

        return sorted(ranked, key=lambda x: x["priority_score"], reverse=True)

    def _count_dependents(self, skill):
        """Count how many skills list this skill as a prerequisite."""
        count = 0
        for canonical in self.normalizer.get_all_canonical_skills():
            prereqs = self.normalizer.get_skill_prerequisites(canonical)
            if skill in prereqs:
                count += 1
        return count

    def _compute_skill_vector_similarity(self, user_skills, job_skills):
        """
        Compute cosine similarity between user skill vector and job requirement vector.
        Each dimension represents a skill from the ontology.
        """
        all_skills = self.normalizer.get_all_canonical_skills()
        if not all_skills:
            return 0.0

        user_vector = np.array([
            1 if skill in user_skills else 0
            for skill in all_skills
        ]).reshape(1, -1)

        job_vector = np.array([
            1 if skill in job_skills else 0
            for skill in all_skills
        ]).reshape(1, -1)

        try:
            similarity = cosine_similarity(user_vector, job_vector)
            return round(float(similarity[0][0]), 4)
        except Exception:
            return 0.0

    def _classify_gap_severity(self, match_percentage, missing_count, total_required):
        """
        Classify overall gap severity.
        """
        if match_percentage >= 80:
            return "Low"
        elif match_percentage >= 60:
            return "Medium"
        elif match_percentage >= 40:
            return "High"
        else:
            return "Critical"

    def _analyze_category_gaps(self, user_skills, job_skills):
        """
        Analyze skill gaps broken down by category.
        """
        categories = {}

        for skill in job_skills:
            category = self.normalizer.get_skill_category(skill)
            if category not in categories:
                categories[category] = {
                    "required": [],
                    "matched": [],
                    "missing": [],
                    "coverage": 0.0
                }
            categories[category]["required"].append(skill)

            if skill in user_skills:
                categories[category]["matched"].append(skill)
            else:
                categories[category]["missing"].append(skill)

        # Calculate coverage per category
        for cat in categories:
            required = len(categories[cat]["required"])
            matched = len(categories[cat]["matched"])
            categories[cat]["coverage"] = round(
                (matched / required * 100) if required > 0 else 0, 1
            )

        return categories

    def cluster_skill_gaps(self, missing_skills, n_clusters=3):
        """
        Cluster missing skills into groups using K-Means
        based on skill category and difficulty.

        Useful for grouping related skills to learn together.
        """
        if len(missing_skills) < n_clusters:
            return [{"cluster": 0, "skills": missing_skills}]

        # Build feature vectors for each missing skill
        category_map = {}
        all_categories = list(set(
            self.normalizer.get_skill_category(s) for s in missing_skills
        ))
        for i, cat in enumerate(all_categories):
            category_map[cat] = i

        difficulty_map = {"beginner": 0, "intermediate": 1, "advanced": 2}

        features = []
        for skill in missing_skills:
            cat = self.normalizer.get_skill_category(skill)
            diff = self.normalizer.get_skill_difficulty(skill)
            weight = self.normalizer.get_market_weight(skill)

            features.append([
                category_map.get(cat, 0),
                difficulty_map.get(diff, 1),
                weight
            ])

        features = np.array(features)

        try:
            n_clusters = min(n_clusters, len(missing_skills))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features)

            clusters = {}
            for i, skill in enumerate(missing_skills):
                label = int(labels[i])
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(skill)

            return [
                {"cluster": k, "skills": v}
                for k, v in sorted(clusters.items())
            ]
        except Exception:
            return [{"cluster": 0, "skills": missing_skills}]


# ====================================
# SINGLETON
# ====================================
_gap_engine = None

def get_gap_engine():
    global _gap_engine
    if _gap_engine is None:
        _gap_engine = SkillGapEngine()
    return _gap_engine
