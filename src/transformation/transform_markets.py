import pandas as pd


REQUIRED_COLUMNS = [
    "id",
    "question",
    "probability",
    "volume",
    "createdTime",
    "isResolved"
]


def transform_markets(markets):

    df = pd.DataFrame(markets)

    # 1. Check required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # 2. Select relevant columns
    df = df[REQUIRED_COLUMNS].copy()

    # 3. Rename columns
    df = df.rename(columns={
        "id": "market_id",
        "isResolved": "is_resolved",
        "createdTime": "created_at"
    })

    # 4. Convert data types
    df["probability"] = pd.to_numeric(
        df["probability"], errors="coerce"
    )

    df["volume"] = pd.to_numeric(
        df["volume"], errors="coerce"
    )

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        unit="ms",
        errors="coerce"
    )

    # 5. Handle missing values
    df["question"] = df["question"].fillna("Unknown")
    df["volume"] = df["volume"].fillna(0)

    # 6. Remove invalid records
    df = df.dropna(subset=["market_id", "probability"])

    # Probability must be between 0 and 1
    df = df[
        df["probability"].between(0, 1)
    ]

    # 7. Remove duplicates
    df = df.drop_duplicates(
        subset=["market_id"],
        keep="last"
    )

    # 8. Reset index
    df = df.reset_index(drop=True)

    return df