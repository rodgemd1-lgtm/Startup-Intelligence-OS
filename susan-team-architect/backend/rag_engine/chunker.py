"""Smart text chunking for RAG ingestion."""
from __future__ import annotations
import re


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~0.75 tokens per word for English."""
    return int(len(text.split()) * 1.33)


def _max_words_for_tokens(max_tokens: int) -> int:
    """Convert a token limit to an approximate word limit."""
    return max(1, int(max_tokens / 1.33))


def _split_long_segment(text: str, max_tokens: int, overlap: int) -> list[str]:
    """Split a single long segment (no sentence boundaries) by word count."""
    words = text.split()
    max_words = _max_words_for_tokens(max_tokens)
    overlap_words = _max_words_for_tokens(overlap)
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap_words
    return chunks


def chunk_text(
    text: str,
    max_tokens: int = 500,
    overlap: int = 50,
) -> list[str]:
    """Split text into chunks by sentence boundaries, respecting token limits."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current_chunk: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = _estimate_tokens(sentence)

        # If a single sentence exceeds the limit, split it by words
        if sentence_tokens > max_tokens and not current_chunk:
            chunks.extend(_split_long_segment(sentence, max_tokens, overlap))
            continue

        if current_tokens + sentence_tokens > max_tokens and current_chunk:
            chunks.append(" ".join(current_chunk))
            # Keep overlap sentences
            overlap_tokens = 0
            overlap_start = len(current_chunk)
            for i in range(len(current_chunk) - 1, -1, -1):
                overlap_tokens += _estimate_tokens(current_chunk[i])
                if overlap_tokens >= overlap:
                    overlap_start = i
                    break
            current_chunk = current_chunk[overlap_start:]
            current_tokens = sum(_estimate_tokens(s) for s in current_chunk)

            # If after overlap, adding this sentence still exceeds, split it
            if current_tokens + sentence_tokens > max_tokens and sentence_tokens > max_tokens:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                chunks.extend(_split_long_segment(sentence, max_tokens, overlap))
                continue

        current_chunk.append(sentence)
        current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks if chunks else [text]


def chunk_markdown(
    text: str,
    max_tokens: int = 500,
) -> list[str]:
    """Split markdown by headings, then by token limit within sections."""
    sections = re.split(r'\n(?=#{1,3}\s)', text.strip())
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if _estimate_tokens(section) <= max_tokens:
            chunks.append(section)
        else:
            chunks.extend(chunk_text(section, max_tokens=max_tokens, overlap=50))
    return chunks if chunks else [text]
