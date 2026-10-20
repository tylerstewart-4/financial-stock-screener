import pandas as pd
import random

tickers = pd.read_csv("tickers.csv")

data = []

for ticker in tickers["Ticker"]:

    data.append({
        "Ticker": ticker,
        "PE": random.randint(10, 80),
        "ROE": random.randint(5, 45),
        "DebtEquity": round(random.uniform(0, 3), 2),
        "FScore": random.randint(3, 9),
        "CurrentRatio": round(random.uniform(0.5, 4), 2),
        "RevenueGrowth": random.randint(-5, 40),
        "MarketCapBillions": random.randint(1, 3500),
        "Sector": "Unknown"
    })

df = pd.DataFrame(data)

df.to_csv("stocks.csv", index=False)

print("stocks.csv generated!")
