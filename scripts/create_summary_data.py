"""
Script to create pre-aggregated summary data from the 10M row dataset
This creates small, fast-loading summary files for historical charts
"""

import pandas as pd
import json
from datetime import datetime

print("Creating pre-aggregated summary data...")
print("This will take a few minutes but only needs to run once...")

# Read the dataset in chunks and aggregate
chunk_size = 500000
monthly_summary = {}
locality_summary = {}

print("\nProcessing dataset in chunks...")
chunk_count = 0

for chunk in pd.read_csv(
    '10 Million House Rent Data of 40 cities/House_Rent_10M_balanced_40cities.csv',
    usecols=['Posted On', 'City', 'Area Locality', 'Rent', 'BHK'],
    parse_dates=['Posted On'],
    chunksize=chunk_size
):
    chunk_count += 1
    print(f"Processing chunk {chunk_count}... ({len(chunk)} rows)")
    
    # Aggregate monthly demand by city
    chunk['YearMonth'] = chunk['Posted On'].dt.to_period('M').astype(str)
    monthly_counts = chunk.groupby(['City', 'YearMonth']).size()
    
    for (city, month), count in monthly_counts.items():
        if city not in monthly_summary:
            monthly_summary[city] = {}
        monthly_summary[city][month] = monthly_summary[city].get(month, 0) + count
    
    # Aggregate locality data by city
    locality_counts = chunk.groupby(['City', 'Area Locality']).agg({
        'Rent': ['count', 'sum'],
        'BHK': 'first'
    })
    
    for (city, locality), row in locality_counts.iterrows():
        if city not in locality_summary:
            locality_summary[city] = {}
        if locality not in locality_summary[city]:
            locality_summary[city][locality] = {'count': 0, 'rent_sum': 0}
        
        locality_summary[city][locality]['count'] += int(row[('Rent', 'count')])
        locality_summary[city][locality]['rent_sum'] += float(row[('Rent', 'sum')])

print(f"\nProcessed {chunk_count} chunks")
print(f"Cities found: {len(monthly_summary)}")

# Save monthly summary
print("\nSaving monthly_summary.json...")
with open('Product_1_Rental_Demand_Forecasting/monthly_summary.json', 'w') as f:
    json.dump(monthly_summary, f)

# Save locality summary  
print("Saving locality_summary.json...")
with open('Product_2_Demand_Supply_Gap_Identification/locality_summary.json', 'w') as f:
    json.dump(locality_summary, f)

print("\n✅ Summary files created successfully!")
print(f"   - Product_1_Rental_Demand_Forecasting/monthly_summary.json")
print(f"   - Product_2_Demand_Supply_Gap_Identification/locality_summary.json")
print("\nThese files are small and will load instantly!")
