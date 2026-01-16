# Product 1: Rental Demand Forecasting Tool

## Overview
A predictive model that estimates future rental demand based on historical patterns. This tool helps developers, investors, and strategic planners make informed decisions about property development timing and market entry.

## Dataset Attributes Used
- Posted On (date)
- City (40 major Indian cities)
- BHK (property type)
- Rent (monthly rent in INR)

## Demand Insights Delivered
- Forecasted demand by city and property type
- Anticipated high-demand periods
- Early identification of emerging demand locations

## Why It Is Demand-Focused
The forecasting model extends historical demand patterns into future tenant behavior, providing actionable insights for real estate market participants.

## Target Users
- **Developers**: Identify optimal timing for launching new properties
- **Investors**: Spot undervalued markets before demand surges
- **Strategic Planners**: Allocate resources based on predicted demand trends

## Key Components
1. **Data Preparation** (`prepare_demand_data.py`) - Processes raw rental data into model-ready format
2. **Model Training** (`train_demand_model.py`) - Trains the LightGBM forecasting model
3. **Model Serving** (`serve_demand_model.py`) - Loads and serves the trained model
4. **API Server** (`api_server.py`) - Provides RESTful API for web integration
5. **Evaluation Reports** - Various reports documenting model performance and readiness

## Technical Implementation
- **Model Type**: LightGBM gradient boosting regressor
- **Performance**: 0.1312% MAPE (92.3% improvement over baseline)
- **Features**: 20+ engineered features including temporal, demographic, and historical patterns
- **API**: Flask-based REST API with endpoints for single and batch predictions

## How to Use
1. Ensure all requirements are installed: `pip install -r requirements.txt`
2. Start the API server: `python api_server.py`
3. Access endpoints at `http://localhost:5001`

## API Endpoints
- `GET /health` - Check if the API is running
- `GET /model/info` - Get model information
- `GET /cities` - List supported cities
- `POST /predict` - Get demand prediction for a city and date
- `POST /predict/batch` - Get batch predictions

## Related Documentation
- [Model Enhancement Report](MODEL_ENHANCEMENT_REPORT.md)
- [Model Evaluation Report](MODEL_EVALUATION_REPORT.md)
- [Model Readiness Report](MODEL_READINESS_REPORT.md)
- [Web API Integration Guide](WEB_API_INTEGRATION.md)
- [Web Integration Summary](WEB_INTEGRATION_SUMMARY.md)