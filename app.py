import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Fundamental Stock Screener")

# Load data
df = pd.read_csv("stocks.csv")

# Sidebar Filters
st.sidebar.header("Filters")

max_pe = st.sidebar.slider("Maximum PE", 1, 100, 40)
min_roe = st.sidebar.slider("Minimum ROE", 0, 100, 20)
max_de = st.sidebar.slider("Maximum Debt to Equity", 0.0, 5.0, 2.0)
min_fscore = st.sidebar.slider("Minimum F Score", 0, 9, 6)

# Recommendation Logic
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

# Apply Filters
filtered_df = df[
    (df["PE"] <= max_pe)
    & (df["ROE"] >= min_roe)
    & (df["DebtEquity"] <= max_de)
    & (df["FScore"] >= min_fscore)
]

# Dashboard Stats
buy_count = len(filtered_df[filtered_df["Recommendation"] == "BUY"])
hold_count = len(filtered_df[filtered_df["Recommendation"] == "HOLD"])
sell_count = len(filtered_df[filtered_df["Recommendation"] == "SELL"])

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

# Table
st.subheader("Screening Results")
st.dataframe(filtered_df)
