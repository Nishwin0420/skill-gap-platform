"""
Advanced Resume & JD Parser Module
===================================
Enhanced PDF and text parsing for resumes and job descriptions.
Extracts structured sections from documents.
"""

from PyPDF2 import PdfReader
import re


def extract_text_from_pdf(file):
    """
    Extract text content from a PDF file.

    Args:
        file: File-like object or path to PDF

    Returns:
        Extracted text string
    """
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception:
        return ""


def parse_resume_sections(text):
    """
    Parse resume text into structured sections.

    Args:
        text: Raw resume text

    Returns:
        Dict with sections: summary, experience, education, skills, projects
    """
    sections = {
        "summary": "",
        "experience": "",
        "education": "",
        "skills": "",
        "projects": "",
        "certifications": "",
        "full_text": text
    }

    # Define section header patterns
    section_patterns = {
        "summary": r"(?:summary|objective|profile|about\s*me)\s*[:\-]?\s*\n",
        "experience": r"(?:experience|work\s*experience|employment|work\s*history)\s*[:\-]?\s*\n",
        "education": r"(?:education|academic|qualification|degree)\s*[:\-]?\s*\n",
        "skills": r"(?:skills|technical\s*skills|core\s*competencies|technologies)\s*[:\-]?\s*\n",
        "projects": r"(?:projects|personal\s*projects|key\s*projects)\s*[:\-]?\s*\n",
        "certifications": r"(?:certifications?|certificates?|courses?)\s*[:\-]?\s*\n"
    }

    text_lower = text.lower()

    # Find section boundaries
    boundaries = []
    for section_name, pattern in section_patterns.items():
        matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
        for match in matches:
            boundaries.append((match.start(), match.end(), section_name))

    # Sort by position
    boundaries.sort(key=lambda x: x[0])

    # Extract section content
    for i, (start, end, name) in enumerate(boundaries):
        if i + 1 < len(boundaries):
            next_start = boundaries[i + 1][0]
            sections[name] = text[end:next_start].strip()
        else:
            sections[name] = text[end:].strip()

    return sections


def parse_job_description(text):
    """
    Parse job description text into structured components.

    Args:
        text: Raw JD text

    Returns:
        Dict with: title, requirements, responsibilities, qualifications
    """
    result = {
        "title": "",
        "requirements": "",
        "responsibilities": "",
        "qualifications": "",
        "full_text": text
    }

    section_patterns = {
        "requirements": r"(?:requirements?|required\s*skills?|must\s*have)\s*[:\-]?\s*\n",
        "responsibilities": r"(?:responsibilities|duties|role\s*description|what\s*you.*do)\s*[:\-]?\s*\n",
        "qualifications": r"(?:qualifications?|preferred|nice\s*to\s*have|desired)\s*[:\-]?\s*\n"
    }

    text_lower = text.lower()

    boundaries = []
    for section_name, pattern in section_patterns.items():
        matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
        for match in matches:
            boundaries.append((match.start(), match.end(), section_name))

    boundaries.sort(key=lambda x: x[0])

    for i, (start, end, name) in enumerate(boundaries):
        if i + 1 < len(boundaries):
            next_start = boundaries[i + 1][0]
            result[name] = text[end:next_start].strip()
        else:
            result[name] = text[end:].strip()

    # Try to extract title (first line)
    lines = text.strip().split("\n")
    if lines:
        result["title"] = lines[0].strip()

    return result


def extract_years_of_experience(text):
    """
    Extract years of experience mentioned in text.

    Args:
        text: Input text

    Returns:
        Float years of experience (0 if not found)
    """
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
        r'experience\s*[:\-]?\s*(\d+)\+?\s*years?',
    ]

    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return float(match.group(1))

    return 0.0


# ====================================
# TEST
# ====================================
if __name__ == "__main__":
    sample = """
    John Doe
    Software Engineer with 5+ years of experience

    Summary:
    Passionate developer skilled in Python and cloud technologies.

    Experience:
    Senior Developer at TechCorp (2020-2024)
    - Built microservices using FastAPI
    - Deployed on AWS using Docker

    Skills:
    Python, JavaScript, React, PostgreSQL, Docker, AWS

    Education:
    B.Tech in Computer Science, MIT (2019)
    """

    sections = parse_resume_sections(sample)
    print("\n=== Resume Sections ===")
    for key, value in sections.items():
        if key != "full_text":
            print(f"\n[{key.upper()}]\n{value[:100]}")

    exp = extract_years_of_experience(sample)
    print(f"\nYears of Experience: {exp}")
