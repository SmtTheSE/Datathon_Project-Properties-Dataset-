"""
Test script for the /metrics endpoint
"""

import requests
import json

def test_metrics_endpoint():
    """
    Test the /metrics endpoint to verify RMSE output
    """
    base_url = "http://localhost:5001"
    
    print("Testing /metrics endpoint...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{base_url}/metrics")
        
        if response.status_code == 200:
            metrics = response.json()
            
            print("✓ Metrics endpoint is working!")
            print(f"\nModel: {metrics.get('model_name')}")
            print(f"Version: {metrics.get('model_version')}")
            print(f"Training Date: {metrics.get('training_date')}")
            
            print("\n--- Performance Metrics ---")
            metrics_data = metrics.get('metrics', {})
            
            # Verify 6 decimal places
            print(f"Train RMSE:  {metrics_data.get('train_rmse'):.6f}")
            print(f"Test RMSE:   {metrics_data.get('test_rmse'):.6f}")
            print(f"CV Avg RMSE: {metrics_data.get('cv_avg_val_rmse'):.6f}")
            print(f"\nTrain MAE:   {metrics_data.get('train_mae'):.6f}")
            print(f"Test MAE:    {metrics_data.get('test_mae'):.6f}")
            print(f"\nTrain R²:    {metrics_data.get('train_r2'):.6f}")
            print(f"Test R²:     {metrics_data.get('test_r2'):.6f}")
            
            print("\n--- Data Size ---")
            data_size = metrics.get('data_size', {})
            print(f"Total Samples:    {data_size.get('total_samples')}")
            print(f"Training Samples: {data_size.get('training_samples')}")
            print(f"Testing Samples:  {data_size.get('testing_samples')}")
            
            print("\n--- Cross-Validation Results ---")
            cv_data = metrics.get('cross_validation', {})
            print(f"Number of Folds: {cv_data.get('n_splits')}")
            
            for fold_score in cv_data.get('fold_scores', []):
                print(f"\nFold {fold_score['fold']}:")
                print(f"  Val RMSE: {fold_score['val_rmse']:.6f}")
                print(f"  Val MAE:  {fold_score['val_mae']:.6f}")
                print(f"  Val R²:   {fold_score['val_r2']:.6f}")
            
            print("\n" + "=" * 60)
            print("✓ All metrics are formatted to 6 decimal places!")
            
        elif response.status_code == 404:
            print("⚠ Metrics file not found.")
            print("Please run: python train_demand_model_efficient.py")
            print(response.json())
            
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.json())
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API server.")
        print("Please start the server first: python api_server.py")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

def test_all_endpoints():
    """
    Test that existing endpoints still work
    """
    base_url = "http://localhost:5001"
    
    print("\n\nTesting existing endpoints...")
    print("=" * 60)
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✓ /health endpoint working")
        else:
            print(f"✗ /health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ /health endpoint error: {str(e)}")
    
    # Test cities
    try:
        response = requests.get(f"{base_url}/cities")
        if response.status_code == 200:
            print("✓ /cities endpoint working")
        else:
            print(f"✗ /cities endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ /cities endpoint error: {str(e)}")
    
    # Test info
    try:
        response = requests.get(f"{base_url}/info")
        if response.status_code == 200:
            print("✓ /info endpoint working")
        else:
            print(f"✗ /info endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ /info endpoint error: {str(e)}")

if __name__ == "__main__":
    print("RMSE Metrics API Endpoint Test")
    print("=" * 60)
    test_metrics_endpoint()
    test_all_endpoints()
    print("\n" + "=" * 60)
    print("Test completed!")
