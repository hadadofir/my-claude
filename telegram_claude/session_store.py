"""Persistent per-user Claude session tracking with rollover.

Sessions survive bot restarts (saved to a JSON file). A session is rolled over
when its transcript grows too large or it has been idle too long; the caller
asks the old session for a handoff summary and seeds the new one with it.
"""
import glob
import json
import os
import time

SUMMARY_PROMPT = (
    "Write a handoff summary of this whole conversation for a fresh session that will "
    "continue it. Max ~25 short lines, plain text. Include: who the user is and how they "
    "like to work, what was done (with key file paths, entity IDs, commands), decisions "
    "made, and anything still open or pending confirmation. No preamble."
)


def transcript_size(session_id: str) -> int:
    paths = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session_id}.jsonl"))
    return max((os.path.getsize(p) for p in paths), default=0)


class SessionStore:
    def __init__(self, path: str, max_bytes: int = 2_000_000, idle_hours: float = 8):
        self.path, self.max_bytes, self.idle_s = path, max_bytes, idle_hours * 3600
        try:
            with open(path) as f:
                self.data: dict = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}

    def _save(self) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.data, f, indent=1)
        os.replace(tmp, self.path)

    def get(self, uid: int) -> str | None:
        return (self.data.get(str(uid)) or {}).get("session_id")

    def set(self, uid: int, session_id: str) -> None:
        entry = self.data.setdefault(str(uid), {})
        if entry.get("session_id") != session_id:
            entry["started"] = time.time()
        entry.update(session_id=session_id, last_used=time.time())
        self._save()

    def clear(self, uid: int) -> None:
        self.data.pop(str(uid), None)
        self._save()

    def rollover_reason(self, uid: int) -> str | None:
        entry = self.data.get(str(uid))
        if not entry or not entry.get("session_id"):
            return None
        if transcript_size(entry["session_id"]) > self.max_bytes:
            return "size"
        if time.time() - entry.get("last_used", time.time()) > self.idle_s:
            return "idle"
        return None

    def status(self, uid: int) -> dict:
        entry = self.data.get(str(uid)) or {}
        sid = entry.get("session_id")
        return {
            "session_id": sid,
            "size_mb": round(transcript_size(sid) / 1e6, 2) if sid else 0,
            "age_h": round((time.time() - entry["started"]) / 3600, 1) if entry.get("started") else 0,
            "idle_min": round((time.time() - entry["last_used"]) / 60) if entry.get("last_used") else 0,
        }


def seeded_prompt(summary: str, prompt: str) -> str:
    """First prompt of a rolled-over session: previous summary + the new message."""
    return (
        "[Context carried over from the previous conversation — treat as background]\n"
        f"{summary.strip()}\n\n[New message from the user]\n{prompt}"
    )
