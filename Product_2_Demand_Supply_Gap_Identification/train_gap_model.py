import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
import pickle
import os
from datetime import datetime
from sklearn.ensemble import IsolationForest

def train_gap_model():
    """
    Train a model to identify demand-supply gaps in rental markets.
    Enhanced with better feature engineering and hyperparameter tuning.
    """
    print("Training enhanced demand-supply gap identification model...")
    
    # Load prepared data with external factors
    data_path = '/tmp/enhanced_gap_analysis_data.csv'
    if not os.path.exists(data_path):
        print(f"Error: Enhanced prepared data not found at {data_path}")
        print("Please run integrate_external_data.py and prepare_gap_data_with_external_factors() first.")
        return
    
    df = pd.read_csv(data_path, low_memory=False)
    
    print(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
    
    # Handle missing values
    df = df.fillna(0)
    
    # Outlier detection and treatment
    print("Detecting and treating outliers...")
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_columns = [col for col in numeric_columns if col not in ['Gap', 'Gap_Ratio']]  # Exclude target variables
    
    # Use Isolation Forest to detect outliers in feature space
    iso_forest = IsolationForest(contamination=0.1, random_state=42)
    outlier_labels = iso_forest.fit_predict(df[numeric_columns[:10]])  # Use first 10 numeric columns to avoid memory issues
    df = df[outlier_labels == 1]  # Keep inliers only
    print(f"Dataset after outlier removal: {len(df)} rows")
    
    # Feature engineering enhancements
    print("Performing enhanced feature engineering...")
    
    # Temporal features
    df['Season'] = df['Month'].map({1: 'Winter', 2: 'Winter', 3: 'Spring', 4: 'Spring', 
                                   5: 'Spring', 6: 'Summer', 7: 'Summer', 8: 'Summer', 
                                   9: 'Autumn', 10: 'Autumn', 11: 'Autumn', 12: 'Winter'})
    
    # Create seasonal dummy variables
    df = pd.get_dummies(df, columns=['Season'], prefix='Season')
    
    # Interaction features between supply and rent
    df['Supply_Rent_Interaction'] = df['Supply'] * df['Avg_Rent']
    df['Supply_Rent_Ratio'] = df['Supply'] / (df['Avg_Rent'] + 1)  # +1 to avoid division by zero
    
    # Interaction features between supply and economic factors
    economic_cols = ['Avg_Economic_Health', 'Avg_Employment', 'Avg_Interest', 'Avg_Inflation']
    for econ_col in economic_cols:
        if econ_col in df.columns:
            df[f'Supply_{econ_col}_Interaction'] = df['Supply'] * df[econ_col]
    
    # Lag features for time series (if we have sufficient data)
    df = df.sort_values(['City', 'Area Locality', 'BHK', 'Year', 'Month'])
    
    # Rolling statistics by city and area
    for col in ['Avg_Rent', 'Supply']:
        df[f'{col}_MA3'] = df.groupby(['City', 'Area Locality', 'BHK'])[col].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )
        df[f'{col}_Change'] = df.groupby(['City', 'Area Locality', 'BHK'])[col].pct_change().fillna(0)
    
    # Create categorical encodings
    categorical_columns = ['City', 'City_Tier', 'Region', 'BHK']
    df_encoded = pd.get_dummies(df, columns=categorical_columns, prefix=categorical_columns)
    
    # For Area Locality, we'll use label encoding since there are too many for one-hot
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    
    # Handle unknown values in Area Locality by encoding them as a special value
    all_localities = df['Area Locality'].astype(str).unique()
    le.fit(all_localities)
    
    # Save the label encoder
    with open('/tmp/gap_label_encoder.pkl', 'wb') as f:
        pickle.dump(le, f)
    
    df_encoded['Area_Locality_Encoded'] = le.transform(df['Area Locality'].astype(str))
    
    # Drop the original Area Locality column
    df_encoded = df_encoded.drop(['Area Locality'], axis=1)
    
    # Ensure we have consistent columns (in case some cities/tiers are missing in test set)
    feature_columns = [col for col in df_encoded.columns if col not in ['Gap', 'Gap_Ratio']]
    
    # Define features and target
    X = df_encoded[feature_columns]
    y = df_encoded['Gap_Ratio']  # Using ratio for better generalization
    
    # Convert to appropriate types for LightGBM
    for col in X.columns:
        if X[col].dtype == 'object':
            X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
    
    # Fill any remaining NaN values
    X = X.fillna(0)
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
    
    # Save the scaler
    with open('/tmp/gap_scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    # Save feature columns for inference
    with open('/tmp/gap_feature_columns.pkl', 'wb') as f:
        pickle.dump(feature_columns, f)
    
    # Time series split for validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Enhanced model parameters with better regularization
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'boosting_type': 'gbdt',
        'num_leaves': 127,  # Increased for more complexity
        'learning_rate': 0.01,  # Reduced for better convergence
        'feature_fraction': 0.85,
        'bagging_fraction': 0.85,
        'bagging_freq': 5,
        'min_data_in_leaf': 25,  # Reduced for more sensitivity
        'lambda_l1': 0.3,
        'lambda_l2': 0.3,
        'min_gain_to_split': 0.01,
        'verbose': -1,
        'device_type': 'cpu'
    }
    
    # Time series split for validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Cross-validation with better metrics
    cv_scores = []
    fold = 1
    
    for train_idx, val_idx in tscv.split(X_scaled):
        X_train, X_val = X_scaled.iloc[train_idx], X_scaled.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        # Create LightGBM datasets
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
        
        # Train model with early stopping
        model = lgb.train(
            params,
            train_data,
            valid_sets=[val_data],
            num_boost_round=2000,
            callbacks=[lgb.early_stopping(stopping_rounds=100), lgb.log_evaluation(period=0)]
        )
        
        # Make predictions and evaluate
        y_pred = model.predict(X_val)
        fold_mape = mean_absolute_percentage_error(y_val, y_pred)
        fold_rmse = mean_squared_error(y_val, y_pred, squared=False)
        
        cv_scores.append({'fold': fold, 'mape': fold_mape, 'rmse': fold_rmse})
        print(f"Fold {fold}: MAPE = {fold_mape:.4f}, RMSE = {fold_rmse:.4f}")
        fold += 1
    
    print(f"\nCross-validation results:")
    for score in cv_scores:
        print(f"Fold {score['fold']}: MAPE = {score['mape']:.4f}, RMSE = {score['rmse']:.4f}")
    
    # Calculate average metrics
    avg_mape = np.mean([s['mape'] for s in cv_scores])
    avg_rmse = np.mean([s['rmse'] for s in cv_scores])
    print(f"\nAverage MAPE: {avg_mape:.4f}")
    print(f"Average RMSE: {avg_rmse:.4f}")
    
    # Train final model on full dataset
    print("\nTraining final model on full dataset...")
    train_data = lgb.Dataset(X_scaled, label=y)
    
    final_model = lgb.train(
        params,
        train_data,
        num_boost_round=model.best_iteration if hasattr(model, 'best_iteration') else 1000
    )
    
    # Save the model
    with open('/tmp/gap_model.pkl', 'wb') as f:
        pickle.dump(final_model, f)
    
    print("Enhanced model training completed and saved to /tmp/gap_model.pkl")
    
    # Feature importance
    print("\nTop 10 Most Important Features:")
    feature_importance = sorted(zip(feature_columns, final_model.feature_importance()), 
                               key=lambda x: x[1], reverse=True)
    for i, (feature, importance) in enumerate(feature_importance[:10]):
        print(f"{i+1}. {feature}: {importance}")
    
    # Save feature importance
    importance_df = pd.DataFrame({
        'feature': feature_columns,
        'importance': final_model.feature_importance()
    }).sort_values('importance', ascending=False)
    
    importance_path = '/tmp/gap_feature_importance.csv'
    importance_df.to_csv(importance_path, index=False)
    print(f"Feature importance saved to {importance_path}")

    return final_model, avg_mape, avg_rmse

if __name__ == "__main__":
    train_gap_model()