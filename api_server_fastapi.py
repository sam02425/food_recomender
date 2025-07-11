import os
import csv
import json
import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import logging
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security
import cv2
import numpy as np
from fer import FER
import base64
import io
from PIL import Image

# Import ML recommendations
from backend.api.ml_recommendations import router as ml_router

# Environment variables
from dotenv import load_dotenv
load_dotenv()

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))

S3_BUCKET = os.environ.get('S3_BUCKET')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
S3_ANALYTICS_PREFIX = os.environ.get('S3_ANALYTICS_PREFIX', '')
if S3_ANALYTICS_PREFIX and not S3_ANALYTICS_PREFIX.endswith('/'):
    S3_ANALYTICS_PREFIX += '/'
ANALYTICS_FILENAME = f"{S3_ANALYTICS_PREFIX}analytics_events.csv"
LOCAL_ANALYTICS_PATH = os.path.join("data", ANALYTICS_FILENAME.replace('/', '_'))

USE_S3 = all([S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY])
if USE_S3:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )

app = FastAPI(title="Curry Creations API", docs_url="/docs", redoc_url="/redoc")

# Include ML recommendation routes
app.include_router(ml_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("curry_creations_api")

# API Key security for admin endpoints
API_KEY = os.environ.get("ADMIN_API_KEY", "testkey")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return api_key

# Models
class QuestionnaireSubmission(BaseModel):
    customer_phone: Optional[str]
    answers: Dict[str, Any]

# New Models for Facial Recognition and Mood Analysis
class MoodData(BaseModel):
    emotion: str
    confidence: float
    timestamp: str
    section: str  # e.g., "protein_selection", "base_selection", etc.

class FacialRecognitionData(BaseModel):
    customer_id: str
    face_id: str
    timestamp: str
    confidence: float

class SectionMoodSummary(BaseModel):
    section: str
    emotions: Dict[str, float]  # e.g., {"happy": 0.6, "confused": 0.3, "neutral": 0.1}
    total_duration: float
    dominant_emotion: str

# Enhanced Models for Detailed Analytics
class DetailedMoodData(BaseModel):
    emotion: str
    confidence: float
    timestamp: str
    section: str
    duration: float
    previous_emotion: Optional[str]
    interaction_type: str  # e.g., "hover", "click", "scroll", "view"
    interaction_details: Dict[str, Any]

class CustomerJourneyData(BaseModel):
    customer_phone: str
    session_id: str
    start_time: str
    end_time: Optional[str]
    sections_visited: List[str]
    total_duration: float
    mood_summary: Dict[str, Dict[str, float]]
    interaction_summary: Dict[str, Dict[str, int]]
    completion_rate: float

# Enhanced Models for UI/UX Research
class UIInteractionData(BaseModel):
    element_id: str
    element_type: str
    interaction_type: str
    timestamp: str
    duration: float
    position: Dict[str, float]  # x, y coordinates
    viewport_size: Dict[str, float]  # width, height
    scroll_position: Dict[str, float]  # x, y scroll
    emotion: Optional[str]
    confidence: Optional[float]

class HeatmapData(BaseModel):
    section: str
    element_id: str
    interaction_count: int
    average_duration: float
    emotion_distribution: Dict[str, float]
    position: Dict[str, float]

# RL-style mood/feedback scoring utility
MOOD_POINTS = {
    'happy': 1,
    'surprised': 1,
    'amazed': 1,
    'angry': -1,
    'confused': -1
}

FEEDBACK_POINTS = {
    'satisfaction': 1,  # e.g., positive feedback +1, negative -1
    'frustration': -1
}

# Helper functions for analytics events

def read_analytics_events() -> List[Dict[str, Any]]:
    events = []
    if USE_S3:
        try:
            obj = s3_client.get_object(Bucket=S3_BUCKET, Key=ANALYTICS_FILENAME)
            lines = obj['Body'].read().decode('utf-8').splitlines()
            reader = csv.DictReader(lines)
            for row in reader:
                try:
                    row['data'] = json.loads(row['data'])
                except Exception:
                    pass
                events.append(row)
        except s3_client.exceptions.NoSuchKey:
            pass  # No file yet
        except Exception as e:
            print(f"Error reading analytics events from S3: {e}")
    else:
        if os.path.exists(LOCAL_ANALYTICS_PATH):
            with open(LOCAL_ANALYTICS_PATH, "r", newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        row['data'] = json.loads(row['data'])
                    except Exception:
                        pass
                    events.append(row)
    return events

def append_analytics_event(event_type, data):
    fieldnames = ["timestamp", "event_type", "data"]
    row = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event_type": event_type,
        "data": json.dumps(data)
    }
    if USE_S3:
        events = read_analytics_events()
        events.append(row)
        from io import StringIO
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for e in events:
            writer.writerow({k: e[k] if k != 'data' else json.dumps(e[k]) if isinstance(e[k], dict) else e[k] for k in fieldnames})
        s3_client.put_object(Bucket=S3_BUCKET, Key=ANALYTICS_FILENAME, Body=output.getvalue())
    else:
        os.makedirs(os.path.dirname(LOCAL_ANALYTICS_PATH), exist_ok=True)
        write_header = not os.path.exists(LOCAL_ANALYTICS_PATH)
        with open(LOCAL_ANALYTICS_PATH, "a", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)

def record_analytics_event(event_type, data):
    append_analytics_event(event_type, data)

# Email sending

def send_analytics_email(subject, content):
    try:
        msg = MIMEMultipart()
        msg['From'] = ADMIN_EMAIL
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'html'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(ADMIN_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# Helper for rendering nested answers as HTML

def render_answers_html(answers):
    html = ""
    for q, a in answers.items():
        if isinstance(a, dict):
            html += f"<li><strong>{q}:</strong><ul>{render_answers_html(a)}</ul></li>"
        else:
            html += f"<li><strong>{q}:</strong> {a}</li>"
    return html

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# Questionnaire endpoint
@app.post("/api/questionnaire")
async def submit_questionnaire(submission: QuestionnaireSubmission):
    try:
        # Get customer journey data
        journey_data = await get_customer_journey(submission.customer_phone)

        # Record questionnaire with detailed analytics
        record_analytics_event('questionnaire_response', {
            'customer_phone': submission.customer_phone,
            'answers': submission.answers,
            'customer_journey': journey_data.get('customer_journey', [])
        })

        # Send enhanced email notification
        subject = "New Customer Questionnaire Response with Detailed Analytics"
        content = f"""
        <h2>New Questionnaire Response</h2>
        <p><strong>Customer Phone:</strong> {submission.customer_phone}</p>

        <h3>Customer Journey Analysis:</h3>
        {''.join(f"""
        <h4>Session {session['session_id']}</h4>
        <ul>
            <li>Duration: {session['total_duration']:.1f} seconds</li>
            <li>Completion Rate: {session['completion_rate']:.1%}</li>
            <li>Section Sequence:
                <ul>
                    {''.join(f"<li>{s['section']}: {s['duration']:.1f}s ({s['emotions']})</li>"
                            for s in session['section_sequence'])}
                </ul>
            </li>
        </ul>
        """ for session in journey_data.get('customer_journey', []))}

        <h3>Questionnaire Answers:</h3>
        <ul>
            {render_answers_html(submission.answers)}
        </ul>
        """
        send_analytics_email(subject, content)

        return {"success": True, "message": "Questionnaire submitted successfully"}
    except Exception as e:
        print("QUESTIONNAIRE ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

# Analytics events endpoint
@app.get("/api/admin/analytics-events")
async def get_analytics_events(api_key: str = Depends(get_api_key)):
    """Get all analytics events (admin only, API key required)"""
    try:
        events = read_analytics_events()
        logger.info("Admin analytics events accessed.")
        return {"success": True, "events": events}
    except Exception as e:
        logger.error(f"Error in get_analytics_events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Home endpoint
@app.get("/")
def home():
    return HTMLResponse(
        """
        <html>
            <head>
                <title>Curry Creations API (FastAPI)</title>
            </head>
            <body>
                <h1>Curry Creations API Server (FastAPI)</h1>
                <p>This server provides the API endpoints for the Curry Creations application.</p>
                <h2>Available Endpoints:</h2>
                <ul>
                    <li><code>POST /api/questionnaire</code> - Submit customer questionnaire</li>
                    <li><code>GET /api/admin/analytics-events</code> - Get analytics events</li>
                    <li><code>GET /health</code> - Health check</li>
                    <li><code>/docs</code> - OpenAPI docs</li>
                </ul>
            </body>
        </html>
        """
    )

@app.post("/api/start-order")
async def start_order():
    order_data = {
        "order_id": f"ORD{int(datetime.datetime.now().timestamp())}",
        "timestamp": datetime.datetime.now().isoformat(),
        "items": [],
        "total_price": 0.0
    }
    return {"success": True, "order_data": order_data}

@app.get("/api/menu-data")
async def menu_data():
    try:
        proteins = [
            {"name": "Chicken", "price": 4.50, "description": "Grilled chicken pieces", "calories": 180},
            {"name": "Egg", "price": 3.00, "description": "Boiled or fried egg", "calories": 70},
            {"name": "Paneer/Indian Cheese", "price": 4.00, "description": "Fresh Indian cheese cubes", "calories": 200},
            {"name": "Soya", "price": 3.50, "description": "Marinated soya chunks", "calories": 150},
            {"name": "Potato", "price": 2.50, "description": "Spiced potato cubes", "calories": 120},
            {"name": "Pepperoni", "price": 4.50, "description": "Sliced pepperoni", "calories": 250}
        ]
        sauces = [
            {"name": "Curry Special", "price": 1.50, "description": "House special curry sauce", "calories": 60},
            {"name": "Malai Masala", "price": 1.50, "description": "Creamy masala sauce", "calories": 80},
            {"name": "Curry Masala", "price": 1.50, "description": "Traditional curry masala", "calories": 70},
            {"name": "Marinara", "price": 1.00, "description": "Classic tomato sauce", "calories": 40},
            {"name": "Yogurt/Raita", "price": 1.00, "description": "Cooling yogurt sauce", "calories": 30},
            {"name": "Red Spicy Sauce", "price": 1.00, "description": "Hot chili sauce", "calories": 20},
            {"name": "Mint Sauce", "price": 1.00, "description": "Fresh mint sauce", "calories": 25},
            {"name": "Green Spicy Sauce", "price": 1.00, "description": "Spicy green chili sauce", "calories": 25}
        ]
        bases = {
            "Biryani": [
                {"name": "Rice", "price": 2.00, "description": "Fragrant basmati rice", "calories": 210}
            ],
            "Sandwich & Subs": [
                {"name": "Sourdough", "price": 2.50, "description": "Tangy artisan bread", "calories": 160},
                {"name": "Ciabatta", "price": 2.50, "description": "Italian white bread", "calories": 170},
                {"name": "White Bread", "price": 2.00, "description": "Classic soft bread", "calories": 150},
                {"name": "Hoagie Bun", "price": 2.50, "description": "Submarine sandwich roll", "calories": 180}
            ],
            "Wrap": [
                {"name": "Naan", "price": 2.00, "description": "Traditional Indian flatbread", "calories": 220},
                {"name": "Pita", "price": 2.00, "description": "Mediterranean pocket bread", "calories": 170}
            ],
            "Bowl": [
                {"name": "Bowl", "price": 2.00, "description": "Served in a bowl, no bread", "calories": 50}
            ]
        }
        veggies = [
            {"name": "Grilled Onion", "price": 0.50, "description": "Caramelized grilled onions", "premium": False, "calories": 15},
            {"name": "Bell Pepper", "price": 0.50, "description": "Colorful bell peppers", "premium": False, "calories": 10},
            {"name": "Tomato", "price": 0.50, "description": "Fresh sliced tomatoes", "premium": False, "calories": 8},
            {"name": "Cilantro", "price": 0.50, "description": "Fresh cilantro/coriander", "premium": False, "calories": 2},
            {"name": "Avocado", "price": 3.00, "description": "Fresh avocado slices", "premium": True, "calories": 50},
            {"name": "Pineapple", "price": 1.00, "description": "Sweet pineapple pieces", "premium": False, "calories": 20},
            {"name": "Spinach", "price": 1.00, "description": "Fresh spinach leaves", "premium": False, "calories": 7},
            {"name": "Jalapeño", "price": 0.50, "description": "Spicy jalapeño slices", "premium": False, "calories": 4}
        ]
        pricing_rules = [
            {"rule_type": "free_items", "applies_to": "veggies", "value": "5", "description": "First 5 veggies are free"},
            {"rule_type": "extra_price", "applies_to": "veggies", "value": "1.00", "description": "Price for each additional regular veggie"},
            {"rule_type": "premium_item", "applies_to": "Avocado", "value": "3.00", "description": "Premium price for avocado"}
        ]
        drinks = [
            {"name": "Coke", "calories": 140},
            {"name": "Pepsi", "calories": 150},
            {"name": "Mango Yogurt", "calories": 180},
            {"name": "Strawberry Yogurt", "calories": 170},
            {"name": "Almond Yogurt", "calories": 160}
        ]
        return {
            'success': True,
            'menu_data': {
                'proteins': proteins,
                'sauces': sauces,
                'bases': bases,
                'veggies': veggies,
                'drinks': drinks
            },
            'pricing_rules': pricing_rules
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customer-orders")
async def customer_orders(phone: str):
    orders = []
    try:
        # Read from CSV (or use your own data source)
        if os.path.exists("data/orders.csv"):
            import csv
            with open("data/orders.csv", "r", newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get("phone_number") == phone:
                        items = []
                        try:
                            items = json.loads(row.get("items", "[]"))
                        except Exception:
                            pass
                        orders.append({
                            "order_id": row.get("order_id", ""),
                            "timestamp": row.get("timestamp", ""),
                            "dish_name": items[0].get("dish_name", "") if items else "",
                            "protein": items[0].get("protein", "") if items else "",
                            "sauce": items[0].get("sauce", "") if items else "",
                            "base_type": items[0].get("base_type", "") if items else "",
                            "base_option": items[0].get("base_option", "") if items else ""
                        })
        return {"success": True, "orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class HealthRecommendationsRequest(BaseModel):
    activity_level: Optional[str] = "work"
    customer_phone: Optional[str] = None

@app.post("/api/health-recommendations")
async def health_recommendations(request: HealthRecommendationsRequest):
    """Get health-based food recommendations based on activity level and customer phone."""
    logger.info(f"Health recommendations requested: {request.activity_level}, {request.customer_phone}")
    activity_level = request.activity_level
    customer_phone = request.customer_phone
    # LLM-style recommendations
    recs = {
        "study": {
            "proteins": ["Egg", "Paneer/Indian Cheese"],
            "sauces": ["Mint Sauce", "Yogurt/Raita"],
            "base_types": ["Wrap", "Bowl"],
            "veggies": ["Spinach", "Bell Pepper", "Tomato", "Cilantro"],
            "reasoning": "For study sessions, these brain-boosting proteins and light carbs provide sustained mental energy without crashes.",
            "calories": 420
        },
        "active": {
            "proteins": ["Chicken", "Soya"],
            "sauces": ["Curry Special", "Red Spicy Sauce"],
            "base_types": ["Bowl", "Biryani"],
            "veggies": ["Spinach", "Bell Pepper", "Grilled Onion", "Avocado"],
            "reasoning": "For an active lifestyle, these protein-rich options support muscle recovery and growth.",
            "calories": 520
        },
        "gym": {
            "proteins": ["Chicken", "Soya"],
            "sauces": ["Curry Special", "Red Spicy Sauce"],
            "base_types": ["Bowl", "Biryani"],
            "veggies": ["Spinach", "Bell Pepper", "Grilled Onion", "Avocado"],
            "reasoning": "For an active lifestyle, these protein-rich options support muscle recovery and growth.",
            "calories": 520
        },
        "chilling": {
            "proteins": ["Paneer/Indian Cheese", "Potato"],
            "sauces": ["Malai Masala", "Curry Special"],
            "base_types": ["Bowl", "Wrap"],
            "veggies": ["Avocado", "Tomato", "Cilantro", "Jalapeño"],
            "reasoning": "For relaxation time, these comfort food options provide a perfect balance of flavor and nutrition.",
            "calories": 410
        },
        "work": {
            "proteins": ["Chicken", "Egg", "Soya"],
            "sauces": ["Curry Special", "Mint Sauce", "Malai Masala"],
            "base_types": ["Sandwich", "Wrap"],
            "veggies": ["Bell Pepper", "Tomato", "Spinach", "Grilled Onion"],
            "reasoning": "For your workday, these balanced options provide steady energy without causing post-meal drowsiness.",
            "calories": 430
        }
    }
    rec = recs.get(activity_level, recs["work"])
    if customer_phone:
        scores = get_customer_item_scores(customer_phone)
        for key in ["proteins", "sauces", "base_types", "veggies"]:
            if key in rec:
                rec[key] = sorted(rec[key], key=lambda x: scores.get(x, 0), reverse=True)
        rec["rl_scores"] = scores
    return {"success": True, "recommendations": rec}

@app.post("/api/weather-recommendations")
async def weather_recommendations(data: dict = Body(...)):
    # LLM-style weather recs
    weather_condition = data.get("weather_condition", "sunny")
    temperature = data.get("temperature", 25)
    time_of_day = data.get("time_of_day", "afternoon")
    if weather_condition in ["rainy", "cloudy"] or temperature < 15:
        base_types = ["Bowl", "Biryani"]
        suggested_base = "Bowl"
        reasoning = f"For {weather_condition} weather at {temperature}°C, these warming options provide comfort and satisfaction."
        calories = 480
    elif weather_condition == "hot" or temperature > 28:
        base_types = ["Wrap", "Sandwich & Subs"]
        suggested_base = "Wrap"
        reasoning = f"For hot weather at {temperature}°C, these lighter options are more refreshing."
        calories = 390
    else:
        if time_of_day == "morning":
            base_types = ["Wrap", "Sandwich & Subs"]
            suggested_base = "Wrap"
            reasoning = f"For a {weather_condition} {time_of_day}, these options offer portability and convenience."
            calories = 350
        else:
            base_types = ["Bowl", "Wrap"]
            suggested_base = "Bowl"
            reasoning = f"For a {weather_condition} {time_of_day}, these options offer the perfect balance."
            calories = 420
    return {"success": True, "recommendations": {
        "base_types": base_types,
        "suggested_base": suggested_base,
        "reasoning": reasoning,
        "calories": calories
    }}

class DishNameRequest(BaseModel):
    protein: Optional[str] = "Chicken"
    base_type: Optional[str] = "Bowl"
    customer_name: Optional[str] = ""

@app.post("/api/dish-name")
async def dish_name(request: DishNameRequest):
    """Generate a creative dish name based on selections."""
    logger.info(f"Dish name requested: {request.dict()}")
    protein = request.protein
    base_type = request.base_type
    customer_name = request.customer_name
    # LLM-style creative naming
    prefixes = ["Mumbai", "Delhi", "Tandoori", "Bombay", "Spicy", "Maharaja", "Royal", "Curry", "Masala", "Fusion", "Incredible", "Signature"]
    suffixes = ["Delight", "Special", "Express", "Creation", "Fiesta", "Magic", "Wonder", "Fusion", "Sensation", "Experience"]
    styles = ["Street Style", "Chef's Special", "House Favorite", "Traditional", "Homestyle", "Gourmet", "Premium", "Classic", "Artisan"]
    name_templates = [
        f"{random.choice(prefixes)} {protein} {base_type}",
        f"{protein} {base_type} {random.choice(suffixes)}",
        f"{random.choice(styles)} {protein} {base_type}",
        f"{random.choice(prefixes)} {random.choice(suffixes)} {protein}",
        f"{protein} {random.choice(prefixes)} {base_type}"
    ]
    if customer_name:
        personal_templates = [
            f"{customer_name}'s {random.choice(prefixes)} {protein}",
            f"{customer_name}'s {protein} {random.choice(suffixes)}",
            f"{customer_name}'s Special {base_type}",
            f"The {customer_name} {random.choice(suffixes)}",
        ]
        name_templates = personal_templates + name_templates
    random.shuffle(name_templates)
    suggestions = {
        "name": name_templates[0],
        "alternatives": name_templates[1:4],
        "format_used": "Creative fusion naming with Indian regional influences"
    }
    return {"success": True, "suggestions": suggestions}

class RecommendationFeedbackRequest(BaseModel):
    recommendation_type: str
    feedback: str
    customer_phone: Optional[str] = None
    custom_suggestion: Optional[str] = None
    weather_condition: Optional[str] = None
    activity_level: Optional[str] = None

@app.post("/api/recommendation-feedback")
async def recommendation_feedback(request: RecommendationFeedbackRequest):
    """Submit feedback on recommendations."""
    logger.info(f"Recommendation feedback: {request.recommendation_type}, {request.feedback}, {request.customer_phone}")
    # ... existing logic ...
    return {"success": True, "result": "Feedback received"}

class AddItemRequest(BaseModel):
    protein: Optional[str] = ""
    sauce: Optional[str] = ""
    base_type: Optional[str] = ""
    base_option: Optional[str] = ""
    veggies: Optional[List[str]] = []
    price: Optional[float] = 12.99
    dish_name: Optional[str] = ""
    customer_phone: Optional[str] = ""
    customer_name: Optional[str] = ""

@app.post("/api/add-item")
async def add_item(request: AddItemRequest):
    """Add an item to the order."""
    logger.info(f"Add item: {request.dict()}")
    item = request.dict()
    item["item_id"] = "ITEM1"
    return {"success": True, "item": item}

class CompleteOrderRequest(BaseModel):
    customer_phone: Optional[str] = ""
    customer_name: Optional[str] = ""

@app.post("/api/complete-order")
async def complete_order(request: CompleteOrderRequest):
    """Complete the order and suggest a drink."""
    logger.info(f"Complete order: {request.dict()}")
    order_id = f"ORD{int(datetime.datetime.now().timestamp())}"
    drink_options = [
        {"name": "Coke", "calories": 140},
        {"name": "Pepsi", "calories": 150},
        {"name": "Mango Yogurt", "calories": 180},
        {"name": "Strawberry Yogurt", "calories": 170},
        {"name": "Almond Yogurt", "calories": 160}
    ]
    healthy_drinks = [d for d in drink_options if "Yogurt" in d["name"] or "Almond" in d["name"]]
    suggested_drink = random.choice(healthy_drinks)
    return {
        "success": True,
        "order": {
            "order_id": order_id,
            "total_price": 12.99,
            "timestamp": datetime.datetime.now().isoformat(),
            "customer_phone": request.customer_phone,
            "customer_name": request.customer_name,
            "suggested_drink": suggested_drink
        }
    }

# New endpoints for facial recognition and mood analysis
# All facial/biometric code, models, and endpoints have been removed for privacy-first deployment.
# Only standard login and new 3-agent system endpoints remain.

@app.get("/api/mood-analysis/summary/{customer_phone}")
async def get_mood_summary(customer_phone: str):
    try:
        events = read_analytics_events()
        mood_events = [e for e in events if e.get('event_type') == 'mood_analysis'
                      and e.get('data', {}).get('customer_phone') == customer_phone]

        # Group by section
        section_moods = {}
        for event in mood_events:
            section = event['data']['section']
            emotion = event['data']['emotion']
            if section not in section_moods:
                section_moods[section] = {}
            if emotion not in section_moods[section]:
                section_moods[section][emotion] = 0
            section_moods[section][emotion] += 1

        # Calculate summaries
        summaries = []
        for section, emotions in section_moods.items():
            total = sum(emotions.values())
            emotion_percentages = {e: (count/total) for e, count in emotions.items()}
            dominant_emotion = max(emotion_percentages.items(), key=lambda x: x[1])[0]

            summaries.append({
                "section": section,
                "emotions": emotion_percentages,
                "total_duration": total,
                "dominant_emotion": dominant_emotion
            })

        return {
            "success": True,
            "mood_summary": summaries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mood-analysis/timeline/{session_id}")
async def get_mood_timeline(session_id: str):
    try:
        events = read_analytics_events()
        mood_events = [
            {
                "timestamp": e["data"].get("timestamp", e.get("timestamp")),
                "section": e["data"].get("section"),
                "emotion": e["data"].get("emotion"),
                "confidence": e["data"].get("confidence")
            }
            for e in events
            if e.get("event_type") == "mood_analysis" and e["data"].get("session_id") == session_id
        ]
        # Sort by timestamp
        mood_events.sort(key=lambda x: x["timestamp"])
        return {"success": True, "timeline": mood_events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New analytics endpoints
class AnalyticsSessionStartRequest(BaseModel):
    customer_phone: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = {}
    initial_section: Optional[str] = "start"

@app.post("/api/analytics/session-start")
async def start_analytics_session(request: AnalyticsSessionStartRequest):
    """Start an analytics session."""
    logger.info(f"Analytics session start: {request.dict()}")
    session_id = f"SESSION_{int(datetime.datetime.now().timestamp())}"
    customer_phone = request.customer_phone
    record_analytics_event('session_start', {
        'session_id': session_id,
        'customer_phone': customer_phone,
        'start_time': datetime.datetime.now().isoformat(),
        'device_info': request.device_info,
        'initial_section': request.initial_section
    })
    return {
        "success": True,
        "session_id": session_id
    }

class AnalyticsSectionInteractionRequest(BaseModel):
    session_id: str
    section: str
    interaction_type: str
    interaction_details: Optional[Dict[str, Any]] = {}
    duration: Optional[float] = 0.0
    emotion: Optional[str] = None

@app.post("/api/analytics/section-interaction")
async def record_section_interaction(request: AnalyticsSectionInteractionRequest):
    """Record a section interaction event."""
    logger.info(f"Section interaction: {request.dict()}")
    record_analytics_event('section_interaction', {
        'session_id': request.session_id,
        'section': request.section,
        'interaction_type': request.interaction_type,
        'interaction_details': request.interaction_details,
        'duration': request.duration,
        'emotion': request.emotion,
        'timestamp': datetime.datetime.now().isoformat()
    })
    return {"success": True}

class AnalyticsSessionEndRequest(BaseModel):
    session_id: str
    customer_phone: Optional[str] = None
    completion_status: Optional[str] = "completed"

@app.post("/api/analytics/session-end")
async def end_analytics_session(request: AnalyticsSessionEndRequest):
    """End an analytics session and record summary."""
    logger.info(f"Analytics session end: {request.dict()}")
    session_id = request.session_id
    customer_phone = request.customer_phone
    completion_status = request.completion_status
    # Get all events for this session
    events = read_analytics_events()
    session_events = [e for e in events if e.get('data', {}).get('session_id') == session_id]
    start_time = min(e['timestamp'] for e in session_events)
    end_time = datetime.datetime.now().isoformat()
    total_duration = (datetime.datetime.fromisoformat(end_time) - datetime.datetime.fromisoformat(start_time)).total_seconds()
    sections_visited = set()
    mood_summary = {}
    interaction_summary = {}
    for event in session_events:
        if event['event_type'] == 'section_interaction':
            section = event['data']['section']
            sections_visited.add(section)
            if section not in mood_summary:
                mood_summary[section] = {}
            emotion = event['data'].get('emotion')
            if emotion:
                mood_summary[section][emotion] = mood_summary[section].get(emotion, 0) + 1
            if section not in interaction_summary:
                interaction_summary[section] = {}
            interaction_type = event['data']['interaction_type']
            interaction_summary[section][interaction_type] = (
                interaction_summary[section].get(interaction_type, 0) + 1
            )
    expected_sections = {"start", "protein_selection", "base_selection", "sauce_selection", "veggie_selection", "checkout"}
    completion_rate = len(sections_visited.intersection(expected_sections)) / len(expected_sections)
    record_analytics_event('session_end', {
        'session_id': session_id,
        'customer_phone': customer_phone,
        'start_time': start_time,
        'end_time': end_time,
        'total_duration': total_duration,
        'sections_visited': list(sections_visited),
        'mood_summary': mood_summary,
        'interaction_summary': interaction_summary,
        'completion_rate': completion_rate,
        'completion_status': completion_status
    })
    return {
        "success": True,
        "session_summary": {
            "total_duration": total_duration,
            "sections_visited": list(sections_visited),
            "completion_rate": completion_rate,
            "mood_summary": mood_summary,
            "interaction_summary": interaction_summary
        }
    }

@app.get("/api/analytics/customer-journey/{customer_phone}")
async def get_customer_journey(customer_phone: str):
    try:
        events = read_analytics_events()
        customer_events = [e for e in events if e.get('data', {}).get('customer_phone') == customer_phone]

        # Group events by session
        sessions = {}
        for event in customer_events:
            session_id = event.get('data', {}).get('session_id')
            if session_id:
                if session_id not in sessions:
                    sessions[session_id] = []
                sessions[session_id].append(event)

        # Analyze each session
        journey_data = []
        for session_id, session_events in sessions.items():
            # Get session start and end
            start_event = next((e for e in session_events if e['event_type'] == 'session_start'), None)
            end_event = next((e for e in session_events if e['event_type'] == 'session_end'), None)

            if start_event and end_event:
                start_time = start_event['data']['start_time']
                end_time = end_event['data']['end_time']
                total_duration = end_event['data']['total_duration']

                # Get section sequence
                section_events = [e for e in session_events if e['event_type'] == 'section_interaction']
                section_sequence = []
                current_section = None
                section_start_time = None

                for event in section_events:
                    section = event['data']['section']
                    if section != current_section:
                        if current_section and section_start_time:
                            section_duration = (
                                datetime.datetime.fromisoformat(event['timestamp']) -
                                datetime.datetime.fromisoformat(section_start_time)
                            ).total_seconds()
                            section_sequence.append({
                                'section': current_section,
                                'duration': section_duration,
                                'emotions': event['data'].get('emotion', 'unknown')
                            })
                        current_section = section
                        section_start_time = event['timestamp']

                journey_data.append({
                    'session_id': session_id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'total_duration': total_duration,
                    'section_sequence': section_sequence,
                    'completion_rate': end_event['data'].get('completion_rate', 0),
                    'mood_summary': end_event['data'].get('mood_summary', {}),
                    'interaction_summary': end_event['data'].get('interaction_summary', {})
                })

        return {
            "success": True,
            "customer_journey": journey_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/aggregate-metrics")
async def get_aggregate_metrics():
    try:
        events = read_analytics_events()
        session_events = [e for e in events if e['event_type'] == 'session_end']

        # Calculate aggregate metrics
        total_sessions = len(session_events)
        completion_rates = [e['data'].get('completion_rate', 0) for e in session_events]
        avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0

        # Aggregate mood data by section
        section_moods = {}
        for event in session_events:
            mood_summary = event['data'].get('mood_summary', {})
            for section, emotions in mood_summary.items():
                if section not in section_moods:
                    section_moods[section] = {}
                for emotion, count in emotions.items():
                    section_moods[section][emotion] = section_moods[section].get(emotion, 0) + count

        # Calculate average section duration
        section_durations = {}
        for event in session_events:
            interaction_summary = event['data'].get('interaction_summary', {})
            for section, interactions in interaction_summary.items():
                if section not in section_durations:
                    section_durations[section] = []
                section_durations[section].append(sum(interactions.values()))

        avg_section_durations = {
            section: sum(durations) / len(durations)
            for section, durations in section_durations.items()
        }

        return {
            "success": True,
            "aggregate_metrics": {
                "total_sessions": total_sessions,
                "average_completion_rate": avg_completion_rate,
                "section_moods": section_moods,
                "average_section_durations": avg_section_durations
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New visualization and UI/UX research endpoints
class AnalyticsUIInteractionRequest(BaseModel):
    session_id: Optional[str] = None
    customer_phone: Optional[str] = None
    element_id: str
    element_type: str
    interaction_type: str
    timestamp: Optional[str] = None
    duration: Optional[float] = 0.0
    position: Optional[Dict[str, float]] = {}
    viewport_size: Optional[Dict[str, float]] = {}
    scroll_position: Optional[Dict[str, float]] = {}
    emotion: Optional[str] = None
    confidence: Optional[float] = None

@app.post("/api/analytics/ui-interaction")
async def record_ui_interaction(request: AnalyticsUIInteractionRequest):
    """Record a UI interaction event."""
    logger.info(f"UI interaction: {request.dict()}")
    record_analytics_event('ui_interaction', {
        'session_id': request.session_id,
        'customer_phone': request.customer_phone,
        'element_id': request.element_id,
        'element_type': request.element_type,
        'interaction_type': request.interaction_type,
        'timestamp': request.timestamp or datetime.datetime.now().isoformat(),
        'duration': request.duration,
        'position': request.position,
        'viewport_size': request.viewport_size,
        'scroll_position': request.scroll_position,
        'emotion': request.emotion,
        'confidence': request.confidence
    })
    return {"success": True}

@app.get("/api/analytics/heatmap/{section}")
async def get_section_heatmap(section: str):
    try:
        events = read_analytics_events()
        ui_events = [e for e in events if e['event_type'] == 'ui_interaction'
                    and e['data'].get('element_type') in ['button', 'card', 'image', 'text']]

        # Group interactions by element
        element_data = {}
        for event in ui_events:
            element_id = event['data']['element_id']
            if element_id not in element_data:
                element_data[element_id] = {
                    'interaction_count': 0,
                    'total_duration': 0,
                    'emotions': {},
                    'positions': []
                }

            data = element_data[element_id]
            data['interaction_count'] += 1
            data['total_duration'] += event['data'].get('duration', 0)

            # Track emotions
            emotion = event['data'].get('emotion')
            if emotion:
                data['emotions'][emotion] = data['emotions'].get(emotion, 0) + 1

            # Track positions
            if 'position' in event['data']:
                data['positions'].append(event['data']['position'])

        # Calculate heatmap data
        heatmap_data = []
        for element_id, data in element_data.items():
            if data['positions']:
                avg_x = sum(p['x'] for p in data['positions']) / len(data['positions'])
                avg_y = sum(p['y'] for p in data['positions']) / len(data['positions'])

                # Calculate emotion distribution
                total_emotions = sum(data['emotions'].values())
                emotion_distribution = {
                    emotion: count/total_emotions
                    for emotion, count in data['emotions'].items()
                } if total_emotions > 0 else {}

                heatmap_data.append({
                    'element_id': element_id,
                    'interaction_count': data['interaction_count'],
                    'average_duration': data['total_duration'] / data['interaction_count'],
                    'emotion_distribution': emotion_distribution,
                    'position': {'x': avg_x, 'y': avg_y}
                })

        return {
            "success": True,
            "heatmap_data": heatmap_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/user-flow")
async def get_user_flow_analysis():
    try:
        events = read_analytics_events()
        session_events = [e for e in events if e['event_type'] == 'session_end']

        # Analyze user flow patterns
        flow_patterns = {}
        for event in session_events:
            section_sequence = event['data'].get('section_sequence', [])
            sequence_key = '->'.join(s['section'] for s in section_sequence)

            if sequence_key not in flow_patterns:
                flow_patterns[sequence_key] = {
                    'count': 0,
                    'completion_rates': [],
                    'durations': [],
                    'emotions': {}
                }

            pattern = flow_patterns[sequence_key]
            pattern['count'] += 1
            pattern['completion_rates'].append(event['data'].get('completion_rate', 0))
            pattern['durations'].append(event['data'].get('total_duration', 0))

            # Aggregate emotions
            for section, emotions in event['data'].get('mood_summary', {}).items():
                if section not in pattern['emotions']:
                    pattern['emotions'][section] = {}
                for emotion, count in emotions.items():
                    pattern['emotions'][section][emotion] = pattern['emotions'][section].get(emotion, 0) + count

        # Calculate statistics for each pattern
        flow_analysis = []
        for sequence, data in flow_patterns.items():
            sections = sequence.split('->')
            avg_completion = sum(data['completion_rates']) / len(data['completion_rates'])
            avg_duration = sum(data['durations']) / len(data['durations'])

            # Calculate emotion distributions
            emotion_distributions = {}
            for section, emotions in data['emotions'].items():
                total = sum(emotions.values())
                emotion_distributions[section] = {
                    emotion: count/total
                    for emotion, count in emotions.items()
                } if total > 0 else {}

            flow_analysis.append({
                'sequence': sections,
                'frequency': data['count'],
                'average_completion_rate': avg_completion,
                'average_duration': avg_duration,
                'emotion_distributions': emotion_distributions
            })

        return {
            "success": True,
            "flow_analysis": sorted(flow_analysis, key=lambda x: x['frequency'], reverse=True)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/ui-metrics")
async def get_ui_metrics():
    try:
        events = read_analytics_events()
        ui_events = [e for e in events if e['event_type'] == 'ui_interaction']

        # Calculate UI-specific metrics
        metrics = {
            'interaction_patterns': {},
            'element_engagement': {},
            'emotional_responses': {},
            'time_distribution': {},
            'error_rates': {},
            'accessibility_metrics': {}
        }

        for event in ui_events:
            data = event['data']
            element_type = data.get('element_type')
            interaction_type = data.get('interaction_type')

            # Track interaction patterns
            pattern_key = f"{element_type}:{interaction_type}"
            if pattern_key not in metrics['interaction_patterns']:
                metrics['interaction_patterns'][pattern_key] = {
                    'count': 0,
                    'total_duration': 0,
                    'emotions': {}
                }
            pattern = metrics['interaction_patterns'][pattern_key]
            pattern['count'] += 1
            pattern['total_duration'] += data.get('duration', 0)

            # Track element engagement
            if element_type not in metrics['element_engagement']:
                metrics['element_engagement'][element_type] = {
                    'interactions': 0,
                    'unique_users': set(),
                    'average_duration': 0,
                    'total_duration': 0
                }
            element = metrics['element_engagement'][element_type]
            element['interactions'] += 1
            element['unique_users'].add(data.get('customer_phone'))
            element['total_duration'] += data.get('duration', 0)

            # Track emotional responses
            emotion = data.get('emotion')
            if emotion:
                if element_type not in metrics['emotional_responses']:
                    metrics['emotional_responses'][element_type] = {}
                if emotion not in metrics['emotional_responses'][element_type]:
                    metrics['emotional_responses'][element_type][emotion] = 0
                metrics['emotional_responses'][element_type][emotion] += 1

            # Track time distribution
            hour = datetime.datetime.fromisoformat(data['timestamp']).hour
            if hour not in metrics['time_distribution']:
                metrics['time_distribution'][hour] = 0
            metrics['time_distribution'][hour] += 1

        # Calculate averages and percentages
        for element_type, data in metrics['element_engagement'].items():
            data['average_duration'] = data['total_duration'] / data['interactions'] if data['interactions'] > 0 else 0
            data['unique_users'] = len(data['unique_users'])

        # Calculate emotion percentages
        for element_type, emotions in metrics['emotional_responses'].items():
            total = sum(emotions.values())
            metrics['emotional_responses'][element_type] = {
                emotion: count/total
                for emotion, count in emotions.items()
            }

        return {
            "success": True,
            "ui_metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/accessibility-metrics")
async def get_accessibility_metrics():
    try:
        events = read_analytics_events()
        ui_events = [e for e in events if e['event_type'] == 'ui_interaction']

        metrics = {
            'keyboard_navigation': {
                'usage_count': 0,
                'success_rate': 0,
                'average_time': 0
            },
            'screen_reader': {
                'usage_count': 0,
                'elements_accessed': set()
            },
            'color_contrast': {
                'compliant_elements': 0,
                'non_compliant_elements': 0
            },
            'text_size': {
                'default_users': 0,
                'enlarged_text_users': 0
            }
        }

        for event in ui_events:
            data = event['data']
            interaction_type = data.get('interaction_type')

            # Track keyboard navigation
            if interaction_type == 'keyboard':
                metrics['keyboard_navigation']['usage_count'] += 1
                metrics['keyboard_navigation']['average_time'] += data.get('duration', 0)

            # Track screen reader usage
            if interaction_type == 'screen_reader':
                metrics['screen_reader']['usage_count'] += 1
                metrics['screen_reader']['elements_accessed'].add(data.get('element_id'))

            # Track color contrast compliance
            if 'color_contrast' in data:
                if data['color_contrast'] >= 4.5:  # WCAG AA standard
                    metrics['color_contrast']['compliant_elements'] += 1
                else:
                    metrics['color_contrast']['non_compliant_elements'] += 1

            # Track text size preferences
            if 'text_size' in data:
                if data['text_size'] > 16:  # Default browser text size
                    metrics['text_size']['enlarged_text_users'] += 1
                else:
                    metrics['text_size']['default_users'] += 1

        # Calculate success rates and averages
        if metrics['keyboard_navigation']['usage_count'] > 0:
            metrics['keyboard_navigation']['average_time'] /= metrics['keyboard_navigation']['usage_count']

        metrics['screen_reader']['elements_accessed'] = len(metrics['screen_reader']['elements_accessed'])

        return {
            "success": True,
            "accessibility_metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/analytics/sessions')
async def list_sessions():
    events = read_analytics_events()
    sessions = {}
    for e in events:
        session_id = e.get('data', {}).get('session_id')
        customer_phone = e.get('data', {}).get('customer_phone')
        if session_id:
            sessions[session_id] = customer_phone
    session_list = [
        {"session_id": sid, "customer_phone": phone} for sid, phone in sessions.items()
    ]
    return {"success": True, "sessions": session_list}

@app.get('/api/mood-analysis/aggregate-timeline')
async def aggregate_mood_timeline():
    try:
        events = read_analytics_events()
        mood_events = [
            {
                "timestamp": e["data"].get("timestamp", e.get("timestamp")),
                "section": e["data"].get("section"),
                "emotion": e["data"].get("emotion"),
                "confidence": e["data"].get("confidence")
            }
            for e in events
            if e.get("event_type") == "mood_analysis"
        ]
        # Aggregate by section and emotion
        section_emotions = {}
        for e in mood_events:
            section = e["section"]
            emotion = e["emotion"]
            if not section or not emotion:
                continue
            if section not in section_emotions:
                section_emotions[section] = {}
            if emotion not in section_emotions[section]:
                section_emotions[section][emotion] = 0
            section_emotions[section][emotion] += 1
        # Calculate percentages
        section_percentages = {}
        for section, emotions in section_emotions.items():
            total = sum(emotions.values())
            section_percentages[section] = {
                emotion: count / total for emotion, count in emotions.items()
            }
        # Optionally, bin mood events by minute for time series
        from collections import defaultdict
        import math
        time_series = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        for e in mood_events:
            if not e["timestamp"] or not e["section"] or not e["emotion"]:
                continue
            # Bin by minute
            ts = e["timestamp"]
            if 'T' in ts:
                minute = ts[:16]  # 'YYYY-MM-DDTHH:MM'
            else:
                minute = ts
            time_series[e["section"]][minute][e["emotion"]] += 1
        # Convert to list format
        section_time_series = {}
        for section, minutes in time_series.items():
            section_time_series[section] = []
            for minute, emotions in sorted(minutes.items()):
                entry = {"minute": minute}
                entry.update(emotions)
                section_time_series[section].append(entry)
        return {
            "success": True,
            "aggregate": {
                "section_emotions": section_emotions,
                "section_percentages": section_percentages,
                "section_time_series": section_time_series
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# RL-style mood/feedback scoring utility
def get_customer_item_scores(customer_phone):
    events = read_analytics_events()
    # Map: item_name -> score
    item_scores = {}
    # Mood analytics
    for e in events:
        data = e.get('data', {})
        if data.get('customer_phone') != customer_phone:
            continue
        # Mood events
        if e.get('event_type') == 'mood_analysis':
            item = data.get('item') or data.get('section')  # fallback to section if item not present
            mood = data.get('emotion')
            if item and mood in MOOD_POINTS:
                item_scores[item] = item_scores.get(item, 0) + MOOD_POINTS[mood]
        # Section interaction with emotion
        if e.get('event_type') == 'section_interaction':
            item = data.get('item') or data.get('section')
            mood = data.get('emotion')
            if item and mood in MOOD_POINTS:
                item_scores[item] = item_scores.get(item, 0) + MOOD_POINTS[mood]
        # Questionnaire/feedback
        if e.get('event_type') == 'questionnaire_response':
            answers = data.get('answers', {})
            # Example: use satisfaction and frustration
            sat = answers.get('satisfaction', {})
            if isinstance(sat, dict):
                for k, v in sat.items():
                    if isinstance(v, (int, float)):
                        if v >= 3:  # positive
                            item_scores[k] = item_scores.get(k, 0) + FEEDBACK_POINTS['satisfaction']
                        elif v <= 2:  # negative
                            item_scores[k] = item_scores.get(k, 0) + FEEDBACK_POINTS['frustration']
    return item_scores

class RecommendationsRequest(BaseModel):
    weather_condition: Optional[str] = None
    activity_level: Optional[str] = None
    customer_phone: Optional[str] = None
    temperature: Optional[float] = None
    time_of_day: Optional[str] = None

@app.post("/api/recommendations")
async def recommendations(request: RecommendationsRequest):
    """Unified endpoint for personalized recommendations (health, weather, history)."""
    logger.info(f"Unified recommendations requested: {request.dict()}")
    # Health-based
    health_data = None
    if request.activity_level:
        health_data = await health_recommendations(
            HealthRecommendationsRequest(
                activity_level=request.activity_level,
                customer_phone=request.customer_phone
            )
        )
    # Weather-based
    weather_data = None
    if request.weather_condition or request.temperature or request.time_of_day:
        weather_data = await weather_recommendations({
            "weather_condition": request.weather_condition or "sunny",
            "temperature": request.temperature or 25,
            "time_of_day": request.time_of_day or "afternoon"
        })
    # Combine
    recommendations = {
        "health": health_data["recommendations"] if health_data and health_data["success"] else None,
        "weather": weather_data["recommendations"] if weather_data and weather_data["success"] else None
    }
    return {"success": True, "recommendations": recommendations}