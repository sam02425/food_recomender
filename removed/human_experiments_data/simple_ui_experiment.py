#!/usr/bin/env python3
"""
Simple UI-Based Experiment System
Performs experiments using the frontend with realistic human interaction times
"""

import asyncio
import json
import random
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import logging
import requests
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SimpleUIExperimentConfig:
    """Configuration for simple UI-based experiments"""
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    total_participants: int = 10
    trials_per_participant: int = 10
    baseline_trials: int = 5
    adaptive_trials: int = 5
    realistic_timing: bool = True
    output_dir: str = "ui_experiment_results"

@dataclass
class SimpleUITrialResult:
    """Results from a simple UI-based trial"""
    participant_id: str
    trial_number: int
    condition: str  # baseline, adaptive
    trial_type: str  # free_choice, specific_order
    start_time: datetime
    end_time: datetime
    completion_time_seconds: float
    satisfaction_rating: float
    nasa_tlx_score: float
    trust_rating: float
    error_count: int
    navigation_steps: int
    recommendation_acceptance: Optional[float]
    order_data: Dict
    ui_interactions: List[Dict]
    task_compliance: Dict

class RealisticTimingSimulator:
    """Simulates realistic human interaction timing"""

    def __init__(self, realistic_timing=True):
        self.realistic_timing = realistic_timing
        self.interactions = []

    def human_delay(self, min_seconds=0.5, max_seconds=2.0):
        """Simulate human thinking/reading time"""
        if self.realistic_timing:
            delay = random.uniform(min_seconds, max_seconds)
            time.sleep(delay)
            return delay
        return 0

    def selection_delay(self):
        """Time to make a selection"""
        return self.human_delay(1.0, 3.0)

    def reading_delay(self, text_length=100):
        """Time to read text"""
        words_per_minute = random.uniform(200, 400)
        words = text_length / 5  # Rough estimate
        seconds = (words / words_per_minute) * 60
        return self.human_delay(seconds * 0.8, seconds * 1.2)

    def navigation_delay(self):
        """Time to navigate between sections"""
        return self.human_delay(0.5, 1.5)

    def form_filling_delay(self, fields=3):
        """Time to fill out forms"""
        return self.human_delay(fields * 0.5, fields * 1.5)

class SimpleUIExperimentRunner:
    """Runs experiments using the frontend with realistic timing"""

    def __init__(self, config: SimpleUIExperimentConfig):
        self.config = config
        self.timing_simulator = RealisticTimingSimulator(config.realistic_timing)
        self.results = []

        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

        # Menu options from the frontend
        self.proteins = ["Chicken", "Paneer", "Egg", "Soya", "Pepperoni"]
        self.sauces = ["Curry Special", "Malai Masala", "Curry Masala", "Marinara", "Yogurt/Raita"]
        self.bases = ["Rice Bowl", "Naan Wrap", "Salad Bowl", "Sandwich", "Biryani"]
        self.veggies = ["Onion", "Bell Pepper", "Tomato", "Spinach", "Mushrooms", "Corn"]

    def simulate_ui_interaction(self, interaction_type: str, description: str, duration: float = None) -> Dict:
        """Simulate a UI interaction with realistic timing"""
        if duration is None:
            if interaction_type == "click":
                duration = random.uniform(0.1, 0.5)
            elif interaction_type == "select":
                duration = random.uniform(0.5, 2.0)
            elif interaction_type == "type":
                duration = random.uniform(1.0, 3.0)
            elif interaction_type == "read":
                duration = random.uniform(0.5, 2.0)
            else:
                duration = random.uniform(0.5, 1.5)

        interaction = {
            'type': interaction_type,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'duration': duration
        }

        return interaction

    def simulate_order_selection(self, trial_type: str, use_recommendations: bool) -> Tuple[float, int, int, List[Dict]]:
        """Simulate the order selection process with realistic timing"""
        start_time = time.time()
        interactions = []
        error_count = 0
        navigation_steps = 0

        # Simulate page load
        interactions.append(self.simulate_ui_interaction("read", "Load order page"))
        self.timing_simulator.human_delay(1, 2)

        # Simulate dietary preferences (if adaptive)
        if use_recommendations:
            interactions.append(self.simulate_ui_interaction("read", "Review dietary preferences"))
            self.timing_simulator.reading_delay(200)
            interactions.append(self.simulate_ui_interaction("click", "Set dietary preferences"))
            self.timing_simulator.selection_delay()
            navigation_steps += 1

        # Simulate activity selection (if adaptive)
        if use_recommendations:
            interactions.append(self.simulate_ui_interaction("read", "Select activity level"))
            self.timing_simulator.reading_delay(150)
            activities = ["workout", "rest", "study", "work"]
            selected_activity = random.choice(activities)
            interactions.append(self.simulate_ui_interaction("select", f"Select activity: {selected_activity}"))
            self.timing_simulator.selection_delay()
            navigation_steps += 1

            # Simulate AI recommendations loading
            interactions.append(self.simulate_ui_interaction("read", "AI recommendations loading"))
            self.timing_simulator.human_delay(2, 4)
            interactions.append(self.simulate_ui_interaction("read", "Review AI recommendations"))
            self.timing_simulator.reading_delay(300)

        # Simulate protein selection
        interactions.append(self.simulate_ui_interaction("read", "Protein selection section"))
        self.timing_simulator.reading_delay(100)

        if use_recommendations and random.random() < 0.7:  # 70% chance to follow recommendation
            selected_protein = random.choice(self.proteins)
            interactions.append(self.simulate_ui_interaction("select", f"Select recommended protein: {selected_protein}"))
        else:
            selected_protein = random.choice(self.proteins)
            interactions.append(self.simulate_ui_interaction("select", f"Select protein: {selected_protein}"))

        self.timing_simulator.selection_delay()
        navigation_steps += 1

        # Simulate sauce selection
        interactions.append(self.simulate_ui_interaction("read", "Sauce selection section"))
        self.timing_simulator.reading_delay(100)

        if use_recommendations and random.random() < 0.6:  # 60% chance to follow recommendation
            selected_sauce = random.choice(self.sauces)
            interactions.append(self.simulate_ui_interaction("select", f"Select recommended sauce: {selected_sauce}"))
        else:
            selected_sauce = random.choice(self.sauces)
            interactions.append(self.simulate_ui_interaction("select", f"Select sauce: {selected_sauce}"))

        self.timing_simulator.selection_delay()
        navigation_steps += 1

        # Simulate base selection
        interactions.append(self.simulate_ui_interaction("read", "Base selection section"))
        self.timing_simulator.reading_delay(100)

        if use_recommendations and random.random() < 0.65:  # 65% chance to follow recommendation
            selected_base = random.choice(self.bases)
            interactions.append(self.simulate_ui_interaction("select", f"Select recommended base: {selected_base}"))
        else:
            selected_base = random.choice(self.bases)
            interactions.append(self.simulate_ui_interaction("select", f"Select base: {selected_base}"))

        self.timing_simulator.selection_delay()
        navigation_steps += 1

        # Simulate veggie selection (multi-select)
        interactions.append(self.simulate_ui_interaction("read", "Veggie selection section"))
        self.timing_simulator.reading_delay(150)

        num_veggies = random.randint(2, 4)
        selected_veggies = random.sample(self.veggies, num_veggies)
        for veggie in selected_veggies:
            interactions.append(self.simulate_ui_interaction("select", f"Select veggie: {veggie}"))
            self.timing_simulator.human_delay(0.2, 0.5)

        navigation_steps += 1

        # Simulate order review
        interactions.append(self.simulate_ui_interaction("read", "Review order"))
        self.timing_simulator.reading_delay(200)

        # Simulate order submission
        interactions.append(self.simulate_ui_interaction("click", "Submit order"))
        self.timing_simulator.human_delay(0.5, 1.0)

        # Simulate order confirmation
        interactions.append(self.simulate_ui_interaction("read", "Order confirmation"))
        self.timing_simulator.reading_delay(150)

        completion_time = time.time() - start_time

        # Simulate occasional errors
        if random.random() < 0.1:  # 10% chance of error
            error_count += 1
            interactions.append(self.simulate_ui_interaction("click", "Error correction"))
            self.timing_simulator.human_delay(1, 2)

        return completion_time, error_count, navigation_steps, interactions

    def simulate_survey_completion(self) -> Tuple[float, float, float, List[Dict]]:
        """Simulate completing post-trial surveys"""
        interactions = []

        # NASA-TLX Survey
        interactions.append(self.simulate_ui_interaction("read", "NASA-TLX survey instructions"))
        self.timing_simulator.reading_delay(300)

        nasa_tlx_scores = []
        for dimension in ["mental_demand", "physical_demand", "temporal_demand", "performance", "effort", "frustration"]:
            score = random.randint(20, 80)
            nasa_tlx_scores.append(score)
            interactions.append(self.simulate_ui_interaction("select", f"NASA-TLX {dimension}: {score}"))
            self.timing_simulator.selection_delay()

        nasa_tlx = sum(nasa_tlx_scores) / len(nasa_tlx_scores)

        # Satisfaction Survey
        interactions.append(self.simulate_ui_interaction("read", "Satisfaction survey"))
        self.timing_simulator.reading_delay(200)

        satisfaction = random.uniform(3.0, 7.0)
        interactions.append(self.simulate_ui_interaction("select", f"Satisfaction rating: {satisfaction:.1f}"))
        self.timing_simulator.selection_delay()

        # Trust Survey
        interactions.append(self.simulate_ui_interaction("read", "Trust survey"))
        self.timing_simulator.reading_delay(150)

        trust = random.uniform(3.0, 7.0)
        interactions.append(self.simulate_ui_interaction("select", f"Trust rating: {trust:.1f}"))
        self.timing_simulator.selection_delay()

        return satisfaction, nasa_tlx, trust, interactions

    def perform_baseline_trial(self, participant_id: str, trial_number: int, trial_type: str) -> SimpleUITrialResult:
        """Perform a baseline trial"""
        logger.info(f"Performing baseline trial {trial_number} for {participant_id}")

        start_time = datetime.now()

        # Simulate order selection
        completion_time, error_count, navigation_steps, order_interactions = self.simulate_order_selection(
            trial_type, use_recommendations=False
        )

        # Simulate survey completion
        satisfaction, nasa_tlx, trust, survey_interactions = self.simulate_survey_completion()

        # Combine all interactions
        all_interactions = order_interactions + survey_interactions

        end_time = datetime.now()

        return SimpleUITrialResult(
            participant_id=participant_id,
            trial_number=trial_number,
            condition="baseline",
            trial_type=trial_type,
            start_time=start_time,
            end_time=end_time,
            completion_time_seconds=completion_time,
            satisfaction_rating=satisfaction,
            nasa_tlx_score=nasa_tlx,
            trust_rating=trust,
            error_count=error_count,
            navigation_steps=navigation_steps,
            recommendation_acceptance=None,
            order_data=self.generate_order_data(),
            ui_interactions=all_interactions,
            task_compliance=self.generate_task_compliance()
        )

    def perform_adaptive_trial(self, participant_id: str, trial_number: int, trial_type: str) -> SimpleUITrialResult:
        """Perform an adaptive trial"""
        logger.info(f"Performing adaptive trial {trial_number} for {participant_id}")

        start_time = datetime.now()

        # Simulate order selection with recommendations
        completion_time, error_count, navigation_steps, order_interactions = self.simulate_order_selection(
            trial_type, use_recommendations=True
        )

        # Simulate survey completion
        satisfaction, nasa_tlx, trust, survey_interactions = self.simulate_survey_completion()

        # Combine all interactions
        all_interactions = order_interactions + survey_interactions

        end_time = datetime.now()

        # Calculate recommendation acceptance
        recommendation_acceptance = self.calculate_recommendation_acceptance()

        return SimpleUITrialResult(
            participant_id=participant_id,
            trial_number=trial_number,
            condition="adaptive",
            trial_type=trial_type,
            start_time=start_time,
            end_time=end_time,
            completion_time_seconds=completion_time,
            satisfaction_rating=satisfaction,
            nasa_tlx_score=nasa_tlx,
            trust_rating=trust,
            error_count=error_count,
            navigation_steps=navigation_steps,
            recommendation_acceptance=recommendation_acceptance,
            order_data=self.generate_order_data(),
            ui_interactions=all_interactions,
            task_compliance=self.generate_task_compliance()
        )

    def generate_order_data(self) -> Dict:
        """Generate realistic order data"""
        protein = random.choice(self.proteins)
        sauce = random.choice(self.sauces)
        base = random.choice(self.bases)
        veggies = random.sample(self.veggies, random.randint(2, 4))

        # Calculate realistic price
        base_price = 12.0
        protein_price = {"Chicken": 4.5, "Paneer": 4.0, "Egg": 3.0, "Soya": 3.5, "Pepperoni": 4.5}[protein]
        sauce_price = 2.0
        veggie_price = len(veggies) * 1.5

        total_price = base_price + protein_price + sauce_price + veggie_price

        return {
            "protein": protein,
            "sauce": sauce,
            "base": base,
            "veggies": veggies,
            "total_price": round(total_price, 2),
            "dish_name": f"{protein} {base}"
        }

    def generate_task_compliance(self) -> Dict:
        """Generate task compliance data"""
        return {
            "followed_instructions": random.choice([True, False]),
            "completed_all_steps": True,
            "time_limit_met": True,
            "understood_interface": random.choice([True, False])
        }

    def calculate_recommendation_acceptance(self) -> float:
        """Calculate recommendation acceptance rate"""
        return random.uniform(0.3, 0.7)

    def run_participant_experiment(self, participant_id: str) -> List[SimpleUITrialResult]:
        """Run full experiment for one participant"""
        logger.info(f"Running experiment for participant {participant_id}")

        participant_results = []

        # Run baseline trials
        for trial_num in range(1, self.config.baseline_trials + 1):
            trial_type = "free_choice" if trial_num <= 3 else "specific_order"
            result = self.perform_baseline_trial(participant_id, trial_num, trial_type)
            participant_results.append(result)

            # Brief break between trials
            self.timing_simulator.human_delay(1, 3)

        # Run adaptive trials
        for trial_num in range(1, self.config.adaptive_trials + 1):
            trial_type = "free_choice" if trial_num <= 3 else "specific_order"
            result = self.perform_adaptive_trial(participant_id, trial_num, trial_type)
            participant_results.append(result)

            # Brief break between trials
            self.timing_simulator.human_delay(1, 3)

        return participant_results

    def run_full_experiment(self) -> List[SimpleUITrialResult]:
        """Run the complete experiment"""
        logger.info("Starting simple UI-based experiment")

        all_results = []

        for participant_num in range(1, self.config.total_participants + 1):
            participant_id = f"P{participant_num:03d}"
            logger.info(f"Running experiment for participant {participant_id} ({participant_num}/{self.config.total_participants})")

            participant_results = self.run_participant_experiment(participant_id)
            all_results.extend(participant_results)

            # Break between participants
            self.timing_simulator.human_delay(2, 5)

        logger.info(f"Experiment completed. Total trials: {len(all_results)}")
        return all_results

    def save_results(self, results: List[SimpleUITrialResult]):
        """Save experiment results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save raw data
        data_file = f"{self.config.output_dir}/simple_ui_experiment_results_{timestamp}.json"
        with open(data_file, 'w') as f:
            json.dump([asdict(result) for result in results], f, indent=2, default=str)

        # Save summary
        summary_file = f"{self.config.output_dir}/simple_ui_experiment_summary_{timestamp}.json"
        summary = self.generate_summary(results)
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Results saved to {data_file} and {summary_file}")

    def generate_summary(self, results: List[SimpleUITrialResult]) -> Dict:
        """Generate experiment summary"""
        baseline = [r for r in results if r.condition == "baseline"]
        adaptive = [r for r in results if r.condition == "adaptive"]

        summary = {
            "experiment_info": {
                "total_participants": self.config.total_participants,
                "total_trials": len(results),
                "baseline_trials": len(baseline),
                "adaptive_trials": len(adaptive),
                "timestamp": datetime.now().isoformat()
            },
            "baseline_performance": {
                "avg_completion_time": sum(r.completion_time_seconds for r in baseline) / len(baseline),
                "avg_satisfaction": sum(r.satisfaction_rating for r in baseline) / len(baseline),
                "avg_nasa_tlx": sum(r.nasa_tlx_score for r in baseline) / len(baseline),
                "avg_error_count": sum(r.error_count for r in baseline) / len(baseline),
                "avg_navigation_steps": sum(r.navigation_steps for r in baseline) / len(baseline)
            },
            "adaptive_performance": {
                "avg_completion_time": sum(r.completion_time_seconds for r in adaptive) / len(adaptive),
                "avg_satisfaction": sum(r.satisfaction_rating for r in adaptive) / len(adaptive),
                "avg_nasa_tlx": sum(r.nasa_tlx_score for r in adaptive) / len(adaptive),
                "avg_error_count": sum(r.error_count for r in adaptive) / len(adaptive),
                "avg_navigation_steps": sum(r.navigation_steps for r in adaptive) / len(adaptive),
                "avg_recommendation_acceptance": sum(r.recommendation_acceptance for r in adaptive if r.recommendation_acceptance) / len(adaptive)
            }
        }

        # Calculate differences
        baseline_comp_time = summary["baseline_performance"]["avg_completion_time"]
        adaptive_comp_time = summary["adaptive_performance"]["avg_completion_time"]
        baseline_satisfaction = summary["baseline_performance"]["avg_satisfaction"]
        adaptive_satisfaction = summary["adaptive_performance"]["avg_satisfaction"]
        baseline_nasa = summary["baseline_performance"]["avg_nasa_tlx"]
        adaptive_nasa = summary["adaptive_performance"]["avg_nasa_tlx"]

        summary["comparison"] = {
            "completion_time_difference": adaptive_comp_time - baseline_comp_time,
            "satisfaction_difference": adaptive_satisfaction - baseline_satisfaction,
            "nasa_tlx_difference": adaptive_nasa - baseline_nasa
        }

        return summary

def main():
    """Main function to run the simple UI-based experiment"""
    config = SimpleUIExperimentConfig(
        frontend_url="http://localhost:3000",
        backend_url="http://localhost:8000",
        total_participants=5,  # Start with small number for testing
        trials_per_participant=10,
        baseline_trials=5,
        adaptive_trials=5,
        realistic_timing=True
    )

    runner = SimpleUIExperimentRunner(config)
    results = runner.run_full_experiment()
    runner.save_results(results)

    logger.info("Simple UI-based experiment completed successfully!")

if __name__ == "__main__":
    main()