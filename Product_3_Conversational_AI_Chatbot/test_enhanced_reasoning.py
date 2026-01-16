"""
Quick test for enhanced question-based reasoning
Tests edge cases that previously didn't work well
"""

from chatbot_engine import RentalPropertyChatbot

def test_enhanced_reasoning():
    """Test the enhanced NLP patterns"""
    
    chatbot = RentalPropertyChatbot()
    
    print("="*80)
    print("TESTING ENHANCED QUESTION-BASED REASONING")
    print("="*80)
    
    # Test scenarios that should now work better
    test_cases = [
        {
            "setup": "What's the demand in Mumbai?",
            "follow_up": "And what about Bangalore?",
            "expected": "Should understand this as demand query for Bangalore"
        },
        {
            "setup": "Tell me about demand in Delhi",
            "follow_up": "Show me the historical trends",
            "expected": "Should understand this as historical query for Delhi (using context)"
        },
        {
            "setup": "Where should I invest in Mumbai?",
            "follow_up": "And the gap?",
            "expected": "Should understand this as gap analysis for Mumbai (using context)"
        },
        {
            "setup": None,
            "follow_up": "how's bangalore doing?",
            "expected": "Should understand as demand query"
        },
        {
            "setup": None,
            "follow_up": "Show me Bombay opportunities",
            "expected": "Should recognize Bombay as Mumbai"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}")
        print(f"{'='*80}")
        
        # Reset chatbot for each test
        chatbot = RentalPropertyChatbot()
        
        if test["setup"]:
            print(f"\nSetup Query: '{test['setup']}'")
            response = chatbot.chat(test["setup"])
            print(f"Response: {response[:100]}...")
        
        print(f"\nTest Query: '{test['follow_up']}'")
        print(f"Expected: {test['expected']}")
        print("-" * 80)
        
        response = chatbot.chat(test["follow_up"])
        print(f"Response:\n{response}")
        
        # Check if response is not the default "I'm not sure" message
        if "not quite sure" not in response.lower() and "couldn't identify" not in response.lower():
            print("\n✅ PASSED - Got specific response!")
        else:
            print("\n⚠️ NEEDS REVIEW - Got default/error response")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_enhanced_reasoning()
