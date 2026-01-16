import pandas as pd
import json
import os
import numpy as np

def generate_summary_files():
    """
    Generate monthly_summary.json and locality_summary.json from the dataset
    """
    print("Generating summary JSON files...")
    
    # Dataset path candidates
    candidates = [
        'House_Rent_10M_balanced_40cities.csv',
        '../House_Rent_10M_balanced_40cities.csv',
        '../../House_Rent_10M_balanced_40cities.csv',
        '/Users/sittminthar/Desktop/Datathon_Project-Properties-Dataset-/10 Million House Rent Data of 40 cities/House_Rent_10M_balanced_40cities.csv'
    ]
    
    data_path = None
    for path in candidates:
        if os.path.exists(path):
            data_path = path
            print(f"Found dataset at: {data_path}")
            break
            
    if not data_path:
        print("Error: Dataset not found. Please place 'House_Rent_10M_balanced_40cities.csv' in the current directory or project root.")
        return
    
    # Read the dataset (only needed columns to save memory)
    print("Reading dataset...")
    df = pd.read_csv(data_path, usecols=['City', 'Area Locality', 'Posted On', 'BHK'], low_memory=False)
    
    # Convert 'Posted On' to datetime
    print("Processing dates...")
    df['Posted On'] = pd.to_datetime(df['Posted On'], format='mixed', dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Posted On'])
    
    # 1. Generate monthly_summary.json
    print("Generating monthly summary...")
    df['YearMonth'] = df['Posted On'].dt.strftime('%Y-%m')
    
    monthly_data = {}
    
    # Group by City and YearMonth
    city_monthly = df.groupby(['City', 'YearMonth']).size().reset_index(name='count')
    
    for _, row in city_monthly.iterrows():
        city = row['City']
        period = row['YearMonth']
        count = int(row['count'])
        
        if city not in monthly_data:
            monthly_data[city] = {}
        
        monthly_data[city][period] = count
        
    # Save monthly_summary.json
    monthly_path = 'monthly_summary.json'
    with open(monthly_path, 'w') as f:
        json.dump(monthly_data, f, indent=2)
    print(f"Saved {monthly_path}")
    
    # 2. Generate locality_summary.json
    print("Generating locality summary...")
    
    locality_data = {}
    
    # Group by City and Locality
    # Use value_counts or groupby
    locality_counts = df.groupby(['City', 'Area Locality']).size().reset_index(name='count')
    
    for _, row in locality_counts.iterrows():
        city = row['City']
        locality = row['Area Locality']
        count = int(row['count'])
        
        if city not in locality_data:
            locality_data[city] = {}
            
        locality_data[city][locality] = {
            'count': count
        }
        
    # Save locality_summary.json
    locality_path = 'locality_summary.json'
    with open(locality_path, 'w') as f:
        json.dump(locality_data, f, indent=2)
    print(f"Saved {locality_path}")
    print("Done!")

if __name__ == "__main__":
    generate_summary_files()
