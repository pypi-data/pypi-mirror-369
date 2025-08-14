#!/usr/bin/env python3
"""
Smart Model Selection System for Swiss AI CLI
Enhanced routing with intelligent fallback chains, caching, and task-specific preferences
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, NamedTuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import logging

# Rich for beautiful CLI output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
import sys

# Fix Windows console encoding issues
if sys.platform == "win32":
    console = Console(force_terminal=True, width=120)
else:
    console = Console()

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Enhanced task classification"""
    CODING = "coding"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    DEBUGGING = "debugging"
    EXPLANATION = "explanation"
    CREATIVE_WRITING = "creative_writing"
    GENERAL = "general"

class ModelTier(Enum):
    """Model cost tiers for prioritization"""
    FREE = "free"
    LOW_COST = "low_cost"
    MEDIUM_COST = "medium_cost"
    HIGH_COST = "high_cost"

class ModelHealth(Enum):
    """Model health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_id: str
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    total_requests: int = 0
    failed_requests: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    error_streak: int = 0
    health_status: ModelHealth = ModelHealth.UNKNOWN
    
    def update_success(self, response_time: float):
        """Record a successful request"""
        self.total_requests += 1
        self.last_success = datetime.now()
        self.error_streak = 0
        
        # Update rolling average response time
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (self.avg_response_time * 0.8) + (response_time * 0.2)
        
        self.success_rate = (self.total_requests - self.failed_requests) / self.total_requests
        self._update_health()
    
    def update_failure(self, error: str = ""):
        """Record a failed request"""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_failure = datetime.now()
        self.error_streak += 1
        
        self.success_rate = (self.total_requests - self.failed_requests) / self.total_requests
        self._update_health()
    
    def _update_health(self):
        """Update health status based on metrics"""
        if self.total_requests < 5:
            self.health_status = ModelHealth.UNKNOWN
        elif self.success_rate >= 0.9 and self.error_streak < 3:
            self.health_status = ModelHealth.HEALTHY
        elif self.success_rate >= 0.7 and self.error_streak < 5:
            self.health_status = ModelHealth.DEGRADED
        else:
            self.health_status = ModelHealth.UNHEALTHY

@dataclass
class ModelInfo:
    """Comprehensive model information"""
    id: str
    name: str
    provider: str
    tier: ModelTier
    context_length: int
    max_tokens: int = 4096
    cost_per_token: float = 0.0
    capabilities: List[TaskType] = field(default_factory=list)
    is_available: bool = True
    rate_limit_rpm: Optional[int] = None
    rate_limit_tpm: Optional[int] = None

class ModelCache:
    """Thread-safe model response caching"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached response if valid"""
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                    return value
                else:
                    del self._cache[key]
            return None
    
    def set(self, key: str, value: Any):
        """Cache a response"""
        with self._lock:
            # Clean old entries if cache is full
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k][1])
                del self._cache[oldest_key]
            
            self._cache[key] = (value, datetime.now())
    
    def clear(self):
        """Clear all cached entries"""
        with self._lock:
            self._cache.clear()

class ModelSelector:
    """Intelligent model selection with performance tracking and fallback chains"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.performance_tracker: Dict[str, ModelPerformance] = {}
        self.cache = ModelCache()
        self._lock = threading.RLock()
        
        # Initialize model registry
        self.available_models = self._initialize_model_registry()
        
        # Task-specific preferences (can be overridden by config)
        self.task_preferences = {
            TaskType.CODING: ["deepseek/deepseek-r1:free", "deepseek/deepseek-chat-v3-0324:free"],
            TaskType.CODE_GENERATION: ["deepseek/deepseek-r1:free", "google/gemini-2.0-flash-exp:free"],
            TaskType.CODE_REVIEW: ["deepseek/deepseek-r1:free", "deepseek/deepseek-chat-v3-0324:free"],
            TaskType.DEBUGGING: ["deepseek/deepseek-r1:free", "deepseek/deepseek-chat-v3-0324:free"],
            TaskType.RESEARCH: ["deepseek/deepseek-r1:free", "google/gemini-2.0-flash-exp:free"],
            TaskType.ANALYSIS: ["deepseek/deepseek-r1:free", "google/gemini-2.0-flash-exp:free"],
            TaskType.DOCUMENTATION: ["deepseek/deepseek-chat-v3-0324:free", "google/gemini-2.0-flash-exp:free"],
            TaskType.EXPLANATION: ["deepseek/deepseek-r1:free", "google/gemini-2.0-flash-exp:free"],
            TaskType.CREATIVE_WRITING: ["google/gemini-2.0-flash-exp:free", "deepseek/deepseek-chat-v3-0324:free"],
            TaskType.GENERAL: ["deepseek/deepseek-r1:free", "google/gemini-2.0-flash-exp:free"]
        }
        
        logger.info(f"ModelSelector initialized with {len(self.available_models)} models")
    
    def _initialize_model_registry(self) -> Dict[str, ModelInfo]:
        """Initialize registry of available models"""
        models = {}
        
        # Canonical models as of 2025 - Updated with correct OpenRouter model IDs
        free_models = [
            # xAI Grok
            ModelInfo(
                id="x-ai/grok-4",
                name="Grok 4",
                provider="xAI",
                tier=ModelTier.HIGH_COST,
                context_length=32768,
                max_tokens=8192,
                capabilities=[TaskType.GENERAL, TaskType.CODING, TaskType.ANALYSIS]
            ),
            ModelInfo(
                id="x-ai/grok-3",
                name="Grok 3",
                provider="xAI",
                tier=ModelTier.MEDIUM_COST,
                context_length=32768,
                max_tokens=8192,
                capabilities=[TaskType.GENERAL, TaskType.ANALYSIS]
            ),
            # OpenAI GPT-5 series
            ModelInfo(
                id="openai/gpt-5",
                name="GPT-5",
                provider="OpenAI",
                tier=ModelTier.HIGH_COST,
                context_length=32768,
                max_tokens=8192,
                capabilities=[TaskType.GENERAL, TaskType.CODING, TaskType.ANALYSIS]
            ),
            ModelInfo(
                id="openai/gpt-5-mini",
                name="GPT-5 Mini",
                provider="OpenAI",
                tier=ModelTier.MEDIUM_COST,
                context_length=32768,
                max_tokens=8192,
                capabilities=[TaskType.GENERAL, TaskType.ANALYSIS]
            ),
            ModelInfo(
                id="google/gemini-2.0-flash-exp:free",
                name="Gemini 2.0 Flash Experimental (Free)",
                provider="Google",
                tier=ModelTier.FREE,
                context_length=32768,
                max_tokens=4096,
                capabilities=[TaskType.GENERAL, TaskType.RESEARCH, TaskType.CREATIVE_WRITING, TaskType.EXPLANATION, TaskType.ANALYSIS]
            ),
            # Popular paid (or regionally limited) options as canonical entries
            ModelInfo(
                id="google/gemini-2.5-pro",
                name="Gemini 2.5 Pro",
                provider="Google",
                tier=ModelTier.MEDIUM_COST,
                context_length=32768,
                max_tokens=8192,
                capabilities=[TaskType.GENERAL, TaskType.CODING, TaskType.ANALYSIS, TaskType.DOCUMENTATION]
            ),
            ModelInfo(
                id="google/gemini-2.5-flash",
                name="Gemini 2.5 Flash",
                provider="Google",
                tier=ModelTier.LOW_COST,
                context_length=32768,
                max_tokens=8192,
                capabilities=[TaskType.GENERAL, TaskType.RESEARCH, TaskType.CREATIVE_WRITING, TaskType.EXPLANATION]
            ),
            ModelInfo(
                id="google/gemini-2.5-flash-lite",
                name="Gemini 2.5 Flash Lite",
                provider="Google",
                tier=ModelTier.LOW_COST,
                context_length=32768,
                max_tokens=4096,
                capabilities=[TaskType.GENERAL, TaskType.RESEARCH]
            ),
            ModelInfo(
                id="google/gemini-2.5-pro-exp-03-25:free",
                name="Gemini 2.5 Pro Experimental (Free)",
                provider="Google",
                tier=ModelTier.FREE,
                context_length=32768,
                max_tokens=4096,
                capabilities=[TaskType.GENERAL, TaskType.RESEARCH, TaskType.ANALYSIS, TaskType.EXPLANATION]
            ),
            ModelInfo(
                id="meta-llama/llama-3.3-70b-instruct:free",
                name="Llama 3.3 70B Instruct (Free)",
                provider="Meta",
                tier=ModelTier.FREE,
                context_length=32768,
                max_tokens=4096,
                capabilities=[TaskType.GENERAL, TaskType.CODING, TaskType.ANALYSIS, TaskType.DOCUMENTATION]
            ),
            ModelInfo(
                id="qwen/qwq-32b:free",
                name="QwQ 32B (Free)",
                provider="Alibaba",
                tier=ModelTier.FREE,
                context_length=32768,
                max_tokens=4096,
                capabilities=[TaskType.RESEARCH, TaskType.ANALYSIS, TaskType.GENERAL, TaskType.CODING]
            ),
            ModelInfo(
                id="qwen/qwen3-coder",
                name="Qwen3 Coder",
                provider="Qwen",
                tier=ModelTier.LOW_COST,
                context_length=32768,
                max_tokens=8192,
                capabilities=[TaskType.CODING, TaskType.CODE_GENERATION, TaskType.CODE_REVIEW, TaskType.DEBUGGING]
            ),
            ModelInfo(
                id="qwen/qwen3-235b-a22b-thinking-2507",
                name="Qwen3 235B A22B Thinking 2507",
                provider="Qwen",
                tier=ModelTier.HIGH_COST,
                context_length=32768,
                max_tokens=8192,
                capabilities=[TaskType.RESEARCH, TaskType.ANALYSIS, TaskType.EXPLANATION]
            ),
            ModelInfo(
                id="qwen/qwen3-30b-a3b-instruct-2507",
                name="Qwen3 30B A3B Instruct 2507",
                provider="Qwen",
                tier=ModelTier.MEDIUM_COST,
                context_length=32768,
                max_tokens=8192,
                capabilities=[TaskType.GENERAL, TaskType.ANALYSIS]
            ),
            # DeepSeek popular entries
            ModelInfo(
                id="deepseek/deepseek-r1:free",
                name="DeepSeek R1 (Free)",
                provider="DeepSeek",
                tier=ModelTier.FREE,
                context_length=64000,
                max_tokens=8192,
                capabilities=[TaskType.CODING, TaskType.RESEARCH, TaskType.ANALYSIS, TaskType.CODE_REVIEW, TaskType.EXPLANATION, TaskType.DEBUGGING]
            ),
            ModelInfo(
                id="deepseek/deepseek-chat-v3-0324:free",
                name="DeepSeek V3 0324 (Free)",
                provider="DeepSeek",
                tier=ModelTier.FREE,
                context_length=32768,
                max_tokens=4096,
                capabilities=[TaskType.GENERAL, TaskType.CODING, TaskType.ANALYSIS, TaskType.DOCUMENTATION, TaskType.CREATIVE_WRITING]
            ),
            # Additional commonly requested models (availability may vary)
            ModelInfo(
                id="moonshot/kimi-k2:free",
                name="Kimi K2 (Free)",
                provider="MoonshotAI",
                tier=ModelTier.FREE,
                context_length=32768,
                max_tokens=4096,
                capabilities=[TaskType.GENERAL, TaskType.CODING, TaskType.ANALYSIS]
            ),
            ModelInfo(
                id="qwen/qwen2.5-coder",
                name="Qwen 2.5 Coder",
                provider="Qwen",
                tier=ModelTier.LOW_COST,
                context_length=32768,
                max_tokens=4096,
                capabilities=[TaskType.CODING, TaskType.CODE_GENERATION, TaskType.CODE_REVIEW, TaskType.DEBUGGING]
            ),
        ]
        
        for model in free_models:
            models[model.id] = model
        
        return models
    
    def select_model(self, task_type: TaskType, context: str = "", 
                    preferred_models: Optional[List[str]] = None) -> Tuple[str, float]:
        """
        Select the best model for a task with confidence score
        
        Returns:
            Tuple[model_id, confidence_score]
        """
        with self._lock:
            # Get candidate models
            candidates = self._get_candidate_models(task_type, preferred_models)
            
            if not candidates:
                # Fallback to any available model
                candidates = list(self.available_models.keys())
            
            # Score models based on multiple factors
            scored_models = []
            for model_id in candidates:
                score = self._calculate_model_score(model_id, task_type, context)
                scored_models.append((model_id, score))
            
            # Sort by score (highest first)
            scored_models.sort(key=lambda x: x[1], reverse=True)
            
            best_model, confidence = scored_models[0]
            
            logger.info(f"Selected model {best_model} for {task_type.value} (confidence: {confidence:.2f})")
            return best_model, confidence
    
    def _get_candidate_models(self, task_type: TaskType, 
                            preferred_models: Optional[List[str]] = None) -> List[str]:
        """Get candidate models for a task type"""
        candidates = []
        
        # Add user preferences first
        if preferred_models:
            candidates.extend(preferred_models)
        
        # Add task-specific preferences
        task_models = self.task_preferences.get(task_type, [])
        candidates.extend(task_models)
        
        # Add models with matching capabilities
        for model_id, model_info in self.available_models.items():
            if task_type in model_info.capabilities and model_info.is_available:
                candidates.append(model_id)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for model_id in candidates:
            if model_id not in seen and model_id in self.available_models:
                seen.add(model_id)
                unique_candidates.append(model_id)
        
        return unique_candidates
    
    def _calculate_model_score(self, model_id: str, task_type: TaskType, context: str) -> float:
        """Calculate comprehensive model score for selection"""
        model_info = self.available_models.get(model_id)
        if not model_info or not model_info.is_available:
            return 0.0
        
        score = 0.5  # Base score
        
        # Task capability match
        if task_type in model_info.capabilities:
            score += 0.3
        
        # Performance history
        if model_id in self.performance_tracker:
            perf = self.performance_tracker[model_id]
            
            # Success rate bonus
            score += perf.success_rate * 0.2
            
            # Response time penalty (prefer faster models)
            if perf.avg_response_time > 0:
                time_penalty = min(perf.avg_response_time / 30.0, 0.1)  # Cap at 0.1
                score -= time_penalty
            
            # Health status adjustment
            health_adjustments = {
                ModelHealth.HEALTHY: 0.1,
                ModelHealth.DEGRADED: -0.05,
                ModelHealth.UNHEALTHY: -0.2,
                ModelHealth.UNKNOWN: 0.0
            }
            score += health_adjustments[perf.health_status]
            
            # Recent error streak penalty
            if perf.error_streak > 0:
                score -= min(perf.error_streak * 0.05, 0.15)
        
        # Context length consideration
        context_length_needed = len(context) + 1000  # Buffer for response
        if context_length_needed > model_info.context_length:
            score -= 0.3  # Heavy penalty for insufficient context
        
        # Model tier preference (free models are preferred)
        tier_bonuses = {
            ModelTier.FREE: 0.1,
            ModelTier.LOW_COST: 0.05,
            ModelTier.MEDIUM_COST: 0.0,
            ModelTier.HIGH_COST: -0.1
        }
        score += tier_bonuses.get(model_info.tier, 0.0)
        
        return max(0.0, min(1.0, score))
    
    def get_fallback_chain(self, primary_model: str, task_type: TaskType, 
                          max_fallbacks: int = 3) -> List[str]:
        """Get ordered fallback models for a primary model"""
        candidates = self._get_candidate_models(task_type)
        
        # Remove primary model from candidates
        fallbacks = [m for m in candidates if m != primary_model]
        
        # Score remaining models
        scored_fallbacks = []
        for model_id in fallbacks:
            score = self._calculate_model_score(model_id, task_type, "")
            scored_fallbacks.append((model_id, score))
        
        # Sort and return top fallbacks
        scored_fallbacks.sort(key=lambda x: x[1], reverse=True)
        return [model_id for model_id, _ in scored_fallbacks[:max_fallbacks]]
    
    def record_request_success(self, model_id: str, response_time: float):
        """Record a successful model request"""
        with self._lock:
            if model_id not in self.performance_tracker:
                self.performance_tracker[model_id] = ModelPerformance(model_id)
            
            self.performance_tracker[model_id].update_success(response_time)
            logger.debug(f"Recorded success for {model_id}: {response_time:.2f}s")
    
    def record_request_failure(self, model_id: str, error: str = ""):
        """Record a failed model request"""
        with self._lock:
            if model_id not in self.performance_tracker:
                self.performance_tracker[model_id] = ModelPerformance(model_id)
            
            self.performance_tracker[model_id].update_failure(error)
            logger.warning(f"Recorded failure for {model_id}: {error}")
    
    def get_model_health(self, model_id: str) -> ModelHealth:
        """Get current health status of a model"""
        if model_id in self.performance_tracker:
            return self.performance_tracker[model_id].health_status
        return ModelHealth.UNKNOWN
    
    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all models"""
        stats = {}
        for model_id, perf in self.performance_tracker.items():
            model_info = self.available_models.get(model_id, {})
            stats[model_id] = {
                'name': getattr(model_info, 'name', model_id),
                'success_rate': perf.success_rate,
                'avg_response_time': perf.avg_response_time,
                'total_requests': perf.total_requests,
                'health_status': perf.health_status.value,
                'error_streak': perf.error_streak,
                'last_success': perf.last_success.isoformat() if perf.last_success else None,
                'last_failure': perf.last_failure.isoformat() if perf.last_failure else None
            }
        return stats
    
    def display_model_status(self):
        """Display model status using Rich console"""
        table = Table(title="Model Performance Status", box=box.ROUNDED)
        table.add_column("Model", style="cyan")
        table.add_column("Health", style="green")
        table.add_column("Success Rate", style="blue")
        table.add_column("Avg Time", style="yellow")
        table.add_column("Requests", style="white")
        table.add_column("Errors", style="red")
        
        for model_id, model_info in self.available_models.items():
            if model_id in self.performance_tracker:
                perf = self.performance_tracker[model_id]
                
                # Health status with emoji
                health_display = {
                    ModelHealth.HEALTHY: "🟢 Healthy",
                    ModelHealth.DEGRADED: "🟡 Degraded", 
                    ModelHealth.UNHEALTHY: "🔴 Unhealthy",
                    ModelHealth.UNKNOWN: "⚪ Unknown"
                }[perf.health_status]
                
                table.add_row(
                    model_info.name,
                    health_display,
                    f"{perf.success_rate:.1%}",
                    f"{perf.avg_response_time:.1f}s",
                    str(perf.total_requests),
                    str(perf.error_streak)
                )
            else:
                table.add_row(
                    model_info.name,
                    "⚪ Unknown",
                    "No data",
                    "No data", 
                    "0",
                    "0"
                )
        
        console.print(table)
    
    def reset_performance_data(self):
        """Reset all performance tracking data"""
        with self._lock:
            self.performance_tracker.clear()
            self.cache.clear()
            logger.info("Performance data reset")
    
    def save_performance_data(self, file_path: str):
        """Save performance data to file"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'performance': {}
            }
            
            for model_id, perf in self.performance_tracker.items():
                data['performance'][model_id] = {
                    'success_rate': perf.success_rate,
                    'avg_response_time': perf.avg_response_time,
                    'total_requests': perf.total_requests,
                    'failed_requests': perf.failed_requests,
                    'error_streak': perf.error_streak,
                    'health_status': perf.health_status.value,
                    'last_success': perf.last_success.isoformat() if perf.last_success else None,
                    'last_failure': perf.last_failure.isoformat() if perf.last_failure else None
                }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Performance data saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save performance data: {e}")
    
    def load_performance_data(self, file_path: str):
        """Load performance data from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            performance_data = data.get('performance', {})
            
            for model_id, perf_data in performance_data.items():
                perf = ModelPerformance(model_id)
                perf.success_rate = perf_data.get('success_rate', 0.0)
                perf.avg_response_time = perf_data.get('avg_response_time', 0.0)
                perf.total_requests = perf_data.get('total_requests', 0)
                perf.failed_requests = perf_data.get('failed_requests', 0)
                perf.error_streak = perf_data.get('error_streak', 0)
                perf.health_status = ModelHealth(perf_data.get('health_status', 'unknown'))
                
                if perf_data.get('last_success'):
                    perf.last_success = datetime.fromisoformat(perf_data['last_success'])
                if perf_data.get('last_failure'):
                    perf.last_failure = datetime.fromisoformat(perf_data['last_failure'])
                
                self.performance_tracker[model_id] = perf
            
            logger.info(f"Performance data loaded from {file_path}")
            
        except Exception as e:
            logger.warning(f"Failed to load performance data: {e}")

# Convenience function for global access
_global_model_selector: Optional[ModelSelector] = None

def get_model_selector() -> ModelSelector:
    """Get the global model selector instance"""
    global _global_model_selector
    if _global_model_selector is None:
        _global_model_selector = ModelSelector()
    return _global_model_selector