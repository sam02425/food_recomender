"""
Collaborative Filtering System for Food Recommendations
Implements user-based and item-based collaborative filtering
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF
from surprise import Dataset, Reader, SVD, accuracy
from surprise.model_selection import train_test_split
import joblib
import logging
from typing import Dict, List, Tuple, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollaborativeFilteringEngine:
    def __init__(self, model_path: str = "models/cf_model.joblib"):
        self.model_path = model_path
        self.user_item_matrix = None
        self.item_features = None
        self.user_features = None
        self.svd_model = None
        self.nmf_model = None
        self.item_similarity_matrix = None
        self.user_similarity_matrix = None

        # Initialize with sample data structure
        self.initialize_models()

    def initialize_models(self):
        """Initialize models with default configuration"""
        try:
            self.load_models()
        except FileNotFoundError:
            logger.info("No existing models found. Initializing new models.")
            self.create_default_models()

    def create_default_models(self):
        """Create default models with sample data"""
        # Sample user-item interactions (user_id, item_combination, rating)
        sample_data = [
            (1, "Chicken-Rice_Bowl-Curry_Special", 5),
            (1, "Paneer-Naan_Wrap-Malai_Masala", 4),
            (2, "Chicken-Rice_Bowl-Curry_Special", 4),
            (2, "Egg-Salad_Bowl-Yogurt_Raita", 5),
            (3, "Paneer-Rice_Bowl-Malai_Masala", 5),
            (3, "Soya-Salad_Bowl-Green_Spicy", 3),
            (4, "Chicken-Biryani-Curry_Masala", 4),
            (4, "Pepperoni-Naan_Wrap-Curry_Special", 3),
            (5, "Egg-Rice_Bowl-Curry_Special", 4),
            (5, "Paneer-Salad_Bowl-Malai_Masala", 5),
        ]

        df = pd.DataFrame(sample_data, columns=['user_id', 'item_combo', 'rating'])
        self.train_models(df)

    def preprocess_order_data(self, orders_data: List[Dict]) -> pd.DataFrame:
        """Convert order data to user-item matrix format"""
        processed_data = []

        for order in orders_data:
            user_id = order.get('customer_id', order.get('user_id'))
            if not user_id:
                continue

            # Create item combination string
            protein = order.get('selected_protein', 'Unknown')
            base = order.get('selected_base', 'Unknown')
            sauce = order.get('selected_sauce', 'Unknown')

            item_combo = f"{protein}-{base}-{sauce}"

            # Use explicit rating if available, otherwise infer from completion
            rating = order.get('rating', 4 if order.get('completed', True) else 2)

            processed_data.append({
                'user_id': user_id,
                'item_combo': item_combo,
                'rating': rating,
                'timestamp': order.get('timestamp', ''),
                'mood': order.get('mood', 'neutral'),
                'activity': order.get('activity', 'unknown')
            })

        return pd.DataFrame(processed_data)

    def train_models(self, df: pd.DataFrame):
        """Train collaborative filtering models"""
        logger.info("Training collaborative filtering models...")

        # Create user-item matrix
        self.user_item_matrix = df.pivot_table(
            index='user_id',
            columns='item_combo',
            values='rating',
            fill_value=0
        )

        # Train SVD model using Surprise library
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(df[['user_id', 'item_combo', 'rating']], reader)
        trainset, testset = train_test_split(data, test_size=.25)

        self.svd_model = SVD(n_factors=10, random_state=42)
        self.svd_model.fit(trainset)

        # Calculate accuracy
        predictions = self.svd_model.test(testset)
        rmse = accuracy.rmse(predictions, verbose=False)
        logger.info(f"SVD Model RMSE: {rmse}")

        # Train NMF model for implicit feedback
        if len(self.user_item_matrix) > 0:
            self.nmf_model = NMF(n_components=5, random_state=42)
            self.nmf_model.fit(self.user_item_matrix.fillna(0))

        # Calculate similarity matrices
        self.calculate_similarity_matrices()

        # Save models
        self.save_models()

        logger.info("Collaborative filtering models trained successfully")

    def calculate_similarity_matrices(self):
        """Calculate user and item similarity matrices"""
        if self.user_item_matrix is not None and len(self.user_item_matrix) > 1:
            # User similarity
            self.user_similarity_matrix = cosine_similarity(
                self.user_item_matrix.fillna(0)
            )

            # Item similarity
            self.item_similarity_matrix = cosine_similarity(
                self.user_item_matrix.fillna(0).T
            )

    def get_user_recommendations(self, user_id: int, n_recommendations: int = 5) -> List[Dict]:
        """Get recommendations for a specific user"""
        try:
            if self.svd_model is None:
                return self.get_fallback_recommendations(n_recommendations)

            # Get all possible items
            if self.user_item_matrix is not None:
                all_items = self.user_item_matrix.columns.tolist()
            else:
                all_items = [
                    "Chicken-Rice_Bowl-Curry_Special",
                    "Paneer-Naan_Wrap-Malai_Masala",
                    "Egg-Salad_Bowl-Yogurt_Raita"
                ]

            # Get user's rated items
            user_rated_items = set()
            if self.user_item_matrix is not None and user_id in self.user_item_matrix.index:
                user_rated_items = set(
                    self.user_item_matrix.loc[user_id][
                        self.user_item_matrix.loc[user_id] > 0
                    ].index
                )

            # Get predictions for unrated items
            recommendations = []
            for item in all_items:
                if item not in user_rated_items:
                    prediction = self.svd_model.predict(user_id, item)

                    # Parse item combination
                    parts = item.split('-')
                    protein = parts[0] if len(parts) > 0 else "Chicken"
                    base = parts[1] if len(parts) > 1 else "Rice_Bowl"
                    sauce = parts[2] if len(parts) > 2 else "Curry_Special"

                    recommendations.append({
                        'protein': protein.replace('_', '/'),
                        'base': base.replace('_', ' '),
                        'sauce': sauce.replace('_', ' '),
                        'predicted_rating': prediction.est,
                        'confidence': min(prediction.est / 5.0, 1.0),
                        'reason': f"Based on similar users' preferences (predicted rating: {prediction.est:.2f})"
                    })

            # Sort by predicted rating and return top N
            recommendations.sort(key=lambda x: x['predicted_rating'], reverse=True)
            return recommendations[:n_recommendations]

        except Exception as e:
            logger.error(f"Error generating user recommendations: {e}")
            return self.get_fallback_recommendations(n_recommendations)

    def get_similar_users(self, user_id: int, n_users: int = 5) -> List[int]:
        """Find users similar to the given user"""
        if (self.user_similarity_matrix is None or
            self.user_item_matrix is None or
            user_id not in self.user_item_matrix.index):
            return []

        user_idx = list(self.user_item_matrix.index).index(user_id)
        similarities = self.user_similarity_matrix[user_idx]

        # Get indices of most similar users (excluding self)
        similar_indices = np.argsort(similarities)[::-1][1:n_users+1]
        similar_users = [self.user_item_matrix.index[idx] for idx in similar_indices]

        return similar_users

    def get_item_based_recommendations(self, user_id: int, n_recommendations: int = 5) -> List[Dict]:
        """Get recommendations based on item similarity"""
        try:
            if (self.item_similarity_matrix is None or
                self.user_item_matrix is None or
                user_id not in self.user_item_matrix.index):
                return self.get_fallback_recommendations(n_recommendations)

            user_ratings = self.user_item_matrix.loc[user_id]
            liked_items = user_ratings[user_ratings >= 4].index.tolist()

            if not liked_items:
                return self.get_fallback_recommendations(n_recommendations)

            # Calculate item-based scores
            item_scores = {}
            for item in self.user_item_matrix.columns:
                if user_ratings[item] == 0:  # Unrated item
                    score = 0
                    for liked_item in liked_items:
                        if liked_item in self.user_item_matrix.columns:
                            item_idx = list(self.user_item_matrix.columns).index(item)
                            liked_idx = list(self.user_item_matrix.columns).index(liked_item)
                            similarity = self.item_similarity_matrix[item_idx][liked_idx]
                            score += similarity * user_ratings[liked_item]

                    if score > 0:
                        item_scores[item] = score

            # Convert to recommendations format
            recommendations = []
            sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)

            for item, score in sorted_items[:n_recommendations]:
                parts = item.split('-')
                protein = parts[0] if len(parts) > 0 else "Chicken"
                base = parts[1] if len(parts) > 1 else "Rice_Bowl"
                sauce = parts[2] if len(parts) > 2 else "Curry_Special"

                recommendations.append({
                    'protein': protein.replace('_', '/'),
                    'base': base.replace('_', ' '),
                    'sauce': sauce.replace('_', ' '),
                    'predicted_rating': min(score, 5.0),
                    'confidence': min(score / 5.0, 1.0),
                    'reason': f"Similar to items you liked (similarity score: {score:.2f})"
                })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating item-based recommendations: {e}")
            return self.get_fallback_recommendations(n_recommendations)

    def get_fallback_recommendations(self, n_recommendations: int = 5) -> List[Dict]:
        """Fallback recommendations when ML models fail"""
        fallback_recs = [
            {
                'protein': 'Chicken',
                'base': 'Rice Bowl',
                'sauce': 'Curry Special',
                'predicted_rating': 4.5,
                'confidence': 0.8,
                'reason': 'Popular choice among all users'
            },
            {
                'protein': 'Paneer/Indian Cheese',
                'base': 'Naan Wrap',
                'sauce': 'Malai Masala',
                'predicted_rating': 4.3,
                'confidence': 0.7,
                'reason': 'Highly rated vegetarian option'
            },
            {
                'protein': 'Egg',
                'base': 'Salad Bowl',
                'sauce': 'Yogurt/Raita',
                'predicted_rating': 4.0,
                'confidence': 0.6,
                'reason': 'Healthy and balanced choice'
            }
        ]
        return fallback_recs[:n_recommendations]

    def update_with_feedback(self, user_id: int, item_combo: str, rating: float, feedback_text: str = ""):
        """Update models with new user feedback"""
        try:
            # Add new data point
            new_data = pd.DataFrame([{
                'user_id': user_id,
                'item_combo': item_combo,
                'rating': rating
            }])

            # Retrain with new data (in production, you'd want incremental learning)
            if self.user_item_matrix is not None:
                existing_data = []
                for user in self.user_item_matrix.index:
                    for item in self.user_item_matrix.columns:
                        rating_val = self.user_item_matrix.loc[user, item]
                        if rating_val > 0:
                            existing_data.append({
                                'user_id': user,
                                'item_combo': item,
                                'rating': rating_val
                            })

                combined_data = pd.concat([
                    pd.DataFrame(existing_data),
                    new_data
                ], ignore_index=True)

                self.train_models(combined_data)

            logger.info(f"Updated model with feedback from user {user_id}")

        except Exception as e:
            logger.error(f"Error updating model with feedback: {e}")

    def save_models(self):
        """Save trained models to disk"""
        try:
            model_data = {
                'user_item_matrix': self.user_item_matrix,
                'svd_model': self.svd_model,
                'nmf_model': self.nmf_model,
                'user_similarity_matrix': self.user_similarity_matrix,
                'item_similarity_matrix': self.item_similarity_matrix
            }
            joblib.dump(model_data, self.model_path)
            logger.info(f"Models saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving models: {e}")

    def load_models(self):
        """Load trained models from disk"""
        try:
            model_data = joblib.load(self.model_path)
            self.user_item_matrix = model_data['user_item_matrix']
            self.svd_model = model_data['svd_model']
            self.nmf_model = model_data['nmf_model']
            self.user_similarity_matrix = model_data['user_similarity_matrix']
            self.item_similarity_matrix = model_data['item_similarity_matrix']
            logger.info(f"Models loaded from {self.model_path}")
        except FileNotFoundError:
            raise FileNotFoundError("No saved models found")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise