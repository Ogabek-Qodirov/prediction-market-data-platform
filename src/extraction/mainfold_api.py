import requests
import time

API_URL = "https://api.manifold.markets/v0/markets"

def validate_markets(markets):
    """Check basic data quality of extracted markets."""

    if not isinstance(markets, list):
        raise ValueError("API response must be a list")

    for market in markets:
        if not isinstance(market, dict):
            raise ValueError("Each market must be a dictionary")

        if not market.get("id"):
            raise ValueError("Market is missing its ID")

        if not market.get("question"):
            raise ValueError("Market is missing its question")

    return True

def fetch_markets(limit=100, max_pages=3, retries=3):

    all_markets = []
    before = None

    with requests.Session() as session:

        for page in range(max_pages):

            params = {"limit": limit}

            if before:
                params["before"] = before

            for attempt in range(retries):

                try:
                    response = session.get(
                        API_URL,
                        params=params,
                        timeout=20
                    )

                    response.raise_for_status()

                    markets = response.json()
                    break

                except requests.exceptions.RequestException as error:

                    print(f"Attempt {attempt + 1} failed: {error}")

                    if attempt == retries - 1:
                        raise

                    time.sleep(2)

            if not markets:
                break

            validate_markets(markets)

            all_markets.extend(markets)

            before = markets[-1]["id"]

            print(
                f"Page {page + 1}: "
                f"{len(markets)} markets collected"
            )

    return all_markets