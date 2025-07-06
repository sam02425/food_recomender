"""
Adaptive Artificial Participant System with GROQ LLM Integration
Simulates realistic human participants that learn and adapt during food ordering experiments
"""

import asyncio
import json
import random
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import aiohttp
import numpy as np
from scipy import stats
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ParticipantProfile:
    """Realistic participant profile with personality and preferences"""
    participant_id: str
    age: int
    gender: str
    dietary_restrictions: List[str]
    allergens: List[str]
    cultural_background: str
    tech_savviness: float  # 0-1 scale
    food_adventurousness: float  # 0-1 scale
    health_consciousness: float  # 0-1 scale
    price_sensitivity: float  # 0-1 scale
    time_pressure: float  # 0-1 scale
    mood: float  # -1 to 1 scale
    fatigue: float  # 0-1 scale
    learning_rate: float  # 0-1 scale
    trust_in_recommendations: float  # 0-1 scale
    previous_experience: Dict[str, Any]

@dataclass
class TrialData:
    """Data collected from a single trial"""
    trial_id: str
    participant_id: str
    trial_type: str  # 'baseline' or 'adaptive'
    start_time: datetime
    end_time: datetime
    task_completion_time: float
    satisfaction_score: float
    nasa_tlx_scores: Dict[str, float]
    sus_scores: Dict[str, float]
    recommendation_acceptance_rate: float
    dietary_compliance: bool
    privacy_concerns: List[str]
    cultural_mismatches: List[str]
    learning_insights: List[str]
    system_failures: List[str]
    final_order: Dict[str, Any]
    llm_feedback: Optional[str] = None

class OpenAIClient:
    """Client for OpenAI ChatGPT API"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_participant_feedback(self, participant: ParticipantProfile, trial_data: TrialData,
                                     system_performance: Dict[str, Any]) -> str:
        """Get realistic participant feedback using OpenAI ChatGPT"""

        prompt = f"""
You are a realistic human participant in a food ordering experiment. Based on the following information, provide authentic, human-like feedback about your experience.

Participant Profile:
- Age: {participant.age}
- Cultural background: {participant.cultural_background}
- Dietary restrictions: {participant.dietary_restrictions}
- Tech savviness: {participant.tech_savviness:.2f}
- Food adventurousness: {participant.food_adventurousness:.2f}
- Health consciousness: {participant.health_consciousness:.2f}
- Current mood: {participant.mood:.2f}
- Fatigue level: {participant.fatigue:.2f}

Trial Experience:
- Trial type: {trial_data.trial_type}
- Task completion time: {trial_data.task_completion_time:.1f} seconds
- Satisfaction: {trial_data.satisfaction_score:.1f}/5
- Recommendation acceptance: {trial_data.recommendation_acceptance_rate:.1%}
- Dietary compliance: {trial_data.dietary_compliance}
- Privacy concerns: {trial_data.privacy_concerns}
- Cultural mismatches: {trial_data.cultural_mismatches}
- System failures: {trial_data.system_failures}

System Performance:
- Recommendations provided: {system_performance.get('recommendations_count', 0)}
- Dietary filtering accuracy: {system_performance.get('dietary_accuracy', 0):.1%}
- Response time: {system_performance.get('response_time', 0):.1f}s

Provide 2-3 sentences of realistic, varied feedback that reflects this participant's personality and experience. Be authentic - include frustrations, confusion, positive surprises, or indifference as appropriate. Don't be overly formal or perfect.
"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 150
            }

            async with self.session.post(self.base_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    logger.warning(f"OpenAI API error: {response.status}")
                    return self._generate_fallback_feedback(participant, trial_data)

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return self._generate_fallback_feedback(participant, trial_data)

    def _generate_fallback_feedback(self, participant: ParticipantProfile, trial_data: TrialData) -> str:
        """Generate fallback feedback when OpenAI is unavailable"""
        feedback_templates = [
            "The system was okay, but I'm not sure about the recommendations.",
            "It took longer than expected to find what I wanted.",
            "The dietary restrictions worked well for me.",
            "I wish there were more options that fit my preferences.",
            "The interface was confusing at first but I got used to it.",
            "Some recommendations didn't make sense for my diet.",
            "I appreciate the health-focused suggestions.",
            "The system seemed to understand my preferences better over time."
        ]
        return random.choice(feedback_templates)

class GROQClient:
    """Client for GROQ LLM API (legacy support)"""

    def __init__(self, api_key: str, model: str = "llama3-8b-8192"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_participant_feedback(self, participant: ParticipantProfile, trial_data: TrialData,
                                     system_performance: Dict[str, Any]) -> str:
        """Get realistic participant feedback using GROQ (legacy)"""

        prompt = f"""
You are a realistic human participant in a food ordering experiment. Based on the following information, provide authentic, human-like feedback about your experience.

Participant Profile:
- Age: {participant.age}
- Cultural background: {participant.cultural_background}
- Dietary restrictions: {participant.dietary_restrictions}
- Tech savviness: {participant.tech_savviness:.2f}
- Food adventurousness: {participant.food_adventurousness:.2f}
- Health consciousness: {participant.health_consciousness:.2f}
- Current mood: {participant.mood:.2f}
- Fatigue level: {participant.fatigue:.2f}

Trial Experience:
- Trial type: {trial_data.trial_type}
- Task completion time: {trial_data.task_completion_time:.1f} seconds
- Satisfaction: {trial_data.satisfaction_score:.1f}/5
- Recommendation acceptance: {trial_data.recommendation_acceptance_rate:.1%}
- Dietary compliance: {trial_data.dietary_compliance}
- Privacy concerns: {trial_data.privacy_concerns}
- Cultural mismatches: {trial_data.cultural_mismatches}
- System failures: {trial_data.system_failures}

System Performance:
- Recommendations provided: {system_performance.get('recommendations_count', 0)}
- Dietary filtering accuracy: {system_performance.get('dietary_accuracy', 0):.1%}
- Response time: {system_performance.get('response_time', 0):.1f}s

Provide 2-3 sentences of realistic, varied feedback that reflects this participant's personality and experience. Be authentic - include frustrations, confusion, positive surprises, or indifference as appropriate. Don't be overly formal or perfect.
"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 150
            }

            async with self.session.post(self.base_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    logger.warning(f"GROQ API error: {response.status}")
                    return self._generate_fallback_feedback(participant, trial_data)

        except Exception as e:
            logger.error(f"Error calling GROQ API: {e}")
            return self._generate_fallback_feedback(participant, trial_data)

    def _generate_fallback_feedback(self, participant: ParticipantProfile, trial_data: TrialData) -> str:
        """Generate fallback feedback when GROQ is unavailable"""
        feedback_templates = [
            "The system was okay, but I'm not sure about the recommendations.",
            "It took longer than expected to find what I wanted.",
            "The dietary restrictions worked well for me.",
            "I wish there were more options that fit my preferences.",
            "The interface was confusing at first but I got used to it.",
            "Some recommendations didn't make sense for my diet.",
            "I appreciate the health-focused suggestions.",
            "The system seemed to understand my preferences better over time."
        ]
        return random.choice(feedback_templates)

class AdaptiveParticipantSystem:
    """Main system for running adaptive artificial participants"""

    def __init__(self, openai_api_key: str = None, groq_api_key: str = None,
                 num_participants: int = 50, trials_per_participant: int = 10):
        self.openai_api_key = openai_api_key
        self.groq_api_key = groq_api_key
        self.num_participants = num_participants
        self.trials_per_participant = trials_per_participant
        self.participants: List[ParticipantProfile] = []
        self.trial_data: List[TrialData] = []
        self.system_performance_history: List[Dict[str, Any]] = []

        # Determine which API to use
        if openai_api_key and openai_api_key != 'YOUR_OPENAI_API_KEY_HERE':
            self.primary_api = 'openai'
            self.primary_api_key = openai_api_key
        elif groq_api_key and groq_api_key != 'YOUR_GROQ_API_KEY_HERE':
            self.primary_api = 'groq'
            self.primary_api_key = groq_api_key
        else:
            self.primary_api = 'fallback'
            self.primary_api_key = None

        # Menu data matching the actual app
        self.menu_data = {
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
            }
        }

    def generate_realistic_participants(self) -> List[ParticipantProfile]:
        """Generate diverse, realistic participant profiles"""
        participants = []

        # Cultural backgrounds with realistic distributions
        cultural_backgrounds = {
            'South Asian': 0.35,  # Higher due to curry focus
            'Western': 0.25,
            'Middle Eastern': 0.15,
            'East Asian': 0.15,
            'Other': 0.10
        }

        # Dietary restrictions with realistic patterns
        dietary_patterns = {
            'vegetarian': 0.25,
            'vegan': 0.08,
            'halal': 0.12,
            'no_pork': 0.15,
            'no_beef': 0.10,
            'none': 0.30
        }

        for i in range(self.num_participants):
            participant_id = f"P{i+1:03d}"

            # Age distribution (18-65)
            age = int(np.random.normal(32, 12))
            age = max(18, min(65, age))

            # Gender
            gender = random.choice(['Male', 'Female', 'Non-binary'])

            # Cultural background
            cultural_bg = random.choices(
                list(cultural_backgrounds.keys()),
                weights=list(cultural_backgrounds.values())
            )[0]

            # Dietary restrictions based on cultural background
            dietary_restrictions = []
            if cultural_bg == 'South Asian':
                dietary_restrictions = random.choices(
                    ['vegetarian', 'none', 'no_beef'],
                    weights=[0.4, 0.4, 0.2]
                )
            elif cultural_bg == 'Middle Eastern':
                dietary_restrictions = random.choices(
                    ['halal', 'none', 'no_pork'],
                    weights=[0.6, 0.3, 0.1]
                )
            else:
                dietary_restrictions = random.choices(
                    list(dietary_patterns.keys()),
                    weights=list(dietary_patterns.values())
                )

            # Remove 'none' from restrictions list
            if 'none' in dietary_restrictions:
                dietary_restrictions = []

            # Allergens (realistic prevalence)
            allergens = []
            allergen_prevalence = {
                'dairy': 0.08, 'nuts': 0.06, 'gluten': 0.05,
                'eggs': 0.04, 'soy': 0.03, 'peanuts': 0.02
            }
            for allergen, prevalence in allergen_prevalence.items():
                if random.random() < prevalence:
                    allergens.append(allergen)

            # Personality traits (realistic distributions)
            tech_savviness = np.random.beta(2, 2)  # Bell curve around 0.5
            food_adventurousness = np.random.beta(1.5, 2)  # Slightly conservative
            health_consciousness = np.random.beta(2, 1.5)  # Slightly health-focused
            price_sensitivity = np.random.beta(2, 2)
            time_pressure = np.random.beta(1.5, 2)
            mood = np.random.normal(0, 0.3)  # Slight negative bias
            mood = max(-1, min(1, mood))
            fatigue = np.random.beta(1, 2)  # Most people aren't very fatigued
            learning_rate = np.random.beta(2, 1.5)  # Most people learn moderately
            trust_in_recommendations = np.random.beta(1.5, 2)  # Slightly skeptical

            participant = ParticipantProfile(
                participant_id=participant_id,
                age=age,
                gender=gender,
                dietary_restrictions=dietary_restrictions,
                allergens=allergens,
                cultural_background=cultural_bg,
                tech_savviness=tech_savviness,
                food_adventurousness=food_adventurousness,
                health_consciousness=health_consciousness,
                price_sensitivity=price_sensitivity,
                time_pressure=time_pressure,
                mood=mood,
                fatigue=fatigue,
                learning_rate=learning_rate,
                trust_in_recommendations=trust_in_recommendations,
                previous_experience={}
            )

            participants.append(participant)

        return participants

    def simulate_trial(self, participant: ParticipantProfile, trial_type: str,
                      trial_number: int) -> Tuple[TrialData, Dict[str, Any]]:
        """Simulate a single trial with realistic behavior"""

        trial_id = f"{participant.participant_id}_{trial_type}_{trial_number}"
        start_time = datetime.now()

        # Simulate system performance (with realistic failures)
        system_performance = self._simulate_system_performance(participant, trial_type, trial_number)

        # Simulate participant behavior
        behavior = self._simulate_participant_behavior(participant, trial_type, trial_number, system_performance)

        # Calculate task completion time (with learning effects)
        base_time = 120  # Base time in seconds
        learning_bonus = participant.learning_rate * trial_number * 5
        mood_effect = (participant.mood + 1) * 10  # Better mood = faster
        fatigue_penalty = participant.fatigue * 20
        tech_bonus = participant.tech_savviness * 15

        task_completion_time = base_time - learning_bonus + mood_effect + fatigue_penalty - tech_bonus
        task_completion_time = max(30, min(300, task_completion_time))  # Bounds

        # Simulate satisfaction (realistic variance)
        base_satisfaction = 3.0
        system_quality = system_performance.get('overall_quality', 0.5)
        dietary_success = 1.0 if behavior['dietary_compliance'] else 0.5
        recommendation_success = behavior['recommendation_acceptance_rate']

        satisfaction = base_satisfaction + (system_quality - 0.5) + (dietary_success - 0.75) + (recommendation_success - 0.5)
        satisfaction = max(1.0, min(5.0, satisfaction + np.random.normal(0, 0.3)))

        # Simulate NASA TLX scores
        nasa_tlx = {
            'mental_demand': np.random.normal(3, 1.5),
            'physical_demand': np.random.normal(2, 1),
            'temporal_demand': np.random.normal(3, 1.5),
            'performance': np.random.normal(3, 1.5),
            'effort': np.random.normal(3, 1.5),
            'frustration': np.random.normal(3, 1.5)
        }

        # Adjust based on actual experience
        if task_completion_time > 180:
            nasa_tlx['temporal_demand'] += 1
            nasa_tlx['frustration'] += 0.5

        if not behavior['dietary_compliance']:
            nasa_tlx['frustration'] += 1
            nasa_tlx['mental_demand'] += 0.5

        # Clamp values
        for key in nasa_tlx:
            nasa_tlx[key] = max(1, min(7, nasa_tlx[key]))

        # Simulate SUS scores
        sus_base = 70 if system_performance.get('overall_quality', 0.5) > 0.6 else 50
        sus_scores = {
            'usefulness': sus_base + np.random.normal(0, 10),
            'ease_of_use': sus_base + np.random.normal(0, 10),
            'learnability': sus_base + np.random.normal(0, 10),
            'satisfaction': sus_base + np.random.normal(0, 10)
        }

        # Clamp SUS scores
        for key in sus_scores:
            sus_scores[key] = max(0, min(100, sus_scores[key]))

        end_time = start_time + timedelta(seconds=task_completion_time)

        trial_data = TrialData(
            trial_id=trial_id,
            participant_id=participant.participant_id,
            trial_type=trial_type,
            start_time=start_time,
            end_time=end_time,
            task_completion_time=task_completion_time,
            satisfaction_score=satisfaction,
            nasa_tlx_scores=nasa_tlx,
            sus_scores=sus_scores,
            recommendation_acceptance_rate=behavior['recommendation_acceptance_rate'],
            dietary_compliance=behavior['dietary_compliance'],
            privacy_concerns=behavior['privacy_concerns'],
            cultural_mismatches=behavior['cultural_mismatches'],
            learning_insights=behavior['learning_insights'],
            system_failures=behavior['system_failures'],
            final_order=behavior['final_order']
        )

        return trial_data, system_performance

    def _simulate_system_performance(self, participant: ParticipantProfile,
                                   trial_type: str, trial_number: int) -> Dict[str, Any]:
        """Simulate realistic system performance with failures"""

        # Base performance varies by trial type
        if trial_type == 'baseline':
            base_quality = 0.6  # Baseline system is decent but not great
        else:
            base_quality = 0.7 + (trial_number * 0.02)  # Adaptive system improves slightly

        # Dietary filtering accuracy (realistic failures)
        dietary_accuracy = 0.85  # 15% failure rate is realistic
        if participant.dietary_restrictions:
            # More restrictions = more likely to fail
            failure_rate = 0.1 + (len(participant.dietary_restrictions) * 0.05)
            if random.random() < failure_rate:
                dietary_accuracy = 0.6  # Significant failure

        # Recommendation quality
        recommendation_quality = base_quality
        if participant.cultural_background == 'South Asian':
            recommendation_quality += 0.1  # System better for target demographic
        elif participant.cultural_background == 'Middle Eastern':
            recommendation_quality -= 0.05  # Slightly worse for halal users

        # Response time
        response_time = np.random.normal(2.0, 0.5)  # 2 seconds average
        if trial_type == 'adaptive':
            response_time += 0.5  # Adaptive system is slower

        # System failures
        failures = []
        if random.random() < 0.1:  # 10% chance of recommendation failure
            failures.append("Recommendation system unavailable")
        if random.random() < 0.05:  # 5% chance of dietary filter failure
            failures.append("Dietary filtering error")
        if random.random() < 0.03:  # 3% chance of slow response
            failures.append("System slow response")

        return {
            'overall_quality': base_quality,
            'dietary_accuracy': dietary_accuracy,
            'recommendation_quality': recommendation_quality,
            'response_time': response_time,
            'recommendations_count': random.randint(3, 8),
            'failures': failures
        }

    def _simulate_participant_behavior(self, participant: ParticipantProfile,
                                     trial_type: str, trial_number: int,
                                     system_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate realistic participant behavior and decisions"""

        # Recommendation acceptance (based on trust and system quality)
        base_acceptance = participant.trust_in_recommendations
        system_quality = system_performance.get('recommendation_quality', 0.5)
        learning_effect = participant.learning_rate * trial_number * 0.02

        acceptance_rate = base_acceptance * system_quality + learning_effect
        acceptance_rate = max(0.1, min(0.9, acceptance_rate + np.random.normal(0, 0.1)))

        # Dietary compliance (realistic failures)
        dietary_compliance = True
        if participant.dietary_restrictions:
            compliance_rate = system_performance.get('dietary_accuracy', 0.85)
            if random.random() > compliance_rate:
                dietary_compliance = False

        # Privacy concerns (realistic patterns)
        privacy_concerns = []
        if participant.tech_savviness < 0.3:
            privacy_concerns.append("Data collection concerns")
        if trial_type == 'adaptive' and random.random() < 0.2:
            privacy_concerns.append("Personalization feels invasive")

        # Cultural mismatches
        cultural_mismatches = []
        if participant.cultural_background == 'Middle Eastern' and 'halal' in participant.dietary_restrictions:
            if random.random() < 0.15:  # 15% chance of halal mismatch
                cultural_mismatches.append("Halal certification unclear")
        if participant.cultural_background == 'South Asian':
            if random.random() < 0.1:  # 10% chance of spice level mismatch
                cultural_mismatches.append("Spice levels not appropriate")

        # Learning insights
        learning_insights = []
        if trial_number > 1:
            if participant.learning_rate > 0.6:
                learning_insights.append("Learned to trust recommendations more")
            if participant.tech_savviness > 0.7:
                learning_insights.append("Found interface shortcuts")

        # System failures experienced
        system_failures = system_performance.get('failures', [])

        # Final order simulation
        final_order = self._simulate_final_order(participant, dietary_compliance)

        return {
            'recommendation_acceptance_rate': acceptance_rate,
            'dietary_compliance': dietary_compliance,
            'privacy_concerns': privacy_concerns,
            'cultural_mismatches': cultural_mismatches,
            'learning_insights': learning_insights,
            'system_failures': system_failures,
            'final_order': final_order
        }

    def _simulate_final_order(self, participant: ParticipantProfile, dietary_compliance: bool) -> Dict[str, Any]:
        """Simulate realistic final order based on participant preferences"""

        # Protein selection
        available_proteins = [p for p in self.menu_data['proteins']
                            if dietary_compliance or not participant.dietary_restrictions]

        if not available_proteins:
            available_proteins = [p for p in self.menu_data['proteins']
                                if p['name'] in ['Soya', 'Potato']]  # Fallback to vegetarian

        selected_protein = random.choice(available_proteins)

        # Sauce selection
        selected_sauce = random.choice(self.menu_data['sauces'])

        # Base selection
        base_type = random.choice(list(self.menu_data['base_types'].keys()))
        base_option = random.choice(self.menu_data['base_types'][base_type])

        return {
            'protein': selected_protein['name'],
            'sauce': selected_sauce,
            'base_type': base_type,
            'base_option': base_option,
            'total_price': selected_protein['price'] + 2.0  # Base price
        }

    async def run_experiment(self) -> Dict[str, Any]:
        """Run the complete experiment with all participants"""

        logger.info(f"Starting experiment with {self.num_participants} participants")

        # Generate participants
        self.participants = self.generate_realistic_participants()
        logger.info(f"Generated {len(self.participants)} participant profiles")

        # Run trials
        if self.primary_api == 'openai':
            async with OpenAIClient(self.primary_api_key) as openai_client:
                for participant in self.participants:
                    logger.info(f"Running trials for participant {participant.participant_id}")

                    # Run baseline trials (first 5)
                    for trial_num in range(1, 6):
                        trial_data, system_perf = self.simulate_trial(
                            participant, 'baseline', trial_num
                        )

                        # Get LLM feedback for every 3rd trial to save API usage
                        if trial_num % 3 == 0:
                            trial_data.llm_feedback = await openai_client.get_participant_feedback(
                                participant, trial_data, system_perf
                            )

                        self.trial_data.append(trial_data)
                        self.system_performance_history.append(system_perf)

                        # Update participant based on experience
                        self._update_participant_from_trial(participant, trial_data)

                    # Run adaptive trials (last 5)
                    for trial_num in range(1, 6):
                        trial_data, system_perf = self.simulate_trial(
                            participant, 'adaptive', trial_num
                        )

                        # Get LLM feedback for every 3rd trial
                        if trial_num % 3 == 0:
                            trial_data.llm_feedback = await openai_client.get_participant_feedback(
                                participant, trial_data, system_perf
                            )

                        self.trial_data.append(trial_data)
                        self.system_performance_history.append(system_perf)

                        # Update participant based on experience
                        self._update_participant_from_trial(participant, trial_data)

        elif self.primary_api == 'groq':
            async with GROQClient(self.primary_api_key) as groq_client:
                for participant in self.participants:
                    logger.info(f"Running trials for participant {participant.participant_id}")

                    # Run baseline trials (first 5)
                    for trial_num in range(1, 6):
                        trial_data, system_perf = self.simulate_trial(
                            participant, 'baseline', trial_num
                        )

                        # Get LLM feedback for every 3rd trial to save API usage
                        if trial_num % 3 == 0:
                            trial_data.llm_feedback = await groq_client.get_participant_feedback(
                                participant, trial_data, system_perf
                            )

                        self.trial_data.append(trial_data)
                        self.system_performance_history.append(system_perf)

                        # Update participant based on experience
                        self._update_participant_from_trial(participant, trial_data)

                    # Run adaptive trials (last 5)
                    for trial_num in range(1, 6):
                        trial_data, system_perf = self.simulate_trial(
                            participant, 'adaptive', trial_num
                        )

                        # Get LLM feedback for every 3rd trial
                        if trial_num % 3 == 0:
                            trial_data.llm_feedback = await groq_client.get_participant_feedback(
                                participant, trial_data, system_perf
                            )

                        self.trial_data.append(trial_data)
                        self.system_performance_history.append(system_perf)

                        # Update participant based on experience
                        self._update_participant_from_trial(participant, trial_data)

        elif self.primary_api == 'fallback':
            logger.warning("No primary API key provided. LLM feedback will be unavailable.")
            for participant in self.participants:
                logger.info(f"Running trials for participant {participant.participant_id}")

                # Run baseline trials (first 5)
                for trial_num in range(1, 6):
                    trial_data, system_perf = self.simulate_trial(
                        participant, 'baseline', trial_num
                    )

                    self.trial_data.append(trial_data)
                    self.system_performance_history.append(system_perf)

                    # Update participant based on experience
                    self._update_participant_from_trial(participant, trial_data)

                # Run adaptive trials (last 5)
                for trial_num in range(1, 6):
                    trial_data, system_perf = self.simulate_trial(
                        participant, 'adaptive', trial_num
                    )

                    self.trial_data.append(trial_data)
                    self.system_performance_history.append(system_perf)

                    # Update participant based on experience
                    self._update_participant_from_trial(participant, trial_data)

        # Small delay to avoid overwhelming the API
        await asyncio.sleep(0.1)

        logger.info("Experiment completed")
        return self._generate_experiment_results()

    def _update_participant_from_trial(self, participant: ParticipantProfile, trial_data: TrialData):
        """Update participant based on trial experience (learning and adaptation)"""

        # Update trust based on recommendation success
        if trial_data.recommendation_acceptance_rate > 0.7:
            participant.trust_in_recommendations += 0.05
        elif trial_data.recommendation_acceptance_rate < 0.3:
            participant.trust_in_recommendations -= 0.05

        participant.trust_in_recommendations = max(0, min(1, participant.trust_in_recommendations))

        # Update mood based on satisfaction
        if trial_data.satisfaction_score > 4:
            participant.mood += 0.1
        elif trial_data.satisfaction_score < 2:
            participant.mood -= 0.1

        participant.mood = max(-1, min(1, participant.mood))

        # Update fatigue (increases over time)
        participant.fatigue += 0.02
        participant.fatigue = min(1, participant.fatigue)

        # Store experience
        if trial_data.trial_type not in participant.previous_experience:
            participant.previous_experience[trial_data.trial_type] = []

        participant.previous_experience[trial_data.trial_type].append({
            'satisfaction': trial_data.satisfaction_score,
            'completion_time': trial_data.task_completion_time,
            'dietary_compliance': trial_data.dietary_compliance
        })

    def _generate_experiment_results(self) -> Dict[str, Any]:
        """Generate comprehensive experiment results"""

        # Convert to DataFrame for analysis
        trial_dicts = []
        for trial in self.trial_data:
            trial_dict = asdict(trial)
            # Convert datetime objects to strings for JSON serialization
            trial_dict['start_time'] = trial_dict['start_time'].isoformat()
            trial_dict['end_time'] = trial_dict['end_time'].isoformat()
            trial_dicts.append(trial_dict)

        df = pd.DataFrame(trial_dicts)

        # Separate baseline and adaptive trials
        baseline_trials = df[df['trial_type'] == 'baseline']
        adaptive_trials = df[df['trial_type'] == 'adaptive']

        # Calculate key metrics
        results = {
            'experiment_summary': {
                'total_participants': self.num_participants,
                'total_trials': len(self.trial_data),
                'baseline_trials': len(baseline_trials),
                'adaptive_trials': len(adaptive_trials),
                'experiment_duration': 'Simulated'
            },
            'performance_metrics': {
                'baseline': {
                    'avg_completion_time': baseline_trials['task_completion_time'].mean(),
                    'avg_satisfaction': baseline_trials['satisfaction_score'].mean(),
                    'avg_recommendation_acceptance': baseline_trials['recommendation_acceptance_rate'].mean(),
                    'dietary_compliance_rate': baseline_trials['dietary_compliance'].mean(),
                    'avg_nasa_tlx': baseline_trials['nasa_tlx_scores'].apply(lambda x: np.mean(list(x.values()))).mean(),
                    'avg_sus': baseline_trials['sus_scores'].apply(lambda x: np.mean(list(x.values()))).mean()
                },
                'adaptive': {
                    'avg_completion_time': adaptive_trials['task_completion_time'].mean(),
                    'avg_satisfaction': adaptive_trials['satisfaction_score'].mean(),
                    'avg_recommendation_acceptance': adaptive_trials['recommendation_acceptance_rate'].mean(),
                    'dietary_compliance_rate': adaptive_trials['dietary_compliance'].mean(),
                    'avg_nasa_tlx': adaptive_trials['nasa_tlx_scores'].apply(lambda x: np.mean(list(x.values()))).mean(),
                    'avg_sus': adaptive_trials['sus_scores'].apply(lambda x: np.mean(list(x.values()))).mean()
                }
            },
            'statistical_analysis': self._perform_statistical_analysis(baseline_trials, adaptive_trials),
            'participant_diversity': self._analyze_participant_diversity(),
            'system_performance': self._analyze_system_performance(),
            'qualitative_insights': self._extract_qualitative_insights()
        }

        return results

    def _perform_statistical_analysis(self, baseline_trials: pd.DataFrame,
                                    adaptive_trials: pd.DataFrame) -> Dict[str, Any]:
        """Perform statistical analysis comparing baseline vs adaptive"""

        metrics = ['task_completion_time', 'satisfaction_score', 'recommendation_acceptance_rate']
        analysis = {}

        for metric in metrics:
            baseline_data = baseline_trials[metric].dropna()
            adaptive_data = adaptive_trials[metric].dropna()

            if len(baseline_data) > 0 and len(adaptive_data) > 0:
                # T-test
                t_stat, p_value = stats.ttest_ind(baseline_data, adaptive_data)

                # Effect size (Cohen's d)
                pooled_std = np.sqrt(((len(baseline_data) - 1) * baseline_data.var() +
                                    (len(adaptive_data) - 1) * adaptive_data.var()) /
                                   (len(baseline_data) + len(adaptive_data) - 2))
                cohens_d = (adaptive_data.mean() - baseline_data.mean()) / pooled_std

                analysis[metric] = {
                    'baseline_mean': baseline_data.mean(),
                    'adaptive_mean': adaptive_data.mean(),
                    'difference': adaptive_data.mean() - baseline_data.mean(),
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05,
                    'effect_size': cohens_d,
                    'effect_magnitude': self._interpret_effect_size(cohens_d)
                }

        return analysis

    def _interpret_effect_size(self, cohens_d: float) -> str:
        """Interpret Cohen's d effect size"""
        if abs(cohens_d) < 0.2:
            return 'negligible'
        elif abs(cohens_d) < 0.5:
            return 'small'
        elif abs(cohens_d) < 0.8:
            return 'medium'
        else:
            return 'large'

    def _analyze_participant_diversity(self) -> Dict[str, Any]:
        """Analyze participant diversity and subgroup performance"""

        # Create a mapping of participant IDs to their profiles
        participant_map = {p.participant_id: p for p in self.participants}

        # Create trial data with participant information
        trial_data_with_participants = []
        for trial in self.trial_data:
            participant = participant_map.get(trial.participant_id)
            if participant:
                trial_dict = asdict(trial)
                trial_dict['cultural_background'] = participant.cultural_background
                trial_dict['dietary_restrictions'] = participant.dietary_restrictions
                trial_data_with_participants.append(trial_dict)

        df = pd.DataFrame(trial_data_with_participants)

        if df.empty:
            return {'cultural_backgrounds': {}, 'dietary_restrictions': {}}

        # Cultural background analysis
        cultural_analysis = {}
        if 'cultural_background' in df.columns:
            for bg in df['cultural_background'].unique():
                if pd.notna(bg):  # Check for non-null values
                    bg_trials = df[df['cultural_background'] == bg]
                    cultural_analysis[bg] = {
                        'count': len(bg_trials),
                        'avg_satisfaction': bg_trials['satisfaction_score'].mean(),
                        'avg_completion_time': bg_trials['task_completion_time'].mean(),
                        'dietary_compliance_rate': bg_trials['dietary_compliance'].mean()
                    }

        # Dietary restrictions analysis
        dietary_analysis = {}
        if 'dietary_restrictions' in df.columns:
            for restriction in ['vegan', 'vegetarian', 'halal', 'none']:
                if restriction == 'none':
                    restriction_trials = df[df['dietary_restrictions'].apply(lambda x: len(x) == 0 if isinstance(x, list) else True)]
                else:
                    restriction_trials = df[df['dietary_restrictions'].apply(lambda x: restriction in x if isinstance(x, list) else False)]

                if len(restriction_trials) > 0:
                    dietary_analysis[restriction] = {
                        'count': len(restriction_trials),
                        'avg_satisfaction': restriction_trials['satisfaction_score'].mean(),
                        'dietary_compliance_rate': restriction_trials['dietary_compliance'].mean()
                    }

        return {
            'cultural_backgrounds': cultural_analysis,
            'dietary_restrictions': dietary_analysis
        }

    def _analyze_system_performance(self) -> Dict[str, Any]:
        """Analyze system performance across trials"""

        if not self.system_performance_history:
            return {}

        df = pd.DataFrame(self.system_performance_history)

        return {
            'avg_response_time': df['response_time'].mean(),
            'avg_recommendation_quality': df['recommendation_quality'].mean(),
            'avg_dietary_accuracy': df['dietary_accuracy'].mean(),
            'failure_rate': len(df[df['failures'].apply(lambda x: len(x) > 0)]) / len(df),
            'common_failures': self._get_common_failures()
        }

    def _get_common_failures(self) -> Dict[str, int]:
        """Get frequency of different system failures"""
        failure_counts = {}
        for perf in self.system_performance_history:
            for failure in perf.get('failures', []):
                failure_counts[failure] = failure_counts.get(failure, 0) + 1
        return failure_counts

    def _extract_qualitative_insights(self) -> Dict[str, Any]:
        """Extract qualitative insights from LLM feedback and participant behavior"""

        # Collect all LLM feedback
        feedbacks = [trial.llm_feedback for trial in self.trial_data if trial.llm_feedback]

        # Analyze privacy concerns
        privacy_concerns = []
        for trial in self.trial_data:
            privacy_concerns.extend(trial.privacy_concerns)

        # Analyze cultural mismatches
        cultural_mismatches = []
        for trial in self.trial_data:
            cultural_mismatches.extend(trial.cultural_mismatches)

        # Analyze learning insights
        learning_insights = []
        for trial in self.trial_data:
            learning_insights.extend(trial.learning_insights)

        return {
            'llm_feedback_count': len(feedbacks),
            'sample_feedback': feedbacks[:5] if feedbacks else [],
            'privacy_concerns': list(set(privacy_concerns)),
            'cultural_mismatches': list(set(cultural_mismatches)),
            'learning_insights': list(set(learning_insights)),
            'system_failures': self._get_common_failures()
        }

    def save_results(self, filename: str = None):
        """Save experiment results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"adaptive_experiment_results_{timestamp}.json"

        results = self._generate_experiment_results()

        # Add raw data
        results['raw_data'] = {
            'participants': [asdict(p) for p in self.participants],
            'trials': [asdict(t) for t in self.trial_data],
            'system_performance': self.system_performance_history
        }

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Results saved to {filename}")
        return filename

async def main():
    """Main function to run the experiment"""

    # You'll need to set your GROQ API key
    groq_api_key = "YOUR_GROQ_API_KEY_HERE"  # Replace with actual key

    # Create and run the experiment
    experiment = AdaptiveParticipantSystem(
        groq_api_key=groq_api_key,
        num_participants=50,
        trials_per_participant=10
    )

    try:
        results = await experiment.run_experiment()

        # Print key results
        print("\n=== EXPERIMENT RESULTS ===")
        print(f"Total participants: {results['experiment_summary']['total_participants']}")
        print(f"Total trials: {results['experiment_summary']['total_trials']}")

        print("\n=== PERFORMANCE COMPARISON ===")
        baseline = results['performance_metrics']['baseline']
        adaptive = results['performance_metrics']['adaptive']

        print(f"Task Completion Time:")
        print(f"  Baseline: {baseline['avg_completion_time']:.1f}s")
        print(f"  Adaptive: {adaptive['avg_completion_time']:.1f}s")
        print(f"  Difference: {adaptive['avg_completion_time'] - baseline['avg_completion_time']:.1f}s")

        print(f"\nSatisfaction Score:")
        print(f"  Baseline: {baseline['avg_satisfaction']:.2f}/5")
        print(f"  Adaptive: {adaptive['avg_satisfaction']:.2f}/5")
        print(f"  Difference: {adaptive['avg_satisfaction'] - baseline['avg_satisfaction']:.2f}")

        print(f"\nRecommendation Acceptance:")
        print(f"  Baseline: {baseline['avg_recommendation_acceptance']:.1%}")
        print(f"  Adaptive: {adaptive['avg_recommendation_acceptance']:.1%}")
        print(f"  Difference: {adaptive['avg_recommendation_acceptance'] - baseline['avg_recommendation_acceptance']:.1%}")

        # Save results
        filename = experiment.save_results()
        print(f"\nResults saved to: {filename}")

    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())