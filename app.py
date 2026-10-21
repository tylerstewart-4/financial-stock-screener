import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(
    page_title="Industry Stock Screener",
    layout="wide"
)

st.title("Industry Stock Screener")

# ---------------------------------------------------
# LOAD LIVE DATA
# ---------------------------------------------------

@st.cache_data(ttl=86400)
def load_stock_data(csv_file):

    tickers = pd.read_csv(csv_file)

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

                "DebtEquity": info.get(
                    "debtToEquity",
                    0
                ),

                "CurrentRatio": info.get(
                    "currentRatio",
                    0
                ),

                "RevenueGrowth": (
                    info.get("revenueGrowth", 0) * 100
                    if info.get("revenueGrowth")
                    else 0
                ),

                "MarketCapBillions": (
                    info.get("marketCap", 0)
                    / 1000000000
                ),

                "Sector": info.get(
                    "sector",
                    "Unknown"
                )
            })

        except Exception:
            pass

    df = pd.DataFrame(rows)

    if len(df) == 0:
        return pd.DataFrame()

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
# ---------------------------------------------------
# DATA SOURCE
# ---------------------------------------------------

df = load_stock_data("tickers.csv")
df = df.drop_duplicates(
    subset=["Ticker"]
)
# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

df = load_stock_data("tickers.csv")

st.write("Rows loaded:", len(df))
st.dataframe(df.head(10))

if len(df) == 0:

    st.error("No stock data loaded.")
    st.stop()

st.info(
    f"Companies Loaded: {len(df)}"
)

# --------------------------------------------------
# STRENGTH SCORE
# --------------------------------------------------

def calculate_strength_score(row):

    score = 0

    if row["PE"] <= 20:
        score += 3
    elif row["PE"] <= 30:
        score += 2

    if row["ROE"] >= 20:
        score += 2
    elif row["ROE"] >= 10:
        score += 1

    if row["MarketCapBillions"] <= 20:
        score += 2

    if row["RevenueGrowth"] >= 15:
        score += 2
    elif row["RevenueGrowth"] >= 5:
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
    ["All"] + sorted(df["Sector"].dropna().unique().tolist())
)

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

st.sidebar.header("Financial Filters")

max_pe = st.sidebar.slider(
    "Maximum PE",
    1,
    100,
    50
)

min_roe = st.sidebar.slider(
    "Minimum ROE",
    0,
    100,
    5
)

max_de = st.sidebar.slider(
    "Maximum Debt to Equity",
    0.0,
    5.0,
    3.0
)

min_strength = st.sidebar.slider(
    "Minimum Strength Score",
    0,
    9,
    1
)

min_growth = st.sidebar.slider(
    "Minimum Revenue Growth (%)",
    -20,
    50,
    -5
)

min_current = st.sidebar.slider(
    "Minimum Current Ratio",
    0.0,
    5.0,
    0.0
)

max_marketcap = st.sidebar.slider(
    "Maximum Market Cap ($ Billions)",
    1,
    5000,
    5000
)

discovery_cap = st.sidebar.slider(
    "Discovery Market Cap Limit ($ Billions)",
    1,
    100,
    20
)

min_criteria = st.sidebar.slider(
    "Minimum Criteria Met",
    1,
    6,
    3
)

# ---------------------------------------------------
# CRITERIA SCORE
# ---------------------------------------------------

def calculate_criteria_met(row):

    criteria = 0

    if row["PE"] <= max_pe:
        criteria += 1

    if row["ROE"] >= min_roe:
        criteria += 1

    if row["DebtEquity"] <= max_de:
        criteria += 1

    if row["StrengthScore"] >= min_strength:
        criteria += 1

    if row["RevenueGrowth"] >= min_growth:
        criteria += 1

    if row["CurrentRatio"] >= min_current:
        criteria += 1

    return criteria


df["CriteriaMet"] = df.apply(
    calculate_criteria_met,
    axis=1
)

# --------------------------------------------------
# SCORE
# --------------------------------------------------

def calculate_score(row):

    score = 0

    missing_data = 0

    if row["PE"] == 0:
        missing_data += 1

    if row["ROE"] == 0:
        missing_data += 1

    if row["DebtEquity"] == 0:
        missing_data += 1

    if row["CurrentRatio"] == 0:
        missing_data += 1

    if row["RevenueGrowth"] == 0:
        missing_data += 1

    # ROE

    if row["ROE"] >= 30:
        score += 25
    elif row["ROE"] >= 20:
        score += 15

    # PE

    if row["PE"] <= 20 and row["PE"] > 0:
        score += 25
    elif row["PE"] <= 30 and row["PE"] > 0:
        score += 15

    # Debt

    if row["DebtEquity"] <= 1 and row["DebtEquity"] > 0:
        score += 20

    # Strength

    score += row["StrengthScore"] * 5

    # Growth

    if row["RevenueGrowth"] >= 15:
        score += 15

    # Missing Data Penalty

    score -= missing_data * 15

    return max(min(score, 100), 0)


df["Score"] = df.apply(
    calculate_score,
    axis=1
)

# ---------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------

def recommendation(score):

    if score >= 60:
        return "BUY"
    elif score >= 35:
        return "HOLD"
    else:
        return "SELL"


df["Recommendation"] = df["Score"].apply(
    recommendation
)

# ---------------------------------------------------
# FILTER DATA
# ---------------------------------------------------

filtered_df = df[
    (df["CriteriaMet"] >= min_criteria)
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

st.success(
    f"{len(filtered_df)} of {len(df)} companies passed the screen "
    f"({round(len(filtered_df)/len(df)*100,1)}%)."
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

c1, c2, c3 = st.columns(3)

c1.metric("BUY", buy_count)
c2.metric("HOLD", hold_count)
c3.metric("SELL", sell_count)

# ---------------------------------------------------
# RESULTS
# ---------------------------------------------------

st.subheader("Screening Results")
st.dataframe(filtered_df)

# ---------------------------------------------------
# DISCOVERY
# ---------------------------------------------------

st.subheader("🚀 Small Cap Discovery")

discovery_df = filtered_df[
    filtered_df["MarketCapBillions"] <= discovery_cap
]

st.dataframe(discovery_df.head(10))
# --------------------------------------------------
# CLEAN SCATTER DATA
# --------------------------------------------------

scatter_df = filtered_df[
    (filtered_df["PE"] >= 0)
    & (filtered_df["PE"] <= 100)
    & (filtered_df["ROE"] >= -50)
    & (filtered_df["ROE"] <= 100)
]

# --------------------------------------------------
# SCATTER PLOT
# --------------------------------------------------

if len(scatter_df) > 0:

    scatter = px.scatter(
        scatter_df,
        x="PE",
        y="ROE",
        color="Recommendation",
        hover_name="Ticker",
        title="ROE vs PE Analysis",
        color_discrete_map={
            "BUY": "#00C853",
            "HOLD": "#1976D2",
            "SELL": "#8B0000"
        }
    )

    scatter.update_layout(
        xaxis_title="PE Ratio",
        yaxis_title="ROE (%)"
    )

    st.plotly_chart(
        scatter,
        use_container_width=True
    )
    scatter.update_layout(
    title_x=0.5
)
# --------------------------------------------------
# SECTOR RANKINGS
# --------------------------------------------------

st.subheader("📊 Sector Rankings")

sector_scores = (
    filtered_df
    .groupby("Sector")["Score"]
    .mean()
    .reset_index()
)

if len(sector_scores) > 0:

    chart = px.bar(
        sector_scores,
        x="Sector",
        y="Score",
        color="Score"
    )

    st.plotly_chart(
        chart,
        use_container_width=True
    )
# --------------------------------------------------
# TOP BUYS
# --------------------------------------------------

st.subheader("🏆 Top 10 Buy Opportunities")

top_buys = filtered_df[
    filtered_df["Recommendation"] == "BUY"
].head(10)

st.dataframe(top_buys)
# --------------------------------------------------
# TOP SELLS
# --------------------------------------------------

st.subheader("⚠️ Top 10 Sell Opportunities")

top_sells = filtered_df[
    filtered_df["Recommendation"] == "SELL"
].head(10)

st.dataframe(top_sells)
# --------------------------------------------------
# PIE CHART
# --------------------------------------------------

if len(filtered_df) > 0:

    fig = px.pie(
        filtered_df,
        names="Recommendation",
        title="Buy / Hold / Sell Distribution",
        color="Recommendation",
        color_discrete_map={
            "BUY": "#00C853",   # Green
            "HOLD": "#1976D2",  # Blue
            "SELL": "#8B0000"   # Dark Red
        }
    )

    fig.update_traces(
        textinfo="percent+label"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
 # --------------------------------------------------
# INVESTMENT CONCLUSION
# --------------------------------------------------

st.subheader("📝 Investment Conclusion")

if len(filtered_df) > 0:

    best_stock = filtered_df.iloc[0]

    st.write(
        f"The highest-ranked company is {best_stock['Ticker']} "
        f"with a score of {best_stock['Score']:.1f}."
    )

    st.write(
        f"This company passed {best_stock['CriteriaMet']} screening criteria "
        f"and scored highly due to its profitability, valuation, growth profile, "
        f"financial strength, and overall fundamentals."
    )

    st.write(
        f"Key metrics include:"
    )

    st.write(
        f"• PE Ratio: {best_stock['PE']:.2f}"
    )

    st.write(
        f"• ROE: {best_stock['ROE']:.2f}%"
    )

    st.write(
        f"• Debt to Equity: {best_stock['DebtEquity']:.2f}"
    )

    st.write(
        f"• Revenue Growth: {best_stock['RevenueGrowth']:.2f}%"
    )

    st.write(
        f"• Market Cap: {best_stock['MarketCapBillions']:.2f} Billion"
    )

    st.write(
        f"• Sector: {best_stock['Sector']}"
    )
# ---------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------

st.download_button(
    "Download Screening Results",
    filtered_df.to_csv(index=False),
    "screening_results.csv",
    "text/csv"
)
