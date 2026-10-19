import streamlit as st
import pandas as pd

st.title("Fundamental Stock Screener")

data = {
    "Ticker": ["AAPL", "MSFT", "NVDA", "GOOGL"],
    "PE": [35, 32, 45, 28],
    "ROE": [25, 30, 40, 22]
}

df = pd.DataFrame(data)

# Sidebar filter
max_pe = st.sidebar.slider(
    "Maximum PE Ratio",
    10,
    50,
    40
)

filtered_df = df[df["PE"] <= max_pe]

st.dataframe(filtered_df)
