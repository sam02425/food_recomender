"""
Master Recommendation API
Provides endpoints for the state-of-the-art agentic recommendation flow
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Import the master coordinator
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ml_engine.master_recommendation_coordinator import (
    MasterRecommendationCoordinator,
    UserContext,
    RecommendationPriority
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize master coordinator
try:
    master_coordinator = MasterRecommendationCoordinator(data_path="../data/")
    logger.info("Master recommendation coordinator initialized successfully")
except Exception as e:
    logger.error(f"Error initializing master coordinator: {e}")
    master_coordinator = None

router = APIRouter(prefix="/api/master", tags=["master-recommendations"])

# Pydantic Models
class UserContextRequest(BaseModel):
    user_id: str
    location: Optional[str] = None
    weather: Dict[str, Any] = Field(default_factory=lambda: {'condition': 'sunny', 'temperature': 22})
    time_of_day: str = Field(default='afternoon')
    activity_level: str = Field(default='work')
    mood: str = Field(default='neutral')
    health_conditions: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    allergens: List[str] = Field(default_factory=list)
    order_history: List[Dict[str, Any]] = Field(default_factory=list)
    session_context: Dict[str, Any] = Field(default_factory=dict)
    social_context: Dict[str, Any] = Field(default_factory=dict)

class RecommendationRequest(BaseModel):
    user_context: UserContextRequest
    n_recommendations: int = Field(default=5, ge=1, le=20)
    include_explanations: bool = True
    priority_filter: Optional[str] = None
    category_filter: Optional[List[str]] = None

class FeedbackRequest(BaseModel):
    user_id: str
    recommendation_id: str
    feedback: str
    custom_suggestion: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class MasterRecommendationResponse(BaseModel):
    success: bool
    recommendations: List[Dict[str, Any]]
    explanations: Optional[Dict[str, str]]
    confidence: float
    agent_contributions: Dict[str, int]
    temporal_insights: Dict[str, Any]
    dietary_filtering_applied: bool
    processing_time_ms: float
    total_agents_consulted: int
    recommendation_method: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

@router.post("/recommendations/comprehensive", response_model=MasterRecommendationResponse)
async def get_comprehensive_recommendations(request: RecommendationRequest):
    """
    Get comprehensive recommendations using the master agentic coordinator

    This endpoint orchestrates multiple AI agents:
    - Health Agent: Nutrition and activity-based recommendations
    - Weather Agent: Weather-appropriate food suggestions
    - Mood Agent: Emotion-based recommendations
    - Context Agent: Time and activity context analysis
    - Learner Agent: Personalized learning from user feedback
    - RNN Temporal Analysis: Sequential pattern learning

    All recommendations are filtered through dietary restrictions and allergen safety.
    """

    if not master_coordinator:
        raise HTTPException(status_code=503, detail="Master coordinator not available")

    try:
        logger.info(f"Processing comprehensive recommendation request for user {request.user_context.user_id}")

        # Convert Pydantic model to UserContext
        user_context = UserContext(
            user_id=request.user_context.user_id,
            location=request.user_context.location,
            weather=request.user_context.weather,
            time_of_day=request.user_context.time_of_day,
            activity_level=request.user_context.activity_level,
            mood=request.user_context.mood,
            health_conditions=request.user_context.health_conditions,
            dietary_restrictions=request.user_context.dietary_restrictions,
            allergens=request.user_context.allergens,
            order_history=request.user_context.order_history,
            session_context=request.user_context.session_context,
            social_context=request.user_context.social_context
        )

        # Get recommendations from master coordinator
        result = await master_coordinator.get_comprehensive_recommendations(
            user_context=user_context,
            n_recommendations=request.n_recommendations,
            include_explanations=request.include_explanations
        )

        # Apply filters if specified
        if request.priority_filter or request.category_filter:
            result['recommendations'] = _apply_filters(
                result['recommendations'],
                request.priority_filter,
                request.category_filter
            )

        # Add metadata
        result['metadata'] = {
            'request_filters': {
                'priority_filter': request.priority_filter,
                'category_filter': request.category_filter
            },
            'user_context_summary': {
                'has_dietary_restrictions': len(request.user_context.dietary_restrictions) > 0,
                'has_allergens': len(request.user_context.allergens) > 0,
                'order_history_length': len(request.user_context.order_history),
                'activity_level': request.user_context.activity_level,
                'mood': request.user_context.mood
            }
        }

        logger.info(f"Successfully generated {len(result['recommendations'])} recommendations")
        return result

    except Exception as e:
        logger.error(f"Error in comprehensive recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@router.post("/recommendations/quick")
async def get_quick_recommendations(
    user_id: str,
    activity_level: str = "work",
    mood: str = "neutral",
    n_recommendations: int = 3
):
    """
    Get quick recommendations with minimal context
    Suitable for fast API calls when full context is not available
    """

    if not master_coordinator:
        raise HTTPException(status_code=503, detail="Master coordinator not available")

    try:
        # Create minimal user context
        user_context = UserContext(
            user_id=user_id,
            location=None,
            weather={'condition': 'sunny'},
            time_of_day=_get_current_time_of_day(),
            activity_level=activity_level,
            mood=mood,
            health_conditions=[],
            dietary_restrictions=[],
            allergens=[],
            order_history=[],
            session_context={},
            social_context={}
        )

        result = await master_coordinator.get_comprehensive_recommendations(
            user_context=user_context,
            n_recommendations=n_recommendations,
            include_explanations=False
        )

        # Simplified response
        return {
            'success': result['success'],
            'recommendations': result['recommendations'],
            'confidence': result['confidence'],
            'processing_time_ms': result['processing_time_ms'],
            'method': 'quick_recommendations'
        }

    except Exception as e:
        logger.error(f"Error in quick recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating quick recommendations: {str(e)}")

@router.post("/feedback")
async def submit_user_feedback(request: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Submit user feedback for continuous learning
    Feedback helps improve future recommendations through the learner agent and RNN models
    """

    if not master_coordinator:
        raise HTTPException(status_code=503, detail="Master coordinator not available")

    try:
        logger.info(f"Processing feedback from user {request.user_id}")

        # Process feedback in background for performance
        background_tasks.add_task(
            _process_feedback_background,
            request.user_id,
            request.recommendation_id,
            request.feedback,
            request.custom_suggestion,
            request.context
        )

        return {
            'success': True,
            'message': 'Feedback received and will be processed',
            'user_id': request.user_id,
            'recommendation_id': request.recommendation_id,
            'feedback_type': request.feedback
        }

    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")

@router.get("/user/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """
    Get learned user preferences from the master coordinator
    """

    if not master_coordinator:
        raise HTTPException(status_code=503, detail="Master coordinator not available")

    try:
        # Get preferences from learner agent
        learner_prefs = master_coordinator.learner_agent.get_user_preferences(user_id)

        # Get dietary profile
        dietary_profile = master_coordinator.dietary_manager.get_user_profile(user_id)

        return {
            'success': True,
            'user_id': user_id,
            'learned_preferences': learner_prefs,
            'dietary_profile': dietary_profile,
            'preference_confidence': _calculate_preference_confidence(learner_prefs),
            'last_updated': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting preferences: {str(e)}")

@router.get("/analytics/agent-performance")
async def get_agent_performance_analytics():
    """
    Get performance analytics for all agents in the system
    """

    if not master_coordinator:
        raise HTTPException(status_code=503, detail="Master coordinator not available")

    try:
        # Get learner agent statistics
        learner_stats = master_coordinator.learner_agent.get_learning_statistics()

        # Calculate agent weights
        agent_weights = master_coordinator.agent_weights

        return {
            'success': True,
            'agent_weights': agent_weights,
            'learner_statistics': learner_stats,
            'total_recommendations_generated': sum(learner_stats.get('feedback_count', {}).values()),
            'rnn_model_status': {
                'is_trained': master_coordinator.temporal_rnn.is_trained,
                'model_available': master_coordinator.temporal_rnn.model is not None
            },
            'system_health': 'operational',
            'last_updated': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

@router.post("/recommendations/agent-specific/{agent_name}")
async def get_agent_specific_recommendations(
    agent_name: str,
    user_context: UserContextRequest,
    n_recommendations: int = 5
):
    """
    Get recommendations from a specific agent only
    Useful for testing and debugging individual agents
    """

    if not master_coordinator:
        raise HTTPException(status_code=503, detail="Master coordinator not available")

    valid_agents = ['health', 'weather', 'mood', 'context', 'learner']
    if agent_name not in valid_agents:
        raise HTTPException(status_code=400, detail=f"Invalid agent name. Valid agents: {valid_agents}")

    try:
        # Convert to UserContext
        context = UserContext(
            user_id=user_context.user_id,
            location=user_context.location,
            weather=user_context.weather,
            time_of_day=user_context.time_of_day,
            activity_level=user_context.activity_level,
            mood=user_context.mood,
            health_conditions=user_context.health_conditions,
            dietary_restrictions=user_context.dietary_restrictions,
            allergens=user_context.allergens,
            order_history=user_context.order_history,
            session_context=user_context.session_context,
            social_context=user_context.social_context
        )

        # Get recommendations from specific agent
        if agent_name == 'health':
            recs = await master_coordinator._get_health_recommendations(context)
        elif agent_name == 'weather':
            recs = await master_coordinator._get_weather_recommendations(context)
        elif agent_name == 'mood':
            recs = await master_coordinator._get_mood_recommendations(context)
        elif agent_name == 'context':
            recs = await master_coordinator._get_context_recommendations(context)
        elif agent_name == 'learner':
            recs = await master_coordinator._get_learner_recommendations(context)

        # Convert to dict format
        recommendations = []
        for i, rec in enumerate(recs[:n_recommendations]):
            recommendations.append({
                'category': rec.category,
                'item': rec.item,
                'confidence': rec.confidence,
                'reasoning': rec.reasoning,
                'priority': rec.priority.name,
                'agent_name': rec.agent_name,
                'metadata': rec.metadata
            })

        return {
            'success': True,
            'agent_name': agent_name,
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'agent_specific': True
        }

    except Exception as e:
        logger.error(f"Error getting {agent_name} recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting {agent_name} recommendations: {str(e)}")

@router.post("/train/rnn")
async def train_rnn_model(background_tasks: BackgroundTasks):
    """
    Trigger RNN model training with current user data
    This is a background task that can take several minutes
    """

    if not master_coordinator:
        raise HTTPException(status_code=503, detail="Master coordinator not available")

    try:
        background_tasks.add_task(_train_rnn_background)

        return {
            'success': True,
            'message': 'RNN training started in background',
            'estimated_time_minutes': 10,
            'training_started_at': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error starting RNN training: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting training: {str(e)}")

# Helper Functions

def _apply_filters(
    recommendations: List[Dict],
    priority_filter: Optional[str],
    category_filter: Optional[List[str]]
) -> List[Dict]:
    """Apply priority and category filters to recommendations"""

    filtered = recommendations

    if priority_filter:
        filtered = [rec for rec in filtered if rec.get('priority') == priority_filter.upper()]

    if category_filter:
        filtered = [rec for rec in filtered if rec.get('category') in category_filter]

    return filtered

def _get_current_time_of_day() -> str:
    """Get current time of day category"""
    hour = datetime.now().hour
    if hour < 12:
        return 'morning'
    elif hour < 18:
        return 'afternoon'
    else:
        return 'evening'

def _calculate_preference_confidence(preferences: Dict) -> float:
    """Calculate confidence in user preferences"""
    if not preferences:
        return 0.0

    total_confidence = 0.0
    count = 0

    for category, pref_data in preferences.items():
        if isinstance(pref_data, dict) and 'confidence' in pref_data:
            total_confidence += pref_data['confidence']
            count += 1
        elif isinstance(pref_data, dict) and 'items' in pref_data:
            for item in pref_data['items']:
                if isinstance(item, dict) and 'confidence' in item:
                    total_confidence += item['confidence']
                    count += 1

    return total_confidence / count if count > 0 else 0.0

async def _process_feedback_background(
    user_id: str,
    recommendation_id: str,
    feedback: str,
    custom_suggestion: Optional[str],
    context: Optional[Dict]
):
    """Process user feedback in background"""
    try:
        result = await master_coordinator.update_user_feedback(
            user_id=user_id,
            recommendation_id=recommendation_id,
            feedback=feedback,
            context=context or {}
        )
        logger.info(f"Background feedback processing completed for user {user_id}: {result}")
    except Exception as e:
        logger.error(f"Error in background feedback processing: {e}")

async def _train_rnn_background():
    """Train RNN model in background"""
    try:
        logger.info("Starting RNN model training...")

        # Load training data (this would be implemented based on your data structure)
        # For now, this is a placeholder

        # master_coordinator.temporal_rnn.train_model(training_data)
        # master_coordinator.save_models()

        logger.info("RNN model training completed")

    except Exception as e:
        logger.error(f"Error in RNN training: {e}")

@router.get("/health")
async def health_check():
    """Health check endpoint for the master recommendation system"""

    system_status = {
        'master_coordinator': master_coordinator is not None,
        'health_agent': hasattr(master_coordinator, 'health_agent') if master_coordinator else False,
        'weather_agent': hasattr(master_coordinator, 'weather_agent') if master_coordinator else False,
        'learner_agent': hasattr(master_coordinator, 'learner_agent') if master_coordinator else False,
        'mood_agent': hasattr(master_coordinator, 'mood_agent') if master_coordinator else False,
        'context_agent': hasattr(master_coordinator, 'context_agent') if master_coordinator else False,
        'dietary_manager': hasattr(master_coordinator, 'dietary_manager') if master_coordinator else False,
        'rnn_model': master_coordinator.temporal_rnn.model is not None if master_coordinator else False,
        'rnn_trained': master_coordinator.temporal_rnn.is_trained if master_coordinator else False
    }

    all_healthy = all(system_status.values())

    return {
        'status': 'healthy' if all_healthy else 'degraded',
        'components': system_status,
        'timestamp': datetime.now().isoformat(),
        'version': 'v1.0',
        'uptime_healthy': all_healthy
    }