"""
Interview Prep Module
======================
Generates role-specific interview questions and preparation tips.
Based on gap analysis — focuses on areas where user needs improvement.

Innovation Factor: Unique to this platform
"""

from backend.nlp.skill_normalizer import get_normalizer


# Role-based interview question bank
INTERVIEW_QUESTIONS = {
    "python": [
        {"q": "What are Python decorators? Explain with an example.", "level": "intermediate", "type": "technical"},
        {"q": "Explain the difference between list, tuple, and set in Python.", "level": "beginner", "type": "technical"},
        {"q": "What are generators in Python and when would you use them?", "level": "intermediate", "type": "technical"},
        {"q": "Explain GIL (Global Interpreter Lock) in Python.", "level": "advanced", "type": "technical"},
    ],
    "machine learning": [
        {"q": "What is the bias-variance tradeoff?", "level": "intermediate", "type": "technical"},
        {"q": "Explain the difference between supervised and unsupervised learning.", "level": "beginner", "type": "technical"},
        {"q": "How do you handle overfitting in a model?", "level": "intermediate", "type": "technical"},
        {"q": "Explain the working of Random Forest algorithm.", "level": "intermediate", "type": "technical"},
        {"q": "What evaluation metrics would you use for an imbalanced dataset?", "level": "advanced", "type": "technical"},
    ],
    "deep learning": [
        {"q": "What is backpropagation? Explain step by step.", "level": "intermediate", "type": "technical"},
        {"q": "Compare CNN and RNN architectures.", "level": "intermediate", "type": "technical"},
        {"q": "What is transfer learning and when is it useful?", "level": "intermediate", "type": "technical"},
        {"q": "Explain vanishing gradient problem and how to solve it.", "level": "advanced", "type": "technical"},
    ],
    "react": [
        {"q": "What are React hooks? Explain useState and useEffect.", "level": "beginner", "type": "technical"},
        {"q": "What is the Virtual DOM and how does React use it?", "level": "intermediate", "type": "technical"},
        {"q": "Explain React component lifecycle methods.", "level": "intermediate", "type": "technical"},
        {"q": "How would you optimize a React application's performance?", "level": "advanced", "type": "technical"},
    ],
    "sql": [
        {"q": "What is the difference between INNER JOIN and LEFT JOIN?", "level": "beginner", "type": "technical"},
        {"q": "Explain indexing in databases and when to use it.", "level": "intermediate", "type": "technical"},
        {"q": "Write a query to find the second highest salary.", "level": "intermediate", "type": "technical"},
        {"q": "What are ACID properties in databases?", "level": "intermediate", "type": "technical"},
    ],
    "docker": [
        {"q": "What is Docker and how is it different from a VM?", "level": "beginner", "type": "technical"},
        {"q": "Explain Dockerfile, Docker image, and Docker container.", "level": "intermediate", "type": "technical"},
        {"q": "How do you manage multi-container applications?", "level": "intermediate", "type": "technical"},
    ],
    "aws": [
        {"q": "What are the key AWS services for deploying a web application?", "level": "beginner", "type": "technical"},
        {"q": "Explain the difference between EC2, Lambda, and ECS.", "level": "intermediate", "type": "technical"},
        {"q": "How would you design a highly available architecture on AWS?", "level": "advanced", "type": "technical"},
    ],
    "javascript": [
        {"q": "Explain closures in JavaScript with an example.", "level": "intermediate", "type": "technical"},
        {"q": "What is the event loop in JavaScript?", "level": "intermediate", "type": "technical"},
        {"q": "Explain promises and async/await.", "level": "intermediate", "type": "technical"},
        {"q": "What is the difference between var, let, and const?", "level": "beginner", "type": "technical"},
    ],
    "data analysis": [
        {"q": "What steps do you follow in a data analysis project?", "level": "beginner", "type": "technical"},
        {"q": "How do you handle missing data?", "level": "intermediate", "type": "technical"},
        {"q": "Explain correlation vs causation with examples.", "level": "intermediate", "type": "technical"},
    ],
    "git": [
        {"q": "What is the difference between git merge and git rebase?", "level": "intermediate", "type": "technical"},
        {"q": "Explain branching strategies (Git Flow, Trunk-based).", "level": "intermediate", "type": "technical"},
    ],
}

# Behavioral questions
BEHAVIORAL_QUESTIONS = [
    {"q": "Tell me about a challenging technical problem you solved.", "level": "all", "type": "behavioral"},
    {"q": "How do you stay updated with new technologies?", "level": "all", "type": "behavioral"},
    {"q": "Describe a situation where you had to learn a new technology quickly.", "level": "all", "type": "behavioral"},
    {"q": "Tell me about a time you worked in a team to deliver a project.", "level": "all", "type": "behavioral"},
    {"q": "How do you prioritize tasks when working on multiple projects?", "level": "all", "type": "behavioral"},
]


class InterviewPrepGenerator:
    """
    Generates personalized interview preparation materials
    based on the user's skill gaps and target role.
    """

    def __init__(self):
        self.normalizer = get_normalizer()

    def generate_prep(self, user_skills, job_skills, target_role=None, gap_analysis=None, job_description=None):
        """
        Generate interview preparation questions and tips.
        Tries Groq LLM for dynamic questions; falls back to static dict.

        Args:
            user_skills: Skills user has
            job_skills: Skills required by the job
            target_role: Target job role
            gap_analysis: Output from SkillGapEngine
            job_description: Raw JD text for Groq context (optional)

        Returns:
            Dict with questions, tips, and preparation strategy
        """
        matched = set(user_skills) & set(job_skills)
        missing = set(job_skills) - set(user_skills)

        # ── Try Groq LLM for dynamic questions ──────────────────
        ai_result = None
        try:
            from backend.api_clients.groq_client import generate_interview_questions
            ai_result = generate_interview_questions(
                user_skills=list(matched),
                missing_skills=list(missing),
                target_role=target_role,
                job_description=job_description,
            )
        except Exception:
            pass

        if ai_result and ai_result.get("questions"):
            q_data = ai_result["questions"]
            tech_questions = {
                "your_skills": [q for q in q_data.get("technical_questions", [])
                                if q.get("skill", "").lower() in {s.lower() for s in matched}][:8],
                "gap_skills": [q for q in q_data.get("technical_questions", [])
                               if q.get("skill", "").lower() in {s.lower() for s in missing}][:6],
            }
            # If skill-split yields nothing, put all technical in your_skills
            if not tech_questions["your_skills"] and not tech_questions["gap_skills"]:
                tech_questions["your_skills"] = q_data.get("technical_questions", [])[:8]

            behavioral = q_data.get("behavioral_questions", BEHAVIORAL_QUESTIONS[:4])

            tips = self._generate_tips(matched, missing, target_role)
            study_plan = self._generate_study_plan(missing, gap_analysis)

            return {
                "target_role": target_role or "General",
                "total_questions": len(tech_questions["your_skills"]) + len(tech_questions["gap_skills"]) + len(behavioral),
                "technical_questions": tech_questions,
                "behavioral_questions": behavioral,
                "preparation_tips": tips,
                "study_plan": study_plan,
                "confidence_areas": list(matched)[:5],
                "weak_areas": list(missing)[:5],
                "ai_generated": True,
                "ai_model": ai_result.get("model", "groq"),
            }

        # ── Fallback: static question dictionary ─────────────────
        matched_questions = []
        for skill in matched:
            skill_lower = skill.lower()
            if skill_lower in INTERVIEW_QUESTIONS:
                matched_questions.extend(INTERVIEW_QUESTIONS[skill_lower])
            else:
                matched_questions.extend([
                    {"q": f"Can you explain your experience and expertise working with {skill}?", "level": "intermediate", "type": "technical"},
                    {"q": f"Describe a complex problem you solved using {skill}.", "level": "advanced", "type": "technical"}
                ])

        gap_questions = []
        for skill in missing:
            skill_lower = skill.lower()
            if skill_lower in INTERVIEW_QUESTIONS:
                gap_questions.extend(INTERVIEW_QUESTIONS[skill_lower][:2])
            else:
                gap_questions.extend([
                    {"q": f"How would you approach learning {skill} for this role?", "level": "beginner", "type": "technical"},
                    {"q": f"What do you know about {skill} and its core principles?", "level": "beginner", "type": "technical"}
                ])

        for q in matched_questions + gap_questions:
            q["source"] = "curated"

        tips = self._generate_tips(matched, missing, target_role)
        study_plan = self._generate_study_plan(missing, gap_analysis)

        return {
            "target_role": target_role or "General",
            "total_questions": len(matched_questions) + len(gap_questions) + len(BEHAVIORAL_QUESTIONS),
            "technical_questions": {
                "your_skills": matched_questions[:10],
                "gap_skills": gap_questions[:8],
            },
            "behavioral_questions": BEHAVIORAL_QUESTIONS,
            "preparation_tips": tips,
            "study_plan": study_plan,
            "confidence_areas": list(matched)[:5],
            "weak_areas": list(missing)[:5],
            "ai_generated": False,
        }


    def _generate_tips(self, matched, missing, target_role):
        tips = []

        if matched:
            tips.append(f"💪 You'll likely be tested on: {', '.join(list(matched)[:5])}. Prepare deep examples.")

        if missing:
            tips.append(f"⚠️ Be ready to explain how you'd learn: {', '.join(list(missing)[:3])}")
            tips.append("💡 Frame skill gaps positively: 'I'm currently learning X through Y'")

        tips.append("📝 Prepare 2-3 project examples demonstrating your technical skills")
        tips.append("🎯 Research the company's tech stack and recent projects")
        tips.append("⏰ Practice answering in 2-3 minutes per question")

        if target_role:
            tips.append(f"🔍 Study common {target_role} interview patterns and system design questions")

        return tips

    def _generate_study_plan(self, missing, gap_analysis):
        if not missing:
            return {"message": "No gaps — focus on deepening existing skills!"}

        plan = {
            "priority_topics": [],
            "estimated_prep_days": 0
        }

        for skill in list(missing)[:5]:
            hours = self.normalizer.get_estimated_hours(skill)
            difficulty = self.normalizer.get_skill_difficulty(skill)

            plan["priority_topics"].append({
                "skill": skill,
                "difficulty": difficulty,
                "suggested_prep_hours": min(hours, 20),
                "focus": f"Learn fundamentals + prepare 2 interview answers about {skill}"
            })
            plan["estimated_prep_days"] += min(hours // 8, 5)

        return plan


# ====================================
# SINGLETON
# ====================================
_prep_gen = None

def get_interview_prep():
    global _prep_gen
    if _prep_gen is None:
        _prep_gen = InterviewPrepGenerator()
    return _prep_gen
