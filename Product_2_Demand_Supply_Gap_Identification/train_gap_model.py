import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import lightgbm as lgb
import pickle
import os
from datetime import datetime

def train_gap_model():
    """
    Train a model to identify demand-supply gaps in rental markets.
    """
    print("Training demand-supply gap identification model...")
    
    # Load prepared data
    data_path = '/tmp/gap_analysis_data.csv'
    if not os.path.exists(data_path):
        print(f"Error: Prepared data not found at {data_path}")
        print("Please run prepare_gap_data.py first.")
        return
    
    df = pd.read_csv(data_path)
    
    # Handle missing values
    df = df.fillna(0)
    
    # Feature engineering
    # Create categorical encodings
    df_encoded = pd.get_dummies(df, columns=['City', 'City_Tier', 'Region', 'BHK'], prefix=['City', 'Tier', 'Region', 'BHK'])
    
    # For Area Locality, we'll use label encoding since there are too many for one-hot
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    df_encoded['Area_Locality_Encoded'] = le.fit_transform(df_encoded['Area Locality'])
    
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
    
    # Time series split for validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Model parameters
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
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
    fold = 1
    
    for train_idx, val_idx in tscv.split(X):
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
        
        cv_scores.append({'fold': fold, 'rmse': rmse, 'mape': mape})
        print(f"Fold {fold}: RMSE = {rmse:.4f}, MAPE = {mape:.4f}")
        fold += 1
    
    # Print CV results
    avg_rmse = np.mean([score['rmse'] for score in cv_scores])
    avg_mape = np.mean([score['mape'] for score in cv_scores])
    print(f"\nCross-validation results:")
    print(f"Average RMSE: {avg_rmse:.4f}")
    print(f"Average MAPE: {avg_mape:.4f}")
    
    # Train final model on all data
    print("\nTraining final model on all data...")
    train_data = lgb.Dataset(X, label=y)
    final_model = lgb.train(
        params,
        train_data,
        num_boost_round=1000,
        callbacks=[lgb.log_evaluation(period=0)]
    )
    
    # Save model
    model_path = '/tmp/gap_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(final_model, f)
    
    # Save feature columns for inference
    feature_path = '/tmp/gap_feature_columns.pkl'
    with open(feature_path, 'wb') as f:
        pickle.dump(feature_columns, f)
    
    # Save label encoder
    le_path = '/tmp/gap_label_encoder.pkl'
    with open(le_path, 'wb') as f:
        pickle.dump(le, f)
    
    print(f"Model saved to {model_path}")
    print(f"Feature columns saved to {feature_path}")
    print(f"Label encoder saved to {le_path}")
    
    # Feature importance
    importance_df = pd.DataFrame({
        'feature': X.columns,
        'importance': final_model.feature_importance()
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Important Features:")
    print(importance_df.head(10))
    
    # Save feature importance
    importance_path = '/tmp/gap_feature_importance.csv'
    importance_df.to_csv(importance_path, index=False)
    print(f"Feature importance saved to {importance_path}")

if __name__ == "__main__":
    train_gap_model()