import numpy as np
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import settings

class TextSimilarity:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        if not text_a.strip() or not text_b.strip():
            return 0.0
        try:
            tfidf = self.vectorizer.fit_transform([text_a, text_b])
            return float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
        except Exception:
            return 0.0

    def find_similar(self, text: str, corpus_texts: List[str], threshold: float = settings.similarity_threshold) -> List[Tuple[int, float]]:
        if not text.strip() or not corpus_texts:
            return []
        try:
            tfidf = self.vectorizer.fit_transform([text] + corpus_texts)
            sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
            return [(i, float(score)) for i, score in enumerate(sims) if score >= threshold]
        except Exception:
            return []

    def cluster_texts(self, texts: List[str], threshold: float = settings.similarity_threshold) -> List[List[int]]:
        if not texts:
            return []
        if len(texts) == 1:
            return [[0]]
        
        try:
            tfidf = self.vectorizer.fit_transform(texts)
            sim_matrix = cosine_similarity(tfidf)
        except Exception:
            return [[i] for i in range(len(texts))]

        n = len(texts)
        visited = set()
        clusters = []

        for i in range(n):
            if i in visited:
                continue
            cluster = [i]
            visited.add(i)
            for j in range(i + 1, n):
                if j not in visited and sim_matrix[i, j] >= threshold:
                    cluster.append(j)
                    visited.add(j)
            clusters.append(cluster)
        
        return clusters

vector_store = TextSimilarity()
