#!/usr/bin/env python3
"""
Collaborative orchestrator for Swiss AI CLI agents
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import logging

from .base import BaseAgent, AgentContext, AgentResult, AgentType, CollaborationMessage

logger = logging.getLogger(__name__)

@dataclass
class CollaborationStats:
    """Statistics for collaboration tracking"""
    total_requests: int = 0
    successful_collaborations: int = 0
    failed_collaborations: int = 0
    avg_collaboration_time: float = 0.0
    agent_usage: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    collaboration_patterns: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    def update(self, result: AgentResult, selected_agent: AgentType):
        """Update stats with new result"""
        self.total_requests += 1
        self.agent_usage[selected_agent.value] += 1
        
        if result.success:
            self.successful_collaborations += 1
        else:
            self.failed_collaborations += 1
        
        # Update collaboration patterns
        if result.collaboration_requests:
            for collab in result.collaboration_requests:
                pattern = f"{selected_agent.value}->{collab.target_agent.value}"
                self.collaboration_patterns[pattern] += 1

class CollaborativeOrchestrator:
    """Orchestrates collaboration between agents"""
    
    def __init__(self, config_manager=None, model_selector=None, router=None):
        self.config_manager = config_manager
        self.model_selector = model_selector
        self.router = router
        
        # Agent registry
        self.agents: Dict[AgentType, BaseAgent] = {}
        
        # Collaboration tracking
        self.collaboration_stats = CollaborationStats()
        self.active_collaborations: Dict[str, Any] = {}
        
        logger.info("CollaborativeOrchestrator initialized")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_type] = agent
        logger.info(f"Registered agent: {agent.agent_type.value}")
    
    def unregister_agent(self, agent_type: AgentType):
        """Unregister an agent"""
        if agent_type in self.agents:
            del self.agents[agent_type]
            logger.info(f"Unregistered agent: {agent_type.value}")
    
    async def process_request(self, user_input: str, 
                            conversation_history: List[Dict] = None) -> str:
        """Process a user request through the collaborative system"""
        
        # Route the request to determine best agent
        if self.router:
            routing_decision = self.router.route_request(user_input)
            selected_agent_type = routing_decision.selected_agent
            
            # Display routing decision if configured
            if hasattr(self.router, 'display_routing_decision'):
                self.router.display_routing_decision(routing_decision)
        else:
            # Fallback to simple classification
            selected_agent_type = self._simple_classify(user_input)
        
        # Create agent context
        context = AgentContext(
            user_input=user_input,
            conversation_history=conversation_history or [],
            execution_trace=[f"user_request -> {selected_agent_type.value}_agent"]
        )
        
        # Add selected model to context if available from routing
        if self.router and hasattr(routing_decision, 'selected_model'):
            context.selected_model = routing_decision.selected_model
        
        # Process through selected agent
        start_time = time.time()
        
        try:
            if selected_agent_type in self.agents:
                result = await self.agents[selected_agent_type].process(context)
            else:
                # Fallback to general agent
                if AgentType.GENERAL in self.agents:
                    result = await self.agents[AgentType.GENERAL].process(context)
                else:
                    return "No suitable agent available to handle this request."
            
            result.execution_time = time.time() - start_time
            
            # Update collaboration stats
            self.collaboration_stats.update(result, selected_agent_type)
            
            # Handle collaboration requests
            if result.collaboration_requests:
                collaboration_results = await self._handle_collaborations(
                    result.collaboration_requests, context
                )
                
                # Combine results
                combined_response = result.response
                for collab_result in collaboration_results:
                    combined_response += f"\n\n[Collaborative Insight from {collab_result.agent_type.value.upper()}]\n{collab_result.response}"
                
                return combined_response
            
            return result.response
            
        except Exception as e:
            logger.error(f"Error in collaborative processing: {e}")
            return f"Error processing request: {e}"
    
    async def _handle_collaborations(self, collaborations: List[CollaborationMessage], 
                                   base_context: AgentContext) -> List[AgentResult]:
        """Handle collaboration requests"""
        results = []
        
        for collab in collaborations:
            if collab.target_agent not in self.agents:
                logger.warning(f"Target agent {collab.target_agent.value} not available")
                continue
            
            # Create collaboration context
            collab_context = AgentContext(
                user_input=collab.request,
                conversation_history=base_context.conversation_history,
                project_info=base_context.project_info,
                collaboration_depth=base_context.collaboration_depth + 1,
                max_collaboration_depth=base_context.max_collaboration_depth,
                collaboration_chain=base_context.collaboration_chain + [collab.target_agent],
                shared_context={**base_context.shared_context, **collab.context}
            )
            
            try:
                collab_result = await self.agents[collab.target_agent].process(collab_context)
                results.append(collab_result)
                
                logger.info(f"Collaboration with {collab.target_agent.value} completed")
                
            except Exception as e:
                logger.error(f"Collaboration with {collab.target_agent.value} failed: {e}")
        
        return results
    
    def _simple_classify(self, user_input: str) -> AgentType:
        """Simple fallback classification if no router available"""
        user_lower = user_input.lower()
        
        # Simple keyword-based classification
        if any(word in user_lower for word in ['code', 'debug', 'function', 'class', 'method']):
            return AgentType.CODE
        elif any(word in user_lower for word in ['analyze', 'research', 'explain', 'understand']):
            return AgentType.ANALYSIS
        elif any(word in user_lower for word in ['file', 'read', 'write', 'save', 'open']):
            return AgentType.FILE
        elif any(word in user_lower for word in ['git', 'commit', 'push', 'pull', 'branch']):
            return AgentType.GIT
        elif any(word in user_lower for word in ['remember', 'recall', 'history', 'previous']):
            return AgentType.MEMORY
        elif any(word in user_lower for word in ['think', 'consider', 'reflect', 'plan']):
            return AgentType.REFLECTION
        else:
            return AgentType.GENERAL
    
    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Get collaboration statistics"""
        total_requests = self.collaboration_stats.total_requests
        
        return {
            'total_requests': total_requests,
            'successful_requests': self.collaboration_stats.successful_collaborations,
            'failed_requests': self.collaboration_stats.failed_collaborations,
            'success_rate': (self.collaboration_stats.successful_collaborations / total_requests * 100) if total_requests > 0 else 0,
            'avg_processing_time': self.collaboration_stats.avg_collaboration_time,
            'agent_usage': dict(self.collaboration_stats.agent_usage),
            'collaboration_patterns': dict(self.collaboration_stats.collaboration_patterns),
            'active_agents': [agent_type.value for agent_type in self.agents.keys()],
            'total_agents': len(self.agents)
        }
    
    def get_agent_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all agents"""
        health = {}
        
        for agent_type, agent in self.agents.items():
            health[agent_type.value] = {
                'active': agent.is_active,
                'capabilities': agent.get_capabilities(),
                'type': agent_type.value
            }
        
        return health
    
    def set_agent_active(self, agent_type: AgentType, active: bool):
        """Set agent active state"""
        if agent_type in self.agents:
            self.agents[agent_type].set_active(active)
    
    def reset_stats(self):
        """Reset collaboration statistics"""
        self.collaboration_stats = CollaborationStats()
        logger.info("Collaboration statistics reset")
    
    def shutdown(self):
        """Shutdown orchestrator and all agents"""
        logger.info("Shutting down collaborative orchestrator")
        
        # Cleanup any active collaborations
        self.active_collaborations.clear()
        
        # Shutdown agents if they have cleanup methods
        for agent in self.agents.values():
            if hasattr(agent, 'shutdown'):
                try:
                    agent.shutdown()
                except Exception as e:
                    logger.warning(f"Error shutting down agent {agent.agent_type.value}: {e}")
        
        logger.info("Collaborative orchestrator shutdown complete")