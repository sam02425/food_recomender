"""
Configuration file for the Adaptive Artificial Participant Experiment
"""

import os
from typing import Dict, Any

class ExperimentConfig:
    """Configuration settings for the adaptive participant experiment"""

    # Experiment parameters
    NUM_PARTICIPANTS = 50
    TRIALS_PER_PARTICIPANT = 10
    BASELINE_TRIALS = 5
    ADAPTIVE_TRIALS = 5

    # OpenAI API settings (ChatGPT)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY_HERE')
    OPENAI_MODEL = "gpt-3.5-turbo"  # Alternative: "gpt-4", "gpt-4-turbo"

    # Legacy GROQ settings (for backward compatibility)
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'YOUR_GROQ_API_KEY_HERE')
    GROQ_MODEL = "llama3-8b-8192"  # Alternative: "mixtral-8x7b-32768"

    # LLM feedback settings
    LLM_FEEDBACK_FREQUENCY = 3  # Get feedback every N trials to save API usage
    ENABLE_LLM_FEEDBACK = True

    # Menu configuration (matching actual app)
    MENU_CONFIG = {
        'proteins': [
            {'name': 'Chicken', 'price': 4.50, 'dietary': ['halal', 'no_pork']},
            {'name': 'Egg', 'price': 3.00, 'dietary': ['vegetarian', 'halal']},
            {'name': 'Paneer/Indian Cheese', 'price': 4.00, 'dietary': ['vegetarian', 'halal']},
            {'name': 'Soya', 'price': 3.50, 'dietary': ['vegan', 'vegetarian', 'halal']},
            {'name': 'Potato', 'price': 2.50, 'dietary': ['vegan', 'vegetarian', 'halal']},
            {'name': 'Pepperoni', 'price': 4.50, 'dietary': ['no_beef']}
        ],
        'sauces': [
            'Curry Special', 'Malai Masala', 'Curry Masala', 'Marinara',
            'Yogurt/Raita', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce'
        ],
        'base_types': {
            'Biryani': ['Rice'],
            'Sandwich & Subs': ['Sourdough', 'Ciabatta', 'White Bread', 'Hoagie Bun'],
            'Wrap': ['Naan', 'Pitta'],
            'Bowl': ['Bowl', 'Rice Bowl'],
            'Salad': ['Mixed Greens']
        },
        'veggies': [
            'Grilled Onion', 'Bell Pepper', 'Tomato', 'Cilantro', 'Avocado',
            'Pineapple', 'Spinach', 'Jalapeño', 'Banana Pepper', 'Fried Onions',
            'Corn', 'Cabbage', 'Ghee', 'Mango Chutney'
        ],
        'garnishes': [
            'Crispy Onions', 'Fresh Cilantro', 'Pomegranate Seeds', 'Toasted Almonds'
        ]
    }

    # Dietary restrictions configuration
    DIETARY_RESTRICTIONS = {
        'vegan': {
            'name': 'Vegan',
            'description': 'No animal products',
            'excluded_proteins': ['Chicken', 'Egg', 'Paneer/Indian Cheese', 'Pepperoni'],
            'allowed_proteins': ['Soya', 'Potato'],
            'excluded_sauces': ['Malai Masala', 'Yogurt/Raita'],
            'allowed_sauces': ['Curry Special', 'Curry Masala', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce']
        },
        'vegetarian': {
            'name': 'Vegetarian',
            'description': 'No meat, fish, or poultry',
            'excluded_proteins': ['Chicken', 'Pepperoni'],
            'allowed_proteins': ['Egg', 'Paneer/Indian Cheese', 'Soya', 'Potato'],
            'excluded_sauces': [],
            'allowed_sauces': ['Curry Special', 'Malai Masala', 'Curry Masala', 'Marinara', 'Yogurt/Raita', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce']
        },
        'halal': {
            'name': 'Halal',
            'description': 'Islamic dietary laws',
            'excluded_proteins': ['Pepperoni'],
            'allowed_proteins': ['Chicken', 'Egg', 'Paneer/Indian Cheese', 'Soya', 'Potato'],
            'excluded_sauces': [],
            'allowed_sauces': ['Curry Special', 'Malai Masala', 'Curry Masala', 'Marinara', 'Yogurt/Raita', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce']
        },
        'no_beef': {
            'name': 'No Beef',
            'description': 'No beef products',
            'excluded_proteins': [],
            'allowed_proteins': ['Chicken', 'Egg', 'Paneer/Indian Cheese', 'Soya', 'Potato', 'Pepperoni'],
            'excluded_sauces': [],
            'allowed_sauces': ['Curry Special', 'Malai Masala', 'Curry Masala', 'Marinara', 'Yogurt/Raita', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce']
        },
        'no_pork': {
            'name': 'No Pork',
            'description': 'No pork products',
            'excluded_proteins': ['Pepperoni'],
            'allowed_proteins': ['Chicken', 'Egg', 'Paneer/Indian Cheese', 'Soya', 'Potato'],
            'excluded_sauces': [],
            'allowed_sauces': ['Curry Special', 'Malai Masala', 'Curry Masala', 'Marinara', 'Yogurt/Raita', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce']
        }
    }

    # Allergens configuration
    ALLERGENS = {
        'dairy': {
            'name': 'Dairy',
            'ingredients': ['milk', 'cheese', 'paneer', 'cream', 'butter', 'yogurt', 'ghee', 'whey', 'casein']
        },
        'eggs': {
            'name': 'Eggs',
            'ingredients': ['egg', 'eggs', 'egg white', 'egg yolk', 'mayonnaise']
        },
        'nuts': {
            'name': 'Tree Nuts',
            'ingredients': ['almonds', 'cashew', 'walnuts', 'pistachios', 'pecans', 'hazelnuts']
        },
        'peanuts': {
            'name': 'Peanuts',
            'ingredients': ['peanuts', 'peanut oil', 'peanut butter']
        },
        'soy': {
            'name': 'Soy',
            'ingredients': ['soy', 'soya', 'tofu', 'soy sauce', 'soybean']
        },
        'gluten': {
            'name': 'Gluten',
            'ingredients': ['wheat', 'barley', 'rye', 'naan', 'bread', 'flour']
        },
        'shellfish': {
            'name': 'Shellfish',
            'ingredients': ['shrimp', 'lobster', 'crab', 'prawns']
        },
        'fish': {
            'name': 'Fish',
            'ingredients': ['fish', 'salmon', 'tuna', 'cod']
        },
        'sesame': {
            'name': 'Sesame',
            'ingredients': ['sesame', 'tahini', 'sesame oil']
        }
    }

    # Cultural background distributions
    CULTURAL_DISTRIBUTIONS = {
        'South Asian': 0.35,  # Higher due to curry focus
        'Western': 0.25,
        'Middle Eastern': 0.15,
        'East Asian': 0.15,
        'Other': 0.10
    }

    # Dietary restriction patterns
    DIETARY_PATTERNS = {
        'vegetarian': 0.25,
        'vegan': 0.08,
        'halal': 0.12,
        'no_pork': 0.15,
        'no_beef': 0.10,
        'none': 0.30
    }

    # Allergen prevalence
    ALLERGEN_PREVALENCE = {
        'dairy': 0.08,
        'nuts': 0.06,
        'gluten': 0.05,
        'eggs': 0.04,
        'soy': 0.03,
        'peanuts': 0.02
    }

    # System performance parameters
    SYSTEM_PERFORMANCE = {
        'baseline_quality': 0.6,
        'adaptive_quality_base': 0.7,
        'adaptive_improvement_rate': 0.02,
        'dietary_accuracy_base': 0.85,
        'response_time_baseline': 2.0,
        'response_time_adaptive_penalty': 0.5,
        'failure_rates': {
            'recommendation_failure': 0.10,
            'dietary_filter_failure': 0.05,
            'slow_response': 0.03
        }
    }

    # Behavioral parameters
    BEHAVIORAL_PARAMS = {
        'base_task_time': 120,  # seconds
        'learning_bonus_per_trial': 5,
        'mood_effect_multiplier': 10,
        'fatigue_penalty_multiplier': 20,
        'tech_savviness_bonus': 15,
        'min_task_time': 30,
        'max_task_time': 300,
        'base_satisfaction': 3.0,
        'satisfaction_variance': 0.3
    }

    # Output settings
    OUTPUT_CONFIG = {
        'save_raw_data': True,
        'save_participant_profiles': True,
        'save_trial_details': True,
        'generate_summary_report': True,
        'output_format': 'json',  # 'json' or 'csv'
        'results_directory': 'results'
    }

    # Statistical analysis settings
    STATISTICAL_CONFIG = {
        'significance_level': 0.05,
        'confidence_interval': 0.95,
        'effect_size_thresholds': {
            'negligible': 0.2,
            'small': 0.5,
            'medium': 0.8,
            'large': 1.0
        }
    }

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get complete configuration as dictionary"""
        return {
            'experiment_params': {
                'num_participants': cls.NUM_PARTICIPANTS,
                'trials_per_participant': cls.TRIALS_PER_PARTICIPANT,
                'baseline_trials': cls.BASELINE_TRIALS,
                'adaptive_trials': cls.ADAPTIVE_TRIALS
            },
            'llm_settings': {
                'openai_api_key': cls.OPENAI_API_KEY,
                'openai_model': cls.OPENAI_MODEL,
                'groq_api_key': cls.GROQ_API_KEY,
                'groq_model': cls.GROQ_MODEL,
                'feedback_frequency': cls.LLM_FEEDBACK_FREQUENCY,
                'enable_feedback': cls.ENABLE_LLM_FEEDBACK
            },
            'menu_config': cls.MENU_CONFIG,
            'dietary_restrictions': cls.DIETARY_RESTRICTIONS,
            'allergens': cls.ALLERGENS,
            'cultural_distributions': cls.CULTURAL_DISTRIBUTIONS,
            'dietary_patterns': cls.DIETARY_PATTERNS,
            'allergen_prevalence': cls.ALLERGEN_PREVALENCE,
            'system_performance': cls.SYSTEM_PERFORMANCE,
            'behavioral_params': cls.BEHAVIORAL_PARAMS,
            'output_config': cls.OUTPUT_CONFIG,
            'statistical_config': cls.STATISTICAL_CONFIG
        }

    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        errors = []

        # Check that at least one API key is set
        if cls.OPENAI_API_KEY == 'YOUR_OPENAI_API_KEY_HERE' and cls.GROQ_API_KEY == 'YOUR_GROQ_API_KEY_HERE':
            errors.append("At least one API key (OpenAI or GROQ) must be set")

        if cls.NUM_PARTICIPANTS <= 0:
            errors.append("Number of participants must be positive")

        if cls.TRIALS_PER_PARTICIPANT <= 0:
            errors.append("Trials per participant must be positive")

        if cls.BASELINE_TRIALS + cls.ADAPTIVE_TRIALS != cls.TRIALS_PER_PARTICIPANT:
            errors.append("Baseline + adaptive trials must equal total trials per participant")

        # Check probability distributions sum to 1
        cultural_sum = sum(cls.CULTURAL_DISTRIBUTIONS.values())
        if abs(cultural_sum - 1.0) > 0.01:
            errors.append(f"Cultural distributions must sum to 1.0, got {cultural_sum}")

        dietary_sum = sum(cls.DIETARY_PATTERNS.values())
        if abs(dietary_sum - 1.0) > 0.01:
            errors.append(f"Dietary patterns must sum to 1.0, got {dietary_sum}")

        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True