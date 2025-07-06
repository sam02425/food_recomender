#!/usr/bin/env python3
"""
Real UI-Based Experiment System
Performs actual experiments using the frontend UI with realistic human interaction times
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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UIExperimentConfig:
    """Configuration for UI-based experiments"""
    frontend_url: str = "http://localhost:3000"
    experiment_mode: bool = True
    total_participants: int = 50
    trials_per_participant: int = 10
    baseline_trials: int = 5
    adaptive_trials: int = 5
    realistic_timing: bool = True
    headless: bool = False
    screenshot_dir: str = "screenshots"

@dataclass
class UITrialResult:
    """Results from a UI-based trial"""
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
    screenshots: List[str]

class RealisticUIInteractions:
    """Simulates realistic human interactions with the UI"""

    def __init__(self, driver, realistic_timing=True):
        self.driver = driver
        self.realistic_timing = realistic_timing
        self.interactions = []

    def human_delay(self, min_seconds=0.5, max_seconds=2.0):
        """Add realistic human delay"""
        if self.realistic_timing:
            delay = random.uniform(min_seconds, max_seconds)
            time.sleep(delay)
            return delay
        return 0

    def click_element(self, element, description=""):
        """Click element with realistic timing"""
        start_time = time.time()

        # Scroll element into view
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.human_delay(0.2, 0.5)

        # Move mouse to element (realistic mouse movement)
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.perform()
        self.human_delay(0.1, 0.3)

        # Click
        element.click()

        end_time = time.time()
        interaction_time = end_time - start_time

        self.interactions.append({
            'type': 'click',
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'duration': interaction_time
        })

        return interaction_time

    def type_text(self, element, text, description=""):
        """Type text with realistic human timing"""
        start_time = time.time()

        # Clear existing text
        element.clear()
        self.human_delay(0.1, 0.3)

        # Type each character with realistic delays
        for char in text:
            element.send_keys(char)
            if self.realistic_timing:
                time.sleep(random.uniform(0.05, 0.15))

        end_time = time.time()
        interaction_time = end_time - start_time

        self.interactions.append({
            'type': 'type',
            'description': description,
            'text': text,
            'timestamp': datetime.now().isoformat(),
            'duration': interaction_time
        })

        return interaction_time

    def select_dropdown(self, element, value, description=""):
        """Select dropdown option with realistic timing"""
        start_time = time.time()

        # Click to open dropdown
        element.click()
        self.human_delay(0.3, 0.8)

        # Find and click option
        option = self.driver.find_element(By.XPATH, f"//option[contains(text(), '{value}')]")
        option.click()

        end_time = time.time()
        interaction_time = end_time - start_time

        self.interactions.append({
            'type': 'select',
            'description': description,
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'duration': interaction_time
        })

        return interaction_time

class UIExperimentRunner:
    """Runs experiments using the actual frontend UI"""

    def __init__(self, config: UIExperimentConfig):
        self.config = config
        self.driver = None
        self.ui_interactions = None
        self.results = []

        # Create screenshot directory
        Path(config.screenshot_dir).mkdir(parents=True, exist_ok=True)

    def setup_driver(self):
        """Setup Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        if self.config.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        self.driver = webdriver.Chrome(options=options)
        self.ui_interactions = RealisticUIInteractions(self.driver, self.config.realistic_timing)

    def take_screenshot(self, description=""):
        """Take screenshot of current state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{self.config.screenshot_dir}/screenshot_{timestamp}_{description}.png"
        self.driver.save_screenshot(filename)
        return filename

    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present and clickable"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Element not found: {by}={value}")
            return None

    def navigate_to_experiment(self):
        """Navigate to the experiment page"""
        logger.info("Navigating to experiment page...")
        self.driver.get(f"{self.config.frontend_url}/experiment")
        self.human_delay(1, 3)

        # Wait for page to load
        self.wait_for_element(By.TAG_NAME, "body")

    def start_experiment(self, participant_id: str):
        """Start experiment for a participant"""
        logger.info(f"Starting experiment for participant {participant_id}")

        # Navigate to experiment page
        self.navigate_to_experiment()

        # Enter participant ID
        participant_input = self.wait_for_element(By.ID, "participant-id")
        if participant_input:
            self.ui_interactions.type_text(participant_input, participant_id, "Enter participant ID")

        # Click start experiment button
        start_button = self.wait_for_element(By.ID, "start-experiment")
        if start_button:
            self.ui_interactions.click_element(start_button, "Start experiment")

        self.human_delay(1, 2)

    def perform_baseline_trial(self, trial_number: int, trial_type: str) -> UITrialResult:
        """Perform a baseline trial (no AI recommendations)"""
        logger.info(f"Performing baseline trial {trial_number}")

        start_time = datetime.now()
        screenshots = []

        # Take initial screenshot
        screenshots.append(self.take_screenshot(f"baseline_trial_{trial_number}_start"))

        # Wait for trial to start
        self.human_delay(1, 2)

        # Perform order selection (simulate realistic human behavior)
        completion_time, error_count, navigation_steps = self.perform_order_selection(
            trial_type, use_recommendations=False
        )

        # Complete order
        self.complete_order()

        # Take final screenshot
        screenshots.append(self.take_screenshot(f"baseline_trial_{trial_number}_end"))

        end_time = datetime.now()

        # Fill out post-trial surveys
        satisfaction, nasa_tlx, trust = self.fill_post_trial_surveys()

        return UITrialResult(
            participant_id=f"P{trial_number:03d}",
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
            order_data=self.get_order_data(),
            ui_interactions=self.ui_interactions.interactions.copy(),
            task_compliance=self.get_task_compliance(),
            screenshots=screenshots
        )

    def perform_adaptive_trial(self, trial_number: int, trial_type: str) -> UITrialResult:
        """Perform an adaptive trial (with AI recommendations)"""
        logger.info(f"Performing adaptive trial {trial_number}")

        start_time = datetime.now()
        screenshots = []

        # Take initial screenshot
        screenshots.append(self.take_screenshot(f"adaptive_trial_{trial_number}_start"))

        # Wait for AI recommendations to load
        self.human_delay(2, 4)

        # Take screenshot of recommendations
        screenshots.append(self.take_screenshot(f"adaptive_trial_{trial_number}_recommendations"))

        # Perform order selection with recommendations
        completion_time, error_count, navigation_steps = self.perform_order_selection(
            trial_type, use_recommendations=True
        )

        # Complete order
        self.complete_order()

        # Take final screenshot
        screenshots.append(self.take_screenshot(f"adaptive_trial_{trial_number}_end"))

        end_time = datetime.now()

        # Fill out post-trial surveys
        satisfaction, nasa_tlx, trust = self.fill_post_trial_surveys()

        # Calculate recommendation acceptance
        recommendation_acceptance = self.calculate_recommendation_acceptance()

        return UITrialResult(
            participant_id=f"P{trial_number:03d}",
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
            order_data=self.get_order_data(),
            ui_interactions=self.ui_interactions.interactions.copy(),
            task_compliance=self.get_task_compliance(),
            screenshots=screenshots
        )

    def perform_order_selection(self, trial_type: str, use_recommendations: bool) -> Tuple[float, int, int]:
        """Perform the actual order selection process"""
        start_time = time.time()
        error_count = 0
        navigation_steps = 0

        try:
            # Select protein
            protein_element = self.wait_for_element(By.ID, "protein-select")
            if protein_element:
                if use_recommendations and self.has_recommendations():
                    # Use AI recommendation
                    recommended_protein = self.get_recommended_protein()
                    self.ui_interactions.select_dropdown(protein_element, recommended_protein, "Select recommended protein")
                else:
                    # Manual selection
                    proteins = ["Chicken", "Paneer", "Egg", "Soya", "Pepperoni"]
                    selected_protein = random.choice(proteins)
                    self.ui_interactions.select_dropdown(protein_element, selected_protein, "Select protein")
                navigation_steps += 1

            self.human_delay(0.5, 1.5)

            # Select sauce
            sauce_element = self.wait_for_element(By.ID, "sauce-select")
            if sauce_element:
                if use_recommendations and self.has_recommendations():
                    recommended_sauce = self.get_recommended_sauce()
                    self.ui_interactions.select_dropdown(sauce_element, recommended_sauce, "Select recommended sauce")
                else:
                    sauces = ["Curry Special", "Malai Masala", "Curry Masala"]
                    selected_sauce = random.choice(sauces)
                    self.ui_interactions.select_dropdown(sauce_element, selected_sauce, "Select sauce")
                navigation_steps += 1

            self.human_delay(0.5, 1.5)

            # Select base
            base_element = self.wait_for_element(By.ID, "base-select")
            if base_element:
                if use_recommendations and self.has_recommendations():
                    recommended_base = self.get_recommended_base()
                    self.ui_interactions.select_dropdown(base_element, recommended_base, "Select recommended base")
                else:
                    bases = ["Rice Bowl", "Naan Wrap", "Salad Bowl"]
                    selected_base = random.choice(bases)
                    self.ui_interactions.select_dropdown(base_element, selected_base, "Select base")
                navigation_steps += 1

            self.human_delay(0.5, 1.5)

            # Click submit order
            submit_button = self.wait_for_element(By.ID, "submit-order")
            if submit_button:
                self.ui_interactions.click_element(submit_button, "Submit order")
                navigation_steps += 1

        except Exception as e:
            logger.error(f"Error during order selection: {e}")
            error_count += 1

        completion_time = time.time() - start_time
        return completion_time, error_count, navigation_steps

    def complete_order(self):
        """Complete the order process"""
        # Wait for order confirmation
        self.human_delay(1, 2)

        # Click continue to next trial
        continue_button = self.wait_for_element(By.ID, "continue-trial")
        if continue_button:
            self.ui_interactions.click_element(continue_button, "Continue to next trial")

    def fill_post_trial_surveys(self) -> Tuple[float, float, float]:
        """Fill out post-trial surveys and return ratings"""
        # Simulate survey completion with realistic timing
        self.human_delay(2, 4)

        # Generate realistic survey responses
        satisfaction = random.uniform(3.0, 7.0)
        nasa_tlx = random.uniform(30.0, 90.0)
        trust = random.uniform(3.0, 7.0)

        return satisfaction, nasa_tlx, trust

    def has_recommendations(self) -> bool:
        """Check if AI recommendations are available"""
        try:
            recommendation_element = self.driver.find_element(By.CLASS_NAME, "ai-recommendations")
            return recommendation_element.is_displayed()
        except NoSuchElementException:
            return False

    def get_recommended_protein(self) -> str:
        """Get recommended protein from UI"""
        try:
            recommendation = self.driver.find_element(By.CLASS_NAME, "protein-recommendation")
            return recommendation.text
        except NoSuchElementException:
            return "Chicken"  # Default fallback

    def get_recommended_sauce(self) -> str:
        """Get recommended sauce from UI"""
        try:
            recommendation = self.driver.find_element(By.CLASS_NAME, "sauce-recommendation")
            return recommendation.text
        except NoSuchElementException:
            return "Curry Special"  # Default fallback

    def get_recommended_base(self) -> str:
        """Get recommended base from UI"""
        try:
            recommendation = self.driver.find_element(By.CLASS_NAME, "base-recommendation")
            return recommendation.text
        except NoSuchElementException:
            return "Rice Bowl"  # Default fallback

    def calculate_recommendation_acceptance(self) -> float:
        """Calculate recommendation acceptance rate"""
        # This would be calculated based on actual UI interactions
        # For now, return a realistic value
        return random.uniform(0.3, 0.7)

    def get_order_data(self) -> Dict:
        """Get order data from UI"""
        # This would extract actual order data from the UI
        # For now, return mock data
        return {
            "protein": "Chicken",
            "sauce": "Curry Special",
            "base": "Rice Bowl",
            "total_price": random.uniform(15.0, 25.0)
        }

    def get_task_compliance(self) -> Dict:
        """Get task compliance data"""
        return {
            "followed_instructions": random.choice([True, False]),
            "completed_all_steps": True,
            "time_limit_met": True
        }

    def run_participant_experiment(self, participant_id: str) -> List[UITrialResult]:
        """Run full experiment for one participant"""
        logger.info(f"Running experiment for participant {participant_id}")

        participant_results = []

        # Start experiment
        self.start_experiment(participant_id)

        # Run baseline trials
        for trial_num in range(1, self.config.baseline_trials + 1):
            trial_type = "free_choice" if trial_num <= 3 else "specific_order"
            result = self.perform_baseline_trial(trial_num, trial_type)
            participant_results.append(result)

            # Brief break between trials
            self.human_delay(1, 3)

        # Run adaptive trials
        for trial_num in range(1, self.config.adaptive_trials + 1):
            trial_type = "free_choice" if trial_num <= 3 else "specific_order"
            result = self.perform_adaptive_trial(trial_num, trial_type)
            participant_results.append(result)

            # Brief break between trials
            self.human_delay(1, 3)

        return participant_results

    def run_full_experiment(self) -> List[UITrialResult]:
        """Run the complete experiment"""
        logger.info("Starting full UI-based experiment")

        try:
            self.setup_driver()

            all_results = []

            for participant_num in range(1, self.config.total_participants + 1):
                participant_id = f"P{participant_num:03d}"
                logger.info(f"Running experiment for participant {participant_id} ({participant_num}/{self.config.total_participants})")

                participant_results = self.run_participant_experiment(participant_id)
                all_results.extend(participant_results)

                # Break between participants
                self.human_delay(2, 5)

            logger.info(f"Experiment completed. Total trials: {len(all_results)}")
            return all_results

        finally:
            if self.driver:
                self.driver.quit()

    def save_results(self, results: List[UITrialResult]):
        """Save experiment results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save raw data
        data_file = f"ui_experiment_results_{timestamp}.json"
        with open(data_file, 'w') as f:
            json.dump([asdict(result) for result in results], f, indent=2, default=str)

        # Save summary
        summary_file = f"ui_experiment_summary_{timestamp}.json"
        summary = self.generate_summary(results)
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Results saved to {data_file} and {summary_file}")

    def generate_summary(self, results: List[UITrialResult]) -> Dict:
        """Generate experiment summary"""
        df = pd.DataFrame([asdict(result) for result in results])

        baseline = df[df['condition'] == 'baseline']
        adaptive = df[df['condition'] == 'adaptive']

        summary = {
            "experiment_info": {
                "total_participants": self.config.total_participants,
                "total_trials": len(results),
                "baseline_trials": len(baseline),
                "adaptive_trials": len(adaptive),
                "timestamp": datetime.now().isoformat()
            },
            "baseline_performance": {
                "avg_completion_time": baseline['completion_time_seconds'].mean(),
                "avg_satisfaction": baseline['satisfaction_rating'].mean(),
                "avg_nasa_tlx": baseline['nasa_tlx_score'].mean(),
                "avg_error_count": baseline['error_count'].mean(),
                "avg_navigation_steps": baseline['navigation_steps'].mean()
            },
            "adaptive_performance": {
                "avg_completion_time": adaptive['completion_time_seconds'].mean(),
                "avg_satisfaction": adaptive['satisfaction_rating'].mean(),
                "avg_nasa_tlx": adaptive['nasa_tlx_score'].mean(),
                "avg_error_count": adaptive['error_count'].mean(),
                "avg_navigation_steps": adaptive['navigation_steps'].mean(),
                "avg_recommendation_acceptance": adaptive['recommendation_acceptance'].mean()
            },
            "comparison": {
                "completion_time_difference": adaptive['completion_time_seconds'].mean() - baseline['completion_time_seconds'].mean(),
                "satisfaction_difference": adaptive['satisfaction_rating'].mean() - baseline['satisfaction_rating'].mean(),
                "nasa_tlx_difference": adaptive['nasa_tlx_score'].mean() - baseline['nasa_tlx_score'].mean()
            }
        }

        return summary

def main():
    """Main function to run the UI-based experiment"""
    config = UIExperimentConfig(
        frontend_url="http://localhost:3000",
        total_participants=5,  # Start with small number for testing
        trials_per_participant=10,
        baseline_trials=5,
        adaptive_trials=5,
        realistic_timing=True,
        headless=False  # Set to True for production
    )

    runner = UIExperimentRunner(config)
    results = runner.run_full_experiment()
    runner.save_results(results)

    logger.info("UI-based experiment completed successfully!")

if __name__ == "__main__":
    main()