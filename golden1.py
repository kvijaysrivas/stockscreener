import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# List of stocks (NSE symbols)
# -----------------------------
nifty_stocks = [ 
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", # Largecap 
    "LT.NS", "AXISBANK.NS", "BAJAJFINSV.NS", "ADANIPORTS.NS", "WIPRO.NS", # Midcap 
    "CROMPTON.NS", "SONATSOFTW.NS", "BALAMINES.NS", "KEI.NS", "POLYCAB.NS",
    "GILLETTE.NS", "BAJAJCON.NS", "SHK.NS", "TATACHEM.NS" # Smallcap 
]

# -----------------------------
# Function to check Golden Cross
# -----------------------------
def check_golden_cross(stock, recent_days, plot=False):
    try:
        data = yf.download(stock, period="1y", interval="1d", progress=False)
        if data.empty:
            return None

        # Moving averages
        data["SMA50"] = data["Close"].rolling(window=50).mean()
        data["SMA200"] = data["Close"].rolling(window=200).mean()
        data = data.dropna()

        # Identify crossover events
        data["cross"] = (data["SMA50"] > data["SMA200"]).astype(int)
        data["cross_shift"] = data["cross"].shift(1)

        cross_points = data[data["cross"] != data["cross_shift"]]

        if cross_points.empty:
            return None

        # Take the last crossover point
        last_cross_date = cross_points.index[-1]
        last_cross_type = cross_points["cross"].iloc[-1]  # 1 = Golden, 0 = Death

        # Must be golden cross (1)
        if last_cross_type != 1:
            return None

        # Must be within recent_days
        within_days = (data.index[-1] - last_cross_date).days <= recent_days

        # Must still be valid today
        valid_now = data["SMA50"].iloc[-1] > data["SMA200"].iloc[-1]

        if within_days and valid_now:
            if plot:
                plt.figure(figsize=(10, 5))
                plt.plot(data.index, data["Close"], label="Close Price", alpha=0.7)
                plt.plot(data.index, data["SMA50"], label="50-DMA")
                plt.plot(data.index, data["SMA200"], label="200-DMA")
                plt.axvline(last_cross_date, color="green", linestyle="--", label="Golden Cross")
                plt.title(f"Golden Crossover (Valid): {stock}")
                plt.legend()
                plt.show()
            return stock, last_cross_date.strftime("%Y-%m-%d")

    except Exception as e:
        print(f"Error for {stock}: {e}")
        return None

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    golden_stocks = []
    recent_days = 10  # only crossovers within last 30 days

    for stock in nifty_stocks:
        result = check_golden_cross(stock, recent_days=recent_days, plot=True)
        if result:
            golden_stocks.append(result)

    print("\n📌 Stocks with Golden Crossover (still valid, last", recent_days, "days):")
    if golden_stocks:
        for s, d in golden_stocks:
            print(f"{s} → crossover on {d}")
    else:
        print("None found")


