import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title="Industry Stock Screener", layout="wide")

st.title("Industry Stock Screener")

@st.cache_data(ttl=3600)
def load_stock_data():

    tickers = pd.read_csv("tickers.csv")

    rows = []

    for ticker in tickers["Ticker"]:

        try:

            stock = yf.Ticker(ticker)
            info = stock.info

            rows.append({
                "Ticker": ticker,
                "PE": info.get("trailingPE", 0),

                "ROE": (
                    info.get("returnOnEquity", 0) * 100
                    if info.get("returnOnEquity")
                    else 0
                ),

                "DebtEquity": info.get("debtToEquity", 0),

                "CurrentRatio": info.get("currentRatio", 0),

                "RevenueGrowth": (
                    info.get("revenueGrowth", 0) * 100
                    if info.get("revenueGrowth")
                    else 0
                ),

                "MarketCapBillions": (
                    info.get("marketCap", 0) / 1_000_000_000
                ),

                "Sector": info.get(
                    "sector",
                    "Unknown"
                )
            })

        except:
            pass

    df = pd.DataFrame(rows)

    if len(df) == 0:
        return df

    numeric_cols = [
        "PE",
        "ROE",
        "DebtEquity",
        "CurrentRatio",
        "RevenueGrowth",
        "MarketCapBillions"
    ]

    for col in numeric_cols:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    return df


df = load_stock_data()

if len(df) == 0:
    st.error("No stock data loaded")
    st.stop()

st.caption(
    f"Analyzing {len(df)} companies using live Yahoo Finance data."
)

# --------------------------------------------------
# STRENGTH SCORE
# --------------------------------------------------

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
    elif row["CurrentRatio"] >= 1:
        score += 1

    if row["DebtEquity"] <= 1:
        score += 2
    elif row["DebtEquity"] <= 2:
        score += 1

    return score


df["StrengthScore"] = df.apply(
    calculate_strength_score,
    axis=1
)

# --------------------------------------------------
# FILTERS
# --------------------------------------------------

industry = st.sidebar.selectbox(
    "Industry",
    ["All"] + sorted(df["Sector"].unique())
)

max_pe = st.sidebar.slider(
    "Maximum PE",
    1,
    100,
    40
)

min_roe = st.sidebar.slider(
    "Minimum ROE",
    0,
    100,
    10
)

max_de = st.sidebar.slider(
    "Maximum Debt to Equity",
    0.0,
    5.0,
    2.0
)

min_strength = st.sidebar.slider(
    "Minimum Strength Score",
    0,
    9,
    2
)

min_growth = st.sidebar.slider(
    "Minimum Revenue Growth",
    -20,
    50,
    0
)

min_current = st.sidebar.slider(
    "Minimum Current Ratio",
    0.0,
    5.0,
    0.0
)

max_marketcap = st.sidebar.slider(
    "Maximum Market Cap (Billions)",
    1,
    5000,
    5000
)

# --------------------------------------------------
# SCORE
# --------------------------------------------------

def calculate_score(row):

    score = 0

    if row["ROE"] >= 30:
        score += 25
    elif row["ROE"] >= 20:
        score += 15

    if row["PE"] <= 20:
        score += 25
    elif row["PE"] <= 30:
        score += 15

    if row["DebtEquity"] <= 1:
        score += 20

    score += row["StrengthScore"] * 5

    if row["RevenueGrowth"] >= 15:
        score += 15

    return min(score, 100)

df["Score"] = df.apply(
    calculate_score,
    axis=1
)

def recommendation(score):

    if score >= 75:
        return "BUY"
    elif score >= 50:
        return "HOLD"
    else:
        return "SELL"

df["Recommendation"] = df["Score"].apply(
    recommendation
)

filtered_df = df[
    (df["PE"] <= max_pe)
    & (df["ROE"] >= min_roe)
    & (df["DebtEquity"] <= max_de)
    & (df["StrengthScore"] >= min_strength)
    & (df["RevenueGrowth"] >= min_growth)
    & (df["CurrentRatio"] >= min_current)
    & (df["MarketCapBillions"] <= max_marketcap)
]

if industry != "All":
    filtered_df = filtered_df[
        filtered_df["Sector"] == industry
    ]

filtered_df = filtered_df.sort_values(
    by="Score",
    ascending=False
)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

buy_count = len(
    filtered_df[
        filtered_df["Recommendation"] == "BUY"
    ]
)

hold_count = len(
    filtered_df[
        filtered_df["Recommendation"] == "HOLD"
    ]
)

sell_count = len(
    filtered_df[
        filtered_df["Recommendation"] == "SELL"
    ]
)

c1, c2, c3 = st.columns(3)

c1.metric("BUY", buy_count)
c2.metric("HOLD", hold_count)
c3.metric("SELL", sell_count)

if len(filtered_df) > 0:

    fig = px.pie(
        filtered_df,
        names="Recommendation"
    )

    st.plotly_chart(fig)

    scatter = px.scatter(
        filtered_df,
        x="PE",
        y="ROE",
        color="Recommendation",
        hover_name="Ticker"
    )

    st.plotly_chart(scatter)

st.subheader("Screening Results")
st.dataframe(filtered_df)

st.subheader("🚀 Small Cap Discovery")

small_caps = filtered_df[
    filtered_df["MarketCapBillions"] <= 50
]

st.dataframe(
    small_caps.head(10)
)

st.subheader("🏆 Top 10 Buys")

top_buys = filtered_df[
    filtered_df["Recommendation"] == "BUY"
].head(10)

st.dataframe(top_buys)

st.subheader("⚠️ Top 10 Sells")

top_sells = filtered_df[
    filtered_df["Recommendation"] == "SELL"
].head(10)

st.dataframe(top_sells)

st.subheader("📊 Sector Rankings")

sector_scores = (
    filtered_df
    .groupby("Sector")["Score"]
    .mean()
    .reset_index()
)

sector_chart = px.bar(
    sector_scores,
    x="Sector",
    y="Score",
    color="Score"
)

st.plotly_chart(sector_chart)

st.subheader("📥 Downloads")

st.download_button(
    "Download Results",
    filtered_df.to_csv(index=False),
    "screening_results.csv",
    "text/csv"
)
