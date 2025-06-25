"""
ML Integration Agent - Bridges ML recommendations with existing agent system
Provides seamless integration between traditional rule-based agents and ML models
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json

# Import existing agents
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.Health_Ag import HealthRecommenderAgent
from agents.Weather_Ag import WeatherRecommenderAgent
from agents.Learner_Ag import LearnerAgent
from agents.Face_Ag import EnhancedFaceRecognitionAgent
from agents.Record_Ag import RecordKeeperAgent

# Import ML components
from ml_engine.ml_recommendation_api import MLRecommendationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLIntegrationAgent:
    """
    Integration agent that coordinates between ML models and traditional agents
    Provides unified recommendation interface with fallback mechanisms
    """

    def __init__(self, data_path: str = "data/"):
        self.data_path = data_path

        # Initialize ML engine
        logger.info("Initializing ML Integration Agent...")
        self.ml_engine = MLRecommendationEngine(data_path)

        # Initialize traditional agents
        self.health_agent = HealthRecommenderAgent()
        self.weather_agent = WeatherRecommenderAgent()
        self.learner_agent = LearnerAgent(f"{data_path}learning_data.json")
        self.face_agent = EnhancedFaceRecognitionAgent()
        self.record_agent = RecordKeeperAgent()

        # Configuration
        self.use_ml_primary = True  # Use ML as primary, agents as fallback
        self.ml_confidence_threshold = 0.6  # Minimum confidence for ML recommendations
        self.hybrid_weight_ml = 0.7  # Weight for ML vs traditional in hybrid mode
        self.hybrid_weight_traditional = 0.3

        logger.info("ML Integration Agent initialized successfully")

    async def get_unified_recommendations(
        self,
        user_id: str,
        context: Dict[str, Any],
        mode: str = "hybrid",  # "ml_only", "traditional_only", "hybrid"
        n_recommendations: int = 5
    ) -> Dict[str, Any]:
        """
        Get unified recommendations using the specified mode

        Args:
            user_id: User identifier
            context: Request context (activity, mood, weather, etc.)
            mode: Recommendation mode
            n_recommendations: Number of recommendations to return

        Returns:
            Unified recommendation response
        """

        try:
            logger.info(f"Getting unified recommendations for user {user_id} in {mode} mode")

            if mode == "ml_only":
                return await self._get_ml_only_recommendations(user_id, context, n_recommendations)

            elif mode == "traditional_only":
                return await self._get_traditional_only_recommendations(user_id, context, n_recommendations)

            elif mode == "hybrid":
                return await self._get_hybrid_recommendations(user_id, context, n_recommendations)

            else:
                raise ValueError(f"Unknown recommendation mode: {mode}")

        except Exception as e:
            logger.error(f"Error getting unified recommendations: {e}")
            # Fallback to traditional agents
            return await self._get_traditional_only_recommendations(user_id, context, n_recommendations)

    async def _get_ml_only_recommendations(
        self,
        user_id: str,
        context: Dict[str, Any],
        n_recommendations: int
    ) -> Dict[str, Any]:
        """Get recommendations using only ML models"""

        try:
            ml_results = await self.ml_engine.get_comprehensive_recommendations(
                user_id=user_id,
                context=context,
                n_recommendations=n_recommendations
            )

            if ml_results.get('success') and ml_results.get('confidence', 0) >= self.ml_confidence_threshold:
                return {
                    'success': True,
                    'mode': 'ml_only',
                    'recommendations': ml_results['recommendations'],
                    'explanations': ml_results.get('explanations', {}),
                    'confidence': ml_results['confidence'],
                    'sources': ml_results.get('sources', {}),
                    'ml_details': ml_results,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # ML confidence too low, fall back to traditional
                logger.warning(f"ML confidence {ml_results.get('confidence', 0)} below threshold, falling back")
                return await self._get_traditional_only_recommendations(user_id, context, n_recommendations)

        except Exception as e:
            logger.error(f"Error in ML-only recommendations: {e}")
            return await self._get_traditional_only_recommendations(user_id, context, n_recommendations)

    async def _get_traditional_only_recommendations(
        self,
        user_id: str,
        context: Dict[str, Any],
        n_recommendations: int
    ) -> Dict[str, Any]:
        """Get recommendations using only traditional agents"""

        try:
            # Extract context parameters
            activity_level = context.get('activity_level', 'work')
            mood = context.get('mood', 'neutral')
            weather_data = context.get('weather', {'condition': 'sunny'})
            time_of_day = context.get('time_of_day', 'afternoon')
            customer_history = context.get('customer_history', [])

            # Get recommendations from traditional agents
            health_recs = self.health_agent.get_recommendations(
                activity_level=activity_level,
                customer_id=user_id,
                previous_orders=customer_history,
                mood=mood
            )

            weather_recs = self.weather_agent.get_recommendations(
                weather_data=weather_data,
                time_of_day=time_of_day,
                customer_id=user_id,
                mood=mood,
                customer_history=customer_history
            )

            # Get customer preferences from record keeper
            customer_prefs = self.record_agent.get_recommended_items(
                phone_number=user_id,
                activity_level=activity_level
            )

            # Combine traditional recommendations
            combined_recs = self._combine_traditional_recommendations(
                health_recs, weather_recs, customer_prefs, n_recommendations
            )

            return {
                'success': True,
                'mode': 'traditional_only',
                'recommendations': combined_recs,
                'explanations': self._generate_traditional_explanations(health_recs, weather_recs),
                'confidence': 0.8,  # Traditional agents have good confidence
                'sources': {
                    'health_agent': len(health_recs.get('proteins', [])),
                    'weather_agent': len(weather_recs.get('proteins', [])),
                    'customer_history': len(customer_prefs.get('proteins', []))
                },
                'traditional_details': {
                    'health_recommendations': health_recs,
                    'weather_recommendations': weather_recs,
                    'customer_preferences': customer_prefs
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in traditional-only recommendations: {e}")
            return self._get_fallback_recommendations(n_recommendations)

    async def _get_hybrid_recommendations(
        self,
        user_id: str,
        context: Dict[str, Any],
        n_recommendations: int
    ) -> Dict[str, Any]:
        """Get hybrid recommendations combining ML and traditional approaches"""

        try:
            # Get recommendations from both systems in parallel
            ml_task = self.ml_engine.get_comprehensive_recommendations(
                user_id=user_id,
                context=context,
                n_recommendations=n_recommendations
            )

            traditional_task = self._get_traditional_only_recommendations(
                user_id, context, n_recommendations
            )

            ml_results, traditional_results = await asyncio.gather(
                ml_task, traditional_task, return_exceptions=True
            )

            # Handle exceptions
            if isinstance(ml_results, Exception):
                logger.warning(f"ML recommendations failed: {ml_results}")
                ml_results = {'success': False}

            if isinstance(traditional_results, Exception):
                logger.warning(f"Traditional recommendations failed: {traditional_results}")
                traditional_results = {'success': False}

            # Combine results intelligently
            hybrid_recs = self._create_intelligent_hybrid(
                ml_results, traditional_results, n_recommendations
            )

            # Calculate combined confidence
            ml_confidence = ml_results.get('confidence', 0) if ml_results.get('success') else 0
            traditional_confidence = traditional_results.get('confidence', 0) if traditional_results.get('success') else 0

            combined_confidence = (
                ml_confidence * self.hybrid_weight_ml +
                traditional_confidence * self.hybrid_weight_traditional
            )

            return {
                'success': True,
                'mode': 'hybrid',
                'recommendations': hybrid_recs,
                'explanations': self._generate_hybrid_explanations(ml_results, traditional_results),
                'confidence': combined_confidence,
                'sources': {
                    'ml_models': ml_results.get('sources', {}) if ml_results.get('success') else {},
                    'traditional_agents': traditional_results.get('sources', {}) if traditional_results.get('success') else {}
                },
                'component_results': {
                    'ml_results': ml_results,
                    'traditional_results': traditional_results
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in hybrid recommendations: {e}")
            return await self._get_traditional_only_recommendations(user_id, context, n_recommendations)

    def _combine_traditional_recommendations(
        self,
        health_recs: Dict[str, Any],
        weather_recs: Dict[str, Any],
        customer_prefs: Dict[str, Any],
        n_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Combine recommendations from traditional agents"""

        recommendations = []

        # Helper function to add items
        def add_items(source_data, category, source_name, weight=1.0):
            items = source_data.get(category, [])
            for i, item in enumerate(items[:3]):  # Top 3 from each source
                rec = {
                    'category': category.rstrip('s'),  # Remove plural
                    'item': item,
                    'predicted_rating': 4.0 + (0.5 * (3-i) * weight),  # Higher rating for top items
                    'confidence': 0.8 * weight,
                    'source': source_name,
                    'method': 'rule_based',
                    'reason': source_data.get('reasoning', f'{source_name} recommendation')
                }
                recommendations.append(rec)

        # Add health recommendations (higher weight)
        for category in ['proteins', 'sauces', 'base_types', 'veggies']:
            add_items(health_recs, category, 'health_agent', 1.0)

        # Add weather recommendations (medium weight)
        for category in ['proteins', 'sauces', 'base_types']:
            add_items(weather_recs, category, 'weather_agent', 0.8)

        # Add customer preferences (highest weight for personalization)
        for category in ['proteins', 'sauces', 'base_types', 'veggies']:
            add_items(customer_prefs, category, 'customer_history', 1.2)

        # Remove duplicates and sort by rating
        unique_recs = {}
        for rec in recommendations:
            key = f"{rec['category']}_{rec['item']}"
            if key not in unique_recs or rec['predicted_rating'] > unique_recs[key]['predicted_rating']:
                unique_recs[key] = rec

        final_recs = list(unique_recs.values())
        final_recs.sort(key=lambda x: x['predicted_rating'], reverse=True)

        return final_recs[:n_recommendations]

    def _create_intelligent_hybrid(
        self,
        ml_results: Dict[str, Any],
        traditional_results: Dict[str, Any],
        n_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Create intelligent hybrid recommendations"""

        hybrid_recs = []

        # Get ML recommendations with weight boost
        if ml_results.get('success') and ml_results.get('recommendations'):
            for rec in ml_results['recommendations']:
                rec_copy = rec.copy()
                rec_copy['hybrid_score'] = rec.get('predicted_rating', 4.0) * self.hybrid_weight_ml
                rec_copy['ml_contribution'] = True
                hybrid_recs.append(rec_copy)

        # Get traditional recommendations
        if traditional_results.get('success') and traditional_results.get('recommendations'):
            for rec in traditional_results['recommendations']:
                rec_copy = rec.copy()
                rec_copy['hybrid_score'] = rec.get('predicted_rating', 4.0) * self.hybrid_weight_traditional
                rec_copy['traditional_contribution'] = True
                hybrid_recs.append(rec_copy)

        # Remove duplicates, keeping the one with higher hybrid score
        unique_recs = {}
        for rec in hybrid_recs:
            key = f"{rec.get('category', 'unknown')}_{rec.get('item', 'unknown')}"

            if key not in unique_recs or rec['hybrid_score'] > unique_recs[key]['hybrid_score']:
                # Combine sources if both ML and traditional suggest the same item
                if key in unique_recs:
                    existing = unique_recs[key]
                    rec['source'] = f"{existing.get('source', '')}, {rec.get('source', '')}"
                    rec['reason'] = f"Recommended by both ML and traditional systems. {rec.get('reason', '')}"
                    rec['consensus'] = True

                unique_recs[key] = rec

        # Sort by hybrid score and return top N
        final_recs = list(unique_recs.values())
        final_recs.sort(key=lambda x: x.get('hybrid_score', 0), reverse=True)

        return final_recs[:n_recommendations]

    def _generate_traditional_explanations(
        self,
        health_recs: Dict[str, Any],
        weather_recs: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate explanations for traditional recommendations"""

        explanations = {}

        health_reasoning = health_recs.get('reasoning', '')
        weather_reasoning = weather_recs.get('reasoning', '')

        explanations['overview'] = (
            f"These recommendations are based on your activity level and current weather conditions. "
            f"{health_reasoning} {weather_reasoning}"
        ).strip()

        return explanations

    def _generate_hybrid_explanations(
        self,
        ml_results: Dict[str, Any],
        traditional_results: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate explanations for hybrid recommendations"""

        explanations = {}

        # Combine explanations from both systems
        ml_explanation = ""
        if ml_results.get('success') and ml_results.get('explanations'):
            ml_explanation = ml_results['explanations'].get('overview', '')

        traditional_explanation = ""
        if traditional_results.get('success') and traditional_results.get('explanations'):
            traditional_explanation = traditional_results['explanations'].get('overview', '')

        explanations['overview'] = (
            f"These recommendations combine machine learning insights with traditional nutritional guidance. "
            f"{ml_explanation} {traditional_explanation}"
        ).strip()

        return explanations

    async def process_unified_feedback(
        self,
        user_id: str,
        feedback_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process feedback and update both ML models and traditional agents"""

        try:
            logger.info(f"Processing unified feedback for user {user_id}")

            # Process with ML engine
            ml_feedback_task = self.ml_engine.process_user_feedback(
                user_id=user_id,
                feedback_data=feedback_data
            )

            # Process with traditional agents
            traditional_feedback_task = self._process_traditional_feedback(
                user_id, feedback_data, context
            )

            # Execute both in parallel
            ml_result, traditional_result = await asyncio.gather(
                ml_feedback_task, traditional_feedback_task, return_exceptions=True
            )

            # Handle exceptions
            if isinstance(ml_result, Exception):
                logger.warning(f"ML feedback processing failed: {ml_result}")
                ml_result = {'success': False, 'error': str(ml_result)}

            if isinstance(traditional_result, Exception):
                logger.warning(f"Traditional feedback processing failed: {traditional_result}")
                traditional_result = {'success': False, 'error': str(traditional_result)}

            return {
                'success': True,
                'user_id': user_id,
                'ml_feedback_result': ml_result,
                'traditional_feedback_result': traditional_result,
                'unified_processing': True,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error processing unified feedback: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def _process_traditional_feedback(
        self,
        user_id: str,
        feedback_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process feedback with traditional agents"""

        try:
            results = {}

            # Process with learner agent
            feedback_type = feedback_data.get('feedback_type', 'implicit')

            if feedback_type == 'explicit':
                ratings = feedback_data.get('explicit_ratings', {})
                for category, rating in ratings.items():
                    feedback_val = 'accept' if rating >= 4 else ('ignore' if rating < 3 else 'custom')

                    learner_result = self.learner_agent.process_feedback(
                        recommendation_type=category,
                        feedback=feedback_val,
                        customer_id=user_id,
                        context=context
                    )
                    results[f'learner_{category}'] = learner_result

            elif feedback_type == 'implicit':
                selections = feedback_data.get('selections', {})

                # Process health agent feedback
                if 'protein' in selections:
                    health_result = self.health_agent.process_feedback(
                        feedback_type='accept',
                        items_selected=selections,
                        activity_level=context.get('activity_level', 'work'),
                        customer_id=user_id
                    )
                    results['health_agent'] = health_result

                # Process weather agent feedback
                if 'base' in selections:
                    weather_result = self.weather_agent.process_feedback(
                        feedback_type='accept',
                        items_selected=selections,
                        weather_condition=context.get('weather', {}).get('condition', 'sunny'),
                        time_of_day=context.get('time_of_day', 'afternoon'),
                        customer_id=user_id
                    )
                    results['weather_agent'] = weather_result

            return {
                'success': True,
                'results': results,
                'processed_feedback_type': feedback_type
            }

        except Exception as e:
            logger.error(f"Error processing traditional feedback: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_fallback_recommendations(self, n_recommendations: int) -> Dict[str, Any]:
        """Fallback recommendations when all systems fail"""

        fallback_recs = [
            {
                'category': 'protein',
                'item': 'Chicken',
                'predicted_rating': 4.5,
                'confidence': 0.8,
                'source': 'fallback',
                'method': 'default',
                'reason': 'Popular and safe choice'
            },
            {
                'category': 'base',
                'item': 'Rice Bowl',
                'predicted_rating': 4.3,
                'confidence': 0.7,
                'source': 'fallback',
                'method': 'default',
                'reason': 'Customer favorite'
            },
            {
                'category': 'sauce',
                'item': 'Curry Special',
                'predicted_rating': 4.4,
                'confidence': 0.8,
                'source': 'fallback',
                'method': 'default',
                'reason': 'Signature dish'
            }
        ]

        return {
            'success': True,
            'mode': 'fallback',
            'recommendations': fallback_recs[:n_recommendations],
            'explanations': {'overview': 'Default recommendations when personalization is unavailable'},
            'confidence': 0.6,
            'sources': {'fallback': len(fallback_recs)},
            'timestamp': datetime.now().isoformat()
        }

    async def get_system_health(self) -> Dict[str, Any]:
        """Get health status of all recommendation systems"""

        try:
            # Check ML system health
            ml_insights = await self.ml_engine.get_model_insights()

            # Check traditional agents health
            traditional_health = {
                'health_agent': {
                    'status': 'healthy' if self.health_agent.health_data else 'degraded',
                    'data_size': len(self.health_agent.health_data.get('activity_recommendations', {}))
                },
                'weather_agent': {
                    'status': 'healthy' if self.weather_agent.weather_data else 'degraded',
                    'data_size': len(self.weather_agent.weather_data.get('condition_recommendations', {}))
                },
                'learner_agent': {
                    'status': 'healthy',
                    'feedback_count': len(self.learner_agent.learning_data.get('feedback_history', [])),
                    'customer_count': len(self.learner_agent.learning_data.get('customer_preferences', {}))
                }
            }

            # Overall system health
            overall_status = 'healthy'
            if ml_insights.get('error') or any(agent['status'] != 'healthy' for agent in traditional_health.values()):
                overall_status = 'degraded'

            return {
                'overall_status': overall_status,
                'ml_system': ml_insights,
                'traditional_agents': traditional_health,
                'integration_status': 'operational',
                'last_checked': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return {
                'overall_status': 'error',
                'error': str(e),
                'last_checked': datetime.now().isoformat()
            }