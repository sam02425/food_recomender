# backend/agents/problem_prevention_agent.py
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from .base_agent import BaseAgent, AgentResult, AgentType, UserContext, AgentConfig
from backend.database import get_database

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ProblemType(Enum):
    DELIVERY_DELAY = "delivery_delay"
    ORDER_ACCURACY = "order_accuracy"
    RESTAURANT_CAPACITY = "restaurant_capacity"
    PAYMENT_ISSUE = "payment_issue"
    DELIVERY_AREA = "delivery_area"
    MENU_AVAILABILITY = "menu_availability"

class ProblemPreventionAgent(BaseAgent):
    """
    Replaces Health Recommender and Entertainer agents.
    Focuses on preventing the 25% of orders that have problems.
    Addresses delivery time, order accuracy, fee transparency.
    """

    def __init__(self, user_id: str):
        super().__init__(AgentType.PROBLEM_PREVENTION, user_id)
        self.db = get_database()
        self.risk_thresholds = {
            RiskLevel.LOW: 0.3,
            RiskLevel.MEDIUM: 0.6,
            RiskLevel.HIGH: 0.8
        }

    async def process(self, context: UserContext, **kwargs) -> AgentResult:
        """Analyze potential problems and provide prevention strategies"""
        start_time = datetime.now()

        try:
            order_details = kwargs.get("order_details", {})

            # Run all problem prevention checks
            risk_analysis = await self._analyze_delivery_risks(context, order_details)
            validation_results = await self._validate_order_feasibility(order_details)
            prevention_strategies = await self._generate_prevention_strategies(
                risk_analysis, validation_results, context
            )

            # Calculate overall risk score
            overall_risk = self._calculate_overall_risk(risk_analysis)

            result_data = {
                "risk_analysis": risk_analysis,
                "validation_results": validation_results,
                "prevention_strategies": prevention_strategies,
                "overall_risk": overall_risk,
                "recommendations": await self._generate_problem_prevention_recommendations(
                    risk_analysis, validation_results, overall_risk
                )
            }

            # Confidence based on data availability and risk clarity
            confidence = self._calculate_prevention_confidence(risk_analysis, validation_results)

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

    async def _analyze_delivery_risks(
        self, context: UserContext, order_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze various delivery-related risks"""
        risks = {}

        # Time-based delivery risk
        risks["time_risk"] = await self._assess_time_based_risk(context)

        # Restaurant capacity risk
        if order_details.get("restaurant_id"):
            risks["capacity_risk"] = await self._assess_restaurant_capacity_risk(
                order_details["restaurant_id"], context
            )

        # Weather impact risk
        risks["weather_risk"] = await self._assess_weather_delivery_risk(context)

        # Historical performance risk
        risks["historical_risk"] = await self._assess_historical_performance_risk(
            order_details.get("restaurant_id"), context
        )

        # Distance and location risk
        risks["location_risk"] = await self._assess_location_delivery_risk(context)

        return risks

    async def _assess_time_based_risk(self, context: UserContext) -> Dict[str, Any]:
        """Assess delivery delay risk based on time of day"""
        current_hour = context.current_time.hour
        current_day = context.current_time.weekday()

        # Get historical delivery performance for this time
        performance_data = await self.db.fetch_one("""
            SELECT
                AVG(EXTRACT(EPOCH FROM (delivered_at - created_at))/60) as avg_delivery_time,
                COUNT(*) as order_count,
                COUNT(CASE WHEN delivered_at > estimated_delivery_time THEN 1 END) as late_orders
            FROM orders
            WHERE EXTRACT(HOUR FROM created_at) = $1
            AND EXTRACT(DOW FROM created_at) = $2
            AND status = 'completed'
            AND delivered_at IS NOT NULL
            AND created_at > NOW() - INTERVAL '30 days'
        """, current_hour, current_day)

        if performance_data and performance_data["order_count"] > 10:
            avg_time = performance_data["avg_delivery_time"] or 30
            late_rate = (performance_data["late_orders"] or 0) / performance_data["order_count"]

            # Calculate risk level
            if late_rate > 0.3 or avg_time > 45:
                risk_level = RiskLevel.HIGH
            elif late_rate > 0.15 or avg_time > 35:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
        else:
            # Default risk assessment for insufficient data
            if (current_hour in [12, 13, 18, 19]) and current_day < 5:  # Rush hours weekday
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            avg_time = 30
            late_rate = 0.2

        return {
            "risk_level": risk_level.value,
            "estimated_delivery_time": int(avg_time),
            "late_probability": round(late_rate, 3),
            "reason": f"Based on {current_hour}:00 {['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][current_day]} patterns"
        }

    async def _assess_restaurant_capacity_risk(
        self, restaurant_id: int, context: UserContext
    ) -> Dict[str, Any]:
        """Assess risk based on restaurant's current capacity"""
        # Get current active orders for restaurant
        current_load = await self.db.fetch_one("""
            SELECT COUNT(*) as active_orders,
                   AVG(EXTRACT(EPOCH FROM (NOW() - created_at))/60) as avg_prep_time
            FROM orders
            WHERE restaurant_id = $1
            AND status IN ('confirmed', 'preparing', 'ready')
            AND created_at > NOW() - INTERVAL '2 hours'
        """, restaurant_id)

        # Get restaurant's typical capacity
        capacity_data = await self.db.fetch_one("""
            SELECT
                AVG(order_count) as avg_hourly_orders,
                MAX(order_count) as max_hourly_orders
            FROM (
                SELECT
                    DATE_TRUNC('hour', created_at) as hour,
                    COUNT(*) as order_count
                FROM orders
                WHERE restaurant_id = $1
                AND created_at > NOW() - INTERVAL '7 days'
                GROUP BY DATE_TRUNC('hour', created_at)
            ) hourly_stats
        """, restaurant_id)

        active_orders = current_load["active_orders"] if current_load else 0
        avg_capacity = capacity_data["avg_hourly_orders"] if capacity_data else 10

        # Calculate capacity utilization
        capacity_utilization = active_orders / max(avg_capacity, 1)

        if capacity_utilization > 1.5:
            risk_level = RiskLevel.HIGH
            delay_estimate = 20
        elif capacity_utilization > 1.0:
            risk_level = RiskLevel.MEDIUM
            delay_estimate = 10
        else:
            risk_level = RiskLevel.LOW
            delay_estimate = 0

        return {
            "risk_level": risk_level.value,
            "capacity_utilization": round(capacity_utilization, 2),
            "active_orders": active_orders,
            "estimated_delay": delay_estimate,
            "recommendation": "Consider alternative restaurant" if risk_level == RiskLevel.HIGH else None
        }

    async def _assess_weather_delivery_risk(self, context: UserContext) -> Dict[str, Any]:
        """Assess weather impact on delivery"""
        # This would integrate with weather data from Context Intelligence Agent
        # For now, return basic assessment
        return {
            "risk_level": RiskLevel.LOW.value,
            "weather_impact": "normal",
            "estimated_delay": 0
        }

    async def _assess_historical_performance_risk(
        self, restaurant_id: Optional[int], context: UserContext
    ) -> Dict[str, Any]:
        """Assess risk based on restaurant's historical performance"""
        if not restaurant_id:
            return {"risk_level": RiskLevel.LOW.value, "data_available": False}

        # Get restaurant performance metrics
        performance = await self.db.fetch_one("""
            SELECT
                COUNT(*) as total_orders,
                AVG(rating) as avg_rating,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
                COUNT(CASE WHEN delivered_at > estimated_delivery_time THEN 1 END) as late_orders,
                AVG(EXTRACT(EPOCH FROM (delivered_at - created_at))/60) as avg_delivery_time
            FROM orders
            WHERE restaurant_id = $1
            AND created_at > NOW() - INTERVAL '30 days'
        """, restaurant_id)

        if not performance or performance["total_orders"] < 5:
            return {"risk_level": RiskLevel.MEDIUM.value, "reason": "insufficient_data"}

        # Calculate risk factors
        cancellation_rate = performance["cancelled_orders"] / performance["total_orders"]
        late_rate = (performance["late_orders"] or 0) / performance["total_orders"]
        avg_rating = performance["avg_rating"] or 3.0

        # Determine risk level
        if cancellation_rate > 0.1 or late_rate > 0.3 or avg_rating < 3.5:
            risk_level = RiskLevel.HIGH
        elif cancellation_rate > 0.05 or late_rate > 0.15 or avg_rating < 4.0:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return {
            "risk_level": risk_level.value,
            "metrics": {
                "cancellation_rate": round(cancellation_rate, 3),
                "late_delivery_rate": round(late_rate, 3),
                "avg_rating": round(avg_rating, 1),
                "avg_delivery_time": int(performance["avg_delivery_time"] or 30)
            },
            "total_orders": performance["total_orders"]
        }

    async def _assess_location_delivery_risk(self, context: UserContext) -> Dict[str, Any]:
        """Assess delivery risk based on location"""
        if not context.location:
            return {"risk_level": RiskLevel.HIGH.value, "reason": "no_location"}

        # Check if location is in known problem areas
        problem_areas = await self.db.fetch_all("""
            SELECT area_name, issue_type, severity
            FROM delivery_problem_areas
            WHERE ST_Contains(area, ST_Point($1, $2))
        """, context.location.get("longitude", 0), context.location.get("latitude", 0))

        if problem_areas:
            return {
                "risk_level": RiskLevel.MEDIUM.value,
                "issues": [dict(area) for area in problem_areas],
                "recommendation": "Verify delivery address"
            }

        return {"risk_level": RiskLevel.LOW.value}

    async def _validate_order_feasibility(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if order can be fulfilled successfully"""
        validations = {}

        # Menu item availability
        if order_details.get("items"):
            validations["menu_availability"] = await self._check_menu_availability(
                order_details["items"]
            )

        # Delivery area validation
        if order_details.get("delivery_address"):
            validations["delivery_area"] = await self._validate_delivery_area(
                order_details["delivery_address"], order_details.get("restaurant_id")
            )

        # Payment method validation
        if order_details.get("payment_method"):
            validations["payment"] = await self._validate_payment_method(
                order_details["payment_method"]
            )

        # Restaurant operating hours
        if order_details.get("restaurant_id"):
            validations["restaurant_hours"] = await self._check_restaurant_hours(
                order_details["restaurant_id"]
            )

        return validations

    async def _check_menu_availability(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if menu items are currently available"""
        unavailable_items = []

        for item in items:
            item_id = item.get("menu_item_id")
            if item_id:
                availability = await self.db.fetch_one("""
                    SELECT is_available, out_of_stock_reason
                    FROM menu_items
                    WHERE id = $1
                """, item_id)

                if not availability or not availability["is_available"]:
                    unavailable_items.append({
                        "item_id": item_id,
                        "reason": availability["out_of_stock_reason"] if availability else "item_not_found"
                    })

        return {
            "all_available": len(unavailable_items) == 0,
            "unavailable_items": unavailable_items,
            "validation_passed": len(unavailable_items) == 0
        }

    async def _validate_delivery_area(
        self, delivery_address: Dict[str, Any], restaurant_id: Optional[int]
    ) -> Dict[str, Any]:
        """Validate delivery to the specified address"""
        if not restaurant_id:
            return {"validation_passed": False, "reason": "no_restaurant"}

        # Check if restaurant delivers to this area
        delivers_to_area = await self.db.fetch_one("""
            SELECT * FROM restaurant_delivery_zones
            WHERE restaurant_id = $1
            AND ST_Contains(delivery_area, ST_Point($2, $3))
        """,
            restaurant_id,
            delivery_address.get("longitude", 0),
            delivery_address.get("latitude", 0)
        )

        return {
            "validation_passed": delivers_to_area is not None,
            "reason": "outside_delivery_area" if not delivers_to_area else None,
            "alternative_suggestion": "pickup" if not delivers_to_area else None
        }

    async def _validate_payment_method(self, payment_method: Dict[str, Any]) -> Dict[str, Any]:
        """Validate payment method"""
        # Basic payment validation logic
        method_type = payment_method.get("type")

        if method_type in ["card", "digital_wallet"]:
            return {"validation_passed": True}
        elif method_type == "cash":
            return {
                "validation_passed": True,
                "note": "Cash payments may have longer delivery times"
            }
        else:
            return {
                "validation_passed": False,
                "reason": "unsupported_payment_method"
            }

    async def _check_restaurant_hours(self, restaurant_id: int) -> Dict[str, Any]:
        """Check if restaurant is currently open"""
        current_time = datetime.now()
        current_day = current_time.weekday()
        current_time_only = current_time.time()

        hours = await self.db.fetch_one("""
            SELECT opens_at, closes_at, is_open_24h
            FROM restaurant_hours
            WHERE restaurant_id = $1 AND day_of_week = $2
        """, restaurant_id, current_day)

        if not hours:
            return {"validation_passed": False, "reason": "no_hours_data"}

        if hours["is_open_24h"]:
            return {"validation_passed": True, "note": "24h_operation"}

        opens_at = hours["opens_at"]
        closes_at = hours["closes_at"]

        # Handle overnight hours (e.g., 22:00 to 02:00)
        if closes_at < opens_at:
            is_open = current_time_only >= opens_at or current_time_only <= closes_at
        else:
            is_open = opens_at <= current_time_only <= closes_at

        return {
            "validation_passed": is_open,
            "reason": "restaurant_closed" if not is_open else None,
            "opens_at": opens_at.strftime("%H:%M") if not is_open and opens_at else None,
            "closes_at": closes_at.strftime("%H:%M")
        }

    async def _generate_prevention_strategies(
        self, risk_analysis: Dict[str, Any],
        validation_results: Dict[str, Any],
        context: UserContext
    ) -> List[Dict[str, Any]]:
        """Generate strategies to prevent identified problems"""
        strategies = []

        # Time-based strategies
        time_risk = risk_analysis.get("time_risk", {})
        if time_risk.get("risk_level") == RiskLevel.HIGH.value:
            strategies.append({
                "type": "time_adjustment",
                "recommendation": "Consider ordering for later delivery",
                "reason": f"Current delivery time: {time_risk.get('estimated_delivery_time')} minutes",
                "alternative_times": await self._suggest_better_delivery_times(context)
            })

        # Capacity-based strategies
        capacity_risk = risk_analysis.get("capacity_risk", {})
        if capacity_risk.get("risk_level") == RiskLevel.HIGH.value:
            strategies.append({
                "type": "restaurant_alternative",
                "recommendation": "Consider alternative restaurants",
                "reason": "High order volume at selected restaurant",
                "alternatives": await self._suggest_alternative_restaurants(context)
            })

        # Validation-based strategies
        menu_validation = validation_results.get("menu_availability", {})
        if not menu_validation.get("validation_passed", True):
            strategies.append({
                "type": "menu_substitution",
                "recommendation": "Some items unavailable, suggest alternatives",
                "unavailable_items": menu_validation.get("unavailable_items", []),
                "alternatives": await self._suggest_menu_alternatives(menu_validation)
            })

        return strategies

    def _calculate_overall_risk(self, risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall risk score from individual risk assessments"""
        risk_scores = []
        risk_factors = []

        for risk_type, risk_data in risk_analysis.items():
            if isinstance(risk_data, dict) and "risk_level" in risk_data:
                level = risk_data["risk_level"]
                if level == RiskLevel.HIGH.value:
                    risk_scores.append(0.8)
                elif level == RiskLevel.MEDIUM.value:
                    risk_scores.append(0.5)
                else:
                    risk_scores.append(0.2)
                risk_factors.append(risk_type)

        if risk_scores:
            avg_risk = sum(risk_scores) / len(risk_scores)
            max_risk = max(risk_scores)

            # Overall risk is weighted average of average and maximum
            overall_score = (avg_risk * 0.6) + (max_risk * 0.4)

            if overall_score > 0.7:
                overall_level = RiskLevel.HIGH
            elif overall_score > 0.4:
                overall_level = RiskLevel.MEDIUM
            else:
                overall_level = RiskLevel.LOW
        else:
            overall_score = 0.2
            overall_level = RiskLevel.LOW

        return {
            "score": round(overall_score, 3),
            "level": overall_level.value,
            "contributing_factors": risk_factors
        }

    async def _generate_problem_prevention_recommendations(
        self, risk_analysis: Dict[str, Any],
        validation_results: Dict[str, Any],
        overall_risk: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate final recommendations to prevent problems"""
        recommendations = []

        if overall_risk["level"] == RiskLevel.HIGH.value:
            recommendations.append({
                "priority": "high",
                "type": "risk_warning",
                "message": "High risk of delivery issues detected",
                "action": "review_order_details"
            })

        # Add specific recommendations based on individual risks
        for risk_type, risk_data in risk_analysis.items():
            if isinstance(risk_data, dict) and risk_data.get("risk_level") == RiskLevel.HIGH.value:
                if risk_type == "time_risk":
                    recommendations.append({
                        "priority": "medium",
                        "type": "delivery_delay_warning",
                        "message": f"Expected delivery time: {risk_data.get('estimated_delivery_time')} minutes",
                        "action": "confirm_acceptable"
                    })
                elif risk_type == "capacity_risk":
                    recommendations.append({
                        "priority": "medium",
                        "type": "restaurant_busy_warning",
                        "message": "Restaurant is currently busy",
                        "action": "suggest_alternatives"
                    })

        return recommendations

    async def _suggest_better_delivery_times(self, context: UserContext) -> List[str]:
        """Suggest better delivery times based on historical data"""
        # Implementation would analyze historical performance
        return ["30 minutes later", "1 hour later"]

    async def _suggest_alternative_restaurants(self, context: UserContext) -> List[Dict[str, Any]]:
        """Suggest alternative restaurants with better availability"""
        # Implementation would find similar restaurants with lower risk
        return []

    async def _suggest_menu_alternatives(self, menu_validation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest alternative menu items for unavailable ones"""
        # Implementation would find similar available items
        return []

    def _calculate_prevention_confidence(
        self, risk_analysis: Dict[str, Any], validation_results: Dict[str, Any]
    ) -> float:
        """Calculate confidence in problem prevention analysis"""
        # Base confidence on data availability
        data_points = 0
        total_possible = 0

        for risk_type, risk_data in risk_analysis.items():
            total_possible += 1
            if isinstance(risk_data, dict) and "risk_level" in risk_data:
                data_points += 1

        for validation_type, validation_data in validation_results.items():
            total_possible += 1
            if isinstance(validation_data, dict) and "validation_passed" in validation_data:
                data_points += 1

        return data_points / total_possible if total_possible > 0 else 0.5

    async def update_model(self, feedback: Dict[str, Any]) -> bool:
        """Update problem prevention model based on actual outcomes"""
        try:
            outcome_data = {
                "user_id": self.user_id,
                "predicted_risks": feedback.get("predicted_risks", {}),
                "actual_problems": feedback.get("actual_problems", []),
                "prevention_effectiveness": feedback.get("prevention_effectiveness"),
                "timestamp": datetime.now()
            }

            # Store outcome for model improvement
            await self.db.execute("""
                INSERT INTO problem_prevention_outcomes
                (user_id, predicted_risks, actual_problems, prevention_effectiveness, created_at)
                VALUES ($1, $2, $3, $4, $5)
            """,
                outcome_data["user_id"],
                json.dumps(outcome_data["predicted_risks"]),
                json.dumps(outcome_data["actual_problems"]),
                outcome_data["prevention_effectiveness"],
                outcome_data["timestamp"]
            )

            return True

        except Exception:
            return False