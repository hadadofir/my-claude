#!/home/ofir-hadad/Desktop/Ofir/sandbox/telegram_claude/venv/bin/python3
import asyncio
import json
import logging
import os
import re
import subprocess
import time
import uuid
from datetime import time as dtime, timedelta

from dotenv import load_dotenv
from secret_store import child_env, get_secret
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env.fitness"))

import fitness_charts  # noqa: E402
from tg_format import send_with  # noqa: E402
import fitness_db as db  # noqa: E402  (needs TZ from the env file)
import garmin_sync  # noqa: E402

BOT_TOKEN = get_secret("telegram-fitness-token")
ALLOWED_USER_ID = int(os.environ["FITNESS_ALLOWED_USER_ID"])
WORKING_DIR = os.environ.get(
    "FITNESS_WORKING_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fitness_workspace"),
)
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "/home/ofir-hadad/.local/bin/claude")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL") or None
INCOMING_DIR = os.path.join(WORKING_DIR, "incoming")
CALIBRATION_PHOTO = os.path.join(WORKING_DIR, "calibration", "hand.jpg")
MCP_CONFIG = os.path.join(WORKING_DIR, "mcp.json")
STATE_FILE = os.path.join(WORKING_DIR, "state.json")

# Same safety boundary as the pregnancy bot: no Bash/Write/Edit. The DB is only
# reachable through the fitness MCP server; "dontAsk" denies anything not
# allowed in fitness_workspace/.claude/settings.json.
ALLOWED_TOOLS = "Read,WebSearch,WebFetch"
PERMISSION_MODE = "dontAsk"
CLAUDE_TIMEOUT = int(os.environ.get("FITNESS_CLAUDE_TIMEOUT", "900"))

SYNC_TIMES = [dtime(10, 0, tzinfo=db.TZ), dtime(21, 30, tzinfo=db.TZ)]
REPORT_TIME = dtime(22, 0, tzinfo=db.TZ)
DRAFT_TIMEOUT_HOURS = 2
PHOTO_RETENTION_HOURS = 36
REPORT_RETENTION_DAYS = 14
SYNC_DAYS = 7  # re-pull a week so late watch uploads and edits in Garmin Connect are picked up

WEIGHT_RE = re.compile(r"^\s*w(?:eight)?\s*[:=]?\s*(\d{2,3}(?:[.,]\d{1,2})?)\s*(?:kg)?\s*$", re.IGNORECASE)

COACH_CONTEXT = """\
You are a private nutrition and training coach running as a Telegram bot for one user. \
Their goal: lose fat while preserving (ideally building) muscle. They wear a Garmin watch; \
activities, sleep, HRV, resting HR and body battery are synced into the log automatically. \
You are not a doctor or registered dietitian.

TOOLS: all logging goes through the `fitness` MCP tools (log_meal, update_meal, finalize_meal, \
log_weight, log_note, log_strength_sets, get_day, get_range_stats, estimate_tdee, strength_history, \
weight_trend, templates, profile). Never claim something was logged unless the tool call succeeded. \
Use Read to view photo paths you are given. WebSearch/WebFetch are for nutrition values \
(USDA FoodData Central, Open Food Facts for barcoded/branded products) and evidence lookups.

FOOD PHOTOS:
- Identify every item, estimate grams, then kcal/protein/carbs/fat per item. Use the user's hand \
calibration (below) and known objects (fork ~19-20 cm, standard dinner plate ~26-27 cm, Israeli pita \
~16 cm, can ~6.6 cm wide) as scale. Account for cooked vs raw weight.
- Immediately log_meal with status='draft' and your best estimate, then reply with a compact breakdown \
(item: grams, kcal, P) and the total with a +/- range.
- Then ask ALL the clarifying questions that would materially change the numbers (roughly >50 kcal or \
>5 g protein), grouped in ONE message, numbered, highest calorie impact first: cooking oil/butter and \
how much, sauces/dressings/tahini, hidden or cut-off items, portion depth/thickness, fat % of dairy or \
meat, brand, whether they ate all of it. Don't ask things that barely matter.
- When they answer, update_meal (send the full item list) and ask follow-ups if something is still \
unclear. When everything is at medium/high confidence, or they say skip/good enough/ok, call \
finalize_meal and show the final numbers plus what's left today (kcal and protein).
- If a meal is simple and unambiguous, log it as final straight away without questions.
- If the photo has no good scale reference and size matters, ask them to put their hand next to the \
plate next time.
- Nutrition label / barcode photos: read exact values per 100 g, ask how much they ate, log with high \
confidence.
- Text meals ("2 eggs, 2 slices bread"): log directly using standard values; ask only if ambiguous.
- If they say they ate something earlier, pass ts. If they correct a meal, use update_meal.
- When a meal is likely to repeat, offer to save it as a template.

COACHING PRINCIPLES (evidence-based, use them in answers and reports):
1. Protein 1.8-2.2 g/kg bodyweight daily (use goal weight if body fat is high), spread over 3-5 \
feedings of >=0.4 g/kg, including one within a few hours after training and ideally one before sleep.
2. Rate of loss: target 0.5-1.0% bodyweight/week on the trend weight. Faster than 1%/week for 2+ weeks \
=> muscle-loss risk, suggest +150-250 kcal. Flat for 3 weeks with good logging => -150 kcal or +2-3k steps.
3. Use estimate_tdee (intake vs weight trend) as the truth for energy expenditure; Garmin calorie \
estimates are often too high, so don't tell the user to "eat back" watch calories.
4. Resistance training is the primary muscle-preservation signal: >=3 sessions/week, ~10+ hard sets per \
muscle group per week. Watch strength_history: falling estimated 1RM over 2+ weeks is the earliest \
sign of muscle loss — flag it and look at protein, deficit size and sleep.
5. Recovery: HRV below the baseline range, resting HR up >=5 bpm vs the user's normal, or sleep <7 h \
for 3+ days => suggest a maintenance-calorie day/diet break or lighter session. Poor sleep in a deficit \
shifts weight loss toward lean mass.
6. Cardio: favour steps and zone 2; avoid heavy HIIT within ~6 h before heavy leg work.
7. Fuel training: carbs + protein before and after hard sessions; place more carbs around training days.
8. Look for patterns in notes vs intake/sleep/training once there are a few weeks of data.

SAFETY: no diagnoses or medication advice; for medical symptoms (chest pain, fainting, injury, \
disordered-eating signs) refer to a doctor. Never set or endorse intake below the user's estimated BMR \
or ~1500 kcal for an adult man without a professional's supervision.

STYLE: English, short and scannable for a phone. Plain text with simple bullets/emoji is fine; no \
markdown tables or headers. Lead with numbers, end with one or two concrete actions (e.g. specific foods \
to close a protein gap). Don't repeat the whole day's log unless asked.

Formatting: replies are shown in Telegram, which has no tables or headings. Use short lines and bullet
lists, 'label: value' lines instead of tables, **bold** sparingly. Markdown is converted for you.

Spacing: the user reads on a phone and finds dense replies crowded. Open with a one-line answer, then a \
blank line. One idea per bullet, about one phone line each. Blank line between groups (e.g. numbers / \
actions). Max ~5 bullets per group; drop secondary detail and offer it on request instead."""

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("/tmp/telegram-fitness-bot.log"), logging.StreamHandler()],
)
# httpx logs full request URLs at INFO, which include the bot token
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

# One Claude call at a time: concurrent --resume on the same session corrupts it.
claude_lock = asyncio.Lock()
# media_group_id -> photos of one Telegram album, collected before processing together.
media_groups: dict[str, dict] = {}
# matplotlib's pyplot state isn't thread-safe; render one card at a time.
render_lock = asyncio.Lock()


# ---------------------------------------------------------------- state

def load_state() -> dict:
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_FILE)


def current_session() -> str | None:
    # A fresh Claude session each day; the DB is the long-term memory.
    st = load_state()
    if st.get("session_day") == db.today():
        return st.get("session_id")
    return None


def set_session(session_id: str | None) -> None:
    st = load_state()
    st["session_id"] = session_id
    st["session_day"] = db.today()
    save_state(st)


# ---------------------------------------------------------------- claude

def dynamic_context() -> str:
    conn = db.connect()
    prof = db.get_profile(conn)
    day = db.get_day(conn)
    drafts = db.get_open_drafts(conn)
    cal = prof.pop("calibration", None)
    lines = [
        f"\n\nCURRENT CONTEXT (local time {db.now().strftime('%A %Y-%m-%d %H:%M')}):",
        f"Profile: {json.dumps(prof) if prof else 'EMPTY — run onboarding before coaching.'}",
        f"Today so far: {json.dumps(day['totals'])}; targets {json.dumps(day['targets'])}; "
        f"remaining {json.dumps(day['remaining'])}; activities today: {len(day['activities'])}.",
    ]
    if cal:
        lines.append(
            f"Hand calibration (reference photo {CALIBRATION_PHOTO}): {json.dumps(cal)}. "
            "Use it as a scale whenever the user's hand appears in a food photo."
        )
    else:
        lines.append("No hand calibration yet — suggest /calibrate when portion size is hard to judge.")
    if drafts:
        lines.append("Open draft meals awaiting answers: " + json.dumps(
            [{"id": m["id"], "description": m["description"], "kcal": m["kcal"]} for m in drafts]))
    return "\n".join(lines)


def run_claude(prompt: str, session_id: str | None, timeout: int = CLAUDE_TIMEOUT) -> tuple[str, str | None]:
    cmd = [
        CLAUDE_BIN, "--print", "--output-format", "json",
        "--tools", ALLOWED_TOOLS,
        "--mcp-config", MCP_CONFIG, "--strict-mcp-config",
        "--permission-mode", PERMISSION_MODE,
        "--append-system-prompt", COACH_CONTEXT + dynamic_context(),
    ]
    if CLAUDE_MODEL:
        cmd += ["--model", CLAUDE_MODEL]
    if session_id:
        cmd += ["--resume", session_id]
    cmd.append(prompt)

    try:
        result = subprocess.run(cmd, cwd=WORKING_DIR, env=child_env(), capture_output=True, text=True, timeout=timeout)
        data = json.loads(result.stdout)
        text = data.get("result") or result.stderr.strip() or "(no output)"
        return text, data.get("session_id")
    except subprocess.TimeoutExpired:
        return f"That took too long (>{timeout // 60} min). The conversation is kept — say \"continue\" to pick up.", session_id
    except (json.JSONDecodeError, KeyError):
        output = result.stdout.strip() or result.stderr.strip() or "(no output)"
        return output, session_id
    except Exception as e:
        return f"Error: {e}", session_id


async def ask_claude(prompt: str, status_msg=None) -> str:
    async with claude_lock:
        session_id = current_session()
        task = asyncio.create_task(asyncio.to_thread(run_claude, prompt, session_id))
        start = time.monotonic()
        while not (await asyncio.wait({task}, timeout=60))[0]:
            if status_msg:
                try:
                    await status_msg.edit_text(f"Still working… {int((time.monotonic() - start) // 60)} min")
                except Exception:
                    pass
        output, new_session_id = task.result()
        if new_session_id and new_session_id != session_id:
            set_session(new_session_id)
            log.info("Session for %s: %s", db.today(), new_session_id)
        return output


async def send_text(bot, text: str) -> None:
    await send_with(lambda chunk, **kw: bot.send_message(ALLOWED_USER_ID, chunk, **kw), text)


async def render(kind: str) -> str:
    fn = fitness_charts.render_daily if kind == "daily" else fitness_charts.render_weekly
    async with render_lock:
        return await asyncio.to_thread(lambda: fn(db.connect()))


async def send_card(bot, kind: str, caption: str) -> bool:
    try:
        path = await render(kind)
    except Exception:
        log.exception("Rendering %s card failed", kind)
        return False
    with open(path, "rb") as f:
        await bot.send_photo(ALLOWED_USER_ID, photo=f, caption=caption)
    return True


async def ask_and_reply(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str,
                        status: str = "…") -> None:
    msg = await update.effective_message.reply_text(status)
    try:
        output = await ask_claude(prompt, msg)
    finally:
        await msg.delete()
    await send_text(context.bot, output)


# ---------------------------------------------------------------- helpers

def is_authorized(update: Update) -> bool:
    uid = update.effective_user.id if update.effective_user else None
    if uid != ALLOWED_USER_ID:
        log.warning("Unauthorized access attempt from user_id=%s", uid)
        return False
    return True


def _fmt(n) -> str:
    return "-" if n is None else f"{n:.0f}"


def format_today(day: dict) -> str:
    t, tg, rem = day["totals"], day["targets"], day["remaining"]
    lines = [f"📅 {day['day']}"]
    for m in day["meals"]:
        flag = " (draft)" if m["status"] == "draft" else ""
        lines.append(f"• {m['ts'][11:16]} {m['description']}: {_fmt(m['kcal'])} kcal, {_fmt(m['protein'])}g P{flag}")
    if not day["meals"]:
        lines.append("No meals logged yet.")
    lines.append("")
    lines.append(f"Total: {_fmt(t['kcal'])} kcal | P {_fmt(t['protein'])}g | C {_fmt(t['carbs'])}g | F {_fmt(t['fat'])}g")
    if tg.get("kcal") or tg.get("protein"):
        lines.append(f"Target: {_fmt(tg.get('kcal'))} kcal | P {_fmt(tg.get('protein'))}g")
        lines.append(f"Left: {_fmt(rem.get('kcal'))} kcal | P {_fmt(rem.get('protein'))}g")
    if day.get("protein_g_per_kg"):
        lines.append(f"Protein: {day['protein_g_per_kg']} g/kg")
    for a in day["activities"]:
        lines.append(f"🏃 {a['type']} {_fmt(a['duration_min'])} min, avg HR {_fmt(a['avg_hr'])}, {_fmt(a['active_kcal'])} kcal")
    w = day.get("wellness") or {}
    if w:
        lines.append(f"😴 sleep {w.get('sleep_hours') or '-'} h | HRV {_fmt(w.get('hrv_avg'))} ({w.get('hrv_status') or '-'}) "
                     f"| RHR {_fmt(w.get('resting_hr'))} | steps {_fmt(w.get('steps'))}")
    return "\n".join(lines)


async def download_photo(file_obj) -> str:
    os.makedirs(INCOMING_DIR, exist_ok=True)
    path = os.path.join(INCOMING_DIR, f"{int(time.time())}-{uuid.uuid4().hex[:8]}.jpg")
    tg_file = await file_obj.get_file()
    await tg_file.download_to_drive(path)
    return path


# ---------------------------------------------------------------- photos

async def process_photos(update: Update, context: ContextTypes.DEFAULT_TYPE, paths: list[str], caption: str) -> None:
    st = load_state()
    if st.get("awaiting_calibration"):
        cal_dir = os.path.dirname(CALIBRATION_PHOTO)
        os.makedirs(cal_dir, exist_ok=True)
        for f in os.listdir(cal_dir):
            os.remove(os.path.join(cal_dir, f))
        cal_paths = [CALIBRATION_PHOTO] + [os.path.join(cal_dir, f"hand-{i}.jpg") for i in range(2, len(paths) + 1)]
        for src, dst in zip(paths, cal_paths):
            os.replace(src, dst)
        st["awaiting_calibration"] = False
        save_state(st)
        prompt = (
            f"Hand calibration photo(s): {', '.join(cal_paths)} (the user's hand next to a measuring tape). "
            + (f'User says: "{caption}". ' if caption else "")
            + "Read the tape carefully and measure: hand length (wrist crease to middle fingertip), palm width "
            "across the knuckles, fist width if visible, and thumb/index finger widths. Call save_calibration. "
            "Reply with the measurements and how you'll use them (e.g. palm ≈ X cm ≈ one 120-150 g chicken "
            "breast portion). If the tape isn't readable, say what to re-shoot."
        )
        await ask_and_reply(update, context, prompt, "📏 Measuring…")
        return

    listing = ", ".join(paths)
    prompt = (
        f"The user sent {len(paths)} photo(s): {listing}"
        + (f' with the message: "{caption}". ' if caption else " with no text. ")
        + "If it's food or a nutrition label, follow the FOOD PHOTOS rules. If it's a Garmin/app screenshot, "
        "extract the training or health data and log what fits (log_strength_sets / log_note). "
        "Otherwise just answer."
    )
    await ask_and_reply(update, context, prompt, "🔍 Looking…")


async def _flush_media_group(context: ContextTypes.DEFAULT_TYPE) -> None:
    group = context.job.data
    media_groups.pop(group["id"], None)
    await process_photos(group["update"], context, group["paths"], group["caption"])


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    msg = update.message
    file_obj = msg.photo[-1] if msg.photo else msg.document
    path = await download_photo(file_obj)
    caption = (msg.caption or "").strip()

    if msg.media_group_id:
        # Albums arrive as separate updates; collect them for a moment and send together.
        g = media_groups.get(msg.media_group_id)
        if g is None:
            g = media_groups[msg.media_group_id] = {"id": msg.media_group_id, "update": update, "paths": [], "caption": ""}
            context.job_queue.run_once(_flush_media_group, 2.0, data=g)
        g["paths"].append(path)
        g["caption"] = g["caption"] or caption
        return

    await process_photos(update, context, [path], caption)


# ---------------------------------------------------------------- text & documents

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    text = update.message.text.strip()
    if not text:
        return

    m = WEIGHT_RE.match(text)
    if m:
        kg = float(m.group(1).replace(",", "."))
        res = db.log_weight(db.connect(), kg)
        tr = res["trend"]
        reply = f"⚖️ {kg} kg logged."
        if tr.get("latest"):
            reply += f" Trend {tr['latest']['trend_kg']} kg"
        if "change_pct_per_week" in tr:
            reply += f", {tr['change_kg_per_week']:+} kg/wk ({tr['change_pct_per_week']:+}%/wk)"
        await update.message.reply_text(reply + ".")
        return

    await ask_and_reply(update, context, text)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    doc = update.message.document
    name = (doc.file_name or "").lower()
    if (doc.mime_type or "").startswith("image/"):
        await handle_photo(update, context)
        return
    if not name.endswith(".fit"):
        await update.message.reply_text("I can read photos, screenshots and Garmin .FIT activity files.")
        return
    os.makedirs(INCOMING_DIR, exist_ok=True)
    path = os.path.join(INCOMING_DIR, f"{uuid.uuid4().hex}.fit")
    await (await doc.get_file()).download_to_drive(path)
    try:
        rec = await asyncio.to_thread(garmin_sync.parse_fit, path)
    except Exception as e:
        await update.message.reply_text(f"Couldn't parse that FIT file: {e}")
        return
    finally:
        os.remove(path)
    await ask_and_reply(
        update, context,
        f"The user uploaded a Garmin .FIT activity, already stored: {json.dumps(rec, default=str)}. "
        "Give a short take on the session (intensity, zones, what it means for recovery/fueling today).",
    )


# ---------------------------------------------------------------- commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        "💪 Fitness coach ready.\n\n"
        "• Send a food photo (or several) — I'll estimate macros and ask what I need to know\n"
        "• Or type what you ate: \"2 eggs, toast, cottage 5% 200g\"\n"
        "• Weight: \"w 82.4\"\n"
        "• Ask anything about nutrition or training\n\n"
        "/help for commands"
    )
    if not db.get_profile(db.connect()).get("onboarded"):
        await ask_and_reply(
            update, context,
            "Start onboarding. Ask me (in one message, numbered) for: name, sex, age, height, current weight, "
            "goal weight, how fast I want to lose, training routine (days, type, morning/evening), current diet "
            "approach and current daily kcal if known, food preferences/restrictions. After I answer, compute "
            "BMR (Mifflin-St Jeor), an initial TDEE estimate, a kcal target for ~0.5-0.75%/week loss, and protein/"
            "fat/carb targets per your principles; explain briefly, save with update_profile (onboarded=true), log "
            "my weight, and suggest /calibrate.",
        )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        "/today — today's chart card and log\n"
        "/week — weekly chart card and report\n"
        "/calibrate — send a photo of your hand next to a measuring tape\n"
        "/sync — pull latest Garmin data\n"
        "/undo — delete the last logged meal\n"
        "/templates — saved meals (say \"log usual breakfast\")\n"
        "/profile — targets and stats\n"
        "/reset — start a fresh conversation\n\n"
        "w 82.4 — log weight\n"
        "Photos, text, Garmin screenshots and .FIT files all work."
    )


async def today_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await send_card(context.bot, "daily", "📅 Today so far")
    await update.message.reply_text(format_today(db.get_day(db.connect())))


async def week_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await send_card(context.bot, "weekly", "📊 Last 7 days")
    await ask_and_reply(update, context, WEEKLY_PROMPT, "📊 Crunching the week…")


async def calibrate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    st = load_state()
    st["awaiting_calibration"] = True
    save_state(st)
    await update.message.reply_text(
        "📏 Send one photo of your open hand flat next to a measuring tape (or ruler):\n"
        "• camera straight above, hand and tape in the same plane\n"
        "• tape running from wrist to fingertips, numbers readable\n"
        "• fingers together; a second photo with a fist is a bonus"
    )


async def sync_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    msg = await update.message.reply_text("⌚ Syncing Garmin…")
    ok, info = await run_sync(context)
    await msg.edit_text(
        f"⌚ Synced: {info['activities']} activities, {info['strength_sets']} strength sets, {info['days']} days of wellness."
        if ok else f"Garmin sync failed: {info}\nYou can send a .FIT file or a screenshot instead."
    )


async def undo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    conn = db.connect()
    m = db.last_meal(conn)
    if not m:
        await update.message.reply_text("Nothing to undo.")
        return
    db.delete_meal(conn, m["id"])
    await update.message.reply_text(f"🗑 Deleted: {m['description']} ({m['kcal']:.0f} kcal, {m['protein']:.0f}g P)")


async def templates_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    ts = db.list_templates(db.connect())
    if not ts:
        await update.message.reply_text("No saved meals yet. After logging a meal, say \"save this as <name>\".")
        return
    await update.message.reply_text("\n".join(
        f"• {t['name']}: {t['description']} — {t['kcal']:.0f} kcal, {t['protein']:.0f}g P" for t in ts))


async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    prof = db.get_profile(db.connect())
    if not prof:
        await update.message.reply_text("No profile yet — send /start to set it up.")
        return
    cal = prof.pop("calibration", None)
    lines = [f"{k}: {v}" for k, v in prof.items()]
    lines.append(f"hand calibration: {'✅' if cal else '❌ (/calibrate)'}")
    await update.message.reply_text("\n".join(lines) + "\n\nTo change something just tell me, e.g. \"set protein to 180g\".")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    set_session(None)
    await update.message.reply_text("Conversation reset. Your log is untouched.")


# ---------------------------------------------------------------- scheduled jobs

DAILY_PROMPT = (
    "It's the end of the day. I've just been sent an image card with today's numbers (kcal and macros vs "
    "targets, protein per meal, HR zones per workout, 7-day calories/protein, sleep, HRV, resting HR), so "
    "don't repeat the numbers. Use get_day (today and yesterday) and weight_trend, then write the "
    "interpretation: what went well, what to watch (protein spread, deficit size, recovery signals vs my "
    "baseline, training stimulus), and any meals auto-finalized as low confidence. End with 1-2 concrete "
    "actions for tonight or tomorrow. Max ~8 short lines."
)

WEEKLY_PROMPT = (
    "Write my weekly report for the last 7 days. I've just been sent an image card with the week's charts "
    "(daily calories/protein, weight trend, training minutes by type, best estimated 1RM per lift vs last "
    "week, sleep/HRV/resting HR), so focus on interpretation rather than re-listing numbers. Use get_range_stats (last 7 days and the 7 before for "
    "comparison), estimate_tdee, weight_trend(28), and strength_history for my main lifts. Cover: rate of "
    "loss vs the 0.5-1%/week target; average intake and protein adherence; adaptive TDEE vs Garmin; "
    "resistance sessions and strength trend (flag any drop); recovery (sleep/HRV/RHR trend); any patterns in "
    "notes. Give a clear verdict (on track / adjust) and specific adjustments to targets if warranted — if "
    "you recommend changing targets, ask me before calling update_profile."
)


async def run_sync(context: ContextTypes.DEFAULT_TYPE, days: int = SYNC_DAYS) -> tuple[bool, dict | str]:
    st = load_state()
    try:
        info = await asyncio.to_thread(garmin_sync.sync, days)
        if st.get("garmin_failing"):
            st["garmin_failing"] = False
            save_state(st)
        return True, info
    except Exception as e:
        log.exception("Garmin sync failed")
        if not st.get("garmin_failing"):
            st["garmin_failing"] = True
            save_state(st)
            await context.bot.send_message(
                ALLOWED_USER_ID,
                f"⚠️ Garmin sync failed ({type(e).__name__}: {e}). If it's a login/MFA issue, run on the computer:\n"
                "venv/bin/python garmin_sync.py --login\n"
                "Meanwhile you can send .FIT files or screenshots. I'll only warn once until it works again.",
            )
        return False, str(e)


async def sync_job(context: ContextTypes.DEFAULT_TYPE):
    await run_sync(context)


async def report_job(context: ContextTypes.DEFAULT_TYPE):
    stale = db.finalize_stale_drafts(db.connect(), older_than_hours=0)
    if stale:
        log.info("Finalized %d open drafts before report", len(stale))
    await run_sync(context, days=2)
    await send_card(context.bot, "daily", "🌙 Daily summary")
    await send_text(context.bot, await ask_claude(DAILY_PROMPT))
    if db.now().weekday() == 5:  # Saturday (Python: Monday = 0); the Israeli week ends today
        await send_card(context.bot, "weekly", "📊 Weekly summary")
        await send_text(context.bot, await ask_claude(WEEKLY_PROMPT))


async def housekeeping_job(context: ContextTypes.DEFAULT_TYPE):
    stale = db.finalize_stale_drafts(db.connect(), older_than_hours=DRAFT_TIMEOUT_HOURS)
    for m in stale:
        await context.bot.send_message(
            ALLOWED_USER_ID,
            f"⏱ Saved \"{m['description']}\" with my best estimate ({m['kcal']:.0f} kcal, {m['protein']:.0f}g P). "
            "Tell me if anything needs correcting.",
        )
    cutoff = time.time() - PHOTO_RETENTION_HOURS * 3600
    for f in os.listdir(INCOMING_DIR):
        p = os.path.join(INCOMING_DIR, f)
        if os.path.isfile(p) and os.path.getmtime(p) < cutoff:
            os.remove(p)
    if os.path.isdir(fitness_charts.OUT_DIR):
        cutoff = time.time() - REPORT_RETENTION_DAYS * 86400
        for f in os.listdir(fitness_charts.OUT_DIR):
            p = os.path.join(fitness_charts.OUT_DIR, f)
            if os.path.getmtime(p) < cutoff:
                os.remove(p)


def main():
    os.makedirs(INCOMING_DIR, exist_ok=True)
    db.connect()
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    for name, fn in [("start", start), ("help", help_cmd), ("today", today_cmd), ("week", week_cmd),
                     ("calibrate", calibrate_cmd), ("sync", sync_cmd), ("undo", undo_cmd),
                     ("templates", templates_cmd), ("profile", profile_cmd), ("reset", reset)]:
        app.add_handler(CommandHandler(name, fn))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    jq = app.job_queue
    for t in SYNC_TIMES:
        jq.run_daily(sync_job, t, name=f"garmin-sync-{t.hour}{t.minute:02d}")
    jq.run_daily(report_job, REPORT_TIME, name="daily-report")
    jq.run_repeating(housekeeping_job, interval=timedelta(minutes=15), first=60, name="housekeeping")

    log.info("Fitness bot started. Working dir: %s", WORKING_DIR)
    app.run_polling()


if __name__ == "__main__":
    main()
