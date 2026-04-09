"""
Resume ATS (Applicant Tracking System) Scorer
================================================
Scores resumes against ATS compatibility criteria.
Provides an ATS-readiness score and actionable improvement tips.

Features:
    - Keyword density analysis
    - Section completeness check
    - Format scoring
    - Role-specific scoring
    - Improvement suggestions

Innovation Factor: Unique to this platform
"""

import re
from backend.nlp.skill_normalizer import get_normalizer
from backend.nlp.resume_parser import parse_resume_sections, extract_years_of_experience


class ATSScorer:
    """
    Automated Tracking System compatibility scorer.
    Evaluates resume quality against ATS criteria.
    """

    def __init__(self):
        self.normalizer = get_normalizer()

    def score_resume(self, resume_text, job_skills=None):
        """
        Score a resume for ATS compatibility.
        Returns score 0-100 with breakdown.
        """
        sections = parse_resume_sections(resume_text)
        experience = extract_years_of_experience(resume_text)

        scores = {}

        # 1. Section Completeness (25 pts)
        scores["section_completeness"] = self._score_sections(sections)

        # 2. Keyword Density (25 pts)
        scores["keyword_density"] = self._score_keyword_density(
            resume_text, job_skills or []
        )

        # 3. Format & Length (20 pts)
        scores["format_quality"] = self._score_format(resume_text)

        # 4. Action Verbs & Impact (15 pts)
        scores["action_language"] = self._score_action_language(resume_text)

        # 5. Contact & Metadata (15 pts)
        scores["metadata"] = self._score_metadata(resume_text)

        total = sum(scores.values())

        # Generate suggestions
        suggestions = self._generate_suggestions(scores, sections, resume_text, job_skills)

        return {
            "ats_score": round(total, 1),
            "max_score": 100,
            "grade": self._get_grade(total),
            "breakdown": {
                "section_completeness": {"score": scores["section_completeness"], "max": 25},
                "keyword_density": {"score": scores["keyword_density"], "max": 25},
                "format_quality": {"score": scores["format_quality"], "max": 20},
                "action_language": {"score": scores["action_language"], "max": 15},
                "metadata": {"score": scores["metadata"], "max": 15},
            },
            "suggestions": suggestions,
            "word_count": len(resume_text.split()),
            "experience_detected": experience
        }

    def _score_sections(self, sections):
        """Score based on presence of key resume sections."""
        required = ["summary", "experience", "education", "skills"]
        optional = ["projects", "certifications"]

        score = 0
        for sec in required:
            if sections.get(sec, "").strip():
                score += 5

        for sec in optional:
            if sections.get(sec, "").strip():
                score += 2.5

        return min(score, 25)

    def _score_keyword_density(self, text, job_skills):
        """Score based on relevant keyword usage."""
        if not job_skills:
            return 15  # Default if no JD provided

        text_lower = text.lower()
        matched = sum(1 for skill in job_skills if skill.lower() in text_lower)
        ratio = matched / max(len(job_skills), 1)

        return round(min(ratio * 25, 25), 1)

    def _score_format(self, text):
        """Score based on resume format quality."""
        score = 0
        words = len(text.split())

        # Word count (300-800 ideal for one page)
        if 300 <= words <= 800:
            score += 8
        elif 200 <= words <= 1200:
            score += 5
        else:
            score += 2

        # Has bullet points
        bullets = text.count("•") + text.count("-") + text.count("*")
        if bullets >= 5:
            score += 6
        elif bullets >= 2:
            score += 3

        # Has numbers (quantified achievements)
        numbers = len(re.findall(r'\d+', text))
        if numbers >= 5:
            score += 6
        elif numbers >= 2:
            score += 3

        return min(score, 20)

    def _score_action_language(self, text):
        """Score based on use of strong action verbs."""
        action_verbs = [
            "developed", "implemented", "designed", "managed", "led",
            "created", "built", "optimized", "improved", "delivered",
            "analyzed", "deployed", "automated", "collaborated", "architected",
            "integrated", "launched", "reduced", "increased", "achieved",
            "engineered", "mentored", "streamlined", "migrated", "scaled"
        ]

        text_lower = text.lower()
        found = sum(1 for verb in action_verbs if verb in text_lower)

        if found >= 8:
            return 15
        elif found >= 5:
            return 12
        elif found >= 3:
            return 8
        elif found >= 1:
            return 5
        return 2

    def _score_metadata(self, text):
        """Score based on contact info and professional metadata."""
        score = 0
        text_lower = text.lower()

        # Email
        if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
            score += 4

        # Phone
        if re.search(r'[\+]?[\d\-\(\)\s]{10,}', text):
            score += 3

        # LinkedIn or GitHub
        if "linkedin" in text_lower or "github" in text_lower:
            score += 4

        # Location
        location_keywords = ["india", "usa", "city", "state", "remote"]
        if any(kw in text_lower for kw in location_keywords):
            score += 2

        # Professional title
        titles = ["engineer", "developer", "analyst", "scientist", "manager", "architect"]
        if any(t in text_lower for t in titles):
            score += 2

        return min(score, 15)

    def _get_grade(self, score):
        if score >= 85:
            return "A+"
        elif score >= 75:
            return "A"
        elif score >= 65:
            return "B+"
        elif score >= 55:
            return "B"
        elif score >= 45:
            return "C"
        else:
            return "D"

    def _generate_suggestions(self, scores, sections, text, job_skills):
        """Generate actionable improvement suggestions."""
        suggestions = []

        if scores["section_completeness"] < 20:
            missing = []
            for sec in ["summary", "experience", "education", "skills"]:
                if not sections.get(sec, "").strip():
                    missing.append(sec.title())
            if missing:
                suggestions.append(f"❌ Add missing sections: {', '.join(missing)}")

        if scores["keyword_density"] < 15 and job_skills:
            text_lower = text.lower()
            missing_kw = [s for s in job_skills if s.lower() not in text_lower][:5]
            if missing_kw:
                suggestions.append(f"🔑 Add job keywords: {', '.join(missing_kw)}")

        if scores["format_quality"] < 12:
            suggestions.append("📝 Add quantified achievements with numbers (e.g., 'Improved performance by 30%')")

        if scores["action_language"] < 10:
            suggestions.append("💪 Use stronger action verbs: developed, implemented, optimized, delivered")

        if scores["metadata"] < 10:
            suggestions.append("📧 Ensure your email, phone, and LinkedIn/GitHub links are included")

        words = len(text.split())
        if words < 200:
            suggestions.append("📄 Resume is too short. Expand experience and project descriptions.")
        elif words > 1000:
            suggestions.append("📄 Resume is too long. Keep it concise (1-2 pages max)")

        if not suggestions:
            suggestions.append("✅ Your resume looks great! Minor optimization may further improve ATS scoring.")

        return suggestions


# ====================================
# SINGLETON
# ====================================
_scorer = None

def get_ats_scorer():
    global _scorer
    if _scorer is None:
        _scorer = ATSScorer()
    return _scorer
