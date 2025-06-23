# src/utils/llm_client.py
"""
LLM Client Utility for Intelligent Food Recommendation Insights
"""

import os
import logging
from typing import Optional, Dict, Any
import json

# Configure logging
logger = logging.getLogger(__name__)

def get_llm_response(prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
    """
    Get response from LLM for generating intelligent food recommendation insights.

    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum tokens in the response
        temperature: Temperature for response generation

    Returns:
        LLM response string or None if unavailable
    """
    try:
        # Try OpenAI first if available
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            return _get_openai_response(prompt, max_tokens, temperature)

        # Try other LLM providers or fall back to contextual generation
        return _generate_contextual_response(prompt)

    except Exception as e:
        logger.error(f"Error getting LLM response: {e}")
        return None

def _get_openai_response(prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
    """Get response from OpenAI API."""
    try:
        import openai

        openai.api_key = os.getenv("OPENAI_API_KEY")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a culinary expert and food scientist specializing in weather-appropriate food recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content.strip()

    except ImportError:
        logger.warning("OpenAI library not available")
        return None
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return None

def _generate_contextual_response(prompt: str) -> str:
    """
    Generate contextual response when LLM is not available.
    Uses rule-based approach to create meaningful food insights.
    """
    try:
        # Extract key information from prompt
        prompt_lower = prompt.lower()

        # Weather-based insights
        weather_insights = {
            "sunny": "bright, energizing flavors that complement the beautiful weather",
            "hot": "cooling, refreshing options that won't weigh you down in the heat",
            "rainy": "warming, comforting combinations that boost your mood on a dreary day",
            "cold": "hearty, warming spices that help maintain body temperature",
            "snowy": "rich, satisfying options that provide warmth and comfort",
            "cloudy": "balanced flavors that aren't too heavy for uncertain weather"
        }

        # Time-based insights
        time_insights = {
            "morning": "energizing nutrients to start your day right",
            "afternoon": "sustained energy to power through your productive hours",
            "evening": "satisfying comfort to help you unwind and relax"
        }

        # Extract weather condition
        weather_condition = None
        for condition in weather_insights.keys():
            if condition in prompt_lower:
                weather_condition = condition
                break

        # Extract time of day
        time_of_day = None
        for time_period in time_insights.keys():
            if time_period in prompt_lower:
                time_of_day = time_period
                break

        # Extract food items mentioned
        proteins = []
        sauces = []
        bases = []

        food_items = {
            "chicken": "proteins", "paneer": "proteins", "egg": "proteins", "soya": "proteins",
            "curry": "sauces", "mint": "sauces", "yogurt": "sauces", "malai": "sauces",
            "bowl": "bases", "wrap": "bases", "biryani": "bases", "sandwich": "bases"
        }

        for item, category in food_items.items():
            if item in prompt_lower:
                if category == "proteins":
                    proteins.append(item.title())
                elif category == "sauces":
                    sauces.append(item.title())
                elif category == "bases":
                    bases.append(item.title())

        # Generate contextual response
        response_parts = []

        if weather_condition and time_of_day:
            response_parts.append(f"Perfect for {weather_condition} {time_of_day}!")

        if proteins and sauces:
            response_parts.append(f"This combination of {', '.join(proteins)} with {', '.join(sauces)} provides {weather_insights.get(weather_condition, 'great flavor and nutrition')}.")

        if time_of_day:
            response_parts.append(f"The pairing delivers {time_insights.get(time_of_day, 'excellent nutrition')}.")

        # Add food science insight
        if weather_condition in ["hot", "sunny"]:
            response_parts.append("The cooling properties help regulate body temperature naturally.")
        elif weather_condition in ["cold", "snowy", "rainy"]:
            response_parts.append("The warming spices boost circulation and provide comfort.")

        # Combine into coherent response
        if response_parts:
            return " ".join(response_parts)
        else:
            return "This thoughtfully balanced combination provides excellent nutrition and satisfying flavors for your current conditions."

    except Exception as e:
        logger.error(f"Error in contextual response generation: {e}")
        return "A carefully crafted combination that's perfect for your current weather and time of day."

def get_location_based_insight(location: str, weather_data: Dict[str, Any]) -> str:
    """
    Generate location-specific food insights.

    Args:
        location: Location string
        weather_data: Current weather data

    Returns:
        Location-specific insight
    """
    try:
        location_lower = location.lower()
        condition = weather_data.get("condition", "cloudy")
        temperature = weather_data.get("temperature", 20)

        # Location-specific insights
        location_insights = {
            "san francisco": "perfect for the Bay Area's dynamic weather",
            "new york": "ideal for the city's fast-paced lifestyle",
            "chicago": "great for the Windy City's hearty appetite",
            "miami": "suited for the tropical climate",
            "seattle": "perfect for the Pacific Northwest vibe",
            "los angeles": "ideal for the sunny California lifestyle"
        }

        # Find matching location
        location_insight = "suited for your local climate"
        for city, insight in location_insights.items():
            if city in location_lower:
                location_insight = insight
                break

        return f"This combination is {location_insight} and {condition} weather at {temperature}°C."

    except Exception as e:
        logger.error(f"Error generating location insight: {e}")
        return "This combination is perfectly suited for your current location and weather."