#!/usr/bin/env python3
"""
Base agent classes for Swiss AI CLI
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of agents available"""
    CODE = "code"
    ANALYSIS = "analysis"
    MEMORY = "memory"
    FILE = "file"
    GIT = "git"
    REFLECTION = "reflection"
    GENERAL = "general"

@dataclass
class AgentContext:
    """Context passed to agents for processing"""
    user_input: str
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    project_info: Dict[str, Any] = field(default_factory=dict)
    memory_context: str = ""
    relevant_files: List[str] = field(default_factory=list)
    intent_keywords: List[str] = field(default_factory=list)
    execution_trace: List[str] = field(default_factory=list)
    collaboration_depth: int = 0
    max_collaboration_depth: int = 2
    collaboration_chain: List[AgentType] = field(default_factory=list)
    shared_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResult:
    """Result returned by agent processing"""
    agent_type: AgentType
    success: bool
    response: str
    actions_taken: List[str] = field(default_factory=list)
    confidence: float = 0.0
    suggested_next_agents: List[AgentType] = field(default_factory=list)
    collaboration_requests: List['CollaborationMessage'] = field(default_factory=list)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    error_details: Optional[str] = None

@dataclass
class CollaborationMessage:
    """Message for agent collaboration"""
    target_agent: AgentType
    request: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"  # low, normal, high
    expected_response_type: str = "analysis"  # analysis, action, data

class BaseAgent(ABC):
    """Base class for all Swiss AI agents"""
    
    def __init__(self, agent_type: AgentType, config_manager=None, api_client=None):
        self.agent_type = agent_type
        self.config_manager = config_manager
        self.api_client = api_client
        self.capabilities: List[str] = []
        self.is_active = True
        
    @abstractmethod
    async def process(self, context: AgentContext) -> AgentResult:
        """Process a request and return result"""
        pass
    
    def can_handle(self, context: AgentContext) -> bool:
        """Check if agent can handle the given context"""
        return self.is_active
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities.copy()
    
    def set_active(self, active: bool):
        """Set agent active state"""
        self.is_active = active
        logger.info(f"Agent {self.agent_type.value} {'activated' if active else 'deactivated'}")
    
    def _create_success_result(self, response: str, **kwargs) -> AgentResult:
        """Helper to create successful result"""
        return AgentResult(
            agent_type=self.agent_type,
            success=True,
            response=response,
            **kwargs
        )
    
    def _create_error_result(self, error: str, **kwargs) -> AgentResult:
        """Helper to create error result"""
        return AgentResult(
            agent_type=self.agent_type,
            success=False,
            response=f"Error: {error}",
            error_details=error,
            **kwargs
        )