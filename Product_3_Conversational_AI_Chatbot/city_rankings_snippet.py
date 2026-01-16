    def get_city_rankings(self, top=True, count=5):
        """
        Get top or bottom cities ranked by demand
        
        Args:
            top: If True, return top cities. If False, return bottom cities.
            count: Number of cities to return (default 5)
        """
        try:
            # Get all cities
            response = requests.get(f"{self.demand_api_url}/cities", timeout=5)
            if response.status_code != 200:
                return {"error": "Failed to fetch cities"}
            
            cities = response.json().get('cities', [])
            
            # Get demand for each city
            city_demands = []
            for city in cities:
                try:
                    pred_response = requests.post(
                        f"{self.demand_api_url}/predict",
                        json={
                            "city": city,
                            "date": "2024-08-15",
                            "economic_factors": {
                                "inflation_rate": 6.5,
                                "interest_rate": 7.0,
                                "employment_rate": 85.0
                            }
                        },
                        timeout=5
                    )
                    
                    if pred_response.status_code == 200:
                        demand = pred_response.json().get('predicted_demand', 0)
                        city_demands.append({
                            'city': city,
                            'demand': demand,
                            'monthly_demand': demand * 30
                        })
                except:
                    continue
            
            # Sort by demand
            city_demands.sort(key=lambda x: x['demand'], reverse=top)
            
            return {
                'cities': city_demands[:count],
                'is_top': top
            }
            
        except Exception as e:
            return {"error": str(e)}


# ADD THIS TO generate_response method, AFTER the 'historical' intent handler:

        elif intent == 'top_cities':
            if 'error' in data:
                return "I apologize, but I couldn't fetch the city rankings at this moment. Please try again."
            
            cities = data.get('cities', [])
            if not cities:
                return "I couldn't retrieve city data at this moment."
            
            response = "Based on current market analysis, here are the **top 5 cities** with the highest rental demand:\n\n"
            
            for i, city_data in enumerate(cities, 1):
                city = city_data['city']
                demand = city_data['demand']
                monthly = city_data['monthly_demand']
                response += f"{i}. **{city}**: {demand:,} properties/day (~{monthly:,}/month)\n"
            
            response += "\nThese cities show strong market activity and are excellent for investment opportunities."
            return response
        
        elif intent == 'bottom_cities':
            if 'error' in data:
                return "I apologize, but I couldn't fetch the city rankings at this moment. Please try again."
            
            cities = data.get('cities', [])
            if not cities:
                return "I couldn't retrieve city data at this moment."
            
            response = "Based on current market analysis, here are the **bottom 5 cities** with the lowest rental demand:\n\n"
            
            for i, city_data in enumerate(cities, 1):
                city = city_data['city']
                demand = city_data['demand']
                monthly = city_data['monthly_demand']
                response += f"{i}. **{city}**: {demand:,} properties/day (~{monthly:,}/month)\n"
            
            response += "\nThese cities show lower market activity. Investors should exercise caution and conduct thorough due diligence before investing in these markets."
            return response
