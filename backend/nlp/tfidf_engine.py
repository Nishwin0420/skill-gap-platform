"""
TF-IDF Engine Module
====================
Provides TF-IDF based text similarity computation for comparing
resumes against job descriptions at the document level.

Uses scikit-learn TfidfVectorizer with cosine similarity.

References:
    - Ahmed et al. (2023) — NLP for Skill Extraction from Job Descriptions
    - scikit-learn documentation
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class TFIDFEngine:
    """
    TF-IDF based document similarity engine.
    Computes text similarity between resumes and job descriptions using
    TF-IDF vectorization and cosine similarity.
    """

    def __init__(self, max_features=5000, ngram_range=(1, 3)):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words="english",
            ngram_range=ngram_range,
            sublinear_tf=True,
            min_df=1
        )
        self.is_fitted = False

    def compute_similarity(self, text1, text2):
        """
        Compute cosine similarity between two texts using TF-IDF.

        Args:
            text1: First text (e.g., resume)
            text2: Second text (e.g., job description)

        Returns:
            Float similarity score between 0 and 1
        """
        try:
            corpus = [text1.lower(), text2.lower()]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return round(float(similarity[0][0]), 4)
        except Exception:
            return 0.0

    def get_important_terms(self, text, top_n=15):
        """
        Get the most important terms in a text based on TF-IDF scores.

        Args:
            text: Input text
            top_n: Number of top terms to return

        Returns:
            List of (term, score) tuples sorted by importance
        """
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text.lower()])
            feature_names = self.vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            top_indices = scores.argsort()[-top_n:][::-1]
            return [
                (feature_names[i], round(float(scores[i]), 4))
                for i in top_indices
                if scores[i] > 0
            ]
        except Exception:
            return []

    def compare_multiple(self, reference_text, candidate_texts):
        """
        Compare a reference text against multiple candidate texts.
        Useful for ranking multiple JDs against a resume.

        Args:
            reference_text: The reference text (e.g., resume)
            candidate_texts: List of candidate texts (e.g., job descriptions)

        Returns:
            List of (index, similarity_score) sorted by score desc
        """
        try:
            corpus = [reference_text.lower()] + [t.lower() for t in candidate_texts]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)

            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            scores = similarities[0]

            results = [
                (i, round(float(scores[i]), 4))
                for i in range(len(candidate_texts))
            ]
            return sorted(results, key=lambda x: x[1], reverse=True)
        except Exception:
            return []

    def get_skill_relevance_vector(self, text, skill_list):
        """
        Compute TF-IDF relevance of each skill within a text.

        Args:
            text: Input text
            skill_list: List of skill names to check

        Returns:
            Dict of skill → relevance score
        """
        text_lower = text.lower()
        relevance = {}

        for skill in skill_list:
            # Count occurrences and compute a simple relevance
            count = text_lower.count(skill.lower())
            relevance[skill] = min(count * 0.2, 1.0)

        return relevance


# ====================================
# SINGLETON
# ====================================
_tfidf_engine = None

def get_tfidf_engine():
    global _tfidf_engine
    if _tfidf_engine is None:
        _tfidf_engine = TFIDFEngine()
    return _tfidf_engine


# ====================================
# TEST
# ====================================
if __name__ == "__main__":
    engine = TFIDFEngine()

    resume = """
    Experienced in Python, machine learning, and data analysis.
    Built REST APIs using FastAPI and Django. 
    Worked with PostgreSQL and MongoDB databases.
    """

    jd = """
    Looking for a Python developer with experience in machine learning,
    deep learning, and TensorFlow. Must know SQL and data analysis.
    Experience with FastAPI preferred.
    """

    similarity = engine.compute_similarity(resume, jd)
    print(f"\nResume-JD Similarity: {similarity:.4f}")

    print("\nTop terms in resume:")
    for term, score in engine.get_important_terms(resume):
        print(f"  {term}: {score}")
