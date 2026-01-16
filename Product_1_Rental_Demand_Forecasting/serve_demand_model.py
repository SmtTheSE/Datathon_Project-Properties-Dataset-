"""
Enhanced Model Serving Module for Rental Demand Forecasting Tool

This module prepares the trained model for integration with a web application.
It provides functions to load the enhanced model and make predictions for rental demand
based on city and date inputs, incorporating external economic factors.
"""

import pandas as pd
import numpy as np
import lightgbm as lgb
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

# Load city classification data
TIER_1 = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad']
SOUTH_CITIES = ['Bangalore', 'Chennai', 'Hyderabad', 'Kochi', 'Coimbatore', 'Mysore']
WEST_CITIES = ['Mumbai', 'Pune', 'Ahmedabad', 'Surat', 'Indore']
NORTH_CITIES = ['Delhi', 'Chandigarh', 'Jaipur', 'Lucknow', 'Kanpur']
EAST_CITIES = ['Kolkata', 'Bhubaneswar', 'Patna', 'Ranchi']
HOLIDAYS_2022 = [
    '2022-04-10', # Ram Navami
    '2022-04-14', # Ambedkar Jayanti
    '2022-04-15', # Good Friday
    '2022-05-03', # Eid-ul-Fitr
    '2022-05-16', # Buddha Purnima
    '2022-07-10'  # Eid-ul-Adha
]

class RentalDemandForecaster:
    """
    A class to forecast rental demand based on trained enhanced LightGBM model.
    
    This class provides methods to:
    1. Load a pre-trained enhanced model
    2. Generate features for prediction including external economic factors
    3. Make demand forecasts
    """
    
    def __init__(self, model_path: str = "/tmp/enhanced_demand_forecast_model.txt"):
        """
        Initialize the forecaster with a trained enhanced model.
        
        Args:
            model_path (str): Path to the trained enhanced model file
        """
        if model_path and os.path.exists(model_path):
            self.model = lgb.Booster(model_file=model_path)
        else:
            self.model = None
            print(f"Warning: Enhanced model file not found at {model_path}. Predictions will not work until a model is loaded.")
            
        # Load features list
        features_path = '/tmp/demand_forecast_features.pkl'
        if os.path.exists(features_path):
            with open(features_path, 'rb') as f:
                self.features = pickle.load(f)
        else:
            # Fallback to basic features if enhanced features not available
            self.features = [
                'DayOfWeek', 'Month', 'Quarter', 'IsWeekend',
                'inflation_rate', 'interest_rate', 'employment_rate', 'covid_impact_score',
                'Demand_Lag_1', 'Demand_Lag_7', 'Demand_Lag_14',
                'Demand_Rolling_Mean_7', 'Demand_Rolling_Mean_14', 'Demand_Rolling_Mean_30',
                'Demand_Rolling_Std_7', 'Demand_Rolling_Std_14', 'Demand_Rolling_Std_30',
                'Growth_Rate_7'
            ]
    
    def _generate_features(self, city: str, date: str, economic_factors: Dict[str, float] = None) -> pd.DataFrame:
        """
        Generate features for prediction based on city, date, and economic factors.
        
        Args:
            city (str): The city for which to generate features
            date (str): The date for which to generate features (format: YYYY-MM-DD)
            economic_factors (Dict[str, float]): Economic factors (inflation, interest, employment, etc.)
            
        Returns:
            pd.DataFrame: DataFrame with generated features
        """
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        
        # Default economic factors if not provided
        if economic_factors is None:
            economic_factors = {
                'inflation_rate': 6.0,  # Default India inflation rate
                'interest_rate': 7.5,   # Default interest rate
                'employment_rate': 80.0, # Default employment rate
                'covid_impact_score': 0.1, # Default low impact
                'gdp_growth': 7.0       # Default GDP growth
            }
        
        # Generate base features
        features = {
            'DayOfWeek': date_obj.weekday(),
            'Month': date_obj.month,
            'Day': date_obj.day,
            'Quarter': (date_obj.month - 1) // 3 + 1,
            'IsWeekend': 1 if date_obj.weekday() >= 5 else 0,
            'inflation_rate': economic_factors.get('inflation_rate', 6.0),
            'interest_rate': economic_factors.get('interest_rate', 7.5),
            'employment_rate': economic_factors.get('employment_rate', 80.0),
            'covid_impact_score': economic_factors.get('covid_impact_score', 0.1),
            'gdp_growth': economic_factors.get('gdp_growth', 7.0),
            'Economic_Health_Score': (
                economic_factors.get('employment_rate', 80.0) * 0.4 + 
                (100 - economic_factors.get('interest_rate', 7.5)) * 0.3 + 
                (100 - economic_factors.get('inflation_rate', 6.0)) * 0.3
            ),
            'IsMonsoon': 1 if date_obj.month in [6, 7, 8, 9] else 0,
            'IsSummer': 1 if date_obj.month in [3, 4, 5] else 0,
            'IsWinter': 1 if date_obj.month in [11, 12, 1, 2] else 0
        }
        
        # Add lag and rolling features (using defaults since we don't have historical data for this specific prediction)
        for lag in [1, 7, 14]:
            features[f'Demand_Lag_{lag}'] = 100.0  # Default value
        
        for window in [7, 14, 30]:
            features[f'Demand_Rolling_Mean_{window}'] = 100.0  # Default value
            features[f'Demand_Rolling_Std_{window}'] = 10.0    # Default value
        
        features['Growth_Rate_7'] = 0.0  # Default growth rate
        
        # Create DataFrame
        df = pd.DataFrame([features])
        
        return df
    
    def predict_demand(self, city: str, date: str, economic_factors: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Predict rental demand for a specific city and date.
        
        Args:
            city (str): The city for which to predict demand
            date (str): The date for which to predict demand (format: YYYY-MM-DD)
            economic_factors (Dict[str, float]): Economic factors to consider
            
        Returns:
            Dict[str, Any]: Prediction result with demand and confidence
        """
        if self.model is None:
            return {
                "error": "Model not loaded. Please ensure the enhanced model file exists.",
                "predicted_demand": None,
                "confidence_interval": None
            }
        
        try:
            # Generate features
            features_df = self._generate_features(city, date, economic_factors)
            
            # Ensure all required features are present
            for feature in self.features:
                if feature not in features_df.columns:
                    features_df[feature] = 0  # Default value for missing features
            
            # Reorder features to match training
            features_df = features_df[self.features]
            
            # Make prediction
            prediction = self.model.predict(features_df)[0]
            
            # Ensure prediction is positive
            prediction = max(0, prediction)
            
            # Calculate a basic confidence interval based on model performance
            # In a real implementation, this would use quantile regression or ensemble methods
            confidence_interval = {
                "lower": max(0, prediction * 0.8),  # 20% lower bound
                "upper": prediction * 1.2          # 20% upper bound
            }
            
            return {
                "city": city,
                "date": date,
                "predicted_demand": float(prediction),
                "confidence_interval": confidence_interval
            }
        except Exception as e:
            return {
                "error": f"Prediction failed: {str(e)}",
                "predicted_demand": None,
                "confidence_interval": None
            }
    
    def predict_batch(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict rental demand for multiple requests.
        
        Args:
            requests: List of prediction requests with city, date, and optional economic factors
            
        Returns:
            Dict[str, Any]: Batch prediction results
        """
        predictions = []
        
        for req in requests:
            city = req.get("city")
            date = req.get("date")
            economic_factors = req.get("economic_factors", None)
            
            result = self.predict_demand(city, date, economic_factors)
            predictions.append(result)
        
        return {"predictions": predictions}


# Example usage
if __name__ == "__main__":
    # Initialize the forecaster
    forecaster = RentalDemandForecaster()
    
    # Example prediction
    result = forecaster.predict_demand(
        city="Mumbai", 
        date="2023-06-15",
        economic_factors={
            "inflation_rate": 6.5,
            "interest_rate": 7.0,
            "employment_rate": 82.0,
            "covid_impact_score": 0.05,
            "gdp_growth": 7.2
        }
    )
    
    print("Prediction result:", result)

"""
Efficient Demand Forecasting Model Service
Provides fast predictions for rental demand forecasting
"""
import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

class DemandForecastService:
    def __init__(self):
        """Initialize the demand forecasting service"""
        import onnxruntime as ort
        try:
            # Load the efficient model (ONNX format)
            model_path = 'demand_model.onnx'
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"{model_path} not found")
                
            self.sess = ort.InferenceSession(model_path)
            self.input_name = self.sess.get_inputs()[0].name
            self.input_shape = self.sess.get_inputs()[0].shape
            print("Efficient demand forecasting model (ONNX) loaded successfully!")
        except Exception as e:
            print(f"Error loading ONNX model: {e}")
            print("Predictions will return dummy values.")
            self.sess = None

    def prepare_single_prediction_features(self, city, year, month, economic_indicators):
        """Prepare features for a single prediction"""
        # Create a DataFrame with single row
        data = {
            'Year': [year],
            'Month': [month],
            'inflation_rate': [economic_indicators.get('inflation_rate', 6.0)],
            'interest_rate': [economic_indicators.get('interest_rate', 7.0)],
            'employment_rate': [economic_indicators.get('employment_rate', 85.0)],
            'covid_impact_score': [economic_indicators.get('covid_impact_score', 0.1)],
            'Economic_Health_Score': [economic_indicators.get('economic_health_score', 0.8)],
            'Month_Sin': [np.sin(2 * np.pi * month / 12)],
            'Month_Cos': [np.cos(2 * np.pi * month / 12)],
        }
        
        # City encoding matching LabelEncoder (sorted alphabetical order)
        cities_list = sorted([
            "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", 
            "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur",
            "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna", "Vadodara",
            "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
            "Rajkot", "Kalyan", "Varanasi", "Srinagar", "Aurangabad", "Amritsar",
            "Allahabad", "Jabalpur", "Coimbatore", "Chandigarh", "Mysore", "Gurgaon",
            "Jodhpur", "Madurai", "Ranchi", "Bhubaneswar", "Kochi", "Jalandhar",
            "Surat" 
        ])
        
        # Create mapping
        city_map = {city: i for i, city in enumerate(cities_list)}
        
        # Add encoded city
        data['City_encoded'] = [city_map.get(city, -1)]
        
        df = pd.DataFrame(data)
        return df

    def predict_demand(self, city, year, month, economic_indicators=None):
        """Predict rental demand for a given city and time period"""
        if self.sess is None:
            # Return a dummy prediction if no model is available
            return {
                'city': city,
                'year': year,
                'month': month,
                'predicted_demand': 1000,
                'confidence': 'low',
                'message': 'Dummy prediction - model not loaded'
            }
        
        if economic_indicators is None:
            economic_indicators = {}
        
        # Prepare features
        df = self.prepare_single_prediction_features(city, year, month, economic_indicators)
        
        # Get feature columns (should match training)
        feature_cols = [
            'Year', 'Month', 
            'inflation_rate', 'interest_rate', 'employment_rate', 
            'covid_impact_score', 'Economic_Health_Score',
            'Month_Sin', 'Month_Cos',
            'City_encoded'
        ]
        
        # Ensure all required columns exist
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0.0  # Default value
        
        X = df[feature_cols].astype(np.float32)
        
        # Make prediction using ONNX Runtime
        # The scaler is embedded in the ONNX pipeline, so we pass raw features
        input_data = {self.input_name: X.values}
        prediction = self.sess.run(None, input_data)[0][0]
        
        # Ensure prediction is positive
        prediction = max(0, prediction)
        
        return {
            'city': city,
            'year': year,
            'month': month,
            'predicted_demand': int(prediction),
            'confidence': 'high' if prediction > 50 else 'medium',
            'economic_indicators_used': economic_indicators
        }

    def get_historical_demand(self, city, months=12, economic_indicators=None):
        """
        Get historical demand data for the last N months for charting
        Uses real data from the 10M row dataset
        
        Args:
            city: City name
            months: Number of months of historical data (default 12)
            economic_indicators: Optional economic indicators (not used for historical data)
            
        Returns:
            List of dictionaries with month names and demand values
        """
        try:
            from data_loader import get_data_loader
            
            # Get data loader instance
            loader = get_data_loader()
            
            # Get real historical data from dataset
            historical_data = loader.get_historical_demand_by_city(city, months)
            
            print(f"DEBUG: get_historical_demand called for {city}, requested {months} months, got {len(historical_data)} months")
            
            return historical_data
            
        except Exception as e:
            print(f"Error loading historical data: {e}")
            # Fallback to model-based predictions if data loading fails
            from datetime import datetime, timedelta
            
            if economic_indicators is None:
                economic_indicators = {
                    'inflation_rate': 6.0,
                    'interest_rate': 7.0,
                    'employment_rate': 85.0,
                    'covid_impact_score': 0.1,
                    'economic_health_score': 0.8
                }
            
            current_date = datetime.now()
            historical_data = []
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            for i in range(months, 0, -1):
                target_date = current_date - timedelta(days=30 * i)
                year = target_date.year
                month = target_date.month
                
                prediction = self.predict_demand(city, year, month, economic_indicators)
                
                historical_data.append({
                    'month': month_names[month - 1],
                    'demand': prediction['predicted_demand'],
                    'year': year
                })
            
            return historical_data

    def predict_batch_demand(self, demand_requests):
        """Predict rental demand for multiple requests"""
        results = []
        for request in demand_requests:
            result = self.predict_demand(
                request['city'],
                request['year'],
                request['month'],
                request.get('economic_indicators', {})
            )
            results.append(result)
        return results

# Example usage
if __name__ == "__main__":
    service = DemandForecastService()
    
    # Example prediction
    result = service.predict_demand(
        city="Mumbai",
        year=2023,
        month=6,
        economic_indicators={
            'inflation_rate': 5.5,
            'interest_rate': 6.5,
            'employment_rate': 87.0,
            'covid_impact_score': 0.05,
            'economic_health_score': 0.85
        }
    )
    
    print("Prediction result:", result)
