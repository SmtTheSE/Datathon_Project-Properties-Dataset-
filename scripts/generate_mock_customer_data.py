"""
Script to generate mock 'Customer Behavior' data.
This simulates the new dataset expected in the Final Round.
Schema: User_ID, City, Locality, Action_Type, Timestamp, Device_Type
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_mock_data():
    print("Generating mock 'Customer Behavior' dataset...")
    
    # 1. Define scope
    n_rows = 50000
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata']
    actions = ['View_Property', 'Contact_Agent', 'Shortlist', 'Search']
    
    # 2. Generate random data
    data = {
        'User_ID': [f'U{i:06d}' for i in np.random.randint(1, 10000, n_rows)],
        'City': np.random.choice(cities, n_rows),
        'Action_Type': np.random.choice(actions, n_rows, p=[0.6, 0.1, 0.2, 0.1]),
        'Timestamp': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(n_rows)],
        'Device': np.random.choice(['Mobile', 'Desktop', 'App'], n_rows)
    }
    
    df = pd.DataFrame(data)
    
    # 3. Add 'Locality' based on City (to make it realistic for joining)
    # We use a simple mapping to ensure keys match our main dataset
    locality_map = {
        'Mumbai': ['Bandra', 'Andheri', 'Powai', 'Worli', 'Juhu'],
        'Delhi': ['Hauz Khas', 'Vasant Kunj', 'Dwarka', 'Saket', 'Lajpat Nagar'],
        'Bangalore': ['Koramangala', 'Indiranagar', 'Whitefield', 'HSR Layout', 'Jayanagar'],
        'Hyderabad': ['Gachibowli', 'Jubilee Hills', 'Banjara Hills', 'Madhapur', 'Kondapur'],
        'Chennai': ['Adyar', 'Anna Nagar', 'T Nagar', 'Velachery', 'Mylapore'],
        'Kolkata': ['Salt Lake', 'Ballygunge', 'New Town', 'Park Street', 'Jadavpur']
    }
    
    # helper to assign locality
    def get_locality(city):
        if city in locality_map:
            return np.random.choice(locality_map[city])
        return 'Unknown'
        
    df['Locality'] = df['City'].apply(get_locality)
    
    # 4. Save to CSV
    output_dir = os.path.join(os.getcwd(), 'data', 'final_round_mock')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'mock_customer_behavior.csv')
    df.to_csv(output_path, index=False)
    
    print(f"✅ Mock data generated: {n_rows} rows")
    print(f"📍 Saved to: {output_path}")
    print("\nPreview:")
    print(df.head())
    
    return output_path

if __name__ == "__main__":
    generate_mock_data()
