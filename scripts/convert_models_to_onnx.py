import os
import joblib
import numpy as np
from sklearn.pipeline import Pipeline
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnx

def convert_product_1():
    print("Converting Product 1 (Demand Forecasting)...")
    base_path = "Product_1_Rental_Demand_Forecasting"
    model_path = os.path.join(base_path, "demand_forecast_model_efficient.pkl")
    scaler_path = os.path.join(base_path, "feature_scaler_efficient.pkl")
    output_path = os.path.join(base_path, "demand_model.onnx")

    if not os.path.exists(model_path):
        print(f"Error: {model_path} not found")
        return

    # Load models
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # Create a pipeline
    pipeline = Pipeline([
        ('scaler', scaler),
        ('model', model)
    ])

    # Define input type (check feature count from scaler)
    # The scaler stores n_features_in_
    n_features = scaler.n_features_in_
    initial_type = [('float_input', FloatTensorType([None, n_features]))]

    # Convert with explicit opset version for compatibility
    # Render supports opset 20 (stable), not 21 (under development)
    onnx_model = convert_sklearn(pipeline, initial_types=initial_type, target_opset=20)

    # Force IR version for compatibility (Render supports max IR 9)
    onnx_model.ir_version = 9

    # Save
    with open(output_path, "wb") as f:
        f.write(onnx_model.SerializeToString())
    print(f"Saved to {output_path} (opset 20, IR version 9)")

def convert_product_2():
    print("Converting Product 2 (Gap Analysis)...")
    base_path = "Product_2_Demand_Supply_Gap_Identification"
    model_path = os.path.join(base_path, "gap_analysis_model_efficient.pkl")
    scaler_path = os.path.join(base_path, "feature_scaler_gap_efficient.pkl")
    output_path = os.path.join(base_path, "gap_model.onnx")

    if not os.path.exists(model_path):
        print(f"Error: {model_path} not found")
        return

    # Load models
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # Create a pipeline
    pipeline = Pipeline([
        ('scaler', scaler),
        ('model', model)
    ])

    # Define input type
    n_features = scaler.n_features_in_
    initial_type = [('float_input', FloatTensorType([None, n_features]))]

    # Convert with explicit opset version for compatibility
    onnx_model = convert_sklearn(pipeline, initial_types=initial_type, target_opset=20)
    
    # Force IR version for compatibility (Render supports max IR 9)
    onnx_model.ir_version = 9

    # Save
    with open(output_path, "wb") as f:
        f.write(onnx_model.SerializeToString())
    print(f"Saved to {output_path} (opset 20, IR version 9)")

if __name__ == "__main__":
    try:
        convert_product_1()
        convert_product_2()
        print("\nConversion complete!")
        print("Models are now compatible with onnxruntime 1.17.1 (opset 20, IR version 9)")
    except ImportError as e:
        print("Error: Missing libraries.")
        print("Please run: pip install skl2onnx onnx")
        print(f"Details: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
