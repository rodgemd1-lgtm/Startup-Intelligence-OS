---
description: Ingest data into Susan's RAG knowledge base
allowed-tools: Bash, Read, Write, WebFetch
---

# Susan Data Ingestion

Ingest data into the RAG knowledge base for a company or as shared knowledge.

## Usage
`/susan-ingest [source] [--type data_type] [--company company_id]`

## Execution

1. Determine the source type (markdown file, directory, URL)
2. Run the appropriate ingestor:

```bash
cd susan-team-architect/backend && python3 -c "
from rag_engine.ingestion import MarkdownIngestor
ingestor = MarkdownIngestor()
count = ingestor.ingest('$1', company_id='${3:-shared}', data_type='${2:-behavioral_economics}')
print(f'Ingested {count} chunks')
"
```

3. Report the number of chunks ingested and their data types
