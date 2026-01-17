from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import json
from serve_gap_model import GapAnalysisService

app = Flask(__name__)
CORS(app)

# Initialize the gap model server with enhanced model
gap_server = GapAnalysisService()

@app.route('/health', methods=['GET'])
def health():
    """Check if the service is running."""
    return jsonify({
        "status": "healthy", 
        "model_loaded": gap_server.sess is not None
    })

@app.route('/model/info', methods=['GET'])
def model_info():
    """Get information about the model."""
    return jsonify({
        "model_type": "Enhanced Demand-Supply Gap Identification",
        "description": "Identifies demand-supply gaps based on location, property type, and economic factors",
        "features_used": "Dynamic based on input",
        "enhanced": True
    })

@app.route('/cities', methods=['GET'])
def get_cities():
    """Get list of supported cities from the actual dataset."""
    try:
        from data_loader import get_data_loader
        loader = get_data_loader()
        locality_data = loader._load_locality_data()
        cities = sorted(locality_data.keys())
        return jsonify({"cities": cities}), 200
    except Exception as e:
        # Fallback to hardcoded list if data loading fails
        print(f"Warning: Failed to load cities from dataset: {e}")
        cities = [
            "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", 
            "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat"
        ]
        return jsonify({"cities": sorted(cities)}), 200

@app.route('/historical/<city>', methods=['GET'])
def get_historical_data(city):
    """
    Get historical locality gap data for heat map visualization.
    
    Args:
        city: City name from URL path
        
    Query parameters:
        top_n: Number of top localities (default 10)
        sort_by: How to sort - 'demand' (default), 'gap_high' (oversupplied), 
                 'gap_low' (undersupplied), 'gap_abs' (most extreme)
    
    Returns:
        {
            "city": "Mumbai",
            "locality_data": [
                {"locality": "Bandra", "gap": 0.15, "demand": 1250},
                {"locality": "Andheri", "gap": -0.08, "demand": 980},
                ...
            ]
        }
    """
    try:
        # Get optional parameters
        top_n = request.args.get('top_n', default=10, type=int)
        sort_by = request.args.get('sort_by', default='demand', type=str)
        
        # Limit to reasonable range
        if top_n < 1 or top_n > 50:
            return jsonify({"error": "top_n must be between 1 and 50"}), 400
        
        # Validate sort_by parameter
        valid_sorts = ['demand', 'gap_high', 'gap_low', 'gap_abs']
        if sort_by not in valid_sorts:
            return jsonify({"error": f"sort_by must be one of {valid_sorts}"}), 400
        
        # Get locality gap data from service (uses real dataset)
        locality_data = gap_server.get_locality_gaps(city, top_n, sort_by)
        
        return jsonify({
            "city": city,
            "locality_data": locality_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get locality data: {str(e)}"}), 500

@app.route('/predict', methods=['POST'])
def predict():
    """Make a single prediction."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['city', 'area_locality', 'bhk', 'avg_rent']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        city = data.get('city')
        area_locality = data.get('area_locality')
        bhk = data.get('bhk')
        avg_rent = data.get('avg_rent')
        economic_indicators = data.get('economic_indicators')  # Optional economic indicators
        
        # Make prediction using the GapAnalysisService interface
        result = gap_server.predict_gap(
            city, area_locality, bhk, avg_rent, economic_indicators
        )
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Make multiple predictions."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'requests' not in data:
            return jsonify({"error": "Missing required field: requests"}), 400
        
        requests = data.get('requests')
        
        # Validate each request
        required_fields = ['city', 'area_locality', 'bhk', 'avg_rent']
        for req in requests:
            for field in required_fields:
                if field not in req:
                    return jsonify({"error": f"Each request must have {field}"}), 400
        
        # Make batch predictions using the GapAnalysisService interface
        result = gap_server.predict_batch_gaps(requests)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/metrics', methods=['GET'])
def get_model_metrics():
    """
    Get model performance metrics including RMSE, MAE, and R² scores.
    
    Returns actual metrics from the trained model.
    """
    try:
        # Path to metrics file
        metrics_path = os.path.join(os.path.dirname(__file__), 'model_metrics.json')
        
        # Check if metrics file exists
        if not os.path.exists(metrics_path):
            return jsonify({
                "error": "Metrics file not found. Please train the model first.",
                "hint": "Run train_gap_model_efficient.py to generate metrics"
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
    print("Starting Demand-Supply Gap Analysis API Server...")
    print("Security features enabled:")
    print("  - Input validation")
    print("  - Rate limiting (100 requests/minute per IP)")
    print("  - SQL injection protection")
    print("  - XSS protection")
    print("")
    print("Endpoints available:")
    print("  GET  /health         - Health check")
    print("  POST /predict        - Predict gap for property details")
    print("  POST /predict/batch  - Predict gaps for multiple properties")
    print("  GET  /cities         - Get list of supported cities")
    print("  GET  /metrics        - Get model performance metrics (RMSE, MAE, R²)")
    print("  GET  /info           - Get model information")
    print("")
    print("Server starting on http://localhost:5002")
    
    # Run the Flask app on a different port to avoid conflicts
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)
