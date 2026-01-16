"""
Comprehensive Test Queries for Chatbot - Aligned with Product Workflows
Tests all three products: Demand Forecasting, Gap Analysis, and Historical Data
"""

# ============================================================================
# PRODUCT 1: DEMAND FORECASTING QUERIES
# API: POST /predict (Port 5001)
# Parameters: city, date, economic_factors
# ============================================================================

DEMAND_FORECAST_QUERIES = [
    # Basic demand queries
    "What is the demand in Mumbai?",
    "Show me demand forecast for Delhi",
    "Predict rental demand in Bangalore",
    "How many rentals in Chennai?",
    
    # Date-specific queries
    "What's the demand in Mumbai for August 2024?",
    "Demand forecast for Delhi in January 2025",
    "Show me Mumbai demand for July 2024",
    "Predict demand in Bangalore for next month",
    
    # Natural language variations
    "I want to know rental demand in Hyderabad",
    "Tell me about demand in Kolkata",
    "How's Mumbai doing?",
    "What about Bangalore?",
    "How is the rental market in Pune?",
    
    # Follow-up queries (context-aware)
    "And what about Delhi?",  # After asking about Mumbai
    "How about Bangalore?",  # After asking about another city
]

# ============================================================================
# PRODUCT 2: GAP ANALYSIS QUERIES
# API: POST /predict (Port 5002)
# Parameters: city, area_locality, bhk, avg_rent, economic_indicators
# ============================================================================

GAP_ANALYSIS_QUERIES = [
    # General investment queries (no specific locality)
    "Where should I invest in Mumbai?",
    "Show me investment opportunities in Delhi",
    "Best areas to invest in Bangalore",
    "Which localities in Chennai have high demand?",
    "Investment opportunities in Hyderabad",
    
    # BHK-specific queries (NEW - should trigger gap analysis)
    "What is the demand for Mumbai with 2 BHK?",
    "Show me 3 BHK properties in Delhi",
    "I want 2 BHK in Bangalore",
    "Looking for 1 BHK apartments in Chennai",
    "2 BHK investment in Pune",
    
    # Rent-specific queries (NEW - should trigger gap analysis)
    "What is the demand for Mumbai with rent 35000?",
    "Show me properties with average rent 50k in Delhi",
    "I want to invest with rent around 40000 in Bangalore",
    "Properties with 30k rent in Chennai",
    "Average rent 45000 in Hyderabad",
    
    # BHK + Rent combined (NEW - should trigger gap analysis)
    "What is the demand for Mumbai with 2 BHK and rent 35000?",
    "Show me 3 BHK properties with 50k rent in Delhi",
    "I want 2 BHK apartments around 40000 rent in Bangalore",
    "Looking for 1 BHK with average rent 25000 in Chennai",
    "2 BHK investment with rent 35k in Pune",
    
    # Specific locality queries (using Area XXX format)
    "Show me Area 191 in Mumbai",
    "What about Area 523 in Delhi?",
    "Analyze Area 870 in Bangalore",
    "Gap analysis for Area 191 in Mumbai",
    
    # Locality + BHK + Rent (complete query)
    "Show me Area 191 in Mumbai with 2 BHK and rent 35000",
    "Area 523 in Delhi with 3 BHK and 50k rent",
    "I want to invest in Area 870 Bangalore, 2 BHK, rent 40000",
    
    # Undersupplied areas (high demand - good for investors)
    "Which areas are undersupplied in Mumbai?",
    "Show me undersupplied areas in Delhi",
    "High demand areas in Bangalore",
    "Where is demand high in Chennai?",
    
    # Oversupplied areas (low demand - good for renters)
    "Which areas are oversupplied in Mumbai?",
    "Show me oversupplied areas in Delhi",
    "Renter's market in Bangalore",
    "Where is supply high in Chennai?",
]

# ============================================================================
# PRODUCT 3: HISTORICAL DATA QUERIES
# API: GET /historical/{city}?months=12 (Port 5001)
# Parameters: city, months
# ============================================================================

HISTORICAL_DATA_QUERIES = [
    # Basic historical queries
    "Show historical demand in Mumbai",
    "Past trends in Delhi",
    "Historical data for Bangalore",
    "Show me Chennai trends",
    
    # Specific time periods
    "Show me last 6 months data for Mumbai",
    "Historical trends for Delhi over 12 months",
    "Past year data for Bangalore",
]

# ============================================================================
# CITY RANKING QUERIES
# ============================================================================

CITY_RANKING_QUERIES = [
    # Top cities
    "Show me top 5 cities",
    "Which are the best cities for investment?",
    "Top cities with highest demand",
    "Best cities overall",
    
    # Bottom cities
    "Show me worst 5 cities",
    "Which cities have lowest demand?",
    "Cities to avoid for investment",
    
    # Single city rankings
    "Which is the best city?",
    "What is the top city for investment?",
    "Which city has the lowest demand?",
    "Show me the worst city",
]

# ============================================================================
# CONVERSATIONAL QUERIES
# ============================================================================

CONVERSATIONAL_QUERIES = [
    # Greetings
    "Hello",
    "Hi there",
    "Good morning",
    "Hey",
    
    # Help
    "Help",
    "What can you do?",
    "How does this work?",
    
    # Thank you
    "Thanks",
    "Thank you",
    "That's helpful",
    
    # Goodbye
    "Bye",
    "Goodbye",
    "See you later",
]

# ============================================================================
# EDGE CASES & COMPLEX QUERIES
# ============================================================================

EDGE_CASE_QUERIES = [
    # Multiple parameters
    "What is the demand forecast for Mumbai in January 2024 with 2 BHK and average rent 35000?",
    "Show me gap analysis for Delhi with 3 BHK, rent 50k in Area 523",
    "I want to invest in Bangalore, 2 BHK, rent around 40000, show me best areas",
    
    # Context switching
    "What's the demand in Mumbai?",  # Demand forecast
    "And the gap analysis?",  # Should show gap for Mumbai
    "What about Delhi?",  # Should show gap for Delhi
    
    # Ambiguous queries (should ask for clarification)
    "Show me data",  # Missing city
    "What about investment?",  # Missing city
    "2 BHK properties",  # Missing city
]

# ============================================================================
# EXPECTED INTENT MAPPING
# ============================================================================

EXPECTED_INTENTS = {
    # Demand Forecast
    "What is the demand in Mumbai?": "demand_forecast",
    "Show me demand for August 2024 in Delhi": "demand_forecast",
    
    # Gap Analysis (general)
    "Where should I invest in Mumbai?": "gap_analysis",
    "Best areas in Delhi": "gap_analysis",
    
    # Gap Analysis (BHK/rent - should NOT be demand_forecast)
    "What is the demand for Mumbai with 2 BHK?": "gap_analysis",
    "Show me properties with rent 35000 in Delhi": "gap_analysis",
    "2 BHK and rent 35k in Bangalore": "gap_analysis",
    
    # Historical
    "Show historical data for Mumbai": "historical",
    "Past trends in Delhi": "historical",
    
    # City Rankings
    "Top 5 cities": "top_cities",
    "Best city": "top_city",
    "Worst cities": "bottom_cities",
}

# ============================================================================
# TEST EXECUTION INSTRUCTIONS
# ============================================================================

TEST_INSTRUCTIONS = """
HOW TO TEST:

1. Start the chatbot API server:
   cd Product_3_Conversational_AI_Chatbot
   python api_server.py

2. Open chatbot demo in browser:
   Open chatbot_demo.html

3. Test each category:
   - Copy queries from each section above
   - Paste into chatbot interface
   - Verify the response matches expected behavior

4. Verify for each query:
   ✓ Correct intent detected (demand_forecast, gap_analysis, historical)
   ✓ Correct parameters extracted (city, BHK, rent, locality, date)
   ✓ Appropriate API called (Port 5001 or 5002)
   ✓ Response is natural and informative
   ✓ Context is maintained across follow-up queries

5. Critical Tests (BHK/Rent Detection):
   These queries MUST be detected as gap_analysis, NOT demand_forecast:
   - "What is the demand for Mumbai with 2 BHK?"
   - "Show me properties with rent 35000 in Delhi"
   - "2 BHK and rent 35k in Bangalore"
   
   Verify in response:
   - Should show gap analysis data (locality list or specific gap ratio)
   - Should NOT show demand forecast (predicted_demand number)

6. Parameter Extraction Tests:
   Query: "Show me Area 191 in Mumbai with 2 BHK and rent 35000"
   Expected extraction:
   - city: "Mumbai"
   - locality: "Area 191"
   - bhk: "2"
   - rent: 35000
   
   Query: "3 BHK with 50k rent in Delhi"
   Expected extraction:
   - city: "Delhi"
   - bhk: "3"
   - rent: 50000

7. Context Awareness Tests:
   Sequence:
   User: "What's the demand in Mumbai?"
   Bot: [Shows demand forecast for Mumbai]
   User: "And the gap analysis?"
   Bot: [Should show gap analysis for Mumbai - using context]
"""

if __name__ == "__main__":
    print("=" * 80)
    print("CHATBOT TEST QUERIES - ALIGNED WITH PRODUCT WORKFLOWS")
    print("=" * 80)
    
    print("\n📊 PRODUCT 1: DEMAND FORECASTING")
    print("-" * 80)
    for i, query in enumerate(DEMAND_FORECAST_QUERIES, 1):
        print(f"{i}. {query}")
    
    print("\n🎯 PRODUCT 2: GAP ANALYSIS")
    print("-" * 80)
    for i, query in enumerate(GAP_ANALYSIS_QUERIES, 1):
        print(f"{i}. {query}")
    
    print("\n📈 HISTORICAL DATA")
    print("-" * 80)
    for i, query in enumerate(HISTORICAL_DATA_QUERIES, 1):
        print(f"{i}. {query}")
    
    print("\n🏆 CITY RANKINGS")
    print("-" * 80)
    for i, query in enumerate(CITY_RANKING_QUERIES, 1):
        print(f"{i}. {query}")
    
    print("\n💬 CONVERSATIONAL")
    print("-" * 80)
    for i, query in enumerate(CONVERSATIONAL_QUERIES, 1):
        print(f"{i}. {query}")
    
    print("\n⚠️  EDGE CASES")
    print("-" * 80)
    for i, query in enumerate(EDGE_CASE_QUERIES, 1):
        print(f"{i}. {query}")
    
    print("\n" + "=" * 80)
    print("TOTAL TEST QUERIES:", 
          len(DEMAND_FORECAST_QUERIES) + 
          len(GAP_ANALYSIS_QUERIES) + 
          len(HISTORICAL_DATA_QUERIES) +
          len(CITY_RANKING_QUERIES) +
          len(CONVERSATIONAL_QUERIES) +
          len(EDGE_CASE_QUERIES))
    print("=" * 80)
    
    print("\n" + TEST_INSTRUCTIONS)
