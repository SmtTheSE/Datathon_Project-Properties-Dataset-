import pandas as pd
import numpy as np
from datetime import datetime
import os

def prepare_gap_data():
    """
    Prepare data for the demand-supply gap identification model.
    This function processes the raw rental data to create features for identifying 
    areas where demand exceeds supply or vice versa.
    """
    print("Loading and preparing data for demand-supply gap identification...")
    
    # Load the dataset
    data_path = '../House_Rent_10M_balanced_40cities.csv'
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        print("Please ensure the dataset is in the correct location.")
        return
    
    # Read the dataset
    df = pd.read_csv(data_path, low_memory=False)
    
    # Convert 'Posted On' to datetime (handling mixed formats)
    df['Posted On'] = pd.to_datetime(df['Posted On'], infer_datetime_format=True, errors='coerce')
    
    # Check for any rows where date conversion failed
    invalid_dates = df['Posted On'].isna().sum()
    if invalid_dates > 0:
        print(f"Warning: {invalid_dates} rows had invalid dates and will be dropped")
        df = df.dropna(subset=['Posted On'])
    
    # Extract temporal features
    df['Year'] = df['Posted On'].dt.year
    df['Month'] = df['Posted On'].dt.month
    df['Day'] = df['Posted On'].dt.day
    df['DayOfWeek'] = df['Posted On'].dt.dayofweek
    df['WeekOfYear'] = df['Posted On'].dt.isocalendar().week
    df['Quarter'] = df['Posted On'].dt.quarter
    
    # Create supply and demand metrics
    # Supply is measured by number of listings
    supply_df = df.groupby(['City', 'Area Locality', 'BHK', 'Year', 'Month']).size().reset_index(name='Supply')
    
    # Add back other features
    temp_df = df.groupby(['City', 'Area Locality', 'BHK', 'Year', 'Month']).agg({
        'Rent': ['mean', 'median', 'std']
    }).reset_index()
    
    temp_df.columns = ['City', 'Area Locality', 'BHK', 'Year', 'Month', 'Avg_Rent', 'Median_Rent', 'Std_Rent']
    
    # Merge supply and rent features
    supply_df = supply_df.merge(temp_df, on=['City', 'Area Locality', 'BHK', 'Year', 'Month'])
    
    # Calculate demand proxy (this would ideally come from a separate demand source)
    # For now, we'll use a smoothed version of supply as a demand proxy
    supply_df['Demand_Proxy'] = supply_df.groupby(['City', 'Area Locality', 'BHK'])['Supply'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    
    # Calculate gap metric
    supply_df['Gap'] = supply_df['Demand_Proxy'] - supply_df['Supply']
    supply_df['Gap_Ratio'] = supply_df['Gap'] / (supply_df['Demand_Proxy'] + 1e-8)  # Adding small epsilon to avoid division by zero
    
    # Location encoding features
    city_tier_mapping = {
        'Mumbai': 'Tier1', 'Delhi': 'Tier1', 'Bangalore': 'Tier1', 'Hyderabad': 'Tier1', 
        'Chennai': 'Tier1', 'Kolkata': 'Tier1', 'Pune': 'Tier2', 'Ahmedabad': 'Tier2',
        'Jaipur': 'Tier2', 'Surat': 'Tier2', 'Kanpur': 'Tier2', 'Lucknow': 'Tier2',
        'Nagpur': 'Tier2', 'Indore': 'Tier2', 'Bhopal': 'Tier2', 'Patna': 'Tier2',
        'Vadodara': 'Tier2', 'Ghaziabad': 'Tier2', 'Visakhapatnam': 'Tier2', 'Agra': 'Tier2',
        'Thane': 'Tier2', 'Kalyan': 'Tier2', 'Varanasi': 'Tier2', 'Raipur': 'Tier2',
        'Aurangabad': 'Tier2', 'Meerut': 'Tier2', 'Jabalpur': 'Tier2', 'Vijaywada': 'Tier2',
        'Gwalior': 'Tier2', 'Madurai': 'Tier2', 'Amritsar': 'Tier2', 'Allahabad': 'Tier2',
        'Coimbatore': 'Tier2', 'Ranchi': 'Tier2', 'Jalandhar': 'Tier2', 'Tiruchirappalli': 'Tier2'
    }
    
    supply_df['City_Tier'] = supply_df['City'].map(city_tier_mapping)
    
    # Regional encoding
    city_region_mapping = {
        'Mumbai': 'West', 'Delhi': 'North', 'Bangalore': 'South', 'Hyderabad': 'South',
        'Chennai': 'South', 'Kolkata': 'East', 'Pune': 'West', 'Ahmedabad': 'West',
        'Jaipur': 'North', 'Surat': 'West', 'Kanpur': 'North', 'Lucknow': 'North',
        'Nagpur': 'West', 'Indore': 'West', 'Bhopal': 'West', 'Patna': 'East',
        'Vadodara': 'West', 'Ghaziabad': 'North', 'Visakhapatnam': 'East', 'Agra': 'North',
        'Thane': 'West', 'Kalyan': 'West', 'Varanasi': 'North', 'Raipur': 'West',
        'Aurangabad': 'West', 'Meerut': 'North', 'Jabalpur': 'West', 'Vijaywada': 'South',
        'Gwalior': 'North', 'Madurai': 'South', 'Amritsar': 'North', 'Allahabad': 'North',
        'Coimbatore': 'South', 'Ranchi': 'East', 'Jalandhar': 'North', 'Tiruchirappalli': 'South'
    }
    
    supply_df['Region'] = supply_df['City'].map(city_region_mapping)
    
    # Save processed data
    output_path = '/tmp/gap_analysis_data.csv'
    supply_df.to_csv(output_path, index=False)
    print(f"Data preparation completed. Saved to {output_path}")
    print(f"Processed data shape: {supply_df.shape}")
    print("\nSample of processed data:")
    print(supply_df.head())

if __name__ == "__main__":
    prepare_gap_data()