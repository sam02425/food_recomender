#!/usr/bin/env python3
"""
Test script for customer history functionality
Tests order saving, retrieval, and dietary preferences
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PHONE = "555-123-4567"

def test_customer_history():
    """Test the complete customer history workflow"""
    print("🧪 Testing Customer History System")
    print("=" * 50)

    # Test 1: Get customer orders (should be empty initially)
    print("\n1. Testing initial customer data retrieval...")
    response = requests.get(f"{BASE_URL}/api/customer-orders?phone={TEST_PHONE}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Customer data retrieved successfully")
        print(f"   Has previous orders: {data.get('has_previous_orders', False)}")
        print(f"   Total orders: {data.get('total_orders', 0)}")
        print(f"   Dietary profile: {data.get('dietary_profile', {})}")
    else:
        print(f"❌ Failed to get customer data: {response.status_code}")
        return False

    # Test 2: Save dietary preferences
    print("\n2. Testing dietary preferences saving...")
    dietary_data = {
        "customer_phone": TEST_PHONE,
        "restrictions": ["vegetarian", "no_beef"],
        "allergens": ["nuts", "dairy"]
    }

    response = requests.post(f"{BASE_URL}/api/customer/save-dietary", json=dietary_data)
    if response.status_code == 200:
        print("✅ Dietary preferences saved successfully")
    else:
        print(f"❌ Failed to save dietary preferences: {response.status_code}")
        return False

    # Test 3: Save a sample order
    print("\n3. Testing order saving...")
    order_data = {
        "customer_phone": TEST_PHONE,
        "order_details": {
            "protein": ["Paneer"],
            "sauce": ["Curry Special"],
            "base_type": "Biryani",
            "base_option": "Rice",
            "veggies": ["Onion", "Tomato"],
            "garnishes": ["Cilantro"],
            "dish_name": "Paneer Curry Biryani"
        }
    }

    response = requests.post(f"{BASE_URL}/api/customer/save-order", json=order_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Order saved successfully: {result.get('order_id', 'Unknown')}")
    else:
        print(f"❌ Failed to save order: {response.status_code}")
        return False

    # Test 4: Save another order
    print("\n4. Testing second order saving...")
    order_data2 = {
        "customer_phone": TEST_PHONE,
        "order_details": {
            "protein": ["Chicken"],
            "sauce": ["Malai Masala"],
            "base_type": "Sandwich & Subs",
            "base_option": "Sourdough",
            "veggies": ["Lettuce", "Cucumber"],
            "garnishes": ["Mint"],
            "dish_name": "Chicken Malai Sandwich"
        }
    }

    response = requests.post(f"{BASE_URL}/api/customer/save-order", json=order_data2)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Second order saved successfully: {result.get('order_id', 'Unknown')}")
    else:
        print(f"❌ Failed to save second order: {response.status_code}")
        return False

    # Test 5: Retrieve customer data again
    print("\n5. Testing customer data retrieval after orders...")
    response = requests.get(f"{BASE_URL}/api/customer-orders?phone={TEST_PHONE}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Customer data retrieved successfully")
        print(f"   Has previous orders: {data.get('has_previous_orders', False)}")
        print(f"   Total orders: {data.get('total_orders', 0)}")
        print(f"   Recent orders: {len(data.get('recent_orders', []))}")
        print(f"   Favorite items: {data.get('favorite_items', [])}")

        # Show recent orders details
        recent_orders = data.get('recent_orders', [])
        for i, order in enumerate(recent_orders, 1):
            print(f"   Order {i}: {order.get('items', {}).get('dish_name', 'Unknown')} - ${order.get('total_price', 0)} - {order.get('total_calories', 0)} cal")

        # Show dietary profile
        dietary_profile = data.get('dietary_profile', {})
        print(f"   Dietary restrictions: {dietary_profile.get('restrictions', [])}")
        print(f"   Allergies: {dietary_profile.get('allergies', [])}")

    else:
        print(f"❌ Failed to get customer data: {response.status_code}")
        return False

    # Test 6: Test with different customer
    print("\n6. Testing with different customer...")
    different_phone = "555-987-6543"
    response = requests.get(f"{BASE_URL}/api/customer-orders?phone={different_phone}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Different customer data retrieved")
        print(f"   Has previous orders: {data.get('has_previous_orders', False)}")
        print(f"   Total orders: {data.get('total_orders', 0)}")
    else:
        print(f"❌ Failed to get different customer data: {response.status_code}")
        return False

    print("\n" + "=" * 50)
    print("🎉 All customer history tests passed!")
    return True

def test_menu_with_portion_sizes():
    """Test menu data with portion sizes"""
    print("\n🧪 Testing Menu with Portion Sizes")
    print("=" * 50)

    response = requests.get(f"{BASE_URL}/api/menu-data")
    if response.status_code == 200:
        data = response.json()
        print("✅ Menu data retrieved successfully")

        # Check proteins for portion sizes
        proteins = data.get('proteins', [])
        if proteins:
            protein = proteins[0]
            print(f"   Sample protein: {protein.get('name', 'Unknown')}")
            print(f"   Base price: ${protein.get('price', 0)}")
            print(f"   Base calories: {protein.get('calories', 0)}")

            portion_sizes = protein.get('portion_sizes', {})
            if portion_sizes:
                print("   Portion sizes available:")
                for size, details in portion_sizes.items():
                    print(f"     {size}: {details.get('name', 'Unknown')} - ${details.get('price', 0)} - {details.get('calories', 0)} cal")
            else:
                print("   ❌ No portion sizes found")
        else:
            print("   ❌ No proteins found")
    else:
        print(f"❌ Failed to get menu data: {response.status_code}")
        return False

    return True

if __name__ == "__main__":
    print("🚀 Starting Customer History Tests")
    print(f"Testing against: {BASE_URL}")

    try:
        # Test basic connectivity
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print(f"❌ Server not responding: {response.status_code}")
            exit(1)

        print("✅ Server is responding")

        # Run tests
        success1 = test_customer_history()
        success2 = test_menu_with_portion_sizes()

        if success1 and success2:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n❌ Some tests failed!")
            exit(1)

    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("Make sure the server is running with: python simple_server.py")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)