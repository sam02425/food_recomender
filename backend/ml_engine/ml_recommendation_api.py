"""
ML Recommendation API - Main orchestrator for machine learning recommendations
Integrates collaborative filtering, NLP feedback analysis, and preference learning
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import pandas as pd

from .collaborative_filtering import CollaborativeFilteringEngine
from .nlp_feedback_analyzer import NLPFeedbackAnalyzer
from .preference_learning import PreferenceLearningAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLRecommendationEngine:
    """Main ML recommendation engine that coordinates all ML components"""

    def __init__(self, data_path: str = "data/"):
        self.data_path = data_path

        # Initialize ML components
        logger.info("Initializing ML Recommendation Engine...")

        self.collaborative_filter = CollaborativeFilteringEngine(
            model_path=f"{data_path}models/collaborative_filtering.joblib"
        )

        self.nlp_analyzer = NLPFeedbackAnalyzer(
            model_path=f"{data_path}models/nlp_feedback.joblib"
        )

        self.preference_learner = PreferenceLearningAgent(
            model_path=f"{data_path}models/preference_learning.joblib"
        )

        # Load user interaction data
        self.user_interactions = self._load_user_interactions()

        logger.info("ML Recommendation Engine initialized successfully")

    def _load_user_interactions(self) -> List[Dict]:
        """Load user interaction data from various sources"""
        interactions = []

        try:
            # Load from learning data
            with open(f"{self.data_path}learning_data.json", 'r') as f:
                learning_data = json.load(f)

            # Convert feedback history to interactions
            for feedback in learning_data.get('feedback_history', []):
                interaction = {
                    'user_id': feedback.get('customer_id', 'anonymous'),
                    'timestamp': feedback.get('timestamp'),
                    'type': 'feedback',
                    'category': feedback.get('type'),
                    'action': feedback.get('feedback'),
                    'context': feedback.get('context', {})
                }
                interactions.append(interaction)

            logger.info(f"Loaded {len(interactions)} user interactions")

        except Exception as e:
            logger.error(f"Error loading user interactions: {e}")

        return interactions

    async def get_comprehensive_recommendations(
        self,
        user_id: str,
        context: Dict[str, Any],
        n_recommendations: int = 5
    ) -> Dict[str, Any]:
        """Get comprehensive recommendations using all ML approaches"""

        try:
            logger.info(f"Generating comprehensive recommendations for user {user_id}")

            # Gather recommendations from all sources
            tasks = [
                self._get_collaborative_recommendations(user_id, context, n_recommendations),
                self._get_preference_based_recommendations(user_id, context, n_recommendations),
                self._get_context_aware_recommendations(context, n_recommendations)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            collaborative_recs = results[0] if not isinstance(results[0], Exception) else []
            preference_recs = results[1] if not isinstance(results[1], Exception) else []
            context_recs = results[2] if not isinstance(results[2], Exception) else []

            # Combine and rank recommendations
            combined_recs = self._combine_recommendations(
                collaborative_recs,
                preference_recs,
                context_recs,
                n_recommendations
            )

            # Generate explanations
            explanations = self._generate_explanations(combined_recs, user_id, context)

            return {
                'success': True,
                'user_id': user_id,
                'recommendations': combined_recs,
                'explanations': explanations,
                'confidence': self._calculate_overall_confidence(combined_recs),
                'sources': {
                    'collaborative_filtering': len(collaborative_recs),
                    'preference_learning': len(preference_recs),
                    'context_aware': len(context_recs)
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating comprehensive recommendations: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_recommendations': self._get_fallback_recommendations(n_recommendations)
            }

    async def _get_collaborative_recommendations(
        self,
        user_id: str,
        context: Dict[str, Any],
        n_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Get recommendations from collaborative filtering"""

        try:
            # Convert user interaction history to collaborative filtering format
            user_orders = self._get_user_order_history(user_id)

            if not user_orders:
                # For new users, use item-based recommendations
                recs = self.collaborative_filter.get_fallback_recommendations(n_recommendations)
            else:
                # Get user-based recommendations
                recs = self.collaborative_filter.get_user_recommendations(
                    user_id=hash(user_id) % 10000,  # Convert to int ID
                    n_recommendations=n_recommendations
                )

            # Add source information
            for rec in recs:
                rec['source'] = 'collaborative_filtering'
                rec['method'] = 'user_similarity' if user_orders else 'popularity'

            return recs

        except Exception as e:
            logger.error(f"Error in collaborative filtering recommendations: {e}")
            return []

    async def _get_preference_based_recommendations(
        self,
        user_id: str,
        context: Dict[str, Any],
        n_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Get recommendations from preference learning"""

        try:
            # Get user preferences
            preferences = self.preference_learner.get_user_preferences(user_id)

            recommendations = []

            # Convert preferences to recommendations
            for category, pref_data in preferences.get('categories', {}).items():
                items = pref_data.get('items', [])

                for item in items[:2]:  # Top 2 per category
                    recommendation = {
                        'category': category,
                        'item': item['item'],
                        'predicted_rating': item.get('predicted_rating', 4.0),
                        'confidence': item.get('confidence', 0.5),
                        'source': 'preference_learning',
                        'method': pref_data.get('method', 'ml_prediction'),
                        'reason': f"Based on your {category} preferences"
                    }
                    recommendations.append(recommendation)

            # Sort by predicted rating
            recommendations.sort(key=lambda x: x['predicted_rating'], reverse=True)

            return recommendations[:n_recommendations]

        except Exception as e:
            logger.error(f"Error in preference-based recommendations: {e}")
            return []

    async def _get_context_aware_recommendations(
        self,
        context: Dict[str, Any],
        n_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Get context-aware recommendations based on situation"""

        try:
            recommendations = []

            # Activity-based recommendations
            activity = context.get('activity_level', 'unknown')
            mood = context.get('mood', 'neutral')
            time_of_day = context.get('time_of_day', 'afternoon')
            weather = context.get('weather', {}).get('condition', 'sunny')

            # Create context-based recommendations
            if activity == 'gym' or activity == 'active':
                recommendations.extend([
                    {
                        'category': 'protein',
                        'item': 'Chicken',
                        'predicted_rating': 4.8,
                        'confidence': 0.9,
                        'source': 'context_aware',
                        'method': 'activity_based',
                        'reason': f"High protein content ideal for {activity} activity"
                    },
                    {
                        'category': 'base',
                        'item': 'Rice Bowl',
                        'predicted_rating': 4.6,
                        'confidence': 0.8,
                        'source': 'context_aware',
                        'method': 'activity_based',
                        'reason': "Complex carbohydrates for sustained energy"
                    }
                ])

            elif activity == 'study' or activity == 'work':
                recommendations.extend([
                    {
                        'category': 'protein',
                        'item': 'Egg',
                        'predicted_rating': 4.5,
                        'confidence': 0.8,
                        'source': 'context_aware',
                        'method': 'activity_based',
                        'reason': "Brain-boosting nutrients for focus"
                    },
                    {
                        'category': 'sauce',
                        'item': 'Malai Masala',
                        'predicted_rating': 4.3,
                        'confidence': 0.7,
                        'source': 'context_aware',
                        'method': 'activity_based',
                        'reason': "Mild and comforting for concentration"
                    }
                ])

            # Mood-based adjustments
            if mood in ['happy', 'excited']:
                recommendations.append({
                    'category': 'sauce',
                    'item': 'Green Spicy Sauce',
                    'predicted_rating': 4.4,
                    'confidence': 0.6,
                    'source': 'context_aware',
                    'method': 'mood_based',
                    'reason': f"Spicy flavors match your {mood} mood"
                })

            elif mood in ['relaxed', 'chilling']:
                recommendations.append({
                    'category': 'base',
                    'item': 'Salad Bowl',
                    'predicted_rating': 4.2,
                    'confidence': 0.6,
                    'source': 'context_aware',
                    'method': 'mood_based',
                    'reason': f"Light and fresh for {mood} moments"
                })

            # Weather-based recommendations
            if weather in ['hot', 'sunny']:
                recommendations.append({
                    'category': 'sauce',
                    'item': 'Yogurt/Raita',
                    'predicted_rating': 4.3,
                    'confidence': 0.7,
                    'source': 'context_aware',
                    'method': 'weather_based',
                    'reason': f"Cooling option for {weather} weather"
                })

            elif weather in ['cold', 'rainy']:
                recommendations.append({
                    'category': 'sauce',
                    'item': 'Curry Masala',
                    'predicted_rating': 4.5,
                    'confidence': 0.8,
                    'source': 'context_aware',
                    'method': 'weather_based',
                    'reason': f"Warming spices perfect for {weather} weather"
                })

            return recommendations[:n_recommendations]

        except Exception as e:
            logger.error(f"Error in context-aware recommendations: {e}")
            return []

    def _combine_recommendations(
        self,
        collaborative_recs: List[Dict],
        preference_recs: List[Dict],
        context_recs: List[Dict],
        n_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Combine recommendations from different sources with weighted scoring"""

        all_recommendations = []

        # Weight different sources
        weights = {
            'collaborative_filtering': 0.4,
            'preference_learning': 0.4,
            'context_aware': 0.2
        }

        # Add weighted scores to recommendations
        for recs, source_weight in [(collaborative_recs, weights['collaborative_filtering']),
                                   (preference_recs, weights['preference_learning']),
                                   (context_recs, weights['context_aware'])]:

            for rec in recs:
                # Calculate weighted score
                base_rating = rec.get('predicted_rating', 4.0)
                confidence = rec.get('confidence', 0.5)
                weighted_score = base_rating * confidence * source_weight

                rec['weighted_score'] = weighted_score
                all_recommendations.append(rec)

        # Remove duplicates (same category + item)
        unique_recs = {}
        for rec in all_recommendations:
            key = f"{rec.get('category', 'unknown')}_{rec.get('item', 'unknown')}"

            if key not in unique_recs or rec['weighted_score'] > unique_recs[key]['weighted_score']:
                unique_recs[key] = rec

        # Sort by weighted score and return top N
        final_recommendations = list(unique_recs.values())
        final_recommendations.sort(key=lambda x: x['weighted_score'], reverse=True)

        return final_recommendations[:n_recommendations]

    def _generate_explanations(
        self,
        recommendations: List[Dict],
        user_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate explanations for recommendations"""

        explanations = {}

        # Overall explanation
        sources = set(rec.get('source', 'unknown') for rec in recommendations)
        source_names = {
            'collaborative_filtering': "users with similar preferences",
            'preference_learning': "your personal taste profile",
            'context_aware': "your current situation"
        }

        source_list = [source_names.get(s, s) for s in sources]

        explanations['overview'] = f"These recommendations are based on {', '.join(source_list)}."

        # Individual explanations
        for i, rec in enumerate(recommendations):
            explanations[f'item_{i+1}'] = rec.get('reason', 'Recommended based on our analysis')

        return explanations

    def _calculate_overall_confidence(self, recommendations: List[Dict]) -> float:
        """Calculate overall confidence in recommendations"""
        if not recommendations:
            return 0.0

        confidences = [rec.get('confidence', 0.5) for rec in recommendations]
        return sum(confidences) / len(confidences)

    async def process_user_feedback(
        self,
        user_id: str,
        feedback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process user feedback and update all ML components"""

        try:
            logger.info(f"Processing feedback from user {user_id}")

            # Extract feedback components
            explicit_feedback = feedback_data.get('explicit_ratings', {})
            implicit_feedback = feedback_data.get('selections', {})
            text_feedback = feedback_data.get('text_feedback', '')
            order_details = feedback_data.get('order_details', {})

            # Process with NLP analyzer
            nlp_analysis = {}
            if text_feedback:
                nlp_analysis = self.nlp_analyzer.analyze_feedback(text_feedback, order_details)

            # Update collaborative filtering
            cf_result = {}
            if explicit_feedback or implicit_feedback:
                # Convert feedback to collaborative filtering format
                item_combo = self._create_item_combination(implicit_feedback)
                rating = self._convert_feedback_to_rating(explicit_feedback, nlp_analysis)

                self.collaborative_filter.update_with_feedback(
                    user_id=hash(user_id) % 10000,
                    item_combo=item_combo,
                    rating=rating,
                    feedback_text=text_feedback
                )
                cf_result = {'updated': True, 'rating': rating}

            # Update preference learning
            preference_result = {}
            if feedback_data:
                interaction_data = {
                    'activity_level': feedback_data.get('context', {}).get('activity_level'),
                    'mood': feedback_data.get('context', {}).get('mood'),
                    'weather': feedback_data.get('context', {}).get('weather'),
                    'selections': implicit_feedback,
                    'feedback': explicit_feedback,
                    'ratings': explicit_feedback,
                    'order_history': self._get_user_order_history(user_id)
                }

                preference_result = self.preference_learner.process_user_interaction(
                    user_id, interaction_data
                )

            # Store feedback for future analysis
            self._store_feedback(user_id, feedback_data, nlp_analysis)

            return {
                'success': True,
                'user_id': user_id,
                'nlp_analysis': nlp_analysis,
                'collaborative_filtering': cf_result,
                'preference_learning': preference_result,
                'processed_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error processing user feedback: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _create_item_combination(self, selections: Dict[str, Any]) -> str:
        """Create item combination string for collaborative filtering"""
        protein = selections.get('protein', 'Unknown')
        base = selections.get('base', 'Unknown')
        sauce = selections.get('sauce', 'Unknown')

        return f"{protein}-{base}-{sauce}"

    def _convert_feedback_to_rating(
        self,
        explicit_feedback: Dict[str, Any],
        nlp_analysis: Dict[str, Any]
    ) -> float:
        """Convert various feedback forms to a numerical rating"""

        # If explicit rating provided
        if 'overall_rating' in explicit_feedback:
            return float(explicit_feedback['overall_rating'])

        # Use NLP sentiment analysis
        if nlp_analysis and 'preference_score' in nlp_analysis:
            return nlp_analysis['preference_score'] * 5  # Convert 0-1 to 0-5

        # Use implicit feedback
        feedback_scores = []
        for category, feedback in explicit_feedback.items():
            if feedback == 'accept':
                feedback_scores.append(5)
            elif feedback == 'ignore':
                feedback_scores.append(2)
            elif feedback == 'custom':
                feedback_scores.append(3)

        if feedback_scores:
            return sum(feedback_scores) / len(feedback_scores)

        # Default neutral rating
        return 3.0

    def _get_user_order_history(self, user_id: str) -> List[Dict]:
        """Get user's order history"""
        # Filter interactions for this user
        user_orders = []
        for interaction in self.user_interactions:
            if interaction.get('user_id') == user_id and interaction.get('type') == 'order':
                user_orders.append(interaction)

        return user_orders

    def _store_feedback(
        self,
        user_id: str,
        feedback_data: Dict[str, Any],
        nlp_analysis: Dict[str, Any]
    ):
        """Store feedback for future analysis"""

        feedback_record = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'feedback_data': feedback_data,
            'nlp_analysis': nlp_analysis,
            'type': 'feedback'
        }

        self.user_interactions.append(feedback_record)

        # Keep only recent interactions (last 10000)
        if len(self.user_interactions) > 10000:
            self.user_interactions = self.user_interactions[-10000:]

    def _get_fallback_recommendations(self, n_recommendations: int) -> List[Dict[str, Any]]:
        """Get fallback recommendations when ML fails"""

        fallback = [
            {
                'category': 'protein',
                'item': 'Chicken',
                'predicted_rating': 4.5,
                'confidence': 0.8,
                'source': 'fallback',
                'reason': 'Popular choice'
            },
            {
                'category': 'base',
                'item': 'Rice Bowl',
                'predicted_rating': 4.3,
                'confidence': 0.7,
                'source': 'fallback',
                'reason': 'Customer favorite'
            },
            {
                'category': 'sauce',
                'item': 'Curry Special',
                'predicted_rating': 4.4,
                'confidence': 0.8,
                'source': 'fallback',
                'reason': 'Signature dish'
            }
        ]

        return fallback[:n_recommendations]

    async def get_model_insights(self) -> Dict[str, Any]:
        """Get insights about all ML models"""

        try:
            cf_stats = {
                'user_item_matrix_size': (
                    len(self.collaborative_filter.user_item_matrix.index)
                    if self.collaborative_filter.user_item_matrix is not None else 0,
                    len(self.collaborative_filter.user_item_matrix.columns)
                    if self.collaborative_filter.user_item_matrix is not None else 0
                ),
                'model_trained': self.collaborative_filter.svd_model is not None
            }

            preference_stats = self.preference_learner.get_model_stats()

            nlp_stats = {
                'sentiment_analyzer_loaded': self.nlp_analyzer.sentiment_analyzer is not None,
                'sentence_transformer_loaded': self.nlp_analyzer.sentence_transformer is not None,
                'tfidf_trained': self.nlp_analyzer.tfidf_vectorizer is not None
            }

            return {
                'collaborative_filtering': cf_stats,
                'preference_learning': preference_stats,
                'nlp_analysis': nlp_stats,
                'total_interactions': len(self.user_interactions),
                'system_health': 'healthy',
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting model insights: {e}")
            return {'error': str(e)}

    async def retrain_models(self) -> Dict[str, Any]:
        """Retrain all ML models with latest data"""

        try:
            logger.info("Starting model retraining...")

            # Prepare training data from interactions
            training_data = self._prepare_training_data()

            # Retrain collaborative filtering
            if training_data['orders']:
                df = pd.DataFrame(training_data['orders'])
                self.collaborative_filter.train_models(df)

            # Retrain NLP analyzer
            if training_data['feedback']:
                self.nlp_analyzer.train_preference_model(training_data['feedback'])

            # Preference learning is updated incrementally, so no separate retraining needed

            logger.info("Model retraining completed")

            return {
                'success': True,
                'retrained_models': ['collaborative_filtering', 'nlp_analyzer'],
                'training_data_size': {
                    'orders': len(training_data['orders']),
                    'feedback': len(training_data['feedback'])
                },
                'retrained_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error retraining models: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _prepare_training_data(self) -> Dict[str, List[Dict]]:
        """Prepare training data from user interactions"""

        orders = []
        feedback = []

        for interaction in self.user_interactions:
            if interaction.get('type') == 'order':
                orders.append({
                    'customer_id': interaction['user_id'],
                    'selected_protein': interaction.get('selections', {}).get('protein'),
                    'selected_base': interaction.get('selections', {}).get('base'),
                    'selected_sauce': interaction.get('selections', {}).get('sauce'),
                    'rating': interaction.get('rating', 4),
                    'completed': True,
                    'timestamp': interaction.get('timestamp'),
                    'mood': interaction.get('context', {}).get('mood'),
                    'activity': interaction.get('context', {}).get('activity_level')
                })

            elif interaction.get('type') == 'feedback':
                feedback_text = interaction.get('feedback_data', {}).get('text_feedback', '')
                if feedback_text:
                    feedback.append({
                        'feedback_text': feedback_text,
                        'rating': interaction.get('feedback_data', {}).get('explicit_ratings', {}).get('overall_rating', 3),
                        'order_details': interaction.get('feedback_data', {}).get('order_details', {})
                    })

        return {
            'orders': orders,
            'feedback': feedback
        }