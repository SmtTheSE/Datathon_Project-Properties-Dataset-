"""
Test script for chatbot economic factors and date flexibility enhancement
"""

import sys
sys.path.append('.')

from chatbot_engine import RentalPropertyChatbot

def test_chatbot_enhancements():
    """Test all combinations of queries"""
    
    print("=" * 80)
    print("CHATBOT ENHANCEMENT TESTS")
    print("=" * 80)
    
    chatbot = RentalPropertyChatbot()
    
    test_queries = [
        # Simple queries (backward compatibility)
        ("Simple query", "What's the demand in Mumbai?"),
        
        # Date only
        ("Date only", "What's demand in Mumbai in February 2023?"),
        ("Date only 2", "Show Delhi demand for August 2024"),
        
        # Economic factors only
        ("Economics only - inflation", "Mumbai demand with 8% inflation"),
        ("Economics only - interest", "Delhi with 7.5% interest rate"),
        ("Economics only - employment", "Bangalore with 90% employment"),
        ("Economics only - multiple", "Chennai with 8% inflation and 9% interest"),
        
        # Both date and economic factors
        ("Date + Economics", "Mumbai demand in Feb 2023 with 8% inflation and 9% interest"),
        ("Date + Economics 2", "Delhi for August 2024 with 7.5% interest rate"),
        ("Date + Economics 3", "Bangalore in March 2025 assuming 85% employment and 6% inflation"),
    ]
    
    for test_name, query in test_queries:
        print(f"\n{'='*80}")
        print(f"TEST: {test_name}")
        print(f"QUERY: {query}")
        print(f"{'='*80}")
        
        # Test extraction methods
        city = chatbot.extract_city(query)
        date = chatbot.extract_date(query)
        economic_factors = chatbot.extract_economic_factors(query)
        
        print(f"\nEXTRACTED:")
        print(f"  City: {city}")
        print(f"  Date: {date}")
        print(f"  Economic Factors: {economic_factors}")
        
        print(f"\n{'='*80}\n")

if __name__ == "__main__":
    test_chatbot_enhancements()
