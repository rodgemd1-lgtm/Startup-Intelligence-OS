# PAI V6: Multi-Channel — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Jake is everywhere. Add iMessage, Slack, Discord, and Voice channels. Implement channel-aware personality adaptation. Context persists across all channels via LosslessClaw.

**Depends On:** V0-V5 complete

**Score Target:** 84 → 88

---

## Pre-Flight Checklist

- [ ] V5 exit criteria all passed (learning engine operational)
- [ ] OpenClaw gateway stable for 30+ days
- [ ] LosslessClaw context persistence proven across restarts
- [ ] Notification system respects per-channel rules (V4)

---

## Phase 6A: Additional Channels

### Task 1: Add iMessage Channel (BlueBubbles)

**Files:**
- Create: `pai/channels/imessage/setup.md`
- Create: `pai/config/bluebubbles.json`

**Implementation steps:**
1. Install BlueBubbles server on Mac Studio (requires macOS + iCloud)
   ```bash
   brew install --cask bluebubbles
   ```
2. Configure BlueBubbles REST API (port 1234)
3. Create OpenClaw channel adapter for BlueBubbles
   ```bash
   openclaw channels add bluebubbles --api-url http://localhost:1234
   ```
4. Configure allowed contacts (Mike's phone number only)
5. Test: send iMessage to Mac Studio → Jake responds
6. Verify LosslessClaw maintains context across Telegram AND iMessage
7. Create launchd plist for BlueBubbles auto-start

**Commit:** `feat(pai): iMessage channel via BlueBubbles — send/receive through Mac Studio`

---

### Task 2: Add Slack Workspace Channel

**Files:**
- Create: `pai/channels/slack/setup.md`
- Create: `pai/config/slack-app.json`

**Implementation steps:**
1. Create Slack app in Mike's workspace (Socket Mode for security)
2. Configure bot token scopes: `chat:write`, `im:history`, `im:read`, `im:write`
3. Add Slack channel to OpenClaw:
   ```bash
   openclaw channels add slack --app-token xapp-... --bot-token xoxb-...
   ```
4. Configure: DMs only (no channel posting without APPROVE)
5. Test: DM Jake in Slack → full Opus response
6. Verify cross-channel context: start conversation in Telegram, continue in Slack

**Commit:** `feat(pai): Slack channel — DM-only with Socket Mode`

---

### Task 3: Add Discord Server Channel

**Files:**
- Create: `pai/channels/discord/setup.md`

**Implementation steps:**
1. Create Discord bot application
2. Add to OpenClaw:
   ```bash
   openclaw channels add discord --token ... --allowed-guilds ...
   ```
3. Configure: respond in DMs and specific channels only
4. Test: message Jake in Discord → full response
5. Verify cross-channel context persistence

**Commit:** `feat(pai): Discord channel — DMs + allowed channels`

---

### Task 4: Add Voice Interface (ElevenLabs TTS)

**Files:**
- Create: `pai/channels/voice/voice_server.py`
- Create: `pai/config/voice.json`

**Implementation steps:**
1. Set up ElevenLabs API with cloned voice (or pre-built voice)
2. Create voice server on Mac Studio (port 8888, Miessler-compatible)
3. Voice server endpoints:
   - `POST /notify` — text → TTS → play through speakers
   - `POST /listen` — STT → text → Jake → TTS response
4. Configure voice notifications for P0 alerts
5. Integrate with OpenClaw Companion App (if available)
6. Wake word detection (optional — "Hey Jake")
7. Voice response formatting: shorter, more conversational than text

**Voice config:**
```json
{
  "provider": "elevenlabs",
  "voice_id": "jake-custom",
  "model": "eleven_multilingual_v2",
  "stability": 0.5,
  "similarity_boost": 0.8,
  "output_format": "mp3_44100_128",
  "max_response_length": 200,
  "wake_word": "Hey Jake",
  "stt_provider": "whisper"
}
```

**Commit:** `feat(pai): voice interface — ElevenLabs TTS + Whisper STT on Mac Studio`

---

## Phase 6B: Channel-Aware Personality

### Task 5: Implement Channel Personality Adaptation

**Files:**
- Create: `pai/intelligence/channel_personality.py`
- Update: `pai/SOUL.md` (add channel-specific overrides)

**Personality rules per channel:**
| Channel | Tone | Length | Emoji | Format |
|---------|------|--------|-------|--------|
| Telegram | Casual, sassy | Short (< 500 chars default) | Yes | Markdown |
| iMessage | Brief, personal | Very short (< 200 chars) | Minimal | Plain text |
| Slack | Professional, structured | Medium | No | Mrkdwn |
| Discord | Casual, friendly | Medium | Yes | Markdown |
| Voice | Conversational, concise | Very short | N/A | Spoken |
| Claude Code | Full technical, detailed | Long | No | Markdown |

**Implementation steps:**
1. Create ChannelPersonality class with per-channel system prompt overrides
2. Inject channel-specific personality at message processing time
3. Adjust response length, formatting, and tone based on channel
4. Example: same question in Telegram gets a sassy 3-line answer; in Slack gets a structured paragraph
5. Test: ask same question across 4 channels, verify tone differences

**Commit:** `feat(pai): channel-aware personality — adaptive tone, length, and formatting per channel`

---

## Phase 6C: Cross-Channel Context

### Task 6: Verify Cross-Channel Context Persistence

**Tests:**
1. Start conversation in Telegram → continue in Slack → LosslessClaw remembers
2. Receive email triage in Telegram → discuss it in iMessage → context flows
3. Voice notification about P0 → respond via Telegram → Jake knows what you're referring to
4. All channels share the same LosslessClaw DAG (single SQLite on Mac Studio)

**Implementation steps:**
1. Verify LosslessClaw tags messages with channel source
2. Verify cross-channel search works: `lcm_grep` returns results from all channels
3. Create channel context header: "Last interaction was 2 hours ago via Slack about X"
4. Test with 4+ channel handoffs over 48 hours

**Commit:** `feat(pai): cross-channel context verification — LosslessClaw persistence across all channels`

---

## V6 Exit Criteria (All Must Pass)

- [ ] iMessage channel working (BlueBubbles on Mac Studio)
- [ ] Slack channel working (DM-only, Socket Mode)
- [ ] Discord channel working (DMs + allowed channels)
- [ ] Voice interface working (ElevenLabs TTS + Whisper STT)
- [ ] Jake reachable on 4+ channels simultaneously
- [ ] Channel personality adapts tone/length/format per channel
- [ ] Context persists across all channels via LosslessClaw
- [ ] Cross-channel handoffs work (start in one, continue in another)
- [ ] Voice interaction working on Mac Studio (TTS + STT)
- [ ] All channels respect DND and notification rules from V4

**Score target: 84 → 88**
