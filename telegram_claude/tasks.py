"""Read-only view of the master task list (sandbox/TASKS.md) for /tasks and the weekly review."""
import datetime
import os
import re
from dataclasses import dataclass, field

TASKS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TASKS.md")
HA_TODO_FILE = os.path.expanduser("~/ha-backups/HA-TODO.md")
STALE_DAYS = 14

TASK_RE = re.compile(r"^- \[ \] \[(\w+)\] (.+?)(?: — waiting: (\w+).*?)?(?: · added (\d{4}-\d{2}-\d{2}))?$")
SECTION_ICONS = {"Home server": "🖥", "Home Assistant": "🏠", "Bots": "🤖", "Projects": "🚀"}
WAITING_ICONS = {"Claude": "🧠", "external": "📦"}


@dataclass
class Task:
    id: str
    title: str
    section: str
    waiting: str
    added: datetime.date | None
    details: list[str] = field(default_factory=list)


def open_tasks() -> list[Task]:
    """Parse open tasks (with their indented detail lines), skipping the Done section."""
    tasks, section, current = [], "", None
    with open(TASKS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("## "):
                section, current = line[3:].strip(), None
            elif section == "Done":
                continue
            elif m := TASK_RE.match(line):
                added = datetime.date.fromisoformat(m.group(4)) if m.group(4) else None
                current = Task(m.group(1), m.group(2), section, m.group(3) or "", added)
                tasks.append(current)
            elif current and line.startswith("  - "):
                current.details.append(line[4:])
            else:
                current = None
    return tasks


def _ha_open_count() -> int:
    try:
        with open(HA_TODO_FILE, encoding="utf-8") as f:
            return sum(1 for line in f if line.lstrip().startswith("- [ ]"))
    except FileNotFoundError:
        return 0


def _line(t: Task, today: datetime.date, with_details: bool) -> str:
    marks = WAITING_ICONS.get(t.waiting, "")
    if t.added and (today - t.added).days >= STALE_DAYS:
        marks += "⚠️"
    out = f"**{t.id}** · {t.title}" + (f" {marks}" if marks else "")
    if with_details:
        out += "".join(f"\n      ↳ {d}" for d in t.details)
    return out


def format_tasks(query: str = "", weekly: bool = False) -> str:
    """Compact list by section. `query` filters by section letter ("H") or task ID ("H4");
    a filtered view also shows each task's detail lines."""
    today = datetime.date.today()
    tasks = open_tasks()
    q = query.strip().upper()
    if q:
        tasks = [t for t in tasks if t.id == q or (q.isalpha() and t.id.rstrip("0123456789") == q)]
        if not tasks:
            return f"No open task matches \"{query}\"."

    header = "📋 **Weekly task review**" if weekly else "📋 **Open tasks**"
    blocks = [f"{header} ({len(tasks)})"]
    section = None
    for t in tasks:
        if t.section != section:
            section = t.section
            blocks.append(f"\n{SECTION_ICONS.get(section, '•')} **{section}**")
        blocks.append(_line(t, today, with_details=bool(q)))

    footer = [f"🧠 on Claude · 📦 external · ⚠️ open {STALE_DAYS}+ days"]
    if not q:
        ha = _ha_open_count()
        if ha:
            footer.append(f"+ {ha} detailed items in HA-TODO.md")
        footer.append("Details: /tasks H  or  /tasks H4")
    if weekly:
        footer.append("Reply to update, e.g. \"H6 done\".")
    return "\n".join(blocks) + "\n\n" + "\n".join(footer)
