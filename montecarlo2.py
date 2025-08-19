import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# ---------------------------
# 1) Download stock data
# ---------------------------
ticker = "HSCL.NS"
data = yf.download(ticker, start="2013-01-01", end="2025-07-31", auto_adjust=True)
data = data['Close']  # This will be a Series

# Calculate daily returns
daily_returns = data.pct_change().dropna()

# ---------------------------
# 2) Simulation parameters
# ---------------------------
num_simulations = 1000
num_years = 5
num_days = 252 * num_years  # 3 trading years

last_price = float(data.iloc[-1])
mu = float(daily_returns.mean())      # Convert Series mean to float safely
sigma = float(daily_returns.std())    # Convert Series std to float safely

dt = 1 / 252

print(f"Data fetched successfully. Last price: ₹{last_price:.2f}")
print(f"Mean daily return: {mu:.6f}")
print(f"Daily volatility: {sigma:.6f}")
print(f"Simulating {num_simulations} paths for {num_years} years ({num_days} days)...")

# ---------------------------
# 3) Monte Carlo Simulation using GBM
# ---------------------------
simulations = np.zeros((num_days, num_simulations))

for i in range(num_simulations):
    prices = np.zeros(num_days)
    prices[0] = last_price
    for t in range(1, num_days):
        z = np.random.standard_normal()
        prices[t] = prices[t - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z)
    simulations[:, i] = prices

print("Simulations completed.")
# 3) Monte Carlo Simulation using GBM
# ---------------------------
simulations = np.zeros((num_days, num_simulations))

for i in range(num_simulations):
    prices = np.zeros(num_days)
    prices[0] = last_price
    for t in range(1, num_days):
        z = np.random.standard_normal()
        prices[t] = prices[t - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z)
    simulations[:, i] = prices

print("Simulations completed.")

# Add probability calculation for hitting a target price
target_price = 70  # Replace with your desired target price

# `simulations` has shape (num_days, num_simulations)
# We transpose to get (num_simulations, num_days) for easier iteration
simulations_T = simulations.T  # shape: (num_simulations, num_days)

# Check whether in any day the price crosses the target
hits = np.any(simulations_T >= target_price, axis=1)

# Calculate probability as fraction of simulations hitting the target
probability_of_hitting = np.mean(hits)

print(f"Probability of hitting or exceeding ₹{target_price}: {probability_of_hitting * 100:.2f}%")

# ---------------------------
# 4) Probabilistic Forecast at Final Day
# ---------------------------
final_prices = simulations[-1, :]
percentiles = np.percentile(final_prices, [5, 25, 50, 75, 95])

print(f"\nProbabilistic Forecast for {ticker} after {num_years} Years:")
print(f"5th Percentile: ₹{percentiles[0]:.2f}")
print(f"25th Percentile: ₹{percentiles[1]:.2f}")
print(f"Median (50th): ₹{percentiles[2]:.2f}")
print(f"75th Percentile: ₹{percentiles[3]:.2f}")
print(f"95th Percentile: ₹{percentiles[4]:.2f}")

# Save forecast results to CSV
forecast_df = pd.DataFrame({
    "Percentile": ["5%", "25%", "50%", "75%", "95%"],
    "Final Price": percentiles
})
forecast_df.to_csv(f"forecast_{ticker}.csv", index=False)
pd.DataFrame({"Final Prices": final_prices}).to_csv(f"final_prices_{ticker}.csv", index=False)
print(f"Forecast and final prices saved to forecast_{ticker}.csv and final_prices_{ticker}.csv.")

# ---------------------------
# 5) Plot simulation paths with percentile bands
# ---------------------------
plt.figure(figsize=(14, 7))

# Plot all simulation paths WITHOUT adding them to the legend
plt.plot(simulations, linewidth=0.5, alpha=0.6, color='lightgrey')

# Add a dummy line for the legend
plt.plot([], [], linewidth=0.5, color='lightgrey', label='Simulations')

# Calculate percentiles across time for bands
time_percentiles = np.percentile(simulations, [5, 50, 95], axis=1)
days = np.arange(num_days)

plt.plot(days, time_percentiles[0, :], color='red', label='5th Percentile')
plt.plot(days, time_percentiles[1, :], color='black', label='Median (50th)')
plt.plot(days, time_percentiles[2, :], color='green', label='95th Percentile')
plt.fill_between(days, time_percentiles[0, :], time_percentiles[2, :], color='gray', alpha=0.2, label='5%-95% Band')

plt.title(f"Monte Carlo Simulation (GBM) - {ticker} Stock Price for {num_years} Years")
plt.xlabel("Day")
plt.ylabel("Simulated Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.subplots_adjust(top=0.88)

try:
    plt.show()
except Exception as e:
    print(f"Plot closed early, continuing without error: {e}")

# ---------------------------
# 6) Histogram of final prices
# ---------------------------
plt.figure(figsize=(10, 5))
plt.hist(final_prices, bins=50, color='skyblue', edgecolor='black')
plt.title(f"Distribution of Final Prices after {num_years} Years ({ticker})")
plt.xlabel("Final Price")
plt.ylabel("Frequency")
plt.grid(True)
plt.tight_layout()

try:
    plt.show()
except Exception as e:
    print(f"Plot closed early, continuing without error: {e}")
