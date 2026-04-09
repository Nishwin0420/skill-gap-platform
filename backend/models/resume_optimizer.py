"""
Resume ATS Optimizer
=====================
Analyzes matched skills that are poorly highlighted in the resume
and generates targeted bullet-point rewrite suggestions to improve
ATS (Applicant Tracking System) pass rates.

Strategy:
  1. For each matched skill, count keyword occurrences in experience/projects
  2. Skills mentioned < 2 times are considered "under-highlighted"
  3. Generate 2-3 rewrite templates using JD context + TF-IDF keyword extraction
  4. Score ATS impact (how much the rewrite improves keyword density)

No external LLM API needed — fully offline NLP-based generation.
"""

import re
from typing import List, Dict, Optional
from collections import Counter


class ResumeOptimizer:
    """
    Generates targeted ATS bullet-point rewrite suggestions based on
    skill keyword analysis in resume vs. job description.
    """

    # Bullet-point action verb banks per skill category
    ACTION_VERBS = {
        "programming_languages": ["Developed", "Built", "Engineered", "Implemented", "Architected"],
        "machine_learning_ai":   ["Trained", "Optimized", "Deployed", "Fine-tuned", "Evaluated"],
        "data_science":          ["Analyzed", "Modeled", "Visualized", "Processed", "Extracted"],
        "databases":             ["Designed", "Optimized", "Migrated", "Maintained", "Queried"],
        "cloud_devops":          ["Deployed", "Automated", "Configured", "Orchestrated", "Provisioned"],
        "web_development":       ["Developed", "Designed", "Integrated", "Launched", "Optimized"],
        "tools_frameworks":      ["Utilized", "Integrated", "Configured", "Leveraged", "Implemented"],
        "default":               ["Applied", "Utilized", "Implemented", "Leveraged", "Developed"],
    }

    # Context templates: {verb} {skill} to {outcome}
    TEMPLATE_PATTERNS = [
        "{verb} {skill} to {outcome}, improving {metric} by {improvement}",
        "{verb} scalable solutions using {skill} for {domain} applications, reducing {metric} by {improvement}",
        "Led {domain} project leveraging {skill} — achieved {metric} improvement of {improvement}",
    ]

    OUTCOMES = [
        "streamline data workflows", "automate repetitive tasks",
        "enhance system performance", "accelerate delivery cycles",
        "improve model accuracy", "increase deployment reliability",
    ]

    METRICS = [
        "processing time", "system latency", "deployment frequency",
        "model accuracy", "test coverage", "build time", "error rate",
    ]

    IMPROVEMENTS = ["30%", "40%", "25%", "2×", "50%", "3×"]

    DOMAINS = [
        "production-scale", "enterprise", "data-intensive",
        "cloud-native", "real-time", "distributed",
    ]

    def _count_skill_mentions(self, skill: str, text: str) -> int:
        """Count how many times a skill keyword appears in text (case-insensitive)."""
        if not text or not skill:
            return 0
        pattern = re.compile(re.escape(skill.lower()), re.IGNORECASE)
        return len(pattern.findall(text))

    def _extract_jd_context_words(self, skill: str, jd_text: str, top_n: int = 5) -> List[str]:
        """Extract frequent context words near the skill in the JD for targeted rewrites."""
        if not jd_text:
            return []

        # Find words near the skill in JD
        text_lower = jd_text.lower()
        skill_lower = skill.lower()
        context_words = []

        idx = 0
        while True:
            pos = text_lower.find(skill_lower, idx)
            if pos == -1:
                break
            window_start = max(0, pos - 100)
            window_end = min(len(text_lower), pos + 100)
            window = text_lower[window_start:window_end]
            words = re.findall(r'\b[a-z]{4,}\b', window)
            context_words.extend(words)
            idx = pos + 1

        # Filter common stopwords
        stopwords = {
            "with", "that", "this", "have", "will", "from", "your",
            "they", "their", "about", "experience", "required", "skills",
            "using", "working", "ability", "knowledge", "team", "work",
        }
        filtered = [w for w in context_words if w not in stopwords]
        freq = Counter(filtered)
        return [w for w, _ in freq.most_common(top_n)]

    def _get_verbs_for_category(self, category: str) -> List[str]:
        return self.ACTION_VERBS.get(category, self.ACTION_VERBS["default"])

    def _generate_rewrites(
        self,
        skill: str,
        category: str,
        context_words: List[str],
        seed: int = 0,
    ) -> List[str]:
        """Generate 2-3 ATS-optimized bullet point rewrites."""
        import hashlib

        def pick(lst, offset=0):
            idx = (int(hashlib.md5(f"{skill}{offset}".encode()).hexdigest(), 16) + offset) % len(lst)
            return lst[idx]

        verbs = self._get_verbs_for_category(category)
        suggestions = []

        for i, template in enumerate(self.TEMPLATE_PATTERNS):
            verb = pick(verbs, i)
            outcome = pick(self.OUTCOMES, i + 1)
            metric = pick(self.METRICS, i + 2)
            improvement = pick(self.IMPROVEMENTS, i)
            domain_word = context_words[i % len(context_words)] if context_words else pick(self.DOMAINS, i)

            suggestion = template.format(
                verb=verb,
                skill=skill.title(),
                outcome=outcome,
                metric=metric,
                improvement=improvement,
                domain=domain_word,
            )
            suggestions.append(f"• {suggestion}.")

        return suggestions

    def _compute_ats_impact(self, current_count: int, skill: str, jd_text: str) -> float:
        """
        Estimate ATS impact score (0-10):
        Higher score = rewrite will make a bigger difference.
        """
        jd_mentions = self._count_skill_mentions(skill, jd_text)
        # Skills that appear often in JD but rarely in resume = high impact
        if current_count == 0:
            base = min(10.0, jd_mentions * 2.5)
        elif current_count == 1:
            base = min(8.0, jd_mentions * 1.5)
        else:
            base = max(1.0, 5.0 - current_count)
        return round(base, 1)

    def optimize(
        self,
        matched_skills: List[str],
        resume_sections: Dict,
        jd_text: str,
        skill_categories: Optional[Dict[str, str]] = None,
        highlight_threshold: int = 2,
    ) -> Dict:
        """
        Analyze matched skills that are under-highlighted in the resume.

        Args:
            matched_skills: Skills present in both resume and JD
            resume_sections: Parsed resume sections dict (experience, projects, etc.)
            jd_text: Full job description text
            skill_categories: Mapping of skill -> category (from normalizer)
            highlight_threshold: Min mentions needed to be "well highlighted"

        Returns:
            Dict with under_highlighted list, suggestions, and summary
        """
        experience_text = resume_sections.get("experience", "")
        projects_text = resume_sections.get("projects", "")
        skills_text = resume_sections.get("skills", "")
        combined_resume = f"{experience_text} {projects_text} {skills_text}"

        suggestions = []
        well_highlighted = []

        for skill in matched_skills:
            mention_count = self._count_skill_mentions(skill, combined_resume)

            if mention_count < highlight_threshold:
                # This skill is under-highlighted — generate rewrites
                category = (skill_categories or {}).get(skill, "default")
                context_words = self._extract_jd_context_words(skill, jd_text)
                rewrites = self._generate_rewrites(skill, category, context_words)
                ats_impact = self._compute_ats_impact(mention_count, skill, jd_text)

                suggestions.append({
                    "skill": skill,
                    "current_mentions": mention_count,
                    "suggested_rewrites": rewrites,
                    "ats_impact_score": ats_impact,
                    "jd_context_keywords": context_words,
                    "urgency": (
                        "High" if ats_impact >= 7
                        else "Medium" if ats_impact >= 4
                        else "Low"
                    ),
                })
            else:
                well_highlighted.append(skill)

        # Sort by ATS impact descending
        suggestions.sort(key=lambda x: x["ats_impact_score"], reverse=True)

        return {
            "ats_suggestions": suggestions,
            "well_highlighted_skills": well_highlighted,
            "under_highlighted_count": len(suggestions),
            "well_highlighted_count": len(well_highlighted),
            "summary": {
                "total_matched_skills": len(matched_skills),
                "skills_needing_highlight": len(suggestions),
                "skills_well_highlighted": len(well_highlighted),
                "avg_ats_impact": (
                    round(sum(s["ats_impact_score"] for s in suggestions) / len(suggestions), 1)
                    if suggestions else 0.0
                ),
                "highest_impact_skill": (
                    suggestions[0]["skill"] if suggestions else None
                ),
            },
        }


# ====================================
# SINGLETON
# ====================================
_optimizer = None


def get_resume_optimizer() -> ResumeOptimizer:
    global _optimizer
    if _optimizer is None:
        _optimizer = ResumeOptimizer()
    return _optimizer
