import json
from datetime import date
from pathlib import Path

def get_default_db_path() -> Path:
    return Path(__file__).parent.parent / "planner_data.json"

def load(db_file: Path) -> dict:
    if db_file.exists():
        return json.loads(db_file.read_text())
    return {"next_id": 1, "topics": []}

def save(db: dict, db_file: Path):
    db_file.write_text(json.dumps(db, indent=2))

def parse_date(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError:
        raise SystemExit(f"Invalid date '{s}'. Use YYYY-MM-DD.")
