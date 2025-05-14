"""
Weather Recommender Agent for weather-based food recommendations.
"""

import os
import csv
import json
import logging
import random
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("weather_recommender_agent")

class WeatherRecommenderAgent:
    """Agent for making weather-based food recommendations."""

    def __init__(self, weather_data_path: str):
        """
        Initialize the weather recommender agent.

        Args:
            weather_data_path: Path to weather recommendations CSV
        """
        self.weather_data_path = weather_data_path
        self.weather_data = self._load_weather_data()

        # Default weather-based recommendations
        self.default_recommendations = {
            "rainy": {
                "proteins": ["Chicken", "Paneer/Indian Cheese"],
                "sauces": ["Curry Special", "Malai Masala"],
                "base_types": ["Bowl", "Biryani"],
                "reasoning": "Warm, comforting options perfect for rainy weather."
            },
            "cold": {
                "proteins": ["Chicken", "Paneer/Indian Cheese"],
                "sauces": ["Curry Masala", "Red Spicy Sauce"],
                "base_types": ["Bowl", "Biryani"],
                "reasoning": "Warming, spicier options to help maintain body temperature in cold weather."
            },
            "hot": {
                "proteins": ["Chicken", "Paneer/Indian Cheese", "Potato"],
                "sauces": ["Yogurt/Raita", "Mint Sauce"],
                "base_types": ["Bowl", "Wrap"],
                "reasoning": "Cooling options with refreshing flavors for hot weather."
            },
            "sunny": {
                "proteins": ["Chicken", "Egg", "Soya"],
                "sauces": ["Mint Sauce", "Curry Special"],
                "base_types": ["Wrap", "Sandwich"],
                "reasoning": "Fresh, balanced options to enjoy in sunny weather."
            },
            "cloudy": {
                "proteins": ["Chicken", "Egg", "Paneer/Indian Cheese"],
                "sauces": ["Curry Special", "Malai Masala"],
                "base_types": ["Bowl", "Sandwich"],
                "reasoning": "Comforting yet not too heavy, perfect for cloudy weather."
            }
        }

        # Time of day recommendations
        self.time_recommendations = {
            "morning": {
                "proteins": ["Egg", "Paneer/Indian Cheese"],
                "sauces": ["Mint Sauce", "Yogurt/Raita"],
                "base_types": ["Wrap", "Sandwich"],
                "reasoning": "Lighter options with protein for a great start to your day."
            },
            "afternoon": {
                "proteins": ["Chicken", "Paneer/Indian Cheese", "Soya"],
                "sauces": ["Curry Special", "Malai Masala"],
                "base_types": ["Bowl", "Biryani"],
                "reasoning": "Balanced, substantial meal to fuel your afternoon."
            },
            "evening": {
                "proteins": ["Chicken", "Paneer/Indian Cheese", "Potato"],
                "sauces": ["Curry Masala", "Malai Masala"],
                "base_types": ["Bowl", "Wrap"],
                "reasoning": "Flavorful, comforting options for your evening meal."
            }
        }

        logger.info("Weather recommender agent initialized")

    def _load_weather_data(self) -> Dict[str, Any]:
        """
        Load weather recommendation data from CSV.

        Returns:
            Weather recommendation data
        """
        weather_data = {
            "condition_recommendations": {},
            "time_recommendations": {}
        }

        # Create default weather data file if it doesn't exist
        if not os.path.exists(self.weather_data_path):
            self._initialize_weather_data()

        try:
            with open(self.weather_data_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    condition = row.get("condition")
                    time_of_day = row.get("time_of_day")
                    category = row.get("category")
                    item = row.get("item")
                    score = int(row.get("score", 0))
                    reasoning = row.get("reasoning", "")

                    # Process condition recommendations
                    if condition and category and item:
                        if condition not in weather_data["condition_recommendations"]:
                            weather_data["condition_recommendations"][condition] = {}

                        if category not in weather_data["condition_recommendations"][condition]:
                            weather_data["condition_recommendations"][condition][category] = []

                        weather_data["condition_recommendations"][condition][category].append({
                            "item": item,
                            "score": score,
                            "reasoning": reasoning
                        })

                    # Process time of day recommendations
                    if time_of_day and category and item:
                        if time_of_day not in weather_data["time_recommendations"]:
                            weather_data["time_recommendations"][time_of_day] = {}

                        if category not in weather_data["time_recommendations"][time_of_day]:
                            weather_data["time_recommendations"][time_of_day][category] = []

                        weather_data["time_recommendations"][time_of_day][category].append({
                            "item": item,
                            "score": score,
                            "reasoning": reasoning
                        })

            logger.info(f"Loaded weather data with {len(weather_data['condition_recommendations'])} conditions and {len(weather_data['time_recommendations'])} time periods")
            return weather_data

        except Exception as e:
            logger.error(f"Error loading weather data: {e}")
            return {"condition_recommendations": {}, "time_recommendations": {}}

    def _initialize_weather_data(self) -> None:
        """Initialize weather data file with default values."""
        try:
            with open(self.weather_data_path, 'w', newline='') as file:
                fieldnames = ["condition", "time_of_day", "category", "item", "score", "reasoning"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                # Add default weather condition recommendations
                for condition, recommendations in self.default_recommendations.items():
                    # Proteins
                    for i, protein in enumerate(recommendations["proteins"]):
                        writer.writerow({
                            "condition": condition,
                            "time_of_day": "",
                            "category": "proteins",
                            "item": protein,
                            "score": 5 - i,  # Higher score for first items
                            "reasoning": recommendations["reasoning"]
                        })

                    # Sauces
                    for i, sauce in enumerate(recommendations["sauces"]):
                        writer.writerow({
                            "condition": condition,
                            "time_of_day": "",
                            "category": "sauces",
                            "item": sauce,
                            "score": 5 - i,
                            "reasoning": recommendations["reasoning"]
                        })

                    # Base types
                    for i, base_type in enumerate(recommendations["base_types"]):
                        writer.writerow({
                            "condition": condition,
                            "time_of_day": "",
                            "category": "base_types",
                            "item": base_type,
                            "score": 5 - i,
                            "reasoning": recommendations["reasoning"]
                        })

                # Add default time of day recommendations
                for time_of_day, recommendations in self.time_recommendations.items():
                    # Proteins
                    for i, protein in enumerate(recommendations["proteins"]):
                        writer.writerow({
                            "condition": "",
                            "time_of_day": time_of_day,
                            "category": "proteins",
                            "item": protein,
                            "score": 5 - i,
                            "reasoning": recommendations["reasoning"]
                        })

                    # Sauces
                    for i, sauce in enumerate(recommendations["sauces"]):
                        writer.writerow({
                            "condition": "",
                            "time_of_day": time_of_day,
                            "category": "sauces",
                            "item": sauce,
                            "score": 5 - i,
                            "reasoning": recommendations["reasoning"]
                        })

                    # Base types
                    for i, base_type in enumerate(recommendations["base_types"]):
                        writer.writerow({
                            "condition": "",
                            "time_of_day": time_of_day,
                            "category": "base_types",
                            "item": base_type,
                            "score": 5 - i,
                            "reasoning": recommendations["reasoning"]
                        })

            logger.info(f"Initialized weather data file: {self.weather_data_path}")

        except Exception as e:
            logger.error(f"Error initializing weather data: {e}")

    def get_current_weather(self, lat: float = 40.7128, lon: float = -74.0060) -> Dict[str, Any]:
        """
        Get current weather data for a location.

        For demo purposes, this uses a simplified API call and provides
        fallback random weather if API is unavailable.

        Args:
            lat: Latitude (default: New York City)
            lon: Longitude (default: New York City)

        Returns:
            Weather data
        """
        try:
            # Try to get weather data from a free API
            # Note: In a production system, you'd use a proper weather API with an API key
            api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature,rain,snowfall,cloud_cover,wind_speed"

            response = requests.get(api_url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})

                # Check if current data is available
                if current and "temperature" in current:
                    temperature = current.get("temperature")
                    rain = current.get("rain", 0)
                    snowfall = current.get("snowfall", 0)
                    cloud_cover = current.get("cloud_cover", 0)
                    wind_speed = current.get("wind_speed", 0)

                    # Determine weather condition
                    condition = self._determine_condition(temperature, rain, snowfall, cloud_cover, wind_speed)

                    logger.info(f"Retrieved current weather: {condition}, {temperature}°C")

                    return {
                        "temperature": temperature,
                        "condition": condition,
                        "rain": rain,
                        "snowfall": snowfall,
                        "cloud_cover": cloud_cover,
                        "wind_speed": wind_speed,
                        "timestamp": datetime.now().isoformat(),
                        "source": "api"
                    }

            # Fallback to random weather if API call fails
            return self._get_random_weather()

        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            return self._get_random_weather()

    def _get_random_weather(self) -> Dict[str, Any]:
        """
        Generate random weather data for demo purposes.

        Returns:
            Random weather data
        """
        # Generate random temperature between -5°C and 35°C
        temperature = round(random.uniform(-5, 35), 1)

        # Random values for other parameters
        rain = random.uniform(0, 5) if temperature > 0 else 0
        snowfall = random.uniform(0, 5) if temperature < 2 else 0
        cloud_cover = random.uniform(0, 100)
        wind_speed = random.uniform(0, 30)

        # Determine condition
        condition = self._determine_condition(temperature, rain, snowfall, cloud_cover, wind_speed)

        logger.info(f"Generated random weather: {condition}, {temperature}°C")

        return {
            "temperature": temperature,
            "condition": condition,
            "rain": rain,
            "snowfall": snowfall,
            "cloud_cover": cloud_cover,
            "wind_speed": wind_speed,
            "timestamp": datetime.now().isoformat(),
            "source": "random"
        }

    def _determine_condition(self, temperature: float, rain: float, snowfall: float,
                           cloud_cover: float, wind_speed: float) -> str:
        """
        Determine weather condition from parameters.

        Args:
            temperature: Temperature in °C
            rain: Rain in mm
            snowfall: Snowfall in cm
            cloud_cover: Cloud cover percentage
            wind_speed: Wind speed in km/h

        Returns:
            Weather condition
        """
        if snowfall > 0:
            return "snowy"
        elif rain > 0:
            return "rainy"
        elif cloud_cover > 80:
            return "cloudy"
        elif cloud_cover > 30:
            return "partly_cloudy"
        else:
            if temperature > 25:
                return "hot"
            elif temperature < 5:
                return "cold"
            else:
                return "sunny"

    def get_recommendations(self, weather_data: Dict[str, Any], time_of_day: str,
                          customer_id: Optional[str] = None,
                          mood: str = "neutral") -> Dict[str, Any]:
        """
        Get weather-based food recommendations.

        Args:
            weather_data: Current weather data
            time_of_day: Time of day (morning, afternoon, evening)
            customer_id: Optional customer ID for personalization
            mood: Customer's current mood

        Returns:
            Weather-based recommendations
        """
        # Extract condition from weather data
        condition = weather_data.get("condition", "sunny")
        temperature = weather_data.get("temperature", 20)

        # Normalize time of day
        if time_of_day.lower() in ["morning", "breakfast", "am"]:
            time_of_day = "morning"
        elif time_of_day.lower() in ["afternoon", "lunch", "noon", "midday"]:
            time_of_day = "afternoon"
        elif time_of_day.lower() in ["evening", "night", "dinner", "pm"]:
            time_of_day = "evening"
        else:
            # Default to afternoon
            time_of_day = "afternoon"

        # Get recommendations from loaded data
        weather_recs = {}
        time_recs = {}

        # Get weather condition recommendations
        if condition in self.weather_data["condition_recommendations"]:
            condition_data = self.weather_data["condition_recommendations"][condition]

            # Get top proteins
            if "proteins" in condition_data:
                proteins = sorted(condition_data["proteins"], key=lambda x: x["score"], reverse=True)
                weather_recs["proteins"] = [p["item"] for p in proteins[:3]]

            # Get top sauces
            if "sauces" in condition_data:
                sauces = sorted(condition_data["sauces"], key=lambda x: x["score"], reverse=True)
                weather_recs["sauces"] = [s["item"] for s in sauces[:3]]

            # Get top base types
            if "base_types" in condition_data:
                base_types = sorted(condition_data["base_types"], key=lambda x: x["score"], reverse=True)
                weather_recs["base_types"] = [b["item"] for b in base_types[:3]]

            # Get reasoning
            if "proteins" in condition_data and condition_data["proteins"]:
                weather_recs["reasoning"] = condition_data["proteins"][0]["reasoning"]

        # Get time of day recommendations
        if time_of_day in self.weather_data["time_recommendations"]:
            time_data = self.weather_data["time_recommendations"][time_of_day]

            # Get top proteins
            if "proteins" in time_data:
                proteins = sorted(time_data["proteins"], key=lambda x: x["score"], reverse=True)
                time_recs["proteins"] = [p["item"] for p in proteins[:3]]

            # Get top sauces
            if "sauces" in time_data:
                sauces = sorted(time_data["sauces"], key=lambda x: x["score"], reverse=True)
                time_recs["sauces"] = [s["item"] for s in sauces[:3]]

            # Get top base types
            if "base_types" in time_data:
                base_types = sorted(time_data["base_types"], key=lambda x: x["score"], reverse=True)
                time_recs["base_types"] = [b["item"] for b in base_types[:3]]

            # Get reasoning
            if "proteins" in time_data and time_data["proteins"]:
                time_recs["reasoning"] = time_data["proteins"][0]["reasoning"]

        # Use defaults if no recommendations found
        if not weather_recs and condition in self.default_recommendations:
            weather_recs = self.default_recommendations[condition]
        elif not weather_recs:
            # Fallback to "sunny" if condition not found
            weather_recs = self.default_recommendations["sunny"]

        if not time_recs and time_of_day in self.time_recommendations:
            time_recs = self.time_recommendations[time_of_day]
        elif not time_recs:
            # Fallback to "afternoon" if time of day not found
            time_recs = self.time_recommendations["afternoon"]

        # Combine weather and time recommendations (60% weather, 40% time)
        combined_recs = {}

        # Choose the best protein from each source
        if "proteins" in weather_recs and "proteins" in time_recs:
            combined_recs["proteins"] = [
                weather_recs["proteins"][0],  # Top weather protein
                time_recs["proteins"][0]  # Top time protein
            ]
            # Add additional unique proteins
            for protein in weather_recs["proteins"][1:] + time_recs["proteins"][1:]:
                if protein not in combined_recs["proteins"]:
                    combined_recs["proteins"].append(protein)
                    if len(combined_recs["proteins"]) >= 3:
                        break
        elif "proteins" in weather_recs:
            combined_recs["proteins"] = weather_recs["proteins"][:3]
        elif "proteins" in time_recs:
            combined_recs["proteins"] = time_recs["proteins"][:3]

        # Similarly for sauces and base types
        if "sauces" in weather_recs and "sauces" in time_recs:
            combined_recs["sauces"] = [
                weather_recs["sauces"][0],
                time_recs["sauces"][0]
            ]
            for sauce in weather_recs["sauces"][1:] + time_recs["sauces"][1:]:
                if sauce not in combined_recs["sauces"]:
                    combined_recs["sauces"].append(sauce)
                    if len(combined_recs["sauces"]) >= 3:
                        break
        elif "sauces" in weather_recs:
            combined_recs["sauces"] = weather_recs["sauces"][:3]
        elif "sauces" in time_recs:
            combined_recs["sauces"] = time_recs["sauces"][:3]

        if "base_types" in weather_recs and "base_types" in time_recs:
            combined_recs["base_types"] = [
                weather_recs["base_types"][0],
                time_recs["base_types"][0]
            ]
            for base in weather_recs["base_types"][1:] + time_recs["base_types"][1:]:
                if base not in combined_recs["base_types"]:
                    combined_recs["base_types"].append(base)
                    if len(combined_recs["base_types"]) >= 3:
                        break
        elif "base_types" in weather_recs:
            combined_recs["base_types"] = weather_recs["base_types"][:3]
        elif "base_types" in time_recs:
            combined_recs["base_types"] = time_recs["base_types"][:3]

        # Combine reasoning
        weather_reason = weather_recs.get("reasoning", "")
        time_reason = time_recs.get("reasoning", "")

        if weather_reason and time_reason:
            combined_recs["reasoning"] = f"{weather_reason} {time_reason}"
        elif weather_reason:
            combined_recs["reasoning"] = weather_reason
        elif time_reason:
            combined_recs["reasoning"] = time_reason

        # Add weather and time information
        combined_recs["weather_condition"] = condition
        combined_recs["temperature"] = temperature
        combined_recs["time_of_day"] = time_of_day

        # Get top suggestion for base
        if "base_types" in combined_recs and combined_recs["base_types"]:
            combined_recs["suggested_base"] = combined_recs["base_types"][0]
        else:
            combined_recs["suggested_base"] = "Bowl"  # Default option

        # Add timestamp
        combined_recs["timestamp"] = datetime.now().isoformat()

        # Adjust based on mood if applicable
        combined_recs = self._adjust_for_mood(combined_recs, mood)

        logger.info(f"Generated weather recommendations for {condition}, {temperature}°C, {time_of_day}")
        return combined_recs

    def _adjust_for_mood(self, recommendations: Dict[str, Any], mood: str) -> Dict[str, Any]:
        """
        Adjust recommendations based on mood.

        Args:
            recommendations: Base recommendations
            mood: Customer mood

        Returns:
            Mood-adjusted recommendations
        """
        # Only adjust for certain moods
        if mood not in ["sad", "stressed", "tired", "angry"]:
            return recommendations

        adjusted_recs = recommendations.copy()

        # Add mood-specific reasoning
        if mood == "sad":
            mood_text = "For your current mood, we've recommended comforting options that may help boost your spirits."
        elif mood == "stressed":
            mood_text = "For your current mood, we've included calming options that may help reduce stress."
        elif mood == "tired":
            mood_text = "For your current mood, we've suggested energizing options that may help combat fatigue."
        elif mood == "angry":
            mood_text = "For your current mood, we've recommended balanced options with cooling ingredients."

        if "reasoning" in adjusted_recs:
            adjusted_recs["reasoning"] = f"{adjusted_recs['reasoning']} {mood_text}"
        else:
            adjusted_recs["reasoning"] = mood_text

        # For sad or stressed moods, suggest a bowl base type for comfort
        if mood in ["sad", "stressed"]:
            adjusted_recs["suggested_base"] = "Bowl"
        # For tired moods, suggest a more substantial option
        elif mood == "tired":
            if "hot" in recommendations.get("weather_condition", ""):
                adjusted_recs["suggested_base"] = "Bowl"
            else:
                adjusted_recs["suggested_base"] = "Biryani"

        return adjusted_recs

    def update_recommendation_scores(self, condition: str, time_of_day: str, category: str,
                                   item: str, feedback_score: int) -> bool:
        """
        Update recommendation scores based on feedback.

        Args:
            condition: Weather condition
            time_of_day: Time of day
            category: Item category
            item: Item name
            feedback_score: Feedback score (1-5)

        Returns:
            Success status
        """
        try:
            # Load current data
            current_data = []
            with open(self.weather_data_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                current_data = list(reader)

            # Determine if updating weather condition or time of day
            if condition:
                # Find and update the matching weather condition row
                item_found = False
                for row in current_data:
                    if (row["condition"] == condition and
                        row["category"] == category and
                        row["item"] == item and
                        row["time_of_day"] == ""):

                        # Update score (weighted average with existing score)
                        current_score = int(row["score"])
                        # 70% existing score, 30% new feedback
                        new_score = int(0.7 * current_score + 0.3 * feedback_score)
                        row["score"] = str(new_score)
                        item_found = True
                        break

                # If item not found, add it
                if not item_found:
                    new_row = {
                        "condition": condition,
                        "time_of_day": "",
                        "category": category,
                        "item": item,
                        "score": str(feedback_score),
                        "reasoning": f"Customer preference for {condition} weather"
                    }
                    current_data.append(new_row)

            elif time_of_day:
                # Find and update the matching time of day row
                item_found = False
                for row in current_data:
                    if (row["time_of_day"] == time_of_day and
                        row["category"] == category and
                        row["item"] == item and
                        row["condition"] == ""):

                        # Update score
                        current_score = int(row["score"])
                        new_score = int(0.7 * current_score + 0.3 * feedback_score)
                        row["score"] = str(new_score)
                        item_found = True
                        break

                # If item not found, add it
                if not item_found:
                    new_row = {
                        "condition": "",
                        "time_of_day": time_of_day,
                        "category": category,
                        "item": item,
                        "score": str(feedback_score),
                        "reasoning": f"Customer preference for {time_of_day}"
                    }
                    current_data.append(new_row)

            # Write updated data back to CSV
            with open(self.weather_data_path, 'w', newline='') as file:
                fieldnames = ["condition", "time_of_day", "category", "item", "score", "reasoning"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(current_data)

            # Reload weather data
            self.weather_data = self._load_weather_data()

            if condition:
                logger.info(f"Updated recommendation score for {condition} - {category} - {item}")
            else:
                logger.info(f"Updated recommendation score for {time_of_day} - {category} - {item}")

            return True

        except Exception as e:
            logger.error(f"Error updating recommendation score: {e}")
            return False

    def process_feedback(self, weather_condition: str, time_of_day: str,
                        feedback_type: str, items_selected: Dict[str, Any],
                        custom_suggestion: Optional[str] = None) -> Dict[str, Any]:
        """
        Process feedback on weather recommendations.

        Args:
            weather_condition: Weather condition
            time_of_day: Time of day
            feedback_type: Feedback type (accept, ignore, custom)
            items_selected: Selected food items
            custom_suggestion: Custom suggestion if provided

        Returns:
            Processed feedback result
        """
        result = {
            "weather_condition": weather_condition,
            "time_of_day": time_of_day,
            "feedback_type": feedback_type,
            "processed": False,
            "message": ""
        }

        try:
            # Process based on feedback type
            if feedback_type == "accept":
                # Increase scores for selected items
                if "base_type" in items_selected:
                    # Update weather condition score
                    self.update_recommendation_scores(
                        condition=weather_condition,
                        time_of_day="",
                        category="base_types",
                        item=items_selected["base_type"],
                        feedback_score=5  # High score for accepted items
                    )

                    # Update time of day score
                    self.update_recommendation_scores(
                        condition="",
                        time_of_day=time_of_day,
                        category="base_types",
                        item=items_selected["base_type"],
                        feedback_score=5
                    )

                result["processed"] = True
                result["message"] = "Recommendation accepted and scores updated"

            elif feedback_type == "custom" and custom_suggestion:
                # Handle custom suggestion for base type
                # Update weather condition score
                self.update_recommendation_scores(
                    condition=weather_condition,
                    time_of_day="",
                    category="base_types",
                    item=custom_suggestion,
                    feedback_score=5
                )

                # Update time of day score
                self.update_recommendation_scores(
                    condition="",
                    time_of_day=time_of_day,
                    category="base_types",
                    item=custom_suggestion,
                    feedback_score=5
                )

                result["processed"] = True
                result["message"] = f"Custom suggestion '{custom_suggestion}' processed"

            elif feedback_type == "ignore":
                # No changes needed for ignore
                result["processed"] = True
                result["message"] = "Recommendation ignored"

            return result

        except Exception as e:
            logger.error(f"Error processing weather recommendation feedback: {e}")
            result["processed"] = False
            result["message"] = f"Error processing feedback: {str(e)}"
            return result

    def get_weather_emoji(self, condition: str) -> str:
        """
        Get emoji representing weather condition.

        Args:
            condition: Weather condition

        Returns:
            Emoji representing the condition
        """
        weather_emojis = {
            "sunny": "☀️",
            "partly_cloudy": "⛅",
            "cloudy": "☁️",
            "rainy": "🌧️",
            "snowy": "❄️",
            "hot": "🔥",
            "cold": "🥶"
        }
        return weather_emojis.get(condition, "🌤️")