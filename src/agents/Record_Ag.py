import os
import csv
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("record_keeper_agent")

class RecordKeeperAgent:
    """Enhanced agent for managing customer and order records with improved customer tracking."""

    def __init__(self, orders_path: str, feedback_path: str, customers_path: str):
        """
        Initialize the record keeper agent.

        Args:
            orders_path: Path to orders CSV file
            feedback_path: Path to feedback CSV file
            customers_path: Path to customers CSV file
        """
        self.orders_path = orders_path
        self.feedback_path = feedback_path
        self.customers_path = customers_path

        # Ensure directories exist
        for path in [orders_path, feedback_path, customers_path]:
            os.makedirs(os.path.dirname(path), exist_ok=True)

        # Create files with headers if they don't exist
        self._initialize_csv_file(
            customers_path,
            ["customer_id", "name", "phone_number", "face_id", "visit_count", "last_visit", "created_at", "preferences"]
        )

        self._initialize_csv_file(
            orders_path,
            ["order_id", "customer_id", "phone_number", "customer_name", "timestamp", "items", "total_price", "weather", "activity", "mood"]
        )

        self._initialize_csv_file(
            feedback_path,
            ["feedback_id", "order_id", "customer_id", "timestamp", "health_feedback", "weather_feedback", "name_feedback"]
        )

        logger.info("Enhanced record keeper agent initialized")

    def _initialize_csv_file(self, file_path: str, headers: List[str]) -> None:
        """
        Initialize a CSV file with headers if it doesn't exist.

        Args:
            file_path: Path to CSV file
            headers: Column headers
        """
        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
            logger.debug(f"Initialized CSV file: {file_path}")

    def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve customer information by customer ID.

        Args:
            customer_id: Customer ID to search for

        Returns:
            Customer data or None if not found
        """
        try:
            with open(self.customers_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["customer_id"] == customer_id:
                        # Parse preferences from JSON if exists
                        preferences = {}
                        if "preferences" in row and row["preferences"]:
                            try:
                                preferences = json.loads(row["preferences"])
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse preferences for customer {customer_id}")

                        return {
                            "customer_id": row["customer_id"],
                            "name": row["name"],
                            "phone_number": row["phone_number"],
                            "face_id": row["face_id"],
                            "visit_count": int(row["visit_count"]) if row["visit_count"] else 0,
                            "last_visit": row["last_visit"],
                            "created_at": row["created_at"],
                            "preferences": preferences
                        }
            return None
        except Exception as e:
            logger.error(f"Error finding customer by ID: {e}")
            return None

    def get_customer_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve customer information by phone number.

        Args:
            phone_number: Phone number to search for

        Returns:
            Customer data or None if not found
        """
        try:
            # Normalize phone number - remove non-digits
            phone_number = ''.join(c for c in phone_number if c.isdigit())

            with open(self.customers_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Compare normalized phone numbers
                    row_phone = ''.join(c for c in row["phone_number"] if c.isdigit())
                    if row_phone == phone_number:
                        # Parse preferences from JSON if exists
                        preferences = {}
                        if "preferences" in row and row["preferences"]:
                            try:
                                preferences = json.loads(row["preferences"])
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse preferences for phone {phone_number}")

                        return {
                            "customer_id": row["customer_id"],
                            "name": row["name"],
                            "phone_number": row["phone_number"],
                            "face_id": row["face_id"],
                            "visit_count": int(row["visit_count"]) if row["visit_count"] else 0,
                            "last_visit": row["last_visit"],
                            "created_at": row["created_at"],
                            "preferences": preferences
                        }
            return None
        except Exception as e:
            logger.error(f"Error finding customer by phone: {e}")
            return None

    def update_customer(self, customer_data: Dict[str, Any]) -> bool:
        """
        Update customer information.

        Args:
            customer_data: Customer data to update

        Returns:
            Success status
        """
        customer_id = customer_data.get("customer_id")
        phone_number = customer_data.get("phone_number")

        if not (customer_id or phone_number):
            logger.error("Cannot update customer: Missing customer_id or phone_number")
            return False

        try:
            # Read all customers
            customers = []
            customer_exists = False
            fieldnames = []

            with open(self.customers_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                fieldnames = reader.fieldnames or []

                for row in reader:
                    # Check if customer exists by ID or phone
                    if (customer_id and row["customer_id"] == customer_id) or \
                       (phone_number and self._normalize_phone(row["phone_number"]) == self._normalize_phone(phone_number)):
                        # Update existing customer
                        row["name"] = customer_data.get("name", row["name"])

                        if phone_number:
                            row["phone_number"] = phone_number

                        if "face_id" in customer_data:
                            row["face_id"] = customer_data.get("face_id", row["face_id"])

                        # Update visit count
                        visit_count = int(row["visit_count"]) if row["visit_count"] else 0
                        row["visit_count"] = str(visit_count + 1)

                        # Update last visit
                        row["last_visit"] = datetime.now().isoformat()

                        # Update preferences if provided
                        if "preferences" in customer_data:
                            # Ensure preferences is a JSON string
                            if isinstance(customer_data["preferences"], dict):
                                row["preferences"] = json.dumps(customer_data["preferences"])
                            else:
                                row["preferences"] = customer_data["preferences"]

                        customer_exists = True
                        customer_id = row["customer_id"]  # Ensure we have the ID for later

                    customers.append(row)

            # If customer doesn't exist, add new entry
            if not customer_exists:
                if not customer_id:
                    customer_id = f"CUST{uuid.uuid4().hex[:8]}"

                new_customer = {
                    "customer_id": customer_id,
                    "name": customer_data.get("name", ""),
                    "phone_number": phone_number or "",
                    "face_id": customer_data.get("face_id", ""),
                    "visit_count": "1",
                    "last_visit": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                    "preferences": customer_data.get("preferences", "")
                }

                # Ensure preferences is a JSON string
                if isinstance(new_customer["preferences"], dict):
                    new_customer["preferences"] = json.dumps(new_customer["preferences"])

                customers.append(new_customer)

            # Write updated customers back to CSV
            with open(self.customers_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(customers)

            logger.info(f"{'Updated' if customer_exists else 'Added'} customer {customer_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating customer: {e}")
            return False

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number by removing non-digit characters."""
        return ''.join(c for c in phone if c.isdigit())

    def save_order(self, order_data: Dict[str, Any]) -> bool:
        """
        Save an order to the records with enhanced customer linking.

        Args:
            order_data: Order data to save

        Returns:
            Success status
        """
        order_id = order_data.get("order_id")
        if not order_id:
            logger.error("Cannot save order: Missing order_id")
            return False

        try:
            # Include customer phone and name in order record if available
            customer_phone = order_data.get("customer_phone", "")
            customer_name = order_data.get("customer_name", "")

            # Prepare row for CSV
            row = {
                "order_id": order_id,
                "customer_id": order_data.get("customer_id", ""),
                "phone_number": customer_phone,
                "customer_name": customer_name,
                "timestamp": order_data.get("timestamp", datetime.now().isoformat()),
                "items": json.dumps(order_data.get("items", [])),
                "total_price": str(order_data.get("total_price", 0.0)),
                "weather": json.dumps(order_data.get("weather", {})),
                "activity": order_data.get("activity", ""),
                "mood": order_data.get("mood", "")
            }

            # Read existing file to get headers
            fieldnames = []
            try:
                with open(self.orders_path, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    fieldnames = reader.fieldnames or []
            except FileNotFoundError:
                # If file doesn't exist, use the keys from our row
                fieldnames = list(row.keys())

            # Ensure all our new fields are in the fieldnames list
            for field in row.keys():
                if field not in fieldnames:
                    fieldnames.append(field)

            # Append to CSV
            with open(self.orders_path, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if file.tell() == 0:  # File is empty, write header
                    writer.writeheader()
                writer.writerow(row)

            # Update customer's preferences if applicable
            if customer_phone:
                self._update_customer_preferences(customer_phone, order_data)

            logger.info(f"Saved order {order_id} for customer {customer_name} ({customer_phone})")
            return True

        except Exception as e:
            logger.error(f"Error saving order: {e}")
            return False

    def _update_customer_preferences(self, phone_number: str, order_data: Dict[str, Any]) -> None:
        """
        Update customer preferences based on their order.

        Args:
            phone_number: Customer's phone number
            order_data: Order data containing selections
        """
        if not phone_number:
            return

        # Get customer data
        customer = self.get_customer_by_phone(phone_number)
        if not customer:
            return

        try:
            # Get current preferences
            preferences = customer.get("preferences", {})
            if isinstance(preferences, str) and preferences:
                preferences = json.loads(preferences)
            elif not preferences:
                preferences = {}

            # Initialize order counters if needed
            if "order_counts" not in preferences:
                preferences["order_counts"] = {}

            # Extract items from the order
            items = order_data.get("items", [])
            for item in items:
                # Count protein selections
                protein = item.get("protein")
                if protein:
                    preferences["order_counts"]["proteins"] = preferences["order_counts"].get("proteins", {})
                    preferences["order_counts"]["proteins"][protein] = preferences["order_counts"]["proteins"].get(protein, 0) + 1

                # Count sauce selections
                sauce = item.get("sauce")
                if sauce:
                    preferences["order_counts"]["sauces"] = preferences["order_counts"].get("sauces", {})
                    preferences["order_counts"]["sauces"][sauce] = preferences["order_counts"]["sauces"].get(sauce, 0) + 1

                # Count base type selections
                base_type = item.get("base_type")
                if base_type:
                    preferences["order_counts"]["base_types"] = preferences["order_counts"].get("base_types", {})
                    preferences["order_counts"]["base_types"][base_type] = preferences["order_counts"]["base_types"].get(base_type, 0) + 1

                # Count veggie selections
                veggies = item.get("veggies", [])
                if veggies:
                    preferences["order_counts"]["veggies"] = preferences["order_counts"].get("veggies", {})
                    for veggie in veggies:
                        preferences["order_counts"]["veggies"][veggie] = preferences["order_counts"]["veggies"].get(veggie, 0) + 1

            # Update activity preferences
            activity = order_data.get("activity")
            if activity:
                preferences["activities"] = preferences.get("activities", {})
                preferences["activities"][activity] = preferences["activities"].get(activity, 0) + 1

            # Store updated preferences
            customer_data = {
                "phone_number": phone_number,
                "preferences": preferences
            }
            self.update_customer(customer_data)

            logger.info(f"Updated preferences for customer with phone {phone_number}")

        except Exception as e:
            logger.error(f"Error updating customer preferences: {e}")

    def get_customer_orders(self, customer_id: Optional[str] = None, phone_number: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all orders for a specific customer by ID or phone number.

        Args:
            customer_id: Customer ID
            phone_number: Customer phone number

        Returns:
            List of customer order data
        """
        orders = []

        if not (customer_id or phone_number):
            logger.warning("No customer ID or phone number provided to get_customer_orders")
            return orders

        try:
            with open(self.orders_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Match by customer ID or phone number (normalized)
                    if ((customer_id and row["customer_id"] == customer_id) or
                        (phone_number and row.get("phone_number") and
                         self._normalize_phone(row["phone_number"]) == self._normalize_phone(phone_number))):

                        # Parse items from JSON
                        items = []
                        try:
                            items = json.loads(row["items"])
                        except json.JSONDecodeError:
                            pass

                        # Parse weather from JSON
                        weather = {}
                        try:
                            weather = json.loads(row["weather"])
                        except json.JSONDecodeError:
                            pass

                        orders.append({
                            "order_id": row["order_id"],
                            "customer_id": row["customer_id"],
                            "phone_number": row.get("phone_number", ""),
                            "customer_name": row.get("customer_name", ""),
                            "timestamp": row["timestamp"],
                            "items": items,
                            "total_price": float(row["total_price"]) if row["total_price"] else 0.0,
                            "weather": weather,
                            "activity": row["activity"],
                            "mood": row["mood"]
                        })

            # Sort by timestamp (newest first)
            orders.sort(key=lambda x: x["timestamp"], reverse=True)

            logger.info(f"Retrieved {len(orders)} orders for customer {customer_id or phone_number}")
            return orders

        except Exception as e:
            logger.error(f"Error retrieving customer orders: {e}")
            return []

    def get_customer_preferences(self, phone_number: str) -> Dict[str, Any]:
        """
        Get a customer's preferences based on their order history.

        Args:
            phone_number: Customer's phone number

        Returns:
            Dictionary of customer preferences
        """
        customer = self.get_customer_by_phone(phone_number)
        if not customer:
            return {}

        preferences = customer.get("preferences", {})
        if isinstance(preferences, str) and preferences:
            try:
                preferences = json.loads(preferences)
            except json.JSONDecodeError:
                preferences = {}

        # If no stored preferences, generate from order history
        if not preferences or not preferences.get("order_counts"):
            orders = self.get_customer_orders(phone_number=phone_number)

            # Initialize preferences structure
            preferences = {
                "order_counts": {
                    "proteins": {},
                    "sauces": {},
                    "base_types": {},
                    "veggies": {}
                },
                "activities": {}
            }

            # Process orders to build preferences
            for order in orders:
                # Track activity
                activity = order.get("activity")
                if activity:
                    preferences["activities"][activity] = preferences["activities"].get(activity, 0) + 1

                # Process items
                for item in order.get("items", []):
                    if isinstance(item, dict):
                        # Count protein
                        protein = item.get("protein")
                        if protein:
                            preferences["order_counts"]["proteins"][protein] = preferences["order_counts"]["proteins"].get(protein, 0) + 1

                        # Count sauce
                        sauce = item.get("sauce")
                        if sauce:
                            preferences["order_counts"]["sauces"][sauce] = preferences["order_counts"]["sauces"].get(sauce, 0) + 1

                        # Count base type
                        base_type = item.get("base_type")
                        if base_type:
                            preferences["order_counts"]["base_types"][base_type] = preferences["order_counts"]["base_types"].get(base_type, 0) + 1

                        # Count veggies
                        veggies = item.get("veggies", [])
                        for veggie in veggies:
                            preferences["order_counts"]["veggies"][veggie] = preferences["order_counts"]["veggies"].get(veggie, 0) + 1

            # Store generated preferences
            if orders:
                customer_data = {
                    "phone_number": phone_number,
                    "preferences": preferences
                }
                self.update_customer(customer_data)

        return preferences

    def get_recommended_items(self, phone_number: str, activity_level: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get recommended items based on customer's order history and activity level.

        Args:
            phone_number: Customer's phone number
            activity_level: Optional current activity level

        Returns:
            Dictionary of recommended items by category
        """
        preferences = self.get_customer_preferences(phone_number)
        if not preferences:
            return {}

        recommendations = {
            "proteins": [],
            "sauces": [],
            "base_types": [],
            "veggies": []
        }

        # Get top items by category
        order_counts = preferences.get("order_counts", {})

        # Function to get top N items from a category
        def get_top_items(category, n=3):
            if category in order_counts:
                # Sort by count, descending
                sorted_items = sorted(order_counts[category].items(), key=lambda x: x[1], reverse=True)
                # Return top N item names
                return [item[0] for item in sorted_items[:n]]
            return []

        # Get top items for each category
        recommendations["proteins"] = get_top_items("proteins")
        recommendations["sauces"] = get_top_items("sauces")
        recommendations["base_types"] = get_top_items("base_types")
        recommendations["veggies"] = get_top_items("veggies", 5)

        # If activity level provided, prioritize items for that activity
        # This would reference a mapping of recommended items by activity
        # For now, we'll use a simple approach
        if activity_level:
            # Example of logic to adjust recommendations based on activity
            activity_recommendations = {
                "study": {
                    "proteins": ["Egg", "Paneer/Indian Cheese"],
                    "base_types": ["Wrap", "Bowl"]
                },
                "active": {
                    "proteins": ["Chicken", "Soya"],
                    "base_types": ["Bowl", "Biryani"]
                },
                "work": {
                    "proteins": ["Chicken", "Egg"],
                    "base_types": ["Sandwich", "Wrap"]
                },
                "chilling": {
                    "proteins": ["Paneer/Indian Cheese", "Potato"],
                    "base_types": ["Bowl", "Wrap"]
                }
            }

            # If we have activity recommendations, merge them with personal preferences
            if activity_level in activity_recommendations:
                act_recs = activity_recommendations[activity_level]

                # Merge proteins: put activity recommendations first, then add personal preferences
                if "proteins" in act_recs:
                    new_proteins = act_recs["proteins"].copy()
                    for protein in recommendations["proteins"]:
                        if protein not in new_proteins:
                            new_proteins.append(protein)
                    recommendations["proteins"] = new_proteins[:3]  # Limit to top 3

                # Similarly for base types
                if "base_types" in act_recs:
                    new_bases = act_recs["base_types"].copy()
                    for base in recommendations["base_types"]:
                        if base not in new_bases:
                            new_bases.append(base)
                    recommendations["base_types"] = new_bases[:3]  # Limit to top 3

        return recommendations

    def save_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """
        Save customer feedback to the records.

        Args:
            feedback_data: Feedback data to save

        Returns:
            Success status
        """
        feedback_id = feedback_data.get("feedback_id")
        if not feedback_id:
            logger.error("Cannot save feedback: Missing feedback_id")
            return False

        try:
            # Prepare row for CSV
            row = {
                "feedback_id": feedback_id,
                "order_id": feedback_data.get("order_id", ""),
                "customer_id": feedback_data.get("customer_id", ""),
                "timestamp": feedback_data.get("timestamp", datetime.now().isoformat()),
                "health_feedback": feedback_data.get("health_feedback", "{}"),
                "weather_feedback": feedback_data.get("weather_feedback", "{}"),
                "name_feedback": feedback_data.get("name_feedback", "{}")
            }

            # Append to CSV
            with open(self.feedback_path, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=list(row.keys()))
                if file.tell() == 0:  # File is empty, write header
                    writer.writeheader()
                writer.writerow(row)

            logger.info(f"Saved feedback {feedback_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return False