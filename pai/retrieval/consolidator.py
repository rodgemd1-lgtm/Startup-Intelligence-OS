"""PAI Memory Consolidation Pipeline.

Three consolidation cycles:
1. Session End -> Work (create session record from conversation, auto)
2. Work Completion -> Learning (extract patterns, auto)
3. Learning Review -> Wisdom (promote proven patterns, weekly + approval)

Adapted from Miessler's PAI WorkCompletionLearning hook.
"""
import json
import os
from datetime import datetime
from pathlib import Path


class PAIConsolidator:
    """Manages memory promotion between tiers."""

    def __init__(self, base_dir: str = None):
        base = base_dir or os.path.join(
            os.path.dirname(__file__), "..", "MEMORY"
        )
        self.work_dir = os.path.join(base, "WORK")
        self.learning_dir = os.path.join(base, "LEARNING")
        self.wisdom_dir = os.path.join(base, "WISDOM")
        self.state_dir = os.path.join(base, "STATE")

    def create_work_session(self, session_id: str, description: str) -> str:
        """Create a new work session directory (Tier 2).

        Called at session start.
        """
        session_dir = os.path.join(self.work_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(os.path.join(session_dir, "artifacts"), exist_ok=True)

        # Create META.json
        meta = {
            "session_id": session_id,
            "description": description,
            "started_at": datetime.now().isoformat(),
            "status": "active",
            "tags": [],
        }
        with open(os.path.join(session_dir, "META.json"), "w") as f:
            json.dump(meta, f, indent=2)

        # Update state
        self._update_state(session_id, "active")
        return session_dir

    def close_work_session(self, session_id: str, rating: int = 0) -> dict:
        """Close a work session and extract learning.

        Called at session end. Triggers learning extraction.
        """
        session_dir = os.path.join(self.work_dir, session_id)
        if not os.path.exists(session_dir):
            return {"error": "Session not found"}

        # Update META
        meta_path = os.path.join(session_dir, "META.json")
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                meta = json.load(f)
            meta["ended_at"] = datetime.now().isoformat()
            meta["status"] = "completed"
            meta["rating"] = rating
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=2)

        # Record rating
        if rating > 0:
            self._record_rating(session_id, rating)

        # Extract learning
        learning = self._extract_learning(session_id)

        self._update_state(session_id, "completed")
        return {"session_id": session_id, "learning_extracted": learning}

    def _extract_learning(self, session_id: str) -> dict:
        """Extract learning patterns from a completed session.

        Creates a learning template file to be enriched by Claude.
        """
        learning_file = os.path.join(
            self.learning_dir,
            f"{datetime.now().strftime('%Y-%m-%d')}-{session_id[:8]}.md",
        )

        # Read artifacts from the session
        session_dir = os.path.join(self.work_dir, session_id)
        artifacts = []
        artifacts_dir = os.path.join(session_dir, "artifacts")
        if os.path.exists(artifacts_dir):
            for fname in os.listdir(artifacts_dir):
                fpath = os.path.join(artifacts_dir, fname)
                if os.path.isfile(fpath):
                    artifacts.append(fname)

        # Write learning template
        os.makedirs(self.learning_dir, exist_ok=True)
        with open(learning_file, "w") as f:
            f.write(f"# Learning Extract - {session_id}\n\n")
            f.write(f"**Session:** {session_id}\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write("## What Happened\n\n*(Auto-populated at session close)*\n\n")
            f.write("## What Worked\n\n\n")
            f.write("## What Didn't Work\n\n\n")
            f.write("## Patterns Detected\n\n\n")
            f.write("## Rules to Add/Update\n\n\n")
            if artifacts:
                f.write(f"\n## Artifacts ({len(artifacts)})\n\n")
                for a in artifacts:
                    f.write(f"- `{a}`\n")

        return {"learning_file": learning_file, "artifacts_count": len(artifacts)}

    def _record_rating(self, session_id: str, rating: int):
        """Append a rating to the ratings ledger."""
        ratings_path = os.path.join(self.state_dir, "ratings.jsonl")
        entry = {
            "session_id": session_id,
            "rating": rating,
            "timestamp": datetime.now().isoformat(),
        }
        with open(ratings_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _update_state(self, session_id: str, status: str):
        """Update the work state registry."""
        state_path = os.path.join(self.state_dir, "work.json")
        with open(state_path) as f:
            state = json.load(f)

        if status == "active":
            state["active_session"] = session_id
            state["total_sessions"] += 1
            state["sessions"].append({
                "id": session_id,
                "started_at": datetime.now().isoformat(),
                "status": "active",
            })
        elif status == "completed":
            state["active_session"] = None
            for s in state["sessions"]:
                if s["id"] == session_id:
                    s["status"] = "completed"
                    s["ended_at"] = datetime.now().isoformat()

        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

    def get_active_session(self) -> dict:
        """Get the currently active work session, if any."""
        state_path = os.path.join(self.state_dir, "work.json")
        if not os.path.exists(state_path):
            return {}
        with open(state_path) as f:
            state = json.load(f)
        return {"active": state.get("active_session"), "total": state.get("total_sessions", 0)}

    def list_sessions(self, limit: int = 10) -> list:
        """List recent work sessions."""
        state_path = os.path.join(self.state_dir, "work.json")
        if not os.path.exists(state_path):
            return []
        with open(state_path) as f:
            state = json.load(f)
        return state.get("sessions", [])[-limit:]
