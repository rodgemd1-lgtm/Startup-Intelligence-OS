---
name: briefing
description: Run Jake's morning briefing pipeline — pulls unread email from iCloud + Exchange, today's calendar events via Orchard, and produces a prioritized summary with VIP detection and urgency scoring.
---

Run Jake's morning briefing pipeline and present results to the user.

## Steps

1. Run the pipeline:
```bash
bin/jake-morning-pipeline.sh
```

2. Present the output to the user in a clean, scannable format.

3. If there are VIP or urgent (U4/U5) messages, highlight them prominently.

4. If the user asks for more detail on any email, use `mail-app-cli` to fetch the full message:
```bash
~/go/bin/mail-app-cli messages show <message-id>
```

5. If the user wants to act on calendar items (join meeting, prep for meeting), offer to run `/prep` for that meeting.
