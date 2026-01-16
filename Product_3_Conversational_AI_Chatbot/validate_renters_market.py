"""
Validate renter's market responses show TRUE facts from API data
"""

import requests
import json
from chatbot_engine import RentalPropertyChatbot

def validate_renters_market_facts():
    """Validate that renter's market query returns accurate data"""
    
    print("="*80)
    print("VALIDATING RENTER'S MARKET DATA ACCURACY")
    print("="*80)
    
    # Test cities
    cities = ["Mumbai", "Delhi", "Bangalore"]
    
    for city in cities:
        print(f"\n{'='*80}")
        print(f"TESTING: {city}")
        print(f"{'='*80}")
        
        # Get raw API data
        print(f"\n1. RAW API DATA:")
        print("-" * 80)
        try:
            response = requests.get(f'http://localhost:5002/historical/{city}?top_n=10', timeout=5)
            api_data = response.json()
            
            localities = api_data.get('locality_data', [])
            
            # Sort by gap (descending) to get least undersupplied
            sorted_by_gap = sorted(localities, key=lambda x: x.get('gap', -999), reverse=True)[:5]
            
            print(f"Top 5 areas by GAP (closest to 0 = least competitive):")
            for i, loc in enumerate(sorted_by_gap, 1):
                locality = loc.get('locality')
                demand = loc.get('demand')
                gap = loc.get('gap')
                print(f"{i}. {locality}: Demand={demand}, Gap={gap:.3f}")
            
            # Check if any have positive gap (truly oversupplied)
            has_oversupply = any(loc.get('gap', -1) > 0 for loc in sorted_by_gap)
            print(f"\nHas truly oversupplied areas (gap > 0)? {has_oversupply}")
            
            if not has_oversupply:
                print(f"✅ CORRECT: All areas have negative gap (demand > supply)")
            
        except Exception as e:
            print(f"❌ Error fetching API data: {e}")
            continue
        
        # Get chatbot response
        print(f"\n2. CHATBOT RESPONSE:")
        print("-" * 80)
        
        bot = RentalPropertyChatbot()
        chatbot_response = bot.chat(f"Show me renter's market in {city}")
        print(chatbot_response)
        
        # Validate facts
        print(f"\n3. FACT VALIDATION:")
        print("-" * 80)
        
        facts_correct = []
        
        # Check 1: Does it correctly identify all areas as high demand?
        if not has_oversupply:
            if "All areas" in chatbot_response and "high demand" in chatbot_response:
                facts_correct.append("✅ Correctly identifies all areas have high demand")
            else:
                facts_correct.append("❌ Should state all areas have high demand")
        
        # Check 2: Are the gap values accurate?
        for loc in sorted_by_gap[:3]:
            gap_str = f"{loc.get('gap'):.2f}"
            if gap_str in chatbot_response:
                facts_correct.append(f"✅ Gap value {gap_str} is accurate")
            else:
                facts_correct.append(f"⚠️ Gap value {gap_str} not found in response")
        
        # Check 3: Does it mention the city name correctly?
        if city in chatbot_response:
            facts_correct.append(f"✅ City name '{city}' appears correctly")
        else:
            facts_correct.append(f"❌ City name '{city}' missing or incorrect")
        
        # Check 4: Does it provide honest assessment?
        if not has_oversupply:
            if "undersupplied" in chatbot_response or "hot rental market" in chatbot_response:
                facts_correct.append("✅ Provides honest market assessment")
            else:
                facts_correct.append("❌ Should mention market is undersupplied/hot")
        
        for fact in facts_correct:
            print(fact)
        
        # Overall verdict
        passed = all("✅" in fact for fact in facts_correct)
        print(f"\n{'✅ ALL FACTS CORRECT' if passed else '⚠️ SOME ISSUES FOUND'}")
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    validate_renters_market_facts()
