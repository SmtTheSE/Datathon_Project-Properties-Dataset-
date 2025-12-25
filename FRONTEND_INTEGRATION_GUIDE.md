# Frontend Integration Guide for Rental Market Intelligence Dashboard

**Document prepared by**: Sitt Min Thar  
**Contact**: sittminthar005@gmail.com  
**Date**: December 25, 2025  
**Project**: Rental Market Intelligence Dashboard

## Overview

This document provides comprehensive guidelines for Thu Htet Naing to integrate Product 1 (Rental Demand Forecasting) and Product 2 (Demand-Supply Gap Identification) into the web application. The guide includes API endpoints, request/response formats, sample code, and best practices for a seamless user experience.

## Architecture Overview

The system uses a microservice architecture with separate APIs for each product:

- **Product 1 API**: Rental demand forecasting (typically on port 5000)
- **Product 2 API**: Demand-supply gap analysis (typically on port 5001)
- **Frontend Application**: React/Vue.js consuming both APIs
- **API Gateway** (optional): For unified access to both services

## API Endpoints

### Product 1: Rental Demand Forecasting

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check service health |
| GET | `/model/info` | Get model information |
| GET | `/cities` | Get supported cities |
| POST | `/predict` | Single demand prediction |
| POST | `/predict/batch` | Batch demand predictions |

### Product 2: Demand-Supply Gap Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check service health |
| GET | `/model/info` | Get model information |
| GET | `/cities` | Get supported cities |
| POST | `/predict` | Single gap analysis |
| POST | `/predict/batch` | Batch gap analysis |

## Request/Response Formats

### Product 1: Demand Forecasting

#### Single Prediction Request
```json
{
  "city": "Mumbai",
  "date": "2025-06-15"
}
```

#### Single Prediction Response
```json
{
  "city": "Mumbai",
  "date": "2025-06-15",
  "predicted_demand": 125.5,
  "confidence_interval": {
    "lower": 110.2,
    "upper": 140.8
  }
}
```

#### Batch Prediction Request
```json
{
  "requests": [
    {
      "city": "Mumbai",
      "date": "2025-06-15"
    },
    {
      "city": "Delhi",
      "date": "2025-06-16"
    }
  ]
}
```

#### Batch Prediction Response
```json
{
  "predictions": [
    {
      "city": "Mumbai",
      "date": "2025-06-15",
      "predicted_demand": 125.5
    },
    {
      "city": "Delhi",
      "date": "2025-06-16",
      "predicted_demand": 98.3
    }
  ]
}
```

### Product 2: Gap Analysis

#### Single Prediction Request
```json
{
  "city": "Mumbai",
  "area_locality": "Andheri",
  "bhk": "2",
  "year": 2025,
  "month": 6,
  "supply": 150,
  "avg_rent": 25000
}
```

#### Single Prediction Response
```json
{
  "city": "Mumbai",
  "area_locality": "Andheri",
  "bhk": "2",
  "year": 2025,
  "month": 6,
  "supply": 150,
  "demand_proxy": 165.2,
  "absolute_gap": 15.2,
  "gap_ratio": 0.101,
  "interpretation": "Moderate demand surplus - Good investment potential",
  "confidence_interval": {
    "lower": 0.05,
    "upper": 0.15
  }
}
```

## Sample Frontend Implementation

### JavaScript/React Example

```javascript
// Service class for API calls
class RentalMarketService {
  constructor() {
    this.product1Url = process.env.REACT_APP_PRODUCT1_API_URL || 'http://localhost:5000';
    this.product2Url = process.env.REACT_APP_PRODUCT2_API_URL || 'http://localhost:5001';
  }

  // Fetch supported cities from both products
  async getSupportedCities() {
    try {
      const [demandCities, gapCities] = await Promise.all([
        fetch(`${this.product1Url}/cities`).then(res => res.json()),
        fetch(`${this.product2Url}/cities`).then(res => res.json())
      ]);
      
      return {
        demandForecastingCities: demandCities,
        gapAnalysisCities: gapCities
      };
    } catch (error) {
      console.error('Error fetching cities:', error);
      throw error;
    }
  }

  // Get rental demand forecast
  async getDemandForecast(city, date) {
    try {
      const response = await fetch(`${this.product1Url}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ city, date })
      });
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching demand forecast:', error);
      throw error;
    }
  }

  // Get demand-supply gap analysis
  async getGapAnalysis(city, area_locality, bhk, year, month, supply, avg_rent) {
    try {
      const response = await fetch(`${this.product2Url}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          city, 
          area_locality, 
          bhk, 
          year, 
          month, 
          supply, 
          avg_rent 
        })
      });
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching gap analysis:', error);
      throw error;
    }
  }

  // Get combined insights
  async getCombinedInsights(city, area_locality, bhk, date, supply, avg_rent) {
    try {
      const [demandForecast, gapAnalysis] = await Promise.all([
        this.getDemandForecast(city, date),
        this.getGapAnalysis(city, area_locality, bhk, 
                          new Date(date).getFullYear(), 
                          new Date(date).getMonth() + 1, 
                          supply, avg_rent)
      ]);
      
      return {
        demandForecast,
        gapAnalysis,
        combinedInsight: this.calculateCombinedInsight(demandForecast, gapAnalysis)
      };
    } catch (error) {
      console.error('Error fetching combined insights:', error);
      throw error;
    }
  }

  // Calculate combined insight based on both models
  calculateCombinedInsight(demandForecast, gapAnalysis) {
    const { predicted_demand } = demandForecast;
    const { gap_ratio, interpretation } = gapAnalysis;
    
    let investmentPotential = 'Unknown';
    
    if (gap_ratio > 0.05 && predicted_demand > 100) {
      investmentPotential = 'High';
    } else if (gap_ratio > 0 && predicted_demand > 50) {
      investmentPotential = 'Medium';
    } else if (gap_ratio < 0) {
      investmentPotential = 'Low';
    } else {
      investmentPotential = 'Moderate';
    }
    
    return {
      investmentPotential,
      recommendation: this.getRecommendation(investmentPotential, gapAnalysis.interpretation)
    };
  }

  getRecommendation(investmentPotential, gapInterpretation) {
    switch(investmentPotential) {
      case 'High':
        return 'This location shows strong investment potential with both high future demand and current undersupply.';
      case 'Medium':
        return 'Moderate investment opportunity with positive indicators from both models.';
      case 'Low':
        return 'Caution advised - market may be oversupplied based on gap analysis.';
      default:
        return 'Mixed signals - further analysis recommended before investment decision.';
    }
  }
}

// React component example
import React, { useState, useEffect } from 'react';

const MarketInsights = () => {
  const [service] = useState(new RentalMarketService());
  const [cities, setCities] = useState([]);
  const [formData, setFormData] = useState({
    city: '',
    area_locality: '',
    bhk: '2',
    date: new Date().toISOString().split('T')[0],
    supply: 100,
    avg_rent: 20000
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadCities = async () => {
      try {
        const cityData = await service.getSupportedCities();
        setCities(cityData.demandForecastingCities.cities || []);
      } catch (error) {
        console.error('Failed to load cities:', error);
      }
    };
    
    loadCities();
  }, [service]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const data = await service.getCombinedInsights(
        formData.city,
        formData.area_locality,
        formData.bhk,
        formData.date,
        formData.supply,
        formData.avg_rent
      );
      
      setResults(data);
    } catch (error) {
      console.error('Error getting insights:', error);
      alert('Failed to get market insights. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="market-insights">
      <h2>Rental Market Intelligence Dashboard</h2>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>City:</label>
          <select 
            name="city" 
            value={formData.city} 
            onChange={handleInputChange}
            required
          >
            <option value="">Select City</option>
            {cities.map(city => (
              <option key={city} value={city}>{city}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label>Area/Locality:</label>
          <input 
            type="text" 
            name="area_locality" 
            value={formData.area_locality} 
            onChange={handleInputChange}
            required 
          />
        </div>
        
        <div>
          <label>BHK Type:</label>
          <select 
            name="bhk" 
            value={formData.bhk} 
            onChange={handleInputChange}
          >
            <option value="1">1 BHK</option>
            <option value="2">2 BHK</option>
            <option value="3">3 BHK</option>
            <option value="4">4 BHK</option>
          </select>
        </div>
        
        <div>
          <label>Supply Count:</label>
          <input 
            type="number" 
            name="supply" 
            value={formData.supply} 
            onChange={handleInputChange}
            min="1"
          />
        </div>
        
        <div>
          <label>Average Rent (₹):</label>
          <input 
            type="number" 
            name="avg_rent" 
            value={formData.avg_rent} 
            onChange={handleInputChange}
            min="1000"
          />
        </div>
        
        <div>
          <label>Forecast Date:</label>
          <input 
            type="date" 
            name="date" 
            value={formData.date} 
            onChange={handleInputChange}
            required
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Get Market Insights'}
        </button>
      </form>
      
      {results && (
        <div className="results">
          <h3>Market Insights</h3>
          <div className="demand-forecast">
            <h4>Demand Forecast</h4>
            <p>Predicted demand: <strong>{results.demandForecast.predicted_demand.toFixed(2)}</strong> listings</p>
          </div>
          
          <div className="gap-analysis">
            <h4>Supply-Demand Gap</h4>
            <p>Gap ratio: <strong>{(results.gapAnalysis.gap_ratio * 100).toFixed(2)}%</strong></p>
            <p>Interpretation: {results.gapAnalysis.interpretation}</p>
          </div>
          
          <div className="combined-insight">
            <h4>Investment Potential: {results.combinedInsight.investmentPotential}</h4>
            <p>{results.combinedInsight.recommendation}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketInsights;
```

## Best Practices for Frontend Integration

### 1. Error Handling
- Always implement proper error handling for API calls
- Display user-friendly error messages
- Implement retry logic for failed requests
- Show loading states during API calls

### 2. Performance Optimization
- Implement caching for frequently accessed data
- Use pagination for large datasets
- Implement debouncing for search inputs
- Optimize API calls to reduce unnecessary requests

### 3. User Experience
- Provide clear instructions and tooltips
- Validate inputs before sending to API
- Show progress indicators during analysis
- Design responsive layouts for different screen sizes

### 4. Data Visualization
- Use charts and graphs to visualize predictions
- Implement heat maps for city comparisons
- Show trends with time series visualizations
- Highlight key metrics with clear visual indicators

## Environment Configuration

Create a `.env` file in your frontend project root:

```bash
REACT_APP_PRODUCT1_API_URL=http://localhost:5000
REACT_APP_PRODUCT2_API_URL=http://localhost:5001
REACT_APP_API_TIMEOUT=30000
```

## Testing Guidelines

### Unit Tests
```javascript
// Example unit test for service methods
describe('RentalMarketService', () => {
  let service;
  
  beforeEach(() => {
    service = new RentalMarketService();
    // Mock fetch API
    global.fetch = jest.fn();
  });
  
  test('should fetch demand forecast correctly', async () => {
    const mockResponse = {
      city: 'Mumbai',
      date: '2025-06-15',
      predicted_demand: 125.5
    };
    
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockResponse
    });
    
    const result = await service.getDemandForecast('Mumbai', '2025-06-15');
    
    expect(result).toEqual(mockResponse);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/predict'),
      expect.objectContaining({ method: 'POST' })
    );
  });
});
```

### Integration Testing
- Test the combined insights functionality
- Verify data flows between both APIs
- Test error scenarios and fallbacks
- Validate response formatting and data consistency

## Security Considerations

- Never expose API credentials in frontend code
- Implement rate limiting on the frontend
- Sanitize all user inputs
- Use HTTPS for all API communications
- Implement proper authentication if required

## Deployment Considerations

- Configure proxy settings if APIs are on different domains
- Set up environment-specific API URLs
- Implement health checks for both services
- Monitor API response times and error rates
- Plan for graceful degradation if one service is unavailable