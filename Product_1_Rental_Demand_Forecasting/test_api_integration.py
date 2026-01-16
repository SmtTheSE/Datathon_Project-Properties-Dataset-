"""
Test script to demonstrate API integration for Rental Demand Forecasting Tool
"""

import requests
import json
from datetime import datetime, timedelta

def test_api_endpoints():
    """
    Test the main API endpoints
    """
    base_url = "http://localhost:5001"
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test info endpoint
    print("\nTesting info endpoint...")
    try:
        response = requests.get(f"{base_url}/info")
        print(f"Model info: {response.status_code}")
        info = response.json()
        print(f"Service: {info.get('service')}")
        print(f"Description: {info.get('description')}")
    except Exception as e:
        print(f"Info endpoint failed: {e}")
    
    # Test cities endpoint
    print("\nTesting cities endpoint...")
    try:
        response = requests.get(f"{base_url}/cities")
        print(f"Cities list: {response.status_code}")
        cities_data = response.json()
        cities = cities_data.get('cities', [])
        print(f"Available cities: {len(cities)}")
        if cities:
            print(f"Sample cities: {cities[:5]}")
    except Exception as e:
        print(f"Cities endpoint failed: {e}")

def demonstrate_frontend_integration():
    """
    Demonstrate how a frontend would integrate with the API
    """
    print("\n" + "="*50)
    print("FRONTEND INTEGRATION EXAMPLE")
    print("="*50)
    
    print("""
In a real frontend application, you would:

1. Create a form for users to select city and date
2. Send AJAX requests to the API
3. Display the results

Example JavaScript code:
""")
    
    js_example = '''
// Function to predict demand
async function predictRentalDemand(city, date) {
    try {
        const response = await fetch('http://localhost:5001/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                city: city,
                date: date  // Format: 'YYYY-MM-DD'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.predicted_demand;
    } catch (error) {
        console.error('Error predicting demand:', error);
        throw error;
    }
}

// Usage example
predictRentalDemand('Mumbai', '2022-08-15')
    .then(demand => {
        console.log(`Predicted demand for Mumbai on 2022-08-15: ${demand}`);
        // Update UI with the prediction
        document.getElementById('result').innerText = `Predicted demand: ${demand}`;
    })
    .catch(error => {
        console.error('Failed to get prediction:', error);
        // Show error message in UI
        document.getElementById('result').innerText = 'Failed to get prediction';
    });
'''
    
    print(js_example)
    
    print("""
Example HTML form:
""")
    
    html_example = '''
<form id="predictionForm">
    <div>
        <label for="city">City:</label>
        <select id="city" name="city">
            <option value="Mumbai">Mumbai</option>
            <option value="Delhi">Delhi</option>
            <option value="Bangalore">Bangalore</option>
            <!-- Add more cities -->
        </select>
    </div>
    
    <div>
        <label for="date">Date:</label>
        <input type="date" id="date" name="date" required>
    </div>
    
    <button type="submit">Predict Demand</button>
</form>

<div id="result"></div>

<script>
document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const city = document.getElementById('city').value;
    const date = document.getElementById('date').value;
    
    try {
        const demand = await predictRentalDemand(city, date);
        document.getElementById('result').innerText = 
            `Predicted rental demand for ${city} on ${date}: ${demand.toFixed(2)} listings`;
    } catch (error) {
        document.getElementById('result').innerText = 
            'Failed to get prediction. Please try again.';
    }
});
</script>
'''
    
    print(html_example)

def explain_deployment():
    """
    Explain deployment considerations
    """
    print("\n" + "="*50)
    print("DEPLOYMENT CONSIDERATIONS")
    print("="*50)
    
    deployment_notes = """
1. Production Server:
   - Use a production WSGI server like Gunicorn instead of Flask's development server
   - Example: gunicorn -w 4 api_server:app

2. Reverse Proxy:
   - Deploy behind Nginx or Apache for better performance and security

3. Containerization:
   - Create a Dockerfile for consistent deployment across environments

4. Environment Variables:
   - Store configuration in environment variables rather than hardcoded values

5. Monitoring and Logging:
   - Implement proper logging for debugging and monitoring
   - Add health checks for container orchestration

6. Security:
   - Add authentication for API endpoints if needed
   - Implement rate limiting to prevent abuse
   - Use HTTPS in production

7. Scaling:
   - The API is stateless and can be scaled horizontally
   - Consider using a load balancer for multiple instances

8. Model Updates:
   - Plan for periodic model retraining and updates
   - Implement a process for deploying new model versions
"""
    
    print(deployment_notes)

if __name__ == "__main__":
    print("RENTAL DEMAND FORECASTING API INTEGRATION DEMO")
    print("="*50)
    
    test_api_endpoints()
    demonstrate_frontend_integration()
    explain_deployment()
    
    print("\nTo run the actual API server:")
    print("python api_server.py")