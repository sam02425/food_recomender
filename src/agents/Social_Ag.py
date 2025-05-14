# /agents/social_agent.py
"""
Social Agent for handling social media interactions and sharing.
"""

import os
import logging
import random
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("social_agent")

class SocialAgent:
    """Agent for social media interactions and sharing."""

    def __init__(self, social_data_path: str, media_storage_path: str):
        """
        Initialize the social agent.

        Args:
            social_data_path: Path to store social sharing data
            media_storage_path: Path to store uploaded media files
        """
        self.social_data_path = social_data_path
        self.media_storage_path = media_storage_path

        # Ensure directories exist
        os.makedirs(os.path.dirname(social_data_path), exist_ok=True)
        os.makedirs(media_storage_path, exist_ok=True)

        # Load existing social data if available
        self.social_data = self._load_social_data()

        # Platform configurations
        self.platforms = {
            "facebook": {
                "enabled": True,
                "share_text": "Check out my delicious creation at Curry Creations!",
                "hashtags": ["CurryCreations", "FoodLover"]
            },
            "instagram": {
                "enabled": True,
                "share_text": "Loving my custom creation! 😋",
                "hashtags": ["FoodGram", "CurryCreations", "FoodieLife"]
            },
            "tiktok": {
                "enabled": True,
                "share_text": "My perfect meal creation! #FoodTok",
                "hashtags": ["FoodTok", "CurryCreations"]
            }
        }

        logger.info("Social agent initialized")

    def _load_social_data(self) -> Dict[str, Any]:
        """
        Load social sharing data.

        Returns:
            Dictionary of social sharing data
        """
        if os.path.exists(self.social_data_path):
            try:
                with open(self.social_data_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading social data: {e}")

        # Return default structure if file doesn't exist or loading fails
        return {
            "shares": [],
            "popular_hashtags": {},
            "customer_shares": {}
        }

    def _save_social_data(self) -> bool:
        """
        Save social sharing data.

        Returns:
            Success status
        """
        try:
            with open(self.social_data_path, 'w') as f:
                json.dump(self.social_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving social data: {e}")
            return False

    def generate_share_prompt(self, customer_name: str, dish_name: str) -> Dict[str, Any]:
        """
        Generate a personalized social sharing prompt.

        Args:
            customer_name: Customer's name
            dish_name: Name of the dish

        Returns:
            Dictionary with social sharing prompt info
        """
        # Create a sanitized hashtag from customer and dish name
        customer_tag = customer_name.replace(" ", "_").lower() if customer_name else "guest"
        dish_tag = dish_name.replace(" ", "_").lower() if dish_name else "custom_creation"

        # Generate personalized hashtags
        personalized_hashtags = [
            f"{customer_tag}s_masterpiece",
            f"{dish_tag}",
            "CurryCreations"
        ]

        # Generate fun captions
        captions = [
            f"Just crafted my perfect meal! {dish_name} is a masterpiece! 😋",
            f"My culinary creation at Curry Creations! {dish_name} rocks!",
            f"Food heaven found with my {dish_name}! Can't stop won't stop!",
            f"This {dish_name} just made my day at Curry Creations!"
        ]

        # Pick a random caption
        selected_caption = random.choice(captions)

        # Assemble prompts for each platform
        platform_prompts = {}
        for platform, config in self.platforms.items():
            if config["enabled"]:
                # Combine platform-specific hashtags with personalized ones
                all_hashtags = config["hashtags"] + personalized_hashtags
                hashtag_text = " ".join([f"#{tag}" for tag in all_hashtags])

                platform_prompts[platform] = {
                    "caption": f"{selected_caption}\n\n{hashtag_text}",
                    "hashtags": all_hashtags
                }

        return {
            "customer_name": customer_name,
            "dish_name": dish_name,
            "caption": selected_caption,
            "hashtags": personalized_hashtags,
            "platforms": platform_prompts,
            "timestamp": datetime.now().isoformat()
        }

    def store_customer_photo(self, customer_id: str, image_data: bytes,
                            dish_name: str) -> Dict[str, Any]:
        """
        Store a customer's photo with their dish.

        Args:
            customer_id: Customer ID
            image_data: Binary image data
            dish_name: Name of the dish

        Returns:
            Information about the stored photo
        """
        try:
            # Generate a unique filename
            filename = f"{customer_id}_{uuid.uuid4().hex[:8]}.jpg"
            file_path = os.path.join(self.media_storage_path, filename)

            # Save the image
            with open(file_path, 'wb') as f:
                f.write(image_data)

            # Record the image metadata
            image_info = {
                "customer_id": customer_id,
                "dish_name": dish_name,
                "file_path": file_path,
                "filename": filename,
                "timestamp": datetime.now().isoformat()
            }

            # Update social data
            if customer_id not in self.social_data["customer_shares"]:
                self.social_data["customer_shares"][customer_id] = []

            self.social_data["customer_shares"][customer_id].append(image_info)
            self._save_social_data()

            logger.info(f"Stored customer photo for {customer_id} with dish {dish_name}")
            return image_info

        except Exception as e:
            logger.error(f"Error storing customer photo: {e}")
            return {
                "error": str(e),
                "success": False
            }

    def share_to_platforms(self, customer_id: str, image_path: str,
                          caption: str, platforms: List[str]) -> Dict[str, Any]:
        """
        Share a customer's photo to selected social media platforms.
        Note: In a production environment, this would integrate with platform APIs.

        Args:
            customer_id: Customer ID
            image_path: Path to the image file
            caption: Sharing caption
            platforms: List of platforms to share to

        Returns:
            Sharing results
        """
        # In a real implementation, this would use platform APIs to share
        # For now, we'll simulate the sharing process

        results = {}
        share_id = uuid.uuid4().hex

        for platform in platforms:
            if platform in self.platforms and self.platforms[platform]["enabled"]:
                # Simulate API call with random success rate
                success = random.random() > 0.1  # 90% success rate

                if success:
                    result = {
                        "success": True,
                        "platform": platform,
                        "share_id": f"{platform}_{share_id}",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    result = {
                        "success": False,
                        "platform": platform,
                        "error": "Simulated sharing error",
                        "timestamp": datetime.now().isoformat()
                    }

                results[platform] = result

        # Record the sharing attempt
        share_record = {
            "customer_id": customer_id,
            "image_path": image_path,
            "caption": caption,
            "platforms": platforms,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

        self.social_data["shares"].append(share_record)

        # Update popular hashtags
        if caption:
            hashtags = [word.strip('#') for word in caption.split() if word.startswith('#')]
            for tag in hashtags:
                if tag in self.social_data["popular_hashtags"]:
                    self.social_data["popular_hashtags"][tag] += 1
                else:
                    self.social_data["popular_hashtags"][tag] = 1

        self._save_social_data()

        # Return the results
        successful_platforms = [p for p, r in results.items() if r["success"]]
        return {
            "share_id": share_id,
            "success": len(successful_platforms) > 0,
            "successful_platforms": successful_platforms,
            "failed_platforms": [p for p, r in results.items() if not r["success"]],
            "timestamp": datetime.now().isoformat()
        }

    def get_customer_shares(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Get all social shares for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            List of customer's social shares
        """
        return self.social_data["customer_shares"].get(customer_id, [])

    def get_popular_hashtags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most popular hashtags.

        Args:
            limit: Maximum number of hashtags to return

        Returns:
            List of popular hashtags with counts
        """
        # Sort hashtags by count
        sorted_tags = sorted(
            self.social_data["popular_hashtags"].items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Format and return top tags
        return [
            {"tag": tag, "count": count}
            for tag, count in sorted_tags[:limit]
        ]

    def get_sharing_metrics(self) -> Dict[str, Any]:
        """
        Get metrics on social sharing activity.

        Returns:
            Dictionary of sharing metrics
        """
        total_shares = len(self.social_data["shares"])
        platform_counts = {}
        success_count = 0

        # Count shares by platform and success rate
        for share in self.social_data["shares"]:
            for platform, result in share.get("results", {}).items():
                if platform not in platform_counts:
                    platform_counts[platform] = {"total": 0, "success": 0}

                platform_counts[platform]["total"] += 1
                if result.get("success", False):
                    platform_counts[platform]["success"] += 1
                    success_count += 1

        # Calculate overall success rate
        success_rate = (success_count / total_shares * 100) if total_shares > 0 else 0

        return {
            "total_shares": total_shares,
            "success_rate": success_rate,
            "platform_metrics": platform_counts,
            "unique_customers": len(self.social_data["customer_shares"]),
            "popular_hashtags": self.get_popular_hashtags(5)
        }