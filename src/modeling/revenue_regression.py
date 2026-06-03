import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

def engineer_features():
    """
    Simulates a SQL JOIN between your Athena 'tesla_stock' and 'tesla_revenue' tables,
    then executes data science feature engineering.
    """
    print("Loading and joining stock and revenue features...")
    np.random.seed(42)
    
    # Mocking a clean dataset mirroring your Athena SQL JOIN result
    quarters = pd.date_range(start="2020-01-01", end="2026-03-01", freq="QE")
    
    # Feature Engineering: Creating features based on raw data inputs
    revenue_millions = np.linspace(10000, 25000, len(quarters)) + np.random.normal(0, 1200, len(quarters))
    historical_close = (revenue_millions * 0.012) + np.random.normal(0, 25, len(quarters))
    volume_traded = np.random.randint(50000000, 150000000, size=len(quarters))
    
    df = pd.DataFrame({
        "Quarter_Date": quarters,
        "Quarterly_Revenue": revenue_millions,
        "Trading_Volume": volume_traded,
        "Target_Stock_Close": historical_close
    })
    
    # Advance Feature: Rolling average of revenue to catch business acceleration trends
    df['Revenue_Rolling_Avg'] = df['Quarterly_Revenue'].rolling(window=2, min_periods=1).mean()
    return df

def train_predictive_model():
    df = engineer_features()
    
    # Define features (X) and target label (y)
    X = df[["Quarterly_Revenue", "Trading_Volume", "Revenue_Rolling_Avg"]]
    y = df["Target_Stock_Close"]
    
    # Data Split: 80% Training dataset to teach the model, 20% Testing dataset to validate it
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Machine Learning Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Run evaluation predictions
    predictions = model.predict(X_test)
    
    # Compute classic data science evaluation metrics
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print(f"--- Model Evaluation Performance ---")
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"Coefficient of Determination ($R^2$ Score): {r2:.4f}")
    
    # Feature Importance: Show which variables matter most to the model
    importances = model.feature_importances_
    feature_names = X.columns
    
    # Save Feature Importance visual to your GitHub portfolio reports folder
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