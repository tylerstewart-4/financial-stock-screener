import streamlit as st
import pandas as pd

st.title("Fundamental Stock Screener")

df = pd.read_csv("stocks.csv")

st.sidebar.header("Filters")

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

filtered_df = df[
    (df["PE"] <= max_pe) &
    (df["ROE"] >= min_roe)
]

st.dataframe(filtered_df)
