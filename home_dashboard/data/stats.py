"""Daily session stats persistence. Flat dict keyed by ISO date so a
future history view can read the same file with no migration."""
import json
from datetime import date
from pathlib import Path

_STATS_PATH = Path(__file__).resolve().parent.parent / "stats.json"


def _read_all() -> dict:
    if not _STATS_PATH.exists():
        return {}
    try:
        with _STATS_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _write_all(data: dict) -> None:
    with _STATS_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_today() -> dict:
    today_key = date.today().isoformat()
    entry = _read_all().get(today_key, {})
    return {
        "sessions": int(entry.get("sessions", 0)),
        "total_minutes": int(entry.get("total_minutes", 0)),
    }


def record_session(minutes: int) -> None:
    today_key = date.today().isoformat()
    data = _read_all()
    entry = data.get(today_key, {"sessions": 0, "total_minutes": 0})
    entry["sessions"] = int(entry.get("sessions", 0)) + 1
    entry["total_minutes"] = int(entry.get("total_minutes", 0)) + int(minutes)
    data[today_key] = entry
    _write_all(data)


def reset_today() -> None:
    today_key = date.today().isoformat()
    data = _read_all()
    if today_key in data:
        del data[today_key]
        _write_all(data)
