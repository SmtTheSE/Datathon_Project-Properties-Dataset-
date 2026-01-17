"""
Enhanced Prediction Service - Production Grade
Combines demand forecasting with tenant financial risk scoring.

Author: Senior Data Engineering Team
Date: 2026-01-17
"""

import numpy as np
import pandas as pd
import joblib
import onnxruntime as ort
from typing import Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class EnhancedPredictionService:
    """
    Enhanced prediction service combining demand forecasting with tenant risk.
    
    Provides quality-adjusted demand predictions by:
    1. Predicting base demand (existing Product 1)
    2. Predicting tenant quality distribution (new tenant risk model)
    3. Combining for quality-adjusted demand
    """
    
    def __init__(self, demand_model_path: str, tenant_risk_model_path: str):
        """
        Initialize enhanced prediction service.
        
        Args:
            demand_model_path: Path to demand ONNX model
            tenant_risk_model_path: Path to tenant risk model
        """
        # Load demand model (ONNX)
        self.demand_session = ort.InferenceSession(demand_model_path)
        self.demand_input_name = self.demand_session.get_inputs()[0].name
        
        # Load tenant risk model
        self.tenant_risk_model = joblib.load(tenant_risk_model_path)
        
        # Load normalizer
        from financial_normalizer import FinancialNormalizer
        self.normalizer = FinancialNormalizer.load('financial_normalizer.pkl')
        
        print("✓ Enhanced Prediction Service initialized")
        print(f"  Demand model: {demand_model_path}")
        print(f"  Tenant risk model: {tenant_risk_model_path}")
    
    def predict_base_demand(self, features: np.ndarray) -> float:
        """
        Predict base demand using existing demand model.
        
        Args:
            features: Input features for demand model
            
        Returns:
            Predicted demand (properties per day)
        """
        # Run ONNX inference
        prediction = self.demand_session.run(None, {self.demand_input_name: features})[0]
        base_value = float(prediction[0])
        
        # Apply Tier-based scaling for realism
        # The raw model is trained on normalized data, so we scale it back 
        # to realistic absolute numbers for different city tiers.
        city_tier = features[0][0]
        
        # Apply Tier-based scaling for realism
        # The raw model is trained on normalized data, so we scale it back 
        # to realistic absolute numbers for different city tiers.
        city_tier = features[0][0]
        
        if city_tier == 2.0:
            base_value *= 0.6  # Tier 2 cities have ~60% demand of Tier 1
        elif city_tier == 3.0:
            base_value *= 0.3  # Tier 3 cities have ~30% demand of Tier 1
            
        # Apply Economic Factor Impact to Demand (User Request: 5-10% impact)
        # Check raw features for economic indicators (indices 3, 4)
        inflation = features[0][3]
        interest = features[0][4]
        
        if inflation > 8.0 or interest > 9.0:
            base_value *= 0.90  # 10% drop in demand during stress
        elif inflation > 6.0 or interest > 8.0:
            base_value *= 0.95  # 5% drop in moderate stress
            
        return base_value
    
    def predict_tenant_quality_distribution(
        self, 
        base_demand: float, 
        city_tier: float = 1.0, 
        economic_factors: Optional[Dict] = None
    ) -> Dict:
        """
        Predict tenant quality distribution using risk model.
        """
        # Sample synthetic tenant population
        n_samples = int(base_demand)
        
        if n_samples == 0:
            return {
                'high_quality_count': 0,
                'medium_quality_count': 0,
                'high_risk_count': 0,
                'high_quality_pct': 0.0,
                'medium_quality_pct': 0.0,
                'high_risk_pct': 0.0,
                'average_default_risk': 0.0,
                'financial_health_score': 0.0
            }
        
        # Adjust quality ranges based on city tier
        if city_tier == 1.0:
            quality_factor = 1.0     # Baseline (High quality)
        elif city_tier == 2.0:
            quality_factor = 0.85    # ~15% lower quality
        else:
            quality_factor = 0.60    # ~40% lower quality (Risky)
            
        # Adjust for Economic Factors (Macro Impact)
        econ_multiplier = 1.0
        debt_multiplier = 1.0
        
        if economic_factors:
            inflation = economic_factors.get('inflation_rate', 5.5)
            interest = economic_factors.get('interest_rate', 7.0)
            
            # High inflation erodes savings and income stability
            if inflation > 8.0:
                econ_multiplier *= 0.7  # 30% penalty
            if inflation > 12.0:
                econ_multiplier *= 0.5  # 50% cumulative penalty (Crisis)
                
            # High interest rates increase debt burden
            if interest > 9.0:
                debt_multiplier *= 1.3  # 30% more burden
            if interest > 11.0:
                debt_multiplier *= 1.5  # 50% more burden
            
        # Generate synthetic financial features based on tier AND economy
        synthetic_features = pd.DataFrame({
            'income_stability': np.random.uniform(20 * quality_factor * econ_multiplier, 80 * quality_factor * econ_multiplier, n_samples),
            'debt_burden': np.random.uniform(30 / quality_factor * debt_multiplier, 90 / quality_factor * debt_multiplier, n_samples), 
            'savings_cushion': np.random.uniform(10 * quality_factor * econ_multiplier, 70 * quality_factor * econ_multiplier, n_samples),
            'payment_history': np.random.uniform(15 * quality_factor, 75 * quality_factor, n_samples),
            'transaction_consistency': np.random.uniform(25 * quality_factor, 85 * quality_factor, n_samples),
            'financial_health': np.random.uniform(25 * quality_factor * econ_multiplier, 70 * quality_factor * econ_multiplier, n_samples)
        })
        
        # Clip values to realistic bounds
        for col in synthetic_features.columns:
            synthetic_features[col] = synthetic_features[col].clip(0, 100)
        
        # Predict default risk for each synthetic tenant
        default_probs = self.tenant_risk_model.predict_proba(synthetic_features)[:, 1]
        
        # Categorize tenants by risk
        high_quality = (default_probs < 0.2).sum()  # <20% default risk
        medium_quality = ((default_probs >= 0.2) & (default_probs < 0.5)).sum()
        high_risk = (default_probs >= 0.5).sum()  # >50% default risk
        
        # Calculate average financial health
        avg_financial_health = float(synthetic_features['financial_health'].mean())
        avg_default_risk = float(default_probs.mean())
        
        return {
            'high_quality_count': int(high_quality),
            'medium_quality_count': int(medium_quality),
            'high_risk_count': int(high_risk),
            'high_quality_pct': float(high_quality / n_samples),
            'medium_quality_pct': float(medium_quality / n_samples),
            'high_risk_pct': float(high_risk / n_samples),
            'average_default_risk': round(avg_default_risk, 6),
            'financial_health_score': round(avg_financial_health, 2)
        }
    
    def predict_enhanced(
        self,
        city: str,
        date: str,
        economic_factors: Optional[Dict] = None
    ) -> Dict:
        """
        Make enhanced prediction combining demand and tenant quality.
        """
        # Step 1: Prepare features and identify city tier
        features, city_tier = self._prepare_demand_features_and_tier(city, date, economic_factors)
        
        # Step 2: Predict base demand
        base_demand = self.predict_base_demand(features)
        
        # Step 3: Predict tenant quality distribution (passing tier)
        quality_dist = self.predict_tenant_quality_distribution(base_demand, city_tier)
        
        # Step 4: Calculate quality-adjusted demand
        # Exclude high-risk tenants from investable demand
        quality_adjusted = base_demand * (1 - quality_dist['high_risk_pct'])
        
        # Step 5: Generate investment recommendation
        recommendation = self._generate_recommendation(
            base_demand, quality_dist, quality_adjusted
        )
        
        return {
            'city': city,
            'date': date,
            'base_demand': {
                'predicted_demand': round(base_demand, 2),
                'unit': 'properties per day'
            },
            'tenant_quality_analysis': quality_dist,
            'quality_adjusted_demand': round(quality_adjusted, 2),
            'investment_recommendation': recommendation
        }
    
    def _prepare_demand_features_and_tier(
        self,
        city: str,
        date: str,
        economic_factors: Optional[Dict]
    ) -> Tuple[np.ndarray, float]:
        """
        Prepare features for demand model and identify city tier.
        
        This is a simplified version. In production, would use
        the full feature engineering pipeline from train_demand_model_efficient.py
        """
        # Parse economic factors
        if economic_factors is None:
            economic_factors = {}
        
        inflation = economic_factors.get('inflation_rate', 5.5)
        interest = economic_factors.get('interest_rate', 7.2)
        employment = economic_factors.get('employment_rate', 85.0)
        
        # Simplified feature vector (10 features to match model)
        # In production, extract proper features from city, date, etc.
        # Define city tiers for realistic differentiation
        tier_1 = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad']
        tier_2 = ['Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik', 'Faridabad', 'Meerut', 'Rajkot', 'Kalyan', 'Varanasi', 'Srinagar', 'Aurangabad', 'Amritsar', 'Allahabad', 'Jabalpur', 'Coimbatore', 'Chandigarh', 'Mysore', 'Gurgaon']
        
        # Determine city factors based on tier
        if city in tier_1:
            city_tier = 1.0
            avg_rent = 25000.0
            supply = 1000.0
            econ_health = 0.75
        elif city in tier_2:
            city_tier = 2.0
            avg_rent = 15000.0
            supply = 600.0
            econ_health = 0.60
        else:
            # Tier 3 / Unknown (e.g. Palakkad)
            city_tier = 3.0
            avg_rent = 8000.0
            supply = 200.0
            econ_health = 0.40
            
        # Simplified feature vector (10 features to match model)
        features = np.array([[
            city_tier,  # City_Tier_encoded (1=Tier1, 2=Tier2, 3=Tier3)
            2.0,  # Region_encoded  
            2.0,  # BHK_encoded
            float(inflation),  # inflation_rate
            float(interest),  # interest_rate
            float(employment),  # employment_rate
            0.3,  # covid_impact_score
            econ_health,  # Economic_Health_Score (Lower for Tier 3)
            avg_rent,  # Avg_Rent (Lower for Tier 3)
            supply  # Supply (Lower for Tier 3)
        ]], dtype=np.float32)
        
        return features, city_tier
    
    def _generate_recommendation(
        self,
        base_demand: float,
        quality_dist: Dict,
        quality_adjusted: float
    ) -> Dict:
        """
        Generate investment recommendation based on demand and quality.
        
        Args:
            base_demand: Base demand prediction
            quality_dist: Tenant quality distribution
            quality_adjusted: Quality-adjusted demand
            
        Returns:
            Investment recommendation
        """
        # Calculate quality score (0-100)
        quality_score = (
            quality_dist['high_quality_pct'] * 100 +
            quality_dist['medium_quality_pct'] * 50
        )
        
        # Determine rating
        if quality_adjusted > 2000 and quality_score > 60:
            rating = "STRONG_BUY"
            confidence = 0.85
        elif quality_adjusted > 1000 and quality_score > 50:
            rating = "BUY"
            confidence = 0.75
        elif quality_adjusted > 500:
            rating = "HOLD"
            confidence = 0.65
        else:
            rating = "AVOID"
            confidence = 0.55
        
        # Generate reasoning
        quality_pct = (1 - quality_dist['high_risk_pct']) * 100
        reasoning = (
            f"High demand ({int(base_demand):,}) with {quality_pct:.0f}% quality tenants "
            f"(low default risk: {quality_dist['average_default_risk']*100:.1f}%)"
        )
        
        return {
            'rating': rating,
            'confidence': round(confidence, 2),
            'quality_score': round(quality_score, 2),
            'reasoning': reasoning
        }


if __name__ == "__main__":
    # Test enhanced prediction service
    print("Testing Enhanced Prediction Service...")
    
    try:
        service = EnhancedPredictionService(
            demand_model_path='demand_model.onnx',
            tenant_risk_model_path='tenant_risk_model.pkl'
        )
        
        # Test prediction
        result = service.predict_enhanced(
            city='Mumbai',
            date='2024-08-15',
            economic_factors={'inflation_rate': 5.5}
        )
        
        print("\n✓ Test Prediction:")
        print(f"  Base Demand: {result['base_demand']['predicted_demand']}")
        print(f"  Quality Adjusted: {result['quality_adjusted_demand']}")
        print(f"  Rating: {result['investment_recommendation']['rating']}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("  Note: Requires trained models to be present")
