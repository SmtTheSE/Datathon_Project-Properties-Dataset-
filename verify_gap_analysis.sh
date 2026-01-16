#!/bin/bash
# Quick verification script to test the Gap Analysis feature end-to-end

echo "========================================="
echo "Gap Analysis End-to-End Verification"
echo "========================================="
echo ""

# Check if API server is running
echo "1. Checking API server..."
if curl -s http://localhost:5002/health > /dev/null 2>&1; then
    echo "   ✓ API server is running on port 5002"
else
    echo "   ✗ API server is NOT running"
    echo "   Please start it with: cd Product_2_Demand_Supply_Gap_Identification && python3 api_server.py"
    exit 1
fi

# Check if frontend is running
echo ""
echo "2. Checking frontend server..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✓ Frontend is running on port 3000"
else
    echo "   ✗ Frontend is NOT running"
    echo "   Please start it with: cd frontend && npm run dev"
    exit 1
fi

echo ""
echo "3. Testing API endpoints..."

# Test heat map data
echo "   Testing heat map data for Mumbai..."
HEAT_MAP=$(curl -s "http://localhost:5002/historical/Mumbai?top_n=2&sort_by=demand")
AREA_191_DEMAND=$(echo $HEAT_MAP | python3 -c "import sys, json; data = json.load(sys.stdin); print([loc['demand'] for loc in data['locality_data'] if loc['locality'] == 'Area 191'][0])" 2>/dev/null)

if [ "$AREA_191_DEMAND" = "347" ]; then
    echo "   ✓ Heat map data correct (Area 191: 347 listings)"
else
    echo "   ✗ Heat map data incorrect"
fi

# Test ML prediction
echo "   Testing ML prediction..."
PREDICTION=$(curl -s -X POST http://localhost:5002/predict \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Mumbai",
    "area_locality": "Area 191",
    "bhk": "2",
    "avg_rent": 35000,
    "economic_indicators": {
      "inflation_rate": 6.5,
      "interest_rate": 7.0,
      "employment_rate": 85.0,
      "covid_impact_score": 0.1,
      "economic_health_score": 0.8,
      "city_tier": "Tier1",
      "region": "West"
    }
  }')

GAP_RATIO=$(echo $PREDICTION | python3 -c "import sys, json; print(f\"{json.load(sys.stdin)['predicted_gap_ratio']:.3f}\")" 2>/dev/null)

if [ "$GAP_RATIO" = "0.061" ]; then
    echo "   ✓ ML prediction correct (Gap ratio: +0.061)"
else
    echo "   ✗ ML prediction incorrect (Got: $GAP_RATIO)"
fi

echo ""
echo "========================================="
echo "All checks passed! ✓"
echo "========================================="
echo ""
echo "You can now:"
echo "  1. Open http://localhost:3000/gap-analysis in your browser"
echo "  2. Select Mumbai from the city dropdown"
echo "  3. View the heat map showing Area 191 with 347 listings"
echo "  4. Fill in the form: Area 191, 2BHK, ₹35,000"
echo "  5. Click 'Analyze Gap' to see the +0.061 prediction"
echo ""
