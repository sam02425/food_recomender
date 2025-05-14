# /agents/Record_Keeper_Ag.py
"""
Record Keeper Agent for storing and retrieving customer and order data.
"""

import os
import csv
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("record_keeper_agent")

class RecordKeeperAgent:
    """Agent for managing customer and order records."""

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
            ["customer_id", "name", "phone_number", "face_id", "visit_count", "last_visit", "created_at"]
        )

        self._initialize_csv_file(
            orders_path,
            ["order_id", "customer_id", "timestamp", "items", "total_price", "weather", "activity", "mood"]
        )

        self._initialize_csv_file(
            feedback_path,
            ["feedback_id", "order_id", "customer_id", "timestamp", "health_feedback", "weather_feedback", "name_feedback"]
        )

        logger.info("Record keeper agent initialized")

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

    def get_customer_by_face_id(self, face_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve customer information by face ID.

        Args:
            face_id: Face ID to search for

        Returns:
            Customer data or None if not found
        """
        try:
            with open(self.customers_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["face_id"] == face_id:
                        return {
                            "customer_id": row["customer_id"],
                            "name": row["name"],
                            "phone_number": row["phone_number"],
                            "face_id": row["face_id"],
                            "visit_count": int(row["visit_count"]) if row["visit_count"] else 0,
                            "last_visit": row["last_visit"],
                            "created_at": row["created_at"]
                        }
            return None
        except Exception as e:
            logger.error(f"Error finding customer by face ID: {e}")
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
            with open(self.customers_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["phone_number"] == phone_number:
                        return {
                            "customer_id": row["customer_id"],
                            "name": row["name"],
                            "phone_number": row["phone_number"],
                            "face_id": row["face_id"],
                            "visit_count": int(row["visit_count"]) if row["visit_count"] else 0,
                            "last_visit": row["last_visit"],
                            "created_at": row["created_at"]
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
        if not customer_id:
            logger.error("Cannot update customer: Missing customer_id")
            return False

        try:
            # Read all customers
            customers = []
            customer_exists = False

            with open(self.customers_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["customer_id"] == customer_id:
                        # Update existing customer
                        row["name"] = customer_data.get("name", row["name"])
                        row["phone_number"] = customer_data.get("phone_number", row["phone_number"])
                        row["face_id"] = customer_data.get("face_id", row["face_id"])

                        # Update visit count
                        visit_count = int(row["visit_count"]) if row["visit_count"] else 0
                        row["visit_count"] = str(visit_count + 1)

                        # Update last visit
                        row["last_visit"] = datetime.now().isoformat()

                        customer_exists = True

                    customers.append(row)

            # If customer doesn't exist, add new entry
            if not customer_exists:
                new_customer = {
                    "customer_id": customer_id,
                    "name": customer_data.get("name", ""),
                    "phone_number": customer_data.get("phone_number", ""),
                    "face_id": customer_data.get("face_id", ""),
                    "visit_count": "1",
                    "last_visit": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat()
                }

                customers.append(new_customer)

            # Write updated customers back to CSV
            with open(self.customers_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(customers)

            logger.info(f"{'Updated' if customer_exists else 'Added'} customer {customer_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating customer: {e}")
            return False

    def save_order(self, order_data: Dict[str, Any]) -> bool:
        """
        Save an order to the records.

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
            # Prepare row for CSV
            row = {
                "order_id": order_id,
                "customer_id": order_data.get("customer_id", ""),
                "timestamp": order_data.get("timestamp", datetime.now().isoformat()),
                "items": json.dumps(order_data.get("items", [])),
                "total_price": str(order_data.get("total_price", 0.0)),
                "weather": json.dumps(order_data.get("weather", {})),
                "activity": order_data.get("activity", ""),
                "mood": order_data.get("mood", "")
            }

            # Append to CSV
            with open(self.orders_path, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=list(row.keys()))
                writer.writerow(row)

            logger.info(f"Saved order {order_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving order: {e}")
            return False

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
                writer.writerow(row)

            logger.info(f"Saved feedback {feedback_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return False

    def get_customer_orders(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Get all orders for a specific customer.

        Args:
            customer_id: Customer ID

        Returns:
            List of customer order data
        """
        orders = []

        try:
            with open(self.orders_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["customer_id"] == customer_id:
                        # Parse items from JSON
                        items = []
                        try:
                            items = json.loads(row["items"])
                        except:
                            pass

                        # Parse weather from JSON
                        weather = {}
                        try:
                            weather = json.loads(row["weather"])
                        except:
                            pass

                        orders.append({
                            "order_id": row["order_id"],
                            "customer_id": row["customer_id"],
                            "timestamp": row["timestamp"],
                            "items": items,
                            "total_price": float(row["total_price"]) if row["total_price"] else 0.0,
                            "weather": weather,
                            "activity": row["activity"],
                            "mood": row["mood"]
                        })

            # Sort by timestamp (newest first)
            orders.sort(key=lambda x: x["timestamp"], reverse=True)

            logger.info(f"Retrieved {len(orders)} orders for customer {customer_id}")
            return orders

        except Exception as e:
            logger.error(f"Error retrieving customer orders: {e}")
            return []

    def get_order_details(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific order.

        Args:
            order_id: Order ID

        Returns:
            Order details or None if not found
        """
        try:
            with open(self.orders_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["order_id"] == order_id:
                        # Parse items from JSON
                        items = []
                        try:
                            items = json.loads(row["items"])
                        except:
                            pass

                        # Parse weather from JSON
                        weather = {}
                        try:
                            weather = json.loads(row["weather"])
                        except:
                            pass

                        return {
                            "order_id": row["order_id"],
                            "customer_id": row["customer_id"],
                            "timestamp": row["timestamp"],
                            "items": items,
                            "total_price": float(row["total_price"]) if row["total_price"] else 0.0,
                            "weather": weather,
                            "activity": row["activity"],
                            "mood": row["mood"]
                        }

            logger.warning(f"Order not found: {order_id}")
            return None

        except Exception as e:
            logger.error(f"Error retrieving order details: {e}")
            return None

    def get_customer_feedback(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Get all feedback entries for a specific customer.

        Args:
            customer_id: Customer ID

        Returns:
            List of customer feedback data
        """
        feedback_entries = []

        try:
            with open(self.feedback_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["customer_id"] == customer_id:
                        # Parse feedback JSON
                        health_feedback = {}
                        weather_feedback = {}
                        name_feedback = {}

                        try:
                            health_feedback = json.loads(row["health_feedback"])
                        except:
                            pass

                        try:
                            weather_feedback = json.loads(row["weather_feedback"])
                        except:
                            pass

                        try:
                            name_feedback = json.loads(row["name_feedback"])
                        except:
                            pass

                        feedback_entries.append({
                            "feedback_id": row["feedback_id"],
                            "order_id": row["order_id"],
                            "customer_id": row["customer_id"],
                            "timestamp": row["timestamp"],
                            "health_feedback": health_feedback,
                            "weather_feedback": weather_feedback,
                            "name_feedback": name_feedback
                        })

            # Sort by timestamp (newest first)
            feedback_entries.sort(key=lambda x: x["timestamp"], reverse=True)

            logger.info(f"Retrieved {len(feedback_entries)} feedback entries for customer {customer_id}")
            return feedback_entries

        except Exception as e:
            logger.error(f"Error retrieving customer feedback: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about orders and customers.

        Returns:
            Statistical information
        """
        stats = {
            "total_orders": 0,
            "total_customers": 0,
            "total_revenue": 0.0,
            "avg_order_value": 0.0,
            "popular_proteins": {},
            "popular_sauces": {},
            "popular_bases": {},
            "activity_distribution": {},
            "mood_distribution": {},
            "last_update": datetime.now().isoformat()
        }

        try:
            # Count customers
            with open(self.customers_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                stats["total_customers"] = sum(1 for _ in reader)

            # Process orders
            orders = []
            with open(self.orders_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    stats["total_orders"] += 1
                    stats["total_revenue"] += float(row["total_price"]) if row["total_price"] else 0.0

                    # Activity distribution
                    activity = row["activity"]
                    if activity:
                        stats["activity_distribution"][activity] = stats["activity_distribution"].get(activity, 0) + 1

                    # Mood distribution
                    mood = row["mood"]
                    if mood:
                        stats["mood_distribution"][mood] = stats["mood_distribution"].get(mood, 0) + 1

                    # Process items
                    try:
                        items = json.loads(row["items"])
                        for item in items:
                            # Count proteins
                            protein = item.get("protein")
                            if protein:
                                stats["popular_proteins"][protein] = stats["popular_proteins"].get(protein, 0) + 1

                            # Count sauces
                            sauce = item.get("sauce")
                            if sauce:
                                stats["popular_sauces"][sauce] = stats["popular_sauces"].get(sauce, 0) + 1

                            # Count bases
                            base_type = item.get("base_type")
                            if base_type:
                                stats["popular_bases"][base_type] = stats["popular_bases"].get(base_type, 0) + 1
                    except:
                        pass

            # Calculate average order value
            if stats["total_orders"] > 0:
                stats["avg_order_value"] = stats["total_revenue"] / stats["total_orders"]

            # Sort popularity dictionaries
            stats["popular_proteins"] = dict(sorted(
                stats["popular_proteins"].items(),
                key=lambda x: x[1],
                reverse=True
            ))

            stats["popular_sauces"] = dict(sorted(
                stats["popular_sauces"].items(),
                key=lambda x: x[1],
                reverse=True
            ))

            stats["popular_bases"] = dict(sorted(
                stats["popular_bases"].items(),
                key=lambda x: x[1],
                reverse=True
            ))

            logger.info(f"Generated statistics: {stats['total_orders']} orders, {stats['total_customers']} customers")
            return stats

        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
            return stats

    def export_orders(self, export_path: str) -> Dict[str, Any]:
        """
        Export orders data to a CSV file.

        Args:
            export_path: Path to export file

        Returns:
            Export result
        """
        try:
            if os.path.exists(self.orders_path):
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(export_path), exist_ok=True)

                # Copy orders to export file
                with open(self.orders_path, 'r', newline='') as src_file, \
                     open(export_path, 'w', newline='') as dst_file:
                    reader = csv.DictReader(src_file)
                    writer = csv.DictWriter(dst_file, fieldnames=reader.fieldnames)
                    writer.writeheader()

                    row_count = 0
                    for row in reader:
                        writer.writerow(row)
                        row_count += 1

                logger.info(f"Exported {row_count} orders to {export_path}")

                return {
                    "success": True,
                    "file_path": export_path,
                    "row_count": row_count,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning(f"Orders file does not exist: {self.orders_path}")

                return {
                    "success": False,
                    "message": "Orders file does not exist"
                }

        except Exception as e:
            logger.error(f"Error exporting orders: {e}")

            return {
                "success": False,
                "message": f"Error exporting orders: {str(e)}"
            }

    def export_customers(self, export_path: str) -> Dict[str, Any]:
        """
        Export customers data to a CSV file.

        Args:
            export_path: Path to export file

        Returns:
            Export result
        """
        try:
            if os.path.exists(self.customers_path):
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(export_path), exist_ok=True)

                # Copy customers to export file
                with open(self.customers_path, 'r', newline='') as src_file, \
                     open(export_path, 'w', newline='') as dst_file:
                    reader = csv.DictReader(src_file)
                    writer = csv.DictWriter(dst_file, fieldnames=reader.fieldnames)
                    writer.writeheader()

                    row_count = 0
                    for row in reader:
                        writer.writerow(row)
                        row_count += 1

                logger.info(f"Exported {row_count} customers to {export_path}")

                return {
                    "success": True,
                    "file_path": export_path,
                    "row_count": row_count,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning(f"Customers file does not exist: {self.customers_path}")

                return {
                    "success": False,
                    "message": "Customers file does not exist"
                }

        except Exception as e:
            logger.error(f"Error exporting customers: {e}")

            return {
                "success": False,
                "message": f"Error exporting customers: {str(e)}"
            }

    def export_feedback(self, export_path: str) -> Dict[str, Any]:
        """
        Export feedback data to a CSV file.

        Args:
            export_path: Path to export file

        Returns:
            Export result
        """
        try:
            if os.path.exists(self.feedback_path):
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(export_path), exist_ok=True)

                # Copy feedback to export file
                with open(self.feedback_path, 'r', newline='') as src_file, \
                     open(export_path, 'w', newline='') as dst_file:
                    reader = csv.DictReader(src_file)
                    writer = csv.DictWriter(dst_file, fieldnames=reader.fieldnames)
                    writer.writeheader()

                    row_count = 0
                    for row in reader:
                        writer.writerow(row)
                        row_count += 1

                logger.info(f"Exported {row_count} feedback entries to {export_path}")

                return {
                    "success": True,
                    "file_path": export_path,
                    "row_count": row_count,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning(f"Feedback file does not exist: {self.feedback_path}")

                return {
                    "success": False,
                    "message": "Feedback file does not exist"
                }

        except Exception as e:
            logger.error(f"Error exporting feedback: {e}")

            return {
                "success": False,
                "message": f"Error exporting feedback: {str(e)}"
            }

    def search_customer(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for customers by name or phone number.

        Args:
            search_term: Term to search for

        Returns:
            List of matching customer records
        """
        results = []

        try:
            with open(self.customers_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Check if search term matches name or phone
                    if (search_term.lower() in row["name"].lower() or
                        search_term in row["phone_number"]):
                        results.append({
                            "customer_id": row["customer_id"],
                            "name": row["name"],
                            "phone_number": row["phone_number"],
                            "face_id": row["face_id"],
                            "visit_count": int(row["visit_count"]) if row["visit_count"] else 0,
                            "last_visit": row["last_visit"],
                            "created_at": row["created_at"]
                        })

            logger.info(f"Found {len(results)} customers matching '{search_term}'")
            return results

        except Exception as e:
            logger.error(f"Error searching customers: {e}")
            return []

    def get_frequent_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most frequent customers based on visit count.

        Args:
            limit: Maximum number of customers to return

        Returns:
            List of top customers
        """
        customers = []

        try:
            with open(self.customers_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    customers.append({
                        "customer_id": row["customer_id"],
                        "name": row["name"],
                        "phone_number": row["phone_number"],
                        "visit_count": int(row["visit_count"]) if row["visit_count"] else 0,
                        "last_visit": row["last_visit"]
                    })

            # Sort by visit count (highest first)
            customers.sort(key=lambda x: x["visit_count"], reverse=True)

            # Return top customers
            top_customers = customers[:limit]

            logger.info(f"Retrieved {len(top_customers)} frequent customers")
            return top_customers

        except Exception as e:
            logger.error(f"Error retrieving frequent customers: {e}")
            return []

    def delete_customer(self, customer_id: str) -> bool:
        """
        Delete a customer record (for GDPR compliance).

        Args:
            customer_id: Customer ID to delete

        Returns:
            Success status
        """
        try:
            # Read all customers except the one to delete
            customers = []
            customer_found = False

            with open(self.customers_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["customer_id"] != customer_id:
                        customers.append(row)
                    else:
                        customer_found = True

            if not customer_found:
                logger.warning(f"Customer not found for deletion: {customer_id}")
                return False

            # Write updated customers back to CSV
            with open(self.customers_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(customers)

            # Also anonymize orders and feedback
            self._anonymize_customer_data(customer_id)

            logger.info(f"Deleted customer {customer_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting customer: {e}")
            return False

    def _anonymize_customer_data(self, customer_id: str) -> None:
        """
        Anonymize customer data in orders and feedback.

        Args:
            customer_id: Customer ID to anonymize
        """
        try:
            # Anonymize orders
            orders = []

            with open(self.orders_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["customer_id"] == customer_id:
                        row["customer_id"] = "ANONYMIZED"
                    orders.append(row)

            with open(self.orders_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(orders)

            # Anonymize feedback
            feedback_entries = []

            with open(self.feedback_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["customer_id"] == customer_id:
                        row["customer_id"] = "ANONYMIZED"
                    feedback_entries.append(row)

            with open(self.feedback_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(feedback_entries)

            logger.info(f"Anonymized data for customer {customer_id}")

        except Exception as e:
            logger.error(f"Error anonymizing customer data: {e}")