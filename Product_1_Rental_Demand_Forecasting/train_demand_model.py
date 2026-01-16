import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.model_selection import TimeSeriesSplit
import pickle
import os
from datetime import datetime

def prepare_demand_data_with_external_factors():
    """
    Prepare data for the rental demand forecasting model with external factors.
    """
    print("Loading and preparing data for rental demand forecasting with external factors...")
    
    # Load the enhanced dataset
    enhanced_data_path = '/tmp/enhanced_rental_data_with_external_factors.csv'
    if not os.path.exists(enhanced_data_path):
        print(f"Error: Enhanced dataset not found at {enhanced_data_path}")
        print("Please run integrate_external_data.py first.")
        return None
    
    df = pd.read_csv(enhanced_data_path, low_memory=False)
    print(f"Loaded enhanced dataset with {len(df)} rows and {len(df.columns)} columns")
    
    # Convert 'Posted On' to datetime (handling mixed formats)
    df['Posted On'] = pd.to_datetime(df['Posted On'], errors='coerce')
    
    # Check for any rows where date conversion failed
    invalid_dates = df['Posted On'].isna().sum()
    if invalid_dates > 0:
        print(f"Warning: {invalid_dates} rows had invalid dates and will be dropped")
        df = df.dropna(subset=['Posted On'])
    
    # Extract temporal features
    df['Year'] = df['Posted On'].dt.year
    df['Month'] = df['Posted On'].dt.month
    df['Day'] = df['Posted On'].dt.day
    df['DayOfWeek'] = df['Posted On'].dt.dayofweek
    df['WeekOfYear'] = df['Posted On'].dt.isocalendar().week
    df['Quarter'] = df['Posted On'].dt.quarter
    
    # Aggregate by city and date for demand forecasting
    demand_df = df.groupby(['City', 'Posted On']).size().reset_index(name='Demand_Count')
    
    # Merge with external economic factors
    economic_factors = df[['City', 'Posted On', 'inflation_rate', 'interest_rate', 
                          'employment_rate', 'covid_impact_score', 'gdp_growth', 
                          'Economic_Health_Score']].drop_duplicates()
    
    demand_df = demand_df.merge(
        economic_factors,
        on=['City', 'Posted On'],
        how='left'
    )
    
    # Add temporal features to demand data
    demand_df['DayOfWeek'] = pd.to_datetime(demand_df['Posted On']).dt.dayofweek
    demand_df['Month'] = pd.to_datetime(demand_df['Posted On']).dt.month
    demand_df['Quarter'] = pd.to_datetime(demand_df['Posted On']).dt.quarter
    demand_df['IsWeekend'] = demand_df['DayOfWeek'].isin([5, 6]).astype(int)
    
    # Add lagged features
    demand_df = demand_df.sort_values(['City', 'Posted On'])
    for lag in [1, 7, 14]:
        demand_df[f'Demand_Lag_{lag}'] = demand_df.groupby('City')['Demand_Count'].shift(lag)
    
    # Add rolling features
    for window in [7, 14, 30]:
        demand_df[f'Demand_Rolling_Mean_{window}'] = demand_df.groupby('City')['Demand_Count'].transform(
            lambda x: x.rolling(window=window, min_periods=3).mean()
        )
        demand_df[f'Demand_Rolling_Std_{window}'] = demand_df.groupby('City')['Demand_Count'].transform(
            lambda x: x.rolling(window=window, min_periods=3).std()
        )
    
    # Create growth rate features
    demand_df['Growth_Rate_7'] = demand_df.groupby('City')['Demand_Count'].pct_change(periods=7)
    demand_df['Growth_Rate_7'] = demand_df['Growth_Rate_7'].fillna(0)
    
    # Add seasonal features
    demand_df['IsMonsoon'] = demand_df['Month'].isin([6, 7, 8, 9]).astype(int)
    demand_df['IsSummer'] = demand_df['Month'].isin([3, 4, 5]).astype(int)
    demand_df['IsWinter'] = demand_df['Month'].isin([11, 12, 1, 2]).astype(int)
    
    # Fill any remaining NaN values
    numeric_columns = demand_df.select_dtypes(include=[np.number]).columns
    demand_df[numeric_columns] = demand_df[numeric_columns].fillna(method='ffill').fillna(method='bfill')
    
    # Save prepared data
    output_path = '/tmp/enhanced_demand_forecast_data.csv'
    demand_df.to_csv(output_path, index=False)
    print(f"Prepared demand data saved to {output_path}")
    print(f"Shape: {demand_df.shape}")
    
    return demand_df

def train_demand_model():
    """
    Train a model to forecast rental demand with external factors.
    """
    print("Training enhanced rental demand forecasting model...")
    
    # Prepare data with external factors
    demand_df = prepare_demand_data_with_external_factors()
    if demand_df is None:
        return
    
    # Define features and target
    feature_cols = [
        'DayOfWeek', 'Month', 'Quarter', 'IsWeekend',
        'inflation_rate', 'interest_rate', 'employment_rate', 'covid_impact_score', 
        'gdp_growth', 'Economic_Health_Score',
        'Demand_Lag_1', 'Demand_Lag_7', 'Demand_Lag_14',
        'Demand_Rolling_Mean_7', 'Demand_Rolling_Mean_14', 'Demand_Rolling_Mean_30',
        'Demand_Rolling_Std_7', 'Demand_Rolling_Std_14', 'Demand_Rolling_Std_30',
        'Growth_Rate_7',
        'IsMonsoon', 'IsSummer', 'IsWinter'
    ]
    
    # Filter out rows with NaN values
    demand_df = demand_df.dropna(subset=feature_cols + ['Demand_Count'])
    
    X = demand_df[feature_cols]
    y = demand_df['Demand_Count']
    
    print(f"Training data shape: X={X.shape}, y={y.shape}")
    
    # Time series split for validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Model parameters
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'boosting_type': 'gbdt',
        'num_leaves': 63,
        'learning_rate': 0.05,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'min_data_in_leaf': 50,
        'lambda_l1': 0.1,
        'lambda_l2': 0.1,
        'verbose': -1
    }
    
    # Cross-validation
    cv_scores = []
    models = []
    
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        print(f"Training fold {fold+1}/5...")
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        # Create LightGBM datasets
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
        
        # Train model
        model = lgb.train(
            params,
            train_data,
            valid_sets=[val_data],
            num_boost_round=1000,
            callbacks=[lgb.early_stopping(stopping_rounds=50), lgb.log_evaluation(period=0)]
        )
        
        # Predictions
        y_pred = model.predict(X_val, num_iteration=model.best_iteration)
        
        # Metrics
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        mape = mean_absolute_percentage_error(y_val, y_pred)
        
        cv_scores.append({'fold': fold+1, 'rmse': rmse, 'mape': mape})
        models.append(model)
        
        print(f"Fold {fold+1}: RMSE = {rmse:.4f}, MAPE = {mape:.4f}")
    
    # Print CV results
    avg_rmse = np.mean([score['rmse'] for score in cv_scores])
    avg_mape = np.mean([score['mape'] for score in cv_scores])
    
    print(f"\nCross-validation Results:")
    print(f"Average RMSE: {avg_rmse:.4f}")
    print(f"Average MAPE: {avg_mape:.4f}")
    
    # Select the best model based on CV scores
    best_idx = np.argmin([score['rmse'] for score in cv_scores])
    best_model = models[best_idx]
    
    # Save the best model
    model_path = '/tmp/enhanced_demand_forecast_model.txt'
    best_model.save_model(model_path)
    print(f"Best model saved to {model_path}")
    
    # Save the model features for later use
    features_path = '/tmp/demand_forecast_features.pkl'
    with open(features_path, 'wb') as f:
        pickle.dump(feature_cols, f)
    print(f"Feature list saved to {features_path}")

if __name__ == "__main__":
    train_demand_model()