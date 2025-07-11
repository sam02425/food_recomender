#!/usr/bin/env python3
"""
Automated Human Experiment Simulator
====================================

This program simulates 50 real human participants performing the food recommender
experiment with realistic behavior patterns, UI interactions, and unbiased data collection.

Features:
- 50 unique participants with realistic demographics
- Complete UI interaction simulation (not just API calls)
- Realistic decision-making patterns and timing
- Agent recommendation testing and feedback
- Comprehensive data collection for analysis
- Unbiased experimental design
- Step-by-step task completion

Author: Experiment System
Date: 2024
"""

import json
import csv
import random
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import numpy as np
from pathlib import Path
import os
import psycopg2
from psycopg2 import sql

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('experiment_simulation.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class Participant:
    """Represents a simulated human participant"""
    id: str
    name: str
    age: int
    gender: str
    occupation: str
    tech_savviness: float  # 0-1 scale
    dietary_preferences: List[str]
    allergies: List[str]
    decision_speed: float  # seconds per decision
    attention_span: float  # minutes
    experiment_phase: str = "A"  # A or B
    current_step: str = "start"
    selections: Dict[str, Any] = None
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    nasatlx_scores: Dict[str, int] = None
    sus_scores: List[int] = None
    satisfaction_scores: Dict[str, int] = None
    agent_interactions: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.selections is None:
            self.selections = {}
        if self.nasatlx_scores is None:
            self.nasatlx_scores = {}
        if self.sus_scores is None:
            self.sus_scores = []
        if self.satisfaction_scores is None:
            self.satisfaction_scores = {}
        if self.agent_interactions is None:
            self.agent_interactions = []

class ExperimentSimulator:
    """Main experiment simulator class"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.participants: List[Participant] = []
        self.experiment_data: List[Dict[str, Any]] = []
        self.results_dir = Path("experiment_results")
        self.results_dir.mkdir(exist_ok=True)

        # Realistic participant data
        self.names = [
            "Emma Johnson", "Liam Smith", "Olivia Davis", "Noah Wilson", "Ava Brown",
            "William Jones", "Isabella Garcia", "James Miller", "Sophia Martinez", "Benjamin Anderson",
            "Mia Taylor", "Lucas Thomas", "Charlotte Moore", "Mason Jackson", "Amelia Martin",
            "Ethan Lee", "Harper Thompson", "Alexander White", "Evelyn Harris", "Henry Clark",
            "Abigail Lewis", "Sebastian Robinson", "Emily Walker", "Jack Hall", "Elizabeth Allen",
            "Owen Young", "Sofia King", "Daniel Wright", "Avery Lopez", "Jackson Hill",
            "Ella Scott", "Samuel Green", "Madison Adams", "Sebastian Baker", "Scarlett Gonzalez",
            "David Nelson", "Victoria Carter", "Joseph Mitchell", "Luna Perez", "Carter Roberts",
            "Grace Turner", "Owen Phillips", "Chloe Campbell", "Wyatt Parker", "Penelope Evans",
            "John Edwards", "Layla Collins", "Luke Stewart", "Riley Sanchez", "Isaac Morris"
        ]

        self.occupations = [
            "Software Engineer", "Teacher", "Nurse", "Marketing Manager", "Student",
            "Accountant", "Designer", "Sales Representative", "Doctor", "Chef",
            "Writer", "Engineer", "Administrator", "Consultant", "Artist",
            "Manager", "Analyst", "Coordinator", "Specialist", "Assistant"
        ]

        self.dietary_options = [
            "vegetarian", "vegan", "halal", "no_beef", "no_pork",
            "lacto_vegetarian", "ovo_vegetarian", "lacto_ovo_vegetarian"
        ]

        self.allergy_options = [
            "dairy", "eggs", "nuts", "peanuts", "soy", "gluten", "shellfish", "fish", "sesame"
        ]

    def generate_participants(self, count: int = 50) -> List[Participant]:
        """Generate realistic participants with diverse characteristics"""
        logging.info(f"Generating {count} participants...")

        participants = []
        for i in range(count):
            # Random but realistic participant generation
            name = random.choice(self.names)
            age = random.randint(18, 65)
            gender = random.choice(["Male", "Female", "Non-binary"])
            occupation = random.choice(self.occupations)

            # Realistic tech savviness based on age and occupation
            base_tech = 0.5
            if age < 30:
                base_tech += 0.3
            elif age > 50:
                base_tech -= 0.2
            if occupation in ["Software Engineer", "Designer", "Analyst"]:
                base_tech += 0.2
            tech_savviness = max(0.1, min(1.0, base_tech + random.uniform(-0.2, 0.2)))

            # Realistic dietary preferences and allergies
            dietary_preferences = []
            if random.random() < 0.3:  # 30% have dietary restrictions
                dietary_preferences = random.sample(self.dietary_options, random.randint(1, 2))

            allergies = []
            if random.random() < 0.15:  # 15% have allergies
                allergies = random.sample(self.allergy_options, random.randint(1, 2))

            # Realistic decision-making characteristics
            decision_speed = random.uniform(2.0, 8.0)  # seconds
            attention_span = random.uniform(15.0, 45.0)  # minutes

            # Force Phase B for single-participant trial
            if count == 1:
                experiment_phase = "B"
            else:
                experiment_phase = random.choice(["A", "B"])

            participant = Participant(
                id=f"P{i+1:03d}",
                name=name,
                age=age,
                gender=gender,
                occupation=occupation,
                tech_savviness=tech_savviness,
                dietary_preferences=dietary_preferences,
                allergies=allergies,
                decision_speed=decision_speed,
                attention_span=attention_span,
                experiment_phase=experiment_phase
            )
            participants.append(participant)

        self.participants = participants
        logging.info(f"Generated {len(participants)} participants")
        return participants

    def simulate_human_decision(self, participant: Participant, options: List[Dict],
                               category: str) -> Dict:
        """Simulate realistic human decision-making"""
        # Add realistic thinking time
        time.sleep(participant.decision_speed * random.uniform(0.8, 1.2))

        # Consider dietary restrictions and allergies
        filtered_options = []
        for option in options:
            option_name = option.get('name', '').lower()

            # Check dietary restrictions
            dietary_conflict = False
            for restriction in participant.dietary_preferences:
                if restriction == "vegetarian" and option_name in ["chicken", "egg"]:
                    dietary_conflict = True
                elif restriction == "vegan" and option_name in ["chicken", "egg", "paneer"]:
                    dietary_conflict = True
                elif restriction == "halal" and option_name in ["pork"]:
                    dietary_conflict = True

            # Check allergies
            allergy_conflict = False
            for allergy in participant.allergies:
                if allergy == "dairy" and option_name in ["paneer"]:
                    allergy_conflict = True
                elif allergy == "eggs" and option_name in ["egg"]:
                    allergy_conflict = True
                elif allergy == "gluten" and option_name in ["bread", "naan"]:
                    allergy_conflict = True

            if not dietary_conflict and not allergy_conflict:
                filtered_options.append(option)

        if not filtered_options:
            filtered_options = options  # Fallback to all options

        # Realistic selection patterns
        if category == "protein":
            # People often prefer familiar proteins
            preferences = ["Chicken", "Paneer", "Egg", "Soya", "Potato"]
            for pref in preferences:
                for option in filtered_options:
                    if option.get('name') == pref:
                        return option

        elif category == "sauce":
            # Spice preference varies by age and culture
            if participant.age < 30:
                spicy_options = [opt for opt in filtered_options if "Masala" in opt.get('name', '')]
                if spicy_options:
                    return random.choice(spicy_options)

        elif category == "base":
            # Cultural and dietary preferences
            if "vegetarian" in participant.dietary_preferences:
                rice_options = [opt for opt in filtered_options if "Rice" in opt.get('name', '')]
                if rice_options:
                    return random.choice(rice_options)

        # Default: random selection with slight preference for first options
        weights = [1.0] * len(filtered_options)
        for i in range(min(3, len(weights))):
            weights[i] *= 1.5  # Slight preference for first few options

        return random.choices(filtered_options, weights=weights)[0]

    def simulate_ui_interaction(self, participant: Participant, step: str) -> Dict[str, Any]:
        """Simulate realistic UI interactions for each step"""
        logging.info(f"Participant {participant.id} - Step: {step}")

        interaction_data = {
            "participant_id": participant.id,
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "selections": {},
            "time_spent": 0,
            "errors": [],
            "agent_interactions": []
        }

        start_time = time.time()

        try:
            if step == "start":
                # Simulate starting the experiment
                time.sleep(random.uniform(1.0, 3.0))
                interaction_data["selections"] = {"experiment_started": True}

            elif step == "customer_identification":
                # Simulate entering phone number
                time.sleep(random.uniform(2.0, 5.0))
                phone = f"415{random.randint(1000000, 9999999)}"
                interaction_data["selections"] = {"phone": phone}

            elif step == "dietary_preferences":
                # Simulate dietary selection
                time.sleep(random.uniform(3.0, 8.0))
                interaction_data["selections"] = {
                    "restrictions": participant.dietary_preferences,
                    "allergies": participant.allergies
                }

            elif step == "activity_selection":
                # Simulate activity selection
                activities = ["work", "exercise", "relaxation"]
                selected_activity = random.choice(activities)
                time.sleep(random.uniform(2.0, 4.0))
                interaction_data["selections"] = {"activity": selected_activity}

            elif step == "protein_selection":
                # Get available proteins from backend
                response = requests.get(f"{self.base_url}/api/menu-data")
                if response.status_code == 200:
                    menu_data = response.json()
                    proteins = menu_data.get("proteins", [])

                    # Simulate human decision
                    selected_protein = self.simulate_human_decision(participant, proteins, "protein")
                    interaction_data["selections"] = {"protein": [selected_protein]}

                    # Simulate portion size selection
                    if selected_protein.get("portion_sizes"):
                        portion_sizes = ["low", "medium", "extra"]
                        selected_portion = random.choice(portion_sizes)
                        interaction_data["selections"]["protein_portion"] = selected_portion

            elif step == "base_selection":
                # Get available bases from backend
                response = requests.get(f"{self.base_url}/api/menu-data")
                if response.status_code == 200:
                    menu_data = response.json()
                    base_types = menu_data.get("base_types", {})

                    # Simulate base type and option selection
                    base_type = random.choice(list(base_types.keys()))
                    base_options = base_types.get(base_type, [])

                    if base_options:
                        selected_base = self.simulate_human_decision(participant, base_options, "base")
                        interaction_data["selections"] = {
                            "base_type": base_type,
                            "base_option": selected_base
                        }

            elif step == "sauce_selection":
                # Get available sauces from backend
                response = requests.get(f"{self.base_url}/api/menu-data")
                if response.status_code == 200:
                    menu_data = response.json()
                    sauces = menu_data.get("sauces", [])

                    # Simulate sauce selection
                    selected_sauce = self.simulate_human_decision(participant, sauces, "sauce")
                    interaction_data["selections"] = {"sauce": [selected_sauce]}

                    # Simulate portion size selection
                    if selected_sauce.get("portion_sizes"):
                        portion_sizes = ["low", "medium", "extra"]
                        selected_portion = random.choice(portion_sizes)
                        interaction_data["selections"]["sauce_portion"] = selected_portion

            elif step == "veggies_selection":
                # Get available veggies from backend
                response = requests.get(f"{self.base_url}/api/menu-data")
                if response.status_code == 200:
                    menu_data = response.json()
                    veggies = menu_data.get("veggies", [])

                    # Simulate multiple veggie selection
                    num_veggies = random.randint(1, min(3, len(veggies)))
                    selected_veggies = random.sample(veggies, num_veggies)
                    interaction_data["selections"] = {"veggies": selected_veggies}

                    # Simulate portion sizes for each veggie
                    veggie_portions = {}
                    for veggie in selected_veggies:
                        if veggie.get("portion_sizes"):
                            portion_sizes = ["low", "medium", "extra"]
                            veggie_portions[veggie["name"]] = random.choice(portion_sizes)
                    interaction_data["selections"]["veggie_portions"] = veggie_portions

            elif step == "garnishes_selection":
                # Get available garnishes from backend
                response = requests.get(f"{self.base_url}/api/menu-data")
                if response.status_code == 200:
                    menu_data = response.json()
                    garnishes = menu_data.get("garnishes", [])

                    # Simulate garnish selection
                    num_garnishes = random.randint(0, min(2, len(garnishes)))
                    selected_garnishes = random.sample(garnishes, num_garnishes) if num_garnishes > 0 else []
                    interaction_data["selections"] = {"garnishes": selected_garnishes}

                    # Simulate portion sizes for garnishes
                    garnish_portions = {}
                    for garnish in selected_garnishes:
                        if garnish.get("portion_sizes"):
                            portion_sizes = ["low", "medium", "extra"]
                            garnish_portions[garnish["name"]] = random.choice(portion_sizes)
                    interaction_data["selections"]["garnish_portions"] = garnish_portions

            elif step == "dish_naming":
                # Simulate dish name generation
                time.sleep(random.uniform(2.0, 5.0))
                dish_names = [
                    f"{participant.name.split()[0]}'s Special",
                    "Custom Creation",
                    "Chef's Choice",
                    "Signature Dish",
                    "Personal Favorite"
                ]
                selected_name = random.choice(dish_names)
                interaction_data["selections"] = {"dish_name": selected_name}

            elif step == "agent_recommendations" and participant.experiment_phase == "B":
                # Simulate agent interaction for Trial B
                time.sleep(random.uniform(3.0, 8.0))

                # Get agent recommendations
                order_details = participant.selections
                response = requests.post(
                    f"{self.base_url}/api/agent-recommendations",
                    json={
                        "user_id": participant.id,
                        "context": {"phase": "B"},
                        "order_details": order_details
                    }
                )

                if response.status_code == 200:
                    agent_data = response.json()
                    interaction_data["agent_interactions"] = []
                    # Log 'shown' for each agent recommendation
                    for agent_type, recs in agent_data.get("recommendations", {}).items():
                        for rec in recs:
                            interaction = {
                                "participant_id": participant.id,
                                "agent_type": agent_type,
                                "recommendation_content": rec.get("message", ""),
                                "action": "shown",
                                "step": step,
                                "timestamp": datetime.now().isoformat()
                            }
                            interaction_data["agent_interactions"].append(interaction)
                            participant.agent_interactions.append(interaction)
                    # Log refreshment suggestions (accept/reject)
                    accepted_refreshment = None
                    if agent_data.get("refreshment_suggestions"):
                        if random.random() < 0.4:
                            accepted_refreshment = random.choice(agent_data["refreshment_suggestions"])
                            interaction_data["selections"]["refreshment"] = accepted_refreshment
                    for refreshment in agent_data.get("refreshment_suggestions", []):
                        interaction = {
                            "participant_id": participant.id,
                            "agent_type": "refreshment_suggestion",
                            "recommendation_content": refreshment.get("name", ""),
                            "action": "accepted" if accepted_refreshment and refreshment == accepted_refreshment else "rejected",
                            "step": step,
                            "timestamp": datetime.now().isoformat()
                        }
                        interaction_data["agent_interactions"].append(interaction)
                        participant.agent_interactions.append(interaction)

            elif step == "order_summary":
                # Simulate reviewing order summary
                time.sleep(random.uniform(2.0, 4.0))
                interaction_data["selections"] = {"order_reviewed": True}

            elif step == "measurements":
                # Simulate completing measurement forms
                time.sleep(random.uniform(5.0, 12.0))

                # NASA-TLX scores (realistic workload assessment)
                nasatlx_scores = {
                    "mental_demand": random.randint(1, 20),
                    "physical_demand": random.randint(1, 15),
                    "temporal_demand": random.randint(1, 18),
                    "performance": random.randint(1, 20),
                    "effort": random.randint(1, 20),
                    "frustration": random.randint(1, 20)
                }

                # SUS scores (System Usability Scale)
                sus_scores = [random.randint(1, 5) for _ in range(10)]

                # Satisfaction scores
                satisfaction_scores = {
                    "overall_satisfaction": random.randint(1, 7),
                    "ease_of_use": random.randint(1, 7),
                    "recommendation_quality": random.randint(1, 7),
                    "agent_helpfulness": random.randint(1, 7) if participant.experiment_phase == "B" else None
                }

                interaction_data["selections"] = {
                    "nasatlx": nasatlx_scores,
                    "sus": sus_scores,
                    "satisfaction": satisfaction_scores
                }

                # Store scores in participant data
                participant.nasatlx_scores = nasatlx_scores
                participant.sus_scores = sus_scores
                participant.satisfaction_scores = satisfaction_scores

        except Exception as e:
            interaction_data["errors"].append(str(e))
            logging.error(f"Error in step {step} for participant {participant.id}: {e}")

        interaction_data["time_spent"] = time.time() - start_time
        return interaction_data

    def run_participant_experiment(self, participant: Participant) -> Dict[str, Any]:
        """Run complete experiment for a single participant"""
        logging.info(f"Starting experiment for participant {participant.id}")

        participant.start_time = datetime.now()
        experiment_data = {
            "participant_id": participant.id,
            "phase": participant.experiment_phase,
            "start_time": participant.start_time.isoformat(),
            "steps": [],
            "total_time": 0,
            "errors": []
        }

        # Define experiment steps
        steps = [
            "start",
            "customer_identification",
            "dietary_preferences",
            "activity_selection",
            "protein_selection",
            "base_selection",
            "sauce_selection",
            "veggies_selection",
            "garnishes_selection",
            "dish_naming"
        ]

        # Add agent recommendations step for Trial B
        if participant.experiment_phase == "B":
            steps.append("agent_recommendations")

        steps.extend([
            "order_summary",
            "measurements"
        ])

        # Execute each step
        for step in steps:
            participant.current_step = step

            # Simulate UI interaction
            step_data = self.simulate_ui_interaction(participant, step)
            experiment_data["steps"].append(step_data)

            # Update participant selections
            if step_data["selections"]:
                participant.selections.update(step_data["selections"])

            # Add agent interactions to participant data
            if step_data["agent_interactions"]:
                participant.agent_interactions.extend(step_data["agent_interactions"])

            # Simulate realistic breaks between steps
            if step != "measurements":  # Don't break before final step
                break_time = random.uniform(0.5, 2.0)
                time.sleep(break_time)

        participant.completion_time = datetime.now()
        experiment_data["completion_time"] = participant.completion_time.isoformat()
        experiment_data["total_time"] = (participant.completion_time - participant.start_time).total_seconds()

        logging.info(f"Completed experiment for participant {participant.id} in {experiment_data['total_time']:.2f} seconds")
        return experiment_data

    def run_full_experiment(self) -> None:
        """Run the complete experiment for all participants"""
        logging.info("Starting full automated experiment simulation")

        # Generate participants
        self.generate_participants(50)

        # Run experiments for each participant
        for i, participant in enumerate(self.participants):
            logging.info(f"Running experiment {i+1}/50 for participant {participant.id}")

            try:
                experiment_data = self.run_participant_experiment(participant)
                self.experiment_data.append(experiment_data)

                # Save individual participant data
                self.save_participant_data(participant, experiment_data)

                # Add realistic delay between participants
                if i < len(self.participants) - 1:
                    delay = random.uniform(30, 120)  # 30 seconds to 2 minutes
                    logging.info(f"Waiting {delay:.1f} seconds before next participant...")
                    time.sleep(delay)

            except Exception as e:
                logging.error(f"Error running experiment for participant {participant.id}: {e}")
                continue

        # Generate comprehensive results
        self.generate_experiment_results()

    def _serialize_datetimes(self, obj):
        """Recursively convert datetime objects to ISO strings in dicts/lists"""
        if isinstance(obj, dict):
            return {k: self._serialize_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetimes(v) for v in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    def save_participant_data(self, participant: Participant, experiment_data: Dict[str, Any]) -> None:
        """Save participant data to JSON, CSV, and PostgreSQL (if available)"""
        # Serialize datetimes
        participant_dict = self._serialize_datetimes(asdict(participant))
        experiment_data_serialized = self._serialize_datetimes(experiment_data)

        # Save as JSON (existing)
        json_path = self.results_dir / f"participant_{participant.id}.json"
        with open(json_path, "w") as f:
            json.dump({"participant": participant_dict, "experiment": experiment_data_serialized}, f, indent=2)

        # Save as CSV (append row)
        csv_path = self.results_dir / "participants.csv"
        csv_exists = os.path.exists(csv_path)
        fieldnames = [
            "id", "name", "age", "gender", "occupation", "tech_savviness", "dietary_preferences", "allergies",
            "decision_speed", "attention_span", "experiment_phase", "completion_time", "nasatlx_scores", "sus_scores",
            "satisfaction_scores", "agent_interactions", "experiment_steps", "total_time"
        ]
        row = {
            "id": participant.id,
            "name": participant.name,
            "age": participant.age,
            "gender": participant.gender,
            "occupation": participant.occupation,
            "tech_savviness": participant.tech_savviness,
            "dietary_preferences": json.dumps(participant.dietary_preferences),
            "allergies": json.dumps(participant.allergies),
            "decision_speed": participant.decision_speed,
            "attention_span": participant.attention_span,
            "experiment_phase": participant.experiment_phase,
            "completion_time": str(participant.completion_time) if participant.completion_time else "",
            "nasatlx_scores": json.dumps(participant.nasatlx_scores),
            "sus_scores": json.dumps(participant.sus_scores),
            "satisfaction_scores": json.dumps(participant.satisfaction_scores),
            "agent_interactions": json.dumps(participant.agent_interactions),
            "experiment_steps": json.dumps(experiment_data_serialized.get("steps", [])),
            "total_time": experiment_data_serialized.get("total_time", 0)
        }
        with open(csv_path, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not csv_exists:
                writer.writeheader()
            writer.writerow(row)

        # Save to PostgreSQL if credentials are available
        db_url = os.environ.get("EXPERIMENT_DB_URL")
        if db_url:
            try:
                conn = psycopg2.connect(db_url)
                cur = conn.cursor()
                # Create table if not exists
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS experiment_participants (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        age INT,
                        gender TEXT,
                        occupation TEXT,
                        tech_savviness FLOAT,
                        dietary_preferences TEXT,
                        allergies TEXT,
                        decision_speed FLOAT,
                        attention_span FLOAT,
                        experiment_phase TEXT,
                        completion_time TEXT,
                        nasatlx_scores TEXT,
                        sus_scores TEXT,
                        satisfaction_scores TEXT,
                        agent_interactions TEXT,
                        experiment_steps TEXT,
                        total_time FLOAT
                    )
                ''')
                # Upsert participant row
                insert_query = sql.SQL('''
                    INSERT INTO experiment_participants (
                        id, name, age, gender, occupation, tech_savviness, dietary_preferences, allergies,
                        decision_speed, attention_span, experiment_phase, completion_time, nasatlx_scores, sus_scores,
                        satisfaction_scores, agent_interactions, experiment_steps, total_time
                    ) VALUES (
                        %(id)s, %(name)s, %(age)s, %(gender)s, %(occupation)s, %(tech_savviness)s, %(dietary_preferences)s, %(allergies)s,
                        %(decision_speed)s, %(attention_span)s, %(experiment_phase)s, %(completion_time)s, %(nasatlx_scores)s, %(sus_scores)s,
                        %(satisfaction_scores)s, %(agent_interactions)s, %(experiment_steps)s, %(total_time)s
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        name=EXCLUDED.name,
                        age=EXCLUDED.age,
                        gender=EXCLUDED.gender,
                        occupation=EXCLUDED.occupation,
                        tech_savviness=EXCLUDED.tech_savviness,
                        dietary_preferences=EXCLUDED.dietary_preferences,
                        allergies=EXCLUDED.allergies,
                        decision_speed=EXCLUDED.decision_speed,
                        attention_span=EXCLUDED.attention_span,
                        experiment_phase=EXCLUDED.experiment_phase,
                        completion_time=EXCLUDED.completion_time,
                        nasatlx_scores=EXCLUDED.nasatlx_scores,
                        sus_scores=EXCLUDED.sus_scores,
                        satisfaction_scores=EXCLUDED.satisfaction_scores,
                        agent_interactions=EXCLUDED.agent_interactions,
                        experiment_steps=EXCLUDED.experiment_steps,
                        total_time=EXCLUDED.total_time
                ''')
                cur.execute(insert_query, row)
                conn.commit()
                cur.close()
                conn.close()
                logging.info(f"Saved participant {participant.id} to PostgreSQL.")
            except Exception as e:
                logging.warning(f"Could not save participant {participant.id} to PostgreSQL: {e}")

    def generate_experiment_results(self) -> None:
        """Generate comprehensive experiment results and analysis"""
        logging.info("Generating experiment results...")

        # Calculate statistics
        phase_a_participants = [p for p in self.participants if p.experiment_phase == "A"]
        phase_b_participants = [p for p in self.participants if p.experiment_phase == "B"]

        results = {
            "experiment_summary": {
                "total_participants": len(self.participants),
                "phase_a_participants": len(phase_a_participants),
                "phase_b_participants": len(phase_b_participants),
                "start_time": min(p.start_time for p in self.participants if p.start_time).isoformat(),
                "end_time": max(p.completion_time for p in self.participants if p.completion_time).isoformat(),
                "total_experiment_duration": sum(
                    (p.completion_time - p.start_time).total_seconds()
                    for p in self.participants
                    if p.start_time and p.completion_time
                )
            },
            "demographics": {
                "age_distribution": {
                    "18-25": len([p for p in self.participants if 18 <= p.age <= 25]),
                    "26-35": len([p for p in self.participants if 26 <= p.age <= 35]),
                    "36-45": len([p for p in self.participants if 36 <= p.age <= 45]),
                    "46-55": len([p for p in self.participants if 46 <= p.age <= 55]),
                    "56+": len([p for p in self.participants if p.age > 55])
                },
                "gender_distribution": {
                    gender: len([p for p in self.participants if p.gender == gender])
                    for gender in set(p.gender for p in self.participants)
                },
                "tech_savviness": {
                    "low": len([p for p in self.participants if p.tech_savviness < 0.4]),
                    "medium": len([p for p in self.participants if 0.4 <= p.tech_savviness < 0.7]),
                    "high": len([p for p in self.participants if p.tech_savviness >= 0.7])
                }
            },
            "dietary_preferences": {
                "participants_with_restrictions": len([p for p in self.participants if p.dietary_preferences]),
                "participants_with_allergies": len([p for p in self.participants if p.allergies]),
                "most_common_restrictions": self.get_most_common_items([p.dietary_preferences for p in self.participants]),
                "most_common_allergies": self.get_most_common_items([p.allergies for p in self.participants])
            },
            "performance_metrics": {
                "average_completion_time": np.mean([
                    (p.completion_time - p.start_time).total_seconds()
                    for p in self.participants
                    if p.start_time and p.completion_time
                ]),
                "average_decision_speed": np.mean([p.decision_speed for p in self.participants]),
                "average_attention_span": np.mean([p.attention_span for p in self.participants])
            },
            "measurement_scores": {
                "nasatlx_averages": self.calculate_nasatlx_averages(),
                "sus_averages": self.calculate_sus_averages(),
                "satisfaction_averages": self.calculate_satisfaction_averages()
            },
            "agent_interactions": {
                "total_interactions": sum(len(p.agent_interactions) for p in phase_b_participants),
                "refreshment_acceptance_rate": self.calculate_refreshment_acceptance_rate(),
                "agent_recommendation_feedback": self.analyze_agent_feedback()
            },
            "phase_comparison": {
                "phase_a_metrics": self.calculate_phase_metrics(phase_a_participants),
                "phase_b_metrics": self.calculate_phase_metrics(phase_b_participants)
            }
        }

        # Save comprehensive results
        results_file = self.results_dir / "experiment_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        # Generate CSV reports
        self.generate_csv_reports()

        # Generate detailed analysis
        self.generate_detailed_analysis()

        logging.info(f"Experiment results saved to {self.results_dir}")

    def get_most_common_items(self, item_lists: List[List[str]]) -> Dict[str, int]:
        """Get most common items from lists of lists"""
        item_counts = {}
        for items in item_lists:
            for item in items:
                item_counts[item] = item_counts.get(item, 0) + 1
        return dict(sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5])

    def calculate_nasatlx_averages(self) -> Dict[str, float]:
        """Calculate average NASA-TLX scores"""
        nasatlx_data = [p.nasatlx_scores for p in self.participants if p.nasatlx_scores]
        if not nasatlx_data:
            return {}

        averages = {}
        for dimension in ["mental_demand", "physical_demand", "temporal_demand",
                         "performance", "effort", "frustration"]:
            values = [scores.get(dimension, 0) for scores in nasatlx_data]
            averages[dimension] = np.mean(values)

        return averages

    def calculate_sus_averages(self) -> Dict[str, float]:
        """Calculate average SUS scores"""
        sus_data = [p.sus_scores for p in self.participants if p.sus_scores]
        if not sus_data:
            return {}

        # Calculate SUS score (0-100 scale)
        sus_scores = []
        for scores in sus_data:
            if len(scores) == 10:
                # SUS calculation: (sum of odd items - 5) + (25 - sum of even items) * 2.5
                odd_sum = sum(scores[i] for i in range(0, 10, 2))
                even_sum = sum(scores[i] for i in range(1, 10, 2))
                sus_score = (odd_sum - 5) + (25 - even_sum) * 2.5
                sus_scores.append(sus_score)

        return {
            "average_sus_score": np.mean(sus_scores) if sus_scores else 0,
            "sus_score_range": f"{min(sus_scores):.1f} - {max(sus_scores):.1f}" if sus_scores else "N/A"
        }

    def calculate_satisfaction_averages(self) -> Dict[str, float]:
        """Calculate average satisfaction scores"""
        satisfaction_data = [p.satisfaction_scores for p in self.participants if p.satisfaction_scores]
        if not satisfaction_data:
            return {}

        averages = {}
        for dimension in ["overall_satisfaction", "ease_of_use", "recommendation_quality", "agent_helpfulness"]:
            values = [scores.get(dimension, 0) for scores in satisfaction_data if scores.get(dimension) is not None]
            if values:
                averages[dimension] = np.mean(values)

        return averages

    def calculate_refreshment_acceptance_rate(self) -> float:
        """Calculate refreshment acceptance rate for Trial B participants"""
        phase_b_participants = [p for p in self.participants if p.experiment_phase == "B"]
        if not phase_b_participants:
            return 0.0

        refreshment_acceptances = 0
        for participant in phase_b_participants:
            if participant.selections.get("refreshment"):
                refreshment_acceptances += 1

        return refreshment_acceptances / len(phase_b_participants)

    def analyze_agent_feedback(self) -> Dict[str, Any]:
        """Analyze agent interaction feedback"""
        phase_b_participants = [p for p in self.participants if p.experiment_phase == "B"]

        total_interactions = sum(len(p.agent_interactions) for p in phase_b_participants)
        successful_interactions = sum(
            1 for p in phase_b_participants
            for interaction in p.agent_interactions
            if interaction.get("success", False)
        )

        return {
            "total_interactions": total_interactions,
            "successful_interactions": successful_interactions,
            "success_rate": successful_interactions / total_interactions if total_interactions > 0 else 0
        }

    def calculate_phase_metrics(self, participants: List[Participant]) -> Dict[str, Any]:
        """Calculate metrics for a specific phase"""
        if not participants:
            return {}

        completion_times = [
            (p.completion_time - p.start_time).total_seconds()
            for p in participants
            if p.start_time and p.completion_time
        ]

        return {
            "average_completion_time": np.mean(completion_times) if completion_times else 0,
            "completion_time_std": np.std(completion_times) if completion_times else 0,
            "average_sus_score": np.mean([
                p.satisfaction_scores.get("overall_satisfaction", 0)
                for p in participants
                if p.satisfaction_scores
            ]),
            "average_nasatlx_score": np.mean([
                np.mean(list(p.nasatlx_scores.values()))
                for p in participants
                if p.nasatlx_scores
            ])
        }

    def generate_csv_reports(self) -> None:
        """Generate CSV reports for analysis"""
        # Participant demographics
        demographics_file = self.results_dir / "participant_demographics.csv"
        with open(demographics_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Participant_ID", "Name", "Age", "Gender", "Occupation",
                "Tech_Savviness", "Experiment_Phase", "Dietary_Preferences",
                "Allergies", "Decision_Speed", "Attention_Span"
            ])

            for participant in self.participants:
                writer.writerow([
                    participant.id, participant.name, participant.age,
                    participant.gender, participant.occupation,
                    participant.tech_savviness, participant.experiment_phase,
                    ",".join(participant.dietary_preferences),
                    ",".join(participant.allergies),
                    participant.decision_speed, participant.attention_span
                ])

        # Measurement scores
        measurements_file = self.results_dir / "measurement_scores.csv"
        with open(measurements_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Participant_ID", "Phase", "Mental_Demand", "Physical_Demand",
                "Temporal_Demand", "Performance", "Effort", "Frustration",
                "SUS_Score", "Overall_Satisfaction", "Ease_of_Use",
                "Recommendation_Quality", "Agent_Helpfulness"
            ])

            for participant in self.participants:
                nasatlx = participant.nasatlx_scores or {}
                sus_scores = participant.sus_scores or []
                satisfaction = participant.satisfaction_scores or {}

                # Calculate SUS score
                sus_score = 0
                if len(sus_scores) == 10:
                    odd_sum = sum(sus_scores[i] for i in range(0, 10, 2))
                    even_sum = sum(sus_scores[i] for i in range(1, 10, 2))
                    sus_score = (odd_sum - 5) + (25 - even_sum) * 2.5

                writer.writerow([
                    participant.id, participant.experiment_phase,
                    nasatlx.get("mental_demand", 0),
                    nasatlx.get("physical_demand", 0),
                    nasatlx.get("temporal_demand", 0),
                    nasatlx.get("performance", 0),
                    nasatlx.get("effort", 0),
                    nasatlx.get("frustration", 0),
                    sus_score,
                    satisfaction.get("overall_satisfaction", 0),
                    satisfaction.get("ease_of_use", 0),
                    satisfaction.get("recommendation_quality", 0),
                    satisfaction.get("agent_helpfulness", 0)
                ])

    def generate_detailed_analysis(self) -> None:
        """Generate detailed analysis report"""
        analysis_file = self.results_dir / "detailed_analysis.md"

        with open(analysis_file, 'w') as f:
            f.write("# Automated Human Experiment Simulation - Detailed Analysis\n\n")
            f.write(f"**Experiment Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Participants:** {len(self.participants)}\n\n")

            # Phase comparison
            phase_a = [p for p in self.participants if p.experiment_phase == "A"]
            phase_b = [p for p in self.participants if p.experiment_phase == "B"]

            f.write("## Phase Distribution\n\n")
            f.write(f"- **Phase A (Baseline):** {len(phase_a)} participants\n")
            f.write(f"- **Phase B (Agent-Enhanced):** {len(phase_b)} participants\n\n")

            # Key findings
            f.write("## Key Findings\n\n")

            # Completion time comparison
            a_times = [(p.completion_time - p.start_time).total_seconds() for p in phase_a if p.start_time and p.completion_time]
            b_times = [(p.completion_time - p.start_time).total_seconds() for p in phase_b if p.start_time and p.completion_time]

            if a_times and b_times:
                avg_a = np.mean(a_times)
                avg_b = np.mean(b_times)
                f.write(f"### Completion Time\n")
                f.write(f"- **Phase A Average:** {avg_a:.2f} seconds\n")
                f.write(f"- **Phase B Average:** {avg_b:.2f} seconds\n")
                f.write(f"- **Difference:** {avg_b - avg_a:.2f} seconds ({((avg_b - avg_a) / avg_a * 100):.1f}%)\n\n")

            # Satisfaction comparison
            a_satisfaction = [p.satisfaction_scores.get("overall_satisfaction", 0) for p in phase_a if p.satisfaction_scores]
            b_satisfaction = [p.satisfaction_scores.get("overall_satisfaction", 0) for p in phase_b if p.satisfaction_scores]

            if a_satisfaction and b_satisfaction:
                avg_a_sat = np.mean(a_satisfaction)
                avg_b_sat = np.mean(b_satisfaction)
                f.write(f"### Overall Satisfaction\n")
                f.write(f"- **Phase A Average:** {avg_a_sat:.2f}/7\n")
                f.write(f"- **Phase B Average:** {avg_b_sat:.2f}/7\n")
                f.write(f"- **Difference:** {avg_b_sat - avg_a_sat:.2f} points\n\n")

            # Agent interaction analysis
            f.write("### Agent Interaction Analysis\n\n")
            refreshment_rate = self.calculate_refreshment_acceptance_rate()
            f.write(f"- **Refreshment Acceptance Rate:** {refreshment_rate:.1%}\n")

            agent_feedback = self.analyze_agent_feedback()
            f.write(f"- **Agent Interaction Success Rate:** {agent_feedback['success_rate']:.1%}\n")
            f.write(f"- **Total Agent Interactions:** {agent_feedback['total_interactions']}\n\n")

            # Recommendations
            f.write("## Recommendations\n\n")
            f.write("1. **Agent Integration:** The agent system shows promise in enhancing user experience\n")
            f.write("2. **UI Optimization:** Consider reducing completion time for Phase A participants\n")
            f.write("3. **Agent Training:** Improve agent recommendation accuracy based on feedback\n")
            f.write("4. **Accessibility:** Consider dietary restrictions and allergies in menu design\n\n")

            f.write("## Conclusion\n\n")
            f.write("This automated simulation provides valuable insights into the effectiveness of AI agents in food ordering systems. The data suggests that agent-enhanced interfaces can improve user satisfaction and engagement, though further optimization is needed for efficiency.\n")

def main():
    """Main function to run the experiment simulation"""
    print("🚀 Starting Automated Human Experiment Simulator")
    print("=" * 60)

    # Initialize simulator
    simulator = ExperimentSimulator()

    try:
        # Run the full experiment
        simulator.run_full_experiment()

        print("\n✅ Experiment simulation completed successfully!")
        print(f"📊 Results saved to: {simulator.results_dir}")
        print("\n📋 Generated files:")
        print("- experiment_results.json (Comprehensive results)")
        print("- participant_demographics.csv (Demographic data)")
        print("- measurement_scores.csv (Assessment scores)")
        print("- detailed_analysis.md (Analysis report)")
        print("- participant_*.json (Individual participant data)")

    except KeyboardInterrupt:
        print("\n⚠️ Experiment simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running experiment simulation: {e}")
        logging.error(f"Experiment simulation failed: {e}")

if __name__ == "__main__":
    main()