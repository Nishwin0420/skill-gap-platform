"""
Skill Normalizer Module
=======================
Converts messy user skill inputs into standardized skill data using
O*NET + ESCO ontology and synonym mapping with TF-IDF fuzzy matching.

References:
    - Ahmed et al. (2023) — NLP for Skill Extraction from Job Descriptions
    - O*NET (US Dept of Labor) Skill Taxonomy
    - ESCO European Skills Framework
"""

import json
import os
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ====================================
# LOAD ONTOLOGY DATA
# ====================================
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ONTOLOGY_PATH = DATA_DIR / "skill_ontology.json"


class SkillNormalizer:
    """
    Normalizes messy skill names into canonical forms using:
    1. Direct synonym lookup (O*NET + ESCO mapping)
    2. TF-IDF + Cosine Similarity fuzzy matching
    3. Category-aware normalization
    """

    def __init__(self):
        self.ontology = self._load_ontology()
        self.synonym_map = self._build_synonym_map()
        self.all_skills = list(self.synonym_map.values())
        self.skill_details = self._build_skill_details()
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self._build_tfidf_index()

    def _load_ontology(self):
        """Load skill ontology from JSON file."""
        if ONTOLOGY_PATH.exists():
            with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"categories": {}}

    def _build_synonym_map(self):
        """
        Build a flat synonym → canonical skill mapping.
        Example: {"js": "javascript", "py": "python", "ml": "machine learning"}
        """
        synonym_map = {}
        for category_data in self.ontology.get("categories", {}).values():
            for skill_key, skill_info in category_data.get("skills", {}).items():
                canonical = skill_info.get("canonical", skill_key)
                # Map the canonical name to itself
                synonym_map[canonical.lower()] = canonical
                # Map all synonyms to the canonical name
                for syn in skill_info.get("synonyms", []):
                    synonym_map[syn.lower()] = canonical
        return synonym_map

    def _build_skill_details(self):
        """Build a flat dictionary of canonical_skill → full details."""
        details = {}
        for category_data in self.ontology.get("categories", {}).values():
            for skill_key, skill_info in category_data.get("skills", {}).items():
                canonical = skill_info.get("canonical", skill_key)
                details[canonical] = skill_info
        return details

    def _build_tfidf_index(self):
        """Build TF-IDF index for fuzzy skill matching."""
        all_terms = list(self.synonym_map.keys())
        if all_terms:
            self.tfidf_vectorizer = TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(2, 4),
                max_features=10000
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_terms)

    def normalize_skill(self, raw_skill):
        """
        Normalize a single skill name to its canonical form.

        Args:
            raw_skill: Raw skill string (e.g., "ML", "react.js", "sci-kit learn")

        Returns:
            dict with canonical name, confidence, and method used
        """
        cleaned = raw_skill.lower().strip()

        # Step 1: Direct synonym lookup
        if cleaned in self.synonym_map:
            return {
                "original": raw_skill,
                "canonical": self.synonym_map[cleaned],
                "confidence": 1.0,
                "method": "synonym_lookup"
            }

        # Step 2: TF-IDF fuzzy matching
        if self.tfidf_vectorizer and self.tfidf_matrix is not None:
            query_vec = self.tfidf_vectorizer.transform([cleaned])
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]

            if best_score > 0.5:
                matched_term = list(self.synonym_map.keys())[best_idx]
                return {
                    "original": raw_skill,
                    "canonical": self.synonym_map[matched_term],
                    "confidence": round(float(best_score), 3),
                    "method": "tfidf_fuzzy_match"
                }

        # Step 3: No match found
        return {
            "original": raw_skill,
            "canonical": cleaned,
            "confidence": 0.0,
            "method": "unmatched"
        }

    def normalize_skills(self, raw_skills):
        """
        Normalize a list of raw skill strings.

        Args:
            raw_skills: List of raw skill strings

        Returns:
            List of normalized skill dicts
        """
        results = []
        seen_canonical = set()

        for skill in raw_skills:
            normalized = self.normalize_skill(skill)
            canonical = normalized["canonical"]
            if canonical not in seen_canonical:
                seen_canonical.add(canonical)
                results.append(normalized)

        return results

    def get_skill_info(self, canonical_skill):
        """Get full ontology details for a canonical skill name."""
        return self.skill_details.get(canonical_skill, None)

    def get_skill_category(self, canonical_skill):
        """Get the category of a skill."""
        info = self.get_skill_info(canonical_skill)
        if info:
            return info.get("category", "unknown")
        return "unknown"

    def get_skill_difficulty(self, canonical_skill):
        """Get the difficulty level of a skill."""
        info = self.get_skill_info(canonical_skill)
        if info:
            return info.get("difficulty", "intermediate")
        return "intermediate"

    def get_skill_prerequisites(self, canonical_skill):
        """Get prerequisites for a skill."""
        info = self.get_skill_info(canonical_skill)
        if info:
            return info.get("prerequisites", [])
        return []

    def get_market_weight(self, canonical_skill):
        """Get market demand weight for a skill (0-10)."""
        info = self.get_skill_info(canonical_skill)
        if info:
            return info.get("market_weight", 5)
        return 5

    def get_estimated_hours(self, canonical_skill):
        """Get estimated learning hours for a skill."""
        info = self.get_skill_info(canonical_skill)
        if info:
            return info.get("estimated_hours", 40)
        return 40

    def get_all_canonical_skills(self):
        """Get list of all canonical skill names."""
        return list(self.skill_details.keys())

    def get_skills_by_category(self, category):
        """Get all skills in a category."""
        cat_data = self.ontology.get("categories", {}).get(category, {})
        skills = []
        for skill_info in cat_data.get("skills", {}).values():
            skills.append(skill_info.get("canonical"))
        return skills

    def calculate_skill_diversity(self, skills):
        """
        Calculate how diverse a skill set is across categories.
        Returns a score 0-1 where 1 = skills across all categories.
        """
        if not skills:
            return 0.0

        categories = set()
        for skill in skills:
            cat = self.get_skill_category(skill)
            if cat != "unknown":
                categories.add(cat)

        total_categories = len(self.ontology.get("categories", {}))
        if total_categories == 0:
            return 0.0

        return round(len(categories) / total_categories, 3)


# ====================================
# SINGLETON INSTANCE
# ====================================
_normalizer_instance = None


def get_normalizer():
    """Get or create singleton normalizer instance."""
    global _normalizer_instance
    if _normalizer_instance is None:
        _normalizer_instance = SkillNormalizer()
    return _normalizer_instance


# ====================================
# TEST
# ====================================
if __name__ == "__main__":
    normalizer = get_normalizer()

    test_skills = ["ML", "react.js", "sci-kit learn", "js", "python3", "k8s", "AWS"]
    print("\n=== Skill Normalization Test ===")
    for skill in test_skills:
        result = normalizer.normalize_skill(skill)
        print(f"  {result['original']:15s} → {result['canonical']:20s} "
              f"(confidence: {result['confidence']:.2f}, method: {result['method']})")
