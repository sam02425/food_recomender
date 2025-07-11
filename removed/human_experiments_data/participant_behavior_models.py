#!/usr/bin/env python3
"""
Participant Behavior Models for Artificial Participants

This module contains sophisticated behavioral models that simulate realistic
human decision-making patterns, cognitive processes, and response variability
for artificial participants in the food ordering experiment.

Author: AI Research Assistant
Date: 2024
"""

import random
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CognitiveState:
    """Represents the cognitive state of a participant"""
    attention_level: float  # 0.0 to 1.0
    mental_workload: float  # 0.0 to 1.0
    decision_confidence: float  # 0.0 to 1.0
    fatigue_level: float  # 0.0 to 1.0
    stress_level: float  # 0.0 to 1.0
    engagement_level: float  # 0.0 to 1.0

class DecisionMakingModel:
    """Models realistic human decision-making processes"""

    def __init__(self, participant_profile):
        self.profile = participant_profile
        self.decision_history = []
        self.preference_evolution = {}

    def calculate_decision_time(self, complexity: float, familiarity: float) -> float:
        """Calculate realistic decision time based on Hick's Law"""
        # Hick's Law: RT = a + b * log2(n)
        # where n is number of choices, a and b are constants

        base_time = 0.5  # Base reaction time in seconds
        choice_factor = np.log2(max(2, complexity * 10))  # Log of number of choices
        familiarity_factor = 1.0 - (familiarity * 0.3)  # Familiarity reduces time

        # Individual differences
        speed_factor = self.profile.decision_speed

        # Fatigue effect
        fatigue_penalty = self.profile.session_fatigue * 0.5

        decision_time = (base_time + choice_factor * 0.2) * familiarity_factor * speed_factor
        decision_time += fatigue_penalty

        # Add realistic variability
        decision_time += random.uniform(-0.2, 0.2)

        return max(0.3, decision_time)

    def weighted_choice(self, options: List[Dict], weights: List[float],
                       context: Dict = None) -> Dict:
        """Make a weighted choice with context and preference influence"""

        # Apply context-based adjustments
        adjusted_weights = weights.copy()

        if context:
            # Health consciousness effect
            if context.get('health_focus') and self.profile.health_consciousness > 0.6:
                for i, option in enumerate(options):
                    if option.get('calories', 0) < 150:
                        adjusted_weights[i] *= 1.3
                    elif option.get('calories', 0) > 300:
                        adjusted_weights[i] *= 0.7

            # Price sensitivity effect
            if context.get('budget_constraint') and self.profile.price_sensitivity > 0.7:
                for i, option in enumerate(options):
                    if option.get('price', 0) < 3.0:
                        adjusted_weights[i] *= 1.2
                    elif option.get('price', 0) > 5.0:
                        adjusted_weights[i] *= 0.6

            # Mood effect
            if context.get('mood') == 'happy':
                for i, option in enumerate(options):
                    if 'spicy' in option.get('name', '').lower():
                        adjusted_weights[i] *= 1.1
            elif context.get('mood') == 'stressed':
                for i, option in enumerate(options):
                    if 'comfort' in option.get('name', '').lower():
                        adjusted_weights[i] *= 1.2

        # Normalize weights
        total_weight = sum(adjusted_weights)
        if total_weight > 0:
            adjusted_weights = [w/total_weight for w in adjusted_weights]
        else:
            # Fallback to uniform distribution
            adjusted_weights = [1.0/len(options)] * len(options)

        # Make choice
        chosen_index = random.choices(range(len(options)), weights=adjusted_weights)[0]
        chosen_option = options[chosen_index]

        # Record decision
        self.decision_history.append({
            'timestamp': datetime.now(),
            'options': options,
            'weights': adjusted_weights,
            'chosen': chosen_option,
            'context': context
        })

        return chosen_option

    def evaluate_recommendation(self, recommendation: Dict, context: Dict) -> Tuple[bool, float]:
        """Evaluate whether to accept a recommendation"""

        # Base acceptance probability
        base_acceptance = self.profile.recommendation_trust

        # Context adjustments
        if context.get('trial_number', 1) <= 2:
            # More likely to accept recommendations in early trials
            base_acceptance *= 1.2

        if context.get('condition') == 'adaptive':
            # Slightly higher acceptance in adaptive condition
            base_acceptance *= 1.1

        # Fatigue effect
        if self.profile.session_fatigue > 0.5:
            # More likely to accept recommendations when tired
            base_acceptance *= 1.3

        # Technical proficiency effect
        if self.profile.technical_proficiency == 'low':
            base_acceptance *= 1.2
        elif self.profile.technical_proficiency == 'high':
            base_acceptance *= 0.9

        # Cap at reasonable levels
        base_acceptance = min(0.95, base_acceptance)

        # Make decision
        accept = random.random() < base_acceptance
        confidence = random.uniform(0.6, 0.95) if accept else random.uniform(0.3, 0.7)

        return accept, confidence

class EmotionalStateModel:
    """Models emotional state changes and mood transitions"""

    def __init__(self, participant_profile):
        self.profile = participant_profile
        self.current_emotion = 'neutral'
        self.emotion_history = []
        self.emotion_stability = 0.7  # How stable emotions are

    def update_emotion(self, context: Dict) -> str:
        """Update emotional state based on context and personality"""

        # Base emotion probabilities
        emotion_probs = {
            'happy': 0.15,
            'neutral': 0.30,
            'focused': 0.20,
            'excited': 0.15,
            'contemplative': 0.15,
            'slightly_stressed': 0.05
        }

        # Context adjustments
        if context.get('condition') == 'adaptive':
            emotion_probs['excited'] += 0.05
            emotion_probs['happy'] += 0.03

        if context.get('trial_number', 1) > 3:
            emotion_probs['slightly_stressed'] += 0.02
            emotion_probs['focused'] += 0.03

        # Fatigue effect
        if self.profile.session_fatigue > 0.6:
            emotion_probs['neutral'] += 0.1
            emotion_probs['slightly_stressed'] += 0.05

        # Personality effects
        if self.profile.mood_variability > 0.7:
            # More emotional variability
            emotion_probs['excited'] += 0.05
            emotion_probs['happy'] += 0.03
        elif self.profile.mood_variability < 0.3:
            # More stable emotions
            emotion_probs['neutral'] += 0.1
            emotion_probs['focused'] += 0.05

        # Normalize probabilities
        total_prob = sum(emotion_probs.values())
        emotion_probs = {k: v/total_prob for k, v in emotion_probs.items()}

        # Determine new emotion
        emotions = list(emotion_probs.keys())
        probabilities = list(emotion_probs.values())

        # Consider emotion stability
        if random.random() < self.emotion_stability and self.current_emotion in emotions:
            # Maintain current emotion
            new_emotion = self.current_emotion
        else:
            # Transition to new emotion
            new_emotion = random.choices(emotions, weights=probabilities)[0]

        self.current_emotion = new_emotion

        # Record emotion change
        self.emotion_history.append({
            'timestamp': datetime.now(),
            'emotion': new_emotion,
            'context': context
        })

        return new_emotion

class LearningModel:
    """Models how participants learn and adapt their preferences"""

    def __init__(self, participant_profile):
        self.profile = participant_profile
        self.learned_preferences = {}
        self.adaptation_rate = 0.1  # How quickly preferences adapt

    def update_preferences(self, choice: Dict, outcome: Dict):
        """Update learned preferences based on choice outcome"""

        choice_key = choice.get('name', 'unknown')

        if choice_key not in self.learned_preferences:
            self.learned_preferences[choice_key] = {
                'positive_experiences': 0,
                'negative_experiences': 0,
                'total_choices': 0,
                'last_used': None
            }

        pref = self.learned_preferences[choice_key]
        pref['total_choices'] += 1
        pref['last_used'] = datetime.now()

        # Update based on outcome
        if outcome.get('satisfaction', 5.0) > 5.5:
            pref['positive_experiences'] += 1
        elif outcome.get('satisfaction', 5.0) < 4.0:
            pref['negative_experiences'] += 1

    def get_preference_weight(self, option: Dict) -> float:
        """Get preference weight for an option based on learning"""

        option_key = option.get('name', 'unknown')

        if option_key not in self.learned_preferences:
            return 1.0  # Neutral preference for new options

        pref = self.learned_preferences[option_key]

        if pref['total_choices'] == 0:
            return 1.0

        # Calculate preference based on experience
        positive_ratio = pref['positive_experiences'] / pref['total_choices']
        negative_ratio = pref['negative_experiences'] / pref['total_choices']

        # Preference weight calculation
        weight = 1.0 + (positive_ratio - negative_ratio) * self.adaptation_rate

        # Consider recency
        if pref['last_used']:
            time_since_last = (datetime.now() - pref['last_used']).total_seconds()
            if time_since_last < 300:  # Within 5 minutes
                weight *= 0.9  # Slight preference against recent choices

        return max(0.1, weight)

class FatigueModel:
    """Models cognitive fatigue and its effects on performance"""

    def __init__(self, participant_profile):
        self.profile = participant_profile
        self.fatigue_level = 0.0
        self.performance_history = []

    def update_fatigue(self, trial_number: int, condition: str,
                      completion_time: float, errors: int):
        """Update fatigue level based on performance"""

        # Base fatigue increase
        fatigue_increase = 0.05

        # Trial number effect
        if trial_number > 3:
            fatigue_increase += 0.02

        # Performance-based fatigue
        if completion_time > 10.0:
            fatigue_increase += 0.03

        if errors > 1:
            fatigue_increase += 0.02

        # Condition effect
        if condition == 'baseline':
            fatigue_increase += 0.01  # Baseline is slightly more fatiguing

        # Individual differences
        if self.profile.technical_proficiency == 'low':
            fatigue_increase *= 1.2
        elif self.profile.technical_proficiency == 'high':
            fatigue_increase *= 0.8

        # Update fatigue level
        self.fatigue_level = min(1.0, self.fatigue_level + fatigue_increase)

        # Record performance
        self.performance_history.append({
            'trial_number': trial_number,
            'condition': condition,
            'completion_time': completion_time,
            'errors': errors,
            'fatigue_level': self.fatigue_level,
            'timestamp': datetime.now()
        })

    def get_fatigue_effects(self) -> Dict[str, float]:
        """Get the effects of current fatigue level"""

        effects = {
            'decision_speed_multiplier': 1.0 + (self.fatigue_level * 0.3),
            'error_probability_multiplier': 1.0 + (self.fatigue_level * 0.5),
            'satisfaction_penalty': self.fatigue_level * 0.3,
            'nasa_tlx_bonus': self.fatigue_level * 20.0
        }

        return effects

    def apply_fatigue_effects(self, base_value: float, effect_type: str) -> float:
        """Apply fatigue effects to a base value"""

        effects = self.get_fatigue_effects()

        if effect_type == 'decision_speed':
            return base_value * effects['decision_speed_multiplier']
        elif effect_type == 'error_probability':
            return base_value * effects['error_probability_multiplier']
        elif effect_type == 'satisfaction':
            return max(1.0, base_value - effects['satisfaction_penalty'])
        elif effect_type == 'nasa_tlx':
            return min(100.0, base_value + effects['nasa_tlx_bonus'])
        else:
            return base_value

class SocialInfluenceModel:
    """Models social influence and conformity effects"""

    def __init__(self, participant_profile):
        self.profile = participant_profile
        self.conformity_tendency = random.uniform(0.1, 0.4)
        self.social_proof_sensitivity = random.uniform(0.2, 0.6)

    def evaluate_social_proof(self, recommendation: Dict,
                            popularity_data: Dict = None) -> float:
        """Evaluate the influence of social proof on decision making"""

        if not popularity_data:
            return 0.0

        # Base social proof effect
        social_effect = 0.0

        # Popularity effect
        if popularity_data.get('popularity_score', 0) > 0.7:
            social_effect += 0.2
        elif popularity_data.get('popularity_score', 0) < 0.3:
            social_effect -= 0.1

        # Review effect
        if popularity_data.get('average_rating', 0) > 4.5:
            social_effect += 0.15
        elif popularity_data.get('average_rating', 0) < 3.5:
            social_effect -= 0.1

        # Individual differences
        social_effect *= self.social_proof_sensitivity

        return social_effect

    def apply_conformity_pressure(self, choice: Dict,
                                social_context: Dict) -> Dict:
        """Apply conformity pressure to a choice"""

        if not social_context.get('group_preferences'):
            return choice

        group_prefs = social_context['group_preferences']

        # Check if choice aligns with group
        choice_name = choice.get('name', '')
        group_alignment = 0.0

        for group_choice in group_prefs:
            if choice_name in group_choice.get('name', ''):
                group_alignment = group_choice.get('weight', 0.0)
                break

        # Apply conformity effect
        conformity_bonus = group_alignment * self.conformity_tendency

        # Modify choice weight
        modified_choice = choice.copy()
        modified_choice['weight'] = choice.get('weight', 1.0) + conformity_bonus

        return modified_choice

class BehavioralIntegrator:
    """Integrates all behavioral models for comprehensive participant simulation"""

    def __init__(self, participant_profile):
        self.profile = participant_profile
        self.decision_model = DecisionMakingModel(participant_profile)
        self.emotion_model = EmotionalStateModel(participant_profile)
        self.learning_model = LearningModel(participant_profile)
        self.fatigue_model = FatigueModel(participant_profile)
        self.social_model = SocialInfluenceModel(participant_profile)

    def simulate_choice(self, options: List[Dict], context: Dict) -> Tuple[Dict, float]:
        """Simulate a complete choice process"""

        # Update emotional state
        emotion = self.emotion_model.update_emotion(context)
        context['mood'] = emotion

        # Apply learning effects
        for option in options:
            option['weight'] = self.learning_model.get_preference_weight(option)

        # Apply social influence
        if context.get('social_context'):
            options = [self.social_model.apply_conformity_pressure(opt, context['social_context'])
                      for opt in options]

        # Calculate decision time
        complexity = len(options)
        familiarity = context.get('familiarity', 0.5)
        decision_time = self.decision_model.calculate_decision_time(complexity, familiarity)

        # Apply fatigue effects
        decision_time = self.fatigue_model.apply_fatigue_effects(decision_time, 'decision_speed')

        # Make choice
        weights = [opt.get('weight', 1.0) for opt in options]
        choice = self.decision_model.weighted_choice(options, weights, context)

        return choice, decision_time

    def evaluate_recommendation(self, recommendation: Dict, context: Dict) -> Tuple[bool, float]:
        """Evaluate recommendation acceptance"""

        # Apply fatigue effects to trust
        base_trust = self.profile.recommendation_trust
        fatigue_effects = self.fatigue_model.get_fatigue_effects()

        # Fatigue increases recommendation acceptance
        adjusted_trust = base_trust * (1.0 + fatigue_effects['satisfaction_penalty'])

        # Use decision model for evaluation
        accept, confidence = self.decision_model.evaluate_recommendation(
            recommendation, context
        )

        return accept, confidence

    def update_models(self, trial_result: Dict):
        """Update all behavioral models based on trial results"""

        # Update learning model
        if trial_result.get('order_data'):
            self.learning_model.update_preferences(
                trial_result['order_data'],
                {'satisfaction': trial_result.get('satisfaction_rating', 5.0)}
            )

        # Update fatigue model
        self.fatigue_model.update_fatigue(
            trial_result.get('trial_number', 1),
            trial_result.get('condition', 'baseline'),
            trial_result.get('completion_time_seconds', 6.0),
            trial_result.get('error_count', 0)
        )

        # Update profile fatigue
        self.profile.session_fatigue = self.fatigue_model.fatigue_level

    def get_cognitive_state(self) -> CognitiveState:
        """Get current cognitive state"""

        fatigue_effects = self.fatigue_model.get_fatigue_effects()

        return CognitiveState(
            attention_level=max(0.1, 1.0 - self.fatigue_model.fatigue_level * 0.5),
            mental_workload=min(1.0, 0.3 + self.fatigue_model.fatigue_level * 0.7),
            decision_confidence=max(0.2, 1.0 - self.fatigue_model.fatigue_level * 0.4),
            fatigue_level=self.fatigue_model.fatigue_level,
            stress_level=min(1.0, 0.1 + self.fatigue_model.fatigue_level * 0.3),
            engagement_level=max(0.3, 1.0 - self.fatigue_model.fatigue_level * 0.6)
        )