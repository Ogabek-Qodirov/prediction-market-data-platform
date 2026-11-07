import json
from pathlib import Path
from datetime import datetime, timezone


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def save_markets(markets):

    today = datetime.now(timezone.utc)

    year = today.strftime("%Y")
    month = today.strftime("%m")
    date = today.strftime("%Y-%m-%d")

    output_dir = RAW_DATA_DIR / year / month
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / f"markets_{date}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            markets,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"Saved {len(markets)} markets to: {file_path}")

    return file_path