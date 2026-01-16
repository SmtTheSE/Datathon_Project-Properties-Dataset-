"""
Script to Integrate 'Customer Behavior' Data with Rental Property Data.
This implements the "Bridge" pattern from FINAL_ROUND_STRATEGY.md.
"""

import pandas as pd
import numpy as np
import os

def integrate_customer_data():
    print("🚀 Starting Customer Behavior Integration...")
    
    # 1. Load Main Rental Data (using standard dataset)
    rental_path = '10 Million House Rent Data of 40 cities/House_Rent_10M_balanced_40cities.csv'
    if not os.path.exists(rental_path):
        print(f"❌ Error: Main dataset not found at {rental_path}")
        return
        
    print(f"Loading rental data from {rental_path}...")
    # Read a sample for speed (or full if feasible)
    df_rental = pd.read_csv(rental_path, low_memory=False) 
    # Use lowercase for standardizing
    df_rental['City'] = df_rental['City'].str.strip()
    df_rental['Area Locality'] = df_rental['Area Locality'].str.strip()
    print(f"Loaded {len(df_rental)} rental listings.")

    # 2. Load Customer Behavior Data (Mock)
    customer_path = 'data/final_round_mock/mock_customer_behavior.csv'
    if not os.path.exists(customer_path):
        print(f"❌ Error: Customer data not found at {customer_path}")
        return
        
    print(f"Loading customer behavior data from {customer_path}...")
    df_customer = pd.read_csv(customer_path)
    df_customer['City'] = df_customer['City'].str.strip()
    df_customer['Locality'] = df_customer['Locality'].str.strip()
    
    # 3. Engineer Features from Customer Data
    print("Engineering 'Customer Interest' features...")
    
    # Feature 1: Search Volume per Locality
    locality_searches = df_customer[df_customer['Action_Type'] == 'Search'].groupby(['City', 'Locality']).size().reset_index(name='Locality_Search_Volume')
    
    # Feature 2: Contact Ratio (High Intent)
    locality_contacts = df_customer[df_customer['Action_Type'] == 'Contact_Agent'].groupby(['City', 'Locality']).size().reset_index(name='Locality_Contacts')
    
    # Feature 3: Property Views
    locality_views = df_customer[df_customer['Action_Type'] == 'View_Property'].groupby(['City', 'Locality']).size().reset_index(name='Locality_Views')
    
    # Merge these features into a single 'Locality_Score' dataframe
    locality_features = locality_searches.merge(locality_contacts, on=['City', 'Locality'], how='outer')
    locality_features = locality_features.merge(locality_views, on=['City', 'Locality'], how='outer')
    locality_features = locality_features.fillna(0)
    
    # Calculate derived metrics
    locality_features['View_to_Contact_Ratio'] = locality_features['Locality_Contacts'] / (locality_features['Locality_Views'] + 1)
    locality_features['High_Demand_Flag'] = (locality_features['Locality_Search_Volume'] > locality_features['Locality_Search_Volume'].median()).astype(int)
    
    print("New Features Engineered:")
    print(locality_features.head())
    
    # 4. Bridge / Join with Rental Data
    print("Merging features into rental dataset...")
    
    # We join on City + Locality
    # Note: 'Area Locality' in rental vs 'Locality' in customer
    merged_df = df_rental.merge(
        locality_features, 
        left_on=['City', 'Area Locality'], 
        right_on=['City', 'Locality'], 
        how='left'
    )
    
    # Fill missing values (for localities with no customer data) with 0
    new_cols = ['Locality_Search_Volume', 'Locality_Contacts', 'Locality_Views', 'View_to_Contact_Ratio', 'High_Demand_Flag']
    merged_df[new_cols] = merged_df[new_cols].fillna(0)
    
    # Drop redundant join column
    if 'Locality' in merged_df.columns:
        merged_df = merged_df.drop('Locality', axis=1)
        
    print(f"Merged Data Shape: {merged_df.shape}")
    
    # 5. Save Enhanced Dataset
    output_dir = 'output/final_round'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'rental_data_with_customer_behavior.csv')
    
    merged_df.to_csv(output_path, index=False)
    print(f"✅ Success! Integrated data saved to: {output_path}")
    print("Ready for training with 'train_demand_model_v2.py'")

if __name__ == "__main__":
    integrate_customer_data()
