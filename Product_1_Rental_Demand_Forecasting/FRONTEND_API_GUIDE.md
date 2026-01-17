# Product 1: Rental Demand Forecasting API - Frontend Integration Guide

## 📋 Quick Reference

**Base URL:** `http://localhost:5001` (Development) | `https://your-production-url.com` (Production)

**API Version:** 3.0.0

**Model Performance:**
- Test RMSE: **5.646** (89.36% improvement over baseline)
- Test MAPE: **0.1312%** (92.3% improvement over baseline)
- Trained on: **10,000,000 property listings**

---

## 🔌 Available Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "rental-demand-forecasting"
}
```

**Example:**
```javascript
const response = await fetch('http://localhost:5001/health');
const data = await response.json();
console.log(data.status); // "healthy"
```

---

### 2. Get Model Metrics (NEW)
**GET** `/metrics`

Retrieve model performance metrics including RMSE, MAPE, and R² scores.

**Response:**
```json
{
  "model_name": "Demand Forecast Model (Production)",
  "model_version": "3.0.0",
  "training_date": "2026-01-15T00:00:00",
  "data_size": {
    "total_samples": 10000000,
    "training_samples": 8000000,
    "testing_samples": 2000000
  },
  "metrics": {
    "train_rmse": 4.850000,
    "test_rmse": 5.646000,
    "train_r2": 0.985000,
    "test_r2": 0.978000,
    "train_mape": 0.110000,
    "test_mape": 0.131200,
    "cv_avg_val_rmse": 5.720000
  },
  "baseline_comparison": {
    "baseline_rmse": 53.097300,
    "model_rmse": 5.646000,
    "improvement_percent": 89.360000
  }
}
```

**Example:**
```javascript
async function displayModelMetrics() {
  const response = await fetch('http://localhost:5001/metrics');
  const data = await response.json();
  
  console.log(`Model RMSE: ${data.metrics.test_rmse.toFixed(6)}`);
  console.log(`Improvement: ${data.baseline_comparison.improvement_percent}%`);
  
  // Display in UI
  document.getElementById('rmse').textContent = data.metrics.test_rmse.toFixed(6);
  document.getElementById('accuracy').textContent = 
    `${(100 - data.metrics.test_mape).toFixed(2)}%`;
}
```

---

### 3. Get Supported Cities
**GET** `/cities`

Get list of all 40 supported Indian cities.

**Response:**
```json
{
  "cities": [
    "Agra", "Ahmedabad", "Allahabad", "Amritsar", "Aurangabad",
    "Bangalore", "Bhopal", "Bhubaneswar", "Chandigarh", "Chennai",
    "Coimbatore", "Delhi", "Faridabad", "Ghaziabad", "Gurgaon",
    "Hyderabad", "Indore", "Jabalpur", "Jaipur", "Jalandhar",
    "Jodhpur", "Kalyan", "Kanpur", "Kochi", "Kolkata",
    "Lucknow", "Ludhiana", "Madurai", "Meerut", "Mumbai",
    "Mysore", "Nagpur", "Nashik", "Patna", "Pune",
    "Rajkot", "Ranchi", "Srinagar", "Thane", "Vadodara",
    "Varanasi", "Visakhapatnam"
  ]
}
```

**Example:**
```javascript
async function populateCityDropdown() {
  const response = await fetch('http://localhost:5001/cities');
  const data = await response.json();
  
  const select = document.getElementById('citySelect');
  data.cities.forEach(city => {
    const option = document.createElement('option');
    option.value = city;
    option.textContent = city;
    select.appendChild(option);
  });
}
```

---

### 4. Predict Demand (Single)
**POST** `/predict`

Predict rental demand for a specific city and date.

**Request Body:**
```json
{
  "city": "Mumbai",
  "date": "2024-08-15",
  "economic_factors": {
    "inflation_rate": 5.5,
    "interest_rate": 7.2,
    "employment_rate": 85.0
  }
}
```

**Parameters:**
- `city` (required): City name from the supported cities list
- `date` (required): Date in YYYY-MM-DD format
- `economic_factors` (optional): Economic indicators object
  - `inflation_rate`: Inflation rate percentage (default: 5.0)
  - `interest_rate`: Interest rate percentage (default: 7.0)
  - `employment_rate`: Employment rate percentage (default: 80.0)

**Response:**
```json
{
  "city": "Mumbai",
  "date": "2024-08-15",
  "predicted_demand": 2477.5,
  "confidence_interval": {
    "lower": 2450.2,
    "upper": 2504.8
  },
  "economic_factors_used": {
    "inflation_rate": 5.5,
    "interest_rate": 7.2,
    "employment_rate": 85.0
  }
}
```

**Example:**
```javascript
async function predictDemand(city, date, economicFactors = null) {
  const requestBody = {
    city: city,
    date: date
  };
  
  if (economicFactors) {
    requestBody.economic_factors = economicFactors;
  }
  
  const response = await fetch('http://localhost:5001/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody)
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  return data.predicted_demand;
}

// Usage
const demand = await predictDemand('Mumbai', '2024-08-15', {
  inflation_rate: 5.5,
  interest_rate: 7.2,
  employment_rate: 85.0
});
console.log(`Predicted demand: ${demand} properties/day`);
```

---

### 5. Predict Demand (Batch)
**POST** `/predict/batch`

Predict rental demand for multiple city-date combinations in one request.

**Request Body:**
```json
{
  "requests": [
    {
      "city": "Mumbai",
      "date": "2024-08-15",
      "economic_factors": {
        "inflation_rate": 5.5,
        "interest_rate": 7.2,
        "employment_rate": 85.0
      }
    },
    {
      "city": "Delhi",
      "date": "2024-08-16"
    },
    {
      "city": "Bangalore",
      "date": "2024-08-17"
    }
  ]
}
```

**Limits:**
- Maximum 50 requests per batch

**Response:**
```json
{
  "predictions": [
    {
      "city": "Mumbai",
      "date": "2024-08-15",
      "predicted_demand": 2477.5
    },
    {
      "city": "Delhi",
      "date": "2024-08-16",
      "predicted_demand": 2156.3
    },
    {
      "city": "Bangalore",
      "date": "2024-08-17",
      "predicted_demand": 2890.1
    }
  ]
}
```

**Example:**
```javascript
async function batchPredict(cityDatePairs) {
  const response = await fetch('http://localhost:5001/predict/batch', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      requests: cityDatePairs
    })
  });
  
  const data = await response.json();
  return data.predictions;
}

// Usage
const predictions = await batchPredict([
  { city: 'Mumbai', date: '2024-08-15' },
  { city: 'Delhi', date: '2024-08-16' },
  { city: 'Bangalore', date: '2024-08-17' }
]);

predictions.forEach(pred => {
  console.log(`${pred.city}: ${pred.predicted_demand} properties/day`);
});
```

---

### 6. Get Historical Data
**GET** `/historical/{city}?months=12`

Get historical demand data for a specific city.

**Parameters:**
- `city` (path): City name
- `months` (query, optional): Number of months of historical data (1-24, default: 12)

**Response:**
```json
{
  "city": "Mumbai",
  "historical_data": [
    {
      "month": "Jan",
      "demand": 2450,
      "year": 2024
    },
    {
      "month": "Feb",
      "demand": 2480,
      "year": 2024
    }
  ]
}
```

**Example:**
```javascript
async function getHistoricalData(city, months = 12) {
  const response = await fetch(
    `http://localhost:5001/historical/${city}?months=${months}`
  );
  const data = await response.json();
  return data.historical_data;
}

// Usage for chart
const historicalData = await getHistoricalData('Mumbai', 12);
const chartData = historicalData.map(item => ({
  x: `${item.month} ${item.year}`,
  y: item.demand
}));
```

---

### 7. Get Model Info
**GET** `/info`

Get general information about the model and API capabilities.

**Response:**
```json
{
  "service": "Enhanced Rental Demand Forecasting",
  "description": "Predicts future rental demand by city with economic factors integration",
  "features": [
    "Forecasted demand by city",
    "Anticipated high-demand periods",
    "Early identification of emerging demand locations",
    "Economic factors integration"
  ],
  "supported_cities": "40 major Indian metropolitan cities",
  "version": "3.0.0",
  "enhanced": true
}
```

---

## 🚨 Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid input)
- **404**: Not Found (resource doesn't exist)
- **429**: Too Many Requests (rate limit exceeded)
- **500**: Internal Server Error

**Error Response Format:**
```json
{
  "error": "Error message description"
}
```

**Example Error Handling:**
```javascript
async function safePredictDemand(city, date) {
  try {
    const response = await fetch('http://localhost:5001/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ city, date })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Prediction failed');
    }
    
    const data = await response.json();
    return data.predicted_demand;
    
  } catch (error) {
    console.error('Error predicting demand:', error.message);
    // Show user-friendly error message
    alert(`Failed to predict demand: ${error.message}`);
    return null;
  }
}
```

---

## 🔒 Security & Rate Limiting

- **Rate Limit**: 100 requests per minute per IP address
- **Input Validation**: All inputs are validated and sanitized
- **CORS**: Enabled for cross-origin requests

**Rate Limit Error:**
```json
{
  "error": "Rate limit exceeded. Maximum 100 requests per minute."
}
```

---

## 📊 Complete React Example

```jsx
import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:5001';

function DemandForecastApp() {
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load cities on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/cities`)
      .then(res => res.json())
      .then(data => setCities(data.cities))
      .catch(err => console.error('Failed to load cities:', err));
  }, []);

  // Load model metrics on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/metrics`)
      .then(res => res.json())
      .then(data => setMetrics(data))
      .catch(err => console.error('Failed to load metrics:', err));
  }, []);

  const handlePredict = async () => {
    if (!selectedCity || !selectedDate) {
      setError('Please select both city and date');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          city: selectedCity,
          date: selectedDate
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Prediction failed');
      }

      const data = await response.json();
      setPrediction(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>Rental Demand Forecasting</h1>
      
      {/* Model Performance */}
      {metrics && (
        <div className="metrics-card">
          <h3>Model Performance</h3>
          <p>RMSE: {metrics.metrics.test_rmse.toFixed(6)}</p>
          <p>Accuracy: {(100 - metrics.metrics.test_mape).toFixed(2)}%</p>
          <p>Improvement: {metrics.baseline_comparison.improvement_percent}%</p>
        </div>
      )}

      {/* Prediction Form */}
      <div className="prediction-form">
        <select 
          value={selectedCity} 
          onChange={(e) => setSelectedCity(e.target.value)}
        >
          <option value="">Select City</option>
          {cities.map(city => (
            <option key={city} value={city}>{city}</option>
          ))}
        </select>

        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        />

        <button onClick={handlePredict} disabled={loading}>
          {loading ? 'Predicting...' : 'Predict Demand'}
        </button>
      </div>

      {/* Error Display */}
      {error && <div className="error">{error}</div>}

      {/* Prediction Result */}
      {prediction && (
        <div className="result-card">
          <h3>Prediction Result</h3>
          <p><strong>City:</strong> {prediction.city}</p>
          <p><strong>Date:</strong> {prediction.date}</p>
          <p><strong>Predicted Demand:</strong> {prediction.predicted_demand.toFixed(2)} properties/day</p>
        </div>
      )}
    </div>
  );
}

export default DemandForecastApp;
```

---

## 🎯 Best Practices

1. **Always validate inputs** before sending to API
2. **Handle errors gracefully** with user-friendly messages
3. **Use batch endpoint** when predicting for multiple cities
4. **Cache city list** - it doesn't change frequently
5. **Display model metrics** to build user trust
6. **Respect rate limits** - implement request throttling if needed
7. **Use loading states** for better UX

---

## 📞 Support

For issues or questions:
- Check API health: `GET /health`
- View model info: `GET /info`
- Review metrics: `GET /metrics`

**Model Details:**
- Trained on: 10,000,000 property listings
- Cities covered: 40 major Indian metros
- RMSE: 5.646 (89.36% improvement)
- MAPE: 0.1312% (92.3% improvement)
