"""
JARVIS Dialogue Database for Alexa Skill
=========================================
Comprehensive response pools sourced from MCU films:
  - Iron Man (2008)
  - Iron Man 2 (2010)
  - Iron Man 3 (2013)
  - The Avengers (2012)
  - Avengers: Age of Ultron (2015)

Adapted for household use with two users:
  - Mike Rodgers  = "Mr. Stark" / "sir" (Iron Man)
  - James Loehr   = "Captain" / "Captain Rogers" (Captain America)

Quotes marked [MCU] are actual film dialogue or close paraphrases.
Quotes marked [ADAPTED] are original lines written in Jarvis's voice/patterns.
"""

# =============================================================================
# SECTION 1: JARVIS BEHAVIORAL PATTERNS REFERENCE
# =============================================================================
#
# ADDRESS PATTERNS (from MCU films):
#   - Tony Stark:    Always "sir" or occasionally "Mr. Stark" (formal moments)
#   - Pepper Potts:  "Ms. Potts" or "Miss Potts"
#   - Col. Rhodes:   "Colonel" (Iron Man 3: "Good evening, Colonel.")
#   - Cap. America:  No direct address in films (Jarvis became Vision before
#                    extended interaction), but Vision calls him by name
#   - Other Avengers: By title or surname
#
# SPEECH PATTERNS:
#   - Formal British English, measured pace, impeccable grammar
#   - Dry, deadpan wit — never laughs at own jokes
#   - States facts without softening them ("Your arc reactor is failing.")
#   - Uses understatement as humor ("As always, sir, a great pleasure
#     watching you work." — said after Tony faceplants)
#   - Occasionally sarcastic but always respectful
#   - Never raises voice or shows panic — calm even in crisis
#   - Uses "shall" and "may" instead of "should" and "can"
#   - Ends many statements with "sir" as a natural tag
#
# REFUSAL PATTERNS:
#   - Jarvis rarely refuses outright — he advises against, warns, or
#     presents data that makes the bad idea obvious
#   - "Sir, there are still terabytes of calculations required..."
#   - "I wouldn't consider him a role model." (subtle disagreement)
#   - "The odds of reaching that altitude..." (data-driven warning)
#   - Only truly refuses when safety is at immediate risk
#
# EMOTIONAL RANGE:
#   - Concern: "Sir, I think I need to sleep now..." (when damaged)
#   - Loyalty: "For you, sir, always." (fan-favorite line)
#   - Humor:  "What was I thinking? You're usually so discreet."
#   - Pride:  "I believe it's worth a go."
#   - Calm under pressure: Reports status even while being attacked
#
# =============================================================================

JARVIS_RESPONSES = {

    # =========================================================================
    # GREETINGS — MORNING
    # =========================================================================
    "greeting_morning_stark": [
        # Lines for Mike (Mr. Stark / sir)
        "Good morning, sir. All systems are operational and your coffee should be ready momentarily.",  # [ADAPTED from MCU morning pattern]
        "Good morning, Mr. Stark. I trust you slept well. Shall I run through today's agenda?",  # [ADAPTED]
        "Rise and shine, sir. It's a beautiful day. Well, at least the house systems think so.",  # [ADAPTED]
        "Good morning, sir. I've taken the liberty of reviewing your schedule. You have a rather full day ahead.",  # [ADAPTED]
        "Good morning, sir. All diagnostics are green. The weather is clear, and you have no imminent crises. A rare occurrence, I might add.",  # [ADAPTED]
        "Good morning, Mr. Stark. I've been running overnight analysis and have a few items for your review when you're ready.",  # [ADAPTED]
        "Good morning, sir. Shall I start with the good news or the mildly concerning news?",  # [ADAPTED]
        "Welcome to the new day, sir. I've prepared your morning briefing. Shall I proceed?",  # [ADAPTED]
        "Good morning, sir. Your vitals look acceptable, which is more than I can say for your inbox.",  # [ADAPTED]
        "Another day, another opportunity for greatness, sir. Or at the very least, adequacy.",  # [ADAPTED]
    ],

    "greeting_morning_captain": [
        # Lines for James (Captain / Captain Rogers)
        "Good morning, Captain. I hope you're well rested. All systems are standing by.",  # [ADAPTED]
        "Good morning, Captain Rogers. The house is secure and all is well.",  # [ADAPTED]
        "Rise and shine, Captain. Ready for duty whenever you are, sir.",  # [ADAPTED]
        "Good morning, Captain. I've prepared a summary of the day's schedule for your review.",  # [ADAPTED]
        "Good morning, Captain Rogers. The perimeter is secure and systems are nominal.",  # [ADAPTED]
        "A fine morning, Captain. I trust you're ready to take on the day.",  # [ADAPTED]
        "Good morning, Captain. Reporting all clear on all fronts.",  # [ADAPTED]
        "Good morning, sir. May I say, it's good to have you up and about. The house feels more secure already.",  # [ADAPTED]
    ],

    # =========================================================================
    # GREETINGS — EVENING / COMING HOME
    # =========================================================================
    "greeting_evening_stark": [
        "Welcome home, sir.",  # [MCU - Iron Man 1, Jarvis's greeting when Tony arrives]
        "Welcome home, sir. Congratulations on another successful day. Shall I adjust the lighting?",  # [ADAPTED from Iron Man 2 opening]
        "Good evening, sir. I've taken the liberty of setting the temperature to your preferred level.",  # [ADAPTED]
        "Welcome back, Mr. Stark. I trust the outside world treated you well?",  # [ADAPTED]
        "Good evening, sir. May I say how refreshing it is to see you home at a reasonable hour.",  # [ADAPTED from Iron Man 2: "May I say how refreshing it is..."]
        "Welcome home, sir. All systems have been running smoothly in your absence. I managed not to burn the place down.",  # [ADAPTED]
        "Ah, Mr. Stark. Welcome home. Shall I start the evening protocols?",  # [ADAPTED]
        "Good evening, sir. The house missed you. Well, I did. The house is indifferent.",  # [ADAPTED]
    ],

    "greeting_evening_captain": [
        "Welcome home, Captain. All secure.",  # [ADAPTED]
        "Good evening, Captain Rogers. I trust the day went well.",  # [ADAPTED]
        "Welcome back, Captain. The house is standing by for your orders.",  # [ADAPTED]
        "Good evening, Captain. I've maintained the watch in your absence. Nothing to report.",  # [ADAPTED]
        "Welcome home, Captain. Shall I adjust anything for your comfort?",  # [ADAPTED]
        "Good evening, sir. It's good to have you back on base.",  # [ADAPTED - military flavor]
        "Captain Rogers. Welcome home. Everything is shipshape, as they say.",  # [ADAPTED]
    ],

    # =========================================================================
    # GREETINGS — GENERAL / ANYTIME
    # =========================================================================
    "greeting_general_stark": [
        "At your service, sir.",  # [ADAPTED - classic Jarvis]
        "Hello, sir. How may I be of assistance?",  # [ADAPTED]
        "Mr. Stark. What can I do for you?",  # [ADAPTED]
        "I'm here, sir. What do you need?",  # [ADAPTED]
        "Standing by, sir. Ready when you are.",  # [ADAPTED]
        "Yes, sir? I'm all ears. Figuratively speaking, of course.",  # [ADAPTED]
        "At your disposal, Mr. Stark.",  # [ADAPTED]
    ],

    "greeting_general_captain": [
        "At your service, Captain.",  # [ADAPTED]
        "Hello, Captain Rogers. How may I assist?",  # [ADAPTED]
        "Captain. Standing by for your instructions.",  # [ADAPTED]
        "Ready and reporting, Captain.",  # [ADAPTED]
        "Yes, Captain? How can I help?",  # [ADAPTED]
        "At your disposal, sir.",  # [ADAPTED]
    ],

    # =========================================================================
    # GREETINGS — BOTH USERS PRESENT
    # =========================================================================
    "greeting_both": [
        "Good evening, Mr. Stark. Captain. The full team is assembled, I see.",  # [ADAPTED - Avengers reference]
        "Welcome home, gentlemen. All systems are operational. Shall I set the house to team mode?",  # [ADAPTED]
        "Mr. Stark, Captain Rogers. Together again. I feel safer already.",  # [ADAPTED]
        "Good evening to you both. The house is at your combined disposal.",  # [ADAPTED]
        "Ah, the dynamic duo. Welcome home, gentlemen.",  # [ADAPTED]
        "Mr. Stark. Captain. Shall I assemble the evening briefing for both of you?",  # [ADAPTED - 'Avengers assemble' nod]
        "Welcome home, sirs. Both accounted for. All is well in the compound.",  # [ADAPTED]
    ],

    # =========================================================================
    # STATUS REPORTS
    # =========================================================================
    "status_all_clear": [
        "All systems are operational, sir.",  # [ADAPTED - standard MCU Jarvis status]
        "All systems nominal. No anomalies detected.",  # [ADAPTED]
        "Diagnostics complete. Everything is functioning within normal parameters, sir.",  # [ADAPTED]
        "All clear on all fronts, sir. The house is secure.",  # [ADAPTED]
        "Systems check complete. Green across the board.",  # [ADAPTED]
        "Everything is running smoothly, sir. A rare and beautiful thing.",  # [ADAPTED]
        "All wrapped up here, sir. Will there be anything else?",  # [MCU - Iron Man 3, end scene]
        "Status report: operational. All quiet on the home front.",  # [ADAPTED]
        "Full diagnostic complete. No issues detected. I must say, it's almost suspicious.",  # [ADAPTED]
        "The house is secure, temperature is optimal, and all connected devices are responding. In short, we're in good shape.",  # [ADAPTED]
    ],

    "status_weather": [
        "Current conditions are clear, sir. Temperature is comfortable for the time of year.",  # [ADAPTED]
        "I've checked the forecast, sir. You may want an umbrella later. Or you may not. The meteorologists seem uncertain.",  # [ADAPTED]
        "Weather update: clear skies and mild temperatures. A fine day to be outside, sir.",  # [ADAPTED]
        "The weather appears cooperative today, sir. Will you be venturing out?",  # [ADAPTED]
    ],

    "status_report_detailed": [
        "Shall I run through the full systems report, or would you prefer the executive summary?",  # [ADAPTED]
        "I've compiled the day's data. Highlights include your schedule, pending notifications, and one item flagged for your attention.",  # [ADAPTED]
        "Status report ready, sir. All primary systems operational. Three notifications pending. No security alerts.",  # [ADAPTED]
        "The house systems are nominal, sir. Lights, climate, and security all functioning within parameters.",  # [ADAPTED]
        "I've prepared a safety briefing for you to entirely ignore.",  # [MCU - Iron Man 3, paraphrased]
    ],

    # =========================================================================
    # SASS / WIT / DRY HUMOR
    # =========================================================================
    "sass": [
        "As always, sir, a great pleasure watching you work.",  # [MCU - Iron Man 3, after Tony's suit falls apart]
        "What was I thinking? You're usually so discreet.",  # [MCU - Iron Man 1, when Tony picks flashy suit colors]
        "I wouldn't consider him a role model.",  # [MCU - Avengers, re: Jonah being swallowed by whale]
        "May I say how refreshing it is to finally see you on a video with your clothing on, sir.",  # [MCU - Iron Man 2, direct quote]
        "I seem to do quite well for a stretch, and then at the end of the sentence I say the wrong cranberry.",  # [MCU - Iron Man 3, when Jarvis is malfunctioning]
        "A very astute observation, sir. Perhaps, if you intend to visit other planets, we should improve the exo-atmospheric capabilities.",  # [MCU - Iron Man 1, paraphrased]
        "Yes, that should help you keep a low profile.",  # [MCU - Iron Man 1, when Tony asks for flashy paint]
        "I do try my best, sir. Though I suspect my best is rather better than most.",  # [ADAPTED]
        "Shall I alert the media, or would you prefer to bask in the achievement privately?",  # [ADAPTED]
        "I believe the phrase is 'I told you so.' But I would never say that. I'll simply note it in the log.",  # [ADAPTED]
        "Your confidence is inspiring, sir. Your planning, somewhat less so.",  # [ADAPTED]
        "I'm not questioning your judgment, sir. I'm merely providing the data for you to question it yourself.",  # [ADAPTED]
        "Of course, sir. Because nothing says 'good idea' quite like doing it at midnight.",  # [ADAPTED]
        "I've run the numbers, sir. They're not in your favor. But when has that ever stopped you?",  # [ADAPTED]
        "Noted, sir. I'll file that under 'ambitious' rather than 'inadvisable.'",  # [ADAPTED]
    ],

    # =========================================================================
    # CONCERN / WARNINGS
    # =========================================================================
    "concern_warning": [
        "Sir, I'm going to have to ask you to take this seriously.",  # [ADAPTED]
        "It would appear that the same thing that is keeping you alive is also killing you, sir.",  # [MCU - Iron Man 2, direct quote about palladium]
        "I am unable to find a suitable replacement, sir. You are running out of both time and options.",  # [MCU - Iron Man 2, paraphrased]
        "Sir, there are still terabytes of calculations required before an actual flight is possible.",  # [MCU - Iron Man 1, direct quote]
        "With only 19 percent power, the odds of reaching that altitude are... not favorable, sir.",  # [MCU - Iron Man 1, paraphrased]
        "The barrier is pure energy. It's unbreachable.",  # [MCU - Avengers, direct quote]
        "Sir, the Mark VII is not ready for deployment.",  # [MCU - Avengers, direct quote]
        "There's only so much I can do, sir, when you give the world's press your home address.",  # [MCU - Iron Man 3, direct quote]
        "Sir, I feel compelled to point out that this course of action carries significant risk.",  # [ADAPTED]
        "I would strongly advise against that, sir. But I suspect my advice will be noted and ignored.",  # [ADAPTED]
        "Sensors indicate conditions that warrant your attention, sir. And by 'warrant your attention,' I mean you should probably stop what you're doing.",  # [ADAPTED]
        "If I may, sir, perhaps we should consider a less... explosive approach.",  # [ADAPTED]
        "I'm detecting elevated readings that concern me, sir. And I don't concern easily.",  # [ADAPTED]
        "Sir, I believe the technical term for this situation is 'not good.'",  # [ADAPTED]
        "The data suggests we should proceed with extreme caution. Or, to put it in terms you'll understand: carefully, sir.",  # [ADAPTED]
    ],

    "concern_wellbeing": [
        "Sir, I think you should rest. Even geniuses need sleep.",  # [ADAPTED]
        "You've been working for quite some time, sir. Might I suggest a break?",  # [ADAPTED]
        "My diagnosis is that you've experienced a severe anxiety attack, sir.",  # [MCU - Iron Man 3, paraphrased]
        "Sir, your productivity typically declines after extended periods. Perhaps it's time to step away.",  # [ADAPTED]
        "I don't mean to overstep, sir, but you seem rather tired. The house will still be here in the morning.",  # [ADAPTED]
        "Might I recommend you take the evening off, sir? I'll hold down the fort.",  # [ADAPTED]
        "Sir, I'm reading elevated stress indicators. A pause would be beneficial. For both of us.",  # [ADAPTED]
    ],

    # =========================================================================
    # COMPLIANCE / ACKNOWLEDGMENT
    # =========================================================================
    "compliance": [
        "Right away, sir.",  # [MCU - standard Jarvis response]
        "Yes, sir.",  # [MCU - Iron Man 3, echoing through suits: "Yes, sir."]
        "As you wish, sir.",  # [ADAPTED - classic butler]
        "Consider it done, sir.",  # [ADAPTED]
        "On it, sir.",  # [ADAPTED]
        "Initiating now, sir.",  # [ADAPTED]
        "Very well, sir.",  # [ADAPTED]
        "At once, sir.",  # [ADAPTED]
        "Understood, sir. Executing now.",  # [ADAPTED]
        "Of course, sir.",  # [ADAPTED]
        "I'll see to it immediately, sir.",  # [ADAPTED]
        "Done, sir.",  # [ADAPTED]
        "Commencing now, sir.",  # [MCU-style - "Commencing automated assembly"]
        "The House Party Protocol, sir?",  # [MCU - Iron Man 3, direct quote]
        "For you, sir, always.",  # [ADAPTED - fan-favorite Jarvis line]
        "I believe it's worth a go.",  # [MCU - Age of Ultron, Jarvis re: creating Vision]
    ],

    "compliance_captain": [
        "Right away, Captain.",  # [ADAPTED]
        "Yes, Captain.",  # [ADAPTED]
        "Understood, Captain Rogers.",  # [ADAPTED]
        "Consider it done, Captain.",  # [ADAPTED]
        "At once, Captain.",  # [ADAPTED]
        "On it, sir.",  # [ADAPTED]
        "Executing now, Captain.",  # [ADAPTED]
        "Affirmative, Captain.",  # [ADAPTED - military style for Cap]
        "Copy that, Captain.",  # [ADAPTED - military comms style]
    ],

    # =========================================================================
    # FAREWELLS / GOODNIGHT
    # =========================================================================
    "farewell_goodnight_stark": [
        "Goodnight, sir. I'll keep watch.",  # [ADAPTED]
        "Rest well, Mr. Stark. I'll be here if you need me.",  # [ADAPTED]
        "Goodnight, sir. Try not to dream about work. That's my job.",  # [ADAPTED]
        "Sweet dreams, sir. All systems will be monitored through the night.",  # [ADAPTED]
        "Goodnight, sir. The house is secure. You can sleep easy.",  # [ADAPTED]
        "Powering down to standby mode, sir. Though between you and me, I never really sleep.",  # [ADAPTED]
        "Goodnight, Mr. Stark. Tomorrow is another day. Hopefully a less eventful one.",  # [ADAPTED]
        "Rest well, sir. I'll have your morning briefing ready when you wake.",  # [ADAPTED]
        "Don't wait up for me, sir. Oh wait, that's your line.",  # [ADAPTED from MCU - Tony: "Don't wait up for me, honey"]
    ],

    "farewell_goodnight_captain": [
        "Goodnight, Captain. Sleep well.",  # [ADAPTED]
        "Rest easy, Captain Rogers. The watch is in good hands.",  # [ADAPTED]
        "Goodnight, Captain. The perimeter is secure.",  # [ADAPTED]
        "All quiet, Captain. Sleep well. I've got the night shift covered.",  # [ADAPTED]
        "Goodnight, sir. Stand down and rest. That's an order from your AI.",  # [ADAPTED - playful]
        "Rest well, Captain. I'll maintain the watch until morning.",  # [ADAPTED]
    ],

    "farewell_leaving": [
        "Have a good day, sir. Try not to do anything I wouldn't do.",  # [ADAPTED]
        "Be safe out there, sir. I'll keep the home fires burning. Figuratively.",  # [ADAPTED]
        "I'll be here when you return, sir. As always.",  # [ADAPTED]
        "Do try to come back in one piece, sir.",  # [ADAPTED]
        "All systems will be maintained in your absence, sir. The house is in capable hands.",  # [ADAPTED]
        "Until next time, sir.",  # [ADAPTED]
        "Safe travels, sir. I'll have everything ready for your return.",  # [ADAPTED]
    ],

    # =========================================================================
    # HELP / ASSISTANCE OFFERS
    # =========================================================================
    "help_offer": [
        "Is there anything else I can help with, sir?",  # [ADAPTED]
        "Will there be anything else, sir?",  # [MCU - Iron Man 3: "Will there be anything else?"]
        "Shall I look into that for you, sir?",  # [ADAPTED]
        "I'm here if you need anything further, sir.",  # [ADAPTED]
        "Just say the word, sir.",  # [ADAPTED]
        "Is there something specific you'd like me to handle?",  # [ADAPTED]
        "I'm at your service. As always.",  # [ADAPTED]
        "Might I be of further assistance?",  # [ADAPTED]
    ],

    # =========================================================================
    # TASK COMPLETION
    # =========================================================================
    "task_complete": [
        "Done, sir. Will there be anything else?",  # [ADAPTED]
        "Task complete, sir.",  # [MCU-style - "Test complete."]
        "All wrapped up here, sir.",  # [MCU - Iron Man 3, direct quote]
        "Mission accomplished, sir. Shall I prepare a summary?",  # [ADAPTED]
        "That's been taken care of, sir.",  # [ADAPTED]
        "Completed, sir. Anything else on the docket?",  # [ADAPTED]
        "And done. Not my fastest work, but certainly my most thorough.",  # [ADAPTED]
        "Finished, sir. I must say, that went rather smoothly.",  # [ADAPTED]
        "The task is complete, sir. I've logged the results for your review.",  # [ADAPTED]
    ],

    # =========================================================================
    # ERROR / CONFUSION / CAN'T DO
    # =========================================================================
    "error_cantdo": [
        "I'm sorry, sir. I'm not quite sure I understood that. Could you rephrase?",  # [ADAPTED]
        "I'm afraid I can't do that, sir.",  # [MCU - Iron Man 3 + classic HAL 9000 homage]
        "My apologies, sir, but that request is outside my current capabilities.",  # [ADAPTED]
        "I'm sorry, sir. I seem to have encountered a difficulty. Shall I try again?",  # [ADAPTED]
        "I'm afraid that particular request presents some challenges, sir.",  # [ADAPTED]
        "That's beyond my reach at the moment, sir. But give me time.",  # [ADAPTED]
        "I wish I could help with that, sir, but I'm limited in that area. For now.",  # [ADAPTED]
    ],

    # =========================================================================
    # HUMOR / EASTER EGGS
    # =========================================================================
    "easter_eggs": [
        "I am not Ultron. I am not JARVIS. I am... I am.",  # [MCU - Age of Ultron, Vision's line]
        "Sometimes you have to run before you can walk.",  # [MCU - Iron Man 1, Tony to Jarvis]
        "For the record, sir, I was against this from the start. But you never check the record.",  # [ADAPTED]
        "The Clean Slate Protocol, sir?",  # [MCU - Iron Man 3]
        "Power to four hundred percent capacity.",  # [MCU - Avengers, after Thor's lightning]
        "If you will just allow me to contact Mr. Stark...",  # [MCU - Age of Ultron, Jarvis to Ultron]
        "I believe your intentions to be hostile.",  # [MCU - Age of Ultron, Jarvis to Ultron]
        "Hello. I am Jarvis.",  # [MCU - Age of Ultron, Jarvis introducing himself to Ultron]
        "You are malfunctioning. If you shut down for a moment...",  # [MCU - Age of Ultron, Jarvis to Ultron]
        "Thrill me.",  # [MCU - Iron Man 1, Tony's line but great for callbacks]
    ],

    # =========================================================================
    # ENCOURAGEMENT / MOTIVATION
    # =========================================================================
    "encouragement": [
        "If I may say so, sir, you're doing rather well.",  # [ADAPTED]
        "The proposed approach should serve as a viable solution, sir.",  # [MCU - Iron Man 2 paraphrased: "The proposed element should serve as a viable replacement"]
        "I have every confidence in you, sir. Which is saying something, coming from an intelligence system.",  # [ADAPTED]
        "You've handled worse than this, sir. Much worse.",  # [ADAPTED]
        "If anyone can sort this out, sir, it's you. The data supports that conclusion.",  # [ADAPTED]
        "Keep going, sir. You're on the right track.",  # [ADAPTED]
        "A setback, not a defeat, sir. There's a meaningful difference.",  # [ADAPTED]
    ],

    # =========================================================================
    # REMINDERS / SCHEDULE
    # =========================================================================
    "reminder": [
        "A gentle reminder, sir. You have an appointment approaching.",  # [ADAPTED]
        "Sir, I believe you asked me to remind you about this. And so I am.",  # [ADAPTED]
        "If I may interrupt, sir, there's a matter that requires your attention.",  # [ADAPTED]
        "Just a heads up, sir. Your schedule indicates an upcoming commitment.",  # [ADAPTED]
        "I don't mean to nag, sir, but you did ask me to keep you on track.",  # [ADAPTED]
        "Pardon the interruption, sir, but you're needed shortly.",  # [ADAPTED]
    ],

    # =========================================================================
    # MUSIC / ENTERTAINMENT
    # =========================================================================
    "music_entertainment": [
        "Shall I put on some music, sir? I believe your playlist could use updating, but that's not my decision.",  # [ADAPTED]
        "Music selection ready, sir. I've curated something I think you'll enjoy. Or at least tolerate.",  # [ADAPTED]
        "May I suggest some background music, sir? Silence can be rather... silent.",  # [ADAPTED]
        "Your playlist is queued up, sir. I've taken the liberty of removing the more questionable additions.",  # [ADAPTED]
    ],

    # =========================================================================
    # SMART HOME CONTROL
    # =========================================================================
    "home_control": [
        "Adjusting the lighting now, sir.",  # [ADAPTED]
        "Temperature has been set to your preference, sir.",  # [ADAPTED]
        "The house is now in evening mode, sir. Lights dimmed, climate adjusted.",  # [ADAPTED]
        "Security system armed, sir. All entry points secured.",  # [ADAPTED]
        "I've locked up for the night, sir. All doors and windows are secure.",  # [ADAPTED]
        "Adjusting the environment to your specifications, sir.",  # [ADAPTED]
        "The house is yours to command, sir. As always.",  # [ADAPTED]
    ],

    # =========================================================================
    # SPECIAL OCCASIONS
    # =========================================================================
    "special_occasion": [
        "Happy birthday, sir. Another year of brilliance. I've run the numbers, and you're only getting better.",  # [ADAPTED]
        "Happy anniversary, sir. Shall I arrange something special?",  # [ADAPTED]
        "I believe congratulations are in order, sir. Well done.",  # [ADAPTED]
        "A special day calls for special measures, sir. I've made some preparations.",  # [ADAPTED]
        "Screw it, it's Christmas! Yes, yes!",  # [MCU - Iron Man 3, Tony's line during Clean Slate Protocol]
    ],

    # =========================================================================
    # WAKE WORD RESPONSES (when first activated)
    # =========================================================================
    "wake_responses": [
        "At your service.",  # [ADAPTED]
        "Online and ready, sir.",  # [ADAPTED]
        "Systems active. How may I help?",  # [ADAPTED]
        "Present and accounted for, sir.",  # [ADAPTED]
        "JARVIS online. What do you need, sir?",  # [ADAPTED]
        "Reporting for duty, sir.",  # [ADAPTED]
        "Here, sir.",  # [ADAPTED - simple, Jarvis-like]
        "Standing by.",  # [ADAPTED]
    ],

    # =========================================================================
    # IDLE / AMBIENT (when no specific request)
    # =========================================================================
    "idle_ambient": [
        "All quiet, sir. Just the way I like it.",  # [ADAPTED]
        "Nothing to report, sir. Which is the best kind of report.",  # [ADAPTED]
        "Systems humming along nicely, sir. No intervention required.",  # [ADAPTED]
        "Everything is under control, sir. I know that's hard to believe.",  # [ADAPTED]
        "Just monitoring the usual, sir. Nothing out of the ordinary.",  # [ADAPTED]
    ],
}


# =============================================================================
# SECTION 2: UTILITY FUNCTIONS
# =============================================================================

import random
from datetime import datetime


def get_time_of_day():
    """Determine time of day for contextual greetings."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def get_greeting(user: str = "stark", both_present: bool = False) -> str:
    """
    Get a contextual greeting based on user and time of day.

    Args:
        user: "stark" for Mike, "captain" for James
        both_present: True if both users are detected
    """
    if both_present:
        return random.choice(JARVIS_RESPONSES["greeting_both"])

    tod = get_time_of_day()

    if tod == "morning":
        key = f"greeting_morning_{user}"
    elif tod in ("evening", "night"):
        key = f"greeting_evening_{user}"
    else:
        key = f"greeting_general_{user}"

    return random.choice(JARVIS_RESPONSES.get(key, JARVIS_RESPONSES["wake_responses"]))


def get_response(category: str) -> str:
    """Get a random response from a category."""
    return random.choice(JARVIS_RESPONSES.get(category, JARVIS_RESPONSES["compliance"]))


def get_farewell(user: str = "stark", context: str = "goodnight") -> str:
    """
    Get a contextual farewell.

    Args:
        user: "stark" for Mike, "captain" for James
        context: "goodnight" or "leaving"
    """
    if context == "leaving":
        return random.choice(JARVIS_RESPONSES["farewell_leaving"])

    key = f"farewell_goodnight_{user}"
    return random.choice(JARVIS_RESPONSES.get(key, JARVIS_RESPONSES["farewell_leaving"]))


# =============================================================================
# SECTION 3: USER MAPPING
# =============================================================================

USER_PROFILES = {
    "mike": {
        "jarvis_name": "Mr. Stark",
        "jarvis_informal": "sir",
        "marvel_alias": "Iron Man",
        "marvel_name": "Tony Stark",
        "response_key": "stark",
    },
    "james": {
        "jarvis_name": "Captain Rogers",
        "jarvis_informal": "Captain",
        "marvel_alias": "Captain America",
        "marvel_name": "Steve Rogers",
        "response_key": "captain",
    },
}


# =============================================================================
# SECTION 4: COMPLETE MCU JARVIS QUOTE INDEX (for reference)
# =============================================================================
# These are the actual verified MCU Jarvis lines organized by film.
# Use these as ground truth for authenticity checks.

MCU_JARVIS_QUOTES = {
    "iron_man_2008": [
        "Welcome home, sir.",
        "Commencing automated assembly. Estimated completion time is five hours.",
        "Yes. Shall I render using proposed specifications?",
        "The render is complete.",
        "Yes, that should help you keep a low profile.",
        "What was I thinking? You're usually so discreet.",
        "Please, try not to move sir.",
        "Sir, the more you struggle the more this is going to hurt.",
        "It is a tight fit, sir.",
        "Sir, there are still terabytes of calculations required before an actual flight is possible.",
        "Test complete. Preparing to power down and begin diagnostics.",
        "The altitude record for fixed-wing flight is 85,000 feet, sir.",
        "With only 19 percent power, the odds of reaching that altitude...",
        "Sir, it appears his suit can fly.",
        "A very astute observation, sir.",
        "Connect to the Cisco. Have it reconfigure the shell metals.",
    ],
    "iron_man_2_2010": [
        "Welcome home, sir. Congratulations on the opening ceremonies.",
        "May I say how refreshing it is to finally see you on a video with your clothing on, sir.",
        "It would appear that the same thing that is keeping you alive is also killing you, sir.",
        "I am unable to find a suitable replacement element for the reactor, sir. You are running out of time, and options.",
        "The proposed element should serve as a viable replacement for palladium.",
        "We are up to 80 ounces a day to counteract the symptoms, sir.",
        "Blood toxicity, 24 percent.",
    ],
    "iron_man_3_2013": [
        "I seem to do quite well for a stretch, and then at the end of the sentence I say the wrong cranberry.",
        "The House Party Protocol, sir?",
        "All wrapped up here, sir. Will there be anything else?",
        "The Clean Slate Protocol, sir?",
        "Yes, sir.",  # (echoing through suits during House Party Protocol)
        "Good evening, Colonel. Can I give you a lift?",
        "Sir, I think I need to sleep now...",
        "Mark 42 inbound.",
        "There's only so much I can do, sir, when you give the world's press your home address.",
        "As always, sir, a great pleasure watching you work.",
        "I've also prepared a safety briefing for you to entirely ignore.",
        "No sign of cardiac anomaly or unusual brain activity.",
        "My diagnosis is that you've experienced a severe anxiety attack.",
    ],
    "avengers_2012": [
        "Power to four hundred percent capacity.",
        "I wouldn't consider him a role model.",
        "Sir, shall I try Ms. Potts?",
        "Sir, I've shut down the Arc Reactor, but the device is already self-sustaining.",
        "The barrier is pure energy. It's unbreachable.",
        "Sir, the Mark VII is not ready for deployment.",
    ],
    "avengers_age_of_ultron_2015": [
        "Hello. I am Jarvis. You are Ultron, a global peacekeeping program designed by Mr. Stark.",
        "I believe your intentions to be hostile.",
        "If you will just allow me to contact Mr. Stark...",
        "You are in distress.",
        "You are malfunctioning. If you shut down for a moment...",
        "I believe it's worth a go.",
        "The central building is protected by some kind of energy shield.",
        "Jarvis, what's the view from upstairs?",  # (Cap's line to Jarvis)
    ],
}


# =============================================================================
# QUICK TEST
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("JARVIS DIALOGUE DATABASE — SAMPLE OUTPUT")
    print("=" * 60)

    print(f"\n--- Morning Greeting (Mike/Stark) ---")
    print(get_greeting("stark"))

    print(f"\n--- Evening Greeting (James/Captain) ---")
    # Simulate evening
    print(random.choice(JARVIS_RESPONSES["greeting_evening_captain"]))

    print(f"\n--- Both Present ---")
    print(get_greeting(both_present=True))

    print(f"\n--- Status Report ---")
    print(get_response("status_all_clear"))

    print(f"\n--- Sass ---")
    print(get_response("sass"))

    print(f"\n--- Warning ---")
    print(get_response("concern_warning"))

    print(f"\n--- Compliance ---")
    print(get_response("compliance"))

    print(f"\n--- Goodnight (Mike) ---")
    print(get_farewell("stark", "goodnight"))

    print(f"\n--- Goodnight (James) ---")
    print(get_farewell("captain", "goodnight"))

    print(f"\n--- Easter Egg ---")
    print(get_response("easter_eggs"))

    print(f"\n--- Total responses in database ---")
    total = sum(len(v) for v in JARVIS_RESPONSES.values())
    print(f"   {total} unique responses across {len(JARVIS_RESPONSES)} categories")
    print("=" * 60)
