from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import csv
import os
import random
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict, Counter
import pickle

app = FastAPI(title="Food Recommender API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage
data_path = "data"
os.makedirs(data_path, exist_ok=True)

# In-memory storage for orders and customers
orders = {}
customers = {}
customer_order_history = {}  # Store customer order history
customer_dietary_profiles = {}  # Store customer dietary preferences
current_order_id = 1

# Inventory management system
class InventoryItem:
    def __init__(self, name: str, max_stock: int, prep_time_minutes: int = 0, needs_cutting: bool = False, needs_cooking: bool = False):
        self.name = name
        self.max_stock = max_stock
        self.prep_time_minutes = prep_time_minutes
        self.needs_cutting = needs_cutting
        self.needs_cooking = needs_cooking
        self.current_stock = 0
        self.status = "available"  # available, low_stock, preparing, out_of_stock
        self.prep_start_time = None
        self.estimated_ready_time = None

# Initialize inventory with realistic scenarios
inventory_items = {
    # Proteins
    "Chicken": InventoryItem("Chicken", 50, prep_time_minutes=15, needs_cutting=True, needs_cooking=True),
    "Egg": InventoryItem("Egg", 100, prep_time_minutes=5, needs_cooking=True),
    "Paneer": InventoryItem("Paneer", 30, prep_time_minutes=0, needs_cutting=True),
    "Soya": InventoryItem("Soya", 25, prep_time_minutes=10, needs_cooking=True),
    "Potato": InventoryItem("Potato", 40, prep_time_minutes=8, needs_cutting=True, needs_cooking=True),

    # Sauces
    "Curry Special": InventoryItem("Curry Special", 20, prep_time_minutes=12, needs_cooking=True),
    "Malai Masala": InventoryItem("Malai Masala", 15, prep_time_minutes=8, needs_cooking=True),
    "Curry Masala": InventoryItem("Curry Masala", 18, prep_time_minutes=10, needs_cooking=True),
    "Marinara": InventoryItem("Marinara", 12, prep_time_minutes=5, needs_cooking=True),
    "Yogurt/Raita": InventoryItem("Yogurt/Raita", 25, prep_time_minutes=0),

    # Bases
    "Rice": InventoryItem("Rice", 200, prep_time_minutes=20, needs_cooking=True),
    "Sourdough": InventoryItem("Sourdough", 30, prep_time_minutes=0),
    "Ciabatta": InventoryItem("Ciabatta", 25, prep_time_minutes=0),
    "White Bread": InventoryItem("White Bread", 40, prep_time_minutes=0),
    "Naan": InventoryItem("Naan", 35, prep_time_minutes=8, needs_cooking=True),
    "Pitta": InventoryItem("Pitta", 30, prep_time_minutes=0),

    # Veggies
    "Onion": InventoryItem("Onion", 60, prep_time_minutes=3, needs_cutting=True),
    "Tomato": InventoryItem("Tomato", 50, prep_time_minutes=2, needs_cutting=True),
    "Cucumber": InventoryItem("Cucumber", 40, prep_time_minutes=2, needs_cutting=True),
    "Lettuce": InventoryItem("Lettuce", 35, prep_time_minutes=1, needs_cutting=True),
    "Carrot": InventoryItem("Carrot", 45, prep_time_minutes=4, needs_cutting=True),

    # Garnishes
    "Cilantro": InventoryItem("Cilantro", 30, prep_time_minutes=1, needs_cutting=True),
    "Mint": InventoryItem("Mint", 25, prep_time_minutes=1, needs_cutting=True),
    "Lemon": InventoryItem("Lemon", 40, prep_time_minutes=0),
    "Chili": InventoryItem("Chili", 35, prep_time_minutes=0),
}

def initialize_inventory():
    """Initialize inventory with random stock levels for new experiment trial"""
    for item_name, item in inventory_items.items():
        # Random stock level (0 to max_stock)
        item.current_stock = random.randint(0, item.max_stock)

        # Determine status based on stock level
        if item.current_stock == 0:
            item.status = "out_of_stock"
        elif item.current_stock <= item.max_stock * 0.2:  # Less than 20%
            item.status = "low_stock"
        elif item.current_stock <= item.max_stock * 0.5:  # Less than 50%
            item.status = "preparing"
            # Set preparation start time and estimated ready time
            item.prep_start_time = datetime.now()
            item.estimated_ready_time = item.prep_start_time + timedelta(minutes=item.prep_time_minutes)
        else:
            item.status = "available"

def get_available_menu_items():
    """Get menu items filtered by inventory availability with portion sizes"""
    available_items = {
        "proteins": [],
        "sauces": [],
        "base_types": {
            "Biryani": [],
            "Sandwich & Subs": [],
            "Wrap": []
        },
        "veggies": [],
        "garnishes": []
    }

    # Check proteins
    protein_mapping = {
        "Chicken": "Chicken",
        "Egg": "Egg",
        "Paneer": "Paneer",
        "Soya": "Soya",
        "Potato": "Potato"
    }

    for menu_name, inventory_name in protein_mapping.items():
        if inventory_name in inventory_items:
            item = inventory_items[inventory_name]
            if item.status != "out_of_stock":
                base_calories = 250 if menu_name == "Chicken" else (180 if menu_name == "Egg" else (220 if menu_name == "Paneer" else (150 if menu_name == "Soya" else 200)))
                base_price = 4.50 if menu_name != "Potato" else 3.50

                available_items["proteins"].append({
                    "name": menu_name,
                    "price": base_price,
                    "calories": base_calories,
                    "status": item.status,
                    "wait_time": get_wait_time(item) if item.status == "preparing" else None,
                    "stock_level": item.current_stock,
                    "portion_sizes": {
                        "low": {
                            "name": "Small",
                            "price": round(base_price * 0.7, 2),
                            "calories": round(base_calories * 0.7),
                            "multiplier": 0.7
                        },
                        "medium": {
                            "name": "Regular",
                            "price": base_price,
                            "calories": base_calories,
                            "multiplier": 1.0
                        },
                        "extra": {
                            "name": "Large",
                            "price": round(base_price * 1.4, 2),
                            "calories": round(base_calories * 1.4),
                            "multiplier": 1.4
                        }
                    }
                })

    # Check sauces
    sauce_mapping = {
        "Curry Special": "Curry Special",
        "Malai Masala": "Malai Masala",
        "Curry Masala": "Curry Masala",
        "Marinara": "Marinara",
        "Yogurt/Raita": "Yogurt/Raita"
    }

    for menu_name, inventory_name in sauce_mapping.items():
        if inventory_name in inventory_items:
            item = inventory_items[inventory_name]
            if item.status != "out_of_stock":
                base_calories = 120 if menu_name == "Curry Special" else (150 if menu_name == "Malai Masala" else (130 if menu_name == "Curry Masala" else (80 if menu_name == "Marinara" else 60)))
                base_price = 0.00  # Sauces are typically included

                available_items["sauces"].append({
                    "name": menu_name,
                    "price": base_price,
                    "calories": base_calories,
                    "status": item.status,
                    "wait_time": get_wait_time(item) if item.status == "preparing" else None,
                    "stock_level": item.current_stock,
                    "portion_sizes": {
                        "low": {
                            "name": "Light",
                            "price": base_price,
                            "calories": round(base_calories * 0.6),
                            "multiplier": 0.6
                        },
                        "medium": {
                            "name": "Regular",
                            "price": base_price,
                            "calories": base_calories,
                            "multiplier": 1.0
                        },
                        "extra": {
                            "name": "Extra",
                            "price": base_price,
                            "calories": round(base_calories * 1.5),
                            "multiplier": 1.5
                        }
                    }
                })

    # Check bases
    base_mapping = {
        "Rice": "Rice",
        "Sourdough": "Sourdough",
        "Ciabatta": "Ciabatta",
        "White Bread": "White Bread",
        "Naan": "Naan",
        "Pitta": "Pitta"
    }

    for menu_name, inventory_name in base_mapping.items():
        if inventory_name in inventory_items:
            item = inventory_items[inventory_name]
            if item.status != "out_of_stock":
                base_item = {
                    "name": menu_name,
                    "price": 0.50 if menu_name == "Ciabatta" else 0.00,
                    "calories": 300 if menu_name == "Rice" else (220 if menu_name == "Sourdough" else (240 if menu_name == "Ciabatta" else (200 if menu_name == "White Bread" else (280 if menu_name == "Naan" else 200)))),
                    "status": item.status,
                    "wait_time": get_wait_time(item) if item.status == "preparing" else None,
                    "stock_level": item.current_stock
                }

                # Categorize by base type
                if menu_name == "Rice":
                    available_items["base_types"]["Biryani"].append(base_item)
                elif menu_name in ["Sourdough", "Ciabatta", "White Bread"]:
                    available_items["base_types"]["Sandwich & Subs"].append(base_item)
                elif menu_name in ["Naan", "Pitta"]:
                    available_items["base_types"]["Wrap"].append(base_item)

    # Check veggies
    veggie_mapping = {
        "Onion": "Onion",
        "Tomato": "Tomato",
        "Cucumber": "Cucumber",
        "Lettuce": "Lettuce",
        "Carrot": "Carrot"
    }

    for menu_name, inventory_name in veggie_mapping.items():
        if inventory_name in inventory_items:
            item = inventory_items[inventory_name]
            if item.status != "out_of_stock":
                base_price = 0.75 if menu_name == "Carrot" else 0.50
                base_calories = 40 if menu_name == "Onion" else (25 if menu_name == "Tomato" else (15 if menu_name == "Cucumber" else (5 if menu_name == "Lettuce" else 30)))

                available_items["veggies"].append({
                    "name": menu_name,
                    "price": base_price,
                    "calories": base_calories,
                    "status": item.status,
                    "wait_time": get_wait_time(item) if item.status == "preparing" else None,
                    "stock_level": item.current_stock,
                    "portion_sizes": {
                        "low": {
                            "name": "Small",
                            "price": round(base_price * 0.7, 2),
                            "calories": round(base_calories * 0.7),
                            "multiplier": 0.7
                        },
                        "medium": {
                            "name": "Regular",
                            "price": base_price,
                            "calories": base_calories,
                            "multiplier": 1.0
                        },
                        "extra": {
                            "name": "Large",
                            "price": round(base_price * 1.4, 2),
                            "calories": round(base_calories * 1.4),
                            "multiplier": 1.4
                        }
                    }
                })

    # Check garnishes
    garnish_mapping = {
        "Cilantro": "Cilantro",
        "Mint": "Mint",
        "Lemon": "Lemon",
        "Chili": "Chili"
    }

    for menu_name, inventory_name in garnish_mapping.items():
        if inventory_name in inventory_items:
            item = inventory_items[inventory_name]
            if item.status != "out_of_stock":
                base_price = 0.25
                base_calories = 5

                available_items["garnishes"].append({
                    "name": menu_name,
                    "price": base_price,
                    "calories": base_calories,
                    "status": item.status,
                    "wait_time": get_wait_time(item) if item.status == "preparing" else None,
                    "stock_level": item.current_stock,
                    "portion_sizes": {
                        "low": {
                            "name": "Small",
                            "price": round(base_price * 0.7, 2),
                            "calories": round(base_calories * 0.7),
                            "multiplier": 0.7
                        },
                        "medium": {
                            "name": "Regular",
                            "price": base_price,
                            "calories": base_calories,
                            "multiplier": 1.0
                        },
                        "extra": {
                            "name": "Large",
                            "price": round(base_price * 1.4, 2),
                            "calories": round(base_calories * 1.4),
                            "multiplier": 1.4
                        }
                    }
                })

    return available_items

def get_wait_time(item: InventoryItem) -> Optional[int]:
    """Calculate remaining wait time for preparing items"""
    if item.status != "preparing" or not item.estimated_ready_time:
        return None

    remaining = item.estimated_ready_time - datetime.now()
    if remaining.total_seconds() > 0:
        return int(remaining.total_seconds() / 60)  # Return minutes
    else:
        # Item is ready, update status
        item.status = "available"
        item.prep_start_time = None
        item.estimated_ready_time = None
        return None

def calculate_preparation_time(order_items: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate preparation time based on inventory status and order complexity"""
    base_time = 8  # Base preparation time
    complexity_multiplier = 1.0
    additional_wait_time = 0
    unavailable_items = []
    low_stock_items = []
    preparing_items = []

    # Check each selected item
    for category, items in order_items.items():
        # Always treat as list for uniformity
        if not isinstance(items, list):
            items = [items]
        for item in items:
            # Extract name if dict, else use as string
            if isinstance(item, dict):
                item_name = item.get("name", "")
            else:
                item_name = str(item)
            if not item_name:
                continue
            if item_name in inventory_items:
                inv_item = inventory_items[item_name]
                if inv_item.status == "out_of_stock":
                    unavailable_items.append(item_name)
                elif inv_item.status == "low_stock":
                    low_stock_items.append(item_name)
                    complexity_multiplier += 0.2
                elif inv_item.status == "preparing":
                    preparing_items.append(item_name)
                    wait_time = get_wait_time(inv_item)
                    if wait_time:
                        additional_wait_time = max(additional_wait_time, wait_time)
                    complexity_multiplier += 0.3
                else:
                    if inv_item.needs_cutting:
                        complexity_multiplier += 0.1
                    if inv_item.needs_cooking:
                        complexity_multiplier += 0.2

    # Calculate queue impact
    queue_position = random.randint(1, 50)
    if queue_position <= 5:
        queue_multiplier = 1.0
        queue_wait = queue_position * 1.5
    elif queue_position <= 15:
        queue_multiplier = 1.2
        queue_wait = 7.5 + (queue_position - 5) * 1.2
    elif queue_position <= 30:
        queue_multiplier = 1.5
        queue_wait = 20 + (queue_position - 15) * 1.0
    else:
        queue_multiplier = 2.0
        queue_wait = 35 + (queue_position - 30) * 0.8

    total_preparation = (base_time * complexity_multiplier * queue_multiplier) + queue_wait + additional_wait_time
    ready_time = datetime.now() + timedelta(minutes=int(total_preparation))

    return {
        "total_minutes": int(total_preparation),
        "ready_time": ready_time.strftime("%H:%M"),
        "formatted_duration": f"{int(total_preparation//60):02d}:{int(total_preparation%60):02d}",
        "queue_position": queue_position,
        "complexity_multiplier": round(complexity_multiplier, 2),
        "queue_multiplier": round(queue_multiplier, 2),
        "additional_wait_time": additional_wait_time,
        "unavailable_items": unavailable_items,
        "low_stock_items": low_stock_items,
        "preparing_items": preparing_items
    }

# Initialize inventory on startup
initialize_inventory()
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Models
class CustomerData(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class DietaryProfile(BaseModel):
    restrictions: List[str] = []
    allergies: List[str] = []
    preferences: List[str] = []

class ExperimentSubmission(BaseModel):
    experiment_number: str
    participant_name: str
    participant_email: str
    responses: Dict[str, Any]

class OrderItem(BaseModel):
    selections: Dict[str, Any]

# Removed old request models - no longer needed
# class HealthRecommendationsRequest(BaseModel):
# class WeatherRecommendationsRequest(BaseModel):
# class DishNameRequest(BaseModel):
# class FeedbackRequest(BaseModel):

class CompleteOrderRequest(BaseModel):
    customer_phone: Optional[str] = None
    customer_name: Optional[str] = None

class UpdateCustomerRequest(BaseModel):
    name: str
    email: str
    phone: str

# Basic endpoints
@app.get("/")
async def root():
    return {"message": "Food Recommender API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/agent-status")
async def get_agent_status():
    return {
        "agents": {
            "context_intelligence": {"status": "active", "last_activity": datetime.now().isoformat(), "activity_count": 0},
            "preference_learning": {"status": "active", "last_activity": datetime.now().isoformat(), "activity_count": 0},
            "preparation_time": {"status": "active", "last_activity": datetime.now().isoformat(), "activity_count": 0}
        },
        "timestamp": datetime.now().isoformat()
    }

# Inventory management endpoints
@app.post("/api/inventory/initialize")
async def initialize_inventory_endpoint():
    """Initialize inventory with random stock levels for new experiment trial"""
    initialize_inventory()
    return {
        "message": "Inventory initialized with random stock levels",
        "timestamp": datetime.now().isoformat(),
        "inventory_summary": {
            "total_items": len(inventory_items),
            "out_of_stock": len([item for item in inventory_items.values() if item.status == "out_of_stock"]),
            "low_stock": len([item for item in inventory_items.values() if item.status == "low_stock"]),
            "preparing": len([item for item in inventory_items.values() if item.status == "preparing"]),
            "available": len([item for item in inventory_items.values() if item.status == "available"])
        }
    }

@app.get("/api/inventory/status")
async def get_inventory_status():
    """Get current inventory status for all items"""
    status = {}
    for item_name, item in inventory_items.items():
        status[item_name] = {
            "current_stock": item.current_stock,
            "max_stock": item.max_stock,
            "status": item.status,
            "prep_time_minutes": item.prep_time_minutes,
            "needs_cutting": item.needs_cutting,
            "needs_cooking": item.needs_cooking,
            "wait_time": get_wait_time(item) if item.status == "preparing" else None,
            "estimated_ready_time": item.estimated_ready_time.isoformat() if item.estimated_ready_time else None
        }
    return status

# Order management endpoints
@app.post("/api/start-order")
async def start_order():
    global current_order_id
    order_id = f"order_{current_order_id}"
    current_order_id += 1

    orders[order_id] = {
        "id": order_id,
        "items": [],
        "total": 0.0,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }

    return {"order_id": order_id, "message": "Order started successfully"}

@app.post("/api/add-item")
async def add_item(request: OrderItem):
    # For now, just return success - you can implement actual order logic later
    return {"message": "Item added successfully", "selections": request.selections}

@app.post("/api/complete-order")
async def complete_order(request: CompleteOrderRequest):
    # For now, just return success - you can implement actual completion logic later
    return {
        "message": "Order completed successfully",
        "customer_phone": request.customer_phone,
        "customer_name": request.customer_name
    }

# Customer management endpoints
def generate_personalized_dish_suggestion(order_history, dietary_profile, inventory):
    """Use OpenAI to generate a personalized dish suggestion based on history, dietary, and inventory"""
    try:
        if not OPENAI_API_KEY:
            raise Exception("No OpenAI API key")
        prompt = (
            "You are a food recommendation AI. Given the user's order history, dietary profile, and current inventory, suggest a personalized dish that is available now.\n"
            f"Order history: {json.dumps(order_history)}\n"
            f"Dietary profile: {json.dumps(dietary_profile)}\n"
            f"Inventory: {json.dumps({k:v.current_stock for k,v in inventory.items()})}\n"
            "Respond with a JSON object: {\"dish_name\":..., \"reason\":...}"
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        content = response.choices[0].message['content']
        # Try to parse JSON from the response
        try:
            suggestion = json.loads(content)
        except Exception:
            suggestion = {"dish_name": content.strip(), "reason": "AI generated"}
        return suggestion
    except Exception as e:
        # Fallback: pick favorite or available
        favorites = get_favorite_items(order_history)
        available_proteins = [k for k,v in inventory.items() if v.current_stock > 0]
        dish = favorites[0]['name'] if favorites else (available_proteins[0] if available_proteins else "Chef's Special")
        return {"dish_name": dish, "reason": f"Fallback: {str(e)}"}

@app.get("/api/customer-orders")
async def get_customer_orders(phone: str):
    """Get customer order history and dietary profile, plus personalized dish suggestion"""
    customer_orders = customer_order_history.get(phone, [])
    dietary_profile = customer_dietary_profiles.get(phone, {
        "restrictions": [],
        "allergies": [],
        "preferences": []
    })
    # Personalized dish suggestion
    personalized_dish = generate_personalized_dish_suggestion(
        customer_orders, dietary_profile, inventory_items
    )
    return {
        "customer_phone": phone,
        "has_previous_orders": len(customer_orders) > 0,
        "total_orders": len(customer_orders),
        "recent_orders": customer_orders[-5:] if customer_orders else [],  # Last 5 orders
        "favorite_items": get_favorite_items(customer_orders),
        "dietary_profile": dietary_profile,
        "personalized_dish_suggestion": personalized_dish
    }

def get_favorite_items(orders):
    """Extract favorite items from order history"""
    item_counts = {}
    for order in orders:
        for item in order.get("items", []):
            try:
                if isinstance(item, dict):
                    item_name = item.get("name", "")
                else:
                    item_name = str(item)
                if item_name:
                    item_counts[item_name] = item_counts.get(item_name, 0) + 1
            except Exception:
                continue
    # Return top 3 favorite items
    sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"name": item[0], "count": item[1]} for item in sorted_items[:3]]

@app.post("/api/customer/save-order")
async def save_customer_order(request: Request):
    """Save customer order to history"""
    data = await request.json()
    phone = data.get("customer_phone")
    order_details = data.get("order_details", {})

    if not phone:
        raise HTTPException(status_code=400, detail="Customer phone required")

    # Create order record
    order_record = {
        "order_id": f"order_{len(customer_order_history.get(phone, [])) + 1}",
        "timestamp": datetime.now().isoformat(),
        "items": order_details,
        "total_price": calculate_order_price(order_details),
        "total_calories": calculate_order_calories(order_details)
    }

    # Save to customer history
    if phone not in customer_order_history:
        customer_order_history[phone] = []
    customer_order_history[phone].append(order_record)

    return {"message": "Order saved to customer history", "order_id": order_record["order_id"]}

@app.post("/api/customer/save-dietary")
async def save_customer_dietary(request: Request):
    """Save customer dietary preferences"""
    data = await request.json()
    phone = data.get("customer_phone")
    restrictions = data.get("restrictions", [])
    allergens = data.get("allergens", [])

    if not phone:
        raise HTTPException(status_code=400, detail="Customer phone required")

    customer_dietary_profiles[phone] = {
        "restrictions": restrictions,
        "allergies": allergens,
        "updated_at": datetime.now().isoformat()
    }

    return {"message": "Dietary preferences saved"}

def calculate_order_price(order_details):
    """Calculate total price of order"""
    total = 0.0

    # Protein prices
    proteins = order_details.get("protein", [])
    for protein in proteins:
        if isinstance(protein, dict):
            total += protein.get("price", 4.50)
        else:
            # Default protein price
            total += 4.50

    # Base prices
    base_option = order_details.get("base_option", "")
    if base_option == "Ciabatta":
        total += 0.50

    # Veggie prices
    veggies = order_details.get("veggies", [])
    for veggie in veggies:
        if isinstance(veggie, dict):
            total += veggie.get("price", 0.50)
        else:
            # Default veggie price
            total += 0.50

    # Garnish prices
    garnishes = order_details.get("garnishes", [])
    for garnish in garnishes:
        if isinstance(garnish, dict):
            total += garnish.get("price", 0.25)
        else:
            # Default garnish price
            total += 0.25

    return round(total, 2)

def calculate_order_calories(order_details):
    """Calculate total calories of order"""
    total = 0

    # Protein calories
    proteins = order_details.get("protein", [])
    for protein in proteins:
        if isinstance(protein, dict):
            total += protein.get("calories", 250)
        else:
            # Default protein calories
            total += 250

    # Base calories
    base_option = order_details.get("base_option", "")
    if base_option == "Rice":
        total += 300
    elif base_option == "Sourdough":
        total += 220
    elif base_option == "Ciabatta":
        total += 240
    elif base_option == "White Bread":
        total += 200
    elif base_option == "Naan":
        total += 280
    elif base_option == "Pitta":
        total += 200

    # Sauce calories
    sauces = order_details.get("sauce", [])
    for sauce in sauces:
        if isinstance(sauce, dict):
            total += sauce.get("calories", 120)
        else:
            # Default sauce calories
            total += 120

    # Veggie calories
    veggies = order_details.get("veggies", [])
    for veggie in veggies:
        if isinstance(veggie, dict):
            total += veggie.get("calories", 30)
        else:
            # Default veggie calories
            total += 30

    # Garnish calories
    garnishes = order_details.get("garnishes", [])
    for garnish in garnishes:
        if isinstance(garnish, dict):
            total += garnish.get("calories", 5)
        else:
            # Default garnish calories
            total += 5

    return total

@app.post("/api/update-customer")
async def update_customer(request: UpdateCustomerRequest):
    customers[request.phone] = {
        "name": request.name,
        "email": request.email,
        "phone": request.phone,
        "updated_at": datetime.now().isoformat()
    }
    return {"message": "Customer updated successfully", "customer": customers[request.phone]}

# ML recommendation endpoints (stub implementations)
@app.post("/api/ml/recommendations")
async def get_ml_recommendations(request: Request):
    data = await request.json()
    return {
        "recommendations": [
            {"name": "ML Recommended Dish 1", "confidence": 0.85, "reason": "Based on your preferences"},
            {"name": "ML Recommended Dish 2", "confidence": 0.78, "reason": "Similar to your favorites"}
        ],
        "user_id": data.get("user_id"),
        "context": data.get("context")
    }

@app.post("/api/ml/feedback")
async def submit_ml_feedback(request: Request):
    data = await request.json()
    return {"message": "ML feedback submitted successfully"}

@app.get("/api/ml/preferences/{user_id}")
async def get_user_ml_preferences(user_id: str):
    return {
        "user_id": user_id,
        "preferences": {
            "spice_level": "medium",
            "protein_preference": "chicken",
            "cuisine_style": "indian"
        }
    }

@app.post("/api/ml/analyze-feedback")
async def analyze_text_feedback(request: Request):
    data = await request.json()
    return {
        "sentiment": "positive",
        "keywords": ["delicious", "spicy"],
        "suggestions": ["Try our new spicy variant"]
    }

@app.get("/api/ml/insights")
async def get_ml_model_insights():
    return {
        "model_performance": {
            "accuracy": 0.85,
            "precision": 0.82,
            "recall": 0.88
        },
        "popular_items": ["Chicken Curry", "Paneer Masala", "Biryani"]
    }

@app.post("/api/ml/retrain")
async def retrain_ml_models():
    return {"message": "ML models retraining initiated"}

# Add preference learning system
class PreferenceLearningSystem:
    def __init__(self, data_path="data/"):
        self.data_path = data_path
        self.user_preferences = defaultdict(dict)
        self.item_features = {}
        self.user_order_history = defaultdict(list)
        self.collaborative_matrix = {}
        self.preference_model_path = os.path.join(data_path, "preference_model.pkl")
        self.load_preference_model()

    def load_preference_model(self):
        """Load existing preference model"""
        try:
            if os.path.exists(self.preference_model_path):
                with open(self.preference_model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.user_preferences = data.get('user_preferences', defaultdict(dict))
                    self.item_features = data.get('item_features', {})
                    self.collaborative_matrix = data.get('collaborative_matrix', {})
                print(f"Loaded preference model with {len(self.user_preferences)} users")
        except Exception as e:
            print(f"Could not load preference model: {e}")

    def save_preference_model(self):
        """Save preference model"""
        try:
            os.makedirs(self.data_path, exist_ok=True)
            data = {
                'user_preferences': dict(self.user_preferences),
                'item_features': self.item_features,
                'collaborative_matrix': self.collaborative_matrix
            }
            with open(self.preference_model_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Could not save preference model: {e}")

    def extract_item_features(self, item_name):
        """Extract features from item name for similarity calculation"""
        features = {
            'protein': any(protein in item_name.lower() for protein in ['chicken', 'paneer', 'egg', 'soya', 'potato']),
            'spice_level': any(spice in item_name.lower() for spice in ['spicy', 'hot', 'mild', 'curry']),
            'cuisine_type': any(cuisine in item_name.lower() for cuisine in ['indian', 'biryani', 'curry', 'masala']),
            'base_type': any(base in item_name.lower() for base in ['rice', 'bread', 'naan', 'wrap', 'bowl']),
            'vegetarian': any(veg in item_name.lower() for veg in ['paneer', 'soya', 'potato', 'vegetable'])
        }
        return features

    def update_user_preferences(self, user_id, order_details, feedback=None):
        """Update user preferences based on order and feedback"""
        try:
            # Extract order features
            order_features = self.extract_order_features(order_details)

            # Update user preferences
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {
                    'protein_preferences': defaultdict(float),
                    'spice_preferences': defaultdict(float),
                    'cuisine_preferences': defaultdict(float),
                    'base_preferences': defaultdict(float),
                    'order_count': 0,
                    'last_order': None
                }

            user_prefs = self.user_preferences[user_id]

            # Update preferences based on order
            for feature, value in order_features.items():
                if feature in user_prefs:
                    if isinstance(user_prefs[feature], defaultdict):
                        user_prefs[feature][value] += 1.0
                    else:
                        user_prefs[feature] = value

            # Update order count and last order
            user_prefs['order_count'] += 1
            user_prefs['last_order'] = datetime.now().isoformat()

            # Store order in history
            self.user_order_history[user_id].append({
                'order_details': order_details,
                'features': order_features,
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            })

            # Keep only last 20 orders for memory efficiency
            if len(self.user_order_history[user_id]) > 20:
                self.user_order_history[user_id] = self.user_order_history[user_id][-20:]

            # Save updated model
            self.save_preference_model()

            return True

        except Exception as e:
            print(f"Error updating user preferences: {e}")
            return False

    def extract_order_features(self, order_details):
        """Extract features from order details"""
        features = {}

        # Extract protein preference
        protein = order_details.get('protein', '')
        if protein:
            features['protein'] = protein.lower()

        # Extract spice level from sauce
        sauce = order_details.get('sauce', '')
        if 'curry' in sauce.lower():
            features['spice_level'] = 'spicy'
        elif 'malai' in sauce.lower():
            features['spice_level'] = 'mild'
        else:
            features['spice_level'] = 'medium'

        # Extract base type
        base = order_details.get('base_type', '')
        if base:
            features['base_type'] = base.lower()

        # Determine cuisine type
        if any(indian in str(order_details).lower() for indian in ['curry', 'biryani', 'masala', 'paneer']):
            features['cuisine_type'] = 'indian'
        else:
            features['cuisine_type'] = 'general'

        return features

    def get_personalized_recommendations(self, user_id, current_context=None, n_recommendations=3):
        """Get personalized recommendations based on user preferences"""
        try:
            if user_id not in self.user_preferences:
                return self.get_popular_recommendations(n_recommendations)

            user_prefs = self.user_preferences[user_id]
            recommendations = []

            # Get user's most preferred features
            preferred_protein = max(user_prefs['protein_preferences'].items(), key=lambda x: x[1])[0] if user_prefs['protein_preferences'] else 'chicken'
            preferred_spice = max(user_prefs['spice_preferences'].items(), key=lambda x: x[1])[0] if user_prefs['spice_preferences'] else 'medium'
            preferred_base = max(user_prefs['base_preferences'].items(), key=lambda x: x[1])[0] if user_prefs['base_preferences'] else 'rice'

            # Generate personalized recommendations
            if preferred_protein == 'chicken':
                recommendations.append({
                    "type": "preference_learning",
                    "title": "Your Favorite Protein",
                    "message": f"Based on your {user_prefs['order_count']} previous orders, you love {preferred_protein.title()} dishes",
                    "priority": "high",
                    "confidence": min(0.9, user_prefs['order_count'] * 0.1),
                    "reasoning": f"You've ordered {preferred_protein} {user_prefs['protein_preferences'][preferred_protein]:.0f} times"
                })

            if preferred_spice == 'spicy':
                recommendations.append({
                    "type": "preference_learning",
                    "title": "Spice Level Preference",
                    "message": f"You prefer {preferred_spice} dishes - try our hottest curry options",
                    "priority": "medium",
                    "confidence": min(0.8, user_prefs['order_count'] * 0.08),
                    "reasoning": f"Your spice preference: {preferred_spice}"
                })

            # Collaborative filtering: find similar users
            similar_users = self.find_similar_users(user_id)
            if similar_users:
                recommendations.append({
                    "type": "preference_learning",
                    "title": "Popular Among Similar Users",
                    "message": "Users with similar tastes love our signature dishes",
                    "priority": "medium",
                    "confidence": 0.7,
                    "reasoning": f"Based on {len(similar_users)} similar users"
                })

            # Context-aware recommendations
            if current_context:
                time_of_day = current_context.get('time_of_day', 'afternoon')
                if time_of_day == 'morning' and user_prefs['order_count'] > 0:
                    recommendations.append({
                        "type": "preference_learning",
                        "title": "Morning Preference",
                        "message": "Perfect morning fuel based on your preferences",
                        "priority": "low",
                        "confidence": 0.6,
                        "reasoning": "Optimized for morning consumption"
                    })

            return recommendations[:n_recommendations]

        except Exception as e:
            print(f"Error getting personalized recommendations: {e}")
            return self.get_popular_recommendations(n_recommendations)

    def find_similar_users(self, user_id, n_similar=3):
        """Find users with similar preferences using collaborative filtering"""
        try:
            if user_id not in self.user_preferences:
                return []

            target_user = self.user_preferences[user_id]
            similarities = []

            for other_user_id, other_user in self.user_preferences.items():
                if other_user_id == user_id:
                    continue

                # Calculate similarity based on preferences
                similarity = 0
                common_features = 0

                for feature in ['protein_preferences', 'spice_preferences', 'base_preferences']:
                    if feature in target_user and feature in other_user:
                        target_items = set(target_user[feature].keys())
                        other_items = set(other_user[feature].keys())
                        if target_items and other_items:
                            common = len(target_items.intersection(other_items))
                            total = len(target_items.union(other_items))
                            if total > 0:
                                similarity += common / total
                                common_features += 1

                if common_features > 0:
                    avg_similarity = similarity / common_features
                    similarities.append((other_user_id, avg_similarity))

            # Return top similar users
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [user_id for user_id, sim in similarities[:n_similar] if sim > 0.3]

        except Exception as e:
            print(f"Error finding similar users: {e}")
            return []

    def get_popular_recommendations(self, n_recommendations=3):
        """Get popular recommendations when no user data is available"""
        return [
            {
                "type": "preference_learning",
                "title": "Most Popular Choice",
                "message": "Our most loved dish by all customers",
                "priority": "medium",
                "confidence": 0.6,
                "reasoning": "Based on overall popularity"
            },
            {
                "type": "preference_learning",
                "title": "Chef's Recommendation",
                "message": "Our signature dish with perfect balance",
                "priority": "medium",
                "confidence": 0.7,
                "reasoning": "Chef's special selection"
            }
        ]

# Initialize preference learning system
preference_learning_system = PreferenceLearningSystem(data_path)

# Update the agent recommendations endpoint
@app.post("/api/agent-recommendations")
async def get_agent_recommendations(request: Request):
    """Get recommendations from all 3 agents working together with inventory-aware preparation time"""
    data = await request.json()

    # Simulate agent processing with realistic data
    user_id = data.get("user_id", "user_123")
    context = data.get("context", {})
    order_details = data.get("order_details", {})

    # Calculate preparation time based on inventory status
    prep_time_data = calculate_preparation_time(order_details)

    # Generate agent-specific recommendations
    context_recommendations = [
        {
            "type": "context_intelligence",
            "title": "Inventory-Aware Suggestion",
            "message": f"Queue position: #{prep_time_data['queue_position']}",
            "priority": "medium"
        }
    ]

    if prep_time_data['unavailable_items']:
        context_recommendations.append({
            "type": "context_intelligence",
            "title": "Unavailable Items",
            "message": f"These items are currently out of stock: {', '.join(prep_time_data['unavailable_items'])}",
            "priority": "high"
        })

    if prep_time_data['preparing_items']:
        context_recommendations.append({
            "type": "context_intelligence",
            "title": "Items Being Prepared",
            "message": f"These items are being prepared: {', '.join(prep_time_data['preparing_items'])}",
            "priority": "medium"
        })

    # REAL Preference Learning - not static messages
    preference_recommendations = preference_learning_system.get_personalized_recommendations(
        user_id, context, n_recommendations=3
    )

    preparation_recommendations = [
        {
            "type": "preparation_time",
            "title": "Preparation Time Estimate",
            "message": f"Your order will be ready at {prep_time_data['ready_time']}",
            "priority": "high"
        }
    ]

    if prep_time_data['additional_wait_time'] > 0:
        preparation_recommendations.append({
            "type": "preparation_time",
            "title": "Additional Wait Time",
            "message": f"Some ingredients need {prep_time_data['additional_wait_time']} more minutes to prepare",
            "priority": "high"
        })

    # Suggest refreshment drinks based on wait time
    refreshment_suggestions = []
    if prep_time_data['total_minutes'] > 20:
        refreshment_suggestions = [
            {"name": "Masala Chai", "price": 3.50, "reason": "Perfect for longer waits"},
            {"name": "Mango Lassi", "price": 4.00, "reason": "Refreshing yogurt drink"}
        ]
    elif prep_time_data['total_minutes'] > 15:
        refreshment_suggestions = [
            {"name": "Sweet Lassi", "price": 3.00, "reason": "Classic Indian drink"},
            {"name": "Masala Tea", "price": 2.50, "reason": "Quick spiced tea"}
        ]
    else:
        refreshment_suggestions = [
            {"name": "Water", "price": 1.00, "reason": "Stay hydrated"},
            {"name": "Soda", "price": 2.00, "reason": "Quick refreshment"}
        ]

    return {
        "success": True,
        "agents_called": ["context_intelligence", "preference_learning", "preparation_time"],
        "preparation_time": prep_time_data,
        "recommendations": {
            "context_intelligence": context_recommendations,
            "preference_learning": preference_recommendations,
            "preparation_time": preparation_recommendations
        },
        "refreshment_suggestions": refreshment_suggestions,
        "optimization_strategies": [
            {
                "type": "queue_optimization",
                "title": "Queue Management",
                "message": f"You are #{prep_time_data['queue_position']} in the queue",
                "suggestions": ["Consider simpler order", "Add refreshment drink"]
            }
        ] if prep_time_data['queue_position'] > 20 else []
    }

# Add endpoint to update user preferences
@app.post("/api/preferences/update")
async def update_user_preferences(request: Request):
    """Update user preferences based on order and feedback"""
    data = await request.json()
    user_id = data.get("user_id")
    order_details = data.get("order_details", {})
    feedback = data.get("feedback")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    success = preference_learning_system.update_user_preferences(user_id, order_details, feedback)

    return {
        "success": success,
        "user_id": user_id,
        "preferences_updated": success,
        "timestamp": datetime.now().isoformat()
    }

# Add endpoint to get user preferences
@app.get("/api/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get user preferences and order history"""
    if user_id in preference_learning_system.user_preferences:
        user_prefs = preference_learning_system.user_preferences[user_id]
        order_history = preference_learning_system.user_order_history[user_id]

        return {
            "user_id": user_id,
            "preferences": dict(user_prefs),
            "order_count": user_prefs.get('order_count', 0),
            "last_order": user_prefs.get('last_order'),
            "order_history": order_history[-5:] if order_history else [],  # Last 5 orders
            "similar_users": preference_learning_system.find_similar_users(user_id)
        }
    else:
        return {
            "user_id": user_id,
            "preferences": None,
            "order_count": 0,
            "message": "No preference data available"
        }

# Dietary restrictions endpoints
@app.post("/api/dietary/restrictions/{user_id}")
async def set_user_dietary_restrictions(user_id: str, request: Request):
    data = await request.json()
    return {"message": "Dietary restrictions updated", "restrictions": data.get("restrictions", [])}

@app.post("/api/dietary/allergens/{user_id}")
async def set_user_allergens(user_id: str, request: Request):
    data = await request.json()
    return {"message": "Allergens updated", "allergens": data.get("allergens", [])}

@app.get("/api/dietary/profile/{user_id}")
async def get_user_dietary_profile(user_id: str):
    return {
        "restrictions": ["vegetarian"],
        "allergies": ["nuts"],
        "preferences": ["spicy"]
    }

@app.get("/api/dietary/safe-options/{user_id}")
async def get_safe_options(user_id: str, category: str):
    safe_options = {
        "proteins": ["Paneer", "Soya"],
        "sauces": ["Curry Special", "Marinara"],
        "bases": ["Rice", "Naan"]
    }
    return {"safe_options": safe_options.get(category, [])}

@app.post("/api/dietary/filter-recommendations/{user_id}")
async def filter_recommendations(user_id: str, request: Request):
    data = await request.json()
    recommendations = data.get("recommendations", [])
    # Filter based on dietary restrictions (simplified)
    return {"filtered_recommendations": recommendations[:3]}

@app.get("/api/dietary/ingredient-info")
async def get_ingredient_info(item_name: str):
    return {
        "name": item_name,
        "allergens": [],
        "dietary_info": "vegetarian",
        "calories": 200
    }

@app.delete("/api/dietary/restrictions/{user_id}")
async def clear_user_dietary_restrictions(user_id: str):
    return {"message": "Dietary restrictions cleared"}

@app.delete("/api/dietary/allergens/{user_id}")
async def clear_user_allergens(user_id: str):
    return {"message": "Allergens cleared"}

@app.get("/api/dietary/stats")
async def get_dietary_stats():
    return {
        "total_users": 100,
        "vegetarian_users": 45,
        "vegan_users": 15,
        "allergy_aware_users": 30
    }

@app.get("/api/menu-data")
async def get_menu_data():
    """Get menu data filtered by inventory availability"""
    return get_available_menu_items()

@app.get("/api/dietary/restrictions/available")
async def get_available_restrictions():
    return {
        "data": {
            "restrictions": {
                "vegan": {"description": "No animal products", "allowed_proteins": ["Tofu", "Soya"]},
                "vegetarian": {"description": "No meat, fish, or eggs", "allowed_proteins": ["Paneer", "Soya", "Potato"]},
                "lacto_vegetarian": {"description": "Dairy allowed, no meat/fish/eggs", "allowed_proteins": ["Paneer", "Soya", "Potato"]},
                "ovo_vegetarian": {"description": "Eggs allowed, no meat/fish/dairy", "allowed_proteins": ["Egg", "Soya", "Potato"]},
                "lacto_ovo_vegetarian": {"description": "Dairy and eggs allowed, no meat/fish", "allowed_proteins": ["Paneer", "Egg", "Soya", "Potato"]},
                "halal": {"description": "Halal certified only", "allowed_proteins": ["Chicken", "Egg", "Paneer", "Soya", "Potato"]},
                "no_beef": {"description": "No beef products", "allowed_proteins": ["Chicken", "Egg", "Paneer", "Soya", "Potato"]},
                "no_pork": {"description": "No pork products", "allowed_proteins": ["Chicken", "Egg", "Paneer", "Soya", "Potato"]}
            }
        }
    }

@app.get("/api/dietary/allergens/available")
async def get_available_allergens():
    return {
        "data": {
            "allergens": {
                "dairy": {"ingredients": ["Paneer", "Cheese", "Yogurt"]},
                "eggs": {"ingredients": ["Egg"]},
                "nuts": {"ingredients": ["Cashew", "Almond"]},
                "peanuts": {"ingredients": ["Peanut"]},
                "soy": {"ingredients": ["Soya"]},
                "gluten": {"ingredients": ["Bread", "Naan"]},
                "shellfish": {"ingredients": []},
                "fish": {"ingredients": []},
                "sesame": {"ingredients": ["Sesame Seeds"]}
            }
        }
    }

# Experiment endpoints
def log_experiment_to_csv(participant_name, participant_email, experiment_number, responses):
    """Log experiment data to CSV with step timings and selections"""
    log_path = os.path.join(data_path, "experiment_log.csv")
    file_exists = os.path.exists(log_path)
    # Extract step timings if present
    step_timings = responses.get("step_timings", {})
    # Flatten step timings for CSV
    step_fields = []
    step_values = []
    for step, timing in step_timings.items():
        for key in ["start", "end", "duration"]:
            field = f"{step}_{key}"
            step_fields.append(field)
            step_values.append(timing.get(key, ""))
    # Total time
    total_time = responses.get("total_time", "")
    # All selections/responses as JSON
    selections_json = json.dumps(responses.get("selections", responses), ensure_ascii=False)
    # Submission timestamp
    submission_time = datetime.now().isoformat()
    # CSV header
    fieldnames = [
        "experiment_number", "participant_name", "participant_email", "total_time", "submission_time"
    ] + step_fields + ["selections_json"]
    # CSV row
    row = [
        experiment_number, participant_name, participant_email, total_time, submission_time
    ] + step_values + [selections_json]
    # Write to CSV
    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(fieldnames)
        writer.writerow(row)

# Participant registration models
class ParticipantRegistration(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    age: int
    gender: str
    country: str
    ethnicity: Optional[str] = None
    occupation: Optional[str] = None
    tech_proficiency: Optional[str] = "intermediate"
    ordering_frequency: Optional[str] = "medium"
    personality_traits: Optional[Dict[str, float]] = {}
    activity_preferences: Optional[List[str]] = ["work", "study"]
    protein_preferences: Optional[List[str]] = ["Chicken"]
    feedback_pattern: Optional[str] = "selective"
    baseline_emotions: Optional[List[str]] = ["neutral"]
    decision_style: Optional[str] = "cautious_deliberate"

class ParticipantResponse(BaseModel):
    participant_id: str
    experiment_number: str
    nasa_tlx_scores: Optional[Dict[str, int]] = None
    sus_scores: Optional[Dict[str, int]] = None
    satisfaction_scores: Optional[Dict[str, int]] = None
    task_completion_time: Optional[float] = None
    errors_made: Optional[int] = None
    decision_changes: Optional[int] = None
    agent_interactions: Optional[Dict[str, Any]] = None
    comments: Optional[str] = None

# Global storage for registered participants
registered_participants = {}
participant_counter = 1

@app.post("/api/participants/register")
async def register_participant(registration: ParticipantRegistration):
    """Register a new participant for the experiment"""
    global participant_counter

    # Validate age
    if registration.age < 18 or registration.age > 100:
        raise HTTPException(status_code=400, detail="Age must be between 18 and 100")

    # Check if email already registered
    for participant in registered_participants.values():
        if participant["email"] == registration.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Generate participant ID
    participant_id = f"P{participant_counter:03d}"
    participant_counter += 1

    # Create participant record
    participant = {
        "participant_id": participant_id,
        "name": registration.name,
        "email": registration.email,
        "phone": registration.phone,
        "age": registration.age,
        "gender": registration.gender,
        "country": registration.country,
        "ethnicity": registration.ethnicity,
        "occupation": registration.occupation,
        "tech_proficiency": registration.tech_proficiency,
        "ordering_frequency": registration.ordering_frequency,
        "personality_traits": registration.personality_traits,
        "activity_preferences": registration.activity_preferences,
        "protein_preferences": registration.protein_preferences,
        "feedback_pattern": registration.feedback_pattern,
        "baseline_emotions": registration.baseline_emotions,
        "decision_style": registration.decision_style,
        "registration_time": datetime.now().isoformat(),
        "experiments_completed": 0,
        "status": "registered"
    }

    registered_participants[participant_id] = participant

    # Save to CSV
    participants_file = os.path.join(data_path, "registered_participants.csv")
    file_exists = os.path.exists(participants_file)

    with open(participants_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "participant_id", "name", "email", "phone", "age", "gender", "country",
                "ethnicity", "occupation", "tech_proficiency", "ordering_frequency",
                "registration_time", "status"
            ])
        writer.writerow([
            participant_id, registration.name, registration.email, registration.phone,
            registration.age, registration.gender, registration.country,
            registration.ethnicity, registration.occupation, registration.tech_proficiency,
            registration.ordering_frequency, participant["registration_time"], "registered"
        ])

    return {
        "success": True,
        "participant_id": participant_id,
        "message": f"Participant {registration.name} registered successfully"
    }

@app.get("/api/participants")
async def get_participants():
    """Get list of all registered participants"""
    return {
        "participants": list(registered_participants.values()),
        "total_count": len(registered_participants)
    }

@app.get("/api/participants/{participant_id}")
async def get_participant(participant_id: str):
    """Get specific participant details"""
    if participant_id not in registered_participants:
        raise HTTPException(status_code=404, detail="Participant not found")

    return registered_participants[participant_id]

@app.post("/api/participants/{participant_id}/submit-response")
async def submit_participant_response(participant_id: str, response: ParticipantResponse):
    """Submit experiment response from a participant"""
    if participant_id not in registered_participants:
        raise HTTPException(status_code=404, detail="Participant not found")

    # Validate that all required subjective scores are provided
    missing_scores = []
    if not response.nasa_tlx_scores:
        missing_scores.append("NASA-TLX scores")
    if not response.sus_scores:
        missing_scores.append("SUS scores")
    if not response.satisfaction_scores:
        missing_scores.append("Satisfaction scores")

    if missing_scores:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required subjective scores: {', '.join(missing_scores)}"
        )

    # Save response to CSV
    responses_file = os.path.join(data_path, "participant_responses.csv")
    file_exists = os.path.exists(responses_file)

    with open(responses_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "participant_id", "experiment_number", "submission_time",
                "nasa_tlx_scores", "sus_scores", "satisfaction_scores",
                "task_completion_time", "errors_made", "decision_changes",
                "agent_interactions", "comments"
            ])

        writer.writerow([
            participant_id, response.experiment_number, datetime.now().isoformat(),
            json.dumps(response.nasa_tlx_scores), json.dumps(response.sus_scores),
            json.dumps(response.satisfaction_scores), response.task_completion_time,
            response.errors_made, response.decision_changes,
            json.dumps(response.agent_interactions), response.comments
        ])

    # Update participant record
    registered_participants[participant_id]["experiments_completed"] += 1

    return {
        "success": True,
        "message": f"Response submitted for experiment {response.experiment_number}"
    }

@app.post("/api/agent-interaction")
async def log_agent_interaction(
    participant_id: str = Body(...),
    agent_type: str = Body(...),
    recommendation_content: str = Body(...),
    action: str = Body(...),  # "shown", "accepted", "rejected"
    step: str = Body(...),
    timestamp: str = Body(...)
):
    log_path = os.path.join(data_path, "agent_interactions.csv")
    file_exists = os.path.exists(log_path)
    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "participant_id", "agent_type", "recommendation_content",
                "action", "step", "timestamp"
            ])
        writer.writerow([
            participant_id, agent_type, recommendation_content, action, step, timestamp
        ])
    return {"message": "Agent interaction logged"}

@app.post("/api/experiment/submit")
async def submit_experiment(submission: ExperimentSubmission):
    # Check for subjective scores
    responses = submission.responses
    missing_scores = []
    for key in ["nasatlx_scores", "satisfaction_scores", "sus_scores"]:
        if not responses.get(key):
            missing_scores.append(key)
    if missing_scores:
        print(f"WARNING: Missing subjective scores: {missing_scores} for participant {submission.participant_name}")
    # Save to CSV (existing)
    csv_file = os.path.join(data_path, f"experiment_{submission.experiment_number}.csv")
    file_exists = os.path.exists(csv_file)
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'participant_name', 'participant_email', 'responses'])
        writer.writerow([
            datetime.now().isoformat(),
            submission.participant_name,
            submission.participant_email,
            json.dumps(submission.responses)
        ])
    # Log to experiment_log.csv for analytics
    log_experiment_to_csv(
        submission.participant_name,
        submission.participant_email,
        submission.experiment_number,
        submission.responses
    )
    return {"message": "Experiment data saved successfully"}

@app.get("/api/experiment/{experiment_number}/analytics")
async def get_experiment_analytics(experiment_number: str):
    csv_file = os.path.join(data_path, f"experiment_{experiment_number}.csv")

    if not os.path.exists(csv_file):
        return {"error": "Experiment not found"}

    participants = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            participants.append(row)

    return {
        "experiment_number": experiment_number,
        "total_participants": len(participants),
        "unique_emails": len(set(p['participant_email'] for p in participants)),
        "sample_responses": participants[:5] if participants else []
    }

@app.get("/api/experiment/{experiment_number}/export")
async def export_experiment_data(experiment_number: str):
    csv_file = os.path.join(data_path, f"experiment_{experiment_number}.csv")

    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail="Experiment not found")

    return {"csv_file": csv_file, "download_url": f"/download/{experiment_number}"}

@app.post("/api/start-automated-experiments")
async def start_automated_experiments():
    """Start automated experiments for agent testing"""
    return {
        "message": "Automated experiments started",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "experiments": [
            {
                "id": "agent_test_1",
                "name": "Agent Performance Test",
                "status": "active",
                "participants": 0
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)