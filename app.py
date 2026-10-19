import streamlit as st
import pandas as pd

# Page title
st.title("Fundamental Stock Screener")

# Load stock data
df = pd.read_csv("stocks (1).csv")

# Sidebar filters
st.sidebar.header("Filters")

max_pe = st.sidebar.slider(
    "Maximum PE",
    min_value=1,
    max_value=100,
    value=40
)

min_roe = st.sidebar.slider(
    "Minimum ROE",
    min_value=0,
    max_value=100,
    value=20
)

# Recommendation logic
def recommendation(row):

    if row["PE"] <= 30 and row["ROE"] >= 20:
        return "BUY"

    elif row["ROE"] >= 20:
        return "HOLD"

    else:
        return "SELL"

# Add recommendation column
df["Recommendation"] = df.apply(recommendation, axis=1)

# Apply filters
filtered_df = df[
    (df["PE"] <= max_pe) &
    (df["ROE"] >= min_roe)
]

# Display results
st.subheader("Screening Results")
st.dataframe(filtered_df)
