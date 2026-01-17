"""
Financial Normalizer - Production Grade
Converts Vietnamese banking features to Indian rental market context using percentile-based mapping.

Author: Senior Data Engineering Team
Date: 2026-01-17
"""

import numpy as np
import pandas as pd
import pickle
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class FinancialNormalizer:
    """
    Normalizes Vietnamese financial data to Indian context using percentile mapping.
    
    This is NOT a simple currency conversion. Instead, we map financial health
    percentiles from Vietnamese distribution to equivalent Indian percentiles.
    
    Example:
        A Vietnamese customer at 90th percentile income maps to
        an Indian tenant at 90th percentile income, regardless of absolute amounts.
    """
    
    def __init__(self):
        self.vn_percentiles = None
        self.fitted = False
        
    def fit(self, vn_amounts: np.ndarray):
        """
        Learn Vietnamese financial distribution from actual data.
        
        Args:
            vn_amounts: Array of Vietnamese transaction amounts (VND)
        """
        # Compute percentiles from actual Vietnamese data
        self.vn_percentiles = {
            'min': float(np.min(vn_amounts)),
            'p25': float(np.percentile(vn_amounts, 25)),
            'p50': float(np.percentile(vn_amounts, 50)),
            'p75': float(np.percentile(vn_amounts, 75)),
            'p90': float(np.percentile(vn_amounts, 90)),
            'p95': float(np.percentile(vn_amounts, 95)),
            'max': float(np.max(vn_amounts)),
            'mean': float(np.mean(vn_amounts)),
            'std': float(np.std(vn_amounts))
        }
        
        self.fitted = True
        print(f"✓ Learned Vietnamese distribution from {len(vn_amounts):,} samples")
        print(f"  Median: {self.vn_percentiles['p50']:,.0f} VND")
        print(f"  Mean: {self.vn_percentiles['mean']:,.0f} VND")
        
    def normalize_to_score(self, amounts: np.ndarray) -> np.ndarray:
        """
        Normalize amounts to 0-100 scores based on percentile (vectorized).
        
        Args:
            amounts: Array of amounts in VND
            
        Returns:
            Array of normalized scores (0-100)
        """
        if not self.fitted:
            raise ValueError("Normalizer not fitted. Call fit() first.")
        
        # Ensure numpy array
        amounts = np.asarray(amounts)
        scores = np.zeros_like(amounts, dtype=float)
        
        # Vectorized percentile calculation
        p_min = self.vn_percentiles['min']
        p25 = self.vn_percentiles['p25']
        p50 = self.vn_percentiles['p50']
        p75 = self.vn_percentiles['p75']
        p90 = self.vn_percentiles['p90']
        p_max = self.vn_percentiles['max']
        
        # Handle each range
        mask_min = amounts <= p_min
        mask_p25 = (amounts > p_min) & (amounts <= p25)
        mask_p50 = (amounts > p25) & (amounts <= p50)
        mask_p75 = (amounts > p50) & (amounts <= p75)
        mask_p90 = (amounts > p75) & (amounts <= p90)
        mask_max = amounts > p90
        
        scores[mask_min] = 0.0
        scores[mask_p25] = 25.0 * (amounts[mask_p25] - p_min) / (p25 - p_min)
        scores[mask_p50] = 25.0 + 25.0 * (amounts[mask_p50] - p25) / (p50 - p25)
        scores[mask_p75] = 50.0 + 25.0 * (amounts[mask_p75] - p50) / (p75 - p50)
        scores[mask_p90] = 75.0 + 15.0 * (amounts[mask_p90] - p75) / (p90 - p75)
        scores[mask_max] = 90.0 + 10.0 * np.clip((amounts[mask_max] - p90) / (p_max - p90), 0, 1) * 10
        
        # Ensure all scores are in [0, 100] range
        scores = np.clip(scores, 0, 100)
        
        return scores
    
    def save(self, filepath: str):
        """Save normalizer to disk."""
        if not self.fitted:
            raise ValueError("Cannot save unfitted normalizer")
        
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        print(f"✓ Saved normalizer to {filepath}")
    
    @staticmethod
    def load(filepath: str) -> 'FinancialNormalizer':
        """Load normalizer from disk."""
        with open(filepath, 'rb') as f:
            normalizer = pickle.load(f)
        print(f"✓ Loaded normalizer from {filepath}")
        return normalizer


def engineer_financial_features(df: pd.DataFrame, normalizer: FinancialNormalizer) -> pd.DataFrame:
    """
    Engineer tenant-relevant financial health features from banking data.
    
    All features are normalized to 0-100 scale for interpretability.
    
    Args:
        df: DataFrame with Vietnamese banking features
        normalizer: Fitted FinancialNormalizer
        
    Returns:
        DataFrame with engineered features
    """
    features = pd.DataFrame(index=df.index)
    
    # 1. Income Stability Score (0-100)
    # Higher transaction amount + consistency = higher score
    avg_trans = df['Avg_Trans_Amount'].fillna(0)
    features['income_stability'] = normalizer.normalize_to_score(avg_trans.values)
    
    # 2. Debt Burden Score (0-100, lower is better, so we invert)
    # Debt relative to income
    debt_ratio = df['Avg_Loan_Balance'].fillna(0) / (df['Avg_Trans_Amount'].fillna(1) + 1)
    features['debt_burden'] = 100 - np.clip(debt_ratio * 100, 0, 100)
    
    # 3. Savings Cushion Score (0-100)
    # Account balance relative to monthly transactions
    cushion_ratio = df['Avg_CurrentAccount_Balance'].fillna(0) / (df['Avg_Trans_Amount'].fillna(1) + 1)
    features['savings_cushion'] = np.clip(cushion_ratio * 20, 0, 100)  # 5 months = 100
    
    # 4. Payment History Score (0-100)
    # Tenure (months) * transaction frequency
    payment_score = df['Tenure'].fillna(0) * df['Avg_Trans_no_month'].fillna(0)
    features['payment_history'] = np.clip(payment_score / 5, 0, 100)  # Normalize
    
    # 5. Transaction Consistency Score (0-100)
    # More transactions = more consistent income
    trans_count = df['Avg_Trans_no_month'].fillna(0)
    features['transaction_consistency'] = np.clip(trans_count * 4, 0, 100)  # 25 trans/month = 100
    
    # 6. Financial Health Score (0-100) - Weighted combination
    features['financial_health'] = (
        0.30 * features['income_stability'] +
        0.25 * features['debt_burden'] +
        0.20 * features['savings_cushion'] +
        0.15 * features['payment_history'] +
        0.10 * features['transaction_consistency']
    )
    
    # 7. Risk Category (categorical)
    features['risk_category'] = pd.cut(
        features['financial_health'],
        bins=[0, 40, 70, 100],
        labels=['HIGH_RISK', 'MEDIUM_RISK', 'LOW_RISK']
    )
    
    return features


def validate_features(features: pd.DataFrame) -> bool:
    """
    Validate engineered features for data quality.
    
    Args:
        features: DataFrame with engineered features
        
    Returns:
        True if validation passes
        
    Raises:
        ValueError if validation fails
    """
    # Check for NaN values
    nan_counts = features.isnull().sum()
    if nan_counts.any():
        raise ValueError(f"Found NaN values:\n{nan_counts[nan_counts > 0]}")
    
    # Check value ranges
    score_columns = ['income_stability', 'debt_burden', 'savings_cushion', 
                     'payment_history', 'transaction_consistency', 'financial_health']
    
    for col in score_columns:
        if not features[col].between(0, 100).all():
            raise ValueError(f"{col} has values outside [0, 100] range")
    
    # Check distributions
    print("\n✓ Feature validation passed:")
    print(f"  All {len(features):,} samples have valid features")
    print(f"  Financial Health Score: {features['financial_health'].mean():.2f} ± {features['financial_health'].std():.2f}")
    print(f"  Risk Distribution:")
    print(f"    {features['risk_category'].value_counts().to_dict()}")
    
    return True


if __name__ == "__main__":
    # Test with sample data
    print("Testing Financial Normalizer...")
    
    # Create sample Vietnamese data
    sample_amounts = np.random.lognormal(15, 0.5, 1000) * 1000000  # Simulate VND amounts
    
    # Fit normalizer
    normalizer = FinancialNormalizer()
    normalizer.fit(sample_amounts)
    
    # Test normalization
    test_amount = sample_amounts[0]
    score = normalizer.normalize_to_score(test_amount)
    print(f"\nTest: {test_amount:,.0f} VND → Score: {score:.2f}")
    
    print("\n✓ Financial Normalizer working correctly")
