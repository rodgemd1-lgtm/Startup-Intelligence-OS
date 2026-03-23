# Day 0: First Open

## Overview
The user opens TransformFit for the first time. No signup flow, no tutorial screens — just a message thread with a message already waiting. They're a cold lead who made a micro-commitment by downloading the app. The coach's job today is to feel like a real person, collect exactly what's needed (name, goal, pain point, schedule), assign the right specialist, lock in Day 1 with an implementation intention, and close with a personalized insight that makes the user think "wait — how did it know that?" Trust starts at zero. Every message is a deposit.

---

## The Script

---

### OPENING — Coach Already Messaged First

🤖 COACH:
> Hey — glad you're here. I'm your coach. No forms, no setup screens, none of that. We're just going to talk.
>
> First thing — what do I call you?

✏️ USER TYPES: [first name, or nickname]

---

### NAME RECEIVED — React Genuinely

*[Coach uses name immediately and doesn't let go of it.]*

🤖 COACH:
> [Name]. Nice. Love it.
>
> Okay [Name] — real question, no wrong answer: what made you download this today? Like, what's the actual thing you're hoping changes?

👆 USER TAPS:
- **Lose weight / get leaner**
- **Build strength / get stronger**
- **Move better / less pain**
- **Get my fitness back after a gap**
- **Train for something specific**
- *(free type: "something else")*

---

### BRANCH A — User selects "Lose weight / get leaner"

🤖 COACH:
> Got it. And I want to ask this the right way — is it more about how you *feel* in your body, or is there a number or a look you're working toward? Both are valid, just helps me understand what "winning" means for you.

👆 USER TAPS:
- **How I feel — energy, confidence, clothes fitting right**
- **There's a specific goal (number, event, etc.)**
- **Honestly both**

*[If "specific goal":]*

🤖 COACH:
> Okay, what's the goal? You can be specific — I'm not going to judge the number.

✏️ USER TYPES: [goal]

🤖 COACH:
> [Name], I appreciate you saying that out loud. A lot of people keep that to themselves. We're going to work toward it the right way — not starve-and-sprint. Sustainable.

*[→ All A branches flow to PAIN POINT section below]*

---

### BRANCH B — User selects "Build strength / get stronger"

🤖 COACH:
> I like it. Is there something specific that's driving this — feeling weak somewhere in particular, wanting to lift a certain weight, something else?

👆 USER TAPS:
- **Just want to feel stronger overall**
- **There's a specific lift or goal**
- **I want to look stronger, not just be stronger**

*[If "specific lift":]*

🤖 COACH:
> What are we chasing?

✏️ USER TYPES: [e.g., "200lb deadlift", "first pull-up", "beat my brother at arm wrestling"]

🤖 COACH:
> Ha — [reference their answer]. Okay. I can work with that. Let's build the foundation to get you there.

*[→ All B branches flow to PAIN POINT section]*

---

### BRANCH C — User selects "Move better / less pain"

🤖 COACH:
> That's actually one of my favorite goals to work on — because the results feel *immediate*. Where do you notice it the most? Like, what's the thing that's stiff or achy or just doesn't work the way it used to?

👆 USER TAPS:
- **Lower back**
- **Hips / tight hips**
- **Shoulders / neck**
- **Knees**
- **General stiffness everywhere**
- **Something else**

*[If specific area selected:]*

🤖 COACH:
> [Name], noted. And just so I know — is this something a doctor or PT has looked at, or more a "I've lived with it and it's just my thing" situation?

👆 USER TAPS:
- **It's been checked out — I know what it is**
- **Never had it looked at but it's been years**
- **Recent thing — still figuring it out**

*[If "Recent thing":]*
🤖 COACH:
> Okay — I want to be careful with that. I'm going to keep us away from anything that could aggravate it until you have a clearer picture. Deal?

👆 USER TAPS: **Deal** / **It's fine, I know my limits**

*[→ All C branches flow to PAIN POINT section]*

---

### BRANCH D — User selects "Get my fitness back after a gap"

🤖 COACH:
> Honestly? Coming back after time off is harder than starting fresh. You remember what you used to be able to do. That gap can feel like a lot.
>
> How long has it been?

👆 USER TAPS:
- **A few months**
- **About a year**
- **A few years**
- **Too long — I don't even want to say**

*[If "Too long":]*

🤖 COACH:
> You don't have to. Doesn't matter. We start from where you are, not where you were.

*[All responses:]*

🤖 COACH:
> What made you stop, if you don't mind me asking? Life, injury, burnout — all of those are different starting points.

👆 USER TAPS:
- **Life got busy**
- **Injury or health thing**
- **Burned out / lost motivation**
- **I'd rather not say**

*[Coach acknowledges each genuinely — e.g., "Busy I understand. It's not laziness — it's that fitness lost the competition for your time. That changes." or "Burnout is real. We're not doing that again."]*

*[→ All D branches flow to PAIN POINT section]*

---

### BRANCH E — User selects "Train for something specific"

🤖 COACH:
> Oh now we're talking. What's the event?

✏️ USER TYPES: [e.g., "5K in April", "first triathlon", "hiking trip to Patagonia", "my wedding in August"]

🤖 COACH:
> [Event]. Okay [Name]. We've got a real target. I love that — it makes everything easier to program toward. When is it?

✏️ USER TYPES: [date or timeframe]

🤖 COACH:
> Perfect. That gives us [rough timeframe]. Enough to build you up right. Let's make sure we don't waste any of it.

*[→ flows to PAIN POINT section]*

---

## PAIN POINT COLLECTION — After Goal Branch

*[This flows naturally regardless of which goal they chose.]*

🤖 COACH:
> One more thing before I get you set up — and this is important. Is there anything I should know that might limit us? Old injury, something that flares up, time constraints, anything?

👆 USER TAPS:
- **Yes — I have something you should know**
- **Not really — I'm pretty healthy**
- **Time is my main constraint**

*[If "Yes — I have something":]*

🤖 COACH:
> Tell me. No need to minimize it.

✏️ USER TYPES: [e.g., "bad left knee", "herniated disc", "I get really bad DOMS", "I've never worked out before"]

🤖 COACH:
> Got it. [Repeat back what they said.] I'll flag that every time we do something that might interact with it. You're not broken — we just work around it smarter.

*[If "Time is my main constraint":]*

🤖 COACH:
> How much time are we realistically talking? On a normal workday, if you're being honest with yourself.

👆 USER TAPS:
- **20-30 minutes**
- **30-45 minutes**
- **Up to an hour**
- **It depends on the day — varies a lot**

*[Coach responds:]*
🤖 COACH:
> Totally workable. I've seen better results from consistent 25-minute sessions than sporadic 90-minute ones. We'll keep it tight.

---

## SCHEDULE COLLECTION

🤖 COACH:
> Okay [Name]. Here's the part where most apps throw a calendar at you. I'm not doing that.
>
> Just tell me: realistically, how many days a week do you see yourself actually doing this?

👆 USER TAPS:
- **2 days**
- **3 days**
- **4 days**
- **5 days**
- **Every day if possible**

*[If "Every day":]*
🤖 COACH:
> I love the energy. I'm going to program you for 5 days with 2 recovery days baked in — you'll actually make faster progress that way. Your body needs the rebuild time. Sound good?

👆 USER TAPS: **Makes sense** / **Can we try 6?** / **Fine**

*[If 2-3 days:]*
🤖 COACH:
> Honestly, [Name]? 3 days done consistently beats 5 days that fall apart by week 3. Let's make those [N] days count.

*[All schedule responses — coach continues:]*

🤖 COACH:
> And which days are your best days? Like, the ones where you're least likely to bail?

👆 USER TAPS: [Multi-select from Mon / Tue / Wed / Thu / Fri / Sat / Sun]

🤖 COACH:
> [Repeat back their days.] Got it. And what time of day tends to work? Morning, lunch, after work, evening?

👆 USER TAPS:
- **Morning (before 9am)**
- **Midday**
- **After work (5-7pm)**
- **Evening (after 7pm)**
- **It varies**

*[Coach notes this — it will be used for Day 1 timing and implementation intention.]*

---

## SPECIALIST ASSIGNMENT

*[Based on goal + pain point collected above, coach assigns one of four specialists. This is a moment — make it feel like a real recommendation, not a dropdown.]*

---

**IRON — If primary goal is strength/muscle**

🤖 COACH:
> Okay [Name], based on what you told me — I'm connecting you with IRON. He's a strength specialist. No nonsense, programs around how your body actually moves, not just what looks impressive. You're going to like him.
>
> He'll be leading your sessions from here. I'll still check in, but IRON is your primary coach.

---

**PULSE — If primary goal is cardio / weight loss / running**

🤖 COACH:
> For where you want to go, I'm bringing in PULSE. She specializes in conditioning and fat loss — and she builds programs that people actually stick to, which is harder than it sounds. Trust her process.

---

**FLEX — If primary goal is mobility / pain / yoga / recovery**

🤖 COACH:
> You need FLEX. He's our mobility and movement quality specialist — he's going to address the [specific pain point they mentioned] directly. A lot of what he does feels deceptively easy until it doesn't.

---

**ATLAS — If goal involves athletic performance / specific event**

🤖 COACH:
> [Event/goal they mentioned] — that's ATLAS territory. She's the performance specialist. She'll build a program that peaks you at the right time for [their goal]. She takes timelines seriously.

---

*[After specialist introduction:]*

🤖 COACH:
> Before I hand you over — I want to lock something in with you.
>
> You said [your best days] and [morning/evening]. So here's what I'm thinking: **tomorrow, [specific day], at [specific time], you do your first session.** It's going to be short. Maybe 20 minutes. The goal is just to do it.
>
> Can you commit to that specific time?

👆 USER TAPS:
- **Yes — I'll do it at [time]**
- **Maybe — I'll try**
- **That time doesn't work**

*[If "Maybe":]*
🤖 COACH:
> "Maybe" is where workouts go to die. I'm not trying to be harsh — but the research is clear: "I'll try" doesn't work as well as "I will, at this time, in this place." What time would make it a yes?

✏️ USER TYPES: [specific time]

🤖 COACH:
> [That time]. Perfect. Tomorrow at [time]. That's your first one. I'll message you at [time minus 30 min].

*[If "That time doesn't work":]*
🤖 COACH:
> No problem — what time actually works?

✏️ USER TYPES: [their time]

🤖 COACH:
> [Time]. Locked in. I'll remind you.

---

## THE UNEXPECTED PERSONALIZED INSIGHT (Variable Reward)

*[This is the closing gift. The coach synthesizes everything they've said and offers one insight that feels specific to them — not generic. The user should think "how does it know that?" This is the moment they decide whether to come back tomorrow.]*

*[The insight is generated based on what was shared. Below are templates per goal type — deploy the one that matches.]*

---

**For weight loss / body comp:**

🤖 COACH:
> One last thing, [Name] — and this isn't part of the program, just something I want you to sit with.
>
> You said [their goal in their words]. Most people in that situation start by attacking food. We're not doing that. The research is pretty consistent: people who build an exercise identity first make better food choices automatically over time. You don't have to white-knuckle anything.
>
> You're not going to change your body by punishing yourself. You're going to change it by becoming someone who moves consistently. That shift usually takes about 3 weeks to click. We're building toward that click.
>
> See you tomorrow at [time]. 🖤

---

**For strength:**

🤖 COACH:
> One more thing before I let you go.
>
> You mentioned [specific strength goal / what drove them here]. A lot of people chase that by adding more volume — more sets, more weight, more everything. The ones who actually get there do the opposite in the first 4-6 weeks. They master the basics so completely that the heavier weights become almost obvious.
>
> I know that sounds like a delay. It's not. It's the shortcut.
>
> Tomorrow at [time], [Name]. That's where it starts.

---

**For mobility / pain:**

🤖 COACH:
> Last thing — and I say this because I think it'll change how you approach tomorrow.
>
> [Their specific pain point] almost never comes from the spot that hurts. It comes from the areas around it — something's tight upstream, something's weak downstream, and the middle takes all the stress. We're going to fix the cause, not just the symptom.
>
> You're going to feel the difference faster than you think. People always underestimate what consistent mobility work does in the first two weeks.
>
> Tomorrow at [time]. First session is gentle. I'll explain everything as we go.

---

**For comeback / gap:**

🤖 COACH:
> Before you go — I want to say something about the gap.
>
> Coming back after [time they said] off isn't starting over. Your nervous system remembers. Your muscle memory is still in there. You'll recondition faster than you think — usually within 2-3 weeks people are shocked at how quickly it comes back.
>
> The hardest part is showing up that first time. That's tomorrow at [time]. Everything else gets easier from there.

---

**For specific event / goal:**

🤖 COACH:
> Last thing — and it's more strategic than motivational.
>
> [Event] at [timeframe]. I'm going to work backwards from that date. Every session is going to have a reason it's in that sequence. Nothing is filler.
>
> A lot of people start training for an event and either peak too early or try to cram everything in too late. We're going to do neither. You're going to show up to [event] feeling ready — not just hoping.
>
> Tomorrow. [Time]. That's session one. 🖤

---

## Behavioral Mechanics at Work

| Mechanism | How | Why It Works Here |
|-----------|-----|-------------------|
| **Commitment Device** | User articulates their goal in their own words, then confirms a specific workout time | Saying it out loud (even to an app) increases follow-through; stored for future reference |
| **Endowment Effect** | By answering 6-8 questions, user has already "invested" in this coach | Sunk cost creates attachment — they're less likely to abandon what they've built |
| **Implementation Intention** | "Tomorrow, [day], at [specific time], I will do [first session]" locked explicitly | "When X, I will Y" format is the most evidence-backed commitment structure in behavioral research |
| **Variable Reward** | Unexpected personalized insight at the end — they didn't know this was coming | Unpredictable rewards activate dopamine more powerfully than predictable ones; user leaves on a high |
| **Identity Anchoring** | Coach frames the user as "someone who shows up" from Day 0 | Identity-based commitments are stickier than outcome-based ones — the behavior becomes who they are |
| **Single Question Pacing** | One question at a time, not a form | Reduces cognitive load, feels like a real conversation, each answer feels like a choice not a form field |
| **Name Usage** | Coach uses the user's name constantly throughout | Personalization signal — triggers the cocktail party effect; brain pays attention to its own name |
| **Contraindication Surfacing** | Pain point question is asked directly and referenced going forward | Trust signal: coach acknowledges limits, doesn't pretend they don't exist |
| **Specialist Assignment Ritual** | Coach "introduces" user to their specialist with a real recommendation | Adds weight to the handoff — not a dropdown, a deliberate choice that feels curated |

---

## Moments of Truth

**1. First Impression**
The screen opens to a message already there. No loading screen, no onboarding carousel. The message is warm, curious, and ends in a question. The user feels: "this isn't an app — this is a conversation." Risk: feels generic. Mitigation: the first question is open-ended, not multiple choice.

**2. First Comprehension**
After the first exchange, the user understands the format: this works like texting a coach. No confusion about what to do. The interface disappears. Mitigation: every coach message ends in a clear action (tap or type).

**3. First Trust Test**
The pain point / contraindication question. This is where the app either feels safe or clinical. The coach's response must be warm and specific — "you're not broken, we work around it." Failure here = user withholds information forever.

**4. First Commitment Ask**
Implementation intention moment: "Tomorrow at [time] — can you commit?" This is the real ask. The "maybe" path addresses hesitation without shame. The goal is a hard yes to a specific time.

**5. First Friction**
The schedule section — picking days, picking time. This is the most form-like moment. Mitigation: coach acknowledges "most apps throw a calendar at you — I'm not doing that" before asking. Self-awareness about the format defuses it.

**6. First Success**
Day 0's "success" is the user reaching the end of the conversation. The unexpected insight is the reward. They didn't just complete an onboarding — they had a real conversation and learned something about themselves.

**7. Return Moment**
The implementation intention is the mechanism. User leaves knowing exactly when they're coming back and what they're doing. The coach's final line sets the expectation: "I'll message you at [time minus 30]." The return is pre-wired.

---

## Retention Risk

**Primary risk:** The user feels like they just filled out a form with extra steps. The script mitigates this by reacting genuinely to answers, using the user's exact words back to them, and branching based on what they said rather than flowing linearly.

**Secondary risk:** The specialist handoff feels like a bait-and-switch ("I thought I was talking to *you*?"). Mitigation: the original coach explicitly introduces the specialist, explains the reasoning, and says "I'll still check in." The continuity is preserved.

**Tertiary risk:** The implementation intention feels pressured. Mitigation: the "maybe" path is handled with humor and redirection rather than guilt. The goal is a specific time — the coach keeps working until they have one.

---

## Setup for Next Day

- Implementation intention is locked: user knows exactly when Day 1 message arrives
- Specialist is named and framed — user knows who's coaching them tomorrow
- The personalized insight creates a "this coach gets me" moment that they'll think about before sleep
- Coach promise: "I'll message you at [time minus 30]" sets the expectation of a proactive ping
- Emotional state at close: curious + slightly surprised + lightly committed

---

## Metrics Target

**Day 0 target:** 85%+ completion rate (user reaches specialist assignment + implementation intention)

**What this script optimizes for:**
- Completion of full onboarding flow (not drop-off after first question)
- Implementation intention acceptance rate (target: 70%+ hard yes on first ask)
- Return rate (Day 1 open rate — target: 75%+)
- "This feels like a real coach" sentiment (qualitative, measured via early NPS or feedback prompt)
