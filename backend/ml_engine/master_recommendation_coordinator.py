"""
Master Recommendation Coordinator Agent
State-of-the-art agentic flow for food recommendations

This agent coordinates multiple specialized recommendation agents:
- Weather Agent
- Health Agent
- Mood Agent
- Learner Agent
- Context Agent
- Temporal Agent

Uses RNN models for sequential pattern learning and provides
filtered recommendations through dietary restrictions.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import joblib
from dataclasses import dataclass
from enum import Enum

# Deep Learning Components
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, Embedding, Input, Concatenate
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Import existing agents
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from temp_repo.src.agents.Health_Ag import HealthRecommenderAgent
    from temp_repo.src.agents.Weather_Ag import WeatherRecommenderAgent
    from temp_repo.src.agents.Learner_Ag import LearnerAgent
except ImportError:
    # Fallback imports
    class HealthRecommenderAgent:
        def get_recommendations(self, **kwargs):
            return {'proteins': ['Chicken'], 'bases': ['Rice'], 'sauces': ['Curry']}

    class WeatherRecommenderAgent:
        def get_recommendations(self, **kwargs):
            return {'proteins': ['Fish'], 'bases': ['Bowl'], 'sauces': ['Mild']}

    class LearnerAgent:
        def __init__(self, *args): pass
        def get_recommendations(self, **kwargs):
            return {'proteins': ['Tofu'], 'bases': ['Noodles'], 'sauces': ['Spicy']}

from .dietary_restrictions import DietaryRestrictionsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationPriority(Enum):
    """Priority levels for different recommendation sources"""
    CRITICAL = 1.0      # Dietary restrictions, health conditions
    HIGH = 0.8          # Personal preferences, weather
    MEDIUM = 0.6        # Mood, social trends
    LOW = 0.4           # Random exploration
    FALLBACK = 0.2      # Default recommendations

@dataclass
class AgentRecommendation:
    """Structured recommendation from an agent"""
    agent_name: str
    category: str
    item: str
    confidence: float
    reasoning: str
    priority: RecommendationPriority
    context_relevance: float
    temporal_weight: float
    metadata: Dict[str, Any]

@dataclass
class UserContext:
    """Complete user context for recommendations"""
    user_id: str
    location: Optional[str]
    weather: Dict[str, Any]
    time_of_day: str
    activity_level: str
    mood: str
    health_conditions: List[str]
    dietary_restrictions: List[str]
    allergens: List[str]
    order_history: List[Dict]
    session_context: Dict[str, Any]
    social_context: Dict[str, Any]

class TemporalPatternRNN:
    """RNN model for learning temporal eating patterns"""

    def __init__(self, sequence_length: int = 10, feature_dim: int = 50):
        self.sequence_length = sequence_length
        self.feature_dim = feature_dim
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False

    def build_model(self):
        """Build RNN architecture for temporal pattern learning"""
        # Input for sequential data
        sequence_input = Input(shape=(self.sequence_length, self.feature_dim), name='sequence_input')

        # Context input for current state
        context_input = Input(shape=(20,), name='context_input')

        # RNN layers
        lstm1 = LSTM(128, return_sequences=True, dropout=0.2)(sequence_input)
        lstm2 = LSTM(64, return_sequences=False, dropout=0.2)(lstm1)

        # Context processing
        context_dense = Dense(32, activation='relu')(context_input)

        # Combine temporal and context features
        combined = Concatenate()([lstm2, context_dense])

        # Output layers for different categories
        protein_output = Dense(64, activation='relu')(combined)
        protein_output = Dropout(0.3)(protein_output)
        protein_output = Dense(10, activation='softmax', name='protein')(protein_output)

        base_output = Dense(64, activation='relu')(combined)
        base_output = Dropout(0.3)(base_output)
        base_output = Dense(8, activation='softmax', name='base')(base_output)

        sauce_output = Dense(64, activation='relu')(combined)
        sauce_output = Dropout(0.3)(sauce_output)
        sauce_output = Dense(12, activation='softmax', name='sauce')(sauce_output)

        # Preference score output
        preference_output = Dense(32, activation='relu')(combined)
        preference_output = Dense(1, activation='sigmoid', name='preference_score')(preference_output)

        # Create model
        self.model = Model(
            inputs=[sequence_input, context_input],
            outputs=[protein_output, base_output, sauce_output, preference_output]
        )

        # Compile with multiple loss functions
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss={
                'protein': 'categorical_crossentropy',
                'base': 'categorical_crossentropy',
                'sauce': 'categorical_crossentropy',
                'preference_score': 'binary_crossentropy'
            },
            loss_weights={
                'protein': 1.0,
                'base': 1.0,
                'sauce': 1.0,
                'preference_score': 2.0  # Higher weight for preference learning
            },
            metrics=['accuracy']
        )

        logger.info("RNN model built successfully")

    def prepare_sequence_data(self, order_history: List[Dict]) -> np.ndarray:
        """Prepare sequential data from order history"""
        if len(order_history) < self.sequence_length:
            # Pad with zeros if insufficient history
            padded_history = [{}] * (self.sequence_length - len(order_history)) + order_history
        else:
            padded_history = order_history[-self.sequence_length:]

        sequences = []
        for order in padded_history:
            # Extract features from each order
            features = self._extract_order_features(order)
            sequences.append(features)

        return np.array(sequences).reshape(1, self.sequence_length, self.feature_dim)

    def _extract_order_features(self, order: Dict) -> np.ndarray:
        """Extract numerical features from an order"""
        features = np.zeros(self.feature_dim)

        if not order:
            return features

        # Time features
        if 'timestamp' in order:
            try:
                dt = datetime.fromisoformat(order['timestamp'])
                features[0] = dt.hour / 24.0  # Hour of day
                features[1] = dt.weekday() / 7.0  # Day of week
            except:
                pass

        # Category encodings (one-hot style)
        protein = order.get('protein', '')
        if protein:
            protein_hash = hash(protein) % 10
            features[2 + protein_hash] = 1.0

        base = order.get('base', '')
        if base:
            base_hash = hash(base) % 8
            features[12 + base_hash] = 1.0

        sauce = order.get('sauce', '')
        if sauce:
            sauce_hash = hash(sauce) % 10
            features[20 + sauce_hash] = 1.0

        # Context features
        features[30] = order.get('rating', 3.0) / 5.0  # Normalized rating
        features[31] = 1.0 if order.get('weather') == 'sunny' else 0.0
        features[32] = 1.0 if order.get('activity_level') == 'active' else 0.0
        features[33] = order.get('total_price', 15.0) / 30.0  # Normalized price

        return features

    def predict_preferences(self, sequence_data: np.ndarray, context_features: np.ndarray) -> Dict[str, Any]:
        """Predict user preferences using trained RNN"""
        if not self.is_trained or self.model is None:
            return self._get_default_predictions()

        try:
            predictions = self.model.predict([sequence_data, context_features.reshape(1, -1)], verbose=0)

            protein_probs = predictions[0][0]
            base_probs = predictions[1][0]
            sauce_probs = predictions[2][0]
            preference_score = predictions[3][0][0]

            return {
                'protein_preferences': protein_probs.tolist(),
                'base_preferences': base_probs.tolist(),
                'sauce_preferences': sauce_probs.tolist(),
                'overall_preference_score': float(preference_score),
                'confidence': min(1.0, preference_score * 2)  # Convert to confidence
            }

        except Exception as e:
            logger.error(f"Error in RNN prediction: {e}")
            return self._get_default_predictions()

    def _get_default_predictions(self) -> Dict[str, Any]:
        """Default predictions when RNN is not available"""
        return {
            'protein_preferences': [0.1] * 10,
            'base_preferences': [0.125] * 8,
            'sauce_preferences': [0.083] * 12,
            'overall_preference_score': 0.5,
            'confidence': 0.3
        }

class MoodAgent:
    """Specialized agent for mood-based recommendations"""

    def __init__(self):
        self.mood_mappings = {
            'happy': {'proteins': ['Chicken', 'Prawns'], 'flavors': ['mild', 'sweet'], 'spice': 'medium'},
            'stressed': {'proteins': ['Fish', 'Tofu'], 'flavors': ['comfort', 'familiar'], 'spice': 'mild'},
            'energetic': {'proteins': ['Beef', 'Chicken'], 'flavors': ['bold', 'spicy'], 'spice': 'high'},
            'relaxed': {'proteins': ['Fish', 'Vegetable'], 'flavors': ['light', 'fresh'], 'spice': 'mild'},
            'sad': {'proteins': ['Chicken', 'Paneer'], 'flavors': ['comfort', 'rich'], 'spice': 'medium'},
            'excited': {'proteins': ['Prawns', 'Chicken'], 'flavors': ['adventurous', 'new'], 'spice': 'high'},
            'tired': {'proteins': ['Fish', 'Tofu'], 'flavors': ['simple', 'nourishing'], 'spice': 'low'},
            'neutral': {'proteins': ['Chicken', 'Fish'], 'flavors': ['balanced'], 'spice': 'medium'}
        }

    def get_recommendations(self, mood: str, context: Dict = None) -> List[AgentRecommendation]:
        """Get mood-based recommendations"""
        mood = mood.lower() if mood else 'neutral'
        mapping = self.mood_mappings.get(mood, self.mood_mappings['neutral'])

        recommendations = []

        # Protein recommendations
        for protein in mapping['proteins']:
            rec = AgentRecommendation(
                agent_name='mood_agent',
                category='protein',
                item=protein,
                confidence=0.8,
                reasoning=f"Selected for {mood} mood - promotes comfort and satisfaction",
                priority=RecommendationPriority.MEDIUM,
                context_relevance=0.9,
                temporal_weight=1.0,
                metadata={'mood': mood, 'flavor_profile': mapping['flavors']}
            )
            recommendations.append(rec)

        return recommendations

class ContextAgent:
    """Agent for context-aware recommendations"""

    def __init__(self):
        self.context_rules = {
            'time_of_day': {
                'morning': {'base_types': ['Bowl', 'Wrap'], 'proteins': ['Chicken', 'Fish'], 'preference': 'light'},
                'afternoon': {'base_types': ['Rice Bowl', 'Hoagie'], 'proteins': ['Beef', 'Chicken'], 'preference': 'hearty'},
                'evening': {'base_types': ['Rice Bowl', 'Wrap'], 'proteins': ['Fish', 'Vegetable'], 'preference': 'digestible'}
            },
            'activity_level': {
                'gym': {'proteins': ['Chicken', 'Fish'], 'focus': 'high_protein'},
                'work': {'base_types': ['Bowl', 'Hoagie'], 'focus': 'convenient'},
                'study': {'proteins': ['Fish', 'Tofu'], 'focus': 'brain_food'},
                'chilling': {'base_types': ['Rice Bowl'], 'focus': 'comfort'}
            }
        }

    def get_recommendations(self, context: UserContext) -> List[AgentRecommendation]:
        """Get context-based recommendations"""
        recommendations = []

        # Time-based recommendations
        time_rules = self.context_rules['time_of_day'].get(context.time_of_day, {})
        for category, items in time_rules.items():
            if category in ['proteins', 'base_types'] and isinstance(items, list):
                for item in items:
                    rec = AgentRecommendation(
                        agent_name='context_agent',
                        category=category.rstrip('s'),
                        item=item,
                        confidence=0.7,
                        reasoning=f"Optimal for {context.time_of_day} consumption",
                        priority=RecommendationPriority.MEDIUM,
                        context_relevance=1.0,
                        temporal_weight=1.0,
                        metadata={'time_of_day': context.time_of_day}
                    )
                    recommendations.append(rec)

        # Activity-based recommendations
        activity_rules = self.context_rules['activity_level'].get(context.activity_level, {})
        for category, items in activity_rules.items():
            if category == 'proteins' and isinstance(items, list):
                for item in items:
                    rec = AgentRecommendation(
                        agent_name='context_agent',
                        category='protein',
                        item=item,
                        confidence=0.75,
                        reasoning=f"Supports {context.activity_level} activity requirements",
                        priority=RecommendationPriority.MEDIUM,
                        context_relevance=0.9,
                        temporal_weight=1.0,
                        metadata={'activity_level': context.activity_level, 'focus': activity_rules.get('focus')}
                    )
                    recommendations.append(rec)

        return recommendations

class MasterRecommendationCoordinator:
    """
    Master coordinator that orchestrates all recommendation agents
    and provides filtered, personalized recommendations
    """

    def __init__(self, data_path: str = "data/"):
        self.data_path = data_path

        # Initialize all agents
        logger.info("Initializing Master Recommendation Coordinator...")

        # Core agents
        self.health_agent = HealthRecommenderAgent()
        self.weather_agent = WeatherRecommenderAgent()
        self.learner_agent = LearnerAgent(f"{data_path}learning_data.json")
        self.mood_agent = MoodAgent()
        self.context_agent = ContextAgent()

        # Filtering system
        self.dietary_manager = DietaryRestrictionsManager()

        # RNN for temporal patterns
        self.temporal_rnn = TemporalPatternRNN()
        self.temporal_rnn.build_model()

        # Recommendation fusion weights
        self.agent_weights = {
            'health_agent': 0.25,
            'weather_agent': 0.20,
            'learner_agent': 0.20,
            'mood_agent': 0.15,
            'context_agent': 0.20
        }

        # Load models if they exist
        self._load_models()

        logger.info("Master Recommendation Coordinator initialized successfully")

    def _load_models(self):
        """Load pre-trained models"""
        try:
            model_path = f"{self.data_path}models/temporal_rnn.h5"
            if os.path.exists(model_path):
                self.temporal_rnn.model = tf.keras.models.load_model(model_path)
                self.temporal_rnn.is_trained = True
                logger.info("Loaded pre-trained RNN model")
        except Exception as e:
            logger.warning(f"Could not load RNN model: {e}")

    def save_models(self):
        """Save trained models"""
        try:
            os.makedirs(f"{self.data_path}models", exist_ok=True)
            if self.temporal_rnn.model and self.temporal_rnn.is_trained:
                self.temporal_rnn.model.save(f"{self.data_path}models/temporal_rnn.h5")
                logger.info("Saved RNN model")
        except Exception as e:
            logger.error(f"Error saving models: {e}")

    async def get_comprehensive_recommendations(
        self,
        user_context: UserContext,
        n_recommendations: int = 5,
        include_explanations: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive recommendations from all agents with filtering

        Args:
            user_context: Complete user context
            n_recommendations: Number of final recommendations
            include_explanations: Whether to include explanations

        Returns:
            Comprehensive recommendation response
        """

        start_time = datetime.now()

        try:
            logger.info(f"Getting comprehensive recommendations for user {user_context.user_id}")

            # Step 1: Gather recommendations from all agents in parallel
            agent_recommendations = await self._gather_agent_recommendations(user_context)

            # Step 2: Apply RNN temporal analysis
            temporal_insights = self._analyze_temporal_patterns(user_context)

            # Step 3: Fuse all recommendations
            fused_recommendations = self._fuse_recommendations(
                agent_recommendations,
                temporal_insights,
                user_context
            )

            # Step 4: Apply dietary restrictions and allergen filtering
            safe_recommendations = self._apply_dietary_filtering(
                fused_recommendations,
                user_context
            )

            # Step 5: Rank and select final recommendations
            final_recommendations = self._rank_and_select(
                safe_recommendations,
                n_recommendations,
                user_context
            )

            # Step 6: Generate explanations
            explanations = self._generate_explanations(
                final_recommendations,
                agent_recommendations,
                temporal_insights
            ) if include_explanations else {}

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(final_recommendations)

            return {
                'success': True,
                'recommendations': final_recommendations,
                'explanations': explanations,
                'confidence': overall_confidence,
                'agent_contributions': self._summarize_agent_contributions(agent_recommendations),
                'temporal_insights': temporal_insights,
                'dietary_filtering_applied': len(user_context.dietary_restrictions) > 0 or len(user_context.allergens) > 0,
                'processing_time_ms': processing_time * 1000,
                'total_agents_consulted': len(agent_recommendations),
                'recommendation_method': 'multi_agent_rnn_fusion',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in comprehensive recommendations: {e}")
            return self._get_fallback_recommendations(n_recommendations)

    async def _gather_agent_recommendations(self, user_context: UserContext) -> Dict[str, List[AgentRecommendation]]:
        """Gather recommendations from all agents in parallel"""

        agent_tasks = {}

        # Health Agent
        agent_tasks['health'] = asyncio.create_task(
            self._get_health_recommendations(user_context)
        )

        # Weather Agent
        agent_tasks['weather'] = asyncio.create_task(
            self._get_weather_recommendations(user_context)
        )

        # Learner Agent
        agent_tasks['learner'] = asyncio.create_task(
            self._get_learner_recommendations(user_context)
        )

        # Mood Agent
        agent_tasks['mood'] = asyncio.create_task(
            self._get_mood_recommendations(user_context)
        )

        # Context Agent
        agent_tasks['context'] = asyncio.create_task(
            self._get_context_recommendations(user_context)
        )

        # Wait for all tasks to complete
        agent_results = {}
        for agent_name, task in agent_tasks.items():
            try:
                agent_results[agent_name] = await task
            except Exception as e:
                logger.error(f"Error from {agent_name}: {e}")
                agent_results[agent_name] = []

        return agent_results

    async def _get_health_recommendations(self, user_context: UserContext) -> List[AgentRecommendation]:
        """Get health agent recommendations"""
        try:
            health_recs = self.health_agent.get_recommendations(
                activity_level=user_context.activity_level,
                customer_id=user_context.user_id,
                previous_orders=user_context.order_history,
                mood=user_context.mood
            )

            recommendations = []
            for category, items in health_recs.items():
                if isinstance(items, list):
                    for i, item in enumerate(items[:3]):  # Top 3 per category
                        rec = AgentRecommendation(
                            agent_name='health_agent',
                            category=category.rstrip('s'),
                            item=item,
                            confidence=0.85 - (i * 0.1),  # Decreasing confidence
                            reasoning=f"Health-optimized for {user_context.activity_level} activity",
                            priority=RecommendationPriority.HIGH,
                            context_relevance=0.9,
                            temporal_weight=1.0,
                            metadata={'health_focus': True, 'activity_level': user_context.activity_level}
                        )
                        recommendations.append(rec)

            return recommendations

        except Exception as e:
            logger.error(f"Error getting health recommendations: {e}")
            return []

    async def _get_weather_recommendations(self, user_context: UserContext) -> List[AgentRecommendation]:
        """Get weather agent recommendations"""
        try:
            weather_recs = self.weather_agent.get_recommendations(
                weather_data=user_context.weather,
                time_of_day=user_context.time_of_day,
                customer_id=user_context.user_id,
                mood=user_context.mood,
                customer_history=user_context.order_history
            )

            recommendations = []
            for category, items in weather_recs.items():
                if isinstance(items, list):
                    for i, item in enumerate(items[:3]):
                        rec = AgentRecommendation(
                            agent_name='weather_agent',
                            category=category.rstrip('s'),
                            item=item,
                            confidence=0.8 - (i * 0.1),
                            reasoning=f"Weather-appropriate for {user_context.weather.get('condition', 'current')} conditions",
                            priority=RecommendationPriority.HIGH,
                            context_relevance=0.85,
                            temporal_weight=1.0,
                            metadata={'weather_condition': user_context.weather.get('condition')}
                        )
                        recommendations.append(rec)

            return recommendations

        except Exception as e:
            logger.error(f"Error getting weather recommendations: {e}")
            return []

    async def _get_learner_recommendations(self, user_context: UserContext) -> List[AgentRecommendation]:
        """Get learner agent recommendations"""
        try:
            # The learner agent learns from user feedback patterns
            user_prefs = self.learner_agent.get_user_preferences(user_context.user_id)

            recommendations = []

            # Convert learner preferences to recommendations
            for category, pref_data in user_prefs.items():
                if isinstance(pref_data, dict) and 'items' in pref_data:
                    for i, item_info in enumerate(pref_data['items'][:3]):
                        if isinstance(item_info, dict):
                            item = item_info.get('item', item_info.get('name', ''))
                            confidence = item_info.get('confidence', 0.7)
                        else:
                            item = str(item_info)
                            confidence = 0.7

                        if item:
                            rec = AgentRecommendation(
                                agent_name='learner_agent',
                                category=category.rstrip('s'),
                                item=item,
                                confidence=confidence,
                                reasoning="Based on your learning preferences and past feedback",
                                priority=RecommendationPriority.HIGH,
                                context_relevance=0.95,
                                temporal_weight=1.0,
                                metadata={'learning_based': True, 'user_feedback': True}
                            )
                            recommendations.append(rec)

            return recommendations

        except Exception as e:
            logger.error(f"Error getting learner recommendations: {e}")
            return []

    async def _get_mood_recommendations(self, user_context: UserContext) -> List[AgentRecommendation]:
        """Get mood agent recommendations"""
        return self.mood_agent.get_recommendations(user_context.mood, user_context.session_context)

    async def _get_context_recommendations(self, user_context: UserContext) -> List[AgentRecommendation]:
        """Get context agent recommendations"""
        return self.context_agent.get_recommendations(user_context)

    def _analyze_temporal_patterns(self, user_context: UserContext) -> Dict[str, Any]:
        """Analyze temporal patterns using RNN"""

        if not user_context.order_history:
            return {
                'temporal_analysis_available': False,
                'reason': 'Insufficient order history'
            }

        try:
            # Prepare sequence data
            sequence_data = self.temporal_rnn.prepare_sequence_data(user_context.order_history)

            # Prepare context features
            context_features = self._extract_context_features(user_context)

            # Get RNN predictions
            predictions = self.temporal_rnn.predict_preferences(sequence_data, context_features)

            return {
                'temporal_analysis_available': True,
                'rnn_predictions': predictions,
                'sequence_length': len(user_context.order_history),
                'pattern_confidence': predictions.get('confidence', 0.5),
                'temporal_trends': self._extract_temporal_trends(user_context.order_history)
            }

        except Exception as e:
            logger.error(f"Error in temporal analysis: {e}")
            return {
                'temporal_analysis_available': False,
                'reason': f'Analysis error: {str(e)}'
            }

    def _extract_context_features(self, user_context: UserContext) -> np.ndarray:
        """Extract numerical context features for RNN"""
        features = np.zeros(20)

        # Time features
        now = datetime.now()
        features[0] = now.hour / 24.0
        features[1] = now.weekday() / 7.0

        # Weather features (one-hot encoding)
        weather_condition = user_context.weather.get('condition', 'sunny').lower()
        weather_map = {'sunny': 2, 'rainy': 3, 'cloudy': 4, 'hot': 5, 'cold': 6}
        features[weather_map.get(weather_condition, 2)] = 1.0

        # Activity features
        activity_map = {'work': 7, 'gym': 8, 'study': 9, 'chilling': 10}
        activity_idx = activity_map.get(user_context.activity_level, 7)
        features[activity_idx] = 1.0

        # Mood features
        mood_map = {'happy': 11, 'stressed': 12, 'energetic': 13, 'relaxed': 14, 'neutral': 15}
        mood_idx = mood_map.get(user_context.mood, 15)
        features[mood_idx] = 1.0

        # History features
        features[16] = min(len(user_context.order_history) / 10.0, 1.0)  # Order history length
        features[17] = len(user_context.dietary_restrictions) / 5.0  # Dietary restrictions
        features[18] = len(user_context.allergens) / 10.0  # Allergens
        features[19] = 1.0 if user_context.location else 0.0  # Has location

        return features

    def _extract_temporal_trends(self, order_history: List[Dict]) -> Dict[str, Any]:
        """Extract temporal trends from order history"""
        if len(order_history) < 3:
            return {'trends_available': False}

        trends = {
            'trends_available': True,
            'favorite_proteins': {},
            'time_preferences': {},
            'rating_trends': []
        }

        # Analyze protein preferences over time
        for order in order_history:
            protein = order.get('protein', '')
            if protein:
                trends['favorite_proteins'][protein] = trends['favorite_proteins'].get(protein, 0) + 1

        # Analyze time preferences
        for order in order_history:
            if 'timestamp' in order:
                try:
                    dt = datetime.fromisoformat(order['timestamp'])
                    hour_group = 'morning' if dt.hour < 12 else 'afternoon' if dt.hour < 18 else 'evening'
                    trends['time_preferences'][hour_group] = trends['time_preferences'].get(hour_group, 0) + 1
                except:
                    pass

        # Rating trends
        for order in order_history[-5:]:  # Last 5 orders
            if 'rating' in order:
                trends['rating_trends'].append(order['rating'])

        return trends

    def _fuse_recommendations(
        self,
        agent_recommendations: Dict[str, List[AgentRecommendation]],
        temporal_insights: Dict[str, Any],
        user_context: UserContext
    ) -> List[AgentRecommendation]:
        """Fuse recommendations from all sources"""

        all_recommendations = []

        # Collect all recommendations
        for agent_name, recommendations in agent_recommendations.items():
            for rec in recommendations:
                # Apply agent weight
                rec.confidence *= self.agent_weights.get(agent_name, 0.5)

                # Apply temporal weighting if available
                if temporal_insights.get('temporal_analysis_available'):
                    temporal_weight = self._calculate_temporal_weight(rec, temporal_insights)
                    rec.temporal_weight = temporal_weight
                    rec.confidence *= temporal_weight

                all_recommendations.append(rec)

        # Remove duplicates and consolidate
        consolidated_recs = self._consolidate_duplicates(all_recommendations)

        return consolidated_recs

    def _calculate_temporal_weight(self, recommendation: AgentRecommendation, temporal_insights: Dict) -> float:
        """Calculate temporal weight based on RNN predictions"""

        if not temporal_insights.get('rnn_predictions'):
            return 1.0

        rnn_preds = temporal_insights['rnn_predictions']

        # Map recommendation to RNN prediction categories
        if recommendation.category == 'protein':
            # Use protein preferences from RNN
            protein_prefs = rnn_preds.get('protein_preferences', [])
            if protein_prefs:
                # Simple mapping - in practice, you'd have a proper item-to-index mapping
                avg_preference = sum(protein_prefs) / len(protein_prefs)
                return min(2.0, max(0.5, avg_preference * 2))

        elif recommendation.category == 'base':
            base_prefs = rnn_preds.get('base_preferences', [])
            if base_prefs:
                avg_preference = sum(base_prefs) / len(base_prefs)
                return min(2.0, max(0.5, avg_preference * 2))

        # Default temporal weight
        return rnn_preds.get('overall_preference_score', 0.8)

    def _consolidate_duplicates(self, recommendations: List[AgentRecommendation]) -> List[AgentRecommendation]:
        """Consolidate duplicate recommendations from multiple agents"""

        consolidated = {}

        for rec in recommendations:
            key = f"{rec.category}_{rec.item}"

            if key in consolidated:
                existing = consolidated[key]
                # Combine confidences (weighted average)
                combined_confidence = (existing.confidence + rec.confidence) / 2

                # Take the higher priority
                combined_priority = max(existing.priority, rec.priority, key=lambda x: x.value)

                # Combine reasoning
                combined_reasoning = f"{existing.reasoning}; {rec.reasoning}"

                # Update the existing recommendation
                existing.confidence = min(1.0, combined_confidence * 1.2)  # Boost for consensus
                existing.priority = combined_priority
                existing.reasoning = combined_reasoning
                existing.metadata['agent_consensus'] = existing.metadata.get('agent_consensus', []) + [rec.agent_name]

            else:
                consolidated[key] = rec
                rec.metadata['agent_consensus'] = [rec.agent_name]

        return list(consolidated.values())

    def _apply_dietary_filtering(
        self,
        recommendations: List[AgentRecommendation],
        user_context: UserContext
    ) -> List[AgentRecommendation]:
        """Apply dietary restrictions and allergen filtering"""

        if not user_context.dietary_restrictions and not user_context.allergens:
            return recommendations

        safe_recommendations = []

        for rec in recommendations:
            # Check dietary restrictions
            if user_context.dietary_restrictions:
                is_safe = self.dietary_manager.check_dietary_compliance(
                    {'item': rec.item, 'category': rec.category},
                    user_context.dietary_restrictions
                )
                if not is_safe:
                    logger.debug(f"Filtered {rec.item} due to dietary restrictions")
                    continue

            # Check allergens
            if user_context.allergens:
                contains_allergens = self.dietary_manager.check_allergen_presence(
                    rec.item,
                    user_context.allergens
                )
                if contains_allergens:
                    logger.debug(f"Filtered {rec.item} due to allergens")
                    continue

            # Add safety metadata
            rec.metadata['dietary_safe'] = True
            rec.metadata['allergen_safe'] = True
            safe_recommendations.append(rec)

        return safe_recommendations

    def _rank_and_select(
        self,
        recommendations: List[AgentRecommendation],
        n_recommendations: int,
        user_context: UserContext
    ) -> List[Dict[str, Any]]:
        """Rank and select final recommendations"""

        # Calculate final scores
        for rec in recommendations:
            rec.metadata['final_score'] = self._calculate_final_score(rec, user_context)

        # Sort by final score
        recommendations.sort(key=lambda x: x.metadata['final_score'], reverse=True)

        # Select top N and convert to dict format
        final_recs = []
        for i, rec in enumerate(recommendations[:n_recommendations]):
            final_rec = {
                'category': rec.category,
                'item': rec.item,
                'predicted_rating': min(5.0, rec.confidence * 5),
                'confidence': rec.confidence,
                'source': rec.agent_name,
                'reasoning': rec.reasoning,
                'priority': rec.priority.name,
                'temporal_weight': rec.temporal_weight,
                'context_relevance': rec.context_relevance,
                'final_score': rec.metadata['final_score'],
                'agent_consensus': rec.metadata.get('agent_consensus', []),
                'dietary_safe': rec.metadata.get('dietary_safe', True),
                'allergen_safe': rec.metadata.get('allergen_safe', True),
                'rank': i + 1,
                'recommendation_id': f"rec_{user_context.user_id}_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            final_recs.append(final_rec)

        return final_recs

    def _calculate_final_score(self, rec: AgentRecommendation, user_context: UserContext) -> float:
        """Calculate final recommendation score"""

        base_score = rec.confidence
        priority_weight = rec.priority.value
        context_weight = rec.context_relevance
        temporal_weight = rec.temporal_weight

        # Agent consensus bonus
        consensus_count = len(rec.metadata.get('agent_consensus', []))
        consensus_bonus = min(0.3, consensus_count * 0.1)

        # Safety bonus (dietary compliance)
        safety_bonus = 0.1 if rec.metadata.get('dietary_safe') and rec.metadata.get('allergen_safe') else 0

        # Final score calculation
        final_score = (
            base_score * 0.4 +
            priority_weight * 0.2 +
            context_weight * 0.2 +
            temporal_weight * 0.1 +
            consensus_bonus +
            safety_bonus
        )

        return min(1.0, final_score)

    def _calculate_overall_confidence(self, recommendations: List[Dict]) -> float:
        """Calculate overall confidence in recommendations"""
        if not recommendations:
            return 0.0

        confidences = [rec['confidence'] for rec in recommendations]
        avg_confidence = sum(confidences) / len(confidences)

        # Boost confidence if multiple agents agree
        consensus_counts = [len(rec.get('agent_consensus', [])) for rec in recommendations]
        avg_consensus = sum(consensus_counts) / len(consensus_counts)
        consensus_boost = min(0.2, (avg_consensus - 1) * 0.1)

        return min(1.0, avg_confidence + consensus_boost)

    def _generate_explanations(
        self,
        final_recommendations: List[Dict],
        agent_recommendations: Dict[str, List[AgentRecommendation]],
        temporal_insights: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate explanations for recommendations"""

        explanations = {}

        # Overall explanation
        total_agents = len([agents for agents in agent_recommendations.values() if agents])
        explanations['overview'] = (
            f"These recommendations were generated by analyzing input from {total_agents} "
            f"specialized AI agents, including health, weather, mood, learning, and context analysis. "
        )

        if temporal_insights.get('temporal_analysis_available'):
            explanations['overview'] += (
                "Advanced neural network analysis of your eating patterns was also applied. "
            )

        # Individual explanations
        for i, rec in enumerate(final_recommendations):
            agent_list = ', '.join(rec.get('agent_consensus', []))
            explanations[f'recommendation_{i+1}'] = (
                f"{rec['item']} was recommended by {agent_list}. "
                f"Reasoning: {rec['reasoning']}. "
                f"Confidence: {rec['confidence']:.2f}, Priority: {rec['priority']}"
            )

        # Temporal insights explanation
        if temporal_insights.get('temporal_analysis_available'):
            explanations['temporal_analysis'] = (
                "Your recommendation includes analysis of temporal eating patterns using "
                "recurrent neural networks that learned from your order history. "
                f"Pattern confidence: {temporal_insights.get('pattern_confidence', 0.5):.2f}"
            )

        return explanations

    def _summarize_agent_contributions(self, agent_recommendations: Dict[str, List[AgentRecommendation]]) -> Dict[str, int]:
        """Summarize contributions from each agent"""
        return {
            agent: len(recs) for agent, recs in agent_recommendations.items()
        }

    def _get_fallback_recommendations(self, n_recommendations: int) -> Dict[str, Any]:
        """Fallback recommendations when system fails"""

        fallback_recs = [
            {
                'category': 'protein',
                'item': 'Chicken',
                'predicted_rating': 4.5,
                'confidence': 0.8,
                'source': 'fallback_system',
                'reasoning': 'Popular and safe choice when personalization is unavailable',
                'priority': 'HIGH',
                'rank': 1
            },
            {
                'category': 'base',
                'item': 'Rice Bowl',
                'predicted_rating': 4.3,
                'confidence': 0.7,
                'source': 'fallback_system',
                'reasoning': 'Customer favorite base option',
                'priority': 'MEDIUM',
                'rank': 2
            },
            {
                'category': 'sauce',
                'item': 'Curry Special',
                'predicted_rating': 4.4,
                'confidence': 0.8,
                'source': 'fallback_system',
                'reasoning': 'Signature sauce with broad appeal',
                'priority': 'MEDIUM',
                'rank': 3
            }
        ]

        return {
            'success': True,
            'recommendations': fallback_recs[:n_recommendations],
            'explanations': {'overview': 'Default recommendations provided when personalization is unavailable'},
            'confidence': 0.6,
            'agent_contributions': {'fallback_system': len(fallback_recs)},
            'temporal_insights': {'temporal_analysis_available': False},
            'dietary_filtering_applied': False,
            'processing_time_ms': 10,
            'total_agents_consulted': 0,
            'recommendation_method': 'fallback',
            'timestamp': datetime.now().isoformat()
        }

    async def update_user_feedback(
        self,
        user_id: str,
        recommendation_id: str,
        feedback: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Update system with user feedback for continuous learning"""

        try:
            # Update learner agent
            learner_result = self.learner_agent.process_feedback(
                recommendation_type='master_coordinator',
                feedback=feedback,
                customer_id=user_id,
                context=context or {}
            )

            # TODO: Update RNN model with feedback (requires training data preparation)
            # This would involve retraining the RNN with new feedback data

            return {
                'success': True,
                'feedback_processed': True,
                'learner_updated': learner_result.get('processed', False),
                'recommendation_id': recommendation_id,
                'message': f'Successfully processed {feedback} feedback'
            }

        except Exception as e:
            logger.error(f"Error updating user feedback: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendation_id': recommendation_id
            }