import sys
import os
import json
import logging
import requests
import time
import subprocess
import signal

# Disable logging to keep output clean
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('root').setLevel(logging.ERROR)

def check_endpoint(name, port, expected_key):
    url = f"http://localhost:{port}/metrics"
    print(f"\n{'='*20} Testing {name} ({url}) {'='*20}")
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: 200 OK")
            
            # Check for the expected comparison data key
            if expected_key in data:
                items = data[expected_key]
                count = len(items)
                print(f"✅ Comparison Data Found: '{expected_key}'")
                print(f"✅ Count: {count} items")
                if count > 0:
                    print("✅ Sample Item:")
                    print(json.dumps(items[0], indent=2))
            else:
                print(f"❌ Missing comparison data key: '{expected_key}'")
                print(f"Keys found: {list(data.keys())}")
                
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")

def main():
    # Define products configuration
    products = [
        {
            "name": "Product 1 (Demand)",
            "port": 5001,
            "key": "predictions_sample",
            "script": "Product_1_Rental_Demand_Forecasting/api_server.py"
        },
        {
            "name": "Product 2 (Gap)",
            "port": 5002,
            "key": "predictions_sample",
            "script": "Product_2_Demand_Supply_Gap_Identification/api_server.py"
        },
        {
            "name": "Product 3 (Chatbot)",
            "port": 5003,
            "key": "test_cases_results",
            "script": "Product_3_Conversational_AI_Chatbot/api_server.py"
        }
    ]
    
    # We assume servers are running or will be started by the system/user.
    # But to make this "run all api", this script is just the TESTER.
    # The agent will handle starting the servers.
    
    for p in products:
        check_endpoint(p["name"], p["port"], p["key"])

if __name__ == "__main__":
    main()
