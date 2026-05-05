"""
Groq LLM API Client
=====================
Generates dynamic, contextual interview questions using Groq's
fast inference API (llama3-8b-8192).

Requires: GROQ_API_KEY environment variable.
Fallback: Returns None if key missing or call fails — caller uses static dict.

Free tier: 30 RPM, 14,400 RPD — more than sufficient.
"""

import os
import requests
from typing import Optional, List, Dict

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"
TIMEOUT = 15  # seconds


def generate_interview_questions(
    user_skills: List[str],
    missing_skills: List[str],
    target_role: Optional[str],
    job_description: Optional[str],
) -> Optional[Dict]:
    """
    Generate live, contextual interview questions using Groq LLM.

    Args:
        user_skills: Skills the candidate has
        missing_skills: Skills they are missing (gap)
        target_role: Job title (e.g. "ML Engineer")
        job_description: Full JD text for context

    Returns:
        Dict with technical and behavioral questions, or None on failure.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None

    role_str = target_role or "Software Engineer"
    user_str = ", ".join(user_skills[:10]) if user_skills else "General programming"
    gap_str = ", ".join(missing_skills[:8]) if missing_skills else "None identified"

    # Truncate JD to keep tokens manageable
    jd_excerpt = (job_description or "")[:800].strip()
    jd_section = f"\n\nJob Description Excerpt:\n{jd_excerpt}" if jd_excerpt else ""

    system_prompt = (
        "You are an expert technical interviewer. Generate a structured set of "
        "interview questions in valid JSON format only — no explanations outside JSON."
    )

    user_prompt = f"""Generate interview questions for a {role_str} candidate.

Candidate's skills: {user_str}
Skill gaps to probe: {gap_str}{jd_section}

Return ONLY a JSON object with this exact structure:
{{
  "technical_questions": [
    {{"q": "question text", "level": "beginner|intermediate|advanced", "type": "technical", "skill": "related skill"}},
    ... (8 questions total)
  ],
  "behavioral_questions": [
    {{"q": "question text", "level": "all", "type": "behavioral"}},
    ... (4 questions total)
  ]
}}

Make questions highly specific to the job description and skill gaps. Do not include any text outside the JSON."""

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 1200,
            },
            timeout=TIMEOUT,
        )

        if response.status_code != 200:
            return None

        content = response.json()["choices"][0]["message"]["content"].strip()

        # Parse JSON from response
        import json
        # Strip any markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        parsed = json.loads(content)

        # Validate structure
        if "technical_questions" not in parsed:
            return None

        # Mark all as AI-generated
        for q in parsed.get("technical_questions", []):
            q["source"] = "ai"
        for q in parsed.get("behavioral_questions", []):
            q["source"] = "ai"

        return {
            "questions": parsed,
            "ai_generated": True,
            "model": MODEL,
        }

    except Exception:
        return None  # Caller falls back to static dict
