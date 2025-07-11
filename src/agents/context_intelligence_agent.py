# backend/agents/context_intelligence_agent.py
import asyncio
import aiohttp
from datetime import datetime, time
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent, AgentResult, AgentType, UserContext, AgentConfig
from backend.database import get_database
from backend.app.models.restaurant import Restaurant
from backend.app.models.delivery import DeliveryZone

class ContextIntelligenceAgent(BaseAgent):
    """
    Replaces Weather Agent and contextual parts of Face Recognition Agent.
    Focuses on actionable context: location, time, restaurant availability.
    """

    def __init__(self, user_id: str):
        super().__init__(AgentType.CONTEXT_INTELLIGENCE, user_id)
        self.db = get_database()
        self.weather_api_key = "your_weather_api_key"  # Move to environment
        self.cache = {}

    async def process(self, context: UserContext, **kwargs) -> AgentResult:
        """Analyze user context and provide actionable recommendations"""
        start_time = datetime.now()

        try:
            # Get all context information
            location_context = await self._get_location_context(context)
            time_context = await self._get_time_context(context)
            restaurant_context = await self._get_restaurant_availability(context)
            weather_context = await self._get_weather_context(context)

            # Combine all context data
            context_data = {
                "location": location_context,
                "time": time_context,
                "restaurants": restaurant_context,
                "weather": weather_context,
                "recommendations": await self._generate_context_recommendations(
                    location_context, time_context, restaurant_context, weather_context
                )
            }

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return AgentResult(
                agent_type=self.agent_type,
                success=True,
                data=context_data,
                confidence=0.9,
                execution_time_ms=int(execution_time)
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return AgentResult(
                agent_type=self.agent_type,
                success=False,
                data={"error": str(e)},
                confidence=0.0,
                execution_time_ms=int(execution_time)
            )

    async def _get_location_context(self, context: UserContext) -> Dict[str, Any]:
        """Get location-based context information"""
        if not context.location:
            return {"deliverable": False, "reason": "no_location"}

        # Check if location is in delivery zones
        delivery_zones = await self.db.fetch_all(
            "SELECT * FROM delivery_zones WHERE ST_Contains(area, ST_Point($1, $2))",
            context.location.get("longitude", 0),
            context.location.get("latitude", 0)
        )

        return {
            "deliverable": len(delivery_zones) > 0,
            "delivery_zones": [dict(zone) for zone in delivery_zones],
            "location": context.location
        }

    async def _get_time_context(self, context: UserContext) -> Dict[str, Any]:
        """Analyze time-based context"""
        current_time = context.current_time
        hour = current_time.hour

        # Define meal periods
        if 6 <= hour < 11:
            meal_period = "breakfast"
        elif 11 <= hour < 16:
            meal_period = "lunch"
        elif 16 <= hour < 20:
            meal_period = "dinner"
        elif 20 <= hour < 24:
            meal_period = "late_night"
        else:
            meal_period = "overnight"

        # Determine urgency based on time patterns
        urgency = "normal"
        if meal_period == "lunch" and 12 <= hour <= 13:
            urgency = "high"  # Lunch rush
        elif meal_period == "dinner" and 18 <= hour <= 19:
            urgency = "high"  # Dinner rush

        return {
            "meal_period": meal_period,
            "urgency": urgency,
            "current_hour": hour,
            "is_weekend": current_time.weekday() >= 5,
            "suggested_delivery_time": self._calculate_optimal_delivery_time(urgency)
        }

    async def _get_restaurant_availability(self, context: UserContext) -> Dict[str, Any]:
        """Get real-time restaurant availability"""
        current_time = context.current_time

        # Get restaurants open at current time
        open_restaurants = await self.db.fetch_all("""
            SELECT r.*, rh.opens_at, rh.closes_at
            FROM restaurants r
            JOIN restaurant_hours rh ON r.id = rh.restaurant_id
            WHERE rh.day_of_week = $1
            AND $2 BETWEEN rh.opens_at AND rh.closes_at
            AND r.is_active = true
        """, current_time.weekday(), current_time.time())

        # Check delivery capacity
        busy_restaurants = await self._check_restaurant_capacity(
            [r["id"] for r in open_restaurants]
        )

        return {
            "open_count": len(open_restaurants),
            "busy_restaurants": busy_restaurants,
            "available_restaurants": [
                dict(r) for r in open_restaurants
                if r["id"] not in busy_restaurants
            ]
        }

    async def _get_weather_context(self, context: UserContext) -> Dict[str, Any]:
        """Get weather context (simplified, actionable focus)"""
        if not context.location:
            return {"available": False}

        try:
            # Use cached weather if available and recent
            cache_key = f"weather_{context.location.get('latitude')}_{context.location.get('longitude')}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if (datetime.now() - cached_data["timestamp"]).seconds < 1800:  # 30 min cache
                    return cached_data["data"]

            # Fetch weather data
            lat = context.location.get("latitude")
            lon = context.location.get("longitude")

            async with aiohttp.ClientSession() as session:
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
                async with session.get(weather_url) as response:
                    weather_data = await response.json()

            # Extract actionable weather context
            temp = weather_data["main"]["temp"]
            condition = weather_data["weather"][0]["main"]

            weather_context = {
                "temperature": temp,
                "condition": condition,
                "food_preference_hint": self._weather_to_food_preference(temp, condition),
                "delivery_impact": self._assess_weather_delivery_impact(condition),
                "available": True
            }

            # Cache the result
            self.cache[cache_key] = {
                "data": weather_context,
                "timestamp": datetime.now()
            }

            return weather_context

        except Exception as e:
            return {"available": False, "error": str(e)}

    def _weather_to_food_preference(self, temp: float, condition: str) -> str:
        """Convert weather to subtle food preference hints"""
        if temp < 10:
            return "warm_comfort"
        elif temp > 25:
            return "light_refreshing"
        elif condition in ["Rain", "Thunderstorm"]:
            return "warm_comfort"
        else:
            return "neutral"

    def _assess_weather_delivery_impact(self, condition: str) -> str:
        """Assess how weather affects delivery"""
        if condition in ["Thunderstorm", "Snow"]:
            return "high_delay"
        elif condition in ["Rain", "Drizzle"]:
            return "moderate_delay"
        else:
            return "normal"

    async def _check_restaurant_capacity(self, restaurant_ids: List[int]) -> List[int]:
        """Check which restaurants are at capacity"""
        # Get current order counts for restaurants
        busy_restaurants = await self.db.fetch_all("""
            SELECT restaurant_id, COUNT(*) as active_orders
            FROM orders
            WHERE restaurant_id = ANY($1)
            AND status IN ('preparing', 'ready', 'out_for_delivery')
            AND created_at > NOW() - INTERVAL '2 hours'
            GROUP BY restaurant_id
            HAVING COUNT(*) > 15  -- Capacity threshold
        """, restaurant_ids)

        return [r["restaurant_id"] for r in busy_restaurants]

    def _calculate_optimal_delivery_time(self, urgency: str) -> int:
        """Calculate optimal delivery time in minutes"""
        base_time = 30

        if urgency == "high":
            return base_time + 15  # Rush periods take longer
        else:
            return base_time

    async def _generate_context_recommendations(
        self, location_ctx: Dict, time_ctx: Dict,
        restaurant_ctx: Dict, weather_ctx: Dict
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on context"""
        recommendations = []

        # Location-based recommendations
        if not location_ctx["deliverable"]:
            recommendations.append({
                "type": "location_warning",
                "message": "Delivery not available to this location",
                "action": "pickup_suggestion"
            })

        # Time-based recommendations
        if time_ctx["urgency"] == "high":
            recommendations.append({
                "type": "time_warning",
                "message": f"Peak {time_ctx['meal_period']} time - expect longer delivery",
                "estimated_delay": 15
            })

        # Restaurant availability
        if restaurant_ctx["open_count"] < 5:
            recommendations.append({
                "type": "availability_warning",
                "message": f"Only {restaurant_ctx['open_count']} restaurants open",
                "suggestion": "Consider ordering soon"
            })

        # Weather impact
        if weather_ctx.get("delivery_impact") != "normal":
            recommendations.append({
                "type": "weather_warning",
                "message": f"Weather may cause delays: {weather_ctx.get('condition')}",
                "estimated_delay": 10 if weather_ctx.get("delivery_impact") == "moderate_delay" else 20
            })

        return recommendations

    async def update_model(self, feedback: Dict[str, Any]) -> bool:
        """Update context intelligence based on feedback"""
        # For context intelligence, we mainly update delivery time predictions
        try:
            if feedback.get("actual_delivery_time") and feedback.get("predicted_delivery_time"):
                # Update delivery time prediction accuracy
                await self.db.execute("""
                    INSERT INTO delivery_predictions
                    (user_id, predicted_time, actual_time, context_factors)
                    VALUES ($1, $2, $3, $4)
                """,
                self.user_id,
                feedback["predicted_delivery_time"],
                feedback["actual_delivery_time"],
                feedback.get("context_factors", {})
                )
            return True
        except Exception:
            return False