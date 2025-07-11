#!/usr/bin/env python3
"""
Test script for the inventory management system
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_inventory_system():
    print("🧪 Testing Inventory Management System")
    print("=" * 50)

    # Test 1: Initialize inventory
    print("\n1. Initializing inventory...")
    response = requests.post(f"{BASE_URL}/api/inventory/initialize")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Inventory initialized successfully")
        print(f"   Total items: {data['inventory_summary']['total_items']}")
        print(f"   Out of stock: {data['inventory_summary']['out_of_stock']}")
        print(f"   Low stock: {data['inventory_summary']['low_stock']}")
        print(f"   Preparing: {data['inventory_summary']['preparing']}")
        print(f"   Available: {data['inventory_summary']['available']}")
    else:
        print(f"❌ Failed to initialize inventory: {response.status_code}")
        return

    # Test 2: Get inventory status
    print("\n2. Getting inventory status...")
    response = requests.get(f"{BASE_URL}/api/inventory/status")
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Inventory status retrieved")

        # Show some examples
        for item_name, item_data in list(status.items())[:5]:
            print(f"   {item_name}: {item_data['status']} (Stock: {item_data['current_stock']})")
            if item_data['status'] == 'preparing' and item_data['wait_time']:
                print(f"     ⏱️ Ready in {item_data['wait_time']} minutes")
    else:
        print(f"❌ Failed to get inventory status: {response.status_code}")

    # Test 3: Get menu data (filtered by inventory)
    print("\n3. Getting menu data (filtered by inventory)...")
    response = requests.get(f"{BASE_URL}/api/menu-data")
    if response.status_code == 200:
        menu_data = response.json()
        print(f"✅ Menu data retrieved")

        # Show available proteins
        proteins = menu_data.get('proteins', [])
        print(f"   Available proteins: {len(proteins)}")
        for protein in proteins:
            status_text = f" ({protein['status']})" if protein.get('status') else ""
            stock_text = f" [Stock: {protein['stock_level']}]" if protein.get('stock_level') is not None else ""
            wait_text = f" [Wait: {protein['wait_time']}m]" if protein.get('wait_time') else ""
            print(f"     {protein['name']}{status_text}{stock_text}{wait_text}")

        # Show available sauces
        sauces = menu_data.get('sauces', [])
        print(f"   Available sauces: {len(sauces)}")
        for sauce in sauces:
            status_text = f" ({sauce['status']})" if sauce.get('status') else ""
            stock_text = f" [Stock: {sauce['stock_level']}]" if sauce.get('stock_level') is not None else ""
            wait_text = f" [Wait: {sauce['wait_time']}m]" if sauce.get('wait_time') else ""
            print(f"     {sauce['name']}{status_text}{stock_text}{wait_text}")
    else:
        print(f"❌ Failed to get menu data: {response.status_code}")

    # Test 4: Test agent recommendations with inventory
    print("\n4. Testing agent recommendations with inventory...")
    order_details = {
        "protein": ["Chicken", "Paneer"],
        "sauce": ["Curry Special"],
        "base": ["Rice"],
        "veggies": ["Onion", "Tomato"],
        "garnishes": ["Cilantro"]
    }

    response = requests.post(
        f"{BASE_URL}/api/agent-recommendations",
        json={
            "user_id": "test_user",
            "context": {"activity": "work"},
            "order_details": order_details
        }
    )

    if response.status_code == 200:
        agent_data = response.json()
        print(f"✅ Agent recommendations retrieved")
        print(f"   Preparation time: {agent_data['preparation_time']['formatted_duration']}")
        print(f"   Queue position: #{agent_data['preparation_time']['queue_position']}")
        print(f"   Complexity multiplier: {agent_data['preparation_time']['complexity_multiplier']}")

        if agent_data['preparation_time']['unavailable_items']:
            print(f"   ❌ Unavailable: {agent_data['preparation_time']['unavailable_items']}")
        if agent_data['preparation_time']['low_stock_items']:
            print(f"   ⚠️ Low stock: {agent_data['preparation_time']['low_stock_items']}")
        if agent_data['preparation_time']['preparing_items']:
            print(f"   🔄 Preparing: {agent_data['preparation_time']['preparing_items']}")
        if agent_data['preparation_time']['additional_wait_time'] > 0:
            print(f"   ⏱️ Additional wait: {agent_data['preparation_time']['additional_wait_time']} minutes")
    else:
        print(f"❌ Failed to get agent recommendations: {response.status_code}")

    print("\n" + "=" * 50)
    print("✅ Inventory system test completed!")

if __name__ == "__main__":
    try:
        test_inventory_system()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")