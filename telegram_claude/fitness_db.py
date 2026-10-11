"""SQLite store for the fitness bot, shared by the MCP server, Garmin sync and the bot.

Every public function here takes plain values and returns JSON-serialisable
dicts/lists so fitness_mcp.py can expose them to Claude as-is.
"""
import json
import os
import sqlite3
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo(os.environ.get("TZ", "Asia/Jerusalem"))
DB_PATH = os.environ.get(
    "FITNESS_DB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fitness_workspace", "fitness.db"),
)
KCAL_PER_KG = 7700

SCHEMA = """
CREATE TABLE IF NOT EXISTS profile (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    day TEXT NOT NULL,
    meal_type TEXT,
    description TEXT NOT NULL,
    items_json TEXT NOT NULL,
    kcal REAL NOT NULL, protein REAL NOT NULL, carbs REAL NOT NULL, fat REAL NOT NULL,
    source TEXT,
    confidence TEXT,
    status TEXT NOT NULL DEFAULT 'final',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS meals_day ON meals(day);
CREATE TABLE IF NOT EXISTS meal_templates (
    name TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    items_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS weights (
    day TEXT PRIMARY KEY,
    kg REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS activities (
    id TEXT PRIMARY KEY,
    start TEXT NOT NULL,
    day TEXT NOT NULL,
    type TEXT,
    name TEXT,
    duration_min REAL,
    distance_km REAL,
    avg_hr REAL, max_hr REAL,
    hr_zones_json TEXT,
    aerobic_te REAL, anaerobic_te REAL,
    active_kcal REAL,
    training_load REAL,
    source TEXT
);
CREATE INDEX IF NOT EXISTS activities_day ON activities(day);
CREATE TABLE IF NOT EXISTS strength_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT NOT NULL,
    activity_id TEXT,
    exercise TEXT NOT NULL,
    reps INTEGER,
    kg REAL,
    source TEXT
);
CREATE INDEX IF NOT EXISTS strength_day ON strength_sets(day);
CREATE TABLE IF NOT EXISTS daily_wellness (
    day TEXT PRIMARY KEY,
    sleep_hours REAL, sleep_score REAL,
    hrv_avg REAL, hrv_status TEXT, hrv_baseline_low REAL, hrv_baseline_high REAL,
    resting_hr REAL,
    body_battery_min REAL, body_battery_max REAL,
    stress_avg REAL,
    steps INTEGER,
    garmin_total_kcal REAL, garmin_active_kcal REAL
);
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    day TEXT NOT NULL,
    text TEXT NOT NULL
);
"""

PROFILE_FIELDS = {
    "name", "sex", "age", "height_cm", "start_weight_kg", "goal_weight_kg",
    "target_rate_pct_per_week", "activity_baseline", "kcal_target", "protein_target_g",
    "carb_target_g", "fat_target_g", "training_notes", "diet_notes", "onboarded",
    "calibration",
}


def now() -> datetime:
    return datetime.now(TZ)


def today() -> str:
    return now().date().isoformat()


def connect(path: str | None = None) -> sqlite3.Connection:
    path = path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # The MCP server runs sync tools in worker threads; calls are sequential, so sharing is safe.
    # WAL + busy timeout because the bot and the MCP server are separate processes on the same file.
    conn = sqlite3.connect(path, check_same_thread=False, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    return conn


def _rows(cur) -> list[dict]:
    return [dict(r) for r in cur.fetchall()]


def _parse_day(d: str | None) -> str:
    return date.fromisoformat(d).isoformat() if d else today()


# ---------------------------------------------------------------- profile

def get_profile(conn) -> dict:
    out = {}
    for r in conn.execute("SELECT key, value FROM profile"):
        out[r["key"]] = json.loads(r["value"])
    return out


def update_profile(conn, fields: dict) -> dict:
    unknown = set(fields) - PROFILE_FIELDS
    if unknown:
        raise ValueError(f"Unknown profile fields: {sorted(unknown)}. Allowed: {sorted(PROFILE_FIELDS)}")
    with conn:
        for k, v in fields.items():
            if v is None:
                conn.execute("DELETE FROM profile WHERE key = ?", (k,))
            else:
                conn.execute(
                    "INSERT INTO profile(key, value) VALUES(?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                    (k, json.dumps(v)),
                )
    return get_profile(conn)


def save_calibration(conn, hand_length_cm: float, palm_width_cm: float,
                     fist_width_cm: float | None, finger_widths_cm: dict | None,
                     notes: str | None) -> dict:
    cal = {
        "hand_length_cm": hand_length_cm,
        "palm_width_cm": palm_width_cm,
        "fist_width_cm": fist_width_cm,
        "finger_widths_cm": finger_widths_cm or {},
        "notes": notes,
        "saved": now().isoformat(timespec="minutes"),
    }
    update_profile(conn, {"calibration": cal})
    return cal


# ---------------------------------------------------------------- meals

def _totals(items: list[dict]) -> dict:
    t = {"kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
    for it in items:
        for k in t:
            t[k] += float(it.get(k) or 0)
    return {k: round(v, 1) for k, v in t.items()}


def _validate_items(items: list[dict]) -> list[dict]:
    if not items:
        raise ValueError("items must be a non-empty list")
    clean = []
    for it in items:
        if "name" not in it:
            raise ValueError(f"each item needs a name: {it}")
        clean.append({
            "name": it["name"],
            "grams": it.get("grams"),
            "kcal": float(it.get("kcal") or 0),
            "protein": float(it.get("protein") or 0),
            "carbs": float(it.get("carbs") or 0),
            "fat": float(it.get("fat") or 0),
            **({"note": it["note"]} if it.get("note") else {}),
        })
    return clean


def _meal_row(r) -> dict:
    d = dict(r)
    d["items"] = json.loads(d.pop("items_json"))
    return d


def log_meal(conn, description: str, items: list[dict], meal_type: str | None = None,
             source: str | None = None, confidence: str | None = None,
             ts: str | None = None, status: str = "final") -> dict:
    if status not in ("draft", "final"):
        raise ValueError("status must be 'draft' or 'final'")
    items = _validate_items(items)
    t = _totals(items)
    when = datetime.fromisoformat(ts) if ts else now()
    if when.tzinfo is None:
        when = when.replace(tzinfo=TZ)
    with conn:
        cur = conn.execute(
            "INSERT INTO meals(ts, day, meal_type, description, items_json, kcal, protein, carbs, fat, "
            "source, confidence, status, created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (when.isoformat(timespec="minutes"), when.date().isoformat(), meal_type, description,
             json.dumps(items), t["kcal"], t["protein"], t["carbs"], t["fat"],
             source, confidence, status, now().isoformat(timespec="seconds")),
        )
    return get_meal(conn, cur.lastrowid)


def get_meal(conn, meal_id: int) -> dict:
    r = conn.execute("SELECT * FROM meals WHERE id = ?", (meal_id,)).fetchone()
    if not r:
        raise ValueError(f"No meal with id {meal_id}")
    return _meal_row(r)


def update_meal(conn, meal_id: int, description: str | None = None, items: list[dict] | None = None,
                meal_type: str | None = None, confidence: str | None = None,
                ts: str | None = None) -> dict:
    get_meal(conn, meal_id)
    sets, vals = [], []
    if description is not None:
        sets.append("description = ?"); vals.append(description)
    if meal_type is not None:
        sets.append("meal_type = ?"); vals.append(meal_type)
    if confidence is not None:
        sets.append("confidence = ?"); vals.append(confidence)
    if ts is not None:
        when = datetime.fromisoformat(ts)
        if when.tzinfo is None:
            when = when.replace(tzinfo=TZ)
        sets += ["ts = ?", "day = ?"]; vals += [when.isoformat(timespec="minutes"), when.date().isoformat()]
    if items is not None:
        items = _validate_items(items)
        t = _totals(items)
        sets += ["items_json = ?", "kcal = ?", "protein = ?", "carbs = ?", "fat = ?"]
        vals += [json.dumps(items), t["kcal"], t["protein"], t["carbs"], t["fat"]]
    if sets:
        with conn:
            conn.execute(f"UPDATE meals SET {', '.join(sets)} WHERE id = ?", (*vals, meal_id))
    return get_meal(conn, meal_id)


def finalize_meal(conn, meal_id: int) -> dict:
    get_meal(conn, meal_id)
    with conn:
        conn.execute("UPDATE meals SET status = 'final' WHERE id = ?", (meal_id,))
    return get_meal(conn, meal_id)


def delete_meal(conn, meal_id: int) -> dict:
    m = get_meal(conn, meal_id)
    with conn:
        conn.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
    return {"deleted": m}


def last_meal(conn) -> dict | None:
    r = conn.execute("SELECT * FROM meals ORDER BY id DESC LIMIT 1").fetchone()
    return _meal_row(r) if r else None


def get_open_drafts(conn) -> list[dict]:
    return [_meal_row(r) for r in conn.execute("SELECT * FROM meals WHERE status = 'draft' ORDER BY id")]


def finalize_stale_drafts(conn, older_than_hours: float = 2) -> list[dict]:
    cutoff = (now() - timedelta(hours=older_than_hours)).isoformat(timespec="seconds")
    stale = [_meal_row(r) for r in conn.execute(
        "SELECT * FROM meals WHERE status = 'draft' AND created_at < ?", (cutoff,))]
    with conn:
        for m in stale:
            conn.execute("UPDATE meals SET status = 'final', confidence = 'low' WHERE id = ?", (m["id"],))
    return stale


# ---------------------------------------------------------------- templates

def save_template(conn, name: str, meal_id: int) -> dict:
    m = get_meal(conn, meal_id)
    with conn:
        conn.execute(
            "INSERT INTO meal_templates(name, description, items_json) VALUES(?,?,?) "
            "ON CONFLICT(name) DO UPDATE SET description = excluded.description, items_json = excluded.items_json",
            (name.lower().strip(), m["description"], json.dumps(m["items"])),
        )
    return {"saved": name, "description": m["description"], **_totals(m["items"])}


def list_templates(conn) -> list[dict]:
    out = []
    for r in conn.execute("SELECT * FROM meal_templates ORDER BY name"):
        items = json.loads(r["items_json"])
        out.append({"name": r["name"], "description": r["description"], **_totals(items)})
    return out


def log_template(conn, name: str, multiplier: float = 1.0, meal_type: str | None = None,
                 ts: str | None = None) -> dict:
    r = conn.execute("SELECT * FROM meal_templates WHERE name = ?", (name.lower().strip(),)).fetchone()
    if not r:
        raise ValueError(f"No template '{name}'. Existing: {[t['name'] for t in list_templates(conn)]}")
    items = json.loads(r["items_json"])
    if multiplier != 1.0:
        items = [{**it, **{k: round(float(it.get(k) or 0) * multiplier, 1)
                           for k in ("kcal", "protein", "carbs", "fat")},
                  "grams": round(it["grams"] * multiplier) if it.get("grams") else it.get("grams")}
                 for it in items]
    desc = r["description"] + (f" (x{multiplier:g})" if multiplier != 1.0 else "")
    return log_meal(conn, desc, items, meal_type=meal_type, source="template", confidence="high", ts=ts)


# ---------------------------------------------------------------- weight, notes, strength

def log_weight(conn, kg: float, day: str | None = None) -> dict:
    d = _parse_day(day)
    with conn:
        conn.execute("INSERT INTO weights(day, kg) VALUES(?, ?) ON CONFLICT(day) DO UPDATE SET kg = excluded.kg",
                     (d, kg))
    return {"day": d, "kg": kg, "trend": weight_trend(conn, days=14)}


def log_note(conn, text: str) -> dict:
    n = now()
    with conn:
        cur = conn.execute("INSERT INTO notes(ts, day, text) VALUES(?,?,?)",
                           (n.isoformat(timespec="minutes"), n.date().isoformat(), text))
    return {"id": cur.lastrowid, "text": text}


def log_strength_sets(conn, exercise: str, sets: list[dict], day: str | None = None,
                      activity_id: str | None = None, source: str = "manual") -> dict:
    d = _parse_day(day)
    with conn:
        for s in sets:
            conn.execute(
                "INSERT INTO strength_sets(day, activity_id, exercise, reps, kg, source) VALUES(?,?,?,?,?,?)",
                (d, activity_id, exercise.lower().strip(), s.get("reps"), s.get("kg"), source),
            )
    return {"day": d, "exercise": exercise, "sets": sets}


# ---------------------------------------------------------------- garmin upserts

def upsert_activity(conn, a: dict) -> None:
    cols = ["id", "start", "day", "type", "name", "duration_min", "distance_km", "avg_hr", "max_hr",
            "hr_zones_json", "aerobic_te", "anaerobic_te", "active_kcal", "training_load", "source"]
    vals = [a.get(c) for c in cols]
    with conn:
        conn.execute(
            f"INSERT INTO activities({', '.join(cols)}) VALUES({', '.join('?' * len(cols))}) "
            f"ON CONFLICT(id) DO UPDATE SET {', '.join(f'{c} = excluded.{c}' for c in cols[1:])}",
            vals,
        )


def replace_activity_sets(conn, activity_id: str, day: str, sets: list[dict]) -> None:
    with conn:
        conn.execute("DELETE FROM strength_sets WHERE activity_id = ? AND source = 'garmin'", (activity_id,))
        for s in sets:
            conn.execute(
                "INSERT INTO strength_sets(day, activity_id, exercise, reps, kg, source) VALUES(?,?,?,?,?,'garmin')",
                (day, activity_id, s["exercise"], s.get("reps"), s.get("kg")),
            )


def upsert_wellness(conn, day: str, fields: dict) -> None:
    fields = {k: v for k, v in fields.items() if v is not None}
    if not fields:
        return
    cols = list(fields)
    with conn:
        conn.execute(
            f"INSERT INTO daily_wellness(day, {', '.join(cols)}) VALUES(?, {', '.join('?' * len(cols))}) "
            f"ON CONFLICT(day) DO UPDATE SET {', '.join(f'{c} = excluded.{c}' for c in cols)}",
            (day, *fields.values()),
        )


# ---------------------------------------------------------------- queries

def weight_trend(conn, days: int = 28, end: str | None = None) -> dict:
    """Exponentially smoothed weight (alpha 0.25, roughly a 7-day window) plus weekly rate."""
    end_d = date.fromisoformat(_parse_day(end))
    start_d = end_d - timedelta(days=days - 1)
    rows = _rows(conn.execute("SELECT day, kg FROM weights WHERE day BETWEEN ? AND ? ORDER BY day",
                              (start_d.isoformat(), end_d.isoformat())))
    if not rows:
        return {"points": 0}
    ema, smoothed = None, []
    for r in rows:
        ema = r["kg"] if ema is None else ema + 0.25 * (r["kg"] - ema)
        smoothed.append({"day": r["day"], "kg": r["kg"], "trend_kg": round(ema, 2)})
    out = {"points": len(rows), "latest": smoothed[-1], "first": smoothed[0]}
    # Rate from a least-squares slope over raw weigh-ins: the EMA lags and would understate it.
    xs = [(date.fromisoformat(r["day"]) - start_d).days for r in rows]
    span = xs[-1] - xs[0]
    if span >= 7 and len(rows) >= 4:
        mx, my = sum(xs) / len(xs), sum(r["kg"] for r in rows) / len(rows)
        slope = sum((x - mx) * (r["kg"] - my) for x, r in zip(xs, rows)) / sum((x - mx) ** 2 for x in xs)
        per_week = slope * 7
        out["change_kg_per_week"] = round(per_week, 2)
        out["change_pct_per_week"] = round(per_week / smoothed[-1]["trend_kg"] * 100, 2)
    return out


def _day_totals(conn, day: str) -> dict:
    r = conn.execute(
        "SELECT COUNT(*) n, COALESCE(SUM(kcal),0) kcal, COALESCE(SUM(protein),0) protein, "
        "COALESCE(SUM(carbs),0) carbs, COALESCE(SUM(fat),0) fat FROM meals WHERE day = ?", (day,)
    ).fetchone()
    return {k: round(r[k], 1) if k != "n" else r[k] for k in r.keys()}


def get_day(conn, day: str | None = None) -> dict:
    d = _parse_day(day)
    prof = get_profile(conn)
    meals = [_meal_row(r) for r in conn.execute("SELECT * FROM meals WHERE day = ? ORDER BY ts", (d,))]
    totals = _day_totals(conn, d)
    targets = {"kcal": prof.get("kcal_target"), "protein": prof.get("protein_target_g"),
               "carbs": prof.get("carb_target_g"), "fat": prof.get("fat_target_g")}
    remaining = {k: round(targets[k] - totals[k], 1) for k in targets if targets[k] is not None}
    weight = conn.execute("SELECT kg FROM weights WHERE day <= ? ORDER BY day DESC LIMIT 1", (d,)).fetchone()
    out = {
        "day": d,
        "meals": [{k: m[k] for k in ("id", "ts", "meal_type", "description", "kcal", "protein",
                                     "carbs", "fat", "confidence", "status")} for m in meals],
        "totals": totals,
        "targets": targets,
        "remaining": remaining,
        "activities": _rows(conn.execute(
            "SELECT id, start, type, name, duration_min, distance_km, avg_hr, max_hr, hr_zones_json, "
            "aerobic_te, anaerobic_te, active_kcal, training_load FROM activities WHERE day = ? ORDER BY start", (d,))),
        "strength_sets": _rows(conn.execute(
            "SELECT exercise, reps, kg FROM strength_sets WHERE day = ? ORDER BY id", (d,))),
        "wellness": dict(r) if (r := conn.execute("SELECT * FROM daily_wellness WHERE day = ?", (d,)).fetchone()) else None,
        "weight_today": (w["kg"] if (w := conn.execute("SELECT kg FROM weights WHERE day = ?", (d,)).fetchone()) else None),
        "notes": _rows(conn.execute("SELECT ts, text FROM notes WHERE day = ? ORDER BY id", (d,))),
    }
    if weight and totals["protein"]:
        out["protein_g_per_kg"] = round(totals["protein"] / weight["kg"], 2)
    return out


def get_range_stats(conn, start: str, end: str) -> dict:
    s, e = _parse_day(start), _parse_day(end)
    prof = get_profile(conn)
    days = _rows(conn.execute(
        "SELECT day, COUNT(*) meals, SUM(kcal) kcal, SUM(protein) protein, SUM(carbs) carbs, SUM(fat) fat "
        "FROM meals WHERE day BETWEEN ? AND ? GROUP BY day ORDER BY day", (s, e)))
    n = len(days)
    avg = {k: round(sum(d[k] for d in days) / n, 1) for k in ("kcal", "protein", "carbs", "fat")} if n else {}
    pt = prof.get("protein_target_g")
    kt = prof.get("kcal_target")
    adherence = {}
    if n and pt:
        adherence["protein_days_hit_pct"] = round(100 * sum(d["protein"] >= 0.95 * pt for d in days) / n)
    if n and kt:
        adherence["kcal_days_within_10pct_pct"] = round(100 * sum(abs(d["kcal"] - kt) <= 0.1 * kt for d in days) / n)
    span_days = (date.fromisoformat(e) - date.fromisoformat(s)).days + 1
    acts = _rows(conn.execute(
        "SELECT type, COUNT(*) n, ROUND(SUM(duration_min)) minutes, ROUND(SUM(active_kcal)) active_kcal, "
        "ROUND(SUM(training_load)) load FROM activities WHERE day BETWEEN ? AND ? GROUP BY type", (s, e)))
    strength = _rows(conn.execute(
        "SELECT exercise, COUNT(*) sets, MAX(kg) top_kg, "
        "MAX(CASE WHEN kg IS NOT NULL AND reps IS NOT NULL THEN kg * (1 + reps / 30.0) END) best_e1rm "
        "FROM strength_sets WHERE day BETWEEN ? AND ? GROUP BY exercise ORDER BY sets DESC", (s, e)))
    for x in strength:
        if x["best_e1rm"]:
            x["best_e1rm"] = round(x["best_e1rm"], 1)
    well = conn.execute(
        "SELECT ROUND(AVG(sleep_hours),2) sleep_h, ROUND(AVG(sleep_score)) sleep_score, ROUND(AVG(hrv_avg)) hrv, "
        "ROUND(AVG(resting_hr),1) rhr, ROUND(AVG(steps)) steps, ROUND(AVG(stress_avg)) stress, "
        "ROUND(AVG(garmin_total_kcal)) garmin_total_kcal FROM daily_wellness WHERE day BETWEEN ? AND ?", (s, e)
    ).fetchone()
    return {
        "start": s, "end": e, "days_in_range": span_days, "days_logged": n,
        "avg_per_logged_day": avg, "adherence": adherence, "daily": days,
        "weight": weight_trend(conn, days=span_days, end=e),
        "activities_by_type": acts,
        "strength_by_exercise": strength,
        "wellness_avg": dict(well) if well else None,
        "notes": _rows(conn.execute("SELECT day, text FROM notes WHERE day BETWEEN ? AND ? ORDER BY id", (s, e))),
    }


def strength_history(conn, exercise: str, weeks: int = 8) -> list[dict]:
    """Best estimated 1RM (Epley) per week for one exercise; falling values are an early muscle-loss signal."""
    since = (now().date() - timedelta(weeks=weeks)).isoformat()
    rows = _rows(conn.execute(
        "SELECT strftime('%Y-W%W', day) week, MAX(kg * (1 + reps / 30.0)) e1rm, MAX(kg) top_kg, COUNT(*) sets "
        "FROM strength_sets WHERE exercise = ? AND day >= ? AND kg IS NOT NULL AND reps IS NOT NULL "
        "GROUP BY week ORDER BY week", (exercise.lower().strip(), since)))
    for r in rows:
        r["e1rm"] = round(r["e1rm"], 1)
    return rows


def estimate_tdee(conn, days: int = 21) -> dict:
    """Adaptive TDEE: average intake minus the energy equivalent of the trend-weight change.

    Only days with logged food count toward average intake, so partially logged
    days bias it low; the result reports coverage so the caller can judge.
    """
    end_d = now().date() - timedelta(days=1)  # today is incomplete
    start_d = end_d - timedelta(days=days - 1)
    s, e = start_d.isoformat(), end_d.isoformat()
    intake = _rows(conn.execute(
        "SELECT day, SUM(kcal) kcal FROM meals WHERE day BETWEEN ? AND ? GROUP BY day", (s, e)))
    trend = weight_trend(conn, days=days, end=e)
    out = {"window": [s, e], "days_with_food_logged": len(intake), "weigh_ins": trend.get("points", 0)}
    if len(intake) < max(7, days // 2) or "change_kg_per_week" not in trend:
        out["status"] = "not_enough_data"
        out["need"] = "at least half the window with food logged and weigh-ins spanning 7+ days"
        return out
    avg_intake = sum(r["kcal"] for r in intake) / len(intake)
    daily_change_kcal = trend["change_kg_per_week"] / 7 * KCAL_PER_KG
    tdee = avg_intake - daily_change_kcal
    garmin = conn.execute("SELECT AVG(garmin_total_kcal) g FROM daily_wellness WHERE day BETWEEN ? AND ?",
                          (s, e)).fetchone()["g"]
    out.update({
        "status": "ok",
        "avg_intake_kcal": round(avg_intake),
        "trend_change_kg_per_week": trend["change_kg_per_week"],
        "estimated_tdee_kcal": round(tdee),
        "garmin_avg_total_kcal": round(garmin) if garmin else None,
        "logging_coverage_pct": round(100 * len(intake) / days),
    })
    return out
