import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Financial Stock Screener")

import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Fundamental Stock Screener")

tickers = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "META",
    "NVDA",
    "AMD",
    "INTC",
    "COST",
    "JNJ"
]

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "Ticker": ticker,
            "PE": info.get("trailingPE"),
            "PB": info.get("priceToBook"),
            "ROE": info.get("returnOnEquity"),
            "DebtEquity": info.get("debtToEquity"),
            "MarketCap": info.get("marketCap")
        }

    except:
        return None

data = []

for ticker in tickers:
    row = get_stock_data(ticker)

    if row:
        data.append(row)

df = pd.DataFrame(data)

st.dataframe(df)
