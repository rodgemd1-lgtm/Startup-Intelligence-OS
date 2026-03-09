"""Chunking utilities aligned with Startup-Intelligence-OS."""
from __future__ import annotations

import re


def estimate_tokens(text: str) -> int:
    return int(len(text.split()) * 1.33)


def chunk_text(text: str, max_tokens: int = 500, overlap: int = 50) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = estimate_tokens(sentence)
        if current and current_tokens + sentence_tokens > max_tokens:
            chunks.append(" ".join(current))
            overlap_sentences: list[str] = []
            overlap_tokens = 0
            for previous in reversed(current):
                overlap_sentences.insert(0, previous)
                overlap_tokens += estimate_tokens(previous)
                if overlap_tokens >= overlap:
                    break
            current = overlap_sentences
            current_tokens = sum(estimate_tokens(item) for item in current)
        current.append(sentence)
        current_tokens += sentence_tokens

    if current:
        chunks.append(" ".join(current))

    return chunks if chunks else [text]


def chunk_markdown(text: str, max_tokens: int = 500) -> list[str]:
    sections = re.split(r"\n(?=#{1,3}\s)", text.strip())
    chunks: list[str] = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if estimate_tokens(section) <= max_tokens:
            chunks.append(section)
        else:
            chunks.extend(chunk_text(section, max_tokens=max_tokens))
    return chunks if chunks else [text]

