"""Local hybrid retrieval for structured and narrative chunks."""

from collections import Counter
import math
import re
from typing import Optional


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class HybridRetriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.doc_freq = Counter()
        self.corpus_size = len(chunks)
        for chunk in chunks:
            for token in set(tokenize(chunk["content"])):
                self.doc_freq[token] += 1

    def search(self, query: str, category: Optional[str] = None, entity_type: Optional[str] = None, top_k: int = 5) -> list[dict]:
        query_terms = tokenize(query)
        results = []
        for chunk in self.chunks:
            if category and chunk.get("category") != category:
                continue
            if entity_type and chunk.get("entity_type") != entity_type:
                continue
            score = self._score(query_terms, chunk["content"])
            if score <= 0:
                continue
            results.append({**chunk, "score": score})
        return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]

    def _score(self, query_terms: list[str], content: str) -> float:
        doc_terms = tokenize(content)
        term_freq = Counter(doc_terms)
        score = 0.0
        for term in query_terms:
            if term not in term_freq:
                continue
            idf = math.log((1 + self.corpus_size) / (1 + self.doc_freq[term])) + 1
            score += term_freq[term] * idf
        return score
