from rag_engine.chunker import chunk_text, chunk_markdown

def test_chunk_text_splits_by_size():
    text = "word " * 1000  # ~1000 words
    chunks = chunk_text(text, max_tokens=500, overlap=50)
    assert len(chunks) >= 2
    assert all(len(c.split()) <= 600 for c in chunks)  # rough token estimate

def test_chunk_text_preserves_content():
    text = "Hello world. This is a test."
    chunks = chunk_text(text, max_tokens=500, overlap=0)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_chunk_markdown_splits_by_heading():
    md = "# Section 1\nContent 1.\n\n## Section 2\nContent 2.\n\n# Section 3\nContent 3."
    chunks = chunk_markdown(md, max_tokens=500)
    assert len(chunks) >= 2  # Should split on headings

def test_chunk_markdown_metadata():
    md = "# My Section\nSome content here."
    chunks = chunk_markdown(md, max_tokens=500)
    assert len(chunks) >= 1
