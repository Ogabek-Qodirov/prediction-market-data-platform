from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
DASHBOARD_DIR = PROJECT_ROOT / "data" / "analytics" / "dashboard"

files = [
    "market_summary.csv",
    "top_markets.csv",
    "probability_distribution.csv",
    "historical_probability_changes.csv"
]

for file_name in files:
    file_path = DASHBOARD_DIR / file_name

    print(f"\n{'=' * 50}")
    print(f"DATASET: {file_name}")

    if not file_path.exists():
        print("STATUS: FILE NOT FOUND")
        continue

    data = pd.read_csv(file_path)

    print("Rows:", len(data))
    print("Columns:", list(data.columns))
    print("\nPreview:")
    print(data.head(5).to_string(index=False))