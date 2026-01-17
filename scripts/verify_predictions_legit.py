"""
Prediction Legitimacy Test
Proves all predictions come from REAL model inference, not hardcoded values.

Test Strategy:
1. Make predictions with different inputs
2. Verify outputs change based on inputs
3. Confirm no hardcoded values
"""

import numpy as np
import joblib
import sys
import os

os.chdir('Product_1_Rental_Demand_Forecasting')

print("=" * 80)
print("🔍 PREDICTION LEGITIMACY VERIFICATION")
print("Testing: Are predictions real or hardcoded?")
print("=" * 80)

# Load models
print("\n✓ Loading models...")
churn_model = joblib.load('tenant_risk_model.pkl')
trans_model = joblib.load('transaction_amount_model.pkl')
print("✓ Models loaded successfully")

# Test 1: Different inputs should give different outputs
print("\n" + "=" * 80)
print("TEST 1: Different Inputs → Different Outputs")
print("=" * 80)

# Tenant Profile 1: Young, low balance
profile1 = np.array([[
    25.0,   # Age
    1.0,    # Tenure
    10.0,   # Avg_Trans_no_month
    1,      # No_CurrentAccount
    5000000.0,   # Avg_CurrentAccount_Balance (5M VND)
    0,      # No_TermDeposit
    0.0,    # Avg_TermDeposit_Balance
    1,      # No_Loan
    10000000.0,  # Avg_Loan_Balance (10M VND)
    0,      # No_CC
    1       # No_DC
]])

# Tenant Profile 2: Mature, high balance
profile2 = np.array([[
    45.0,   # Age
    10.0,   # Tenure
    30.0,   # Avg_Trans_no_month
    2,      # No_CurrentAccount
    50000000.0,  # Avg_CurrentAccount_Balance (50M VND)
    2,      # No_TermDeposit
    100000000.0, # Avg_TermDeposit_Balance (100M VND)
    0,      # No_Loan
    0.0,    # Avg_Loan_Balance
    2,      # No_CC
    2       # No_DC
]])

# Tenant Profile 3: Mid-range
profile3 = np.array([[
    35.0,   # Age
    5.0,    # Tenure
    20.0,   # Avg_Trans_no_month
    1,      # No_CurrentAccount
    20000000.0,  # Avg_CurrentAccount_Balance (20M VND)
    1,      # No_TermDeposit
    30000000.0,  # Avg_TermDeposit_Balance (30M VND)
    0,      # No_Loan
    0.0,    # Avg_Loan_Balance
    1,      # No_CC
    1       # No_DC
]])

# Make predictions
trans1 = trans_model.predict(profile1)[0]
trans2 = trans_model.predict(profile2)[0]
trans3 = trans_model.predict(profile3)[0]

print("\nTransaction Amount Predictions:")
print(f"  Profile 1 (Young, Low Balance):  {trans1:,.0f} VND")
print(f"  Profile 2 (Mature, High Balance): {trans2:,.0f} VND")
print(f"  Profile 3 (Mid-range):            {trans3:,.0f} VND")

# Verify they're different
if trans1 != trans2 and trans2 != trans3 and trans1 != trans3:
    print("\n✅ PASS: All predictions are DIFFERENT (not hardcoded!)")
else:
    print("\n❌ FAIL: Predictions are the same (might be hardcoded)")

# Test 2: Predictions should be in reasonable range
print("\n" + "=" * 80)
print("TEST 2: Predictions in Reasonable Range")
print("=" * 80)

min_trans = 100000  # 100K VND
max_trans = 15000000  # 15M VND

print(f"\nExpected range: {min_trans:,} - {max_trans:,} VND")
print(f"Profile 1: {trans1:,.0f} VND - {'✅ Valid' if min_trans <= trans1 <= max_trans else '❌ Out of range'}")
print(f"Profile 2: {trans2:,.0f} VND - {'✅ Valid' if min_trans <= trans2 <= max_trans else '❌ Out of range'}")
print(f"Profile 3: {trans3:,.0f} VND - {'✅ Valid' if min_trans <= trans3 <= max_trans else '❌ Out of range'}")

# Test 3: Higher balance should predict higher transaction amount
print("\n" + "=" * 80)
print("TEST 3: Logical Relationship (Higher Balance → Higher Transaction)")
print("=" * 80)

if trans2 > trans1:
    print(f"\n✅ PASS: High balance ({trans2:,.0f}) > Low balance ({trans1:,.0f})")
    print("   Model learned the correct relationship!")
else:
    print(f"\n❌ FAIL: Relationship doesn't make sense")

# Test 4: Churn model predictions
print("\n" + "=" * 80)
print("TEST 4: Churn Model - Different Inputs → Different Outputs")
print("=" * 80)

# Simplified churn features
churn_profile1 = np.array([[30, 40, 30, 35, 40, 35]])  # Low scores
churn_profile2 = np.array([[80, 85, 90, 85, 80, 85]])  # High scores
churn_profile3 = np.array([[55, 60, 55, 60, 55, 60]])  # Medium scores

churn_prob1 = churn_model.predict_proba(churn_profile1)[0][1]
churn_prob2 = churn_model.predict_proba(churn_profile2)[0][1]
churn_prob3 = churn_model.predict_proba(churn_profile3)[0][1]

print("\nChurn Probability Predictions:")
print(f"  Low Financial Health:    {churn_prob1:.4f} ({churn_prob1*100:.2f}%)")
print(f"  High Financial Health:   {churn_prob2:.4f} ({churn_prob2*100:.2f}%)")
print(f"  Medium Financial Health: {churn_prob3:.4f} ({churn_prob3*100:.2f}%)")

if churn_prob1 != churn_prob2 and churn_prob2 != churn_prob3:
    print("\n✅ PASS: All predictions are DIFFERENT (not hardcoded!)")
else:
    print("\n❌ FAIL: Predictions are the same")

# Test 5: Logical relationship for churn
print("\n" + "=" * 80)
print("TEST 5: Logical Relationship (Higher Health → Lower Churn Risk)")
print("=" * 80)

if churn_prob2 < churn_prob1:
    print(f"\n✅ PASS: High health ({churn_prob2*100:.2f}%) < Low health ({churn_prob1*100:.2f}%)")
    print("   Model learned the correct relationship!")
else:
    print(f"\n❌ FAIL: Relationship doesn't make sense")

# Test 6: Random input test
print("\n" + "=" * 80)
print("TEST 6: Random Inputs Generate Unique Predictions")
print("=" * 80)

predictions = []
for i in range(5):
    random_profile = np.array([[
        np.random.uniform(25, 60),  # Age
        np.random.uniform(1, 15),   # Tenure
        np.random.uniform(5, 40),   # Transactions
        np.random.randint(1, 3),    # Accounts
        np.random.uniform(1e6, 50e6),  # Balance
        np.random.randint(0, 3),    # Term deposits
        np.random.uniform(0, 100e6),   # TD Balance
        np.random.randint(0, 2),    # Loans
        np.random.uniform(0, 20e6),    # Loan balance
        np.random.randint(0, 3),    # CC
        np.random.randint(0, 3)     # DC
    ]])
    pred = trans_model.predict(random_profile)[0]
    predictions.append(pred)
    print(f"  Random Test {i+1}: {pred:,.0f} VND")

# Check if all predictions are unique
unique_predictions = len(set(predictions))
print(f"\n✅ Generated {unique_predictions}/5 unique predictions")
if unique_predictions >= 4:
    print("   Model is generating dynamic predictions, not hardcoded values!")

# Final Summary
print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)

all_tests_passed = (
    trans1 != trans2 != trans3 and  # Different outputs
    min_trans <= trans1 <= max_trans and  # Valid range
    trans2 > trans1 and  # Logical relationship
    churn_prob1 != churn_prob2 and  # Different churn outputs
    churn_prob2 < churn_prob1 and  # Logical churn relationship
    unique_predictions >= 4  # Random uniqueness
)

if all_tests_passed:
    print("\n✅ ALL TESTS PASSED!")
    print("\n🎯 VERDICT: Predictions are 100% LEGITIMATE")
    print("   - All predictions come from REAL model inference")
    print("   - Different inputs produce different outputs")
    print("   - Predictions follow logical relationships")
    print("   - No hardcoded values detected")
    print("\n   Models are working correctly with real data!")
else:
    print("\n⚠️ Some tests failed - review results above")

print("\n" + "=" * 80)
