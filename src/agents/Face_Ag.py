# /agents/Face_Ag.py
"""
Enhanced Face Recognition Agent for customer identification, login authentication,
and real-time mood tracking for feedback purposes.
"""

import os
import csv
import time
import json
import logging
import uuid
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import base64
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("face_recognition_agent")

class EnhancedFaceRecognitionAgent:
    """Enhanced agent for face recognition, login authentication, and real-time mood tracking."""

    def __init__(self, customer_data_path: str, face_images_dir: str):
        """
        Initialize the enhanced face recognition agent.

        Args:
            customer_data_path: Path to customer data CSV
            face_images_dir: Directory to store face images
        """
        self.customer_data_path = customer_data_path
        self.face_images_dir = face_images_dir
        self.recognition_threshold = 0.65  # Similarity threshold
        self.mood_history_path = os.path.join(face_images_dir, "mood_history.csv")

        # Ensure directories exist
        os.makedirs(self.face_images_dir, exist_ok=True)

        # Load face encodings if available
        self.face_encodings = self._load_face_encodings()

        # Enhanced mood detection with feedback analysis
        self.moods = {
            "happy": {"valence": 0.8, "arousal": 0.6, "feedback": "positive"},
            "excited": {"valence": 0.9, "arousal": 0.9, "feedback": "very_positive"},
            "satisfied": {"valence": 0.7, "arousal": 0.4, "feedback": "positive"},
            "neutral": {"valence": 0.5, "arousal": 0.5, "feedback": "neutral"},
            "confused": {"valence": 0.4, "arousal": 0.6, "feedback": "negative"},
            "disappointed": {"valence": 0.3, "arousal": 0.4, "feedback": "negative"},
            "angry": {"valence": 0.2, "arousal": 0.8, "feedback": "very_negative"},
            "frustrated": {"valence": 0.3, "arousal": 0.7, "feedback": "negative"},
            "surprised": {"valence": 0.6, "arousal": 0.8, "feedback": "neutral"},
            "tired": {"valence": 0.4, "arousal": 0.2, "feedback": "neutral"},
            "stressed": {"valence": 0.3, "arousal": 0.7, "feedback": "negative"}
        }

        # Real-time mood tracking state
        self.current_session_moods = {}
        self.recommendation_feedback = {}

        # Initialize mood history CSV
        self._initialize_mood_history()

        logger.info(f"Enhanced face recognition agent initialized with {len(self.face_encodings)} face encodings")

    def _initialize_mood_history(self):
        """Initialize mood history CSV file if it doesn't exist."""
        if not os.path.exists(self.mood_history_path):
            with open(self.mood_history_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp', 'customer_id', 'face_id', 'mood',
                    'valence', 'arousal', 'confidence', 'context',
                    'recommendation_type', 'feedback_type'
                ])

    def authenticate_customer(self, image_data: bytes) -> Dict[str, Any]:
        """
        Authenticate a customer using face recognition for login purposes.

        Args:
            image_data: Binary image data from camera

        Returns:
            Authentication result with customer details
        """
        try:
            recognition_result = self.recognize_face(image_data)

            if recognition_result.get("recognized"):
                customer_id = recognition_result["customer_id"]
                face_id = recognition_result["face_id"]

                # Load customer profile
                customer_profile = self._get_customer_profile(customer_id)

                # Initialize mood tracking session
                self.current_session_moods[customer_id] = {
                    "session_start": datetime.now().isoformat(),
                    "face_id": face_id,
                    "mood_samples": [],
                    "recommendation_reactions": []
                }

                logger.info(f"Customer authenticated: {customer_id}")

                return {
                    "authenticated": True,
                    "customer_id": customer_id,
                    "face_id": face_id,
                    "customer_profile": customer_profile,
                    "confidence": recognition_result["confidence"],
                    "session_id": f"session_{uuid.uuid4().hex[:8]}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "authenticated": False,
                    "new_customer": True,
                    "confidence": recognition_result.get("confidence", 0.0),
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {
                "authenticated": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def track_real_time_mood(self, image_data: bytes, customer_id: str = None,
                           context: str = "general") -> Dict[str, Any]:
        """
        Track customer mood in real-time for feedback analysis.

        Args:
            image_data: Binary image data from camera
            customer_id: Customer ID if known
            context: Context like 'viewing_recommendations', 'making_choice', etc.

        Returns:
            Real-time mood analysis with feedback interpretation
        """
        try:
            # Analyze current mood
            mood_result = self.analyze_mood(image_data)

            if not mood_result.get("success"):
                return mood_result

            mood = mood_result["mood"]
            confidence = mood_result["confidence"]
            mood_data = self.moods[mood]

            # Interpret feedback based on mood and context
            feedback_interpretation = self._interpret_mood_feedback(mood, context, confidence)

            # Store mood sample if we have customer_id
            if customer_id and customer_id in self.current_session_moods:
                mood_sample = {
                    "timestamp": datetime.now().isoformat(),
                    "mood": mood,
                    "confidence": confidence,
                    "context": context,
                    "feedback_type": feedback_interpretation["feedback_type"],
                    "valence": mood_data["valence"],
                    "arousal": mood_data["arousal"]
                }

                self.current_session_moods[customer_id]["mood_samples"].append(mood_sample)

                # Save to mood history
                self._save_mood_to_history(customer_id, mood_sample)

            return {
                "success": True,
                "mood": mood,
                "confidence": confidence,
                "feedback_interpretation": feedback_interpretation,
                "mood_data": mood_data,
                "context": context,
                "timestamp": datetime.now().isoformat(),
                "session_mood_trend": self._get_session_mood_trend(customer_id) if customer_id else None
            }

        except Exception as e:
            logger.error(f"Real-time mood tracking error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def analyze_recommendation_reaction(self, image_data: bytes, customer_id: str,
                                     recommendation_type: str, recommendation_data: Dict) -> Dict[str, Any]:
        """
        Analyze customer's facial reaction to specific recommendations.

        Args:
            image_data: Binary image data
            customer_id: Customer ID
            recommendation_type: Type of recommendation (weather, health, etc.)
            recommendation_data: The recommendation that was shown

        Returns:
            Reaction analysis for feedback purposes
        """
        try:
            # Get mood reaction
            mood_result = self.track_real_time_mood(
                image_data,
                customer_id,
                context=f"viewing_{recommendation_type}_recommendation"
            )

            if not mood_result.get("success"):
                return mood_result

            mood = mood_result["mood"]
            confidence = mood_result["confidence"]
            feedback_interpretation = mood_result["feedback_interpretation"]

            # Analyze reaction to specific recommendation
            reaction_analysis = {
                "recommendation_id": recommendation_data.get("id", f"{recommendation_type}_{uuid.uuid4().hex[:8]}"),
                "recommendation_type": recommendation_type,
                "customer_reaction": {
                    "mood": mood,
                    "confidence": confidence,
                    "feedback_type": feedback_interpretation["feedback_type"],
                    "likely_acceptance": feedback_interpretation["likely_acceptance"],
                    "engagement_level": feedback_interpretation["engagement_level"]
                },
                "recommendation_content": recommendation_data,
                "analysis_timestamp": datetime.now().isoformat()
            }

            # Store reaction for learning
            if customer_id in self.current_session_moods:
                self.current_session_moods[customer_id]["recommendation_reactions"].append(reaction_analysis)

            # Store in recommendation feedback tracking
            self.recommendation_feedback[reaction_analysis["recommendation_id"]] = reaction_analysis

            logger.info(f"Analyzed reaction for {customer_id}: {mood} ({feedback_interpretation['feedback_type']})")

            return {
                "success": True,
                "reaction_analysis": reaction_analysis,
                "feedback_summary": feedback_interpretation,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Recommendation reaction analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _interpret_mood_feedback(self, mood: str, context: str, confidence: float) -> Dict[str, Any]:
        """
        Interpret mood as feedback for recommendations.

        Args:
            mood: Detected mood
            context: Context of the mood detection
            confidence: Confidence in mood detection

        Returns:
            Feedback interpretation
        """
        mood_data = self.moods[mood]
        feedback_type = mood_data["feedback"]

        # Determine likely acceptance based on mood and confidence
        if feedback_type == "very_positive":
            likely_acceptance = min(0.95, 0.7 + (confidence * 0.25))
        elif feedback_type == "positive":
            likely_acceptance = min(0.85, 0.6 + (confidence * 0.25))
        elif feedback_type == "neutral":
            likely_acceptance = 0.5
        elif feedback_type == "negative":
            likely_acceptance = max(0.15, 0.4 - (confidence * 0.25))
        else:  # very_negative
            likely_acceptance = max(0.05, 0.3 - (confidence * 0.25))

        # Determine engagement level
        arousal = mood_data["arousal"]
        if arousal > 0.7:
            engagement_level = "high"
        elif arousal > 0.4:
            engagement_level = "medium"
        else:
            engagement_level = "low"

        # Context-specific adjustments
        if "recommendation" in context:
            # User is viewing recommendations
            if mood in ["confused", "frustrated"]:
                interpretation = "User may find recommendations unclear or overwhelming"
            elif mood in ["happy", "excited", "satisfied"]:
                interpretation = "User appears pleased with recommendations"
            elif mood == "neutral":
                interpretation = "User is considering recommendations neutrally"
            else:
                interpretation = f"User appears {mood} about recommendations"
        elif "choice" in context or "selection" in context:
            # User is making a choice
            if mood in ["confused", "frustrated"]:
                interpretation = "User may need assistance with selection"
            elif mood in ["happy", "satisfied"]:
                interpretation = "User confident in their choice"
            else:
                interpretation = f"User seems {mood} during selection process"
        else:
            interpretation = f"User appears {mood} in general context"

        return {
            "feedback_type": feedback_type,
            "likely_acceptance": likely_acceptance,
            "engagement_level": engagement_level,
            "interpretation": interpretation,
            "confidence": confidence,
            "mood_valence": mood_data["valence"],
            "mood_arousal": mood_data["arousal"]
        }

    def _get_session_mood_trend(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get mood trend for current session.

        Args:
            customer_id: Customer ID

        Returns:
            Session mood trend analysis
        """
        if customer_id not in self.current_session_moods:
            return None

        mood_samples = self.current_session_moods[customer_id]["mood_samples"]

        if len(mood_samples) < 2:
            return {"trend": "insufficient_data", "sample_count": len(mood_samples)}

        # Calculate trend in valence and arousal
        recent_moods = mood_samples[-5:]  # Last 5 mood samples

        valences = [sample["valence"] for sample in recent_moods]
        arousals = [sample["arousal"] for sample in recent_moods]

        # Simple trend calculation
        valence_trend = (valences[-1] - valences[0]) if len(valences) > 1 else 0
        arousal_trend = (arousals[-1] - arousals[0]) if len(arousals) > 1 else 0

        # Determine overall trend
        if valence_trend > 0.1:
            overall_trend = "improving"
        elif valence_trend < -0.1:
            overall_trend = "declining"
        else:
            overall_trend = "stable"

        return {
            "trend": overall_trend,
            "valence_trend": valence_trend,
            "arousal_trend": arousal_trend,
            "sample_count": len(mood_samples),
            "current_mood": mood_samples[-1]["mood"],
            "average_valence": sum(valences) / len(valences),
            "average_arousal": sum(arousals) / len(arousals)
        }

    def _save_mood_to_history(self, customer_id: str, mood_sample: Dict):
        """Save mood sample to history CSV."""
        try:
            face_id = self.current_session_moods[customer_id]["face_id"]

            with open(self.mood_history_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    mood_sample["timestamp"],
                    customer_id,
                    face_id,
                    mood_sample["mood"],
                    mood_sample["valence"],
                    mood_sample["arousal"],
                    mood_sample["confidence"],
                    mood_sample["context"],
                    "",  # recommendation_type (filled if applicable)
                    mood_sample["feedback_type"]
                ])
        except Exception as e:
            logger.error(f"Error saving mood to history: {e}")

    def get_customer_feedback_summary(self, customer_id: str) -> Dict[str, Any]:
        """
        Get comprehensive feedback summary for a customer's session.

        Args:
            customer_id: Customer ID

        Returns:
            Feedback summary with recommendations for system improvement
        """
        if customer_id not in self.current_session_moods:
            return {"error": "No active session found for customer"}

        session_data = self.current_session_moods[customer_id]
        mood_samples = session_data["mood_samples"]
        reactions = session_data["recommendation_reactions"]

        if not mood_samples:
            return {"error": "No mood data available"}

        # Calculate session statistics
        total_samples = len(mood_samples)
        positive_samples = len([m for m in mood_samples if self.moods[m["mood"]]["feedback"] in ["positive", "very_positive"]])
        negative_samples = len([m for m in mood_samples if self.moods[m["mood"]]["feedback"] in ["negative", "very_negative"]])

        # Calculate average mood metrics
        avg_valence = sum(m["valence"] for m in mood_samples) / total_samples
        avg_arousal = sum(m["arousal"] for m in mood_samples) / total_samples
        avg_confidence = sum(m["confidence"] for m in mood_samples) / total_samples

        # Analyze recommendation reactions
        recommendation_analysis = {}
        if reactions:
            for reaction in reactions:
                rec_type = reaction["recommendation_type"]
                if rec_type not in recommendation_analysis:
                    recommendation_analysis[rec_type] = {"positive": 0, "negative": 0, "neutral": 0}

                feedback_type = reaction["customer_reaction"]["feedback_type"]
                if feedback_type in ["positive", "very_positive"]:
                    recommendation_analysis[rec_type]["positive"] += 1
                elif feedback_type in ["negative", "very_negative"]:
                    recommendation_analysis[rec_type]["negative"] += 1
                else:
                    recommendation_analysis[rec_type]["neutral"] += 1

        return {
            "customer_id": customer_id,
            "session_summary": {
                "duration": (datetime.now() - datetime.fromisoformat(session_data["session_start"])).total_seconds() / 60,
                "total_mood_samples": total_samples,
                "positive_ratio": positive_samples / total_samples,
                "negative_ratio": negative_samples / total_samples,
                "average_valence": avg_valence,
                "average_arousal": avg_arousal,
                "average_confidence": avg_confidence
            },
            "recommendation_feedback": recommendation_analysis,
            "mood_trend": self._get_session_mood_trend(customer_id),
            "recommendations": self._generate_system_recommendations(avg_valence, avg_arousal, recommendation_analysis)
        }

    def _generate_system_recommendations(self, avg_valence: float, avg_arousal: float,
                                       recommendation_analysis: Dict) -> List[str]:
        """Generate recommendations for system improvement based on mood analysis."""
        recommendations = []

        if avg_valence < 0.4:
            recommendations.append("Consider simplifying the recommendation interface - customer showed signs of confusion/frustration")

        if avg_arousal < 0.3:
            recommendations.append("Customer engagement was low - consider more interactive or visually appealing recommendations")

        if avg_valence > 0.7 and avg_arousal > 0.6:
            recommendations.append("Customer highly engaged and positive - current recommendation style working well")

        # Analyze specific recommendation types
        for rec_type, analysis in recommendation_analysis.items():
            total = sum(analysis.values())
            if total > 0:
                negative_ratio = analysis["negative"] / total
                if negative_ratio > 0.6:
                    recommendations.append(f"{rec_type} recommendations received poor response - review algorithm")
                elif analysis["positive"] / total > 0.7:
                    recommendations.append(f"{rec_type} recommendations well-received - consider similar approach for other types")

        return recommendations

    def _load_face_encodings(self) -> Dict[str, Dict[str, Any]]:
        """
        Load face encodings from storage.

        Returns:
            Dictionary of face encodings by face_id
        """
        encodings = {}

        # Check if customer data file exists
        if not os.path.exists(self.customer_data_path):
            logger.warning(f"Customer data file not found: {self.customer_data_path}")
            return encodings

        try:
            with open(self.customer_data_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    face_id = row.get("face_id")
                    customer_id = row.get("customer_id")

                    if face_id and customer_id:
                        # Look for the face encoding file
                        encoding_path = os.path.join(self.face_images_dir, f"{face_id}.json")
                        if os.path.exists(encoding_path):
                            try:
                                with open(encoding_path, 'r') as f:
                                    encoding_data = json.load(f)
                                    encodings[face_id] = {
                                        "encoding": encoding_data.get("encoding"),
                                        "customer_id": customer_id
                                    }
                            except Exception as e:
                                logger.error(f"Error loading face encoding for {face_id}: {e}")

            logger.info(f"Loaded {len(encodings)} face encodings")
            return encodings

        except Exception as e:
            logger.error(f"Error loading face encodings: {e}")
            return {}

    def recognize_face(self, image_data: bytes) -> Dict[str, Any]:
        """
        Recognize a face from image data.

        In a real implementation, this would:
        1. Process the image and detect faces
        2. Extract face encodings
        3. Compare with stored encodings for matches

        For this demo, we'll simulate recognition with either:
        - A match to an existing face (if available)
        - No match, suggesting a new customer

        Args:
            image_data: Binary image data

        Returns:
            Recognition result
        """
        try:
            # In a real implementation, we would:
            # 1. Use a library like face_recognition to extract face encodings
            # 2. Compare the encoding with stored encodings
            # 3. Return the best match if above threshold

            # For demo purposes, let's simulate face recognition
            if random.random() > 0.3 and self.face_encodings:  # 70% chance to recognize if we have encodings
                # Randomly select a stored face
                face_id, face_data = random.choice(list(self.face_encodings.items()))

                return {
                    "recognized": True,
                    "face_id": face_id,
                    "customer_id": face_data["customer_id"],
                    "confidence": random.uniform(0.7, 0.95),
                    "timestamp": datetime.now().isoformat()
                }

            # Not recognized
            return {
                "recognized": False,
                "face_id": None,
                "confidence": random.uniform(0.3, 0.6),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error recognizing face: {e}")
            return {
                "recognized": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def store_face(self, image_data: bytes, customer_id: str) -> Dict[str, Any]:
        """
        Store a face for a customer.

        Args:
            image_data: Binary image data
            customer_id: Customer ID

        Returns:
            Storage result
        """
        try:
            # Generate a unique face ID
            face_id = f"face_{uuid.uuid4().hex[:8]}"

            # In a real implementation, we would:
            # 1. Extract face encoding from the image
            # 2. Save the encoding to a file
            # 3. Optionally save the image

            # Save the image for demo purposes
            image_path = os.path.join(self.face_images_dir, f"{face_id}.jpg")
            with open(image_path, 'wb') as f:
                f.write(image_data)

            # Create a mock encoding and save it
            mock_encoding = [random.random() for _ in range(128)]  # 128-dimensional face encoding
            encoding_path = os.path.join(self.face_images_dir, f"{face_id}.json")

            with open(encoding_path, 'w') as f:
                json.dump({
                    "encoding": mock_encoding,
                    "timestamp": datetime.now().isoformat()
                }, f)

            # Add to in-memory encodings
            self.face_encodings[face_id] = {
                "encoding": mock_encoding,
                "customer_id": customer_id
            }

            logger.info(f"Stored face for customer {customer_id} with face ID {face_id}")

            return {
                "success": True,
                "face_id": face_id,
                "customer_id": customer_id,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error storing face: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def analyze_mood(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze facial expression to determine mood using ML models ONLY.
        NO FALLBACK SIMULATIONS - experiment integrity requirement.

        Args:
            image_data: Binary image data

        Returns:
            Mood analysis result or error if ML detection fails
        """
        try:
            # REAL ML IMPLEMENTATION ONLY - NO SIMULATIONS FOR EXPERIMENT
            # This method should only use actual computer vision models
            # If no ML models are available, return error instead of fake data

            logger.error("Real ML mood detection not implemented - cannot return simulated data for experiment")

            return {
                "success": False,
                "error": "ML mood detection not available - experiment requires real detection",
                "timestamp": datetime.now().isoformat(),
                "ml_available": False
            }

        except Exception as e:
            logger.error(f"Error analyzing mood: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "ml_available": False
            }

    def _get_mood_food_recommendations(self, mood: str) -> Dict[str, Any]:
        """
        Get food recommendations based on mood.

        Args:
            mood: Detected mood

        Returns:
            Food recommendations for the mood
        """
        recommendations = {
            "happy": {
                "proteins": ["Chicken", "Paneer/Indian Cheese"],
                "sauces": ["Curry Special", "Mint Sauce"],
                "spice_level": "medium",
                "base_types": ["Wrap", "Bowl"],
                "reasoning": "Elevate your positive mood with flavorful, balanced options."
            },
            "sad": {
                "proteins": ["Paneer/Indian Cheese", "Chicken"],
                "sauces": ["Malai Masala", "Curry Special"],
                "spice_level": "medium-high",
                "base_types": ["Bowl", "Biryani"],
                "reasoning": "Comfort foods with rich flavors to boost your mood naturally."
            },
            "tired": {
                "proteins": ["Chicken", "Egg"],
                "sauces": ["Red Spicy Sauce", "Curry Masala"],
                "spice_level": "high",
                "base_types": ["Biryani", "Bowl"],
                "reasoning": "Energizing spices and proteins to help combat fatigue."
            },
            "stressed": {
                "proteins": ["Paneer/Indian Cheese", "Potato"],
                "sauces": ["Yogurt/Raita", "Mint Sauce"],
                "spice_level": "low-medium",
                "base_types": ["Bowl", "Wrap"],
                "reasoning": "Calming ingredients that won't add to stress levels."
            },
            "angry": {
                "proteins": ["Potato", "Paneer/Indian Cheese"],
                "sauces": ["Yogurt/Raita", "Mint Sauce"],
                "spice_level": "low",
                "base_types": ["Wrap", "Sandwich"],
                "reasoning": "Cooling ingredients that help restore balance."
            },
            "surprised": {
                "proteins": ["Chicken", "Soya"],
                "sauces": ["Curry Special", "Malai Masala"],
                "spice_level": "medium",
                "base_types": ["Wrap", "Sandwich"],
                "reasoning": "Balanced flavors to complement your heightened senses."
            },
            "neutral": {
                "proteins": ["Chicken", "Paneer/Indian Cheese", "Soya"],
                "sauces": ["Curry Special", "Malai Masala", "Mint Sauce"],
                "spice_level": "medium",
                "base_types": ["Bowl", "Wrap", "Sandwich"],
                "reasoning": "A balanced selection that you can customize to your preference."
            }
        }

        return recommendations.get(mood, recommendations["neutral"])

    def update_face(self, face_id: str, new_image_data: bytes) -> Dict[str, Any]:
        """
        Update a stored face with new image data.

        Args:
            face_id: Face ID to update
            new_image_data: New image data

        Returns:
            Update result
        """
        try:
            if face_id not in self.face_encodings:
                return {
                    "success": False,
                    "error": f"Face ID {face_id} not found",
                    "timestamp": datetime.now().isoformat()
                }

            # Get customer ID
            customer_id = self.face_encodings[face_id]["customer_id"]

            # Save the updated image
            image_path = os.path.join(self.face_images_dir, f"{face_id}.jpg")
            with open(image_path, 'wb') as f:
                f.write(new_image_data)

            # Create a new mock encoding and save it
            mock_encoding = [random.random() for _ in range(128)]
            encoding_path = os.path.join(self.face_images_dir, f"{face_id}.json")

            with open(encoding_path, 'w') as f:
                json.dump({
                    "encoding": mock_encoding,
                    "timestamp": datetime.now().isoformat()
                }, f)

            # Update in-memory encodings
            self.face_encodings[face_id] = {
                "encoding": mock_encoding,
                "customer_id": customer_id
            }

            logger.info(f"Updated face for customer {customer_id} with face ID {face_id}")

            return {
                "success": True,
                "face_id": face_id,
                "customer_id": customer_id,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error updating face: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def image_to_base64(self, image_path: str) -> Optional[str]:
        """
        Convert an image file to base64 for web display.

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded string or None if failed
        """
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            return None

    def get_customer_image(self, face_id: str) -> Optional[str]:
        """
        Get the stored face image for a customer.

        Args:
            face_id: Face ID

        Returns:
            Base64 encoded image or None if not found
        """
        image_path = os.path.join(self.face_images_dir, f"{face_id}.jpg")
        if os.path.exists(image_path):
            return self.image_to_base64(image_path)
        return None

    def get_mood_emoji(self, mood: str) -> str:
        """
        Get emoji representing a mood.

        Args:
            mood: Mood string

        Returns:
            Emoji representing the mood
        """
        mood_emojis = {
            "happy": "😊",
            "sad": "😢",
            "neutral": "😐",
            "surprised": "😲",
            "angry": "😠",
            "tired": "😴",
            "stressed": "😰"
        }
        return mood_emojis.get(mood, "😐")

    def _get_customer_profile(self, customer_id: str) -> Dict[str, Any]:
        """
        Get customer profile from data file.

        Args:
            customer_id: Customer ID

        Returns:
            Customer profile data
        """
        try:
            if not os.path.exists(self.customer_data_path):
                return {}

            with open(self.customer_data_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get("customer_id") == customer_id:
                        return {
                            "customer_id": customer_id,
                            "name": row.get("name", "Unknown"),
                            "phone_number": row.get("phone_number", ""),
                            "preferences": row.get("preferences", ""),
                            "visit_count": int(row.get("visit_count", 0)),
                            "last_visit": row.get("last_visit", ""),
                            "face_id": row.get("face_id", "")
                        }
            return {}
        except Exception as e:
            logger.error(f"Error loading customer profile: {e}")
            return {}

    def end_session(self, customer_id: str) -> Dict[str, Any]:
        """
        End mood tracking session and generate final feedback summary.

        Args:
            customer_id: Customer ID

        Returns:
            Final session summary
        """
        if customer_id not in self.current_session_moods:
            return {"error": "No active session found"}

        # Get final summary
        summary = self.get_customer_feedback_summary(customer_id)

        # Clean up session data
        del self.current_session_moods[customer_id]

        logger.info(f"Ended session for customer {customer_id}")

        return {
            "success": True,
            "session_ended": True,
            "final_summary": summary,
            "timestamp": datetime.now().isoformat()
        }

    def get_active_sessions(self) -> List[str]:
        """Get list of active mood tracking sessions."""
        return list(self.current_session_moods.keys())

    def get_mood_statistics(self) -> Dict[str, Any]:
        """Get overall mood statistics from history."""
        if not os.path.exists(self.mood_history_path):
            return {"error": "No mood history available"}

        try:
            mood_counts = {}
            feedback_counts = {"positive": 0, "negative": 0, "neutral": 0}
            total_samples = 0

            with open(self.mood_history_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    mood = row.get("mood", "")
                    feedback_type = row.get("feedback_type", "")

                    if mood:
                        mood_counts[mood] = mood_counts.get(mood, 0) + 1
                        total_samples += 1

                    if "positive" in feedback_type:
                        feedback_counts["positive"] += 1
                    elif "negative" in feedback_type:
                        feedback_counts["negative"] += 1
                    else:
                        feedback_counts["neutral"] += 1

            return {
                "total_samples": total_samples,
                "mood_distribution": mood_counts,
                "feedback_distribution": feedback_counts,
                "most_common_mood": max(mood_counts, key=mood_counts.get) if mood_counts else "neutral"
            }

        except Exception as e:
            logger.error(f"Error getting mood statistics: {e}")
            return {"error": str(e)}