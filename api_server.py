# api_server.py
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import csv
import random
import datetime
import time

app = Flask(__name__)
# Enable CORS for all routes and all origins with all methods
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE"]}})

# Customer data storage (simple in-memory for testing, use database in production)
customers = {}
orders_history = []

# Load customer data from CSV if available
def load_customer_data():
    try:
        if os.path.exists('data/customers.csv'):
            with open('data/customers.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    phone = row.get('phone_number')
                    if phone:
                        customers[phone] = {
                            'name': row.get('name', ''),
                            'phone_number': phone,
                            'face_id': row.get('face_id', ''),
                            'visit_count': int(row.get('visit_count', 0)),
                            'last_visit': row.get('last_visit', '')
                        }
            print(f"Loaded {len(customers)} customers from CSV")
    except Exception as e:
        print(f"Error loading customer data: {e}")

# Load orders data from CSV if available
def load_orders_data():
    try:
        if os.path.exists('data/orders.csv'):
            with open('data/orders.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        items = json.loads(row.get('items', '[]'))
                        orders_history.append({
                            'order_id': row.get('order_id', ''),
                            'customer_id': row.get('customer_id', ''),
                            'phone_number': row.get('phone_number', ''),
                            'items': items,
                            'timestamp': row.get('timestamp', '')
                        })
                    except:
                        pass
            print(f"Loaded {len(orders_history)} orders from CSV")
    except Exception as e:
        print(f"Error loading orders data: {e}")

# Load data at startup
load_customer_data()
load_orders_data()

# Simulated LLM recommendation generator
def generate_llm_recommendations(recommendation_type, **params):
    """
    Generate creative recommendations that simulate LLM outputs

    Args:
        recommendation_type: Type of recommendation to generate
        params: Additional parameters for specific recommendation types

    Returns:
        Dictionary with simulated LLM recommendations
    """
    # Extract customer phone for personalization if available
    customer_phone = params.get("customer_phone")
    customer_name = None
    previous_orders = []

    # Look up customer data and previous orders if phone provided
    if customer_phone and customer_phone in customers:
        customer_name = customers[customer_phone].get('name')
        # Find previous orders for this customer
        previous_orders = [order for order in orders_history
                          if order.get('phone_number') == customer_phone]

    # Track if we used personalization
    personalized = False
    personalization_text = ""

    if recommendation_type == "health":
        activity_level = params.get("activity_level", "work")

        # Different recommendations based on activity level
        if activity_level == "study":
            proteins = ["Egg", "Paneer/Indian Cheese"]
            sauces = ["Mint Sauce", "Yogurt/Raita"]
            base_types = ["Wrap", "Bowl"]
            veggies = ["Spinach", "Bell Pepper", "Tomato", "Cilantro"]
            reasoning = "For study sessions, these brain-boosting proteins and light carbs provide sustained mental energy without causing crashes. The leafy greens and vegetables offer essential nutrients that improve focus and cognitive function."

        elif activity_level == "active" or activity_level == "gym":
            proteins = ["Chicken", "Soya"]
            sauces = ["Curry Special", "Red Spicy Sauce"]
            base_types = ["Bowl", "Biryani"]
            veggies = ["Spinach", "Bell Pepper", "Grilled Onion", "Avocado"]
            reasoning = "For an active lifestyle, these protein-rich options support muscle recovery and growth. The complex carbohydrates provide sustained energy throughout your workout, while the vegetable selection offers essential micronutrients."

        elif activity_level == "chilling" or activity_level == "relaxing":
            proteins = ["Paneer/Indian Cheese", "Potato"]
            sauces = ["Malai Masala", "Curry Special"]
            base_types = ["Bowl", "Wrap"]
            veggies = ["Avocado", "Tomato", "Cilantro", "Jalapeño"]
            reasoning = "For relaxation time, these comfort food options provide a perfect balance of flavor and nutrition. The creamy proteins pair beautifully with aromatic spices to create a satisfying meal experience."

        else:  # work or default
            proteins = ["Chicken", "Egg", "Soya"]
            sauces = ["Curry Special", "Mint Sauce", "Malai Masala"]
            base_types = ["Sandwich", "Wrap"]
            veggies = ["Bell Pepper", "Tomato", "Spinach", "Grilled Onion"]
            reasoning = "For your workday, these balanced options provide steady energy without causing post-meal drowsiness. The protein and fiber combination helps maintain focus and productivity throughout your shift."

        # Personalize based on previous orders if available
        if previous_orders and len(previous_orders) > 0:
            # Extract proteins from previous orders
            previous_proteins = []
            previous_sauces = []
            previous_base_types = []
            for order in previous_orders:
                for item in order.get('items', []):
                    if isinstance(item, dict):
                        if 'protein' in item and item['protein']:
                            previous_proteins.append(item['protein'])
                        if 'sauce' in item and item['sauce']:
                            previous_sauces.append(item['sauce'])
                        if 'base_type' in item and item['base_type']:
                            previous_base_types.append(item['base_type'])

            # Count occurrences
            protein_counts = {}
            for protein in previous_proteins:
                if protein in protein_counts:
                    protein_counts[protein] += 1
                else:
                    protein_counts[protein] = 1

            # Get most frequent protein
            if protein_counts:
                favorite_protein = max(protein_counts.items(), key=lambda x: x[1])[0]
                # Add to recommendations if not already there
                if favorite_protein not in proteins:
                    proteins.insert(0, favorite_protein)
                    personalized = True

            # Similarly for sauces and base types
            if previous_sauces:
                sauce_counts = {}
                for sauce in previous_sauces:
                    if sauce in sauce_counts:
                        sauce_counts[sauce] += 1
                    else:
                        sauce_counts[sauce] = 1

                if sauce_counts:
                    favorite_sauce = max(sauce_counts.items(), key=lambda x: x[1])[0]
                    if favorite_sauce not in sauces:
                        sauces.insert(0, favorite_sauce)
                        personalized = True

            if previous_base_types:
                base_counts = {}
                for base in previous_base_types:
                    if base in base_counts:
                        base_counts[base] += 1
                    else:
                        base_counts[base] = 1

                if base_counts:
                    favorite_base = max(base_counts.items(), key=lambda x: x[1])[0]
                    if favorite_base not in base_types:
                        base_types.insert(0, favorite_base)
                        personalized = True

        # Add personalization text if used
        if personalized:
            personalization_text = f"Based on your previous orders, we've added some of your favorite options. "
            reasoning = personalization_text + reasoning

        # Randomly choose an additional protein and sauce for more variety
        all_proteins = ["Chicken", "Egg", "Paneer/Indian Cheese", "Soya", "Potato", "Pepperoni"]
        all_sauces = ["Curry Special", "Malai Masala", "Curry Masala", "Marinara", "Yogurt/Raita", "Red Spicy Sauce", "Mint Sauce", "Green Spicy Sauce"]

        extra_protein = random.choice([p for p in all_proteins if p not in proteins])
        extra_sauce = random.choice([s for s in all_sauces if s not in sauces])

        # Sometimes add these extras
        if random.random() > 0.5:
            proteins.append(extra_protein)
        if random.random() > 0.5:
            sauces.append(extra_sauce)

        return {
            "proteins": proteins,
            "sauces": sauces,
            "base_types": base_types,
            "veggies": veggies,
            "reasoning": reasoning,
            "timestamp": datetime.datetime.now().isoformat(),
            "activity_level": activity_level,
            "personalized": personalized
        }

    elif recommendation_type == "weather":
        weather_condition = params.get("weather_condition", "sunny")
        temperature = params.get("temperature", 25)
        time_of_day = params.get("time_of_day", "afternoon")
        customer_phone = params.get("customer_phone")

        # Personalization flag
        personalized = False

        # Different recommendations based on weather and time
        if weather_condition in ["rainy", "cloudy"] or temperature < 15:
            base_types = ["Bowl", "Biryani"]
            suggested_base = "Bowl"
            reasoning = f"For {weather_condition} weather at {temperature}°C, these warming options provide comfort and satisfaction. The bowl format keeps everything warm longer while you enjoy your meal."

        elif weather_condition == "hot" or temperature > 28:
            base_types = ["Wrap", "Sandwich & Subs"]
            suggested_base = "Wrap"
            reasoning = f"For hot weather at {temperature}°C, these lighter options are more refreshing and won't weigh you down. The wrap format is perfect for keeping all flavors contained while being easy to handle."

        else:  # sunny or default
            if time_of_day == "morning":
                base_types = ["Wrap", "Sandwich & Subs"]
                suggested_base = "Wrap"
                reasoning = f"For a {weather_condition} {time_of_day}, these options offer portability and convenience to start your day. The wrap format is easy to eat on-the-go while containing all flavors."
            else:
                base_types = ["Bowl", "Wrap"]
                suggested_base = "Bowl"
                reasoning = f"For a {weather_condition} {time_of_day}, these options offer the perfect balance between satisfaction and freshness. The bowl format lets you appreciate each component of your meal."

        # Personalize based on previous orders if available
        if previous_orders and len(previous_orders) > 0:
            # Extract base types from previous orders
            previous_base_types = []
            for order in previous_orders:
                for item in order.get('items', []):
                    if isinstance(item, dict) and 'base_type' in item and item['base_type']:
                        previous_base_types.append(item['base_type'])

            # Count occurrences
            base_counts = {}
            for base in previous_base_types:
                if base in base_counts:
                    base_counts[base] += 1
                else:
                    base_counts[base] = 1

            # Get most frequent base
            if base_counts:
                favorite_base = max(base_counts.items(), key=lambda x: x[1])[0]
                # Set as suggested base if it appears frequently enough
                if base_counts[favorite_base] >= 2:
                    suggested_base = favorite_base
                    if favorite_base not in base_types:
                        base_types.insert(0, favorite_base)
                    personalized = True

        # Add personalization text if used
        if personalized and customer_name:
            personalization_text = f"{customer_name}, based on your previous orders, we've suggested your preferred base type. "
            reasoning = personalization_text + reasoning

        return {
            "weather_condition": weather_condition,
            "temperature": temperature,
            "time_of_day": time_of_day,
            "base_types": base_types,
            "suggested_base": suggested_base,
            "reasoning": reasoning,
            "timestamp": datetime.datetime.now().isoformat(),
            "personalized": personalized
        }

    elif recommendation_type == "dish_name":
        protein = params.get("protein", "Chicken")
        base_type = params.get("base_type", "Bowl")
        customer_name = params.get("customer_name", "")

        # Creative naming components
        prefixes = [
            "Mumbai", "Delhi", "Tandoori", "Bombay", "Spicy", "Maharaja",
            "Royal", "Curry", "Masala", "Fusion", "Incredible", "Signature"
        ]

        suffixes = [
            "Delight", "Special", "Express", "Creation", "Fiesta",
            "Magic", "Wonder", "Fusion", "Sensation", "Experience"
        ]

        styles = [
            "Street Style", "Chef's Special", "House Favorite", "Traditional",
            "Homestyle", "Gourmet", "Premium", "Classic", "Artisan"
        ]

        # Generate creative names
        name_templates = [
            f"{random.choice(prefixes)} {protein} {base_type}",
            f"{protein} {base_type} {random.choice(suffixes)}",
            f"{random.choice(styles)} {protein} {base_type}",
            f"{random.choice(prefixes)} {random.choice(suffixes)} {protein}",
            f"{protein} {random.choice(prefixes)} {base_type}"
        ]

        # Personalized names if customer name provided
        if customer_name:
            personal_templates = [
                f"{customer_name}'s {random.choice(prefixes)} {protein}",
                f"{customer_name}'s {protein} {random.choice(suffixes)}",
                f"{customer_name}'s Special {base_type}",
                f"The {customer_name} {random.choice(suffixes)}",
            ]
            # Add the personalized options to the front of the list
            name_templates = personal_templates + name_templates

        # Shuffle and select
        random.shuffle(name_templates)

        return {
            "name": name_templates[0],
            "alternatives": name_templates[1:4],
            "format_used": "Creative fusion naming with Indian regional influences"
        }

    # Default response if no matching type
    return {"error": "Unknown recommendation type"}

# Mock functions to simulate the kiosk
def start_new_order():
    order_id = f"ORD{int(time.time())}"
    return {
        "order_id": order_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "items": [],
        "total_price": 0.0
    }

def get_health_recommendations(activity_level, customer_phone=None):
    """
    Get health-based food recommendations for a specific activity level.
    Uses simulated LLM recommendations for variety and creativity.
    """
    try:
        # Get LLM-style recommendations for the activity level
        recommendations = generate_llm_recommendations(
            "health",
            activity_level=activity_level,
            customer_phone=customer_phone
        )

        return {
            "success": True,
            "recommendations": recommendations
        }
    except Exception as e:
        print(f"Error in health_recommendations: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def get_weather_recommendations(customer_phone=None):
    """
    Get weather-based food recommendations.
    Uses simulated LLM recommendations based on current weather and time.
    """
    try:
        # Generate random weather data for simulation
        # In a real app, this would come from a weather API
        weather_conditions = ["sunny", "rainy", "cloudy", "hot", "cold"]
        weather_condition = random.choice(weather_conditions)
        temperature = random.randint(5, 35)

        # Get current time of day
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"

        # Get LLM-style recommendations for this weather
        recommendations = generate_llm_recommendations(
            "weather",
            weather_condition=weather_condition,
            temperature=temperature,
            time_of_day=time_of_day,
            customer_phone=customer_phone
        )

        return {
            "success": True,
            "recommendations": recommendations
        }
    except Exception as e:
        print(f"Error in weather_recommendations: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def get_dish_name(selections):
    """
    Get creative dish name suggestions.
    Uses simulated LLM to generate unique, creative names.
    """
    try:
        protein = selections.get('protein', 'Chicken')
        base_type = selections.get('base_type', 'Bowl')
        customer_name = selections.get('customer_name', '')

        # Get LLM-style creative dish names
        suggestions = generate_llm_recommendations(
            "dish_name",
            protein=protein,
            base_type=base_type,
            customer_name=customer_name
        )

        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        print(f"Error in dish_name: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def process_recommendation_feedback(rec_type, feedback, customer_phone=None, custom=None):
    """
    Process feedback on recommendations and store it with customer data if available
    """
    # In a real implementation, this would store feedback in a database
    # For this demo, we'll just print it
    print(f"Received {feedback} feedback for {rec_type} from {customer_phone if customer_phone else 'anonymous'}")

    if customer_phone and customer_phone in customers:
        # Update customer preferences (in a real system)
        print(f"Updating preferences for customer: {customers[customer_phone].get('name', 'unknown')}")

    return {"status": "success"}

def add_order_item(selections):
    """
    Add an item to the order, including customer data if provided
    """
    return {
        "item_id": "ITEM1",
        "protein": selections.get("protein", ""),
        "sauce": selections.get("sauce", ""),
        "base_type": selections.get("base_type", ""),
        "base_option": selections.get("base_option", ""),
        "veggies": selections.get("veggies", []),
        "price": 12.99,
        "dish_name": selections.get("dish_name", ""),
        "customer_phone": selections.get("customer_phone", ""),
        "customer_name": selections.get("customer_name", "")
    }

def complete_order(customer_phone=None, customer_name=None):
    """
    Complete order and associate with customer if data is provided
    """
    order_id = f"ORD{int(time.time())}"

    # Store customer association in a real implementation
    if customer_phone:
        print(f"Associating order {order_id} with customer phone: {customer_phone}")

    if customer_name:
        print(f"Associating order {order_id} with customer name: {customer_name}")

    # Update visit count for customer
    if customer_phone and customer_phone in customers:
        customers[customer_phone]['visit_count'] = customers[customer_phone].get('visit_count', 0) + 1
        customers[customer_phone]['last_visit'] = datetime.datetime.now().isoformat()
        print(f"Updated visit count for customer: {customers[customer_phone].get('name', 'unknown')}")

    return {
        "order_id": order_id,
        "total_price": 12.99,
        "timestamp": datetime.datetime.now().isoformat(),
        "customer_phone": customer_phone,
        "customer_name": customer_name
    }

def get_customer_orders(phone_number):
    """
    Get previous orders for a customer by phone number
    """
    if not phone_number:
        return {"success": False, "error": "Phone number is required"}

    # Check if we need to format the phone number
    if phone_number and len(phone_number) == 10:
        # Ensure we search with a standardized format
        phone_number = phone_number.strip()

    # Find orders for this customer
    customer_orders = []

    # In a real implementation, query orders from database
    # For this demo, check the in-memory orders_history
    for order in orders_history:
        if order.get('phone_number') == phone_number:
            # Extract items from order
            items = order.get('items', [])
            for item in items:
                if isinstance(item, dict):
                    customer_orders.append({
                        'order_id': order.get('order_id', ''),
                        'timestamp': order.get('timestamp', ''),
                        'dish_name': item.get('dish_name', ''),
                        'protein': item.get('protein', ''),
                        'sauce': item.get('sauce', ''),
                        'base_type': item.get('base_type', ''),
                        'base_option': item.get('base_option', '')
                    })

    # If we found orders, return them
    if customer_orders:
        print(f"Found {len(customer_orders)} previous orders for phone: {phone_number}")
        return {"success": True, "orders": customer_orders}

    # If customer exists but no orders
    if phone_number in customers:
        print(f"Customer found but no orders for phone: {phone_number}")
        return {"success": True, "orders": []}

    # If customer not found
    print(f"No customer found for phone: {phone_number}")
    return {"success": False, "error": "Customer not found"}

def update_customer_info(customer_data):
    """
    Update or create customer information
    """
    phone_number = customer_data.get('phone_number')
    name = customer_data.get('name')

    if not phone_number:
        return {"success": False, "error": "Phone number is required"}

    # Update existing customer or create new one
    if phone_number in customers:
        customers[phone_number]['name'] = name or customers[phone_number].get('name', '')
        customers[phone_number]['last_visit'] = datetime.datetime.now().isoformat()
        print(f"Updated customer: {name}")
    else:
        customers[phone_number] = {
            'name': name or '',
            'phone_number': phone_number,
            'face_id': customer_data.get('face_id', ''),
            'visit_count': 1,
            'last_visit': datetime.datetime.now().isoformat(),
            'created_at': datetime.datetime.now().isoformat()
        }
        print(f"Created new customer: {name}")

    return {"success": True, "customer": customers[phone_number]}

# API Routes
@app.route('/api/start-order', methods=['POST', 'OPTIONS'])
def api_start_order():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    try:
        result = start_new_order()
        return jsonify({"success": True, "order_data": result})
    except Exception as e:
        print(f"Error in start_order: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health-recommendations', methods=['POST', 'OPTIONS'])
def api_health_recommendations():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    try:
        data = request.json or {}
        activity_level = data.get('activity_level', 'work')
        customer_phone = data.get('customer_phone')  # Get customer phone if provided
        result = get_health_recommendations(activity_level, customer_phone)
        return jsonify(result)
    except Exception as e:
        print(f"Error in health_recommendations: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/weather-recommendations', methods=['POST', 'OPTIONS'])
def api_weather_recommendations():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    try:
        data = request.json or {}
        customer_phone = data.get('customer_phone')  # Get customer phone if provided
        result = get_weather_recommendations(customer_phone)
        return jsonify(result)
    except Exception as e:
        print(f"Error in weather_recommendations: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dish-name', methods=['POST', 'OPTIONS'])
def api_dish_name():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    try:
        data = request.json or {}
        selections = data.get('selections', {})
        result = get_dish_name(selections)
        return jsonify(result)
    except Exception as e:
        print(f"Error in dish_name: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recommendation-feedback', methods=['POST', 'OPTIONS'])
def api_recommendation_feedback():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    try:
        data = request.json or {}
        recommendation_type = data.get('recommendation_type')
        feedback = data.get('feedback')
        customer_phone = data.get('customer_phone')  # Get customer phone if provided
        custom_suggestion = data.get('custom_suggestion')
        result = process_recommendation_feedback(recommendation_type, feedback, customer_phone, custom_suggestion)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        print(f"Error in recommendation_feedback: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/add-item', methods=['POST', 'OPTIONS'])
def api_add_item():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    try:
        data = request.json or {}
        selections = data.get('selections', {})
        result = add_order_item(selections)
        return jsonify({"success": True, "item": result})
    except Exception as e:
        print(f"Error in add_item: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/complete-order', methods=['POST', 'OPTIONS'])
def api_complete_order():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    try:
        data = request.json or {}
        customer_phone = data.get('customer_phone')
        customer_name = data.get('customer_name')
        result = complete_order(customer_phone, customer_name)
        return jsonify({"success": True, "order": result})
    except Exception as e:
        print(f"Error in complete_order: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/customer-orders', methods=['GET', 'OPTIONS'])
def api_customer_orders():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    try:
        phone = request.args.get('phone')
        result = get_customer_orders(phone)
        return jsonify(result)
    except Exception as e:
        print(f"Error in customer_orders: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/update-customer', methods=['POST', 'OPTIONS'])
def api_update_customer():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    try:
        data = request.json or {}
        result = update_customer_info(data)
        return jsonify(result)
    except Exception as e:
        print(f"Error in update_customer: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/menu-data', methods=['GET', 'OPTIONS'])
def api_menu_data():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    try:
        # Create mock menu data
        proteins = [
            {"name": "Chicken", "price": 4.50, "description": "Grilled chicken pieces"},
            {"name": "Egg", "price": 3.00, "description": "Boiled or fried egg"},
            {"name": "Paneer/Indian Cheese", "price": 4.00, "description": "Fresh Indian cheese cubes"},
            {"name": "Soya", "price": 3.50, "description": "Marinated soya chunks"},
            {"name": "Potato", "price": 2.50, "description": "Spiced potato cubes"},
            {"name": "Pepperoni", "price": 4.50, "description": "Sliced pepperoni"}
        ]

        sauces = [
            {"name": "Curry Special", "price": 1.50, "description": "House special curry sauce"},
            {"name": "Malai Masala", "price": 1.50, "description": "Creamy masala sauce"},
            {"name": "Curry Masala", "price": 1.50, "description": "Traditional curry masala"},
            {"name": "Marinara", "price": 1.00, "description": "Classic tomato sauce"},
            {"name": "Yogurt/Raita", "price": 1.00, "description": "Cooling yogurt sauce"},
            {"name": "Red Spicy Sauce", "price": 1.00, "description": "Hot chili sauce"},
            {"name": "Mint Sauce", "price": 1.00, "description": "Fresh mint sauce"},
            {"name": "Green Spicy Sauce", "price": 1.00, "description": "Spicy green chili sauce"}
        ]

        bases = {
            "Biryani": [
                {"name": "Rice", "price": 2.00, "description": "Fragrant basmati rice"}
            ],
            "Sandwich & Subs": [
                {"name": "Sourdough", "price": 2.50, "description": "Tangy artisan bread"},
                {"name": "Ciabatta", "price": 2.50, "description": "Italian white bread"},
                {"name": "White Bread", "price": 2.00, "description": "Classic soft bread"},
                {"name": "Hoagie Bun", "price": 2.50, "description": "Submarine sandwich roll"}
            ],
            "Wrap": [
                {"name": "Naan", "price": 2.00, "description": "Traditional Indian flatbread"},
                {"name": "Pita", "price": 2.00, "description": "Mediterranean pocket bread"}
            ],
            "Bowl": [
                {"name": "Bowl", "price": 2.00, "description": "Served in a bowl, no bread"}
            ]
        }

        veggies = [
            {"name": "Grilled Onion", "price": 0.50, "description": "Caramelized grilled onions", "premium": False},
            {"name": "Bell Pepper", "price": 0.50, "description": "Colorful bell peppers", "premium": False},
            {"name": "Tomato", "price": 0.50, "description": "Fresh sliced tomatoes", "premium": False},
            {"name": "Cilantro", "price": 0.50, "description": "Fresh cilantro/coriander", "premium": False},
            {"name": "Avocado", "price": 3.00, "description": "Fresh avocado slices", "premium": True},
            {"name": "Pineapple", "price": 1.00, "description": "Sweet pineapple pieces", "premium": False},
            {"name": "Spinach", "price": 1.00, "description": "Fresh spinach leaves", "premium": False},
            {"name": "Jalapeño", "price": 0.50, "description": "Spicy jalapeño slices", "premium": False}
        ]

        pricing_rules = [
            {"rule_type": "free_items", "applies_to": "veggies", "value": "5", "description": "First 5 veggies are free"},
            {"rule_type": "extra_price", "applies_to": "veggies", "value": "1.00", "description": "Price for each additional regular veggie"},
            {"rule_type": "premium_item", "applies_to": "Avocado", "value": "3.00", "description": "Premium price for avocado"}
        ]

        return jsonify({
            'success': True,
            'menu_data': {
                'proteins': proteins,
                'sauces': sauces,
                'bases': bases,
                'veggies': veggies
            },
            'pricing_rules': pricing_rules
        })
    except Exception as e:
        print(f"Error in menu_data: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return """
    <html>
        <head>
            <title>Curry Creations API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #e67e22; }
                ul { list-style-type: none; padding: 0; }
                li { padding: 8px; margin-bottom: 5px; background-color: #f5f5f5; }
                code { background-color: #f5f5f5; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>Curry Creations API Server</h1>
            <p>This server provides the API endpoints for the Agents Protin - Curry Creations application.</p>
            <h2>Available Endpoints:</h2>
            <ul>
                <li><code>POST /api/start-order</code> - Start a new order</li>
                <li><code>POST /api/health-recommendations</code> - Get health-based recommendations</li>
                <li><code>POST /api/weather-recommendations</code> - Get weather-based recommendations</li>
                <li><code>POST /api/dish-name</code> - Get dish name suggestions</li>
                <li><code>POST /api/recommendation-feedback</code> - Submit feedback on recommendations</li>
                <li><code>POST /api/add-item</code> - Add an item to the order</li>
                <li><code>POST /api/complete-order</code> - Complete the current order</li>
                <li><code>GET /api/menu-data</code> - Get menu data</li>
                <li><code>GET /api/customer-orders</code> - Get customer's previous orders</li>
                <li><code>POST /api/update-customer</code> - Update customer information</li>
            </ul>
            <p>The API is running and ready to accept requests from the frontend.</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting Curry Creations API server on http://localhost:5000")
    print("CORS is enabled for all origins")
    app.run(host='0.0.0.0', port=5000, debug=True)