# API Request Specifications

Complete JSON request specifications for all API endpoints to help frontend developers build forms correctly.

---

## Product 1: Rental Demand Forecasting API

**Base URL:** `http://localhost:5001` (or your deployed URL)

### 1. Single Prediction - `/predict`

**Method:** `POST`  
**Endpoint:** `/predict`  
**Content-Type:** `application/json`

#### Request Body Structure

```json
{
  "city": "Mumbai",
  "date": "2024-08-15",
  "economic_factors": {
    "inflation_rate": 6.5,
    "interest_rate": 7.0,
    "employment_rate": 82.0,
    "covid_impact_score": 0.05,
    "gdp_growth": 7.2,
    "economic_health_score": 0.85
  }
}
```

#### Field Specifications

| Field | Type | Required | Description | Valid Values/Range | Default |
|-------|------|----------|-------------|-------------------|---------|
| `city` | string | **Yes** | City name | Any of 40+ Indian cities (see `/cities` endpoint) | - |
| `date` | string | **Yes** | Prediction date | Format: `YYYY-MM-DD` | - |
| `economic_factors` | object | No | Economic indicators | See below | Auto-filled defaults |

#### Economic Factors Object (Optional)

| Field | Type | Required | Description | Valid Range | Default |
|-------|------|----------|-------------|-------------|---------|
| `inflation_rate` | number | No | Inflation rate (%) | 0-20 | 6.0 |
| `interest_rate` | number | No | Interest rate (%) | 0-15 | 7.0 |
| `employment_rate` | number | No | Employment rate (%) | 0-100 | 85.0 |
| `covid_impact_score` | number | No | COVID impact score | 0-1 | 0.1 |
| `gdp_growth` | number | No | GDP growth rate (%) | -10 to 15 | 7.0 |
| `economic_health_score` | number | No | Overall economic health | 0-1 | 0.8 |

> **Note:** If `economic_factors` is omitted entirely, the API will use default values for all economic indicators.

#### Example Requests

**Minimal Request (Required fields only):**
```json
{
  "city": "Mumbai",
  "date": "2024-08-15"
}
```

**Full Request (With all economic factors):**
```json
{
  "city": "Bangalore",
  "date": "2024-12-25",
  "economic_factors": {
    "inflation_rate": 5.5,
    "interest_rate": 6.5,
    "employment_rate": 87.0,
    "covid_impact_score": 0.05,
    "gdp_growth": 7.5,
    "economic_health_score": 0.9
  }
}
```

**Partial Economic Factors:**
```json
{
  "city": "Delhi",
  "date": "2024-10-01",
  "economic_factors": {
    "inflation_rate": 6.2,
    "interest_rate": 7.5
  }
}
```

#### Response Format

```json
{
  "city": "Mumbai",
  "year": 2024,
  "month": 8,
  "predicted_demand": 2450,
  "confidence": "high",
  "economic_indicators_used": {
    "inflation_rate": 6.5,
    "interest_rate": 7.0,
    "employment_rate": 82.0,
    "covid_impact_score": 0.05,
    "economic_health_score": 0.85
  }
}
```

---

### 2. Batch Prediction - `/predict/batch`

**Method:** `POST`  
**Endpoint:** `/predict/batch`  
**Content-Type:** `application/json`

#### Request Body Structure

```json
{
  "requests": [
    {
      "city": "Mumbai",
      "date": "2024-08-15",
      "economic_factors": {
        "inflation_rate": 6.5,
        "interest_rate": 7.0
      }
    },
    {
      "city": "Delhi",
      "date": "2024-09-01"
    },
    {
      "city": "Bangalore",
      "date": "2024-10-15",
      "economic_factors": {
        "inflation_rate": 5.8,
        "interest_rate": 6.8,
        "employment_rate": 88.0
      }
    }
  ]
}
```

#### Field Specifications

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `requests` | array | **Yes** | Array of prediction requests | Max 50 items |

Each item in `requests` follows the same structure as the single prediction endpoint.

#### Response Format

```json
{
  "predictions": [
    {
      "city": "Mumbai",
      "year": 2024,
      "month": 8,
      "predicted_demand": 2450,
      "confidence": "high",
      "economic_indicators_used": {...}
    },
    {
      "city": "Delhi",
      "year": 2024,
      "month": 9,
      "predicted_demand": 1980,
      "confidence": "high",
      "economic_indicators_used": {...}
    }
  ]
}
```

---

### 3. Get Supported Cities - `/cities`

**Method:** `GET`  
**Endpoint:** `/cities`

#### Response Format

```json
{
  "cities": [
    "Agra",
    "Ahmedabad",
    "Allahabad",
    "Amritsar",
    "Aurangabad",
    "Bangalore",
    "Bhopal",
    "Bhubaneswar",
    "Chandigarh",
    "Chennai",
    "Coimbatore",
    "Delhi",
    "Faridabad",
    "Ghaziabad",
    "Gurgaon",
    "Hyderabad",
    "Indore",
    "Jabalpur",
    "Jaipur",
    "Jalandhar",
    "Kalyan",
    "Kanpur",
    "Kochi",
    "Kolkata",
    "Lucknow",
    "Ludhiana",
    "Madurai",
    "Meerut",
    "Mumbai",
    "Mysore",
    "Nagpur",
    "Nashik",
    "Patna",
    "Pune",
    "Rajkot",
    "Ranchi",
    "Srinagar",
    "Surat",
    "Thane",
    "Vadodara",
    "Varanasi",
    "Visakhapatnam"
  ]
}
```

---

### 4. Get Historical Data - `/historical/<city>`

**Method:** `GET`  
**Endpoint:** `/historical/{city}`  
**Query Parameters:**
- `months` (optional): Number of months of historical data (1-24, default: 12)

#### Example Request

```
GET /historical/Mumbai?months=12
```

#### Response Format

```json
{
  "city": "Mumbai",
  "historical_data": [
    {
      "month": "Jan",
      "demand": 2450,
      "year": 2024
    },
    {
      "month": "Feb",
      "demand": 2480,
      "year": 2024
    },
    {
      "month": "Mar",
      "demand": 2520,
      "year": 2024
    }
  ]
}
```

---

## Product 2: Demand-Supply Gap Analysis API

**Base URL:** `http://localhost:5002` (or your deployed URL)

### 1. Single Gap Prediction - `/predict`

**Method:** `POST`  
**Endpoint:** `/predict`  
**Content-Type:** `application/json`

#### Request Body Structure

```json
{
  "city": "Mumbai",
  "area_locality": "Bandra",
  "bhk": 2,
  "avg_rent": 35000,
  "economic_indicators": {
    "inflation_rate": 5.5,
    "interest_rate": 6.5,
    "employment_rate": 87.0,
    "covid_impact_score": 0.05,
    "economic_health_score": 0.85,
    "city_tier": "Tier1",
    "region": "West"
  }
}
```

#### Field Specifications

| Field | Type | Required | Description | Valid Values/Range | Default |
|-------|------|----------|-------------|-------------------|---------|
| `city` | string | **Yes** | City name | Any of 40+ Indian cities | - |
| `area_locality` | string | **Yes** | Locality/Area name | Any locality name | - |
| `bhk` | integer | **Yes** | Number of bedrooms | 1, 2, 3, 4, 5+ | - |
| `avg_rent` | number | **Yes** | Average rent (₹) | > 0 | - |
| `economic_indicators` | object | No | Economic indicators | See below | Auto-filled defaults |

#### Economic Indicators Object (Optional)

| Field | Type | Required | Description | Valid Values | Default |
|-------|------|----------|-------------|--------------|---------|
| `inflation_rate` | number | No | Inflation rate (%) | 0-20 | 6.0 |
| `interest_rate` | number | No | Interest rate (%) | 0-15 | 7.0 |
| `employment_rate` | number | No | Employment rate (%) | 0-100 | 85.0 |
| `covid_impact_score` | number | No | COVID impact score | 0-1 | 0.1 |
| `economic_health_score` | number | No | Overall economic health | 0-1 | 0.8 |
| `city_tier` | string | No | City tier classification | "Tier1", "Tier2" | "Tier1" |
| `region` | string | No | Geographic region | "North", "South", "East", "West" | "West" |

#### Example Requests

**Minimal Request:**
```json
{
  "city": "Mumbai",
  "area_locality": "Bandra",
  "bhk": 2,
  "avg_rent": 35000
}
```

**Full Request:**
```json
{
  "city": "Bangalore",
  "area_locality": "Koramangala",
  "bhk": 3,
  "avg_rent": 45000,
  "economic_indicators": {
    "inflation_rate": 5.8,
    "interest_rate": 6.8,
    "employment_rate": 88.0,
    "covid_impact_score": 0.03,
    "economic_health_score": 0.9,
    "city_tier": "Tier1",
    "region": "South"
  }
}
```

#### Response Format

```json
{
  "city": "Mumbai",
  "area_locality": "Bandra",
  "bhk": 2,
  "avg_rent": 35000,
  "predicted_gap_ratio": 0.061,
  "gap_severity": "low",
  "demand_supply_status": "demand_exceeds_supply",
  "economic_indicators_used": {
    "inflation_rate": 5.5,
    "interest_rate": 6.5,
    "employment_rate": 87.0,
    "covid_impact_score": 0.05,
    "economic_health_score": 0.85,
    "city_tier": "Tier1",
    "region": "West"
  }
}
```

#### Gap Ratio Interpretation

- **Positive value** (e.g., +0.061): Demand exceeds supply (undersupplied)
- **Negative value** (e.g., -0.15): Supply exceeds demand (oversupplied)
- **Gap Severity:**
  - `low`: |gap_ratio| ≤ 0.1
  - `medium`: 0.1 < |gap_ratio| ≤ 0.3
  - `high`: |gap_ratio| > 0.3

---

### 2. Batch Gap Prediction - `/predict/batch`

**Method:** `POST`  
**Endpoint:** `/predict/batch`  
**Content-Type:** `application/json`

#### Request Body Structure

```json
{
  "requests": [
    {
      "city": "Mumbai",
      "area_locality": "Bandra",
      "bhk": 2,
      "avg_rent": 35000,
      "economic_indicators": {
        "inflation_rate": 5.5,
        "city_tier": "Tier1",
        "region": "West"
      }
    },
    {
      "city": "Delhi",
      "area_locality": "Connaught Place",
      "bhk": 3,
      "avg_rent": 40000
    }
  ]
}
```

#### Response Format

```json
{
  "predictions": [
    {
      "city": "Mumbai",
      "area_locality": "Bandra",
      "bhk": 2,
      "avg_rent": 35000,
      "predicted_gap_ratio": 0.061,
      "gap_severity": "low",
      "demand_supply_status": "demand_exceeds_supply",
      "economic_indicators_used": {...}
    },
    {
      "city": "Delhi",
      "area_locality": "Connaught Place",
      "bhk": 3,
      "avg_rent": 40000,
      "predicted_gap_ratio": -0.12,
      "gap_severity": "medium",
      "demand_supply_status": "supply_exceeds_demand",
      "economic_indicators_used": {...}
    }
  ]
}
```

---

### 3. Get Locality Gap Data - `/historical/<city>`

**Method:** `GET`  
**Endpoint:** `/historical/{city}`  
**Query Parameters:**
- `top_n` (optional): Number of top localities (1-50, default: 10)
- `sort_by` (optional): Sorting method
  - `demand` (default): Sort by highest demand
  - `gap_high`: Sort by most oversupplied (most negative gap)
  - `gap_low`: Sort by most undersupplied (most positive gap)
  - `gap_abs`: Sort by most extreme gaps (absolute value)

#### Example Request

```
GET /historical/Mumbai?top_n=10&sort_by=demand
```

#### Response Format

```json
{
  "city": "Mumbai",
  "locality_data": [
    {
      "locality": "Area 191",
      "gap": 0.249,
      "demand": 347
    },
    {
      "locality": "Area 145",
      "gap": -0.18,
      "demand": 298
    },
    {
      "locality": "Area 203",
      "gap": 0.12,
      "demand": 275
    }
  ]
}
```

---

## Frontend Form Building Guide

### Product 1: Demand Forecasting Form

#### Recommended Form Fields

```html
<!-- Required Fields -->
<select name="city" required>
  <!-- Populate from /cities endpoint -->
</select>

<input type="date" name="date" required />

<!-- Optional Economic Factors (Collapsible Section) -->
<input type="number" name="inflation_rate" min="0" max="20" step="0.1" placeholder="6.0" />
<input type="number" name="interest_rate" min="0" max="15" step="0.1" placeholder="7.0" />
<input type="number" name="employment_rate" min="0" max="100" step="0.1" placeholder="85.0" />
<input type="number" name="covid_impact_score" min="0" max="1" step="0.01" placeholder="0.1" />
<input type="number" name="gdp_growth" min="-10" max="15" step="0.1" placeholder="7.0" />
<input type="number" name="economic_health_score" min="0" max="1" step="0.01" placeholder="0.8" />
```

#### JavaScript Example

```javascript
async function submitDemandForecast(formData) {
  const requestBody = {
    city: formData.city,
    date: formData.date // Format: YYYY-MM-DD
  };
  
  // Only include economic_factors if at least one field is filled
  const economicFactors = {};
  if (formData.inflation_rate) economicFactors.inflation_rate = parseFloat(formData.inflation_rate);
  if (formData.interest_rate) economicFactors.interest_rate = parseFloat(formData.interest_rate);
  if (formData.employment_rate) economicFactors.employment_rate = parseFloat(formData.employment_rate);
  if (formData.covid_impact_score) economicFactors.covid_impact_score = parseFloat(formData.covid_impact_score);
  if (formData.gdp_growth) economicFactors.gdp_growth = parseFloat(formData.gdp_growth);
  if (formData.economic_health_score) economicFactors.economic_health_score = parseFloat(formData.economic_health_score);
  
  if (Object.keys(economicFactors).length > 0) {
    requestBody.economic_factors = economicFactors;
  }
  
  const response = await fetch('http://localhost:5001/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestBody)
  });
  
  return await response.json();
}
```

---

### Product 2: Gap Analysis Form

#### Recommended Form Fields

```html
<!-- Required Fields -->
<select name="city" required>
  <!-- Populate from /cities endpoint -->
</select>

<input type="text" name="area_locality" required placeholder="e.g., Bandra" />

<select name="bhk" required>
  <option value="1">1 BHK</option>
  <option value="2">2 BHK</option>
  <option value="3">3 BHK</option>
  <option value="4">4 BHK</option>
  <option value="5">5+ BHK</option>
</select>

<input type="number" name="avg_rent" required min="1000" step="100" placeholder="35000" />

<!-- Optional Economic Indicators (Collapsible Section) -->
<input type="number" name="inflation_rate" min="0" max="20" step="0.1" placeholder="6.0" />
<input type="number" name="interest_rate" min="0" max="15" step="0.1" placeholder="7.0" />
<input type="number" name="employment_rate" min="0" max="100" step="0.1" placeholder="85.0" />
<input type="number" name="covid_impact_score" min="0" max="1" step="0.01" placeholder="0.1" />
<input type="number" name="economic_health_score" min="0" max="1" step="0.01" placeholder="0.8" />

<select name="city_tier">
  <option value="">Auto-detect</option>
  <option value="Tier1">Tier 1</option>
  <option value="Tier2">Tier 2</option>
</select>

<select name="region">
  <option value="">Auto-detect</option>
  <option value="North">North</option>
  <option value="South">South</option>
  <option value="East">East</option>
  <option value="West">West</option>
</select>
```

#### JavaScript Example

```javascript
async function submitGapAnalysis(formData) {
  const requestBody = {
    city: formData.city,
    area_locality: formData.area_locality,
    bhk: parseInt(formData.bhk),
    avg_rent: parseFloat(formData.avg_rent)
  };
  
  // Only include economic_indicators if at least one field is filled
  const economicIndicators = {};
  if (formData.inflation_rate) economicIndicators.inflation_rate = parseFloat(formData.inflation_rate);
  if (formData.interest_rate) economicIndicators.interest_rate = parseFloat(formData.interest_rate);
  if (formData.employment_rate) economicIndicators.employment_rate = parseFloat(formData.employment_rate);
  if (formData.covid_impact_score) economicIndicators.covid_impact_score = parseFloat(formData.covid_impact_score);
  if (formData.economic_health_score) economicIndicators.economic_health_score = parseFloat(formData.economic_health_score);
  if (formData.city_tier) economicIndicators.city_tier = formData.city_tier;
  if (formData.region) economicIndicators.region = formData.region;
  
  if (Object.keys(economicIndicators).length > 0) {
    requestBody.economic_indicators = economicIndicators;
  }
  
  const response = await fetch('http://localhost:5002/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestBody)
  });
  
  return await response.json();
}
```

---

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "error": "Missing required field: city"
}
```

#### 429 Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded. Maximum 100 requests per minute."
}
```

#### 500 Internal Server Error
```json
{
  "error": "Prediction failed: [error details]"
}
```

### Validation Rules

1. **City names:** Only letters, spaces, and hyphens; max 50 characters
2. **Date format:** Must be `YYYY-MM-DD`
3. **Numeric fields:** Must be within specified ranges
4. **Batch requests:** Maximum 50 items per batch

---

## Testing Examples

### cURL Examples

**Product 1 - Minimal Request:**
```bash
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Mumbai",
    "date": "2024-08-15"
  }'
```

**Product 1 - Full Request:**
```bash
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Mumbai",
    "date": "2024-08-15",
    "economic_factors": {
      "inflation_rate": 6.5,
      "interest_rate": 7.0,
      "employment_rate": 82.0,
      "covid_impact_score": 0.05,
      "gdp_growth": 7.2,
      "economic_health_score": 0.85
    }
  }'
```

**Product 2 - Minimal Request:**
```bash
curl -X POST http://localhost:5002/predict \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Mumbai",
    "area_locality": "Bandra",
    "bhk": 2,
    "avg_rent": 35000
  }'
```

**Product 2 - Full Request:**
```bash
curl -X POST http://localhost:5002/predict \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Mumbai",
    "area_locality": "Bandra",
    "bhk": 2,
    "avg_rent": 35000,
    "economic_indicators": {
      "inflation_rate": 5.5,
      "interest_rate": 6.5,
      "employment_rate": 87.0,
      "covid_impact_score": 0.05,
      "economic_health_score": 0.85,
      "city_tier": "Tier1",
      "region": "West"
    }
  }'
```

---

## Quick Reference

### Product 1 Required Fields
- `city` (string)
- `date` (YYYY-MM-DD)

### Product 2 Required Fields
- `city` (string)
- `area_locality` (string)
- `bhk` (integer)
- `avg_rent` (number)

### Optional Economic Parameters (Both Products)
- `inflation_rate` (0-20)
- `interest_rate` (0-15)
- `employment_rate` (0-100)
- `covid_impact_score` (0-1)
- `economic_health_score` (0-1)

### Product 2 Additional Optional Parameters
- `city_tier` ("Tier1" or "Tier2")
- `region` ("North", "South", "East", "West")
- `gdp_growth` (-10 to 15) - Product 1 only

---

## Support

For issues or questions, please refer to:
- Technical Architecture: `docs/TECHNICAL_ARCHITECTURE.md`
- Project Structure: `docs/PROJECT_STRUCTURE.md`
- Main README: `docs/README.md`
