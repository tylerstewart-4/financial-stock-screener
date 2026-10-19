import streamlit as st
import pandas as pd

st.title("Fundamental Stock Screener")

data = {
    "Ticker": ["AAPL", "MSFT", "NVDA", "GOOGL"],
    "PE": [35, 32, 45, 28],
    "ROE": [0.25, 0.30, 0.40, 0.22]
}

df = pd.DataFrame(data)

st.dataframe(df)
