# FRONTEND INTEGRATION GUIDE

## API Integration Overview

This guide provides instructions for frontend developer to integrate with the rental market intelligence API servers.

## Base URLs

### Product 1: Rental Demand Forecasting
- Development: `http://localhost:5001`
- Production: `[Production URL]`

### Product 2: Demand-Supply Gap Identification
- Development: `http://localhost:5002`
- Production: `[Production URL]`

## Authentication

No authentication required for development. For production deployment, API key authentication will be implemented.

## Common Headers

```http
Content-Type: application/json
Accept: application/json
```

## Error Handling

The API returns standard HTTP status codes:
- `200 OK` - Success
- `400 Bad Request` - Invalid input data
- `500 Internal Server Error` - Server error

## CORS Configuration

API servers are configured to allow requests from any origin during development:
```python
Access-Control-Allow-Origin: *
```

## Health Check

Verify API server availability:
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "rental_demand_forecast|gap_identification",
  "version": "1.0.0"
}
```

## Frontend Implementation Examples

### JavaScript (Fetch API)
```javascript
// Health check
fetch('http://localhost:5001/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Single prediction
fetch('http://localhost:5001/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    city: 'Mumbai',
    bhk: 2,
    posted_on: '2024-01-15'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### React Hook Example
```javascript
import { useState, useEffect } from 'react';

function useRentalAPI() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const predictDemand = async (input) => {
    try {
      const response = await fetch('http://localhost:5001/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input)
      });
      
      if (!response.ok) throw new Error('API request failed');
      
      const result = await response.json();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  return { data, loading, error, predictDemand };
}
```

## Response Format

Both products return consistent response formats:

### Success Response
```json
{
  "success": true,
  "data": {
    "prediction": 75000,
    "confidence": 0.89,
    "model_version": "1.0.0"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Invalid input parameters",
  "details": "City parameter is required"
}
```

## Batch Processing

For multiple predictions, use the batch endpoint to improve performance:

```bash
POST /predict/batch
```

Input format:
```json
{
  "records": [
    {
      "city": "Bangalore",
      "bhk": 2,
      "posted_on": "2024-01-15"
    },
    {
      "city": "Hyderabad",
      "bhk": 3,
      "posted_on": "2024-01-16"
    }
  ]
}
```

## Environment Configuration

Create a config file for different environments:

```javascript
// config/api.js
const API_CONFIG = {
  development: {
    DEMAND_API_URL: 'http://localhost:5001',
    GAP_API_URL: 'http://localhost:5002'
  },
  production: {
    DEMAND_API_URL: 'https://api.production.com/demand',
    GAP_API_URL: 'https://api.production.com/gap'
  }
};

export default API_CONFIG[process.env.NODE_ENV || 'development'];
```

## Performance Tips

1. Cache frequent predictions when possible
2. Use batch endpoints for multiple predictions
3. Implement loading states for better UX
4. Add timeout handling (recommended: 10 seconds)
5. Implement retry logic for failed requests

## Security Considerations

1. Never expose API keys in client-side code
2. Validate all user inputs before sending to API
3. Sanitize API responses before displaying
4. Use HTTPS in production environments

## Troubleshooting

### Common Issues

**CORS Errors**
- Ensure backend server has CORS enabled
- Check browser console for specific error messages

**Connection Refused**
- Verify API server is running
- Check port numbers and localhost configuration

**Invalid Response**
- Validate request payload structure
- Check API documentation for required fields
# Rental Market Intelligence Platform

## Project Overview

This project implements two AI products for analyzing the Indian rental market:

- **Product 1**: Rental Demand Forecasting Model
- **Product 2**: Demand-Supply Gap Identification Model

Both products are trained and ready to use with pre-trained models included.

## Quick Start (Minimal Installation)

For immediate use without large datasets:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install Git LFS and download model files:
   ```bash
   git lfs install
   git lfs pull
   ```

   > **Important**: You must run `git lfs pull` to download the pre-trained model files. Without these files, the API servers will not function.

3. Navigate to either product directory:
   ```bash
   cd Product_1_Rental_Demand_Forecasting
   # or
   cd Product_2_Demand_Supply_Gap_Identification
   ```

4. Install dependencies:
   ```bash
   pip install flask scikit-learn pandas numpy
   ```

5. Start the API server:
   ```bash
   python api_server.py
   ```

## Repository Structure Optimization

This repository has been optimized to be lightweight for deployment:

- Large raw datasets (~5GB) are not included in the Git repository
- Only essential trained models and API servers are included
- Pre-trained model files (.pkl) are managed through Git LFS
- All functionality preserved while minimizing repository size

## API Endpoints

### Product 1 (Port 5001):
- `GET /health` - Health check
- `POST /predict` - Make demand forecast
- `POST /predict/batch` - Batch predictions

### Product 2 (Port 5002):
- `GET /health` - Health check
- `POST /predict` - Make gap analysis
- `POST /predict/batch` - Batch predictions

## Model Files (Managed via Git LFS)

The pre-trained models are stored using Git LFS:
- `demand_forecast_model_efficient.pkl` - Product 1 model
- `gap_analysis_model_efficient.pkl` - Product 2 model
- Feature scalers for preprocessing

## Frontend Integration

See [FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md) for detailed instructions on integrating with the API servers.

## Re-training Models (Optional)

If you need to retrain the models with additional data:

1. Follow the quick start steps above
2. Download the original datasets separately (not included in Git due to size)
3. Place the data files in the appropriate directories
4. Run the training scripts:
   ```bash
   python train_demand_model_efficient.py  # For Product 1
   python train_gap_model_efficient.py     # For Product 2
   ```

## Requirements

- Python 3.8+
- Git LFS (for model files)
- Dependencies listed in each product's documentation

## License

[Specify your license here]