# backend/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime

class AgentType(Enum):
    CONTEXT_INTELLIGENCE = "context_intelligence"
    PREFERENCE_LEARNING = "preference_learning"
    PREPARATION_TIME = "preparation_time"

@dataclass
class AgentResult:
    """Standardized result format for all agents"""
    agent_type: AgentType
    success: bool
    data: Dict[str, Any]
    confidence: float
    execution_time_ms: int
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserContext:
    """User context information for agents"""
    user_id: str
    session_id: str
    current_time: datetime
    location: Optional[Dict[str, Any]] = None
    device_info: Optional[Dict[str, Any]] = None
    order_history: Optional[List[Dict[str, Any]]] = None

class BaseAgent(ABC):
    """Base class for all recommendation agents"""

    def __init__(self, agent_type: AgentType, user_id: str):
        self.agent_type = agent_type
        self.user_id = user_id
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.is_active = True

    @abstractmethod
    async def process(self, context: UserContext, **kwargs) -> AgentResult:
        """Process user context and return recommendations"""
        pass

    @abstractmethod
    async def update_model(self, feedback: Dict[str, Any]) -> bool:
        """Update agent's internal model based on feedback"""
        pass

    async def get_health_status(self) -> Dict[str, Any]:
        """Return agent health and performance metrics"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id
        }

class AgentConfig:
    """Configuration settings for agents"""

    # Context Intelligence settings
    CONTEXT_CACHE_TTL_SECONDS = 300
    DELIVERY_RADIUS_KM = 15
    RESTAURANT_AVAILABILITY_CHECK_INTERVAL = 60

    # Preference Learning settings
    PREFERENCE_MIN_ORDERS_FOR_LEARNING = 3
    PREFERENCE_DECAY_FACTOR = 0.95
    RECOMMENDATION_COUNT = 5

    # Preparation Time settings
    PREPARATION_TIME_THRESHOLD = 0.7
    ORDER_VALIDATION_RULES = [
        "check_kitchen_capacity",
        "validate_order_complexity",
        "verify_ingredient_availability",
        "calculate_preparation_time"
    ]