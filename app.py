import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------
# PAGE TITLE
# ------------------------
st.title("Industry Stock Screener")

# ------------------------
# LOAD DATA
# ------------------------
df = pd.read_csv("stocks.csv")

# Clean column names
df.columns = df.columns.str.strip()

# Clean sector values
df["Sector"] = df["Sector"].fillna("Unknown")
df["Sector"] = df["Sector"].astype(str).str.strip()

# ------------------------
# INDUSTRY FILTER
# ------------------------
industry = st.sidebar.selectbox(
    "Select Industry",
    ["All"] + sorted(df["Sector"].unique().tolist())
)

# ------------------------
# FINANCIAL FILTERS
# ------------------------
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

min_fscore = st.sidebar.slider(
    "Minimum F Score",
    0,
    9,
    6
)

# ------------------------
# RECOMMENDATION LOGIC
# ------------------------
def calculate_score(row):

    score = 0

    # ROE Score
    if row["ROE"] >= 30:
        score += 30
    elif row["ROE"] >= 20:
        score += 20
    elif row["ROE"] >= 10:
        score += 10

    # PE Score
    if row["PE"] <= 20:
        score += 25
    elif row["PE"] <= 30:
        score += 15
    elif row["PE"] <= 40:
        score += 5

    # Debt-to-Equity Score
    if row["DebtEquity"] <= 0.5:
        score += 20
    elif row["DebtEquity"] <= 1:
        score += 15
    elif row["DebtEquity"] <= 2:
        score += 5

    # F-Score
    score += row["FScore"] * 2.5

    return round(score, 1)

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

df["Recommendation"] = df["Score"].apply(recommendation)
# ------------------------
# APPLY FILTERS
# ------------------------
filtered_df = df[
    (df["PE"] <= max_pe)
    & (df["ROE"] >= min_roe)
    & (df["DebtEquity"] <= max_de)
    & (df["FScore"] >= min_fscore)
]

if industry != "All":
    filtered_df = filtered_df[
        filtered_df["Sector"] == industry
    ]

# ------------------------
# DASHBOARD STATS
# ------------------------
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

# ------------------------
# PIE CHART
# ------------------------
if len(filtered_df) > 0:

    fig = px.pie(
        filtered_df,
        names="Recommendation",
        title="Buy / Hold / Sell Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

# ------------------------
# SCATTER PLOT
# ------------------------
if len(filtered_df) > 0:

    fig2 = px.scatter(
        filtered_df,
        x="PE",
        y="ROE",
        color="Recommendation",
        hover_name="Ticker",
        title="ROE vs PE Analysis"
    )

    st.plotly_chart(fig2, use_container_width=True)

# ------------------------
# RESULTS TABLE
# ------------------------
st.subheader("Screening Results")

st.dataframe(
    filtered_df,
    use_container_width=True
)
st.subheader("🏆 Top 10 Buy Opportunities")

top_buys = filtered_df[
    filtered_df["Recommendation"] == "BUY"
].sort_values(
    by="Score",
    ascending=False
).head(10)

st.dataframe(
    top_buys[
        [
            "Ticker",
            "Sector",
            "Score",
            "ROE",
            "PE",
            "FScore"
        ]
    ]
)
st.subheader("⚠️ Top Sell Opportunities")

top_sells = filtered_df[
    filtered_df["Recommendation"] == "SELL"
].sort_values(
    by="Score",
    ascending=True
).head(10)

st.dataframe(
    top_sells[
        [
            "Ticker",
            "Sector",
            "Score",
            "ROE",
            "PE",
            "FScore"
        ]
    ]
)
