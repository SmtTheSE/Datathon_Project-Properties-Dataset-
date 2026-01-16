
from chatbot_engine import RentalPropertyChatbot
import unittest

class TestChatbotLogic(unittest.TestCase):
    def test_gap_interpretation(self):
        bot = RentalPropertyChatbot()
        
        # Mock data for Undersupplied (Positive Gap)
        # Gap = Demand - Supply. Demand(100) - Supply(50) = 50. Gap Ratio = 50/100 = 0.5
        undersupplied_data = {
            'city': 'TestCity',
            'locality_data': [
                {'locality': 'Area A', 'gap': 0.5, 'demand': 100}
            ]
        }
        
        # Mock data for Oversupplied (Negative Gap)
        # Gap = Demand - Supply. Demand(50) - Supply(100) = -50. Gap Ratio = -50/50 = -1.0
        oversupplied_data = {
            'city': 'TestCity',
            'locality_data': [
                {'locality': 'Area B', 'gap': -0.5, 'demand': 50}
            ]
        }
        
        # Test 1: Positive Gap -> Should say "Undersupplied"
        response_under = bot.generate_response('gap_analysis', undersupplied_data, "query")
        print("\n--- Positive Gap (0.5) Response ---")
        print(response_under)
        self.assertIn("undersupplied", response_under.lower())
        self.assertIn("positive gap", response_under.lower())
        
        # Test 2: Negative Gap -> Should say "Oversupplied"
        response_over = bot.generate_response('gap_analysis', oversupplied_data, "query")
        print("\n--- Negative Gap (-0.5) Response ---")
        print(response_over)
        self.assertIn("oversupplied", response_over.lower())
        self.assertIn("negative gap", response_over.lower())

if __name__ == '__main__':
    unittest.main()
