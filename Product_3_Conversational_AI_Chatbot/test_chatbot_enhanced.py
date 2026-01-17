import sys
import os

# Add Product 3 to path
sys.path.append(os.path.join(os.getcwd(), 'Product_3_Conversational_AI_Chatbot'))

from chatbot_engine import RentalPropertyChatbot

def test_enhanced_chatbot():
    print("🤖 Initializing Chatbot...")
    bot = RentalPropertyChatbot()
    
    # Test queries
    queries = [
        "What is the tenant quality in Mumbai?",
        "Is it safe to invest in Pune?",
        "Check financial health of tenants in Bangalore",
        "What is the risk score for Delhi?"
    ]
    
    print("\n🚀 Testing Enhanced Chatbot Capabilities")
    print("=" * 50)
    
    for query in queries:
        print(f"\n👤 User: {query}")
        
        # 1. Detect Intent
        intent, conf = bot.detect_intent(query)
        print(f"   [Debug] Detected Intent: {intent} ({conf})")
        
        # 2. Get Response
        response = bot.chat(query)
        print(f"🤖 Chatbot:\n{response}")
        print("-" * 50)

if __name__ == "__main__":
    test_enhanced_chatbot()
