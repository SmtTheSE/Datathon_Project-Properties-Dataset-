"""
CRITICAL FIX: Intent Detection False Positive
"""

from chatbot_engine import RentalPropertyChatbot

def test_demand_vs_gap_distinction():
    """Test that demand forecast queries are NOT misclassified as gap analysis"""
    chatbot = RentalPropertyChatbot()
    
    print("=" * 80)
    print("TESTING DEMAND FORECAST vs GAP ANALYSIS DISTINCTION")
    print("=" * 80)
    
    # These should be DEMAND_FORECAST (no BHK/rent parameters)
    demand_queries = [
        "What is the rental demand forecast for Mumbai for January 2023?",
        "Show me demand forecast for Delhi",
        "Predict rental demand in Bangalore",
        "What's the demand in Mumbai?",
        "Rental demand for Chennai",
    ]
    
    # These should be GAP_ANALYSIS (has BHK or rent parameters)
    gap_queries = [
        "What is the demand for Mumbai with 2 BHK?",
        "Show me properties with rent 35000 in Delhi",
        "2 BHK and rent 35k in Bangalore",
        "Average rent 50000 in Mumbai",
        "3 BHK properties in Chennai",
    ]
    
    print("\n📊 DEMAND FORECAST QUERIES (should NOT trigger gap_analysis):")
    print("-" * 80)
    passed = 0
    failed = 0
    
    for query in demand_queries:
        intent, conf = chatbot.detect_intent(query)
        status = "✓" if intent == "demand_forecast" else "✗ FAIL"
        if intent == "demand_forecast":
            passed += 1
        else:
            failed += 1
        print(f"{status} {query}")
        print(f"   → Detected: {intent} (expected: demand_forecast)")
    
    print(f"\nDemand Forecast: {passed}/{len(demand_queries)} passed")
    
    print("\n🎯 GAP ANALYSIS QUERIES (should trigger gap_analysis):")
    print("-" * 80)
    gap_passed = 0
    gap_failed = 0
    
    for query in gap_queries:
        intent, conf = chatbot.detect_intent(query)
        status = "✓" if intent == "gap_analysis" else "✗ FAIL"
        if intent == "gap_analysis":
            gap_passed += 1
        else:
            gap_failed += 1
        print(f"{status} {query}")
        print(f"   → Detected: {intent} (expected: gap_analysis)")
    
    print(f"\nGap Analysis: {gap_passed}/{len(gap_queries)} passed")
    
    print("\n" + "=" * 80)
    total_passed = passed + gap_passed
    total_tests = len(demand_queries) + len(gap_queries)
    print(f"OVERALL: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total_tests - total_passed} tests failed")
    print("=" * 80)
    
    return total_passed == total_tests

if __name__ == "__main__":
    test_demand_vs_gap_distinction()
