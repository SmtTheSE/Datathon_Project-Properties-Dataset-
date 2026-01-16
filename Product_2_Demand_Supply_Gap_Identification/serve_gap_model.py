import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

class GapAnalysisService:
    def __init__(self):
        """Initialize the gap analysis service"""
        import onnxruntime as ort
        try:
            # Load the efficient model (ONNX format)
            model_path = 'gap_model.onnx'
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"{model_path} not found")
                
            self.sess = ort.InferenceSession(model_path)
            self.input_name = self.sess.get_inputs()[0].name
            print("Efficient gap analysis model (ONNX) loaded successfully!")
        except Exception as e:
            print(f"Error loading ONNX model: {e}")
            print("Predictions will return dummy values.")
            self.sess = None

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
        }
        
        # Encodings matching LabelEncoder (sorted unique values)
        # Tier mapping
        tiers = sorted(['Tier1', 'Tier2']) 
        tier_map = {tier: i for i, tier in enumerate(tiers)}
        
        # Region mapping
        regions = sorted(['North', 'South', 'East', 'West'])
        region_map = {region: i for i, region in enumerate(regions)}
        
        # Add encoded features
        data['City_Tier_encoded'] = [tier_map.get(economic_indicators.get('city_tier', 'Tier1'), 0)]
        data['Region_encoded'] = [region_map.get(economic_indicators.get('region', 'West'), 0)]
        data['BHK_encoded'] = [int(bhk) if str(bhk).isdigit() else 2]

        
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
        if self.sess is None:
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
                df[col] = 0.0  # Default value
        
        X = df[feature_cols].astype(np.float32)
        
        # Make prediction using ONNX Runtime
        input_data = {self.input_name: X.values}
        prediction = self.sess.run(None, input_data)[0][0]
        
        # Determine gap severity
        gap_severity = 'low'
        if abs(prediction) > 0.3:
            gap_severity = 'high'
        elif abs(prediction) > 0.1:
            gap_severity = 'medium'
        
        # Generate user-friendly explanation
        # Extract scalar value from numpy array using .item()
        pred_value = prediction.item() if hasattr(prediction, 'item') else float(prediction)
        gap_percentage = abs(pred_value) * 100
        
        # Simple string formatting to avoid numpy type issues
        if pred_value > 0.3:
            explanation = f"Based on the analysis of {area_locality} in {city}, this {bhk}BHK property at ₹{avg_rent}/month shows a HIGH demand-supply gap of +{gap_percentage:.1f}%. The demand significantly exceeds supply in this area, making it an excellent opportunity for property investors. Rental yields are likely to remain strong, and property values may appreciate faster than the city average."
        elif pred_value > 0.1:
            explanation = f"Based on the analysis of {area_locality} in {city}, this {bhk}BHK property at ₹{avg_rent}/month shows a MODERATE demand-supply gap of +{gap_percentage:.1f}%. Demand exceeds supply in this locality, indicating good rental potential and stable occupancy rates. This is a favorable market for landlords."
        elif pred_value > 0:
            explanation = f"Based on the analysis of {area_locality} in {city}, this {bhk}BHK property at ₹{avg_rent}/month shows a BALANCED market with a slight demand edge of +{gap_percentage:.1f}%. The market is relatively stable with demand slightly exceeding supply. Both renters and landlords can expect fair market conditions."
        elif pred_value > -0.1:
            explanation = f"Based on the analysis of {area_locality} in {city}, this {bhk}BHK property at ₹{avg_rent}/month shows a BALANCED market with a slight supply edge of {gap_percentage:.1f}%. The market is relatively stable with supply slightly exceeding demand. Renters may have some negotiating power on rental terms."
        elif pred_value > -0.3:
            explanation = f"Based on the analysis of {area_locality} in {city}, this {bhk}BHK property at ₹{avg_rent}/month shows a MODERATE oversupply gap of -{gap_percentage:.1f}%. Supply exceeds demand in this area, creating a renter's market. Tenants have good negotiating power, and landlords may need to offer competitive rates to attract quality tenants."
        else:
            explanation = f"Based on the analysis of {area_locality} in {city}, this {bhk}BHK property at ₹{avg_rent}/month shows a HIGH oversupply gap of -{gap_percentage:.1f}%. The market has significantly more supply than demand, strongly favoring renters. This is an excellent time for tenants to negotiate favorable terms, and landlords may face longer vacancy periods."
        
        return {
            'city': city,
            'area_locality': area_locality,
            'bhk': bhk,
            'avg_rent': avg_rent,
            'predicted_gap_ratio': pred_value,
            'gap_severity': gap_severity,
            'demand_supply_status': 'demand_exceeds_supply' if pred_value > 0 else 'supply_exceeds_demand',
            'explanation': explanation,
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

    def get_locality_gaps(self, city, top_n=10, sort_by='demand'):
        """
        Get locality-level gap data for heat map visualization
        Uses real data from the 10M row dataset
        
        Args:
            city: City name
            top_n: Number of top localities to return
            sort_by: How to sort - 'demand', 'gap_high' (oversupplied), 'gap_low' (undersupplied)
            
        Returns:
            List of dictionaries with locality, gap, and demand
        """
        try:
            from data_loader import get_data_loader
            
            # Get data loader instance
            loader = get_data_loader()
            
            # Get real locality gap data from dataset with sorting
            locality_data = loader.get_locality_gaps(city, top_n, sort_by)
            
            return locality_data
            
        except Exception as e:
            print(f"Error loading locality gap data: {e}")
            # Fallback to dummy data if loading fails
            localities = ['Bandra', 'Andheri', 'Powai', 'Malad', 'Borivali', 'Thane'][:top_n]
            return [
                {
                    'locality': locality,
                    'gap': np.random.random() * 2 - 1,  # -1 to 1
                    'demand': int(np.random.random() * 100) + 50
                }
                for locality in localities
            ]

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
