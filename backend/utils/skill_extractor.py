import re
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Skill dictionary (can be expanded later)
SKILL_SET = [
    "python", "java", "c++", "machine learning", "deep learning",
    "data analysis", "sql", "mysql", "mongodb",
    "html", "css", "javascript", "react", "node.js",
    "tensorflow", "pytorch", "nlp", "pandas", "numpy"
]


# 🔹 1. Regex-based (best for phrases)
def extract_skills_regex(text):
    text = text.lower()
    extracted = []

    for skill in SKILL_SET:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            extracted.append(skill)

    return extracted


# 🔹 2. NLP Token-based (single word detection)
def extract_skills_nlp(text):
    doc = nlp(text.lower())
    extracted = []

    for token in doc:
        if token.text in SKILL_SET:
            extracted.append(token.text)

    return extracted


# 🔹 3. Phrase matching (simple but effective)
def extract_skills_phrase(text):
    text = text.lower()
    extracted = []

    for skill in SKILL_SET:
        if skill in text:
            extracted.append(skill)

    return extracted


# 🔹 4. FINAL COMBINED FUNCTION (IMPORTANT)
def extract_skills(text):
    regex_skills = extract_skills_regex(text)
    nlp_skills = extract_skills_nlp(text)
    phrase_skills = extract_skills_phrase(text)

    # Combine all methods
    combined = set(regex_skills + nlp_skills + phrase_skills)

    return sorted(list(combined))


# 🔹 Test block
if __name__ == "__main__":
    sample_text = """
    I have experience in Python, Pandas, and Machine Learning.
    Also worked with SQL, TensorFlow, and React.
    """

    print("Final Extracted Skills:", extract_skills(sample_text))