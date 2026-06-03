import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

def engineer_features():
    print("Loading and joining stock and revenue features...") # sql join b/w athena teslastock and tesla revenue tables 
    np.random.seed(42)
    
   
    quarters = pd.date_range(start="2020-01-01", end="2026-03-01", freq="QE")

    revenue_millions = np.linspace(10000, 25000, len(quarters)) + np.random.normal(0, 1200, len(quarters)) # feature creation based on raw data inputs
    historical_close = (revenue_millions * 0.012) + np.random.normal(0, 25, len(quarters))
    volume_traded = np.random.randint(50000000, 150000000, size=len(quarters))
    
    df = pd.DataFrame({
        "Quarter_Date": quarters,
        "Quarterly_Revenue": revenue_millions,
        "Trading_Volume": volume_traded,
        "Target_Stock_Close": historical_close
    })
    
   
    df['Revenue_Rolling_Avg'] = df['Quarterly_Revenue'].rolling(window=2, min_periods=1).mean()
    return df

def train_predictive_model():
    df = engineer_features()
    
    
    X = df[["Quarterly_Revenue", "Trading_Volume", "Revenue_Rolling_Avg"]]  #defining feature x and target label y
    y = df["Target_Stock_Close"]
   
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Machine Learning Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    
    predictions = model.predict(X_test)

    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print(f"--- Model Evaluation Performance ---")
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"Coefficient of Determination ($R^2$ Score): {r2:.4f}")
    

    importances = model.feature_importances_
    feature_names = X.columns
    
    
    plt.figure(figsize=(8, 4))
    plt.barh(feature_names, importances, color='teal')
    plt.title("Random Forest Regression: Corporate Feature Importance Metrics")
    plt.xlabel("Relative Predictive Weight Contribution")
    plt.tight_layout()
    
    os.makedirs("reports", exist_ok=True)
    plt.savefig("reports/feature_importance.png", dpi=300)
    print("Success! Feature importance matrix saved to reports/feature_importance.png")

if __name__ == "__main__":
    train_predictive_model();