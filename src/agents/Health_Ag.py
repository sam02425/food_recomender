# /agents/Health_Ag.py
"""
Health Recommender Agent for making activity-based food recommendations.
"""

import os
import csv
import json
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("health_recommender_agent")

class HealthRecommenderAgent:
    """Agent for making health-based food recommendations."""

    def __init__(self, health_data_path: str):
        """
        Initialize the health recommender agent.

        Args:
            health_data_path: Path to health recommendations CSV
        """
        self.health_data_path = health_data_path
        self.health_data = self._load_health_data()

        # Default health recommendations by activity
        self.default_recommendations = {
            "study": {
                "proteins": ["Egg", "Paneer/Indian Cheese", "Chicken"],
                "sauces": ["Mint Sauce", "Malai Masala"],
                "base_types": ["Wrap", "Bowl"],
                "veggies": ["Spinach", "Bell Pepper", "Tomato"],
                "reasoning": "Brain-boosting nutrients to enhance focus and memory without causing energy crashes."
            },
            "active": {
                "proteins": ["Chicken", "Paneer/Indian Cheese", "Egg"],
                "sauces": ["Curry Special", "Yogurt/Raita"],
                "base_types": ["Bowl", "Biryani"],
                "veggies": ["Spinach", "Bell Pepper", "Grilled Onion", "Corn"],
                "reasoning": "Protein-rich meal with complex carbs to fuel your workout and support muscle recovery."
            },
            "gym": {
                "proteins": ["Chicken", "Soya", "Egg"],
                "sauces": ["Yogurt/Raita", "Curry Special"],
                "base_types": ["Bowl", "Wrap"],
                "veggies": ["Spinach", "Bell Pepper", "Avocado"],
                "reasoning": "High-protein options with healthy fats to support muscle building and recovery."
            },
            "work": {
                "proteins": ["Chicken", "Paneer/Indian Cheese", "Potato"],
                "sauces": ["Curry Special", "Malai Masala"],
                "base_types": ["Wrap", "Sandwich"],
                "veggies": ["Tomato", "Bell Pepper", "Grilled Onion"],
                "reasoning": "Balanced meal for sustained energy throughout your workday."
            },
            "chilling": {
                "proteins": ["Paneer/Indian Cheese", "Potato", "Pepperoni"],
                "sauces": ["Malai Masala", "Mint Sauce", "Marinara"],
                "base_types": ["Bowl", "Sandwich"],
                "veggies": ["Bell Pepper", "Tomato", "Avocado", "Pineapple"],
                "reasoning": "Comfort food options that are satisfying while still being nutritious."
            }
        }

        logger.info("Health recommender agent initialized")

    def _load_health_data(self) -> Dict[str, Any]:
        """
        Load health recommendation data from CSV.

        Returns:
            Health recommendation data
        """
        health_data = {
            "activity_recommendations": {},
            "nutrient_info": {}
        }

        # Create default health data file if it doesn't exist
        if not os.path.exists(self.health_data_path):
            self._initialize_health_data()

        try:
            with open(self.health_data_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    activity = row.get("activity")
                    item = row.get("item")
                    category = row.get("category")
                    recommendation_type = row.get("recommendation_type")
                    score = int(row.get("score", 0))
                    reasoning = row.get("reasoning", "")

                    if activity and category and item:
                        if activity not in health_data["activity_recommendations"]:
                            health_data["activity_recommendations"][activity] = {}

                        if category not in health_data["activity_recommendations"][activity]:
                            health_data["activity_recommendations"][activity][category] = []

                        health_data["activity_recommendations"][activity][category].append({
                            "item": item,
                            "score": score,
                            "reasoning": reasoning
                        })

                    if recommendation_type == "nutrient_info" and item:
                        health_data["nutrient_info"][item] = {
                            "benefits": row.get("benefits", ""),
                            "category": category
                        }

            logger.info(f"Loaded health data with {len(health_data['activity_recommendations'])} activities")
            return health_data

        except Exception as e:
            logger.error(f"Error loading health data: {e}")
            return {"activity_recommendations": {}, "nutrient_info": {}}

    def _initialize_health_data(self) -> None:
        """Initialize health data file with default values."""
        try:
            with open(self.health_data_path, 'w', newline='') as file:
                fieldnames = ["activity", "category", "item", "recommendation_type", "score", "reasoning", "benefits"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                # Add default activity recommendations
                for activity, recommendations in self.default_recommendations.items():
                    # Proteins
                    for i, protein in enumerate(recommendations["proteins"]):
                        writer.writerow({
                            "activity": activity,
                            "category": "proteins",
                            "item": protein,
                            "recommendation_type": "activity",
                            "score": 5 - i,  # Higher score for first items
                            "reasoning": recommendations["reasoning"],
                            "benefits": ""
                        })

                    # Sauces
                    for i, sauce in enumerate(recommendations["sauces"]):
                        writer.writerow({
                            "activity": activity,
                            "category": "sauces",
                            "item": sauce,
                            "recommendation_type": "activity",
                            "score": 5 - i,
                            "reasoning": recommendations["reasoning"],
                            "benefits": ""
                        })

                    # Base types
                    for i, base_type in enumerate(recommendations["base_types"]):
                        writer.writerow({
                            "activity": activity,
                            "category": "base_types",
                            "item": base_type,
                            "recommendation_type": "activity",
                            "score": 5 - i,
                            "reasoning": recommendations["reasoning"],
                            "benefits": ""
                        })

                    # Veggies
                    for i, veggie in enumerate(recommendations["veggies"]):
                        writer.writerow({
                            "activity": activity,
                            "category": "veggies",
                            "item": veggie,
                            "recommendation_type": "activity",
                            "score": 5 - i,
                            "reasoning": recommendations["reasoning"],
                            "benefits": ""
                        })

                # Add nutrient info
                nutrient_info = {
                    "Chicken": "High-quality protein source for muscle maintenance and repair.",
                    "Egg": "Complete protein with essential amino acids and choline for brain health.",
                    "Paneer/Indian Cheese": "Good source of calcium and protein for bone health.",
                    "Soya": "Plant-based protein with isoflavones that may have heart health benefits.",
                    "Potato": "Contains resistant starch for gut health and provides sustained energy.",
                    "Pepperoni": "Source of protein and B-vitamins for energy metabolism.",
                    "Spinach": "Rich in iron for oxygen transport and energy production.",
                    "Bell Pepper": "Excellent source of vitamin C for immune function and antioxidant protection.",
                    "Avocado": "Healthy monounsaturated fats and fiber for heart health and satiety.",
                    "Tomato": "Contains lycopene for skin and heart health."
                }

                for item, benefits in nutrient_info.items():
                    writer.writerow({
                        "activity": "",
                        "category": "all",
                        "item": item,
                        "recommendation_type": "nutrient_info",
                        "score": 0,
                        "reasoning": "",
                        "benefits": benefits
                    })

            logger.info(f"Initialized health data file: {self.health_data_path}")

        except Exception as e:
            logger.error(f"Error initializing health data: {e}")

    def get_recommendations(self, activity_level: str, customer_id: Optional[str] = None,
                          previous_orders: List[Dict[str, Any]] = None,
                          mood: str = "neutral") -> Dict[str, Any]:
        """
        Get health recommendations based on activity level.

        Args:
            activity_level: Activity level (study, active/gym, work, chilling)
            customer_id: Optional customer ID for personalization
            previous_orders: Optional list of previous orders
            mood: Customer's current mood

        Returns:
            Health recommendations
        """
        # Normalize activity level
        if activity_level.lower() in ["gym", "workout", "exercise", "training"]:
            activity_level = "gym"
        elif activity_level.lower() in ["active", "sports", "playing"]:
            activity_level = "active"
        elif activity_level.lower() in ["studying", "reading", "learning"]:
            activity_level = "study"
        elif activity_level.lower() in ["office", "working", "job"]:
            activity_level = "work"
        elif activity_level.lower() in ["relaxing", "resting", "chilling", "leisure"]:
            activity_level = "chilling"
        else:
            # Default to work if unrecognized
            activity_level = "work"

        # Get recommendations from loaded data
        recommendations = {}
        if activity_level in self.health_data["activity_recommendations"]:
            activity_recs = self.health_data["activity_recommendations"][activity_level]

            # Get top proteins
            if "proteins" in activity_recs:
                proteins = sorted(activity_recs["proteins"], key=lambda x: x["score"], reverse=True)
                recommendations["proteins"] = [p["item"] for p in proteins[:3]]

            # Get top sauces
            if "sauces" in activity_recs:
                sauces = sorted(activity_recs["sauces"], key=lambda x: x["score"], reverse=True)
                recommendations["sauces"] = [s["item"] for s in sauces[:3]]

            # Get top base types
            if "base_types" in activity_recs:
                base_types = sorted(activity_recs["base_types"], key=lambda x: x["score"], reverse=True)
                recommendations["base_types"] = [b["item"] for b in base_types[:3]]

            # Get top veggies
            if "veggies" in activity_recs:
                veggies = sorted(activity_recs["veggies"], key=lambda x: x["score"], reverse=True)
                recommendations["veggies"] = [v["item"] for v in veggies[:5]]

            # Get reasoning
            if "proteins" in activity_recs and activity_recs["proteins"]:
                recommendations["reasoning"] = activity_recs["proteins"][0]["reasoning"]

        # Use defaults if no recommendations found
        if not recommendations and activity_level in self.default_recommendations:
            recommendations = self.default_recommendations[activity_level]
        elif not recommendations:
            # Fallback to "work" if activity level not found
            recommendations = self.default_recommendations["work"]

        # Personalize based on previous orders if available
        if customer_id and previous_orders:
            recommendations = self._personalize_recommendations(
                recommendations,
                previous_orders,
                activity_level
            )

        # Adjust based on mood
        recommendations = self._adjust_for_mood(recommendations, mood)

        # Get health benefits for recommended items
        recommendations["health_benefits"] = self._get_health_benefits(recommendations)

        # Add timestamp
        recommendations["timestamp"] = datetime.now().isoformat()
        recommendations["activity_level"] = activity_level

        logger.info(f"Generated health recommendations for activity: {activity_level}")
        return recommendations

    def _personalize_recommendations(self, recommendations: Dict[str, Any],
                                   previous_orders: List[Dict[str, Any]],
                                   activity_level: str) -> Dict[str, Any]:
        """
        Personalize recommendations based on previous orders.

        Args:
            recommendations: Base recommendations
            previous_orders: Previous customer orders
            activity_level: Current activity level

        Returns:
            Personalized recommendations
        """
        # If no previous orders, return base recommendations
        if not previous_orders:
            return recommendations

        # Extract items from previous orders
        previous_proteins = []
        previous_sauces = []
        previous_base_types = []
        previous_veggies = []

        for order in previous_orders:
            items = order.get("items", [])

            # Handle both list and JSON string formats
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except:
                    items = []

            for item in items:
                if isinstance(item, dict):
                    if "protein" in item:
                        previous_proteins.append(item["protein"])

                    if "sauce" in item:
                        previous_sauces.append(item["sauce"])

                    if "base_type" in item:
                        previous_base_types.append(item["base_type"])

                    if "veggies" in item and isinstance(item["veggies"], list):
                        previous_veggies.extend(item["veggies"])

        # Count occurrences
        protein_counts = {}
        for protein in previous_proteins:
            protein_counts[protein] = protein_counts.get(protein, 0) + 1

        sauce_counts = {}
        for sauce in previous_sauces:
            sauce_counts[sauce] = sauce_counts.get(sauce, 0) + 1

        base_type_counts = {}
        for base_type in previous_base_types:
            base_type_counts[base_type] = base_type_counts.get(base_type, 0) + 1

        veggie_counts = {}
        for veggie in previous_veggies:
            veggie_counts[veggie] = veggie_counts.get(veggie, 0) + 1

        # Mix favorite items with recommendations (70% recommendations, 30% favorites)
        personalized_recs = recommendations.copy()

        # Personalize proteins
        if protein_counts and "proteins" in recommendations:
            favorite_proteins = [p[0] for p in sorted(protein_counts.items(), key=lambda x: x[1], reverse=True)]
            base_proteins = recommendations["proteins"]

            # Create a mix of recommendations and favorites
            personalized_proteins = []
            for i in range(min(3, len(base_proteins))):
                if i == 0 and favorite_proteins:  # Add a favorite in first position
                    personalized_proteins.append(favorite_proteins[0])
                else:
                    # Add recommendation if not already added
                    for protein in base_proteins:
                        if protein not in personalized_proteins:
                            personalized_proteins.append(protein)
                            break

            personalized_recs["proteins"] = personalized_proteins[:3]  # Limit to 3

        # Similarly for sauces, base types, and veggies
        if sauce_counts and "sauces" in recommendations:
            favorite_sauces = [s[0] for s in sorted(sauce_counts.items(), key=lambda x: x[1], reverse=True)]
            base_sauces = recommendations["sauces"]

            personalized_sauces = []
            for i in range(min(3, len(base_sauces))):
                if i == 0 and favorite_sauces:
                    personalized_sauces.append(favorite_sauces[0])
                else:
                    for sauce in base_sauces:
                        if sauce not in personalized_sauces:
                            personalized_sauces.append(sauce)
                            break

            personalized_recs["sauces"] = personalized_sauces[:3]

        if base_type_counts and "base_types" in recommendations:
            favorite_base_types = [b[0] for b in sorted(base_type_counts.items(), key=lambda x: x[1], reverse=True)]
            base_base_types = recommendations["base_types"]

            personalized_base_types = []
            for i in range(min(3, len(base_base_types))):
                if i == 0 and favorite_base_types:
                    personalized_base_types.append(favorite_base_types[0])
                else:
                    for base_type in base_base_types:
                        if base_type not in personalized_base_types:
                            personalized_base_types.append(base_type)
                            break

            personalized_recs["base_types"] = personalized_base_types[:3]

        if veggie_counts and "veggies" in recommendations:
            favorite_veggies = [v[0] for v in sorted(veggie_counts.items(), key=lambda x: x[1], reverse=True)]
            base_veggies = recommendations["veggies"]

            personalized_veggies = []
            for i in range(min(5, len(base_veggies))):
                if i < 2 and i < len(favorite_veggies):  # Add up to 2 favorites
                    personalized_veggies.append(favorite_veggies[i])
                else:
                    for veggie in base_veggies:
                        if veggie not in personalized_veggies:
                            personalized_veggies.append(veggie)
                            break

            personalized_recs["veggies"] = personalized_veggies[:5]

        # Update reasoning to mention personalization
        personalized_recs["reasoning"] = f"{recommendations.get('reasoning', '')} This recommendation includes some of your previous favorites."

        return personalized_recs

    def _adjust_for_mood(self, recommendations: Dict[str, Any], mood: str) -> Dict[str, Any]:
        """
        Adjust recommendations based on mood.

        Args:
            recommendations: Base recommendations
            mood: Customer mood

        Returns:
            Mood-adjusted recommendations
        """
        mood_adjustments = {
            "happy": {
                "reasoning_suffix": "These options complement your positive mood with balanced nutrition.",
                "veggie_additions": ["Bell Pepper", "Pineapple"]  # Colorful options
            },
            "sad": {
                "reasoning_suffix": "These choices include mood-boosting nutrients that may help improve your mood.",
                "veggie_additions": ["Avocado", "Spinach"]  # Mood-boosting nutrients
            },
            "stressed": {
                "reasoning_suffix": "These options include calming ingredients that may help reduce stress.",
                "veggie_additions": ["Avocado", "Spinach"]  # Stress-reducing foods
            },
            "tired": {
                "reasoning_suffix": "These energy-boosting options may help combat fatigue.",
                "veggie_additions": ["Spinach", "Bell Pepper"]  # Energy-boosting foods
            },
            "angry": {
                "reasoning_suffix": "These balanced choices include calming ingredients to help restore balance.",
                "veggie_additions": ["Spinach", "Tomato"]  # Calming foods
            }
        }

        # If no mood adjustments needed or mood not recognized
        if mood not in mood_adjustments:
            return recommendations

        adjusted_recs = recommendations.copy()

        # Add mood-specific reasoning
        if "reasoning" in adjusted_recs:
            adjusted_recs["reasoning"] = f"{adjusted_recs['reasoning']} {mood_adjustments[mood]['reasoning_suffix']}"
        else:
            adjusted_recs["reasoning"] = mood_adjustments[mood]['reasoning_suffix']

        # Adjust veggie recommendations for mood
        if "veggies" in adjusted_recs:
            # Add mood-specific veggies if not already present
            mood_veggies = mood_adjustments[mood]["veggie_additions"]
            current_veggies = adjusted_recs["veggies"]

            for veggie in mood_veggies:
                if veggie not in current_veggies:
                    # Replace a random veggie with the mood-specific one
                    if len(current_veggies) > 0:
                        replace_idx = random.randint(0, len(current_veggies) - 1)
                        current_veggies[replace_idx] = veggie

        return adjusted_recs

    def _get_health_benefits(self, recommendations: Dict[str, Any]) -> List[str]:
        """
        Get health benefits for recommended items.

        Args:
            recommendations: Food recommendations

        Returns:
            List of health benefit statements
        """
        benefits = []

        # Get benefits for proteins
        for protein in recommendations.get("proteins", [])[:1]:  # Just the top protein
            if protein in self.health_data["nutrient_info"]:
                benefits.append(f"{protein}: {self.health_data['nutrient_info'][protein]['benefits']}")
            elif protein == "Chicken":
                benefits.append(f"{protein}: High-quality protein for muscle maintenance and repair.")
            elif protein == "Egg":
                benefits.append(f"{protein}: Complete protein with essential amino acids and choline for brain health.")
            elif protein == "Paneer/Indian Cheese":
                benefits.append(f"{protein}: Good source of calcium and protein for bone health.")

        # Get benefits for veggies
        for veggie in recommendations.get("veggies", [])[:2]:  # Top 2 veggies
            if veggie in self.health_data["nutrient_info"]:
                benefits.append(f"{veggie}: {self.health_data['nutrient_info'][veggie]['benefits']}")
            elif veggie == "Spinach":
                benefits.append(f"{veggie}: Rich in iron for oxygen transport and energy production.")
            elif veggie == "Bell Pepper":
                benefits.append(f"{veggie}: Excellent source of vitamin C for immune function.")
            elif veggie == "Avocado":
                benefits.append(f"{veggie}: Healthy monounsaturated fats and fiber for heart health.")

        # Add activity-specific benefit
        activity_level = recommendations.get("activity_level")
        if activity_level == "study":
            benefits.append("This combination provides nutrients that support cognitive function and focus.")
        elif activity_level in ["active", "gym"]:
            benefits.append("This meal offers a good balance of proteins and nutrients to support physical activity.")
        elif activity_level == "work":
            benefits.append("These options provide steady energy to help you stay productive throughout your workday.")
        elif activity_level == "chilling":
            benefits.append("This balanced meal supports relaxation while still providing good nutrition.")

        return benefits

    def update_recommendation_scores(self, activity: str, category: str, item: str,
                                    feedback_score: int) -> bool:
        """
        Update recommendation scores based on feedback.

        Args:
            activity: Activity type
            category: Item category
            item: Item name
            feedback_score: Feedback score (1-5)

        Returns:
            Success status
        """
        try:
            # Load current data
            current_data = []
            with open(self.health_data_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                current_data = list(reader)

            # Find and update the matching row
            item_found = False
            for row in current_data:
                if (row["activity"] == activity and
                    row["category"] == category and
                    row["item"] == item and
                    row["recommendation_type"] == "activity"):

                    # Update score (weighted average with existing score)
                    current_score = int(row["score"])
                    # 70% existing score, 30% new feedback
                    new_score = int(0.7 * current_score + 0.3 * feedback_score)
                    row["score"] = str(new_score)
                    item_found = True
                    break

            # If item not found, add it
            if not item_found:
                new_row = {
                    "activity": activity,
                    "category": category,
                    "item": item,
                    "recommendation_type": "activity",
                    "score": str(feedback_score),
                    "reasoning": f"Customer preference for {activity} activity",
                    "benefits": ""
                }
                current_data.append(new_row)

            # Write updated data back to CSV
            with open(self.health_data_path, 'w', newline='') as file:
                fieldnames = ["activity", "category", "item", "recommendation_type", "score", "reasoning", "benefits"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(current_data)

            # Reload health data
            self.health_data = self._load_health_data()

            logger.info(f"Updated recommendation score for {activity} - {category} - {item}")
            return True

        except Exception as e:
            logger.error(f"Error updating recommendation score: {e}")
            return False

    def process_feedback(self, activity_level: str, feedback_type: str,
                        items_selected: Dict[str, Any],
                        custom_suggestion: Optional[str] = None) -> Dict[str, Any]:
        """
        Process feedback on health recommendations.

        Args:
            activity_level: Activity level
            feedback_type: Feedback type (accept, ignore, custom)
            items_selected: Selected food items
            custom_suggestion: Custom suggestion if provided

        Returns:
            Processed feedback result
        """
        result = {
            "activity_level": activity_level,
            "feedback_type": feedback_type,
            "processed": False,
            "message": ""
        }

        try:
            # Process based on feedback type
            if feedback_type == "accept":
                # Increase scores for selected items
                if "protein" in items_selected:
                    self.update_recommendation_scores(
                        activity=activity_level,
                        category="proteins",
                        item=items_selected["protein"],
                        feedback_score=5  # High score for accepted items
                    )

                if "sauce" in items_selected:
                    self.update_recommendation_scores(
                        activity=activity_level,
                        category="sauces",
                        item=items_selected["sauce"],
                        feedback_score=5
                    )

                if "base_type" in items_selected:
                    self.update_recommendation_scores(
                        activity=activity_level,
                        category="base_types",
                        item=items_selected["base_type"],
                        feedback_score=5
                    )

                result["processed"] = True
                result["message"] = "Recommendation accepted and scores updated"

            elif feedback_type == "custom" and custom_suggestion:
                # Handle custom suggestion
                # In a real implementation, we would parse the suggestion and update scores
                # For this demo, we'll increase the score for the custom suggestion item

                # Determine the category based on the suggestion
                all_proteins = [p["item"] for p in self.health_data.get("activity_recommendations", {}).get(activity_level, {}).get("proteins", [])]
                all_sauces = [s["item"] for s in self.health_data.get("activity_recommendations", {}).get(activity_level, {}).get("sauces", [])]
                all_base_types = [b["item"] for b in self.health_data.get("activity_recommendations", {}).get(activity_level, {}).get("base_types", [])]

                if custom_suggestion in all_proteins:
                    category = "proteins"
                elif custom_suggestion in all_sauces:
                    category = "sauces"
                elif custom_suggestion in all_base_types:
                    category = "base_types"
                else:
                    # Default to proteins if not found
                    category = "proteins"

                self.update_recommendation_scores(
                    activity=activity_level,
                    category=category,
                    item=custom_suggestion,
                    feedback_score=5
                )

                result["processed"] = True
                result["message"] = f"Custom suggestion '{custom_suggestion}' processed"

            elif feedback_type == "ignore":
                # No changes needed for ignore
                result["processed"] = True
                result["message"] = "Recommendation ignored"

            return result

        except Exception as e:
            logger.error(f"Error processing health recommendation feedback: {e}")
            result["processed"] = False
            result["message"] = f"Error processing feedback: {str(e)}"
            return result