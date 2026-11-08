
from src.extraction.mainfold_api import fetch_markets

from src.storage.local_storage import (
    save_markets,
    save_snapshot_metadata,
    load_markets,
    save_processed_markets
)

from src.transformation.transform_markets import transform_markets


# ==========================================
# 1. EXTRACT DATA FROM MANIFOLD API
# ==========================================

markets = fetch_markets(
    limit=100,
    max_pages=3,
    retries=3
)


# ==========================================
# 2. SAVE RAW JSON SNAPSHOT
# ==========================================

file_path = save_markets(markets)


# ==========================================
# 3. SAVE SNAPSHOT METADATA
# ==========================================

save_snapshot_metadata(markets, file_path)


# ==========================================
# 4. LOAD RAW JSON SNAPSHOT
# ==========================================

loaded_markets = load_markets(file_path)


# ==========================================
# 5. TRANSFORM RAW DATA
# ==========================================

df = transform_markets(loaded_markets)


# ==========================================
# 6. SAVE PROCESSED DATA AS PARQUET
# ==========================================

processed_file = save_processed_markets(df)


# ==========================================
# 7. PIPELINE RESULTS
# ==========================================

print("\n========== PIPELINE RESULTS ==========")

print("Extracted records:", len(markets))
print("Loaded records:", len(loaded_markets))
print("Transformed records:", len(df))

print("Raw JSON file:", file_path)
print("Processed Parquet file:", processed_file)


# ==========================================
# 8. DATA QUALITY SUMMARY
# ==========================================

print("\n========== DATA QUALITY ==========")

print("Total rows:", len(df))
print("Total columns:", len(df.columns))

print(
    "Duplicate market IDs:",
    df["market_id"].duplicated().sum()
)

print("\nMissing values:")
print(df.isnull().sum())

print("\n========== TRANSFORMED DATA ==========")
print(df.head())

# ==========================================
# 9. STORAGE COMPARISON
# ==========================================

json_size = file_path.stat().st_size
parquet_size = processed_file.stat().st_size

print("\n========== STORAGE COMPARISON ==========")

print(f"JSON size: {json_size / 1024:.2f} KB")
print(f"Parquet size: {parquet_size / 1024:.2f} KB")

if parquet_size > 0:
    compression_ratio = json_size / parquet_size
    print(f"Size ratio: {compression_ratio:.2f}x")