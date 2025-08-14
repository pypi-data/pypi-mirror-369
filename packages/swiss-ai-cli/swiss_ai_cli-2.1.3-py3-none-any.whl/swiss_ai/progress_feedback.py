#!/usr/bin/env python3
"""
Progress Indicators and Real-time Feedback for Swiss AI CLI
Beautiful progress bars, spinners, and status updates
"""

import time
import asyncio
from typing import Optional, Dict, Any, List, Callable, Union
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager
import threading

from rich.console import Console
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, BarColumn, 
    TimeElapsedColumn, TimeRemainingColumn, MofNCompleteColumn,
    TaskProgressColumn, ProgressColumn
)
from rich.status import Status
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.spinner import Spinner
from rich import box

console = Console()

class OperationType(Enum):
    """Types of operations for different progress styles"""
    ANALYSIS = "analysis"
    GENERATION = "generation" 
    REVIEW = "review"
    NETWORK = "network"
    FILE_PROCESSING = "file_processing"
    MODEL_LOADING = "model_loading"
    HEALTH_CHECK = "health_check"
    CONFIGURATION = "configuration"
    BATCH_PROCESSING = "batch_processing"

class FeedbackLevel(Enum):
    """Feedback detail levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    VERBOSE = "verbose"

@dataclass
class OperationStep:
    """Individual step in a multi-step operation"""
    name: str
    description: str
    weight: float = 1.0  # Relative weight for progress calculation
    estimated_time: Optional[float] = None
    status: str = "pending"  # pending, running, completed, failed

@dataclass
class OperationConfig:
    """Configuration for operation progress display"""
    operation_type: OperationType
    title: str
    steps: List[OperationStep]
    show_spinner: bool = True
    show_progress_bar: bool = True
    show_elapsed_time: bool = True
    show_remaining_time: bool = True
    show_steps: bool = True
    feedback_level: FeedbackLevel = FeedbackLevel.STANDARD

class ProgressManager:
    """Advanced progress management with multiple tracking modes"""
    
    def __init__(self):
        self.active_operations: Dict[str, Any] = {}
        self.feedback_level = FeedbackLevel.STANDARD
        self.console = console
        
        # Operation-specific configurations
        self.operation_configs = {
            OperationType.ANALYSIS: {
                "spinner": "dots",
                "color": "blue",
                "prefix": "🔍",
                "messages": [
                    "Analyzing code structure...",
                    "Evaluating complexity...", 
                    "Generating insights...",
                    "Finalizing analysis..."
                ]
            },
            OperationType.GENERATION: {
                "spinner": "arc",
                "color": "green", 
                "prefix": "✨",
                "messages": [
                    "Understanding requirements...",
                    "Generating code...",
                    "Optimizing output...",
                    "Validating results..."
                ]
            },
            OperationType.REVIEW: {
                "spinner": "dots2",
                "color": "yellow",
                "prefix": "🔍", 
                "messages": [
                    "Scanning for issues...",
                    "Analyzing patterns...",
                    "Checking best practices...",
                    "Compiling feedback..."
                ]
            },
            OperationType.NETWORK: {
                "spinner": "line",
                "color": "cyan",
                "prefix": "🌐",
                "messages": [
                    "Connecting to API...",
                    "Sending request...",
                    "Waiting for response...",
                    "Processing results..."
                ]
            },
            OperationType.MODEL_LOADING: {
                "spinner": "bouncingBall",
                "color": "magenta",
                "prefix": "🧠",
                "messages": [
                    "Initializing model...",
                    "Loading parameters...",
                    "Optimizing performance...",
                    "Ready for inference..."
                ]
            }
        }
    
    def set_feedback_level(self, level: FeedbackLevel):
        """Set global feedback level"""
        self.feedback_level = level
    
    @contextmanager
    def operation(
        self,
        operation_type: OperationType,
        title: str,
        steps: Optional[List[str]] = None,
        show_steps: bool = True
    ):
        """Context manager for tracked operations"""
        operation_id = f"{operation_type.value}_{int(time.time())}"
        
        try:
            # Start operation
            self._start_operation(operation_id, operation_type, title, steps, show_steps)
            
            # Yield operation controller
            yield OperationController(self, operation_id)
            
        finally:
            # End operation
            self._end_operation(operation_id)
    
    def _start_operation(
        self, 
        operation_id: str, 
        operation_type: OperationType, 
        title: str,
        steps: Optional[List[str]] = None,
        show_steps: bool = True
    ):
        """Start tracking an operation"""
        config = self.operation_configs.get(operation_type, {})
        
        if self.feedback_level == FeedbackLevel.MINIMAL:
            # Just show simple message
            prefix = config.get("prefix", "")
            self.console.print(f"{prefix} {title}...")
            return
        
        # Create progress display
        if steps and show_steps:
            self._start_multi_step_operation(operation_id, operation_type, title, steps)
        else:
            self._start_simple_operation(operation_id, operation_type, title)
    
    def _start_simple_operation(self, operation_id: str, operation_type: OperationType, title: str):
        """Start simple spinner-based operation"""
        config = self.operation_configs.get(operation_type, {})
        spinner_style = config.get("spinner", "dots")
        color = config.get("color", "blue")
        prefix = config.get("prefix", "")
        
        status = Status(
            f"{prefix} {title}",
            spinner=spinner_style,
            console=self.console
        )
        status.start()
        
        self.active_operations[operation_id] = {
            "type": "simple",
            "status": status,
            "config": config,
            "start_time": time.time()
        }
    
    def _start_multi_step_operation(
        self, 
        operation_id: str, 
        operation_type: OperationType, 
        title: str, 
        steps: List[str]
    ):
        """Start multi-step operation with progress bar"""
        config = self.operation_configs.get(operation_type, {})
        
        # Create progress bar
        progress = Progress(
            SpinnerColumn(spinner_style=config.get("spinner", "dots")),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style=config.get("color", "blue")),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=self.console
        )
        
        progress.start()
        task_id = progress.add_task(title, total=len(steps))
        
        self.active_operations[operation_id] = {
            "type": "multi_step",
            "progress": progress,
            "task_id": task_id,
            "steps": steps,
            "current_step": 0,
            "config": config,
            "start_time": time.time()
        }
    
    def _end_operation(self, operation_id: str):
        """End operation and cleanup"""
        if operation_id not in self.active_operations:
            return
        
        operation = self.active_operations[operation_id]
        
        if operation["type"] == "simple":
            operation["status"].stop()
        elif operation["type"] == "multi_step":
            operation["progress"].stop()
        
        del self.active_operations[operation_id]
    
    def update_operation(
        self, 
        operation_id: str, 
        message: Optional[str] = None,
        step: Optional[int] = None,
        advance: bool = False
    ):
        """Update operation progress"""
        if operation_id not in self.active_operations:
            return
        
        operation = self.active_operations[operation_id]
        
        if operation["type"] == "simple":
            if message:
                prefix = operation["config"].get("prefix", "")
                operation["status"].update(f"{prefix} {message}")
        
        elif operation["type"] == "multi_step":
            progress = operation["progress"]
            task_id = operation["task_id"]
            
            if step is not None:
                operation["current_step"] = step
                step_name = operation["steps"][step] if step < len(operation["steps"]) else "Completing..."
                progress.update(task_id, description=step_name)
            
            if advance:
                progress.advance(task_id)
                operation["current_step"] += 1
            
            if message:
                progress.update(task_id, description=message)

class OperationController:
    """Controller for managing operation progress"""
    
    def __init__(self, manager: ProgressManager, operation_id: str):
        self.manager = manager
        self.operation_id = operation_id
    
    def update(self, message: str):
        """Update operation message"""
        self.manager.update_operation(self.operation_id, message=message)
    
    def step(self, step_index: int, message: Optional[str] = None):
        """Move to specific step"""
        self.manager.update_operation(
            self.operation_id, 
            step=step_index, 
            message=message
        )
    
    def advance(self, message: Optional[str] = None):
        """Advance to next step"""
        self.manager.update_operation(
            self.operation_id,
            advance=True,
            message=message
        )

class FeedbackNotifier:
    """Provides feedback notifications and status updates"""
    
    def __init__(self):
        self.console = console
        self.notifications_enabled = True
    
    def success(self, message: str, details: Optional[str] = None):
        """Show success notification"""
        self.console.print(f"[green]✓[/green] {message}")
        if details:
            self.console.print(f"  [dim]{details}[/dim]")
    
    def warning(self, message: str, details: Optional[str] = None):
        """Show warning notification"""
        self.console.print(f"[yellow]⚠[/yellow] {message}")
        if details:
            self.console.print(f"  [dim]{details}[/dim]")
    
    def error(self, message: str, details: Optional[str] = None):
        """Show error notification"""
        self.console.print(f"[red]✗[/red] {message}")
        if details:
            self.console.print(f"  [dim]{details}[/dim]")
    
    def info(self, message: str, details: Optional[str] = None):
        """Show info notification"""
        self.console.print(f"[blue]ℹ[/blue] {message}")
        if details:
            self.console.print(f"  [dim]{details}[/dim]")
    
    def completion(self, operation: str, duration: float, stats: Optional[Dict[str, Any]] = None):
        """Show operation completion notification"""
        duration_str = f"{duration:.1f}s" if duration < 60 else f"{duration/60:.1f}m"
        
        self.console.print(f"[green]✨ {operation} completed[/green] [dim]({duration_str})[/dim]")
        
        if stats:
            self._show_completion_stats(stats)
    
    def _show_completion_stats(self, stats: Dict[str, Any]):
        """Show completion statistics"""
        if not stats:
            return
        
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1))
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in stats.items():
            table.add_row(key.replace("_", " ").title(), str(value))
        
        self.console.print(table)

class BatchProgressTracker:
    """Track progress for batch operations"""
    
    def __init__(self, title: str, total_items: int, show_individual: bool = True):
        self.title = title
        self.total_items = total_items
        self.show_individual = show_individual
        self.completed_items = 0
        self.failed_items = 0
        self.start_time = time.time()
        
        # Create progress display
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console
        )
        
        self.progress.start()
        self.main_task = self.progress.add_task(self.title, total=total_items)
    
    def update_item(self, item_name: str, status: str = "processing"):
        """Update current item being processed"""
        if self.show_individual:
            self.progress.update(
                self.main_task,
                description=f"{self.title} - {item_name} ({status})"
            )
    
    def complete_item(self, success: bool = True):
        """Mark item as completed"""
        if success:
            self.completed_items += 1
        else:
            self.failed_items += 1
        
        self.progress.advance(self.main_task)
    
    def finish(self):
        """Finish batch operation"""
        self.progress.stop()
        
        duration = time.time() - self.start_time
        success_rate = (self.completed_items / self.total_items * 100) if self.total_items > 0 else 0
        
        # Show completion summary
        notifier = FeedbackNotifier()
        notifier.completion(
            self.title,
            duration,
            {
                "Total Items": self.total_items,
                "Completed": self.completed_items,
                "Failed": self.failed_items,
                "Success Rate": f"{success_rate:.1f}%"
            }
        )

class RealTimeMonitor:
    """Real-time monitoring and live updates"""
    
    def __init__(self, title: str):
        self.title = title
        self.metrics = {}
        self.status_messages = []
        self.start_time = time.time()
        self.live = None
    
    def start(self):
        """Start live monitoring"""
        self.live = Live(self._generate_display(), refresh_per_second=2, console=console)
        self.live.start()
    
    def stop(self):
        """Stop live monitoring"""
        if self.live:
            self.live.stop()
    
    def update_metric(self, name: str, value: Any):
        """Update a metric value"""
        self.metrics[name] = value
        if self.live:
            self.live.update(self._generate_display())
    
    def add_status(self, message: str):
        """Add status message"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_messages.append(f"[{timestamp}] {message}")
        
        # Keep only last 5 messages
        if len(self.status_messages) > 5:
            self.status_messages.pop(0)
        
        if self.live:
            self.live.update(self._generate_display())
    
    def _generate_display(self):
        """Generate live display content"""
        # Create metrics table
        metrics_table = Table(title="Metrics", box=box.ROUNDED)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="white")
        
        for name, value in self.metrics.items():
            metrics_table.add_row(name, str(value))
        
        # Create status panel
        status_text = "\n".join(self.status_messages[-3:]) if self.status_messages else "No status updates"
        status_panel = Panel(
            status_text,
            title="Recent Activity",
            border_style="blue"
        )
        
        # Runtime info
        runtime = time.time() - self.start_time
        runtime_text = f"Runtime: {runtime:.1f}s"
        
        # Combine in main panel
        content = Table.grid()
        content.add_column()
        content.add_row(f"[bold]{self.title}[/bold] - {runtime_text}")
        content.add_row("")
        content.add_row(metrics_table)
        content.add_row("")
        content.add_row(status_panel)
        
        return Panel(content, title="🔄 Live Monitor", border_style="green")

# Global instances
progress_manager = ProgressManager()
notifier = FeedbackNotifier()

# Convenience functions
def show_progress(operation_type: OperationType, title: str, steps: Optional[List[str]] = None):
    """Convenience function to show progress"""
    return progress_manager.operation(operation_type, title, steps)

def show_success(message: str, details: Optional[str] = None):
    """Show success message"""
    notifier.success(message, details)

def show_warning(message: str, details: Optional[str] = None):
    """Show warning message"""
    notifier.warning(message, details)

def show_error(message: str, details: Optional[str] = None):
    """Show error message"""
    notifier.error(message, details)

def show_info(message: str, details: Optional[str] = None):
    """Show info message"""
    notifier.info(message, details)

def track_batch(title: str, total_items: int, show_individual: bool = True):
    """Create batch progress tracker"""
    return BatchProgressTracker(title, total_items, show_individual)

def monitor_realtime(title: str):
    """Create real-time monitor"""
    return RealTimeMonitor(title)

# Async progress utilities
async def with_progress(
    operation_type: OperationType,
    title: str,
    async_func: Callable,
    *args,
    **kwargs
):
    """Run async function with progress tracking"""
    with show_progress(operation_type, title) as progress:
        try:
            result = await async_func(*args, **kwargs)
            return result
        except Exception as e:
            progress.update(f"Error: {str(e)}")
            raise

# Spinner decorators
def with_spinner(operation_type: OperationType = OperationType.ANALYSIS, title: str = "Processing"):
    """Decorator to add spinner to function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with show_progress(operation_type, title):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def with_async_spinner(operation_type: OperationType = OperationType.ANALYSIS, title: str = "Processing"):
    """Decorator to add spinner to async function"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            with show_progress(operation_type, title):
                return await func(*args, **kwargs)
        return wrapper
    return decorator