# api_server.py
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime

from src.utils.llm_client import get_llm_response
import logging
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environment variables loaded from .env file")
except ImportError:
    print("python-dotenv not installed, using environment variables directly")

app = Flask(__name__)
# Enable CORS for all routes and all origins with all methods
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE"]}})

# Mock functions to simulate the kiosk
def start_new_order():
    return {
        "order_id": "ORD12345",
        "timestamp": "2023-07-25T12:00:00",
        "items": [],
        "total_price": 0.0
    }


def get_health_recommendations(activity_level):
    """Get health recommendations based on activity level."""
    try:
        # Try to get LLM recommendations
        prompt = f"""
        You are a food recommendation system for an Indian fusion restaurant called Curry Creations.
        Provide health-based food recommendations for a customer whose activity level is: {activity_level}

        Return the recommendations in this JSON format:
        {{
            "proteins": ["protein1", "protein2"],
            "sauces": ["sauce1", "sauce2"],
            "base_types": ["base_type1", "base_type2"],
            "veggies": ["veggie1", "veggie2", "veggie3"],
            "reasoning": "Explanation why these foods are good for this activity level"
        }}

        Available proteins: Chicken, Egg, Paneer/Indian Cheese, Soya, Potato, Pepperoni
        Available sauces: Curry Special, Malai Masala, Curry Masala, Marinara, Yogurt/Raita, Red Spicy Sauce, Mint Sauce, Green Spicy Sauce
        Available base types: Bowl, Wrap, Sandwich, Biryani
        Available veggies: Grilled Onion, Bell Pepper, Tomato, Cilantro, Avocado, Pineapple, Spinach, Jalapeño
        """

        llm_response = get_llm_response(prompt, max_tokens=500)

        if llm_response:
            try:
                # Parse the JSON response
                recommendations = json.loads(llm_response)

                # Add timestamp and activity level
                recommendations["timestamp"] = datetime.datetime.now().isoformat()
                recommendations["activity_level"] = activity_level

                return {"success": True, "recommendations": recommendations}
            except json.JSONDecodeError:
                # If JSON parsing fails, log error and fall back to default
                print(f"Failed to parse LLM response as JSON: {llm_response}")

        # Fall back to default recommendations if LLM fails
        default_recs = {
            "proteins": ["Chicken", "Paneer/Indian Cheese"],
            "sauces": ["Curry Special", "Mint Sauce"],
            "base_types": ["Bowl"],
            "veggies": ["Bell Pepper", "Spinach", "Tomato"],
            "reasoning": "Based on your activity level, these options provide balanced nutrition.",
            "timestamp": datetime.datetime.now().isoformat(),
            "activity_level": activity_level
        }
        return {"success": True, "recommendations": default_recs}

    except Exception as e:
        print(f"Error in health_recommendations: {e}")
        return {"success": False, "error": str(e)}, 500

def get_weather_recommendations():
    """Get weather-based recommendations."""
    try:
        # For demo purposes, simulate getting weather data
        import random
        weather_condition = random.choice(["sunny", "rainy", "cloudy", "hot", "cold"])
        temperature = random.randint(5, 35)
        current_hour = datetime.datetime.now().hour
        time_of_day = "morning" if 5 <= current_hour < 12 else "afternoon" if 12 <= current_hour < 17 else "evening"

        # Get LLM recommendations based on weather
        prompt = f"""
        You are a food recommendation system for an Indian fusion restaurant called Curry Creations.
        Provide weather-based food recommendations for a customer in these conditions:
        - Weather: {weather_condition}
        - Temperature: {temperature}°C
        - Time of day: {time_of_day}

        Return the recommendations in this JSON format:
        {{
            "base_types": ["base_type1", "base_type2"],
            "suggested_base": "most recommended base type",
            "reasoning": "Explanation why these foods are good for this weather"
        }}

        Available base types: Bowl, Wrap, Sandwich, Biryani
        """

        llm_response = get_llm_response(prompt, max_tokens=300)

        if llm_response:
            try:
                llm_recs = json.loads(llm_response)

                # Create the full response
                recommendations = {
                    "weather_condition": weather_condition,
                    "temperature": temperature,
                    "time_of_day": time_of_day,
                    "base_types": llm_recs.get("base_types", ["Bowl", "Wrap"]),
                    "suggested_base": llm_recs.get("suggested_base", "Bowl"),
                    "reasoning": llm_recs.get("reasoning", "Based on the current weather, these options would be most enjoyable."),
                    "timestamp": datetime.datetime.now().isoformat()
                }

                return {"success": True, "recommendations": recommendations}
            except json.JSONDecodeError:
                print(f"Failed to parse LLM response as JSON: {llm_response}")

        # Fall back to default recommendations
        default_recs = {
            "weather_condition": weather_condition,
            "temperature": temperature,
            "time_of_day": time_of_day,
            "base_types": ["Bowl", "Wrap"],
            "suggested_base": "Bowl" if weather_condition in ["rainy", "cold"] else "Wrap",
            "reasoning": "These options are best suited for the current weather conditions.",
            "timestamp": datetime.datetime.now().isoformat()
        }
        return {"success": True, "recommendations": default_recs}

    except Exception as e:
        print(f"Error in weather_recommendations: {e}")
        return {"success": False, "error": str(e)}, 500

def get_dish_name(selections):
    """Get creative dish names based on selections."""
    try:
        protein = selections.get('protein', '')
        base_type = selections.get('base_type', '')

        # Generate creative dish names using LLM
        prompt = f"""
        You are a creative naming specialist for an Indian fusion restaurant called Curry Creations.
        Create a fun, catchy name for a dish with these components:
        - Protein: {protein}
        - Base type: {base_type}

        Return your response in this JSON format:
        {{
            "name": "primary dish name",
            "alternatives": ["alternative name 1", "alternative name 2", "alternative name 3"],
            "format_used": "brief description of naming convention used"
        }}

        Make the name creative, fun, and memorable. Incorporate Indian fusion elements.
        """

        llm_response = get_llm_response(prompt, max_tokens=200)

        if llm_response:
            try:
                suggestions = json.loads(llm_response)
                return {"success": True, "suggestions": suggestions}
            except json.JSONDecodeError:
                print(f"Failed to parse LLM response as JSON: {llm_response}")

        # Fall back to default names
        default_names = {
            "name": f"{protein} {base_type} Delight",
            "alternatives": [
                f"Curry {protein} {base_type}",
                f"Fusion {protein} Creation",
                f"Spicy {protein} {base_type}"
            ],
            "format_used": "Standard naming format"
        }
        return {"success": True, "suggestions": default_names}

    except Exception as e:
        print(f"Error in dish_name: {e}")
        return {"success": False, "error": str(e)}, 500

def process_recommendation_feedback(rec_type, feedback, custom=None):
    return {"status": "success"}

def add_order_item(selections):
    return {
        "item_id": "ITEM1",
        "protein": selections.get("protein", ""),
        "sauce": selections.get("sauce", ""),
        "base_type": selections.get("base_type", ""),
        "base_option": selections.get("base_option", ""),
        "veggies": selections.get("veggies", []),
        "price": 12.99,
        "dish_name": selections.get("dish_name", "")
    }

def complete_order():
    return {
        "order_id": "ORD12345",
        "total_price": 12.99,
        "timestamp": "2023-07-25T12:30:00"
    }

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
        result = get_health_recommendations(activity_level)
        return jsonify({"success": True, "recommendations": result})
    except Exception as e:
        print(f"Error in health_recommendations: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/weather-recommendations', methods=['POST', 'OPTIONS'])
def api_weather_recommendations():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    try:
        result = get_weather_recommendations()
        return jsonify({"success": True, "recommendations": result})
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
        return jsonify({"success": True, "suggestions": result})
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
        custom_suggestion = data.get('custom_suggestion')
        result = process_recommendation_feedback(recommendation_type, feedback, custom_suggestion)
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
        result = complete_order()
        return jsonify({"success": True, "order": result})
    except Exception as e:
        print(f"Error in complete_order: {e}")
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
            </ul>
            <p>The API is running and ready to accept requests from the frontend.</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting Curry Creations API server on http://localhost:5000")
    print("CORS is enabled for all origins")
    app.run(host='0.0.0.0', port=5000, debug=True)