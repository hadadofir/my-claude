"""Read-only view of the master task list (sandbox/TASKS.md) for /tasks and the weekly review."""
import datetime
import os
import re

TASKS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TASKS.md")
HA_TODO_FILE = os.path.expanduser("~/ha-backups/HA-TODO.md")
STALE_DAYS = 14

OPEN_RE = re.compile(r"^- \[ \] (.+)$")
ADDED_RE = re.compile(r"added (\d{4}-\d{2}-\d{2})")


def open_tasks() -> list[tuple[str, str]]:
    """Return (section, line) for every open task, skipping the Done section."""
    tasks, section = [], ""
    with open(TASKS_FILE, encoding="utf-8") as f:
        for line in f:
            if line.startswith("## "):
                section = line[3:].strip()
            elif section != "Done" and (m := OPEN_RE.match(line.strip())):
                tasks.append((section, m.group(1)))
    return tasks


def _ha_open_count() -> int:
    try:
        with open(HA_TODO_FILE, encoding="utf-8") as f:
            return sum(1 for line in f if line.lstrip().startswith("- [ ]"))
    except FileNotFoundError:
        return 0


def _age_days(task: str, today: datetime.date) -> int | None:
    m = ADDED_RE.search(task)
    return (today - datetime.date.fromisoformat(m.group(1))).days if m else None


def format_tasks(weekly: bool = False) -> str:
    today = datetime.date.today()
    tasks = open_tasks()
    lines = ["📋 **Weekly task review**" if weekly else f"📋 **Open tasks ({len(tasks)})**"]
    section = None
    for sec, task in tasks:
        if sec != section:
            section = sec
            lines.append(f"\n**{sec}**")
        lines.append(f"- {task}")
    stale = [t for _, t in tasks if (_age_days(t, today) or 0) >= STALE_DAYS]
    if stale:
        lines.append(f"\n⚠️ **Open {STALE_DAYS}+ days ({len(stale)})**")
        lines += [f"- {t.split(' — ')[0]}" for t in stale]
    ha = _ha_open_count()
    if ha:
        lines.append(f"\nHA-TODO.md: {ha} more detailed open items")
    if weekly:
        lines.append("\nReply to update anything (e.g. \"close the AC filters task\").")
    return "\n".join(lines)
