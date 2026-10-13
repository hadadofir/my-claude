#!/home/ofir-hadad/Desktop/Ofir/sandbox/telegram_claude/venv/bin/python3
import asyncio
import json
import os
import re
import subprocess
import logging
import time
import datetime
import functools
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from secret_store import child_env, get_secret
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from session_store import SUMMARY_PROMPT, SessionStore, seeded_prompt
from tg_format import send_formatted, send_with
from tasks import TASKS_FILE, format_tasks

load_dotenv()

BOT_TOKEN = get_secret("telegram-claude-token")
ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])
WORKING_DIR = os.environ.get("WORKING_DIR", "/home/ofir-hadad/Desktop/Ofir")
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "/home/ofir-hadad/.local/bin/claude")
PERMISSION_MODE = os.environ.get("PERMISSION_MODE", "bypassPermissions")
CLAUDE_TIMEOUT = int(os.environ.get("CLAUDE_TIMEOUT", "1200"))
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions_claude.json")
INCOMING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "incoming")

TELEGRAM_CONTEXT = (
    "You are running headless as the backend for a personal Telegram bot, not in an "
    "interactive terminal. The user is messaging you remotely from their phone and "
    "cannot see or approve individual tool calls — permission checks are bypassed for "
    "this session, so nothing stops a destructive action before it runs. Because of "
    "that, be conservative: avoid irreversible or high-blast-radius actions (deleting "
    "files, force-pushing, dropping data, sending messages/emails on the user's behalf, "
    "changing system/service config, killing processes) unless the user's instruction is "
    "explicit and unambiguous about wanting that specific action. If a request is risky "
    "or could be interpreted multiple ways, explain what you'd do and ask for "
    "confirmation in your reply instead of just doing it. Keep replies reasonably "
    "concise since they're read on a phone screen.\n\n"
    "To send the user a file (an image, a document, a generated report, etc.) as a "
    "Telegram attachment, put a line by itself in your final reply in the exact form "
    "`SEND_FILE: <absolute path>` — one such line per file, multiple allowed. The file "
    "must already exist on disk at that path. Don't wrap the line in backticks or add "
    "other text to it; the bot detects these lines, uploads the files, and removes the "
    "lines from the visible reply.\n\n"
    "Formatting: replies are shown in Telegram, which has no tables or headings. Prefer "
    "short paragraphs and bullet lists; write 'label: value' lines instead of tables; "
    "use **bold** sparingly and `code` for paths/IDs. Markdown is converted for you.\n\n"
    f"Task tracking: the user's master open-task list is {TASKS_FILE}. Read it before "
    "task-related requests. When a task is added, progressed or finished (including "
    "\"add task …\" / \"close H3\" messages), update it in the file's format "
    "(each task has a stable ID like S2/H3/B1/P1; new tasks get the next unused number) and "
    "commit it in that git repo. The user can view it with /tasks."
)

SEND_FILE_RE = re.compile(r"^SEND_FILE:\s*(.+)$", re.MULTILINE)

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("/tmp/telegram-claude.log"), logging.StreamHandler()],
)
# httpx logs full request URLs at INFO, which include the bot token
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

# telegram_user_id -> claude session (persisted, rolled over when too big/idle)
store = SessionStore(STATE_FILE)
user_locks: dict[int, asyncio.Lock] = {}


def is_authorized(update: Update) -> bool:
    uid = update.effective_user.id
    if uid != ALLOWED_USER_ID:
        log.warning("Unauthorized access attempt from user_id=%s", uid)
        return False
    return True


def run_claude(prompt: str, session_id: str | None, timeout: int = CLAUDE_TIMEOUT) -> tuple[str, str | None]:
    cmd = [CLAUDE_BIN, "--print", "--output-format", "json",
           "--permission-mode", PERMISSION_MODE,
           "--append-system-prompt", TELEGRAM_CONTEXT]
    if session_id:
        cmd += ["--resume", session_id]
    cmd.append(prompt)

    try:
        result = subprocess.run(
            cmd, cwd=WORKING_DIR, env=child_env(), capture_output=True, text=True, timeout=timeout
        )
        data = json.loads(result.stdout)
        text = data.get("result") or result.stderr.strip() or "(no output)"
        new_session_id = data.get("session_id")
        return text, new_session_id
    except subprocess.TimeoutExpired:
        return f"Request timed out (>{timeout // 60} min). The conversation is kept — send \"continue\" to pick up.", session_id
    except (json.JSONDecodeError, KeyError):
        output = result.stdout.strip() or result.stderr.strip() or "(no output)"
        return output, session_id
    except Exception as e:
        return f"Error: {e}", session_id


async def send_attached_files(update: Update, text: str) -> str:
    """Extract SEND_FILE markers, upload each as a Telegram document, and
    return the reply text with those marker lines stripped out."""
    for path in (p.strip() for p in SEND_FILE_RE.findall(text)):
        try:
            with open(path, "rb") as f:
                await update.message.reply_document(document=f, filename=os.path.basename(path))
        except FileNotFoundError:
            await update.message.reply_text(f"(couldn't attach {path}: file not found)")
        except Exception as e:
            log.exception("Failed to send file %s", path)
            await update.message.reply_text(f"(couldn't attach {path}: {e})")
    return SEND_FILE_RE.sub("", text).strip()


async def run_with_progress(status_msg, prompt: str, session_id: str | None):
    """Run Claude in a worker thread, editing the status message every minute."""
    task = asyncio.create_task(asyncio.to_thread(run_claude, prompt, session_id))
    start = time.monotonic()
    while True:
        done, _ = await asyncio.wait({task}, timeout=60)
        if done:
            return task.result()
        try:
            await status_msg.edit_text(f"Still working… {int((time.monotonic() - start) // 60)} min")
        except Exception:
            pass


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    prompt = update.message.text.strip()
    if prompt:
        await ask_claude(update, prompt)


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save an incoming photo/document and hand its path to Claude with the caption."""
    if not is_authorized(update):
        return
    msg = update.message
    file_obj = msg.photo[-1] if msg.photo else msg.document
    os.makedirs(INCOMING_DIR, exist_ok=True)
    name = getattr(file_obj, "file_name", None) or "photo.jpg"
    path = os.path.join(INCOMING_DIR, f"{int(time.time())}-{file_obj.file_unique_id}-{os.path.basename(name)}")
    tg_file = await file_obj.get_file()
    await tg_file.download_to_drive(path)
    caption = (msg.caption or "").strip()
    kind = "a photo" if msg.photo else "a file"
    prompt = f"The user sent {kind}, saved at {path} (use Read to view it)."
    prompt += f' Their caption: "{caption}"' if caption else " No caption — look at it and respond."
    await ask_claude(update, prompt)


async def ask_claude(update: Update, prompt: str):
    uid = update.effective_user.id
    lock = user_locks.setdefault(uid, asyncio.Lock())
    if lock.locked():
        await update.message.reply_text("⏳ Queued — I'll handle this after the current request.")
    async with lock:
        thinking = await update.message.reply_text("Thinking...")
        session_id = store.get(uid)

        reason = store.rollover_reason(uid)
        if reason:
            await thinking.edit_text("🔄 Conversation got long — summarizing it into a fresh session…")
            summary, _ = await asyncio.to_thread(run_claude, SUMMARY_PROMPT, session_id, 300)
            log.info("Rollover (%s) for user %s from %s", reason, uid, session_id)
            prompt = seeded_prompt(summary, prompt)
            session_id = None
            await update.message.reply_text("🔄 Started a new conversation with a summary of the previous one.")

        output, new_session_id = await run_with_progress(thinking, prompt, session_id)

        if new_session_id:
            store.set(uid, new_session_id)
            if not session_id:
                log.info("New session started for user %s: %s", uid, new_session_id)

        await thinking.delete()
        output = await send_attached_files(update, output)
        if output:
            await send_formatted(update.message, output)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    st = store.status(update.effective_user.id)
    if not st["session_id"]:
        await update.message.reply_text("No active conversation.")
        return
    await update.message.reply_text(
        f"Session: {st['session_id'][:8]}…\nSize: {st['size_mb']} MB (rolls over at "
        f"{store.max_bytes / 1e6:g} MB)\nAge: {st['age_h']} h · idle {st['idle_min']} min"
    )


async def new_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start fresh but carry a summary of the current conversation."""
    if not is_authorized(update):
        return
    uid = update.effective_user.id
    session_id = store.get(uid)
    if not session_id:
        await update.message.reply_text("No active conversation — just send a message.")
        return
    async with user_locks.setdefault(uid, asyncio.Lock()):
        msg = await update.message.reply_text("Summarizing the current conversation…")
        summary, _ = await asyncio.to_thread(run_claude, SUMMARY_PROMPT, session_id, 300)
        output, new_session_id = await asyncio.to_thread(
            run_claude, seeded_prompt(summary, "Reply only: ready."), None, 300)
        if new_session_id:
            store.set(uid, new_session_id)
        await msg.edit_text("🔄 New conversation started with a summary of the previous one.")


async def tasks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await send_formatted(update.message, format_tasks(" ".join(context.args)))


async def weekly_review(context: ContextTypes.DEFAULT_TYPE):
    send = functools.partial(context.bot.send_message, ALLOWED_USER_ID)
    await send_with(send, format_tasks(weekly=True))


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    uid = update.effective_user.id
    store.clear(uid)
    await update.message.reply_text("Conversation reset. Starting fresh.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        "Claude Code bot ready.\n"
        f"Working directory: {WORKING_DIR}\n\n"
        "Send any message to run it as a Claude prompt.\n"
        "Use /reset to start a fresh conversation."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        "/start — show status\n"
        "/status — conversation size and age\n"
        "/new — fresh conversation, keeping a summary\n"
        "/reset — clear conversation history (no summary)\n"
        "/tasks — open task list (/tasks H for a section, /tasks H4 for one task)\n"
        "/help — show this message\n\n"
        "Any other message is sent directly to Claude Code."
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("new", new_conversation))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("tasks", tasks_cmd))
    # Weekly task review: Sunday 09:00 Israel time (days: 0=Sunday)
    app.job_queue.run_daily(weekly_review, datetime.time(9, 0, tzinfo=ZoneInfo("Asia/Jerusalem")), days=(0,))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_file))
    log.info("Bot started. Working dir: %s", WORKING_DIR)
    app.run_polling()


if __name__ == "__main__":
    main()
