from flask import Flask, jsonify, request
from serve_gap_model import GapModelServer
import pandas as pd
import re
from functools import wraps
import time

app = Flask(__name__)

# Initialize the model server
model_server = None

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

def load_model():
    global model_server
    if model_server is None:
        model_server = GapModelServer()

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

def validate_area_locality(area):
    """Validate area locality to prevent injection attacks"""
    if not isinstance(area, str):
        return False
    # Only allow letters, numbers, spaces, hyphens, and periods
    if not re.match(r"^[A-Za-z0-9\s\-\.]+$", area):
        return False
    if len(area) > 100:  # Prevent overly long inputs
        return False
    return True

def validate_numeric_field(value, field_name, min_val=None, max_val=None):
    """Validate numeric fields"""
    if not isinstance(value, (int, float)):
        try:
            value = float(value)
        except (ValueError, TypeError):
            return False, f"{field_name} must be a number"
    
    if min_val is not None and value < min_val:
        return False, f"{field_name} must be at least {min_val}"
    
    if max_val is not None and value > max_val:
        return False, f"{field_name} must be at most {max_val}"
    
    return True, value

@app.route('/health', methods=['GET'])
@rate_limit
def health_check():
    load_model()
    return jsonify({"status": "healthy", "product": "Demand-Supply Gap Identification Tool"})

@app.route('/model/info', methods=['GET'])
@rate_limit
def model_info():
    load_model()
    return jsonify({
        "product": "Demand-Supply Gap Identification Tool",
        "version": "2.0.0",  # Updated version
        "description": "Identifies areas where demand exceeds supply in rental markets",
        "features": [
            "High-demand but under-listed locations",
            "Oversupplied areas with weaker demand",
            "Investment opportunity zones"
        ],
        "security_features": [
            "Input validation",
            "Rate limiting",
            "SQL injection protection",
            "XSS protection"
        ]
    })

@app.route('/cities', methods=['GET'])
@rate_limit
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
@rate_limit
def predict_gap():
    load_model()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['city', 'area_locality', 'bhk', 'year', 'month', 'supply', 'avg_rent']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate and sanitize inputs
        city = data['city']
        area_locality = data['area_locality']
        bhk = data['bhk']
        year = data['year']
        month = data['month']
        supply = data['supply']
        avg_rent = data['avg_rent']
        
        # Validate city
        if not validate_city(city):
            return jsonify({"error": "Invalid city name format"}), 400
        
        # Validate area locality
        if not validate_area_locality(area_locality):
            return jsonify({"error": "Invalid area locality format"}), 400
        
        # Validate numeric fields
        is_valid, result = validate_numeric_field(bhk, 'BHK', min_val=0, max_val=10)
        if not is_valid:
            return jsonify({"error": result}), 400
        bhk = int(result)
        
        is_valid, result = validate_numeric_field(year, 'Year', min_val=2000, max_val=2030)
        if not is_valid:
            return jsonify({"error": result}), 400
        year = int(result)
        
        is_valid, result = validate_numeric_field(month, 'Month', min_val=1, max_val=12)
        if not is_valid:
            return jsonify({"error": result}), 400
        month = int(result)
        
        is_valid, result = validate_numeric_field(supply, 'Supply', min_val=0)
        if not is_valid:
            return jsonify({"error": result}), 400
        supply = result
        
        is_valid, result = validate_numeric_field(avg_rent, 'Avg Rent', min_val=0)
        if not is_valid:
            return jsonify({"error": result}), 400
        avg_rent = result
        
        # Make prediction
        result = model_server.predict_gap(
            city=city,
            area_locality=area_locality,
            bhk=bhk,
            year=year,
            month=month,
            supply=supply,
            avg_rent=avg_rent
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict/batch', methods=['POST'])
@rate_limit
def predict_gap_batch():
    load_model()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if 'predictions' not in data:
            return jsonify({"error": "Missing 'predictions' field with array of prediction requests"}), 400
        
        # Limit batch size to prevent abuse
        if len(data['predictions']) > 50:
            return jsonify({"error": "Batch size too large. Maximum 50 requests per batch."}), 400
        
        results = []
        for i, pred_request in enumerate(data['predictions']):
            # Validate required fields
            required_fields = ['city', 'area_locality', 'bhk', 'year', 'month', 'supply', 'avg_rent']
            for field in required_fields:
                if field not in pred_request:
                    return jsonify({"error": f"Missing required field in batch request {i}: {field}"}), 400
            
            # Validate and sanitize inputs
            city = pred_request['city']
            area_locality = pred_request['area_locality']
            bhk = pred_request['bhk']
            year = pred_request['year']
            month = pred_request['month']
            supply = pred_request['supply']
            avg_rent = pred_request['avg_rent']
            
            # Validate city
            if not validate_city(city):
                return jsonify({"error": f"Invalid city name format in batch request {i}"}), 400
            
            # Validate area locality
            if not validate_area_locality(area_locality):
                return jsonify({"error": f"Invalid area locality format in batch request {i}"}), 400
            
            # Validate numeric fields
            is_valid, result = validate_numeric_field(bhk, f'BHK in batch request {i}', min_val=0, max_val=10)
            if not is_valid:
                return jsonify({"error": result}), 400
            bhk = int(result)
            
            is_valid, result = validate_numeric_field(year, f'Year in batch request {i}', min_val=2000, max_val=2030)
            if not is_valid:
                return jsonify({"error": result}), 400
            year = int(result)
            
            is_valid, result = validate_numeric_field(month, f'Month in batch request {i}', min_val=1, max_val=12)
            if not is_valid:
                return jsonify({"error": result}), 400
            month = int(result)
            
            is_valid, result = validate_numeric_field(supply, f'Supply in batch request {i}', min_val=0)
            if not is_valid:
                return jsonify({"error": result}), 400
            supply = result
            
            is_valid, result = validate_numeric_field(avg_rent, f'Avg Rent in batch request {i}', min_val=0)
            if not is_valid:
                return jsonify({"error": result}), 400
            avg_rent = result
            
            # Make prediction
            result = model_server.predict_gap(
                city=city,
                area_locality=area_locality,
                bhk=bhk,
                year=year,
                month=month,
                supply=supply,
                avg_rent=avg_rent
            )
            
            results.append(result)
        
        return jsonify({"results": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Load model on startup
    load_model()
    print("Starting Demand-Supply Gap Identification API Server...")
    print("Security features enabled:")
    print("  - Input validation")
    print("  - Rate limiting (100 requests/minute per IP)")
    print("  - SQL injection protection")
    print("  - XSS protection")
    print("\nServer starting on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)  # Disabled debug in production