"""
Note Taker Agent for handling customer order selections.
"""

import os
import csv
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("note_taker_agent")

class NoteTakerAgent:
    """Agent for taking customer order selections."""

    def __init__(self, menu_data_path: str):
        """
        Initialize the note taker agent.

        Args:
            menu_data_path: Path to menu items CSV
        """
        self.menu_data_path = menu_data_path
        self.menu = self._load_menu_data()
        self.current_selections = {
            "protein": None,
            "sauce": None,
            "base_type": None,
            "base_option": None,
            "veggies": [],
            "dish_name": None
        }

        logger.info("Note taker agent initialized")

    def _load_menu_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load menu data from CSV file.

        Returns:
            Menu data categorized by item type
        """
        menu = {
            "proteins": [],
            "sauces": [],
            "bases": {},
            "veggies": []
        }

        if not os.path.exists(self.menu_data_path):
            logger.warning(f"Menu data file not found: {self.menu_data_path}")
            return menu

        try:
            with open(self.menu_data_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    category = row.get("category", "")
                    item_name = row.get("item", "")
                    price = float(row.get("price", 0))
                    description = row.get("description", "")

                    # Parse attributes
                    attributes = {}
                    if row.get("attributes"):
                        try:
                            attributes = json.loads(row.get("attributes"))
                        except:
                            pass

                    item_data = {
                        "name": item_name,
                        "price": price,
                        "description": description,
                        "attributes": attributes
                    }

                    if category == "proteins":
                        menu["proteins"].append(item_data)
                    elif category == "sauces":
                        menu["sauces"].append(item_data)
                    elif category == "bases":
                        # Group bases by their type
                        base_type = attributes.get("base_type", "Other")
                        if base_type not in menu["bases"]:
                            menu["bases"][base_type] = []
                        menu["bases"][base_type].append(item_data)
                    elif category == "veggies":
                        menu["veggies"].append(item_data)

            logger.info(f"Loaded menu data with {len(menu['proteins'])} proteins, {len(menu['sauces'])} sauces, {len(menu['bases'])} base types, {len(menu['veggies'])} veggies")
            return menu

        except Exception as e:
            logger.error(f"Error loading menu data: {e}")
            return menu

    def get_menu_options(self, category: str) -> List[Dict[str, Any]]:
        """
        Get menu options for a category.

        Args:
            category: Menu category (proteins, sauces, bases, veggies)

        Returns:
            List of menu items for the category
        """
        if category == "bases":
            # Return all base types and options
            base_options = []
            for base_type, items in self.menu["bases"].items():
                for item in items:
                    base_options.append({
                        "base_type": base_type,
                        "base_option": item["name"],
                        "price": item["price"],
                        "description": item["description"]
                    })
            return base_options

        return self.menu.get(category, [])

    def get_base_options(self, base_type: str) -> List[Dict[str, Any]]:
        """
        Get base options for a specific base type.

        Args:
            base_type: Base type (Biryani, Sandwich, Wrap, Bowl)

        Returns:
            List of base options for the type
        """
        return self.menu["bases"].get(base_type, [])

    def select_protein(self, protein: str) -> Dict[str, Any]:
        """
        Select a protein for the order.

        Args:
            protein: Selected protein name

        Returns:
            Updated selections
        """
        # Find protein in menu
        protein_data = None
        for item in self.menu["proteins"]:
            if item["name"] == protein:
                protein_data = item
                break

        if not protein_data:
            logger.warning(f"Protein not found in menu: {protein}")
            return self.current_selections

        # Update selections
        self.current_selections["protein"] = protein

        logger.info(f"Selected protein: {protein}")
        return self.current_selections

    def select_sauce(self, sauce: str) -> Dict[str, Any]:
        """
        Select a sauce for the order.

        Args:
            sauce: Selected sauce name

        Returns:
            Updated selections
        """
        # Find sauce in menu
        sauce_data = None
        for item in self.menu["sauces"]:
            if item["name"] == sauce:
                sauce_data = item
                break

        if not sauce_data:
            logger.warning(f"Sauce not found in menu: {sauce}")
            return self.current_selections

        # Update selections
        self.current_selections["sauce"] = sauce

        logger.info(f"Selected sauce: {sauce}")
        return self.current_selections

    def select_base(self, base_type: str, base_option: str) -> Dict[str, Any]:
        """
        Select a base for the order.

        Args:
            base_type: Selected base type
            base_option: Selected base option

        Returns:
            Updated selections
        """
        # Find base in menu
        base_options = self.menu["bases"].get(base_type, [])
        base_data = None
        for item in base_options:
            if item["name"] == base_option:
                base_data = item
                break

        if not base_data:
            logger.warning(f"Base option not found in menu: {base_type} - {base_option}")
            return self.current_selections

        # Update selections
        self.current_selections["base_type"] = base_type
        self.current_selections["base_option"] = base_option

        logger.info(f"Selected base: {base_type} - {base_option}")
        return self.current_selections

    def select_veggies(self, veggies: List[str]) -> Dict[str, Any]:
        """
        Select veggies for the order.

        Args:
            veggies: List of selected veggies

        Returns:
            Updated selections
        """
        # Validate veggies
        valid_veggies = []
        for veggie in veggies:
            veggie_found = False
            for item in self.menu["veggies"]:
                if item["name"] == veggie:
                    veggie_found = True
                    valid_veggies.append(veggie)
                    break

            if not veggie_found:
                logger.warning(f"Veggie not found in menu: {veggie}")

        # Update selections
        self.current_selections["veggies"] = valid_veggies

        logger.info(f"Selected veggies: {valid_veggies}")
        return self.current_selections

    def set_dish_name(self, dish_name: str) -> Dict[str, Any]:
        """
        Set a custom dish name.

        Args:
            dish_name: Custom dish name

        Returns:
            Updated selections
        """
        self.current_selections["dish_name"] = dish_name

        logger.info(f"Set custom dish name: {dish_name}")
        return self.current_selections

    def get_order_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current order selections.

        Returns:
            Order summary
        """
        # Calculate price
        total_price = 0.0

        # Add protein price
        if self.current_selections["protein"]:
            for item in self.menu["proteins"]:
                if item["name"] == self.current_selections["protein"]:
                    total_price += item["price"]
                    break

        # Add sauce price
        if self.current_selections["sauce"]:
            for item in self.menu["sauces"]:
                if item["name"] == self.current_selections["sauce"]:
                    total_price += item["price"]
                    break

        # Add base price
        if self.current_selections["base_type"] and self.current_selections["base_option"]:
            base_options = self.menu["bases"].get(self.current_selections["base_type"], [])
            for item in base_options:
                if item["name"] == self.current_selections["base_option"]:
                    total_price += item["price"]
                    break

        # Add veggie prices
        veggies = self.current_selections["veggies"]
        veggie_count = len(veggies)
        extra_veggie_count = max(0, veggie_count - 5)  # First 5 veggies free

        # Add price for each veggie
        for veggie in veggies:
            # Check if premium veggie (like avocado)
            for item in self.menu["veggies"]:
                if item["name"] == veggie:
                    if item["price"] > 1.0:  # Premium veggie
                        total_price += item["price"]
                    elif veggies.index(veggie) >= 5:  # Extra regular veggie
                        total_price += 1.0  # $1 for each extra regular veggie
                    break

        # Build summary
        protein_details = {"name": self.current_selections["protein"]}
        for item in self.menu["proteins"]:
            if item["name"] == self.current_selections["protein"]:
                protein_details["price"] = item["price"]
                protein_details["description"] = item["description"]
                break

        sauce_details = {"name": self.current_selections["sauce"]}
        for item in self.menu["sauces"]:
            if item["name"] == self.current_selections["sauce"]:
                sauce_details["price"] = item["price"]
                sauce_details["description"] = item["description"]
                break

        base_details = {
            "type": self.current_selections["base_type"],
            "option": self.current_selections["base_option"]
        }
        base_options = self.menu["bases"].get(self.current_selections["base_type"], [])
        for item in base_options:
            if item["name"] == self.current_selections["base_option"]:
                base_details["price"] = item["price"]
                base_details["description"] = item["description"]
                break

        veggie_details = []
        for veggie in self.current_selections["veggies"]:
            for item in self.menu["veggies"]:
                if item["name"] == veggie:
                    veggie_details.append({
                        "name": veggie,
                        "price": item["price"],
                        "description": item["description"],
                        "premium": item["price"] > 1.0
                    })
                    break

        return {
            "protein": protein_details,
            "sauce": sauce_details,
            "base": base_details,
            "veggies": veggie_details,
            "dish_name": self.current_selections["dish_name"],
            "total_price": total_price,
            "extra_veggie_count": extra_veggie_count,
            "timestamp": datetime.now().isoformat()
        }

    def reset_selections(self) -> Dict[str, Any]:
        """
        Reset the current selections.

        Returns:
            Empty selections
        """
        self.current_selections = {
            "protein": None,
            "sauce": None,
            "base_type": None,
            "base_option": None,
            "veggies": [],
            "dish_name": None
        }

        logger.info("Reset order selections")
        return self.current_selections

    def get_current_selections(self) -> Dict[str, Any]:
        """
        Get the current selections.

        Returns:
            Current selections
        """
        return self.current_selections

    def validate_selections(self) -> Dict[str, Any]:
        """
        Validate the current selections.

        Returns:
            Validation result
        """
        missing = []

        if not self.current_selections["protein"]:
            missing.append("protein")

        if not self.current_selections["sauce"]:
            missing.append("sauce")

        if not self.current_selections["base_type"] or not self.current_selections["base_option"]:
            missing.append("base")

        if not self.current_selections["veggies"]:
            missing.append("veggies")

        if missing:
            return {
                "valid": False,
                "missing": missing,
                "message": f"Please select: {', '.join(missing)}"
            }

        return {
            "valid": True,
            "message": "All selections complete"
        }

    def get_allergens(self) -> Dict[str, List[str]]:
        """
        Get allergens for current selections.

        Returns:
            Dictionary of allergens by selection type
        """
        allergens = {
            "protein": [],
            "sauce": [],
            "base": [],
            "veggies": []
        }

        # Protein allergens
        if self.current_selections["protein"]:
            for item in self.menu["proteins"]:
                if item["name"] == self.current_selections["protein"]:
                    allergens["protein"] = item["attributes"].get("allergens", [])
                    break

        # Sauce allergens
        if self.current_selections["sauce"]:
            for item in self.menu["sauces"]:
                if item["name"] == self.current_selections["sauce"]:
                    allergens["sauce"] = item["attributes"].get("allergens", [])
                    break

        # Base allergens
        if self.current_selections["base_type"] and self.current_selections["base_option"]:
            base_options = self.menu["bases"].get(self.current_selections["base_type"], [])
            for item in base_options:
                if item["name"] == self.current_selections["base_option"]:
                    allergens["base"] = item["attributes"].get("allergens", [])
                    break

        # Veggie allergens
        veggie_allergens = []
        for veggie in self.current_selections["veggies"]:
            for item in self.menu["veggies"]:
                if item["name"] == veggie:
                    veggie_allergens.extend(item["attributes"].get("allergens", []))
                    break
        allergens["veggies"] = list(set(veggie_allergens))  # Remove duplicates

        return allergens

    def get_health_attributes(self) -> Dict[str, Any]:
        """
        Get health attributes for current selections.

        Returns:
            Health-related attributes
        """
        health_info = {
            "spice_level": 0,
            "health_index": 0,
            "nutritional_highlights": []
        }

        # Protein spice level and nutrition
        if self.current_selections["protein"]:
            for item in self.menu["proteins"]:
                if item["name"] == self.current_selections["protein"]:
                    health_info["spice_level"] += item["attributes"].get("spice_level", 0)
                    if item["name"] == "Chicken":
                        health_info["nutritional_highlights"].append("High-quality protein")
                    elif item["name"] == "Egg":
                        health_info["nutritional_highlights"].append("Complete protein with essential amino acids")
                    elif item["name"] == "Paneer/Indian Cheese":
                        health_info["nutritional_highlights"].append("Good source of calcium")
                    elif item["name"] == "Soya":
                        health_info["nutritional_highlights"].append("Plant-based protein")
                    break

        # Sauce spice level
        if self.current_selections["sauce"]:
            for item in self.menu["sauces"]:
                if item["name"] == self.current_selections["sauce"]:
                    health_info["spice_level"] += item["attributes"].get("spice_level", 0)
                    if "Spicy" in item["name"]:
                        health_info["nutritional_highlights"].append("Metabolism-boosting spices")
                    if item["name"] == "Yogurt/Raita":
                        health_info["nutritional_highlights"].append("Probiotics for gut health")
                    break

        # Average the spice level
        health_info["spice_level"] = min(5, max(1, round(health_info["spice_level"] / 2)))

        # Veggie health index
        total_health_index = 0
        veggie_count = len(self.current_selections["veggies"])

        for veggie in self.current_selections["veggies"]:
            for item in self.menu["veggies"]:
                if item["name"] == veggie:
                    total_health_index += item["attributes"].get("health_index", 3)

                    # Add nutritional highlights for key veggies
                    if veggie == "Spinach":
                        health_info["nutritional_highlights"].append("Iron-rich leafy green")
                    elif veggie == "Avocado":
                        health_info["nutritional_highlights"].append("Healthy fats")
                    elif veggie == "Bell Pepper":
                        health_info["nutritional_highlights"].append("Vitamin C source")
                    break

        # Calculate average health index
        if veggie_count > 0:
            health_info["health_index"] = round(total_health_index / veggie_count)

        return health_info