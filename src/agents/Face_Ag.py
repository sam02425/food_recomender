# /agents/Face_Ag.py
"""
Face Recognition Agent for customer identification and mood analysis.
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
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("face_recognition_agent")

class FaceRecognitionAgent:
    """Agent for face recognition and mood analysis."""

    def __init__(self, customer_data_path: str, face_images_dir: str):
        """
        Initialize the face recognition agent.

        Args:
            customer_data_path: Path to customer data CSV
            face_images_dir: Directory to store face images
        """
        self.customer_data_path = customer_data_path
        self.face_images_dir = face_images_dir
        self.recognition_threshold = 0.65  # Similarity threshold

        # Ensure directories exist
        os.makedirs(self.face_images_dir, exist_ok=True)

        # Load face encodings if available
        self.face_encodings = self._load_face_encodings()

        # Initialize mood detection
        self.moods = ["happy", "sad", "neutral", "surprised", "angry", "tired", "stressed"]

        logger.info("Face recognition agent initialized")

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
        Analyze facial expression to determine mood.

        Args:
            image_data: Binary image data

        Returns:
            Mood analysis result
        """
        try:
            # In a real implementation, we would:
            # 1. Use computer vision to detect facial features
            # 2. Apply a mood classification model
            # 3. Return the detected mood with confidence

            # For demo purposes, simulate mood detection
            # Weight moods differently - happy and neutral more common
            mood_weights = {
                "happy": 0.3,
                "neutral": 0.3,
                "tired": 0.15,
                "stressed": 0.1,
                "sad": 0.1,
                "surprised": 0.03,
                "angry": 0.02
            }

            # Random selection with weights
            mood = random.choices(
                list(mood_weights.keys()),
                weights=list(mood_weights.values()),
                k=1
            )[0]

            # Random confidence
            confidence = random.uniform(0.65, 0.95)

            # Get recommendations for food based on mood
            food_recs = self._get_mood_food_recommendations(mood)

            logger.info(f"Analyzed mood: {mood} with {confidence:.2f} confidence")

            return {
                "mood": mood,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "recommendations": food_recs
            }

        except Exception as e:
            logger.error(f"Error analyzing mood: {e}")
            return {
                "mood": "neutral",  # Default to neutral on error
                "error": str(e),
                "timestamp": datetime.now().isoformat()
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