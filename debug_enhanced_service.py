
import os
import sys

# Add directory to path
base_dir = '/Users/sittminthar/Downloads/Datathon_Project-Properties-Dataset--master/Product_1_Rental_Demand_Forecasting'
sys.path.append(base_dir)

os.chdir(base_dir)

try:
    from enhanced_prediction_service import EnhancedPredictionService
    
    demand_model_path = os.path.join(base_dir, 'demand_model.onnx')
    tenant_risk_model_path = os.path.join(base_dir, 'tenant_risk_model.pkl')
    
    print(f"Attempting to load service with:")
    print(f"Demand: {demand_model_path}")
    print(f"Risk: {tenant_risk_model_path}")
    
    service = EnhancedPredictionService(
        demand_model_path=demand_model_path,
        tenant_risk_model_path=tenant_risk_model_path
    )
    print("SUCCESS: Service loaded")
except Exception as e:
    import traceback
    traceback.print_exc()
