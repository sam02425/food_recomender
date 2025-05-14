"""
Entertainer Agent for creating fun, customized dish names.
"""

import os
import csv
import json
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("entertainer_agent")

class EntertainerAgent:
    """Agent for creating entertaining dish names."""

    def __init__(self, naming_data_path: str):
        """
        Initialize the entertainer agent.

        Args:
            naming_data_path: Path to dish naming data CSV
        """
        self.naming_data_path = naming_data_path
        self.naming_data = self._load_naming_data()

        # Default naming patterns
        self.default_patterns = {
            # Weather-based naming patterns
            "weather": {
                "sunny": ["Sunshine", "Solar", "Bright", "Daylight"],
                "rainy": ["Rainy Day", "Monsoon", "Downpour", "Drizzle"],
                "cloudy": ["Cloudy", "Overcast", "Gray Sky", "Misty"],
                "snowy": ["Snowy", "Frosty", "Winter", "Flurry"],
                "hot": ["Sizzling", "Spicy Heat", "Fiery", "Scorching"],
                "cold": ["Chilled", "Cool", "Frosty", "Arctic"]
            },

            # Mood-based naming patterns
            "mood": {
                "happy": ["Happy", "Joyful", "Cheerful", "Smiling"],
                "sad": ["Comfort", "Soulful", "Uplifting", "Warming"],
                "neutral": ["Classic", "Balanced", "Special", "Signature"],
                "tired": ["Energizing", "Revitalizing", "Refreshing", "Boost"],
                "stressed": ["Calming", "Zen", "Tranquil", "Relaxing"],
                "surprised": ["Surprising", "Adventurous", "Bold", "Unexpected"],
                "angry": ["Cooling", "Balanced", "Harmonious", "Soothing"]
            },

            # Protein-based adjectives
            "protein": {
                "Chicken": ["Tender", "Juicy", "Grilled", "Roasted"],
                "Egg": ["Golden", "Farm-Fresh", "Sunny", "Perfect"],
                "Paneer/Indian Cheese": ["Creamy", "Authentic", "Soft", "Melty"],
                "Soya": ["Plant-Powered", "Green", "Earth", "Protein-Packed"],
                "Potato": ["Fluffy", "Golden", "Hearty", "Comforting"],
                "Pepperoni": ["Savory", "Spiced", "Italian", "Zesty"]
            },

            # Base type formats
            "base_type": {
                "Bowl": ["Bowl", "Bowl of Joy", "Power Bowl", "Fusion Bowl"],
                "Wrap": ["Wrap", "Roll", "Fusion Wrap", "Hand-Rolled Wrap"],
                "Sandwich": ["Sandwich", "Fusion Sandwich", "Stacked Sandwich", "Delight Sandwich"],
                "Biryani": ["Biryani", "Royal Biryani", "Aromatic Biryani", "Flavorful Biryani"]
            }
        }

        logger.info("Entertainer agent initialized")

    def _load_naming_data(self) -> Dict[str, Any]:
        """
        Load dish naming data from CSV.

        Returns:
            Dish naming data
        """
        naming_data = {
            "weather_patterns": {},
            "mood_patterns": {},
            "protein_adjectives": {},
            "base_formats": {},
            "custom_names": []
        }

        # Create default naming data file if it doesn't exist
        if not os.path.exists(self.naming_data_path):
            self._initialize_naming_data()

        try:
            with open(self.naming_data_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    pattern_type = row.get("pattern_type")
                    context = row.get("context")
                    term = row.get("term")
                    score = int(row.get("score", 0))
                    custom_name = row.get("custom_name")

                    # Process weather patterns
                    if pattern_type == "weather" and context and term:
                        if context not in naming_data["weather_patterns"]:
                            naming_data["weather_patterns"][context] = []

                        naming_data["weather_patterns"][context].append({
                            "term": term,
                            "score": score
                        })

                    # Process mood patterns
                    elif pattern_type == "mood" and context and term:
                        if context not in naming_data["mood_patterns"]:
                            naming_data["mood_patterns"][context] = []

                        naming_data["mood_patterns"][context].append({
                            "term": term,
                            "score": score
                        })

                    # Process protein adjectives
                    elif pattern_type == "protein" and context and term:
                        if context not in naming_data["protein_adjectives"]:
                            naming_data["protein_adjectives"][context] = []

                        naming_data["protein_adjectives"][context].append({
                            "term": term,
                            "score": score
                        })

                    # Process base formats
                    elif pattern_type == "base_type" and context and term:
                        if context not in naming_data["base_formats"]:
                            naming_data["base_formats"][context] = []

                        naming_data["base_formats"][context].append({
                            "term": term,
                            "score": score
                        })

                    # Store custom names
                    elif pattern_type == "custom" and custom_name:
                        naming_data["custom_names"].append(custom_name)

            logger.info(f"Loaded naming data with {len(naming_data['weather_patterns'])} weather patterns, {len(naming_data['mood_patterns'])} mood patterns")
            return naming_data

        except Exception as e:
            logger.error(f"Error loading naming data: {e}")
            return {
                "weather_patterns": {},
                "mood_patterns": {},
                "protein_adjectives": {},
                "base_formats": {},
                "custom_names": []
            }

    def _initialize_naming_data(self) -> None:
        """Initialize naming data file with default values."""
        try:
            with open(self.naming_data_path, 'w', newline='') as file:
                fieldnames = ["pattern_type", "context", "term", "score", "custom_name"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                # Add default weather patterns
                for weather, terms in self.default_patterns["weather"].items():
                    for i, term in enumerate(terms):
                        writer.writerow({
                            "pattern_type": "weather",
                            "context": weather,
                            "term": term,
                            "score": 5 - i,
                            "custom_name": ""
                        })

                # Add default mood patterns
                for mood, terms in self.default_patterns["mood"].items():
                    for i, term in enumerate(terms):
                        writer.writerow({
                            "pattern_type": "mood",
                            "context": mood,
                            "term": term,
                            "score": 5 - i,
                            "custom_name": ""
                        })

                # Add default protein adjectives
                for protein, terms in self.default_patterns["protein"].items():
                    for i, term in enumerate(terms):
                        writer.writerow({
                            "pattern_type": "protein",
                            "context": protein,
                            "term": term,
                            "score": 5 - i,
                            "custom_name": ""
                        })

                # Add default base formats
                for base_type, terms in self.default_patterns["base_type"].items():
                    for i, term in enumerate(terms):
                        writer.writerow({
                            "pattern_type": "base_type",
                            "context": base_type,
                            "term": term,
                            "score": 5 - i,
                            "custom_name": ""
                        })

                # Add some sample custom names
                custom_names = [
                    "The Flavor Fiesta",
                    "Ultimate Fusion Delight",
                    "Protein Power-Up",
                    "Chef's Special Creation",
                    "Taste Explosion",
                    "Culinary Adventure",
                    "Spice Symphony",
                    "Perfect Harmony Bowl",
                    "Deluxe Comfort Meal",
                    "Gourmet Fusion Express"
                ]

                for name in custom_names:
                    writer.writerow({
                        "pattern_type": "custom",
                        "context": "",
                        "term": "",
                        "score": 0,
                        "custom_name": name
                    })

            logger.info(f"Initialized naming data file: {self.naming_data_path}")

        except Exception as e:
            logger.error(f"Error initializing naming data: {e}")

    def generate_dish_name(self, customer_name: str, protein: str, base_type: str,
                         weather: str, mood: str = "neutral") -> Dict[str, Any]:
        """
        Generate a fun dish name based on inputs.

        Args:
            customer_name: Customer name for personalization
            protein: Selected protein
            base_type: Selected base type
            weather: Current weather condition
            mood: Customer mood

        Returns:
            Generated dish name suggestions
        """
        result = {
            "name": "",
            "alternatives": [],
            "format_used": "",
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Normalize inputs
            if not customer_name:
                customer_name = "Guest"
            else:
                # Get first name only
                customer_name = customer_name.split()[0]

            # Normalize weather
            normalized_weather = weather.lower()
            if "sun" in normalized_weather:
                normalized_weather = "sunny"
            elif "rain" in normalized_weather or "storm" in normalized_weather:
                normalized_weather = "rainy"
            elif "cloud" in normalized_weather:
                normalized_weather = "cloudy"
            elif "snow" in normalized_weather:
                normalized_weather = "snowy"
            elif any(w in normalized_weather for w in ["hot", "warm", "heat"]):
                normalized_weather = "hot"
            elif any(w in normalized_weather for w in ["cold", "chill", "cool", "freeze"]):
                normalized_weather = "cold"
            else:
                normalized_weather = "sunny"  # Default

            # Get naming components
            weather_terms = self._get_terms("weather_patterns", normalized_weather)
            mood_terms = self._get_terms("mood_patterns", mood)
            protein_terms = self._get_terms("protein_adjectives", protein)
            base_terms = self._get_terms("base_formats", base_type)

            # Fallback to defaults if no terms found
            if not weather_terms and normalized_weather in self.default_patterns["weather"]:
                weather_terms = self.default_patterns["weather"][normalized_weather]

            if not mood_terms and mood in self.default_patterns["mood"]:
                mood_terms = self.default_patterns["mood"][mood]

            if not protein_terms and protein in self.default_patterns["protein"]:
                protein_terms = self.default_patterns["protein"][protein]

            if not base_terms and base_type in self.default_patterns["base_type"]:
                base_terms = self.default_patterns["base_type"][base_type]

            # Use defaults if still no terms
            weather_terms = weather_terms or ["Special"]
            mood_terms = mood_terms or ["Signature"]
            protein_terms = protein_terms or ["Delicious"]
            base_terms = base_terms or [base_type]

            # Generate name formats
            name_formats = [
                # Format 1: [Customer]'s [Weather] [Protein] [Base]
                lambda: f"{customer_name}'s {random.choice(weather_terms)} {protein} {random.choice(base_terms)}",

                # Format 2: [Customer]'s [Mood] [Protein] [Base]
                lambda: f"{customer_name}'s {random.choice(mood_terms)} {protein} {random.choice(base_terms)}",

                # Format 3: [Weather] [Protein] [Base] by [Customer]
                lambda: f"{random.choice(weather_terms)} {protein} {random.choice(base_terms)} by {customer_name}",

                # Format 4: [Protein Adj] [Protein] [Base] ([Weather/Mood])
                lambda: f"{random.choice(protein_terms)} {protein} {random.choice(base_terms)} ({random.choice(weather_terms + mood_terms)})",

                # Format 5: [Customer]'s [Protein Adj] [Base] Special
                lambda: f"{customer_name}'s {random.choice(protein_terms)} {random.choice(base_terms)} Special"
            ]

            # Select a random format and generate the name
            selected_format = random.randint(0, len(name_formats) - 1)
            primary_name = name_formats[selected_format]()

            # Generate alternative names
            alternatives = []
            for i in range(2):  # Generate 2 alternatives
                format_idx = random.randint(0, len(name_formats) - 1)
                while format_idx == selected_format:
                    format_idx = random.randint(0, len(name_formats) - 1)

                alternative = name_formats[format_idx]()
                alternatives.append(alternative)

            # Occasionally add a creative custom name
            if self.naming_data["custom_names"] and random.random() < 0.3:
                custom_base = random.choice(self.naming_data["custom_names"])
                custom_name = f"{customer_name}'s {custom_base} with {protein}"
                alternatives.append(custom_name)

            # Set result
            result["name"] = primary_name
            result["alternatives"] = alternatives
            result["format_used"] = f"Format {selected_format + 1}"

            logger.info(f"Generated dish name: {primary_name}")
            return result

        except Exception as e:
            logger.error(f"Error generating dish name: {e}")

            # Fallback to a simple name format
            fallback_name = f"{customer_name}'s {protein} {base_type}"
            result["name"] = fallback_name
            result["alternatives"] = [
                f"{protein} {base_type} Special",
                f"Signature {protein} {base_type}"
            ]
            result["format_used"] = "Fallback Format"

            return result

    def _get_terms(self, category: str, context: str) -> List[str]:
        """
        Get naming terms from a category and context.

        Args:
            category: Term category
            context: Context for terms

        Returns:
            List of terms
        """
        terms = []

        # Get terms with scores
        term_data = []
        if context in self.naming_data.get(category, {}):
            term_data = self.naming_data[category][context]

        # Sort by score and extract terms
        if term_data:
            sorted_terms = sorted(term_data, key=lambda x: x["score"], reverse=True)
            terms = [t["term"] for t in sorted_terms]

        return terms

    def add_custom_name(self, name: str) -> bool:
        """
        Add a custom dish name to the database.

        Args:
            name: Custom dish name

        Returns:
            Success status
        """
        try:
            # Load current data
            current_data = []
            with open(self.naming_data_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                current_data = list(reader)

            # Add new custom name
            new_row = {
                "pattern_type": "custom",
                "context": "",
                "term": "",
                "score": 0,
                "custom_name": name
            }
            current_data.append(new_row)

            # Write updated data back to CSV
            with open(self.naming_data_path, 'w', newline='') as file:
                fieldnames = ["pattern_type", "context", "term", "score", "custom_name"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(current_data)

            # Update in-memory data
            self.naming_data["custom_names"].append(name)

            logger.info(f"Added custom dish name: {name}")
            return True

        except Exception as e:
            logger.error(f"Error adding custom dish name: {e}")
            return False

    def update_term_score(self, pattern_type: str, context: str, term: str,
                        score_change: int) -> bool:
        """
        Update the score for a naming term.

        Args:
            pattern_type: Pattern type (weather, mood, protein, base_type)
            context: Context for the term
            term: The term to update
            score_change: Amount to change the score by

        Returns:
            Success status
        """
        try:
            # Load current data
            current_data = []
            with open(self.naming_data_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                current_data = list(reader)

            # Find and update the matching row
            term_found = False
            for row in current_data:
                if (row["pattern_type"] == pattern_type and
                    row["context"] == context and
                    row["term"] == term):

                    # Update score
                    current_score = int(row["score"])
                    new_score = max(1, min(5, current_score + score_change))  # Keep between 1-5
                    row["score"] = str(new_score)
                    term_found = True
                    break

            # If term not found, add it with a default score
            if not term_found and term:
                default_score = 3  # Middle score
                new_score = max(1, min(5, default_score + score_change))

                new_row = {
                    "pattern_type": pattern_type,
                    "context": context,
                    "term": term,
                    "score": str(new_score),
                    "custom_name": ""
                }
                current_data.append(new_row)

            # Write updated data back to CSV
            with open(self.naming_data_path, 'w', newline='') as file:
                fieldnames = ["pattern_type", "context", "term", "score", "custom_name"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(current_data)

            # Reload naming data
            self.naming_data = self._load_naming_data()

            logger.info(f"Updated term score for {pattern_type} - {context} - {term}")
            return True

        except Exception as e:
            logger.error(f"Error updating term score: {e}")
            return False

    def process_feedback(self, name_suggestion: str, feedback_type: str,
                       custom_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process feedback on a name suggestion.

        Args:
            name_suggestion: Suggested dish name
            feedback_type: Feedback type (accept, ignore, custom)
            custom_name: Custom name if provided

        Returns:
            Processed feedback result
        """
        result = {
            "name_suggestion": name_suggestion,
            "feedback_type": feedback_type,
            "processed": False,
            "message": ""
        }

        try:
            # Process based on feedback type
            if feedback_type == "accept":
                # Parse the name to determine the patterns used
                # This is a simplified approach; in a real system,
                # you'd want to track which format was used and adjust accordingly

                # For demo purposes, we'll just increase scores for any recognizable terms in the name
                words = name_suggestion.replace("'s", "").split()

                # Check for weather terms
                for weather, term_list in self.default_patterns["weather"].items():
                    for term in term_list:
                        if term in words:
                            self.update_term_score("weather", weather, term, 1)

                # Check for mood terms
                for mood, term_list in self.default_patterns["mood"].items():
                    for term in term_list:
                        if term in words:
                            self.update_term_score("mood", mood, term, 1)

                # Check for protein adjectives
                for protein, term_list in self.default_patterns["protein"].items():
                    for term in term_list:
                        if term in words:
                            self.update_term_score("protein", protein, term, 1)

                # Check for base formats
                for base_type, term_list in self.default_patterns["base_type"].items():
                    for term in term_list:
                        if term in words:
                            self.update_term_score("base_type", base_type, term, 1)

                result["processed"] = True
                result["message"] = "Name suggestion accepted and pattern scores updated"

            elif feedback_type == "custom" and custom_name:
                # Add the custom name to the database
                self.add_custom_name(custom_name)

                result["processed"] = True
                result["message"] = f"Custom name '{custom_name}' added to database"

            elif feedback_type == "ignore":
                # No changes needed for ignore
                result["processed"] = True
                result["message"] = "Name suggestion ignored"

            return result

        except Exception as e:
            logger.error(f"Error processing name suggestion feedback: {e}")
            result["processed"] = False
            result["message"] = f"Error processing feedback: {str(e)}"
            return result