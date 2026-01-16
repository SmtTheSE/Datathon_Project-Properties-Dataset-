"""
Test script for Conversational AI Chatbot
Tests various query patterns and validates responses
"""

from chatbot_engine import RentalPropertyChatbot

def test_chatbot():
    """Test chatbot with various queries"""
    
    print("=" * 70)
    print("CONVERSATIONAL AI CHATBOT - TEST SUITE")
    print("=" * 70)
    print()
    
    # Initialize chatbot
    chatbot = RentalPropertyChatbot()
    
    # Test queries
    test_queries = [
        # Demand forecasting
        "What's the demand in Mumbai for August 2024?",
        "Predict rental demand in Delhi",
        "How many rentals in Bangalore next month?",
        
        # Gap analysis
        "Show me investment opportunities in Mumbai",
        "Which areas in Delhi have high demand?",
        "Gap analysis for Bandra area in Mumbai",
        
        # Historical
        "Show historical demand in Chennai",
        "Past trends in Pune",
        
        # Help
        "help",
        
        # Edge cases
        "demand in XYZ city",  # Unknown city
        "hello",  # Greeting
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {query}")
        print(f"{'='*70}")
        
        # Get intent
        intent, confidence = chatbot.detect_intent(query)
        print(f"Intent: {intent} (confidence: {confidence:.2f})")
        
        # Extract entities
        city = chatbot.extract_city(query)
        if city:
            print(f"City: {city}")
        
        # Get response
        response = chatbot.chat(query)
        print(f"\nResponse:\n{response}")
        print()

if __name__ == "__main__":
    test_chatbot()
