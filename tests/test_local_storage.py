
import json
import pandas as pd
import pytest

from src.storage import local_storage


# 1. Test saving markets as JSON
def test_save_markets(tmp_path, monkeypatch):
    monkeypatch.setattr(
        local_storage,
        "RAW_DATA_DIR",
        tmp_path / "raw"
    )

    markets = [
        {"id": "market_1", "question": "Will it rain?"}
    ]

    file_path = local_storage.save_markets(markets)

    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == markets


# 2. Test saving snapshot metadata
def test_save_snapshot_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(
        local_storage,
        "PROJECT_ROOT",
        tmp_path
    )

    file_path = tmp_path / "data" / "raw" / "markets.json"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("[]", encoding="utf-8")

    markets = [
        {"id": "market_1", "question": "Will it rain?"}
    ]

    local_storage.save_snapshot_metadata(markets, file_path)

    metadata_file = tmp_path / "data" / "metadata.csv"

    assert metadata_file.exists()

    metadata = pd.read_csv(metadata_file)

    assert len(metadata) == 1
    assert metadata.iloc[0]["records_count"] == 1
    assert metadata.iloc[0]["status"] == "SUCCESS"


# 3. Test loading markets from JSON
def test_load_markets(tmp_path, monkeypatch):
    monkeypatch.setattr(
        local_storage,
        "validate_markets",
        lambda markets: True
    )

    markets = [
        {"id": "market_1", "question": "Will it rain?"}
    ]

    file_path = tmp_path / "markets.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(markets, file)

    result = local_storage.load_markets(file_path)

    assert result == markets


# 4. Test invalid data during loading
def test_load_markets_rejects_invalid_data(tmp_path, monkeypatch):
    def fake_validate(markets):
        raise ValueError("Invalid market data")

    monkeypatch.setattr(
        local_storage,
        "validate_markets",
        fake_validate
    )

    file_path = tmp_path / "markets.json"
    file_path.write_text('{"invalid": true}', encoding="utf-8")

    with pytest.raises(ValueError):
        local_storage.load_markets(file_path)


# 5. Test saving processed data as Parquet
def test_save_processed_markets(tmp_path, monkeypatch):
    monkeypatch.setattr(
        local_storage,
        "PROCESSED_DATA_DIR",
        tmp_path / "processed"
    )

    df = pd.DataFrame({
        "market_id": ["market_1"],
        "probability": [0.75],
        "volume": [100]
    })

    file_path = local_storage.save_processed_markets(df)

    assert file_path.exists()

    saved_df = pd.read_parquet(file_path)

    assert len(saved_df) == 1
    assert "snapshot_time" in saved_df.columns
    assert saved_df.iloc[0]["market_id"] == "market_1"
