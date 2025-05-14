# /main.py
"""
Main application for the self-ordering kiosk system.
This integrates all agent components and manages the ordering workflow.
"""

import os
import csv
import time
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Import agent modules
from agents.face_recognition_agent import FaceRecognitionAgent
from agents.note_taker_agent import NoteTakerAgent
from agents.health_recommender_agent import HealthRecommenderAgent
from agents.weather_recommender_agent import WeatherRecommenderAgent
from agents.entertainer_agent import EntertainerAgent
from agents.learner_agent import LearnerAgent
from agents.record_keeper_agent import RecordKeeperAgent

# Import UI components
from ui.kiosk_app import run_kiosk_ui

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("kiosk_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("kiosk_system")

class SelfOrderingKiosk:
    """Main self-ordering kiosk system that integrates all agents."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the self-ordering kiosk system.

        Args:
            data_dir: Directory for data storage
        """
        # Ensure data directory exists
        self.data_dir = data_dir
        self._ensure_data_directories()

        # Initialize agents
        self.face_agent = FaceRecognitionAgent(
            customer_data_path=os.path.join(data_dir, "customers.csv"),
            face_images_dir=os.path.join(data_dir, "face_images")
        )

        self.note_taker = NoteTakerAgent(
            menu_data_path=os.path.join(data_dir, "menu_items.csv")
        )

        self.health_recommender = HealthRecommenderAgent(
            health_data_path=os.path.join(data_dir, "health_recommendations.csv")
        )

        self.weather_recommender = WeatherRecommenderAgent(
            weather_data_path=os.path.join(data_dir, "weather_recommendations.csv")
        )

        self.entertainer = EntertainerAgent(
            naming_data_path=os.path.join(data_dir, "dish_naming.csv")
        )

        self.learner = LearnerAgent(
            learning_data_path=os.path.join(data_dir, "learning_data.json")
        )

        self.record_keeper = RecordKeeperAgent(
            orders_path=os.path.join(data_dir, "orders.csv"),
            feedback_path=os.path.join(data_dir, "feedback.csv"),
            customers_path=os.path.join(data_dir, "customers.csv")
        )

        # Current session state
        self.current_order = {
            "order_id": None,
            "customer_id": None,
            "customer_name": None,
            "phone_number": None,
            "face_id": None,
            "mood": None,
            "activity_level": None,
            "timestamp": None,
            "items": [],
            "total_price": 0.0,
            "weather_data": {},
            "recommendations": {},
            "feedback": {}
        }

        # Load menu items
        self.menu_items = self._load_menu_items()

        logger.info("Self-ordering kiosk system initialized")

    def _ensure_data_directories(self) -> None:
        """Ensure all required data directories exist."""
        directories = [
            self.data_dir,
            os.path.join(self.data_dir, "face_images"),
            os.path.join(self.data_dir, "receipts")
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")

        # Ensure CSV files exist with headers
        self._initialize_csv_file(
            os.path.join(self.data_dir, "customers.csv"),
            ["customer_id", "name", "phone_number", "face_id", "visit_count", "last_visit", "created_at"]
        )

        self._initialize_csv_file(
            os.path.join(self.data_dir, "orders.csv"),
            ["order_id", "customer_id", "timestamp", "items", "total_price", "weather", "activity", "mood"]
        )

        self._initialize_csv_file(
            os.path.join(self.data_dir, "feedback.csv"),
            ["feedback_id", "order_id", "customer_id", "timestamp", "health_feedback", "weather_feedback", "name_feedback"]
        )

        self._initialize_csv_file(
            os.path.join(self.data_dir, "menu_items.csv"),
            ["category", "item", "price", "description", "attributes"]
        )

    def _initialize_csv_file(self, file_path: str, headers: List[str]) -> None:
        """Initialize a CSV file with headers if it doesn't exist."""
        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
            logger.debug(f"Initialized CSV file: {file_path}")

    def _load_menu_items(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load menu items from CSV."""
        menu = {
            "proteins": [],
            "sauces": [],
            "bases": [],
            "veggies": []
        }

        menu_path = os.path.join(self.data_dir, "menu_items.csv")

        if not os.path.exists(menu_path):
            # Initialize with default menu items
            self._initialize_default_menu()

        try:
            with open(menu_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    category = row.get("category", "")
                    if category in menu:
                        menu[category].append({
                            "name": row.get("item", ""),
                            "price": float(row.get("price", 0)),
                            "description": row.get("description", ""),
                            "attributes": json.loads(row.get("attributes", "{}")) if row.get("attributes") else {}
                        })
        except Exception as e:
            logger.error(f"Error loading menu items: {e}")
            # Initialize with default menu items if loading fails
            self._initialize_default_menu()
            menu = self._load_menu_items()

        return menu

    def _initialize_default_menu(self) -> None:
        """Initialize the menu with default items."""
        menu_path = os.path.join(self.data_dir, "menu_items.csv")

        default_menu = [
            # Proteins
            {"category": "proteins", "item": "Chicken", "price": "4.50", "description": "Grilled chicken pieces", "attributes": '{"spice_level": 2, "allergens": ["poultry"]}'},
            {"category": "proteins", "item": "Egg", "price": "3.00", "description": "Boiled or fried egg", "attributes": '{"spice_level": 1, "allergens": ["egg"]}'},
            {"category": "proteins", "item": "Paneer/Indian Cheese", "price": "4.00", "description": "Fresh Indian cheese cubes", "attributes": '{"spice_level": 1, "allergens": ["dairy"]}'},
            {"category": "proteins", "item": "Soya", "price": "3.50", "description": "Marinated soya chunks", "attributes": '{"spice_level": 2, "allergens": ["soy"]}'},
            {"category": "proteins", "item": "Potato", "price": "2.50", "description": "Spiced potato cubes", "attributes": '{"spice_level": 2, "allergens": []}'},
            {"category": "proteins", "item": "Pepperoni", "price": "4.50", "description": "Sliced pepperoni", "attributes": '{"spice_level": 3, "allergens": ["pork"]}'},

            # Sauces
            {"category": "sauces", "item": "Curry Special", "price": "1.50", "description": "House special curry sauce", "attributes": '{"spice_level": 3, "allergens": ["mustard"]}'},
            {"category": "sauces", "item": "Malai Masala", "price": "1.50", "description": "Creamy masala sauce", "attributes": '{"spice_level": 2, "allergens": ["dairy"]}'},
            {"category": "sauces", "item": "Curry Masala", "price": "1.50", "description": "Traditional curry masala", "attributes": '{"spice_level": 4, "allergens": []}'},
            {"category": "sauces", "item": "Marinara", "price": "1.00", "description": "Classic tomato sauce", "attributes": '{"spice_level": 2, "allergens": []}'},
            {"category": "sauces", "item": "Yogurt/Raita", "price": "1.00", "description": "Cooling yogurt sauce", "attributes": '{"spice_level": 1, "allergens": ["dairy"]}'},
            {"category": "sauces", "item": "Red Spicy Sauce", "price": "1.00", "description": "Hot chili sauce", "attributes": '{"spice_level": 5, "allergens": []}'},
            {"category": "sauces", "item": "Mint Sauce", "price": "1.00", "description": "Fresh mint sauce", "attributes": '{"spice_level": 1, "allergens": []}'},
            {"category": "sauces", "item": "Green Spicy Sauce", "price": "1.00", "description": "Spicy green chili sauce", "attributes": '{"spice_level": 4, "allergens": []}'},

            # Bases
            {"category": "bases", "item": "Rice", "price": "2.00", "description": "Steamed basmati rice", "attributes": '{"base_type": "Biryani", "allergens": []}'},
            {"category": "bases", "item": "Sour Dough", "price": "2.50", "description": "Fresh sourdough bread", "attributes": '{"base_type": "Sandwich", "allergens": ["gluten"]}'},
            {"category": "bases", "item": "Ciabatta", "price": "2.50", "description": "Italian ciabatta bread", "attributes": '{"base_type": "Sandwich", "allergens": ["gluten"]}'},
            {"category": "bases", "item": "White Bread", "price": "2.00", "description": "Soft white bread", "attributes": '{"base_type": "Sandwich", "allergens": ["gluten"]}'},
            {"category": "bases", "item": "Hoagie Bun", "price": "2.50", "description": "Submarine sandwich roll", "attributes": '{"base_type": "Sandwich", "allergens": ["gluten"]}'},
            {"category": "bases", "item": "Naan", "price": "2.00", "description": "Traditional Indian flatbread", "attributes": '{"base_type": "Wrap", "allergens": ["gluten", "dairy"]}'},
            {"category": "bases", "item": "Pita", "price": "2.00", "description": "Mediterranean pita bread", "attributes": '{"base_type": "Wrap", "allergens": ["gluten"]}'},

            # Veggies
            {"category": "veggies", "item": "Grilled Onion", "price": "0.50", "description": "Caramelized grilled onions", "attributes": '{"health_index": 3, "allergens": []}'},
            {"category": "veggies", "item": "Bell Pepper", "price": "0.50", "description": "Colorful bell peppers", "attributes": '{"health_index": 4, "allergens": []}'},
            {"category": "veggies", "item": "Tomato", "price": "0.50", "description": "Fresh sliced tomatoes", "attributes": '{"health_index": 4, "allergens": []}'},
            {"category": "veggies", "item": "Cilantro", "price": "0.50", "description": "Fresh cilantro/coriander", "attributes": '{"health_index": 3, "allergens": []}'},
            {"category": "veggies", "item": "Avocado", "price": "3.00", "description": "Fresh avocado slices", "attributes": '{"health_index": 5, "allergens": []}'},
            {"category": "veggies", "item": "Pineapple", "price": "1.00", "description": "Sweet pineapple pieces", "attributes": '{"health_index": 4, "allergens": []}'},
            {"category": "veggies", "item": "Spinach", "price": "1.00", "description": "Fresh spinach leaves", "attributes": '{"health_index": 5, "allergens": []}'},
            {"category": "veggies", "item": "Jalapeño", "price": "0.50", "description": "Spicy jalapeño slices", "attributes": '{"health_index": 3, "allergens": []}'},
            {"category": "veggies", "item": "Banana Pepper", "price": "0.50", "description": "Mild banana pepper rings", "attributes": '{"health_index": 3, "allergens": []}'},
            {"category": "veggies", "item": "Fried Onions", "price": "0.50", "description": "Crispy fried onions", "attributes": '{"health_index": 2, "allergens": []}'},
            {"category": "veggies", "item": "Corn", "price": "0.50", "description": "Sweet corn kernels", "attributes": '{"health_index": 3, "allergens": []}'},
            {"category": "veggies", "item": "Cabbage", "price": "0.50", "description": "Shredded fresh cabbage", "attributes": '{"health_index": 4, "allergens": []}'},
            {"category": "veggies", "item": "Ghee", "price": "0.50", "description": "Clarified butter", "attributes": '{"health_index": 2, "allergens": ["dairy"]}'},
            {"category": "veggies", "item": "Mango Chutney", "price": "1.00", "description": "Sweet mango chutney", "attributes": '{"health_index": 3, "allergens": []}'}
        ]

        with open(menu_path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["category", "item", "price", "description", "attributes"])
            writer.writeheader()
            writer.writerows(default_menu)

        logger.info("Initialized default menu items")

    def start_new_order(self) -> Dict[str, Any]:
        """
        Start a new customer order.

        Returns:
            Current order data
        """
        # Reset current order
        self.current_order = {
            "order_id": f"ORD{int(time.time())}",
            "customer_id": None,
            "customer_name": None,
            "phone_number": None,
            "face_id": None,
            "mood": None,
            "activity_level": None,
            "timestamp": datetime.datetime.now().isoformat(),
            "items": [],
            "total_price": 0.0,
            "weather_data": {},
            "recommendations": {},
            "feedback": {}
        }

        # Get current weather
        self.current_order["weather_data"] = self.weather_recommender.get_current_weather()

        logger.info(f"Started new order: {self.current_order['order_id']}")
        return self.current_order

    def identify_customer(self, image_data: Optional[bytes] = None, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Identify a customer by face image or phone number.

        Args:
            image_data: Optional face image data
            phone_number: Optional phone number

        Returns:
            Customer identification result
        """
        customer_data = {}

        # Try to identify by face if provided
        if image_data:
            face_result = self.face_agent.recognize_face(image_data)

            if face_result["recognized"]:
                customer_data = self.record_keeper.get_customer_by_face_id(face_result["face_id"])

                if customer_data:
                    # Update mood from face analysis
                    mood_result = self.face_agent.analyze_mood(image_data)
                    self.current_order["mood"] = mood_result.get("mood", "neutral")

                    logger.info(f"Customer identified by face: {customer_data.get('name')}")

                    # Update current order
                    self.current_order["customer_id"] = customer_data.get("customer_id")
                    self.current_order["customer_name"] = customer_data.get("name")
                    self.current_order["phone_number"] = customer_data.get("phone_number")
                    self.current_order["face_id"] = face_result["face_id"]

                    return {
                        "identified": True,
                        "method": "face",
                        "customer_data": customer_data,
                        "mood": self.current_order["mood"]
                    }

        # Try to identify by phone number if provided or face recognition failed
        if phone_number:
            customer_data = self.record_keeper.get_customer_by_phone(phone_number)

            if customer_data:
                logger.info(f"Customer identified by phone: {customer_data.get('name')}")

                # Update current order
                self.current_order["customer_id"] = customer_data.get("customer_id")
                self.current_order["customer_name"] = customer_data.get("name")
                self.current_order["phone_number"] = phone_number
                self.current_order["face_id"] = customer_data.get("face_id")

                return {
                    "identified": True,
                    "method": "phone",
                    "customer_data": customer_data,
                    "mood": self.current_order.get("mood", "neutral")
                }
            else:
                # New customer
                logger.info(f"New customer with phone: {phone_number}")

                # Generate new customer ID
                customer_id = f"CUST{int(time.time())}"

                # If we have face data, store it
                face_id = None
                if image_data:
                    face_result = self.face_agent.store_face(image_data, customer_id)
                    face_id = face_result.get("face_id")

                # Update current order
                self.current_order["customer_id"] = customer_id
                self.current_order["phone_number"] = phone_number
                self.current_order["face_id"] = face_id

                return {
                    "identified": False,
                    "method": "phone",
                    "new_customer_id": customer_id,
                    "mood": self.current_order.get("mood", "neutral")
                }

        # Failed to identify customer
        logger.warning("Failed to identify customer")
        return {
            "identified": False,
            "method": None,
            "error": "Could not identify customer"
        }

    def update_customer_info(self, name: str) -> Dict[str, Any]:
        """
        Update customer information.

        Args:
            name: Customer name

        Returns:
            Updated customer data
        """
        if not self.current_order["customer_id"]:
            return {"error": "No customer ID in current order"}

        # Update current order
        self.current_order["customer_name"] = name

        # Store or update customer record
        customer_data = {
            "customer_id": self.current_order["customer_id"],
            "name": name,
            "phone_number": self.current_order["phone_number"],
            "face_id": self.current_order["face_id"],
        }

        self.record_keeper.update_customer(customer_data)

        logger.info(f"Updated customer info: {name}")
        return customer_data

    def get_health_recommendations(self, activity_level: str) -> Dict[str, Any]:
        """
        Get health recommendations based on activity level.

        Args:
            activity_level: Customer activity level (study, active/gym, work, chilling)

        Returns:
            Health recommendations
        """
        self.current_order["activity_level"] = activity_level

        # Get previous order information if available
        previous_orders = []
        if self.current_order["customer_id"]:
            previous_orders = self.record_keeper.get_customer_orders(self.current_order["customer_id"])

        # Get recommendations
        recommendations = self.health_recommender.get_recommendations(
            activity_level=activity_level,
            customer_id=self.current_order["customer_id"],
            previous_orders=previous_orders,
            mood=self.current_order.get("mood", "neutral")
        )

        # Store recommendations
        self.current_order["recommendations"]["health"] = recommendations

        logger.info(f"Generated health recommendations for activity: {activity_level}")
        return recommendations

    def get_weather_recommendations(self) -> Dict[str, Any]:
        """
        Get weather-based recommendations.

        Returns:
            Weather recommendations
        """
        # Get current time of day
        hour = datetime.datetime.now().hour
        time_of_day = "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 17 else "evening"

        # Get recommendations
        recommendations = self.weather_recommender.get_recommendations(
            weather_data=self.current_order["weather_data"],
            time_of_day=time_of_day,
            customer_id=self.current_order["customer_id"],
            mood=self.current_order.get("mood", "neutral")
        )

        # Store recommendations
        self.current_order["recommendations"]["weather"] = recommendations

        logger.info(f"Generated weather recommendations for {time_of_day}")
        return recommendations

    def get_dish_name(self, selections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get entertaining dish name based on selections.

        Args:
            selections: Current food selections

        Returns:
            Dish name suggestions
        """
        name_suggestions = self.entertainer.generate_dish_name(
            customer_name=self.current_order.get("customer_name", ""),
            protein=selections.get("protein", ""),
            base_type=selections.get("base_type", ""),
            weather=self.current_order["weather_data"].get("condition", ""),
            mood=self.current_order.get("mood", "neutral")
        )

        # Store suggestions
        self.current_order["recommendations"]["dish_name"] = name_suggestions

        logger.info(f"Generated dish name suggestions")
        return name_suggestions

    def process_recommendation_feedback(self, recommendation_type: str, feedback: str,
                                      custom_suggestion: Optional[str] = None) -> Dict[str, Any]:
        """
        Process feedback on recommendations.

        Args:
            recommendation_type: Type of recommendation (health, weather, dish_name)
            feedback: Feedback type (ignore, accept, custom)
            custom_suggestion: Custom suggestion if provided

        Returns:
            Updated recommendations
        """
        # Store feedback
        self.current_order["feedback"][recommendation_type] = {
            "feedback": feedback,
            "custom_suggestion": custom_suggestion
        }

        # Update learning model based on feedback
        self.learner.process_feedback(
            recommendation_type=recommendation_type,
            feedback=feedback,
            custom_suggestion=custom_suggestion,
            customer_id=self.current_order.get("customer_id"),
            context={
                "mood": self.current_order.get("mood"),
                "activity_level": self.current_order.get("activity_level"),
                "weather": self.current_order["weather_data"],
                "current_selections": self.current_order.get("current_selections", {})
            }
        )

        logger.info(f"Processed {recommendation_type} recommendation feedback: {feedback}")

        # Return updated recommendations if applicable
        if feedback == "accept" or (feedback == "custom" and custom_suggestion):
            # Update the stored recommendation
            if feedback == "accept":
                # Keep existing recommendation
                return self.current_order["recommendations"].get(recommendation_type, {})
            else:
                # Update with custom suggestion
                updated_recommendations = self.current_order["recommendations"].get(recommendation_type, {})

                if recommendation_type == "health":
                    updated_recommendations["suggested_protein"] = custom_suggestion
                elif recommendation_type == "weather":
                    updated_recommendations["suggested_base"] = custom_suggestion
                elif recommendation_type == "dish_name":
                    updated_recommendations["name"] = custom_suggestion

                self.current_order["recommendations"][recommendation_type] = updated_recommendations
                return updated_recommendations

        # Return existing recommendations for "ignore" case
        return self.current_order["recommendations"].get(recommendation_type, {})

    def add_order_item(self, selections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add an item to the current order.

        Args:
            selections: Food selections for the item

        Returns:
            Updated order item
        """
        # Calculate item price
        item_price = self._calculate_item_price(selections)

        # Create order item
        order_item = {
            "item_id": f"ITEM{len(self.current_order['items']) + 1}",
            "protein": selections.get("protein", ""),
            "sauce": selections.get("sauce", ""),
            "base_type": selections.get("base_type", ""),
            "base_option": selections.get("base_option", ""),
            "veggies": selections.get("veggies", []),
            "price": item_price,
            "dish_name": selections.get("dish_name", "")
        }

        # Add to current order
        self.current_order["items"].append(order_item)
        self.current_order["total_price"] += item_price

        # Store current selections
        self.current_order["current_selections"] = selections

        logger.info(f"Added item to order: {order_item['dish_name'] or order_item['protein']}")
        return order_item

    def _calculate_item_price(self, selections: Dict[str, Any]) -> float:
        """
        Calculate the price of an order item based on selections.

        Args:
            selections: Food selections

        Returns:
            Item price
        """
        total_price = 0.0

        # Add protein price
        protein = selections.get("protein", "")
        for item in self.menu_items["proteins"]:
            if item["name"] == protein:
                total_price += item["price"]
                break

        # Add sauce price
        sauce = selections.get("sauce", "")
        for item in self.menu_items["sauces"]:
            if item["name"] == sauce:
                total_price += item["price"]
                break

        # Add base price
        base_option = selections.get("base_option", "")
        for item in self.menu_items["bases"]:
            if item["name"] == base_option:
                total_price += item["price"]
                break

        # Add veggie prices
        veggies = selections.get("veggies", [])
        veggie_count = len(veggies)
        extra_veggie_count = max(0, veggie_count - 5)  # First 5 veggies included

        # Add price for each veggie
        for veggie in veggies:
            # Check if it's a premium item like avocado
            is_premium = False
            for item in self.menu_items["veggies"]:
                if item["name"] == veggie:
                    if item["price"] > 1.0:  # Premium veggie
                        total_price += item["price"]
                        is_premium = True
                    break

            # Count non-premium veggies for the extra charge
            if not is_premium and veggies.index(veggie) >= 5:
                total_price += 1.0  # $1 for each extra regular veggie

        return total_price

    def complete_order(self) -> Dict[str, Any]:
        """
        Complete the current order.

        Returns:
            Completed order data
        """
        # Save the order to records
        order_data = {
            "order_id": self.current_order["order_id"],
            "customer_id": self.current_order["customer_id"],
            "timestamp": self.current_order["timestamp"],
            "items": self.current_order["items"],
            "total_price": self.current_order["total_price"],
            "weather": self.current_order["weather_data"],
            "activity": self.current_order["activity_level"],
            "mood": self.current_order["mood"]
        }

        self.record_keeper.save_order(order_data)

        # Save feedback
        if self.current_order["feedback"]:
            feedback_data = {
                "feedback_id": f"FDB{int(time.time())}",
                "order_id": self.current_order["order_id"],
                "customer_id": self.current_order["customer_id"],
                "timestamp": datetime.datetime.now().isoformat(),
                "health_feedback": json.dumps(self.current_order["feedback"].get("health", {})),
                "weather_feedback": json.dumps(self.current_order["feedback"].get("weather", {})),
                "name_feedback": json.dumps(self.current_order["feedback"].get("dish_name", {}))
            }

            self.record_keeper.save_feedback(feedback_data)

        # Generate receipt
        receipt_path = self._generate_receipt()

        logger.info(f"Completed order: {self.current_order['order_id']}")
        return {
            "order_id": self.current_order["order_id"],
            "customer_name": self.current_order["customer_name"],
            "total_price": self.current_order["total_price"],
            "item_count": len(self.current_order["items"]),
            "receipt_path": receipt_path
        }

    def _generate_receipt(self) -> str:
        """
        Generate a receipt for the current order.

        Returns:
            Path to the receipt file
        """
        receipt_dir = os.path.join(self.data_dir, "receipts")
        receipt_path = os.path.join(receipt_dir, f"receipt_{self.current_order['order_id']}.txt")

        # Create receipt content
        receipt_content = [
            "=" * 40,
            f"ORDER #{self.current_order['order_id']}",
            "=" * 40,
            f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Customer: {self.current_order['customer_name'] or 'Guest'}"
        ]

        if self.current_order["phone_number"]:
            receipt_content.append(f"Phone: {self.current_order['phone_number']}")

        receipt_content.extend([
            "-" * 40,
            "ITEMS:",
            "-" * 40
        ])

        # Add items
        for i, item in enumerate(self.current_order["items"], 1):
            dish_name = item.get("dish_name") or f"{item['protein']} on {item['base_option']}"
            receipt_content.append(f"{i}. {dish_name}")
            receipt_content.append(f"   {item['protein']} with {item['sauce']} on {item['base_option']}")
            receipt_content.append(f"   Veggies: {', '.join(item['veggies'])}")
            receipt_content.append(f"   Price: ${item['price']:.2f}")
            receipt_content.append("")

        receipt_content.extend([
            "-" * 40,
            f"TOTAL: ${self.current_order['total_price']:.2f}",
            "=" * 40,
            "Thank you for your order!",
            "=" * 40
        ])

        # Write receipt to file
        with open(receipt_path, 'w') as f:
            f.write("\n".join(receipt_content))

        logger.info(f"Generated receipt at {receipt_path}")
        return receipt_path

    def get_order_statistics(self) -> Dict[str, Any]:
        """
        Get order statistics for the system.

        Returns:
            Order statistics
        """
        return self.record_keeper.get_statistics()

    def export_daily_data(self, export_dir: str = "exports") -> Dict[str, Any]:
        """
        Export daily data for external processing.

        Args:
            export_dir: Directory for exports

        Returns:
            Export results
        """
        os.makedirs(export_dir, exist_ok=True)

        date_str = datetime.datetime.now().strftime("%Y%m%d")

        # Export orders
        orders_path = os.path.join(export_dir, f"orders_{date_str}.csv")
        orders_result = self.record_keeper.export_orders(orders_path)

        # Export customers
        customers_path = os.path.join(export_dir, f"customers_{date_str}.csv")
        customers_result = self.record_keeper.export_customers(customers_path)

        # Export feedback
        feedback_path = os.path.join(export_dir, f"feedback_{date_str}.csv")
        feedback_result = self.record_keeper.export_feedback(feedback_path)

        logger.info(f"Exported daily data to {export_dir}")

        return {
            "orders_export": orders_result,
            "customers_export": customers_result,
            "feedback_export": feedback_result,
            "export_date": date_str,
            "export_dir": export_dir
        }

def main():
    """Main entry point for the kiosk application."""
    # Initialize the kiosk system
    kiosk = SelfOrderingKiosk()

    # Run the UI
    run_kiosk_ui(kiosk)

if __name__ == "__main__":
    main()