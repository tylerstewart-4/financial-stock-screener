import streamlit as st
import pandas as pd

st.title("Fundamental Stock Screener")

df = pd.read_csv("stocks.csv")

st.write("Columns found:")
st.write(df.columns)

st.dataframe(df)
