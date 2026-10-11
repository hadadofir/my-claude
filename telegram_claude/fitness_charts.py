"""Render the daily and weekly summary cards as PNGs for Telegram.

Static images (no hover), sized for a phone screen. Colors follow the validated
reference palette: blue/orange/aqua categorical, a blue ordinal ramp for HR zones.
"""
import json
import os
from datetime import date, timedelta

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402

import fitness_db as db  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fitness_workspace", "reports")

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e6e5e0"
TRACK = "#f0efec"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ZONES = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]  # ordinal blue ramp, Z1 -> Z5
TRAINING_COLORS = {"Strength": BLUE, "Cardio": ORANGE, "Other": AQUA}

_family = next((f for f in ("Noto Sans", "DejaVu Sans")
                if any(f == x.name for x in font_manager.fontManager.ttflist)), "DejaVu Sans")
plt.rcParams.update({
    "font.family": _family,
    "font.size": 10,
    "text.color": TEXT,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT_2,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.titlepad": 8,
    "axes.titlecolor": TEXT,
    "xtick.color": TEXT_2,
    "ytick.color": TEXT_2,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


# ---------------------------------------------------------------- data

def _days(end: date, n: int) -> list[date]:
    return [end - timedelta(days=i) for i in range(n - 1, -1, -1)]


def _intake_by_day(conn, days: list[date]) -> dict[str, dict]:
    rows = conn.execute(
        "SELECT day, SUM(kcal) kcal, SUM(protein) protein FROM meals WHERE day BETWEEN ? AND ? GROUP BY day",
        (days[0].isoformat(), days[-1].isoformat()))
    return {r["day"]: dict(r) for r in rows}


def _wellness_by_day(conn, days: list[date]) -> dict[str, dict]:
    rows = conn.execute("SELECT * FROM daily_wellness WHERE day BETWEEN ? AND ?",
                        (days[0].isoformat(), days[-1].isoformat()))
    return {r["day"]: dict(r) for r in rows}


def _training_category(t: str | None) -> str:
    t = t or ""
    if "strength" in t:
        return "Strength"
    if any(k in t for k in ("run", "cycl", "bik", "swim", "walk", "cardio", "elliptical", "rowing", "hiit")):
        return "Cardio"
    return "Other"


# ---------------------------------------------------------------- drawing helpers

def _clean(ax, grid_axis: str = "y"):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _empty(ax, title: str, msg: str):
    ax.set_title(title)
    ax.text(0.5, 0.45, msg, ha="center", va="center", color=MUTED, fontsize=9.5, transform=ax.transAxes)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def _tiles(fig, gs_cell, tiles: list[tuple[str, str, str]]):
    """Hero stat tiles: (label, big value, sub line)."""
    sub = gs_cell.subgridspec(1, len(tiles), wspace=0.08)
    for i, (label, value, note) in enumerate(tiles):
        ax = fig.add_subplot(sub[0, i])
        ax.set_axis_off()
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color=TRACK, zorder=0))
        ax.text(0.08, 0.78, label, fontsize=9, color=TEXT_2, transform=ax.transAxes)
        ax.text(0.08, 0.40, value, fontsize=17, fontweight="bold", color=TEXT, transform=ax.transAxes)
        ax.text(0.08, 0.13, note, fontsize=8.5, color=TEXT_2, transform=ax.transAxes)


def _header(fig, title: str, subtitle: str):
    fig.text(0.04, 0.975, title, fontsize=18, fontweight="bold", va="top")
    fig.text(0.04, 0.948, subtitle, fontsize=10.5, color=TEXT_2, va="top")


def _daily_bars(ax, days: list[date], values: list[float | None], target: float | None, title: str,
                unit: str, color: str = BLUE, highlight_last: bool = False):
    xs = range(len(days))
    vals = [v or 0 for v in values]
    colors = [color] * len(days)
    if highlight_last:
        colors = [TRACK if v is None else "#86b6ef" for v in values[:-1]] + [color]
    ax.bar(xs, vals, width=0.62, color=colors, edgecolor=SURFACE, linewidth=2, zorder=2)
    if target:
        ax.axhline(target, color=TEXT_2, linestyle=(0, (4, 3)), linewidth=1.2, zorder=3)
        ax.text(-0.45, target, f"target {target:,.0f}", ha="left", va="bottom", fontsize=8, color=TEXT_2)
    for x, v in zip(xs, values):
        if v is None:
            ax.text(x, 0, "–", ha="center", va="bottom", color=MUTED, fontsize=9)
        elif highlight_last and x == len(days) - 1 or not highlight_last:
            ax.text(x, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=7.5, color=TEXT_2)
    ax.set_xticks(list(xs), [d.strftime("%a")[:2] for d in days])
    top = max([target or 0] + vals)
    ax.set_ylim(0, top * 1.18 if top else 1)
    ax.set_title(f"{title} ({unit})")
    _clean(ax)
    ax.set_yticks([])


def _sleep(ax, days, well):
    vals = [(well.get(d.isoformat()) or {}).get("sleep_hours") for d in days]
    if not any(vals):
        return _empty(ax, "Sleep (h)", "no sleep data")
    xs = range(len(days))
    ax.bar(xs, [v or 0 for v in vals], width=0.62, color=BLUE, edgecolor=SURFACE, linewidth=2, zorder=2)
    ax.axhline(7, color=TEXT_2, linestyle=(0, (4, 3)), linewidth=1.1, zorder=3)
    for x, v in zip(xs, vals):
        if v:
            ax.text(x, v, f"{v:.1f}", ha="center", va="bottom", fontsize=7.5, color=TEXT_2)
    ax.set_ylim(0, max(9, max(v or 0 for v in vals) * 1.15))
    ax.set_xticks(list(xs), [d.strftime("%a")[:2] for d in days])
    ax.set_title("Sleep (h) · line = 7 h")
    _clean(ax)
    ax.set_yticks([])


def _line_metric(ax, days, well, key, title, band=None):
    pts = [(i, (well.get(d.isoformat()) or {}).get(key)) for i, d in enumerate(days)]
    pts = [(i, v) for i, v in pts if v is not None]
    if not pts:
        return _empty(ax, title, "no data")
    if band:
        lo = [(well.get(d.isoformat()) or {}).get(band[0]) for d in days]
        hi = [(well.get(d.isoformat()) or {}).get(band[1]) for d in days]
        if any(lo) and any(hi):
            xs = [i for i in range(len(days)) if lo[i] and hi[i]]
            ax.fill_between(xs, [lo[i] for i in xs], [hi[i] for i in xs], color=TRACK, zorder=1, linewidth=0)
            ax.text(xs[0], hi[xs[0]], " baseline", fontsize=7.5, color=MUTED, va="top")
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=BLUE, linewidth=2, zorder=3)
    ax.scatter(xs, ys, s=30, color=BLUE, edgecolor=SURFACE, linewidth=1.5, zorder=4)
    ax.annotate(f"{ys[-1]:.0f}", (xs[-1], ys[-1]), textcoords="offset points", xytext=(0, 7),
                ha="center", fontsize=8.5, fontweight="bold")
    ax.set_xticks(range(len(days)), [d.strftime("%a")[:2] for d in days])
    ax.set_xlim(-0.5, len(days) - 0.5)
    lo_v, hi_v = min(ys), max(ys)
    if band and any(lo) and any(hi):
        lo_v, hi_v = min(lo_v, min(v for v in lo if v)), max(hi_v, max(v for v in hi if v))
    pad = max(3, (hi_v - lo_v) * 0.25)
    ax.set_ylim(lo_v - pad, hi_v + pad)
    ax.set_title(title)
    _clean(ax)


def _recovery_row(fig, cell, days, well):
    sub = cell.subgridspec(1, 3, wspace=0.28)
    _sleep(fig.add_subplot(sub[0, 0]), days, well)
    _line_metric(fig.add_subplot(sub[0, 1]), days, well, "hrv_avg", "HRV (ms)", band=("hrv_baseline_low", "hrv_baseline_high"))
    _line_metric(fig.add_subplot(sub[0, 2]), days, well, "resting_hr", "Resting HR (bpm)")


def _save(fig, name: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


# ---------------------------------------------------------------- daily card

def render_daily(conn, day: str | None = None) -> str:
    d = date.fromisoformat(db._parse_day(day))
    info = db.get_day(conn, d.isoformat())
    prof = db.get_profile(conn)
    tot, tgt = info["totals"], info["targets"]
    week = _days(d, 7)
    intake = _intake_by_day(conn, week)
    well = _wellness_by_day(conn, week)
    trend = db.weight_trend(conn, days=28, end=d.isoformat())

    fig = plt.figure(figsize=(7.2, 10.8))
    gs = GridSpec(5, 2, figure=fig, height_ratios=[0.8, 1.05, 1.25, 1.1, 1.1],
                  left=0.06, right=0.96, top=0.915, bottom=0.05, hspace=0.62, wspace=0.18)
    _header(fig, "Daily summary", d.strftime("%A, %-d %B %Y"))

    w_today = (well.get(d.isoformat()) or {})
    weight_val = f"{trend['latest']['trend_kg']:.1f} kg" if trend.get("latest") else "–"
    weight_note = (f"{trend['change_kg_per_week']:+.2f} kg/wk" if "change_kg_per_week" in trend
                   else "trend (log daily: w 82.4)")
    _tiles(fig, gs[0, :], [
        ("Calories", f"{tot['kcal']:,.0f}", f"of {tgt['kcal']:,.0f} target" if tgt.get("kcal") else "kcal"),
        ("Protein", f"{tot['protein']:.0f} g",
         f"of {tgt['protein']:.0f} g" + (f" · {info['protein_g_per_kg']} g/kg" if info.get("protein_g_per_kg") else "")
         if tgt.get("protein") else "logged"),
        ("Sleep", f"{w_today['sleep_hours']:.1f} h" if w_today.get("sleep_hours") else "–",
         f"score {w_today['sleep_score']:.0f}" if w_today.get("sleep_score") else "last night"),
        ("Weight", weight_val, weight_note),
    ])

    # Macros vs target: one bar per macro on a gray 100% track, value labels at the end.
    ax = fig.add_subplot(gs[1, :])
    macros = [("Calories", "kcal", "kcal"), ("Protein", "protein", "g"), ("Carbs", "carbs", "g"), ("Fat", "fat", "g")]
    for i, (label, k, unit) in enumerate(macros):
        y = len(macros) - 1 - i
        t = tgt.get(k)
        pct = (tot[k] / t) if t else 0
        ax.barh(y, 1.0, height=0.5, color=TRACK, zorder=1)
        ax.barh(y, min(pct, 1.25), height=0.5, color=BLUE, zorder=2)
        ax.text(-0.02, y, label, ha="right", va="center", fontsize=9.5)
        left = (t - tot[k]) if t else None
        status = "" if t is None else (f"  {left:,.0f} left" if left >= 0 else f"  {-left:,.0f} over")
        val = ax.text(1.29, y, f"{tot[k]:,.0f} / {t:,.0f} {unit}" if t else f"{tot[k]:,.0f} {unit}",
                      ha="left", va="center", fontsize=9, fontweight="bold")
        ax.annotate(status, xycoords=val, xy=(1, 0.5), va="center", fontsize=8, color=TEXT_2)
    ax.axvline(1.0, color=TEXT_2, linewidth=1, linestyle=(0, (2, 2)), zorder=3)
    ax.set_xlim(-0.22, 1.75)
    ax.set_ylim(-0.7, len(macros) - 0.4)
    ax.set_axis_off()
    ax.set_title("Today vs targets")

    # Protein per meal — shows the spread; reference line at 0.4 g/kg per feeding.
    ax = fig.add_subplot(gs[2, 0])
    meals = [m for m in info["meals"]]
    if meals:
        xs = range(len(meals))
        ps = [m["protein"] for m in meals]
        ax.bar(xs, ps, width=0.6, color=BLUE, edgecolor=SURFACE, linewidth=2, zorder=2)
        for x, p in zip(xs, ps):
            ax.text(x, p, f"{p:.0f}", ha="center", va="bottom", fontsize=8, color=TEXT_2)
        kg = (trend.get("latest") or {}).get("kg") or prof.get("start_weight_kg")
        if kg:
            ref = 0.4 * min(kg, prof.get("goal_weight_kg") or kg) if kg > 100 else 0.4 * kg
            ax.axhline(ref, color=TEXT_2, linestyle=(0, (4, 3)), linewidth=1.1, zorder=3)
            ax.set_ylim(0, max(max(ps), ref) * 1.22)
        ax.set_xticks(list(xs), [m["ts"][11:16] for m in meals])
        _clean(ax)
        ax.set_yticks([])
        ax.set_title(f"Protein per meal (g) · line = {ref:.0f} g" if kg else "Protein per meal (g)")
    else:
        _empty(ax, "Protein per meal (g)", "no meals logged")

    # Training: minutes in each HR zone per activity (ordinal ramp Z1 light -> Z5 dark).
    ax = fig.add_subplot(gs[2, 1])
    acts = info["activities"]
    if acts:
        for i, a in enumerate(acts):
            y = len(acts) - 1 - i
            zones = json.loads(a["hr_zones_json"]) if a.get("hr_zones_json") else {}
            left = 0
            for z, col in enumerate(ZONES, start=1):
                v = zones.get(f"z{z}", 0) or 0
                if v:
                    ax.barh(y, v, left=left, height=0.5, color=col, edgecolor=SURFACE, linewidth=1.5, zorder=2)
                    left += v
            if not zones:
                ax.barh(y, a.get("duration_min") or 0, height=0.5, color=TRACK, zorder=2)
            name = (a.get("name") or a.get("type") or "").replace("_", " ")
            ax.text(0, y + 0.36, f"{name} · {a.get('duration_min') or 0:.0f} min · {a.get('active_kcal') or 0:.0f} kcal",
                    fontsize=8, va="bottom", color=TEXT)
        ax.set_ylim(-0.6, len(acts) - 0.1)
        ax.set_yticks([])
        _clean(ax, grid_axis="x")
        handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in ZONES]
        ax.legend(handles, [f"Z{i}" for i in range(1, 6)], ncol=5, loc="lower right", bbox_to_anchor=(1.0, 1.0),
                  frameon=False, fontsize=7.5, handlelength=0.9, handletextpad=0.25, columnspacing=0.6,
                  borderaxespad=0.2)
        ax.set_title("HR zones (min)")
    else:
        _empty(ax, "Training", "rest day")

    _daily_bars(fig.add_subplot(gs[3, 0]), week, [(intake.get(x.isoformat()) or {}).get("kcal") for x in week],
                tgt.get("kcal"), "Calories, last 7 days", "kcal", highlight_last=True)
    _daily_bars(fig.add_subplot(gs[3, 1]), week, [(intake.get(x.isoformat()) or {}).get("protein") for x in week],
                tgt.get("protein"), "Protein, last 7 days", "g", highlight_last=True)

    _recovery_row(fig, gs[4, :], week, well)
    fig.text(0.04, 0.012, "– = nothing logged that day", fontsize=7.5, color=MUTED)
    return _save(fig, f"daily-{d.isoformat()}.png")


# ---------------------------------------------------------------- weekly card

def render_weekly(conn, end: str | None = None) -> str:
    e = date.fromisoformat(db._parse_day(end))
    week = _days(e, 7)
    prev = _days(e - timedelta(days=7), 7)
    prof = db.get_profile(conn)
    stats = db.get_range_stats(conn, week[0].isoformat(), e.isoformat())
    intake = _intake_by_day(conn, week)
    well = _wellness_by_day(conn, week)
    trend = db.weight_trend(conn, days=28, end=e.isoformat())
    acts = [dict(r) for r in conn.execute(
        "SELECT day, type, duration_min FROM activities WHERE day BETWEEN ? AND ?",
        (week[0].isoformat(), e.isoformat()))]

    fig = plt.figure(figsize=(7.2, 12.0))
    gs = GridSpec(5, 2, figure=fig, height_ratios=[0.8, 1.1, 1.15, 1.35, 1.1],
                  left=0.06, right=0.96, top=0.925, bottom=0.04, hspace=0.62, wspace=0.2)
    _header(fig, "Weekly summary", f"{week[0].strftime('%-d %b')} – {e.strftime('%-d %b %Y')}")

    avg = stats["avg_per_logged_day"]
    adh = stats["adherence"]
    strength_n = sum(1 for a in acts if _training_category(a["type"]) == "Strength")
    sleep_vals = [w["sleep_hours"] for w in well.values() if w.get("sleep_hours")]
    _tiles(fig, gs[0, :], [
        ("Avg calories", f"{avg['kcal']:,.0f}" if avg else "–",
         f"{stats['days_logged']}/7 days logged" if avg else "no meals logged"),
        ("Avg protein", f"{avg['protein']:.0f} g" if avg else "–",
         f"target hit {adh['protein_days_hit_pct']}% of days" if "protein_days_hit_pct" in adh else ""),
        ("Weight", f"{trend['change_kg_per_week']:+.2f}" if "change_kg_per_week" in trend else "–",
         f"kg/wk ({trend['change_pct_per_week']:+.2f}%)" if "change_pct_per_week" in trend else "need 7+ days"),
        ("Gym sessions", f"{strength_n}", f"{len(acts)} activities · sleep {sum(sleep_vals) / len(sleep_vals):.1f} h"
         if sleep_vals else f"{len(acts)} activities"),
    ])

    _daily_bars(fig.add_subplot(gs[1, 0]), week, [(intake.get(x.isoformat()) or {}).get("kcal") for x in week],
                prof.get("kcal_target"), "Calories", "kcal")
    _daily_bars(fig.add_subplot(gs[1, 1]), week, [(intake.get(x.isoformat()) or {}).get("protein") for x in week],
                prof.get("protein_target_g"), "Protein", "g")

    # Weight: daily weigh-ins as dots, smoothed trend as a line (last 28 days).
    ax = fig.add_subplot(gs[2, :])
    wrows = [dict(r) for r in conn.execute(
        "SELECT day, kg FROM weights WHERE day BETWEEN ? AND ? ORDER BY day",
        ((e - timedelta(days=27)).isoformat(), e.isoformat()))]
    if wrows:
        xs = [date.fromisoformat(r["day"]) for r in wrows]
        ys = [r["kg"] for r in wrows]
        ema, sm = None, []
        for y in ys:
            ema = y if ema is None else ema + 0.25 * (y - ema)
            sm.append(ema)
        ax.scatter(xs, ys, s=22, color="#86b6ef", edgecolor=SURFACE, linewidth=1, zorder=3, label="weigh-in")
        ax.plot(xs, sm, color=BLUE, linewidth=2, zorder=4, label="trend")
        ax.annotate(f"{sm[-1]:.1f} kg", (xs[-1], sm[-1]), textcoords="offset points", xytext=(6, 0),
                    va="center", fontsize=9, fontweight="bold")
        if prof.get("goal_weight_kg"):
            ax.text(0.99, 0.05, f"goal {prof['goal_weight_kg']} kg", transform=ax.transAxes, ha="right",
                    fontsize=8, color=TEXT_2)
        ax.set_xlim(e - timedelta(days=27.5), e + timedelta(days=2.5))
        lo, hi = min(ys), max(ys)
        ax.set_ylim(lo - 0.8, hi + 0.8)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%-d %b"))
        ax.xaxis.set_major_locator(matplotlib.dates.WeekdayLocator(byweekday=6))  # Sundays
        ax.legend(loc="upper right", frameon=False, fontsize=8, ncol=2)
        ax.set_title("Weight, last 4 weeks (kg)")
        _clean(ax)
        if len(wrows) < 4:
            ax.text(0.5, 0.5, "weigh in daily (w 82.4) for a reliable trend", transform=ax.transAxes,
                    ha="center", fontsize=9, color=MUTED)
    else:
        _empty(ax, "Weight, last 4 weeks (kg)", "no weigh-ins yet — send e.g. \"w 82.4\" each morning")

    # Training minutes per day, stacked by category.
    ax = fig.add_subplot(gs[3, 0])
    if acts:
        bottoms = [0.0] * 7
        idx = {d.isoformat(): i for i, d in enumerate(week)}
        present = []
        for cat, col in TRAINING_COLORS.items():
            vals = [0.0] * 7
            for a in acts:
                if _training_category(a["type"]) == cat:
                    vals[idx[a["day"]]] += a["duration_min"] or 0
            if any(vals):
                present.append(cat)
                ax.bar(range(7), vals, bottom=bottoms, width=0.62, color=col, edgecolor=SURFACE, linewidth=2,
                       zorder=2, label=cat)
                bottoms = [b + v for b, v in zip(bottoms, vals)]
        for x, b in enumerate(bottoms):
            if b:
                ax.text(x, b, f"{b:.0f}", ha="center", va="bottom", fontsize=7.5, color=TEXT_2)
        ax.set_xticks(range(7), [d.strftime("%a")[:2] for d in week])
        ax.set_ylim(0, max(bottoms) * 1.2)
        ax.set_yticks([])
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=len(present), frameon=False, fontsize=8,
                  handlelength=1)
        ax.set_title("Training (min)")
        _clean(ax)
    else:
        _empty(ax, "Training (min)", "no activities")

    # Strength: best estimated 1RM per lift this week, with last week's as a marker.
    ax = fig.add_subplot(gs[3, 1])
    def best(days):
        rows = conn.execute(
            "SELECT exercise, MAX(kg * (1 + reps / 30.0)) e1rm FROM strength_sets WHERE day BETWEEN ? AND ? "
            "AND kg IS NOT NULL AND reps IS NOT NULL GROUP BY exercise", (days[0].isoformat(), days[-1].isoformat()))
        return {r["exercise"]: r["e1rm"] for r in rows}
    cur, old = best(week), best(prev)
    lifts = sorted(cur, key=cur.get, reverse=True)[:7]
    if lifts:
        ys = list(range(len(lifts)))[::-1]
        ax.barh(ys, [cur[l] for l in lifts], height=0.38, color=BLUE, zorder=2)
        had_prev = False
        for y, l in zip(ys, lifts):
            delta = ""
            if l in old:
                had_prev = True
                ax.plot([old[l]] * 2, [y - 0.26, y + 0.26], color=TEXT, linewidth=2, zorder=3)
                diff = cur[l] - old[l]
                delta = f"  {diff:+.1f}"
            ax.text(cur[l], y, f" {cur[l]:.0f}{delta}", va="center", fontsize=7.8, color=TEXT_2)
            ax.text(0, y + 0.24, l.title(), va="bottom", fontsize=7.5, color=TEXT)
        ax.set_yticks([])
        ax.set_xlim(0, max(max(cur.values()), max(old.values(), default=0)) * 1.3)
        ax.set_ylim(-0.6, len(lifts) - 0.1)
        _clean(ax, grid_axis="x")
        ax.set_title("Strength · best est. 1RM (kg)")
        ax.text(0, -0.17, "| = last week" if had_prev else "first week of data, no comparison yet",
                transform=ax.transAxes, fontsize=7.5, color=MUTED)
    else:
        _empty(ax, "Strength · best est. 1RM (kg)", "no weighted sets")

    _recovery_row(fig, gs[4, :], week, well)
    return _save(fig, f"weekly-{e.isoformat()}.png")


if __name__ == "__main__":
    import sys
    c = db.connect()
    print(render_daily(c, sys.argv[1] if len(sys.argv) > 1 else None))
    print(render_weekly(c, sys.argv[1] if len(sys.argv) > 1 else None))
