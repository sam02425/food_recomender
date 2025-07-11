# backend/agents/orchestrator.py
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent, AgentResult, AgentType, UserContext
from .context_intelligence_agent import ContextIntelligenceAgent
from .preference_learning_agent import PreferenceLearningAgent
from .preparation_time_agent import PreparationTimeAgent
from backend.database import get_database

class AgentOrchestrator:
    """
    Updated orchestrator for the simplified 3-agent architecture.
    Replaces the original 7-agent system with focused, high-impact agents.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = get_database()

        # Initialize the three core agents
        self.agents: Dict[AgentType, BaseAgent] = {
            AgentType.CONTEXT_INTELLIGENCE: ContextIntelligenceAgent(user_id),
            AgentType.PREFERENCE_LEARNING: PreferenceLearningAgent(user_id),
            AgentType.PREPARATION_TIME: PreparationTimeAgent(user_id)
        }

        # Orchestrator state
        self.session_id = None
        self.created_at = datetime.now()
        self.total_requests = 0
        self.performance_metrics = {
            "total_execution_time": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "agent_performance": {agent_type.value: {"calls": 0, "avg_time": 0} for agent_type in AgentType}
        }

    async def process_recommendation_request(
        self,
        context: UserContext,
        request_type: str = "full_recommendation",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main entry point for processing recommendation requests.
        Coordinates all three agents to provide comprehensive recommendations.
        """
        start_time = datetime.now()
        self.total_requests += 1

        try:
            # Create session if needed
            if not self.session_id:
                self.session_id = await self._create_session(context)

            # Process request based on type
            if request_type == "full_recommendation":
                result = await self._process_full_recommendation(context, **kwargs)
            elif request_type == "quick_recommendation":
                result = await self._process_quick_recommendation(context, **kwargs)
            elif request_type == "risk_assessment":
                result = await self._process_risk_assessment(context, **kwargs)
            elif request_type == "context_only":
                result = await self._process_context_only(context, **kwargs)
            else:
                result = await self._process_full_recommendation(context, **kwargs)

            # Log successful request
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.performance_metrics["successful_requests"] += 1
            self.performance_metrics["total_execution_time"] += execution_time

            # Add orchestrator metadata
            result["orchestrator_metadata"] = {
                "session_id": self.session_id,
                "request_type": request_type,
                "execution_time_ms": int(execution_time),
                "agents_called": result.get("agents_called", []),
                "total_requests": self.total_requests
            }

            # Log request for analysis
            await self._log_request(context, request_type, result, execution_time)

            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.performance_metrics["failed_requests"] += 1

            error_result = {
                "success": False,
                "error": str(e),
                "orchestrator_metadata": {
                    "session_id": self.session_id,
                    "request_type": request_type,
                    "execution_time_ms": int(execution_time),
                    "error_occurred": True
                }
            }

            await self._log_error(context, request_type, str(e), execution_time)
            return error_result

    async def _process_full_recommendation(
        self, context: UserContext, **kwargs
    ) -> Dict[str, Any]:
        """
        Process full recommendation using all three agents.
        This is the main recommendation flow.
        """
        # Run all agents in parallel for efficiency
        tasks = {
            "context": self.agents[AgentType.CONTEXT_INTELLIGENCE].process(context, **kwargs),
            "preferences": self.agents[AgentType.PREFERENCE_LEARNING].process(context, **kwargs),
            "preparation": self.agents[AgentType.PREPARATION_TIME].process(context, **kwargs)
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        agent_results = {}

        # Process results and handle any exceptions
        for i, (agent_name, task) in enumerate(tasks.items()):
            if isinstance(results[i], Exception):
                agent_results[agent_name] = AgentResult(
                    agent_type=list(AgentType)[i],
                    success=False,
                    data={"error": str(results[i])},
                    confidence=0.0,
                    execution_time_ms=0
                )
            else:
                agent_results[agent_name] = results[i]

        # Combine results intelligently
        combined_recommendations = await self._combine_agent_results(agent_results, context)

        return {
            "success": True,
            "recommendation_type": "full",
            "agent_results": {
                name: {
                    "success": result.success,
                    "data": result.data,
                    "confidence": result.confidence,
                    "execution_time_ms": result.execution_time_ms
                } for name, result in agent_results.items()
            },
            "combined_recommendations": combined_recommendations,
            "agents_called": [AgentType.CONTEXT_INTELLIGENCE.value,
                            AgentType.PREFERENCE_LEARNING.value,
                            AgentType.PROBLEM_PREVENTION.value]
        }

    async def _process_quick_recommendation(
        self, context: UserContext, **kwargs
    ) -> Dict[str, Any]:
        """
        Quick recommendation using only preference learning for speed.
        Used when user wants fast reorder or simple recommendations.
        """
        preference_result = await self.agents[AgentType.PREFERENCE_LEARNING].process(context, **kwargs)

        # Get minimal context for basic validation
        context_result = await self.agents[AgentType.CONTEXT_INTELLIGENCE].process(context, **kwargs)

        quick_recommendations = await self._generate_quick_recommendations(
            preference_result, context_result, context
        )

        return {
            "success": True,
            "recommendation_type": "quick",
            "recommendations": quick_recommendations,
            "agents_called": [AgentType.PREFERENCE_LEARNING.value, AgentType.CONTEXT_INTELLIGENCE.value]
        }

    async def _process_preparation_assessment(
        self, context: UserContext, **kwargs
    ) -> Dict[str, Any]:
        """
        Preparation time assessment only - used during order validation.
        """
        preparation_result = await self.agents[AgentType.PREPARATION_TIME].process(context, **kwargs)
        context_result = await self.agents[AgentType.CONTEXT_INTELLIGENCE].process(context, **kwargs)

        preparation_summary = await self._generate_preparation_summary(preparation_result, context_result)

        return {
            "success": True,
            "recommendation_type": "preparation_assessment",
            "preparation_analysis": preparation_summary,
            "agents_called": [AgentType.PREPARATION_TIME.value, AgentType.CONTEXT_INTELLIGENCE.value]
        }

    async def _process_context_only(
        self, context: UserContext, **kwargs
    ) -> Dict[str, Any]:
        """
        Context intelligence only - used for initial app loading.
        """
        context_result = await self.agents[AgentType.CONTEXT_INTELLIGENCE].process(context, **kwargs)

        return {
            "success": True,
            "recommendation_type": "context_only",
            "context_data": context_result.data if context_result.success else {},
            "agents_called": [AgentType.CONTEXT_INTELLIGENCE.value]
        }

    async def _combine_agent_results(
        self, agent_results: Dict[str, AgentResult], context: UserContext
    ) -> Dict[str, Any]:
        """
        Intelligently combine results from all agents into unified recommendations.
        """
        combined = {
            "primary_recommendations": [],
            "contextual_warnings": [],
            "personalization_insights": [],
            "risk_factors": [],
            "overall_confidence": 0.0
        }

        # Extract data from successful agents
        context_data = agent_results["context"].data if agent_results["context"].success else {}
        preference_data = agent_results["preferences"].data if agent_results["preferences"].success else {}
        preparation_data = agent_results["preparation"].data if agent_results["preparation"].success else {}

        # Combine contextual information
        if context_data.get("recommendations"):
            combined["contextual_warnings"].extend(context_data["recommendations"])

        # Add preference-based recommendations
        if preference_data.get("recommendations"):
            combined["primary_recommendations"].extend(preference_data["recommendations"])

        # Add personalization insights
        if preference_data.get("behavioral_patterns", {}).get("insights"):
            combined["personalization_insights"] = preference_data["behavioral_patterns"]["insights"]

        # Add preparation time factors and optimization strategies
        if preparation_data.get("recommendations"):
            combined["preparation_factors"].extend(preparation_data["recommendations"])

        # Generate unified recommendations
        unified_recommendations = await self._generate_unified_recommendations(
            context_data, preference_data, preparation_data, context
        )
        combined["unified_recommendations"] = unified_recommendations

        # Calculate overall confidence
        confidences = [
            result.confidence for result in agent_results.values() if result.success
        ]
        combined["overall_confidence"] = sum(confidences) / len(confidences) if confidences else 0.0

        return combined

    async def _generate_unified_recommendations(
        self,
        context_data: Dict[str, Any],
        preference_data: Dict[str, Any],
        preparation_data: Dict[str, Any],
        context: UserContext
    ) -> List[Dict[str, Any]]:
        """
        Generate unified recommendations that consider all agent inputs.
        """
        recommendations = []

        # Check for high-priority preparation time warnings first
        preparation_time = preparation_data.get("preparation_time", {})
        if preparation_time.get("total_preparation_minutes", 0) > 25:
            recommendations.append({
                "type": "warning",
                "priority": "high",
                "title": "Extended Preparation Time",
                "message": f"Your order will take {preparation_time.get('total_preparation_minutes')} minutes to prepare",
                "action": "consider_alternatives",
                "source": "preparation_time"
            })

        # Add context-aware recommendations
        time_context = context_data.get("time", {})
        if time_context.get("urgency") == "high":
            recommendations.append({
                "type": "time_suggestion",
                "priority": "medium",
                "title": f"Peak {time_context.get('meal_period', '')} Time",
                "message": "Consider quick reorder or expect longer delivery",
                "action": "show_quick_options",
                "source": "context_intelligence"
            })

        # Add personalized suggestions
        behavioral_patterns = preference_data.get("behavioral_patterns", {})
        if behavioral_patterns.get("data_sufficient"):
            patterns = behavioral_patterns.get("patterns", {})

            # Reorder suggestion for decisive users
            ordering_behavior = patterns.get("ordering_behavior", {})
            if ordering_behavior.get("reorder_tendency", 0) > 0.4:
                recommendations.append({
                    "type": "reorder_suggestion",
                    "priority": "medium",
                    "title": "Quick Reorder",
                    "message": "Order your usual favorites?",
                    "action": "show_recent_orders",
                    "source": "preference_learning"
                })

            # Cuisine-based suggestions
            cuisine_prefs = patterns.get("cuisine_preferences", {})
            if cuisine_prefs.get("preferred_cuisines"):
                top_cuisine = list(cuisine_prefs["preferred_cuisines"].keys())[0]
                recommendations.append({
                    "type": "cuisine_suggestion",
                    "priority": "low",
                    "title": f"Your Favorite: {top_cuisine}",
                    "message": f"Browse {top_cuisine} restaurants",
                    "action": f"filter_by_cuisine_{top_cuisine.lower()}",
                    "source": "preference_learning"
                })

        # Sort by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)

        return recommendations[:5]  # Limit to top 5 recommendations

    async def _generate_quick_recommendations(
        self,
        preference_result: AgentResult,
        context_result: AgentResult,
        context: UserContext
    ) -> List[Dict[str, Any]]:
        """Generate quick recommendations for fast ordering scenarios"""
        recommendations = []

        if preference_result.success:
            patterns = preference_result.data.get("behavioral_patterns", {}).get("patterns", {})

            # Quick reorder option
            ordering_behavior = patterns.get("ordering_behavior", {})
            if ordering_behavior.get("reorder_tendency", 0) > 0.3:
                recommendations.append({
                    "type": "quick_reorder",
                    "title": "Reorder Recent Favorite",
                    "action": "show_recent_orders",
                    "estimated_time": "30 seconds"
                })

            # Cuisine shortcuts
            cuisine_prefs = patterns.get("cuisine_preferences", {})
            if cuisine_prefs.get("preferred_cuisines"):
                for cuisine in list(cuisine_prefs["preferred_cuisines"].keys())[:2]:
                    recommendations.append({
                        "type": "cuisine_shortcut",
                        "title": f"Browse {cuisine}",
                        "action": f"filter_cuisine_{cuisine.lower()}",
                        "estimated_time": "2 minutes"
                    })

        return recommendations

    async def _generate_preparation_summary(
        self,
        preparation_result: AgentResult,
        context_result: AgentResult
    ) -> Dict[str, Any]:
        """Generate preparation time summary for order validation"""
        if not preparation_result.success:
            return {"preparation_time": "unknown", "message": "Unable to assess preparation time"}

        preparation_time = preparation_result.data.get("preparation_time", {})
        complexity_analysis = preparation_result.data.get("complexity_analysis", {})

        return {
            "total_preparation_minutes": preparation_time.get("total_preparation_minutes", 0),
            "ready_time": preparation_time.get("ready_time_formatted", "Unknown"),
            "complexity_level": complexity_analysis.get("complexity_level", "simple"),
            "queue_position": preparation_result.data.get("queue_position", 0),
            "recommendations": preparation_result.data.get("recommendations", []),
            "estimated_impact": self._assess_preparation_impact(preparation_time)
        }

    def _assess_preparation_impact(self, preparation_time: Dict[str, Any]) -> str:
        """Assess the likely impact of preparation time"""
        total_minutes = preparation_time.get("total_preparation_minutes", 0)

        if total_minutes > 30:
            return "Extended wait time - consider refreshment options"
        elif total_minutes > 20:
            return "Moderate wait time - order will be ready shortly"
        else:
            return "Quick preparation - order will be ready soon"

    async def _create_session(self, context: UserContext) -> str:
        """Create a new orchestrator session"""
        session_data = {
            "user_id": self.user_id,
            "created_at": datetime.now(),
            "context": {
                "location": context.location,
                "device_info": context.device_info
            }
        }

        # Store session in database
        session_id = await self.db.fetch_val("""
            INSERT INTO orchestrator_sessions (user_id, session_data, created_at)
            VALUES ($1, $2, $3)
            RETURNING id
        """, self.user_id, json.dumps(session_data, default=str), session_data["created_at"])

        return str(session_id)

    async def _log_request(
        self,
        context: UserContext,
        request_type: str,
        result: Dict[str, Any],
        execution_time: float
    ) -> None:
        """Log request for performance analysis and debugging"""
        try:
            await self.db.execute("""
                INSERT INTO orchestrator_logs
                (session_id, user_id, request_type, execution_time_ms, success, result_summary)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                self.session_id,
                self.user_id,
                request_type,
                int(execution_time),
                result.get("success", False),
                json.dumps({
                    "agents_called": result.get("agents_called", []),
                    "recommendation_count": len(result.get("combined_recommendations", {}).get("primary_recommendations", [])),
                    "risk_level": result.get("risk_analysis", {}).get("overall_risk_level", "unknown")
                })
            )
        except Exception:
            # Don't fail the request if logging fails
            pass

    async def _log_error(
        self,
        context: UserContext,
        request_type: str,
        error: str,
        execution_time: float
    ) -> None:
        """Log error for debugging"""
        try:
            await self.db.execute("""
                INSERT INTO orchestrator_errors
                (session_id, user_id, request_type, error_message, execution_time_ms)
                VALUES ($1, $2, $3, $4, $5)
            """,
                self.session_id,
                self.user_id,
                request_type,
                error[:500],  # Truncate long error messages
                int(execution_time)
            )
        except Exception:
            pass

    async def update_agent_feedback(
        self,
        agent_type: AgentType,
        feedback: Dict[str, Any]
    ) -> bool:
        """Update specific agent based on feedback"""
        if agent_type in self.agents:
            return await self.agents[agent_type].update_model(feedback)
        return False

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics"""
        # Update agent-specific metrics
        for agent_type, agent in self.agents.items():
            health = await agent.get_health_status()
            self.performance_metrics["agent_performance"][agent_type.value].update(health)

        return {
            **self.performance_metrics,
            "session_info": {
                "session_id": self.session_id,
                "created_at": self.created_at.isoformat(),
                "total_requests": self.total_requests,
                "avg_execution_time": (
                    self.performance_metrics["total_execution_time"] / max(self.total_requests, 1)
                )
            }
        }

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of orchestrator and all agents"""
        health_status = {
            "orchestrator": {
                "status": "healthy",
                "session_id": self.session_id,
                "uptime_seconds": (datetime.now() - self.created_at).total_seconds()
            },
            "agents": {}
        }

        # Check each agent
        for agent_type, agent in self.agents.items():
            try:
                agent_health = await agent.get_health_status()
                health_status["agents"][agent_type.value] = {
                    "status": "healthy" if agent.is_active else "inactive",
                    **agent_health
                }
            except Exception as e:
                health_status["agents"][agent_type.value] = {
                    "status": "error",
                    "error": str(e)
                }

        # Overall status
        agent_statuses = [
            agent_info.get("status") for agent_info in health_status["agents"].values()
        ]

        if all(status == "healthy" for status in agent_statuses):
            health_status["overall_status"] = "healthy"
        elif any(status == "error" for status in agent_statuses):
            health_status["overall_status"] = "degraded"
        else:
            health_status["overall_status"] = "partial"

        return health_status