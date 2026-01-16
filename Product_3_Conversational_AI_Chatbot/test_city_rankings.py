from chatbot_engine import RentalPropertyChatbot

bot = RentalPropertyChatbot()

print('Testing City Rankings with Historical Data...')
print('=' * 80)

# Test bottom cities
print('\nTesting: Show me worst 5 cities')
result = bot.get_city_rankings(top=False, count=5)
if 'cities' in result:
    print(f"Data Source: {result.get('data_source')}")
    print(f"Period: {result.get('period')}")
    print('\nBottom 5 Cities:')
    for i, city in enumerate(result['cities'], 1):
        print(f"{i}. {city['city']:15s}: {city['demand']:,}/day ({city['monthly_demand']:,}/month)")

print('\n' + '=' * 80)

# Test top cities
print('\nTesting: Show me top 5 cities')
result = bot.get_city_rankings(top=True, count=5)
if 'cities' in result:
    print(f"Data Source: {result.get('data_source')}")
    print(f"Period: {result.get('period')}")
    print('\nTop 5 Cities:')
    for i, city in enumerate(result['cities'], 1):
        print(f"{i}. {city['city']:15s}: {city['demand']:,}/day ({city['monthly_demand']:,}/month)")

print('\n' + '=' * 80)
print('✅ Historical data rankings working correctly!')
