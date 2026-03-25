"""Voice Interface Server — V6 Multi-Channel

ElevenLabs TTS + Whisper STT on Mac Studio.

Endpoints:
  POST /notify — text → TTS → play through speakers (P0 alerts)
  POST /listen — STT → text → Jake → TTS response
  POST /speak  — text → TTS → audio file (for other channels to use)
  GET  /status — server health check

Voice responses are shorter and more conversational than text.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class VoiceConfig:
    """Voice server configuration."""
    provider: str = "elevenlabs"
    voice_id: str = "jake-custom"
    model: str = "eleven_multilingual_v2"
    stability: float = 0.5
    similarity_boost: float = 0.8
    output_format: str = "mp3_44100_128"
    max_response_words: int = 200
    wake_word: str = "Hey Jake"
    stt_provider: str = "whisper"
    stt_model: str = "whisper-1"
    port: int = 8888


class VoiceServer:
    """Voice interface for Jake.

    Provides TTS (text-to-speech) and STT (speech-to-text) capabilities.
    Designed to run as a service on Mac Studio.
    """

    CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "voice.json"
    AUDIO_DIR = Path(__file__).parent / "audio"

    def __init__(self, config: VoiceConfig | None = None):
        self.config = config or self._load_config()
        self.AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    def text_to_speech(self, text: str) -> Path | None:
        """Convert text to speech audio file.

        Returns path to the generated audio file, or None on failure.
        """
        # Trim for voice brevity
        words = text.split()
        if len(words) > self.config.max_response_words:
            text = " ".join(words[:self.config.max_response_words]) + "."

        if self.config.provider == "elevenlabs":
            return self._elevenlabs_tts(text)
        elif self.config.provider == "say":
            return self._macos_say(text)
        return None

    def speech_to_text(self, audio_path: Path) -> str | None:
        """Convert speech audio to text.

        Returns transcribed text, or None on failure.
        """
        if self.config.stt_provider == "whisper":
            return self._whisper_stt(audio_path)
        return None

    def notify(self, text: str) -> bool:
        """Play a notification through Mac speakers (P0 alerts)."""
        audio = self.text_to_speech(text)
        if not audio:
            # Fallback to macOS say command
            try:
                subprocess.run(
                    ["say", "-v", "Samantha", text[:500]],
                    timeout=30,
                )
                return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return False

        return self._play_audio(audio)

    def format_for_voice(self, text: str) -> str:
        """Convert text response to voice-friendly format.

        Voice responses should be:
        - Conversational, not formal
        - Short (< 200 words)
        - No markdown formatting
        - No URLs or code blocks
        - Natural pauses (commas, periods)
        """
        import re

        result = text

        # Remove all markdown
        result = re.sub(r"^#{1,6}\s+", "", result, flags=re.MULTILINE)
        result = re.sub(r"\*\*(.+?)\*\*", r"\1", result)
        result = re.sub(r"\*(.+?)\*", r"\1", result)
        result = re.sub(r"```[\s\S]*?```", "", result)
        result = re.sub(r"`(.+?)`", r"\1", result)
        result = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", result)

        # Remove bullet points
        result = re.sub(r"^[\s]*[-*+]\s+", "", result, flags=re.MULTILINE)
        result = re.sub(r"^[\s]*\d+\.\s+", "", result, flags=re.MULTILINE)

        # Remove excess whitespace
        result = re.sub(r"\n{2,}", ". ", result)
        result = re.sub(r"\n", " ", result)
        result = re.sub(r"\s{2,}", " ", result)

        # Trim to word limit
        words = result.split()
        if len(words) > self.config.max_response_words:
            result = " ".join(words[:self.config.max_response_words]) + "."

        return result.strip()

    def _elevenlabs_tts(self, text: str) -> Path | None:
        """Generate speech using ElevenLabs API."""
        try:
            from elevenlabs import generate, save
        except ImportError:
            # Fallback: try the REST API directly
            return self._elevenlabs_rest(text)

        try:
            audio = generate(
                text=text,
                voice=self.config.voice_id,
                model=self.config.model,
            )
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            output = self.AUDIO_DIR / f"tts-{ts}.mp3"
            save(audio, str(output))
            return output
        except Exception:
            return None

    def _elevenlabs_rest(self, text: str) -> Path | None:
        """ElevenLabs TTS via REST API (no SDK dependency)."""
        import os
        api_key = os.environ.get("ELEVENLABS_API_KEY", "")
        if not api_key:
            return None

        try:
            import httpx
            resp = httpx.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{self.config.voice_id}",
                headers={"xi-api-key": api_key, "Content-Type": "application/json"},
                json={
                    "text": text,
                    "model_id": self.config.model,
                    "voice_settings": {
                        "stability": self.config.stability,
                        "similarity_boost": self.config.similarity_boost,
                    },
                },
                timeout=30,
            )
            if resp.status_code == 200:
                ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
                output = self.AUDIO_DIR / f"tts-{ts}.mp3"
                output.write_bytes(resp.content)
                return output
        except Exception:
            pass
        return None

    def _macos_say(self, text: str) -> Path | None:
        """Fallback: macOS built-in say command → AIFF file."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        output = self.AUDIO_DIR / f"tts-{ts}.aiff"
        try:
            subprocess.run(
                ["say", "-v", "Samantha", "-o", str(output), text[:1000]],
                timeout=30,
            )
            return output if output.exists() else None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def _whisper_stt(self, audio_path: Path) -> str | None:
        """Transcribe audio using OpenAI Whisper API."""
        import os
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return None

        try:
            import httpx
            with open(audio_path, "rb") as f:
                resp = httpx.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    files={"file": (audio_path.name, f, "audio/mpeg")},
                    data={"model": self.config.stt_model},
                    timeout=30,
                )
            if resp.status_code == 200:
                return resp.json().get("text", "")
        except Exception:
            pass
        return None

    def _play_audio(self, audio_path: Path) -> bool:
        """Play audio through Mac speakers."""
        try:
            subprocess.run(
                ["afplay", str(audio_path)],
                timeout=60,
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _load_config(self) -> VoiceConfig:
        if self.CONFIG_PATH.exists():
            try:
                data = json.loads(self.CONFIG_PATH.read_text())
                return VoiceConfig(**{k: v for k, v in data.items() if hasattr(VoiceConfig, k)})
            except (json.JSONDecodeError, OSError, TypeError):
                pass
        return VoiceConfig()
