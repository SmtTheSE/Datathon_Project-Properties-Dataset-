"""
Quick Automated Test for Intent Detection and Parameter Extraction
Tests critical BHK/Rent detection functionality
"""

import sys
sys.path.append('.')

from chatbot_engine import RentalPropertyChatbot

def test_intent_detection():
    """Test that BHK/rent queries are correctly detected as gap_analysis"""
    chatbot = RentalPropertyChatbot()
    
    print("=" * 80)
    print("TESTING INTENT DETECTION")
    print("=" * 80)
    
    # Critical tests: These MUST be gap_analysis, NOT demand_forecast
    critical_tests = [
        ("What is the demand for Mumbai with 2 BHK?", "gap_analysis"),
        ("Show me properties with rent 35000 in Delhi", "gap_analysis"),
        ("2 BHK and rent 35k in Bangalore", "gap_analysis"),
        ("What is the demand for Mumbai with 2 BHK and rent 35000?", "gap_analysis"),
        ("3 BHK properties in Delhi", "gap_analysis"),
        ("Average rent 50k in Mumbai", "gap_analysis"),
    ]
    
    # These should remain demand_forecast
    demand_tests = [
        ("What is the demand in Mumbai?", "demand_forecast"),
        ("Show me demand for August 2024 in Delhi", "demand_forecast"),
        ("Predict rental demand in Bangalore", "demand_forecast"),
    ]
    
    all_tests = critical_tests + demand_tests
    passed = 0
    failed = 0
    
    for query, expected_intent in all_tests:
        detected_intent, confidence = chatbot.detect_intent(query)
        status = "✓ PASS" if detected_intent == expected_intent else "✗ FAIL"
        
        if detected_intent == expected_intent:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}")
        print(f"Query: {query}")
        print(f"Expected: {expected_intent}")
        print(f"Detected: {detected_intent} (confidence: {confidence:.2f})")
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(all_tests)} tests")
    print("=" * 80)
    
    return failed == 0

def test_parameter_extraction():
    """Test BHK and rent parameter extraction"""
    chatbot = RentalPropertyChatbot()
    
    print("\n" + "=" * 80)
    print("TESTING PARAMETER EXTRACTION")
    print("=" * 80)
    
    test_cases = [
        # (query, expected_bhk, expected_rent)
        ("2 BHK in Mumbai", "2", None),
        ("3 BHK properties", "3", None),
        ("rent 35000 in Delhi", None, 35000),
        ("average rent 50k", None, 50000),
        ("2 BHK with rent 35000", "2", 35000),
        ("3 BHK and 50k rent", "3", 50000),
        ("Show me Area 191 in Mumbai with 2 BHK and rent 35000", "2", 35000),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_bhk, expected_rent in test_cases:
        extracted_bhk = chatbot.extract_bhk(query)
        extracted_rent = chatbot.extract_rent(query)
        
        bhk_match = extracted_bhk == expected_bhk
        rent_match = extracted_rent == expected_rent
        
        status = "✓ PASS" if (bhk_match and rent_match) else "✗ FAIL"
        
        if bhk_match and rent_match:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}")
        print(f"Query: {query}")
        print(f"Expected BHK: {expected_bhk}, Extracted: {extracted_bhk} {'✓' if bhk_match else '✗'}")
        print(f"Expected Rent: {expected_rent}, Extracted: {extracted_rent} {'✓' if rent_match else '✗'}")
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    return failed == 0

def test_locality_extraction():
    """Test locality extraction (Area XXX format)"""
    chatbot = RentalPropertyChatbot()
    
    print("\n" + "=" * 80)
    print("TESTING LOCALITY EXTRACTION")
    print("=" * 80)
    
    test_cases = [
        ("Show me Area 191 in Mumbai", "Area 191"),
        ("What about Area 523 in Delhi?", "Area 523"),
        ("Analyze Area 870 in Bangalore", "Area 870"),
        ("Gap analysis for Area 191", "Area 191"),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_locality in test_cases:
        extracted_locality = chatbot.extract_locality(query)
        
        status = "✓ PASS" if extracted_locality == expected_locality else "✗ FAIL"
        
        if extracted_locality == expected_locality:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}")
        print(f"Query: {query}")
        print(f"Expected: {expected_locality}")
        print(f"Extracted: {extracted_locality}")
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    return failed == 0

if __name__ == "__main__":
    print("\n🧪 CHATBOT AUTOMATED TESTS\n")
    
    intent_pass = test_intent_detection()
    param_pass = test_parameter_extraction()
    locality_pass = test_locality_extraction()
    
    print("\n" + "=" * 80)
    print("OVERALL RESULTS")
    print("=" * 80)
    print(f"Intent Detection: {'✓ PASS' if intent_pass else '✗ FAIL'}")
    print(f"Parameter Extraction: {'✓ PASS' if param_pass else '✗ FAIL'}")
    print(f"Locality Extraction: {'✓ PASS' if locality_pass else '✗ FAIL'}")
    
    if intent_pass and param_pass and locality_pass:
        print("\n🎉 ALL TESTS PASSED! Chatbot is ready for testing.")
    else:
        print("\n⚠️  SOME TESTS FAILED. Please review the implementation.")
    print("=" * 80)
