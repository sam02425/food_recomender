# /agents/Learner_Ag.py
"""
Learner Agent for reinforcement learning based on feedback.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("learner_agent")

class LearnerAgent:
    """Agent for learning from user feedback across other agents."""

    def __init__(self, learning_data_path: str):
        """
        Initialize the learner agent.

        Args:
            learning_data_path: Path to store learning data in JSON format
        """
        self.learning_data_path = learning_data_path
        self.learning_data = self._load_learning_data()

        # Initialize learning models for each recommendation type
        if "models" not in self.learning_data:
            self.learning_data["models"] = {
                "health": self._init_model("health"),
                "weather": self._init_model("weather"),
                "dish_name": self._init_model("dish_name")
            }

        # Initialize customer preferences
        if "customer_preferences" not in self.learning_data:
            self.learning_data["customer_preferences"] = {}

        # Save initial data
        self._save_learning_data()

        logger.info("Learner agent initialized")

    def _init_model(self, model_type: str) -> Dict[str, Any]:
        """
        Initialize a learning model structure.

        Args:
            model_type: Type of model to initialize

        Returns:
            Initialized model structure
        """
        model = {
            "type": model_type,
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "feedback_count": 0,
            "accept_count": 0,
            "ignore_count": 0,
            "custom_count": 0,
            "patterns": {},
            "context_weights": {},
            "feature_weights": {}
        }

        # Add model-specific attributes
        if model_type == "health":
            model["activity_weights"] = {
                "study": 1.0,
                "active": 1.0,
                "gym": 1.0,
                "work": 1.0,
                "chilling": 1.0
            }
            model["feature_weights"] = {
                "activity_level": 0.5,
                "mood": 0.3,
                "previous_orders": 0.2
            }

        elif model_type == "weather":
            model["condition_weights"] = {
                "sunny": 1.0,
                "rainy": 1.0,
                "cloudy": 1.0,
                "partly_cloudy": 1.0,
                "hot": 1.0,
                "cold": 1.0,
                "snowy": 1.0
            }
            model["time_weights"] = {
                "morning": 1.0,
                "afternoon": 1.0,
                "evening": 1.0
            }
            model["feature_weights"] = {
                "weather_condition": 0.4,
                "time_of_day": 0.4,
                "mood": 0.2
            }

        elif model_type == "dish_name":
            model["format_weights"] = {
                "format_1": 1.0,  # [Customer]'s [Weather] [Protein] [Base]
                "format_2": 1.0,  # [Customer]'s [Mood] [Protein] [Base]
                "format_3": 1.0,  # [Weather] [Protein] [Base] by [Customer]
                "format_4": 1.0,  # [Protein Adj] [Protein] [Base] ([Weather/Mood])
                "format_5": 1.0   # [Customer]'s [Protein Adj] [Base] Special
            }
            model["feature_weights"] = {
                "weather": 0.3,
                "mood": 0.3,
                "protein": 0.2,
                "base_type": 0.2
            }

        return model

    def _load_learning_data(self) -> Dict[str, Any]:
        """
        Load learning data from JSON file.

        Returns:
            Learning data
        """
        if os.path.exists(self.learning_data_path):
            try:
                with open(self.learning_data_path, 'r') as file:
                    data = json.load(file)
                    logger.info(f"Loaded learning data with {len(data.get('models', {}))} models")
                    return data
            except Exception as e:
                logger.error(f"Error loading learning data: {e}")

        # Return empty structure if file doesn't exist or error occurs
        return {
            "models": {},
            "customer_preferences": {},
            "feedback_history": [],
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def _save_learning_data(self) -> bool:
        """
        Save learning data to JSON file.

        Returns:
            Success status
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.learning_data_path), exist_ok=True)

            # Update timestamp
            self.learning_data["updated_at"] = datetime.now().isoformat()

            # Write to file
            with open(self.learning_data_path, 'w') as file:
                json.dump(self.learning_data, file, indent=2)

            logger.info(f"Saved learning data to {self.learning_data_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
            return False

    def process_feedback(self, recommendation_type: str, feedback: str,
                       custom_suggestion: Optional[str] = None,
                       customer_id: Optional[str] = None,
                       context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process feedback and update learning models.

        Args:
            recommendation_type: Type of recommendation (health, weather, dish_name)
            feedback: Feedback type (accept, ignore, custom)
            custom_suggestion: Custom suggestion if provided
            customer_id: Optional customer ID for personalization
            context: Additional context for the feedback

        Returns:
            Processing result
        """
        result = {
            "processed": False,
            "model_updated": False,
            "customer_updated": False,
            "message": ""
        }

        # Validate recommendation type
        if recommendation_type not in ["health", "weather", "dish_name"]:
            result["message"] = f"Invalid recommendation type: {recommendation_type}"
            return result

        # Get model
        model = self.learning_data["models"].get(recommendation_type)
        if not model:
            # Initialize if not exists
            model = self._init_model(recommendation_type)
            self.learning_data["models"][recommendation_type] = model

        # Create feedback record
        feedback_record = {
            "type": recommendation_type,
            "feedback": feedback,
            "custom_suggestion": custom_suggestion,
            "customer_id": customer_id,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }

        # Add to history
        self.learning_data.setdefault("feedback_history", []).append(feedback_record)

        # Update model based on feedback
        model["feedback_count"] += 1
        model["updated_at"] = datetime.now().isoformat()

        if feedback == "accept":
            model["accept_count"] += 1
            self._update_model_weights(model, "accept", context, custom_suggestion)

        elif feedback == "ignore":
            model["ignore_count"] += 1
            self._update_model_weights(model, "ignore", context, custom_suggestion)

        elif feedback == "custom" and custom_suggestion:
            model["custom_count"] += 1
            self._update_model_weights(model, "custom", context, custom_suggestion)

        # Update customer preferences if customer ID provided
        if customer_id:
            self._update_customer_preferences(customer_id, recommendation_type, feedback, custom_suggestion, context)
            result["customer_updated"] = True

        # Save updated data
        save_success = self._save_learning_data()

        result["processed"] = True
        result["model_updated"] = True
        result["message"] = f"Successfully processed {feedback} feedback for {recommendation_type}"

        if not save_success:
            result["message"] += " (Warning: Failed to save learning data)"

        logger.info(f"Processed {feedback} feedback for {recommendation_type}")
        return result

    def _update_model_weights(self, model: Dict[str, Any], feedback_type: str,
                           context: Optional[Dict[str, Any]],
                           custom_suggestion: Optional[str]) -> None:
        """
        Update model weights based on feedback.

        Args:
            model: Model to update
            feedback_type: Type of feedback
            context: Context for the feedback
            custom_suggestion: Custom suggestion if applicable
        """
        if not context:
            return

        model_type = model["type"]

        # Extract relevant context variables based on model type
        if model_type == "health":
            activity_level = context.get("activity_level")
            mood = context.get("mood")

            # Update activity weights
            if activity_level and activity_level in model["activity_weights"]:
                if feedback_type == "accept":
                    # Increase weight slightly
                    model["activity_weights"][activity_level] *= 1.05
                elif feedback_type == "ignore":
                    # Decrease weight slightly
                    model["activity_weights"][activity_level] *= 0.98
                elif feedback_type == "custom":
                    # Custom feedback has stronger impact
                    model["activity_weights"][activity_level] *= 1.1

            # Update context weights
            if mood:
                context_key = f"mood_{mood}"
                model["context_weights"][context_key] = model["context_weights"].get(context_key, 1.0)

                if feedback_type == "accept":
                    model["context_weights"][context_key] *= 1.05
                elif feedback_type == "custom":
                    model["context_weights"][context_key] *= 1.1

        elif model_type == "weather":
            weather_condition = context.get("weather", {}).get("condition")
            time_of_day = context.get("time_of_day")

            # Update condition weights
            if weather_condition and weather_condition in model["condition_weights"]:
                if feedback_type == "accept":
                    model["condition_weights"][weather_condition] *= 1.05
                elif feedback_type == "ignore":
                    model["condition_weights"][weather_condition] *= 0.98
                elif feedback_type == "custom":
                    model["condition_weights"][weather_condition] *= 1.1

            # Update time weights
            if time_of_day and time_of_day in model["time_weights"]:
                if feedback_type == "accept":
                    model["time_weights"][time_of_day] *= 1.05
                elif feedback_type == "ignore":
                    model["time_weights"][time_of_day] *= 0.98
                elif feedback_type == "custom":
                    model["time_weights"][time_of_day] *= 1.1

        elif model_type == "dish_name":
            # Update format weights if format information available
            format_used = context.get("current_selections", {}).get("format_used", "")

            if format_used.startswith("Format "):
                format_num = format_used.split(" ")[1]
                format_key = f"format_{format_num}"

                if format_key in model["format_weights"]:
                    if feedback_type == "accept":
                        model["format_weights"][format_key] *= 1.05
                    elif feedback_type == "ignore":
                        model["format_weights"][format_key] *= 0.98
                    elif feedback_type == "custom":
                        # Slight decrease for custom since they didn't like the format
                        model["format_weights"][format_key] *= 0.95

    def _update_customer_preferences(self, customer_id: str, recommendation_type: str,
                                  feedback: str, custom_suggestion: Optional[str],
                                  context: Optional[Dict[str, Any]]) -> None:
        """
        Update customer preferences based on feedback.

        Args:
            customer_id: Customer ID
            recommendation_type: Type of recommendation
            feedback: Feedback type
            custom_suggestion: Custom suggestion if applicable
            context: Context for the feedback
        """
        # Initialize customer preferences if not exists
        if customer_id not in self.learning_data["customer_preferences"]:
            self.learning_data["customer_preferences"][customer_id] = {
                "health": {
                    "preferred_proteins": {},
                    "preferred_sauces": {},
                    "preferred_base_types": {},
                    "activity_preferences": {}
                },
                "weather": {
                    "preferred_base_types": {},
                    "condition_preferences": {},
                    "time_preferences": {}
                },
                "dish_name": {
                    "preferred_formats": {},
                    "custom_names": []
                },
                "first_seen": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }

        customer_prefs = self.learning_data["customer_preferences"][customer_id]
        customer_prefs["last_updated"] = datetime.now().isoformat()

        # Process feedback based on recommendation type
        if recommendation_type == "health":
            if feedback == "accept" and context and "current_selections" in context:
                selections = context["current_selections"]

                # Update protein preferences
                if "protein" in selections:
                    protein = selections["protein"]
                    customer_prefs["health"]["preferred_proteins"][protein] = customer_prefs["health"]["preferred_proteins"].get(protein, 0) + 1

                # Update sauce preferences
                if "sauce" in selections:
                    sauce = selections["sauce"]
                    customer_prefs["health"]["preferred_sauces"][sauce] = customer_prefs["health"]["preferred_sauces"].get(sauce, 0) + 1

                # Update base type preferences
                if "base_type" in selections:
                    base_type = selections["base_type"]
                    customer_prefs["health"]["preferred_base_types"][base_type] = customer_prefs["health"]["preferred_base_types"].get(base_type, 0) + 1

            # Update activity preferences
            if context and "activity_level" in context:
                activity = context["activity_level"]
                activity_prefs = customer_prefs["health"]["activity_preferences"]

                if activity not in activity_prefs:
                    activity_prefs[activity] = {
                        "count": 0,
                        "accepted": 0,
                        "ignored": 0,
                        "custom": 0
                    }

                activity_prefs[activity]["count"] += 1

                if feedback == "accept":
                    activity_prefs[activity]["accepted"] += 1
                elif feedback == "ignore":
                    activity_prefs[activity]["ignored"] += 1
                elif feedback == "custom":
                    activity_prefs[activity]["custom"] += 1

        elif recommendation_type == "weather":
            if feedback == "accept" and context and "current_selections" in context:
                selections = context["current_selections"]

                # Update base type preferences
                if "base_type" in selections:
                    base_type = selections["base_type"]
                    customer_prefs["weather"]["preferred_base_types"][base_type] = customer_prefs["weather"]["preferred_base_types"].get(base_type, 0) + 1

            # Update condition preferences
            if context and "weather" in context and "condition" in context["weather"]:
                condition = context["weather"]["condition"]
                condition_prefs = customer_prefs["weather"]["condition_preferences"]

                if condition not in condition_prefs:
                    condition_prefs[condition] = {
                        "count": 0,
                        "accepted": 0,
                        "ignored": 0,
                        "custom": 0
                    }

                condition_prefs[condition]["count"] += 1

                if feedback == "accept":
                    condition_prefs[condition]["accepted"] += 1
                elif feedback == "ignore":
                    condition_prefs[condition]["ignored"] += 1
                elif feedback == "custom":
                    condition_prefs[condition]["custom"] += 1

            # Update time preferences
            if context and "time_of_day" in context:
                time_of_day = context["time_of_day"]
                time_prefs = customer_prefs["weather"]["time_preferences"]

                if time_of_day not in time_prefs:
                    time_prefs[time_of_day] = {
                        "count": 0,
                        "accepted": 0,
                        "ignored": 0,
                        "custom": 0
                    }

                time_prefs[time_of_day]["count"] += 1

                if feedback == "accept":
                    time_prefs[time_of_day]["accepted"] += 1
                elif feedback == "ignore":
                    time_prefs[time_of_day]["ignored"] += 1
                elif feedback == "custom":
                    time_prefs[time_of_day]["custom"] += 1

        elif recommendation_type == "dish_name":
            # Update format preferences
            if context and "current_selections" in context and "format_used" in context["current_selections"]:
                format_used = context["current_selections"]["format_used"]

                if format_used.startswith("Format "):
                    format_num = format_used.split(" ")[1]
                    format_key = f"format_{format_num}"

                    customer_prefs["dish_name"]["preferred_formats"][format_key] = customer_prefs["dish_name"]["preferred_formats"].get(format_key, 0) + 1

            # Store custom names
            if feedback == "custom" and custom_suggestion:
                customer_prefs["dish_name"]["custom_names"].append({
                    "name": custom_suggestion,
                    "timestamp": datetime.now().isoformat()
                })

    def get_customer_preferences(self, customer_id: str) -> Dict[str, Any]:
        """
        Get customer preferences.

        Args:
            customer_id: Customer ID

        Returns:
            Customer preference data or empty dict if not found
        """
        return self.learning_data.get("customer_preferences", {}).get(customer_id, {})

    def get_model_insights(self, model_type: str) -> Dict[str, Any]:
        """
        Get insights about a learning model.

        Args:
            model_type: Type of model (health, weather, dish_name)

        Returns:
            Model insights
        """
        model = self.learning_data.get("models", {}).get(model_type)

        if not model:
            return {
                "found": False,
                "message": f"No model found for type: {model_type}"
            }

        # Calculate acceptance rate
        feedback_count = model.get("feedback_count", 0)
        accept_count = model.get("accept_count", 0)
        ignore_count = model.get("ignore_count", 0)
        custom_count = model.get("custom_count", 0)

        acceptance_rate = (accept_count / feedback_count) * 100 if feedback_count > 0 else 0
        custom_rate = (custom_count / feedback_count) * 100 if feedback_count > 0 else 0

        # Get model-specific insights
        insights = {
            "type": model_type,
            "feedback_count": feedback_count,
            "acceptance_rate": round(acceptance_rate, 2),
            "custom_rate": round(custom_rate, 2),
            "created_at": model.get("created_at"),
            "updated_at": model.get("updated_at"),
            "feature_weights": model.get("feature_weights", {}),
            "found": True
        }

        # Add model-specific weights
        if model_type == "health":
            insights["activity_weights"] = model.get("activity_weights", {})

        elif model_type == "weather":
            insights["condition_weights"] = model.get("condition_weights", {})
            insights["time_weights"] = model.get("time_weights", {})

        elif model_type == "dish_name":
            insights["format_weights"] = model.get("format_weights", {})

        return insights

    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Get statistics about feedback across all models.

        Returns:
            Feedback statistics
        """
        stats = {
            "total_feedback": 0,
            "health": {
                "total": 0,
                "accept": 0,
                "ignore": 0,
                "custom": 0
            },
            "weather": {
                "total": 0,
                "accept": 0,
                "ignore": 0,
                "custom": 0
            },
            "dish_name": {
                "total": 0,
                "accept": 0,
                "ignore": 0,
                "custom": 0
            }
        }

        # Process feedback history
        for feedback in self.learning_data.get("feedback_history", []):
            rec_type = feedback.get("type")
            feedback_type = feedback.get("feedback")

            if rec_type in stats:
                stats[rec_type]["total"] += 1
                stats["total_feedback"] += 1

                if feedback_type in ["accept", "ignore", "custom"]:
                    stats[rec_type][feedback_type] += 1

        # Calculate percentages
        for rec_type in ["health", "weather", "dish_name"]:
            total = stats[rec_type]["total"]

            if total > 0:
                stats[rec_type]["accept_pct"] = round((stats[rec_type]["accept"] / total) * 100, 2)
                stats[rec_type]["ignore_pct"] = round((stats[rec_type]["ignore"] / total) * 100, 2)
                stats[rec_type]["custom_pct"] = round((stats[rec_type]["custom"] / total) * 100, 2)
            else:
                stats[rec_type]["accept_pct"] = 0
                stats[rec_type]["ignore_pct"] = 0
                stats[rec_type]["custom_pct"] = 0

        return stats

    def reset_model(self, model_type: str) -> Dict[str, Any]:
        """
        Reset a learning model to its initial state.

        Args:
            model_type: Type of model to reset

        Returns:
            Reset result
        """
        if model_type not in ["health", "weather", "dish_name"]:
            return {
                "reset": False,
                "message": f"Invalid model type: {model_type}"
            }

        # Initialize new model
        self.learning_data["models"][model_type] = self._init_model(model_type)

        # Save changes
        success = self._save_learning_data()

        logger.info(f"Reset {model_type} model")

        return {
            "reset": success,
            "message": f"Model {model_type} reset successfully" if success else f"Error resetting model {model_type}"
        }

    def backup_learning_data(self, backup_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a backup of learning data.

        Args:
            backup_path: Optional path for backup file

        Returns:
            Backup result
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{os.path.splitext(self.learning_data_path)[0]}_backup_{timestamp}.json"

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)

            # Copy data to backup file
            with open(backup_path, 'w') as file:
                json.dump(self.learning_data, file, indent=2)

            logger.info(f"Created learning data backup at {backup_path}")

            return {
                "success": True,
                "backup_path": backup_path,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error creating backup: {e}")

            return {
                "success": False,
                "message": f"Error creating backup: {str(e)}"
            }