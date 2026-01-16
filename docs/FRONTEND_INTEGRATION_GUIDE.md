# Frontend Integration Guide

## Overview
This document provides instructions for frontend developer to integrate with the pre-trained ML models for the Rental Market Intelligence Platform. The backend models are already trained and ready for API integration.

## Prerequisites

- Git installed on your system
- Git LFS (Large File Storage) installed
- Python 3.8+ (for running the API servers)

## Installation

### 1. Install Git LFS

Git LFS is required to download the pre-trained model files. If you don't have Git LFS installed:

**On macOS:**
```bash
brew install git-lfs
```

**On Windows (with Git for Windows):**
Git LFS is usually included with Git for Windows installer.

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get install git-lfs
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 3. Initialize Git LFS and Download Model Files

After cloning, you need to initialize Git LFS and download the large model files:

```bash
git lfs install
git lfs pull
```

This will download the pre-trained model files (`.pkl` files) that are required for the API servers to function.

> **Note**: The repository has been optimized to be lightweight. Large raw data files (~5GB) are not included in the Git repository as they are not needed for running the pre-trained models. Only the essential trained models and API servers are included.

## API Server Setup

### 1. Navigate to Product Directories

For Product 1 (Rental Demand Forecasting):
```bash
cd Product_1_Rental_Demand_Forecasting
```

For Product 2 (Demand-Supply Gap Identification):
```bash
cd Product_2_Demand_Supply_Gap_Identification
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

If there's no `requirements.txt` file, install the necessary packages:

```bash
pip install flask scikit-learn pandas numpy
```

### 3. Start API Servers

For Product 1:
```bash
python api_server.py
```

For Product 2:
```bash
python api_server.py
```

The API servers will start on their respective ports (likely 5001 and 5002).

## Available API Endpoints

### Product 1 - Rental Demand Forecasting
- `GET /health` - Check API health
- `GET /model/info` - Get model information
- `POST /predict` - Make a prediction for rental demand
- `POST /predict/batch` - Make batch predictions

### Product 2 - Demand-Supply Gap Identification
- `GET /health` - Check API health
- `GET /model/info` - Get model information
- `POST /predict` - Make a prediction for demand-supply gap
- `POST /predict/batch` - Make batch predictions

## API Request Examples

### For Rental Demand Forecasting:
```javascript
fetch('http://localhost:5001/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    city: "Mumbai",
    year: 2024,
    month: 6,
    economic_indicators: {
      inflation_rate: 6.5,
      interest_rate: 7.0,
      employment_rate: 85.0
    }
  })
})
.then(response => response.json())
.then(data => {
  console.log('Predicted demand:', data.predicted_demand);
});
```

### For Demand-Supply Gap Analysis:
```javascript
fetch('http://localhost:5002/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    city: "Mumbai",
    area_locality: "Area 191",
    bhk: "2",
    avg_rent: 35000,
    economic_indicators: {
      inflation_rate: 6.0,
      interest_rate: 7.0,
      employment_rate: 85.0,
      covid_impact_score: 0.1,
      economic_health_score: 0.85
    }
  })
})
.then(response => response.json())
.then(data => {
  console.log('Gap ratio:', data.predicted_gap_ratio);
  console.log('Gap severity:', data.gap_severity);
});
```

## Model Testing Information

The models have been extensively tested and validated with the following results:

### Product 1: Rental Demand Forecasting
- **Performance**: The model provides realistic demand forecasts for major Indian cities
- **Features**: Incorporates economic indicators like inflation, interest rates, and employment data
- **Validation**: Uses time-series appropriate validation (TimeSeriesSplit) to prevent data leakage
- **Ready for Production**: The model has been tested with diverse scenarios and shows consistent performance

### Product 2: Demand-Supply Gap Identification
- **Performance**: Successfully identifies markets with different gap conditions
- **Features**: Considers rent levels, economic factors, and supply metrics
- **Validation**: Trained with diverse market conditions showing both demand > supply and supply > demand scenarios
- **Ready for Production**: The model has been validated with multiple real-world scenarios

## Important Notes

1. **Git LFS Required**: You must run `git lfs pull` to download the pre-trained model files. Without these files, the API servers will not function.

2. **No Training Required**: The models are pre-trained and ready to use. You do not need to run any training scripts.

3. **Model Files**: The `.pkl` files contain the trained models and are essential for API functionality.

4. **Optimized Repository**: The repository has been optimized to be lightweight. Large raw data files are not included as they are not needed for API operation.

5. **API Documentation**: The API servers may have additional endpoints or parameters. Check the specific `api_server.py` files for detailed implementation.

6. **Error Handling**: The API servers include error handling for invalid inputs. Make sure to validate your requests before sending them.

## Troubleshooting

### If the API server fails to start:
1. Verify that you've run `git lfs pull` to download the model files
2. Check that all required dependencies are installed
3. Ensure the correct port is available

### If predictions seem incorrect:
1. Verify that the input format matches the expected schema
2. Check that the model files were downloaded correctly via Git LFS

### For performance issues:
1. The models are optimized for production use, but processing large batches may take time
2. Consider implementing caching for frequently requested predictions