import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from sklearn.preprocessing import LabelEncoder, StandardScaler

class GapModelServer:
    """
    Serve the demand-supply gap identification model.
    """
    
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.label_encoder = None
        self.scaler = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model, feature columns, label encoder, and scaler."""
        model_path = '/tmp/gap_model.pkl'
        feature_path = '/tmp/gap_feature_columns.pkl'
        le_path = '/tmp/gap_label_encoder.pkl'
        scaler_path = '/tmp/gap_scaler.pkl'
        
        if not os.path.exists(model_path) or not os.path.exists(feature_path) or not os.path.exists(le_path) or not os.path.exists(scaler_path):
            raise FileNotFoundError("Model files not found. Please train the model first.")
        
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
            
        with open(feature_path, 'rb') as f:
            self.feature_columns = pickle.load(f)
            
        with open(le_path, 'rb') as f:
            self.label_encoder = pickle.load(f)
            
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
            
        print("Model loaded successfully.")
    
    def prepare_features(self, city, area_locality, bhk, year, month, supply, avg_rent):
        """
        Prepare features for prediction.
        """
        # Create a dataframe with the input
        data = pd.DataFrame({
            'City': [city],
            'Area Locality': [area_locality],
            'BHK': [bhk],
            'Year': [year],
            'Month': [month],
            'Supply': [supply],
            'Avg_Rent': [avg_rent],
            'Median_Rent': [avg_rent],  # Simplified assumption
            'Std_Rent': [avg_rent * 0.2],  # Simplified assumption
            'Min_Rent': [avg_rent * 0.8],  # Simplified assumption
            'Max_Rent': [avg_rent * 1.2],  # Simplified assumption
            'Day': [15],  # Mid-month default
            'DayOfWeek': [3],  # Thursday default
            'WeekOfYear': [25],  # Mid-year default
            'Quarter': [2],  # Q2 default
            'Demand_Proxy': [supply * 1.1],  # Simplified assumption
            'Gap': [supply * 0.1],  # Simplified assumption
            'Supply_Momentum': [0],  # Default
            'Supply_MA3': [supply],  # Default
            'Supply_MA6': [supply],  # Default
            'Supply_Trend': [0],  # Default
            'Rent_Change': [0],  # Default
            'Rent_MA3': [avg_rent],  # Default
            'Rent_Volatility': [0.1],  # Default
            'Monthly_Supply_Index': [supply],  # Default
            'Seasonal_Supply_Factor': [1.0],  # Default
            'City_Avg_Rent': [avg_rent],  # Default
            'City_Rent_Std': [avg_rent * 0.1],  # Default
            'Rent_Relative_To_City': [1.0]  # Default
        })
        
        # Add derived features
        data['Gap_Ratio'] = data['Gap'] / (data['Demand_Proxy'] + 1e-8)
        
        # Location encoding features
        city_tier_mapping = {
            'Mumbai': 'Tier1', 'Delhi': 'Tier1', 'Bangalore': 'Tier1', 'Hyderabad': 'Tier1', 
            'Chennai': 'Tier1', 'Kolkata': 'Tier1', 'Pune': 'Tier2', 'Ahmedabad': 'Tier2',
            'Jaipur': 'Tier2', 'Surat': 'Tier2', 'Kanpur': 'Tier2', 'Lucknow': 'Tier2',
            'Nagpur': 'Tier2', 'Indore': 'Tier2', 'Bhopal': 'Tier2', 'Patna': 'Tier2',
            'Vadodara': 'Tier2', 'Ghaziabad': 'Tier2', 'Visakhapatnam': 'Tier2', 'Agra': 'Tier2',
            'Thane': 'Tier2', 'Kalyan': 'Tier2', 'Varanasi': 'Tier2', 'Raipur': 'Tier2',
            'Aurangabad': 'Tier2', 'Meerut': 'Tier2', 'Jabalpur': 'Tier2', 'Vijaywada': 'Tier2',
            'Gwalior': 'Tier2', 'Madurai': 'Tier2', 'Amritsar': 'Tier2', 'Allahabad': 'Tier2',
            'Coimbatore': 'Tier2', 'Ranchi': 'Tier2', 'Jalandhar': 'Tier2', 'Tiruchirappalli': 'Tier2'
        }
        
        region_mapping = {
            'Mumbai': 'West', 'Delhi': 'North', 'Bangalore': 'South', 'Hyderabad': 'South',
            'Chennai': 'South', 'Kolkata': 'East', 'Pune': 'West', 'Ahmedabad': 'West',
            'Jaipur': 'North', 'Surat': 'West', 'Kanpur': 'North', 'Lucknow': 'North',
            'Nagpur': 'West', 'Indore': 'West', 'Bhopal': 'West', 'Patna': 'East',
            'Vadodara': 'West', 'Ghaziabad': 'North', 'Visakhapatnam': 'East', 'Agra': 'North',
            'Thane': 'West', 'Kalyan': 'West', 'Varanasi': 'North', 'Raipur': 'West',
            'Aurangabad': 'West', 'Meerut': 'North', 'Jabalpur': 'West', 'Vijaywada': 'South',
            'Gwalior': 'North', 'Madurai': 'South', 'Amritsar': 'North', 'Allahabad': 'North',
            'Coimbatore': 'South', 'Ranchi': 'East', 'Jalandhar': 'North', 'Tiruchirappalli': 'South'
        }
        
        data['City_Tier'] = data['City'].map(city_tier_mapping).fillna('Tier2')
        data['Region'] = data['City'].map(region_mapping).fillna('West')
        
        # One-hot encode categorical variables
        data_encoded = pd.get_dummies(data, columns=['City', 'City_Tier', 'Region', 'BHK'], 
                                     prefix=['City', 'Tier', 'Region', 'BHK'])
        
        # Encode Area Locality using the fitted label encoder
        try:
            area_encoded = self.label_encoder.transform([area_locality])
        except ValueError:
            # If area_locality is not in the fitted encoder, use a default value
            print(f"Warning: Area '{area_locality}' not in training data. Using default encoding.")
            area_encoded = [0]  # Default to 0 if not in training set
        
        data_encoded['Area_Locality_Encoded'] = area_encoded
        
        # Ensure all feature columns are present
        for col in self.feature_columns:
            if col not in data_encoded.columns:
                data_encoded[col] = 0
        
        # Reorder columns to match training
        data_encoded = data_encoded[self.feature_columns]
        
        # Scale features
        data_scaled = pd.DataFrame(self.scaler.transform(data_encoded), columns=data_encoded.columns)
        
        return data_scaled
    
    def predict_gap(self, city, area_locality, bhk, year, month, supply, avg_rent):
        """
        Predict demand-supply gap for given parameters.
        """
        # Prepare features
        features = self.prepare_features(city, area_locality, bhk, year, month, supply, avg_rent)
        
        # Make prediction
        gap_ratio = self.model.predict(features)[0]
        
        # Calculate absolute gap
        demand_proxy = supply * (1 + gap_ratio)
        absolute_gap = demand_proxy - supply
        
        return {
            'city': city,
            'area_locality': area_locality,
            'bhk': bhk,
            'year': year,
            'month': month,
            'supply': supply,
            'demand_proxy': demand_proxy,
            'absolute_gap': absolute_gap,
            'gap_ratio': gap_ratio,
            'interpretation': self._interpret_gap(gap_ratio)
        }
    
    def _interpret_gap(self, gap_ratio):
        """
        Provide interpretation of the gap ratio.
        """
        if gap_ratio > 0.2:
            return "High demand, significant undersupply - Strong investment opportunity"
        elif gap_ratio > 0.05:
            return "Moderate demand surplus - Good investment potential"
        elif gap_ratio > -0.05:
            return "Balanced market - Stable conditions"
        elif gap_ratio > -0.2:
            return "Slight oversupply - Caution advised"
        else:
            return "Significant oversupply - Avoid investment"

def load_gap_model():
    """
    Load and return the gap model server.
    """
    try:
        return GapModelServer()
    except Exception as e:
        print(f"Error loading gap model: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    model_server = load_gap_model()
    if model_server:
        result = model_server.predict_gap(
            city="Mumbai",
            area_locality="Andheri",
            bhk="2",
            year=2024,
            month=6,
            supply=150,
            avg_rent=25000
        )
        print("Sample prediction:")
        print(result)