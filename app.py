import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Industry Stock Screener",
    layout="wide"
)

st.title("Industry Stock Screener")

# ---------------------------------------------------
# STOCK UNIVERSE
# ---------------------------------------------------

universe = st.sidebar.selectbox(
    "Stock Universe",
    [
        "Custom Watchlist",
        "S&P 500",
        "Russell 2000"
    ]
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_stock_data(csv_file):

    df = pd.read_csv(csv_file)

    numeric_cols = [
        "PE",
        "ROE",
        "DebtEquity",
        "CurrentRatio",
        "RevenueGrowth",
        "MarketCapBillions"
    ]

    for col in numeric_cols:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

    return df


if universe == "Custom Watchlist":

    df = load_stock_data("tickers.csv")

elif universe == "S&P 500":

    df = load_stock_data("sp500.csv")

else:

    df = load_stock_data("russell2000.csv")


if len(df) == 0:

    st.error("No stock data loaded.")
    st.stop()

st.info(
    f"Universe: {universe} | Companies Loaded: {len(df)}"
)

# ---------------------------------------------------
# STRENGTH SCORE
# ---------------------------------------------------

def calculate_strength_score(row):

    score = 0

    if row["ROE"] >= 20:
        score += 3
    elif row["ROE"] >= 10:
        score += 2
    elif row["ROE"] > 0:
        score += 1

    if row["RevenueGrowth"] >= 15:
        score += 2
    elif row["RevenueGrowth"] >= 5:
        score += 1

    if row["CurrentRatio"] >= 2:
        score += 2
    elif row["CurrentRatio
