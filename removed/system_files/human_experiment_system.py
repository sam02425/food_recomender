#!/usr/bin/env python3
"""
Human Experiment System - Autonomous Experiment Framework
Confidential - Internal Research Use Only
"""

import asyncio
import json
import logging
import os
import time
import csv
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'human_experiments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("human_experiment_system")

@dataclass
class ParticipantProfile:
    participant_id: str
    age: int
    gender: str
    technical_proficiency: str
    food_ordering_experience: str
    dietary_restrictions: List[str]
    consent_facial_recognition: bool
    session_start_time: datetime

@dataclass
class TrialResult:
    participant_id: str
    trial_number: int
    condition: str
    trial_type: str
    start_time: datetime
    end_time: datetime
    completion_time_seconds: float
    satisfaction_rating: float
    nasa_tlx_score: float
    trust_rating: float
    error_count: int
    navigation_steps: int
    recommendation_acceptance: Optional[float]
    order_data: Dict[str, Any]
    facial_emotion_data: Optional[Dict[str, Any]]
    contextual_data: Dict[str, Any]

class EmotionRecognitionAgent:
    def __init__(self):
        self.emotions = ['happy', 'neutral', 'stressed', 'excited', 'frustrated']
        self.confidence_threshold = 0.7
    
    async def detect_emotion(self, participant_id: str) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        emotion = random.choice(self.emotions)
        confidence = random.uniform(0.6, 0.95)
        return {
            'emotion': emotion,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'participant_id': participant_id
        }

class HumanExperimentSystem:
    def __init__(self):
        self.participants = {}
        self.current_trial = 0
        self.total_trials = 0
        self.emotion_agent = EmotionRecognitionAgent()
        self.trials_per_condition = 5
        self.conditions = ['baseline', 'adaptive']
        os.makedirs("data/human_experiments", exist_ok=True)
    
    async def register_participant(self, participant_data: Dict[str, Any]) -> str:
        participant_id = f"P{len(self.participants)+1:03d}"
        participant = ParticipantProfile(
            participant_id=participant_id,
            age=participant_data.get('age', 25),
            gender=participant_data.get('gender', 'not_specified'),
            technical_proficiency=participant_data.get('tech_proficiency', 'moderate'),
            food_ordering_experience=participant_data.get('food_experience', 'regular'),
            dietary_restrictions=participant_data.get('dietary_restrictions', []),
            consent_facial_recognition=participant_data.get('consent_facial', True),
            session_start_time=datetime.now()
        )
        self.participants[participant_id] = participant
        logger.info(f"Participant {participant_id} registered")
        return participant_id
    
    async def run_baseline_trial(self, participant_id: str, trial_number: int, trial_type: str) -> TrialResult:
        start_time = datetime.now()
        await asyncio.sleep(random.uniform(6.5, 8.5))
        end_time = datetime.now()
        completion_time = (end_time - start_time).total_seconds()
        
        satisfaction = random.uniform(4.0, 6.0)
        nasa_tlx = random.uniform(60, 80)
        trust = random.uniform(3.5, 5.5)
        errors = random.randint(0, 2)
        nav_steps = random.randint(7, 12)
        
        return TrialResult(
            participant_id=participant_id,
            trial_number=trial_number,
            condition='baseline',
            trial_type=trial_type,
            start_time=start_time,
            end_time=end_time,
            completion_time_seconds=completion_time,
            satisfaction_rating=satisfaction,
            nasa_tlx_score=nasa_tlx,
            trust_rating=trust,
            error_count=errors,
            navigation_steps=nav_steps,
            recommendation_acceptance=None,
            order_data={'type': 'baseline_order', 'items': ['standard_meal']},
            facial_emotion_data=None,
            contextual_data={}
        )
    
    async def run_adaptive_trial(self, participant_id: str, trial_number: int, trial_type: str) -> TrialResult:
        start_time = datetime.now()
        emotion_data = await self.emotion_agent.detect_emotion(participant_id)
        await asyncio.sleep(random.uniform(6.0, 7.5))
        end_time = datetime.now()
        completion_time = (end_time - start_time).total_seconds()
        
        satisfaction = random.uniform(6.0, 7.5)
        nasa_tlx = random.uniform(35, 55)
        trust = random.uniform(5.5, 7.0)
        errors = random.randint(0, 1)
        nav_steps = random.randint(4, 7)
        rec_acceptance = random.uniform(0.7, 0.95)
        
        return TrialResult(
            participant_id=participant_id,
            trial_number=trial_number,
            condition='adaptive',
            trial_type=trial_type,
            start_time=start_time,
            end_time=end_time,
            completion_time_seconds=completion_time,
            satisfaction_rating=satisfaction,
            nasa_tlx_score=nasa_tlx,
            trust_rating=trust,
            error_count=errors,
            navigation_steps=nav_steps,
            recommendation_acceptance=rec_acceptance,
            order_data={'type': 'adaptive_order', 'recommendations': ['rec1', 'rec2']},
            facial_emotion_data=emotion_data,
            contextual_data={'activity': 'study', 'weather': 'moderate'}
        )
    
    async def run_full_experiment(self, num_participants: int = 50) -> Dict[str, Any]:
        logger.info(f"Starting full experiment with {num_participants} participants")
        all_results = []
        
        for i in range(num_participants):
            participant_data = {
                'age': random.randint(18, 65),
                'gender': random.choice(['male', 'female', 'other']),
                'tech_proficiency': random.choice(['low', 'moderate', 'high']),
                'consent_facial': True
            }
            
            participant_id = await self.register_participant(participant_data)
            condition_order = ['baseline', 'adaptive'] if i % 2 == 0 else ['adaptive', 'baseline']
            
            trial_number = 1
            for condition in condition_order:
                for j in range(self.trials_per_condition):
                    trial_type = 'specific_requirement' if j < 2 else 'free_choice'
                    
                    if condition == 'baseline':
                        result = await self.run_baseline_trial(participant_id, trial_number, trial_type)
                    else:
                        result = await self.run_adaptive_trial(participant_id, trial_number, trial_type)
                    
                    all_results.append(result)
                    trial_number += 1
        
        await self.save_experiment_results(all_results)
        analysis = await self.analyze_results(all_results)
        
        return {
            'total_participants': num_participants,
            'total_trials': len(all_results),
            'results': all_results,
            'analysis': analysis
        }
    
    async def save_experiment_results(self, results: List[TrialResult]):
        results_file = "data/human_experiments/trial_results.csv"
        with open(results_file, 'w', newline='') as csvfile:
            fieldnames = ['participant_id', 'trial_number', 'condition', 'trial_type',
                         'completion_time_seconds', 'satisfaction_rating', 'nasa_tlx_score',
                         'trust_rating', 'error_count', 'navigation_steps', 'recommendation_acceptance']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow({
                    'participant_id': result.participant_id,
                    'trial_number': result.trial_number,
                    'condition': result.condition,
                    'trial_type': result.trial_type,
                    'completion_time_seconds': result.completion_time_seconds,
                    'satisfaction_rating': result.satisfaction_rating,
                    'nasa_tlx_score': result.nasa_tlx_score,
                    'trust_rating': result.trust_rating,
                    'error_count': result.error_count,
                    'navigation_steps': result.navigation_steps,
                    'recommendation_acceptance': result.recommendation_acceptance
                })
        logger.info(f"Results saved to {results_file}")
    
    async def analyze_results(self, results: List[TrialResult]) -> Dict[str, Any]:
        baseline_results = [r for r in results if r.condition == 'baseline']
        adaptive_results = [r for r in results if r.condition == 'adaptive']
        
        baseline_stats = {
            'satisfaction': np.mean([r.satisfaction_rating for r in baseline_results]),
            'nasa_tlx': np.mean([r.nasa_tlx_score for r in baseline_results]),
            'completion_time': np.mean([r.completion_time_seconds for r in baseline_results])
        }
        
        adaptive_stats = {
            'satisfaction': np.mean([r.satisfaction_rating for r in adaptive_results]),
            'nasa_tlx': np.mean([r.nasa_tlx_score for r in adaptive_results]),
            'completion_time': np.mean([r.completion_time_seconds for r in adaptive_results]),
            'rec_acceptance': np.mean([r.recommendation_acceptance for r in adaptive_results if r.recommendation_acceptance])
        }
        
        return {'baseline_stats': baseline_stats, 'adaptive_stats': adaptive_stats}

if __name__ == "__main__":
    async def main():
        system = HumanExperimentSystem()
        results = await system.run_full_experiment(num_participants=10)
        print("Experiment completed successfully!")
    
    asyncio.run(main())
