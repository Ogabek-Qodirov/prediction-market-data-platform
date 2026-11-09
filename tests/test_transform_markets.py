
import pytest
from src.transformation.transform_markets import transform_markets


def test_transform_markets_returns_dataframe():
    markets = [
        {
            "id": "market_1",
            "question": "Will Bitcoin reach $100k?",
            "probability": 0.75,
            "volume": 1500,
            "createdTime": 1700000000000,
            "isResolved": False
        }
    ]

    result = transform_markets(markets)

    assert len(result) == 1
    assert "market_id" in result.columns
    assert "probability" in result.columns


def test_transform_markets_removes_duplicate_markets():
    market = {
        "id": "market_1",
        "question": "Will Bitcoin reach $100k?",
        "probability": 0.75,
        "volume": 1500,
        "createdTime": 1700000000000,
        "isResolved": False
    }

    result = transform_markets([market, market])

    assert len(result) == 1


def test_transform_markets_returns_empty_dataframe_for_empty_input():
    result = transform_markets([])

    assert result.empty


def test_invalid_probability_is_removed():
    markets = [
        {
            "id": "market_1",
            "question": "Test market",
            "probability": 1.5,
            "volume": 100,
            "createdTime": 1700000000000,
            "isResolved": False
        }
    ]

    result = transform_markets(markets)

    assert len(result) == 0


def test_missing_probability_is_removed():
    markets = [
        {
            "id": "market_1",
            "question": "Test market",
            "probability": "invalid",
            "volume": 100,
            "createdTime": 1700000000000,
            "isResolved": False
        }
    ]

    result = transform_markets(markets)

    assert len(result) == 0


def test_missing_volume_is_replaced_with_zero():
    markets = [
        {
            "id": "market_1",
            "question": "Test market",
            "probability": 0.75,
            "volume": None,
            "createdTime": 1700000000000,
            "isResolved": False
        }
    ]

    result = transform_markets(markets)

    assert result.iloc[0]["volume"] == 0


def test_missing_question_is_replaced_with_unknown():
    markets = [
        {
            "id": "market_1",
            "question": None,
            "probability": 0.75,
            "volume": 100,
            "createdTime": 1700000000000,
            "isResolved": False
        }
    ]

    result = transform_markets(markets)

    assert result.iloc[0]["question"] == "Unknown"


def test_missing_required_column_raises_error():
    markets = [
        {
            "id": "market_1",
            "question": "Test market",
            "probability": 0.75
        }
    ]

    with pytest.raises(ValueError):
        transform_markets(markets)
