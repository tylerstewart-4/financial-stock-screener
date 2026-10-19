import streamlit as st
import pandas as pd

st.title("Fundamental Stock Screener")

df = pd.read_csv("stocks (1).csv")

st.write("Columns found:")
st.write(df.columns)

st.dataframe(df)
    filtered_df,
    use_container_width=True
)
