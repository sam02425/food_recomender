"""
FastAPI endpoints for ML-based recommendations
Integrates with existing agent system and provides ML-powered recommendations
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Traditional agents - simplified implementation for ML integration
class HealthRecommenderAgent:
    def __init__(self, data_path=None):
        self.data_path = data_path

    def get_recommendation(self, activity_level="work", customer_phone=None, **kwargs):
        # Simple logic based on activity level
        protein_map = {
            "gym": "Chicken",
            "active": "Egg",
            "work": "Paneer/Indian Cheese",
            "study": "Soya",
            "chilling": "Potato"
        }
        return {
            "protein": protein_map.get(activity_level, "Chicken"),
            "reason": f"Recommended for {activity_level} activity",
            "confidence": 0.8
        }

class WeatherRecommenderAgent:
    def __init__(self, data_path=None):
        self.data_path = data_path

    def get_recommendation(self, customer_phone=None, **kwargs):
        # Simple weather-based recommendation
        return {
            "sauce": "Curry Special",
            "base": "Rice Bowl",
            "reason": "Good for current weather conditions",
            "confidence": 0.7
        }

class LearnerAgent:
    def __init__(self, data_path=None):
        self.data_path = data_path
        self.feedback_data = []

    def learn_from_feedback(self, feedback_type, feedback, custom_suggestion=None, customer_phone=None, **kwargs):
        # Simple feedback storage
        self.feedback_data.append({
            "type": feedback_type,
            "feedback": feedback,
            "custom": custom_suggestion,
            "timestamp": datetime.now().isoformat()
        })
        return True

# Import ML components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ml_engine.ml_recommendation_api import MLRecommendationEngine
from ml_engine.dietary_restrictions import DietaryRestrictionsManager

# Initialize ML engine with proper data path
try:
    ml_engine = MLRecommendationEngine(data_path="../data/")
    dietary_manager = DietaryRestrictionsManager()
    logger.info("ML engine and dietary manager initialized successfully")
except Exception as e:
    logger.error(f"Error initializing ML engine: {e}")
    ml_engine = None
    dietary_manager = None

# Initialize traditional agents
health_agent = HealthRecommenderAgent()
weather_agent = WeatherRecommenderAgent()
learner_agent = LearnerAgent()

router = APIRouter(prefix="/api/ml", tags=["ml-recommendations"])

# Pydantic models
class RecommendationRequest(BaseModel):
    user_id: str
    context: Dict[str, Any]
    n_recommendations: Optional[int] = 5
    include_explanations: Optional[bool] = True

class FeedbackRequest(BaseModel):
    user_id: str
    feedback_type: str  # 'explicit', 'implicit', 'text'
    feedback_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = {}

class MLRecommendationResponse(BaseModel):
    success: bool
    recommendations: List[Dict[str, Any]]
    explanations: Optional[Dict[str, str]]
    confidence: float
    sources: Dict[str, int]
    traditional_agent_recs: Optional[Dict[str, Any]]
    timestamp: str

class FeedbackResponse(BaseModel):
    success: bool
    user_id: str
    processed_feedback: Dict[str, Any]
    updated_preferences: Optional[Dict[str, Any]]
    timestamp: str

@router.post("/recommendations", response_model=MLRecommendationResponse)
async def get_ml_recommendations(request: RecommendationRequest):
    """Get ML-powered recommendations with traditional agent fallback"""

    try:
        logger.info(f"Getting ML recommendations for user {request.user_id}")

        # Get ML recommendations
        ml_results = await ml_engine.get_comprehensive_recommendations(
            user_id=request.user_id,
            context=request.context,
            n_recommendations=request.n_recommendations
        )

        # Get traditional agent recommendations for comparison/fallback
        traditional_recs = await _get_traditional_agent_recommendations(
            request.user_id,
            request.context
        )

        # Combine and enhance recommendations
        if ml_results.get('success'):
            # ML recommendations successful
            final_recs = ml_results['recommendations']
            explanations = ml_results.get('explanations', {}) if request.include_explanations else None
            confidence = ml_results.get('confidence', 0.5)
            sources = ml_results.get('sources', {})

            # Add traditional recommendations as fallback
            if len(final_recs) < request.n_recommendations:
                traditional_items = _extract_traditional_items(traditional_recs)
                final_recs.extend(traditional_items[:request.n_recommendations - len(final_recs)])

        else:
            # ML failed, use traditional recommendations
            logger.warning("ML recommendations failed, using traditional agents")
            final_recs = _extract_traditional_items(traditional_recs)
            explanations = _generate_traditional_explanations(traditional_recs) if request.include_explanations else None
            confidence = 0.7  # Traditional agents have good confidence
            sources = {"traditional_agents": len(final_recs)}

        # Apply dietary restrictions filtering
        if dietary_manager:
            original_count = len(final_recs)
            final_recs = dietary_manager.filter_recommendations(request.user_id, final_recs)

            # Update sources and confidence if items were filtered
            if len(final_recs) < original_count:
                sources['dietary_filtered'] = original_count - len(final_recs)
                logger.info(f"Filtered {original_count - len(final_recs)} recommendations due to dietary restrictions")

        return MLRecommendationResponse(
            success=True,
            recommendations=final_recs[:request.n_recommendations],
            explanations=explanations,
            confidence=confidence,
            sources=sources,
            traditional_agent_recs=traditional_recs,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error getting ML recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback", response_model=FeedbackResponse)
async def process_ml_feedback(request: FeedbackRequest, background_tasks: BackgroundTasks):
    """Process user feedback and update ML models"""

    try:
        logger.info(f"Processing ML feedback for user {request.user_id}")

        # Process feedback with ML engine
        ml_feedback_result = await ml_engine.process_user_feedback(
            user_id=request.user_id,
            feedback_data=request.feedback_data
        )

        # Also update traditional agents in background
        background_tasks.add_task(
            _update_traditional_agents,
            request.user_id,
            request.feedback_data,
            request.context
        )

        # Get updated user preferences
        updated_preferences = None
        if ml_feedback_result.get('success'):
            try:
                updated_preferences = ml_engine.preference_learner.get_user_preferences(request.user_id)
            except Exception as e:
                logger.warning(f"Could not get updated preferences: {e}")

        return FeedbackResponse(
            success=ml_feedback_result.get('success', False),
            user_id=request.user_id,
            processed_feedback=ml_feedback_result,
            updated_preferences=updated_preferences,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error processing ML feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/hybrid/{user_id}")
async def get_hybrid_recommendations(
    user_id: str,
    activity_level: Optional[str] = "work",
    mood: Optional[str] = "neutral",
    weather_condition: Optional[str] = "sunny",
    time_of_day: Optional[str] = "afternoon",
    n_recommendations: Optional[int] = 5
):
    """Get hybrid recommendations combining ML and traditional agents"""

    try:
        context = {
            'activity_level': activity_level,
            'mood': mood,
            'weather': {'condition': weather_condition},
            'time_of_day': time_of_day
        }

        # Get recommendations from both systems
        ml_task = ml_engine.get_comprehensive_recommendations(user_id, context, n_recommendations)
        traditional_task = _get_traditional_agent_recommendations(user_id, context)

        ml_results, traditional_results = await asyncio.gather(ml_task, traditional_task)

        # Combine results intelligently
        hybrid_recs = _create_hybrid_recommendations(ml_results, traditional_results, n_recommendations)

        # Apply dietary restrictions filtering
        if dietary_manager:
            original_count = len(hybrid_recs)
            hybrid_recs = dietary_manager.filter_recommendations(user_id, hybrid_recs)
            logger.info(f"Hybrid recommendations: Filtered {original_count - len(hybrid_recs)} items due to dietary restrictions")

        return {
            "success": True,
            "user_id": user_id,
            "hybrid_recommendations": hybrid_recs,
            "ml_results": ml_results,
            "traditional_results": traditional_results,
            "combination_method": "weighted_merge",
            "dietary_filtered": len(hybrid_recs) < n_recommendations,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting hybrid recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/preferences/{user_id}")
async def get_user_ml_preferences(user_id: str):
    """Get user's learned preferences from ML models"""

    try:
        # Get preferences from ML engine
        ml_preferences = ml_engine.preference_learner.get_user_preferences(user_id)

        # Get collaborative filtering insights
        cf_recommendations = ml_engine.collaborative_filter.get_user_recommendations(
            user_id=hash(user_id) % 10000,
            n_recommendations=10
        )

        # Get similar users
        similar_users = ml_engine.preference_learner._get_similar_users(user_id)

        # Get traditional agent preferences for comparison
        traditional_preferences = learner_agent.get_customer_preferences(user_id)

        return {
            "success": True,
            "user_id": user_id,
            "ml_preferences": ml_preferences,
            "collaborative_filtering": {
                "recommendations": cf_recommendations,
                "similar_users": similar_users
            },
            "traditional_preferences": traditional_preferences,
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting user ML preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/insights")
async def get_ml_model_insights():
    """Get insights about ML model performance and status"""

    try:
        ml_insights = await ml_engine.get_model_insights()

        # Get traditional agent insights
        traditional_insights = {
            "health_agent": {
                "data_loaded": bool(health_agent.health_data),
                "total_recommendations": len(health_agent.health_data.get("activity_recommendations", {}))
            },
            "weather_agent": {
                "data_loaded": bool(weather_agent.weather_data),
                "total_recommendations": len(weather_agent.weather_data.get("condition_recommendations", {}))
            },
            "learner_agent": {
                "models": learner_agent.learning_data.get("models", {}),
                "total_customers": len(learner_agent.learning_data.get("customer_preferences", {})),
                "feedback_history_size": len(learner_agent.learning_data.get("feedback_history", []))
            }
        }

        return {
            "success": True,
            "ml_models": ml_insights,
            "traditional_agents": traditional_insights,
            "system_status": "operational",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting model insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/retrain")
async def retrain_ml_models(background_tasks: BackgroundTasks):
    """Trigger retraining of ML models"""

    try:
        # Start retraining in background
        background_tasks.add_task(_retrain_models_background)

        return {
            "success": True,
            "message": "Model retraining started in background",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error starting model retraining: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/feedback")
async def analyze_text_feedback(
    feedback_text: str,
    order_details: Optional[Dict[str, Any]] = {}
):
    """Analyze text feedback using NLP"""

    try:
        analysis = ml_engine.nlp_analyzer.analyze_feedback(feedback_text, order_details)

        return {
            "success": True,
            "feedback_text": feedback_text,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error analyzing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def _get_traditional_agent_recommendations(user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Get recommendations from traditional agents"""

    try:
        activity_level = context.get('activity_level', 'work')
        mood = context.get('mood', 'neutral')
        weather_data = context.get('weather', {'condition': 'sunny'})
        time_of_day = context.get('time_of_day', 'afternoon')

        # Get health recommendations
        health_recs = health_agent.get_recommendations(
            activity_level=activity_level,
            customer_id=user_id,
            mood=mood
        )

        # Get weather recommendations
        weather_recs = weather_agent.get_recommendations(
            weather_data=weather_data,
            time_of_day=time_of_day,
            customer_id=user_id,
            mood=mood
        )

        return {
            "health_recommendations": health_recs,
            "weather_recommendations": weather_recs
        }

    except Exception as e:
        logger.error(f"Error getting traditional recommendations: {e}")
        return {}

def _extract_traditional_items(traditional_recs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract items from traditional agent recommendations"""

    items = []

    # Extract from health recommendations
    health_data = traditional_recs.get("health_recommendations", {})
    for category in ['proteins', 'sauces', 'base_types', 'veggies']:
        for item in health_data.get(category, []):
            items.append({
                'category': category.rstrip('s'),  # Remove plural
                'item': item,
                'predicted_rating': 4.0,
                'confidence': 0.7,
                'source': 'health_agent',
                'reason': health_data.get('reasoning', 'Health-based recommendation')
            })

    # Extract from weather recommendations
    weather_data = traditional_recs.get("weather_recommendations", {})
    for category in ['proteins', 'sauces', 'base_types']:
        for item in weather_data.get(category, []):
            items.append({
                'category': category.rstrip('s'),
                'item': item,
                'predicted_rating': 4.0,
                'confidence': 0.7,
                'source': 'weather_agent',
                'reason': weather_data.get('reasoning', 'Weather-based recommendation')
            })

    return items

def _generate_traditional_explanations(traditional_recs: Dict[str, Any]) -> Dict[str, str]:
    """Generate explanations for traditional recommendations"""

    explanations = {}

    health_reasoning = traditional_recs.get("health_recommendations", {}).get("reasoning", "")
    weather_reasoning = traditional_recs.get("weather_recommendations", {}).get("reasoning", "")

    explanations['overview'] = f"Recommendations based on your activity level and current weather. {health_reasoning} {weather_reasoning}"

    return explanations

def _create_hybrid_recommendations(
    ml_results: Dict[str, Any],
    traditional_results: Dict[str, Any],
    n_recommendations: int
) -> List[Dict[str, Any]]:
    """Create hybrid recommendations from ML and traditional sources"""

    hybrid_recs = []

    # Start with ML recommendations if available
    if ml_results.get('success') and ml_results.get('recommendations'):
        ml_recs = ml_results['recommendations']
        # Give ML recommendations higher weight
        for rec in ml_recs:
            rec['hybrid_score'] = rec.get('predicted_rating', 4.0) * 1.2  # 20% boost for ML
            hybrid_recs.append(rec)

    # Add traditional recommendations
    traditional_items = _extract_traditional_items(traditional_results)
    for rec in traditional_items:
        rec['hybrid_score'] = rec.get('predicted_rating', 4.0) * 1.0  # No boost
        hybrid_recs.append(rec)

    # Remove duplicates and sort by hybrid score
    unique_recs = {}
    for rec in hybrid_recs:
        key = f"{rec.get('category')}_{rec.get('item')}"
        if key not in unique_recs or rec['hybrid_score'] > unique_recs[key]['hybrid_score']:
            unique_recs[key] = rec

    final_recs = list(unique_recs.values())
    final_recs.sort(key=lambda x: x['hybrid_score'], reverse=True)

    return final_recs[:n_recommendations]

async def _update_traditional_agents(user_id: str, feedback_data: Dict[str, Any], context: Dict[str, Any]):
    """Update traditional agents with feedback (background task)"""

    try:
        # Update learner agent
        feedback_type = feedback_data.get('feedback_type', 'implicit')

        if feedback_type == 'explicit':
            # Process explicit ratings
            ratings = feedback_data.get('explicit_ratings', {})
            for category, rating in ratings.items():
                learner_agent.process_feedback(
                    recommendation_type=category,
                    feedback='accept' if rating >= 4 else 'ignore',
                    customer_id=user_id,
                    context=context
                )

        elif feedback_type == 'implicit':
            # Process selections as implicit feedback
            selections = feedback_data.get('selections', {})
            learner_agent.process_feedback(
                recommendation_type='health',
                feedback='accept',
                customer_id=user_id,
                context={'current_selections': selections, **context}
            )

        logger.info(f"Updated traditional agents for user {user_id}")

    except Exception as e:
        logger.error(f"Error updating traditional agents: {e}")

async def _retrain_models_background():
    """Retrain ML models in background"""

    try:
        logger.info("Starting background model retraining...")
        result = await ml_engine.retrain_models()
        logger.info(f"Background retraining completed: {result}")

    except Exception as e:
        logger.error(f"Error in background retraining: {e}")