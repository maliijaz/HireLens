from __future__ import annotations
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_tfidf_scores(jd_text: str, resume_texts: list[str]) -> list[float]:
    if not resume_texts:
        return []

    corpus = [jd_text] + resume_texts
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=10_000,
        sublinear_tf=True,
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    jd_vector = tfidf_matrix[0]
    resume_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(jd_vector, resume_vectors).flatten()

    max_sim = similarities.max()
    if max_sim > 0:
        normalized = (similarities / max_sim).tolist()
    else:
        normalized = similarities.tolist()

    return [float(s) for s in normalized]
