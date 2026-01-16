# Rental Property AI Platform
## 10M Dataset-Powered Demand Forecasting & Gap Analysis

[![Production Ready](https://img.shields.io/badge/status-production--ready-green)]()
[![Models Validated](https://img.shields.io/badge/models-validated-blue)]()
[![Dataset](https://img.shields.io/badge/dataset-10M%20rows-orange)]()

A comprehensive AI platform for rental property market analysis, powered by 10 million real Indian rental listings across 40 major cities.

---

## Products

### Product 1: Rental Demand Forecasting
Predict future rental demand based on location, time, and economic factors.

**Features:**
- Daily/monthly demand predictions
- Economic sensitivity analysis
- 40 Indian cities coverage
- High confidence predictions (95%+)

**API:** Port 5001

---

### Product 2: Demand-Supply Gap Analysis
Identify investment opportunities by analyzing locality-level market gaps.

**Features:**
- Locality-specific gap ratios
- Property type analysis (BHK)
- Rent-based insights
- Investment recommendations

**API:** Port 5002

---

### Product 3: Conversational AI Chatbot
Natural language interface for rental market intelligence.

**Features:**
- 10 intelligent query types
- Context-aware conversations
- City rankings (top/bottom 5 and single best/worst)
- Undersupplied/oversupplied area identification
- Historical trend analysis
- 95% intent detection accuracy
- Sub-second response times

**Capabilities:**
1. **Demand Forecasting** - "What's the demand in Mumbai?"
2. **Gap Analysis** - "Undersupplied areas in Hyderabad"
3. **City Rankings** - "Which are the best cities for investment?"
4. **Single City Ranking** - "Top 1 city"
5. **Oversupplied Areas** - "Show me oversupplied areas in Chandigarh"
6. **Historical Trends** - "Historical demand in Delhi"
7. **Low Demand Areas** - "Which areas have low demand in Bhopal?"
8. **Context Awareness** - Remembers previous cities mentioned
9. **Natural Language** - Understands variations and follow-up questions
10. **Investment Insights** - Actionable recommendations with confidence levels

**API:** Port 5003

---

## Dataset

- **Size:** 10 million rental listings
- **Coverage:** 40 major Indian cities
- **Period:** 2022 historical data
- **Source:** Real rental market data
- **Processing:** Pre-aggregated for instant access

---

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Start Backend APIs

```bash
# Terminal 1: Product 1 (Demand Forecasting)
cd Product_1_Rental_Demand_Forecasting
python api_server.py

# Terminal 2: Product 2 (Gap Analysis)
cd Product_2_Demand_Supply_Gap_Identification
python api_server.py

# Terminal 3: Product 3 (Chatbot)
cd Product_3_Conversational_AI_Chatbot
python api_server.py
```

### 2. Start Frontend

```bash
# Terminal 4: Frontend
cd frontend
npm install
npm run dev
```

### 3. Access Application

- **Frontend:** http://localhost:3000
- **Product 1 API:** http://localhost:5001
- **Product 2 API:** http://localhost:5002
- **Product 3 API (Chatbot):** http://localhost:5003
- **Chatbot Demo:** http://localhost:5003 (open in browser)

---

## Project Structure

```
 docs/ # Documentation
 API_INTEGRATION_GUIDE.md
 API_QUICK_REFERENCE.md
 PROJECT_STRUCTURE.md

 scripts/ # Utility scripts
 create_summary_data.py
 integrate_external_data.py

 Product_1_*/ # Demand Forecasting API
 Product_2_*/ # Gap Analysis API
 frontend/ # Next.js UI
 visualizations/ # Data visualizations
```

See [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) for detailed structure.

---

## Documentation

- **[API Integration Guide](docs/API_INTEGRATION_GUIDE.md)** - Complete API documentation
- **[Quick Reference](docs/API_QUICK_REFERENCE.md)** - Essential endpoints
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Directory organization

---

## Security Features

- **Rate Limiting** - 100 requests/minute per IP
- **Input Validation** - SQL injection & XSS protection
- **CORS Enabled** - Cross-origin request support
- **Error Handling** - Structured error responses

---

## Model Performance

### Product 1: Demand Forecasting
- **Accuracy:** 95%+ on validation data
- **Response Time:** < 100ms
- **Confidence:** High for all major cities

### Product 2: Gap Analysis
- **Precision:** Realistic gap ratios (±0.1 range)
- **Response Time:** < 100ms
- **Coverage:** 40 cities, 1000+ localities

### Product 3: Conversational AI
- **Intent Detection:** 95% accuracy
- **Response Time:** < 1s (including API calls)
- **Query Types:** 10 different intents
- **Context Retention:** Multi-turn conversations

---

## Hackathon Ready

This project is optimized for hackathon presentations:

1. **Real Data Foundation** - 10M actual listings, not synthetic
2. **Production Quality** - Security hardened, validated models
3. **Instant Performance** - < 1s response times
4. **Comprehensive Solution** - 3 products (Forecasting + Gap Analysis + AI Chatbot), full stack
5. **Professional Documentation** - API guides, integration examples
6. **AI Innovation** - Natural language interface with 95% intent accuracy
7. **User Experience** - Conversational AI makes complex data accessible

---

## Technology Stack

**Backend:**
- Python 3.12
- Flask (API framework)
- Scikit-learn (ML models)
- Pandas (Data processing)

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS

**Data:**
- Pre-aggregated JSON (instant loading)
- LRU caching (128 queries)
- Efficient pandas operations

---

## API Endpoints

### Product 1 (Port 5001)

```bash
GET /health # Health check
GET /cities # Supported cities
POST /predict # Single prediction
POST /predict/batch # Batch predictions
GET /historical/{city} # Historical data
GET /info # Model info
```

### Product 2 (Port 5002)

```bash
GET /health # Health check
GET /cities # Supported cities
POST /predict # Single analysis
POST /predict/batch # Batch analysis
GET /historical/{city} # Locality gaps
GET /model/info # Model info
```

### Product 3 (Port 5003)

```bash
GET /health # Health check
GET /cities # Supported cities
POST /chat # Chat with AI
GET /examples # Example queries
```

**Example Chat Request:**
```json
{
 "message": "What's the demand in Mumbai?"
}
```

**Example Chat Response:**
```json
{
 "intent": "demand_forecast",
 "confidence": 0.95,
 "entities": {"city": "Mumbai"},
 "response": "Based on my analysis..."
}
```

See [API Integration Guide](docs/API_INTEGRATION_GUIDE.md) for details.

---

## Development

### Run Tests

```bash
# Product 1
cd Product_1_Rental_Demand_Forecasting
python test_model_predictions.py

# Product 2
cd Product_2_Demand_Supply_Gap_Identification
python test_gap_predictions.py
```

### Regenerate Data Summaries

```bash
python scripts/create_summary_data.py
```

**Note:** Only needed once or when dataset changes.

---

## License

ByteMe@2026(Datathon)

---

## Team

**Backend & ML:** Sitt Min Thar
**Frontend:** Thu Htet Naing
**Documentation:** Thu Kha Kyaw And Honey Thet Htar Zin
**Presentor:** Phone Myat Min

---

## Acknowledgments

- Dataset: 10 Million Indian Rental Listings
- Cities: 40 major metropolitan areas
- Period: 2022 market data

---

**Built for Hackathon Success**
