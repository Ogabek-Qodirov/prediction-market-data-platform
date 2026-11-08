import json
from pathlib import Path
from datetime import datetime
import csv
from src.extraction.mainfold_api import validate_markets

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def save_markets(markets):

    today = datetime.now()

    year = today.strftime("%Y")
    month = today.strftime("%m")
    timestamp = today.strftime("%Y-%m-%d_%H-%M-%S")

    output_dir = RAW_DATA_DIR / year / month
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / f"markets_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            markets,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"Saved {len(markets)} markets to: {file_path}")

    return file_path

def save_snapshot_metadata(markets, file_path):

    metadata_file = PROJECT_ROOT / "data" / "metadata.csv"

    metadata_file.parent.mkdir(parents=True, exist_ok=True)

    file_exists = metadata_file.exists()

    with open(metadata_file, "a", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "extraction_time",
                "records_count",
                "file_path",
                "status"
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "extraction_time": datetime.now().isoformat(),
            "records_count": len(markets),
            "file_path": str(file_path.relative_to(PROJECT_ROOT)),
            "status": "SUCCESS"
        })

    print("Snapshot metadata saved.")

def load_markets(file_path):
        """Load markets from a saved JSON snapshot."""

        with open(file_path, "r", encoding="utf-8") as file:
            markets = json.load(file)

        validate_markets(markets)

        print(f"Loaded {len(markets)} markets from: {file_path}")

        return markets

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def save_processed_markets(df):
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_time = datetime.now()
    timestamp = snapshot_time.strftime("%Y-%m-%d_%H-%M-%S")

    df = df.copy()
    df["snapshot_time"] = snapshot_time

    file_path = PROCESSED_DATA_DIR / f"markets_{timestamp}.parquet"

    df.to_parquet(
        file_path,
        index=False,
        engine="pyarrow"
    )

    print(f"Processed data saved to: {file_path}")
    return file_path