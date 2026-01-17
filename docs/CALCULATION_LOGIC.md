# Metrics & Calculation Logic Documentation

This document details the mathematical flows, feature engineering, and performance metric calculations used in our **Demand Forecasting (Product 1)** and **Gap Identification (Product 2)** models.

## 1. RMSE (Root Mean Square Error) Calculation

**Definition:** RMSE measures the average magnitude of the error between predicted values and observed values. It penalizes larger errors more heavily than smaller ones.

**Code Implementation:**
We use the standard implementation from `sklearn.metrics` combined with NumPy.

```python
from sklearn.metrics import mean_squared_error
import numpy as np

# Logic used in training scripts
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
```

**Formula:**
$$RMSE = \sqrt{\frac{1}{n}\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$

Where:
- $n$ = Number of samples
- $y_i$ = Actual value (Ground Truth)
- $\hat{y}_i$ = Predicted value by model

---

## 2. Product 1: Rental Demand Forecasting Flow

### A. Target Variable (`y`)
The target variable is **`Demand_Count`**.
- **Source:** Aggregated count of property interactions/searches per City per Date.
- **Unit:** Count (integer).

### B. Feature Flow (`X`)
Input data goes through the following transformations before reaching the model:

1.  **Temporal Features:**
    - `Year`, `Month` extracted from 'Posted On'.
    - **Cyclical Encoding:** Month is converted to sine/cosine components to preserve seasonal continuity.
      - `Month_Sin = sin(2 * π * Month / 12)`
      - `Month_Cos = cos(2 * π * Month / 12)`

2.  **Economic Features:**
    - `inflation_rate`, `interest_rate`
   

3.  **Scaling:**
    - Features are standardized using `StandardScaler` (Z-score normalization) before training.

### C. Evaluation (RMSE Interpretation)
- **Context:** If the validation RMSE is **250**, it means the model's predictions for daily demand are, on average, off by roughly 250 interactions.
- **Goal:** Minimize this value to effectively match the variance in user traffic.

---

## 3. Product 2: Demand-Supply Gap Identification Flow

### A. Core Metric: Gap Ratio
This is a derived metric used to define market health.

**Formula:**
$$Gap\ Ratio = \frac{(Demand - Supply)}{(Supply + 1)}$$

*Note: We add +1 to the denominator to prevent division by zero.*

**Interpretation:**
- **Positive Values (> 0):** Undersupply (High Demand).
- **Negative Values (< 0):** Oversupply (Low Demand).
- **Near Zero:** Balanced Market.

### B. Feature Flow (`Calculate Demand & Gap`)
In `train_gap_model_efficient.py`, the flow is:

1.  **Synthesize Demand Factor:**
    Based on Rent, Employment, and Economic Health.
    ```python
    Demand_Factor = (
        (Normalized_Rent * 0.3) +
        (Normalized_Employment * 0.3) +
        (Economic_Health * 0.2) +
        Random_Noise
    )
    ```

2.  **Calculate Demand Count:**
    $$Demand = Supply \times Demand\_Factor$$

3.  **Calculate Target (`y`):**
    The model is trained specifically to predict the **`Gap_Ratio`**.

### C. Evaluation (RMSE Interpretation)
- **Target Range:** Gap Ratio typically ranges from -1.0 to +3.0 (or higher).
- **Context:** An RMSE of **0.05** means the model predicts the market tightness ratio with very high precision (within ±5% margin of the actual calculated gap).

---

## 4. Evaluation Strategy

For both products, we use **Time Series Cross-Validation (`TimeSeriesSplit`)**.
This ensures we calculate RMSE on "future" data relative to the training set, mimicking real-world production performance.

1.  Split data into 5 chronological folds.
2.  Train on Past $\rightarrow$ Predict Future.
3.  Calculate RMSE for each fold.
4.  **Final Score:** Average RMSE across all folds.
