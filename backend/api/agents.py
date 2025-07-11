# backend/api/agents.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid

from pydantic import BaseModel, Field
from src.agents.orchestrator import AgentOrchestrator
from src.agents.base_agent import UserContext, AgentType
from backend.database import get_database
from backend.app.api.auth import get_current_user

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])
security = HTTPBearer()

# Request/Response Models
class LocationModel(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None

class DeviceInfoModel(BaseModel):
    user_agent: str
    screen_size: str
    platform: str

class UserContextModel(BaseModel):
    user_id: str
    session_id: str
    current_time: datetime
    location: Optional[LocationModel] = None
    device_info: Optional[DeviceInfoModel] = None

class RecommendationRequestModel(BaseModel):
    user_context: UserContextModel
    request_type: str = Field(default="full_recommendation",
                             description="Type of recommendation request")
    order_details: Optional[Dict[str, Any]] = None
    current_menu: Optional[List[Dict[str, Any]]] = None

class AgentFeedbackModel(BaseModel):
    agent_type: str
    feedback: Dict[str, Any]

class OrderOutcomeModel(BaseModel):
    user_id: str
    order_id: str
    delivered_on_time: bool
    actual_delivery_time: int
    predicted_delivery_time: int
    customer_satisfaction: int = Field(ge=1, le=5)
    problems_encountered: List[str] = []
    agent_recommendations_used: List[str] = []

class ExperimentTrialModel(BaseModel):
    experiment_id: str
    user_id: str
    trial_type: str = Field(description="baseline or adaptive")
    start_time: datetime
    end_time: datetime
    task_completion_time: int
    nasa_tlx_scores: Dict[str, int]
    sus_score: int = Field(ge=0, le=100)
    user_satisfaction: int = Field(ge=1, le=7)
    recommendations_accepted: int
    errors_made: int
    navigation_steps: int

# Store active orchestrators (in production, use Redis or similar)
active_orchestrators: Dict[str, AgentOrchestrator] = {}

def get_orchestrator(user_id: str) -> AgentOrchestrator:
    """Get or create agent orchestrator for user"""
    if user_id not in active_orchestrators:
        active_orchestrators[user_id] = AgentOrchestrator(user_id)
    return active_orchestrators[user_id]

def convert_to_user_context(context_model: UserContextModel) -> UserContext:
    """Convert API model to internal UserContext"""
    return UserContext(
        user_id=context_model.user_id,
        session_id=context_model.session_id,
        current_time=context_model.current_time,
        location=context_model.location.dict() if context_model.location else None,
        device_info=context_model.device_info.dict() if context_model.device_info else None
    )

@router.post("/recommendations")
async def get_recommendations(
    request: RecommendationRequestModel,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    Get personalized recommendations from the agent system
    """
    try:
        # Validate request type
        valid_types = ["full_recommendation", "quick_recommendation", "risk_assessment", "context_only"]
        if request.request_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid request type. Must be one of: {valid_types}")

        # Get orchestrator for user
        orchestrator = get_orchestrator(request.user_context.user_id)

        # Convert to internal format
        user_context = convert_to_user_context(request.user_context)

        # Process recommendation request
        result = await orchestrator.process_recommendation_request(
            context=user_context,
            request_type=request.request_type,
            order_details=request.order_details,
            current_menu=request.current_menu
        )

        # Log request in background
        background_tasks.add_task(
            log_recommendation_request,
            request.user_context.user_id,
            request.request_type,
            result
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.post("/feedback")
async def submit_feedback(
    feedback: AgentFeedbackModel,
    current_user = Depends(get_current_user)
):
    """
    Submit feedback to improve agent performance
    """
    try:
        # Get orchestrator for user
        user_id = current_user["user_id"]
        orchestrator = get_orchestrator(user_id)

        # Convert agent type string to enum
        try:
            agent_type = AgentType(feedback.agent_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid agent type: {feedback.agent_type}")

        # Submit feedback to specific agent
        success = await orchestrator.update_agent_feedback(agent_type, feedback.feedback)

        return {"success": success}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@router.get("/performance/{user_id}")
async def get_performance_metrics(
    user_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get agent performance metrics for a user
    """
    try:
        # Check if user can access these metrics
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(status_code=403, detail="Admin access required")
        orchestrator = get_orchestrator(user_id)
        metrics = await orchestrator.get_performance_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.get("/health")
async def get_health_status(current_user = Depends(get_current_user)):
    """
    Get health status of all agent systems (admin only)
    """
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    try:
        temp_orchestrator = AgentOrchestrator("health_check")
        health_status = await temp_orchestrator.health_check()
        health_status["system"] = {
            "active_orchestrators": len(active_orchestrators),
            "timestamp": datetime.now().isoformat()
        }
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.post("/order-outcome")
async def report_order_outcome(
    outcome: OrderOutcomeModel,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    Report order outcome for agent learning
    """
    try:
        # Verify user can report this outcome
        if current_user["user_id"] != outcome.user_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")

        # Process outcome in background
        background_tasks.add_task(
            process_order_outcome,
            outcome.dict()
        )

        return {"success": True, "message": "Order outcome recorded"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to report order outcome: {str(e)}")

@router.post("/experiments/trial-data")
async def submit_experiment_data(
    trial_data: ExperimentTrialModel,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    Submit experiment trial data for research
    """
    try:
        # Validate trial type
        if trial_data.trial_type not in ["baseline", "adaptive"]:
            raise HTTPException(status_code=400, detail="Invalid trial type. Must be 'baseline' or 'adaptive'")

        # Store experiment data in background
        background_tasks.add_task(
            store_experiment_data,
            trial_data.dict()
        )

        return {"success": True, "message": "Experiment data recorded"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit experiment data: {str(e)}")

@router.get("/users/{user_id}/patterns")
async def get_user_patterns(
    user_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get user's ordering patterns summary
    """
    try:
        # Check access permissions
        if current_user["user_id"] != user_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")

        orchestrator = get_orchestrator(user_id)

        # Create temporary context to get pattern analysis
        temp_context = UserContext(
            user_id=user_id,
            session_id=str(uuid.uuid4()),
            current_time=datetime.now()
        )

        # Get preference learning results
        preference_agent = orchestrator.agents[AgentType.PREFERENCE_LEARNING]
        result = await preference_agent.process(temp_context)

        if result.success:
            return result.data.get("behavioral_patterns", {})
        else:
            return {"error": "Unable to analyze patterns", "data_sufficient": False}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user patterns: {str(e)}")

@router.put("/users/{user_id}/preferences")
async def update_user_preferences(
    user_id: str,
    preferences: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """
    Update user preferences manually
    """
    try:
        # Check access permissions
        if current_user["user_id"] != user_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")

        db = get_database()

        # Update user preferences in database
        await db.execute("""
            INSERT INTO user_preferences (user_id, preferences, updated_at)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id)
            DO UPDATE SET preferences = $2, updated_at = $3
        """, user_id, json.dumps(preferences), datetime.now())

        return {"success": True, "message": "Preferences updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

# Background task functions
async def log_recommendation_request(
    user_id: str,
    request_type: str,
    result: Dict[str, Any]
):
    """Log recommendation request for analytics"""
    try:
        db = get_database()
        await db.execute("""
            INSERT INTO recommendation_logs
            (user_id, request_type, success, execution_time_ms, agents_called, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
        """,
            user_id,
            request_type,
            result.get("success", False),
            result.get("orchestrator_metadata", {}).get("execution_time_ms", 0),
            json.dumps(result.get("agents_called", [])),
            datetime.now()
        )
    except Exception as e:
        print(f"Failed to log recommendation request: {e}")

async def process_order_outcome(outcome_data: Dict[str, Any]):
    """Process order outcome for agent learning"""
    try:
        db = get_database()

        # Store outcome data
        await db.execute("""
            INSERT INTO order_outcomes
            (user_id, order_id, delivered_on_time, actual_delivery_time,
             predicted_delivery_time, customer_satisfaction, problems_encountered,
             agent_recommendations_used, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
            outcome_data["user_id"],
            outcome_data["order_id"],
            outcome_data["delivered_on_time"],
            outcome_data["actual_delivery_time"],
            outcome_data["predicted_delivery_time"],
            outcome_data["customer_satisfaction"],
            json.dumps(outcome_data["problems_encountered"]),
            json.dumps(outcome_data["agent_recommendations_used"]),
            datetime.now()
        )

        # Update agent models with this feedback
        user_id = outcome_data["user_id"]
        if user_id in active_orchestrators:
            orchestrator = active_orchestrators[user_id]

            # Submit feedback to relevant agents
            feedback = {
                "type": "order_outcome",
                "actual_delivery_time": outcome_data["actual_delivery_time"],
                "predicted_delivery_time": outcome_data["predicted_delivery_time"],
                "customer_satisfaction": outcome_data["customer_satisfaction"],
                "problems_encountered": outcome_data["problems_encountered"]
            }

            await orchestrator.update_agent_feedback(AgentType.PROBLEM_PREVENTION, feedback)
            await orchestrator.update_agent_feedback(AgentType.CONTEXT_INTELLIGENCE, feedback)

    except Exception as e:
        print(f"Failed to process order outcome: {e}")

async def store_experiment_data(trial_data: Dict[str, Any]):
    """Store experiment trial data"""
    try:
        db = get_database()
        await db.execute("""
            INSERT INTO experiment_trials
            (experiment_id, user_id, trial_type, start_time, end_time,
             task_completion_time, nasa_tlx_scores, sus_score, user_satisfaction,
             recommendations_accepted, errors_made, navigation_steps, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        """,
            trial_data["experiment_id"],
            trial_data["user_id"],
            trial_data["trial_type"],
            trial_data["start_time"],
            trial_data["end_time"],
            trial_data["task_completion_time"],
            json.dumps(trial_data["nasa_tlx_scores"]),
            trial_data["sus_score"],
            trial_data["user_satisfaction"],
            trial_data["recommendations_accepted"],
            trial_data["errors_made"],
            trial_data["navigation_steps"],
            datetime.now()
        )
    except Exception as e:
        print(f"Failed to store experiment data: {e}")

# Cleanup function for orchestrators (should be called periodically)
async def cleanup_inactive_orchestrators():
    """Remove orchestrators for inactive users"""
    current_time = datetime.now()
    to_remove = []

    for user_id, orchestrator in active_orchestrators.items():
        # Remove orchestrators inactive for more than 1 hour
        if (current_time - orchestrator.created_at).total_seconds() > 3600:
            if orchestrator.total_requests == 0:  # No activity
                to_remove.append(user_id)

    for user_id in to_remove:
        del active_orchestrators[user_id]

    print(f"Cleaned up {len(to_remove)} inactive orchestrators")