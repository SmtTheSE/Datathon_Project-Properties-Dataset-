"""
Fast Data Loader Module using Pre-Aggregated JSON Files
Loads historical data instantly from small summary files
"""

import json
import numpy as np
import os
from datetime import datetime, timedelta
from functools import lru_cache

class HistoricalDataLoader:
    """
    Loads pre-aggregated historical data from JSON files for instant access
    """
    
    def __init__(self, 
                 monthly_summary_path=None,
                 locality_summary_path=None):
        """Initialize with paths to summary files"""
        # Determine absolute path to data files (in same directory as this script)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        if monthly_summary_path is None:
            monthly_summary_path = os.path.join(base_dir, 'monthly_summary.json')
            
        if locality_summary_path is None:
            locality_summary_path = os.path.join(base_dir, 'locality_summary.json')
            
        self.monthly_summary_path = monthly_summary_path
        self.locality_summary_path = locality_summary_path
        self._monthly_data = None
        self._locality_data = None
        
    def _load_monthly_data(self):
        """Load monthly summary data (called once and cached)"""
        if self._monthly_data is None:
            try:
                with open(self.monthly_summary_path, 'r') as f:
                    self._monthly_data = json.load(f)
                print(f"Loaded monthly data for {len(self._monthly_data)} cities")
            except FileNotFoundError:
                print(f"Warning: {self.monthly_summary_path} not found")
                self._monthly_data = {}
        return self._monthly_data
    
    def _load_locality_data(self):
        """Load locality summary data (called once and cached)"""
        if self._locality_data is None:
            try:
                with open(self.locality_summary_path, 'r') as f:
                    self._locality_data = json.load(f)
                print(f"Loaded locality data for {len(self._locality_data)} cities")
            except FileNotFoundError:
                print(f"Warning: {self.locality_summary_path} not found")
                self._locality_data = {}
        return self._locality_data
    
    @lru_cache(maxsize=128)
    def get_historical_demand_by_city(self, city, months=12):
        """
        Get historical demand data for a specific city
        
        Args:
            city: City name
            months: Number of months of historical data
            
        Returns:
            List of dictionaries with month, demand, and year
        """
        monthly_data = self._load_monthly_data()
        
        if city not in monthly_data:
            print(f"No data found for city: {city}")
            return []
        
        city_data = monthly_data[city]
        
        # Convert period strings to datetime and sort
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        result = []
        for period_str, count in city_data.items():
            # Period format: "2024-01"
            year, month = period_str.split('-')
            result.append({
                'month': month_names[int(month) - 1],
                'demand': count,
                'year': int(year)
            })
        
        # Sort by date (year, month)
        result.sort(key=lambda x: (x['year'], month_names.index(x['month'])))
        
        # Return last N months
        return result[-months:]
    
    def get_locality_gaps(self, city, top_n=10, sort_by='demand'):
        """
        Get locality-level gap data for a specific city
        
        Args:
            city: City name
            top_n: Number of top localities to return
            sort_by: How to sort results - 'demand' (default), 'gap_high' (most oversupplied), 
                     'gap_low' (most undersupplied), 'gap_abs' (most extreme gaps)
            
        Returns:
            List of dictionaries with locality, gap, and demand
        """
        locality_data = self._load_locality_data()
        
        if city not in locality_data:
            print(f"No locality data found for city: {city}")
            return []
        
        city_localities = locality_data[city]
        
        # Calculate statistics
        result = []
        counts = [loc_data['count'] for loc_data in city_localities.values()]
        overall_mean = np.mean(counts) if counts else 1
        
        for locality, loc_data in city_localities.items():
            count = loc_data['count']
            
            # Calculate gap as normalized deviation from mean
            # CORRECT DEFINITION:
            # Positive gap (count > mean) = HIGH demand (undersupplied) - good for investors
            # Negative gap (count < mean) = LOW demand (oversupplied) - good for renters
            gap = (count - overall_mean) / overall_mean if overall_mean > 0 else 0
            gap = np.clip(gap, -1, 1)  # Clip to [-1, 1]
            
            result.append({
                'locality': locality,
                'gap': float(gap),
                'demand': int(count)
            })
        
        # Sort based on sort_by parameter
        if sort_by == 'gap_high':
            # Highest positive gap = Most undersupplied (high demand) - good for INVESTORS
            result.sort(key=lambda x: x['gap'], reverse=True)
        elif sort_by == 'gap_low':
            # Lowest negative gap = Most oversupplied (low demand) - good for RENTERS
            result.sort(key=lambda x: x['gap'])
        elif sort_by == 'gap_abs':
            # Most extreme gaps (highest absolute value)
            result.sort(key=lambda x: abs(x['gap']), reverse=True)
        else:  # Default: sort by demand
            result.sort(key=lambda x: x['demand'], reverse=True)
        
        return result[:top_n]

# Global instance
_data_loader = None

def get_data_loader():
    """Get or create the global data loader instance"""
    global _data_loader
    if _data_loader is None:
        _data_loader = HistoricalDataLoader()
    return _data_loader
