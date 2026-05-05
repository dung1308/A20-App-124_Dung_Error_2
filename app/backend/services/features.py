# services/features.py

import numpy as np

def extract_features(query: str, doc: str, distance: float, metadata: dict):
    query_words = set(query.lower().split())
    doc_words = set(doc.lower().split())

    keyword_overlap = len(query_words & doc_words)

    return np.array([
        1.0 - distance if distance is not None else 0.0,   # semantic score
        keyword_overlap,                                   # keyword match
        len(doc_words) / 100,                              # normalized length
        1 if metadata.get("source") == "cv" else 0         # CV boost
    ])