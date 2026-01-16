import pandas as pd
import numpy as np
from datetime import datetime

# 1. Configuration & Tiers
# T1 = Major Metros, T2 = Growing Cities
TIER_1 = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad']
HOLIDAYS_2022 = [
    '2022-04-10', # Ram Navami
    '2022-04-14', # Ambedkar Jayanti
    '2022-04-15', # Good Friday
    '2022-05-03', # Eid-ul-Fitr
    '2022-05-16', # Buddha Purnima
    '2022-07-10'  # Eid-ul-Adha
]

# Regional groupings for additional demographic splits
SOUTH_CITIES = ['Bangalore', 'Chennai', 'Hyderabad', 'Kochi', 'Coimbatore', 'Mysore']
WEST_CITIES = ['Mumbai', 'Pune', 'Ahmedabad', 'Surat', 'Indore']
NORTH_CITIES = ['Delhi', 'Chandigarh', 'Jaipur', 'Lucknow', 'Kanpur']
EAST_CITIES = ['Kolkata', 'Bhubaneswar', 'Patna', 'Ranchi']

def prepare_data(csv_path):
    print("Loading data...")
    # Loading only necessary columns to save memory
    df = pd.read_csv(csv_path, usecols=['Posted On', 'City'])
    df['Posted On'] = pd.to_datetime(df['Posted On'])
    
    print("Aggregating demand (Listing Volume)...")
    # Demand = Daily Count of Listings per City
    demand_df = df.groupby(['City', 'Posted On']).size().reset_index(name='Demand')
    
    # Ensure all date-city combinations exist (filling gaps with 0 if any)
    cities = demand_df['City'].unique()
    dates = pd.date_range(start=demand_df['Posted On'].min(), end=demand_df['Posted On'].max())
    idx = pd.MultiIndex.from_product([cities, dates], names=['City', 'Posted On'])
    demand_df = demand_df.set_index(['City', 'Posted On']).reindex(idx, fill_value=0).reset_index()
    
    print("Feature Engineering...")
    # A. Temporal Features
    demand_df['DayOfWeek'] = demand_df['Posted On'].dt.dayofweek
    demand_df['IsWeekend'] = demand_df['DayOfWeek'].isin([5, 6]).astype(int)
    demand_df['DayOfMonth'] = demand_df['Posted On'].dt.day
    demand_df['Month'] = demand_df['Posted On'].dt.month
    demand_df['Quarter'] = demand_df['Posted On'].dt.quarter
    demand_df['WeekOfYear'] = demand_df['Posted On'].dt.isocalendar().week
    
    # B. Real-World Signals
    demand_df['IsTier1'] = demand_df['City'].isin(TIER_1).astype(int)
    demand_df['IsMonsoon'] = (demand_df['Posted On'].dt.month >= 6).astype(int)
    demand_df['IsHoliday'] = demand_df['Posted On'].dt.strftime('%Y-%m-%d').isin(HOLIDAYS_2022).astype(int)
    
    # C. Demographic/Regional Features
    demand_df['IsSouth'] = demand_df['City'].isin(SOUTH_CITIES).astype(int)
    demand_df['IsWest'] = demand_df['City'].isin(WEST_CITIES).astype(int)
    demand_df['IsNorth'] = demand_df['City'].isin(NORTH_CITIES).astype(int)
    demand_df['IsEast'] = demand_df['City'].isin(EAST_CITIES).astype(int)
    
    # D. Historical Features (Lags & Rolling)
    demand_df = demand_df.sort_values(['City', 'Posted On'])
    # Lags (Shifted by 1 for causality - predicting tomorrow)
    for lag in [1, 7, 14]:
        demand_df[f'Lag_{lag}'] = demand_df.groupby('City')['Demand'].shift(lag)
    
    # Rolling Windows
    demand_df['Rolling_Mean_7'] = demand_df.groupby('City')['Demand'].transform(lambda x: x.shift(1).rolling(window=7).mean())
    demand_df['Rolling_Mean_14'] = demand_df.groupby('City')['Demand'].transform(lambda x: x.shift(1).rolling(window=14).mean())
    demand_df['Rolling_Std_7'] = demand_df.groupby('City')['Demand'].transform(lambda x: x.shift(1).rolling(window=7).std())
    
    # E. Growth indicators
    demand_df['Growth_Rate_7'] = demand_df.groupby('City')['Demand'].pct_change(periods=7)
    
    # F. Drop rows with NaN from lags
    demand_df = demand_df.dropna()
    
    # 2. Chronological Split (Real-World)
    print("Splitting data...")
    train_df = demand_df[demand_df['Posted On'] < '2022-07-01']
    test_df = demand_df[demand_df['Posted On'] >= '2022-07-01']
    
    return train_df, test_df

if __name__ == "__main__":
    CSV_PATH = "/Users/sittminthar/Desktop/Datathon_Project-Properties-Dataset-/10 Million House Rent Data of 40 cities/House_Rent_10M_balanced_40cities.csv"
    train, test = prepare_data(CSV_PATH)
    
    # Save mixed combined data for the detailed training script which splits it internally
    combined = pd.concat([train, test])
    combined.to_csv("/tmp/enhanced_demand_forecasting_data.csv", index=False)
    
    # Also save separate files just in case
    train.to_csv("/tmp/train_demand.csv", index=False)
    test.to_csv("/tmp/test_demand.csv", index=False)
    print(f"Prepared. Train shape: {train.shape}, Test shape: {test.shape}")