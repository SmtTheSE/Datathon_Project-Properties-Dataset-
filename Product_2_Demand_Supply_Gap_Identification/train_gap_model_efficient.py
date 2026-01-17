"""
Efficient Production-Ready Gap Analysis Model
Trains quickly with optimized parameters for production use
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_sample_data():
    """Load a representative sample of the data for faster training"""
    print("Loading sample data for efficient training...")
    
    # Check if the enhanced data file exists
    data_path = '/tmp/enhanced_gap_analysis_data.csv'
    
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
            'Area Locality': [f'Area_{i%50}' for i in range(n_samples)],
            'BHK': np.random.choice([1, 2, 3, 4], n_samples),
            'Posted On': dates,
            'Rent': np.random.normal(25000, 10000, n_samples).clip(5000, 100000),
            'inflation_rate': np.random.uniform(2, 8, n_samples),
            'interest_rate': np.random.uniform(5, 12, n_samples),
            'employment_rate': np.random.uniform(70, 90, n_samples),
            'covid_impact_score': np.random.uniform(0, 1, n_samples),
            'Economic_Health_Score': np.random.uniform(0.5, 1.0, n_samples),
        })
        
        # Create gap-related features
        df['Avg_Rent'] = df.groupby(['City', 'Area Locality', 'BHK'])['Rent'].transform('mean')
        df['Std_Rent'] = df.groupby(['City', 'Area Locality', 'BHK'])['Rent'].transform('std').fillna(0)
        df['Supply'] = np.random.poisson(50, n_samples)  # Simulate supply counts
        
        # Calculate demand as a function of rent, economic factors, and city popularity
        df['Demand_Factor'] = (
            (df['Avg_Rent'] / df['Avg_Rent'].mean()) * 0.3 +
            (df['employment_rate'] / 100) * 0.3 +
            (df['Economic_Health_Score']) * 0.2 +
            np.random.normal(1.0, 0.1, size=n_samples) * 0.2  # Add some randomness
        ).clip(lower=0.1)
        
        df['Demand_Count'] = df['Supply'] * df['Demand_Factor']
        
        # Calculate gap metrics
        df['Gap_Ratio'] = (df['Demand_Count'] - df['Supply']) / (df['Supply'] + 1)
        
        # Add geographic features
        city_tiers = {
            'Mumbai': 'Tier1', 'Delhi': 'Tier1', 'Bangalore': 'Tier1', 'Hyderabad': 'Tier1',
            'Chennai': 'Tier1', 'Kolkata': 'Tier1', 'Pune': 'Tier1', 'Ahmedabad': 'Tier1',
            'Jaipur': 'Tier2', 'Surat': 'Tier2'
        }
        
        df['City_Tier'] = df['City'].map(city_tiers).fillna('Tier3')
        df['Region'] = df['City'].apply(lambda x: 'West' if x in ['Mumbai', 'Pune', 'Ahmedabad'] else 
                                               'North' if x in ['Delhi', 'Jaipur'] else 
                                               'South' if x in ['Bangalore', 'Chennai', 'Hyderabad'] else 'Other')
    
    return df

def prepare_features(df):
    """Prepare features for gap analysis"""
    print("Preparing features...")
    
    # Define feature columns for gap analysis based on available columns
    feature_cols = [
        'Avg_Rent', 'Std_Rent', 'Supply', 
        'inflation_rate', 'interest_rate', 'employment_rate', 
        'covid_impact_score', 'Economic_Health_Score'
    ]
    
    # Add engineered features
    df['Rent_to_Supply_Ratio'] = df['Avg_Rent'] / (df['Supply'] + 1)
    df['Economic_Factor'] = (
        df['employment_rate'] * 0.4 + 
        (100 - df['interest_rate']) * 0.3 + 
        (100 - df['inflation_rate']) * 0.3
    )
    feature_cols.extend(['Rent_to_Supply_Ratio', 'Economic_Factor'])
    
    # Handle categorical features
    categorical_cols = ['City_Tier', 'Region', 'BHK']
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
            feature_cols.append(f'{col}_encoded')
    
    # Handle missing values
    df = df.fillna(df.median(numeric_only=True))
    
    X = df[feature_cols]
    y = df['Gap_Ratio']
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y, feature_cols, scaler

def train_efficient_model():
    """Train an efficient gap analysis model"""
    print("Training efficient gap analysis model...")
    
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
        print(f"Fold {fold+1}: Train MAE: {train_mae:.4f}, Val MAE: {val_mae:.4f}")
    
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
    
    print(f"Training MAE: {train_mae:.4f}")
    print(f"Testing MAE: {test_mae:.4f}")
    print(f"Training RMSE: {train_rmse:.4f}")
    print(f"Testing RMSE: {test_rmse:.4f}")
    print(f"Training R²: {train_r2:.4f}")
    print(f"Testing R²: {test_r2:.4f}")
    
    # Calculate cross-validation averages
    avg_val_mae = np.mean([score['val_mae'] for score in cv_scores])
    avg_val_rmse = np.mean([score['val_rmse'] for score in cv_scores])
    print(f"Average CV Validation MAE: {avg_val_mae:.4f}")
    print(f"Average CV Validation MAE: {avg_val_rmse:.4f}")
    
    # Save the model and scaler
    joblib.dump(model, 'gap_analysis_model_efficient.pkl')
    joblib.dump(scaler, 'feature_scaler_gap_efficient.pkl')
    print("Model and scaler saved successfully!")
    
    # Save metrics to JSON file for API consumption
    metrics_data = {
        "model_name": "Gap Analysis Model (Production)",
        "model_version": "2.0.0",
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
        "features": feature_cols,
        "target_variable": "Gap_Ratio",
        "target_interpretation": {
            "positive_values": "Undersupply (High Demand)",
            "negative_values": "Oversupply (Low Demand)",
            "near_zero": "Balanced Market"
        }
    }
    
    # Add Comparison Data (Actual vs Predicted) to metrics_data
    print("Generating prediction samples for visualization...")
    predictions_sample = []
    
    # Take a sample of test predictions (e.g., 100 points)
    n_comparison = min(100, len(y_test))
    indices = np.random.choice(len(y_test), n_comparison, replace=False)
    
    for idx in indices:
        predictions_sample.append({
            "actual": float(y_test.iloc[idx]),
            "predicted": float(y_pred_test[idx]),
            "locality_encoded": 0  # Simplified for demo
        })
    
    metrics_data["predictions_sample"] = predictions_sample
    
    with open('model_metrics.json', 'w') as f:
        json.dump(metrics_data, f, indent=2)
    print("Metrics saved to model_metrics.json (with prediction samples)")
    
    return model, scaler, feature_cols

def main():
    """Main function to train the efficient model"""
    print("Starting efficient gap analysis model training...")
    model, scaler, feature_cols = train_efficient_model()
    print("Model training completed successfully!")
    print(f"Features used: {feature_cols}")

if __name__ == "__main__":
    main()