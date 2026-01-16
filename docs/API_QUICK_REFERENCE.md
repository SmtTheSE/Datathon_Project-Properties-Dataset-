# API Quick Reference Card
## For Frontend Developers

### Product 1: Demand Forecasting (Port 5001)

**Get Historical Data (for charts):**
```bash
GET /historical/{city}?months=12
```

**Predict Future Demand:**
```bash
POST /predict
{
 "city": "Mumbai",
 "date": "2024-08-15",
 "economic_factors": {
 "inflation_rate": 6.5,
 "interest_rate": 7.0,
 "employment_rate": 85.0
 }
}
```

**Get Supported Cities:**
```bash
GET /cities
```

---

### Product 2: Gap Analysis (Port 5002)

**Get Locality Heat Map Data:**
```bash
GET /historical/{city}?top_n=10
```

**Analyze Investment Gap:**
```bash
POST /predict
{
 "city": "Mumbai",
 "area_locality": "Area 191",
 "bhk": "2",
 "avg_rent": 35000,
 "economic_indicators": {
 "inflation_rate": 6.0,
 "interest_rate": 7.0,
 "employment_rate": 85.0,
 "covid_impact_score": 0.1,
 "economic_health_score": 0.85
 }
}
```

---

### Key Points

 **Rate Limit:** 100 requests/minute
 **Response Time:** < 1 second
 **Security:** Input validation, XSS protection
 **CORS:** Enabled
 **Error Format:** `{"error": "message"}`

---

### TypeScript Example

```typescript
// Fetch historical data
const data = await fetch('http://localhost:5001/historical/Mumbai?months=12')
 .then(res => res.json());

// Predict demand
const prediction = await fetch('http://localhost:5001/predict', {
 method: 'POST',
 headers: { 'Content-Type': 'application/json' },
 body: JSON.stringify({
 city: 'Mumbai',
 date: '2024-08-15',
 economic_factors: {
 inflation_rate: 6.5,
 interest_rate: 7.0,
 employment_rate: 85.0
 }
 })
}).then(res => res.json());
```

---

**Full Documentation:** See `API_INTEGRATION_GUIDE.md`
