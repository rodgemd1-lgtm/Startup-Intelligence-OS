---
description: Query Susan's RAG knowledge base
allowed-tools: Bash, Read
---

# Susan Knowledge Query

Search the RAG knowledge base for relevant information.

## Usage
`/susan-query "your question" [--company company_id] [--types type1,type2]`

## Execution

1. Run the query:

```bash
cd susan-team-architect/backend && python3 -c "
from rag_engine.retriever import Retriever
r = Retriever()
results = r.search('$1', '${2:-shared}', top_k=5)
for hit in results:
    print(f'[{hit[\"similarity\"]:.3f}] [{hit[\"data_type\"]}] {hit[\"content\"][:200]}')
    print('---')
"
```

2. Present results with similarity scores and source metadata
