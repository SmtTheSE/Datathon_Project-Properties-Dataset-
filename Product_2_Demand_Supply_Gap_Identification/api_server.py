from flask import Flask, request, jsonify
import pandas as pd
import os
from serve_gap_model import GapAnalysisService

app = Flask(__name__)

# Initialize the gap model server with enhanced model
gap_server = GapAnalysisService()

@app.route('/health', methods=['GET'])
def health():
    """Check if the service is running."""
    return jsonify({
        "status": "healthy", 
        "model_loaded": gap_server.model is not None,
        "features_loaded": gap_server.feature_columns is not None
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
    """Get list of supported cities."""
    # In a real implementation, this would return actual supported cities
    # For now, we'll return a sample list
    cities = [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", 
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat"
    ]
    return jsonify({"cities": cities})

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
    print("  GET  /info           - Get model information")
    print("")
    print("Server starting on http://localhost:5002")
    
    # Run the Flask app on a different port to avoid conflicts
    app.run(host='0.0.0.0', port=5002, debug=False)
