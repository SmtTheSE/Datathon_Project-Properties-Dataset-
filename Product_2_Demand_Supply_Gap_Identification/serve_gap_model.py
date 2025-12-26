import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

class GapAnalysisService:
    def __init__(self):
        """Initialize the gap analysis service"""
        try:
            # Load the efficient model and scaler
            self.model = joblib.load('gap_analysis_model_efficient.pkl')
            self.scaler = joblib.load('feature_scaler_gap_efficient.pkl')
            print("Efficient gap analysis model loaded successfully!")
        except FileNotFoundError:
            print("Efficient model not found, attempting to load original model...")
            try:
                self.model = joblib.load('gap_analysis_model.pkl')
                self.scaler = joblib.load('feature_scaler_gap.pkl')
                print("Original model loaded successfully!")
            except FileNotFoundError:
                print("No model found. Initialize with a dummy model for testing.")
                self.model = None
                self.scaler = None

    def prepare_single_prediction_features(self, city, area_locality, bhk, avg_rent, economic_indicators):
        """Prepare features for a single gap prediction"""
        # Create a DataFrame with single row
        data = {
            'Avg_Rent': [avg_rent],
            'Std_Rent': [avg_rent * 0.2],  # Placeholder standard deviation
            'Supply': [50],  # Placeholder supply value
            'inflation_rate': [economic_indicators.get('inflation_rate', 6.0)],
            'interest_rate': [economic_indicators.get('interest_rate', 7.0)],
            'employment_rate': [economic_indicators.get('employment_rate', 85.0)],
            'covid_impact_score': [economic_indicators.get('covid_impact_score', 0.1)],
            'Economic_Health_Score': [economic_indicators.get('economic_health_score', 0.8)],
            'City_Tier_encoded': [hash(economic_indicators.get('city_tier', 'Tier1')) % 100],
            'Region_encoded': [hash(economic_indicators.get('region', 'West')) % 100],
            'BHK_encoded': [int(bhk) if str(bhk).isdigit() else 2]  # Default to 2 BHK
        }
        
        # Add engineered features
        df = pd.DataFrame(data)
        df['Rent_to_Supply_Ratio'] = df['Avg_Rent'] / (df['Supply'] + 1)
        df['Economic_Factor'] = (
            df['employment_rate'] * 0.4 + 
            (100 - df['interest_rate']) * 0.3 + 
            (100 - df['inflation_rate']) * 0.3
        )
        
        return df

    def predict_gap(self, city, area_locality, bhk, avg_rent, economic_indicators=None):
        """Predict demand-supply gap for a given property and location"""
        if self.model is None:
            # Return a dummy prediction if no model is available
            return {
                'city': city,
                'area_locality': area_locality,
                'bhk': bhk,
                'avg_rent': avg_rent,
                'predicted_gap_ratio': 0.1,  # Default value
                'gap_severity': 'medium',
                'message': 'Dummy prediction - model not loaded'
            }
        
        if economic_indicators is None:
            economic_indicators = {}
        
        # Prepare features
        df = self.prepare_single_prediction_features(city, area_locality, bhk, avg_rent, economic_indicators)
        
        # Get feature columns (should match training)
        feature_cols = [
            'Avg_Rent', 'Std_Rent', 'Supply', 
            'inflation_rate', 'interest_rate', 'employment_rate', 
            'covid_impact_score', 'Economic_Health_Score',
            'Rent_to_Supply_Ratio', 'Economic_Factor',
            'City_Tier_encoded', 'Region_encoded', 'BHK_encoded'
        ]
        
        # Ensure all required columns exist
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0  # Default value
        
        X = df[feature_cols]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        prediction = self.model.predict(X_scaled)[0]
        
        # Determine gap severity
        gap_severity = 'low'
        if abs(prediction) > 0.3:
            gap_severity = 'high'
        elif abs(prediction) > 0.1:
            gap_severity = 'medium'
        
        return {
            'city': city,
            'area_locality': area_locality,
            'bhk': bhk,
            'avg_rent': avg_rent,
            'predicted_gap_ratio': float(prediction),
            'gap_severity': gap_severity,
            'demand_supply_status': 'demand_exceeds_supply' if prediction > 0 else 'supply_exceeds_demand',
            'economic_indicators_used': economic_indicators
        }

    def predict_batch_gaps(self, gap_requests):
        """Predict demand-supply gaps for multiple requests"""
        results = []
        for request in gap_requests:
            result = self.predict_gap(
                request['city'],
                request['area_locality'],
                request['bhk'],
                request['avg_rent'],
                request.get('economic_indicators', {})
            )
            results.append(result)
        return results

# Example usage
if __name__ == "__main__":
    service = GapAnalysisService()
    
    # Example prediction
    result = service.predict_gap(
        city="Mumbai",
        area_locality="Bandra",
        bhk=2,
        avg_rent=25000,
        economic_indicators={
            'inflation_rate': 5.5,
            'interest_rate': 6.5,
            'employment_rate': 87.0,
            'covid_impact_score': 0.05,
            'economic_health_score': 0.85,
            'city_tier': 'Tier1',
            'region': 'West'
        }
    )
    
    print("Prediction result:", result)
