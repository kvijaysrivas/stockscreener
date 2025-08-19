import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# Step 1: Define NIFTY 500 Stock List (sample subset here)
nifty500_stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS",
    "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "ITC.NS", "LT.NS", "AXISBANK.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "BAJFINANCE.NS", "HCLTECH.NS", "WIPRO.NS", "SUNPHARMA.NS",
    "ULTRACEMCO.NS", "TITAN.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ADANIPOWER.NS",
    "POWERGRID.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "GRASIM.NS", "HDFCLIFE.NS", "ONGC.NS",
    "COALINDIA.NS", "NTPC.NS", "BAJAJFINSV.NS", "TECHM.NS", "BRITANNIA.NS", "CIPLA.NS",
    "DRREDDY.NS", "DIVISLAB.NS", "HAVELLS.NS", "EICHERMOT.NS", "M&M.NS", "HEROMOTOCO.NS",
    "SHREECEM.NS", "BPCL.NS", "IOC.NS", "INDUSINDBK.NS", "VEDL.NS", "DMART.NS",
]

# Step 2: Download 2 years of price data
end = datetime.datetime.today()
start = end - datetime.timedelta(days=730)

# ✅ FIX: Use "Close" instead of "Adj Close"
data = yf.download(nifty500_stocks, start=start, end=end)['Close']

# Step 3: Calculate Momentum (12-month return excluding last 1 month)
momentum_scores = {}
for stock in data.columns:
    prices = data[stock].dropna()
    if len(prices) > 252:  # Ensure enough data
        past_12m = prices[-252:]      # Last 12 months
        past_1m = prices[-21:]        # Last 1 month
        momentum_return = (past_12m[-22] / past_12m[0]) - 1  # 12m return
        last_month_return = (past_1m[-1] / past_1m[0]) - 1   # 1m return
        final_momentum = momentum_return - last_month_return # As per book
        momentum_scores[stock] = final_momentum

# Step 4: Rank Stocks by Momentum
momentum_df = pd.DataFrame(momentum_scores.items(), columns=['Stock', 'Momentum'])
momentum_df = momentum_df.sort_values(by='Momentum', ascending=False).reset_index(drop=True)

# Step 5: Select Top 20 Momentum Stocks
top_stocks = momentum_df.head(20)

# Output
print("📈 Top 20 Quantitative Momentum Stocks (NIFTY 500):")
print(top_stocks)

# Save to CSV
top_stocks.to_csv("top_momentum_nifty500.csv", index=False)


# Save to CSV
top_stocks.to_csv("top_momentum_nifty500.csv", index=False)
