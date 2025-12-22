# Properties Dataset Datathon Project

This repository contains machine learning models and tools developed for analyzing a large-scale rental properties dataset.

## Dataset Overview

The dataset contains 10 million property rental listings across 40 major Indian metropolitan cities with the following attributes:
- Posted On (date)
- City (40 major Indian cities)
- BHK (property type)
- Rent (monthly rent in INR)

## Project Structure

```
├── Product_1_Rental_Demand_Forecasting/
│   ├── prepare_demand_data.py - Data preprocessing script
│   ├── train_demand_model.py - Model training implementation
│   ├── serve_demand_model.py - Model serving module
│   ├── api_server.py - REST API for model predictions
│   ├── requirements.txt - Python dependencies
│   ├── test_api_integration.py - API integration tests
│   ├── test_model_predictions.py - Model prediction tests
│   ├── MODEL_ENHANCEMENT_REPORT.md - Details on model improvements
│   ├── MODEL_EVALUATION_REPORT.md - Model performance evaluation
│   ├── MODEL_READINESS_REPORT.md - Comprehensive model readiness documentation
│   ├── WEB_API_INTEGRATION.md - Instructions for web API integration
│   ├── WEB_INTEGRATION_SUMMARY.md - Summary of web integration process
│   ├── DIRECT_ANSWER.md - Direct answer to model legitimacy question
│   └── README.md - Product-specific documentation
├── House_Rent_10M_balanced_40cities.csv - Main dataset (not tracked in Git due to size)
└── README.md - This file
```

## Products

### Product 1: Rental Demand Forecasting Tool

A predictive model that estimates future rental demand to help developers, investors, and strategic planners make informed decisions.

Key features:
- Forecasted demand by city and property type
- Anticipated high-demand periods
- Early identification of emerging demand locations

For detailed information about this product, see [Product_1_Rental_Demand_Forecasting/README.md](Product_1_Rental_Demand_Forecasting/README.md).

## Repository Management

Due to the large size of the dataset file (House_Rent_10M_balanced_40cities.csv), it is not tracked in Git. Git LFS is configured for large file storage, but the file is also excluded in .gitignore to prevent accidental commits.

## Getting Started

1. Navigate to the specific product folder you're interested in
2. Follow the README instructions in that folder
3. Install required dependencies with `pip install -r requirements.txt`
4. Run the application as described in the product documentation

## Future Development

Additional products will be added as separate folders following the same organizational structure as Product_1.