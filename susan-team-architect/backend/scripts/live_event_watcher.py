#!/usr/bin/env python3
"""Live event watcher — polls a live results page for an athlete and sends Telegram alerts.

Designed to run as a detached subprocess outside Hermes' sandbox.
Uses Playwright (if available) or requests+BeautifulSoup for JS-rendered pages.

Usage:
    python scripts/live_event_watcher.py \
        --url "https://uwwtrack.anet.live/meets/62410/live" \
        --athlete "Rodgers" \
        --event "Shot Put" \
        --interval 60 \
        --timeout 180

    python scripts/live_event_watcher.py --dry-run --url "..." --athlete "Rodgers"
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path.home() / ".hermes/.env")

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("live-watcher")

# ---------------------------------------------------------------------------
# Telegram helpers
# ---------------------------------------------------------------------------

def discover_chat_id(token: str) -> str | None:
    """Auto-discover Telegram chat ID from recent bot updates."""
    cache_file = Path.home() / ".jake" / "telegram_chat_id"
    if cache_file.is_file():
        cached = cache_file.read_text().strip()
        if cached:
            return cached

    try:
        resp = requests.get(
            f"https://api.telegram.org/bot{token}/getUpdates",
            params={"offset": -1, "limit": 1},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("result", [])
            if results:
                msg = results[0].get("message", results[0].get("callback_query", {}).get("message", {}))
                chat = msg.get("chat", {})
                chat_id = str(chat.get("id", ""))
                if chat_id:
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                    cache_file.write_text(chat_id)
                    return chat_id
    except requests.RequestException:
        pass
    return None


def send_telegram(message: str, token: str, chat_id: str) -> bool:
    """Send a message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=15,
        )
        if resp.status_code == 200:
            logger.info("Telegram message sent successfully")
            return True
        logger.error("Telegram API error: %d — %s", resp.status_code, resp.text)
        return False
    except requests.RequestException as e:
        logger.error("Telegram send failed: %s", e)
        return False


# ---------------------------------------------------------------------------
# Page fetching — Playwright preferred, falls back to requests
# ---------------------------------------------------------------------------

_playwright_browser = None


def fetch_page_playwright(url: str, wait_ms: int = 5000) -> str:
    """Fetch a JS-rendered page using Playwright. Returns page text content."""
    global _playwright_browser
    try:
        from playwright.sync_api import sync_playwright

        if _playwright_browser is None:
            pw = sync_playwright().start()
            _playwright_browser = pw.chromium.launch(headless=True)

        page = _playwright_browser.new_page()
        page.goto(url, timeout=15000)
        page.wait_for_timeout(wait_ms)
        content = page.content()
        text = page.inner_text("body")
        page.close()
        return text
    except ImportError:
        logger.warning("Playwright not available — falling back to requests")
        return fetch_page_requests(url)
    except Exception as e:
        logger.error("Playwright fetch failed: %s — falling back to requests", e)
        return fetch_page_requests(url)


def fetch_page_requests(url: str) -> str:
    """Fetch page via requests. Won't work for JS-rendered SPAs but tries."""
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        return resp.text
    except requests.RequestException as e:
        logger.error("Request fetch failed: %s", e)
        return ""


def fetch_page(url: str, use_playwright: bool = True) -> str:
    """Fetch a page, preferring Playwright for JS-rendered content."""
    if use_playwright:
        return fetch_page_playwright(url)
    return fetch_page_requests(url)


# ---------------------------------------------------------------------------
# Athlete search logic
# ---------------------------------------------------------------------------

def search_for_athlete(page_text: str, athlete_name: str, event_name: str | None = None) -> dict:
    """Search the page text for an athlete's name and context.

    Returns a dict with:
        found: bool
        context: str  — surrounding text for the match
        event_live: bool — whether the relevant event appears to be live
        results: list[str] — any result marks found near the athlete's name
    """
    result = {
        "found": False,
        "context": "",
        "event_live": False,
        "results": [],
    }

    if not page_text:
        return result

    # Case-insensitive search for athlete name
    pattern = re.compile(re.escape(athlete_name), re.IGNORECASE)
    matches = list(pattern.finditer(page_text))

    if not matches:
        return result

    result["found"] = True

    # Extract context around each match (200 chars before and after)
    contexts = []
    for match in matches:
        start = max(0, match.start() - 200)
        end = min(len(page_text), match.end() + 200)
        ctx = page_text[start:end].strip()
        contexts.append(ctx)

    result["context"] = "\n---\n".join(contexts[:3])  # Max 3 contexts

    # Check if the event is live
    if event_name:
        # Look for event name near "live" or "Up Now" indicators
        event_pattern = re.compile(re.escape(event_name), re.IGNORECASE)
        if event_pattern.search(page_text):
            # Check for live indicators near the event
            live_indicators = ["Live", "Up Now", "In Progress", "Flight"]
            for indicator in live_indicators:
                if indicator.lower() in page_text.lower():
                    result["event_live"] = True
                    break

    # Look for result marks near the athlete's name (e.g., "45-00.00", "45-03.25")
    for match in matches:
        start = max(0, match.start() - 100)
        end = min(len(page_text), match.end() + 100)
        nearby = page_text[start:end]
        # Match field event marks (e.g., 45-00.00, 32-09.25)
        marks = re.findall(r'\d{1,3}-\d{2}(?:\.\d{2})?', nearby)
        result["results"].extend(marks)

    return result


# ---------------------------------------------------------------------------
# Status tracking
# ---------------------------------------------------------------------------

class WatcherState:
    """Track what we've already notified about to avoid duplicate alerts."""

    def __init__(self):
        self.athlete_found_notified = False
        self.event_live_notified = False
        self.last_results: list[str] = []
        self.poll_count = 0
        self.start_time = datetime.now()

    def new_results(self, results: list[str]) -> list[str]:
        """Return only results we haven't seen before."""
        new = [r for r in results if r not in self.last_results]
        self.last_results = list(set(self.last_results + results))
        return new


# ---------------------------------------------------------------------------
# Main watcher loop
# ---------------------------------------------------------------------------

def run_watcher(
    url: str,
    athlete: str,
    event: str | None,
    interval: int,
    timeout_minutes: int,
    dry_run: bool,
    use_playwright: bool,
    token: str,
    chat_id: str,
):
    """Main polling loop."""
    state = WatcherState()
    deadline = datetime.now() + timedelta(minutes=timeout_minutes)
    event_display = event or "any event"

    logger.info(
        "Starting watcher: athlete=%s, event=%s, url=%s, interval=%ds, timeout=%dm",
        athlete, event_display, url, interval, timeout_minutes,
    )

    # Send initial notification
    start_msg = (
        f"*\U0001f3c3 Live Event Watcher Started*\n\n"
        f"Watching for: *{athlete}*\n"
        f"Event: *{event_display}*\n"
        f"Polling every {interval}s until {deadline.strftime('%I:%M %p')}\n"
        f"URL: {url}"
    )
    if dry_run:
        print(start_msg)
    else:
        send_telegram(start_msg, token, chat_id)

    # Handle graceful shutdown
    running = True
    def handle_signal(sig, frame):
        nonlocal running
        running = False
        logger.info("Shutdown signal received")
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    while running and datetime.now() < deadline:
        state.poll_count += 1
        logger.info("Poll #%d — fetching %s", state.poll_count, url)

        page_text = fetch_page(url, use_playwright=use_playwright)

        if not page_text:
            logger.warning("Empty page content — will retry")
            time.sleep(interval)
            continue

        result = search_for_athlete(page_text, athlete, event)

        # Notification logic
        if result["event_live"] and not state.event_live_notified:
            msg = (
                f"*\U0001f534 EVENT IS LIVE!*\n\n"
                f"*{event_display}* is now live!\n"
                f"Watching for *{athlete}*...\n"
                f"\U0001f517 {url}"
            )
            if dry_run:
                print(msg)
            else:
                send_telegram(msg, token, chat_id)
            state.event_live_notified = True

        if result["found"] and not state.athlete_found_notified:
            msg = (
                f"*\U0001f3af {athlete} SPOTTED!*\n\n"
                f"Found on the live results page.\n"
                f"Context:\n```\n{result['context'][:500]}\n```\n"
                f"\U0001f517 {url}"
            )
            if dry_run:
                print(msg)
            else:
                send_telegram(msg, token, chat_id)
            state.athlete_found_notified = True

        # Check for new results/marks
        if result["results"]:
            new_marks = state.new_results(result["results"])
            if new_marks:
                marks_str = ", ".join(new_marks)
                msg = (
                    f"*\U0001f4ca New Result for {athlete}!*\n\n"
                    f"Mark(s): *{marks_str}*\n"
                    f"\U0001f517 {url}"
                )
                if dry_run:
                    print(msg)
                else:
                    send_telegram(msg, token, chat_id)

        logger.info(
            "Poll #%d result: found=%s, event_live=%s, marks=%s",
            state.poll_count, result["found"], result["event_live"], result["results"],
        )

        time.sleep(interval)

    # Final summary
    elapsed = datetime.now() - state.start_time
    summary = (
        f"*\U0001f3c1 Watcher Complete*\n\n"
        f"Athlete: *{athlete}*\n"
        f"Polls: {state.poll_count}\n"
        f"Duration: {int(elapsed.total_seconds() / 60)} min\n"
        f"Found: {'Yes' if state.athlete_found_notified else 'No'}\n"
        f"Results: {', '.join(state.last_results) if state.last_results else 'None recorded'}"
    )
    if dry_run:
        print(summary)
    else:
        send_telegram(summary, token, chat_id)

    logger.info("Watcher finished after %d polls", state.poll_count)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Live event watcher with Telegram alerts")
    parser.add_argument("--url", required=True, help="URL to poll for live results")
    parser.add_argument("--athlete", required=True, help="Athlete name to search for")
    parser.add_argument("--event", default=None, help="Event name to watch (e.g. 'Shot Put')")
    parser.add_argument("--interval", type=int, default=60, help="Poll interval in seconds (default: 60)")
    parser.add_argument("--timeout", type=int, default=180, help="Max runtime in minutes (default: 180)")
    parser.add_argument("--dry-run", action="store_true", help="Print notifications without sending")
    parser.add_argument("--no-playwright", action="store_true", help="Skip Playwright, use requests only")
    args = parser.parse_args()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    if not chat_id and token:
        chat_id = discover_chat_id(token) or ""

    if not args.dry_run and (not token or not chat_id):
        print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID required (or auto-discoverable)", file=sys.stderr)
        sys.exit(1)

    run_watcher(
        url=args.url,
        athlete=args.athlete,
        event=args.event,
        interval=args.interval,
        timeout_minutes=args.timeout,
        dry_run=args.dry_run,
        use_playwright=not args.no_playwright,
        token=token,
        chat_id=chat_id,
    )


if __name__ == "__main__":
    main()
