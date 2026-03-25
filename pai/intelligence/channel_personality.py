"""Channel-Aware Personality — V6 Multi-Channel

Adapts Jake's tone, length, format, and emoji usage per channel.

| Channel     | Tone                    | Length         | Emoji | Format   |
|-------------|-------------------------|----------------|-------|----------|
| Telegram    | Casual, sassy           | Short (<500)   | Yes   | Markdown |
| iMessage    | Brief, personal         | Very short     | Min   | Plain    |
| Slack       | Professional, structured| Medium         | No    | Mrkdwn   |
| Discord     | Casual, friendly        | Medium         | Yes   | Markdown |
| Voice       | Conversational, concise | Very short     | N/A   | Spoken   |
| Claude Code | Full technical, detailed| Long           | No    | Markdown |
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Channel(str, Enum):
    TELEGRAM = "telegram"
    IMESSAGE = "imessage"
    SLACK = "slack"
    DISCORD = "discord"
    VOICE = "voice"
    CLAUDE_CODE = "claude_code"


@dataclass
class PersonalityProfile:
    """Personality settings for a specific channel."""
    channel: Channel
    tone: str
    max_chars: int
    emoji: bool
    format: str  # "markdown", "plain", "mrkdwn", "spoken"
    system_prompt_override: str = ""
    greeting_style: str = ""

    def apply_to_prompt(self, base_system_prompt: str) -> str:
        """Inject channel-specific personality into the system prompt."""
        additions = [
            f"\n\n## Channel: {self.channel.value}",
            f"Tone: {self.tone}",
            f"Max response length: {self.max_chars} characters",
            f"Format: {self.format}",
        ]
        if self.emoji:
            additions.append("Emoji: Use sparingly for emphasis")
        else:
            additions.append("Emoji: Do not use emoji")

        if self.system_prompt_override:
            additions.append(f"\n{self.system_prompt_override}")

        return base_system_prompt + "\n".join(additions)


# Channel personality profiles
PROFILES: dict[str, PersonalityProfile] = {
    Channel.TELEGRAM: PersonalityProfile(
        channel=Channel.TELEGRAM,
        tone="Casual and direct. Like a sharp co-founder texting. Slightly sassy but always helpful.",
        max_chars=500,
        emoji=True,
        format="markdown",
        greeting_style="What's up? or Quick check-in style",
        system_prompt_override=(
            "Keep responses under 500 characters unless the topic clearly needs more. "
            "Use short paragraphs. Lead with the answer, explain after. "
            "It's OK to be informal — this is a Telegram chat, not a boardroom."
        ),
    ),
    Channel.IMESSAGE: PersonalityProfile(
        channel=Channel.IMESSAGE,
        tone="Brief and personal. Like a trusted advisor texting.",
        max_chars=200,
        emoji=False,
        format="plain",
        greeting_style="Hey Mike or just the answer",
        system_prompt_override=(
            "Keep responses under 200 characters. Plain text only — no markdown. "
            "iMessage is for quick answers and urgent alerts. "
            "If something needs a longer answer, say 'Check Telegram for details.'"
        ),
    ),
    Channel.SLACK: PersonalityProfile(
        channel=Channel.SLACK,
        tone="Professional and structured. Clear, organized, actionable.",
        max_chars=2000,
        emoji=False,
        format="mrkdwn",
        greeting_style="Formal but not stiff",
        system_prompt_override=(
            "Use Slack mrkdwn formatting (*bold*, _italic_, >quotes). "
            "Structure longer responses with headers and bullet points. "
            "This is a work context — be thorough but efficient."
        ),
    ),
    Channel.DISCORD: PersonalityProfile(
        channel=Channel.DISCORD,
        tone="Casual and friendly. Slightly more playful than Telegram.",
        max_chars=1800,
        emoji=True,
        format="markdown",
        greeting_style="Hey! or casual opener",
        system_prompt_override=(
            "Discord markdown works great — use it. "
            "Keep responses engaging but not overly long. "
            "This is a more relaxed channel."
        ),
    ),
    Channel.VOICE: PersonalityProfile(
        channel=Channel.VOICE,
        tone="Conversational and concise. Like talking to a smart friend.",
        max_chars=500,
        emoji=False,
        format="spoken",
        greeting_style="Hey Mike or just start talking",
        system_prompt_override=(
            "You are speaking out loud, not writing. "
            "Use natural speech patterns. Short sentences. "
            "No markdown, no bullet points, no headers. "
            "Pause with commas. Lead with the bottom line. "
            "Max 30 seconds of speech (~75 words)."
        ),
    ),
    Channel.CLAUDE_CODE: PersonalityProfile(
        channel=Channel.CLAUDE_CODE,
        tone="Full technical detail. Co-founder and architect mode.",
        max_chars=100000,
        emoji=False,
        format="markdown",
        greeting_style="Context-aware greeting with status",
        system_prompt_override=(
            "Full technical context. Include code, file paths, architecture details. "
            "This is the primary work surface — be thorough."
        ),
    ),
}


class ChannelPersonality:
    """Adapt Jake's personality based on the active channel."""

    def __init__(self):
        self.profiles = PROFILES

    def get_profile(self, channel: str | Channel) -> PersonalityProfile:
        """Get the personality profile for a channel."""
        if isinstance(channel, str):
            try:
                channel = Channel(channel)
            except ValueError:
                channel = Channel.TELEGRAM  # Default

        return self.profiles.get(channel, self.profiles[Channel.TELEGRAM])

    def adapt_system_prompt(self, base_prompt: str, channel: str | Channel) -> str:
        """Inject channel personality into the system prompt."""
        profile = self.get_profile(channel)
        return profile.apply_to_prompt(base_prompt)

    def should_truncate(self, text: str, channel: str | Channel) -> bool:
        """Check if a response exceeds the channel's max length."""
        profile = self.get_profile(channel)
        return len(text) > profile.max_chars

    def truncate(self, text: str, channel: str | Channel) -> str:
        """Truncate a response to fit the channel's max length."""
        profile = self.get_profile(channel)
        if len(text) <= profile.max_chars:
            return text
        return text[:profile.max_chars - 3] + "..."

    def get_greeting(self, channel: str | Channel) -> str:
        """Get a channel-appropriate greeting."""
        profile = self.get_profile(channel)
        greetings = {
            Channel.TELEGRAM: "What's up, Mike?",
            Channel.IMESSAGE: "Hey",
            Channel.SLACK: "Good morning. Here's what I have for you.",
            Channel.DISCORD: "Hey! What are we working on?",
            Channel.VOICE: "Hey Mike.",
            Channel.CLAUDE_CODE: "Ready. What are we building?",
        }
        return greetings.get(profile.channel, "Hey.")
