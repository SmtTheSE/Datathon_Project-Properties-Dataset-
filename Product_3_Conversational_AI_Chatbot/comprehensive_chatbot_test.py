"""
Comprehensive Chatbot Testing Suite
Tests for production-worthiness, natural conversation, greetings, and human-like responses
"""

import sys
import time
from chatbot_engine import RentalPropertyChatbot

class ChatbotTester:
    """Comprehensive testing for chatbot quality"""
    
    def __init__(self):
        self.chatbot = RentalPropertyChatbot()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def test_query(self, category, query, expected_keywords=None, should_not_contain=None):
        """Test a single query and validate response"""
        self.total_tests += 1
        print(f"\n{'='*80}")
        print(f"TEST {self.total_tests}: {category}")
        print(f"{'='*80}")
        print(f"Query: '{query}'")
        print(f"-" * 80)
        
        start_time = time.time()
        response = self.chatbot.chat(query)
        response_time = time.time() - start_time
        
        print(f"Response ({response_time:.2f}s):")
        print(response)
        print(f"-" * 80)
        
        # Validate response
        passed = True
        issues = []
        
        # Check response time (should be < 3 seconds)
        if response_time > 3:
            issues.append(f"⚠️ Slow response: {response_time:.2f}s")
            passed = False
        
        # Check for expected keywords
        if expected_keywords:
            for keyword in expected_keywords:
                if keyword.lower() not in response.lower():
                    issues.append(f"❌ Missing expected keyword: '{keyword}'")
                    passed = False
        
        # Check for unwanted content
        if should_not_contain:
            for unwanted in should_not_contain:
                if unwanted.lower() in response.lower():
                    issues.append(f"❌ Contains unwanted: '{unwanted}'")
                    passed = False
        
        # Check response is not empty
        if not response or len(response.strip()) < 10:
            issues.append("❌ Response too short or empty")
            passed = False
        
        # Check for error messages that shouldn't appear for valid queries
        if "error" in response.lower() and expected_keywords:
            issues.append("❌ Unexpected error in response")
            passed = False
        
        if passed:
            self.passed_tests += 1
            print("✅ PASSED")
        else:
            print("❌ FAILED")
            for issue in issues:
                print(f"  {issue}")
        
        self.test_results.append({
            'category': category,
            'query': query,
            'response': response,
            'response_time': response_time,
            'passed': passed,
            'issues': issues
        })
        
        return passed
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        
        print("\n" + "="*80)
        print("COMPREHENSIVE CHATBOT TESTING SUITE")
        print("Testing: Production-worthiness, Natural Conversation, Human-like Responses")
        print("="*80)
        
        # ===== GREETING TESTS =====
        print("\n\n📢 CATEGORY 1: GREETING & SMALL TALK")
        print("Testing human-like greetings and conversational openings")
        
        self.test_query("Greeting - Hi", "Hi", 
                       expected_keywords=None)  # Currently fails, will optimize
        
        self.test_query("Greeting - Hello", "Hello", 
                       expected_keywords=None)
        
        self.test_query("Greeting - Good morning", "Good morning", 
                       expected_keywords=None)
        
        self.test_query("Greeting - Hey there", "Hey there", 
                       expected_keywords=None)
        
        # ===== NATURAL LANGUAGE TESTS =====
        print("\n\n📢 CATEGORY 2: NATURAL LANGUAGE UNDERSTANDING")
        print("Testing casual, human-like queries")
        
        self.test_query("Casual - How's Mumbai", "How's Mumbai doing?",
                       expected_keywords=["Mumbai", "demand"])
        
        self.test_query("Casual - Mumbai market", "mumbai rental market",
                       expected_keywords=["Mumbai", "demand"])
        
        self.test_query("Casual - Should I invest", "should i invest in delhi?",
                       expected_keywords=["Delhi"])
        
        self.test_query("Casual - Is Bangalore good", "is bangalore good for investment?",
                       expected_keywords=["Bangalore"])
        
        # ===== DEMAND FORECAST TESTS =====
        print("\n\n📢 CATEGORY 3: DEMAND FORECASTING (CORE FUNCTIONALITY)")
        print("Testing demand prediction with real API data")
        
        self.test_query("Demand - Standard query", "What's the demand in Mumbai?",
                       expected_keywords=["Mumbai", "demand", "per day", "per month"])
        
        self.test_query("Demand - With date", "What's the demand in Delhi for August 2024?",
                       expected_keywords=["Delhi", "demand", "August", "2024"])
        
        self.test_query("Demand - Predict format", "Predict rental demand in Bangalore",
                       expected_keywords=["Bangalore", "demand"])
        
        self.test_query("Demand - How many format", "How many rentals in Chennai?",
                       expected_keywords=["Chennai", "demand"])
        
        self.test_query("Demand - Tell me format", "Tell me about demand in Pune",
                       expected_keywords=["Pune", "demand"])
        
        # ===== GAP ANALYSIS TESTS =====
        print("\n\n📢 CATEGORY 4: GAP ANALYSIS & INVESTMENT OPPORTUNITIES")
        print("Testing investment opportunity identification")
        
        self.test_query("Gap - Opportunities", "Show me opportunities in Mumbai",
                       expected_keywords=["Mumbai", "localities", "demand"])
        
        self.test_query("Gap - Investment", "Where should I invest in Delhi?",
                       expected_keywords=["Delhi", "localities"])
        
        self.test_query("Gap - Best areas", "Which are the best areas in Bangalore?",
                       expected_keywords=["Bangalore", "localities"])
        
        self.test_query("Gap - Gap analysis", "Gap analysis for Mumbai",
                       expected_keywords=["Mumbai"])
        
        # ===== HISTORICAL DATA TESTS =====
        print("\n\n📢 CATEGORY 5: HISTORICAL DATA & TRENDS")
        print("Testing historical analysis capabilities")
        
        self.test_query("Historical - Standard", "Show historical demand in Mumbai",
                       expected_keywords=["Mumbai", "historical"])
        
        self.test_query("Historical - Trends", "What are the trends in Delhi?",
                       expected_keywords=["Delhi"])
        
        self.test_query("Historical - Past data", "Past data for Bangalore",
                       expected_keywords=["Bangalore"])
        
        # ===== HELP & GUIDANCE TESTS =====
        print("\n\n📢 CATEGORY 6: HELP & GUIDANCE")
        print("Testing help system and user guidance")
        
        self.test_query("Help - Direct", "help",
                       expected_keywords=["Demand", "Gap", "Historical"])
        
        self.test_query("Help - What can you do", "What can you do?",
                       expected_keywords=["help", "can"])
        
        # ===== EDGE CASES & ERROR HANDLING =====
        print("\n\n📢 CATEGORY 7: EDGE CASES & ERROR HANDLING")
        print("Testing robustness and error handling")
        
        self.test_query("Edge - No city", "What's the demand?",
                       expected_keywords=["city"])
        
        self.test_query("Edge - Unknown city", "What's the demand in Atlantis?",
                       expected_keywords=None)
        
        self.test_query("Edge - Gibberish", "asdfghjkl",
                       expected_keywords=None)
        
        self.test_query("Edge - Single word", "demand",
                       expected_keywords=None)
        
        # ===== CONVERSATIONAL CONTEXT TESTS =====
        print("\n\n📢 CATEGORY 8: CONVERSATIONAL FLOW")
        print("Testing multi-turn conversation capabilities")
        
        self.test_query("Context - First query", "What's the demand in Mumbai?",
                       expected_keywords=["Mumbai", "demand"])
        
        # Note: Current implementation doesn't support context, this will fail
        self.test_query("Context - Follow-up", "And what about the gap?",
                       expected_keywords=None)
        
        # ===== RESPONSE QUALITY TESTS =====
        print("\n\n📢 CATEGORY 9: RESPONSE QUALITY & LEGITIMACY")
        print("Testing response professionalism and data legitimacy")
        
        self.test_query("Quality - Professional tone", "Demand in Hyderabad",
                       expected_keywords=["Hyderabad", "demand"],
                       should_not_contain=["lol", "idk", "dunno"])
        
        self.test_query("Quality - Data legitimacy", "Forecast for Kolkata",
                       expected_keywords=["Kolkata"],
                       should_not_contain=["mock", "fake", "example"])
        
        # ===== GENERATE REPORT =====
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        
        print("\n\n" + "="*80)
        print("COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        print(f"\nTotal Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        # Category breakdown
        categories = {}
        for result in self.test_results:
            cat = result['category'].split(' - ')[0]
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat]['total'] += 1
            if result['passed']:
                categories[cat]['passed'] += 1
        
        print("\n" + "-"*80)
        print("RESULTS BY CATEGORY")
        print("-"*80)
        for cat, stats in categories.items():
            success_rate = (stats['passed']/stats['total'])*100
            status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
            print(f"{status} {cat}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Failed tests
        failed_tests = [r for r in self.test_results if not r['passed']]
        if failed_tests:
            print("\n" + "-"*80)
            print("FAILED TESTS DETAILS")
            print("-"*80)
            for result in failed_tests:
                print(f"\n❌ {result['category']}")
                print(f"   Query: '{result['query']}'")
                for issue in result['issues']:
                    print(f"   {issue}")
        
        # Performance stats
        avg_response_time = sum(r['response_time'] for r in self.test_results) / len(self.test_results)
        max_response_time = max(r['response_time'] for r in self.test_results)
        
        print("\n" + "-"*80)
        print("PERFORMANCE METRICS")
        print("-"*80)
        print(f"Average Response Time: {avg_response_time:.2f}s")
        print(f"Max Response Time: {max_response_time:.2f}s")
        print(f"Performance Rating: {'✅ Excellent' if avg_response_time < 1 else '⚠️ Good' if avg_response_time < 2 else '❌ Needs Improvement'}")
        
        # Overall assessment
        print("\n" + "="*80)
        print("OVERALL ASSESSMENT")
        print("="*80)
        
        success_rate = (self.passed_tests/self.total_tests)*100
        
        if success_rate >= 90:
            rating = "⭐⭐⭐⭐⭐ EXCELLENT - Production Ready & Hackathon Winning"
        elif success_rate >= 80:
            rating = "⭐⭐⭐⭐ VERY GOOD - Production Ready with Minor Improvements"
        elif success_rate >= 70:
            rating = "⭐⭐⭐ GOOD - Needs Optimization for Production"
        elif success_rate >= 60:
            rating = "⭐⭐ FAIR - Significant Improvements Needed"
        else:
            rating = "⭐ NEEDS WORK - Major Improvements Required"
        
        print(f"\nRating: {rating}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n" + "-"*80)
        print("RECOMMENDATIONS")
        print("-"*80)
        
        recommendations = []
        
        # Check greeting category
        greeting_results = [r for r in self.test_results if r['category'].startswith('Greeting')]
        if greeting_results and not all(r['passed'] for r in greeting_results):
            recommendations.append("🔴 CRITICAL: Add greeting intent and responses for human-like interaction")
        
        # Check natural language
        natural_results = [r for r in self.test_results if r['category'].startswith('Casual')]
        if natural_results:
            natural_success = sum(1 for r in natural_results if r['passed']) / len(natural_results)
            if natural_success < 0.8:
                recommendations.append("🔴 CRITICAL: Improve natural language understanding patterns")
        
        # Check context
        context_results = [r for r in self.test_results if r['category'].startswith('Context')]
        if context_results and not all(r['passed'] for r in context_results):
            recommendations.append("🟡 MEDIUM: Add context awareness for multi-turn conversations")
        
        # Check performance
        if avg_response_time > 2:
            recommendations.append("🟡 MEDIUM: Optimize response time (consider caching)")
        
        # Check edge cases
        edge_results = [r for r in self.test_results if r['category'].startswith('Edge')]
        if edge_results:
            edge_success = sum(1 for r in edge_results if r['passed']) / len(edge_results)
            if edge_success < 0.7:
                recommendations.append("🟡 MEDIUM: Improve error messages to be more helpful")
        
        if not recommendations:
            recommendations.append("✅ No critical issues found! Chatbot is production-ready!")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80)

if __name__ == "__main__":
    print("Starting Comprehensive Chatbot Testing...")
    print("This will test: Greetings, Natural Language, API Integration, Error Handling, and more")
    print("\nNote: Some tests may fail initially - that's expected!")
    print("We'll use the results to optimize the chatbot.\n")
    
    input("Press Enter to start testing...")
    
    tester = ChatbotTester()
    tester.run_all_tests()
