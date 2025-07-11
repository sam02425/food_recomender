# backend/agents/preference_learning_agent.py
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from .base_agent import BaseAgent, AgentResult, AgentType, UserContext, AgentConfig
from backend.database import get_database
from backend.app.models.user_preferences import UserPreference
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class PreferenceLearningAgent(BaseAgent):
    """
    Combines Learner Agent, Record Keeper Agent, and Social/Trust Agent.
    Focuses on behavioral pattern learning without intrusive emotion detection.
    """

    def __init__(self, user_id: str):
        super().__init__(AgentType.PREFERENCE_LEARNING, user_id)
        self.db = get_database()
        self.preference_cache = {}
        self.similarity_threshold = 0.7

    async def process(self, context: UserContext, **kwargs) -> AgentResult:
        """Learn from user behavior and provide personalized recommendations"""
        start_time = datetime.now()

        try:
            # Get user's order history and preferences
            order_history = await self._get_order_history(context.user_id)
            behavioral_patterns = await self._analyze_behavioral_patterns(order_history, context)

            # Generate recommendations based on learned preferences
            recommendations = await self._generate_preference_recommendations(
                behavioral_patterns, context, kwargs.get("current_menu", [])
            )

            # Calculate confidence based on data quality
            confidence = self._calculate_confidence(order_history, behavioral_patterns)

            result_data = {
                "behavioral_patterns": behavioral_patterns,
                "recommendations": recommendations,
                "user_profile": await self._get_user_profile_summary(),
                "learning_metrics": {
                    "total_orders": len(order_history),
                    "pattern_confidence": confidence,
                    "last_order": order_history[0]["created_at"].isoformat() if order_history else None
                }
            }

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return AgentResult(
                agent_type=self.agent_type,
                success=True,
                data=result_data,
                confidence=confidence,
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

    async def _get_order_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's order history for pattern analysis"""
        orders = await self.db.fetch_all("""
            SELECT o.*, oi.menu_item_id, oi.quantity, oi.customizations,
                   mi.name, mi.category, mi.price, mi.cuisine_type,
                   r.name as restaurant_name, r.cuisine_type as restaurant_cuisine
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            JOIN restaurants r ON o.restaurant_id = r.id
            WHERE o.user_id = $1
            AND o.status = 'completed'
            ORDER BY o.created_at DESC
            LIMIT $2
        """, user_id, limit)

        return [dict(order) for order in orders]

    async def _analyze_behavioral_patterns(
        self, order_history: List[Dict], context: UserContext
    ) -> Dict[str, Any]:
        """Analyze user behavioral patterns from order history"""
        if not order_history:
            return {"patterns": {}, "insights": [], "data_sufficient": False}

        patterns = {
            "temporal_patterns": self._analyze_temporal_patterns(order_history),
            "cuisine_preferences": self._analyze_cuisine_preferences(order_history),
            "price_sensitivity": self._analyze_price_patterns(order_history),
            "restaurant_loyalty": self._analyze_restaurant_loyalty(order_history),
            "customization_patterns": self._analyze_customization_patterns(order_history),
            "ordering_behavior": self._analyze_ordering_behavior(order_history, context)
        }

        insights = self._generate_behavioral_insights(patterns)

        return {
            "patterns": patterns,
            "insights": insights,
            "data_sufficient": len(order_history) >= AgentConfig.PREFERENCE_MIN_ORDERS_FOR_LEARNING
        }

    def _analyze_temporal_patterns(self, orders: List[Dict]) -> Dict[str, Any]:
        """Analyze when user typically orders"""
        order_times = []
        order_days = []

        for order in orders:
            created_at = order["created_at"]
            order_times.append(created_at.hour)
            order_days.append(created_at.weekday())

        # Find most common ordering times and days
        time_counter = Counter(order_times)
        day_counter = Counter(order_days)

        return {
            "preferred_hours": dict(time_counter.most_common(3)),
            "preferred_days": dict(day_counter.most_common(3)),
            "most_active_hour": time_counter.most_common(1)[0][0] if time_counter else None,
            "weekend_vs_weekday": {
                "weekend_orders": sum(1 for day in order_days if day >= 5),
                "weekday_orders": sum(1 for day in order_days if day < 5)
            }
        }

    def _analyze_cuisine_preferences(self, orders: List[Dict]) -> Dict[str, Any]:
        """Analyze cuisine and category preferences"""
        cuisines = [order["cuisine_type"] for order in orders if order["cuisine_type"]]
        categories = [order["category"] for order in orders if order["category"]]

        cuisine_counter = Counter(cuisines)
        category_counter = Counter(categories)

        # Calculate diversity score
        diversity_score = len(set(cuisines)) / len(cuisines) if cuisines else 0

        return {
            "preferred_cuisines": dict(cuisine_counter.most_common(5)),
            "preferred_categories": dict(category_counter.most_common(5)),
            "cuisine_diversity": diversity_score,
            "top_cuisine": cuisine_counter.most_common(1)[0][0] if cuisine_counter else None,
            "cuisine_distribution": {
                cuisine: count/len(cuisines) for cuisine, count in cuisine_counter.items()
            } if cuisines else {}
        }

    def _analyze_price_patterns(self, orders: List[Dict]) -> Dict[str, Any]:
        """Analyze price sensitivity and spending patterns"""
        prices = [float(order["price"]) for order in orders if order["price"]]

        if not prices:
            return {"data_available": False}

        avg_price = np.mean(prices)
        price_std = np.std(prices)

        # Categorize price preferences
        if avg_price < 15:
            price_category = "budget_conscious"
        elif avg_price < 25:
            price_category = "moderate_spender"
        else:
            price_category = "premium_buyer"

        return {
            "average_order_value": round(avg_price, 2),
            "price_range": {
                "min": min(prices),
                "max": max(prices),
                "std": round(price_std, 2)
            },
            "price_category": price_category,
            "price_consistency": "consistent" if price_std < avg_price * 0.3 else "varied",
            "data_available": True
        }

    def _analyze_restaurant_loyalty(self, orders: List[Dict]) -> Dict[str, Any]:
        """Analyze restaurant loyalty patterns"""
        restaurants = [order["restaurant_name"] for order in orders]
        restaurant_counter = Counter(restaurants)

        total_orders = len(orders)
        unique_restaurants = len(set(restaurants))

        # Calculate loyalty score
        if total_orders > 0:
            top_restaurant_frequency = restaurant_counter.most_common(1)[0][1] / total_orders
            loyalty_score = top_restaurant_frequency * (1 - unique_restaurants / total_orders)
        else:
            loyalty_score = 0

        return {
            "favorite_restaurants": dict(restaurant_counter.most_common(3)),
            "restaurant_diversity": unique_restaurants,
            "loyalty_score": round(loyalty_score, 3),
            "exploration_tendency": "high" if unique_restaurants / total_orders > 0.7 else "low"
        }

    def _analyze_customization_patterns(self, orders: List[Dict]) -> Dict[str, Any]:
        """Analyze how user customizes orders"""
        customizations = []
        for order in orders:
            if order.get("customizations"):
                try:
                    custom_data = json.loads(order["customizations"])
                    customizations.extend(custom_data.keys() if isinstance(custom_data, dict) else [])
                except:
                    continue

        customization_counter = Counter(customizations)

        return {
            "common_customizations": dict(customization_counter.most_common(5)),
            "customization_frequency": len(customizations) / len(orders) if orders else 0,
            "customization_style": "heavy_customizer" if len(customizations) / len(orders) > 0.5 else "light_customizer"
        }

    def _analyze_ordering_behavior(
        self, orders: List[Dict], context: UserContext
    ) -> Dict[str, Any]:
        """Analyze implicit behavioral signals"""
        # Group orders by session/time proximity
        recent_orders = [
            order for order in orders
            if (datetime.now() - order["created_at"]).days <= 30
        ]

        # Analyze ordering speed (proxy for decision confidence)
        order_frequencies = {}
        for order in recent_orders:
            date_key = order["created_at"].date()
            order_frequencies[date_key] = order_frequencies.get(date_key, 0) + 1

        # Calculate reorder patterns
        item_names = [order["name"] for order in orders]
        reorder_rate = 1 - len(set(item_names)) / len(item_names) if item_names else 0

        return {
            "recent_activity": len(recent_orders),
            "ordering_frequency": len(recent_orders) / 30,  # orders per day
            "reorder_tendency": round(reorder_rate, 3),
            "decision_style": "decisive" if reorder_rate > 0.3 else "exploratory",
            "last_order_days_ago": (datetime.now() - orders[0]["created_at"]).days if orders else None
        }

    def _generate_behavioral_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate human-readable insights from patterns"""
        insights = []

        # Temporal insights
        temporal = patterns.get("temporal_patterns", {})
        if temporal.get("most_active_hour"):
            hour = temporal["most_active_hour"]
            if 11 <= hour <= 14:
                insights.append("Primarily orders lunch during work hours")
            elif 18 <= hour <= 21:
                insights.append("Prefers dinner delivery in evening")

        # Cuisine insights
        cuisine = patterns.get("cuisine_preferences", {})
        if cuisine.get("cuisine_diversity", 0) > 0.7:
            insights.append("Enjoys trying diverse cuisines")
        elif cuisine.get("top_cuisine"):
            insights.append(f"Strong preference for {cuisine['top_cuisine']} cuisine")

        # Price insights
        price = patterns.get("price_sensitivity", {})
        if price.get("price_category") == "budget_conscious":
            insights.append("Budget-conscious with consistent spending patterns")
        elif price.get("price_category") == "premium_buyer":
            insights.append("Willing to pay premium for quality")

        # Behavior insights
        behavior = patterns.get("ordering_behavior", {})
        if behavior.get("reorder_tendency", 0) > 0.4:
            insights.append("Often reorders favorite items")
        elif behavior.get("decision_style") == "exploratory":
            insights.append("Enjoys exploring new menu options")

        return insights

    async def _generate_preference_recommendations(
        self, patterns: Dict[str, Any], context: UserContext, current_menu: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on learned preferences"""
        recommendations = []

        if not patterns.get("data_sufficient", False):
            return [{
                "type": "insufficient_data",
                "message": "Need more order history for personalized recommendations",
                "fallback": "popular_items"
            }]

        # Time-based recommendations
        current_hour = context.current_time.hour
        temporal_patterns = patterns["patterns"].get("temporal_patterns", {})

        if current_hour in temporal_patterns.get("preferred_hours", {}):
            recommendations.append({
                "type": "temporal_match",
                "message": "Based on your usual ordering time",
                "weight": 0.8
            })

        # Cuisine-based recommendations
        cuisine_prefs = patterns["patterns"].get("cuisine_preferences", {})
        if cuisine_prefs.get("preferred_cuisines"):
            top_cuisines = list(cuisine_prefs["preferred_cuisines"].keys())[:2]
            recommendations.extend([{
                "type": "cuisine_preference",
                "cuisine": cuisine,
                "message": f"You often enjoy {cuisine} cuisine",
                "weight": 0.9
            } for cuisine in top_cuisines])

        # Price-based filtering
        price_patterns = patterns["patterns"].get("price_sensitivity", {})
        if price_patterns.get("data_available"):
            avg_price = price_patterns["average_order_value"]
            recommendations.append({
                "type": "price_match",
                "price_range": f"${avg_price-5:.0f}-${avg_price+5:.0f}",
                "message": "Within your typical price range",
                "weight": 0.6
            })

        # Behavioral recommendations
        behavior = patterns["patterns"].get("ordering_behavior", {})
        if behavior.get("reorder_tendency", 0) > 0.4:
            recommendations.append({
                "type": "reorder_suggestion",
                "message": "Quick reorder of recent favorites",
                "action": "show_recent_orders",
                "weight": 0.85
            })

        return recommendations

    def _calculate_confidence(
        self, order_history: List[Dict], patterns: Dict[str, Any]
    ) -> float:
        """Calculate confidence in preference predictions"""
        if not order_history:
            return 0.0

        # Base confidence on data quantity
        data_confidence = min(len(order_history) / 20, 1.0)  # Max confidence at 20+ orders

        # Adjust for data recency
        if order_history:
            days_since_last = (datetime.now() - order_history[0]["created_at"]).days
            recency_factor = max(0.5, 1.0 - (days_since_last / 30))  # Decay over 30 days
        else:
            recency_factor = 0.0

        # Adjust for pattern consistency
        consistency_factor = 1.0
        price_patterns = patterns.get("patterns", {}).get("price_sensitivity", {})
        if price_patterns.get("price_consistency") == "varied":
            consistency_factor *= 0.8

        return data_confidence * recency_factor * consistency_factor

    async def _get_user_profile_summary(self) -> Dict[str, Any]:
        """Get summary of user profile for display"""
        profile = await self.db.fetch_one("""
            SELECT preferences, dietary_restrictions, favorite_cuisines
            FROM user_profiles
            WHERE user_id = $1
        """, self.user_id)

        if profile:
            return dict(profile)
        else:
            return {"new_user": True}

    async def update_model(self, feedback: Dict[str, Any]) -> bool:
        """Update preference learning based on user feedback"""
        try:
            feedback_data = {
                "user_id": self.user_id,
                "feedback_type": feedback.get("type"),
                "item_id": feedback.get("item_id"),
                "rating": feedback.get("rating"),
                "accepted": feedback.get("accepted", False),
                "timestamp": datetime.now()
            }

            # Store feedback for future learning
            await self.db.execute("""
                INSERT INTO user_feedback
                (user_id, feedback_type, item_id, rating, accepted, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                feedback_data["user_id"],
                feedback_data["feedback_type"],
                feedback_data["item_id"],
                feedback_data["rating"],
                feedback_data["accepted"],
                feedback_data["timestamp"]
            )

            # Update preference weights if needed
            if feedback.get("rating") is not None:
                await self._update_preference_weights(feedback)

            return True

        except Exception:
            return False

    async def _update_preference_weights(self, feedback: Dict[str, Any]) -> None:
        """Update internal preference weights based on feedback"""
        # Implementation for updating learned preferences
        # This would involve updating cuisine preferences, price sensitivity, etc.
        # based on user ratings and acceptance of recommendations
        pass