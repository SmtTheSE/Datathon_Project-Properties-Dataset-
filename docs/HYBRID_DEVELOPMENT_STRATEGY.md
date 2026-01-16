# Hybrid Development Strategy
## Frontend Local Data + Backend API Integration

**Team:** ByteMe@2026(Datathon)
**Date:** January 14, 2026

---

## Overview

This document explains our hybrid development approach where the frontend team works with local data (5M rows) while the backend provides production-ready APIs. Both approaches coexist during development and seamlessly integrate for production.

---

## Development Phases

### Phase 1: Parallel Development (Current)

```
Frontend Team Backend Team

 → Load 5M rows locally → Build APIs
 → Client-side filtering → Train models
 → Build UI components → Optimize performance
 → Test with local data → Deploy APIs
```

**Frontend Approach:**
- Load half dataset (5M rows) into browser
- Use JavaScript for filtering/aggregation
- Build and test UI independently
- No API dependency during development

**Backend Approach:**
- Serve predictions via REST APIs
- Use pre-aggregated JSON (instant loading)
- Production-ready from day one
- Independent of frontend implementation

### Phase 2: Integration (Before Hackathon)

```
Frontend Backend API

 → Keep local data
 → Add API calls
 → Use API for predictions
 → Use API for historical
 → Fallback to local data
```

**Integration Steps:**
1. Frontend adds API client functions
2. Replace local predictions with API calls
3. Keep local data as fallback
4. Test both modes

### Phase 3: Production (Post-Hackathon)

```
Frontend Backend API

 → Remove local data
 → Use API exclusively
 → Cache API responses
 → Handle errors gracefully
```

---

## Why This Approach Works

### Benefits for Frontend Team

**1. Independent Development**
- No waiting for backend APIs
- Test UI with real data structure
- Iterate quickly on design
- Build confidence with data

**2. Realistic Testing**
- 5M rows = representative sample
- Same data structure as production
- Can validate UI performance
- Catch edge cases early

**3. Gradual Migration**
- Add API calls incrementally
- Keep local data as fallback
- Low-risk integration
- Easy rollback if needed

### Benefits for Backend Team

**1. API-First Design**
- Clean separation of concerns
- Production-ready from start
- Scalable architecture
- Easy to version/update

**2. Performance Optimization**
- Pre-aggregated data
- Caching strategies
- Load testing possible
- No frontend bottlenecks

**3. Flexibility**
- Frontend can use any framework
- Multiple frontends possible
- Mobile app ready
- Third-party integrations easy

---

## Technical Implementation

### Frontend: Local Data Loading

**File:** `frontend/src/lib/localData.ts`

```typescript
// Load 5M rows from local file
export async function loadLocalData() {
 const response = await fetch('/data/sample_5m.json');
 const data = await response.json();
 return data;
}

// Filter data locally
export function filterByCity(data: any[], city: string) {
 return data.filter(item => item.city === city);
}

// Aggregate locally
export function aggregateMonthly(data: any[]) {
 const grouped = data.reduce((acc, item) => {
 const key = `${item.year}-${item.month}`;
 acc[key] = (acc[key] || 0) + 1;
 return acc;
 }, {});
 return grouped;
}
```

**Usage in Component:**

```typescript
// Option 1: Use local data (development)
const [useLocalData, setUseLocalData] = useState(true);

useEffect(() => {
 if (useLocalData) {
 // Load and process locally
 const data = await loadLocalData();
 const filtered = filterByCity(data, selectedCity);
 const aggregated = aggregateMonthly(filtered);
 setHistoricalData(aggregated);
 } else {
 // Use API (production)
 const response = await fetch(`/api/historical/${selectedCity}`);
 const data = await response.json();
 setHistoricalData(data.historical_data);
 }
}, [selectedCity, useLocalData]);
```

### Backend: API Serving (No Changes Needed)

**Your current API already works perfectly!**

```python
# api_server.py - No changes needed
@app.route('/historical/<city>', methods=['GET'])
def get_historical_data(city):
 months = request.args.get('months', default=12, type=int)
 historical_data = forecaster.get_historical_demand(city, months)
 return jsonify({
 "city": city,
 "historical_data": historical_data
 }), 200
```

**Why no changes needed:**
- API is stateless (doesn't care about frontend implementation)
- Returns JSON (works with any client)
- Already optimized (pre-aggregated data)
- Production-ready (security, caching, validation)

---

## Integration Checklist

### For Frontend Developer (Thu Htet Naing)

**Phase 1: Setup Local Data (Done)**
- [x] Extract 5M rows from dataset
- [x] Convert to JSON format
- [x] Load in frontend
- [x] Build UI with local data

**Phase 2: Add API Integration (Before Hackathon)**
- [ ] Create API client functions
- [ ] Add environment variable for API URL
- [ ] Implement API calls for predictions
- [ ] Implement API calls for historical data
- [ ] Add loading states
- [ ] Add error handling
- [ ] Test with backend APIs

**Phase 3: Hybrid Mode (Hackathon)**
- [ ] Add toggle for local vs API mode
- [ ] Use API for predictions (always)
- [ ] Use local data for charts (fallback)
- [ ] Handle API failures gracefully

**Phase 4: Production (Post-Hackathon)**
- [ ] Remove local data files
- [ ] Use API exclusively
- [ ] Add response caching
- [ ] Optimize bundle size

### For Backend Developer (Sitt Min Thar)

**Phase 1: API Development (Done)**
- [x] Build prediction APIs
- [x] Build historical data APIs
- [x] Optimize performance
- [x] Add security features
- [x] Deploy and test

**Phase 2: Support Frontend Integration (Before Hackathon)**
- [ ] Ensure CORS is configured
- [ ] Test API with frontend
- [ ] Provide API documentation
- [ ] Help debug integration issues

**Phase 3: Production Deployment (Post-Hackathon)**
- [ ] Deploy to cloud
- [ ] Set up monitoring
- [ ] Configure CDN
- [ ] Scale infrastructure

---

## Example: Hybrid Component

**File:** `frontend/src/app/demand-forecasting/page.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';

// Configuration
const USE_API = process.env.NEXT_PUBLIC_USE_API === 'true';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

export default function DemandForecasting() {
 const [historicalData, setHistoricalData] = useState([]);
 const [prediction, setPrediction] = useState(null);

 // Fetch historical data (hybrid approach)
 const fetchHistoricalData = async (city: string) => {
 if (USE_API) {
 // Production: Use API
 try {
 const response = await fetch(`${API_URL}/historical/${city}`);
 const data = await response.json();
 setHistoricalData(data.historical_data);
 } catch (error) {
 console.error('API failed, falling back to local data');
 loadLocalHistoricalData(city);
 }
 } else {
 // Development: Use local data
 loadLocalHistoricalData(city);
 }
 };

 // Local data fallback
 const loadLocalHistoricalData = async (city: string) => {
 const localData = await import('@/data/historical.json');
 const cityData = localData.default[city] || [];
 setHistoricalData(cityData);
 };

 // Predictions always use API (model is backend-only)
 const makePrediction = async (params: any) => {
 try {
 const response = await fetch(`${API_URL}/predict`, {
 method: 'POST',
 headers: { 'Content-Type': 'application/json' },
 body: JSON.stringify(params)
 });
 const data = await response.json();
 setPrediction(data.predicted_demand);
 } catch (error) {
 console.error('Prediction failed:', error);
 // No fallback for predictions - model is backend-only
 alert('Unable to make prediction. Please check API connection.');
 }
 };

 return (
 <div>
 {/* UI components */}
 <button onClick={() => makePrediction({...})}>
 Predict
 </button>
 </div>
 );
}
```

**Environment Variables:**

```bash
# .env.local (development)
NEXT_PUBLIC_USE_API=false
NEXT_PUBLIC_API_URL=http://localhost:5001

# .env.production
NEXT_PUBLIC_USE_API=true
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## Data File Structure

### Frontend Local Data (5M rows)

```
frontend/public/data/
 sample_5m.json # 5M rows sample
 cities.json # City list
 historical/
 mumbai.json # Pre-aggregated for Mumbai
 delhi.json # Pre-aggregated for Delhi
 ...
```

**File Size Estimates:**
- 5M rows JSON: ~500MB (large but manageable)
- Pre-aggregated by city: ~5MB total (better)
- Compressed (gzip): ~50MB (best for production)

**Recommendation:** Use pre-aggregated city files, not full 5M rows

### Backend Data (10M rows)

```
Product_1_Rental_Demand_Forecasting/
 monthly_summary.json # 3.3KB (all cities)
 ...

Product_2_Demand_Supply_Gap_Identification/
 locality_summary.json # 1.8MB (all cities)
 ...
```

**Already optimized!** No changes needed.

---

## Performance Comparison

| Approach | Load Time | Memory | Scalability | Production Ready |
|----------|-----------|--------|-------------|------------------|
| **Frontend Local (5M)** | 5-10s | 500MB | Poor | No |
| **Frontend Aggregated** | 1-2s | 50MB | Medium | Maybe |
| **Backend API (Current)** | <1s | 10MB | Excellent | Yes |

**Recommendation for Hackathon:**
- Demo: Use API (shows production-ready)
- Backup: Have local data if WiFi fails
- Best of both worlds!

---

## Migration Path

### Week 1: Parallel Development
```
Frontend: Build UI with local 5M rows
Backend: Build APIs with 10M rows
Status: Independent, no integration
```

### Week 2: Integration Testing
```
Frontend: Add API calls, keep local fallback
Backend: Test with frontend, fix CORS issues
Status: Hybrid mode working
```

### Week 3: Hackathon Demo
```
Frontend: Use API for predictions, local for charts
Backend: APIs deployed and tested
Status: Production-ready with fallback
```

### Week 4: Production
```
Frontend: Remove local data, API-only
Backend: Scale infrastructure
Status: Full production deployment
```

---

## Advantages of This Approach

### For Hackathon

**1. Reliability**
- Local data as backup if WiFi fails
- API shows production capability
- Best of both worlds

**2. Flexibility**
- Switch modes with environment variable
- Demo both approaches if needed
- Impress judges with options

**3. Risk Mitigation**
- Not dependent on network
- Not dependent on backend uptime
- Multiple fallback layers

### For Production

**1. Scalability**
- API can serve unlimited frontends
- No client-side data loading
- CDN for static assets

**2. Performance**
- Pre-aggregated backend data
- Client-side caching
- Optimal for all users

**3. Maintainability**
- Clear separation of concerns
- Easy to update backend
- Easy to update frontend

---

## Common Questions

**Q: Why not always use local data?**
A: Local data doesn't scale. 5M rows is 500MB - too large for production. API is <1s and works for any dataset size.

**Q: Why not always use API?**
A: During development, frontend team can work independently without waiting for backend. Also provides fallback for demos.

**Q: How do we handle predictions?**
A: Predictions ALWAYS use API. The ML model is backend-only. No fallback possible.

**Q: What about offline mode?**
A: Not a priority for hackathon. Post-hackathon, we can add service workers for offline caching.

**Q: How do we switch between modes?**
A: Environment variable: `NEXT_PUBLIC_USE_API=true/false`

---

## Conclusion

**Your current architecture is perfect!** No code changes needed.

**Frontend developer can:**
- Work with 5M rows locally
- Build UI independently
- Integrate APIs when ready
- Keep local data as fallback

**Backend (your work) is:**
- Production-ready
- API-first design
- Optimized for performance
- Ready for integration

**For hackathon:**
- Use API to show production capability
- Keep local data as backup
- Best of both worlds!

**This hybrid approach is actually a best practice for modern web development!**
