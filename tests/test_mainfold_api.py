
import pytest
import requests
from unittest.mock import Mock, patch

from src.extraction.mainfold_api import (
    validate_markets,
    fetch_markets
)


# 1. Valid market data should pass validation
def test_validate_markets_accepts_valid_data():
    markets = [
        {"id": "market_1", "question": "Will it rain?"},
        {"id": "market_2", "question": "Will Bitcoin rise?"}
    ]

    assert validate_markets(markets) is True


# 2. API response must be a list
def test_validate_markets_rejects_non_list():
    with pytest.raises(ValueError):
        validate_markets({"id": "market_1"})


# 3. Every market must be a dictionary
def test_validate_markets_rejects_non_dictionary():
    with pytest.raises(ValueError):
        validate_markets(["invalid_market"])


# 4. Market must contain an ID
def test_validate_markets_rejects_missing_id():
    markets = [{"question": "Will it rain?"}]

    with pytest.raises(ValueError):
        validate_markets(markets)


# 5. Market must contain a question
def test_validate_markets_rejects_missing_question():
    markets = [{"id": "market_1"}]

    with pytest.raises(ValueError):
        validate_markets(markets)


# 6. Fetch markets successfully
@patch("src.extraction.mainfold_api.requests.Session")
def test_fetch_markets_returns_data(mock_session_class):
    mock_session = Mock()
    mock_session_class.return_value.__enter__.return_value = mock_session

    mock_response = Mock()
    mock_response.json.return_value = [
        {"id": "market_1", "question": "Will it rain?"}
    ]

    mock_session.get.return_value = mock_response

    result = fetch_markets(limit=10, max_pages=1)

    assert len(result) == 1
    assert result[0]["id"] == "market_1"


# 7. Empty API response should return an empty list
@patch("src.extraction.mainfold_api.requests.Session")
def test_fetch_markets_returns_empty_list(mock_session_class):
    mock_session = Mock()
    mock_session_class.return_value.__enter__.return_value = mock_session

    mock_response = Mock()
    mock_response.json.return_value = []

    mock_session.get.return_value = mock_response

    result = fetch_markets(limit=10, max_pages=1)

    assert result == []


# 8. API errors should be retried and eventually raised
@patch("src.extraction.mainfold_api.time.sleep")
@patch("src.extraction.mainfold_api.requests.Session")
def test_fetch_markets_raises_after_retries(
    mock_session_class,
    mock_sleep
):
    mock_session = Mock()
    mock_session_class.return_value.__enter__.return_value = mock_session

    mock_session.get.side_effect = requests.exceptions.ConnectionError(
        "Connection failed"
    )

    with pytest.raises(requests.exceptions.ConnectionError):
        fetch_markets(limit=10, max_pages=1, retries=2)

    assert mock_session.get.call_count == 2
