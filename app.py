
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "analytics" / "dashboard"

st.set_page_config(
    page_title="Prediction Market Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Prediction Market Analytics")
st.caption("Manifold Markets — Data Engineering Project")

# Load datasets
def load_data(filename):
    path = DATA_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


summary = load_data("market_summary.csv")
top_markets = load_data("top_markets.csv")
distribution = load_data("probability_distribution.csv")
history = load_data("historical_probability_changes.csv")

# KPI metrics
st.header("Market Overview")

if not summary.empty:
    row = summary.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Markets",
        f"{int(row['total_markets']):,}"
    )

    col2.metric(
        "Average Probability",
        f"{row['average_probability']:.2%}"
    )

    col3.metric(
        "Average Volume",
        f"{row['average_volume']:,.2f}"
    )
else:
    st.warning("Market summary dataset is unavailable.")

st.divider()

# Probability distribution
st.header("Probability Distribution")

if not distribution.empty:
    chart_data = distribution.set_index("probability_range")
    st.bar_chart(chart_data["market_count"])
else:
    st.info("No probability distribution data available.")

st.divider()

# Top Markets
st.header("Market Explorer")

if not top_markets.empty:
    search = st.text_input(
        "Search markets",
        placeholder="Enter a market question..."
    )

    min_volume = st.number_input(
        "Minimum market volume",
        min_value=0.0,
        value=0.0,
        step=100.0
    )

    filtered_markets = top_markets.copy()

    if "question" in filtered_markets.columns:
        filtered_markets = filtered_markets[
            filtered_markets["question"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    if "volume" in filtered_markets.columns:
        filtered_markets = filtered_markets[
            filtered_markets["volume"] >= min_volume
        ]

    display_columns = [
        column for column in [
            "question",
            "probability",
            "volume",
            "is_resolved"
        ]
        if column in filtered_markets.columns
    ]

    st.caption(f"Found {len(filtered_markets)} markets")

    st.dataframe(
        filtered_markets[display_columns],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No market data available.")


# Historical analysis
st.header("Historical Probability Changes")

if not history.empty:
    required = {
        "market_id",
        "question",
        "snapshot_time",
        "current_probability"
    }

    if required.issubset(history.columns):
        markets = history["market_id"].dropna().unique()

        if len(markets) > 0:
            selected_market = st.selectbox(
                "Select a market",
                markets
            )

            selected_history = history[
                history["market_id"] == selected_market
            ].copy()

            selected_history["snapshot_time"] = pd.to_datetime(
                selected_history["snapshot_time"]
            )

            selected_history = selected_history.sort_values(
                "snapshot_time"
            )

            st.line_chart(
                selected_history.set_index("snapshot_time")[
                    "current_probability"
                ]
            )
        else:
            st.info("No historical market records available.")
    else:
        st.info("Historical dataset is missing required columns.")
else:
    st.info("No historical probability changes available.")
