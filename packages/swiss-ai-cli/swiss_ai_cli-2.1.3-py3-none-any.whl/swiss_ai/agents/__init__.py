"""
Agent system for Swiss AI CLI
"""

from .base import BaseAgent, AgentResult, AgentContext, AgentType
from .collaborative import CollaborativeOrchestrator
from .implementations import (
    GeneralAgent, CodeAgent, AnalysisAgent, FileAgent, 
    GitAgent, ReflectionAgent, MemoryAgent, create_all_agents
)

__all__ = [
    "BaseAgent", "AgentResult", "AgentContext", "AgentType",
    "CollaborativeOrchestrator",
    "GeneralAgent", "CodeAgent", "AnalysisAgent", "FileAgent", 
    "GitAgent", "ReflectionAgent", "MemoryAgent", "create_all_agents"
]