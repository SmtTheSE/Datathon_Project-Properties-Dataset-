"""
Enhanced Data Integration Module for Rental Market Intelligence Platform
Integrates external datasets to improve model robustness and accuracy
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os
import requests
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class DataCollector:
    def __init__(self):
        self.data_sources = {
            'rental_data': [
                'House_Rent_10M_balanced_40cities.csv'  # Original dataset
            ],
            'economic_indicators': [
                'economic_indicators.csv',
                'covid_impact_data.csv'
            ],
            'demographic_data': [
                'population_growth.csv',
                'migration_patterns.csv'
            ],
            'infrastructure_data': [
                'metro_expansion.csv',
                'commercial_development.csv'
            ]
        }
    
    def collect_rental_data(self):
        """Collect rental data from multiple sources"""
        # Check if the large dataset exists, if not create a small sample
        if os.path.exists(self.data_sources['rental_data'][0]):
            print(f"Loading full dataset: {self.data_sources['rental_data'][0]}")
            df = pd.read_csv(self.data_sources['rental_data'][0], low_memory=False, nrows=10000)  # Limit rows for demo
            df['data_source'] = 'original'
            return df
        else:
            print(f"Full dataset not found: {self.data_sources['rental_data'][0]}")
            print("Creating a small sample dataset for demonstration...")
            return self._create_sample_rental_data()
    
    def _create_sample_rental_data(self):
        """Create a small sample rental dataset for demonstration"""
        n_samples = 10000
        
        # Generate sample cities
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 
                  'Pune', 'Ahmedabad', 'Jaipur', 'Surat', 'Kanpur', 'Lucknow']
        
        # Generate sample data
        data = {
            'Property ID': [f'Th{i:08d}' for i in range(n_samples)],
            'Posted On': pd.date_range(start='2020-01-01', end='2022-12-31', freq='D').repeat(3)[:n_samples].tolist(),
            'City': np.random.choice(cities, n_samples),
            'Area Locality': [f'Area_{i%100}' for i in range(n_samples)],
            'BHK': np.random.choice([1, 2, 3, 4], n_samples),
            'Rent': np.random.normal(25000, 10000, n_samples).clip(5000, 100000),
            'Size': np.random.normal(1000, 300, n_samples).clip(300, 3000),
            'Furnishing Status': np.random.choice(['Furnished', 'Semi-Furnished', 'Unfurnished'], n_samples),
            'Tenant Preferred': np.random.choice(['Bachelors', 'Family', 'All'], n_samples),
            'Bathroom': np.random.choice([1, 2, 3, 4], n_samples),
        }
        
        df = pd.DataFrame(data)
        df['data_source'] = 'sample'
        return df
    
    def collect_economic_data(self):
        """Collect economic indicators"""
        economic_data = []
        
        for source in self.data_sources['economic_indicators']:
            if os.path.exists(source):
                df = pd.read_csv(source)
                economic_data.append(df)
        
        # Combine economic data sources
        if economic_data:
            combined_economic = pd.concat(economic_data, ignore_index=True)
        else:
            # Create mock data if sources don't exist
            combined_economic = self._create_mock_economic_data()
        
        return combined_economic
    
    def _create_mock_economic_data(self):
        """Create mock economic data for demonstration"""
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        n_months = len(dates)
        
        return pd.DataFrame({
            'date': dates,
            'inflation_rate': np.random.uniform(2, 8, n_months),
            'interest_rate': np.random.uniform(5, 12, n_months),
            'employment_rate': np.random.uniform(70, 90, n_months),
            'gdp_growth': np.random.uniform(-2, 8, n_months)
        })
    
    def collect_external_data(self):
        """Collect external data sources"""
        # This would integrate real external APIs
        external_data = {
            'covid_impact': self.fetch_covid_impact_data(),
            'interest_rates': self.fetch_interest_rates(),
            'employment_data': self.fetch_employment_data(),
            'inflation_data': self.fetch_inflation_data()
        }
        return external_data
    
    def fetch_covid_impact_data(self):
        """Fetch COVID impact data"""
        # Create mock data for demonstration
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        n_months = len(dates)
        
        return pd.DataFrame({
            'date': dates,
            'covid_impact_score': np.concatenate([
                np.random.uniform(0.7, 1.0, 6),  # High impact in early 2020
                np.random.uniform(0.3, 0.7, 12), # Moderate impact mid-2020
                np.random.uniform(0.1, 0.4, 12), # Low impact 2021
                np.random.uniform(0.0, 0.3, 6)   # Very low impact 2022
            ])
        })
    
    def fetch_interest_rates(self):
        """Fetch interest rate data"""
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        n_months = len(dates)
        
        # Simulate interest rate changes over time
        base_rate = 7.5
        rates = []
        for i in range(n_months):
            # Simulate some trend and seasonal variation
            rate = base_rate + np.sin(i/6) * 0.5 + np.random.normal(0, 0.2)
            rates.append(max(4.0, min(15.0, rate)))  # Keep within reasonable bounds
        
        return pd.DataFrame({
            'date': dates,
            'interest_rate': rates
        })
    
    def fetch_employment_data(self):
        """Fetch employment data"""
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        n_months = len(dates)
        
        # Simulate employment rate changes over time
        base_rate = 80.0
        rates = []
        for i in range(n_months):
            # Simulate recovery from COVID impact
            if i < 6:  # Early COVID period
                rate = base_rate - 8 + np.random.normal(0, 1)
            elif i < 18:  # Recovery period
                rate = base_rate - 8 + (i/3) + np.random.normal(0, 1)
            else:  # Stable period
                rate = base_rate + np.random.normal(0, 0.5)
            
            rates.append(max(60.0, min(95.0, rate)))  # Keep within reasonable bounds
        
        return pd.DataFrame({
            'date': dates,
            'employment_rate': rates
        })
    
    def fetch_inflation_data(self):
        """Fetch inflation data"""
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        n_months = len(dates)
        
        # Simulate inflation changes over time
        base_rate = 5.0
        rates = []
        for i in range(n_months):
            # Simulate some trend and seasonal variation
            rate = base_rate + np.sin(i/12) * 1.5 + np.random.normal(0, 0.5)
            rates.append(max(1.0, min(12.0, rate)))  # Keep within reasonable bounds
        
        return pd.DataFrame({
            'date': dates,
            'inflation_rate': rates
        })


class DataIntegrator:
    def __init__(self):
        self.scaler = StandardScaler()
        self.collector = DataCollector()
    
    def standardize_features(self, df):
        """Standardize features across datasets"""
        # Ensure consistent column names
        column_mapping = {
            'posted_on': 'Posted On',
            'city_name': 'City',
            'area': 'Area Locality',
            'bhk_type': 'BHK',
            'monthly_rent': 'Rent'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Standardize categorical values
        if 'City' in df.columns:
            df['City'] = df['City'].str.title()
        if 'Area Locality' in df.columns:
            df['Area Locality'] = df['Area Locality'].str.title()
        
        # Convert date column to datetime - fixing the format
        if 'Posted On' in df.columns:
            df['Posted On'] = pd.to_datetime(df['Posted On'], errors='coerce', format='%Y-%m-%d')
        
        return df
    
    def integrate_datasets(self):
        """Integrate multiple data sources"""
        print("Collecting rental data...")
        rental_data = self.collector.collect_rental_data()
        print(f"Rental data shape: {rental_data.shape}")
        
        print("Collecting economic data...")
        economic_data = self.collector.collect_economic_data()
        print(f"Economic data shape: {economic_data.shape}")
        
        print("Collecting external data...")
        external_data = self.collector.collect_external_data()
        print("External data collected")
        
        # Standardize rental data
        rental_data = self.standardize_features(rental_data)
        
        # Convert date columns for merging
        economic_data['YearMonth'] = pd.to_datetime(economic_data['date']).dt.to_period('M')
        rental_data['YearMonth'] = pd.to_datetime(rental_data['Posted On']).dt.to_period('M')
        
        # Merge rental data with economic indicators
        print("Merging rental and economic data...")
        integrated_data = rental_data.merge(
            economic_data[['YearMonth', 'inflation_rate', 'interest_rate', 'employment_rate', 'gdp_growth']],
            on='YearMonth',
            how='left'
        )
        
        # Add external data
        covid_data = external_data['covid_impact']
        covid_data['YearMonth'] = pd.to_datetime(covid_data['date']).dt.to_period('M')
        
        print("Merging with COVID impact data...")
        integrated_data = integrated_data.merge(
            covid_data[['YearMonth', 'covid_impact_score']],
            on='YearMonth',
            how='left'
        )
        
        # Fill missing values
        integrated_data['covid_impact_score'] = integrated_data['covid_impact_score'].fillna(0)
        integrated_data['inflation_rate'] = integrated_data['inflation_rate'].fillna(method='ffill').fillna(method='bfill')
        integrated_data['interest_rate'] = integrated_data['interest_rate'].fillna(method='ffill').fillna(method='bfill')
        integrated_data['employment_rate'] = integrated_data['employment_rate'].fillna(method='ffill').fillna(method='bfill')
        integrated_data['gdp_growth'] = integrated_data['gdp_growth'].fillna(method='ffill').fillna(method='bfill')
        
        print(f"Final integrated data shape: {integrated_data.shape}")
        return integrated_data


class EnhancedFeatureEngineer:
    def __init__(self):
        self.city_tiers = {
            'Mumbai': 'Tier1', 'Delhi': 'Tier1', 'Bangalore': 'Tier1', 'Hyderabad': 'Tier1',
            'Chennai': 'Tier1', 'Kolkata': 'Tier1', 'Pune': 'Tier1', 'Ahmedabad': 'Tier1',
            'Jaipur': 'Tier2', 'Surat': 'Tier2', 'Kanpur': 'Tier2', 'Lucknow': 'Tier2',
            'Nagpur': 'Tier2', 'Indore': 'Tier2', 'Bhopal': 'Tier2', 'Patna': 'Tier2',
            'Vadodara': 'Tier2', 'Ghaziabad': 'Tier2', 'Visakhapatnam': 'Tier2', 'Agra': 'Tier2',
            'Thane': 'Tier2', 'Kalyan': 'Tier2', 'Varanasi': 'Tier2', 'Raipur': 'Tier2',
            'Ludhiana': 'Tier2', 'Kochi': 'Tier2', 'Coimbatore': 'Tier2', 'Nashik': 'Tier2',
            'Vijayawada': 'Tier2', 'Mangalore': 'Tier2', 'Mysore': 'Tier2', 'Jodhpur': 'Tier2',
            'Madurai': 'Tier2', 'Chandigarh': 'Tier2', 'Faridabad': 'Tier2', 'Noida': 'Tier2',
            'Bhubaneswar': 'Tier2', 'Kurnool': 'Tier2', 'Gulbarga': 'Tier2', 'Ajmer': 'Tier2'
        }
        
        self.regions = {
            'Mumbai': 'West', 'Pune': 'West', 'Ahmedabad': 'West', 'Surat': 'West', 'Nashik': 'West',
            'Thane': 'West', 'Kalyan': 'West', 'Vadodara': 'West', 'Nagpur': 'West', 'Kochi': 'West',
            'Coimbatore': 'West', 'Mangalore': 'West', 'Mysore': 'West', 'Madurai': 'West',
            'Delhi': 'North', 'Kanpur': 'North', 'Lucknow': 'North', 'Ghaziabad': 'North',
            'Chandigarh': 'North', 'Faridabad': 'North', 'Noida': 'North', 'Jaipur': 'North',
            'Ludhiana': 'North', 'Jodhpur': 'North', 'Varanasi': 'North', 'Agra': 'North',
            'Bangalore': 'South', 'Chennai': 'South', 'Hyderabad': 'South', 'Visakhapatnam': 'South',
            'Vijayawada': 'South', 'Kochi': 'South', 'Coimbatore': 'South', 'Mangalore': 'South',
            'Mysore': 'South', 'Madurai': 'South', 'Kurnool': 'South', 'Gulbarga': 'South',
            'Kolkata': 'East', 'Bhubaneswar': 'East', 'Patna': 'East', 'Raipur': 'East'
        }
    
    def create_enhanced_features(self, df):
        """Create enhanced features with external data"""
        print("Creating enhanced features...")
        
        # Extract temporal features
        df['Year'] = df['Posted On'].dt.year
        df['Month'] = df['Posted On'].dt.month
        df['Day'] = df['Posted On'].dt.day
        df['DayOfWeek'] = df['Posted On'].dt.dayofweek
        df['WeekOfYear'] = df['Posted On'].dt.isocalendar().week
        df['Quarter'] = df['Posted On'].dt.quarter
        
        # Geographic features
        df['City_Tier'] = df['City'].map(self.city_tiers).fillna('Tier3')
        df['Region'] = df['City'].map(self.regions).fillna('Other')
        
        # Create comparative features
        df['Rent_ZScore'] = df.groupby('City')['Rent'].transform(
            lambda x: (x - x.mean()) / (x.std() + 1e-8)  # Add small value to avoid division by zero
        )
        
        # Economic sensitivity metrics
        df['Economic_Sensitivity'] = (
            df['inflation_rate'] * 0.3 + 
            df['interest_rate'] * 0.4 + 
            (100 - df['employment_rate']) * 0.3
        )
        
        # Create seasonal features
        df['IsMonsoon'] = df['Month'].isin([6, 7, 8, 9]).astype(int)
        df['IsSummer'] = df['Month'].isin([3, 4, 5]).astype(int)
        df['IsWinter'] = df['Month'].isin([11, 12, 1, 2]).astype(int)
        
        # Supply-demand indicators
        df['Rent_to_Income_Ratio'] = df['Rent'] / (df['employment_rate'] * 100 + 1)
        
        # Create lagged features for time series
        df = df.sort_values(['City', 'Posted On'])
        df['Rent_Lag_7'] = df.groupby('City')['Rent'].transform(lambda x: x.shift(7))
        df['Rent_Rolling_Mean_14'] = df.groupby('City')['Rent'].transform(
            lambda x: x.rolling(window=14, min_periods=7).mean()
        )
        
        # Economic impact features
        df['Covid_Impact_Adjusted'] = df['Rent'] * (1 - df['covid_impact_score'] * 0.2)
        
        # Cross-regional trend indicators
        df['Regional_Avg_Rent'] = df.groupby(['Region', 'BHK'])['Rent'].transform('mean')
        df['City_to_Regional_Ratio'] = df['Rent'] / (df['Regional_Avg_Rent'] + 1)
        
        # External shock resilience measures
        df['Volatility_Score'] = df.groupby('City')['Rent'].transform(
            lambda x: x.rolling(window=30, min_periods=15).std()
        )
        df['Volatility_Score'] = df['Volatility_Score'].fillna(0)
        
        # Additional economic features
        df['Economic_Health_Score'] = (
            df['employment_rate'] * 0.4 + 
            (100 - df['inflation_rate']) * 0.3 + 
            (15 - df['interest_rate']) * 0.3
        )
        
        # Fill any remaining NaN values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(method='ffill').fillna(method='bfill')
        
        print(f"Feature engineering completed. Data shape: {df.shape}")
        return df


def main():
    """Main function to demonstrate the enhanced data integration"""
    print("Starting enhanced data integration process...")
    
    try:
        # Initialize integrator
        integrator = DataIntegrator()
        
        # Integrate datasets
        integrated_data = integrator.integrate_datasets()
        
        if integrated_data.empty:
            raise ValueError("Integrated data is empty")
            
        # Initialize feature engineer
        feature_engineer = EnhancedFeatureEngineer()
        
        # Create enhanced features
        enhanced_data = feature_engineer.create_enhanced_features(integrated_data)
        
        if enhanced_data.empty:
            raise ValueError("Enhanced data is empty after feature engineering")
            
    except Exception as e:
        print(f"Error in data integration process: {str(e)}")
        raise
        
    # Save the enhanced dataset
    output_dir = os.path.join(os.getcwd(), 'output')
    try:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'enhanced_rental_data_with_external_factors.csv')
        
        enhanced_data.to_csv(output_path, index=False)
        print(f"Enhanced dataset successfully saved to {output_path}")
        print(f"Final dataset shape: {enhanced_data.shape}")
        print(f"Number of unique cities: {enhanced_data['City'].nunique()}")
        print(f"Date range: {enhanced_data['Posted On'].min()} to {enhanced_data['Posted On'].max()}")
    except PermissionError:
        print(f"Permission denied when saving file: {output_path}")
        raise
    except IOError as e:
        print(f"I/O error occurred while saving file: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error when saving dataset: {str(e)}")
        raise
        
    # Final summary
    print(f"Final dataset shape: {enhanced_data.shape}")
    print(f"Columns: {list(enhanced_data.columns)}")
    
    # Save to temp for Product 1
    temp_demand_path = '/tmp/enhanced_demand_forecasting_data.csv'
    try:
        # For demand forecasting, we need to aggregate by city and date
        demand_data = enhanced_data.groupby(['City', 'Posted On']).size().reset_index(name='Demand_Count')
        
        # Merge with economic factors
        economic_cols = ['inflation_rate', 'interest_rate', 'employment_rate', 'covid_impact_score', 'gdp_growth', 'Economic_Health_Score']
        economic_data = enhanced_data[['City', 'Posted On'] + economic_cols].drop_duplicates()
        demand_data = demand_data.merge(economic_data, on=['City', 'Posted On'], how='left')
        
        # Add temporal features
        demand_data['Posted On'] = pd.to_datetime(demand_data['Posted On'])
        demand_data['Year'] = demand_data['Posted On'].dt.year
        demand_data['Month'] = demand_data['Posted On'].dt.month
        
        # Add seasonal features
        demand_data['Month_Sin'] = np.sin(2 * np.pi * demand_data['Month'] / 12)
        demand_data['Month_Cos'] = np.cos(2 * np.pi * demand_data['Month'] / 12)
        
        demand_data.to_csv(temp_demand_path, index=False)
        print(f"Demand forecasting data saved to {temp_demand_path}")
    except Exception as e:
        print(f"Error saving demand forecasting data: {str(e)}")
        raise

    # Save to temp for Product 2
    temp_gap_path = '/tmp/enhanced_gap_analysis_data.csv'
    try:
        # For gap analysis, we aggregate by city, area, BHK, and time
        gap_data = enhanced_data.copy()
        
        # Create gap-related features
        gap_data['Avg_Rent'] = gap_data.groupby(['City', 'Area Locality', 'BHK'])['Rent'].transform('mean')
        gap_data['Std_Rent'] = gap_data.groupby(['City', 'Area Locality', 'BHK'])['Rent'].transform('std').fillna(0)
        
        # Calculate supply as count of listings per city-area-BHK combination
        supply_counts = gap_data.groupby(['City', 'Area Locality', 'BHK']).size().reset_index(name='Supply')
        gap_data = gap_data.merge(supply_counts, on=['City', 'Area Locality', 'BHK'], how='left')
        
        # Calculate demand as a function of rent, economic factors, and city popularity
        # Higher rent and better economic conditions increase demand
        gap_data['Demand_Factor'] = (
            (gap_data['Avg_Rent'] / gap_data['Avg_Rent'].mean()) * 0.3 +
            (gap_data['employment_rate'] / 100) * 0.3 +
            (gap_data['Economic_Health_Score'] / gap_data['Economic_Health_Score'].max()) * 0.2 +
            np.random.normal(1.0, 0.1, size=len(gap_data)) * 0.2  # Add some randomness
        ).clip(lower=0.1)
        
        gap_data['Demand_Count'] = gap_data['Supply'] * gap_data['Demand_Factor']
        
        # Calculate gap metrics - this time with more realistic variation
        gap_data['Gap_Ratio'] = (gap_data['Demand_Count'] - gap_data['Supply']) / (gap_data['Supply'] + 1)
        
        gap_data.to_csv(temp_gap_path, index=False)
        print(f"Gap analysis data saved to {temp_gap_path}")
    except Exception as e:
        print(f"Error saving gap analysis data: {str(e)}")
        raise
    
    return enhanced_data


if __name__ == "__main__":
    enhanced_data = main()