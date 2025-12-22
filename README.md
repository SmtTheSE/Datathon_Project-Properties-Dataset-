# 10 Million House Rent Data of 40 Cities

This dataset is a large-scale, high-fidelity simulation of the property rental market across **40 major Indian metropolitan cities**. With **10,000,000 records**, it is specifically engineered for **advanced Machine Learning**, comprehensive data engineering tasks, and large-scale system testing, offering a realistic view of India's diverse rental market dynamics.

---

## 1. Data Explanation and Scope

The dataset captures two years of simulated property rental listings, encompassing variations in price, property attributes, and city-level market behaviors. Each of the $10,000,000$ rows represents a unique rental listing, making it one of the largest synthetic datasets available for this domain.

### Key Variables for Rent Prediction

| Column | Description | Analytical Relevance |
| :--- | :--- | :--- |
| **Rent** | Monthly rent (in INR) | **Target Variable** for regression models. |
| **Size** | Area of the property in sq.ft | Primary feature correlated with rent. |
| **BHK** | Number of bedrooms (Bedroom, Hall, Kitchen) | Key structural attribute influencing rent and tenant type. |
| **City** | One of 40 major Indian cities | Crucial categorical variable capturing market demand and price floor/ceiling. |
| **Furnishing Status** | Unfurnished / Semi-Furnished / Furnished | Significant factor impacting rental premium. |
| **Area Type** | Super Area / Built Area / Carpet Area / Plot Area | Requires feature engineering/standardization for accurate size comparison. |
| **Year Built** | Construction year of the property | Proxy for property age and maintenance quality. |
| **Tenant Preferred** | Bachelors, Family, or Both | Insights into regional social norms and target marketing. |
| **Point of Contact** | Owner / Agent contact type | Useful for business analytics on listing dynamics. |

### Geographic Coverage:

The data focuses exclusively on **40 major Indian metropolitan cities** (e.g., Mumbai, Delhi, Bangalore, Hyderabad, Chennai, Kolkata, Pune). This concentrated focus ensures the captured rental patterns are highly relevant to the actual market demand centers in the country.

---

## 3. Topic Suggestions for Projects

* **A. Core Machine Learning Project**
* **B. City-wise Rental Market Analysis** (EDA & Visualization)
* **C. Time Series Analysis**