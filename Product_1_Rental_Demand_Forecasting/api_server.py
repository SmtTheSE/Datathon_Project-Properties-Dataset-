"""
REST API Server for Rental Demand Forecasting Tool

This module provides a Flask-based web API to serve rental demand predictions.
It can be easily integrated with frontend web applications.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import onnxruntime as ort
import os
import json
from datetime import datetime
from functools import wraps
import time
import re
from data_loader import get_data_loader
from enhanced_prediction_service import EnhancedPredictionService

# Add the current directory to Python path to import our modules
# sys.path.append(os.path.dirname(os.path.abspath(__file__))) # This line is no longer needed with direct imports

# from serve_demand_model import DemandForecastService # This import is replaced

app = Flask(__name__)
CORS(app)

# Initialize data loader
data_loader = get_data_loader()

# Load ONNX model for base predictions
model_path = os.path.join(os.path.dirname(__file__), 'demand_model.onnx')
ort_session = ort.InferenceSession(model_path)
input_name = ort_session.get_inputs()[0].name

# Initialize enhanced prediction service
try:
    # Define absolute paths for models to ensure Windows compatibility
    base_dir = os.path.dirname(os.path.abspath(__file__))
    demand_model_path = os.path.join(base_dir, 'demand_model.onnx')
    tenant_risk_model_path = os.path.join(base_dir, 'tenant_risk_model.pkl')
    transaction_model_path = os.path.join(base_dir, 'transaction_amount_model.pkl')

    enhanced_service = EnhancedPredictionService(
        demand_model_path=demand_model_path,
        tenant_risk_model_path=tenant_risk_model_path
    )
    enhanced_service_available = True
    print("✓ Enhanced Prediction Service loaded")
except Exception as e:
    enhanced_service_available = False
    print(f"⚠ Enhanced service not available: {e}")

# Import and initialize the base forecaster
from serve_demand_model import DemandForecastService
forecaster = DemandForecastService()

# Rate limiting implementation
REQUEST_COUNT = {}
RATE_LIMIT = 100  # requests per minute
TIME_WINDOW = 60  # seconds

def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time.time()
        
        if client_ip not in REQUEST_COUNT:
            REQUEST_COUNT[client_ip] = []
        
        # Clean old requests
        REQUEST_COUNT[client_ip] = [
            req_time for req_time in REQUEST_COUNT[client_ip] 
            if current_time - req_time < TIME_WINDOW
        ]
        
        # Check if over limit
        if len(REQUEST_COUNT[client_ip]) >= RATE_LIMIT:
            return jsonify({"error": "Rate limit exceeded. Maximum 100 requests per minute."}), 429
        
        # Add current request
        REQUEST_COUNT[client_ip].append(current_time)
        
        return func(*args, **kwargs)
    
    return wrapper

def validate_city(city):
    """Validate city name to prevent injection attacks"""
    if not isinstance(city, str):
        return False
    # Only allow letters, spaces, and hyphens
    if not re.match(r"^[A-Za-z\s\-]+$", city):
        return False
    if len(city) > 50:  # Prevent overly long inputs
        return False
    return True

def validate_date_format(date_str):
    """Validate date format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "rental-demand-forecasting"}), 200

@app.route('/predict', methods=['POST'])
@rate_limit
def predict_demand():
    """
    Predict rental demand for a given city and date.
    
    Expected JSON input:
    {
        "city": "Mumbai",
        "date": "2022-08-15"
    }
    
    Returns:
    {
        "city": "Mumbai",
        "date": "2022-08-15",
        "predicted_demand": 125.5
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        city = data.get('city')
        date_str = data.get('date')
        
        if not city or not date_str:
            return jsonify({"error": "Both 'city' and 'date' are required"}), 400
            
        # Validate city name to prevent injection attacks
        if not validate_city(city):
            return jsonify({"error": "Invalid city name format"}), 400
            
        # Validate date format
        if not validate_date_format(date_str):
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Parse date
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Extract optional economic factors
        economic_factors = data.get('economic_factors')
        
        # Make prediction with enhanced model
        result = forecaster.predict_demand(city, date.year, date.month, economic_factors)
        
        # Return result directly as it matches the expected structure
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/predict/enhanced', methods=['POST'])
@rate_limit
def predict_demand_enhanced():
    """
    Predict rental demand with tenant quality analysis (ENHANCED).
    
    Combines base demand forecasting with tenant financial risk scoring
    to provide quality-adjusted demand predictions.
    
    Expected JSON input:
    {
        "city": "Mumbai",
        "date": "2024-08-15",
        "economic_factors": {
            "inflation_rate": 5.5,
            "interest_rate": 7.2,
            "employment_rate": 85.0
        },
        "include_tenant_quality": true
    }
    
    Returns:
    {
        "city": "Mumbai",
        "date": "2024-08-15",
        "base_demand": {
            "predicted_demand": 2474.71,
            "unit": "properties per day"
        },
        "tenant_quality_analysis": {
            "high_quality_count": 867,
            "medium_quality_count": 1238,
            "high_risk_count": 369,
            "high_quality_pct": 0.35,
            "medium_quality_pct": 0.50,
            "high_risk_pct": 0.15,
            "average_default_risk": 0.152,
            "financial_health_score": 68.5
        },
        "quality_adjusted_demand": 2105.5,
        "investment_recommendation": {
            "rating": "STRONG_BUY",
            "confidence": 0.85,
            "quality_score": 75.0,
            "reasoning": "High demand (2,475) with 85% quality tenants..."
        }
    }
    """
    try:
        # Check if enhanced service is available
        if not enhanced_service_available:
            return jsonify({
                "error": "Enhanced prediction service not available",
                "hint": "Train tenant risk model first: python train_tenant_risk_model.py"
            }), 503
        
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        city = data.get('city')
        date_str = data.get('date')
        
        if not city or not date_str:
            return jsonify({"error": "'city' and 'date' are required"}), 400
        
        # Extract optional economic factors
        economic_factors = data.get('economic_factors')
        
        # Make enhanced prediction
        result = enhanced_service.predict_enhanced(city, date_str, economic_factors)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": f"Enhanced prediction failed: {str(e)}"}), 500

@app.route('/predict/batch', methods=['POST'])
@rate_limit
def predict_demand_batch():
    """
    Predict rental demand for multiple city-date pairs.
    
    Expected JSON input:
    {
        "requests": [
            {"city": "Mumbai", "date": "2022-08-15"},
            {"city": "Delhi", "date": "2022-08-16"}
        ]
    }
    
    Returns:
    {
        "predictions": [
            {"city": "Mumbai", "date": "2022-08-15", "predicted_demand": 125.5},
            {"city": "Delhi", "date": "2022-08-16", "predicted_demand": 98.3}
        ]
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        requests_list = data.get('requests')
        
        if not requests_list:
            return jsonify({"error": "'requests' list is required"}), 400
            
        # Limit batch size to prevent abuse
        if len(requests_list) > 50:
            return jsonify({"error": "Batch size too large. Maximum 50 requests per batch."}), 400
            
        # Validate and parse requests
        parsed_requests = []
        for i, req in enumerate(requests_list):
            city = req.get('city')
            date_str = req.get('date')
            
            if not city or not date_str:
                return jsonify({"error": f"Request {i} must have 'city' and 'date'"}), 400
                
            # Validate city name
            if not validate_city(city):
                return jsonify({"error": f"Invalid city name format in request {i}"}), 400
                
            # Validate date format
            if not validate_date_format(date_str):
                return jsonify({"error": f"Invalid date format in request {i}. Use YYYY-MM-DD"}), 400
                
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                parsed_requests.append({'city': city, 'date': date})
            except ValueError:
                return jsonify({"error": f"Invalid date format in request {i}. Use YYYY-MM-DD"}), 400
        
        # Extract optional economic factors for each request
        for i, req in enumerate(requests_list):
            parsed_requests[i]['economic_factors'] = req.get('economic_factors')
            
        # Prepare requests for batch prediction
        batch_requests = []
        for i, req in enumerate(parsed_requests):
             batch_requests.append({
                 'city': req['city'],
                 'year': req['date'].year,
                 'month': req['date'].month,
                 'economic_indicators': req.get('economic_factors', {})
             })

        # Make batch predictions
        predictions = forecaster.predict_batch_demand(batch_requests)
        
        # Return results
        return jsonify({"predictions": predictions}), 200
        

        
    except Exception as e:
        return jsonify({"error": f"Batch prediction failed: {str(e)}"}), 500

@app.route('/cities', methods=['GET'])
@rate_limit
def get_cities():
    """
    Get list of supported cities.
    
    Returns:
    {
        "cities": ["Mumbai", "Delhi", "Bangalore", ...]
    }
    """
    # Get cities dynamically from the data loader
    try:
        monthly_data = data_loader._load_monthly_data()
        cities = list(monthly_data.keys())
        
        # If no data found (e.g. file missing), fallback to a basic list but log warning
        if not cities:
            print("Warning: No cities found in data loader. Using fallback list.")
            cities = [
                "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", 
                "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur",
                "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna", "Vadodara",
                "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
                "Rajkot", "Kalyan", "Varanasi", "Srinagar", "Aurangabad", "Amritsar",
                "Allahabad", "Jabalpur", "Coimbatore", "Chandigarh", "Mysore", "Gurgaon",
                "Jodhpur", "Madurai", "Ranchi", "Bhubaneswar", "Kochi", "Jalandhar"
            ]
            
        return jsonify({"cities": sorted(cities)}), 200
    except Exception as e:
        print(f"Error fetching dynamic cities: {e}")
        return jsonify({"error": "Failed to load city list"}), 500

@app.route('/historical/<city>', methods=['GET'])
@rate_limit
def get_historical_data(city):
    """
    Get historical demand data for charting from real dataset.
    
    Args:
        city: City name from URL path
        
    Query parameters:
        months: Number of months of historical data (default 12)
    
    Returns:
        {
            "city": "Mumbai",
            "historical_data": [
                {"month": "Jan", "demand": 2450, "year": 2024},
                {"month": "Feb", "demand": 2480, "year": 2024},
                ...
            ]
        }
    """
    try:
        # Validate city name
        if not validate_city(city):
            return jsonify({"error": "Invalid city name format"}), 400
        
        # Get optional months parameter
        months = request.args.get('months', default=12, type=int)
        
        # Limit months to reasonable range
        if months < 1 or months > 24:
            return jsonify({"error": "Months must be between 1 and 24"}), 400
        
        # Get historical data from service (uses real dataset)
        historical_data = forecaster.get_historical_demand(city, months)
        
        return jsonify({
            "city": city,
            "historical_data": historical_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get historical data: {str(e)}"}), 500

@app.route('/info', methods=['GET'])
@rate_limit
def get_model_info():
    """
    Get information about the model and its capabilities.
    
    Returns model information.
    """
    info = {
        "service": "Enhanced Rental Demand Forecasting",
        "description": "Predicts future rental demand by city with economic factors integration",
        "features": [
            "Forecasted demand by city",
            "Anticipated high-demand periods",
            "Early identification of emerging demand locations",
            "Economic factors integration"
        ],
        "supported_cities": "40 major Indian metropolitan cities",
        "data_granularity": "Daily demand forecasts",
        "users": ["Developers", "Investors", "Strategic planners"],
        "version": "3.0.0",  # Updated to enhanced version
        "security_features": [
            "Input validation",
            "Rate limiting",
            "SQL injection protection",
            "XSS protection"
        ],
        "enhanced": True,
        "features_used": len(forecaster.features) if hasattr(forecaster, 'features') else 0
    }
    
    return jsonify(info), 200

@app.route('/metrics', methods=['GET'])
@rate_limit
def get_model_metrics():
    """
    Get model performance metrics including RMSE.
    
    Returns:
    Get model performance metrics including RMSE, MAE, and R² scores.
    
    Returns actual metrics from the trained models (demand + tenant risk).
    """
    try:
        # Path to demand model metrics file
        metrics_path = os.path.join(os.path.dirname(__file__), 'model_metrics.json')
        
        # Check if metrics file exists
        if not os.path.exists(metrics_path):
            return jsonify({
                "error": "Metrics file not found. Please train the model first.",
                "hint": "Run train_demand_model_efficient.py to generate metrics"
            }), 404
        
        # Read demand model metrics from file
        with open(metrics_path, 'r') as f:
            demand_metrics = json.load(f)
        
        # Try to load tenant risk metrics if available
        tenant_risk_path = os.path.join(os.path.dirname(__file__), 'tenant_risk_metrics.json')
        tenant_risk_metrics = None
        
        if os.path.exists(tenant_risk_path):
            with open(tenant_risk_path, 'r') as f:
                tenant_risk_metrics = json.load(f)
        
        # Combine metrics
        combined_metrics = {
            "demand_forecasting": demand_metrics,
            "tenant_risk_scoring": tenant_risk_metrics if tenant_risk_metrics else {
                "status": "not_trained",
                "message": "Train tenant risk model: python train_tenant_risk_model.py"
            },
            "enhanced_features": {
                "quality_adjusted_demand": tenant_risk_metrics is not None,
                "investment_recommendations": tenant_risk_metrics is not None,
                "tenant_quality_analysis": tenant_risk_metrics is not None
            }
        }
        
        # Surface comparison data for easier frontend access
        if "predictions_sample" in demand_metrics:
            combined_metrics["predictions_sample"] = demand_metrics["predictions_sample"]
        
        return jsonify(combined_metrics), 200
        
    except json.JSONDecodeError:
        return jsonify({
            "error": "Invalid metrics file format"
        }), 500
    except Exception as e:

        return jsonify({
            "error": f"Failed to retrieve metrics: {str(e)}"
        }), 500



if __name__ == '__main__':
    # Run the development server
    print("Starting Rental Demand Forecasting API Server...")
    print("Security features enabled:")
    print("  - Input validation")
    print("  - Rate limiting (100 requests/minute per IP)")
    print("  - SQL injection protection")
    print("  - XSS protection")
    print("\nEndpoints available:")
    print("  GET  /health         - Health check")
    print("  POST /predict        - Predict demand for a city and date")
    print("  POST /predict/enhanced - Predict with tenant quality analysis (NEW)")
    print("  POST /predict/batch  - Predict demand for multiple cities")
    print("  GET  /cities         - Get list of supported cities")
    print("  GET  /metrics        - Get model performance metrics (RMSE, MAE, R²)")
    print("  GET  /info           - Get model information")
    print("\nServer starting on http://localhost:5001")
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)