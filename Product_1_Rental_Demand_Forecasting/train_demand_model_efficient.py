"""
Efficient Production-Ready Demand Forecasting Model
Trains quickly with optimized parameters for production use
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import joblib
import warnings
import os
import json
from datetime import datetime
warnings.filterwarnings('ignore')

def load_sample_data():
    """Load a representative sample of the data for faster training"""
    print("Loading sample data for efficient training...")
    
    # Check if the enhanced data file exists
    data_path = '/tmp/enhanced_demand_forecasting_data.csv'
    
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        print(f"Full dataset shape: {df.shape}")
        
        # If dataset is large, use a sample for training
        if len(df) > 10000:
            # Sort by date to ensure we preserve time series order
            df = df.sort_values('Posted On').reset_index(drop=True)
            # Take the most recent 10,000 rows to ensure we have the latest patterns
            df = df.iloc[-10000:].copy()
            print(f"Using most recent {len(df)} rows for training to preserve time series")
    else:
        # Create a small sample dataset if the file doesn't exist
        print("Enhanced data file not found, creating sample data for demonstration...")
        n_samples = 5000
        
        # Create sample data
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 
                  'Pune', 'Ahmedabad', 'Jaipur', 'Surat']
        
        # Generate dates properly
        date_range = pd.date_range(start='2020-01-01', end='2022-12-31', freq='D')
        dates = np.random.choice(date_range, n_samples)
        
        df = pd.DataFrame({
            'City': np.random.choice(cities, n_samples),
            'Posted On': dates,
            'Demand_Count': np.random.poisson(2500, n_samples),  # Use Poisson for count data
            'inflation_rate': np.random.uniform(2, 8, n_samples),
            'interest_rate': np.random.uniform(5, 12, n_samples),
            'employment_rate': np.random.uniform(70, 90, n_samples),
            'covid_impact_score': np.random.uniform(0, 1, n_samples),
            'Economic_Health_Score': np.random.uniform(0.5, 1.0, n_samples),
        })

        
        # Extract temporal features
        df['Posted On'] = pd.to_datetime(df['Posted On'])
        df['Year'] = df['Posted On'].dt.year
        df['Month'] = df['Posted On'].dt.month
        
        # Add seasonal features
        df['Month_Sin'] = np.sin(2 * np.pi * df['Month'] / 12)
        df['Month_Cos'] = np.cos(2 * np.pi * df['Month'] / 12)
    
    return df

def prepare_features(df):
    """Prepare features for demand forecasting"""
    print("Preparing features...")
    
    # Define feature columns
    feature_cols = [
        'Year', 'Month', 
        'inflation_rate', 'interest_rate', 'employment_rate', 
        'covid_impact_score', 'Economic_Health_Score',
        'Month_Sin', 'Month_Cos'
    ]
    
    # Add lag features if available
    lag_cols = [col for col in df.columns if 'Lag' in col]
    feature_cols.extend(lag_cols)
    
    # Add rolling features if available
    roll_cols = [col for col in df.columns if 'Rolling' in col]
    feature_cols.extend(roll_cols)
    
    # Remove columns that might not exist
    feature_cols = [col for col in feature_cols if col in df.columns]
    
    # Handle missing values
    df = df.fillna(df.median(numeric_only=True))
    
    # Encode categorical features if any
    categorical_cols = ['City']
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
            feature_cols.append(f'{col}_encoded')
    
    X = df[feature_cols]
    y = df['Demand_Count']
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y, feature_cols, scaler

def train_efficient_model():
    """Train an efficient demand forecasting model"""
    print("Training efficient demand forecasting model...")
    
    # Load data
    df = load_sample_data()
    
    # Prepare features
    X, y, feature_cols, scaler = prepare_features(df)
    
    # Use TimeSeriesSplit for realistic validation on time series data
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Perform cross-validation
    cv_scores = []
    models = []
    
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        print(f"Training fold {fold+1}/5...")
        X_train_fold, X_val_fold = X[train_idx], X[val_idx]
        y_train_fold, y_val_fold = y.iloc[train_idx], y.iloc[val_idx]
        
        # Train a simpler, faster model
        model = RandomForestRegressor(
            n_estimators=50,        # Reduced for speed
            max_depth=10,           # Limited depth to prevent overfitting
            min_samples_split=10,   # Higher to prevent overfitting
            min_samples_leaf=5,     # Higher to prevent overfitting
            random_state=42,
            n_jobs=-1               # Use all cores
        )
        
        model.fit(X_train_fold, y_train_fold)
        
        # Make predictions
        y_pred_train = model.predict(X_train_fold)
        y_pred_val = model.predict(X_val_fold)
        
        # Calculate metrics
        train_mae = mean_absolute_error(y_train_fold, y_pred_train)
        val_mae = mean_absolute_error(y_val_fold, y_pred_val)
        train_rmse = np.sqrt(mean_squared_error(y_train_fold, y_pred_train))
        val_rmse = np.sqrt(mean_squared_error(y_val_fold, y_pred_val))
        train_r2 = r2_score(y_train_fold, y_pred_train)
        val_r2 = r2_score(y_val_fold, y_pred_val)
        
        cv_scores.append({
            'fold': fold+1,
            'train_mae': train_mae,
            'val_mae': val_mae,
            'train_rmse': train_rmse,
            'val_rmse': val_rmse,
            'train_r2': train_r2,
            'val_r2': val_r2
        })
        
        models.append(model)
        print(f"Fold {fold+1}: Train MAE: {train_mae:.2f}, Val MAE: {val_mae:.2f}")
    
    # Select the best model based on validation MAE
    best_idx = np.argmin([score['val_mae'] for score in cv_scores])
    model = models[best_idx]
    
    # For final evaluation, we'll use a simple train-test split with time-awareness
    # Reserve last 20% of data for testing to simulate real-world scenario
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # Retrain the best model on the training set for final evaluation
    model = RandomForestRegressor(
        n_estimators=50,        # Reduced for speed
        max_depth=10,           # Limited depth to prevent overfitting
        min_samples_split=10,   # Higher to prevent overfitting
        min_samples_leaf=5,     # Higher to prevent overfitting
        random_state=42,
        n_jobs=-1               # Use all cores
    )
    
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Calculate metrics
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    print(f"Training MAE: {train_mae:.2f}")
    print(f"Testing MAE: {test_mae:.2f}")
    print(f"Training RMSE: {train_rmse:.2f}")
    print(f"Testing RMSE: {test_rmse:.2f}")
    print(f"Training R²: {train_r2:.4f}")
    print(f"Testing R²: {test_r2:.4f}")
    
    # Calculate cross-validation averages
    avg_val_mae = np.mean([score['val_mae'] for score in cv_scores])
    avg_val_rmse = np.mean([score['val_rmse'] for score in cv_scores])
    print(f"Average CV Validation MAE: {avg_val_mae:.2f}")
    print(f"Average CV Validation RMSE: {avg_val_rmse:.2f}")
    
    # Save the model and scaler
    joblib.dump(model, 'demand_forecast_model_efficient.pkl')
    joblib.dump(scaler, 'feature_scaler_efficient.pkl')
    print("Model and scaler saved successfully!")
    
    # Save metrics to JSON file for API consumption
    metrics_data = {
        "model_name": "Demand Forecast Model (Efficient)",
        "model_version": "3.0.0",
        "training_date": datetime.now().isoformat(),
        "data_size": {
            "total_samples": len(X),
            "training_samples": len(X_train),
            "testing_samples": len(X_test)
        },
        "metrics": {
            "train_mae": round(float(train_mae), 6),
            "test_mae": round(float(test_mae), 6),
            "train_rmse": round(float(train_rmse), 6),
            "test_rmse": round(float(test_rmse), 6),
            "train_r2": round(float(train_r2), 6),
            "test_r2": round(float(test_r2), 6),
            "cv_avg_val_mae": round(float(avg_val_mae), 6),
            "cv_avg_val_rmse": round(float(avg_val_rmse), 6)
        },
        "cross_validation": {
            "n_splits": 5,
            "fold_scores": [
                {
                    "fold": score['fold'],
                    "train_mae": round(float(score['train_mae']), 6),
                    "val_mae": round(float(score['val_mae']), 6),
                    "train_rmse": round(float(score['train_rmse']), 6),
                    "val_rmse": round(float(score['val_rmse']), 6),
                    "train_r2": round(float(score['train_r2']), 6),
                    "val_r2": round(float(score['val_r2']), 6)
                }
                for score in cv_scores
            ]
        },
        "model_parameters": {
            "n_estimators": 50,
            "max_depth": 10,
            "min_samples_split": 10,
            "min_samples_leaf": 5
        },
        "features": feature_cols
    }
    
    with open('model_metrics.json', 'w') as f:
        json.dump(metrics_data, f, indent=2)
    print("Metrics saved to model_metrics.json")
    
    return model, scaler, feature_cols

def main():
    """Main function to train the efficient model"""
    print("Starting efficient demand forecasting model training...")
    model, scaler, feature_cols = train_efficient_model()
    print("Model training completed successfully!")
    print(f"Features used: {feature_cols}")

if __name__ == "__main__":
    main()