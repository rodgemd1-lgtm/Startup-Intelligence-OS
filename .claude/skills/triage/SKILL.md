---
name: triage
description: Run Jake's email triage pipeline — scans all unread email across iCloud and Exchange, applies 5-level urgency scoring (U5 critical to U1 noise), VIP detection, and recommends actions (reply, review, archive, flag).
---

Run the PAI email triage pipeline and present prioritized results.

## Steps

1. Run the pipeline:
```bash
python3 pai/pipelines/run.py triage
```

2. Present results grouped by urgency level. Lead with critical/high items.

3. For U5/U4 messages, offer to:
   - Show the full email content
   - Draft a reply
   - Flag or archive

4. For U1 (noise) messages, offer to mark as read or archive in bulk:
```bash
~/go/bin/mail-app-cli messages mark <id> --read
```

5. If the user provides additional VIP names or domains, note them for future runs.
