import requests
import json
import time

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_scenario(name, city, factors, description):
    print(f"\n🧪 Testing Scenario: {name}")
    print(f"   Context: {description}")
    print(f"   Input: City={city}, Factors={factors}")
    
    try:
        url = "http://localhost:5001/predict/enhanced"
        payload = {
            "city": city,
            "date": "2024-08-15",
            "economic_factors": factors,
            "include_tenant_quality": True
        }
        
        start = time.time()
        response = requests.post(url, json=payload, timeout=10)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            rec = data['investment_recommendation']
            quality = data['tenant_quality_analysis']
            
            print(f"   ✅ Response in {duration:.2f}s:")
            print(f"      • Base Demand:      {data['base_demand']['predicted_demand']}")
            print(f"      • Investment:       {rec['rating']} ({rec['confidence']*100:.0f}%)")
            print(f"      • Quality Score:    {rec['quality_score']}")
            print(f"      • Grade A Tenants:  {quality['high_quality_pct']*100:.1f}%")
            print(f"      • Grade D Tenants:  {quality['high_risk_pct']*100:.1f}%")
            print(f"      • Risk (Default):   {quality['average_default_risk']*100:.1f}%")
            print(f"      • Adj. Demand:      {data['quality_adjusted_demand']}")
            
            return data
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def verify_gap_analysis(city):
    print(f"\n🧪 Testing Gap Analysis: {city}")
    try:
        url = "http://localhost:5002/predict"
        payload = {
             "city": city, 
             "locality": "Area 1", # Generic area to get city average
             "bhk": "2 BHK", 
             "rent": 25000
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Gap: {data['predicted_gap_ratio']:.3f} ({data['gap_severity']})")
        else:
            print("   ⚠️ Gap API validation skipped (or failed)")
    except:
        print("   ⚠️ Gap API not reachable")

if __name__ == "__main__":
    print_header("PRODUCTION REALISM VERIFICATION")
    print("Verifying that models respond LOGICALLY to different inputs.")
    
    # SCENARIO 1: Prime Market (Mumbai) - Stable Economy
    mumbai = test_scenario(
        "Prime Market (Tier 1)", 
        "Mumbai", 
        {"inflation_rate": 5.5, "interest_rate": 7.0},
        "High demand city, healthy economy"
    )
    
    # SCENARIO 2: Weak Market (Palakkad) - Stable Economy
    palakkad = test_scenario(
        "Weak Market (Tier 3)", 
        "Palakkad", 
        {"inflation_rate": 5.5, "interest_rate": 7.0},
        "Lower tier city, same economy"
    )
    
    # SCENARIO 3: Crisis Mode (Mumbai) - High Inflation
    crisis = test_scenario(
        "Economic Crisis (Tier 1)", 
        "Mumbai", 
        {"inflation_rate": 15.0, "interest_rate": 12.0},
        "Same city, but high inflation/rates (Should lower quality/demand)"
    )

    print_header("VERIFICATION RESULTS")
    
    # Check 1: Tier differentiation
    if mumbai and palakkad:
        diff_demand = mumbai['base_demand']['predicted_demand'] - palakkad['base_demand']['predicted_demand']
        diff_risk = palakkad['tenant_quality_analysis']['average_default_risk'] - mumbai['tenant_quality_analysis']['average_default_risk']
        
        print("1. Tier Differentiation (Mumbai vs Palakkad):")
        print(f"   • Demand Drop: {diff_demand:.0f} points (Expect positive)")
        print(f"   • Risk Increase: +{diff_risk*100:.1f}% (Expect positive)")
        
        if diff_demand > 500 and diff_risk > 0.1:
            print("   ✅ PASS: Model correctly discriminates between City Tiers.")
        else:
            print("   ❌ FAIL: Model treats distinct cities too similarly.")

    # Check 2: Economic Sensitivity
    if mumbai and crisis:
        risk_increase = crisis['tenant_quality_analysis']['average_default_risk'] - mumbai['tenant_quality_analysis']['average_default_risk']
        demand_drop = mumbai['base_demand']['predicted_demand'] - crisis['base_demand']['predicted_demand']
        
        print("\n2. Economic Sensitivity (Normal vs Crisis):")
        print(f"   • Risk Increase:   +{risk_increase*100:.1f}% (Expect increase)")
        print(f"   • Demand Impact:   -{demand_drop:.0f} (Expect decrease)")
        
        if risk_increase > 0.05: # At least 5% increase in risk
            print("   ✅ PASS: Tenant Risk Model reacts to macroeconomic stress.")
        else:
            print("   ⚠️ WARNING: Model sensitivity to inflation seems low.")

    print("\n" + "="*60)
    print(" VERIFICATION COMPLETE")
    print("="*60)
