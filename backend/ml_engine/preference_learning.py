"""
Preference Learning System for Real-time User Preference Discovery
Integrates with existing agents and provides ML-based preference learning
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreferenceLearningAgent:
    def __init__(self, model_path: str = "models/preference_learning.joblib"):
        self.model_path = model_path
        self.preference_models = {}
        self.user_embeddings = {}
        self.item_embeddings = {}
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.user_clusters = None
        self.preference_history = []

        # Initialize models
        self.initialize_models()

    def initialize_models(self):
        """Initialize preference learning models"""
        logger.info("Initializing preference learning models...")

        # Model for each food category
        self.preference_models = {
            'protein': {
                'model': RandomForestRegressor(n_estimators=50, random_state=42),
                'features': ['activity_level', 'mood', 'time_of_day', 'weather', 'previous_choices'],
                'trained': False
            },
            'base': {
                'model': RandomForestRegressor(n_estimators=50, random_state=42),
                'features': ['activity_level', 'mood', 'time_of_day', 'weather', 'previous_choices'],
                'trained': False
            },
            'sauce': {
                'model': RandomForestRegressor(n_estimators=50, random_state=42),
                'features': ['activity_level', 'mood', 'time_of_day', 'weather', 'previous_choices'],
                'trained': False
            },
            'vegetables': {
                'model': RandomForestRegressor(n_estimators=50, random_state=42),
                'features': ['activity_level', 'mood', 'time_of_day', 'weather', 'previous_choices'],
                'trained': False
            },
            'garnishes': {
                'model': RandomForestRegressor(n_estimators=50, random_state=42),
                'features': ['activity_level', 'mood', 'time_of_day', 'weather', 'previous_choices'],
                'trained': False
            }
        }

        # Initialize label encoders for categorical features
        self.label_encoders = {
            'activity_level': LabelEncoder(),
            'mood': LabelEncoder(),
            'time_of_day': LabelEncoder(),
            'weather': LabelEncoder(),
            'protein': LabelEncoder(),
            'base': LabelEncoder(),
            'sauce': LabelEncoder()
        }

        # Try to load existing models
        try:
            self.load_models()
        except FileNotFoundError:
            logger.info("No existing models found. Starting with fresh models.")

    def process_user_interaction(self, user_id: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user interaction and update preference models"""
        try:
            # Extract features from interaction
            features = self._extract_features(interaction_data)

            # Record interaction for training
            interaction_record = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'features': features,
                'selections': interaction_data.get('selections', {}),
                'feedback': interaction_data.get('feedback', {}),
                'ratings': interaction_data.get('ratings', {})
            }

            self.preference_history.append(interaction_record)

            # Update user embeddings
            self._update_user_embeddings(user_id, features, interaction_data)

            # Train models if enough data
            if len(self.preference_history) >= 10:
                self._retrain_models()

            # Generate updated preferences
            preferences = self.get_user_preferences(user_id)

            return {
                'success': True,
                'preferences_updated': True,
                'user_preferences': preferences,
                'model_version': self._get_model_version()
            }

        except Exception as e:
            logger.error(f"Error processing user interaction: {e}")
            return {'success': False, 'error': str(e)}

    def _extract_features(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ML features from interaction data"""
        features = {}

        # Basic context features
        features['activity_level'] = interaction_data.get('activity_level', 'unknown')
        features['mood'] = interaction_data.get('mood', 'neutral')
        features['time_of_day'] = self._get_time_of_day()
        features['weather'] = interaction_data.get('weather', {}).get('condition', 'unknown')

        # User history features
        features['previous_choices'] = len(interaction_data.get('order_history', []))
        features['avg_session_duration'] = interaction_data.get('session_duration', 0)
        features['completion_rate'] = interaction_data.get('completion_rate', 1.0)

        # Preference indicators
        selections = interaction_data.get('selections', {})
        features['protein_choice'] = selections.get('protein', 'unknown')
        features['base_choice'] = selections.get('base', 'unknown')
        features['sauce_choice'] = selections.get('sauce', 'unknown')

        # Interaction patterns
        features['recommendation_acceptance'] = interaction_data.get('accepted_recommendations', 0)
        features['custom_choices'] = interaction_data.get('custom_choices', 0)

        return features

    def _get_time_of_day(self) -> str:
        """Get current time of day category"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 22:
            return 'evening'
        else:
            return 'night'

    def _update_user_embeddings(self, user_id: str, features: Dict[str, Any], interaction_data: Dict[str, Any]):
        """Update user embedding based on new interaction"""
        if user_id not in self.user_embeddings:
            self.user_embeddings[user_id] = {
                'feature_vector': np.zeros(20),  # 20-dimensional embedding
                'interaction_count': 0,
                'last_updated': datetime.now(),
                'preference_scores': {}
            }

        embedding = self.user_embeddings[user_id]

        # Update feature vector (exponential moving average)
        alpha = 0.3  # Learning rate
        new_features = self._vectorize_features(features)
        if len(new_features) == len(embedding['feature_vector']):
            embedding['feature_vector'] = (1 - alpha) * embedding['feature_vector'] + alpha * new_features

        embedding['interaction_count'] += 1
        embedding['last_updated'] = datetime.now()

        # Update preference scores based on feedback
        feedback = interaction_data.get('feedback', {})
        for category, rating in feedback.items():
            if category not in embedding['preference_scores']:
                embedding['preference_scores'][category] = []
            embedding['preference_scores'][category].append(rating)

    def _vectorize_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Convert features to numerical vector"""
        vector = np.zeros(20)

        # Activity level encoding
        activity_map = {'study': 0, 'work': 1, 'active': 2, 'gym': 3, 'chilling': 4}
        vector[0] = activity_map.get(features.get('activity_level'), 0)

        # Mood encoding
        mood_map = {'happy': 1, 'excited': 2, 'focused': 3, 'relaxed': 4, 'neutral': 0}
        vector[1] = mood_map.get(features.get('mood'), 0)

        # Time of day encoding
        time_map = {'morning': 0, 'afternoon': 1, 'evening': 2, 'night': 3}
        vector[2] = time_map.get(features.get('time_of_day'), 0)

        # Weather encoding
        weather_map = {'sunny': 0, 'rainy': 1, 'cloudy': 2, 'hot': 3, 'cold': 4}
        vector[3] = weather_map.get(features.get('weather'), 0)

        # Numerical features
        vector[4] = min(features.get('previous_choices', 0) / 10, 1)  # Normalized
        vector[5] = min(features.get('avg_session_duration', 0) / 300, 1)  # Normalized to 5 minutes
        vector[6] = features.get('completion_rate', 1.0)
        vector[7] = min(features.get('recommendation_acceptance', 0) / 5, 1)
        vector[8] = min(features.get('custom_choices', 0) / 5, 1)

        # Add some random dimensions for future features
        vector[9:] = np.random.normal(0, 0.1, 11)

        return vector

    def _retrain_models(self):
        """Retrain preference models with accumulated data"""
        logger.info("Retraining preference models...")

        try:
            # Prepare training data
            training_data = self._prepare_training_data()

            if len(training_data) < 5:  # Need minimum data
                return

            # Train models for each category
            for category in ['protein', 'base', 'sauce', 'vegetables', 'garnishes']:
                if category in training_data:
                    X, y = training_data[category]
                    if len(X) > 0 and len(y) > 0:
                        model = self.preference_models[category]['model']
                        model.fit(X, y)
                        self.preference_models[category]['trained'] = True
                        logger.info(f"Trained {category} preference model with {len(X)} samples")

            # Update user clusters
            self._update_user_clusters()

            # Save models
            self.save_models()

        except Exception as e:
            logger.error(f"Error retraining models: {e}")

    def _prepare_training_data(self) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """Prepare training data from interaction history"""
        training_data = {}

        for category in ['protein', 'base', 'sauce', 'vegetables', 'garnishes']:
            X_list = []
            y_list = []

            for interaction in self.preference_history:
                features = interaction['features']
                feedback = interaction.get('feedback', {})
                ratings = interaction.get('ratings', {})

                # Create feature vector
                feature_vector = self._create_feature_vector(features)

                # Get target (rating or implicit feedback)
                target = None
                if category in ratings:
                    target = ratings[category]
                elif category in feedback:
                    # Convert feedback to numerical rating
                    feedback_val = feedback[category]
                    if feedback_val == 'accept':
                        target = 5
                    elif feedback_val == 'ignore':
                        target = 2
                    elif feedback_val == 'custom':
                        target = 3

                if target is not None:
                    X_list.append(feature_vector)
                    y_list.append(target)

            if X_list:
                training_data[category] = (np.array(X_list), np.array(y_list))

        return training_data

    def _create_feature_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """Create feature vector for ML models"""
        vector = []

        # Categorical features (encoded)
        for cat_feature in ['activity_level', 'mood', 'time_of_day', 'weather']:
            value = features.get(cat_feature, 'unknown')
            if cat_feature in self.label_encoders:
                try:
                    encoded = self.label_encoders[cat_feature].transform([value])[0]
                except:
                    # Handle unseen categories
                    encoded = 0
            else:
                encoded = 0
            vector.append(encoded)

        # Numerical features
        vector.extend([
            features.get('previous_choices', 0),
            features.get('avg_session_duration', 0),
            features.get('completion_rate', 1.0),
            features.get('recommendation_acceptance', 0),
            features.get('custom_choices', 0)
        ])

        return np.array(vector)

    def _update_user_clusters(self):
        """Update user clusters based on embeddings"""
        if len(self.user_embeddings) < 3:
            return

        try:
            # Get all user embeddings
            embeddings = []
            user_ids = []

            for user_id, embedding_data in self.user_embeddings.items():
                embeddings.append(embedding_data['feature_vector'])
                user_ids.append(user_id)

            embeddings = np.array(embeddings)

            # Apply clustering
            clustering = DBSCAN(eps=0.5, min_samples=2)
            cluster_labels = clustering.fit_predict(embeddings)

            # Store cluster information
            self.user_clusters = {
                'labels': dict(zip(user_ids, cluster_labels)),
                'n_clusters': len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0),
                'updated_at': datetime.now()
            }

            logger.info(f"Updated user clusters: {self.user_clusters['n_clusters']} clusters")

        except Exception as e:
            logger.error(f"Error updating user clusters: {e}")

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get learned preferences for a user"""
        if user_id not in self.user_embeddings:
            return self._get_default_preferences()

        embedding = self.user_embeddings[user_id]
        preferences = {
            'user_id': user_id,
            'interaction_count': embedding['interaction_count'],
            'last_updated': embedding['last_updated'].isoformat(),
            'confidence': min(embedding['interaction_count'] / 10, 1.0),
            'categories': {}
        }

        # Get preferences for each category
        for category in ['protein', 'base', 'sauce', 'vegetables', 'garnishes']:
            preferences['categories'][category] = self._get_category_preferences(user_id, category)

        # Add cluster information
        if self.user_clusters and user_id in self.user_clusters['labels']:
            preferences['cluster'] = self.user_clusters['labels'][user_id]
            preferences['similar_users'] = self._get_similar_users(user_id)

        return preferences

    def _get_category_preferences(self, user_id: str, category: str) -> Dict[str, Any]:
        """Get preferences for a specific category"""
        model_info = self.preference_models.get(category)
        if not model_info or not model_info['trained']:
            return {'items': [], 'confidence': 0.0, 'method': 'default'}

        embedding = self.user_embeddings[user_id]

        # Create feature vector for prediction
        current_features = {
            'activity_level': 'work',  # Default context
            'mood': 'neutral',
            'time_of_day': self._get_time_of_day(),
            'weather': 'sunny',
            'previous_choices': embedding['interaction_count'],
            'avg_session_duration': 120,
            'completion_rate': 1.0,
            'recommendation_acceptance': 3,
            'custom_choices': 1
        }

        feature_vector = self._create_feature_vector(current_features)

        try:
            # Predict preference score
            model = model_info['model']
            predicted_score = model.predict([feature_vector])[0]

            # Get category-specific recommendations
            items = self._get_category_items(category, predicted_score)

            return {
                'items': items,
                'predicted_score': float(predicted_score),
                'confidence': min(embedding['interaction_count'] / 5, 1.0),
                'method': 'ml_prediction'
            }

        except Exception as e:
            logger.error(f"Error getting {category} preferences: {e}")
            return {'items': [], 'confidence': 0.0, 'method': 'error'}

    def _get_category_items(self, category: str, predicted_score: float) -> List[Dict[str, Any]]:
        """Get recommended items for a category based on predicted score"""
        # Map categories to actual menu items
        menu_items = {
            'protein': [
                {'item': 'Chicken', 'base_score': 4.5},
                {'item': 'Paneer/Indian Cheese', 'base_score': 4.2},
                {'item': 'Egg', 'base_score': 4.0},
                {'item': 'Soya', 'base_score': 3.8},
                {'item': 'Potato', 'base_score': 3.5}
            ],
            'base': [
                {'item': 'Rice Bowl', 'base_score': 4.3},
                {'item': 'Naan Wrap', 'base_score': 4.1},
                {'item': 'Salad Bowl', 'base_score': 3.9},
                {'item': 'Biryani', 'base_score': 4.4}
            ],
            'sauce': [
                {'item': 'Curry Special', 'base_score': 4.4},
                {'item': 'Malai Masala', 'base_score': 4.2},
                {'item': 'Green Spicy Sauce', 'base_score': 4.0},
                {'item': 'Yogurt/Raita', 'base_score': 3.8},
                {'item': 'Curry Masala', 'base_score': 4.1}
            ],
            'vegetables': [
                {'item': 'Red Onion', 'base_score': 4.0},
                {'item': 'Bell Pepper', 'base_score': 3.9},
                {'item': 'Spinach', 'base_score': 3.7},
                {'item': 'Tomato', 'base_score': 4.1},
                {'item': 'Corn', 'base_score': 3.8}
            ],
            'garnishes': [
                {'item': 'Cilantro', 'base_score': 4.0},
                {'item': 'Almonds', 'base_score': 3.8},
                {'item': 'Pomegranate', 'base_score': 3.6}
            ]
        }

        items = menu_items.get(category, [])

        # Adjust scores based on prediction
        for item in items:
            # Combine base score with predicted preference
            adjusted_score = (item['base_score'] + predicted_score) / 2
            item['predicted_rating'] = max(1.0, min(5.0, adjusted_score))
            item['confidence'] = abs(predicted_score - 3) / 2  # Higher confidence for stronger predictions

        # Sort by predicted rating
        items.sort(key=lambda x: x['predicted_rating'], reverse=True)

        return items[:3]  # Return top 3

    def _get_similar_users(self, user_id: str) -> List[str]:
        """Get users in the same cluster"""
        if not self.user_clusters or user_id not in self.user_clusters['labels']:
            return []

        user_cluster = self.user_clusters['labels'][user_id]
        if user_cluster == -1:  # Noise point
            return []

        similar_users = [
            uid for uid, cluster in self.user_clusters['labels'].items()
            if cluster == user_cluster and uid != user_id
        ]

        return similar_users[:5]  # Return top 5 similar users

    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default preferences for new users"""
        return {
            'user_id': 'unknown',
            'interaction_count': 0,
            'confidence': 0.0,
            'categories': {
                'protein': {'items': [{'item': 'Chicken', 'predicted_rating': 4.0, 'confidence': 0.5}], 'method': 'default'},
                'base': {'items': [{'item': 'Rice Bowl', 'predicted_rating': 4.0, 'confidence': 0.5}], 'method': 'default'},
                'sauce': {'items': [{'item': 'Curry Special', 'predicted_rating': 4.0, 'confidence': 0.5}], 'method': 'default'},
                'vegetables': {'items': [{'item': 'Red Onion', 'predicted_rating': 4.0, 'confidence': 0.5}], 'method': 'default'},
                'garnishes': {'items': [{'item': 'Cilantro', 'predicted_rating': 4.0, 'confidence': 0.5}], 'method': 'default'}
            }
        }

    def get_collaborative_recommendations(self, user_id: str, n_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get recommendations based on similar users"""
        similar_users = self._get_similar_users(user_id)
        if not similar_users:
            return []

        # Aggregate preferences from similar users
        category_scores = {}

        for similar_user in similar_users:
            if similar_user in self.user_embeddings:
                user_prefs = self.user_embeddings[similar_user].get('preference_scores', {})

                for category, scores in user_prefs.items():
                    if scores:
                        avg_score = sum(scores) / len(scores)
                        if category not in category_scores:
                            category_scores[category] = []
                        category_scores[category].append(avg_score)

        # Generate recommendations
        recommendations = []
        for category, scores in category_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                items = self._get_category_items(category, avg_score)

                for item in items[:2]:  # Top 2 per category
                    recommendations.append({
                        'category': category,
                        'item': item['item'],
                        'predicted_rating': item['predicted_rating'],
                        'confidence': item['confidence'],
                        'reason': f"Popular among similar users (cluster similarity)"
                    })

        # Sort by predicted rating and return top N
        recommendations.sort(key=lambda x: x['predicted_rating'], reverse=True)
        return recommendations[:n_recommendations]

    def _get_model_version(self) -> str:
        """Get current model version identifier"""
        return f"v1.0_{datetime.now().strftime('%Y%m%d_%H%M')}"

    def save_models(self):
        """Save trained models and data"""
        try:
            model_data = {
                'preference_models': self.preference_models,
                'user_embeddings': self.user_embeddings,
                'user_clusters': self.user_clusters,
                'label_encoders': self.label_encoders,
                'preference_history': self.preference_history[-1000:],  # Keep last 1000
                'version': self._get_model_version(),
                'saved_at': datetime.now().isoformat()
            }

            joblib.dump(model_data, self.model_path)
            logger.info(f"Preference models saved to {self.model_path}")

        except Exception as e:
            logger.error(f"Error saving models: {e}")

    def load_models(self):
        """Load trained models and data"""
        try:
            model_data = joblib.load(self.model_path)

            self.preference_models = model_data.get('preference_models', {})
            self.user_embeddings = model_data.get('user_embeddings', {})
            self.user_clusters = model_data.get('user_clusters')
            self.label_encoders = model_data.get('label_encoders', {})
            self.preference_history = model_data.get('preference_history', [])

            logger.info(f"Preference models loaded from {self.model_path}")

        except FileNotFoundError:
            raise FileNotFoundError("No saved models found")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about the models"""
        stats = {
            'total_users': len(self.user_embeddings),
            'total_interactions': len(self.preference_history),
            'trained_models': sum(1 for model in self.preference_models.values() if model['trained']),
            'clusters': self.user_clusters['n_clusters'] if self.user_clusters else 0,
            'model_version': self._get_model_version()
        }

        # Add per-category stats
        for category, model_info in self.preference_models.items():
            stats[f'{category}_trained'] = model_info['trained']

        return stats