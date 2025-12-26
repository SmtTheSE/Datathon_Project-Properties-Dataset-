import pandas as pd
import numpy as np
from serve_gap_model import GapAnalysisService

def test_gap_model():
    """
    Test the demand-supply gap model with sample data.
    """
    print("Testing Demand-Supply Gap Identification Model")
    print("=" * 50)
    
    # Initialize model server
    try:
        model_server = GapAnalysisService()
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return
    
    # Test cases with more diverse scenarios
    test_cases = [
        {
            "name": "High Demand, Low Supply Market",
            "city": "Mumbai",
            "area_locality": "Bandra",
            "bhk": "2",
            "avg_rent": 40000,
            "economic_indicators": {
                "inflation_rate": 8.0,      # High inflation
                "interest_rate": 6.5,       # Moderate interest
                "employment_rate": 90.0,    # High employment
                "covid_impact_score": 0.02, # Low impact
                "economic_health_score": 0.92, # Strong economy
                "city_tier": "Tier1",
                "region": "West"
            }
        },
        {
            "name": "Low Demand, High Supply Market",
            "city": "Tier3_City",
            "area_locality": "Outskirts",
            "bhk": "1",
            "avg_rent": 8000,
            "economic_indicators": {
                "inflation_rate": 4.0,      # Low inflation
                "interest_rate": 8.5,       # High interest
                "employment_rate": 70.0,    # Low employment
                "covid_impact_score": 0.5,  # High impact
                "economic_health_score": 0.5, # Weak economy
                "city_tier": "Tier3",
                "region": "East"
            }
        },
        {
            "name": "Balanced Market",
            "city": "Bangalore",
            "area_locality": "Suburb",
            "bhk": "2",
            "avg_rent": 20000,
            "economic_indicators": {
                "inflation_rate": 6.0,
                "interest_rate": 7.0,
                "employment_rate": 82.0,
                "covid_impact_score": 0.1,
                "economic_health_score": 0.75,
                "city_tier": "Tier1",
                "region": "South"
            }
        },
        {
            "name": "Premium Location",
            "city": "Delhi",
            "area_locality": "Connaught Place",
            "bhk": "3",
            "avg_rent": 60000,
            "economic_indicators": {
                "inflation_rate": 7.0,
                "interest_rate": 6.0,
                "employment_rate": 88.0,
                "covid_impact_score": 0.05,
                "economic_health_score": 0.88,
                "city_tier": "Tier1",
                "region": "North"
            }
        },
        {
            "name": "Budget Segment",
            "city": "Pune",
            "area_locality": "Periphery",
            "bhk": "1",
            "avg_rent": 10000,
            "economic_indicators": {
                "inflation_rate": 5.5,
                "interest_rate": 7.5,
                "employment_rate": 78.0,
                "covid_impact_score": 0.2,
                "economic_health_score": 0.70,
                "city_tier": "Tier2",
                "region": "West"
            }
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
                avg_rent=test_case["avg_rent"],
                economic_indicators=test_case["economic_indicators"]
            )
            
            print(f"\nTest Case {i}: {test_case['name']}")
            print(f"  Location: {result['city']}, {result['area_locality']} ({result['bhk']} BHK)")
            print(f"  Avg Rent: ₹{result['avg_rent']:,}")
            print(f"  Predicted Gap Ratio: {result['predicted_gap_ratio']:.3f}")
            print(f"  Gap Severity: {result['gap_severity'].upper()}")
            print(f"  Status: {result['demand_supply_status'].replace('_', ' ').title()}")
            
        except Exception as e:
            print(f"✗ Error in test case {i}: {e}")
    
    print("\n" + "=" * 50)
    print("Testing completed.")

if __name__ == "__main__":
    test_gap_model()