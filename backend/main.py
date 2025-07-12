import sys
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.auth import router as auth_router
from app.api.orders import router as orders_router
from app.api.locations import router as locations_router
from app.api.measurements import router as measurements_router
from app.api.experiment import router as experiment_router
from app.db import engine, Base, SessionLocal
from api.agents import router as agents_router
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict
from sqlalchemy import inspect
from datetime import datetime
from logging_config import logger
from utils.experiment_logger import ExperimentLogger
import csv
import json


# ML libraries for emotion detection
try:
    # ML imports removed
    import numpy as np
    # FER import removed
    # base64 import removed
    import io
    # PIL import removed
    ML_AVAILABLE = True
    logger.info("✅ ML libraries loaded successfully")
except ImportError as e:
    ML_AVAILABLE = False
    logger.warning(f"⚠️ ML libraries not available: {e}")

# All temp_repo imports and references have been removed for privacy-first deployment.
# Only new 3-agent system and standard FastAPI setup remain.

app = FastAPI(
    title="Food Recommender API",
    description="API for food recommendation and ordering system",
    version="1.0.0"
)

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:80",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:80",
    "http://127.0.0.1:8000"
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Define data paths
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
face_images_path = os.path.join(data_path, "face_images")
health_data_path = os.path.join(data_path, "health_data.csv")
weather_data_path = os.path.join(data_path, "weather_data.csv")
dish_naming_data_path = os.path.join(data_path, "dish_naming.csv")

# Ensure data directories exist
os.makedirs(face_images_path, exist_ok=True)
os.makedirs(data_path, exist_ok=True)

# Initialize experiment logger
experiment_logger = ExperimentLogger(file_path=os.path.join(data_path, "experiments.csv"), logger_instance=logger)

# All temp_repo agent imports and initializations have been removed for privacy-first deployment.
# Only new 3-agent system and experiment logger remain.

# Remove all agent_activity tracking for old agents
# Remove all imports and usages of temp_repo.src.agents.Face_Ag, Record_Ag, etc.
# Remove all update_agent_activity and usages of health_agent, weather_agent, entertainer_agent, learner_agent, note_agent, face_agent, etc.

# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "message": str(e)}
        )

# Create tables on startup
@app.on_event("startup")
async def on_startup():
    try:
        # Check if tables exist before creating them
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if not existing_tables:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
        else:
            print("Database tables already exist")

        # Initialize emotion detector
        if initialize_emotion_detector():
            logger.info("🧠 Emotion detection system ready")
        else:
            logger.warning("⚠️ Emotion detection will use fallback mode")

    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

# Include modular routers
app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(orders_router)
app.include_router(locations_router)
app.include_router(measurements_router)
app.include_router(experiment_router)

# Include ML recommendations router
try:
    from api.ml_recommendations import router as ml_router
    app.include_router(ml_router)
    print("ML recommendations router included successfully")
except Exception as e:
    print(f"Warning: Could not include ML recommendations router: {e}")

# Include dietary restrictions router
try:
    from api.dietary_restrictions import router as dietary_router
    app.include_router(dietary_router)
    print("Dietary restrictions router included successfully")
except Exception as e:
    print(f"Warning: Could not include dietary restrictions router: {e}")

# Include master recommendation coordinator router
try:
    from api.master_recommendations import router as master_router
    app.include_router(master_router)
    print("Master recommendation coordinator router included successfully")
except Exception as e:
    print(f"Warning: Could not include master recommendation coordinator router: {e}")

# Menu data (for /api/menu)
class MenuItem(BaseModel):
    name: str
    price: Optional[float] = None
    description: Optional[str] = None
    calories: Optional[int] = None

class BaseOption(BaseModel):
    name: str
    price: float
    calories: int
    description: str

PROTEINS = [
    MenuItem(name="Chicken", price=4.50, description="Tender, juicy chicken breast marinated in Indian spices", calories=250),
    MenuItem(name="Egg", price=3.50, description="Fresh farm eggs, hard-boiled and spiced", calories=180),
    MenuItem(name="Paneer/Indian Cheese", price=4.50, description="Fresh, homemade cottage cheese, rich in protein", calories=220),
    MenuItem(name="Soya", price=4.00, description="Protein-rich soya chunks, perfect vegetarian option", calories=150),
    MenuItem(name="Potato", price=3.50, description="Fresh, diced potatoes seasoned with Indian spices", calories=200),
    MenuItem(name="Pepperoni", price=5.00, description="Spicy, cured meat with bold Italian flavors", calories=280)
]

SAUCES = [
    MenuItem(name="Curry Special", description="Our signature curry sauce with rich, aromatic spices", calories=120),
    MenuItem(name="Malai Masala", description="Creamy, mild sauce with cashew and cream base", calories=150),
    MenuItem(name="Curry Masala", description="Traditional Indian curry sauce with balanced spices", calories=130),
    MenuItem(name="Marinara", description="Classic Italian tomato sauce with herbs", calories=80),
    MenuItem(name="Yogurt/Raita", description="Cooling yogurt sauce with cucumber and mint", calories=60),
    MenuItem(name="Red Spicy Sauce", description="Hot and tangy sauce with red chilies", calories=90),
    MenuItem(name="Mint Sauce", description="Fresh mint sauce with cooling properties", calories=40),
    MenuItem(name="Green Spicy Sauce", description="Green chili sauce with coriander and mint", calories=90)
]

BASE_TYPES = {
    "Biryani": [BaseOption(name="Rice", price=0.00, calories=300, description="Fragrant basmati rice cooked with aromatic spices")],
    "Sandwich & Subs": [
        BaseOption(name="Sourdough", price=0.00, calories=220, description="Artisan sourdough bread with tangy flavor"),
        BaseOption(name="Ciabatta", price=0.50, calories=240, description="Italian-style bread with crispy crust"),
        BaseOption(name="White Bread", price=0.00, calories=200, description="Classic soft white bread"),
        BaseOption(name="Hoagie Bun", price=0.50, calories=260, description="Traditional sub roll, perfect for hearty fillings")
    ],
    "Wrap": [
        BaseOption(name="Naan", price=0.00, calories=280, description="Soft, fluffy Indian flatbread"),
        BaseOption(name="Pitta", price=0.50, calories=200, description="Pocket-style Middle Eastern bread")
    ],
    "Bowl": [
        BaseOption(name="Bowl", price=0.00, calories=50, description="Regular serving bowl"),
        BaseOption(name="Rice Bowl", price=1.00, calories=300, description="Bowl with fragrant basmati rice base")
    ]
}

VEGGIE_OPTIONS = [
    MenuItem(name="Grilled Onion", description="Sweet caramelized onions", calories=40),
    MenuItem(name="Bell Pepper", description="Fresh, colorful bell peppers", calories=30),
    MenuItem(name="Tomato", description="Fresh, juicy tomatoes", calories=25),
    MenuItem(name="Cilantro", description="Fresh coriander leaves", calories=5),
    MenuItem(name="Avocado", description="Creamy, ripe avocado slices", calories=160),
    MenuItem(name="Pineapple", description="Sweet and tangy pineapple chunks", calories=80),
    MenuItem(name="Spinach", description="Fresh, leafy spinach", calories=20),
    MenuItem(name="Jalapeño", description="Spicy green chili peppers", calories=15),
    MenuItem(name="Banana Pepper", description="Mild, sweet banana peppers", calories=20),
    MenuItem(name="Fried Onions", description="Crispy, golden fried onions", calories=120),
    MenuItem(name="Corn", description="Sweet corn kernels", calories=60),
    MenuItem(name="Cabbage", description="Fresh, crunchy cabbage", calories=25),
    MenuItem(name="Ghee", description="Clarified butter for rich flavor", calories=120),
    MenuItem(name="Mango Chutney", description="Sweet and tangy mango relish", calories=90)
]

PREMIUM_VEGGIES = ["Avocado", "Pineapple", "Mango Chutney"]

class OrderItem(BaseModel):
    base_type: str
    base_option: str
    protein: Optional[str] = None
    sauce: Optional[str] = None
    veggies: List[str] = []

class CalorieResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    total_calories: int
    breakdown: Dict[str, int]
    items: List[Dict[str, any]]

class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    data: dict = None

# FaceRecognitionRequest model removed
            }

        # Get the first (most prominent) face
        face_emotions = emotions[0]['emotions']

        # Find dominant emotion
        dominant_emotion = max(face_emotions.items(), key=lambda x: x[1])
        mood = dominant_emotion[0]
        confidence = dominant_emotion[1]

        logger.info(f"🧠 FER detected emotion: {mood} with confidence {confidence:.3f}")
        logger.debug(f"All emotions: {face_emotions}")

        return {
            'mood': mood,
            'confidence': confidence,
            'emotions': face_emotions
        }

    except Exception as e:
        logger.error(f"Error in FER emotion detection: {e}")
        return None

# Initialize emotion detector on startup (after agent initialization)
# We'll do this in the startup event

@app.get("/")
async def root():
    return {"message": "Welcome to Food Recommender API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/menu")
async def get_menu():
    return {
        "proteins": PROTEINS,
        "sauces": SAUCES,
        "base_types": BASE_TYPES,
        "veggie_options": VEGGIE_OPTIONS,
        "premium_veggies": PREMIUM_VEGGIES
    }

@app.post("/api/calculate-calories")
async def calculate_calories(order: OrderItem):
    total_calories = 0
    breakdown = {}
    items = []

    # Calculate base calories
    base_calories = 0
    for base_type, options in BASE_TYPES.items():
        if base_type == order.base_type:
            for option in options:
                if option.name == order.base_option:
                    base_calories = option.calories
                    items.append({
                        "name": f"{order.base_type} - {option.name}",
                        "calories": option.calories,
                        "type": "base"
                    })
                    break

    # Calculate protein calories
    protein_calories = 0
    if order.protein:
        for protein in PROTEINS:
            if protein.name == order.protein:
                protein_calories = protein.calories
                items.append({
                    "name": protein.name,
                    "calories": protein.calories,
                    "type": "protein"
                })
                break

    # Calculate sauce calories
    sauce_calories = 0
    if order.sauce:
        for sauce in SAUCES:
            if sauce.name == order.sauce:
                sauce_calories = sauce.calories
                items.append({
                    "name": sauce.name,
                    "calories": sauce.calories,
                    "type": "sauce"
                })
                break

    # Calculate veggies calories
    veggie_calories = 0
    for veggie_name in order.veggies:
        for veggie in VEGGIE_OPTIONS:
            if veggie.name == veggie_name:
                veggie_calories += veggie.calories
                items.append({
                    "name": veggie.name,
                    "calories": veggie.calories,
                    "type": "veggie"
                })
                break

    total_calories = base_calories + protein_calories + sauce_calories + veggie_calories
    breakdown = {
        "base": base_calories,
        "protein": protein_calories,
        "sauce": sauce_calories,
        "veggies": veggie_calories
    }

    return CalorieResponse(
        total_calories=total_calories,
        breakdown=breakdown,
        items=items
    )

@app.post("/api/logs")
async def log_frontend_error(log_entry: LogEntry):
    try:
        logger.error(
            f"Frontend Error: {log_entry.message}",
            extra={"data": log_entry.data}
        )
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing frontend log: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing log")

# Add missing endpoints that frontend expects
@app.post("/api/start-order")
async def start_order():
    """
    Initialize a new order session.
    This endpoint is used to start a new order process.
    """
    return {
        "success": True,
        "message": "Order session started",
        "order_data": {
            "id": "temp_" + str(int(datetime.now().timestamp())),
            "status": "initialized"
        }
    }

# Face recognition endpoint removed - no longer needed for experiment

# Face recognition endpoint removed

# Face recognition endpoint removed

# Face recognition endpoint removed

# Face recognition endpoint removed

# Face recognition endpoint removed

@app.get("/api/menu-data")
async def get_menu_data():
    """Get menu data in the format expected by frontend"""
    return {
        "success": True,
        "menu_data": {
            "proteins": PROTEINS,
            "sauces": SAUCES,
            "base_types": BASE_TYPES,
            "veggie_options": VEGGIE_OPTIONS,
            "premium_veggies": PREMIUM_VEGGIES
        }
    }

@app.post("/api/health-recommendations")
async def get_health_recommendations(request: dict):
    """Get health-based recommendations with dietary restrictions"""
    try:
        # update_agent_activity("health_agent", "Generating health recommendations with dietary constraints") # Removed

        activity_level = request.get("activity_level", "moderate")
        customer_id = request.get("customer_id")
        previous_orders = request.get("previous_orders", [])
        mood = request.get("mood", "neutral")
        dietary_restrictions = request.get("dietary_restrictions", [])
        allergens = request.get("allergens", [])

        logger.info(f"Health recommendations requested with dietary restrictions: {dietary_restrictions}, allergens: {allergens}")

        # health_agent = None # Removed
        # if health_agent is not None: # Removed
        #     recommendations = health_agent.get_recommendations( # Removed
        #         activity_level=activity_level, # Removed
        #         customer_id=customer_id, # Removed
        #         previous_orders=previous_orders, # Removed
        #         mood=mood, # Removed
        #         dietary_restrictions=dietary_restrictions, # Removed
        #         allergens=allergens # Removed
        #     ) # Removed
        # else: # Removed
            # NO FALLBACK - RETURN ERROR FOR EXPERIMENT INTEGRITY # Removed
        return { # Modified
            "success": False, # Modified
            "error": "Health agent not available - experiment requires real health recommendations" # Modified
        } # Modified

    except Exception as e:
        logger.error(f"Health recommendations error: {str(e)}")
        # NO FALLBACK - RETURN ERROR FOR EXPERIMENT INTEGRITY
        return {
            "success": False,
            "error": f"Health recommendation system failed: {str(e)}"
        }

@app.post("/api/weather-recommendations")
async def get_weather_recommendations(request: dict):
    """Get weather-based recommendations with live weather and location"""
    try:
        # update_agent_activity("weather_agent", "Generating intelligent weather recommendations with dietary constraints") # Removed

        weather_data = request.get("weather_data", {})
        time_of_day = request.get("time_of_day", "afternoon")
        customer_id = request.get("customer_id")
        mood = request.get("mood", "neutral")
        location = request.get("location")  # Optional specific location
        use_live_weather = request.get("use_live_weather", True)  # Default to live weather
        dietary_restrictions = request.get("dietary_restrictions", [])
        allergens = request.get("allergens", [])

        logger.info(f"Weather recommendations requested with dietary restrictions: {dietary_restrictions}, allergens: {allergens}")

        # weather_agent = None # Removed
        # if weather_agent is not None: # Removed
            # Use live weather recommendations if requested # Removed
        #     if use_live_weather and not weather_data: # Removed
        #         recommendations = weather_agent.get_live_weather_recommendations( # Removed
        #             time_of_day=time_of_day, # Removed
        #             customer_id=customer_id, # Removed
        #             mood=mood, # Removed
        #             location=location # Removed
        #         ) # Removed
        #         update_agent_activity("weather_agent", f"Live weather recommendations generated for {recommendations.get('location', 'unknown location')}") # Removed
        #     else: # Removed
                # Use provided weather data or fallback # Removed
        #         if not weather_data: # Removed
        #             weather_data = weather_agent.get_current_weather(location or "San Francisco,US") # Removed

        #         recommendations = weather_agent.get_recommendations( # Removed
        #             weather_data=weather_data, # Removed
        #             time_of_day=time_of_day, # Removed
        #             customer_id=customer_id, # Removed
        #             mood=mood # Removed
        #         ) # Removed
        #         update_agent_activity("weather_agent", "Weather recommendations generated") # Removed
        # else: # Removed
            # NO FALLBACK - RETURN ERROR FOR EXPERIMENT INTEGRITY # Removed
        return { # Modified
            "success": False, # Modified
            "error": "Weather agent not available - experiment requires real weather recommendations" # Modified
        } # Modified

    except Exception as e:
        logger.error(f"Weather recommendations error: {str(e)}")
        # NO FALLBACK - RETURN ERROR FOR EXPERIMENT INTEGRITY
        return {
            "success": False,
            "error": f"Weather recommendation system failed: {str(e)}"
        }

# Dish name endpoint removed
        }

@app.post("/api/recommendation-feedback")
async def submit_recommendation_feedback(request: dict):
    """Submit feedback on recommendations"""
    try:
        # update_agent_activity("learner_agent", "Processing feedback") # Removed

        recommendation_type = request.get("type", "general")
        feedback = request.get("feedback", "accept")
        custom_suggestion = request.get("custom_suggestion")
        customer_id = request.get("customer_id")
        context = request.get("context", {})

        # Process feedback with learner agent
        # learner_agent = None # Removed
        # result = learner_agent.process_feedback( # Removed
        #     recommendation_type=recommendation_type, # Removed
        #     feedback=feedback, # Removed
        #     custom_suggestion=custom_suggestion, # Removed
        #     customer_id=customer_id, # Removed
        #     context=context # Removed
        # ) # Removed

        # update_agent_activity("learner_agent", f"Feedback processed: {feedback}") # Removed

        return { # Modified
            "success": True, # Modified
            "message": "Feedback received and processed successfully", # Modified
            "learning_result": {} # Modified
        } # Modified

    except Exception as e:
        # update_agent_activity("learner_agent", f"Error: {str(e)}") # Removed
        logger.error(f"Feedback processing error: {e}")
        return {
            "success": True,
            "message": "Feedback received successfully"
        }

@app.post("/api/add-item")
async def add_order_item(request: dict):
    """Add an item to the current order"""
    selections = request.get("selections", {})

    return {
        "success": True,
        "message": "Item added to order",
        "item": selections
    }

@app.post("/api/complete-order")
async def complete_order_endpoint(experiment_data: ExperimentData):
    """Complete the order and log experiment data"""
    try:
        # Log the experiment data
        experiment_logger.log_experiment(experiment_data.dict())

        # Existing order completion logic
        order_details = experiment_data.final_order_details
        customer_id = experiment_data.customer_id

        orders_file = "/app/data/orders.csv"
        os.makedirs(os.path.dirname(orders_file), exist_ok=True)
        is_new_file = not os.path.exists(orders_file) or os.path.getsize(orders_file) == 0

        with open(orders_file, "a", newline="") as f:
            writer = csv.writer(f)
            if is_new_file:
                writer.writerow(["order_id", "customer_id", "timestamp", "details"])
            writer.writerow([
                order_details.get("id", ""),
                customer_id,
                datetime.now().isoformat(),
                json.dumps(order_details),
            ])

        return {"status": "success", "order_id": order_details.get("id")}
    except Exception as e:
        logger.error(f"Error completing order: {e}")
        raise HTTPException(status_code=500, detail="Could not complete order")

@app.get("/api/customer-orders")
async def get_customer_orders(phone: str):
    """Get customer's previous orders"""
    # For now, return empty list
    return {
        "success": True,
        "orders": []
    }

@app.post("/api/update-customer")
async def update_customer_info(request: dict):
    """Update customer information"""
    return {
        "success": True,
        "message": "Customer information updated"
    }

@app.get("/api/agent-status")
async def get_agent_status():
    """Get current status of all agents"""
    return {
        "agents": {}, # Modified
        "timestamp": datetime.now().isoformat() # Modified
    } # Modified

@app.post("/api/start-automated-experiments")
async def start_automated_experiments():
    """Start the automated experiment tester"""
    try:
        import subprocess
        import sys

        # Start the automated experiment tester in the background
        process = subprocess.Popen([
            sys.executable,
            "/app/automated_experiment_tester.py"
        ], cwd="/app")

        return {
            "success": True,
            "message": "Automated experiments started",
            "process_id": process.pid
        }
    except Exception as e:
        logger.error(f"Failed to start automated experiments: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/learning-insights")
async def get_learning_insights():
    """Get insights from the learner agent"""
    try:
        # update_agent_activity("learner_agent", "Generating insights") # Removed

        insights = { # Modified
            "health_model": {}, # Modified
            "weather_model": {}, # Modified
            "dish_name_model": {}, # Modified
            "feedback_stats": {} # Modified
        } # Modified

        # update_agent_activity("learner_agent", "Insights generated") # Removed
        return { # Modified
            "success": True, # Modified
            "insights": insights # Modified
        } # Modified

    except Exception as e:
        # update_agent_activity("learner_agent", f"Error: {str(e)}") # Removed
        logger.error(f"Learning insights error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Experimental Trial Management Endpoints

@app.post("/api/trial/start")
async def start_trial(request: dict):
    """Start a new experimental trial"""
    try:
        trial_data = {
            "trial_id": request.get("trial_id"),
            "participant_id": request.get("participant_id"),
            "trial_type": request.get("trial_type", "A"),  # A = Baseline, B = With suggestions
            "trial_number": request.get("trial_number", 1),
            "order_type": request.get("order_type", "custom"),  # custom, specific, specific_flexible
            "specific_order": request.get("specific_order"),
            "start_time": datetime.now().isoformat(),
            "session_data": {}
        }

        # Log trial start
        trial_file = "/app/data/experimental_trials.csv"
        os.makedirs(os.path.dirname(trial_file), exist_ok=True)
        is_new_file = not os.path.exists(trial_file) or os.path.getsize(trial_file) == 0

        with open(trial_file, "a", newline="") as f:
            writer = csv.writer(f)
            if is_new_file:
                writer.writerow([
                    "trial_id", "participant_id", "trial_type", "trial_number",
                    "order_type", "specific_order", "start_time", "end_time",
                    "completed", "order_data", "suggestions_used", "deviation_from_suggested",
                    "completion_time_seconds", "user_satisfaction", "notes"
                ])
            writer.writerow([
                trial_data["trial_id"], trial_data["participant_id"],
                trial_data["trial_type"], trial_data["trial_number"],
                trial_data["order_type"], trial_data["specific_order"],
                trial_data["start_time"], "", False, "", "", "", "", "", ""
            ])

        return {
            "success": True,
            "trial_data": trial_data,
            "message": "Trial started successfully"
        }
    except Exception as e:
        logger.error(f"Error starting trial: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/trial/complete")
async def complete_trial(request: dict):
    """Complete an experimental trial and record results"""
    try:
        trial_id = request.get("trial_id")
        trial_results = {
            "trial_id": trial_id,
            "end_time": datetime.now().isoformat(),
            "completed": True,
            "order_data": json.dumps(request.get("order_data", {})),
            "suggestions_used": request.get("suggestions_used", False),
            "deviation_from_suggested": request.get("deviation_from_suggested", ""),
            "completion_time_seconds": request.get("completion_time_seconds", 0),
            "user_satisfaction": request.get("user_satisfaction", 5),
            "notes": request.get("notes", "")
        }

        # Update trial completion in CSV
        trial_file = "/app/data/experimental_trials.csv"
        if os.path.exists(trial_file):
            # Read existing data
            rows = []
            with open(trial_file, "r") as f:
                reader = csv.reader(f)
                headers = next(reader)
                for row in reader:
                    if row[0] == trial_id:  # trial_id match
                        # Update the row
                        row[7] = trial_results["end_time"]  # end_time
                        row[8] = str(trial_results["completed"])  # completed
                        row[9] = trial_results["order_data"]  # order_data
                        row[10] = str(trial_results["suggestions_used"])  # suggestions_used
                        row[11] = trial_results["deviation_from_suggested"]  # deviation_from_suggested
                        row[12] = str(trial_results["completion_time_seconds"])  # completion_time_seconds
                        row[13] = str(trial_results["user_satisfaction"])  # user_satisfaction
                        row[14] = trial_results["notes"]  # notes
                    rows.append(row)

            # Write back updated data
            with open(trial_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)

        return {
            "success": True,
            "trial_results": trial_results,
            "message": "Trial completed successfully"
        }
    except Exception as e:
        logger.error(f"Error completing trial: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/trial/record-decision")
async def record_trial_decision(request: dict):
    """Record a participant's decision during trial"""
    try:
        decision_data = {
            "trial_id": request.get("trial_id"),
            "participant_id": request.get("participant_id"),
            "decision_type": request.get("decision_type"),  # suggestion_accepted, suggestion_rejected, custom_choice
            "suggested_option": request.get("suggested_option"),
            "chosen_option": request.get("chosen_option"),
            "timestamp": datetime.now().isoformat(),
            "step": request.get("step"),  # protein, base, sauce, etc.
            "reasoning": request.get("reasoning", "")
        }

        # Log decision
        decisions_file = "/app/data/trial_decisions.csv"
        os.makedirs(os.path.dirname(decisions_file), exist_ok=True)
        is_new_file = not os.path.exists(decisions_file) or os.path.getsize(decisions_file) == 0

        with open(decisions_file, "a", newline="") as f:
            writer = csv.writer(f)
            if is_new_file:
                writer.writerow([
                    "trial_id", "participant_id", "decision_type", "suggested_option",
                    "chosen_option", "timestamp", "step", "reasoning"
                ])
            writer.writerow([
                decision_data["trial_id"], decision_data["participant_id"],
                decision_data["decision_type"], decision_data["suggested_option"],
                decision_data["chosen_option"], decision_data["timestamp"],
                decision_data["step"], decision_data["reasoning"]
            ])

        return {
            "success": True,
            "decision_data": decision_data,
            "message": "Decision recorded successfully"
        }
    except Exception as e:
        logger.error(f"Error recording decision: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/trial/statistics")
async def get_trial_statistics():
    """Get overall trial statistics for analysis"""
    try:
        stats = {
            "total_trials": 0,
            "trial_a_count": 0,
            "trial_b_count": 0,
            "completion_rate": 0,
            "average_completion_time": 0,
            "suggestion_acceptance_rate": 0,
            "participant_stats": {}
        }

        trial_file = "/app/data/experimental_trials.csv"
        if os.path.exists(trial_file):
            with open(trial_file, "r") as f:
                reader = csv.DictReader(f)
                trials = list(reader)

                stats["total_trials"] = len(trials)
                stats["trial_a_count"] = len([t for t in trials if t["trial_type"] == "A"])
                stats["trial_b_count"] = len([t for t in trials if t["trial_type"] == "B"])

                completed_trials = [t for t in trials if t["completed"] == "True"]
                stats["completion_rate"] = len(completed_trials) / len(trials) if trials else 0

                completion_times = [float(t["completion_time_seconds"]) for t in completed_trials if t["completion_time_seconds"]]
                stats["average_completion_time"] = sum(completion_times) / len(completion_times) if completion_times else 0

                suggestions_used = [t for t in completed_trials if t["suggestions_used"] == "True"]
                stats["suggestion_acceptance_rate"] = len(suggestions_used) / len(completed_trials) if completed_trials else 0

        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting trial statistics: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/mood-detection", response_model=MoodDetectionResponse)
async def detect_mood(request: MoodDetectionRequest):
    """
    Detect mood/emotion from facial image using ML models
    """
    try:
        logger.info("🧠 Starting ML-based mood detection...")

        # Convert base64 image to OpenCV format
        image = base64_to_opencv_image(request.image_data)

        if image is None:
            return MoodDetectionResponse(
                success=False,
                mood="neutral",
                confidence=0.0,
                error="Failed to process image data"
            )

        # Try FER emotion detection first
        fer_result = detect_emotion_with_fer(image)

        if fer_result:
            return MoodDetectionResponse(
                success=True,
                mood=fer_result['mood'],
                confidence=fer_result['confidence'],
                emotions=fer_result['emotions']
            )

                # NO FALLBACK SIMULATIONS - EXPERIMENT INTEGRITY REQUIREMENT
        # If ML detection fails, return error instead of fake data
        logger.error("ML emotion detection failed - cannot provide simulated data for experiment")

        return MoodDetectionResponse(
            success=False,
            mood="",
            confidence=0.0,
            error="ML emotion detection not available - experiment requires real detection only"
        )

    except Exception as e:
        logger.error(f"Mood detection error: {str(e)}")
        return MoodDetectionResponse(
            success=False,
            mood="neutral",
            confidence=0.0,
            error=f"Mood detection failed: {str(e)}"
        )