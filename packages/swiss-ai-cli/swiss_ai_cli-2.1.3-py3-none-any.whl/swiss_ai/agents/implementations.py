#!/usr/bin/env python3
"""
Concrete agent implementations for Swiss AI CLI
"""

import asyncio
import logging
from typing import List, Dict, Any
from .base import BaseAgent, AgentResult, AgentContext, AgentType
from ..api.client import SwissAIAPIClient

logger = logging.getLogger(__name__)

class GeneralAgent(BaseAgent):
    """General purpose agent for handling basic queries"""
    
    def __init__(self, config_manager=None, api_client=None):
        super().__init__(AgentType.GENERAL, config_manager, api_client)
        self.capabilities = ["general_conversation", "basic_help", "information", "web_search"]
        self.api_client = api_client or SwissAIAPIClient(config_manager)
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Process general requests"""
        try:
            # Use the routing decision to get the selected model
            selected_model = getattr(context, 'selected_model', 'deepseek/deepseek-r1:free')
            
            # Create system prompt for general assistant
            system_prompt = """You are a helpful AI assistant that provides clear, accurate, and helpful responses. 
You can access real-time information when needed and should provide thoughtful, well-structured answers."""
            
            # Make API call
            api_response = await self.api_client.chat_with_model(
                user_input=context.user_input,
                model=selected_model,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=2048
            )
            
            if api_response.success:
                return self._create_success_result(
                    response=api_response.content,
                    execution_time=api_response.execution_time,
                    shared_data={
                        "agent_used": "general", 
                        "capabilities": self.capabilities,
                        "model_used": api_response.model_used,
                        "api_usage": api_response.usage
                    }
                )
            else:
                return self._create_error_result(
                    f"API call failed: {api_response.error}",
                    shared_data={"model_used": api_response.model_used}
                )
            
        except Exception as e:
            logger.error(f"GeneralAgent error: {e}")
            return self._create_error_result(str(e))

class CodeAgent(BaseAgent):
    """Agent specialized for code-related tasks"""
    
    def __init__(self, config_manager=None, api_client=None):
        super().__init__(AgentType.CODE, config_manager, api_client)
        self.capabilities = ["code_generation", "debugging", "code_review", "refactoring", "optimization"]
        self.api_client = api_client or SwissAIAPIClient(config_manager)
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Process code-related requests"""
        try:
            # Use coding-optimized model
            selected_model = getattr(context, 'selected_model', 'deepseek/deepseek-r1:free')
            
            # Create specialized system prompt for coding
            system_prompt = """You are an expert software engineer and coding assistant. You excel at:
- Writing clean, efficient, and well-documented code
- Debugging complex issues with detailed explanations
- Code review with best practices and security considerations
- Refactoring code for better maintainability and performance
- Explaining technical concepts clearly

Provide practical, working solutions with explanations."""
            
            # Make API call
            api_response = await self.api_client.chat_with_model(
                user_input=context.user_input,
                model=selected_model,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=4096
            )
            
            if api_response.success:
                return self._create_success_result(
                    response=api_response.content,
                    execution_time=api_response.execution_time,
                    shared_data={
                        "agent_used": "code", 
                        "capabilities": self.capabilities,
                        "model_used": api_response.model_used,
                        "api_usage": api_response.usage
                    }
                )
            else:
                return self._create_error_result(
                    f"API call failed: {api_response.error}",
                    shared_data={"model_used": api_response.model_used}
                )
            
        except Exception as e:
            logger.error(f"CodeAgent error: {e}")
            return self._create_error_result(str(e))

class AnalysisAgent(BaseAgent):
    """Agent specialized for analysis tasks"""
    
    def __init__(self, config_manager=None, api_client=None):
        super().__init__(AgentType.ANALYSIS, config_manager, api_client)
        self.capabilities = ["project_analysis", "code_analysis", "architecture_review", "research", "web_search"]
        self.api_client = api_client or SwissAIAPIClient(config_manager)
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Process analysis requests"""
        try:
            # Use analysis-optimized model
            selected_model = getattr(context, 'selected_model', 'deepseek/deepseek-r1:free')
            
            # Create specialized system prompt for analysis
            system_prompt = """You are an expert analyst and researcher. You excel at:
- Comprehensive project and code analysis
- Architecture assessment and recommendations  
- Research synthesis from multiple sources
- Identifying patterns, trends, and insights
- Strategic thinking and problem decomposition

Provide thorough, well-structured analysis with actionable insights."""
            
            # Regular analysis (web search temporarily disabled)
            api_response = await self.api_client.chat_with_model(
                user_input=context.user_input,
                model=selected_model,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=3072
            )
            
            if api_response.success:
                return self._create_success_result(
                    response=api_response.content,
                    execution_time=api_response.execution_time,
                    shared_data={
                        "agent_used": "analysis", 
                        "capabilities": self.capabilities,
                        "model_used": api_response.model_used,
                        "api_usage": api_response.usage
                    }
                )
            else:
                return self._create_error_result(
                    f"API call failed: {api_response.error}",
                    shared_data={"model_used": api_response.model_used}
                )
            
        except Exception as e:
            logger.error(f"AnalysisAgent error: {e}")
            return self._create_error_result(str(e))

class FileAgent(BaseAgent):
    """Agent specialized for file operations"""
    
    def __init__(self, config_manager=None, api_client=None):
        super().__init__(AgentType.FILE, config_manager, api_client)
        self.capabilities = ["file_read", "file_write", "file_analysis"]
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Process file-related requests"""
        try:
            response = f"File Agent activated for: '{context.user_input}'. Ready to handle file operations and analysis."
            
            return self._create_success_result(
                response=response,
                execution_time=0.1,
                shared_data={"agent_used": "file", "capabilities": self.capabilities}
            )
            
        except Exception as e:
            logger.error(f"FileAgent error: {e}")
            return self._create_error_result(str(e))

class GitAgent(BaseAgent):
    """Agent specialized for Git operations"""
    
    def __init__(self, config_manager=None, api_client=None):
        super().__init__(AgentType.GIT, config_manager, api_client)
        self.capabilities = ["git_status", "commit_analysis", "branch_management"]
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Process Git-related requests"""
        try:
            response = f"Git Agent activated for: '{context.user_input}'. Ready to help with version control operations."
            
            return self._create_success_result(
                response=response,
                execution_time=0.1,
                shared_data={"agent_used": "git", "capabilities": self.capabilities}
            )
            
        except Exception as e:
            logger.error(f"GitAgent error: {e}")
            return self._create_error_result(str(e))

class ReflectionAgent(BaseAgent):
    """Agent specialized for strategic thinking and planning"""
    
    def __init__(self, config_manager=None, api_client=None):
        super().__init__(AgentType.REFLECTION, config_manager, api_client)
        self.capabilities = ["strategic_planning", "decision_making", "problem_decomposition"]
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Process reflection and planning requests"""
        try:
            response = f"Reflection Agent activated for: '{context.user_input}'. Ready to help with strategic thinking and planning."
            
            return self._create_success_result(
                response=response,
                execution_time=0.1,
                shared_data={"agent_used": "reflection", "capabilities": self.capabilities}
            )
            
        except Exception as e:
            logger.error(f"ReflectionAgent error: {e}")
            return self._create_error_result(str(e))

class MemoryAgent(BaseAgent):
    """Agent specialized for memory and context management"""
    
    def __init__(self, config_manager=None, api_client=None):
        super().__init__(AgentType.MEMORY, config_manager, api_client)
        self.capabilities = ["context_management", "memory_storage", "history_analysis"]
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Process memory and context requests"""
        try:
            response = f"Memory Agent activated for: '{context.user_input}'. Ready to manage context and conversation history."
            
            return self._create_success_result(
                response=response,
                execution_time=0.1,
                shared_data={"agent_used": "memory", "capabilities": self.capabilities}
            )
            
        except Exception as e:
            logger.error(f"MemoryAgent error: {e}")
            return self._create_error_result(str(e))

def create_all_agents(config_manager=None, api_client=None) -> List[BaseAgent]:
    """Factory function to create all available agents"""
    # Create shared API client if not provided
    if api_client is None:
        from ..api.client import SwissAIAPIClient
        api_client = SwissAIAPIClient(config_manager)
    
    return [
        GeneralAgent(config_manager, api_client),
        CodeAgent(config_manager, api_client),
        AnalysisAgent(config_manager, api_client),
        FileAgent(config_manager, api_client),
        GitAgent(config_manager, api_client),
        ReflectionAgent(config_manager, api_client),
        MemoryAgent(config_manager, api_client),
    ]