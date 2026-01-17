# 🚀 Frontend Guide: Tenant Quality Assessment Features

## Overview
We have enhanced **Product 1 (Rental Demand Forecasting)** with a new **Tenant Quality Assessment** feature.

- **Old Flow:** User inputs city → Gets demand number.
- **New Flow:** User inputs city → Gets demand number + **Tenant Quality Breakdown** + **Investment Recommendations**.

---

## 📡 API Endpoint

- **URL:** `http://localhost:5001/predict/enhanced`
- **Method:** `POST`

---

## 📨 Request Format

There is only **ONE** new field to add: `"include_tenant_quality": true`

```json
{
  "city": "Mumbai",           // Required
  "date": "2024-08-15",       // Required
  "include_tenant_quality": true, // <--- REQUIRED for new features
  "economic_factors": {       // Optional (use defaults functionality)
    "inflation_rate": 5.5,
    "interest_rate": 7.2
  }
}
```

---

## 📦 Response Handling

The response is richer now. Here are the key fields you need to map to UI components:

```json
{
  "base_demand": {
    "predicted_demand": 2474.71 // Base Number
  },
  "tenant_quality_analysis": {
    "grade_a_count": 999,      // Grade A (Premium)
    "grade_b_count": 1107,     // Grade B (Good)
    "grade_c_count": 368,      // Grade C (Fair)
    "grade_d_count": 0,        // Grade D (Risky)
    "average_default_risk": 0.28, // e.g. "28% Avg Risk"
    "financial_health_score": 47.9 // e.g. "48/100 Health"
  },
  "quality_adjusted_demand": 2137.62, // The "Real" Demand
  "investment_recommendation": {
    "rating": "STRONG_BUY",    // Display as Badge
    "confidence": 0.85,        // Display as % Bar or Circle
    "reasoning": "High demand..." // Tooltip or Text
  }
}
```

---

## 💡 TypeScript Interface

Use this interface for type safety in your frontend application:

```typescript
export interface EnhancedPredictionResponse {
  base_demand: {
    predicted_demand: number;
    unit?: string;
  };
  tenant_quality_analysis?: {
    grade_a_count: number;         // Grade A (Premium)
    grade_b_count: number;         // Grade B (Good)
    grade_c_count: number;         // Grade C (Fair)
    grade_d_count: number;         // Grade D (Risky)
    average_default_risk: number;  // 0.0 to 1.0
    financial_health_score: number; // 0 to 100
  };
  quality_adjusted_demand?: number;
  investment_recommendation?: {
    rating: "STRONG_BUY" | "BUY" | "HOLD" | "AVOID";
    confidence: number;
    quality_score?: number;
    reasoning: string;
  };
  city: string;
  date: string;
}
```

---

## 🖥️ Recommended UI Components

### 1. Investment Score Card (Hero Section)
- **Title:** Investment Rating
- **Badge:** display `rating`
  - 🟢 Green for `STRONG_BUY`
  - 🟡 Yellow for `HOLD` / `BUY`
  - 🔴 Red for `AVOID`
- **Confidence:** Circular progress bar using `confidence` (e.g., 85%)
- **Text:** Display `reasoning` prominently.

### 2. Demand Comparison Widget
Show two numbers side-by-side to highlight value:
- **Left:** "Total Demand" (`base_demand.predicted_demand`) - *Greyed out slightly*
- **Right:** "Quality-Adjusted Demand" (`quality_adjusted_demand`) - **Bold/Green**
- **Tooltip:** "Quality-adjusted demand excludes risky tenants likely to default."

### 3. Tenant Quality Breakdown (Donut Chart)
Visualize the `tenant_quality_analysis` grades:
- **Segments:**
  - Grade A (Premium) - `grade_a_count`
  - Grade B (Good) - `grade_b_count`
  - Grade C (Fair) - `grade_c_count`
  - Grade D (Risky) - `grade_d_count`
- **Center Text:** "Tenant Mix"

### 4. Risk Metrics Bar
Simple progress bars for average metrics:
- **Default Risk:** `average_default_risk` (Lower is better)
- **Financial Health:** `financial_health_score` (Higher is better)

---

## ⚠️ Integration Checklist

- [ ] Update API call to use `/predict/enhanced`
- [ ] Add `"include_tenant_quality": true` to payload
- [ ] Handle loading state (ML models take ~100-200ms extra)
- [ ] Add fallback: If `tenant_quality_analysis` or `investment_recommendation` fields are missing, show standard view
- [ ] Format all numbers (e.g. `2,474` instead of `2474.71`)
