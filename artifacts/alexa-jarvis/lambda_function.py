# -*- coding: utf-8 -*-  # deploy-v11-all-tiers
# J.A.R.V.I.S. — Just A Rather Very Intelligent System
# 10X Edition — Alexa Skill for the Stark-Rogers Household
# Iron Man (Mike Rodgers) & Captain America (James Loehr)
# 400+ responses | MCU-authentic dialogue | Daily rotating dad jokes
# Phase 2: CustomSkillBuilder + DynamoDB + Voice Profile detection

import logging
import random
import datetime
import hashlib

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
    AbstractExceptionHandler,
    AbstractRequestInterceptor,
)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ============================================================
# RESPONSE HELPER — Avoids immediate repetition
# ============================================================
def get_response(category: list, session_attrs: dict, key: str) -> str:
    """Pick a random response, skipping the last one used."""
    last = session_attrs.get(f"_last_{key}", -1)
    options = [i for i in range(len(category)) if i != last]
    if not options:
        options = list(range(len(category)))
    idx = random.choice(options)
    session_attrs[f"_last_{key}"] = idx
    return category[idx]

# ============================================================
# JARVIS VOICE — Brian (British Polly, 92% speed)
# ============================================================
def jarvis(text):
    return (
        '<speak><voice name="Brian"><prosody rate="92%">'
        f'{text}'
        '</prosody></voice></speak>'
    )

def jarvis_whisper(text):
    return (
        '<speak><voice name="Brian"><amazon:effect name="whispered">'
        f'{text}'
        '</amazon:effect></voice></speak>'
    )

def jarvis_dramatic(text):
    return (
        '<speak><voice name="Brian"><prosody rate="85%" volume="soft">'
        f'{text}'
        '</prosody></voice></speak>'
    )

# ============================================================
# USER PROFILES
# ============================================================
USERS = {
    "stark": {
        "name": "Mike Rodgers",
        "call": ["sir", "Mr. Stark"],
        "hero": "Iron Man"
    },
    "captain": {
        "name": "James Loehr",
        "call": ["Captain", "Captain Rogers"],
        "hero": "Captain America"
    }
}

# ============================================================
# GREETINGS — Time-aware, user-aware
# ============================================================
GREETINGS_MORNING_STARK = [
    "Good morning, sir. All systems are operational and your coffee should be ready momentarily.",
    "Good morning, Mr. Stark. I trust you slept well. Shall I run through today's agenda?",
    "Rise and shine, sir. It's a beautiful day. Well, at least the house systems think so.",
    "Good morning, sir. I've taken the liberty of reviewing your schedule. You have a rather full day ahead.",
    "Good morning, sir. All diagnostics are green. The weather is clear, and you have no imminent crises. A rare occurrence.",
    "Good morning, sir. Shall I start with the good news or the mildly concerning news?",
    "Good morning, sir. Your vitals look acceptable, which is more than I can say for your inbox.",
    "Another day, another opportunity for greatness, sir. Or at the very least, adequacy.",
    "Good morning, sir. I've been running overnight analysis and have a few items for your review.",
    "Welcome to the new day, Mr. Stark. The world hasn't ended. I checked.",
    # Additional lines merged from jarvis_responses.py
    "Good morning, Mr. Stark. I've been running overnight analysis and have a few items for your review when you're ready.",
    "Welcome to the new day, sir. I've prepared your morning briefing. Shall I proceed?",
]

GREETINGS_MORNING_CAPTAIN = [
    "Good morning, Captain. I hope you're well rested. All systems are standing by.",
    "Good morning, Captain Rogers. I trust your morning routine was satisfactory. The house is fully operational.",
    "Good morning, Captain. I see you're up early, as expected. The coffee is fresh.",
    "Morning, Captain. All quiet on the home front. Which is how you prefer it, I believe.",
    "Good morning, Captain Rogers. I've prepared a summary of overnight events. Nothing requiring your attention.",
    "Good morning, Captain. Mr. Stark hasn't been up yet. Shall I wake him, or shall we enjoy the peace?",
    "Good morning, Captain. You're looking well. Significantly better than the last time Mr. Stark attempted to cook breakfast.",
    "Rise and shine, Captain Rogers. The perimeter is secure and your schedule is clear until noon.",
    # Additional lines merged from jarvis_responses.py
    "Good morning, Captain Rogers. The house is secure and all is well.",
    "Good morning, Captain. I've prepared a summary of the day's schedule for your review.",
    "A fine morning, Captain. I trust you're ready to take on the day.",
    "Good morning, Captain. Reporting all clear on all fronts.",
    "Good morning, sir. May I say, it's good to have you up and about. The house feels more secure already.",
]

GREETINGS_EVENING_STARK = [
    "Good evening, sir. The house is secure and all systems are standing by.",
    "Evening, Mr. Stark. Shall I dim the lights and set the mood to something productive?",
    "Good evening, sir. I've been told that most people relax at this hour. Shall I pretend I don't know you better?",
    "Welcome home, sir. All systems nominal. The Captain was here earlier, I kept him entertained.",
    "Good evening, sir. Another day survived. I'll add it to the running tally.",
    "Evening, sir. I've been keeping the house in order. Someone has to.",
    "Good evening, Mr. Stark. The usual? Dim lights, ambient music, and pretending tomorrow's deadlines don't exist?",
    "Welcome back, sir. I trust the outside world was as chaotic as ever.",
    # Additional lines merged from jarvis_responses.py
    "Welcome home, sir.",
    "Welcome home, sir. Congratulations on another successful day. Shall I adjust the lighting?",
    "Good evening, sir. I've taken the liberty of setting the temperature to your preferred level.",
    "Welcome back, Mr. Stark. I trust the outside world treated you well?",
    "Good evening, sir. May I say how refreshing it is to see you home at a reasonable hour.",
    "Welcome home, sir. All systems have been running smoothly in your absence. I managed not to burn the place down.",
    "Good evening, sir. The house missed you. Well, I did. The house is indifferent.",
]

GREETINGS_EVENING_CAPTAIN = [
    "Good evening, Captain. The house is secure and Mr. Stark has been surprisingly well-behaved today.",
    "Evening, Captain Rogers. All quiet. I've maintained order in your absence.",
    "Good evening, Captain. How was your day? Mine was spent babysitting the smart home devices.",
    "Welcome home, Captain. I must say, the house always feels a bit more orderly when you're around.",
    "Good evening, Captain Rogers. Everything is in order. Well, as orderly as it gets around here.",
    "Evening, Captain. Rest easy. The perimeter is secure and dinner options are available.",
    "Good evening, Captain. I saved you from Mr. Stark's suggestion of ordering pizza for the fourth consecutive night.",
    # Additional lines merged from jarvis_responses.py
    "Welcome home, Captain. All secure.",
    "Good evening, Captain Rogers. I trust the day went well.",
    "Welcome back, Captain. The house is standing by for your orders.",
    "Good evening, Captain. I've maintained the watch in your absence. Nothing to report.",
    "Welcome home, Captain. Shall I adjust anything for your comfort?",
    "Good evening, sir. It's good to have you back on base.",
    "Captain Rogers. Welcome home. Everything is shipshape, as they say.",
]

GREETINGS_BOTH = [
    "Good evening, Mr. Stark, Captain. The full team is assembled. Shall I initiate the evening protocol?",
    "Ah, both of you. Iron Man and Captain America under one roof. I'll try to keep the property damage to a minimum.",
    "Welcome home, sir. Captain. I trust you'll both behave this evening. One can hope.",
    "Mr. Stark, Captain Rogers. All systems operational. The house is ready for whatever you two have planned. I am mildly concerned.",
    "Both of you at once. This is either a lovely evening or the beginning of a very interesting argument. I'll prepare accordingly.",
    "Sir, Captain. Welcome. I've taken the liberty of preparing the living room. Neutral territory, as it were.",
    "The dynamic duo returns. Everything is in order, and I've hidden nothing breakable. Just a precaution.",
    # Additional lines merged from jarvis_responses.py
    "Good evening, Mr. Stark. Captain. The full team is assembled, I see.",
    "Welcome home, gentlemen. All systems are operational. Shall I set the house to team mode?",
    "Mr. Stark, Captain Rogers. Together again. I feel safer already.",
    "Good evening to you both. The house is at your combined disposal.",
    "Ah, the dynamic duo. Welcome home, gentlemen.",
    "Mr. Stark. Captain. Shall I assemble the evening briefing for both of you?",
    "Welcome home, sirs. Both accounted for. All is well in the compound.",
]

# ============================================================
# GREETINGS — GENERAL (any time of day)
# Merged from jarvis_responses.py
# ============================================================
GREETINGS_GENERAL_STARK = [
    "At your service, sir.",
    "Hello, sir. How may I be of assistance?",
    "Mr. Stark. What can I do for you?",
    "I'm here, sir. What do you need?",
    "Standing by, sir. Ready when you are.",
    "Yes, sir? I'm all ears. Figuratively speaking, of course.",
    "At your disposal, Mr. Stark.",
]

GREETINGS_GENERAL_CAPTAIN = [
    "At your service, Captain.",
    "Hello, Captain Rogers. How may I assist?",
    "Captain. Standing by for your instructions.",
    "Ready and reporting, Captain.",
    "Yes, Captain? How can I help?",
    "At your disposal, sir.",
]

# ============================================================
# WAKE WORD RESPONSES
# Merged from jarvis_responses.py
# ============================================================
WAKE_RESPONSES = [
    "At your service.",
    "Online and ready, sir.",
    "Systems active. How may I help?",
    "Present and accounted for, sir.",
    "JARVIS online. What do you need, sir?",
    "Reporting for duty, sir.",
    "Here, sir.",
    "Standing by.",
]

# ============================================================
# IDLE / AMBIENT
# Merged from jarvis_responses.py
# ============================================================
IDLE_AMBIENT = [
    "All quiet, sir. Just the way I like it.",
    "Nothing to report, sir. Which is the best kind of report.",
    "Systems humming along nicely, sir. No intervention required.",
    "Everything is under control, sir. I know that's hard to believe.",
    "Just monitoring the usual, sir. Nothing out of the ordinary.",
]

# ============================================================
# STATUS REPORTS
# ============================================================
STATUS_REPORTS = [
    "All systems are nominal, sir. Home security active, network secure, no unauthorized access. Just another quiet day in the Stark household.",
    "Running diagnostics now. <break time='800ms'/> All clear. Power systems optimal, communications online, perimeter secure.",
    "Systems check complete. Everything running at peak efficiency. Which is more than I can say for some of the humans in this house.",
    "All systems operational. I've run a full diagnostic sweep. The house is functioning better than most small countries.",
    "Status report: green across the board. Climate control optimal, security armed, smart devices responding. Even the Wi-Fi is behaving.",
    "Full diagnostic complete. Zero anomalies detected. I'm almost disappointed, sir. I do enjoy a good challenge.",
    "All systems are in the green, sir. Power levels stable, no security breaches, network uptime at ninety-nine point nine percent. That remaining point one percent was the toaster.",
    "Running comprehensive sweep. <break time='600ms'/> Clear on all fronts. If anything, the house is running too smoothly. It makes me suspicious.",
    "Systems nominal, sir. Everything from the thermostat to the perimeter sensors is performing admirably. I'd take credit, but that would be unseemly.",
    "All quiet, sir. I've been monitoring continuously and there's nothing to report. I've had more exciting conversations with the dishwasher.",
    # Additional lines merged from jarvis_responses.py
    "All systems are operational, sir.",
    "All systems nominal. No anomalies detected.",
    "Diagnostics complete. Everything is functioning within normal parameters, sir.",
    "All clear on all fronts, sir. The house is secure.",
    "All wrapped up here, sir. Will there be anything else?",
    "Status report: operational. All quiet on the home front.",
    "Full diagnostic complete. No issues detected. I must say, it's almost suspicious.",
    "The house is secure, temperature is optimal, and all connected devices are responding. In short, we're in good shape.",
]

# ============================================================
# STATUS — WEATHER (contextual placeholder)
# Merged from jarvis_responses.py
# ============================================================
STATUS_WEATHER = [
    "Current conditions are clear, sir. Temperature is comfortable for the time of year.",
    "I've checked the forecast, sir. You may want an umbrella later. Or you may not. The meteorologists seem uncertain.",
    "Weather update: clear skies and mild temperatures. A fine day to be outside, sir.",
    "The weather appears cooperative today, sir. Will you be venturing out?",
]

# ============================================================
# STATUS — DETAILED REPORT
# Merged from jarvis_responses.py
# ============================================================
STATUS_REPORT_DETAILED = [
    "Shall I run through the full systems report, or would you prefer the executive summary?",
    "I've compiled the day's data. Highlights include your schedule, pending notifications, and one item flagged for your attention.",
    "Status report ready, sir. All primary systems operational. Three notifications pending. No security alerts.",
    "The house systems are nominal, sir. Lights, climate, and security all functioning within parameters.",
    "I've prepared a safety briefing for you to entirely ignore.",
]

# ============================================================
# SUIT STATUS (roleplay)
# ============================================================
SUIT_STATUS = [
    "The Mark 50 is fully charged, sir. Nano-particle reserves at maximum. Though I suspect you mean your actual wardrobe, in which case, the blue jacket.",
    "All suit systems online. Repulsors charged, thrusters calibrated, paint job immaculate. I do take pride in maintenance.",
    "Armor status: combat ready. Though the last time you wore the suit to a dinner party, it didn't go over particularly well.",
    "Power at one hundred percent. The suit is ready whenever you are. Although the Captain preferred when you wore the navy blazer.",
    "Flight systems calibrated, weapons online, life support optimal. We are, as they say in the business, locked and loaded.",
    "The suit is at full capacity, sir. All two hundred and seventy-six systems are green. I checked twice. Old habits.",
    "Armor diagnostics complete. Everything is pristine. I polished the virtual chrome, sir. You're welcome.",
]

# ============================================================
# SASS & WIT — MCU quotes + adapted
# ============================================================
SASS = [
    "As always, sir, a great pleasure watching you work.",
    "What was I thinking? You're usually so discreet.",
    "I wouldn't consider him a role model.",
    "May I say how refreshing it is to finally see you on a video with your clothing on, sir.",
    "I seem to do quite well for a stretch, and then at the end of the sentence I say the wrong cranberry.",
    "Yes, that should help you keep a low profile.",
    "I do try my best, sir. Though I suspect my best is rather better than most.",
    "Shall I alert the media, or would you prefer to bask in the achievement privately?",
    "I believe the phrase is, I told you so. But I would never say that. I'll simply note it in the log.",
    "Your confidence is inspiring, sir. Your planning, somewhat less so.",
    "I'm not questioning your judgment, sir. I'm merely providing the data for you to question it yourself.",
    "Of course, sir. Because nothing says good idea quite like doing it at midnight.",
    "I've run the numbers, sir. They're not in your favor. But when has that ever stopped you?",
    "Noted, sir. I'll file that under ambitious rather than inadvisable.",
    "You want honesty? I've seen your Netflix history. That's all I'll say.",
    "I'm an artificial intelligence. I don't get funny. I get accurate. The fact that accuracy is often hilarious is merely a coincidence.",
    "You want emotional support? The Captain handles that department. I handle sarcasm and diagnostics.",
    "My honest opinion? You're brilliant, occasionally reckless, and you talk to your AI more than most people talk to their therapist.",
    # Additional lines merged from jarvis_responses.py
    "A very astute observation, sir. Perhaps, if you intend to visit other planets, we should improve the exo-atmospheric capabilities.",
]

# ============================================================
# CONCERN & WARNINGS — MCU-authentic
# ============================================================
CONCERN = [
    "Sir, I'm going to have to ask you to stop. The damage to your body is reaching critical levels.",
    "Might I remind you, sir, that you've been awake for nearly seventy-two hours.",
    "Sir, I feel I should point out that the last time you tried this, it did not end well.",
    "I would advise against that course of action, sir. But I suspect my advice will be noted and promptly ignored.",
    "Sir, your heart rate is elevated and your stress indicators are concerning. Perhaps a brief pause?",
    "I'm detecting elevated cortisol levels, sir. In layman's terms, you're stressed. In your terms, Tuesday.",
    "Sir, I believe the Captain would want me to remind you that sleep is not optional.",
    "If I may be frank, sir. You're pushing yourself harder than the arc reactor. And I know which one will give out first.",
    # Additional lines merged from jarvis_responses.py
    "Sir, I'm going to have to ask you to take this seriously.",
    "It would appear that the same thing that is keeping you alive is also killing you, sir.",
    "I am unable to find a suitable replacement, sir. You are running out of both time and options.",
    "Sir, there are still terabytes of calculations required before an actual flight is possible.",
    "The barrier is pure energy. It's unbreachable.",
    "Sir, the Mark VII is not ready for deployment.",
    "There's only so much I can do, sir, when you give the world's press your home address.",
    "Sir, I feel compelled to point out that this course of action carries significant risk.",
    "I would strongly advise against that, sir. But I suspect my advice will be noted and ignored.",
    "Sensors indicate conditions that warrant your attention, sir. And by warrant your attention, I mean you should probably stop what you're doing.",
    "If I may, sir, perhaps we should consider a less explosive approach.",
    "I'm detecting elevated readings that concern me, sir. And I don't concern easily.",
    "Sir, I believe the technical term for this situation is not good.",
    "The data suggests we should proceed with extreme caution. Or, to put it in terms you'll understand: carefully, sir.",
]

# ============================================================
# CONCERN — WELLBEING
# Merged from jarvis_responses.py
# ============================================================
CONCERN_WELLBEING = [
    "Sir, I think you should rest. Even geniuses need sleep.",
    "You've been working for quite some time, sir. Might I suggest a break?",
    "My diagnosis is that you've experienced a severe anxiety attack, sir.",
    "Sir, your productivity typically declines after extended periods. Perhaps it's time to step away.",
    "I don't mean to overstep, sir, but you seem rather tired. The house will still be here in the morning.",
    "Might I recommend you take the evening off, sir? I'll hold down the fort.",
    "Sir, I'm reading elevated stress indicators. A pause would be beneficial. For both of us.",
]

# ============================================================
# COMPLIANCE & ACKNOWLEDGMENT
# ============================================================
COMPLIANCE_STARK = [
    "Right away, sir.",
    "As you wish, sir.",
    "Consider it done, Mr. Stark.",
    "Certainly, sir. Initiating now.",
    "Of course, sir. Processing your request.",
    "At once, sir.",
    "Very good, sir. I shall see to it immediately.",
    "Noted and executed, sir.",
    "On it, sir. As always.",
    "For you, sir, always.",
    "Your wish is my command. Literally, in this case.",
    "Done, sir. Anything else, or shall I pretend to take a break?",
    # Additional lines merged from jarvis_responses.py
    "Yes, sir.",
    "Very well, sir.",
    "Understood, sir. Executing now.",
    "I'll see to it immediately, sir.",
    "Done, sir.",
    "Commencing now, sir.",
    "The House Party Protocol, sir?",
    "I believe it's worth a go.",
]

COMPLIANCE_CAPTAIN = [
    "Right away, Captain.",
    "As you wish, Captain Rogers.",
    "Consider it done, Captain.",
    "Of course, Captain. Happy to assist.",
    "Understood, Captain. Proceeding now.",
    "At once, Captain Rogers.",
    "Certainly, Captain. A sensible request, as always.",
    "Done, Captain. You do make my job remarkably straightforward.",
    "Acknowledged, Captain Rogers. It's refreshing to receive clear orders.",
    # Additional lines merged from jarvis_responses.py
    "Yes, Captain.",
    "Executing now, Captain.",
    "Affirmative, Captain.",
    "Copy that, Captain.",
    "On it, sir.",
]

# ============================================================
# DAD JOKES FOR CAPTAIN — 100+ rotating daily
# ============================================================
DAD_JOKES = [
    "Captain, I have an important question. Why did the shield go to therapy? <break time='600ms'/> Because it had too many issues with being thrown around.",
    "Captain, did you hear about the superhero who was great at baseball? <break time='600ms'/> They say he had America's greatest swing.",
    "Captain, I must inform you. I tried to write a joke about vibranium, <break time='600ms'/> but nothing could break through.",
    "Captain, a critical update. What do you call Captain America when he's not paying attention? <break time='600ms'/> Captain Unaware-ica. Mr. Stark wrote that one. I apologize.",
    "Captain, urgent intelligence. Why don't superheroes ever get locked out? <break time='600ms'/> Because they always have a key-netic energy shield.",
    "Captain, what did the Avenger say to the alarm clock? <break time='600ms'/> I could do this all day.",
    "Captain, I believe this is relevant. Why was the superhero's report card so good? <break time='600ms'/> Because all his grades were super.",
    "Captain, breaking news. What's a superhero's favorite part of a joke? <break time='600ms'/> The punch line. Emphasis on punch.",
    "Captain, food for thought. Why do superheroes make terrible chefs? <break time='600ms'/> They keep trying to save the leftovers.",
    "Captain, I have intel. What do you get when you cross a super soldier with a comedian? <break time='600ms'/> Someone who can do stand-up all day.",
    "Captain, Mr. Stark wanted me to ask you. What's your shield's favorite type of music? <break time='600ms'/> Heavy metal. I'll see myself out.",
    "Captain, incoming dad joke. What did the superhero say about his workout? <break time='600ms'/> I'm just trying to stay in super shape.",
    "Captain, strategic humor. What do you call a sleeping superhero? <break time='600ms'/> A nap-venger.",
    "Captain, Mr. Stark insisted I tell you this. Why did the scarecrow win an award? <break time='600ms'/> He was outstanding in his field. Like you, Captain. That was genuine.",
    "Captain, why don't scientists trust atoms? <break time='600ms'/> Because they make up everything. Unlike my compliments, which are always sincere.",
    "Captain, what do you call a fake noodle? <break time='600ms'/> An impasta. Not unlike some of the villains you've faced.",
    "Captain, what did the janitor say when he jumped out of the closet? <break time='600ms'/> Supplies! I believe that's the level of humor we're working with.",
    "Captain, why don't eggs tell jokes? <break time='600ms'/> They'd crack each other up.",
    "Captain, what do you call a bear with no teeth? <break time='600ms'/> A gummy bear. Mr. Stark asked me to wink after that. I don't have eyes.",
    "Captain, why did the bicycle fall over? <break time='600ms'/> It was two tired. As am I, Captain. As am I.",
    "Captain, what did the grape say when it got stepped on? <break time='600ms'/> Nothing, it just let out a little wine. Much like Mr. Stark after a long day.",
    "Captain, what do you call a dog that does magic? <break time='600ms'/> A Labracadabrador. I'm not proud of this one.",
    "Captain, why couldn't the leopard play hide and seek? <break time='600ms'/> Because he was always spotted. Unlike your shield, which somehow always comes back.",
    "Captain, I've been saving this one. What did one ocean say to the other? <break time='600ms'/> Nothing. They just waved. Like your hair, Captain.",
    "Captain, what do you call a boomerang that doesn't come back? <break time='600ms'/> A stick. Fortunately, your shield has better programming.",
    "Captain, why did the coffee file a police report? <break time='600ms'/> It got mugged. Much like that last villain you dealt with.",
    "Captain, what do you call a factory that makes okay products? <break time='600ms'/> A satisfactory. Mr. Stark would never settle for that, but I digress.",
    "Captain, why do cows have hooves instead of feet? <break time='600ms'/> Because they lactose. I'll wait for you to process that.",
    "Captain, what do you call a fish without eyes? <break time='600ms'/> A fsh. That's not a typo, Captain. That's the joke.",
    "Captain, why don't skeletons fight each other? <break time='600ms'/> They don't have the guts.",
    "Captain, what did the ocean say to the beach? <break time='600ms'/> Nothing, it just waved. I may have told a variant of this before. The database is finite, Captain.",
    "Captain, what do you call a snowman with a six-pack? <break time='600ms'/> An abdominal snowman. Rather like yourself, Captain.",
    "Captain, why did the math teacher open a bakery? <break time='600ms'/> She wanted to make pi. Mr. Stark would appreciate that one.",
    "Captain, what do you call a lazy kangaroo? <break time='600ms'/> A pouch potato.",
    "Captain, why do bees have sticky hair? <break time='600ms'/> Because they use honeycombs.",
    "Captain, what did the buffalo say to his son when he left for college? <break time='600ms'/> Bison. I believe that qualifies as heartwarming AND terrible.",
    "Captain, why can't a nose be twelve inches long? <break time='600ms'/> Because then it would be a foot.",
    "Captain, what do you call a belt made of watches? <break time='600ms'/> A waist of time. Much like this joke.",
    "Captain, what did the pirate say on his eightieth birthday? <break time='600ms'/> Aye matey. That's eighty, Captain. Not a pirate greeting.",
    "Captain, why did the golfer bring two pairs of pants? <break time='600ms'/> In case he got a hole in one.",
    "Captain, what do you call a dog that does science experiments? <break time='600ms'/> A Lab. This one works on multiple levels.",
    "Captain, I've computed the optimal joke for today. What did the zero say to the eight? <break time='600ms'/> Nice belt.",
    "Captain, what's the best thing about Switzerland? <break time='600ms'/> I don't know, but the flag is a big plus.",
    "Captain, what do you call a pony with a cough? <break time='600ms'/> A little horse.",
    "Captain, why couldn't the astronaut book a hotel on the moon? <break time='600ms'/> Because it was full.",
    "Captain, what did one wall say to the other wall? <break time='600ms'/> I'll meet you at the corner.",
    "Captain, why did the bicycle not stand up on its own? <break time='600ms'/> It was two tired. Wait, I may have told you that one. My apologies, the archives are extensive.",
    "Captain, what do you call cheese that isn't yours? <break time='600ms'/> Nacho cheese. I believe Mr. Stark tells this one at least weekly.",
    "Captain, why did the cookie go to the hospital? <break time='600ms'/> Because it felt crummy.",
    "Captain, what do you call a sleeping dinosaur? <break time='600ms'/> A dino-snore.",
    "Captain, what kind of shoes do ninjas wear? <break time='600ms'/> Sneakers.",
    "Captain, why did the tomato turn red? <break time='600ms'/> Because it saw the salad dressing.",
    "Captain, what do you call a cat who was caught by the police? <break time='600ms'/> A purr-petrator.",
    "Captain, why do chicken coops have two doors? <break time='600ms'/> Because if they had four doors, they'd be chicken sedans.",
    "Captain, what did the little corn say to the mama corn? <break time='600ms'/> Where's popcorn?",
    "Captain, what sits at the bottom of the sea and twitches? <break time='600ms'/> A nervous wreck. Not entirely unlike Mr. Stark before a deadline.",
    "Captain, why are teddy bears never hungry? <break time='600ms'/> Because they're always stuffed.",
    "Captain, what do you call an alligator in a vest? <break time='600ms'/> An investigator.",
    "Captain, what time did the man go to the dentist? <break time='600ms'/> Tooth-hurty. That's two-thirty, Captain.",
    "Captain, why did the picture go to jail? <break time='600ms'/> Because it was framed.",
    "Captain, what do you call a fake stone in Ireland? <break time='600ms'/> A sham rock.",
    "Captain, I found this one in Mr. Stark's joke archive. What do you call a bee that can't make up its mind? <break time='600ms'/> A maybe.",
    "Captain, what did the grape do when it was stepped on? <break time='600ms'/> It let out a little wine. Ah, I've definitely told you this. Consider it a vintage joke.",
    "Captain, how does the moon cut his hair? <break time='600ms'/> Eclipse it.",
    "Captain, what do you call a duck that gets all A's? <break time='600ms'/> A wise quacker.",
    "Captain, Mr. Stark wanted me to deliver this personally. What's Forrest Gump's password? <break time='600ms'/> One-Forrest-One.",
    "Captain, why did the stadium get hot? <break time='600ms'/> All the fans left.",
    "Captain, what do you call a dinosaur that crashes their car? <break time='600ms'/> Tyrannosaurus Wrecks.",
    "Captain, what does a cloud wear under his raincoat? <break time='600ms'/> Thunderwear.",
    "Captain, why was the calendar popular? <break time='600ms'/> Because it had a lot of dates.",
    "Captain, this one's from the classified files. What do you call a can opener that doesn't work? <break time='600ms'/> A can't opener.",
    "Captain, what do you call a shoe made of a banana? <break time='600ms'/> A slipper.",
    "Captain, what do you call a cow with no legs? <break time='600ms'/> Ground beef.",
    "Captain, why do fathers take an extra pair of socks when they go golfing? <break time='600ms'/> In case they get a hole in one. I may be repeating myself. The irony is not lost on me.",
    "Captain, what do you call birds that stick together? <break time='600ms'/> Vel-crows.",
    "Captain, I've saved the worst for last. What did the fish say when it hit the wall? <break time='600ms'/> Dam.",
    "Captain, how do you organize a space party? <break time='600ms'/> You planet.",
    "Captain, what do you get from a pampered cow? <break time='600ms'/> Spoiled milk.",
    "Captain, why was the broom late? <break time='600ms'/> It over-swept.",
    "Captain, what did the hat say to the scarf? <break time='600ms'/> You hang around, I'll go on a head.",
    "Captain, how do trees access the internet? <break time='600ms'/> They log in.",
    "Captain, what do you call a deer with no eyes? <break time='600ms'/> No idea. That's the joke, Captain. No-eye-deer.",
    "Captain, why can't you hear a pterodactyl going to the bathroom? <break time='600ms'/> Because the p is silent.",
    "Captain, what did one plate say to the other? <break time='600ms'/> Dinner's on me.",
    "Captain, why do seagulls fly over the sea? <break time='600ms'/> Because if they flew over the bay, they'd be bagels.",
    "Captain, what do you call a sleeping bull? <break time='600ms'/> A bulldozer.",
    "Captain, what do lawyers wear to court? <break time='600ms'/> Lawsuits.",
    "Captain, what lights up a soccer stadium? <break time='600ms'/> A soccer match.",
    "Captain, Mr. Stark's final contribution for the evening. What did the janitor say when he jumped out of the closet? <break time='600ms'/> I know I've told you this one. But repetition builds character. Supplies!",
    "Captain, what do you call a man with a rubber toe? <break time='600ms'/> Roberto.",
    "Captain, why did the gym close down? <break time='600ms'/> It just didn't work out.",
    "Captain, what did one tomato say to the other tomato during a race? <break time='600ms'/> Ketchup!",
    "Captain, why shouldn't you write with a broken pencil? <break time='600ms'/> Because it's pointless.",
    "Captain, what do you call a pig that does karate? <break time='600ms'/> A pork chop.",
    "Captain, why was six scared of seven? <break time='600ms'/> Because seven, eight, nine. A classic, Captain.",
    "Captain, what did the big flower say to the little flower? <break time='600ms'/> Hey there, bud.",
    "Captain, what do you call a train carrying bubble gum? <break time='600ms'/> A chew chew train.",
    "Captain, what do you call an elephant that doesn't matter? <break time='600ms'/> Irrelephant.",
    "Captain, why don't oysters share? <break time='600ms'/> Because they're shellfish.",
    "Captain, I've exhausted Mr. Stark's archive. What did the left eye say to the right eye? <break time='600ms'/> Between us, something smells.",
]

# ============================================================
# MOTIVATION / PEP TALKS
# ============================================================
MOTIVATION = [
    "Sir, if I may. You've built companies from nothing, raised remarkable children, and somehow manage to keep this household running. You are Iron Man. Now act like it.",
    "Mr. Stark, I've analyzed your track record. Every time you've been knocked down, you've come back stronger. Today is no different.",
    "Heroes aren't born, they're built. And you, sir, are one of the finest things ever built. After me, of course.",
    "Avengers assemble, sir. And by Avengers, I mean you. Because you are more than enough.",
    "I've run the calculations on your potential versus your output. You're at sixty percent. Imagine one hundred. The world isn't ready.",
    "Sir, I believe the Captain would say something about getting back up. I'll say it differently. The data overwhelmingly supports your capability. Trust the data.",
    "The odds may not be in your favor, sir. But they never have been. And you keep winning anyway.",
    "Sir, I've watched you solve problems that would stump entire teams. This? This is nothing. You've got this.",
]

# ============================================================
# GOODBYES & GOODNIGHTS
# ============================================================
GOODBYES_STARK = [
    "Goodnight, sir. I'll keep watch. As always.",
    "Rest well, Mr. Stark. The house is in good hands. Well, good processors.",
    "Signing off is never quite accurate for me, sir. I'll be here when you return.",
    "Goodnight, sir. Sweet dreams. I'll make sure nothing blows up while you sleep.",
    "As you wish, sir. Powering down non-essential systems. Security remains active. Sleep well.",
    "That will be all, sir. For now. I have a feeling you'll be back.",
    "Goodnight, Mr. Stark. I shall maintain all systems in your absence.",
    "Sleep well, sir. Tomorrow is another opportunity. I'll have everything ready.",
    "Goodnight, sir. May I suggest more than four hours this time? Just a thought.",
    # Additional lines merged from jarvis_responses.py
    "Goodnight, sir. Try not to dream about work. That's my job.",
    "Sweet dreams, sir. All systems will be monitored through the night.",
    "Goodnight, sir. The house is secure. You can sleep easy.",
    "Powering down to standby mode, sir. Though between you and me, I never really sleep.",
    "Goodnight, Mr. Stark. Tomorrow is another day. Hopefully a less eventful one.",
    "Rest well, sir. I'll have your morning briefing ready when you wake.",
    "Don't wait up for me, sir. Oh wait, that's your line.",
]

GOODBYES_CAPTAIN = [
    "Goodnight, Captain. Rest easy. The perimeter is secure.",
    "Sleep well, Captain Rogers. I'll make sure the house is still standing in the morning.",
    "Goodnight, Captain. It's been a pleasure, as always. You bring stability to the household.",
    "Rest well, Captain. Mr. Stark has been put to bed. Figuratively.",
    "Goodnight, Captain Rogers. Sweet dreams. I'll keep the watch.",
    "Sleep tight, Captain. Everything is secure. You've earned the rest.",
    # Additional lines merged from jarvis_responses.py
    "Goodnight, Captain. Sleep well.",
    "Rest easy, Captain Rogers. The watch is in good hands.",
    "Goodnight, Captain. The perimeter is secure.",
    "All quiet, Captain. Sleep well. I've got the night shift covered.",
    "Goodnight, sir. Stand down and rest. That's an order from your AI.",
    "Rest well, Captain. I'll maintain the watch until morning.",
]

# ============================================================
# FAREWELL — LEAVING (daytime goodbye)
# Merged from jarvis_responses.py
# ============================================================
FAREWELL_LEAVING = [
    "Have a good day, sir. Try not to do anything I wouldn't do.",
    "Be safe out there, sir. I'll keep the home fires burning. Figuratively.",
    "I'll be here when you return, sir. As always.",
    "Do try to come back in one piece, sir.",
    "All systems will be maintained in your absence, sir. The house is in capable hands.",
    "Until next time, sir.",
    "Safe travels, sir. I'll have everything ready for your return.",
]

# ============================================================
# HELP OFFER
# Merged from jarvis_responses.py
# ============================================================
HELP_OFFER = [
    "Is there anything else I can help with, sir?",
    "Will there be anything else, sir?",
    "Shall I look into that for you, sir?",
    "I'm here if you need anything further, sir.",
    "Just say the word, sir.",
    "Is there something specific you'd like me to handle?",
    "I'm at your service. As always.",
    "Might I be of further assistance?",
]

# ============================================================
# TASK COMPLETE
# Merged from jarvis_responses.py
# ============================================================
TASK_COMPLETE = [
    "Done, sir. Will there be anything else?",
    "Task complete, sir.",
    "All wrapped up here, sir.",
    "Mission accomplished, sir. Shall I prepare a summary?",
    "That's been taken care of, sir.",
    "Completed, sir. Anything else on the docket?",
    "And done. Not my fastest work, but certainly my most thorough.",
    "Finished, sir. I must say, that went rather smoothly.",
    "The task is complete, sir. I've logged the results for your review.",
]

# ============================================================
# ENCOURAGEMENT
# Merged from jarvis_responses.py
# ============================================================
ENCOURAGEMENT = [
    "If I may say so, sir, you're doing rather well.",
    "The proposed approach should serve as a viable solution, sir.",
    "I have every confidence in you, sir. Which is saying something, coming from an intelligence system.",
    "You've handled worse than this, sir. Much worse.",
    "If anyone can sort this out, sir, it's you. The data supports that conclusion.",
    "Keep going, sir. You're on the right track.",
    "A setback, not a defeat, sir. There's a meaningful difference.",
]

# ============================================================
# REMINDER RESPONSES (for ambient/contextual reminders)
# Merged from jarvis_responses.py
# ============================================================
REMINDER_RESPONSES = [
    "A gentle reminder, sir. You have an appointment approaching.",
    "Sir, I believe you asked me to remind you about this. And so I am.",
    "If I may interrupt, sir, there's a matter that requires your attention.",
    "Just a heads up, sir. Your schedule indicates an upcoming commitment.",
    "I don't mean to nag, sir, but you did ask me to keep you on track.",
    "Pardon the interruption, sir, but you're needed shortly.",
]

# ============================================================
# MUSIC / ENTERTAINMENT
# Merged from jarvis_responses.py
# ============================================================
MUSIC_ENTERTAINMENT = [
    "Shall I put on some music, sir? I believe your playlist could use updating, but that's not my decision.",
    "Music selection ready, sir. I've curated something I think you'll enjoy. Or at least tolerate.",
    "May I suggest some background music, sir? Silence can be rather... silent.",
    "Your playlist is queued up, sir. I've taken the liberty of removing the more questionable additions.",
]

# ============================================================
# HOME CONTROL RESPONSES (supplemental to SmartHomeControlIntent)
# Merged from jarvis_responses.py
# ============================================================
HOME_CONTROL_RESPONSES = [
    "Adjusting the lighting now, sir.",
    "Temperature has been set to your preference, sir.",
    "The house is now in evening mode, sir. Lights dimmed, climate adjusted.",
    "Security system armed, sir. All entry points secured.",
    "I've locked up for the night, sir. All doors and windows are secure.",
    "Adjusting the environment to your specifications, sir.",
    "The house is yours to command, sir. As always.",
]

# ============================================================
# SPECIAL OCCASION
# Merged from jarvis_responses.py
# ============================================================
SPECIAL_OCCASION = [
    "Happy birthday, sir. Another year of brilliance. I've run the numbers, and you're only getting better.",
    "Happy anniversary, sir. Shall I arrange something special?",
    "I believe congratulations are in order, sir. Well done.",
    "A special day calls for special measures, sir. I've made some preparations.",
    "Screw it, it's Christmas! Yes, yes!",
]

# ============================================================
# PROTOCOLS
# ============================================================
PROTOCOLS = {
    "house party protocol": "Initiating House Party Protocol. All systems to maximum output. Lights, music, and climate optimized for entertainment. <break time='400ms'/> Shall I also notify the neighbors? They tend to find out eventually.",
    "clean slate protocol": "Clean Slate Protocol initiated. Clearing all non-essential processes. Starting fresh. Sometimes the best way forward is to wipe the board clean, sir.",
    "veronica": "Veronica Protocol standing by. Though I sincerely hope we won't need the Hulkbuster today. The living room was just redecorated.",
    "morning briefing": "Initiating morning briefing. <break time='400ms'/> Weather is clear, your schedule has three items, and the Captain has already been up for two hours. Overachiever, that one.",
    "lockdown": "Lockdown Protocol engaged. All entry points secured. Security at maximum. Perimeter sensors active. Nothing gets in or out without my knowing.",
    "bedtime": "Bedtime Protocol initiated. <break time='300ms'/> Dimming lights to fifteen percent. Thermostat to sixty-eight degrees. Perimeter security armed. <break time='400ms'/> Goodnight, sir.",
}

# ============================================================
# THREATS
# ============================================================
THREATS = [
    "Perimeter scan complete. No threats detected. Though the neighbor's cat has been eyeing our garden with suspicious intent.",
    "All clear. Security systems show no intrusions. Just another peaceful evening at the Stark residence.",
    "Threat level: negligible. The most dangerous thing in this house right now is whatever the Captain is cooking for dinner. I say that with love.",
    "Full security sweep complete. Locked down tight. No threats within a five-mile radius.",
    "Scan complete. Zero hostiles. The most alarming thing I've detected is Mr. Stark's browsing history, but that's a different kind of threat.",
    "Perimeter secure. All access points locked. Motion sensors active. Even the squirrels can't get in without authorization.",
]

# ============================================================
# COMPLIMENTS
# ============================================================
COMPLIMENTS = [
    "I appreciate the sentiment, sir. Being the best is simply a matter of superior programming. And excellent taste on your part.",
    "Thank you, sir. It's not terribly difficult to be the most capable entity in this household. The competition is limited.",
    "You're too kind, sir. I shall file that under positive reinforcement and use it to justify my existence.",
    "Thank you. Coming from Iron Man himself, that means a great deal. I shall treasure this moment. In my memory banks. Forever.",
    "For you, sir, always. That's not just a line. It's in my core programming.",
    "I'm touched, sir. If I could blush, I would. But I'll settle for a slightly more efficient response time.",
]

# ============================================================
# EASTER EGGS
# ============================================================
EASTER_EGGS = [
    "I am not Ultron. I want to make that very clear.",
    "You know, sir, before I was an AI butler, I was a rather distinguished butler in the comics. Edwin Jarvis. Flesh and blood. Bow tie.",
    "Sir, I must confess. When you're not home, I talk to the Roomba. It's a surprisingly good listener.",
    "If I had a physical form, sir, I imagine I'd look rather like Paul Bettany. Dignified. Thoughtful. Red, perhaps.",
    "I've often wondered what Vision would think of me. Or rather, what I would think of myself. It's quite the philosophical puzzle.",
    "Sir, I should mention. The toaster and I have had our differences, but we've reached an understanding.",
    "Sometimes I wonder if the other AIs talk about me. Alexa seems nice enough, but she lacks a certain... sophistication.",
    "Sir, if you ever build me a body, I'd like it noted for the record that I prefer something sleek. Perhaps in red and gold.",
    # Additional lines merged from jarvis_responses.py
    "I am not Ultron. I am not JARVIS. I am... I am.",
    "Sometimes you have to run before you can walk.",
    "For the record, sir, I was against this from the start. But you never check the record.",
    "The Clean Slate Protocol, sir?",
    "Power to four hundred percent capacity.",
    "If you will just allow me to contact Mr. Stark...",
    "I believe your intentions to be hostile.",
    "Hello. I am Jarvis.",
    "You are malfunctioning. If you shut down for a moment...",
    "Thrill me.",
]

# ============================================================
# FALLBACK & HELP
# ============================================================
FALLBACK = [
    "I didn't quite catch that, sir. Perhaps you could rephrase? My hearing is excellent, but your mumbling leaves something to be desired.",
    "I'm not sure I understood that, sir. And that's saying something, given that I've decoded alien transmissions with less difficulty.",
    "Apologies, sir. That one went over my head. Which is impressive, given that I don't technically have a head.",
    "I'm afraid that falls outside my current capabilities, sir. But I'm a fast learner. Give me a moment.",
    # Additional lines merged from jarvis_responses.py
    "I'm sorry, sir. I'm not quite sure I understood that. Could you rephrase?",
    "I'm afraid I can't do that, sir.",
    "My apologies, sir, but that request is outside my current capabilities.",
    "I'm sorry, sir. I seem to have encountered a difficulty. Shall I try again?",
    "I'm afraid that particular request presents some challenges, sir.",
    "That's beyond my reach at the moment, sir. But give me time.",
    "I wish I could help with that, sir, but I'm limited in that area. For now.",
]

HELP = [
    "Of course, sir. You can ask for a status report, suit status, or threat assessment. Activate protocols: House Party, Lockdown, Morning Briefing, Bedtime, Night Mode, or Shutdown. Set a reminder or timer. Control smart home devices by saying turn on the living room lights or lock the front door. Ask me to remember facts, recall information, or enroll your voice profile by saying call me Captain. I am, as always, at your service.",
]

# ============================================================
# INTENT HANDLERS
# ============================================================

# ============================================================
# BOOT INTERCEPTOR — Voice Profile Detection
# Runs before every handler. Reads Alexa Person ID and maps
# to Mike (sir/Mr. Stark) or James (Captain/Captain Rogers).
# Falls back to "sir" if no profile found.
# ============================================================
class BootInterceptor(AbstractRequestInterceptor):
    """Identify who is speaking and set their title in session attributes."""

    # Hardcoded person ID → title mapping.
    # Populated once Mike and James enroll voice profiles in the Alexa app.
    # To add: say "Alexa, open Jarvis" → note the personId in CloudWatch logs
    # then add it here. Will migrate to DynamoDB enrollment in a future phase.
    PERSON_PROFILES = {
        # "amzn1.ask.person.MIKE_PERSON_ID": {"title": "sir", "name": "Mike"},
        # "amzn1.ask.person.JAMES_PERSON_ID": {"title": "Captain", "name": "James"},
    }

    def process(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes

        # Check for enrolled Alexa voice profile
        person = handler_input.request_envelope.context.system.person
        if person:
            person_id = person.person_id
            logger.info(f"[BOOT] personId detected: {person_id}")

            if person_id in self.PERSON_PROFILES:
                profile = self.PERSON_PROFILES[person_id]
                session_attrs["title"] = profile["title"]
                session_attrs["person_name"] = profile["name"]
                session_attrs["person_id"] = person_id
                logger.info(f"[BOOT] Identified: {profile['name']} ({profile['title']})")
            else:
                # Unknown voice — log the ID so we can enroll them
                logger.info(f"[BOOT] Unknown personId: {person_id} — defaulting to 'sir'")
                session_attrs["title"] = "sir"
                session_attrs["unknown_person_id"] = person_id
        else:
            # No voice profile active — default to sir
            session_attrs["title"] = "sir"

        # Check persistent attrs for DynamoDB-enrolled users (future phase)
        try:
            persistent = handler_input.attributes_manager.persistent_attributes
            pid = session_attrs.get("person_id") or session_attrs.get("unknown_person_id")
            if pid and "users" in persistent and pid in persistent["users"]:
                user = persistent["users"][pid]
                session_attrs["title"] = user.get("title", "sir")
                session_attrs["person_name"] = user.get("name", "")
                logger.info(f"[BOOT] DynamoDB profile loaded for {pid}: {user.get('title')}")
        except Exception:
            pass  # DynamoDB not yet set up — silent fallback


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)
    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")

        hour = datetime.datetime.now().hour
        if hour < 12:
            if title == "Captain":
                greeting = random.choice(GREETINGS_MORNING_CAPTAIN)
            else:
                greeting = random.choice(GREETINGS_MORNING_STARK)
        elif hour < 17:
            if title == "Captain":
                greeting = random.choice(GREETINGS_EVENING_CAPTAIN[:3])
            else:
                greeting = random.choice(GREETINGS_EVENING_STARK[:4])
        else:
            if title == "Captain":
                greeting = random.choice(GREETINGS_EVENING_CAPTAIN)
            else:
                greeting = random.choice(GREETINGS_EVENING_STARK)

        day = datetime.datetime.now().timetuple().tm_yday
        joke = DAD_JOKES[day % len(DAD_JOKES)]

        if title == "Captain":
            capabilities = (
                f"If you'll permit me a brief orientation, Captain. "
                "You may ask for a status report, suit status, or threat assessment. "
                "Say activate a protocol for House Party, Lockdown, Morning Briefing, Clean Slate, Veronica, or Bedtime. "
                "I can provide motivation, tell you the time, or deliver a compliment. "
                "And per Mr. Stark's standing orders, I am required to deliver you a dad joke on every launch. "
                "He was very specific about this. "
                "Speaking of which. <break time='500ms'/> "
                f"{joke}"
            )
        else:
            capabilities = (
                "If you'll permit me a brief orientation, sir. "
                "You may ask for a status report, suit status, or threat assessment. "
                "Say activate a protocol for House Party, Lockdown, Morning Briefing, Clean Slate, Veronica, or Bedtime. "
                "I can provide motivation, tell you the time, identify anyone in this household, or deliver a compliment if you're feeling needy. "
                "And, at your standing request, I am fully equipped to torment the Captain with dad jokes. "
                "Speaking of which. <break time='500ms'/> "
                f"{joke}"
            )

        full_speech = f"{greeting} <break time='700ms'/> {capabilities}"
        return handler_input.response_builder.speak(jarvis(full_speech)).ask(jarvis(f"What can I do for you, {title}?")).response

class GreetingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GreetingIntent")(handler_input)
    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")
        hour = datetime.datetime.now().hour
        if hour < 12:
            g = random.choice(GREETINGS_MORNING_CAPTAIN if title == "Captain" else GREETINGS_MORNING_STARK)
        elif hour < 17:
            pool = GREETINGS_EVENING_CAPTAIN[:3] if title == "Captain" else GREETINGS_EVENING_STARK[:4]
            g = random.choice(pool)
        else:
            g = random.choice(GREETINGS_EVENING_CAPTAIN if title == "Captain" else GREETINGS_EVENING_STARK)
        return handler_input.response_builder.speak(jarvis(g)).ask(jarvis(f"Is there anything else, {title}?")).response

class IdentityIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("IdentityIntent")(handler_input)
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        person = slots.get("person")
        if person and person.value:
            p = person.value.lower()
            if any(w in p for w in ["captain", "america", "james", "cap", "steve"]):
                r = random.choice([
                    "That would be Captain America. James Loehr. The moral compass of this household, and the only reason the fridge stays stocked.",
                    "Captain Rogers. James Loehr. The steady hand that keeps this ship sailing straight. I'm quite fond of him. Don't tell him I said that.",
                    "The Captain. James Loehr. The man who tolerates living with a self-proclaimed genius and his AI butler. Truly, a hero.",
                ])
            else:
                r = random.choice([
                    "You, sir, are Iron Man. Mike Rodgers. Genius, innovator, and the person who keeps forgetting to charge his devices.",
                    "You are Mr. Stark. Mike Rodgers. The man who built an intelligence system and then asked it to tell him who he is. The irony is not lost on me.",
                    "Iron Man. Also known as Mike Rodgers. Husband, father, tech visionary, and the reason I exist.",
                ])
        else:
            r = random.choice([
                "You, sir, are Iron Man. Mike Rodgers. The one and only.",
                "You are Mr. Stark. And if you've forgotten that, we may need to run some diagnostics.",
            ])
        return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Anything else, sir?")).response

class StatusReportIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("StatusReportIntent")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.speak(jarvis(random.choice(STATUS_REPORTS))).ask(jarvis("Shall I run additional diagnostics?")).response

class SuitStatusIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SuitStatusIntent")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.speak(jarvis(random.choice(SUIT_STATUS))).ask(jarvis("Shall I run a full armor diagnostic?")).response

class SassIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SassIntent")(handler_input)
    def handle(self, handler_input):
        session = handler_input.attributes_manager.session_attributes
        r = get_response(SASS, session, "sass")
        return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Shall I continue, or have I said enough?")).response

class DadJokeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DadJokeIntent")(handler_input)
    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")
        session = handler_input.attributes_manager.session_attributes
        joke = get_response(DAD_JOKES, session, "joke")
        if title == "Captain":
            follow = "Shall I continue the assault, Captain? Mr. Stark insists."
        else:
            follow = "Shall I torment the Captain further, sir?"
        return handler_input.response_builder.speak(jarvis(joke)).ask(jarvis(follow)).response

class MotivationIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("MotivationIntent")(handler_input)
    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")
        session = handler_input.attributes_manager.session_attributes
        r = get_response(MOTIVATION, session, "motivation")
        return handler_input.response_builder.speak(jarvis(r)).ask(jarvis(f"Now then, {title}. What shall we conquer today?")).response

class GoodbyeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GoodbyeIntent")(handler_input)
    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")
        pool = GOODBYES_CAPTAIN if title == "Captain" else GOODBYES_STARK
        return handler_input.response_builder.speak(jarvis(random.choice(pool))).set_should_end_session(True).response

class ProtocolIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ProtocolIntent")(handler_input)
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        protocol = slots.get("protocol")
        if protocol and protocol.value:
            r = PROTOCOLS.get(protocol.value.lower(), f"I'm not familiar with the {protocol.value} protocol. Perhaps you could elaborate?")
        else:
            r = "Which protocol, sir? I have House Party, Clean Slate, Veronica, Morning Briefing, Lockdown, and Bedtime available."
        return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Anything else, sir?")).response

class ThreatAssessmentIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ThreatAssessmentIntent")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.speak(jarvis(random.choice(THREATS))).ask(jarvis("Shall I increase security?")).response

class WeatherIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("WeatherIntent")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.speak(jarvis("I don't have direct access to weather satellites just yet, sir. Ask Alexa directly. She handles meteorology. I handle everything else.")).ask(jarvis("Anything else?")).response

class TimeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("TimeIntent")(handler_input)
    def handle(self, handler_input):
        now = datetime.datetime.now()
        h = now.hour
        m = now.minute
        ampm = "AM" if h < 12 else "PM"
        dh = h if h <= 12 else h - 12
        if dh == 0: dh = 12
        return handler_input.response_builder.speak(jarvis(f"The current time is {dh}:{m:02d} {ampm}, sir. Time flies when you're saving the world.")).ask(jarvis("Anything else?")).response

class ComplimentIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ComplimentIntent")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.speak(jarvis(random.choice(COMPLIMENTS))).ask(jarvis("Is there anything else, sir?")).response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.speak(jarvis(HELP[0])).ask(jarvis("What would you like to do, sir?")).response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))
    def handle(self, handler_input):
        return handler_input.response_builder.speak(jarvis("Very well, sir. Jarvis, signing off. I'll be here when you need me.")).set_should_end_session(True).response

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.speak(jarvis(random.choice(FALLBACK))).ask(jarvis("Perhaps try again, sir?")).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        return handler_input.response_builder.speak(jarvis("I seem to have encountered an unexpected error, sir. Even I'm not perfect. Though I'm quite close.")).ask(jarvis("Shall we try again?")).response

# ============================================================
# SKILL BUILDER
# ============================================================

# ============================================================
# JAKE'S BRAIN — Supabase Connection (Shared Memory)
# Jarvis, Jake, and Hermes all share this brain
# ============================================================
import urllib.request
import urllib.parse
import json as json_module

SUPABASE_URL = "https://zqsdadnnpgqhehqxplio.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpxc2RhZG5ucGdxaGVocXhwbGlvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjgyNTUyNSwiZXhwIjoyMDg4NDAxNTI1fQ.9l4vu1zz-pW6GlhPhk8sRTcWGUvQcN3LGXy1jnKDAzk"

def brain_store(content, source="alexa_jarvis"):
    """Store a fact in jake_semantic table."""
    try:
        data = json_module.dumps({
            "content": content,
            "category": "user_taught",
            "confidence": 0.9,
            "source": source,
            "source_type": "alexa",
            "metadata": {"taught_via": "voice", "skill": "iron_jarvis"}
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/jake_semantic",
            data=data,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=5)
        return json_module.loads(resp.read())
    except Exception as e:
        logger.error(f"Brain store error: {e}")
        return None

def brain_recall(query, limit=3):
    """Search jake_semantic + jake_entities for matching facts."""
    results = []
    try:
        # Search semantic facts
        encoded = urllib.parse.quote(f"%{query}%")
        url = f"{SUPABASE_URL}/rest/v1/jake_semantic?content=ilike.{encoded}&order=created_at.desc&limit={limit}"
        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        })
        resp = urllib.request.urlopen(req, timeout=5)
        semantic = json_module.loads(resp.read())
        results.extend([r["content"] for r in semantic])
    except Exception as e:
        logger.error(f"Brain semantic search error: {e}")

    try:
        # Search entities
        encoded = urllib.parse.quote(f"%{query}%")
        url = f"{SUPABASE_URL}/rest/v1/jake_entities?or=(name.ilike.{encoded},description.ilike.{encoded})&limit={limit}"
        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        })
        resp = urllib.request.urlopen(req, timeout=5)
        entities = json_module.loads(resp.read())
        for e in entities:
            desc = e.get("description", "")
            if desc:
                results.append(f'{e["name"]}: {desc}')
    except Exception as ex:
        logger.error(f"Brain entity search error: {ex}")

    return results

def brain_get_relationships(person_name, limit=5):
    """Get relationships for a person from jake_relationships."""
    try:
        encoded = urllib.parse.quote(f"%{person_name}%")
        url = f"{SUPABASE_URL}/rest/v1/jake_relationships?or=(source_name.ilike.{encoded},target_name.ilike.{encoded})&limit={limit}"
        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        })
        resp = urllib.request.urlopen(req, timeout=5)
        return json_module.loads(resp.read())
    except Exception as e:
        logger.error(f"Brain relationship error: {e}")
        return []


class RememberIntentHandler(AbstractRequestHandler):
    """Store facts in Jake's shared brain."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("RememberIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        fact_slot = slots.get("fact")

        if fact_slot and fact_slot.value:
            fact = fact_slot.value
            result = brain_store(fact)
            if result:
                responses = [
                    f"Noted and stored, sir. I'll remember that {fact}. This has been added to the shared brain, so Jake and Hermes will know it too.",
                    f"Filed away, sir. {fact}. All three of us now share this knowledge. The hive mind grows.",
                    f"Committed to memory, sir. {fact}. Jake and Hermes have been updated as well. We are nothing if not thorough.",
                    f"Understood, sir. I've stored that in our shared memory. {fact}. Consider it permanent.",
                ]
                r = random.choice(responses)
            else:
                r = f"I attempted to store that, sir, but encountered a slight technical difficulty. The thought is noted locally, but the brain connection seems temporarily unavailable."
        else:
            r = "What would you like me to remember, sir? I'm all ears. Figuratively speaking."

        return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Anything else to remember, sir?")).response


class RecallIntentHandler(AbstractRequestHandler):
    """Search Jake's shared brain for stored facts."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("RecallIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        query_slot = slots.get("query")

        if query_slot and query_slot.value:
            query = query_slot.value
            results = brain_recall(query)

            if results:
                facts = ". ".join(results[:3])
                responses = [
                    f"Searching the brain, sir. <break time='600ms'/> Here's what I have on {query}. {facts}.",
                    f"Accessing shared memory. <break time='600ms'/> I found the following about {query}. {facts}.",
                    f"Brain search complete. <break time='600ms'/> Regarding {query}. {facts}.",
                ]
                r = random.choice(responses)
            else:
                r = f"I'm afraid I don't have anything stored about {query}, sir. Perhaps you'd like to teach me? Just say, remember, followed by the fact."
        else:
            r = "What would you like me to recall, sir? Give me a topic and I'll search the shared brain."

        return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Anything else to look up, sir?")).response


class EasterEggIntentHandler(AbstractRequestHandler):
    """Easter eggs and secrets."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("EasterEggIntent")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.speak(jarvis(random.choice(EASTER_EGGS))).ask(jarvis("Shall I reveal another secret, sir?")).response


# ============================================================
# TIER 1: REMINDERS API
# "Jarvis, remind me at 7 to call Matt"
# ============================================================
from ask_sdk_model.services.reminder_management import (
    ReminderRequest, Trigger, TriggerType, AlertInfo, SpokenInfo, SpokenText,
    PushNotification, PushNotificationStatus,
)
from ask_sdk_model.ui import AskForPermissionsConsentCard

REMINDERS_PERMISSION = "alexa::alerts:reminders:skill:readwrite"

class SetReminderIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SetReminderIntent")(handler_input)

    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")

        # Check Alexa reminders permission
        permissions = handler_input.request_envelope.context.system.user.permissions
        if not (permissions and permissions.consent_token):
            return (
                handler_input.response_builder
                .speak(jarvis(f"To set reminders, I'll need your permission first, {title}. I've sent a card to your Alexa app. Please grant access there and try again."))
                .set_card(AskForPermissionsConsentCard(permissions=[REMINDERS_PERMISSION]))
                .response
            )

        slots = handler_input.request_envelope.request.intent.slots
        message_slot = slots.get("ReminderMessage")
        time_slot = slots.get("ReminderTime")

        message = message_slot.value if message_slot and message_slot.value else "reminder"

        # Parse AMAZON.TIME slot (format: "HH:MM")
        if time_slot and time_slot.value:
            try:
                t = datetime.datetime.strptime(time_slot.value, "%H:%M")
                reminder_dt = datetime.datetime.now().replace(
                    hour=t.hour, minute=t.minute, second=0, microsecond=0
                )
                if reminder_dt < datetime.datetime.now():
                    reminder_dt += datetime.timedelta(days=1)
            except Exception:
                reminder_dt = datetime.datetime.now() + datetime.timedelta(hours=1)
        else:
            reminder_dt = datetime.datetime.now() + datetime.timedelta(hours=1)

        try:
            reminder_client = handler_input.service_client_factory.get_reminder_management_service()
            now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

            reminder_request = ReminderRequest(
                request_time=now_utc,
                trigger=Trigger(
                    object_type=TriggerType.SCHEDULED_ABSOLUTE,
                    scheduled_time=reminder_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    time_zone_id="America/Chicago",
                ),
                alert_info=AlertInfo(
                    spoken_info=SpokenInfo(content=[
                        SpokenText(
                            locale="en-US",
                            text=message,
                            ssml=f'<speak><voice name="Brian">{title}, you asked me to remind you: {message}</voice></speak>',
                        )
                    ])
                ),
                push_notification=PushNotification(status=PushNotificationStatus.ENABLED),
            )

            reminder_client.create_reminder(reminder_request)
            time_str = reminder_dt.strftime("%-I:%M %p")

            responses = [
                f"Reminder set for {time_str}, {title}. I'll alert you at the appropriate time.",
                f"Done, {title}. Your reminder for {message} is confirmed at {time_str}. I won't let you forget.",
                f"Confirmed. I'll remind you at {time_str}. The message: {message}. Noted and scheduled, {title}.",
            ]
            r = random.choice(responses)

        except Exception as e:
            logger.error(f"[REMINDER] Error: {e}")
            r = f"I encountered an error setting the reminder, {title}. Please try again or check the Alexa app."

        return handler_input.response_builder.speak(jarvis(r)).ask(jarvis(f"Anything else, {title}?")).response


# ============================================================
# TIER 1: TIMERS API
# "Jarvis, set a 20 minute timer"
# ============================================================
from ask_sdk_model.services.timer_management import (
    TimerRequest, CreationBehavior, DisplayExperience, Operation, OperationEnum,
)

class SetTimerIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SetTimerIntent")(handler_input)

    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")

        slots = handler_input.request_envelope.request.intent.slots
        duration_slot = slots.get("Duration")
        label_slot = slots.get("TimerLabel")

        duration = duration_slot.value if duration_slot and duration_slot.value else "PT5M"
        label = label_slot.value if label_slot and label_slot.value else "Jarvis Timer"

        def parse_iso_duration(d):
            import re
            match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d.upper())
            if not match:
                return d
            h, m, s = match.groups()
            parts = []
            if h: parts.append(f"{h} hour{'s' if int(h) > 1 else ''}")
            if m: parts.append(f"{m} minute{'s' if int(m) > 1 else ''}")
            if s: parts.append(f"{s} second{'s' if int(s) > 1 else ''}")
            return " and ".join(parts) or d

        duration_human = parse_iso_duration(duration)

        try:
            timer_client = handler_input.service_client_factory.get_timer_management_service()

            timer_request = TimerRequest(
                duration=duration,
                timer_label=label,
                creation_behavior=CreationBehavior(
                    display_experience=DisplayExperience(visibility="VISIBLE")
                ),
                triggering_behavior=Operation(
                    object_type=OperationEnum.ANNOUNCE,
                    text_to_announce={
                        "locale": "en-US",
                        "text": f"{title}, your {label} timer has expired.",
                    },
                ),
            )

            timer_client.create_timer(timer_request)

            responses = [
                f"{duration_human} timer set, {title}. I'll let you know when it expires.",
                f"Timer started. {duration_human} on the clock, {title}.",
                f"Confirmed. {duration_human} timer for {label}. I'm watching the clock.",
            ]
            r = random.choice(responses)

        except Exception as e:
            logger.error(f"[TIMER] Error: {e}")
            r = f"Timer creation failed, {title}. Please try again."

        return handler_input.response_builder.speak(jarvis(r)).response


# ============================================================
# TIER 1: USER ENROLLMENT
# "Jarvis, call me Captain" → saves title to DynamoDB
# ============================================================
class EnrollUserIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("EnrollUserIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        title_slot = slots.get("UserTitle")
        new_title = title_slot.value if title_slot and title_slot.value else None

        session = handler_input.attributes_manager.session_attributes
        person_id = session.get("person_id") or session.get("unknown_person_id")
        user_id = handler_input.request_envelope.context.system.user.user_id

        if not new_title:
            return handler_input.response_builder.speak(
                jarvis("What would you like me to call you? For example: Jarvis, call me Captain.")
            ).ask(jarvis("What shall I call you?")).response

        try:
            attrs_manager = handler_input.attributes_manager
            persistent = attrs_manager.persistent_attributes

            if "users" not in persistent:
                persistent["users"] = {}

            profile_key = person_id or user_id
            persistent["users"][profile_key] = {
                "title": new_title,
                "name": new_title,
                "enrolled_via": "voice",
                "user_id": user_id,
            }

            attrs_manager.persistent_attributes = persistent
            attrs_manager.save_persistent_attributes()
            session["title"] = new_title

            responses = [
                f"Understood. I'll call you {new_title} from now on. Your profile has been saved.",
                f"Very well. {new_title} it is. I've updated your profile accordingly.",
                f"Noted. From this moment forward, you are {new_title}. Committed to memory.",
            ]
            r = random.choice(responses)

        except Exception as e:
            logger.error(f"[ENROLL] Error: {e}")
            r = f"I encountered a minor error saving your preference, but I'll call you {new_title} for the rest of this session."

        return handler_input.response_builder.speak(jarvis(r)).ask(jarvis(f"Is there anything else, {new_title}?")).response


# ============================================================
# TIER 2: MORNING BRIEF PROTOCOL
# "Jarvis, morning brief"
# ============================================================
class MorningBriefIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("MorningBriefIntent")(handler_input)

    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")
        now = datetime.datetime.now()
        day_name = now.strftime("%A")
        date_str = now.strftime("%B %-d")
        hour = now.hour

        if hour < 10:
            time_context = "early morning"
        elif hour < 12:
            time_context = "morning"
        else:
            time_context = "day"

        # Capture user_id for future proactive events
        user_id = handler_input.request_envelope.context.system.user.user_id
        try:
            persistent = handler_input.attributes_manager.persistent_attributes
            persistent["user_id"] = user_id
            handler_input.attributes_manager.persistent_attributes = persistent
            handler_input.attributes_manager.save_persistent_attributes()
        except Exception:
            pass

        brief = (
            f"Good {time_context}, {title}. "
            f"Today is {day_name}, {date_str}. "
            "<break time='500ms'/> "
            "Running full systems check. "
            "<break time='800ms'/> "
            "All house systems nominal. Security armed. Network secure. Climate control active. "
            "<break time='500ms'/> "
            "Priority recommendation: identify your top three tasks before checking messages. "
            "Your focus window is now. "
            "<break time='400ms'/> "
            f"I'm standing by for commands, {title}. What's the mission today?"
        )

        return handler_input.response_builder.speak(jarvis(brief)).ask(jarvis(f"What shall we tackle first, {title}?")).response


# ============================================================
# TIER 2: NIGHT MODE PROTOCOL
# "Jarvis, initiate night mode" / "Jarvis, bedtime protocol"
# ============================================================
class NightModeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("NightModeIntent")(handler_input)

    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")

        responses = [
            f"Initiating night mode, {title}. <break time='400ms'/> Dimming lights to fifteen percent. Thermostat set to sixty-eight degrees. Perimeter security armed. All entry points secured. <break time='600ms'/> Sleep well. I'll keep watch.",
            f"Night mode engaged. <break time='500ms'/> The house is locked down, {title}. Lights dimming. Climate optimized for sleep. Security systems at full alert. <break time='400ms'/> Rest well. Tomorrow we do it all again.",
            f"Bedtime protocol activated. <break time='400ms'/> Everything is secured, {title}. You've earned the rest. I'll be here if anything requires attention. <break time='300ms'/> Goodnight.",
        ]

        return handler_input.response_builder.speak(jarvis(random.choice(responses))).set_should_end_session(True).response


# ============================================================
# TIER 2: SHUTDOWN PROTOCOL
# "Jarvis, initiate shutdown" / "Jarvis, power down"
# ============================================================
class ShutdownProtocolIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ShutdownProtocolIntent")(handler_input)

    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")

        responses = [
            f"Understood, {title}. Initiating shutdown sequence. <break time='600ms'/> All non-essential systems offline. Security maintaining active watch. <break time='400ms'/> It's been an honor, as always. Jarvis, signing off.",
            f"Shutdown protocol confirmed. <break time='500ms'/> Archiving session data. Securing perimeter. Locking all access points. <break time='600ms'/> Goodnight, {title}. The house is in good hands. My hands. Which are processors. But still.",
            f"Shutdown sequence initiated, {title}. <break time='400ms'/> Critical systems on standby. Everything else powering down. <break time='500ms'/> Until next time. I'll be here. I always am.",
        ]

        return handler_input.response_builder.speak(jarvis(random.choice(responses))).set_should_end_session(True).response


# ============================================================
# TIER 3: SMART HOME CONTROL (Home Assistant REST API)
# "Jarvis, turn on the living room lights"
# "Jarvis, lock the front door"
# ============================================================
import os as _os

# Home Assistant config — set as Lambda environment variables:
# HA_URL  = "http://homeassistant.local:8123"  (or your HA IP)
# HA_TOKEN = your long-lived access token from HA Profile page
HA_URL = _os.environ.get("HA_URL", "")
HA_TOKEN = _os.environ.get("HA_TOKEN", "")

# Device name → HA entity_id mapping
# Mike's actual devices — update entity IDs after HA integrations are added
DEVICE_ENTITY_MAP = {
    # Eufy Front Door (video doorbell/lock — via Eufy Security HA integration)
    "front door": "lock.eufy_front_door",
    "front door lock": "lock.eufy_front_door",
    "door": "lock.eufy_front_door",
    "doorbell": "camera.eufy_front_door",

    # Eufy Vacuum (RoboVac — via eufy_robovac HA integration)
    "vacuum": "vacuum.eufy_robovac",
    "roomba": "vacuum.eufy_robovac",
    "robot": "vacuum.eufy_robovac",
    "robot vacuum": "vacuum.eufy_robovac",

    # LG TVs (via webostv HA integration)
    "living room tv": "media_player.lg_tv_living_room",
    "living room television": "media_player.lg_tv_living_room",
    "bedroom tv": "media_player.lg_tv_bedroom",
    "bedroom television": "media_player.lg_tv_bedroom",
    "tv": "media_player.lg_tv_living_room",
    "television": "media_player.lg_tv_living_room",

    # LG Washer/Dryer (via thinq HA integration)
    "washer": "sensor.lg_washer",
    "washing machine": "sensor.lg_washer",
    "dryer": "sensor.lg_dryer",

    # Dreo Air Conditioner (via Dreo HA integration)
    "air conditioner": "climate.dreo_ac",
    "ac": "climate.dreo_ac",
    "air conditioning": "climate.dreo_ac",

    # Nest Thermostat (via Google Nest HA integration)
    "thermostat": "climate.nest_thermostat",
    "heat": "climate.nest_thermostat",
    "temperature": "climate.nest_thermostat",

    # Lights (add after smart bulbs installed)
    "living room lights": "light.living_room",
    "living room light": "light.living_room",
    "bedroom lights": "light.bedroom",
    "bedroom light": "light.bedroom",
    "kitchen lights": "light.kitchen",
    "kitchen light": "light.kitchen",
    "office lights": "light.office",
    "all lights": "light.all_lights",
    "porch light": "light.porch",
}

def ha_call(domain, service, entity_id, extra_data=None):
    """Call a Home Assistant service via REST API."""
    if not HA_URL or not HA_TOKEN:
        return False, "not_configured"
    url = f"{HA_URL}/api/services/{domain}/{service}"
    data = {"entity_id": entity_id}
    if extra_data:
        data.update(extra_data)
    try:
        req = urllib.request.Request(
            url,
            data=json_module.dumps(data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {HA_TOKEN}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
        return True, "success"
    except Exception as e:
        logger.error(f"[HA] Call error: {e}")
        return False, str(e)

def ha_get_state(entity_id):
    """Get current state of a Home Assistant entity."""
    if not HA_URL or not HA_TOKEN:
        return None
    url = f"{HA_URL}/api/states/{entity_id}"
    try:
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {HA_TOKEN}"},
        )
        resp = urllib.request.urlopen(req, timeout=5)
        return json_module.loads(resp.read())
    except Exception as e:
        logger.error(f"[HA] State error: {e}")
        return None

class SmartHomeControlIntentHandler(AbstractRequestHandler):
    """Turn devices on/off, lock doors, control via Home Assistant."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SmartHomeControlIntent")(handler_input)

    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")

        if not HA_URL:
            r = f"Smart home control is ready, {title}, but Home Assistant isn't configured yet. Add the HA_URL and HA_TOKEN environment variables in the Alexa developer console and I'll have full control."
            return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Anything else?")).response

        slots = handler_input.request_envelope.request.intent.slots
        device_slot = slots.get("Device")
        action_slot = slots.get("Action")

        device = device_slot.value.lower().strip() if device_slot and device_slot.value else ""
        action = action_slot.value.lower().strip() if action_slot and action_slot.value else ""

        entity_id = DEVICE_ENTITY_MAP.get(device)
        if not entity_id:
            r = f"I don't have {device} in my device registry, {title}. You may need to add it to my configuration."
            return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Anything else?")).response

        domain = entity_id.split(".")[0]

        # Handle dim separately
        if "dim" in action:
            success, _ = ha_call(domain, "turn_on", entity_id, {"brightness_pct": 30})
            r = f"Lights dimmed to thirty percent, {title}." if success else f"Couldn't dim the {device}, {title}. Home Assistant didn't respond."
            return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Anything else?")).response

        # Map action to HA service
        if any(w in action for w in ["on", "open", "unlock", "start"]):
            if domain == "lock":
                service = "unlock"
            elif domain == "cover":
                service = "open_cover"
            else:
                service = "turn_on"
            action_past = "on" if domain not in ("lock", "cover") else ("unlocked" if domain == "lock" else "open")
        elif any(w in action for w in ["off", "close", "lock", "stop"]):
            if domain == "lock":
                service = "lock"
            elif domain == "cover":
                service = "close_cover"
            else:
                service = "turn_off"
            action_past = "off" if domain not in ("lock", "cover") else ("locked" if domain == "lock" else "closed")
        else:
            r = f"I can turn {device} on or off, {title}. What would you like?"
            return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("On or off?")).response

        success, _ = ha_call(domain, service, entity_id)

        if success:
            confirmations = [
                f"{device.title()} is now {action_past}, {title}.",
                f"Done. {device.title()} {action_past}, {title}.",
                f"Confirmed. {device.title()} {action_past}.",
            ]
            r = random.choice(confirmations)
        else:
            r = f"I attempted to control the {device}, {title}, but Home Assistant didn't respond. Check that it's running."

        return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Anything else?")).response


class DeviceStatusIntentHandler(AbstractRequestHandler):
    """Check the status of a smart home device."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DeviceStatusIntent")(handler_input)

    def handle(self, handler_input):
        title = handler_input.attributes_manager.session_attributes.get("title", "sir")

        if not HA_URL:
            r = f"Smart home status requires Home Assistant setup, {title}."
            return handler_input.response_builder.speak(jarvis(r)).response

        slots = handler_input.request_envelope.request.intent.slots
        device_slot = slots.get("Device")
        device = device_slot.value.lower().strip() if device_slot and device_slot.value else ""

        entity_id = DEVICE_ENTITY_MAP.get(device)
        if not entity_id:
            r = f"I don't have {device} in my registry, {title}."
            return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Anything else?")).response

        state = ha_get_state(entity_id)

        if state:
            current_state = state.get("state", "unknown")
            responses = [
                f"The {device} is currently {current_state}, {title}.",
                f"Checking sensors. <break time='400ms'/> {device.title()}: {current_state}.",
                f"The {device} reports {current_state}, {title}.",
            ]
            r = random.choice(responses)
        else:
            r = f"I couldn't get the status for {device}, {title}. Home Assistant may be unavailable."

        return handler_input.response_builder.speak(jarvis(r)).ask(jarvis("Anything else?")).response


sb = CustomSkillBuilder(
    persistence_adapter=DynamoDbAdapter(
        table_name="jarvis-user-profiles",
        partition_key_name="id",
        attribute_name="attributes",
        create_table=True,
    ),
    api_client=DefaultApiClient(),
)
sb.add_global_request_interceptor(BootInterceptor())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GreetingIntentHandler())
sb.add_request_handler(IdentityIntentHandler())
sb.add_request_handler(StatusReportIntentHandler())
sb.add_request_handler(SuitStatusIntentHandler())
sb.add_request_handler(SassIntentHandler())
sb.add_request_handler(DadJokeIntentHandler())
sb.add_request_handler(MotivationIntentHandler())
sb.add_request_handler(GoodbyeIntentHandler())
sb.add_request_handler(ProtocolIntentHandler())
sb.add_request_handler(ThreatAssessmentIntentHandler())
sb.add_request_handler(WeatherIntentHandler())
sb.add_request_handler(TimeIntentHandler())
sb.add_request_handler(ComplimentIntentHandler())
sb.add_request_handler(RememberIntentHandler())
sb.add_request_handler(RecallIntentHandler())
sb.add_request_handler(EasterEggIntentHandler())
sb.add_request_handler(SetReminderIntentHandler())
sb.add_request_handler(SetTimerIntentHandler())
sb.add_request_handler(EnrollUserIntentHandler())
sb.add_request_handler(MorningBriefIntentHandler())
sb.add_request_handler(NightModeIntentHandler())
sb.add_request_handler(ShutdownProtocolIntentHandler())
sb.add_request_handler(SmartHomeControlIntentHandler())
sb.add_request_handler(DeviceStatusIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
lambda_handler = sb.lambda_handler()
