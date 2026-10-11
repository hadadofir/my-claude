#!/home/ofir-hadad/Desktop/Ofir/sandbox/telegram_claude/venv/bin/python3
"""Pull activities and daily wellness from Garmin Connect into fitness.db, and parse .FIT uploads.

First run (handles MFA interactively and caches tokens):
    venv/bin/python garmin_sync.py --login
Afterwards the bot syncs on its own with the cached tokens:
    venv/bin/python garmin_sync.py --days 7
"""
import argparse
import json
import logging
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from secret_store import CREDSTORE, get_secret

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env.fitness"))

import fitness_db as db  # noqa: E402  (needs TZ/FITNESS_DB from the env file)

log = logging.getLogger(__name__)
TOKEN_DIR = os.environ.get(
    "GARMIN_TOKEN_DIR",
    os.path.join(CREDSTORE, "garmin-tokens"),
)


def _client(interactive: bool = False):
    from garminconnect import Garmin

    os.makedirs(TOKEN_DIR, mode=0o700, exist_ok=True)
    g = Garmin(
        email=os.environ.get("GARMIN_EMAIL"),
        password=get_secret("garmin-password"),
        prompt_mfa=(lambda: input("Garmin MFA code: ")) if interactive else None,
    )
    g.login(tokenstore=TOKEN_DIR)
    return g


def _exercise_name(ex: dict) -> str:
    raw = ex.get("name") or ex.get("category") or "unknown"
    return raw.replace("_", " ").lower()


def _activity_record(a: dict, source: str) -> dict:
    start = a.get("startTimeLocal") or ""
    zones = {f"z{i}": round(a[f"hrTimeInZone_{i}"] / 60, 1)
             for i in range(1, 6) if a.get(f"hrTimeInZone_{i}") is not None}
    return {
        "id": str(a["activityId"]),
        "start": start,
        "day": start[:10],
        "type": (a.get("activityType") or {}).get("typeKey"),
        "name": a.get("activityName"),
        "duration_min": round(a["duration"] / 60, 1) if a.get("duration") else None,
        "distance_km": round(a["distance"] / 1000, 2) if a.get("distance") else None,
        "avg_hr": a.get("averageHR"),
        "max_hr": a.get("maxHR"),
        "hr_zones_json": json.dumps(zones) if zones else None,
        "aerobic_te": a.get("aerobicTrainingEffect"),
        "anaerobic_te": a.get("anaerobicTrainingEffect"),
        "active_kcal": a.get("calories"),
        "training_load": a.get("activityTrainingLoad"),
        "source": source,
    }


def _sync_strength_sets(g, conn, rec: dict) -> int:
    data = g.get_activity_exercise_sets(rec["id"]) or {}
    sets = []
    for s in data.get("exerciseSets") or []:
        if s.get("setType") != "ACTIVE":
            continue
        exercises = s.get("exercises") or [{}]
        best = max(exercises, key=lambda e: e.get("probability") or 0)
        weight = s.get("weight")
        sets.append({
            "exercise": _exercise_name(best),
            "reps": s.get("repetitionCount"),
            # Garmin stores set weight in grams.
            "kg": round(weight / 1000, 1) if weight else None,
        })
    db.replace_activity_sets(conn, rec["id"], rec["day"], sets)
    return len(sets)


def _wellness(g, day: str) -> dict:
    out = {}
    try:
        st = g.get_stats(day) or {}
        out.update({
            "resting_hr": st.get("restingHeartRate"),
            "steps": st.get("totalSteps"),
            "stress_avg": st.get("averageStressLevel") if (st.get("averageStressLevel") or -1) >= 0 else None,
            "body_battery_max": st.get("bodyBatteryHighestValue"),
            "body_battery_min": st.get("bodyBatteryLowestValue"),
            "garmin_total_kcal": st.get("totalKilocalories"),
            "garmin_active_kcal": st.get("activeKilocalories"),
        })
    except Exception:
        log.exception("stats failed for %s", day)
    try:
        sl = (g.get_sleep_data(day) or {}).get("dailySleepDTO") or {}
        if sl.get("sleepTimeSeconds"):
            out["sleep_hours"] = round(sl["sleepTimeSeconds"] / 3600, 2)
        out["sleep_score"] = ((sl.get("sleepScores") or {}).get("overall") or {}).get("value")
    except Exception:
        log.exception("sleep failed for %s", day)
    try:
        hrv = ((g.get_hrv_data(day) or {}).get("hrvSummary")) or {}
        base = hrv.get("baseline") or {}
        out.update({
            "hrv_avg": hrv.get("lastNightAvg"),
            "hrv_status": hrv.get("status"),
            "hrv_baseline_low": base.get("balancedLow"),
            "hrv_baseline_high": base.get("balancedUpper"),
        })
    except Exception:
        log.exception("hrv failed for %s", day)
    return out


def sync(days: int = 3, interactive: bool = False) -> dict:
    """Upsert the last `days` days (including today). Safe to run repeatedly."""
    g = _client(interactive)
    conn = db.connect()
    end = db.now().date()
    start = end - timedelta(days=days - 1)
    acts = g.get_activities_by_date(start.isoformat(), end.isoformat()) or []
    n_sets = 0
    for a in acts:
        rec = _activity_record(a, "garmin")
        db.upsert_activity(conn, rec)
        if rec["type"] in ("strength_training", "indoor_cardio", "hiit") or "strength" in (rec["type"] or ""):
            try:
                n_sets += _sync_strength_sets(g, conn, rec)
            except Exception:
                log.exception("exercise sets failed for %s", rec["id"])
    d = start
    while d <= end:
        db.upsert_wellness(conn, d.isoformat(), _wellness(g, d.isoformat()))
        d += timedelta(days=1)
    return {"activities": len(acts), "strength_sets": n_sets, "days": days}


# ---------------------------------------------------------------- .FIT fallback

def parse_fit(path: str) -> dict:
    """Store a manually exported .FIT activity. Returns the stored activity record."""
    from fitparse import FitFile

    fit = FitFile(path)
    session = next((m.get_values() for m in fit.get_messages("session")), None)
    if not session:
        raise ValueError("No session in FIT file — is this an activity export?")
    start: datetime = session.get("start_time")
    if start and start.tzinfo is None:  # FIT timestamps are UTC
        start = start.replace(tzinfo=timezone.utc)
    start_local = start.astimezone(db.TZ) if start else db.now()
    zones_s = session.get("time_in_hr_zone")
    rec = {
        "id": f"fit-{int(start_local.timestamp())}",
        "start": start_local.strftime("%Y-%m-%d %H:%M:%S"),
        "day": start_local.date().isoformat(),
        "type": str(session.get("sport") or "unknown") + (
            f"/{session['sub_sport']}" if session.get("sub_sport") not in (None, "generic") else ""),
        "name": "FIT upload",
        "duration_min": round(session["total_timer_time"] / 60, 1) if session.get("total_timer_time") else None,
        "distance_km": round(session["total_distance"] / 1000, 2) if session.get("total_distance") else None,
        "avg_hr": session.get("avg_heart_rate"),
        "max_hr": session.get("max_heart_rate"),
        "hr_zones_json": json.dumps(
            {f"z{i}": round(s / 60, 1) for i, s in enumerate(zones_s) if s is not None}) if zones_s else None,
        "aerobic_te": session.get("total_training_effect"),
        "anaerobic_te": session.get("total_anaerobic_training_effect"),
        "active_kcal": session.get("total_calories"),
        "training_load": None,
        "source": "fit",
    }
    conn = db.connect()
    db.upsert_activity(conn, rec)
    sets = []
    for m in fit.get_messages("set"):
        v = m.get_values()
        if v.get("set_type") != "active":
            continue
        cat = v.get("category")
        cat = cat[0] if isinstance(cat, (list, tuple)) else cat
        sets.append({"exercise": str(cat or "unknown").replace("_", " ").lower(),
                     "reps": v.get("repetitions"), "kg": v.get("weight")})
    if sets:
        db.replace_activity_sets(conn, rec["id"], rec["day"], sets)
    rec["strength_sets"] = len(sets)
    return rec


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser()
    p.add_argument("--login", action="store_true", help="interactive login (MFA prompt), caches tokens")
    p.add_argument("--days", type=int, default=3)
    p.add_argument("--fit", help="parse a .FIT file instead of syncing")
    args = p.parse_args()
    if args.fit:
        print(parse_fit(args.fit))
    else:
        print(sync(args.days, interactive=args.login))
