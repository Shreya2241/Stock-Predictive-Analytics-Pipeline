import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pyathena import connect

def load_data():
    print("Connecting to Amazon Athena to fetch live TSLA stock data...")
    
    
    conn = connect(
        s3_staging_dir="s3://shreya-stock-pipeline-analytics/athena-query-results/",
        region_name="us-east-1" 
    )
    
   
    query = """                  
    SELECT Date, Close 
    FROM market_analysis_db.tesla_stock 
    ORDER BY Date ASC;
    """
    
   
    df = pd.read_sql(query, conn)
    
  
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index("Date", inplace=True)
    
    df_weekly = df.resample('W').last()
    
    return df_weekly

def run_forecasting():
    df = load_data()
    
    print("Training Weekly SARIMAX Time-Series Model...")
    model = SARIMAX(df['Close'], order=(1, 1, 1), enforce_stationarity=False, enforce_invertibility=False)
    results = model.fit(disp=False)
    

    current_date = df.index[-1]
    end_of_year = pd.Timestamp("2026-12-31")
    
   
    forecast_steps = int(np.ceil((end_of_year - current_date).days / 7))
    print(f"Generating {forecast_steps} weekly (7-day) interval forecast steps until the end of 2026...")
    
    forecast_object = results.get_forecast(steps=forecast_steps)
    forecast_mean = forecast_object.predicted_mean
    confidence_intervals = forecast_object.conf_int()
    

    future_dates = pd.date_range(start=current_date + pd.Timedelta(weeks=1), periods=forecast_steps, freq="W")
    forecast_mean.index = future_dates
    confidence_intervals.index = future_dates
    
    
    plt.figure(figsize=(12, 6))
    plt.plot(df.index[-52:], df['Close'].tail(52), label="Historical Weekly Close (Past Year)", color="#1f77b4", linewidth=2, marker='o', markersize=4)
    
  
    plt.plot(future_dates, forecast_mean, label="Weekly Interval Forecast (Till End of 2026)", color="#2ca02c", linestyle="--", marker="s", linewidth=2)
    
    plt.fill_between(future_dates, confidence_intervals.iloc[:, 0], confidence_intervals.iloc[:, 1], color='#2ca02c', alpha=0.15, label="95% Confidence Interval")
    
    
    plt.title("TSLA Asset Valuation Lifecycle: Macro 7-Day Interval Forecast (Horizon: Dec 2026)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Timeline Year Horizon", fontsize=11, labelpad=10)
    plt.ylabel("Asset Share Price ($)", fontsize=11, labelpad=10)
    plt.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="none")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.xticks(rotation=15)
    plt.tight_layout()
    

    os.makedirs("reports", exist_ok=True)
    plt.savefig("reports/time_series_forecast.png", dpi=300)
    print("Success! Macro weekly interval forecast chart saved to reports/time_series_forecast.png")

if __name__ == "__main__":
    run_forecasting()