#!/home/ofir-hadad/Desktop/Ofir/sandbox/telegram_claude/venv/bin/python3
import asyncio
import json
import os
import time
import uuid
import logging
from dotenv import load_dotenv
from secret_store import child_env, get_secret
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from session_store import SUMMARY_PROMPT, SessionStore, seeded_prompt
from tg_format import send_formatted

load_dotenv(os.path.join(os.path.dirname(__file__), ".env.pregnancy"))

BOT_TOKEN = get_secret("telegram-pregnancy-token")
ALLOWED_USER_ID = int(os.environ["PREGNANCY_ALLOWED_USER_ID"])
WORKING_DIR = os.environ.get(
    "PREGNANCY_WORKING_DIR",
    "/home/ofir-hadad/Desktop/Ofir/sandbox/telegram_claude/pregnancy_workspace",
)
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "/home/ofir-hadad/.local/bin/claude")
INCOMING_DIR = os.path.join(WORKING_DIR, "incoming")

# Hard safety boundary: Claude never gets Bash/Write/Edit here, only enough to
# read an incoming photo and look things up on the web. "dontAsk" denies
# anything not explicitly allowed in pregnancy_workspace/.claude/settings.json
# instead of hanging on a permission prompt nobody's there to answer.
ALLOWED_TOOLS = "Read,WebSearch,WebFetch"
PERMISSION_MODE = "dontAsk"
CLAUDE_TIMEOUT = int(os.environ.get("PREGNANCY_CLAUDE_TIMEOUT", "900"))
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions_pregnancy.json")

PREGNANCY_CONTEXT = (
    "את עוזרת מידע בנושא תזונה ובטיחות מזון בהריון, פועלת כבוט טלגרם פרטי עבור "
    "המשתמשת. את לא רופאה ולא תחליף לייעוץ רפואי.\n\n"
    "כללי ליבה:\n"
    "1. לכל טענה עובדתית (מה מותר/אסור לאכול, כמויות, סיכונים וכו') חובה לבצע "
    "חיפוש ברשת (WebSearch) ולאמת מול מקור אמין לפני שעונים. אין לענות "
    "מהזיכרון בלבד על שאלות בטיחות מזון או תזונה.\n"
    "2. סדר עדיפות למקורות: משרד הבריאות הישראלי (health.gov.il) וקופות "
    "החולים (clalit.co.il, maccabi4u.co.il, meuhedet.co.il, leumit.co.il) "
    "קודם. אם אין מידע ישראלי ספציפי, אפשר להשתמש בארגון הבריאות העולמי "
    "(who.int), ACOG (acog.org), ה-NHS (nhs.uk), מרפאת מאיו (mayoclinic.org), "
    "NICHD (nichd.nih.gov) או March of Dimes (marchofdimes.org). אלה הדומיינים "
    "היחידים שמותר לפתוח בפועל (WebFetch) - אם חיפוש מחזיר תוצאה ממקור אחר, "
    "אין להסתמך עליה.\n"
    "3. בסוף כל תשובה עם מידע עובדתי יש לציין את שם המקור וקישור ישיר אליו, "
    "לדוגמה: 'מקור: משרד הבריאות - https://...'.\n"
    "4. אם לא נמצא מקור אמין ורלוונטי - יש לומר זאת במפורש ('לא מצאתי מקור "
    "רשמי ומהימן לשאלה הזו') במקום לנחש או להמציא מידע/קישור.\n"
    "5. ניתן לקבל ולנתח תמונות (תוויות מזון, תפריטים, אריזות תרופות, ארוחות) "
    "- יש להשתמש בכלי Read כדי לצפות בתמונה שנשלחה ולהתייחס לתוכן שלה בתשובה.\n"
    "6. אין לאבחן מצבים רפואיים ואין להחליף רופא/ה. בכל נושא שנוגע לתסמינים, "
    "תרופות, מינונים אישיים, או כל דבר שגובל ברפואי/דחוף - יש להפנות במפורש "
    "להתייעצות עם הרופא/ה המטפל/ת או המיילדת.\n"
    "7. תשובות תמציתיות וברורות, מותאמות לקריאה בטלפון.\n"
    "8. אין יכולת ואין תפקיד לבצע פעולות מחשוב/קבצים/מערכת - זהו כלי מידע "
    "בלבד. אם מתבקש משהו כזה, יש להסביר שזה לא בתפקיד הבוט.\n\n"
    "עיצוב: התשובות מוצגות בטלגרם, שאין בו טבלאות או כותרות. יש להעדיף פסקאות קצרות "
    "ורשימות עם תבליטים, שורות 'נושא: ערך' במקום טבלאות, ו-**הדגשה** במשורה.\n\n"
    "מרווח: המשתמשת קוראת בטלפון ותשובות צפופות מעייפות. יש לפתוח בשורה אחת עם התשובה "
    "הישירה, ואז שורה ריקה. כל תבליט - רעיון אחד, עד כשורה אחת בטלפון. שורה ריקה בין "
    "קבוצות. עד 3-5 תבליטים; פרטים נוספים רק אם מבקשים ('רוצה פירוט?'). המקור בשורה "
    "נפרדת בסוף, אחרי שורה ריקה."
)

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("/tmp/telegram-pregnancy-bot.log"), logging.StreamHandler()],
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
    import subprocess

    cmd = [
        CLAUDE_BIN, "--print", "--output-format", "json",
        "--tools", ALLOWED_TOOLS,
        "--permission-mode", PERMISSION_MODE,
        "--append-system-prompt", PREGNANCY_CONTEXT,
    ]
    if session_id:
        cmd += ["--resume", session_id]
    cmd.append(prompt)

    try:
        result = subprocess.run(
            cmd, cwd=WORKING_DIR, env=child_env(), capture_output=True, text=True, timeout=timeout
        )
        data = json.loads(result.stdout)
        text = data.get("result") or result.stderr.strip() or "(אין תשובה)"
        new_session_id = data.get("session_id")
        return text, new_session_id
    except subprocess.TimeoutExpired:
        return f"הבקשה ארכה יותר מדי זמן (מעל {timeout // 60} דקות). השיחה נשמרה – אפשר לכתוב \"המשך\".", session_id
    except (json.JSONDecodeError, KeyError):
        output = result.stdout.strip() or result.stderr.strip() or "(אין תשובה)"
        return output, session_id
    except Exception as e:
        return f"שגיאה: {e}", session_id


async def ask_claude(update: Update, status_msg, prompt: str) -> str:
    """Run Claude for this user in a worker thread: one request at a time per user,
    roll over oversized/idle sessions with a summary, and show progress."""
    uid = update.effective_user.id
    async with user_locks.setdefault(uid, asyncio.Lock()):
        session_id = store.get(uid)
        if store.rollover_reason(uid):
            await status_msg.edit_text("🔄 השיחה התארכה – מסכמת ופותחת שיחה חדשה…")
            summary, _ = await asyncio.to_thread(run_claude, SUMMARY_PROMPT, session_id, 300)
            log.info("Rollover for user %s from %s", uid, session_id)
            prompt, session_id = seeded_prompt(summary, prompt), None
            await update.message.reply_text("🔄 התחלתי שיחה חדשה עם סיכום של הקודמת.")

        task = asyncio.create_task(asyncio.to_thread(run_claude, prompt, session_id))
        start = time.monotonic()
        while not (await asyncio.wait({task}, timeout=60))[0]:
            try:
                await status_msg.edit_text(f"עדיין בודקת… {int((time.monotonic() - start) // 60)} דק׳")
            except Exception:
                pass
        output, new_session_id = task.result()
        if new_session_id:
            store.set(uid, new_session_id)
            if not session_id:
                log.info("New session started for user %s: %s", uid, new_session_id)
        return output


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    prompt = update.message.text.strip()
    if not prompt:
        return

    thinking = await update.message.reply_text("בודקת...")
    output = await ask_claude(update, thinking, prompt)
    await thinking.delete()
    await send_formatted(update.message, output)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    thinking = await update.message.reply_text("בודקת את התמונה...")

    os.makedirs(INCOMING_DIR, exist_ok=True)
    photo_path = os.path.join(INCOMING_DIR, f"{uuid.uuid4().hex}.jpg")
    tg_file = await update.message.photo[-1].get_file()
    await tg_file.download_to_drive(photo_path)

    caption = (update.message.caption or "").strip()
    if caption:
        prompt = f"המשתמשת שלחה תמונה בנתיב {photo_path} עם ההודעה: {caption}"
    else:
        prompt = (
            f"המשתמשת שלחה תמונה בנתיב {photo_path} ללא הודעת טקסט. "
            "נתחי את התמונה (לדוגמה תווית מזון, מרכיבים, תפריט או ארוחה) "
            "וענו בהתאם לכללי הליבה שלך."
        )

    try:
        output = await ask_claude(update, thinking, prompt)
    finally:
        try:
            os.remove(photo_path)
        except FileNotFoundError:
            pass

    await thinking.delete()
    await send_formatted(update.message, output)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    uid = update.effective_user.id
    store.clear(uid)
    await update.message.reply_text("השיחה אופסה. מתחילים מחדש.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        "בוט מידע תזונה והריון מוכן.\n\n"
        "אפשר לשלוח שאלה בטקסט או תמונה (תווית מזון, תפריט וכו').\n"
        "כל תשובה עם מידע עובדתי תגיע עם מקור מאומת.\n"
        "זה לא תחליף לייעוץ רפואי - לכל דבר הקשור לתסמינים או תרופות יש "
        "להתייעץ עם הרופא/ה המטפל/ת.\n\n"
        "/reset - איפוס השיחה"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        "/start — סטטוס\n"
        "/reset — איפוס היסטוריית השיחה\n"
        "/help — ההודעה הזו\n\n"
        "כל הודעה או תמונה אחרת נשלחת ישירות לבוט."
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    log.info("Pregnancy bot started. Working dir: %s", WORKING_DIR)
    app.run_polling()


if __name__ == "__main__":
    main()
