"""
Test new low demand and low gap features
"""

from chatbot_engine import RentalPropertyChatbot

def test_new_features():
    """Test the new low demand and low gap query features"""
    
    chatbot = RentalPropertyChatbot()
    
    print("="*80)
    print("TESTING NEW FEATURES: LOW DEMAND & LOW GAP QUERIES")
    print("="*80)
    
    test_queries = [
        ("Low Demand Query 1", "Which areas have low demand in Mumbai?"),
        ("Low Demand Query 2", "Show me affordable areas in Delhi"),
        ("Low Demand Query 3", "Where is it cheap in Bangalore?"),
        ("Low Gap Query 1", "Which areas are oversupplied in Mumbai?"),
        ("Low Gap Query 2", "Show me renter's market in Delhi"),
        ("Low Gap Query 3", "Buyer's market in Bangalore"),
    ]
    
    for test_name, query in test_queries:
        print(f"\n{'='*80}")
        print(f"TEST: {test_name}")
        print(f"{'='*80}")
        print(f"Query: '{query}'")
        print("-" * 80)
        
        response = chatbot.chat(query)
        print(f"Response:\n{response}")
        
        # Check if response is specific (not default error)
        if "not quite sure" not in response.lower() and "couldn't identify" not in response.lower():
            print("\n✅ PASSED - Got specific response!")
        else:
            print("\n⚠️ NEEDS REVIEW - Got default/error response")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_new_features()
