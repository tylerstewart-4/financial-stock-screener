import pandas as pd
import yfinance as yf

tickers = pd.read_csv("tickers.csv")

rows = []

for ticker in tickers["Ticker"]:

    try:

        stock = yf.Ticker(ticker)
        info = stock.info

        rows.append({

            "Ticker": ticker,

            "PE": info.get("trailingPE", 0),

            "ROE": (
                info.get("returnOnEquity", 0) * 100
                if info.get("returnOnEquity")
                else 0
            ),

            "DebtEquity": info.get("debtToEquity", 0),

            "CurrentRatio": info.get("currentRatio", 0),

            "RevenueGrowth": (
                info.get("revenueGrowth", 0) * 100
                if info.get("revenueGrowth")
                else 0
            ),

            "MarketCapBillions": (
                info.get("marketCap", 0) / 1_000_000_000
            ),

            "Sector": info.get(
                "sector",
                "Unknown"
            )
        })

    except Exception as e:

        print(f"Error with {ticker}: {e}")

df = pd.DataFrame(rows)

df.to_csv(
    "stocks.csv",
    index=False
)

print("stocks.csv updated")
