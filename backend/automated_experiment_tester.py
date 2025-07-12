#!/usr/bin/env python3
"""
AI-Powered Human Experiment Simulator
Uses 50 diverse AI personalities to interact with the actual UI like real humans
Supports both Groq and OpenAI APIs interchangeably with authentication
"""

import asyncio
import json
import random
import time
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, Page
from openai import OpenAI
from groq import Groq

# Add Gamini import if available
try:
    from gamini import Gamini
    GAMINI_AVAILABLE = True
except ImportError:
    GAMINI_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIKeyAuthenticator:
    """Authenticates and validates API keys before experiment starts"""

    def __init__(self):
        self.gamini_client = None
        self.groq_client = None
        self.openai_client = None
        self.active_api = None

    async def authenticate_gamini(self, api_key: str) -> bool:
        """Test Gamini API key with a simple request"""
        if not GAMINI_AVAILABLE:
            return False
        try:
            client = Gamini(api_key=api_key)
            response = client.chat.completions.create(
                model="gemini-pro",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            if response.choices and response.choices[0].message.content:
                self.gamini_client = client
                logger.info("✅ Gamini API authenticated successfully")
                return True
        except Exception as e:
            logger.error(f"❌ Gamini API authentication failed: {e}")
        return False

    async def authenticate_groq(self, api_key: str) -> bool:
        """Test Groq API key with a simple request"""
        try:
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            if response.choices and response.choices[0].message.content:
                self.groq_client = client
                logger.info("✅ Groq API authenticated successfully")
                return True
        except Exception as e:
            logger.error(f"❌ Groq API authentication failed: {e}")
        return False

    async def authenticate_openai(self, api_key: str) -> bool:
        """Test OpenAI API key with a simple request"""
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            if response.choices and response.choices[0].message.content:
                self.openai_client = client
                logger.info("✅ OpenAI API authenticated successfully")
                return True
        except Exception as e:
            logger.error(f"❌ OpenAI API authentication failed: {e}")
        return False

    async def authenticate_all_keys(self) -> bool:
        """Authenticate all available API keys, prefer Gamini > Groq > OpenAI"""
        gamini_key = os.getenv("GAMINI_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        llm_key = os.getenv("LLM_API_KEY")

        if not any([gamini_key, groq_key, openai_key, llm_key]):
            logger.error("❌ No API keys found in environment variables")
            return False

        # Prefer Gamini first
        if gamini_key and await self.authenticate_gamini(gamini_key):
            self.active_api = "gamini"
            return True
        # Try Groq next
        if groq_key and await self.authenticate_groq(groq_key):
            self.active_api = "groq"
            return True
        # Try OpenAI as fallback
        if openai_key and await self.authenticate_openai(openai_key):
            self.active_api = "openai"
            return True
        # Try LLM key as final fallback
        if llm_key and await self.authenticate_openai(llm_key):
            self.active_api = "openai"
            return True

        logger.error("❌ All API key authentication attempts failed")
        return False

    async def call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Call the authenticated LLM API with optimized prompt"""
        try:
            if self.active_api == "gamini":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                response = self.gamini_client.chat.completions.create(
                    model="gemini-pro",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                return response.choices[0].message.content.strip()
            elif self.active_api == "groq":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                response = self.groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                return response.choices[0].message.content.strip()
            else:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return "I need to proceed with the task."

# Global API authenticator
api_authenticator = APIKeyAuthenticator()

# Experiment Configuration
EXPERIMENT_CONFIG = {
    "total_participants": 50,
    "trials_per_participant": 10,  # 5 baseline + 5 agent-assisted
    "ui_url": "http://localhost:3000",
    "api_url": "http://localhost:8000",
    "headless": False,  # Set to True for faster execution
    "slow_mo": 100,  # Slow down actions to simulate human behavior
    "timeout": 30000,  # 30 seconds timeout
    "experiment_duration_minutes": 120  # 2 hours total
}

class HumanPersonality:
    """Represents a diverse human personality for AI agents"""

    def __init__(self, personality_id: int, name: str, background: Dict[str, Any]):
        self.personality_id = personality_id
        self.name = name
        self.background = background
        self.current_mood = background.get("baseline_mood", "neutral")
        self.cognitive_load = 0
        self.decision_style = background.get("decision_style", "balanced")
        self.tech_proficiency = background.get("tech_proficiency", "intermediate")
        self.ordering_habits = background.get("ordering_habits", {})
        self.personality_traits = background.get("personality_traits", {})

    def get_personality_prompt(self) -> str:
        """Generate optimized personality prompt for maximum AI efficiency"""
        return f"""You are {self.name}, {self.background['age']}yo {self.background['nationality']} from {self.background['country']}, working as {self.background['occupation']}. Tech level: {self.background['tech_proficiency']}. Decision style: {self.decision_style}. Mood: {self.current_mood}. Ordering: {self.background['ordering_frequency']}. Spice: {self.background.get('spice_tolerance', 'medium')}. Diet: {', '.join(self.background.get('dietary_preferences', []))}. Cultural food: {self.background.get('cultural_food_background', 'diverse')}. Meal: {self.background.get('meal_context', 'lunch')}. Time constraint: {self.background.get('time_constraint', 'moderate')}.

Act authentically as this person. Make decisions based on your background and preferences. React naturally to UI elements. Show appropriate emotions for difficult/easy tasks. Be consistent with your personality throughout the interaction."""

    def update_cognitive_load(self, task_difficulty: str, ui_complexity: str):
        """Update cognitive load based on task difficulty and UI complexity"""
        base_load = {"easy": 10, "medium": 25, "hard": 40, "very_hard": 60}
        complexity_multiplier = {"simple": 0.8, "moderate": 1.0, "complex": 1.3, "very_complex": 1.6}

        load = base_load.get(task_difficulty, 25) * complexity_multiplier.get(ui_complexity, 1.0)

        # Personality-specific modifiers
        if self.tech_proficiency == "beginner":
            load *= 1.2
        elif self.tech_proficiency == "expert":
            load *= 0.8

        if self.current_mood == "stressed":
            load *= 1.3
        elif self.current_mood == "relaxed":
            load *= 0.9

        self.cognitive_load = min(100, max(0, self.cognitive_load + load))
        return self.cognitive_load

    def get_nasa_tlx_scores(self) -> Dict[str, int]:
        """Generate NASA-TLX scores based on personality and cognitive load"""
        base_scores = {
            "mental_demand": 30, "physical_demand": 20, "temporal_demand": 25,
            "performance": 70, "effort": 40, "frustration": 25
        }

        # Adjust based on cognitive load
        if self.cognitive_load > 70:
            base_scores["mental_demand"] += 20
            base_scores["frustration"] += 15
            base_scores["effort"] += 10
        elif self.cognitive_load > 40:
            base_scores["mental_demand"] += 10
            base_scores["frustration"] += 8
        elif self.cognitive_load < 20:
            base_scores["mental_demand"] -= 10
            base_scores["frustration"] -= 8
            base_scores["performance"] += 10

        # Personality-specific adjustments
        if self.tech_proficiency == "beginner":
            base_scores["mental_demand"] += 15
            base_scores["frustration"] += 10
        elif self.tech_proficiency == "expert":
            base_scores["mental_demand"] -= 10
            base_scores["performance"] += 15

        if self.current_mood == "stressed":
            base_scores["temporal_demand"] += 15
            base_scores["frustration"] += 10
        elif self.current_mood == "relaxed":
            base_scores["temporal_demand"] -= 10
            base_scores["frustration"] -= 5

        # Ensure scores are within valid range (0-100)
        for key in base_scores:
            base_scores[key] = max(0, min(100, base_scores[key]))

        return base_scores

class AIParticipant:
    """AI-powered participant that interacts with the UI like a real human"""

    def __init__(self, personality: HumanPersonality, participant_id: str):
        self.personality = personality
        self.participant_id = participant_id
        self.browser = None
        self.page = None
        self.current_trial = 0
        self.trial_data = []
        self.start_time = None
        self.current_condition = None

    async def initialize_browser(self, headless: bool = False):
        """Initialize Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            slow_mo=EXPERIMENT_CONFIG["slow_mo"]
        )
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 720})

    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()

    async def navigate_to_app(self):
        """Navigate to the food ordering app"""
        try:
            await self.page.goto(EXPERIMENT_CONFIG["ui_url"])
            await self.page.wait_for_load_state("networkidle")
            logger.info(f"{self.personality.name} navigated to app")
            return True
        except Exception as e:
            logger.error(f"Navigation error for {self.personality.name}: {e}")
            return False

    async def register_participant(self):
        """Register as a participant"""
        try:
            # Look for registration form or start button
            start_button = await self.page.query_selector('button:has-text("Start")')
            if start_button:
                await start_button.click()
                await self.page.wait_for_timeout(1000)

            # Fill registration form if it exists
            name_input = await self.page.query_selector('input[placeholder*="name" i], input[name*="name" i]')
            if name_input:
                await name_input.fill(self.personality.name)

            email_input = await self.page.query_selector('input[type="email"], input[placeholder*="email" i]')
            if email_input:
                await name_input.fill(f"{self.personality.name.lower().replace(' ', '.')}@example.com")

            # Submit registration
            submit_button = await self.page.query_selector('button:has-text("Submit"), button:has-text("Register")')
            if submit_button:
                await submit_button.click()
                await self.page.wait_for_timeout(2000)

            logger.info(f"{self.personality.name} registered successfully")
            return True
        except Exception as e:
            logger.error(f"Registration error for {self.personality.name}: {e}")
            return False

    async def analyze_ui_state(self) -> Dict[str, Any]:
        """Analyze current UI state and available options"""
        try:
            # Get page content and structure
            page_content = await self.page.content()

            # Look for menu items, buttons, forms
            menu_items = await self.page.query_selector_all('.menu-item, .food-item, [data-testid*="menu"]')
            buttons = await self.page.query_selector_all('button')
            forms = await self.page.query_selector_all('form')

            # Extract text content
            visible_text = await self.page.evaluate("() => document.body.innerText")

            # Look for specific UI elements
            ui_state = {
                "current_page": await self.page.title(),
                "visible_elements": len(menu_items) + len(buttons) + len(forms),
                "menu_items_count": len(menu_items),
                "buttons_count": len(buttons),
                "forms_count": len(forms),
                "visible_text": visible_text[:500],  # First 500 chars
                "url": self.page.url
            }

            return ui_state
        except Exception as e:
            logger.error(f"UI analysis error: {e}")
            return {"error": str(e)}

    async def make_decision(self, context: str, options: List[str] = None) -> Dict[str, Any]:
        """Make a decision based on personality and current context - optimized prompt"""
        try:
            # Get current UI state
            ui_state = await self.analyze_ui_state()

            # Create optimized decision prompt
            decision_prompt = f"""Context: {context}
UI: Page={ui_state.get('current_page', 'Unknown')}, Elements={ui_state.get('visible_elements', 0)}, Text="{ui_state.get('visible_text', '')[:200]}"
Options: {options if options else 'Not specified'}

Based on your personality, what action would you take next? Respond with JSON only:
{{"action": "click|type|wait|scroll|select", "target": "element description", "reasoning": "brief reason", "confidence": 0-100}}"""

            system_prompt = self.personality.get_personality_prompt()

            response = await api_authenticator.call_llm(decision_prompt, system_prompt)

            # Try to parse JSON response
            try:
                decision = json.loads(response)
            except:
                # Fallback decision
                decision = {
                    "action": "click",
                    "target": "Continue or Next button",
                    "reasoning": "Proceeding with the flow",
                    "confidence": 70
                }

            return decision
        except Exception as e:
            logger.error(f"Decision making error: {e}")
            return {
                "action": "wait",
                "target": "page load",
                "reasoning": "Waiting for page to load",
                "confidence": 50
            }

    async def execute_action(self, decision: Dict[str, Any]) -> bool:
        """Execute the decided action on the UI"""
        try:
            action = decision.get("action", "wait")
            target = decision.get("target", "")

            if action == "click":
                # Try to find and click the target
                if "button" in target.lower():
                    button = await self.page.query_selector(f'button:has-text("{target}")')
                    if button:
                        await button.click()
                        await self.page.wait_for_timeout(1000)
                        return True

                # Try other selectors
                selectors = [
                    f'[data-testid*="{target.lower()}"]',
                    f'.{target.lower().replace(" ", "-")}',
                    f'#{target.lower().replace(" ", "-")}'
                ]

                for selector in selectors:
                    element = await self.page.query_selector(selector)
                    if element:
                        await element.click()
                        await self.page.wait_for_timeout(1000)
                        return True

            elif action == "type":
                # Find input field and type
                input_field = await self.page.query_selector('input, textarea')
                if input_field:
                    await input_field.fill(target)
                    await self.page.wait_for_timeout(500)
                    return True

            elif action == "select":
                # Handle dropdown or selection
                select_element = await self.page.query_selector('select, [role="combobox"]')
                if select_element:
                    await select_element.select_option(label=target)
                    await self.page.wait_for_timeout(500)
                    return True

            elif action == "wait":
                await self.page.wait_for_timeout(2000)
                return True

            elif action == "scroll":
                await self.page.evaluate("window.scrollBy(0, 300)")
                await self.page.wait_for_timeout(500)
                return True

            return False
        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return False

    async def complete_order_flow(self, condition: str) -> Dict[str, Any]:
        """Complete the full order flow for one trial"""
        trial_start = time.time()
        trial_data = {
            "participant_id": self.participant_id,
            "personality_name": self.personality.name,
            "condition": condition,
            "trial_start": datetime.now().isoformat(),
            "actions": [],
            "decisions": [],
            "ui_states": [],
            "errors": [],
            "cognitive_load_updates": []
        }

        try:
            # Navigate to app
            if not await self.navigate_to_app():
                raise Exception("Failed to navigate to app")

            # Register if needed
            await self.register_participant()

            # Main order flow
            step_count = 0
            max_steps = 20  # Prevent infinite loops

            while step_count < max_steps:
                step_count += 1

                # Analyze current state
                ui_state = await self.analyze_ui_state()
                trial_data["ui_states"].append(ui_state)

                # Check if we've completed the order
                if "complete" in ui_state.get("current_page", "").lower() or "thank" in ui_state.get("visible_text", "").lower():
                    logger.info(f"{self.personality.name} completed order flow")
                    break

                # Make decision
                context = f"Step {step_count}: {ui_state.get('current_page', 'Unknown page')}"
                decision = await self.make_decision(context)
                trial_data["decisions"].append(decision)

                # Execute action
                success = await self.execute_action(decision)
                trial_data["actions"].append({
                    "step": step_count,
                    "action": decision,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                })

                if not success:
                    trial_data["errors"].append(f"Failed to execute action at step {step_count}")

                # Update cognitive load
                task_difficulty = "medium" if step_count < 5 else "hard"
                ui_complexity = "moderate" if ui_state.get("visible_elements", 0) < 10 else "complex"
                cognitive_load = self.personality.update_cognitive_load(task_difficulty, ui_complexity)
                trial_data["cognitive_load_updates"].append({
                    "step": step_count,
                    "cognitive_load": cognitive_load,
                    "task_difficulty": task_difficulty,
                    "ui_complexity": ui_complexity
                })

                # Wait between actions
                await self.page.wait_for_timeout(random.randint(500, 2000))

            # Calculate trial metrics
            trial_duration = time.time() - trial_start
            trial_data["trial_duration"] = trial_duration
            trial_data["total_steps"] = step_count
            trial_data["success_rate"] = len([a for a in trial_data["actions"] if a["success"]]) / len(trial_data["actions"]) if trial_data["actions"] else 0
            trial_data["final_cognitive_load"] = self.personality.cognitive_load
            trial_data["nasa_tlx_scores"] = self.personality.get_nasa_tlx_scores()

            return trial_data

        except Exception as e:
            logger.error(f"Trial error for {self.personality.name}: {e}")
            trial_data["error"] = str(e)
            trial_data["trial_duration"] = time.time() - trial_start
            return trial_data

    async def run_experiment_trials(self) -> List[Dict[str, Any]]:
        """Run all trials for this participant"""
        all_trials = []

        # Run baseline trials (no agent assistance)
        for trial in range(5):
            logger.info(f"{self.personality.name} starting baseline trial {trial + 1}")
            trial_data = await self.complete_order_flow("baseline")
            trial_data["trial_number"] = trial + 1
            trial_data["trial_type"] = "baseline"
            all_trials.append(trial_data)

            # Reset cognitive load between trials
            self.personality.cognitive_load = 0

            # Wait between trials
            await asyncio.sleep(random.randint(2, 5))

        # Run agent-assisted trials
        for trial in range(5):
            logger.info(f"{self.personality.name} starting agent-assisted trial {trial + 1}")
            trial_data = await self.complete_order_flow("agent_assisted")
            trial_data["trial_number"] = trial + 6
            trial_data["trial_type"] = "agent_assisted"
            all_trials.append(trial_data)

            # Reset cognitive load between trials
            self.personality.cognitive_load = 0

            # Wait between trials
            await asyncio.sleep(random.randint(2, 5))

        return all_trials

class ExperimentOrchestrator:
    """Orchestrates the entire experiment with multiple AI participants"""

    def __init__(self):
        self.participants = []
        self.experiment_data = []
        self.personalities = self.create_diverse_personalities()

    def create_diverse_personalities(self) -> List[HumanPersonality]:
        """Create 50 diverse human personalities"""
        personalities = []

        # Define personality templates
        personality_templates = [
            # Indian Personalities (15)
            {
                "name": "Priya Patel", "age": 28, "nationality": "Indian", "country": "India",
                "occupation": "Software Engineer", "tech_proficiency": "expert",
                "ordering_frequency": "daily", "spice_tolerance": "high",
                "dietary_preferences": ["vegetarian"], "decision_style": "quick_decider",
                "cultural_food_background": "Indian", "family_cuisine": "Indian",
                "meal_context": "lunch", "time_constraint": "high",
                "personality_traits": {"extroverted": 0.7, "analytical": 0.8, "adventurous": 0.6}
            },
            {
                "name": "Rajesh Kumar", "age": 35, "nationality": "Indian", "country": "India",
                "occupation": "Business Analyst", "tech_proficiency": "intermediate",
                "ordering_frequency": "weekly", "spice_tolerance": "medium",
                "dietary_preferences": ["non-vegetarian"], "decision_style": "cautious_deliberate",
                "cultural_food_background": "Indian", "family_cuisine": "Indian",
                "meal_context": "dinner", "time_constraint": "moderate",
                "personality_traits": {"introverted": 0.6, "detail_oriented": 0.8, "traditional": 0.7}
            },
            {
                "name": "Anjali Sharma", "age": 24, "nationality": "Indian", "country": "India",
                "occupation": "Student", "tech_proficiency": "expert",
                "ordering_frequency": "daily", "spice_tolerance": "very_high",
                "dietary_preferences": ["vegan"], "decision_style": "impulsive",
                "cultural_food_background": "Indian", "family_cuisine": "Indian",
                "meal_context": "lunch", "time_constraint": "low",
                "personality_traits": {"extroverted": 0.8, "creative": 0.7, "health_conscious": 0.9}
            },

            # Bangladeshi Personalities (10)
            {
                "name": "Fatima Rahman", "age": 31, "nationality": "Bangladeshi", "country": "Bangladesh",
                "occupation": "Teacher", "tech_proficiency": "beginner",
                "ordering_frequency": "weekly", "spice_tolerance": "high",
                "dietary_preferences": ["halal"], "decision_style": "cautious_deliberate",
                "cultural_food_background": "Bangladeshi", "family_cuisine": "Bangladeshi",
                "meal_context": "dinner", "time_constraint": "moderate",
                "personality_traits": {"introverted": 0.7, "patient": 0.8, "traditional": 0.8}
            },
            {
                "name": "Ahmed Khan", "age": 27, "nationality": "Bangladeshi", "country": "Bangladesh",
                "occupation": "Doctor", "tech_proficiency": "intermediate",
                "ordering_frequency": "daily", "spice_tolerance": "medium",
                "dietary_preferences": ["halal"], "decision_style": "quick_decider",
                "cultural_food_background": "Bangladeshi", "family_cuisine": "Bangladeshi",
                "meal_context": "lunch", "time_constraint": "high",
                "personality_traits": {"extroverted": 0.6, "analytical": 0.9, "busy": 0.8}
            },

            # US Personalities (15)
            {
                "name": "Sarah Johnson", "age": 29, "nationality": "American", "country": "United States",
                "occupation": "Marketing Manager", "tech_proficiency": "expert",
                "ordering_frequency": "daily", "spice_tolerance": "low",
                "dietary_preferences": ["gluten_free"], "decision_style": "quick_decider",
                "cultural_food_background": "American", "family_cuisine": "American",
                "meal_context": "lunch", "time_constraint": "high",
                "personality_traits": {"extroverted": 0.8, "efficient": 0.9, "health_conscious": 0.7}
            },
            {
                "name": "Michael Chen", "age": 33, "nationality": "American", "country": "United States",
                "occupation": "Data Scientist", "tech_proficiency": "expert",
                "ordering_frequency": "weekly", "spice_tolerance": "medium",
                "dietary_preferences": ["vegetarian"], "decision_style": "analytical",
                "cultural_food_background": "Asian-American", "family_cuisine": "Mixed",
                "meal_context": "dinner", "time_constraint": "moderate",
                "personality_traits": {"introverted": 0.7, "analytical": 0.9, "curious": 0.8}
            },
            {
                "name": "Emily Rodriguez", "age": 26, "nationality": "American", "country": "United States",
                "occupation": "Nurse", "tech_proficiency": "intermediate",
                "ordering_frequency": "daily", "spice_tolerance": "high",
                "dietary_preferences": ["none"], "decision_style": "impulsive",
                "cultural_food_background": "Hispanic-American", "family_cuisine": "Mexican",
                "meal_context": "lunch", "time_constraint": "high",
                "personality_traits": {"extroverted": 0.8, "caring": 0.9, "adventurous": 0.7}
            },

            # African American Personalities (10)
            {
                "name": "Marcus Williams", "age": 30, "nationality": "African American", "country": "United States",
                "occupation": "Chef", "tech_proficiency": "intermediate",
                "ordering_frequency": "weekly", "spice_tolerance": "very_high",
                "dietary_preferences": ["none"], "decision_style": "adventurous",
                "cultural_food_background": "African American", "family_cuisine": "Soul Food",
                "meal_context": "dinner", "time_constraint": "low",
                "personality_traits": {"extroverted": 0.8, "creative": 0.9, "food_lover": 0.9}
            },
            {
                "name": "Aisha Thompson", "age": 25, "nationality": "African American", "country": "United States",
                "occupation": "Lawyer", "tech_proficiency": "expert",
                "ordering_frequency": "daily", "spice_tolerance": "medium",
                "dietary_preferences": ["vegan"], "decision_style": "cautious_deliberate",
                "cultural_food_background": "African American", "family_cuisine": "Mixed",
                "meal_context": "lunch", "time_constraint": "high",
                "personality_traits": {"introverted": 0.6, "analytical": 0.8, "principled": 0.9}
            }
        ]

        # Generate 50 unique personalities based on templates
        for i in range(50):
            template = personality_templates[i % len(personality_templates)]

            # Create variations
            personality_data = template.copy()
            personality_data["name"] = f"{template['name']} {i+1}" if i > 0 else template['name']
            personality_data["age"] = template["age"] + random.randint(-5, 5)
            personality_data["tech_proficiency"] = random.choice(["beginner", "intermediate", "expert"])
            personality_data["decision_style"] = random.choice(["quick_decider", "cautious_deliberate", "analytical", "impulsive", "adventurous"])
            personality_data["ordering_frequency"] = random.choice(["daily", "weekly", "monthly"])
            personality_data["spice_tolerance"] = random.choice(["low", "medium", "high", "very_high"])
            personality_data["meal_context"] = random.choice(["breakfast", "lunch", "dinner", "snack"])
            personality_data["time_constraint"] = random.choice(["low", "moderate", "high"])
            personality_data["current_mood"] = random.choice(["happy", "neutral", "stressed", "relaxed", "excited"])

            # Add personality variations
            personality_data["personality_traits"] = {
                "extroverted": random.uniform(0.3, 0.9),
                "analytical": random.uniform(0.4, 0.9),
                "adventurous": random.uniform(0.2, 0.8),
                "patient": random.uniform(0.3, 0.9),
                "efficient": random.uniform(0.4, 0.9),
                "health_conscious": random.uniform(0.2, 0.9)
            }

            personality = HumanPersonality(i+1, personality_data["name"], personality_data)
            personalities.append(personality)

        return personalities

    async def run_experiment(self):
        """Run the complete experiment with all participants"""
        logger.info(f"Starting experiment with {len(self.personalities)} AI participants")

        # Create participants
        for i, personality in enumerate(self.personalities):
            participant_id = f"P{i+1:03d}"
            participant = AIParticipant(personality, participant_id)
            self.participants.append(participant)

        # Run experiments in parallel (with concurrency limit)
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent participants

        async def run_participant(participant):
            async with semaphore:
                try:
                    await participant.initialize_browser(EXPERIMENT_CONFIG["headless"])
                    trials = await participant.run_experiment_trials()
                    self.experiment_data.extend(trials)
                    await participant.close_browser()
                    logger.info(f"Completed experiments for {participant.personality.name}")
                except Exception as e:
                    logger.error(f"Error with participant {participant.personality.name}: {e}")

        # Run all participants
        tasks = [run_participant(participant) for participant in self.participants]
        await asyncio.gather(*tasks)

        # Save results
        await self.save_experiment_results()

        logger.info("Experiment completed successfully!")

    async def save_experiment_results(self):
        """Save experiment results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results
        results_file = f"data/ai_experiment_results_{timestamp}.json"
        os.makedirs("data", exist_ok=True)

        with open(results_file, "w") as f:
            json.dump({
                "experiment_config": EXPERIMENT_CONFIG,
                "total_participants": len(self.participants),
                "total_trials": len(self.experiment_data),
                "results": self.experiment_data
            }, f, indent=2)

        # Save summary CSV
        csv_file = f"data/ai_experiment_summary_{timestamp}.csv"
        import csv

        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "participant_id", "personality_name", "trial_number", "trial_type",
                "trial_duration", "total_steps", "success_rate", "final_cognitive_load",
                "nasa_mental_demand", "nasa_physical_demand", "nasa_temporal_demand",
                "nasa_performance", "nasa_effort", "nasa_frustration"
            ])

            for trial in self.experiment_data:
                nasa_scores = trial.get("nasa_tlx_scores", {})
                writer.writerow([
                    trial["participant_id"],
                    trial["personality_name"],
                    trial["trial_number"],
                    trial["trial_type"],
                    trial["trial_duration"],
                    trial["total_steps"],
                    trial["success_rate"],
                    trial["final_cognitive_load"],
                    nasa_scores.get("mental_demand", 0),
                    nasa_scores.get("physical_demand", 0),
                    nasa_scores.get("temporal_demand", 0),
                    nasa_scores.get("performance", 0),
                    nasa_scores.get("effort", 0),
                    nasa_scores.get("frustration", 0)
                ])

        logger.info(f"Results saved to {results_file} and {csv_file}")

async def main():
    """Main function to run the experiment"""
    try:
        # Authenticate API keys first
        logger.info("🔑 Authenticating API keys...")
        if not await api_authenticator.authenticate_all_keys():
            logger.error("❌ API key authentication failed. Cannot start experiment.")
            return

        logger.info(f"✅ Using {api_authenticator.active_api.upper()} API")

        # Check if frontend is running
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(EXPERIMENT_CONFIG["ui_url"], timeout=5)
                if response.status_code != 200:
                    logger.error("❌ Frontend not accessible")
                    return
            except Exception as e:
                logger.error(f"❌ Frontend not running. Error: {e}")
                return

        # Check if backend is running (use a new client context)
        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"🔍 Checking backend at: {EXPERIMENT_CONFIG['api_url']}/health")
                response = await client.get(EXPERIMENT_CONFIG["api_url"] + "/health", timeout=5)
                logger.info(f"📡 Backend response status: {response.status_code}")
                if response.status_code != 200:
                    logger.error("❌ Backend not accessible")
                    return
                logger.info("✅ Backend is accessible")
            except Exception as e:
                logger.error(f"❌ Backend connectivity error: {e}")
                logger.error("❌ Backend not running. Please start the FastAPI backend first.")
                return

        logger.info("✅ All services are running. Starting experiment...")

        # Run experiment
        orchestrator = ExperimentOrchestrator()
        await orchestrator.run_experiment()

    except Exception as e:
        logger.error(f"❌ Experiment failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())