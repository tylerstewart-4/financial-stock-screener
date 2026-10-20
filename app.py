import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

# ---------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------

st.title("Industry Stock Screener")

# ---------------------------------------------------
# LOAD LIVE DATA
# ---------------------------------------------------

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

# ---------------------------------------------------
# DATAFRAME
# ---------------------------------------------------

df = load_stock_data()

st.subheader("Debug Data")

st.write("Total companies loaded:", len(df))

st.dataframe(df)
if len(df) == 0:

    st.error("No stock data loaded.")
    st.stop()

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

# ---------------------------------------------------
# INDUSTRY FILTER
# ---------------------------------------------------

industry = st.sidebar.selectbox(
    "Select Industry",
    ["All"] + sorted(df["Sector"].unique().tolist())
)

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

st.sidebar.header("Financial Filters")

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
    20
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
    4
)

min_growth = st.sidebar.slider(
    "Minimum Revenue Growth (%)",
    -20,
    50,
    5
)

min_current = st.sidebar.slider(
    "Minimum Current Ratio",
    0.0,
    5.0,
    1.0
)

# ---------------------------------------------------
# MAIN SCORE
# ---------------------------------------------------

def calculate_score(row):

    score = 0

    if row["ROE"] >= 30:
        score += 30
    elif row["ROE"] >= 20:
        score += 20
    elif row["ROE"] >= 10:
        score += 10

    if row["PE"] <= 20:
        score += 25
    elif row["PE"] <= 30:
        score += 15
    elif row["PE"] <= 40:
        score += 5

    if row["DebtEquity"] <= 0.5:
        score += 20
    elif row["DebtEquity"] <= 1:
        score += 15
    elif row["DebtEquity"] <= 2:
        score += 5

    score += row["StrengthScore"] * 5

    if row["CurrentRatio"] >= 2:
        score += 10
    elif row["CurrentRatio"] >= 1:
        score += 5

    if row["RevenueGrowth"] >= 15:
        score += 15
    elif row["RevenueGrowth"] >= 5:
        score += 10

    return min(round(score, 1), 100)

df["Score"] = df.apply(
    calculate_score,
    axis=1
)

# ---------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------

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

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------

filtered_df = df[
    (df["PE"] <= max_pe)
    & (df["ROE"] >= min_roe)
    & (df["DebtEquity"] <= max_de)
    & (df["StrengthScore"] >= min_strength)
    & (df["RevenueGrowth"] >= min_growth)
    & (df["CurrentRatio"] >= min_current)
]

if industry != "All":

    filtered_df = filtered_df[
        filtered_df["Sector"] == industry
    ]

filtered_df = filtered_df.sort_values(
    by="Score",
    ascending=False
)

# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

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

col1, col2, col3 = st.columns(3)

col1.metric("BUY", buy_count)
col2.metric("HOLD", hold_count)
col3.metric("SELL", sell_count)

# ---------------------------------------------------
# CHARTS
# ---------------------------------------------------

if len(filtered_df) > 0:

    fig1 = px.pie(
        filtered_df,
        names="Recommendation",
        title="Buy / Hold / Sell Distribution"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    fig2 = px.scatter(
        filtered_df,
        x="PE",
        y="ROE",
        color="Recommendation",
        hover_name="Ticker",
        title="ROE vs PE Analysis"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ---------------------------------------------------
# RESULTS
# ---------------------------------------------------

st.subheader("Screening Results")

st.dataframe(
    filtered_df,
    use_container_width=True
)

st.download_button(
    "Download Screening Results",
    filtered_df.to_csv(index=False),
    "screening_results.csv",
    "text/csv"
)
