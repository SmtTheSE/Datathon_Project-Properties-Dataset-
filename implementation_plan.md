# Implementation Plan - Cross-Platform Model Deployment (ONNX)

We are addressing the deployment failure caused by pickle incompatibility between Mac (local) and Linux (Render). Instead of retraining on synthetic data (which ignores the high-quality 10M dataset training), we will convert the existing pre-trained models to ONNX format.

## Proposed Changes

### 1. Model Conversion (Local)
- [NEW] `scripts/convert_models_to_onnx.py`: A script to load local `.pkl` models + scalers and export them as `Product_*/demand_model.onnx` and `Product_*/gap_model.onnx`.
- **Action**: Run this locally to generate the binary artifacts.

### 2. Service Layer Updates
We need to change how the Flask apps load and run the models.

#### Product 1 - Demand Forecasting
- [MODIFY] `Product_1_Rental_Demand_Forecasting/serve_demand_model.py`
    - Replace `joblib.load` with `onnxruntime.InferenceSession`.
    - Update `predict()` method to formatting inputs for ONNX runtime (which expects float32 arrays).
    - Remove separate scaler logic (scaler is now embedded in the ONNX pipeline).

#### Product 2 - Gap Analysis
- [MODIFY] `Product_2_Demand_Supply_Gap_Identification/serve_gap_model.py`
    - Similar updates: Replace joblib with ONNX runtime.

### 3. Dependency Management
- [MODIFY] `Product_1_Rental_Demand_Forecasting/requirements.txt`
- [MODIFY] `Product_2_Demand_Supply_Gap_Identification/requirements.txt`
    - Add `onnxruntime==1.17.1` (or stable version).
    - Keep `scikit-learn` if needed for other utils, but primary inference uses ONNX.

### 4. Build Process
- [MODIFY] `render_build.sh` (and copies in product folders)
    - Remove the "retrain models" logic.
    - Keep the installation of dependencies.

## Verification Plan

### Automated Verification
- Run the conversion script locally.
- Run `test_model_predictions.py` locally (after modifying it to check ONNX or creating a new test) to ensure predictions match (or are extremely close to) the pickle version.

### Manual Verification
- Deploy to Render.
- Verify that the service starts without `ValueError`.
