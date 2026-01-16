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