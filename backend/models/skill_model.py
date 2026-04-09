# ================================
# FINAL SKILL MODEL (PHASE 7)
# ================================

SKILL_WEIGHTS = {
    "python": 10,
    "machine learning": 10,
    "deep learning": 10,
    "sql": 8,
    "data analysis": 7,
    "tensorflow": 9,
    "pytorch": 9,
    "react": 6,
    "javascript": 6,
    "html": 5,
    "css": 5
}

LEARNING_RESOURCES = {
    "machine learning": {
        "course": "https://www.coursera.org/learn/machine-learning",
        "youtube": "https://www.youtube.com/results?search_query=machine+learning",
        "pdf": "https://www.cs.cmu.edu/~tom/mlbook.html"
    },
    "python": {
        "course": "https://www.learnpython.org/",
        "youtube": "https://www.youtube.com/results?search_query=python+tutorial",
        "pdf": "https://docs.python.org/3/tutorial/"
    },
    "sql": {
        "course": "https://www.w3schools.com/sql/",
        "youtube": "https://www.youtube.com/results?search_query=sql+tutorial",
        "pdf": "https://www.tutorialspoint.com/sql/sql_tutorial.pdf"
    }
}


def rank_missing_skills(missing):
    return sorted(missing, key=lambda x: SKILL_WEIGHTS.get(x, 5), reverse=True)


def analyze_skill_gap(user_skills, job_skills):
    user_set = set(user_skills)
    job_set = set(job_skills)

    matched = list(user_set & job_set)
    missing = list(job_set - user_set)

    total_weight = sum(SKILL_WEIGHTS.get(s, 5) for s in job_set)
    matched_weight = sum(SKILL_WEIGHTS.get(s, 5) for s in matched)

    match_percentage = (matched_weight / total_weight) * 100 if total_weight else 0

    return {
        "matched_skills": matched,
        "missing_skills": rank_missing_skills(missing),
        "match_percentage": round(match_percentage, 2)
    }


def calculate_employability(match_percentage, experience):
    exp_score = min(experience * 10, 100)
    return round((0.75 * match_percentage) + (0.25 * exp_score), 2)


def job_suitability(match_percentage):
    return "Suitable" if match_percentage >= 60 else "Not Suitable"


def generate_learning_path(missing_skills):
    path = []

    for i, skill in enumerate(missing_skills):

        # Dynamic link generation
        skill_query = skill.replace(" ", "+")

        resources = {
            "course": f"https://www.coursera.org/search?query={skill_query}",
            "youtube": f"https://www.youtube.com/results?search_query={skill_query}",
            "pdf": f"https://www.google.com/search?q={skill_query}+pdf"
        }

        path.append({
            "step": i + 1,
            "skill": skill,
            "resources": resources
        })

    return path


def full_analysis(user_skills, job_skills, experience):
    gap = analyze_skill_gap(user_skills, job_skills)
    score = calculate_employability(gap["match_percentage"], experience)

    return {
        "matched_skills": gap["matched_skills"],
        "missing_skills": gap["missing_skills"],
        "match_percentage": gap["match_percentage"],
        "employability_score": score,
        "job_suitability": job_suitability(gap["match_percentage"]),
        "learning_path": generate_learning_path(gap["missing_skills"]),
        "report": detailed_score_analysis(
    gap["match_percentage"], experience, gap["missing_skills"]
),
"timeline": generate_timeline(gap["missing_skills"]),
"resume_feedback": generate_resume_feedback(user_skills, gap["missing_skills"]),
"recommended_roles": recommend_roles(user_skills),
"explanation": generate_explanation(
    user_skills,
    job_skills,
    gap["match_percentage"],
    gap["missing_skills"]
)
    }
def detailed_score_analysis(match_percentage, experience, missing_skills):
    return {
        "technical_score": match_percentage,
        "experience_score": round(min(experience * 10, 100), 2),

        "skill_gap_severity": (
            "High" if len(missing_skills) > 6 else
            "Medium" if len(missing_skills) > 3 else
            "Low"
        ),

        "overall_rating": (
            "Excellent" if match_percentage >= 75 else
            "Good" if match_percentage >= 50 else
            "Needs Improvement"
        )
    }
def generate_timeline(missing_skills):
    timeline = []

    for i, skill in enumerate(missing_skills):
        timeline.append({
            "week": f"Week {i + 1}",
            "skill": skill,
            "goal": f"Learn fundamentals and build mini project in {skill}"
        })

    return timeline
def generate_resume_feedback(user_skills, missing_skills):
    feedback = []

    # Suggest missing skills improvement
    for skill in missing_skills[:5]:
        feedback.append(f"Add projects or certifications related to {skill}")

    # Suggest strengthening existing skills
    for skill in user_skills[:3]:
        feedback.append(f"Highlight advanced work or projects in {skill}")

    # General improvements
    feedback.append("Include measurable achievements (e.g., improved performance by 20%)")
    feedback.append("Add GitHub or portfolio links to showcase projects")
    feedback.append("Use action verbs like 'Developed', 'Implemented', 'Optimized'")

    return feedback
def recommend_roles(user_skills):
    roles = []

    skill_set = set(user_skills)

    # AI / ML roles
    if {"python", "machine learning"} & skill_set:
        roles.append("Machine Learning Engineer")

    if {"deep learning", "tensorflow", "pytorch"} & skill_set:
        roles.append("AI Engineer")

    # Data roles
    if {"sql", "pandas", "numpy"} & skill_set:
        roles.append("Data Analyst")

    # Web roles
    if {"html", "css", "javascript"} & skill_set:
        roles.append("Frontend Developer")

    if {"node.js", "javascript"} & skill_set:
        roles.append("Backend Developer")

    # General software role
    if {"c", "c++", "java"} & skill_set:
        roles.append("Software Engineer")

    # Default fallback
    if not roles:
        roles.append("Entry-Level Software Developer")

    return list(set(roles))
def generate_explanation(user_skills, job_skills, match_percentage, missing_skills):
    reasons = []

    # Skill-based explanation
    if missing_skills:
        top_missing = missing_skills[:3]
        reasons.append(f"Missing important skills like {', '.join(top_missing)}")

    # Match percentage explanation
    if match_percentage < 40:
        reasons.append("Low overlap between your skills and job requirements")
    elif match_percentage < 70:
        reasons.append("Partial skill match, but improvements needed")
    else:
        reasons.append("Strong alignment with job requirements")

    # Suggestion logic
    if missing_skills:
        suggestion = f"Focus on learning {', '.join(missing_skills[:3])} to improve your chances"
    else:
        suggestion = "You meet most requirements. Focus on refining advanced skills"

    return {
        "summary": f"Your profile matches {match_percentage}% of required skills",
        "reasons": reasons,
        "suggestion": suggestion
    }