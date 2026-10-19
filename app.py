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
def recommendation(row):

    if (
        row["PE"] <= 30
        and row["ROE"] >= 20
        and row["DebtEquity"] <= 1.0
        and row["FScore"] >= 7
    ):
        return "BUY"

    elif row["FScore"] >= 5:
        return "HOLD"

    else:
        return "SELL"


df["Recommendation"] = df.apply(recommendation, axis=1)

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
