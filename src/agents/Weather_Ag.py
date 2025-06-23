# /agents/Weather_Ag.py
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

# Import LLM client for intelligent insights
try:
    from src.utils.llm_client import get_llm_response
except ImportError:
    # Fallback if import fails
    def get_llm_response(prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        return None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("weather_recommender_agent")

class WeatherRecommenderAgent:
    """Agent for making weather-based food recommendations with intelligent LLM insights."""

    def __init__(self, weather_data_path: str):
        """
        Initialize the weather recommender agent.

        Args:
            weather_data_path: Path to weather recommendations CSV
        """
        self.weather_data_path = weather_data_path
        self.weather_data = self._load_weather_data()
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.weather_cache = {}
        self.weather_dish_scores = {
            "Clear": {
                "salad": 0.9,
                "grilled": 0.8,
                "ice cream": 0.9,
                "cold": 0.8
            },
            "Rain": {
                "soup": 0.9,
                "hot": 0.8,
                "stew": 0.9,
                "comfort food": 0.8
            },
            "Snow": {
                "hot chocolate": 0.9,
                "soup": 0.8,
                "warm": 0.9,
                "hearty": 0.8
            }
        }

        # Default weather-based recommendations with enhanced reasoning
        self.default_recommendations = {
            "rainy": {
                "proteins": ["Chicken", "Paneer/Indian Cheese"],
                "sauces": ["Curry Special", "Malai Masala"],
                "base_types": ["Bowl", "Biryani"],
                "reasoning": "🌧️ Perfect for a rainy day! Warm, hearty options that provide comfort while you stay cozy indoors."
            },
            "cold": {
                "proteins": ["Chicken", "Paneer/Indian Cheese"],
                "sauces": ["Curry Masala", "Red Spicy Sauce"],
                "base_types": ["Bowl", "Biryani"],
                "reasoning": "🥶 Beat the cold! Spicy, warming combinations that help maintain body temperature and boost metabolism."
            },
            "hot": {
                "proteins": ["Chicken", "Paneer/Indian Cheese", "Potato"],
                "sauces": ["Yogurt/Raita", "Mint Sauce"],
                "base_types": ["Bowl", "Wrap"],
                "reasoning": "🔥 Stay cool in the heat! Light, refreshing options with cooling sauces that won't weigh you down."
            },
            "sunny": {
                "proteins": ["Chicken", "Egg", "Soya"],
                "sauces": ["Mint Sauce", "Curry Special"],
                "base_types": ["Wrap", "Sandwich"],
                "reasoning": "☀️ Sunny day perfection! Fresh, balanced options perfect for enjoying beautiful weather."
            },
            "cloudy": {
                "proteins": ["Chicken", "Egg", "Paneer/Indian Cheese"],
                "sauces": ["Curry Special", "Malai Masala"],
                "base_types": ["Bowl", "Sandwich"],
                "reasoning": "☁️ Cloudy day comfort! Balanced options that aren't too heavy - perfect for unpredictable weather."
            }
        }

        # Time of day recommendations with enhanced reasoning
        self.time_recommendations = {
            "morning": {
                "proteins": ["Egg", "Paneer/Indian Cheese"],
                "sauces": ["Mint Sauce", "Yogurt/Raita"],
                "base_types": ["Wrap", "Sandwich"],
                "reasoning": "🌅 Morning energy boost! Light proteins and fresh flavors to start your day right."
            },
            "afternoon": {
                "proteins": ["Chicken", "Paneer/Indian Cheese", "Soya"],
                "sauces": ["Curry Special", "Malai Masala"],
                "base_types": ["Bowl", "Biryani"],
                "reasoning": "🌞 Midday fuel! Substantial, balanced meals to power through your afternoon."
            },
            "evening": {
                "proteins": ["Chicken", "Paneer/Indian Cheese", "Potato"],
                "sauces": ["Curry Masala", "Malai Masala"],
                "base_types": ["Bowl", "Wrap"],
                "reasoning": "🌆 Evening satisfaction! Flavorful, comforting options to unwind with."
            }
        }

        logger.info("Weather recommender agent initialized with LLM-powered insights")

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

    def get_current_weather(self, location: str = "San Francisco,US") -> Dict[str, Any]:
        """
        Get current weather data from OpenWeather API.

        Args:
            location: Location string (city,country or lat,lon)

        Returns:
            Weather data dictionary
        """
        if not self.api_key:
            # Generate realistic random weather for demo/testing
            conditions = ["sunny", "cloudy", "rainy", "snowy", "windy"]
            temp_ranges = {
                "sunny": (18, 35),
                "cloudy": (10, 25),
                "rainy": (8, 22),
                "snowy": (-5, 8),
                "windy": (5, 20)
            }

            condition = random.choice(conditions)
            temp_min, temp_max = temp_ranges[condition]
            temperature = round(random.uniform(temp_min, temp_max), 1)

            weather_data = {
                "condition": condition,
                "temperature": temperature,
                "humidity": random.randint(30, 90),
                "wind_speed": round(random.uniform(0, 20), 1),
                "description": f"{condition.title()} weather",
                "location": location,
                "source": "simulated"
            }

            logger.info(f"Generated random weather: {condition}, {temperature}°C")
            return weather_data

        try:
            # Use OpenWeather API for real weather data
            base_url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"  # Celsius temperature
            }

            response = requests.get(base_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Map OpenWeather conditions to our simplified conditions
                condition_mapping = {
                    "clear": "sunny",
                    "clouds": "cloudy",
                    "rain": "rainy",
                    "drizzle": "rainy",
                    "thunderstorm": "rainy",
                    "snow": "snowy",
                    "mist": "cloudy",
                    "fog": "cloudy",
                    "haze": "cloudy"
                }

                weather_condition = data["weather"][0]["main"].lower()
                mapped_condition = condition_mapping.get(weather_condition, "cloudy")

                weather_data = {
                    "condition": mapped_condition,
                    "temperature": round(data["main"]["temp"], 1),
                    "humidity": data["main"]["humidity"],
                    "wind_speed": round(data["wind"]["speed"], 1),
                    "description": data["weather"][0]["description"],
                    "location": f"{data['name']}, {data['sys']['country']}",
                    "source": "openweather_api"
                }

                # Cache the result
                self.weather_cache[location] = {
                    "data": weather_data,
                    "timestamp": datetime.now().timestamp()
                }

                logger.info(f"Retrieved weather from API: {mapped_condition}, {weather_data['temperature']}°C in {weather_data['location']}")
                return weather_data

            else:
                logger.error(f"OpenWeather API error: {response.status_code}")
                # Fall back to random weather
                return self.get_current_weather()

        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            # Fall back to random weather
            return self.get_current_weather()

    def get_cached_weather(self, location: str = "San Francisco,US", cache_duration: int = 600) -> Optional[Dict[str, Any]]:
        """
        Get weather from cache if available and not expired.

        Args:
            location: Location string
            cache_duration: Cache duration in seconds (default 10 minutes)

        Returns:
            Cached weather data or None if expired/unavailable
        """
        if location in self.weather_cache:
            cached = self.weather_cache[location]
            age = datetime.now().timestamp() - cached["timestamp"]

            if age < cache_duration:
                logger.info(f"Using cached weather data for {location}")
                return cached["data"]
            else:
                # Remove expired cache
                del self.weather_cache[location]

        return None

    def get_recommendations(self, weather_data: Dict[str, Any], time_of_day: str,
                          customer_id: Optional[str] = None,
                          mood: str = "neutral",
                          customer_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Get weather-based food recommendations with intelligent LLM insights.

        Args:
            weather_data: Current weather information
            time_of_day: Time of day (morning, afternoon, evening)
            customer_id: Customer identifier for personalization
            mood: Customer mood for recommendation adjustment
            customer_history: Customer's previous order history for personalization

        Returns:
            Weather-based food recommendations with intelligent insights
        """
        # Extract weather parameters
        temperature = weather_data.get("temperature", 20.0)
        humidity = weather_data.get("humidity", 50.0)
        condition = weather_data.get("condition", "sunny")

        # Initialize recommendation containers
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

        # Combine proteins
        if "proteins" in weather_recs and "proteins" in time_recs:
            combined_recs["proteins"] = [
                weather_recs["proteins"][0],
                time_recs["proteins"][0]
            ]
            for protein in weather_recs["proteins"][1:] + time_recs["proteins"][1:]:
                if protein not in combined_recs["proteins"]:
                    combined_recs["proteins"].append(protein)
                    if len(combined_recs["proteins"]) >= 3:
                        break
        elif "proteins" in weather_recs:
            combined_recs["proteins"] = weather_recs["proteins"][:3]
        elif "proteins" in time_recs:
            combined_recs["proteins"] = time_recs["proteins"][:3]

        # Combine sauces
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

        # Combine base types
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

        # Get top suggestion for base
        if "base_types" in combined_recs and combined_recs["base_types"]:
            combined_recs["suggested_base"] = combined_recs["base_types"][0]
        else:
            combined_recs["suggested_base"] = "Bowl"  # Default option

        # Add weather and time information
        combined_recs["weather_condition"] = condition
        combined_recs["temperature"] = temperature
        combined_recs["time_of_day"] = time_of_day

        # Get current location for enhanced recommendations
        current_location = self.get_user_location()
        combined_recs["location"] = weather_data.get("location", current_location)

        # Generate intelligent LLM-powered insights with location context
        try:
            intelligent_reasoning = self.generate_llm_insights(
                weather_condition=condition,
                temperature=temperature,
                time_of_day=time_of_day,
                recommended_combination=combined_recs,
                customer_history=customer_history,
                location=current_location
            )
            combined_recs["reasoning"] = intelligent_reasoning
            combined_recs["llm_powered"] = True
            combined_recs["location_aware"] = True
        except Exception as e:
            logger.error(f"Error generating LLM insights, using fallback: {e}")
            # Combine basic reasoning as fallback
            weather_reason = weather_recs.get("reasoning", "")
            time_reason = time_recs.get("reasoning", "")

            if weather_reason and time_reason:
                combined_recs["reasoning"] = f"{weather_reason} {time_reason}"
            elif weather_reason:
                combined_recs["reasoning"] = weather_reason
            elif time_reason:
                combined_recs["reasoning"] = time_reason
            else:
                combined_recs["reasoning"] = "Recommended combination based on current weather and time."
            combined_recs["llm_powered"] = False
            combined_recs["location_aware"] = False

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

    def calculate_weather_match_score(self, dish_description: str, weather_condition: str) -> float:
        """Calculate how well a dish matches the current weather"""
        if weather_condition not in self.weather_dish_scores:
            return 0.5  # neutral score for unknown weather

        weather_preferences = self.weather_dish_scores[weather_condition]
        score = 0.5  # base score

        # Check if dish matches any weather preferences
        for keyword, keyword_score in weather_preferences.items():
            if keyword.lower() in dish_description.lower():
                score = max(score, keyword_score)

        return score

    def get_weather_challenge_progress(self, user_orders: List[Dict]) -> Dict:
        """Calculate progress towards weather-related challenges"""
        weather_matches = 0
        perfect_matches = 0

        for order in user_orders:
            if "weather_match_score" in order:
                if order["weather_match_score"] >= 0.7:
                    weather_matches += 1
                if order["weather_match_score"] >= 0.9:
                    perfect_matches += 1

        return {
            "weather_matches": weather_matches,
            "perfect_matches": perfect_matches,
            "weather_master_progress": min(weather_matches / 5, 1.0),  # Progress towards Weather Master achievement
            "perfect_match_progress": min(perfect_matches / 3, 1.0)   # Progress towards Perfect Match achievement
        }

    def get_weather_based_challenges(self, current_weather: str) -> List[Dict]:
        """Generate weather-specific challenges based on current conditions"""
        challenges = []

        if current_weather == "Clear":
            challenges.append({
                "id": "sunshine_seeker",
                "title": "Sunshine Seeker",
                "description": "Order a refreshing dish perfect for sunny weather",
                "points": 25,
                "weather_condition": current_weather
            })
        elif current_weather == "Rain":
            challenges.append({
                "id": "rainy_day_comfort",
                "title": "Rainy Day Comfort",
                "description": "Order a comforting dish that pairs well with rain",
                "points": 25,
                "weather_condition": current_weather
            })
        elif current_weather == "Snow":
            challenges.append({
                "id": "winter_warmer",
                "title": "Winter Warmer",
                "description": "Order a warming dish perfect for snowy weather",
                "points": 25,
                "weather_condition": current_weather
            })

        return challenges

    def get_user_location(self) -> str:
        """
        Get user's current location using IP geolocation.
        Fallback to default location if unable to detect.

        Returns:
            Location string in format "City,Country"
        """
        try:
            # Try to get location from IP geolocation service
            response = requests.get("http://ip-api.com/json/", timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    city = data.get("city", "")
                    country = data.get("countryCode", "")
                    location = f"{city},{country}" if city and country else "San Francisco,US"
                    logger.info(f"Detected user location: {location}")
                    return location

            # Fallback if API fails
            logger.warning("Could not detect location, using default")
            return "San Francisco,US"

        except Exception as e:
            logger.error(f"Error detecting location: {e}")
            return "San Francisco,US"

    def generate_llm_insights(self, weather_condition: str, temperature: float,
                            time_of_day: str, recommended_combination: Dict[str, Any],
                            customer_history: Optional[List[Dict]] = None,
                            location: Optional[str] = None) -> str:
        """
        Generate intelligent insights using LLM for why specific combinations are recommended.

        Args:
            weather_condition: Current weather condition
            temperature: Current temperature
            time_of_day: Time of day
            recommended_combination: The recommended food combination
            customer_history: Customer's previous order history
            location: User's current location

        Returns:
            Intelligent explanation for the recommendation
        """
        try:
            # Build context for LLM
            base = recommended_combination.get("suggested_base", "Bowl")
            proteins = ", ".join(recommended_combination.get("proteins", [])[:2])
            sauces = ", ".join(recommended_combination.get("sauces", [])[:2])

            # Add location context
            location_context = ""
            if location:
                location_context = f"Location: {location}\n"

            # Analyze customer history for personalization
            history_context = ""
            if customer_history:
                liked_items = []
                disliked_items = []
                for order in customer_history[-5:]:  # Last 5 orders
                    feedback = order.get("feedback_score", 3)
                    if feedback >= 4:
                        liked_items.extend([order.get("protein", ""), order.get("sauce", "")])
                    elif feedback <= 2:
                        disliked_items.extend([order.get("protein", ""), order.get("sauce", "")])

                if liked_items:
                    history_context = f"Customer preferences: Previously enjoyed {', '.join(filter(None, liked_items[:3]))}. "
                if disliked_items:
                    history_context += f"Tends to avoid: {', '.join(filter(None, disliked_items[:2]))}. "

            # Create enhanced LLM prompt for intelligent insights
            prompt = f"""As a food science expert and culinary advisor, explain why this combination is perfect for the current conditions:

{location_context}Weather: {weather_condition} weather, {temperature}°C
Time: {time_of_day}
Recommendation: {base} with {proteins} and {sauces}
{history_context}

Provide a brief, engaging explanation (60-90 words) covering:
1. Why this base/protein/sauce combo works for {weather_condition} weather at {temperature}°C
2. How it suits {time_of_day} dining in this location
3. Nutritional or comfort benefits specific to these conditions
4. Make it personal, appetizing, and scientifically informed

Use food science principles and keep it conversational like a knowledgeable chef's recommendation."""

            llm_insight = get_llm_response(prompt, max_tokens=150)

            if llm_insight:
                # Add location-specific insight if available
                if location:
                    from src.utils.llm_client import get_location_based_insight
                    location_insight = get_location_based_insight(location, {
                        "condition": weather_condition,
                        "temperature": temperature
                    })
                    return f"{llm_insight} {location_insight}"
                return llm_insight
            else:
                # Fallback to enhanced contextual reasoning
                return self._generate_enhanced_fallback(weather_condition, temperature, time_of_day,
                                                      base, proteins, sauces, location)

        except Exception as e:
            logger.error(f"Error generating LLM insights: {e}")
            return self._generate_enhanced_fallback(weather_condition, temperature, time_of_day,
                                                  recommended_combination.get("suggested_base", "Bowl"),
                                                  ", ".join(recommended_combination.get("proteins", [])[:2]),
                                                  ", ".join(recommended_combination.get("sauces", [])[:2]),
                                                  location)

    def _generate_enhanced_fallback(self, weather_condition: str, temperature: float,
                                  time_of_day: str, base: str, proteins: str, sauces: str,
                                  location: Optional[str] = None) -> str:
        """Generate enhanced contextual fallback reasoning with location awareness."""

        # Weather-specific benefits with temperature context
        if weather_condition == "hot" or temperature > 28:
            weather_benefit = f"offers cooling relief in {temperature}°C heat with refreshing flavors"
            science_note = "The cooling ingredients help regulate body temperature naturally."
        elif weather_condition == "cold" or temperature < 5:
            weather_benefit = f"provides warming comfort in {temperature}°C cold with heat-generating spices"
            science_note = "The warming spices boost circulation and metabolic heat production."
        elif weather_condition == "rainy":
            weather_benefit = "delivers mood-boosting comfort on this rainy day"
            science_note = "Comfort foods release serotonin, naturally improving mood."
        elif weather_condition == "snowy":
            weather_benefit = f"provides hearty warmth perfect for snowy {temperature}°C weather"
            science_note = "Rich, satisfying foods help maintain energy in cold conditions."
        else:
            weather_benefit = f"provides balanced nutrition perfect for {weather_condition} weather at {temperature}°C"
            science_note = "This combination delivers optimal nutrition for current conditions."

        # Time-specific benefits
        time_benefits = {
            "morning": "energizes your start with sustained-release nutrients",
            "afternoon": "fuels peak performance with balanced macronutrients",
            "evening": "provides satisfying comfort to help you unwind"
        }
        time_benefit = time_benefits.get(time_of_day, "suits your dining needs perfectly")

        # Base-specific benefits
        base_benefits = {
            "Bowl": "allows flavors to meld beautifully while keeping everything warm",
            "Wrap": "provides perfect portability and optimal flavor ratios",
            "Biryani": "delivers complex carbohydrates for sustained energy",
            "Sandwich": "offers convenient nutrition in perfectly balanced bites"
        }
        base_benefit = base_benefits.get(base, "delivers exceptional taste and nutrition")

        # Location context
        location_note = ""
        if location:
            if "san francisco" in location.lower():
                location_note = " Perfect for the Bay Area's dynamic climate!"
            elif "new york" in location.lower():
                location_note = " Ideal for city life energy needs!"
            elif any(city in location.lower() for city in ["miami", "los angeles", "phoenix"]):
                location_note = " Great for warm climate dining!"
            elif any(city in location.lower() for city in ["chicago", "boston", "seattle"]):
                location_note = " Perfect for cooler climate comfort!"

        return f"🌟 This {base.lower()} with {proteins} and {sauces} {weather_benefit}. The combination {time_benefit} during {time_of_day}, while the {base.lower()} format {base_benefit}. {science_note}{location_note}"

    def get_live_weather_recommendations(self, time_of_day: str,
                                       customer_id: Optional[str] = None,
                                       mood: str = "neutral",
                                       customer_history: Optional[List[Dict]] = None,
                                       location: Optional[str] = None) -> Dict[str, Any]:
        """
        Get live weather-based recommendations using current location and real-time weather data.

        Args:
            time_of_day: Time of day (morning, afternoon, evening)
            customer_id: Customer identifier for personalization
            mood: Customer mood for recommendation adjustment
            customer_history: Customer's previous order history for personalization
            location: Optional specific location (otherwise auto-detects)

        Returns:
            Live weather-based food recommendations with intelligent insights
        """
        try:
            # Get current location if not provided
            if not location:
                location = self.get_user_location()
                logger.info(f"Auto-detected location: {location}")

            # Check cache first
            cached_weather = self.get_cached_weather(location)
            if cached_weather:
                logger.info(f"Using cached weather data for {location}")
                weather_data = cached_weather
            else:
                # Get current weather for location
                weather_data = self.get_current_weather(location)
                logger.info(f"Fetched live weather data for {location}: {weather_data.get('condition', 'unknown')} at {weather_data.get('temperature', 'unknown')}°C")

            # Get recommendations with the live weather data
            recommendations = self.get_recommendations(
                weather_data=weather_data,
                time_of_day=time_of_day,
                customer_id=customer_id,
                mood=mood,
                customer_history=customer_history
            )

            # Add live weather indicators
            recommendations["live_weather"] = True
            recommendations["weather_source"] = weather_data.get("source", "unknown")
            recommendations["last_updated"] = datetime.now().isoformat()

            # Add weather emoji for visual appeal
            recommendations["weather_emoji"] = self.get_weather_emoji(weather_data.get("condition", "cloudy"))

            logger.info(f"Generated live weather recommendations for {location}")
            return recommendations

        except Exception as e:
            logger.error(f"Error getting live weather recommendations: {e}")
            # Fallback to default weather
            fallback_weather = {
                "condition": "cloudy",
                "temperature": 20.0,
                "location": location or "Unknown",
                "source": "fallback"
            }

            recommendations = self.get_recommendations(
                weather_data=fallback_weather,
                time_of_day=time_of_day,
                customer_id=customer_id,
                mood=mood,
                customer_history=customer_history
            )

            recommendations["live_weather"] = False
            recommendations["weather_source"] = "fallback"
            recommendations["error"] = "Could not fetch live weather data"

            return recommendations