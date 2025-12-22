import pandas as pd
import numpy as np
from serve_gap_model import GapModelServer

def test_gap_model():
    """
    Test the demand-supply gap model with sample data.
    """
    print("Testing Demand-Supply Gap Identification Model")
    print("=" * 50)
    
    # Initialize model server
    try:
        model_server = GapModelServer()
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return
    
    # Test cases
    test_cases = [
        {
            "city": "Mumbai",
            "area_locality": "Andheri",
            "bhk": "2",
            "year": 2024,
            "month": 6,
            "supply": 150,
            "avg_rent": 25000,
            "expected": "high_demand"
        },
        {
            "city": "Delhi",
            "area_locality": "Dwarka",
            "bhk": "3",
            "year": 2024,
            "month": 6,
            "supply": 80,
            "avg_rent": 18000,
            "expected": "moderate_demand"
        },
        {
            "city": "Bangalore",
            "area_locality": "Whitefield",
            "bhk": "1",
            "year": 2024,
            "month": 6,
            "supply": 300,
            "avg_rent": 15000,
            "expected": "balanced"
        },
        {
            "city": "Chennai",
            "area_locality": "T Nagar",
            "bhk": "2",
            "year": 2024,
            "month": 6,
            "supply": 50,
            "avg_rent": 12000,
            "expected": "high_demand"
        }
    ]
    
    print("\nRunning test predictions:")
    print("-" * 30)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            result = model_server.predict_gap(
                city=test_case["city"],
                area_locality=test_case["area_locality"],
                bhk=test_case["bhk"],
                year=test_case["year"],
                month=test_case["month"],
                supply=test_case["supply"],
                avg_rent=test_case["avg_rent"]
            )
            
            print(f"\nTest Case {i}:")
            print(f"  Location: {result['city']}, {result['area_locality']} ({result['bhk']} BHK)")
            print(f"  Supply: {result['supply']} listings")
            print(f"  Demand Proxy: {result['demand_proxy']:.1f} listings")
            print(f"  Absolute Gap: {result['absolute_gap']:.1f} listings")
            print(f"  Gap Ratio: {result['gap_ratio']:.3f}")
            print(f"  Interpretation: {result['interpretation']}")
            
        except Exception as e:
            print(f"✗ Error in test case {i}: {e}")
    
    print("\n" + "=" * 50)
    print("Testing completed.")

if __name__ == "__main__":
    test_gap_model()