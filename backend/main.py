import sys
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.auth import router as auth_router
from app.api.orders import router as orders_router
from app.api.locations import router as locations_router
from app.api.measurements import router as measurements_router
from app.db import engine, Base
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict
from sqlalchemy import inspect
from datetime import datetime
from logging_config import logger
from temp_repo.src.utils.experiment_logger import ExperimentLogger
import csv
import json

# Add the temp_repo directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'temp_repo'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'temp_repo', 'src'))

# Now import agents after path setup
from temp_repo.src.agents.Face_Ag import FaceRecognitionAgent, EnhancedFaceRecognitionAgent
from temp_repo.src.agents.Health_Ag import HealthRecommenderAgent
from temp_repo.src.agents.Weather_Ag import WeatherRecommenderAgent
from temp_repo.src.agents.Entertainer_Ag import EntertainerAgent
from temp_repo.src.agents.Learner_Ag import LearnerAgent
from temp_repo.src.agents.Note_Ag import NoteTakerAgent
from temp_repo.src.agents.Record_Ag import RecordKeeperAgent

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

# Initialize the experiment logger
experiment_logger = ExperimentLogger(file_path=os.path.join(data_path, "experiments.csv"), logger_instance=logger)

# Initialize agents with individual error handling
# Face Agent
try:
    face_agent = FaceRecognitionAgent(os.path.join(data_path, "customers.csv"), face_images_path)
    print("Face agent initialized successfully")
except Exception as e:
    print(f"Warning: Error initializing face agent: {e}")
    face_agent = None

# Health Agent
try:
    health_agent = HealthRecommenderAgent(health_data_path)
    print("Health agent initialized successfully")
except Exception as e:
    print(f"Warning: Error initializing health agent: {e}")
    health_agent = None

# Weather Agent
try:
    weather_agent = WeatherRecommenderAgent(weather_data_path)
    print("Weather agent initialized successfully")
except Exception as e:
    print(f"Warning: Error initializing weather agent: {e}")
    weather_agent = None

# Entertainer Agent
try:
    entertainer_agent = EntertainerAgent(dish_naming_data_path)
    print("Entertainer agent initialized successfully")
except Exception as e:
    print(f"Warning: Error initializing entertainer agent: {e}")
    entertainer_agent = None

# Learner Agent
try:
    learner_agent = LearnerAgent(os.path.join(data_path, "learning_data.json"))
    print("Learner agent initialized successfully")
except Exception as e:
    print(f"Warning: Error initializing learner agent: {e}")
    learner_agent = None

# Note Taker Agent
try:
    note_agent = NoteTakerAgent(os.path.join(data_path, "menu_items.csv"))
    print("Note taker agent initialized successfully")
except Exception as e:
    print(f"Warning: Error initializing note taker agent: {e}")
    note_agent = None

# Agent activity tracking
agent_activity = {
    "face_agent": {"status": "Ready", "last_activity": None, "activity_count": 0},
    "health_agent": {"status": "Ready", "last_activity": None, "activity_count": 0},
    "weather_agent": {"status": "Ready", "last_activity": None, "activity_count": 0},
    "entertainer_agent": {"status": "Ready", "last_activity": None, "activity_count": 0},
    "learner_agent": {"status": "Ready", "last_activity": None, "activity_count": 0},
    "note_agent": {"status": "Ready", "last_activity": None, "activity_count": 0}
}

def update_agent_activity(agent_name: str, activity: str):
    """Update agent activity tracking"""
    agent_activity[agent_name]["status"] = activity
    agent_activity[agent_name]["last_activity"] = datetime.now().isoformat()
    agent_activity[agent_name]["activity_count"] += 1

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
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

# Include modular routers
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(locations_router)
app.include_router(measurements_router)

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

class FaceRecognitionRequest(BaseModel):
    image_data: str

class StoreCustomerFaceRequest(BaseModel):
    name: str = ""
    phone_number: str = ""
    image_data: str
    customer_id: str = None

class ExperimentData(BaseModel):
    experiment_id: str
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    face_recognized: bool = False
    activity_level_input: Optional[str] = None
    health_agent_recommendations: Optional[dict] = None
    weather_condition: Optional[dict] = None
    weather_agent_recommendations: Optional[dict] = None
    selected_base: Optional[str] = None
    selected_protein: Optional[str] = None
    selected_veggies: Optional[List[str]] = None
    selected_sauce: Optional[str] = None
    final_order_details: dict
    dish_name_agent_suggestions: Optional[dict] = None
    final_dish_name: Optional[str] = None

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

@app.post("/api/face-recognition")
async def face_recognition(request: FaceRecognitionRequest):
    """Enhanced face recognition with authentication and mood tracking"""
    image_data = request.image_data
    try:
        import base64
        image_bytes = base64.b64decode(image_data.split(',')[1])
        from temp_repo.src.agents.Face_Ag import EnhancedFaceRecognitionAgent
        from temp_repo.src.agents.Record_Ag import RecordKeeperAgent

        # Create data directory if it doesn't exist
        os.makedirs("/app/data", exist_ok=True)
        os.makedirs("/app/data/face_images", exist_ok=True)

        face_agent = EnhancedFaceRecognitionAgent(
            customer_data_path="data/customers.csv",
            face_images_dir="/app/data/face_images"
        )
        record_keeper = RecordKeeperAgent(
            orders_path="data/orders.csv",
            feedback_path="data/feedback.csv",
            customers_path="data/customers.csv"
        )

        # Use enhanced authentication
        auth_result = face_agent.authenticate_customer(image_bytes)

        if auth_result["authenticated"]:
            customer_data = auth_result["customer_profile"]
            return {
                "success": True,
                "recognized": True,
                "customer_data": customer_data,
                "confidence": auth_result["confidence"],
                "session_id": auth_result["session_id"],
                "message": f"Welcome back, {customer_data.get('name', 'Valued Customer')}!",
                "mood_tracking_enabled": True
            }
        else:
            return {
                "success": True,
                "recognized": False,
                "new_customer": auth_result.get("new_customer", True),
                "message": "New customer detected. Please provide your information.",
                "confidence": auth_result.get("confidence", 0.0)
            }
    except Exception as e:
        logger.error(f"Face recognition error: {str(e)}")
        return {
            "success": False,
            "error": "Face recognition failed",
            "message": "Unable to process image. Please try again."
        }

@app.post("/api/track-mood")
async def track_real_time_mood(request: dict):
    """Track customer mood in real-time for feedback analysis"""
    try:
        image_data = request.get("image_data")
        customer_id = request.get("customer_id")
        context = request.get("context", "general")

        if not image_data:
            return {"success": False, "error": "No image data provided"}

        import base64
        image_bytes = base64.b64decode(image_data.split(',')[1])
        from temp_repo.src.agents.Face_Ag import EnhancedFaceRecognitionAgent

        os.makedirs("/app/data/face_images", exist_ok=True)

        face_agent = EnhancedFaceRecognitionAgent(
            customer_data_path="data/customers.csv",
            face_images_dir="/app/data/face_images"
        )

        mood_result = face_agent.track_real_time_mood(
            image_bytes,
            customer_id,
            context
        )

        return {
            "success": True,
            "mood_analysis": mood_result
        }

    except Exception as e:
        logger.error(f"Real-time mood tracking error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/analyze-recommendation-reaction")
async def analyze_recommendation_reaction(request: dict):
    """Analyze customer's facial reaction to specific recommendations"""
    try:
        image_data = request.get("image_data")
        customer_id = request.get("customer_id")
        recommendation_type = request.get("recommendation_type")
        recommendation_data = request.get("recommendation_data", {})

        if not all([image_data, customer_id, recommendation_type]):
            return {"success": False, "error": "Missing required parameters"}

        import base64
        image_bytes = base64.b64decode(image_data.split(',')[1])
        from temp_repo.src.agents.Face_Ag import EnhancedFaceRecognitionAgent

        os.makedirs("/app/data/face_images", exist_ok=True)

        face_agent = EnhancedFaceRecognitionAgent(
            customer_data_path="data/customers.csv",
            face_images_dir="/app/data/face_images"
        )

        reaction_result = face_agent.analyze_recommendation_reaction(
            image_bytes,
            customer_id,
            recommendation_type,
            recommendation_data
        )

        return {
            "success": True,
            "reaction_analysis": reaction_result
        }

    except Exception as e:
        logger.error(f"Recommendation reaction analysis error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/end-mood-session")
async def end_mood_tracking_session(request: dict):
    """End mood tracking session and get feedback summary"""
    try:
        customer_id = request.get("customer_id")

        if not customer_id:
            return {"success": False, "error": "Customer ID required"}

        from temp_repo.src.agents.Face_Ag import EnhancedFaceRecognitionAgent

        face_agent = EnhancedFaceRecognitionAgent(
            customer_data_path="data/customers.csv",
            face_images_dir="/app/data/face_images"
        )

        session_result = face_agent.end_session(customer_id)

        return {
            "success": True,
            "session_summary": session_result
        }

    except Exception as e:
        logger.error(f"End mood session error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/mood-statistics")
async def get_mood_statistics():
    """Get overall mood statistics from history"""
    try:
        from temp_repo.src.agents.Face_Ag import EnhancedFaceRecognitionAgent

        face_agent = EnhancedFaceRecognitionAgent(
            customer_data_path="data/customers.csv",
            face_images_dir="/app/data/face_images"
        )

        stats = face_agent.get_mood_statistics()

        return {
            "success": True,
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"Mood statistics error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/store-customer-face")
async def store_customer_face(request: StoreCustomerFaceRequest):
    """Store customer face with enhanced tracking capabilities"""
    try:
        import base64
        image_data = request.image_data
        if not image_data:
            return {"success": False, "error": "No image data provided"}
        image_bytes = base64.b64decode(image_data.split(',')[1])
        from temp_repo.src.agents.Face_Ag import EnhancedFaceRecognitionAgent
        from temp_repo.src.agents.Record_Ag import RecordKeeperAgent

        # Create data directory if it doesn't exist
        os.makedirs("/app/data", exist_ok=True)
        os.makedirs("/app/data/face_images", exist_ok=True)

        face_agent = EnhancedFaceRecognitionAgent(
            customer_data_path="data/customers.csv",
            face_images_dir="/app/data/face_images"
        )
        record_keeper = RecordKeeperAgent(
            orders_path="data/orders.csv",
            feedback_path="data/feedback.csv",
            customers_path="data/customers.csv"
        )
        customer_id = request.customer_id
        if not customer_id:
            customer_id = f"CUST{int(datetime.now().timestamp())}"
        face_result = face_agent.store_face(image_bytes, customer_id)
        if face_result["success"]:
            customer_record = {
                "customer_id": customer_id,
                "name": request.name,
                "phone_number": request.phone_number,
                "face_id": face_result["face_id"]
            }
            record_keeper.update_customer(customer_record)
            return {
                "success": True,
                "face_id": face_result["face_id"],
                "customer_id": customer_id,
                "message": "Face stored successfully for future recognition and mood tracking"
            }
        return {"success": False, "error": "Failed to store face"}
    except Exception as e:
        logger.error(f"Store customer face error: {str(e)}")
        return {
            "success": False,
            "error": "Failed to store customer face"
        }

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
    """Get health-based recommendations"""
    try:
        update_agent_activity("health_agent", "Generating health recommendations")

        activity_level = request.get("activity_level", "moderate")
        customer_id = request.get("customer_id")
        previous_orders = request.get("previous_orders", [])
        mood = request.get("mood", "neutral")

        if health_agent is not None:
            recommendations = health_agent.get_recommendations(
                activity_level=activity_level,
                customer_id=customer_id,
                previous_orders=previous_orders,
                mood=mood
            )
        else:
            # Fallback when agent is not available
            recommendations = {
                "proteins": ["Chicken", "Paneer/Indian Cheese"],
                "sauces": ["Curry Masala", "Mint Sauce"],
                "base_types": ["Bowl", "Sandwich & Subs"],
                "veggies": ["Bell Pepper", "Tomato", "Cilantro"],
                "reasoning": "Balanced options for moderate activity (default)"
            }

        update_agent_activity("health_agent", "Health recommendations completed")
        return {
            "success": True,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Health recommendations error: {str(e)}")
        # Fallback to default recommendations
        return {
            "success": True,
            "recommendations": {
                "proteins": ["Chicken", "Paneer/Indian Cheese"],
                "sauces": ["Curry Masala", "Mint Sauce"],
                "base_types": ["Bowl", "Sandwich & Subs"],
                "veggies": ["Bell Pepper", "Tomato", "Cilantro"],
                "reasoning": "Balanced options for moderate activity"
            }
        }

@app.post("/api/weather-recommendations")
async def get_weather_recommendations(request: dict):
    """Get weather-based recommendations with live weather and location"""
    try:
        update_agent_activity("weather_agent", "Generating intelligent weather recommendations")

        weather_data = request.get("weather_data", {})
        time_of_day = request.get("time_of_day", "afternoon")
        customer_id = request.get("customer_id")
        mood = request.get("mood", "neutral")
        location = request.get("location")  # Optional specific location
        use_live_weather = request.get("use_live_weather", True)  # Default to live weather

        if weather_agent is not None:
            # Use live weather recommendations if requested
            if use_live_weather and not weather_data:
                recommendations = weather_agent.get_live_weather_recommendations(
                    time_of_day=time_of_day,
                    customer_id=customer_id,
                    mood=mood,
                    location=location
                )
                update_agent_activity("weather_agent", f"Live weather recommendations generated for {recommendations.get('location', 'unknown location')}")
            else:
                # Use provided weather data or fallback
                if not weather_data:
                    weather_data = weather_agent.get_current_weather(location or "San Francisco,US")

                recommendations = weather_agent.get_recommendations(
                    weather_data=weather_data,
                    time_of_day=time_of_day,
                    customer_id=customer_id,
                    mood=mood
                )
                update_agent_activity("weather_agent", "Weather recommendations generated")
        else:
            # Fallback when agent is not available
            recommendations = {
                "proteins": ["Chicken", "Egg"],
                "sauces": ["Curry Special", "Yogurt/Raita"],
                "base_types": ["Bowl", "Wrap"],
                "veggies": ["Tomato", "Cilantro", "Bell Pepper"],
                "reasoning": "🌟 Weather-appropriate options carefully selected for your dining pleasure. These combinations provide balanced nutrition suitable for any weather conditions.",
                "llm_powered": False,
                "location_aware": False,
                "live_weather": False,
                "weather_source": "fallback"
            }

        return {
            "success": True,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Weather recommendations error: {str(e)}")
        # Enhanced fallback with better reasoning
        return {
            "success": True,
            "recommendations": {
                "proteins": ["Chicken", "Paneer/Indian Cheese"],
                "sauces": ["Curry Special", "Malai Masala"],
                "base_types": ["Bowl", "Sandwich & Subs"],
                "veggies": ["Bell Pepper", "Spinach", "Tomato"],
                "reasoning": "🌟 Comforting options thoughtfully selected for any weather conditions. These balanced combinations provide excellent nutrition and satisfying flavors to enhance your dining experience.",
                "llm_powered": False,
                "location_aware": False,
                "live_weather": False,
                "weather_source": "error_fallback",
                "error": str(e)
            }
        }

@app.post("/api/dish-name")
async def get_dish_name(request: dict):
    """Generate dish name suggestions using AI agent"""
    try:
        update_agent_activity("entertainer_agent", "Generating dish name")

        selections = request.get("selections", {})

        # Extract selections
        protein = selections.get("protein", ["Chicken"])[0] if isinstance(selections.get("protein"), list) else selections.get("protein", "Chicken")
        base_type = selections.get("base_type", "Bowl")
        customer_name = selections.get("customer_name", "Guest")

        # Generate dish name using the agent
        dish_name_result = entertainer_agent.generate_dish_name(
            customer_name=customer_name,
            protein=protein,
            base_type=base_type,
            weather="sunny",  # Default weather, could be enhanced to get real weather
            mood="happy"      # Default mood, could be enhanced to get customer mood
        )

        update_agent_activity("entertainer_agent", "Dish name generated")
        return {
            "success": True,
            "suggestions": {
                "name": dish_name_result.get("name", f"{customer_name}'s Special {protein} {base_type}"),
                "alternatives": dish_name_result.get("alternatives", [
                    f"Chef's Special {protein} {base_type}",
                    f"Fusion {protein} {base_type}",
                    f"Signature {protein} {base_type}"
                ]),
                "format_used": dish_name_result.get("format_used", "AI-generated personalized naming")
            }
        }
    except Exception as e:
        logger.error(f"Dish name generation error: {str(e)}")
        # Fallback to simple naming
        protein = selections.get("protein", ["Chicken"])[0] if isinstance(selections.get("protein"), list) else selections.get("protein", "Chicken")
        base_type = selections.get("base_type", "Bowl")
        customer_name = selections.get("customer_name", "Guest")

        return {
            "success": True,
            "suggestions": {
                "name": f"{customer_name}'s Special {protein} {base_type}",
                "alternatives": [
                    f"Chef's Special {protein} {base_type}",
                    f"Fusion {protein} {base_type}",
                    f"Signature {protein} {base_type}"
                ],
                "format_used": "fallback_template"
            }
        }

@app.post("/api/recommendation-feedback")
async def submit_recommendation_feedback(request: dict):
    """Submit feedback on recommendations"""
    try:
        update_agent_activity("learner_agent", "Processing feedback")

        recommendation_type = request.get("type", "general")
        feedback = request.get("feedback", "accept")
        custom_suggestion = request.get("custom_suggestion")
        customer_id = request.get("customer_id")
        context = request.get("context", {})

        # Process feedback with learner agent
        result = learner_agent.process_feedback(
            recommendation_type=recommendation_type,
            feedback=feedback,
            custom_suggestion=custom_suggestion,
            customer_id=customer_id,
            context=context
        )

        update_agent_activity("learner_agent", f"Feedback processed: {feedback}")

        return {
            "success": True,
            "message": "Feedback received and processed successfully",
            "learning_result": result
        }
    except Exception as e:
        update_agent_activity("learner_agent", f"Error: {str(e)}")
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
        "agents": agent_activity,
        "timestamp": datetime.now().isoformat()
    }

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
        update_agent_activity("learner_agent", "Generating insights")

        insights = {
            "health_model": learner_agent.get_model_insights("health"),
            "weather_model": learner_agent.get_model_insights("weather"),
            "dish_name_model": learner_agent.get_model_insights("dish_name"),
            "feedback_stats": learner_agent.get_feedback_stats()
        }

        update_agent_activity("learner_agent", "Insights generated")
        return {
            "success": True,
            "insights": insights
        }
    except Exception as e:
        update_agent_activity("learner_agent", f"Error: {str(e)}")
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