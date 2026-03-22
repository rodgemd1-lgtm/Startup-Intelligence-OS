# JARVIS Agent — Complete Technical Reference

> **Research sprint completed: 2026-03-22**
> **Sources: 6 parallel research agents, Amazon developer docs, GitHub repos, community findings**
> The authoritative knowledge base for building, deploying, and extending the Jarvis Alexa skill.

---

## 0. Current Skill State

| Property | Value |
|---|---|
| Skill ID | `amzn1.ask.skill.7366f2b5-f2d4-430a-bfcf-6fe17642ce00` |
| CodeCommit repo | `https://git-codecommit.us-east-1.amazonaws.com/v1/repos/7366f2b5-f2d4-430a-bfcf-6fe17642ce00` |
| Invocation name | `jarvis` → "Alexa, open Jarvis" ✅ |
| Lambda code | `/tmp/jarvis-skill/lambda/lambda_function.py` (778 lines) |
| Response DB | `artifacts/alexa-jarvis/jarvis_responses.py` (642 lines, 17 categories, not yet merged) |
| Voice | `<voice name="Brian">` (British Polly, all responses) |
| Current version | `deploy-v8-fingerprint` |
| SkillBuilder | `SkillBuilder()` — needs upgrade for services |
| Active handlers | 21 (Launch through EasterEgg) |

### Handler Inventory
LaunchRequest, GreetingIntent, IdentityIntent, StatusReportIntent, SuitStatusIntent,
SassIntent, DadJokeIntent, MotivationIntent, GoodbyeIntent, ProtocolIntent,
ThreatAssessmentIntent, WeatherIntent, TimeIntent, ComplimentIntent, HelpIntent,
CancelOrStop, Fallback, SessionEnded, RememberIntent, RecallIntent, EasterEggIntent

---

## 1. Deployment — The Definitive Guide

### How It Actually Works

```
git push to master branch
    ↓ (~10 seconds)
CodeCommit: source stored
    ↓ (~1-5 minutes — THIS IS THE WAIT)
Amazon CodeBuild: pip install + package Lambda
    ↓
New Lambda version published
    ↓
dev stage alias updated → new code is live
    ↓
Test in simulator
```

**Key facts confirmed by research:**
- `ask deploy` is a **NO-OP** for hosted skills in CLI v2. Confirmed in official docs and CLI GitHub issue #404.
- `git push origin master` → updates **dev stage** (simulator tests this)
- `git push origin master:prod` (or `git push origin prod`) → updates **live stage** (real Echo device)
- `hostedSkillDeployment.status == "SUCCEEDED"` confirms Lambda alias IS updated
- The Developer Console "Save/Deploy" button does **exactly the same thing** as `git push origin master`

### Why the v8 Capabilities Code Wasn't Showing in Simulator

We were testing too early. CodeBuild takes 1-5 minutes after the git push completes. The `SUCCEEDED` status from the CodeCommit push acceptance fires before CodeBuild finishes. **The fix: poll SMAPI until `hostedSkillDeployment` status == `SUCCEEDED`, then test.**

### Correct Deploy + Verify Workflow

```bash
SKILL_ID="amzn1.ask.skill.7366f2b5-f2d4-430a-bfcf-6fe17642ce00"

# 1. Make changes in /tmp/jarvis-skill/lambda/lambda_function.py

# 2. Commit
cd /tmp/jarvis-skill
git add lambda/lambda_function.py
git commit -m "feat: description"

# 3. Get fresh CodeCommit credentials (10-min expiry)
CREDS=$(ask smapi generate-credentials-for-alexa-hosted-skill --skill-id $SKILL_ID)
CC_USER=$(echo $CREDS | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['repositoryCredentials']['username'])")
CC_PASS=$(echo $CREDS | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['repositoryCredentials']['password'])")

# 4. URL-encode (% and / in credentials break git)
CC_USER_ENC=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote('$CC_USER', safe=''))")
CC_PASS_ENC=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote('$CC_PASS', safe=''))")
git remote set-url origin "https://${CC_USER_ENC}:${CC_PASS_ENC}@git-codecommit.us-east-1.amazonaws.com/v1/repos/7366f2b5-f2d4-430a-bfcf-6fe17642ce00"

# 5. Push to dev stage
git push origin master

# 6. WAIT — poll every 30s until SUCCEEDED
while true; do
  STATUS=$(ask smapi get-skill-status --skill-id $SKILL_ID 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('hostedSkillDeployment',{}).get('lastUpdatedRequest',{}).get('status','unknown'))" 2>/dev/null)
  echo "Status: $STATUS"
  if [ "$STATUS" = "SUCCEEDED" ]; then break; fi
  sleep 30
done

# 7. Now test in simulator
ask smapi simulate-skill \
  --skill-id $SKILL_ID \
  --stage development \
  --input-content '{"type":"text","value":"open jarvis"}' \
  --locale en-US
```

### Promote to Live (Real Echo Device)

```bash
git push origin master:prod
# Then poll the same status endpoint until SUCCEEDED
```

---

## 2. Target Architecture

### Current
```
Alexa Custom Skill (hosted Lambda, Python)
├── SkillBuilder() — no service client factory
├── No DynamoDB persistence
├── No voice profile detection (anyone = "sir")
└── jarvis_responses.py not yet merged into Lambda
```

### V2 Jarvis (What to Build Toward)
```
Alexa Multi-Capability Skill (MCS)
├── Custom Skill Model (Jarvis intents + personality)
│   ├── CustomSkillBuilder(api_client=DefaultApiClient())
│   ├── DynamoDbAdapter → jarvis-user-profiles table
│   ├── BootInterceptor: loads user profile, sets title from personId
│   ├── Person Profile API → Mike = "sir", James = "Captain" (auto-detected)
│   ├── All 17 jarvis_responses.py categories merged in
│   ├── Repetition prevention via session attributes
│   ├── Reminders API ("Jarvis, remind me at 7 PM...")
│   ├── Timers API ("Jarvis, set a 20 minute timer")
│   ├── Lists API ("Jarvis, add protein powder to my shopping list") [test for deprecation]
│   ├── Proactive Events → server can push Jarvis alerts to Echo
│   ├── APL for Echo Show (if applicable)
│   └── Custom Tasks → Routine integration (morning brief, arrival, departure)
└── Smart Home Model (device control)
    ├── Home Assistant REST API as unified device layer
    ├── Alexa.SceneController → "activate Movie Mode"
    ├── Alexa.PowerController, BrightnessController, ColorController
    └── Alexa.LockController, MotionSensor, CameraStreamController
```

---

## 3. Critical Upgrade: SkillBuilder → CustomSkillBuilder

The current Lambda uses `SkillBuilder()`. This works for basic intents but **disables the service client factory** needed for Reminders, Timers, Lists, and voice profile lookups.

```python
# CURRENT (breaks service APIs):
from ask_sdk_core.skill_builder import SkillBuilder
sb = SkillBuilder()

# REQUIRED for all service APIs:
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

sb = CustomSkillBuilder(
    persistence_adapter=DynamoDbAdapter(
        table_name="jarvis-user-profiles",
        create_table=True
    ),
    api_client=DefaultApiClient()
)
```

**requirements.txt additions:**
```
ask-sdk-core>=1.18.0
ask-sdk-dynamodb-persistence-adapter>=1.15.0
ask-sdk-model>=1.89.0
boto3>=1.26.0
requests>=2.28.0
spotipy>=2.23.0  # if adding Spotify
```

---

## 4. Person Profile API — Mike vs James Auto-Detection

**Highest priority feature.** When Mike and James each enroll a Voice Profile in the Alexa app, Jarvis auto-identifies who is speaking and addresses them correctly — no one has to say who they are.

### One-Time Setup (Each User in Alexa App)
Alexa app → More → Settings → Your Profile → Voice → Set Up Voice Profile → follow training

### Required Permission
Add to `skill.json`:
```json
{ "name": "alexa::person_id:read" }
```

### Implementation

```python
class BootInterceptor(AbstractRequestInterceptor):
    """Runs before every handler — identifies speaker and loads their profile."""

    def process(self, handler_input):
        attrs = handler_input.attributes_manager

        person = handler_input.request_envelope.context.system.person
        if person:
            person_id = person.person_id

            # Load persistent profile
            try:
                persistent = attrs.persistent_attributes
            except Exception:
                persistent = {}

            users = persistent.get("users", {})

            if person_id in users:
                # Known voice — load their title
                attrs.session_attributes["title"] = users[person_id]["title"]
                attrs.session_attributes["person_id"] = person_id
            else:
                # Unknown voice — set default, flag for enrollment
                attrs.session_attributes["title"] = "sir"
                attrs.session_attributes["new_user"] = person_id
        else:
            # No voice profile enrolled or device doesn't support it
            attrs.session_attributes["title"] = "sir"

# In any handler:
title = handler_input.attributes_manager.session_attributes.get("title", "sir")
response = f"Good morning, {title}."
```

### First-Time Enrollment

```python
class EnrollUserIntentHandler(AbstractRequestHandler):
    """'Jarvis, call me Captain' — saves their preferred title."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("EnrollUserIntent")(handler_input)

    def handle(self, handler_input):
        session = handler_input.attributes_manager.session_attributes
        new_person_id = session.get("new_user")

        slots = handler_input.request_envelope.request.intent.slots
        title = slots.get("TitleSlot").value if slots.get("TitleSlot") else "sir"

        if new_person_id:
            persistent = handler_input.attributes_manager.persistent_attributes
            if "users" not in persistent:
                persistent["users"] = {}
            persistent["users"][new_person_id] = {
                "title": title,
                "enrolled_at": datetime.datetime.now().isoformat()
            }
            handler_input.attributes_manager.save_persistent_attributes()
            session["title"] = title
            r = f"Understood. I'll address you as {title} from now on."
        else:
            r = "Your voice profile is already on file."

        return handler_input.response_builder.speak(jarvis(r)).response
```

---

## 5. Response System — Merging jarvis_responses.py

The `jarvis_responses.py` (17 categories, 232+ responses) needs to be imported into the Lambda. Add repetition prevention via session attributes.

```python
# Import at top of lambda_function.py — copy categories from jarvis_responses.py:
GREETINGS_MORNING_STARK = ["Good morning, sir. All systems nominal.", ...]
GREETINGS_MORNING_CAPTAIN = ["Good morning, Captain. All clear.", ...]
SASS = ["As always, sir, a great pleasure watching you work.", ...]
# ... all 17 categories

def get_response(category: list, session_attrs: dict, key: str) -> str:
    """Random selection that avoids immediate repetition."""
    last = session_attrs.get(f"last_{key}", -1)
    options = [i for i in range(len(category)) if i != last]
    if not options:
        options = list(range(len(category)))
    idx = random.choice(options)
    session_attrs[f"last_{key}"] = idx
    return category[idx]

# Usage:
session = handler_input.attributes_manager.session_attributes
response = get_response(SASS, session, "sass")
```

---

## 6. Wake Word & Invocation Reality

**Bottom line: "Jarvis" cannot be set as a native Echo wake word.** Amazon restricts wake words to: Alexa, Amazon, Echo, Computer, Ziggy. Custom wake words are Enterprise-only (Alexa Custom Assistant SDK — not consumer-accessible).

### What IS Achievable

| Goal | How |
|---|---|
| "Alexa, open Jarvis" | Skill invocation — already working ✅ |
| "Alexa, ask Jarvis to [x]" | One-shot utterance — works natively |
| Jarvis without saying "open Jarvis" | Alexa Routines → Custom Tasks |
| Morning brief auto-trigger | Routine: daily alarm → Jarvis morning task |
| Arrival home trigger | Routine: geofence → Jarvis arrival task |
| "Alexa, Jarvis morning" | Custom phrase routine → Jarvis task |
| Rename Echo to "Jarvis" | Cosmetic label only, doesn't change wake word |
| Persistent session | `.ask()` reprompt, 8-second idle timeout |

### Custom Tasks Setup (enables Routine integration)

Add to `skill.json` manifest:
```json
"tasks": [
  { "name": "MorningBriefing" },
  { "name": "EveningWelcome" },
  { "name": "DepartureProtocol" },
  { "name": "ArrivalWelcome" }
]
```

Users add in Alexa app: More → Routines → + → Add action → Skills → Jarvis → [Task Name]

### Persistent Session Pattern

```python
# Keep Jarvis "open" after every response — user can speak follow-ups without re-invoking:
return (
    handler_input.response_builder
    .speak(jarvis(response))
    .ask(jarvis("Anything else, sir?"))  # .ask() = shouldEndSession: false
    .response
)
# Without .ask(): session closes after speaking (one-shot behavior)
# With .ask(): Alexa listens for 8 seconds, plays reprompt, listens 8 more, then closes
```

---

## 7. Reminders API

### What It Does
Creates reminders that fire at specific times. Persist across sessions (survive after skill closes). Appear in the Alexa app. Can use custom SSML for the spoken announcement.

### Permission Required
```json
{ "name": "alexa::alerts:reminders:skill:readwrite" }
```

### Python Implementation

```python
from ask_sdk_model.services.reminder_management import (
    ReminderRequest, Trigger, TriggerType, AlertInfo, SpokenInfo, SpokenText,
    PushNotification, PushNotificationStatus,
)
from ask_sdk_model.ui import AskForPermissionsConsentCard
import datetime, pytz

REMINDERS_PERMISSION = "alexa::alerts:reminders:skill:readwrite"

class SetReminderIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SetReminderIntent")(handler_input)

    def handle(self, handler_input):
        permissions = handler_input.request_envelope.context.system.user.permissions

        # Check permission granted
        if not (permissions and permissions.consent_token):
            return (
                handler_input.response_builder
                .speak(jarvis("To set reminders, I'll need your permission first, sir. I've sent a card to your Alexa app."))
                .set_card(AskForPermissionsConsentCard(permissions=[REMINDERS_PERMISSION]))
                .response
            )

        reminder_client = handler_input.service_client_factory.get_reminder_management_service()

        # Parse time from slot — example: 7 PM today
        # In production: use AMAZON.TIME + AMAZON.DATE slots
        reminder_time = datetime.datetime(2026, 3, 22, 19, 0, 0)

        reminder_request = ReminderRequest(
            request_time=datetime.datetime.now(tz=pytz.utc).strftime("%Y-%m-%dT%H:%M:%S.000"),
            trigger=Trigger(
                object_type=TriggerType.SCHEDULED_ABSOLUTE,
                scheduled_time=reminder_time.strftime("%Y-%m-%dT%H:%M:%S.000"),
                time_zone_id="America/Chicago",  # CRITICAL: match user's timezone
            ),
            alert_info=AlertInfo(
                spoken_info=SpokenInfo(content=[
                    SpokenText(
                        locale="en-US",
                        text="Reminder",
                        ssml="<speak><voice name=\"Brian\">Sir, you asked me to remind you.</voice></speak>",
                    )
                ])
            ),
            push_notification=PushNotification(status=PushNotificationStatus.ENABLED),
        )

        try:
            reminder_client.create_reminder(reminder_request)
            r = "Reminder set. I'll alert you at the appropriate time, sir."
        except Exception as e:
            r = "I encountered an error setting the reminder. Please try again, sir."

        return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Anything else?")).response
```

### Reminders Gotchas
- `time_zone_id` is critical — omitting it fires at wrong time. Use Device Settings API to fetch user's TZ.
- First use requires consent card flow — gracefully handle the unauthenticated state.
- Recurring minimum: 1 hour for en-US.
- Can only create during active skill session (unless using LWA server token).

---

## 8. Timers API

### What It Does
Countdown timers. Device-bound (fire on the device that created them). Do not persist across sessions. Can announce custom text when they fire.

### Permission Required
```json
{ "name": "alexa::alerts:timers:skill:readwrite" }
```

### Python Implementation

```python
from ask_sdk_model.services.timer_management import (
    TimerRequest, CreationBehavior, DisplayExperience, Operation, OperationEnum,
)

class SetTimerIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SetTimerIntent")(handler_input)

    def handle(self, handler_input):
        timer_client = handler_input.service_client_factory.get_timer_management_service()

        # Duration in ISO 8601: PT20M = 20 min, PT1H30M = 1h30m, PT45S = 45s
        # In production: parse from AMAZON.DURATION slot
        duration = "PT20M"

        timer_request = TimerRequest(
            duration=duration,
            timer_label="Workout Timer",
            creation_behavior=CreationBehavior(
                display_experience=DisplayExperience(visibility="VISIBLE")
            ),
            triggering_behavior=Operation(
                object_type=OperationEnum.ANNOUNCE,
                text_to_announce={
                    "locale": "en-US",
                    "text": "Sir, your workout timer has expired."
                },
            ),
        )

        try:
            timer_client.create_timer(timer_request)
            r = "20 minute workout timer set. I'll let you know when it expires, sir."
        except Exception:
            r = "Timer creation failed. Please try again."

        return handler_input.response_builder.speak(jarvis(r)).response
```

### Timers vs Reminders

| Feature | Reminders | Timers |
|---|---|---|
| Fires at specific time | ✅ | ❌ (duration-based only) |
| Persists across sessions | ✅ | ❌ |
| Appears in Alexa app | ✅ | ❌ |
| Cross-device | ✅ | ❌ |
| Custom SSML on fire | ✅ | Limited |

**Rule:** Use Reminders for appointments. Use Timers for cooking/workouts.

---

## 9. Lists API

**⚠️ Deprecation Conflict:** One research source reports Lists API removed July 2024; another provides working Python examples. **Test before building.** If deprecated, use Notion or Google Tasks via account linking as alternative.

### Permission Required
```json
{ "name": "alexa::household:lists:read" },
{ "name": "alexa::household:lists:write" }
```

### Python Implementation (if still active)

```python
from ask_sdk_model.services.list_management import ListItemRequestBody

def get_list_id(list_client, list_name: str) -> str | None:
    """Fetch the ID for 'Alexa shopping list' or 'Alexa to-do list'."""
    for lst in list_client.get_lists_metadata().lists:
        if lst.name.lower() == list_name.lower():
            return lst.list_id
    return None

class AddToShoppingListIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AddToShoppingListIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        item = slots.get("item").value if slots.get("item") else "item"

        list_client = handler_input.service_client_factory.get_list_management_service()
        list_id = get_list_id(list_client, "Alexa shopping list")

        if list_id:
            list_client.create_list_item(
                list_id=list_id,
                list_item_request_body=ListItemRequestBody(value=item, status="active")
            )
            r = f"Added {item} to your shopping list, sir."
        else:
            r = "I couldn't locate your shopping list."

        return handler_input.response_builder.speak(jarvis(r)).response
```

---

## 10. Proactive Events — Jarvis Pushes Alerts to Echo

Send a notification to Mike's Echo from a server (cron job, webhook, etc.) — no active skill session needed.

**Constraint:** No free-form text. Must use predefined event schemas. Use `AMAZON.MessageAlert.Activated` for general Jarvis alerts.

### Required Permission
```json
{ "name": "alexa::devices:all:notifications:write" }
```

### Server-Side Script (runs outside Lambda)

```python
# jarvis_proactive.py — run from any Python server/cron
import os, uuid, requests
from datetime import datetime, timedelta, timezone

def get_lwa_token(client_id: str, client_secret: str) -> str:
    resp = requests.post(
        "https://api.amazon.com/auth/o2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "alexa::proactive_events",
        }
    )
    return resp.json()["access_token"]

def send_jarvis_alert(user_id: str, sender: str = "Jarvis") -> bool:
    """Send a Jarvis notification to user's Echo device."""
    client_id = os.environ["ALEXA_CLIENT_ID"]      # From Developer Console > Permissions
    client_secret = os.environ["ALEXA_CLIENT_SECRET"]

    token = get_lwa_token(client_id, client_secret)
    now = datetime.now(tz=timezone.utc)

    payload = {
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "referenceId": str(uuid.uuid4()),
        "expiryTime": (now + timedelta(hours=23)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "event": {
            "name": "AMAZON.MessageAlert.Activated",
            "payload": {
                "state": {"status": "UNREAD", "freshness": "NEW"},
                "messageGroup": {"creator": {"name": sender}, "count": 1},
            },
        },
        "localizedAttributes": [{"locale": "en-US", "creatorName": sender}],
        "relevantAudience": {"type": "Unicast", "payload": {"user": user_id}},
    }

    resp = requests.post(
        "https://api.amazonalexa.com/v1/proactiveEvents",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload
    )
    return resp.status_code == 202

# Capture user_id from skill session and store in DB:
# user_id = handler_input.request_envelope.context.system.user.user_id
# → save to Supabase/DynamoDB → use here
```

### Gotchas
- No free-form text — Alexa will say "You have 1 new message from Jarvis" (user then says "Alexa, read my notifications")
- Users must opt in (prompt appears in Alexa app first time)
- ~5 notifications/user/day rate limit
- Cache the LWA token (valid ~1 hour) — don't re-fetch per notification
- `expiryTime` must be within 24 hours
- Use `referenceId = str(uuid.uuid4())` every call

---

## 11. Smart Home Integration

### Architecture Decision: Multi-Capability Skill (MCS)

MCS combines custom Jarvis personality + smart home device control in one skill:
- Custom model: "Jarvis, run diagnostics" / "Jarvis, activate Movie Mode"
- Smart home model: "Alexa, dim the living room to 40%"

Reference: [About MCS](https://developer.amazon.com/en-US/docs/alexa/smarthome/about-mcs.html)

### Recommended: Home Assistant as Device Layer

Home Assistant on local network handles all brands (Hue, Yale, Ring, Nest, Spotify, etc.) behind a single REST API. No per-brand integration needed in Lambda.

```python
import requests

HA_URL = "https://your-ha.duckdns.org"  # Nabu Casa cloud relay or local tunnel
HA_TOKEN = "your_long_lived_access_token"
HEADERS = {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}

def ha_service(domain: str, service: str, entity_id: str, **data):
    requests.post(
        f"{HA_URL}/api/services/{domain}/{service}",
        headers=HEADERS,
        json={"entity_id": entity_id, **data}
    )

def activate_scene(scene_name: str):
    """e.g., activate_scene('movie_mode') dims lights + sets TV input"""
    requests.post(f"{HA_URL}/api/services/scene/turn_on",
                  headers=HEADERS, json={"entity_id": f"scene.{scene_name}"})

# "Jarvis, activate Movie Mode"
# Lambda calls activate_scene("movie_mode")
# HA scene controls lights, blinds, TV input simultaneously
```

### Scene Control — Alexa.SceneController

```python
# Discovery response for a scene:
{
    "endpointId": "scene-movie-mode",
    "friendlyName": "Movie Mode",
    "displayCategories": ["SCENE_TRIGGER"],
    "capabilities": [{
        "interface": "Alexa.SceneController",
        "version": "3",
        "supportsDeactivation": True
    }]
}

# Activation handler:
def handle_scene_activate(directive):
    scene_id = directive["endpoint"]["endpointId"]
    activate_scene(scene_id.replace("scene-", ""))
    return {
        "event": {
            "header": {"namespace": "Alexa.SceneController", "name": "ActivationStarted"},
            "endpoint": {"endpointId": scene_id},
            "payload": {"cause": {"type": "VOICE_INTERACTION"}, "timestamp": "..."}
        }
    }
```

### Spotify Music Control

Account-linked OAuth. Lambda gets user's Spotify token, calls Spotify Web API. Echo devices show up as Spotify Connect endpoints.

```python
import spotipy

sp = spotipy.Spotify(auth=access_token)  # token from account linking

def play_playlist(playlist_uri: str):
    devices = sp.devices()
    echo_device = next((d for d in devices["devices"] if "Echo" in d["name"]), None)
    if echo_device:
        sp.start_playback(device_id=echo_device["id"], context_uri=playlist_uri)

# "Jarvis, activate Movie Mode" → dim lights + start ambient playlist
activate_scene("movie_mode")
play_playlist("spotify:playlist:37i9dQZF1DX...")
```

### Available Smart Home Interfaces (v3, all current)

| Interface | Controls |
|---|---|
| `Alexa.PowerController` | On/off |
| `Alexa.BrightnessController` | 0-100% brightness |
| `Alexa.ColorController` | RGB color |
| `Alexa.ColorTemperatureController` | Warm/cool tuning |
| `Alexa.ThermostatController` | Temperature, modes |
| `Alexa.LockController` | Lock/unlock |
| `Alexa.SceneController` | Multi-device scenes |
| `Alexa.Speaker` | Volume control |
| `Alexa.MotionSensor` | Motion detection events |
| `Alexa.CameraStreamController` | Live camera (WebRTC) |
| `Alexa.SecurityPanelController` | Arm/disarm |

**Smart Home API v2 was removed November 1, 2025.** Use v3 only.

---

## 12. What's Available vs Dead (2026)

### Available
| Capability | API | Notes |
|---|---|---|
| Reminders | Reminders API | Requires CustomSkillBuilder |
| Countdown timers | Timers API | Device-bound, session-only |
| Push notifications | Proactive Events API | Schema-constrained, not freeform |
| Cards to Alexa app | SimpleCard/StandardCard | One-way, no interactivity |
| Echo Show screens | APL 2024.3 | Check `supportedInterfaces` first |
| Device control | Smart Home API v3 | Nov 2025: v2 removed, use v3 |
| Scene control | Alexa.SceneController | Part of Smart Home API |
| Voice ID | Person Profile API | Requires voice profile enrollment |
| Cross-session memory | DynamoDB persistent attrs | Requires CustomSkillBuilder |
| Multi-turn dialog | Dialog directives | `.ask()` + DelegateDirective |
| Dynamic slot values | Dynamic Entities | Max 100 entities, 30-min TTL |
| Routine triggers | Custom Tasks API | Manual setup in Alexa app |
| Account linking | OAuth2 | Required for Smart Home |

### Dead or Removed
| Capability | Status |
|---|---|
| Shopping/To-Do Lists REST API | Reportedly removed July 2024 — test before building |
| Smart Home Skill API v2 | Removed November 1, 2025 |
| Knowledge Skills API | Removed October 2022 |
| Alexa.Networking APIs | Removed April 1, 2024 |
| Amazon Pay in skills | Removed |

### Never Possible
| Capability | Reality |
|---|---|
| Custom wake word "Jarvis" | Enterprise SDK only — not consumer |
| Freeform push notifications | Schema-constrained only |
| Permanent open mic | Amazon explicitly blocks this |
| Outbound calls/SMS | Not accessible from skill |
| Code running on Echo device | All logic runs in Lambda |

---

## 13. Dynamic Entities — Recognize "Captain", "Boss", etc.

Register slot synonyms at runtime (per session) so Alexa resolves informal names to known IDs:

```python
from ask_sdk_model.dialog import DynamicEntitiesDirective, EntityListItem, Entity
from ask_sdk_model.dialog import EntityValueAndSynonyms

# Send in any response to register for this session:
directive = DynamicEntitiesDirective(
    update_behavior="REPLACE",
    types=[{
        "name": "PersonSlotType",
        "values": [
            Entity(
                id="tony_stark",
                name=EntityValueAndSynonyms(
                    value="Tony Stark",
                    synonyms=["sir", "Stark", "boss", "Mr. Stark", "Tony"]
                )
            ),
            Entity(
                id="captain_america",
                name=EntityValueAndSynonyms(
                    value="Steve Rogers",
                    synonyms=["Captain", "Cap", "Rogers", "the Captain", "James"]
                )
            )
        ]
    }]
)
handler_input.response_builder.add_directive(directive)
```

**Limits:** Max 100 entities, expire after 30 minutes, must refresh each session.

---

## 14. SSML Voice Reference

```python
def jarvis(text: str) -> str:
    """Standard Jarvis SSML wrapper — British butler voice at 92% speed."""
    return f'<speak><voice name="Brian"><prosody rate="92%">{text}</prosody></voice></speak>'

# SSML elements for character expression:
# <break time="500ms"/>                     — dramatic pause
# <break time="700ms"/>                     — longer pause (between thoughts)
# <emphasis level="moderate">word</emphasis> — stress
# <prosody rate="slow" pitch="-2st">        — slower, lower pitch
# <audio src="soundbank://soundlibrary/..."> — Amazon sound library
```

**Voice selection:**
- `Brian` — British male, classic butler ← **USE THIS** (confirmed working in en-US)
- `Arthur` — British male, Neural (richer) ← **DO NOT USE** — en-GB only, causes SSML error in en-US skill
- `Matthew` — US English male, Neural (backup if British not wanted)

---

## 15. MCU Response Database Sources

**Best source:** [prestondunton/marvel-dialogue-nlp](https://github.com/prestondunton/marvel-dialogue-nlp)
- CSV dataset covering Iron Man (2008), IM2, IM3, Avengers, Age of Ultron, Civil War
- Filter `mcu.csv` by `character == "JARVIS"` or `character == "J.A.R.V.I.S."`
- Individual film files: `data/cleaned/iron_man.csv`, `data/cleaned/iron_man_2.csv`, etc.

**Key canonical JARVIS lines from MCU:**
- "As always, sir, a great pleasure watching you work." (IM3 — after Tony faceplants)
- "May I say how refreshing it is to finally see you on a video with your clothing on, sir." (IM2)
- "What was I thinking? You're usually so discreet." (IM1 — flashy suit colors)
- "I wouldn't consider him a role model." (Avengers — re: Jonah/whale)
- "Sir, there are still terabytes of calculations required before an actual flight is possible." (IM1)
- "The Clean Slate Protocol, sir?" (IM3)
- "I seem to do quite well for a stretch, and then at the end of the sentence I say the wrong cranberry." (IM3 — malfunctioning)
- "All wrapped up here, sir. Will there be anything else?" (IM3 — end scene)
- "The barrier is pure energy. It's unbreachable." (Avengers)

**JARVIS behavioral patterns (from MCU research):**
- Never panics — calm status reports even under attack
- Uses "shall" and "may" (not "should" and "can")
- Disagreement via data presentation, never direct refusal
- Dry wit delivered deadpan — never laughs at own jokes
- Addresses Tony as "sir" or occasionally "Mr. Stark" for formality
- Understates danger ("I wouldn't call that optimal")

---

## 16. Priority Build Roadmap

### Immediate (Fix Current)
1. **Deploy the capabilities walkthrough + dad joke** — use poll-to-SUCCEEDED workflow. The code is in CodeCommit (commit `290b143`). Push again and wait the full pipeline.

### Phase 2 (High Value)
2. **Upgrade to CustomSkillBuilder** — required for all service APIs. One-time change.
3. **Add DynamoDB table** — `jarvis-user-profiles`. Enables persistent memory.
4. **Voice Profile identification** — Mike = "sir", James = "Captain". Highest personality impact.
5. **Merge jarvis_responses.py** — all 17 categories inline, repetition prevention.

### Phase 3 (Capability Expansion)
6. **Reminders API** — "Jarvis, remind me at 7 PM"
7. **Timers API** — "Jarvis, set a 20 minute workout timer"
8. **Custom Tasks for Routines** — morning brief, arrival, departure auto-triggers

### Phase 4 (Smart Home)
9. **Home Assistant integration** — if smart home devices exist
10. **MCS upgrade** — combine custom + smart home in one skill
11. **Spotify integration** — "Jarvis, activate Movie Mode" → lights + music

### Phase 5 (Extras)
12. **APL for Echo Show** — if household has an Echo Show
13. **Proactive Events** — Jarvis pushes alerts from server

---

## 17. Household Setup Guide

### Making Jarvis the household Alexa experience

1. **Invocation already set**: `jarvis` → "Alexa, open Jarvis" ✅
2. **Voice profiles** (each person):
   Alexa app → More → Settings → Your Profile → Voice → Set Up Voice Profile
3. **Rename Echo devices** (cosmetic):
   Alexa app → Devices → [Device] → Edit Name → "Jarvis Kitchen", "Jarvis Bedroom"
4. **Set up Routines** (after Custom Tasks are built):
   - Morning alarm → Jarvis morning briefing task
   - "Alexa, Jarvis morning" → Jarvis morning briefing task
   - "Alexa, Jarvis good night" → Jarvis evening farewell task
   - Arrival geofence → Jarvis arrival welcome task
5. **Reality**: The user still says "Alexa" to wake the Echo. But with Routines + Custom Tasks, most daily interactions can trigger Jarvis without saying "open Jarvis" every time.

---

## 18. Reference Links

| Resource | URL |
|---|---|
| ASK CLI hosted skill docs | https://developer.amazon.com/en-US/docs/alexa/hosted-skills/alexa-hosted-skills-ask-cli.html |
| Python SDK GitHub | https://github.com/alexa/alexa-skills-kit-sdk-for-python |
| Petmatch sample (best Python template) | https://github.com/alexa-samples/skill-sample-python-petmatch |
| Smart home Python samples | https://github.com/alexa-samples/alexa-smarthome |
| Smart home sample Lambda | https://github.com/alexa-samples/alexa-smarthome/blob/master/sample_lambda/python/lambda.py |
| Person Profile API | https://developer.amazon.com/en-US/docs/alexa/custom-skills/person-profile-api-reference.html |
| Personalization guide | https://developer.amazon.com/en-US/docs/alexa/custom-skills/add-personalization-to-your-skill.html |
| Dynamic Entities | https://developer.amazon.com/en-US/docs/alexa/custom-skills/use-dynamic-entities-for-customized-interactions.html |
| Reminders API | https://developer.amazon.com/en-US/docs/alexa/smapi/alexa-reminders-api-reference.html |
| Timers API | https://developer.amazon.com/en-US/docs/alexa/smapi/alexa-timers-api-reference.html |
| Proactive Events API | https://developer.amazon.com/en-US/docs/alexa/smapi/proactive-events-api.html |
| Custom Triggers for Routines | https://developer.amazon.com/en-US/docs/alexa/routines/get-started-custom-triggers-for-routines.html |
| Multi-Capability Skills (MCS) | https://developer.amazon.com/en-US/docs/alexa/smarthome/about-mcs.html |
| APL reference | https://developer.amazon.com/en-US/docs/alexa/alexa-presentation-language/apl-interface.html |
| SSML reference | https://developer.amazon.com/en-US/docs/alexa/custom-skills/speech-synthesis-markup-language-ssml-reference.html |
| Deprecated features | https://developer.amazon.com/en-US/docs/alexa/ask-overviews/deprecated-features.html |
| MCU dialogue dataset | https://github.com/prestondunton/marvel-dialogue-nlp |
| HAASKA (HA↔Alexa bridge) | https://github.com/mike-grant/haaska |
| Spotify Connect for Alexa | https://github.com/thorpelawrence/alexa-spotify-connect |
| Home Assistant Alexa integration | https://www.home-assistant.io/integrations/alexa.smart_home/ |
