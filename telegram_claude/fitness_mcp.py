"""Stdio MCP server: the only way the fitness bot's Claude can read or change the log."""
from typing import Any

from mcp.server.mcpserver import MCPServer

import fitness_db as db

server = MCPServer(
    name="fitness",
    instructions=(
        "Food, weight, training and recovery log for a single user on a fat-loss diet. "
        "Meal items are lists of {name, grams, kcal, protein, carbs, fat, note?}; totals are computed for you. "
        "Dates are YYYY-MM-DD and timestamps ISO 8601 in the user's local time (Asia/Jerusalem)."
    ),
)
conn = db.connect()


@server.tool()
def get_profile() -> dict[str, Any]:
    """The user's profile: body stats, goals, kcal/macro targets, hand calibration, notes."""
    return db.get_profile(conn)


@server.tool()
def update_profile(fields: dict[str, Any]) -> dict[str, Any]:
    """Set profile fields. Allowed keys: name, sex, age, height_cm, start_weight_kg, goal_weight_kg,
    target_rate_pct_per_week, activity_baseline, kcal_target, protein_target_g, carb_target_g,
    fat_target_g, training_notes, diet_notes, onboarded. A null value removes the field."""
    return db.update_profile(conn, fields)


@server.tool()
def save_calibration(hand_length_cm: float, palm_width_cm: float, fist_width_cm: float | None = None,
                     finger_widths_cm: dict[str, float] | None = None, notes: str | None = None) -> dict[str, Any]:
    """Store the user's hand dimensions measured from their hand-next-to-tape photo.
    finger_widths_cm e.g. {"thumb": 2.2, "index": 1.8}. Used as a scale for food photos."""
    return db.save_calibration(conn, hand_length_cm, palm_width_cm, fist_width_cm, finger_widths_cm, notes)


@server.tool()
def log_meal(description: str, items: list[dict[str, Any]], meal_type: str | None = None,
             source: str | None = None, confidence: str | None = None, ts: str | None = None,
             status: str = "final") -> dict[str, Any]:
    """Log a meal. meal_type: breakfast/lunch/dinner/snack/pre_workout/post_workout.
    source: photo/text/label/template. confidence: low/medium/high.
    Use status='draft' while you still have clarifying questions; call finalize_meal once answered.
    ts defaults to now; pass it when the user says they ate earlier."""
    return db.log_meal(conn, description, items, meal_type, source, confidence, ts, status)


@server.tool()
def update_meal(meal_id: int, description: str | None = None, items: list[dict[str, Any]] | None = None,
                meal_type: str | None = None, confidence: str | None = None,
                ts: str | None = None) -> dict[str, Any]:
    """Correct a logged meal. Passing items replaces the full item list (send every item, not just changed ones)."""
    return db.update_meal(conn, meal_id, description, items, meal_type, confidence, ts)


@server.tool()
def finalize_meal(meal_id: int) -> dict[str, Any]:
    """Mark a draft meal as final once clarifying questions are answered (or the user says skip)."""
    return db.finalize_meal(conn, meal_id)


@server.tool()
def delete_meal(meal_id: int) -> dict[str, Any]:
    """Delete a meal by id."""
    return db.delete_meal(conn, meal_id)


@server.tool()
def get_open_drafts() -> list[dict[str, Any]]:
    """Draft meals still waiting on answers from the user."""
    return db.get_open_drafts(conn)


@server.tool()
def save_template(name: str, meal_id: int) -> dict[str, Any]:
    """Save a logged meal as a reusable template (e.g. 'usual breakfast')."""
    return db.save_template(conn, name, meal_id)


@server.tool()
def list_templates() -> list[dict[str, Any]]:
    """All saved meal templates with their totals."""
    return db.list_templates(conn)


@server.tool()
def log_template(name: str, multiplier: float = 1.0, meal_type: str | None = None,
                 ts: str | None = None) -> dict[str, Any]:
    """Log a saved template as a meal, optionally scaled (1.5 = one and a half portions)."""
    return db.log_template(conn, name, multiplier, meal_type, ts)


@server.tool()
def log_weight(kg: float, day: str | None = None) -> dict[str, Any]:
    """Log body weight (morning, after the toilet, before eating is best). Returns the smoothed trend."""
    return db.log_weight(conn, kg, day)


@server.tool()
def log_note(text: str) -> dict[str, Any]:
    """Log a free-text check-in: hunger, energy, soreness, mood, how a session felt, etc."""
    return db.log_note(conn, text)


@server.tool()
def log_strength_sets(exercise: str, sets: list[dict[str, Any]], day: str | None = None) -> dict[str, Any]:
    """Log gym sets the watch didn't capture. sets = [{"reps": 8, "kg": 80}, ...]. Use consistent
    exercise names (e.g. 'bench press', 'squat', 'deadlift', 'overhead press', 'pull up', 'row')."""
    return db.log_strength_sets(conn, exercise, sets, day)


@server.tool()
def get_day(day: str | None = None) -> dict[str, Any]:
    """Everything for one day (default today): meals, totals vs targets, remaining, activities,
    strength sets, sleep/HRV/resting HR/body battery, weight, notes."""
    return db.get_day(conn, day)


@server.tool()
def get_range_stats(start: str, end: str) -> dict[str, Any]:
    """Aggregates for a date range: average intake, adherence, weight trend, training by type,
    strength by exercise (best estimated 1RM), wellness averages, notes."""
    return db.get_range_stats(conn, start, end)


@server.tool()
def strength_history(exercise: str, weeks: int = 8) -> list[dict[str, Any]]:
    """Weekly best estimated 1RM for an exercise. A drop over 2+ weeks is an early muscle-loss signal."""
    return db.strength_history(conn, exercise, weeks)


@server.tool()
def weight_trend(days: int = 28) -> dict[str, Any]:
    """Smoothed weight trend and weekly rate of change (kg and % of bodyweight)."""
    return db.weight_trend(conn, days)


@server.tool()
def estimate_tdee(days: int = 21) -> dict[str, Any]:
    """Adaptive TDEE from logged intake and the trend-weight change, compared with Garmin's estimate."""
    return db.estimate_tdee(conn, days)


if __name__ == "__main__":
    server.run("stdio")
