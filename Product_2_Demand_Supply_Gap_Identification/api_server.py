from flask import Flask, jsonify, request
from serve_gap_model import GapModelServer
import pandas as pd

app = Flask(__name__)

# Initialize the model server
model_server = None

def load_model():
    global model_server
    if model_server is None:
        model_server = GapModelServer()

@app.route('/health', methods=['GET'])
def health_check():
    load_model()
    return jsonify({"status": "healthy", "product": "Demand-Supply Gap Identification Tool"})

@app.route('/model/info', methods=['GET'])
def model_info():
    load_model()
    return jsonify({
        "product": "Demand-Supply Gap Identification Tool",
        "version": "1.0.0",
        "description": "Identifies areas where demand exceeds supply in rental markets",
        "features": [
            "High-demand but under-listed locations",
            "Oversupplied areas with weaker demand",
            "Investment opportunity zones"
        ]
    })

@app.route('/cities', methods=['GET'])
def get_cities():
    load_model()
    cities = [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata",
        "Pune", "Ahmedabad", "Jaipur", "Surat", "Kanpur", "Lucknow",
        "Nagpur", "Indore", "Bhopal", "Patna", "Vadodara", "Ghaziabad",
        "Visakhapatnam", "Agra", "Thane", "Kalyan", "Varanasi", "Raipur",
        "Aurangabad", "Meerut", "Jabalpur", "Vijaywada", "Gwalior", "Madurai",
        "Amritsar", "Allahabad", "Coimbatore", "Ranchi", "Jalandhar", "Tiruchirappalli"
    ]
    return jsonify({"cities": cities})

@app.route('/predict', methods=['POST'])
def predict_gap():
    load_model()
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['city', 'area_locality', 'bhk', 'year', 'month', 'supply', 'avg_rent']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Make prediction
        result = model_server.predict_gap(
            city=data['city'],
            area_locality=data['area_locality'],
            bhk=data['bhk'],
            year=data['year'],
            month=data['month'],
            supply=data['supply'],
            avg_rent=data['avg_rent']
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict/batch', methods=['POST'])
def predict_gap_batch():
    load_model()
    try:
        data = request.get_json()
        
        if 'predictions' not in data:
            return jsonify({"error": "Missing 'predictions' field with array of prediction requests"}), 400
        
        results = []
        for pred_request in data['predictions']:
            # Validate required fields
            required_fields = ['city', 'area_locality', 'bhk', 'year', 'month', 'supply', 'avg_rent']
            for field in required_fields:
                if field not in pred_request:
                    return jsonify({"error": f"Missing required field in batch request: {field}"}), 400
            
            # Make prediction
            result = model_server.predict_gap(
                city=pred_request['city'],
                area_locality=pred_request['area_locality'],
                bhk=pred_request['bhk'],
                year=pred_request['year'],
                month=pred_request['month'],
                supply=pred_request['supply'],
                avg_rent=pred_request['avg_rent']
            )
            
            results.append(result)
        
        return jsonify({"results": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Load model on startup
    load_model()
    app.run(host='0.0.0.0', port=5001, debug=True)