# backend/agents/preparation_time_agent.py
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from .base_agent import BaseAgent, AgentResult, AgentType, UserContext, AgentConfig
from backend.database import get_database

class PreparationComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class QueueStatus(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PreparationTimeAgent(BaseAgent):
    """
    Replaces Problem Prevention Agent with focus on preparation time optimization.
    Analyzes order complexity, kitchen capacity, and queue management.
    Provides accurate preparation time estimates and optimization strategies.
    """

    def __init__(self, user_id: str):
        super().__init__(AgentType.PREPARATION_TIME, user_id)
        self.db = get_database()
        self.base_preparation_times = {
            "proteins": {
                "Chicken": 8, "Egg": 5, "Paneer": 6, "Soya": 7, "Potato": 4
            },
            "sauces": {
                "Curry Special": 3, "Malai Masala": 4, "Curry Masala": 3,
                "Marinara": 2, "Yogurt/Raita": 1
            },
            "base_types": {
                "Rice": 2, "Naan": 3, "Sourdough": 1, "Ciabatta": 1, "White Bread": 1
            },
            "veggies": {
                "Onion": 2, "Tomato": 1, "Cucumber": 1, "Lettuce": 1, "Carrot": 2
            },
            "garnishes": {
                "Cilantro": 1, "Mint": 1, "Lemon": 1, "Chili": 1
            }
        }

    async def process(self, context: UserContext, **kwargs) -> AgentResult:
        """Analyze preparation time and provide optimization strategies"""
        start_time = datetime.now()

        try:
            order_details = kwargs.get("order_details", {})

            # Generate random queue position (1-50 orders)
            queue_position = random.randint(1, 50)

            # Analyze order complexity
            complexity_analysis = await self._analyze_order_complexity(order_details)

            # Assess kitchen capacity and queue status
            queue_analysis = await self._analyze_queue_status(queue_position)

            # Calculate preparation time
            preparation_time = await self._calculate_preparation_time(
                complexity_analysis, queue_analysis, context
            )

            # Generate optimization strategies
            optimization_strategies = await self._generate_optimization_strategies(
                complexity_analysis, queue_analysis, preparation_time
            )

            # Suggest refreshment drinks
            refreshment_suggestions = await self._suggest_refreshment_drinks(
                preparation_time, context
            )

            result_data = {
                "queue_position": queue_position,
                "complexity_analysis": complexity_analysis,
                "queue_analysis": queue_analysis,
                "preparation_time": preparation_time,
                "optimization_strategies": optimization_strategies,
                "refreshment_suggestions": refreshment_suggestions,
                "recommendations": await self._generate_preparation_recommendations(
                    complexity_analysis, queue_analysis, preparation_time
                )
            }

            # Calculate confidence based on data quality
            confidence = self._calculate_preparation_confidence(
                complexity_analysis, queue_analysis
            )

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

    async def _analyze_order_complexity(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the complexity of the order based on ingredients and preparation steps"""
        complexity_score = 0
        complexity_factors = []

        # Analyze protein complexity
        proteins = order_details.get("protein", [])
        for protein in proteins:
            base_time = self.base_preparation_times["proteins"].get(protein, 5)
            if base_time > 7:
                complexity_score += 2
                complexity_factors.append(f"Complex protein: {protein}")
            elif base_time > 5:
                complexity_score += 1
                complexity_factors.append(f"Moderate protein: {protein}")

        # Analyze sauce complexity
        sauces = order_details.get("sauce", [])
        for sauce in sauces:
            base_time = self.base_preparation_times["sauces"].get(sauce, 2)
            if base_time > 3:
                complexity_score += 1
                complexity_factors.append(f"Complex sauce: {sauce}")

        # Analyze base complexity
        base_type = order_details.get("baseType")
        if base_type:
            base_time = self.base_preparation_times["base_types"].get(base_type, 2)
            if base_time > 2:
                complexity_score += 1
                complexity_factors.append(f"Complex base: {base_type}")

        # Analyze vegetable count
        veggies = order_details.get("veggies", [])
        if len(veggies) > 3:
            complexity_score += 1
            complexity_factors.append(f"Many vegetables: {len(veggies)} items")
        elif len(veggies) > 1:
            complexity_score += 0.5
            complexity_factors.append(f"Multiple vegetables: {len(veggies)} items")

        # Analyze garnish count
        garnishes = order_details.get("garnishes", [])
        if len(garnishes) > 2:
            complexity_score += 0.5
            complexity_factors.append(f"Multiple garnishes: {len(garnishes)} items")

        # Determine overall complexity
        if complexity_score >= 4:
            complexity_level = PreparationComplexity.COMPLEX
        elif complexity_score >= 2:
            complexity_level = PreparationComplexity.MODERATE
        else:
            complexity_level = PreparationComplexity.SIMPLE

        return {
            "complexity_score": complexity_score,
            "complexity_level": complexity_level.value,
            "complexity_factors": complexity_factors,
            "ingredient_count": len(proteins) + len(sauces) + len(veggies) + len(garnishes) + (1 if base_type else 0)
        }

    async def _analyze_queue_status(self, queue_position: int) -> Dict[str, Any]:
        """Analyze the current queue status and its impact on preparation time"""
        if queue_position <= 5:
            queue_status = QueueStatus.LOW
            queue_multiplier = 1.0
            estimated_wait = queue_position * 2  # 2 minutes per order
        elif queue_position <= 15:
            queue_status = QueueStatus.MEDIUM
            queue_multiplier = 1.2
            estimated_wait = 10 + (queue_position - 5) * 1.5  # 1.5 minutes per order
        elif queue_position <= 30:
            queue_status = QueueStatus.HIGH
            queue_multiplier = 1.5
            estimated_wait = 25 + (queue_position - 15) * 1.2  # 1.2 minutes per order
        else:
            queue_status = QueueStatus.CRITICAL
            queue_multiplier = 2.0
            estimated_wait = 40 + (queue_position - 30) * 1.0  # 1 minute per order

        return {
            "queue_position": queue_position,
            "queue_status": queue_status.value,
            "queue_multiplier": queue_multiplier,
            "estimated_wait_minutes": int(estimated_wait),
            "kitchen_efficiency": self._calculate_kitchen_efficiency(queue_status)
        }

    def _calculate_kitchen_efficiency(self, queue_status: QueueStatus) -> float:
        """Calculate kitchen efficiency based on queue status"""
        efficiency_map = {
            QueueStatus.LOW: 1.0,
            QueueStatus.MEDIUM: 0.9,
            QueueStatus.HIGH: 0.8,
            QueueStatus.CRITICAL: 0.7
        }
        return efficiency_map.get(queue_status, 0.8)

    async def _calculate_preparation_time(
        self,
        complexity_analysis: Dict[str, Any],
        queue_analysis: Dict[str, Any],
        context: UserContext
    ) -> Dict[str, Any]:
        """Calculate total preparation time including queue wait and cooking time"""

        # Base preparation time based on complexity
        complexity_level = complexity_analysis["complexity_level"]
        base_prep_times = {
            PreparationComplexity.SIMPLE.value: 8,
            PreparationComplexity.MODERATE.value: 12,
            PreparationComplexity.COMPLEX.value: 18
        }

        base_preparation = base_prep_times.get(complexity_level, 10)

        # Apply queue multiplier
        queue_multiplier = queue_analysis["queue_multiplier"]
        adjusted_preparation = base_preparation * queue_multiplier

        # Add queue wait time
        queue_wait = queue_analysis["estimated_wait_minutes"]
        total_preparation = adjusted_preparation + queue_wait

        # Calculate ready time
        current_time = context.current_time or datetime.now()
        ready_time = current_time + timedelta(minutes=total_preparation)

        return {
            "base_preparation_minutes": base_preparation,
            "queue_wait_minutes": queue_wait,
            "adjusted_preparation_minutes": int(adjusted_preparation),
            "total_preparation_minutes": int(total_preparation),
            "ready_time": ready_time.isoformat(),
            "ready_time_formatted": ready_time.strftime("%H:%M"),
            "estimated_duration_formatted": f"{int(total_preparation//60):02d}:{int(total_preparation%60):02d}"
        }

    async def _generate_optimization_strategies(
        self,
        complexity_analysis: Dict[str, Any],
        queue_analysis: Dict[str, Any],
        preparation_time: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate strategies to optimize preparation time"""
        strategies = []

        # Queue-based strategies
        if queue_analysis["queue_status"] == QueueStatus.CRITICAL.value:
            strategies.append({
                "type": "queue_optimization",
                "priority": "high",
                "title": "High Queue Volume",
                "message": "Kitchen is very busy. Consider simpler order or wait time.",
                "suggestions": [
                    "Choose pre-made items",
                    "Select fewer customizations",
                    "Consider pickup instead of dine-in"
                ]
            })

        # Complexity-based strategies
        if complexity_analysis["complexity_level"] == PreparationComplexity.COMPLEX.value:
            strategies.append({
                "type": "complexity_reduction",
                "priority": "medium",
                "title": "Complex Order Detected",
                "message": "Your order has many customizations that increase preparation time.",
                "suggestions": [
                    "Reduce number of vegetables",
                    "Choose simpler sauce options",
                    "Select standard base options"
                ]
            })

        # Time-based strategies
        total_time = preparation_time["total_preparation_minutes"]
        if total_time > 25:
            strategies.append({
                "type": "time_management",
                "priority": "medium",
                "title": "Extended Preparation Time",
                "message": f"Your order will take approximately {total_time} minutes to prepare.",
                "suggestions": [
                    "Order a refreshment drink while waiting",
                    "Consider appetizer options",
                    "Check out our quick-bite menu"
                ]
            })

        return strategies

    async def _suggest_refreshment_drinks(
        self,
        preparation_time: Dict[str, Any],
        context: UserContext
    ) -> List[Dict[str, Any]]:
        """Suggest refreshment drinks based on preparation time and context"""
        total_time = preparation_time["total_preparation_minutes"]

        suggestions = []

        if total_time > 20:
            # Long wait time - suggest premium drinks
            suggestions.extend([
                {
                    "name": "Masala Chai",
                    "price": 3.50,
                    "reason": "Perfect warming drink for longer waits",
                    "preparation_time": "2 minutes",
                    "category": "hot_beverage"
                },
                {
                    "name": "Mango Lassi",
                    "price": 4.00,
                    "reason": "Refreshing yogurt drink to pass the time",
                    "preparation_time": "1 minute",
                    "category": "cold_beverage"
                }
            ])
        elif total_time > 15:
            # Medium wait time - suggest standard drinks
            suggestions.extend([
                {
                    "name": "Sweet Lassi",
                    "price": 3.00,
                    "reason": "Classic Indian yogurt drink",
                    "preparation_time": "1 minute",
                    "category": "cold_beverage"
                },
                {
                    "name": "Masala Tea",
                    "price": 2.50,
                    "reason": "Quick spiced tea preparation",
                    "preparation_time": "2 minutes",
                    "category": "hot_beverage"
                }
            ])
        else:
            # Short wait time - suggest quick drinks
            suggestions.extend([
                {
                    "name": "Water",
                    "price": 1.00,
                    "reason": "Stay hydrated while waiting",
                    "preparation_time": "Instant",
                    "category": "beverage"
                },
                {
                    "name": "Soda",
                    "price": 2.00,
                    "reason": "Quick refreshment option",
                    "preparation_time": "Instant",
                    "category": "beverage"
                }
            ])

        return suggestions

    async def _generate_preparation_recommendations(
        self,
        complexity_analysis: Dict[str, Any],
        queue_analysis: Dict[str, Any],
        preparation_time: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate final recommendations for preparation optimization"""
        recommendations = []

        # High priority recommendations
        if queue_analysis["queue_status"] == QueueStatus.CRITICAL.value:
            recommendations.append({
                "priority": "high",
                "type": "queue_warning",
                "message": f"Kitchen is very busy. You are #{queue_analysis['queue_position']} in queue.",
                "action": "consider_alternatives",
                "estimated_impact": "15-20 minutes additional wait"
            })

        if complexity_analysis["complexity_level"] == PreparationComplexity.COMPLEX.value:
            recommendations.append({
                "priority": "medium",
                "type": "complexity_notice",
                "message": "Complex order detected - multiple customizations",
                "action": "review_ingredients",
                "estimated_impact": "5-8 minutes additional preparation"
            })

        # Time-based recommendations
        total_time = preparation_time["total_preparation_minutes"]
        if total_time > 30:
            recommendations.append({
                "priority": "medium",
                "type": "extended_wait",
                "message": f"Total preparation time: {total_time} minutes",
                "action": "add_refreshment",
                "estimated_impact": "Consider ordering a drink while waiting"
            })

        return recommendations

    def _calculate_preparation_confidence(
        self,
        complexity_analysis: Dict[str, Any],
        queue_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence in preparation time analysis"""
        # Base confidence on data quality
        confidence = 0.8

        # Adjust based on complexity analysis quality
        if complexity_analysis.get("ingredient_count", 0) > 0:
            confidence += 0.1

        # Adjust based on queue analysis quality
        if queue_analysis.get("queue_position", 0) > 0:
            confidence += 0.1

        return min(confidence, 1.0)

    async def update_model(self, feedback: Dict[str, Any]) -> bool:
        """Update preparation time model based on actual outcomes"""
        try:
            outcome_data = {
                "user_id": self.user_id,
                "predicted_preparation_time": feedback.get("predicted_preparation_time", 0),
                "actual_preparation_time": feedback.get("actual_preparation_time", 0),
                "queue_position": feedback.get("queue_position", 0),
                "complexity_level": feedback.get("complexity_level", "simple"),
                "customer_satisfaction": feedback.get("customer_satisfaction", 0),
                "timestamp": datetime.now()
            }

            # Store outcome for model improvement
            await self.db.execute("""
                INSERT INTO preparation_time_outcomes
                (user_id, predicted_preparation_time, actual_preparation_time,
                 queue_position, complexity_level, customer_satisfaction, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                outcome_data["user_id"],
                outcome_data["predicted_preparation_time"],
                outcome_data["actual_preparation_time"],
                outcome_data["queue_position"],
                outcome_data["complexity_level"],
                outcome_data["customer_satisfaction"],
                outcome_data["timestamp"]
            )

            return True

        except Exception:
            return False