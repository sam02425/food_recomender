from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, SkipValidation
from datetime import datetime
import json
import random
from enum import Enum

class GameLevel(str, Enum):
    NOVICE = "Novice"
    EXPLORER = "Explorer"
    ADVENTURER = "Adventurer"
    MASTER = "Master"
    LEGEND = "Legend"

class Challenge(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    id: str
    title: str
    description: str
    points: int
    requirements: Dict[str, Union[float, int, bool, str]]
    completed: bool = False
    expires_at: Optional[datetime] = None

class Achievement(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    id: str
    title: str
    description: str
    icon: str
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None

class PlayerState(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    user_id: str
    level: GameLevel
    points: int
    streak_days: int
    current_challenges: List[Challenge]
    achievements: List[Achievement]
    adventure_mode: bool = False
    last_order_date: Optional[datetime] = None

class GameEngineAgent:
    def __init__(self):
        self.player_states: Dict[str, PlayerState] = {}
        self.challenge_templates = self._load_challenge_templates()
        self.achievement_templates = self._load_achievement_templates()

    def _load_challenge_templates(self) -> List[Dict]:
        return [
            {
                "id": "weather_master",
                "title": "Weather Master",
                "description": "Order dishes perfect for today's weather",
                "points": 25,
                "requirements": {"weather_match_score": 0.8}
            },
            {
                "id": "health_champion",
                "title": "Health Champion",
                "description": "Order healthy dishes for 3 days straight",
                "points": 50,
                "requirements": {"healthy_orders": 3}
            },
            {
                "id": "adventure_seeker",
                "title": "Adventure Seeker",
                "description": "Try 3 new exotic dishes",
                "points": 100,
                "requirements": {"new_dishes": 3}
            }
        ]

    def _load_achievement_templates(self) -> List[Dict]:
        return [
            {
                "id": "first_order",
                "title": "First Steps",
                "description": "Place your first order",
                "icon": "🎯"
            },
            {
                "id": "weather_wise",
                "title": "Weather Wise",
                "description": "Order 5 weather-perfect meals",
                "icon": "🌤️"
            },
            {
                "id": "streak_master",
                "title": "Streak Master",
                "description": "Maintain a 7-day ordering streak",
                "icon": "🔥"
            }
        ]

    def get_or_create_player_state(self, user_id: str) -> PlayerState:
        if user_id not in self.player_states:
            self.player_states[user_id] = PlayerState(
                user_id=user_id,
                level=GameLevel.NOVICE,
                points=0,
                streak_days=0,
                current_challenges=[],
                achievements=[]
            )
        return self.player_states[user_id]

    def update_points(self, user_id: str, points: int, reason: str) -> PlayerState:
        player = self.get_or_create_player_state(user_id)
        player.points += points
        self._check_level_up(player)
        return player

    def _check_level_up(self, player: PlayerState):
        level_thresholds = {
            GameLevel.NOVICE: 0,
            GameLevel.EXPLORER: 100,
            GameLevel.ADVENTURER: 500,
            GameLevel.MASTER: 1000,
            GameLevel.LEGEND: 2500
        }

        for level, threshold in level_thresholds.items():
            if player.points >= threshold:
                player.level = level

    def assign_challenges(self, user_id: str) -> List[Challenge]:
        player = self.get_or_create_player_state(user_id)
        available_challenges = [
            Challenge(**template)
            for template in self.challenge_templates
        ]
        player.current_challenges = random.sample(available_challenges, 3)
        return player.current_challenges

    def check_achievements(self, user_id: str, order_data: Dict) -> List[Achievement]:
        player = self.get_or_create_player_state(user_id)
        new_achievements = []

        # Check for achievements based on order_data
        for template in self.achievement_templates:
            achievement = next(
                (a for a in player.achievements if a.id == template["id"]),
                None
            )

            if not achievement:
                achievement = Achievement(**template)
                if self._check_achievement_conditions(achievement, order_data):
                    achievement.unlocked = True
                    achievement.unlocked_at = datetime.now()
                    player.achievements.append(achievement)
                    new_achievements.append(achievement)

        return new_achievements

    def _check_achievement_conditions(self, achievement: Achievement, order_data: Dict) -> bool:
        # Implement achievement condition checking logic
        # This is a placeholder - implement actual conditions based on order_data
        return False

    def calculate_order_points(self, order_data: Dict) -> int:
        base_points = 10
        bonus_points = 0

        # Add points based on order characteristics
        if order_data.get("weather_match_score", 0) > 0.8:
            bonus_points += 15

        if order_data.get("health_score", 0) > 0.7:
            bonus_points += 20

        if order_data.get("adventure_mode", False):
            bonus_points += 50

        return base_points + bonus_points

    def update_streak(self, user_id: str):
        player = self.get_or_create_player_state(user_id)
        current_time = datetime.now()

        if player.last_order_date:
            time_diff = current_time - player.last_order_date
            if time_diff.days == 1:  # Consecutive day
                player.streak_days += 1
            elif time_diff.days > 1:  # Streak broken
                player.streak_days = 1
        else:
            player.streak_days = 1

        player.last_order_date = current_time

        # Award streak bonus points
        if player.streak_days % 7 == 0:  # Weekly streak bonus
            self.update_points(user_id, 100, "Weekly Streak Bonus")

    def get_game_state(self, user_id: str) -> Dict:
        player = self.get_or_create_player_state(user_id)
        return {
            "level": player.level,
            "points": player.points,
            "streak_days": player.streak_days,
            "current_challenges": [c.dict() for c in player.current_challenges],
            "achievements": [a.dict() for a in player.achievements],
            "adventure_mode": player.adventure_mode
        }