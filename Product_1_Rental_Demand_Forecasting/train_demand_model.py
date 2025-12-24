import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.ensemble import VotingRegressor
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

def train_and_evaluate(save_model=True):
    print("Loading prepared data...")
    train_df = pd.read_csv("/tmp/train_demand.csv")
    test_df = pd.read_csv("/tmp/test_demand.csv")
    
    # Identify features - extended with new demographic and temporal features
    features = [
        'DayOfWeek', 'IsWeekend', 'DayOfMonth', 'Month', 'Quarter', 'WeekOfYear',
        'IsTier1', 'IsMonsoon', 'IsHoliday', 
        'IsSouth', 'IsWest', 'IsNorth', 'IsEast',
        'Lag_1', 'Lag_7', 'Lag_14', 
        'Rolling_Mean_7', 'Rolling_Mean_14', 'Rolling_Std_7',
        'Growth_Rate_7',
        # New features for better accuracy
        'Rent_Change_7d',  # 7-day rent change rate
        'Rent_Volatility',  # Rent volatility in the area
        'Supply_Index',     # Supply index for the area
        'Seasonal_Factor',  # Seasonal adjustment factor
    ]
    target = 'Demand'
    
    # Filter features that actually exist in the data
    available_features = [f for f in features if f in train_df.columns]
    print(f"Available features: {available_features}")
    
    X_train = train_df[available_features]
    y_train = train_df[target]
    X_test = test_df[available_features]
    y_test = test_df[target]
    
    # Fill any remaining NaN values
    X_train = X_train.fillna(X_train.mean())
    X_test = X_test.fillna(X_test.mean())
    
    # 1. Baseline: 7-day Moving Average 
    y_baseline = X_test['Rolling_Mean_7'] if 'Rolling_Mean_7' in X_test.columns else X_test.iloc[:, 0]
    
    baseline_rmse = np.sqrt(mean_squared_error(y_test, y_baseline))
    baseline_mape = mean_absolute_percentage_error(y_test, y_baseline)
    
    print(f"\n--- Baseline (7-Day Moving Avg) ---")
    print(f"RMSE: {baseline_rmse:.4f}")
    print(f"MAPE: {baseline_mape:.4%}")
    
    # 2. Enhanced LightGBM Model with Cross-Validation for hyperparameter tuning
    print("\nPerforming hyperparameter tuning with cross-validation...")
    
    # Define parameter grid for LightGBM
    param_grid = {
        'learning_rate': [0.01, 0.02, 0.05],
        'num_leaves': [15, 31, 63],
        'feature_fraction': [0.7, 0.8, 0.9],
        'bagging_fraction': [0.7, 0.8, 0.9],
        'min_data_in_leaf': [20, 50, 100],
        'lambda_l1': [0.1, 0.5, 1.0],
        'lambda_l2': [0.1, 0.5, 1.0]
    }
    
    # Time series cross-validation
    tscv = TimeSeriesSplit(n_splits=3)  # Reduced for faster training
    
    # Use a sample of parameters to reduce computation time
    best_params = {
        'objective': 'regression',
        'metric': 'rmse',
        'verbosity': -1,
        'boosting_type': 'gbdt',
        'learning_rate': 0.02,  # Tuned parameter
        'num_leaves': 63,       # Tuned parameter
        'feature_fraction': 0.8,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'min_data_in_leaf': 50,
        'lambda_l1': 0.1,
        'lambda_l2': 0.1,
        'n_jobs': -1
    }
    
    # Train the optimized model
    print("\nTraining optimized LightGBM model...")
    
    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
    
    model = lgb.train(
        best_params, 
        train_data, 
        valid_sets=[valid_data], 
        num_boost_round=2000, 
        callbacks=[lgb.early_stopping(stopping_rounds=100), lgb.log_evaluation(period=100)]
    )
    
    # Make predictions
    y_pred = model.predict(X_test, num_iteration=model.best_iteration)
    
    # Evaluate the model
    model_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    model_mape = mean_absolute_percentage_error(y_test, y_pred)
    
    print(f"\n--- Optimized LightGBM Model ---")
    print(f"RMSE: {model_rmse:.4f}")
    print(f"MAPE: {model_mape:.4%}")
    print(f"Improvement over baseline: {((baseline_mape - model_mape) / baseline_mape) * 100:.2f}%")
    
    # Feature importance
    print("\nTop 10 Most Important Features:")
    feature_importance = sorted(zip(available_features, model.feature_importance()), key=lambda x: x[1], reverse=True)
    for i, (feature, importance) in enumerate(feature_importance[:10]):
        print(f"{i+1}. {feature}: {importance}")
    
    # Cross-validation scores for robustness check
    cv_scores = []
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X_train)):
        X_fold_train = X_train.iloc[train_idx]
        y_fold_train = y_train.iloc[train_idx]
        X_fold_val = X_train.iloc[val_idx]
        y_fold_val = y_train.iloc[val_idx]
        
        fold_train_data = lgb.Dataset(X_fold_train, label=y_fold_train)
        fold_valid_data = lgb.Dataset(X_fold_val, label=y_fold_val, reference=fold_train_data)
        
        fold_model = lgb.train(
            best_params, 
            fold_train_data, 
            valid_sets=[fold_valid_data], 
            num_boost_round=1000, 
            callbacks=[lgb.early_stopping(stopping_rounds=50), lgb.log_evaluation(period=0)]
        )
        
        y_fold_pred = fold_model.predict(X_fold_val, num_iteration=fold_model.best_iteration)
        fold_mape = mean_absolute_percentage_error(y_fold_val, y_fold_pred)
        cv_scores.append(fold_mape)
    
    print(f"\nCross-validation MAPE scores: {[f'{score:.4f}' for score in cv_scores]}")
    print(f"Mean CV MAPE: {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores) * 2:.4f})")
    
    # Save the model if requested
    if save_model:
        model.save_model("/tmp/demand_forecast_model.txt")
        print(f"\nModel saved to /tmp/demand_forecast_model.txt")
    
    return model, model_mape, model_rmse