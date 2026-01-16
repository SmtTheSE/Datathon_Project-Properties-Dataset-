# Rental Demand Forecasting Web API

This document describes how to integrate and run the web API for the Rental Demand Forecasting Tool (Product 4).

## Overview

The Rental Demand Forecasting Tool provides a RESTful API that can be integrated with a web frontend to deliver rental demand predictions. The API is built with Flask and uses a trained LightGBM model to make predictions.

## Prerequisites

Ensure you have the following installed:
- Python 3.7+
- pip (Python package manager)

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the API Server

Start the API server:
```bash
python api_server.py
```

The server will start on `http://localhost:5001`.

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the service.

### Get Model Information
```
GET /info
```
Returns information about the model and its capabilities.

### Get Supported Cities
```
GET /cities
```
Returns a list of cities supported by the model.

### Predict Demand for Single City-Date Pair
```
POST /predict
```

Request body:
```json
{
  "city": "Mumbai",
  "date": "2022-08-15"
}
```

Response:
```json
{
  "city": "Mumbai",
  "date": "2022-08-15",
  "predicted_demand": 125.5
}
```

### Predict Demand for Multiple City-Date Pairs
```
POST /predict/batch
```

Request body:
```json
{
  "requests": [
    {
      "city": "Mumbai",
      "date": "2022-08-15"
    },
    {
      "city": "Delhi",
      "date": "2022-08-16"
    }
  ]
}
```

Response:
```json
{
  "predictions": [
    {
      "city": "Mumbai",
      "date": "2022-08-15",
      "predicted_demand": 125.5
    },
    {
      "city": "Delhi",
      "date": "2022-08-16",
      "predicted_demand": 98.3
    }
  ]
}
```

## Integration with Frontend

To integrate with a web frontend:

1. Make HTTP requests to the API endpoints
2. Handle responses appropriately
3. Display predictions to users

Example JavaScript code for making a prediction request:
```javascript
const predictDemand = async (city, date) => {
  const response = await fetch('http://localhost:5001/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      city: city,
      date: date
    })
  });
  
  const data = await response.json();
  return data.predicted_demand;
};
```

## Model Information

The model uses the following features for prediction:
- Temporal features (day of week, month, quarter, etc.)
- City classification features (tier, region)
- Seasonal features (monsoon, holidays)
- Historical features (lags, rolling means, growth rates)

Performance metrics:
- MAPE: ~0.13%
- Improvement over baseline: ~92%

## Deployment Considerations

For production deployment, consider:
1. Using a production WSGI server like Gunicorn
2. Adding authentication and rate limiting
3. Implementing proper logging and monitoring
4. Containerizing the application with Docker
5. Deploying behind a reverse proxy like Nginx

## Files Overview

- `api_server.py`: Main Flask application providing REST endpoints
- `serve_demand_model.py`: Model serving module with prediction functions
- `train_demand_model.py`: Model training script (modified to save model)
- `/tmp/demand_forecast_model.txt`: Trained model file (generated after training)

## Notes

1. The model currently uses placeholder values for historical features. In a production environment, these should be replaced with actual historical data.
2. The API is designed to be stateless and can be scaled horizontally.
3. Error handling is implemented for common failure cases.