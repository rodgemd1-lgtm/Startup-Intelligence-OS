#!/usr/bin/env python3
"""
Claude Remote Bot — Control Claude Code from Telegram.

Lets Mike send prompts to Claude CLI from his phone, routed to the
correct project directory based on a prefix keyword.

Usage:
    python scripts/claude_remote_bot.py

Env:
    CLAUDE_REMOTE_BOT_TOKEN  — Telegram bot token (or read from ~/.jake/claude_remote_token)
"""

import asyncio
import logging
import os
import subprocess
import time
from pathlib import Path

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ALLOWED_CHAT_ID = 8634072195

PROJECTS: dict[str, str] = {
    "startup": "~/Startup-Intelligence-OS",
    "os": "~/Startup-Intelligence-OS",
    "oracle": "~/Desktop/oracle-health-ai-enablement",
    "alex": "~/Desktop/alex-recruiting-project/alex-recruiting",
    "james": "~/Desktop/james-os",
}

DEFAULT_PROJECT = "~/Startup-Intelligence-OS"

CLAUDE_CLI = "/Users/mikerodgers/.local/bin/claude"
CLAUDE_TIMEOUT = 300  # 5 minutes

BOOT_TIME = time.time()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("claude-remote")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_token() -> str:
    """Resolve bot token from env var or file."""
    token = os.environ.get("CLAUDE_REMOTE_BOT_TOKEN")
    if token:
        return token.strip()

    token_file = Path.home() / ".jake" / "claude_remote_token"
    if token_file.exists():
        return token_file.read_text().strip()

    raise RuntimeError(
        "No bot token found. Set CLAUDE_REMOTE_BOT_TOKEN or create ~/.jake/claude_remote_token"
    )


def is_authorised(update: Update) -> bool:
    chat_id = update.effective_chat.id
    if chat_id == ALLOWED_CHAT_ID:
        return True
    log.warning("Unauthorized access attempt from chat_id=%s user=%s", chat_id, update.effective_user)
    return False


def parse_project_and_prompt(text: str) -> tuple[str, str]:
    """Return (project_dir, prompt).

    If the message starts with a known prefix followed by ':', route to
    that project. Otherwise use the default.
    """
    text = text.strip()
    if ":" in text:
        prefix, _, rest = text.partition(":")
        key = prefix.strip().lower()
        if key in PROJECTS:
            return str(Path(PROJECTS[key]).expanduser()), rest.strip()
    return str(Path(DEFAULT_PROJECT).expanduser()), text


async def run_claude(project_dir: str, prompt: str) -> str:
    """Run claude CLI as a subprocess and return its output."""
    if not Path(project_dir).is_dir():
        return f"Project directory does not exist: {project_dir}"

    cmd = [
        CLAUDE_CLI,
        "-p", prompt,
        "--model", "sonnet",
        "--output-format", "text",
        "--max-budget-usd", "2.00",
        "--no-session-persistence",
    ]

    log.info("Running claude in %s: %s", project_dir, prompt[:120])

    try:
        proc = await asyncio.wait_for(
            asyncio.create_subprocess_exec(
                *cmd,
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ),
            timeout=5,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=CLAUDE_TIMEOUT,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return "Task timed out after 5 minutes."

        if proc.returncode != 0:
            err = stderr.decode().strip()
            return f"Claude CLI error (exit {proc.returncode}):\n{err}" if err else f"Claude CLI exited with code {proc.returncode}"

        output = stdout.decode().strip()
        return output if output else "(no output)"

    except asyncio.TimeoutError:
        return "Failed to start claude CLI within 5 seconds."
    except FileNotFoundError:
        return f"Claude CLI not found at {CLAUDE_CLI}"
    except Exception as exc:
        return f"Error running claude: {exc}"


def chunk_message(text: str, max_len: int = 4096) -> list[str]:
    """Split text into Telegram-safe chunks."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        chunks.append(text[:max_len])
        text = text[max_len:]
    return chunks


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorised(update):
        return

    text = update.message.text
    if not text:
        return

    project_dir, prompt = parse_project_and_prompt(text)
    project_name = Path(project_dir).name

    await update.message.chat.send_action(ChatAction.TYPING)
    await update.message.reply_text(f"Working on it... ({project_name})")

    result = await run_claude(project_dir, prompt)

    for chunk in chunk_message(result):
        await update.message.reply_text(chunk)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorised(update):
        return

    uptime_secs = int(time.time() - BOOT_TIME)
    hours, remainder = divmod(uptime_secs, 3600)
    minutes, secs = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {secs}s"

    projects_status = []
    for key, path in PROJECTS.items():
        expanded = Path(path).expanduser()
        exists = expanded.is_dir()
        projects_status.append(f"  {key}: {path} {'OK' if exists else 'MISSING'}")

    msg = (
        f"Claude Remote Bot\n"
        f"Uptime: {uptime_str}\n"
        f"Allowed chat: {ALLOWED_CHAT_ID}\n"
        f"Claude CLI: {CLAUDE_CLI}\n"
        f"Timeout: {CLAUDE_TIMEOUT}s\n\n"
        f"Projects:\n" + "\n".join(projects_status)
    )
    await update.message.reply_text(msg)


async def cmd_projects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorised(update):
        return

    lines = ["Available project prefixes:\n"]
    for key, path in PROJECTS.items():
        lines.append(f"  {key}: {path}")
    lines.append(f"\nDefault (no prefix): {DEFAULT_PROJECT}")
    lines.append("\nUsage: prefix: your prompt")
    lines.append("Example: oracle: what's the latest on the website")

    await update.message.reply_text("\n".join(lines))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    token = get_token()

    banner = (
        "\n"
        "===========================================\n"
        "  Claude Remote Bot\n"
        "===========================================\n"
        f"  Chat ID filter: {ALLOWED_CHAT_ID}\n"
        f"  Claude CLI:     {CLAUDE_CLI}\n"
        f"  Timeout:        {CLAUDE_TIMEOUT}s\n"
        f"  Projects:\n"
    )
    for key, path in PROJECTS.items():
        banner += f"    {key:10s} -> {path}\n"
    banner += f"  Default:        {DEFAULT_PROJECT}\n"
    banner += "===========================================\n"
    log.info(banner)

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("projects", cmd_projects))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    log.info("Bot starting long-poll...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
