import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Title
# -----------------------------
st.title("Industry Stock Screener")

# -----------------------------
# Load Data
# -----------------------------
df = pd.read_csv("stocks.csv")

# -----------------------------
# Industry Filter
# -----------------------------
industry = st.sidebar.selectbox(
    "Select Industry",
    ["All"] + sorted(df["Sector"].unique())
)

# -----------------------------
# Financial Filters
# -----------------------------
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

# -----------------------------
# Recommendation Logic
# -----------------------------
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

df["Recommendation"] = df.apply(
    recommendation,
    axis=1
)

# -----------------------------
# Apply Filters
# -----------------------------
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

# -----------------------------
# Dashboard Statistics
# -----------------------------
# Dashboard Statistics
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

# Pie Chart
fig = px.pie(
    filtered_df,
    names="Recommendation",
    title="Buy / Hold / Sell Distribution"
)

st.plotly_chart(fig)

# Scatter Plot
fig2 = px.scatter(
    filtered_df,
    x="PE",
    y="ROE",
    color="Recommendation",
    hover_name="Ticker",
    title="ROE vs PE Analysis"
)

st.plotly_chart(fig2)

# Results Table
st.subheader("Screening Results")
st.dataframe(filtered_df, use_container_width=True)

# Investment Conclusions
st.subheader("Investment Conclusions")

for _, row in filtered_df.iterrows():
    st.write(
        f"**{row['Ticker']}** is rated "
        f"**{row['Recommendation']}** "
        f"with PE = {row['PE']}, "
        f"ROE = {row['ROE']}%, "
        f"Debt/Equity = {row['DebtEquity']}, "
        f"and F-Score = {row['FScore']}."
    )

