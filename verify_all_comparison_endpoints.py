import sys
import os
import json
import logging

# Disable logging to keep output clean
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('root').setLevel(logging.ERROR)

def test_product(name, path, app_file_name='api_server'):
    print(f"\n{'='*20} Testing {name} {'='*20}")
    
    # Add product directory to path
    full_path = os.path.abspath(path)
    if full_path not in sys.path:
        sys.path.insert(0, full_path)
    
    try:
        # Import the app
        # access the module dynamically to avoid import conflicts if we were doing this repeatedly
        # but for a one-off script, simple import is fine, but we need to handle the module name
        # since all are called 'api_server', we need to be careful.
        
        # We will use exec to load the module in a separate namespace
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"{name}_api", os.path.join(full_path, f"{app_file_name}.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"{name}_api"] = module
        spec.loader.exec_module(module)
        
        app = module.app
        client = app.test_client()
        
        # Test /comparison endpoint
        response = client.get('/comparison')
        
        if response.status_code == 200:
            data = response.json
            print(f"✅ Status: 200 OK")
            print(f"✅ Data Type: {type(data)}")
            
            if 'data_points' in data:
                print(f"✅ Data Points: {len(data['data_points'])}")
                print("✅ Sample Item:")
                print(json.dumps(data['data_points'][0], indent=2))
            elif isinstance(data, list): # Handling list format if that's what we returned (the code returned list directly in implementation plan but jsonify(data) which was the full dict in my replacement content)
                # Wait, in P1/P2/P3 I replaced it to return jsonify(data) where data = json.load(f).
                # And the data saved was `comparison_data` dict which has `data_points` list.
                pass
            
            # Print full structure preview
            # print(json.dumps(data, indent=2)[:500] + "...")
            
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Error: {response.get_data(as_text=True)}")
            
    except Exception as e:
        print(f"❌ Execution Error: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    base_dir = "."
    
    # Product 1
    test_product(
        "Product 1 (Demand)", 
        os.path.join(base_dir, "Product_1_Rental_Demand_Forecasting")
    )
    
    # Product 2
    test_product(
        "Product 2 (Gap)", 
        os.path.join(base_dir, "Product_2_Demand_Supply_Gap_Identification")
    )
    
    # Product 3
    test_product(
        "Product 3 (Chatbot)", 
        os.path.join(base_dir, "Product_3_Conversational_AI_Chatbot")
    )

if __name__ == "__main__":
    main()
