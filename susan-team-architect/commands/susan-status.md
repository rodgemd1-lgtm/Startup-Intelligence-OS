---
description: Check the status of Susan's systems — RAG data, agent runs, costs
allowed-tools: Bash, Read
---

# Susan Status Check

Check the current state of all Susan systems.

## Usage
`/susan-status [company]`

## Execution

1. Run status check:

```bash
cd susan-team-architect/backend && python3 -c "
from rag_engine.retriever import Retriever
from susan_core.config import config
r = Retriever()
print(f'Total chunks: {r.count_chunks()}')
print(f'Company chunks: {r.count_chunks(\"$1\")}')
print(f'Shared chunks: {r.count_chunks(\"shared\")}')
"
```

2. Check for existing outputs in `./companies/$1/susan-outputs/`
3. Report which phases have been completed
4. Show recent agent run costs from Supabase
