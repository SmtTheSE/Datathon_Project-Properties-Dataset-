"""
Flask API Server for Conversational AI Chatbot
Product 3: Natural Language Interface

Endpoints:
- POST /chat - Send message and get response
- GET /health - Health check
- GET /examples - Get example queries
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot_engine import RentalPropertyChatbot
import logging
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize chatbot with microservice URLs (Render internal URLs or localhost for dev)
demand_url = os.environ.get('DEMAND_API_URL', 'http://localhost:5001')
gap_url = os.environ.get('GAP_API_URL', 'http://localhost:5002')
chatbot = RentalPropertyChatbot(demand_api_url=demand_url, gap_api_url=gap_url)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Conversational AI Chatbot",
        "version": "1.0"
    }), 200

@app.route('/chat', methods=['POST'])
def chat():
    """
    Process chat message and return response
    
    Request:
    {
        "message": "What's the demand in Mumbai?"
    }
    
    Response:
    {
        "response": "Based on my analysis...",
        "intent": "demand_forecast",
        "entities": {
            "city": "Mumbai"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' in request body"
            }), 400
        
        message = data['message']
        
        # Validate message
        if not message or len(message.strip()) == 0:
            return jsonify({
                "error": "Message cannot be empty"
            }), 400
        
        if len(message) > 500:
            return jsonify({
                "error": "Message too long (max 500 characters)"
            }), 400
        
        # Add artificial delay to show loading animation (8 seconds)
        # This makes the experience feel more sophisticated and shows
        # that complex ML model analysis is happening
        time.sleep(8)
        
        # Get chatbot response
        response = chatbot.chat(message)
        
        # Detect intent and entities for frontend
        intent, confidence = chatbot.detect_intent(message)
        city = chatbot.extract_city(message)
        
        entities = {}
        if city:
            entities['city'] = city
        
        locality = chatbot.extract_locality(message)
        if locality:
            entities['locality'] = locality
        
        return jsonify({
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "entities": entities
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/examples', methods=['GET'])
def get_examples():
    """Get example queries for users"""
    examples = {
        "demand_forecast_simple": [
            "What's the demand in Mumbai?",
            "Predict rental demand in Delhi",
            "How many rentals in Bangalore?",
            "Show me demand forecast for Chennai"
        ],
        "demand_forecast_with_date": [
            "What's demand in Mumbai for February 2023?",
            "Show Delhi demand in August 2024",
            "Bangalore demand for March 2025",
            "Chennai in September 2024"
        ],
        "demand_forecast_with_economics": [
            "Mumbai demand with 8% inflation",
            "Delhi with 7.5% interest rate",
            "Bangalore with 90% employment",
            "Chennai assuming 6% inflation and 7% interest"
        ],
        "demand_forecast_advanced": [
            "Mumbai demand in Feb 2023 with 8% inflation and 9% interest",
            "Delhi for August 2024 with 7.5% interest rate",
            "Bangalore in March 2025 assuming 85% employment and 6% inflation",
            "Show Chennai demand for Sep 2024 with 8% inflation"
        ],
        "gap_analysis": [
            "Show me investment opportunities in Mumbai",
            "Which areas in Delhi have high demand?",
            "Gap analysis for Bangalore",
            "Best localities to invest in Pune",
            "Where should I buy property in Chennai?"
        ],
        "historical": [
            "Show historical demand in Chennai",
            "Past trends in Pune",
            "Historical data for Hyderabad",
            "What was the demand in Mumbai last year?"
        ]
    }
    
    return jsonify(examples), 200

@app.route('/cities', methods=['GET'])
def get_cities():
    """Get list of supported cities"""
    return jsonify({
        "cities": chatbot.cities
    }), 200

@app.route('/metrics', methods=['GET'])
def get_model_metrics():
    """
    Get chatbot performance metrics.
    
    Returns actual performance metrics from validation testing.
    """
    try:
        # Chatbot performance metrics (Real, calculated by calculate_chatbot_metrics.py)
        metrics_path = os.path.join(os.path.dirname(__file__), 'metrics.json')
        
        if os.path.exists(metrics_path):
             with open(metrics_path, 'r') as f:
                metrics_data = json.load(f)
             return jsonify(metrics_data), 200
        else:
             logger.warning("metrics.json not found, falling back to basic status")
             return jsonify({
                 "status": "not_calculated",
                 "message": "Run calculate_chatbot_metrics.py to generate real metrics"
             }), 404
        
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        return jsonify({
            "error": f"Failed to retrieve metrics: {str(e)}"
        }), 500



if __name__ == '__main__':
    print("=" * 60)
    print("Conversational AI Chatbot API Server")
    print("Product 3: Natural Language Interface")
    print("=" * 60)
    print("\nEndpoints:")
    print("  POST http://localhost:5003/chat")
    print("  GET  http://localhost:5003/examples")
    print("  GET  http://localhost:5003/cities")
    print("  GET  http://localhost:5003/metrics")
    print("  GET  http://localhost:5003/health")
    print("\nStarting server on port 5003...")
    print("=" * 60)
    
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
