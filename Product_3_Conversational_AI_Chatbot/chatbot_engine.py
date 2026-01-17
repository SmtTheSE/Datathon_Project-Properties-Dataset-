"""
Conversational AI Chatbot for Rental Property Insights
Product 3: Natural Language Interface to Demand Forecasting & Gap Analysis

This chatbot understands natural language queries like:
- "What's the demand in Mumbai for August 2024?"
- "Show me gap analysis for Bandra area"
- "I want to know rental demand in Delhi"
- "Which localities in Bangalore have high demand?"

It extracts intent, entities, and calls the appropriate APIs.
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import requests

class RentalPropertyChatbot:
    """Intelligent chatbot for rental property insights"""
    
    def __init__(self, demand_api_url="http://localhost:5001", gap_api_url="http://localhost:5002"):
        self.demand_api_url = demand_api_url
        self.gap_api_url = gap_api_url
        
        # Conversational state tracking
        self.last_city = None
        self.last_intent = None
        self.last_trend = None  # Track last historical trend for context
        self.conversation_history = []
        self.user_name = None
        
        # Load city list
        self.cities = self._load_cities()
        
        # Intent patterns with advanced question-based reasoning
        self.intent_patterns = {
            'greeting': [
                r'^(hi|hello|hey|greetings|hola|namaste)\b',
                r'good\s+(morning|afternoon|evening|day)',
                r'^(yo|sup|wassup)\b',
            ],
            'thank_you': [
                r'(thank|thanks|thx|appreciate)',
                r'grateful',
                r'you.*(?:helped|great|awesome|amazing)',
            ],
            'goodbye': [
                r'(bye|goodbye|see you|farewell|later)',
                r'have.*(?:good|nice).*day',
                r'take care',
            ],
            'demand_forecast': [
                r'demand.*(?:in|for|at)\s+(\w+)',
                r'forecast.*(?:in|for|at)\s+(\w+)',
                r'rental.*demand.*(\w+)',
                r'how.*many.*(?:in|at)\s+(\w+)',
                r'predict.*demand.*(\w+)',
                r'what.*demand.*(\w+)',
                # Enhanced natural language patterns
                r'(\w+).*demand',  # "mumbai demand"
                r'demand.*(\w+)',  # "demand mumbai"
                r'how[\'s]*\s+(?:is|are)?\s*(\w+)\s+(?:doing|performing)',  # "how's mumbai doing", "how is bangalore doing"
                r'how.*(?:is|are).*(\w+).*(?:doing|market|performing)',  # "how's mumbai doing"
                r'(\w+).*rental.*market',  # "mumbai rental market"
                r'tell.*(?:me|us).*(?:about|demand).*(\w+)',  # "tell me about demand in mumbai"
                r'know.*demand.*(\w+)',  # "i want to know demand in mumbai"
                r'what.*about.*(\w+)',  # "what about bangalore"
                r'(?:and|how).*about.*(\w+)',  # "and what about bangalore", "how about bangalore"
            ],
            'gap_analysis': [
                r'gap.*(?:in|for|at)\s+(\w+)',
                r'supply.*demand.*(\w+)',
                r'opportunity.*(?:in|at)\s+(\w+)',
                r'invest.*(?:in|at)\s+(\w+)',
                r'which.*(?:area|locality).*(\w+)',
                r'best.*(?:area|locality).*(\w+)',
                # Enhanced natural language patterns
                r'should.*invest.*(\w+)',  # "should i invest in delhi"
                r'(?:is|are).*(\w+).*good.*invest',  # "is bangalore good for investment"
                r'(?:where|which).*(?:should|can).*invest.*(\w+)',  # "where should I invest in mumbai"
                r'(\w+).*(?:investment|invest).*(?:opportunit|area)',  # "mumbai investment opportunities"
                r'(?:show|find|get).*(?:opportunit|invest).*(\w+)',  # "show me opportunities in delhi"
                r'(?:best|top|good).*(?:area|localit|place).*(?:invest|buy).*(\w+)',  # "best areas to invest in bangalore"
                r'(\w+).*(?:gap|supply|demand).*analys',  # "mumbai gap analysis"
                r'(?:what|tell|show).*(?:about|me).*gap.*analys',  # "what about gap analysis"
                r'gap.*analys.*(\w+)',  # "gap analysis for delhi"
                r'(?:demand|supply).*gap.*(\w+)',  # "demand supply gap in mumbai"
                r'analyz.*gap.*(\w+)',  # "analyze gap in delhi"
                r'where.*(?:invest|buy).*(\w+)',  # "where to invest in mumbai"
                r'(\w+).*opportunities',  # "mumbai opportunities"
                r'(\w+).*investment',  # "delhi investment"
                # Undersupplied area patterns
                r'undersuppl.*(?:area|localit).*(\w+)',  # "undersupplied areas in mumbai"
                r'(?:are|any).*undersuppl.*(\w+)',  # "are there undersupplied areas in delhi"
                r'show.*undersuppl.*(\w+)',  # "show me undersupplied areas"
                r'which.*undersuppl.*(\w+)',  # "which areas are undersupplied"
                r'high.*demand.*(?:area|localit).*(\w+)',  # "high demand areas in bangalore"
                # BHK and rent-based patterns (NEW)
                r'\d+\s*bhk.*(?:in|at|for)\s+(\w+)',  # "2 BHK in Mumbai"
                r'(?:with|having)\s*\d+\s*bhk',  # "with 2 BHK"
                r'bhk.*\d+.*(\w+)',  # "BHK 2 in Delhi"
                r'(?:rent|rental).*\d+.*(\w+)',  # "rent 35000 in Mumbai"
                r'average.*rent.*\d+',  # "average rent 35000"
                r'\d+k?\s*(?:rent|rental)',  # "35k rent" or "35000 rent"
                r'(?:area|locality).*\d+',  # "Area 191"
            ],
            'low_gap': [
                r'oversuppl.*(?:area|localit).*(\w+)',  # "oversupplied areas in mumbai"
                r'(?:show|find|get).*oversuppl.*(\w+)',  # "show me oversupplied areas"
                r'(?:which|what).*oversuppl.*(\w+)',  # "which areas are oversupplied"
                r'low.*gap.*(\w+)',  # "low gap areas in delhi"
                r'renter.*market.*(\w+)',  # "renter's market in bangalore"
            ],
            'top_cities': [
                r'(?:top|best|highest).*(?:5|five|10|ten)?.*cit',  # "top 5 cities"
                r'(?:which|what).*(?:best|top).*cit.*(?:invest|demand)',  # "which are the best cities"
                r'(?:rank|list).*cit.*(?:demand|invest)',  # "rank cities by demand"
                r'(?:show|give).*(?:top|best).*cit',  # "show me top cities"
                r'cit.*(?:highest|most).*demand',  # "cities with highest demand"
            ],
            'bottom_cities': [
                r'(?:worst|lowest|bottom).*(?:5|five|10|ten)?.*cit',  # "worst 5 cities"
                r'(?:which|what).*(?:worst|lowest|bad).*cit',  # "which are the worst cities"
                r'cit.*(?:lowest|least).*demand',  # "cities with lowest demand"
                r'(?:avoid|bad).*cit.*invest',  # "cities to avoid for investment"
            ],
            'top_city': [
                r'(?:top|best|highest|number.*1|#1).*(?:1|one|single).*cit',  # "top 1 city"
                r'(?:which|what).*(?:is|the).*(?:best|top).*(?:single|one|1).*cit',  # "which is the best city"
                r'(?:best|top).*cit.*(?:overall|absolute)',  # "best city overall"
                r'(?:single|one).*(?:best|top).*cit',  # "single best city"
            ],
            'bottom_city': [
                r'(?:worst|lowest|bottom|last).*(?:1|one|single).*cit',  # "worst 1 city"
                r'(?:which|what).*(?:is|the).*(?:worst|lowest).*(?:single|one|1).*cit',  # "which is the worst city"
                r'(?:worst|lowest).*cit.*(?:overall|absolute)',  # "worst city overall"
                r'(?:single|one).*(?:worst|lowest).*cit',  # "single worst city"
                r'(?:show|give|tell).*(?:the|me)?.*cit.*(?:with|has).*(?:lowest|worst).*demand',  # "show the city with lowest demand"
                r'(?:which|what).*cit.*(?:has|with).*(?:lowest|worst|least).*demand',  # "which city has the lowest demand"
            ],
            'low_demand': [
                r'low.*demand.*(\w+)',  # "low demand in mumbai"
                r'least.*demand.*(\w+)',  # "least demand in delhi"
                r'(?:which|what).*(?:area|localit).*low.*demand.*(\w+)',  # "which areas have low demand"
                r'(?:cheap|affordable|budget).*(?:area|localit).*(\w+)',  # "cheap areas in mumbai"
                r'where.*(?:cheap|affordable|budget).*(\w+)',  # "where is it cheap in delhi"
                r'(\w+).*low.*demand',  # "mumbai low demand"
            ],
            'low_gap': [
                r'low.*gap.*(\w+)',  # "low gap in mumbai"
                r'oversuppl.*(\w+)',  # "oversupplied areas in delhi" or "what about oversupplied area"
                r'(?:which|what).*(?:area|localit).*oversuppl.*(\w+)',  # "which areas are oversupplied"
                r'(?:which|what).*(?:area|localit).*low.*gap.*(\w+)',  # "which areas have low gap"
                r'renter.*market.*(\w+)',  # "renter's market in mumbai"
                r'buyer.*market.*(\w+)',  # "buyer's market in delhi"
                r'(?:show|find).*oversuppl.*(\w+)',  # "show me oversupplied areas"
                r'(?:any|are there).*oversuppl.*(\w+)',  # "are there oversupplied areas"
            ],
            'historical': [
                r'historical.*(?:in|for)\s+(\w+)',
                r'past.*data.*(\w+)',
                r'trend.*(?:in|for)\s+(\w+)',
                r'show.*history.*(\w+)',
            ],
            'help': [
                r'help',
                r'what.*can.*do',
                r'how.*work',
                r'guide',
                r'assist',
            ],
            'tenant_quality': [
                r'tenant.*quality.*(\w+)',
                r'risk.*score.*(\w+)',
                r'invest.*grade.*(\w+)',
                r'quality.*tenant.*(\w+)',
                r'churn.*risk.*(\w+)',
                r'financial.*health.*(\w+)',
                r'safe.*invest.*(\w+)',
                r'how.*safe.*(\w+)',
                r'tenant.*profile.*(\w+)',
                r'quality.*adjusted.*(\w+)',
            ]
        }
        
        # Follow-up patterns for context-aware reasoning
        self.follow_up_patterns = {
            'demand_forecast': [
                r'^(?:and|what about|how about).*(?:demand|forecast)',
                r'^(?:show|tell).*(?:demand|forecast)',
                r'^demand',
                r'^(?:and|what|how)\s+about',  # "and what about", "what about", "how about"
            ],
            'gap_analysis': [
                r'^(?:and|what about|how about).*(?:gap|invest|opportunit)',
                r'^(?:show|tell).*(?:gap|invest|opportunit)',
                r'^(?:where|which).*(?:invest|area|localit)',
                r'^gap',
                r'^(?:and|what).*(?:the)?\s*gap',  # "and the gap", "what about the gap"
            ],
            'historical': [
                r'^(?:and|what about|how about).*(?:historical|trend|past)',
                r'^(?:show|tell).*(?:historical|trend|past|history)',
                r'^(?:historical|trend)',
            ]
        }
        
        # Month mapping
        self.months = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12,
        }
    
    def _load_cities(self) -> List[str]:
        """Load list of supported cities"""
        try:
            response = requests.get(f"{self.demand_api_url}/cities", timeout=5)
            if response.status_code == 200:
                return response.json().get('cities', [])
        except:
            pass
        
        # Fallback city list
        return [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai',
            'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Surat'
        ]
    
    def detect_intent(self, query: str) -> Tuple[str, float]:
        """Detect user intent from query with advanced question-based reasoning"""
        query_lower = query.lower().strip()
        
        best_intent = 'unknown'
        best_score = 0.0
        
        # PRIORITY CHECK 1: If query mentions BHK or rent, it's likely gap analysis
        # This must come FIRST to prevent demand_forecast from capturing these queries
        has_bhk = re.search(r'\d+\s*bhk', query_lower)
        # More specific rent check: number must be close to 'rent' keyword (within ~20 chars)
        has_rent = (
            re.search(r'(?:rent|rental)[:\s]{0,5}(\d{4,}|\d+k)', query_lower) or  # "rent 35000" or "rent: 35k"
            re.search(r'(\d{4,}|\d+k)[:\s]{0,5}(?:rent|rental)', query_lower) or  # "35000 rent" or "35k rent"
            re.search(r'average[:\s]+(?:rent|rental)', query_lower)  # "average rent"
        )
        
        if has_bhk or has_rent:
            # If BHK or rent is mentioned, prioritize gap analysis
            return 'gap_analysis', 0.95
        
        # PRIORITY CHECK 1.5: "Quality Adjusted" should always be tenant quality
        if 'quality' in query_lower and 'adjusted' in query_lower:
            return 'tenant_quality', 0.98
            
        # PRIORITY CHECK 1.6: Investment Safety / Risk / Grade -> Tenant Quality
        # Explicit patterns that override Gap Analysis "invest" keywords
        # Matches: "safe to invest", "investment grade", "risk in investment"
        if re.search(r'(?:safe|risk|grade|rating).*invest', query_lower) or \
           re.search(r'invest.*(?:safe|risk|grade|rating)', query_lower) or \
           re.search(r'is.*(?:palakkad|mumbai|pune|delhi|bangalore).*safe', query_lower): # specific safety question
            return 'tenant_quality', 0.98
        
        # PRIORITY CHECK 2: Check for specific "low demand" or "oversupplied" queries
        # These should take precedence over general "demand" patterns
        
        # Check for city rankings (no specific city mentioned)
        # Check for single city first (top 1, worst 1)
        if re.search(r'(?:top|best|highest).*(?:1|one|single).*cit', query_lower):
            return 'top_city', 0.95
        if re.search(r'(?:worst|lowest|bottom).*(?:1|one|single).*cit', query_lower):
            return 'bottom_city', 0.95
        
        # Check for queries asking about 'the city' with lowest/worst demand
        if re.search(r'(?:the|which|what).*cit.*(?:lowest|worst|least).*demand', query_lower):
            return 'bottom_city', 0.95
        if re.search(r'(?:show|tell|give).*cit.*(?:lowest|worst).*demand', query_lower):
            return 'bottom_city', 0.95
        
        # Check for queries asking about 'the city' with highest/best demand
        if re.search(r'(?:the|which|what).*cit.*(?:highest|best|most).*demand', query_lower):
            return 'top_city', 0.95
        if re.search(r'(?:show|tell|give).*cit.*(?:highest|best|most).*demand', query_lower):
            return 'top_city', 0.95
        
        # Then check for multiple cities (top 5, worst 5)
        if re.search(r'(?:top|best|highest|worst|lowest|bottom).*cit', query_lower):
            if re.search(r'(?:worst|lowest|bottom)', query_lower):
                return 'bottom_cities', 0.95
            else:
                return 'top_cities', 0.95
        
        if 'gap' in query_lower and 'analys' in query_lower:
            # Explicit gap analysis query
            return 'gap_analysis', 0.95
        
        if 'low' in query_lower and 'demand' in query_lower:
            for pattern in self.intent_patterns.get('low_demand', []):
                if re.search(pattern, query_lower):
                    return 'low_demand', 0.95
        
        if 'oversuppl' in query_lower or ('low' in query_lower and 'gap' in query_lower):
            for pattern in self.intent_patterns.get('low_gap', []):
                if re.search(pattern, query_lower):
                    return 'low_gap', 0.95
        
        # Early check for specific keywords to avoid generic pattern matching
        if 'oversuppl' in query_lower:
            # Prioritize low_gap intent for oversupplied queries
            for pattern in self.intent_patterns.get('low_gap', []):
                if re.search(pattern, query_lower):
                    return 'low_gap', 0.9
        
        if 'undersuppl' in query_lower:
            # Prioritize gap_analysis intent for undersupplied queries
            for pattern in self.intent_patterns.get('gap_analysis', []):
                if re.search(pattern, query_lower):
                    return 'gap_analysis', 0.9
        
        # First, check for follow-up patterns if we have context
        if self.last_intent and self.last_city:
            for intent, patterns in self.follow_up_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, query_lower):
                        # High score for follow-up patterns
                        return intent, 0.9
        
        # Check main intent patterns
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    # Scoring based on pattern specificity
                    score = 0.8 if intent != 'help' else 0.6
                    if score > best_score:
                        best_intent = intent
                        best_score = score
        
        return best_intent, best_score
    
    def extract_city(self, query: str) -> Optional[str]:
        """Extract city name from query with smart matching"""
        query_lower = query.lower().strip()
        
        # Direct city match
        for city in self.cities:
            if city.lower() in query_lower:
                return city
        
        # Check for common variations
        city_variations = {
            'bombay': 'Mumbai',
            'calcutta': 'Kolkata',
            'madras': 'Chennai',
            'bangalore': 'Bangalore',
            'bengaluru': 'Bangalore',
        }
        
        for variation, city in city_variations.items():
            if variation in query_lower:
                return city
        
        # SMART FALLBACK: If no known city found, look for "in [City]" pattern
        # This allows testing new cities like "Palakkad" even if not in the initial list
        match = re.search(r'(?:in|for|at|to)\s+([A-Z][a-z]+(?:-[A-Z][a-z]+)?)', query)
        if match:
            potential_city = match.group(1)
            # Filter out common intent words to avoid false positives
            ignored_words = ['August', 'September', 'October', 'Mumbai', 'Delhi', 'Year', 'Month', 'Demand', 'Quality']
            if potential_city not in ignored_words:
                 return potential_city
                 
        return None
    
    def extract_date(self, query: str) -> Optional[Tuple[int, int]]:
        """Extract date (year, month) from query"""
        query_lower = query.lower()
        
        # Extract year
        year_match = re.search(r'20\d{2}', query)
        year = int(year_match.group()) if year_match else datetime.now().year
        
        # Extract month
        month = None
        for month_name, month_num in self.months.items():
            if month_name in query_lower:
                month = month_num
                break
        
        if not month:
            month = datetime.now().month
        
        return (year, month)
    
    def extract_locality(self, query: str) -> Optional[str]:
        """Extract locality/area from query"""
        # Question words that should not be extracted as localities
        question_words = ['Which', 'What', 'Where', 'How', 'Show', 'Tell', 'Find']
        
        # Look for patterns like "in Bandra", "at Andheri", "Area 191"
        patterns = [
            r'(Area\s+\d+)',  # "Area 191" - check this first as it's most specific
            r'(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',  # "in Bandra", "at Andheri West"
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:area|locality)',  # "Bandra area", "Andheri West locality"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                potential_locality = match.group(1)
                # Don't extract question words or city names as localities
                if potential_locality not in question_words and potential_locality not in self.cities:
                    return potential_locality
        
        return None
    
    def extract_bhk(self, query: str) -> Optional[str]:
        """Extract BHK from query"""
        match = re.search(r'(\d)\s*bhk', query.lower())
        if match:
            return match.group(1)
        return None
    
    def extract_name(self, query: str) -> Optional[str]:
        """Extract user name from introduction"""
        query_lower = query.lower()
        
        # Patterns to match name introductions
        patterns = [
            r'(?:my name is|i am|i\'m|this is|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z][a-z]+)?)',
            r'(?:my name is|i am|i\'m|this is|call me)\s+([A-Z][a-z]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Capitalize properly
                return ' '.join(word.capitalize() for word in name.split())
        
        return None
    
    def extract_rent(self, query: str) -> Optional[int]:
        """Extract rent amount from query - enhanced to handle more formats"""
        # Look for patterns like "35000", "35k", "35,000", "rent: 35000", "average rent 35000"
        patterns = [
            r'(?:rent|rental)[:\s]+([\d,]+)k',  # "rent: 35k" or "rent 35k"
            r'(?:rent|rental)[:\s]+([\d,]{4,})',  # "rent: 35000" or "rent 35,000"
            r'average.*(?:rent|rental).*([\d,]+)k',  # "average rent 35k"
            r'average.*(?:rent|rental).*([\d,]{4,})',  # "average rent 35000"
            r'([\d,]+)k\s*(?:rent|rental)',  # "35k rent"
            r'([\d,]{4,})\s*(?:rent|rental)',  # "35000 rent"
            r'([\d,]+)k(?!\s*bhk)',  # "35k" (but not "2k bhk")
            r'([\d,]{4,})(?!\s*bhk)',  # "35000" (but not "2000 bhk")
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                value = match.group(1).replace(',', '')
                # Check if it has 'k' suffix in the original query around this match
                if 'k' in pattern or (match.end() < len(query) and query[match.end():match.end()+1].lower() == 'k'):
                    value = value + '000'
                try:
                    rent_value = int(value)
                    # Sanity check: rent should be between 5000 and 500000
                    if 5000 <= rent_value <= 500000:
                        return rent_value
                except ValueError:
                    continue
        
        return None
    
    def extract_economic_factors(self, query: str) -> Optional[Dict[str, float]]:
        """
        Extract economic factors from query.
        
        Supports patterns like:
        - "with 8% inflation"
        - "inflation at 6.5%"
        - "interest rate 7%"
        - "7% interest"
        - "85% employment"
        - "employment at 80%"
        
        Returns:
            Dict with extracted economic factors, or None if none found
        """
        query_lower = query.lower()
        economic_factors = {}
        
        # Extract inflation rate - must have "inflation" keyword nearby
        inflation_patterns = [
            r'(\d+\.?\d*)%?\s*inflation\b',  # "8% inflation", "8 inflation"
            r'\binflation\b.*?(\d+\.?\d*)%?',  # "inflation 8%", "inflation at 8"
        ]
        
        for pattern in inflation_patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    value = float(match.group(1))
                    # Sanity check: inflation typically 0-20%
                    if 0 <= value <= 20:
                        economic_factors['inflation_rate'] = value
                        break
                except ValueError:
                    continue
        
        # Extract interest rate - must have "interest" keyword nearby
        interest_patterns = [
            r'(\d+\.?\d*)%?\s*interest\s+rate\b',  # "7% interest rate", "7 interest rate"
            r'\binterest\s+rate\b.*?(\d+\.?\d*)%?',  # "interest rate 7%", "interest rate at 7"
            r'(\d+\.?\d*)%?\s*interest\b(?!\s*rate)',  # "7% interest" (but not "interest rate")
            r'\binterest\b(?!\s*rate).*?(\d+\.?\d*)%?',  # "interest 7%" (but not "interest rate")
        ]
        
        for pattern in interest_patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    value = float(match.group(1))
                    # Sanity check: interest rate typically 0-20%
                    if 0 <= value <= 20:
                        economic_factors['interest_rate'] = value
                        break
                except ValueError:
                    continue
        
        # Extract employment rate - must have "employment" keyword nearby
        employment_patterns = [
            r'(\d+\.?\d*)%?\s*employment\b',  # "85% employment", "85 employment"
            r'\bemployment\b.*?(\d+\.?\d*)%?',  # "employment 85%", "employment at 85"
        ]
        
        for pattern in employment_patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    value = float(match.group(1))
                    # Sanity check: employment rate typically 50-100%
                    if 50 <= value <= 100:
                        economic_factors['employment_rate'] = value
                        break
                except ValueError:
                    continue
        
        # Return None if no factors found, otherwise return the dict
        return economic_factors if economic_factors else None
    
    def call_demand_api(self, city: str, year: int, month: int, economic_factors: Dict[str, float] = None) -> Dict:
        """
        Call demand forecasting API with optional economic factors.
        
        Args:
            city: City name
            year: Year for prediction
            month: Month for prediction
            economic_factors: Optional dict with inflation_rate, interest_rate, employment_rate
        
        Returns:
            API response dict
        """
        try:
            # Use provided economic factors or defaults
            if economic_factors is None:
                economic_factors = {}
            
            # Build economic factors with defaults for missing values
            api_economic_factors = {
                "inflation_rate": economic_factors.get('inflation_rate', 6.5),
                "interest_rate": economic_factors.get('interest_rate', 7.0),
                "employment_rate": economic_factors.get('employment_rate', 85.0)
            }
            
            response = requests.post(
                f"{self.demand_api_url}/predict",
                json={
                    "city": city,
                    "date": f"{year}-{month:02d}-15",
                    "economic_factors": api_economic_factors
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "API request failed"}
        except Exception as e:
            return {"error": str(e)}
    
    def call_gap_api(self, city: str, locality: str = None, bhk: str = "2", rent: int = 30000, sort_by: str = 'demand') -> Dict:
        """Call gap analysis API"""
        try:
            # If no locality specified, get comprehensive locality data
            # Query 50 localities to get a good mix of oversupplied and undersupplied areas
            if not locality:
                response = requests.get(
                    f"{self.gap_api_url}/historical/{city}?top_n=50&sort_by={sort_by}",  # Use sort_by parameter
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": "API request failed"}
            
            # Specific locality analysis
            response = requests.post(
                f"{self.gap_api_url}/predict",
                json={
                    "city": city,
                    "area_locality": locality,
                    "bhk": bhk,
                    "avg_rent": rent,
                    "economic_indicators": {
                        "inflation_rate": 6.0,
                        "interest_rate": 7.0,
                        "employment_rate": 85.0,
                        "covid_impact_score": 0.1,
                        "economic_health_score": 0.85
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "API request failed"}
        except Exception as e:
            return {"error": str(e)}
    
    
    def call_enhanced_demand_api(self, city: str, year: int, month: int, economic_factors: Dict[str, float] = None) -> Dict:
        """
        Call ENHANCED demand forecasting API (Product 1 + Tenant Risk).
        """
        try:
            # Use provided economic factors or defaults
            if economic_factors is None:
                economic_factors = {}
            
            # Build economic factors with defaults for missing values
            api_economic_factors = {
                "inflation_rate": economic_factors.get('inflation_rate', 6.5),
                "interest_rate": economic_factors.get('interest_rate', 7.0),
                "employment_rate": economic_factors.get('employment_rate', 85.0)
            }
            
            response = requests.post(
                f"{self.demand_api_url}/predict/enhanced",
                json={
                    "city": city,
                    "date": f"{year}-{month:02d}-15",
                    "economic_factors": api_economic_factors,
                    "include_tenant_quality": True
                },
                timeout=12
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Enhanced API request failed"}
        except Exception as e:
            return {"error": str(e)}

    def call_historical_api(self, city: str, months: int = 12) -> Dict:
        """Call historical data API"""
        try:
            response = requests.get(
                f"{self.demand_api_url}/historical/{city}?months={months}",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "API request failed"}
        except Exception as e:
            return {"error": str(e)}
    

    def get_city_rankings(self, top=True, count=5):
        """
        Get top or bottom cities ranked by ACTUAL HISTORICAL demand
        Uses real data from 10M dataset (Apr-Jul 2022) for credible insights
        """
        try:
            # Get all cities
            response = requests.get(f"{self.demand_api_url}/cities", timeout=5)
            if response.status_code != 200:
                return {"error": "Failed to fetch cities"}
            
            cities = response.json().get('cities', [])
            city_demands = []
            
            # Get HISTORICAL data for each city (real data from 10M dataset)
            for city in cities:
                try:
                    hist_response = requests.get(
                        f"{self.demand_api_url}/historical/{city}?months=4",  # Get all 4 months
                        timeout=5
                    )
                    
                    if hist_response.status_code == 200:
                        hist_data = hist_response.json().get('historical_data', [])
                        if hist_data:
                            # Calculate total and average demand from historical data
                            total_demand = sum(month['demand'] for month in hist_data)
                            avg_monthly = total_demand / len(hist_data)
                            avg_daily = avg_monthly / 30
                            
                            city_demands.append({
                                'city': city,
                                'demand': int(avg_daily),  # Daily average
                                'monthly_demand': int(avg_monthly),
                                'total_demand': total_demand,
                                'data_source': 'historical'
                            })
                except Exception as e:
                    # Skip cities with errors
                    continue
            
            # Sort by actual historical demand
            city_demands.sort(key=lambda x: x['demand'], reverse=top)
            
            return {
                'cities': city_demands[:count],
                'is_top': top,
                'data_source': 'historical',  # Indicate we're using real data
                'period': 'Apr-Jul 2022'  # Data period
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_response(self, intent: str, data: Dict, query: str) -> str:
        """Generate natural language response"""
        
        if intent == 'demand_forecast':
            if 'error' in data:
                return f"""I apologize, but I'm currently unable to connect to the demand forecasting service. This typically indicates that the API server needs to be started. Based on historical patterns, {self.last_city or 'most major cities'} generally experience strong rental demand. Please try again in a moment, or feel free to ask me about other market insights."""
            
            city = data.get('city', 'the city')
            demand = data.get('predicted_demand', 0)
            confidence = data.get('confidence', 'medium')
            month = data.get('month', '')
            year = data.get('year', '')
            extracted_factors = data.get('_extracted_economic_factors')
            
            # Convert daily to monthly
            monthly_demand = demand * 30
            
            # Build professional response with date and economic context
            response = "Based on my analysis "
            
            # Mention economic factors if custom ones were provided
            if extracted_factors:
                factors_mentioned = []
                if 'inflation_rate' in extracted_factors:
                    factors_mentioned.append(f"**{extracted_factors['inflation_rate']}% inflation**")
                if 'interest_rate' in extracted_factors:
                    factors_mentioned.append(f"**{extracted_factors['interest_rate']}% interest rate**")
                if 'employment_rate' in extracted_factors:
                    factors_mentioned.append(f"**{extracted_factors['employment_rate']}% employment**")
                
                if factors_mentioned:
                    response += f"with {', '.join(factors_mentioned[:-1]) + (' and ' if len(factors_mentioned) > 1 else '') + factors_mentioned[-1] if factors_mentioned else ''}, "
            else:
                response += "of historical patterns and economic indicators, "
            
            # Add date context
            if month and year:
                try:
                    month_name = list(self.months.keys())[list(self.months.values()).index(month)]
                    response += f"the rental demand in **{city}** for **{month_name.capitalize()} {year}** "
                except (ValueError, IndexError):
                    response += f"the rental demand in **{city}** "
            else:
                response += f"the rental demand in **{city}** "
            
            response += f"is approximately **{demand:,} properties per day**, which translates to about **{monthly_demand:,} properties per month**. "
            
            # Add trend context if we have recent historical data
            if self.last_trend is not None and self.last_city == city:
                if self.last_trend < -20:  # Significant decline
                    if monthly_demand > 50000:
                        response += f"This forecast suggests a **recovery** from the recent {abs(self.last_trend):.1f}% decline, likely driven by improved economic conditions or seasonal factors. "
                    else:
                        response += f"Note: Recent historical data showed a {abs(self.last_trend):.1f}% decline. This forecast reflects continuation of that trend. "
                elif self.last_trend > 20:  # Significant growth
                    response += f"This aligns with the recent growth trend of +{self.last_trend:.1f}%. "
            
            # Add confidence context
            if confidence == 'high':
                response += f"The model has high confidence in this prediction. "
            else:
                response += f"This is an estimate based on available trends. "
            
            # Add demand context
            if monthly_demand > 50000:
                response += f"{city} shows strong rental market activity."
            
            return response

        elif intent == 'tenant_quality':
            if 'error' in data:
                 return f"I apologize, but I couldn't access the enhanced reporting system. {data.get('error')}"
            
            city = data.get('city', 'the city')
            base_demand = data.get('base_demand', {}).get('predicted_demand', 0)
            quality_data = data.get('tenant_quality_analysis', {})
            recommendation = data.get('investment_recommendation', {})
            quality_adjusted = data.get('quality_adjusted_demand', 0)
            
            # Extract key metrics
            grade_a = quality_data.get('high_quality_pct', 0) * 100
            grade_b = quality_data.get('medium_quality_pct', 0) * 100
            grade_d = quality_data.get('high_risk_pct', 0) * 100
            risk_score = quality_data.get('average_default_risk', 0) * 100
            
            rating = recommendation.get('rating', 'UNKNOWN').replace('_', ' ')
            confidence = recommendation.get('confidence', 0) * 100
            reasoning = recommendation.get('reasoning', '')
            
            response = f"**📊 Analysis for {city}: Tenant Quality & Investment Risk**\n\n"
            
            # Show economic context if available (User Request)
            # Check both API return data OR the locally extracted factors
            extracted_factors = data.get('economic_factors_used') or data.get('_extracted_economic_factors')
            
            if extracted_factors:
                factors_str = []
                if 'inflation_rate' in extracted_factors:
                    factors_str.append(f"Inflation: {extracted_factors['inflation_rate']}%")
                if 'interest_rate' in extracted_factors:
                    factors_str.append(f"Interest: {extracted_factors['interest_rate']}%")
                
                if factors_str:
                    response += f"⚠️ *Scenario: High Economic Stress ({', '.join(factors_str)})*\n\n"
            
            response += f"Based on our enhanced analysis of tenant financial profiles:\n\n"
            
            response += f"**🏆 Investment Rating: {rating}** ({confidence:.0f}% Confidence)\n"
            response += f"*{reasoning}*\n\n"
            
            response += f"**👥 Tenant Quality Breakdown:**\n"
            response += f"- **Grade A (Premium):** {grade_a:.1f}% - Excellent financial health\n"
            response += f"- **Grade B (Reliable):** {grade_b:.1f}% - Steady payers\n"
            response += f"- **Grade D (Risky):** {grade_d:.1f}% - High churn risk\n\n"
            
            response += f"**📉 Risk Assessment:**\n"
            response += f"- Average Default Risk: **{risk_score:.1f}%**\n"
            response += f"- Quality-Adjusted Demand: **{quality_adjusted:.0f}** (vs {base_demand:.0f} total)\n\n"
            
            response += f"**💡 Recommendation:**\n"
            if rating == "STRONG BUY":
                response += f"Highly recommended. The majority of tenants ({grade_a+grade_b:.0f}%) are financially stable, ensuring consistent rental income."
            elif rating == "BUY":
                response += "Good investment. Tenant quality is solid, but perform standard thorough checks."
            elif rating == "HOLD":
                response += "Proceed with caution. A significant portion of demand comes from high-risk tenants."
            else:
                response += "High risk market. Tenant default probability is elevated."
            
            return response
        
        elif intent == 'gap_analysis':
            if 'error' in data:
                return f"""I apologize, but I'm currently unable to access the gap analysis service. This could indicate that the API needs to be restarted. In the meantime, I'd be happy to help you with demand forecasting or historical trend analysis."""
            
            # Check if it's locality list or specific analysis
            if 'locality_data' in data:
                city = data.get('city', 'the city')
                localities = data.get('locality_data', [])
                
                # Calculate overall gap metrics
                gaps = [loc.get('gap', 0) for loc in localities]
                avg_gap = sum(gaps) / len(gaps) if gaps else 0
                
                # Determine severity
                if abs(avg_gap) > 0.3:
                    severity = "high"
                elif abs(avg_gap) > 0.1:
                    severity = "medium"
                else:
                    severity = "low"
                
                # Determine market status
                if avg_gap > 0.1:
                    market_status = "undersupplied with high demand"
                    investor_note = "excellent for investors"
                elif avg_gap < -0.1:
                    market_status = "oversupplied, representing a renter's market"
                    investor_note = "favorable for renters and buyers"
                else:
                    market_status = "balanced"
                    investor_note = "presenting moderate opportunities"
                
                # Build professional response
                response = f"Based on gap analysis for **{city}**, here are the **top undersupplied areas** (best for investment):\n\n"
                
                # Build area descriptions with clear formatting
                for i, loc in enumerate(localities[:5], 1):
                    locality = loc.get('locality', 'Unknown')
                    demand = loc.get('demand', 0)
                    gap = loc.get('gap', 0)
                    response += f"{i}. **{locality}**: {demand:,} listings, Gap: {gap:+.2f}\n"
                
                # Add market summary
                response += f"\n**Market Summary**: Average gap ratio of {avg_gap:+.3f} ({severity} severity)"
                
                # Add interpretation
                if avg_gap > 0.1:
                    response += f"\n\nThese areas show strong demand exceeding supply. Properties typically rent quickly with lower vacancy rates. Excellent investment opportunities."
                elif avg_gap < -0.1:
                    response += f"\n\nThese areas show supply exceeding demand. Higher vacancy rates and competitive pricing are typical. Favorable for renters."
                else:
                    response += f"\n\nThe market shows balanced supply-demand conditions with moderate competition."
                
                return response
            
            else:
                city = data.get('city', 'the city')
                locality = data.get('area_locality', 'the area')
                gap_ratio = data.get('predicted_gap_ratio', 0)
                severity = data.get('gap_severity', 'unknown')
                status = data.get('demand_supply_status', 'unknown')
                
                response = f"Analysis for {locality} in {city}: Gap ratio of {gap_ratio:.3f} ({severity} severity). "
                
                if status == 'demand_exceeds_supply':
                    response += f"Market status: Demand exceeds supply (undersupplied). Properties typically rent quickly with lower vacancy rates."
                else:
                    response += f"Market status: Supply exceeds demand (oversupplied). Higher competition among landlords with increased vacancy risk."
                
                return response
        
        elif intent == 'low_demand':
            if 'error' in data:
                return f"""Hmm, I'm having trouble accessing the demand data right now. 🤔

But I can help you find low-demand areas once the API is back up!
"""
            
            # Get all localities and find lowest demand
            if 'locality_data' in data:
                city = data.get('city', 'the city')
                localities = data.get('locality_data', [])
                
                # Sort by demand (ascending) to get lowest
                sorted_localities = sorted(localities, key=lambda x: x.get('demand', 999999))[:5]
                
                # Check if there are any truly low-demand areas (negative gap = oversupplied)
                has_low_demand = any(loc.get('gap', 1) < 0 for loc in sorted_localities)
                
                # Build area descriptions
                area_descriptions = []
                for loc in sorted_localities:
                    locality = loc.get('locality', 'Unknown')
                    demand = loc.get('demand', 0)
                    gap = loc.get('gap', 0)
                    area_descriptions.append(f"{locality} ({demand:,} listings, gap: {gap:+.2f})")
                
                if has_low_demand:
                    response = f"Lowest demand areas in {city}: {', '.join(area_descriptions[:-1])}, and {area_descriptions[-1]}. Negative gap values indicate supply exceeds demand. Investors should be aware that these areas may experience lower rental yields and higher vacancy risk."
                else:
                    response = f"All areas in {city} show high demand. Areas with relatively lower competition include {', '.join(area_descriptions[:-1])}, and {area_descriptions[-1]}. The market remains competitive overall."
                
                return response
            else:
                return "I need more data to show you low-demand areas. Try asking about a specific city!"
        
        elif intent == 'low_gap':
            if 'error' in data:
                return f"""Hmm, I'm having trouble accessing the gap analysis data right now. 🤔

But I can help you find oversupplied areas once the API is back up!
"""
            
            # Get all localities - API already sorted by gap_low (most oversupplied first)
            if 'locality_data' in data:
                city = data.get('city', 'the city')
                localities = data.get('locality_data', [])
                
                # API already sorted correctly - just take first 5
                top_oversupplied = localities[:5]
                
                # Check if there are truly oversupplied areas (negative gap)
                has_oversupply = any(loc.get('gap', 1) < 0 for loc in top_oversupplied)
                
                # Build area descriptions
                area_descriptions = []
                for loc in top_oversupplied:
                    locality = loc.get('locality', 'Unknown')
                    demand = loc.get('demand', 0)
                    gap = loc.get('gap', 0)
                    area_descriptions.append(f"{locality} ({demand:,} listings, gap: {gap:+.2f})")
                
                
                if has_oversupply:
                    response = f"Highest oversupply areas in {city}: {', '.join(area_descriptions[:-1])}, and {area_descriptions[-1]}. Negative gap values indicate supply exceeds demand. While this benefits renters, investors should be cautious of higher vacancy risks and potentially lower returns in these locations."
                else:
                    if not area_descriptions:
                        response = f"No oversupplied areas found in {city}. The market appears to be undersupplied overall."
                    elif len(area_descriptions) == 1:
                        response = f"No oversupplied areas found in {city}. Least undersupplied area: {area_descriptions[0]}. Market remains undersupplied overall."
                    else:
                        response = f"No oversupplied areas found in {city}. Least undersupplied areas: {', '.join(area_descriptions[:-1])}, and {area_descriptions[-1]}. Market remains undersupplied overall."
                
                return response
            else:
                return "I need more data to show you oversupplied areas. Try asking about a specific city!"
        
        elif intent == 'historical':
            if 'error' in data:
                return f"Sorry, I couldn't get historical data. Error: {data['error']}"
            
            city = data.get('city', 'the city')
            historical = data.get('historical_data', [])
            
            if not historical:
                return f"No historical data available for {city}."
            
            response = f"Historical rental demand in {city}:\n\n"
            for item in historical[-6:]:  # Last 6 months
                month = item.get('month', '')
                demand = item.get('demand', 0)
                year = item.get('year', '')
                response += f"- **{month} {year}**: {demand:,} listings\n"
            
            # Calculate trend with smart partial-data detection (for internal context only)
            displayed_months = historical[-6:] if len(historical) > 6 else historical
            if len(displayed_months) >= 2:
                first = displayed_months[0]['demand']
                last_item = displayed_months[-1]
                last = last_item['demand']
                
                # Check for partial month data (common in datasets)
                # If last month dropped > 50% compared to second-to-last month, it's likely partial
                is_partial = False
                if len(displayed_months) >= 3:
                    second_last = displayed_months[-2]['demand']
                    if last < (second_last * 0.5): # drastic drop
                         is_partial = True
                         # Use second to last for trend calculation
                         last = second_last
                         # Note: 'first' remains the same (start of period)
                
                change = ((last - first) / first) * 100
                
                # Store trend for context in future forecasts
                self.last_trend = change
            
            return response
        
        elif intent == 'top_cities':
            if 'error' in data:
                return "I apologize, but I couldn't fetch the city rankings at this moment. Please try again."
            
            cities = data.get('cities', [])
            if not cities:
                return "I couldn't retrieve city data at this moment."
            
            period = data.get('period', 'historical period')
            response = f"Based on analysis of **10 million actual rental transactions** ({period}), here are the **top 5 cities** with the highest rental demand:\n\n"
            
            for i, city_data in enumerate(cities, 1):
                city = city_data['city']
                demand = city_data['demand']
                monthly = city_data['monthly_demand']
                response += f"{i}. **{city}**: {demand:,} properties/day (~{monthly:,}/month)\n"
            
            response += f"\n**Data Source**: Real historical data from 10M transactions ({period}). These cities consistently show the strongest rental market activity."
            return response
        
        elif intent == 'bottom_cities':
            if 'error' in data:
                return "I apologize, but I couldn't fetch the city rankings at this moment. Please try again."
            
            cities = data.get('cities', [])
            if not cities:
                return "I couldn't retrieve city data at this moment."
            
            period = data.get('period', 'historical period')
            response = f"Based on analysis of **10 million actual rental transactions** ({period}), here are the **bottom 5 cities** with the lowest rental demand:\n\n"
            
            for i, city_data in enumerate(cities, 1):
                city = city_data['city']
                demand = city_data['demand']
                monthly = city_data['monthly_demand']
                response += f"{i}. **{city}**: {demand:,} properties/day (~{monthly:,}/month)\n"
            
            response += "\nThese cities show lower market activity. Investors should exercise caution and conduct thorough due diligence before investing in these markets."
            return response
        
        elif intent == 'top_city':
            if 'error' in data:
                return "I apologize, but I couldn't fetch the city rankings at this moment. Please try again."
            
            cities = data.get('cities', [])
            if not cities:
                return "I couldn't retrieve city data at this moment."
            
            city_data = cities[0]
            city = city_data['city']
            demand = city_data['demand']
            monthly = city_data['monthly_demand']
            period = data.get('period', 'historical period')
            
            response = f"Based on analysis of **10 million actual rental transactions** ({period}), the **#1 city** with the highest rental demand is:\n\n"
            response += f"🏆 **{city}**: {demand:,} properties/day (~{monthly:,}/month)\n\n"
            response += f"**Data Source**: Real historical data from 10M transactions ({period}). {city} consistently shows the strongest rental market activity and represents the best investment opportunity among all analyzed cities."
            return response
        
        elif intent == 'bottom_city':
            if 'error' in data:
                return "I apologize, but I couldn't fetch the city rankings at this moment. Please try again."
            
            cities = data.get('cities', [])
            if not cities:
                return "I couldn't retrieve city data at this moment."
            
            city_data = cities[0]
            city = city_data['city']
            demand = city_data['demand']
            monthly = city_data['monthly_demand']
            
            response = f"Based on current market analysis, the city with the **lowest rental demand** is:\n\n"
            response += f"⚠️ **{city}**: {demand:,} properties/day (~{monthly:,}/month)\n\n"
            period = data.get('period', 'historical period')
            response += f"**Data Source**: Real historical data from 10M transactions ({period}). {city} shows the weakest market activity among all analyzed cities. Investors should exercise caution and conduct thorough due diligence before considering this market."
            return response
        

        elif intent == 'help':
            return self.get_help_message()
        
        else:
            return self.get_default_response()
    
    def get_greeting_response(self, query: str = "") -> str:
        """Generate warm, personalized greeting"""
        # Try to extract name from the query
        name = self.extract_name(query)
        if name:
            self.user_name = name
        
        # Build personalized greeting
        if self.user_name:
            greeting = f"Hello {self.user_name}"
        else:
            greeting = "Hello"
        
        return f"""{greeting}

I'm your AI Property Investment Assistant. I'm here to help you make smart rental property decisions.

**I can help you with:**
- Rental demand forecasting for any city
- Investment opportunity analysis
- Historical market trends
- Best localities for investment

**Just ask me naturally, like:**
- "What's the demand in Mumbai?"
- "Where should I invest in Delhi?"
- "Show me Bangalore opportunities"

What would you like to know?
"""
    
    def get_thank_you_response(self) -> str:
        """Generate acknowledgment for gratitude"""
        responses = [
            "You're very welcome! 😊 Happy to help you make informed investment decisions. Feel free to ask anything else!",
            "My pleasure! 🏠 I'm here whenever you need property insights. What else can I help you with?",
            "Glad I could help! 💡 Don't hesitate to reach out if you have more questions about the rental market.",
        ]
        import random
        return random.choice(responses)
    
    def get_goodbye_response(self) -> str:
        """Generate warm farewell message"""
        return """Goodbye! 👋 

Best of luck with your property investments! Remember, I'm always here to help you analyze the rental market.

Happy investing! 🏠💰
"""
    
    def get_help_message(self) -> str:
        """Return help message"""
        return """
**Welcome to Rental Property AI Assistant!** 🏠

I can help you with:

**1. Demand Forecasting**
- "What's the demand in Mumbai for August 2024?"
- "Predict rental demand in Delhi"
- "How many rentals in Bangalore next month?"

**2. Investment Opportunities (High Demand)**
- "Show me investment opportunities in Mumbai"
- "Which areas in Delhi have high demand?"
- "Where should I invest in Bangalore?"

**3. Low Demand Areas (For Renters/Buyers)**
- "Which areas have low demand in Mumbai?"
- "Show me affordable areas in Delhi"
- "Where is it cheap in Bangalore?"

**4. Oversupplied Markets (Renter's/Buyer's Market)**
- "Which areas are oversupplied in Mumbai?"
- "Show me renter's market in Delhi"
- "Buyer's market in Bangalore"

**5. Historical Data**
- "Show historical demand in Chennai"
- "Past trends in Pune"
- "Historical data for Hyderabad"

**Supported Cities**: Mumbai, Delhi, Bangalore, Hyderabad, Chennai, Kolkata, Pune, Ahmedabad, Jaipur, Surat, and 30 more!

Just ask me in natural language! 😊
"""
    
    def get_default_response(self, query: str = "") -> str:
        """Return conversational default response for unknown queries"""
        return f"""Hmm, I'm not quite sure what you're asking about. 🤔

I specialize in rental property insights! I can help you with:

💡 **Try asking me:**
- "What's the demand in Mumbai?" - for demand forecasting
- "Where should I invest in Delhi?" - for investment opportunities
- "Show me Bangalore trends" - for historical data

**Supported cities**: Mumbai, Delhi, Bangalore, Hyderabad, Chennai, Kolkata, Pune, Ahmedabad, and 30+ more!

Could you rephrase your question? Or type "help" for more examples! 😊
"""
    
    def chat(self, query: str) -> str:
        """Main chat function - process query and return response with context awareness"""
        
        # Store in conversation history
        self.conversation_history.append(query)
        
        # Detect intent
        intent, confidence = self.detect_intent(query)
        
        # Handle greetings
        if intent == 'greeting':
            return self.get_greeting_response(query)
        
        # Handle thank you
        if intent == 'thank_you':
            return self.get_thank_you_response()
        
        # Handle goodbye
        if intent == 'goodbye':
            return self.get_goodbye_response()
        
        # Handle help
        if intent == 'help':
            return self.get_help_message()
        
        # Extract entities
        city = self.extract_city(query)
        
        # Context awareness: Use last city if not specified
        if not city and self.last_city:
            city = self.last_city
            context_note = f"\n\nSince you didn't mention a city, I'll use your last mentioned city: **{city}**."
        else:
            context_note = ""
        
        # City is NOT required for city ranking intents
        if not city and intent not in ['top_cities', 'bottom_cities', 'top_city', 'bottom_city']:
            # More helpful error message
            cities_sample = ", ".join(self.cities[:8])
            return f"""I'd love to help! 😊 But I need to know which city you're interested in.

**Supported cities include**: {cities_sample}, and 30+ more!

**Try asking:**
- "What's the demand in Mumbai?"
- "Show me opportunities in Delhi"
- "Bangalore rental trends"

Which city would you like to know about?
"""
        
        # Update context
        self.last_city = city
        self.last_intent = intent
        
        # Route to appropriate API based on intent
        if intent == 'demand_forecast':
            year, month = self.extract_date(query)
            economic_factors = self.extract_economic_factors(query)
            
            # UPGRADE: If user specifies economic factors, use the ENHANCED API
            # This ensures they get the "Macro Stress Test" logic (risk analysis) 
            # instead of just a basic demand number.
            if economic_factors:
                 data = self.call_enhanced_demand_api(city, year, month, economic_factors)
                 # Force intent switch to tenant_quality for rich response if risk data is there
                 if 'tenant_quality_analysis' in data:
                     # FIX: Inject extracted factors so the warning label appears
                     data['_extracted_economic_factors'] = economic_factors
                     return self.generate_response('tenant_quality', data, query) + context_note
            
            data = self.call_demand_api(city, year, month, economic_factors)
            # Store economic factors for response generation
            data['_extracted_economic_factors'] = economic_factors
            return self.generate_response(intent, data, query) + context_note
        
        elif intent == 'gap_analysis':
            # Don't extract locality for general gap analysis queries
            # This ensures we get the list of top areas instead of single locality prediction
            locality = None
            bhk = self.extract_bhk(query) or "2"
            rent = self.extract_rent(query) or 30000
            # For investment opportunities, show most undersupplied areas (highest positive gap)
            data = self.call_gap_api(city, locality, bhk, rent, sort_by='gap_high')
            return self.generate_response(intent, data, query) + context_note
        
        elif intent == 'low_demand':
            # Call gap API to get all localities, sorted by lowest demand (oversupplied)
            data = self.call_gap_api(city, locality=None, sort_by='gap_high')
            return self.generate_response(intent, data, query) + context_note
        
        elif intent == 'low_gap':
            locality = self.extract_locality(query)
            # Call gap API to get all localities, sorted by LOWEST gap (most negative = oversupplied)
            data = self.call_gap_api(city, locality=None, sort_by='gap_low')
            return self.generate_response(intent, data, query) + context_note
        
        elif intent == 'historical':
            data = self.call_historical_api(city)
            return self.generate_response(intent, data, query) + context_note

        elif intent == 'tenant_quality':
            year, month = self.extract_date(query)
            economic_factors = self.extract_economic_factors(query)
            # Call the NEW enhanced API
            data = self.call_enhanced_demand_api(city, year, month, economic_factors)
            return self.generate_response(intent, data, query) + context_note
        
        elif intent == 'top_cities':
            data = self.get_city_rankings(top=True)
            return self.generate_response(intent, data, query)
        
        elif intent == 'bottom_cities':
            data = self.get_city_rankings(top=False)
            return self.generate_response(intent, data, query)
        
        elif intent == 'top_city':
            data = self.get_city_rankings(top=True, count=1)
            return self.generate_response(intent, data, query)
        
        elif intent == 'bottom_city':
            data = self.get_city_rankings(top=False, count=1)
            return self.generate_response(intent, data, query)
        
        else:
            return self.get_default_response(query)


# Example usage
if __name__ == "__main__":
    chatbot = RentalPropertyChatbot()
    
    print("Rental Property AI Chatbot")
    print("=" * 50)
    print("Type 'quit' to exit\n")
    
    while True:
        query = input("You: ")
        if query.lower() in ['quit', 'exit', 'bye']:
            print("Chatbot: Goodbye! Happy investing! 🏠")
            break
        
        response = chatbot.chat(query)
        print(f"\nChatbot: {response}\n")
