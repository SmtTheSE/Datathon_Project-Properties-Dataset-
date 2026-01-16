import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.model_selection import TimeSeriesSplit
import pickle
import os
from datetime import datetime

def train_demand_model_v2():
    """
    Train V2 model including 'Customer Behavior' features.
    This demonstrates the model's ability to adapt to new datasets.
    """
    print("🚀 Starting V2 Model Training (with Customer Behavior)...")
    
    # 1. Load the Integrated Data
    data_path = 'output/final_round/rental_data_with_customer_behavior.csv'
    if not os.path.exists(data_path):
        print(f"❌ Error: Integrated dataset not found at {data_path}")
        print("Please run scripts/integrate_customer_behavior.py first.")
        return

    print(f"Loading integrated data from {data_path}...")
    df = pd.read_csv(data_path, low_memory=False)
    
    # Standardize Date
    df['Posted On'] = pd.to_datetime(df['Posted On'], errors='coerce')
    df = df.dropna(subset=['Posted On'])
    
    # 2. Add Temporal Features (same as V1)
    df['Year'] = df['Posted On'].dt.year
    df['Month'] = df['Posted On'].dt.month
    df['DayOfWeek'] = df['Posted On'].dt.dayofweek
    df['Quarter'] = df['Posted On'].dt.quarter
    df['IsWeekend'] = df['DayOfWeek'].isin([5, 6]).astype(int)
    
    # 3. Aggregate for Daily Demand Forecasting
    # We aggregate by City + Date, but we need to aggregated the NEW features as well
    # Since new features are at Locality level, we aggregated them up to City level for this specific model
    # OR we can train a Locality-Level Demand Model. 
    # For V2 compatibility with V1, let's keep it City-Level but include weighted average of customer interest.
    
    print("Aggregating data for daily demand forecasting...")
    
    # Base demand count
    daily_stats = df.groupby(['City', 'Posted On']).size().reset_index(name='Demand_Count')
    
    # Aggregate new Customer Behavior features (Mean/Sum per day per city)
    # Note: These features are static per locality in our mock, but in real life they would be time-series.
    # For the mock, we just take the mean of the localities active on that day.
    
    customer_features = [
        'Locality_Search_Volume', 'Locality_Contacts', 'Locality_Views', 
        'View_to_Contact_Ratio', 'High_Demand_Flag'
    ]
    
    # Check if columns exist (safety)
    existing_cust_features = [c for c in customer_features if c in df.columns]
    
    if existing_cust_features:
        daily_behavior = df.groupby(['City', 'Posted On'])[existing_cust_features].mean().reset_index()
        daily_stats = daily_stats.merge(daily_behavior, on=['City', 'Posted On'], how='left')
    
    
    # 4. Feature Engineering (Lags & Rolling)
    # FIRST: Re-generate temporal features for the AGGREGATED dataframe
    daily_stats['Posted On'] = pd.to_datetime(daily_stats['Posted On'])
    daily_stats['Month'] = daily_stats['Posted On'].dt.month
    daily_stats['DayOfWeek'] = daily_stats['Posted On'].dt.dayofweek
    daily_stats['Quarter'] = daily_stats['Posted On'].dt.quarter
    daily_stats['IsWeekend'] = daily_stats['DayOfWeek'].isin([5, 6]).astype(int)
    
    daily_stats = daily_stats.sort_values(['City', 'Posted On'])
    
    for lag in [1, 7]:
        daily_stats[f'Demand_Lag_{lag}'] = daily_stats.groupby('City')['Demand_Count'].shift(lag)
        
    for window in [7, 14]:
        daily_stats[f'Demand_Rolling_Mean_{window}'] = daily_stats.groupby('City')['Demand_Count'].transform(
            lambda x: x.rolling(window=window, min_periods=3).mean()
        )
    
    # 5. Define Feature Columns for Training
    # We mix original temporal features with NEW Customer Behavior features
    feature_cols = [
        'DayOfWeek', 'Month', 'Quarter', 'IsWeekend',
        'Demand_Lag_1', 'Demand_Lag_7',
        'Demand_Rolling_Mean_7', 'Demand_Rolling_Mean_14'
    ] + existing_cust_features
    
    print(f"Training with Features: {feature_cols}")
    
    # Clean NaNs
    daily_stats = daily_stats.dropna(subset=feature_cols + ['Demand_Count'])
    
    X = daily_stats[feature_cols]
    y = daily_stats['Demand_Count']
    
    # 6. Train LightGBM Model
    print(f"Training on {len(X)} rows...")
    
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'verbosity': -1,
        'learning_rate': 0.05,
        'num_leaves': 31
    }
    
    # Simple split for demo
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]
    
    train_data = lgb.Dataset(X_train, label=y_train)
    val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
    
    model = lgb.train(
        params,
        train_data,
        valid_sets=[val_data],
        num_boost_round=100,
        callbacks=[lgb.log_evaluation(period=20)]
    )
    
    # 7. Evaluate
    y_pred = model.predict(X_val)
    rmse = np.sqrt(mean_squared_error(y_val, y_pred))
    print(f"\n✅ V2 Model Trained Successfully!")
    print(f"RMSE: {rmse:.4f}")
    
    # Check feature importance
    print("\nFeature Importance:")
    importance = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': model.feature_importance()
    }).sort_values('Importance', ascending=False)
    print(importance.head(10))
    
    # 8. Save V2 Model
    output_dir = 'output/models_v2'
    os.makedirs(output_dir, exist_ok=True)
    model.save_model(os.path.join(output_dir, 'demand_model_v2.txt'))
    print(f"\n💾 Model saved to: {output_dir}/demand_model_v2.txt")

if __name__ == "__main__":
    train_demand_model_v2()
