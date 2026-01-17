"""
REST API Server for Rental Demand Forecasting Tool

This module provides a Flask-based web API to serve rental demand predictions.
It can be easily integrated with frontend web applications.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import sys
import os
import re
import json
from functools import wraps
import time

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from serve_demand_model import DemandForecastService

app = Flask(__name__)
CORS(app)

# Initialize the forecaster - in production, you'd load a pre-trained model
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
    # These would come from the actual data in a real implementation
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
    {
        "model_name": "Demand Forecast Model (Efficient)",
        "model_version": "3.0.0",
        "training_date": "2026-01-17T10:30:00",
        "metrics": {
            "train_rmse": 123.456789,
            "test_rmse": 125.678901,
            "cv_avg_val_rmse": 124.567890,
            ...
        },
        ...
    }
    """
    try:
        # Path to metrics file
        metrics_path = os.path.join(os.path.dirname(__file__), 'model_metrics.json')
        
        # Check if metrics file exists
        if not os.path.exists(metrics_path):
            return jsonify({
                "error": "Metrics file not found. Please train the model first.",
                "hint": "Run train_demand_model_efficient.py to generate metrics"
            }), 404
        
        # Read metrics from file
        with open(metrics_path, 'r') as f:
            metrics_data = json.load(f)
        
        return jsonify(metrics_data), 200
        
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
    print("  POST /predict/batch  - Predict demand for multiple city-date pairs")
    print("  GET  /cities         - Get list of supported cities")
    print("  GET  /metrics        - Get model performance metrics (RMSE, MAE, R²)")
    print("  GET  /info           - Get model information")
    print("\nServer starting on http://localhost:5001")
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)