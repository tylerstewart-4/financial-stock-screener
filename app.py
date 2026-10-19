import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Financial Stock Screener")

ticker = st.text_input("Enter a Stock Ticker", "AAPL")

if ticker:
    stock = yf.Ticker(ticker)

    try:
        info = stock.info

        st.subheader(info.get("longName", ticker))

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Current Price",
            f"${info.get('currentPrice', 'N/A')}"
        )

        col2.metric(
            "P/E Ratio",
            info.get("trailingPE", "N/A")
        )

        col3.metric(
            "Market Cap",
            f"${info.get('marketCap', 0):,.0f}"
        )

    except:
        st.error("Unable to retrieve data.")
