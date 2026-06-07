"""User preferences persistence. Scalar config (not history) — kept
separate from stats.py. JSON file at home_dashboard/preferences.json."""
import json
from pathlib import Path

_PREFS_PATH = Path(__file__).resolve().parent.parent / "preferences.json"

DEFAULTS = {
    "music_track": "rain",      # "rain" | "forest" | "white_noise" | "off"
    "volume": 0.4,              # 0.0 .. 1.0
    "custom_focus": 25,         # last custom focus minutes used
    "custom_break": 5,          # last custom break minutes used
}


def load() -> dict:
    """Return preferences merged over defaults. Missing file = all defaults."""
    if not _PREFS_PATH.exists():
        return dict(DEFAULTS)
    try:
        with _PREFS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULTS)
    # Always return defaults filled in — protects against partial files.
    merged = dict(DEFAULTS)
    merged.update({k: v for k, v in data.items() if k in DEFAULTS})
    return merged


def save(prefs: dict) -> None:
    """Persist only known keys; ignore anything stray."""
    clean = {k: prefs[k] for k in DEFAULTS if k in prefs}
    with _PREFS_PATH.open("w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2)
