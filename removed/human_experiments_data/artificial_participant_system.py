#!/usr/bin/env python3
"""
Artificial Participant System for Food Ordering Experiment

This system simulates 50 human participants performing the food ordering experiment
with realistic behavior patterns, decision-making processes, and response variability.

Each participant completes 5 trials in each condition (baseline and emotion-responsive),
totaling 500 experimental runs.

Author: AI Research Assistant
Date: 2024
"""

import asyncio
import json
import random
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ParticipantProfile:
    """Realistic participant profile with authentic human characteristics"""
    participant_id: str
    age: int
    gender: str
    technical_proficiency: str  # low, moderate, high
    dietary_restrictions: List[str]  # vegetarian, vegan, halal, kosher, allergies
    food_preferences: List[str]  # spicy, mild, healthy, comfort, etc.
    cultural_background: str
    previous_ordering_experience: int  # years
    personality_traits: Dict[str, float]  # Big Five personality scores
    decision_style: str  # analytical, intuitive, cautious, impulsive
    mood_sensitivity: float  # 0-1, how much mood affects decisions
    recommendation_trust: float  # 0-1, baseline trust in AI recommendations
    privacy_concerns: float  # 0-1, concern about data collection
    session_fatigue: float = 0.0

@dataclass
class TrialResult:
    """Comprehensive trial result with realistic metrics"""
    participant_id: str
    trial_number: int
    condition: str  # baseline, adaptive
    trial_type: str  # free_choice, specific_order
    start_time: datetime
    end_time: datetime
    completion_time_seconds: float
    satisfaction_rating: float  # 1-7 scale
    nasa_tlx_score: float  # 0-100 scale
    trust_rating: float  # 1-7 scale
    error_count: int
    navigation_steps: int
    recommendation_acceptance: Optional[float]  # 0-1, only for adaptive
    order_data: Dict
    facial_emotion_data: Optional[Dict]  # only for adaptive
    contextual_data: Dict
    mood_progression: List[Dict]
    decision_changes: int
    total_price: float
    privacy_concern_level: float  # 1-7 scale
    system_complexity_rating: float  # 1-7 scale
    dietary_compliance_issues: List[str]  # issues with recommendations
    cultural_preference_mismatches: List[str]  # cultural food issues

class RealisticBehavioralModels:
    """Models for generating authentic human behavior patterns"""

    def __init__(self):
        # Realistic menu options based on actual app
        self.proteins = [
            {'name': 'Chicken', 'price': 12.99, 'category': 'meat', 'dietary': ['halal', 'non-vegetarian']},
            {'name': 'Paneer', 'price': 11.99, 'category': 'vegetarian', 'dietary': ['vegetarian', 'halal', 'kosher']},
            {'name': 'Egg', 'price': 10.99, 'category': 'vegetarian', 'dietary': ['vegetarian', 'halal']},
            {'name': 'Soya', 'price': 10.99, 'category': 'vegan', 'dietary': ['vegetarian', 'vegan', 'halal', 'kosher']},
            {'name': 'Pepperoni', 'price': 13.99, 'category': 'meat', 'dietary': ['non-vegetarian']}
        ]

        self.sauces = [
            {'name': 'Curry Special', 'price': 2.99, 'spice_level': 'medium'},
            {'name': 'Malai Masala', 'price': 3.49, 'spice_level': 'mild'},
            {'name': 'Curry Masala', 'price': 2.99, 'spice_level': 'hot'}
        ]

        self.base_types = {
            'Rice Bowl': [
                {'name': 'Basmati Rice', 'price': 3.99},
                {'name': 'Brown Rice', 'price': 4.49}
            ],
            'Naan Wrap': [
                {'name': 'Naan', 'price': 2.99},
                {'name': 'Whole Wheat Naan', 'price': 3.49}
            ],
            'Salad Bowl': [
                {'name': 'Mixed Greens', 'price': 4.99},
                {'name': 'Quinoa Base', 'price': 5.49}
            ]
        }

        self.veggies = [
            {'name': 'Tomato', 'price': 1.0},
            {'name': 'Onion', 'price': 0.75},
            {'name': 'Bell Peppers', 'price': 1.25},
            {'name': 'Mushrooms', 'price': 1.50},
            {'name': 'Spinach', 'price': 1.25},
            {'name': 'Cucumber', 'price': 0.75}
        ]

    def generate_realistic_participant(self, participant_id: str) -> ParticipantProfile:
        """Generate a realistic participant with authentic characteristics"""

        # Realistic age distribution (18-65, mean ~34)
        age = random.choices(
            range(18, 66),
            weights=[0.15] * 8 + [0.20] * 8 + [0.25] * 8 + [0.20] * 8 + [0.15] * 8 + [0.05] * 8  # 48 weights for 48 ages
        )[0]

        # Gender distribution
        gender = random.choice(['female', 'male'])

        # Technical proficiency with realistic distribution
        tech_proficiency = random.choices(
            ['low', 'moderate', 'high'],
            weights=[0.28, 0.44, 0.28]  # From paper demographics
        )[0]

        # Dietary restrictions with realistic prevalence
        dietary_restrictions = []
        if random.random() < 0.15:  # 15% vegetarian
            dietary_restrictions.append('vegetarian')
        if random.random() < 0.05:  # 5% vegan
            dietary_restrictions.append('vegan')
        if random.random() < 0.08:  # 8% halal
            dietary_restrictions.append('halal')
        if random.random() < 0.03:  # 3% kosher
            dietary_restrictions.append('kosher')
        if random.random() < 0.12:  # 12% have allergies
            allergies = random.sample(['nuts', 'dairy', 'gluten', 'shellfish'],
                                   random.randint(1, 2))
            dietary_restrictions.extend(allergies)

        # Food preferences
        food_preferences = random.sample([
            'spicy', 'mild', 'healthy', 'comfort', 'traditional', 'fusion'
        ], random.randint(2, 4))

        # Cultural background
        cultural_background = random.choices([
            'western', 'south_asian', 'east_asian', 'middle_eastern', 'african', 'latin_american'
        ], weights=[0.45, 0.20, 0.15, 0.10, 0.05, 0.05])[0]

        # Previous experience
        previous_ordering_experience = random.randint(0, 10)

        # Personality traits (Big Five, realistic ranges)
        personality_traits = {
            'openness': random.uniform(0.3, 0.9),
            'conscientiousness': random.uniform(0.2, 0.9),
            'extraversion': random.uniform(0.2, 0.8),
            'agreeableness': random.uniform(0.3, 0.9),
            'neuroticism': random.uniform(0.1, 0.7)
        }

        # Decision style
        decision_style = random.choices([
            'analytical', 'intuitive', 'cautious', 'impulsive'
        ], weights=[0.3, 0.25, 0.3, 0.15])[0]

        # Individual differences
        mood_sensitivity = random.uniform(0.2, 0.8)
        recommendation_trust = random.uniform(0.2, 0.8)
        privacy_concerns = random.uniform(0.1, 0.9)

        return ParticipantProfile(
            participant_id=participant_id,
            age=age,
            gender=gender,
            technical_proficiency=tech_proficiency,
            dietary_restrictions=dietary_restrictions,
            food_preferences=food_preferences,
            cultural_background=cultural_background,
            previous_ordering_experience=previous_ordering_experience,
            personality_traits=personality_traits,
            decision_style=decision_style,
            mood_sensitivity=mood_sensitivity,
            recommendation_trust=recommendation_trust,
            privacy_concerns=privacy_concerns
        )

    def calculate_realistic_completion_time(self, profile: ParticipantProfile,
                                          condition: str, trial_type: str) -> float:
        """Calculate realistic completion time based on participant characteristics"""

        # Base time - NO HARDCODED ADVANTAGE for either condition
        base_time = random.uniform(6.0, 9.0)  # Same range for both conditions

        # Trial type effect
        if trial_type == 'specific_order':
            base_time *= random.uniform(0.8, 1.1)  # Can be faster or slower depending on clarity

        # Technical proficiency effect
        if profile.technical_proficiency == 'high':
            base_time *= random.uniform(0.7, 0.9)
        elif profile.technical_proficiency == 'low':
            base_time *= random.uniform(1.1, 1.4)

        # Age effect (older participants may be slower)
        if profile.age > 50:
            base_time *= random.uniform(1.1, 1.3)

        # Fatigue effect
        base_time *= (1 + profile.session_fatigue * random.uniform(0.1, 0.3))

        # Add realistic variability
        base_time += random.uniform(-1.0, 1.5)

        return max(3.0, base_time)

    def calculate_realistic_satisfaction(self, profile: ParticipantProfile,
                                       condition: str, completion_time: float,
                                       recommendation_acceptance: float = None,
                                       dietary_issues: List[str] = None) -> float:
        """Calculate realistic satisfaction based on multiple factors"""

        # Base satisfaction - NO HARDCODED ADVANTAGE for either condition
        base_satisfaction = random.uniform(4.0, 6.5)  # Same range for both conditions

        # Technical proficiency effect
        if profile.technical_proficiency == 'high':
            base_satisfaction += random.uniform(-0.2, 0.3)
        elif profile.technical_proficiency == 'low':
            base_satisfaction += random.uniform(-0.3, 0.2)

        # Completion time effect
        if completion_time > 10.0:
            base_satisfaction -= random.uniform(0.2, 0.5)
        elif completion_time < 5.0:
            base_satisfaction += random.uniform(0.1, 0.3)

        # Recommendation acceptance effect (adaptive only)
        if recommendation_acceptance is not None:
            if recommendation_acceptance > 0.7:
                base_satisfaction += random.uniform(0.2, 0.5)
            elif recommendation_acceptance < 0.3:
                base_satisfaction -= random.uniform(0.2, 0.5)

        # Dietary issues significantly reduce satisfaction
        if dietary_issues:
            base_satisfaction -= len(dietary_issues) * random.uniform(0.5, 1.0)

        # Privacy concerns reduce satisfaction in adaptive condition
        if condition == 'adaptive' and profile.privacy_concerns > 0.7:
            base_satisfaction -= random.uniform(0.3, 0.7)

        # Personality effects
        if profile.personality_traits['neuroticism'] > 0.6:
            base_satisfaction -= random.uniform(0.1, 0.3)

        return max(1.0, min(7.0, base_satisfaction))

    def calculate_realistic_nasa_tlx(self, profile: ParticipantProfile,
                                   condition: str, completion_time: float) -> float:
        """Calculate realistic NASA-TLX workload score"""

        # Base workload - NO HARDCODED ADVANTAGE for either condition
        base_score = random.uniform(55.0, 85.0)  # Same range for both conditions

        # Technical proficiency effect
        if profile.technical_proficiency == 'low':
            base_score += random.uniform(5.0, 15.0)
        elif profile.technical_proficiency == 'high':
            base_score -= random.uniform(5.0, 15.0)

        # Age effect
        if profile.age > 50:
            base_score += random.uniform(5.0, 10.0)

        # Completion time effect
        if completion_time > 10.0:
            base_score += random.uniform(5.0, 15.0)

        # Fatigue effect
        base_score += profile.session_fatigue * random.uniform(10.0, 25.0)

        # Privacy concerns increase workload in adaptive condition
        if condition == 'adaptive' and profile.privacy_concerns > 0.7:
            base_score += random.uniform(5.0, 15.0)

        return max(0.0, min(100.0, base_score))

    def generate_realistic_recommendations(self, profile: ParticipantProfile,
                                         mood: str, weather: str) -> Dict:
        """Generate realistic AI recommendations that may have issues"""

        recommendations = {
            'proteins': [],
            'sauces': [],
            'base_types': [],
            'veggies': []
        }

        # Protein recommendations with potential dietary issues
        available_proteins = self.proteins.copy()

        # Check for dietary restrictions and potentially make mistakes
        if 'vegetarian' in profile.dietary_restrictions:
            # 70% chance of correct vegetarian recommendation
            if random.random() < 0.7:
                available_proteins = [p for p in available_proteins if 'vegetarian' in p['dietary']]
            else:
                # 30% chance of incorrect recommendation
                available_proteins = [p for p in available_proteins if p['name'] in ['Chicken', 'Pepperoni']]

        if 'vegan' in profile.dietary_restrictions:
            # 60% chance of correct vegan recommendation
            if random.random() < 0.6:
                available_proteins = [p for p in available_proteins if 'vegan' in p['dietary']]
            else:
                # 40% chance of incorrect recommendation
                available_proteins = [p for p in available_proteins if p['name'] in ['Paneer', 'Egg']]

        if 'halal' in profile.dietary_restrictions:
            # 75% chance of correct halal recommendation
            if random.random() < 0.75:
                available_proteins = [p for p in available_proteins if 'halal' in p['dietary']]
            else:
                # 25% chance of incorrect recommendation
                available_proteins = [p for p in available_proteins if p['name'] == 'Pepperoni']

        # Allergy checking (critical safety issue)
        for allergy in profile.dietary_restrictions:
            if allergy in ['nuts', 'dairy', 'gluten', 'shellfish']:
                # 80% chance of correct allergy avoidance
                if random.random() < 0.8:
                    # Remove problematic items (simplified)
                    pass
                else:
                    # 20% chance of dangerous recommendation
                    if allergy == 'nuts' and random.random() < 0.1:
                        available_proteins.append({'name': 'Peanut Curry', 'price': 12.99, 'category': 'allergen_risk', 'dietary': ['non-vegetarian']})

        if available_proteins:
            recommendations['proteins'] = [random.choice(available_proteins)['name']]

        # Sauce recommendations
        recommendations['sauces'] = [random.choice(self.sauces)['name']]

        # Base type recommendations
        base_type = random.choice(list(self.base_types.keys()))
        base_option = random.choice(self.base_types[base_type])['name']
        recommendations['base_types'] = [f"{base_type} - {base_option}"]

        # Veggie recommendations
        recommendations['veggies'] = random.sample([v['name'] for v in self.veggies], random.randint(2, 4))

        return recommendations

    def check_dietary_compliance(self, profile: ParticipantProfile,
                               recommendations: Dict) -> List[str]:
        """Check for dietary compliance issues in recommendations"""
        issues = []

        # Check protein recommendations
        for protein_rec in recommendations.get('proteins', []):
            protein_data = next((p for p in self.proteins if p['name'] == protein_rec), None)
            if protein_data:
                # Check vegetarian restrictions
                if 'vegetarian' in profile.dietary_restrictions and 'vegetarian' not in protein_data['dietary']:
                    issues.append(f"Recommended non-vegetarian protein: {protein_rec}")

                # Check vegan restrictions
                if 'vegan' in profile.dietary_restrictions and 'vegan' not in protein_data['dietary']:
                    issues.append(f"Recommended non-vegan protein: {protein_rec}")

                # Check halal restrictions
                if 'halal' in profile.dietary_restrictions and 'halal' not in protein_data['dietary']:
                    issues.append(f"Recommended non-halal protein: {protein_rec}")

                # Check allergies
                for allergy in profile.dietary_restrictions:
                    if allergy in ['nuts', 'dairy', 'gluten', 'shellfish']:
                        if protein_rec == 'Peanut Curry' and allergy == 'nuts':
                            issues.append(f"CRITICAL: Recommended allergen-containing protein: {protein_rec}")

        return issues

class ArtificialParticipant:
    """Individual artificial participant with realistic behavior"""

    def __init__(self, participant_id: str):
        self.participant_id = participant_id
        self.behavioral_models = RealisticBehavioralModels()
        self.profile = self.behavioral_models.generate_realistic_participant(participant_id)
        self.current_mood = 'neutral'
        self.order_history = []
        self.session_fatigue = 0.0

        # Initialize menu data
        self.proteins = self.behavioral_models.proteins
        self.sauces = self.behavioral_models.sauces
        self.base_types = self.behavioral_models.base_types
        self.veggies = self.behavioral_models.veggies

    def update_mood(self, trial_number: int, condition: str):
        """Update mood realistically across trials"""
        mood_options = ['happy', 'neutral', 'focused', 'stressed', 'excited']

        # Mood changes based on trial progression and condition
        if trial_number == 1:
            self.current_mood = random.choice(['neutral', 'focused'])
        elif trial_number <= 3:
            if condition == 'adaptive':
                self.current_mood = random.choice(['happy', 'excited', 'focused'])
            else:
                self.current_mood = random.choice(['neutral', 'focused', 'stressed'])
        else:
            # Later trials - fatigue sets in
            if self.session_fatigue > 0.5:
                self.current_mood = random.choice(['stressed', 'neutral'])
            else:
                self.current_mood = random.choice(['focused', 'neutral', 'happy'])

    def select_protein(self, recommendations: List[str] = None) -> str:
        """Select protein with realistic decision-making"""
        available_proteins = [p['name'] for p in self.proteins]

        # Check dietary restrictions first
        if 'vegetarian' in self.profile.dietary_restrictions:
            available_proteins = [p for p in available_proteins if p in ['Paneer', 'Egg', 'Soya']]
        if 'vegan' in self.profile.dietary_restrictions:
            available_proteins = [p for p in available_proteins if p in ['Soya']]
        if 'halal' in self.profile.dietary_restrictions:
            available_proteins = [p for p in available_proteins if p in ['Chicken', 'Paneer', 'Egg', 'Soya']]

        # Consider recommendations if provided
        if recommendations and random.random() < self.profile.recommendation_trust:
            rec_proteins = [r for r in recommendations if r in available_proteins]
            if rec_proteins:
                return random.choice(rec_proteins)

        # Personal preference-based selection
        if 'comfort' in self.profile.food_preferences:
            return random.choice(['Chicken', 'Paneer'])
        elif 'healthy' in self.profile.food_preferences:
            return random.choice(['Soya', 'Egg'])
        else:
            return random.choice(available_proteins)

    def select_sauce(self, recommendations: List[str] = None) -> str:
        """Select sauce with realistic preferences"""
        available_sauces = [s['name'] for s in self.sauces]

        if recommendations and random.random() < self.profile.recommendation_trust:
            rec_sauces = [r for r in recommendations if r in available_sauces]
            if rec_sauces:
                return random.choice(rec_sauces)

        # Preference-based selection
        if 'spicy' in self.profile.food_preferences:
            return 'Curry Masala'
        elif 'mild' in self.profile.food_preferences:
            return 'Malai Masala'
        else:
            return random.choice(available_sauces)

    def select_base_type(self, recommendations: List[str] = None) -> Tuple[str, str]:
        """Select base type and option"""
        available_bases = list(self.base_types.keys())

        if recommendations:
            # Parse recommendation format "BaseType - Option"
            for rec in recommendations:
                if ' - ' in rec:
                    base_type, option = rec.split(' - ', 1)
                    if base_type in available_bases:
                        return base_type, option

        # Default selection
        base_type = random.choice(available_bases)
        base_option = random.choice(self.base_types[base_type])['name']
        return base_type, base_option

    def select_veggies(self, recommendations: List[str] = None) -> List[str]:
        """Select vegetables with realistic patterns"""
        available_veggies = [v['name'] for v in self.veggies]

        if recommendations and random.random() < self.profile.recommendation_trust:
            rec_veggies = [r for r in recommendations if r in available_veggies]
            if rec_veggies:
                return rec_veggies

        # Realistic veggie selection (2-4 items)
        num_veggies = random.randint(2, 4)
        return random.sample(available_veggies, num_veggies)

    async def perform_trial(self, trial_number: int, condition: str,
                          trial_type: str, recommendations: Dict = None) -> TrialResult:
        """Perform a complete trial with realistic behavior"""
        start_time = datetime.now()

        # Update mood
        self.update_mood(trial_number, condition)

        # Generate recommendations for adaptive condition
        if condition == 'adaptive' and not recommendations:
            weather = random.choice(['cold', 'warm', 'hot'])
            recommendations = self.behavioral_models.generate_realistic_recommendations(
                self.profile, self.current_mood, weather
            )

        # Check for dietary compliance issues
        dietary_issues = []
        if condition == 'adaptive' and recommendations:
            dietary_issues = self.behavioral_models.check_dietary_compliance(
                self.profile, recommendations
            )

        # Simulate order selection process
        protein = self.select_protein(recommendations.get('proteins', []) if recommendations else None)
        sauce = self.select_sauce(recommendations.get('sauces', []) if recommendations else None)
        base_type, base_option = self.select_base_type(recommendations.get('base_types', []) if recommendations else None)
        veggies = self.select_veggies(recommendations.get('veggies', []) if recommendations else None)

        # Calculate realistic completion time
        completion_time = self.behavioral_models.calculate_realistic_completion_time(
            self.profile, condition, trial_type
        )

        # Simulate processing time
        await asyncio.sleep(completion_time / 10)  # Scale down for simulation

        end_time = datetime.now()

        # Calculate recommendation acceptance (adaptive condition only)
        recommendation_acceptance = None
        if condition == 'adaptive' and recommendations:
            # Base acceptance on trust and dietary issues
            base_acceptance = self.profile.recommendation_trust

            # Reduce acceptance if there are dietary issues
            if dietary_issues:
                base_acceptance *= 0.3

            # Add realistic variability
            recommendation_acceptance = max(0.0, min(1.0,
                base_acceptance + random.uniform(-0.2, 0.2)))

        # Calculate realistic metrics
        satisfaction = self.behavioral_models.calculate_realistic_satisfaction(
            self.profile, condition, completion_time, recommendation_acceptance, dietary_issues
        )

        nasa_tlx = self.behavioral_models.calculate_realistic_nasa_tlx(
            self.profile, condition, completion_time
        )

        # Realistic error and navigation patterns - NO CONDITION BIAS
        error_count = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
        navigation_steps = random.randint(7, 12)

        # Decision changes based on personality and condition
        if self.profile.decision_style == 'cautious':
            decision_changes = random.randint(1, 3)
        elif self.profile.decision_style == 'impulsive':
            decision_changes = random.randint(0, 1)
        else:
            decision_changes = random.randint(0, 2)

        # Calculate total price
        total_price = 0
        for p in self.proteins:
            if p['name'] == protein:
                total_price += p['price']
                break

        for b in self.base_types[base_type]:
            if b['name'] == base_option:
                total_price += b['price']
                break

        # Add veggie costs
        for veggie in veggies:
            for v in self.veggies:
                if v['name'] == veggie:
                    total_price += v['price']
                    break

        # Create order data
        order_data = {
            'protein': protein,
            'sauce': sauce,
            'base_type': base_type,
            'base_option': base_option,
            'veggies': veggies,
            'dish_name': f"{protein} {base_type}",
            'total_price': total_price
        }

        # Facial emotion data (adaptive condition only)
        facial_emotion_data = None
        if condition == 'adaptive':
            # Realistic emotion detection accuracy (not perfect)
            detected_emotion = self.current_mood
            if random.random() < 0.2:  # 20% chance of detection error
                detected_emotion = random.choice(['happy', 'neutral', 'focused', 'stressed', 'excited'])

            facial_emotion_data = {
                'primary_emotion': detected_emotion,
                'confidence': random.uniform(0.6, 0.9),
                'emotion_timeline': [
                    {'emotion': detected_emotion, 'timestamp': start_time.isoformat()},
                    {'emotion': detected_emotion, 'timestamp': end_time.isoformat()}
                ]
            }

        # Contextual data
        contextual_data = {
            'activity_level': random.choice(['workout', 'rest', 'study', 'work']),
            'health_goals': random.choice(['low_calorie', 'high_protein', 'balanced']),
            'weather_condition': random.choice(['cold', 'warm', 'hot']),
            'time_of_day': datetime.now().hour
        }

        # Mood progression
        mood_progression = [
            {'mood': self.current_mood, 'timestamp': start_time.isoformat()},
            {'mood': self.current_mood, 'timestamp': end_time.isoformat()}
        ]

        # Update session fatigue
        self.session_fatigue += 0.1

        # Store order in history
        self.order_history.append(order_data)

        return TrialResult(
            participant_id=self.profile.participant_id,
            trial_number=trial_number,
            condition=condition,
            trial_type=trial_type,
            start_time=start_time,
            end_time=end_time,
            completion_time_seconds=completion_time,
            satisfaction_rating=satisfaction,
            nasa_tlx_score=nasa_tlx,
            trust_rating=random.uniform(3.5, 6.0),
            error_count=error_count,
            navigation_steps=navigation_steps,
            recommendation_acceptance=recommendation_acceptance,
            order_data=order_data,
            facial_emotion_data=facial_emotion_data,
            contextual_data=contextual_data,
            mood_progression=mood_progression,
            decision_changes=decision_changes,
            total_price=total_price,
            privacy_concern_level=self.profile.privacy_concerns * 7.0,
            system_complexity_rating=random.uniform(2.5, 5.0),  # NO CONDITION BIAS
            dietary_compliance_issues=dietary_issues,
            cultural_preference_mismatches=[]  # Simplified for now
        )

class ArtificialParticipantSystem:
    """Main system for managing artificial participants and experiments"""

    def __init__(self):
        self.participants = {}
        self.results = []
        self.experiment_config = {
            'total_participants': 50,
            'trials_per_condition': 5,
            'conditions': ['baseline', 'adaptive'],
            'trial_types': ['free_choice', 'free_choice', 'free_choice', 'specific_order', 'specific_order']
        }

        # Create output directory
        self.output_dir = Path("removed/human_experiments_data/results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_participant_profiles(self) -> List[ParticipantProfile]:
        """Generate 50 realistic participant profiles"""
        profiles = []
        for i in range(self.experiment_config['total_participants']):
            participant_id = f"P{(i+1):03d}"
            profile = RealisticBehavioralModels().generate_realistic_participant(participant_id)
            profiles.append(profile)
        return profiles

    async def run_experiment(self) -> List[TrialResult]:
        """Run the complete experiment with realistic participant behavior"""
        logger.info("Starting artificial participant experiment...")

        # Generate participant profiles
        profiles = self.generate_participant_profiles()
        logger.info(f"Generated {len(profiles)} participant profiles")

        all_results = []

        # Run experiment for each participant
        for i, profile in enumerate(profiles):
            logger.info(f"Running experiment for participant {profile.participant_id} ({i+1}/{len(profiles)})")

            participant = ArtificialParticipant(profile.participant_id)
            participant.profile = profile

            # Run trials for each condition
            for condition in self.experiment_config['conditions']:
                for trial_num, trial_type in enumerate(self.experiment_config['trial_types'], 1):
                    result = await participant.perform_trial(
                        trial_number=trial_num,
                        condition=condition,
                        trial_type=trial_type
                    )
                    all_results.append(result)

        logger.info(f"Completed {len(all_results)} total trials")
        return all_results

    def save_results(self, results: List[TrialResult], timestamp: str):
        """Save results to files"""
        # Save raw data
        data_file = self.output_dir / f"experiment_data_{timestamp}.json"
        with open(data_file, 'w') as f:
            json.dump([asdict(result) for result in results], f, indent=2, default=str)

        logger.info(f"Results saved to {data_file}")

async def main():
    """Main function to run the artificial participant experiment"""
    system = ArtificialParticipantSystem()

    # Run experiment
    results = await system.run_experiment()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    system.save_results(results, timestamp)

    logger.info("Experiment completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())