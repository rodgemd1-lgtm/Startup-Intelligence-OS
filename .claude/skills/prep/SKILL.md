---
name: prep
description: Run Jake's meeting prep pipeline — generates pre-meeting context briefs by searching email threads, extracting attendees, and pulling Susan RAG context. Use before any meeting for full situational awareness.
---

Run the PAI meeting prep pipeline for a specific meeting.

## Steps

1. If the user specifies a meeting title, run:
```bash
python3 pai/pipelines/run.py prep "Meeting Title Here"
```

2. If no meeting specified, check today's calendar for upcoming meetings:
```bash
python3 pai/pipelines/run.py prep --next
```

3. Present the prep brief with:
   - Attendee names detected from the title
   - Related email threads found
   - Susan RAG context (company/project matches)
   - Format-aware prep notes (1:1, standup, review, demo)

4. If Orchard MCP is available, also pull the full event details including Zoom links and notes:
```python
from pai.pipelines.orchard_client import OrchardClient
client = OrchardClient()
events = client.call("calendar_info", {"type": "events", "start_date": "...", "end_date": "..."})
```

5. Offer to draft talking points or an agenda based on the context found.
