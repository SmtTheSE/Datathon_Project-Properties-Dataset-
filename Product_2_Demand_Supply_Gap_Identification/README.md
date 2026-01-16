# Product 2: Demand-Supply Gap Identification Tool

## Overview
A strategic product that highlights areas where demand exceeds supply in rental markets. This tool helps real estate developers and investment analysts identify high-potential investment zones and avoid oversaturated markets.

## Dataset Attributes Used
- City (40 major Indian cities)
- Area Locality
- BHK (property type)
- Posted On (date)
- Rent (monthly rent in INR)

## Demand Insights Delivered
- High-demand but under-listed locations
- Oversupplied areas with weaker demand
- Investment opportunity zones

## Why It Is Demand-Focused
This tool prioritizes unmet tenant demand rather than just listing volume, helping stakeholders make informed decisions based on actual market needs.

## Target Users
- **Real Estate Developers**: Identify underserved markets for new developments
- **Investment Analysts**: Spot profitable investment opportunities and avoid oversaturated areas

## Key Components
1. **Data Preparation** (`prepare_gap_data.py`) - Processes raw rental data to create supply-demand features
2. **Model Training** (`train_gap_model.py`) - Trains the LightGBM gap identification model
3. **Model Serving** (`serve_gap_model.py`) - Loads and serves the trained model
4. **API Server** (`api_server.py`) - Provides RESTful API for web integration

## Technical Implementation
- **Model Type**: LightGBM gradient boosting regressor with spatio-temporal features
- **Features**: Temporal features, location encodings, supply-demand metrics
- **API**: Flask-based REST API with endpoints for single and batch predictions

## How to Use
1. Ensure all requirements are installed: `pip install -r requirements.txt`
2. Prepare the data: `python prepare_gap_data.py`
3. Train the model: `python train_gap_model.py`
4. Start the API server: `python api_server.py`
5. Access endpoints at `http://localhost:5002`

## API Endpoints
- `GET /health` - Check if the API is running
- `GET /model/info` - Get model information
- `GET /cities` - List supported cities
- `POST /predict` - Get gap prediction for a specific location and property type
- `POST /predict/batch` - Get batch predictions

## Model Interpretation
The model outputs a gap ratio indicating the relationship between demand and supply:
- **Positive values**: Demand exceeds supply (investment opportunities)
- **Negative values**: Supply exceeds demand (market saturation)
- **Near zero**: Balanced market conditions

## Related Research
Based on Multi-Task Spatio-Temporal Deep Model approach:
- Best at forecasting demand and gap together
- Captures spatial relationships and time dynamics
- Feature engineering includes temporal features, location encodings, and economic indicators
- Uses rolling cross-validation for better time forecasting generalization
- Evaluated with MAPE/RMSE for forecast accuracy and gap accuracy metrics