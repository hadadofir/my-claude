#!/home/ofir-hadad/Desktop/Ofir/sandbox/telegram_claude/venv/bin/python3
import json
import os
import re
import subprocess
import logging
from dotenv import load_dotenv
from secret_store import child_env, get_secret
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

load_dotenv()

BOT_TOKEN = get_secret("telegram-claude-token")
ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])
WORKING_DIR = os.environ.get("WORKING_DIR", "/home/ofir-hadad/Desktop/Ofir")
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "/home/ofir-hadad/.local/bin/claude")
PERMISSION_MODE = os.environ.get("PERMISSION_MODE", "bypassPermissions")

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
    "lines from the visible reply."
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

# telegram_user_id -> claude session_id
sessions: dict[int, str] = {}


def is_authorized(update: Update) -> bool:
    uid = update.effective_user.id
    if uid != ALLOWED_USER_ID:
        log.warning("Unauthorized access attempt from user_id=%s", uid)
        return False
    return True


def run_claude(prompt: str, session_id: str | None) -> tuple[str, str | None]:
    cmd = [CLAUDE_BIN, "--print", "--output-format", "json",
           "--permission-mode", PERMISSION_MODE,
           "--append-system-prompt", TELEGRAM_CONTEXT]
    if session_id:
        cmd += ["--resume", session_id]
    cmd.append(prompt)

    try:
        result = subprocess.run(
            cmd, cwd=WORKING_DIR, env=child_env(), capture_output=True, text=True, timeout=300
        )
        data = json.loads(result.stdout)
        text = data.get("result") or result.stderr.strip() or "(no output)"
        new_session_id = data.get("session_id")
        return text, new_session_id
    except subprocess.TimeoutExpired:
        return "Request timed out (>5 min).", session_id
    except (json.JSONDecodeError, KeyError):
        output = result.stdout.strip() or result.stderr.strip() or "(no output)"
        return output, session_id
    except Exception as e:
        return f"Error: {e}", session_id


async def send_chunked(update: Update, text: str):
    for i in range(0, max(len(text), 1), 4096):
        await update.message.reply_text(text[i:i + 4096])


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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    prompt = update.message.text.strip()
    if not prompt:
        return

    uid = update.effective_user.id
    thinking = await update.message.reply_text("Thinking...")

    session_id = sessions.get(uid)
    output, new_session_id = run_claude(prompt, session_id)

    if new_session_id:
        sessions[uid] = new_session_id
        if not session_id:
            log.info("New session started for user %s: %s", uid, new_session_id)

    await thinking.delete()
    output = await send_attached_files(update, output)
    if output:
        await send_chunked(update, output)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    uid = update.effective_user.id
    sessions.pop(uid, None)
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
        "/reset — clear conversation history\n"
        "/help — show this message\n\n"
        "Any other message is sent directly to Claude Code."
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    log.info("Bot started. Working dir: %s", WORKING_DIR)
    app.run_polling()


if __name__ == "__main__":
    main()
