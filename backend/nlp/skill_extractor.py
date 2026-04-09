"""
Advanced Skill Extractor Module
================================
Extracts skills from resume/JD text using multi-method NLP pipeline:
1. spaCy NER + PhraseMatcher (500+ skill patterns)
2. TF-IDF keyword extraction
3. HuggingFace Sentence Transformers for semantic matching
4. Regex pattern matching (fallback)

References:
    - Ahmed et al. (2023) — NLP for Skill Extraction from Job Descriptions
    - HuggingFace Transformers documentation
"""

import re
import spacy
from spacy.matcher import PhraseMatcher
from pathlib import Path
import json
import numpy as np

# ====================================
# LOAD DEPENDENCIES
# ====================================
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# ====================================
# LOAD SKILL ONTOLOGY
# ====================================
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ONTOLOGY_PATH = DATA_DIR / "skill_ontology.json"

def _load_all_skill_terms():
    """Load all skill names and synonyms from ontology."""
    terms = set()
    try:
        with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
            ontology = json.load(f)
        for category_data in ontology.get("categories", {}).values():
            for skill_info in category_data.get("skills", {}).values():
                canonical = skill_info.get("canonical", "")
                terms.add(canonical.lower())
                for syn in skill_info.get("synonyms", []):
                    terms.add(syn.lower())
    except FileNotFoundError:
        pass
    return list(terms)


ALL_SKILL_TERMS = _load_all_skill_terms()

# ====================================
# BUILD SPACY PHRASE MATCHER
# ====================================
phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
skill_patterns = [nlp.make_doc(term) for term in ALL_SKILL_TERMS if len(term) > 1]
if skill_patterns:
    phrase_matcher.add("SKILLS", skill_patterns)


# ====================================
# METHOD 1: spaCy PhraseMatcher (Primary)
# ====================================
def extract_skills_phrasematcher(text):
    """
    Extract skills using spaCy PhraseMatcher with 500+ skill patterns.
    Most accurate method for known skills.
    """
    doc = nlp(text.lower())
    matches = phrase_matcher(doc)
    extracted = set()
    for match_id, start, end in matches:
        skill = doc[start:end].text
        extracted.add(skill)
    return list(extracted)


# ====================================
# METHOD 2: Regex Pattern Matching (Fallback)
# ====================================
def extract_skills_regex(text):
    """
    Extract skills using regex word boundary matching.
    Handles multi-word skills and special characters.
    """
    text_lower = text.lower()
    extracted = set()
    for skill in ALL_SKILL_TERMS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            extracted.add(skill)
    return list(extracted)


# ====================================
# METHOD 3: spaCy NER Entity Extraction
# ====================================
def extract_skills_ner(text):
    """
    Extract potential skill-related entities using spaCy NER.
    Catches technology names recognized as organizations/products.
    """
    doc = nlp(text)
    extracted = set()
    tech_labels = {"ORG", "PRODUCT", "WORK_OF_ART"}

    for ent in doc.ents:
        if ent.label_ in tech_labels:
            ent_lower = ent.text.lower()
            # Check if entity matches any known skill
            if ent_lower in ALL_SKILL_TERMS:
                extracted.add(ent_lower)
    return list(extracted)


# ====================================
# METHOD 4: TF-IDF Keyword Extraction
# ====================================
def extract_keywords_tfidf(text, top_n=20):
    """
    Extract important keywords from text using TF-IDF weighting.
    Returns top N keywords by TF-IDF score.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer

    # Create a corpus with the input text
    corpus = [text.lower()]

    vectorizer = TfidfVectorizer(
        max_features=200,
        stop_words="english",
        ngram_range=(1, 3)
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]

        # Get top scoring terms
        top_indices = scores.argsort()[-top_n:][::-1]
        keywords = [(feature_names[i], scores[i]) for i in top_indices if scores[i] > 0]

        # Filter to known skills
        extracted = set()
        for term, score in keywords:
            if term in ALL_SKILL_TERMS:
                extracted.add(term)

        return list(extracted)
    except Exception:
        return []


# ====================================
# METHOD 5: Semantic Matching with Sentence Transformers
# ====================================
_sentence_model = None

def _get_sentence_model():
    """Lazy-load sentence transformer model."""
    global _sentence_model
    if _sentence_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        except ImportError:
            _sentence_model = None
    return _sentence_model


def extract_skills_semantic(text, threshold=0.55):
    """
    Extract skills using semantic similarity with Sentence Transformers.
    Compares text segments against known skill names using embeddings.

    This method catches skills mentioned in paraphrased or indirect ways.
    """
    model = _get_sentence_model()
    if model is None:
        return []

    try:
        # Split text into sentences
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]

        if not sentences:
            return []

        # Get embeddings for sentences and skill names
        canonical_skills = list(set(
            term for term in ALL_SKILL_TERMS
            if len(term) > 2  # Skip very short terms
        ))

        if not canonical_skills:
            return []

        sent_embeddings = model.encode(sentences, convert_to_numpy=True)
        skill_embeddings = model.encode(canonical_skills, convert_to_numpy=True)

        # Calculate similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(sent_embeddings, skill_embeddings)

        # Extract skills above threshold
        extracted = set()
        for i in range(len(sentences)):
            for j in range(len(canonical_skills)):
                if similarities[i][j] > threshold:
                    extracted.add(canonical_skills[j])

        return list(extracted)
    except Exception:
        return []


# ====================================
# COMBINED EXTRACTION PIPELINE
# ====================================
def extract_skills(text, use_semantic=False):
    """
    Master skill extraction using multi-method NLP pipeline.

    Combines results from:
    1. spaCy PhraseMatcher (highest priority)
    2. Regex pattern matching
    3. spaCy NER entity extraction
    4. TF-IDF keyword extraction
    5. Semantic matching (optional, slower)

    Args:
        text: Input text (resume, JD, etc.)
        use_semantic: Whether to use HuggingFace semantic matching

    Returns:
        Sorted list of unique extracted skills
    """
    if not text or len(text.strip()) < 5:
        return []

    # Run all extraction methods
    phrasematcher_skills = extract_skills_phrasematcher(text)
    regex_skills = extract_skills_regex(text)
    ner_skills = extract_skills_ner(text)
    tfidf_skills = extract_keywords_tfidf(text)

    # Combine all results
    all_skills = set(phrasematcher_skills + regex_skills + ner_skills + tfidf_skills)

    # Optional: semantic matching (slower but catches paraphrased mentions)
    if use_semantic:
        semantic_skills = extract_skills_semantic(text)
        all_skills.update(semantic_skills)

    return sorted(list(all_skills))


def extract_skills_with_details(text, use_semantic=False):
    """
    Extract skills AND return extraction method details for transparency.
    Used by XAI module for explainability.
    """
    results = {}

    phrasematcher_skills = extract_skills_phrasematcher(text)
    for s in phrasematcher_skills:
        results[s] = {"method": "phrasematcher", "confidence": 0.95}

    regex_skills = extract_skills_regex(text)
    for s in regex_skills:
        if s not in results:
            results[s] = {"method": "regex", "confidence": 0.85}

    ner_skills = extract_skills_ner(text)
    for s in ner_skills:
        if s not in results:
            results[s] = {"method": "ner", "confidence": 0.70}

    tfidf_skills = extract_keywords_tfidf(text)
    for s in tfidf_skills:
        if s not in results:
            results[s] = {"method": "tfidf", "confidence": 0.60}

    if use_semantic:
        semantic_skills = extract_skills_semantic(text)
        for s in semantic_skills:
            if s not in results:
                results[s] = {"method": "semantic_transformer", "confidence": 0.55}

    return results


# ====================================
# TEST
# ====================================
if __name__ == "__main__":
    sample = """
    Experienced software engineer with 5 years in Python and JavaScript.
    Proficient in React.js, Node.js, and PostgreSQL.
    Built ML models using scikit-learn and TensorFlow.
    Worked with Docker and AWS for deployment.
    Familiar with Agile methodology and CI/CD pipelines.
    """

    print("\n=== Skill Extraction Test ===")
    skills = extract_skills(sample)
    print(f"Extracted {len(skills)} skills: {skills}")

    print("\n=== Detailed Extraction ===")
    detailed = extract_skills_with_details(sample)
    for skill, info in sorted(detailed.items()):
        print(f"  {skill:20s} → method: {info['method']:20s} confidence: {info['confidence']}")
