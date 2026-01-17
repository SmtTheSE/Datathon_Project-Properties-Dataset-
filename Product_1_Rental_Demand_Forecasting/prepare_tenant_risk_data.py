"""
Data Preparation Pipeline - Tenant Risk Model
Prepares Vietnamese banking data for tenant financial risk prediction.

Author: Senior Data Engineering Team
Date: 2026-01-17
"""

import pandas as pd
import numpy as np
import sys
import os
from financial_normalizer import FinancialNormalizer, engineer_financial_features, validate_features

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def load_vietnamese_data(filepath: str) -> pd.DataFrame:
    """
    Load Vietnamese banking dataset.
    
    Args:
        filepath: Path to train.csv
        
    Returns:
        DataFrame with banking data
    """
    print("=" * 60)
    print("PHASE 1: DATA PREPARATION")
    print("=" * 60)
    
    print(f"\nLoading Vietnamese banking dataset...")
    df = pd.read_csv(filepath)
    
    print(f"✓ Loaded {len(df):,} customer records")
    print(f"✓ Features: {df.shape[1]} columns")
    print(f"\nTarget Distribution:")
    print(f"  No Churn: {(df['Churn'] == 0).sum():,} ({(df['Churn'] == 0).mean()*100:.1f}%)")
    print(f"  Churn: {(df['Churn'] == 1).sum():,} ({(df['Churn'] == 1).mean()*100:.1f}%)")
    
    return df


def prepare_features(df: pd.DataFrame) -> tuple:
    """
    Prepare features for tenant risk model.
    
    Args:
        df: Raw banking data
        
    Returns:
        Tuple of (features_df, normalizer)
    """
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING")
    print("=" * 60)
    
    # Step 1: Create and fit normalizer
    print("\n1. Creating financial normalizer...")
    normalizer = FinancialNormalizer()
    normalizer.fit(df['Avg_Trans_Amount'].values)
    
    # Step 2: Engineer features
    print("\n2. Engineering financial health features...")
    features = engineer_financial_features(df, normalizer)
    
    # Step 3: Validate
    print("\n3. Validating features...")
    validate_features(features)
    
    # Step 4: Add target variable
    features['Churn'] = df['Churn']
    
    return features, normalizer


def save_prepared_data(features: pd.DataFrame, normalizer: FinancialNormalizer, output_dir: str):
    """
    Save prepared features and normalizer.
    
    Args:
        features: Engineered features
        normalizer: Fitted normalizer
        output_dir: Directory to save files
    """
    print("\n" + "=" * 60)
    print("SAVING PREPARED DATA")
    print("=" * 60)
    
    # Save features
    features_path = os.path.join(output_dir, 'tenant_risk_features.csv')
    features.to_csv(features_path, index=False)
    print(f"\n✓ Saved features to {features_path}")
    print(f"  Shape: {features.shape}")
    
    # Save normalizer
    normalizer_path = os.path.join(output_dir, 'financial_normalizer.pkl')
    normalizer.save(normalizer_path)
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("FEATURE SUMMARY")
    print("=" * 60)
    print(f"\nFinancial Health Distribution:")
    print(features['financial_health'].describe())
    
    print(f"\nRisk Category Distribution:")
    risk_dist = features['risk_category'].value_counts()
    for category, count in risk_dist.items():
        pct = count / len(features) * 100
        print(f"  {category}: {count:,} ({pct:.1f}%)")
    
    print("\n✓ Data preparation complete!")
    print("=" * 60)


def main():
    """Main data preparation pipeline."""
    # Paths
    data_path = '../dropdatasetnew/train.csv'
    output_dir = '.'
    
    # Check if data exists
    if not os.path.exists(data_path):
        print(f"ERROR: Data file not found at {data_path}")
        print("Please ensure dropdatasetnew/train.csv exists")
        return
    
    # Load data
    df = load_vietnamese_data(data_path)
    
    # Prepare features
    features, normalizer = prepare_features(df)
    
    # Save
    save_prepared_data(features, normalizer, output_dir)


if __name__ == "__main__":
    main()
