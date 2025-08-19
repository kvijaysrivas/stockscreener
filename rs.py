
import matplotlib
matplotlib.use('Agg')  # use non-GUI backend
import yfinance as yf
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import os

# ---------- SETTINGS ----------
START_DATE = "2024-01-01"
END_DATE = datetime.datetime.today().strftime('%Y-%m-%d')
RS_SMA_WINDOW = 50   # can change to 20 or 200
SAVE_CHARTS = True   # if True, saves charts as PNG

# ---------- BENCHMARK ----------
BENCHMARK_SYMBOL = "^NSEI"  # Nifty 50
benchmark_data = yf.download(
    BENCHMARK_SYMBOL,
    start=START_DATE,
    end=END_DATE,
    auto_adjust=True
)['Close']

# ---------- STOCK SYMBOLS ----------
stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS','BANKBARODA.NS',
          'TATAMOTORS.NS', 'RELINFRA.NS','AJANTPHARM.NS','HINDCOPPER.NS','ASHOKLEY.NS']

# ---------- INDEX SYMBOLS ----------
indices = {
    "Nifty Bank": "^NSEBANK",
    "Nifty IT": "^CNXIT",
    "Nifty Auto": "^CNXAUTO",
    "Nifty FMCG": "^CNXFMCG",
    "Nifty Pharma": "^CNXPHARMA",
    "Nifty Infra": "^CNXINFRA",
    "Nifty Metal": "^CNXMETAL"
}

# ---------- FUNCTION TO CALCULATE RELATIVE STRENGTH ----------
def calculate_relative_strength(name, symbol, benchmark_series, plot=False):
    try:
        data = yf.download(
            symbol,
            start=START_DATE,
            end=END_DATE,
            auto_adjust=True
        )['Close']
        
        combined = pd.concat([data, benchmark_series], axis=1)
        combined.columns = ['Price', 'Benchmark']
        combined.dropna(inplace=True)

        combined['Price_Ratio'] = combined['Price'] / combined['Benchmark']
        combined['SMA'] = combined['Price_Ratio'].rolling(window=RS_SMA_WINDOW).mean()
        combined['Above_SMA'] = combined['Price_Ratio'] > combined['SMA']
        combined['Crossover'] = (combined['Above_SMA'] == True) & (combined['Above_SMA'].shift(1) == False)

        latest = combined.iloc[-1]

        # ----- Plotting -----
        if plot:
            plt.figure(figsize=(10,5))
            plt.plot(combined.index, combined['Price_Ratio'], label="RS (Stock / Nifty)", color='blue')
            plt.plot(combined.index, combined['SMA'], label=f"RS {RS_SMA_WINDOW}-day SMA", color='orange')
            
            # Mark crossovers
            cross_points = combined[combined['Crossover'] == True]
            plt.scatter(cross_points.index, cross_points['Price_Ratio'], color='green', marker='^', label='Breakout', s=80)

            plt.title(f"{name} ({symbol}) - Relative Strength vs Nifty")
            plt.xlabel("Date")
            plt.ylabel("Relative Strength")
            plt.legend()
            plt.grid(True)

            if SAVE_CHARTS:
                os.makedirs("charts", exist_ok=True)
                plt.savefig(f"charts/{name}_{symbol}.png")
                plt.close()
            else:
                plt.show()

        return {
            'name': name,
            'symbol': symbol,
            'rs_value': latest['Price_Ratio'],
            'above_sma': bool(latest['Above_SMA']),
            'crossover': bool(latest['Crossover'])
        }
    except Exception as e:
        print(f"⚠️ Error with {name} ({symbol}): {e}")
        return None

# ---------- ANALYSIS RUNNER ----------
def run_analysis():
    print("\n🔍 Checking STOCKS vs NIFTY RS:")
    stock_results = [calculate_relative_strength(sym, sym, benchmark_data, plot=True) for sym in stocks]
    stock_results = [res for res in stock_results if res]
    stock_results = sorted(stock_results, key=lambda x: x['rs_value'], reverse=True)

    for res in stock_results:
        status = "Breakout" if res['crossover'] else ("Above SMA" if res['above_sma'] else "Below SMA")
        print(f"{res['name']:15} | RS={res['rs_value']:.3f} | {status}")

    print("\n📊 Checking SECTOR INDICES vs NIFTY RS:")
    index_results = [calculate_relative_strength(name, symbol, benchmark_data, plot=True) for name, symbol in indices.items()]
    index_results = [res for res in index_results if res]
    index_results = sorted(index_results, key=lambda x: x['rs_value'], reverse=True)

    for res in index_results:
        status = "Breakout" if res['crossover'] else ("Above SMA" if res['above_sma'] else "Below SMA")
        print(f"{res['name']:15} | RS={res['rs_value']:.3f} | {status}")

    # Export to Excel
    df_stocks = pd.DataFrame(stock_results)
    df_indices = pd.DataFrame(index_results)
    with pd.ExcelWriter("RS_Ranking.xlsx") as writer:
        df_stocks.to_excel(writer, sheet_name="Stocks", index=False)
        df_indices.to_excel(writer, sheet_name="Indices", index=False)
    print("\n✅ Results exported to RS_Ranking.xlsx")
    print("📈 Charts saved in /charts folder")

# ---------- MAIN ----------
if __name__ == "__main__":
    run_analysis()


