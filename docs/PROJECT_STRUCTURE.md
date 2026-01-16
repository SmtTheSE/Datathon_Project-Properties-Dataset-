# Rental Property AI - Project Structure

```
Datathon_Project-Properties-Dataset-/

 docs/ # Documentation
 API_INTEGRATION_GUIDE.md # Complete API documentation
 API_QUICK_REFERENCE.md # Quick API reference
 README.md # Project overview (if exists)

 scripts/ # Utility Scripts
 create_summary_data.py # One-time data aggregation script

 data/ # Data Files (gitignored)
 (Large dataset files go here)

 Product_1_Rental_Demand_Forecasting/ # Product 1 API
 api_server.py # Flask API server
 serve_demand_model.py # Model serving logic
 data_loader.py # Fast JSON data loader
 monthly_summary.json # Pre-aggregated data (3.3KB)
 demand_forecast_model_efficient.pkl # Trained model
 feature_scaler_efficient.pkl # Feature scaler
 MODEL_READINESS_REPORT.md # Model documentation

 Product_2_Demand_Supply_Gap_Identification/ # Product 2 API
 api_server.py # Flask API server
 serve_gap_model.py # Model serving logic
 data_loader.py # Fast JSON data loader
 locality_summary.json # Pre-aggregated data (1.8MB)
 gap_analysis_model_efficient.pkl # Trained model
 feature_scaler_gap_efficient.pkl # Feature scaler

 frontend/ # Next.js Frontend
 src/
 app/
 page.tsx # Home page
 demand-forecasting/ # Product 1 UI
 gap-analysis/ # Product 2 UI
 components/ # Shared components
 lib/ # API helpers
 public/
 package.json
 next.config.js

 .gitignore # Git ignore rules
 README.md # Main project README (create if missing)
```

## Directory Purposes

### `/docs` - Documentation
- API integration guides
- Model validation reports
- Setup instructions
- Architecture diagrams

### `/scripts` - Utility Scripts
- Data processing scripts
- One-time setup scripts
- Maintenance utilities

### `/data` - Data Files
- Large dataset files (gitignored)
- Training data
- Test data
- **Note:** Add to `.gitignore`

### `/Product_1_*` & `/Product_2_*` - API Services
- Self-contained API services
- Models and scalers
- Service-specific documentation

### `/frontend` - Web Application
- Next.js/React frontend
- UI components
- API integration code

## Quick Start

1. **Start Backend APIs:**
 ```bash
 # Terminal 1: Product 1
 cd Product_1_Rental_Demand_Forecasting
 python api_server.py

 # Terminal 2: Product 2
 cd Product_2_Demand_Supply_Gap_Identification
 python api_server.py
 ```

2. **Start Frontend:**
 ```bash
 # Terminal 3
 cd frontend
 npm run dev
 ```

3. **Access Application:**
 - Frontend: http://localhost:3000
 - Product 1 API: http://localhost:5001
 - Product 2 API: http://localhost:5002

## Documentation

- **API Integration:** See `docs/API_INTEGRATION_GUIDE.md`
- **Quick Reference:** See `docs/API_QUICK_REFERENCE.md`
- **Model Details:** See `Product_*/MODEL_READINESS_REPORT.md`

## Data Setup

If you need to regenerate aggregated data:
```bash
python scripts/create_summary_data.py
```

**Note:** This only needs to run once. The script processes the 10M row dataset and creates small JSON summary files.
