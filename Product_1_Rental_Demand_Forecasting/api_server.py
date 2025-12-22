"""
REST API Server for Rental Demand Forecasting Tool

This module provides a Flask-based web API to serve rental demand predictions.
It can be easily integrated with frontend web applications.
"""

from flask import Flask, jsonify, request
from datetime import datetime
import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from serve_demand_model import RentalDemandForecaster

app = Flask(__name__)

# Initialize the forecaster - in production, you'd load a pre-trained model
forecaster = RentalDemandForecaster()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "rental-demand-forecasting"}), 200

@app.route('/predict', methods=['POST'])
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
            
        # Parse date
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Make prediction
        # Note: In a real implementation, you would pass actual historical data
        predicted_demand = forecaster.predict_demand(city, date)
        
        # Return result
        return jsonify({
            "city": city,
            "date": date_str,
            "predicted_demand": round(predicted_demand, 2)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/predict/batch', methods=['POST'])
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
            
        requests = data.get('requests')
        
        if not requests:
            return jsonify({"error": "'requests' list is required"}), 400
            
        # Validate and parse requests
        parsed_requests = []
        for req in requests:
            city = req.get('city')
            date_str = req.get('date')
            
            if not city or not date_str:
                return jsonify({"error": "Each request must have 'city' and 'date'"}), 400
                
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                parsed_requests.append({'city': city, 'date': date})
            except ValueError:
                return jsonify({"error": f"Invalid date format in request for {city}. Use YYYY-MM-DD"}), 400
        
        # Make batch predictions
        # Note: In a real implementation, you would pass actual historical data
        predictions = forecaster.predict_demand_batch(parsed_requests)
        
        # Format results
        results = []
        for i, req in enumerate(parsed_requests):
            results.append({
                "city": req['city'],
                "date": req['date'].strftime('%Y-%m-%d'),
                "predicted_demand": round(predictions[i], 2)
            })
        
        # Return results
        return jsonify({"predictions": results}), 200
        
    except Exception as e:
        return jsonify({"error": f"Batch prediction failed: {str(e)}"}), 500

@app.route('/cities', methods=['GET'])
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

@app.route('/info', methods=['GET'])
def get_model_info():
    """
    Get information about the model and its capabilities.
    
    Returns model information.
    """
    info = {
        "service": "Rental Demand Forecasting",
        "description": "Predicts future rental demand by city",
        "features": [
            "Forecasted demand by city",
            "Anticipated high-demand periods",
            "Early identification of emerging demand locations"
        ],
        "supported_cities": "40 major Indian metropolitan cities",
        "data_granularity": "Daily demand forecasts",
        "users": ["Developers", "Investors", "Strategic planners"],
        "version": "1.0.0"
    }
    
    return jsonify(info), 200

if __name__ == '__main__':
    # Run the development server
    print("Starting Rental Demand Forecasting API Server...")
    print("Endpoints available:")
    print("  GET  /health         - Health check")
    print("  POST /predict        - Predict demand for a city and date")
    print("  POST /predict/batch  - Predict demand for multiple city-date pairs")
    print("  GET  /cities         - Get list of supported cities")
    print("  GET  /info           - Get model information")
    print("\nServer starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)