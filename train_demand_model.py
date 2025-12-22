import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.model_selection import TimeSeriesSplit
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
        'Growth_Rate_7'
    ]
    target = 'Demand'
    
    # Filter features that actually exist in the data
    available_features = [f for f in features if f in train_df.columns]
    print(f"Available features: {available_features}")
    
    X_train = train_df[available_features]
    y_train = train_df[target]
    X_test = test_df[available_features]
    y_test = test_df[target]
    
    # 1. Baseline: 7-day Moving Average 
    y_baseline = X_test['Rolling_Mean_7']
    
    baseline_rmse = np.sqrt(mean_squared_error(y_test, y_baseline))
    baseline_mape = mean_absolute_percentage_error(y_test, y_baseline)
    
    print(f"\n--- Baseline (7-Day Moving Avg) ---")
    print(f"RMSE: {baseline_rmse:.4f}")
    print(f"MAPE: {baseline_mape:.4%}")
    
    # 2. Enhanced LightGBM Model with Cross-Validation
    print("\nTraining Enhanced LightGBM with Cross-Validation...")
    
    # Prepare data for cross-validation
    cv_data = pd.concat([train_df, test_df])
    
    # Demographic split - Tier 1 vs Tier 2 cities
    tier1_train = train_df[train_df['IsTier1'] == 1]
    tier2_train = train_df[train_df['IsTier1'] == 0]
    tier1_test = test_df[test_df['IsTier1'] == 1]
    tier2_test = test_df[test_df['IsTier1'] == 0]
    
    # Regional splits
    south_test = test_df[test_df['IsSouth'] == 1] if 'IsSouth' in test_df.columns else pd.DataFrame()
    west_test = test_df[test_df['IsWest'] == 1] if 'IsWest' in test_df.columns else pd.DataFrame()
    north_test = test_df[test_df['IsNorth'] == 1] if 'IsNorth' in test_df.columns else pd.DataFrame()
    east_test = test_df[test_df['IsEast'] == 1] if 'IsEast' in test_df.columns else pd.DataFrame()
    
    # Time series cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'verbosity': -1,
        'boosting_type': 'gbdt',
        'learning_rate': 0.05,
        'num_leaves': 31,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'min_data_in_leaf': 50,
        'lambda_l1': 0.1,
        'lambda_l2': 0.1,
        'n_jobs': -1
    }
    
    # Cross-validation scores
    cv_scores = []
    for fold, (train_idx, val_idx) in enumerate(tscv.split(train_df)):
        X_fold_train = X_train.iloc[train_idx]
        y_fold_train = y_train.iloc[train_idx]
        X_fold_val = X_train.iloc[val_idx]
        y_fold_val = y_train.iloc[val_idx]
        
        train_data = lgb.Dataset(X_fold_train, label=y_fold_train)
        valid_data = lgb.Dataset(X_fold_val, label=y_fold_val, reference=train_data)
        
        model = lgb.train(
            params, 
            train_data, 
            valid_sets=[valid_data], 
            num_boost_round=1000, 
            callbacks=[lgb.early_stopping(stopping_rounds=50), lgb.log_evaluation(period=0)]
        )
        
        y_pred = model.predict(X_fold_val, num_iteration=model.best_iteration)
        fold_mape = mean_absolute_percentage_error(y_fold_val, y_pred)
        cv_scores.append(fold_mape)
    
    print(f"Cross-Validation MAPE: {np.mean(cv_scores):.4%} (+/- {np.std(cv_scores) * 2:.4%})")
    
    # Train final model on all training data
    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
    
    model = lgb.train(
        params, 
        train_data, 
        valid_sets=[valid_data], 
        num_boost_round=1000, 
        callbacks=[lgb.early_stopping(stopping_rounds=50), lgb.log_evaluation(period=0)]
    )
    
    # Predictions on overall test set
    y_pred = model.predict(X_test, num_iteration=model.best_iteration)
    
    model_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    model_mape = mean_absolute_percentage_error(y_test, y_pred)
    
    print(f"--- Enhanced LightGBM Model ---")
    print(f"RMSE: {model_rmse:.4f}")
    print(f"MAPE: {model_mape:.4%}")
    
    # Demographic split evaluation
    if len(tier1_test) > 0:
        tier1_X_test = tier1_test[available_features]
        tier1_y_test = tier1_test[target]
        tier1_pred = model.predict(tier1_X_test, num_iteration=model.best_iteration)
        tier1_mape = mean_absolute_percentage_error(tier1_y_test, tier1_pred)
        print(f"Tier 1 Cities MAPE: {tier1_mape:.4%}")
    
    if len(tier2_test) > 0:
        tier2_X_test = tier2_test[available_features]
        tier2_y_test = tier2_test[target]
        tier2_pred = model.predict(tier2_X_test, num_iteration=model.best_iteration)
        tier2_mape = mean_absolute_percentage_error(tier2_y_test, tier2_pred)
        print(f"Tier 2 Cities MAPE: {tier2_mape:.4%}")
        
    # Regional split evaluation
    regions = [('South', south_test), ('West', west_test), ('North', north_test), ('East', east_test)]
    for region_name, region_data in regions:
        if len(region_data) > 0:
            region_X_test = region_data[available_features]
            region_y_test = region_data[target]
            region_pred = model.predict(region_X_test, num_iteration=model.best_iteration)
            region_mape = mean_absolute_percentage_error(region_y_test, region_pred)
            print(f"{region_name} Region MAPE: {region_mape:.4%}")
    
    # Improvement
    improvement = (baseline_mape - model_mape) / baseline_mape
    print(f"\nTotal MAPE Improvement Over Baseline: {improvement:.2%}")
    
    # Feature Importance
    importance = pd.DataFrame({
        'feature': available_features,
        'importance': model.feature_importance(importance_type='gain')
    }).sort_values('importance', ascending=False)
    
    print("\n--- Feature Importance (Gain) ---")
    print(importance.head(10))  # Show top 10 features
    
    print("\n--- Feature Importance (Gain) ---")
    print(importance)
    
    # Save results for artifact
    importance.to_csv("/tmp/feature_importance.csv", index=False)
    results = pd.DataFrame({
        'Metric': ['RMSE', 'MAPE', 'CV_MAPE_Mean', 'CV_MAPE_Std'],
        'Baseline': [baseline_rmse, baseline_mape, None, None],
        'LightGBM': [model_rmse, model_mape, np.mean(cv_scores), np.std(cv_scores)]
    })
    results.to_csv("/tmp/model_results.csv", index=False)
    
    # Save the trained model for serving
    if save_model:
        model.save_model("/tmp/demand_forecast_model.txt")
        print("\nModel saved to /tmp/demand_forecast_model.txt")

if __name__ == "__main__":
    train_and_evaluate()