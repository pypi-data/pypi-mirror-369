#!/usr/bin/env python3
"""
Intelligent Router for Swiss AI CLI
Combines task routing with model selection for optimal AI interactions
"""

import re
import time
import json
import logging
from enum import Enum
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.text import Text
from rich.align import Align

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Confidence levels for routing decisions"""
    HIGH = "high"      # 0.8 - 1.0
    MEDIUM = "medium"  # 0.6 - 0.8  
    LOW = "low"        # 0.4 - 0.6
    UNCERTAIN = "uncertain"  # 0.0 - 0.4

class AgentType(Enum):
    """Types of agents available for routing"""
    CODE = "code"
    ANALYSIS = "analysis"
    MEMORY = "memory"
    FILE = "file"
    GIT = "git"
    REFLECTION = "reflection"
    GENERAL = "general"

@dataclass
class RoutingDecision:
    """Enhanced routing decision with confidence and reasoning"""
    selected_agent: AgentType
    confidence_score: float
    reasoning: str
    confidence_level: ConfidenceLevel
    alternative_agents: List[Tuple[AgentType, float]] = field(default_factory=list)
    keyword_matches: Dict[str, List[str]] = field(default_factory=dict)
    context_indicators: List[str] = field(default_factory=list)
    selected_model: Optional[str] = None
    model_confidence: float = 0.0

class ContextPattern:
    """Pattern matching for context detection"""
    
    def __init__(self, pattern: str, indicators: List[str], weight: float = 1.0):
        self.pattern = pattern
        self.regex = re.compile(pattern, re.IGNORECASE)
        self.indicators = indicators
        self.weight = weight
    
    def match(self, text: str) -> Tuple[bool, float, List[str]]:
        """Check if pattern matches and return confidence adjustment"""
        matches = self.regex.findall(text)
        if matches:
            confidence_boost = len(matches) * self.weight * 0.1
            return True, min(confidence_boost, 0.3), self.indicators
        return False, 0.0, []

class LearningSystem:
    """Simple learning system to improve routing over time"""
    
    def __init__(self, config_path: str = "."):
        self.config_path = Path(config_path)
        self.learning_file = self.config_path / ".swiss-ai" / "routing_learning.json"
        self.learning_file.parent.mkdir(parents=True, exist_ok=True)
        self.feedback_data = self._load_feedback_data()
        self.successful_patterns = defaultdict(list)
        self.failed_patterns = defaultdict(list)
    
    def _load_feedback_data(self) -> Dict:
        """Load learning data from disk"""
        try:
            if self.learning_file.exists():
                with open(self.learning_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load learning data: {e}")
        return {
            'successful_patterns': {},
            'failed_patterns': {},
            'confidence_adjustments': {},
            'total_decisions': 0,
            'correct_decisions': 0
        }
    
    def record_feedback(self, user_input: str, decision: RoutingDecision, 
                       success: bool, user_satisfaction: Optional[int] = None):
        """Record feedback about a routing decision"""
        timestamp = datetime.now().isoformat()
        
        # Extract key phrases for learning
        key_phrases = self._extract_key_phrases(user_input)
        
        feedback_entry = {
            'timestamp': timestamp,
            'user_input': user_input[:100],  # Truncate for privacy
            'selected_agent': decision.selected_agent.value,
            'confidence_score': decision.confidence_score,
            'success': success,
            'user_satisfaction': user_satisfaction,
            'key_phrases': key_phrases
        }
        
        # Update learning data
        agent_key = decision.selected_agent.value
        if success:
            if agent_key not in self.feedback_data['successful_patterns']:
                self.feedback_data['successful_patterns'][agent_key] = []
            self.feedback_data['successful_patterns'][agent_key].append(feedback_entry)
            
            # Learn successful patterns
            for phrase in key_phrases:
                self.successful_patterns[agent_key].append(phrase)
        else:
            if agent_key not in self.feedback_data['failed_patterns']:
                self.feedback_data['failed_patterns'][agent_key] = []
            self.feedback_data['failed_patterns'][agent_key].append(feedback_entry)
            
            # Learn failed patterns
            for phrase in key_phrases:
                self.failed_patterns[agent_key].append(phrase)
        
        self.feedback_data['total_decisions'] += 1
        if success:
            self.feedback_data['correct_decisions'] += 1
        
        self._save_feedback_data()
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases for pattern learning"""
        # Simple n-gram extraction
        words = re.findall(r'\b\w+\b', text.lower())
        phrases = []
        
        # Add single words
        phrases.extend(words)
        
        # Add bigrams
        for i in range(len(words) - 1):
            phrases.append(f"{words[i]} {words[i+1]}")
        
        # Add trigrams for longer text
        if len(words) > 10:
            for i in range(len(words) - 2):
                phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        return phrases[:20]  # Limit to avoid explosion
    
    def get_confidence_adjustment(self, user_input: str, agent: AgentType) -> float:
        """Get confidence adjustment based on learned patterns"""
        key_phrases = self._extract_key_phrases(user_input)
        agent_key = agent.value
        
        successful_phrases = Counter(self.successful_patterns.get(agent_key, []))
        failed_phrases = Counter(self.failed_patterns.get(agent_key, []))
        
        boost = 0.0
        penalty = 0.0
        
        for phrase in key_phrases:
            # Boost for successful patterns
            if phrase in successful_phrases:
                boost += min(successful_phrases[phrase] * 0.02, 0.1)
            
            # Penalty for failed patterns
            if phrase in failed_phrases:
                penalty += min(failed_phrases[phrase] * 0.02, 0.1)
        
        return max(-0.2, min(0.2, boost - penalty))
    
    def _save_feedback_data(self):
        """Save learning data to disk"""
        try:
            with open(self.learning_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save learning data: {e}")
    
    def get_learning_stats(self) -> Dict:
        """Get learning system statistics"""
        total = self.feedback_data['total_decisions']
        correct = self.feedback_data['correct_decisions']
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            'total_decisions': total,
            'correct_decisions': correct,
            'accuracy_rate': f"{accuracy:.1f}%",
            'learned_patterns': {
                agent: len(patterns) for agent, patterns in self.successful_patterns.items()
            }
        }

class IntelligentRouter:
    """Enhanced router that combines task routing with model selection"""
    
    def __init__(self, config_manager=None, model_selector=None):
        self.config_manager = config_manager
        self.model_selector = model_selector
        self.console = Console()
        self.learning_system = LearningSystem()
        
        # Enhanced keyword patterns with weights
        self.agent_patterns = {
            AgentType.CODE: {
                'primary_keywords': [
                    'debug', 'fix', 'error', 'bug', 'implement', 'create', 
                    'function', 'class', 'method', 'code', 'programming',
                    'algorithm', 'optimization', 'refactor'
                ],
                'secondary_keywords': [
                    'write', 'build', 'develop', 'technical', 'syntax',
                    'variable', 'loop', 'condition', 'api', 'library'
                ],
                'context_patterns': [
                    ContextPattern(r'```[\w]*\n.*?\n```', ['code_block'], 0.3),
                    ContextPattern(r'\b\w+\.\w+\(\)', ['method_call'], 0.2),
                    ContextPattern(r'\bclass\s+\w+', ['class_definition'], 0.2),
                    ContextPattern(r'\bdef\s+\w+', ['function_definition'], 0.2),
                ]
            },
            AgentType.ANALYSIS: {
                'primary_keywords': [
                    'analyze', 'research', 'explain', 'understand', 'review',
                    'examine', 'investigate', 'study', 'compare', 'evaluate'
                ],
                'secondary_keywords': [
                    'overview', 'summary', 'report', 'insights', 'patterns',
                    'trends', 'structure', 'architecture', 'design'
                ],
                'context_patterns': [
                    ContextPattern(r'\b(what|why|how|when|where)\b', ['question_words'], 0.2),
                    ContextPattern(r'\b(architecture|design|pattern)\b', ['design_concepts'], 0.2),
                ]
            },
            AgentType.MEMORY: {
                'primary_keywords': [
                    'remember', 'save', 'store', 'recall', 'history',
                    'previous', 'context', 'session', 'conversation'
                ],
                'secondary_keywords': [
                    'before', 'earlier', 'past', 'logged', 'recorded'
                ],
                'context_patterns': []
            },
            AgentType.FILE: {
                'primary_keywords': [
                    'file', 'read', 'write', 'open', 'save', 'edit',
                    'modify', 'create', 'delete', 'directory', 'folder'
                ],
                'secondary_keywords': [
                    'path', 'filename', 'extension', 'content', 'text'
                ],
                'context_patterns': [
                    ContextPattern(r'\b[\w/\\]+\.\w{2,4}\b', ['file_path'], 0.3),
                    ContextPattern(r'\b[A-Z]:\\', ['windows_path'], 0.2),
                    ContextPattern(r'\b/[\w/]+', ['unix_path'], 0.2),
                ]
            },
            AgentType.GIT: {
                'primary_keywords': [
                    'git', 'commit', 'push', 'pull', 'branch', 'merge',
                    'clone', 'repository', 'version', 'control'
                ],
                'secondary_keywords': [
                    'github', 'gitlab', 'diff', 'log', 'status', 'add'
                ],
                'context_patterns': [
                    ContextPattern(r'\bgit\s+\w+', ['git_command'], 0.3),
                ]
            },
            AgentType.REFLECTION: {
                'primary_keywords': [
                    'think', 'consider', 'reflect', 'ponder', 'evaluate',
                    'assess', 'judge', 'opinion', 'perspective'
                ],
                'secondary_keywords': [
                    'thoughts', 'ideas', 'approach', 'strategy', 'plan'
                ],
                'context_patterns': []
            },
            AgentType.GENERAL: {
                'primary_keywords': [
                    'help', 'question', 'general', 'misc', 'other',
                    'chat', 'talk', 'discuss'
                ],
                'secondary_keywords': [],
                'context_patterns': []
            }
        }
    
    def route_request(self, user_input: str) -> RoutingDecision:
        """Main routing method that combines agent and model selection"""
        
        # Get agent routing decision
        agent_decision = self.classify_with_confidence(user_input)
        
        # Get model selection if model_selector is available
        if self.model_selector:
            from ..models.selector import TaskType
            
            # Map agent type to task type
            task_type_mapping = {
                AgentType.CODE: TaskType.CODING,
                AgentType.ANALYSIS: TaskType.ANALYSIS,
                AgentType.FILE: TaskType.GENERAL,
                AgentType.GIT: TaskType.GENERAL,
                AgentType.MEMORY: TaskType.GENERAL,
                AgentType.REFLECTION: TaskType.GENERAL,
                AgentType.GENERAL: TaskType.GENERAL
            }
            
            task_type = task_type_mapping.get(agent_decision.selected_agent, TaskType.GENERAL)
            selected_model, model_confidence = self.model_selector.select_model(
                task_type, user_input
            )
            
            agent_decision.selected_model = selected_model
            agent_decision.model_confidence = model_confidence
        
        return agent_decision
    
    def classify_with_confidence(self, user_input: str) -> RoutingDecision:
        """Enhanced classification with confidence scoring and reasoning"""
        
        # Calculate confidence scores for each agent
        agent_scores = {}
        keyword_matches = {}
        context_indicators = []
        
        for agent_type in AgentType:
            score, matches, indicators = self._calculate_agent_score(user_input, agent_type)
            agent_scores[agent_type] = score
            if matches:
                keyword_matches[agent_type.value] = matches
            context_indicators.extend(indicators)
        
        # Apply learning system adjustments
        for agent_type in agent_scores:
            adjustment = self.learning_system.get_confidence_adjustment(user_input, agent_type)
            agent_scores[agent_type] += adjustment
        
        # Sort agents by score
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        selected_agent, confidence_score = sorted_agents[0]
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            user_input, selected_agent, confidence_score, 
            keyword_matches.get(selected_agent.value, []), context_indicators
        )
        
        # Determine confidence level
        confidence_level = self._get_confidence_level(confidence_score)
        
        # Get alternative agents
        alternatives = [(agent, score) for agent, score in sorted_agents[1:4]]
        
        return RoutingDecision(
            selected_agent=selected_agent,
            confidence_score=confidence_score,
            reasoning=reasoning,
            confidence_level=confidence_level,
            alternative_agents=alternatives,
            keyword_matches=keyword_matches,
            context_indicators=context_indicators
        )
    
    def _calculate_agent_score(self, user_input: str, agent_type: AgentType) -> Tuple[float, List[str], List[str]]:
        """Calculate confidence score for a specific agent"""
        patterns = self.agent_patterns.get(agent_type, {})
        user_lower = user_input.lower()
        
        score = 0.0
        matched_keywords = []
        context_indicators = []
        
        # Primary keyword matching (higher weight)
        primary_keywords = patterns.get('primary_keywords', [])
        primary_matches = [kw for kw in primary_keywords if kw in user_lower]
        if primary_matches:
            score += min(len(primary_matches) * 0.15, 0.6)  # Cap at 0.6
            matched_keywords.extend(primary_matches)
        
        # Secondary keyword matching (lower weight)
        secondary_keywords = patterns.get('secondary_keywords', [])
        secondary_matches = [kw for kw in secondary_keywords if kw in user_lower]
        if secondary_matches:
            score += min(len(secondary_matches) * 0.1, 0.3)  # Cap at 0.3
            matched_keywords.extend(secondary_matches)
        
        # Context pattern matching
        context_patterns = patterns.get('context_patterns', [])
        for pattern in context_patterns:
            matches, confidence_boost, indicators = pattern.match(user_input)
            if matches:
                score += confidence_boost
                context_indicators.extend(indicators)
        
        # Length and complexity bonuses
        if len(user_input) > 100 and agent_type == AgentType.ANALYSIS:
            score += 0.1  # Complex analysis tasks
        
        if len(user_input.split()) > 20 and agent_type == AgentType.REFLECTION:
            score += 0.1  # Long form thinking tasks
        
        # Special case adjustments
        if not matched_keywords and agent_type == AgentType.GENERAL:
            score = 0.3  # Default fallback score
        
        return min(score, 1.0), matched_keywords, context_indicators
    
    def _generate_reasoning(self, user_input: str, selected_agent: AgentType, 
                          confidence_score: float, keywords: List[str], 
                          context_indicators: List[str]) -> str:
        """Generate human-readable reasoning for the routing decision"""
        reasoning_parts = []
        
        # Confidence level reasoning
        if confidence_score >= 0.8:
            reasoning_parts.append("Strong match")
        elif confidence_score >= 0.6:
            reasoning_parts.append("Good match")
        elif confidence_score >= 0.4:
            reasoning_parts.append("Moderate match")
        else:
            reasoning_parts.append("Weak match, using fallback")
        
        # Keyword reasoning
        if keywords:
            keyword_text = ", ".join(keywords[:3])
            if len(keywords) > 3:
                keyword_text += f" (+{len(keywords)-3} more)"
            reasoning_parts.append(f"detected keywords: {keyword_text}")
        
        # Context reasoning
        if context_indicators:
            context_text = ", ".join(set(context_indicators))
            reasoning_parts.append(f"found {context_text}")
        
        # Agent-specific reasoning
        agent_reasoning = {
            AgentType.CODE: "code-related task identified",
            AgentType.ANALYSIS: "analysis/research task identified", 
            AgentType.FILE: "file operation detected",
            AgentType.GIT: "git operation detected",
            AgentType.MEMORY: "memory/context operation detected",
            AgentType.REFLECTION: "reflective thinking task identified",
            AgentType.GENERAL: "general purpose handling"
        }
        
        if selected_agent in agent_reasoning:
            reasoning_parts.append(agent_reasoning[selected_agent])
        
        return "; ".join(reasoning_parts).capitalize()
    
    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """Convert numeric score to confidence level"""
        if score >= 0.8:
            return ConfidenceLevel.HIGH
        elif score >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNCERTAIN
    
    def display_routing_decision(self, decision: RoutingDecision, show_alternatives: bool = True):
        """Display routing decision with rich console output"""
        
        # Create confidence bar
        confidence_bar = self._create_confidence_bar(decision.confidence_score)
        
        # Color based on confidence level
        color_map = {
            ConfidenceLevel.HIGH: "bright_green",
            ConfidenceLevel.MEDIUM: "yellow", 
            ConfidenceLevel.LOW: "orange3",
            ConfidenceLevel.UNCERTAIN: "red"
        }
        
        color = color_map[decision.confidence_level]
        
        # Create main panel content
        content = f"""[bold cyan]Selected Agent:[/bold cyan] [bold {color}]{decision.selected_agent.value.upper()}[/bold {color}]
[bold cyan]Confidence:[/bold cyan] {confidence_bar} [bold]{decision.confidence_score:.0%}[/bold]
[bold cyan]Reasoning:[/bold cyan] {decision.reasoning}"""
        
        # Add model information if available
        if decision.selected_model:
            content += f"\n[bold cyan]Selected Model:[/bold cyan] {decision.selected_model}"
            content += f"\n[bold cyan]Model Confidence:[/bold cyan] {decision.model_confidence:.0%}"
        
        # Add alternatives if requested and confidence is not high
        if show_alternatives and decision.confidence_level != ConfidenceLevel.HIGH:
            if decision.alternative_agents:
                content += "\n\n[bold yellow]Alternatives:[/bold yellow]"
                for agent, score in decision.alternative_agents[:2]:
                    content += f"\n   • {agent.value.upper()} ({score:.0%})"
        
        # Create and display panel
        panel = Panel(
            content,
            title="🤖 Intelligent Routing",
            border_style=color,
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def _create_confidence_bar(self, confidence: float) -> str:
        """Create a visual confidence bar"""
        bar_length = 16
        filled = int(confidence * bar_length)
        empty = bar_length - filled
        
        if confidence >= 0.8:
            bar_color = "bright_green"
        elif confidence >= 0.6:
            bar_color = "yellow"
        elif confidence >= 0.4:
            bar_color = "orange3"
        else:
            bar_color = "red"
        
        return f"[{bar_color}]{'█' * filled}[/]{' ' * empty}"
    
    def display_learning_stats(self):
        """Display learning system statistics"""
        stats = self.learning_system.get_learning_stats()
        
        table = Table(title="🧠 Learning System Stats")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Decisions", str(stats['total_decisions']))
        table.add_row("Correct Decisions", str(stats['correct_decisions']))
        table.add_row("Accuracy Rate", stats['accuracy_rate'])
        
        # Add learned patterns
        for agent, pattern_count in stats['learned_patterns'].items():
            table.add_row(f"{agent.upper()} Patterns", str(pattern_count))
        
        self.console.print(table)
    
    def record_user_feedback(self, user_input: str, decision: RoutingDecision, 
                           success: bool, satisfaction: Optional[int] = None):
        """Record user feedback for learning"""
        self.learning_system.record_feedback(user_input, decision, success, satisfaction)
        
        # Also record model feedback if model_selector is available
        if self.model_selector and decision.selected_model:
            if success:
                self.model_selector.record_request_success(decision.selected_model, 1.0)
            else:
                self.model_selector.record_request_failure(decision.selected_model, "User reported failure")

# Convenience function for global access
_global_router: Optional[IntelligentRouter] = None

def get_intelligent_router() -> IntelligentRouter:
    """Get the global intelligent router instance"""
    global _global_router
    if _global_router is None:
        _global_router = IntelligentRouter()
    return _global_router