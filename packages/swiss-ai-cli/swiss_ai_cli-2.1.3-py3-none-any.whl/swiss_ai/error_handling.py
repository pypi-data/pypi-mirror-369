#!/usr/bin/env python3
"""
Advanced Error Handling for Swiss AI CLI
Graceful error messages with suggestions and troubleshooting guidance
"""

import sys
import traceback
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from rich import box
from rich.columns import Columns

console = Console()

class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for targeted handling"""
    CONFIGURATION = "configuration"
    API_KEY = "api_key"
    NETWORK = "network"
    FILE_ACCESS = "file_access"
    MODEL_SELECTION = "model_selection"
    COMMAND_SYNTAX = "command_syntax"
    DEPENDENCY = "dependency"
    PERMISSIONS = "permissions"
    RESOURCE = "resource"
    UNKNOWN = "unknown"

@dataclass
class ErrorContext:
    """Context information for better error handling"""
    command: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    user_input: Optional[str] = None
    system_info: Optional[Dict[str, Any]] = None
    recent_commands: Optional[List[str]] = None

@dataclass
class ErrorSolution:
    """Suggested solution for an error"""
    title: str
    description: str
    commands: List[str]
    difficulty: str = "easy"  # easy, medium, hard
    success_rate: float = 0.8  # How often this solution works

class SwissAIError(Exception):
    """Enhanced error class with rich context and suggestions"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        suggestions: Optional[List[str]] = None,
        solutions: Optional[List[ErrorSolution]] = None,
        context: Optional[ErrorContext] = None,
        exit_code: int = 1,
        show_traceback: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.suggestions = suggestions or []
        self.solutions = solutions or []
        self.context = context or ErrorContext()
        self.exit_code = exit_code
        self.show_traceback = show_traceback

class ErrorAnalyzer:
    """Analyzes errors and provides intelligent suggestions"""
    
    def __init__(self):
        self.common_patterns = self._load_common_patterns()
        self.solution_database = self._load_solution_database()
        self.troubleshooting_guides = self._load_troubleshooting_guides()
    
    def analyze_error(self, error: Exception, context: ErrorContext) -> SwissAIError:
        """Analyze an error and return enhanced error information"""
        if isinstance(error, SwissAIError):
            return error
        
        error_str = str(error)
        error_type = type(error).__name__
        
        # Detect error category
        category = self._detect_category(error_str, error_type, context)
        
        # Determine severity
        severity = self._determine_severity(error, category)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(error_str, category, context)
        
        # Find solutions
        solutions = self._find_solutions(error_str, category, context)
        
        return SwissAIError(
            message=error_str,
            category=category,
            severity=severity,
            suggestions=suggestions,
            solutions=solutions,
            context=context,
            show_traceback=severity == ErrorSeverity.CRITICAL
        )
    
    def _detect_category(self, error_str: str, error_type: str, context: ErrorContext) -> ErrorCategory:
        """Detect error category based on patterns"""
        error_lower = error_str.lower()
        
        # API Key related
        if any(keyword in error_lower for keyword in ['api key', 'api_key', 'authentication', 'unauthorized', '401']):
            return ErrorCategory.API_KEY
        
        # Configuration related
        if any(keyword in error_lower for keyword in ['config', 'configuration', 'yaml', 'setting']):
            return ErrorCategory.CONFIGURATION
        
        # Network related
        if any(keyword in error_lower for keyword in ['network', 'connection', 'timeout', 'unreachable', '503', '502']):
            return ErrorCategory.NETWORK
        
        # File access related
        if any(keyword in error_lower for keyword in ['no such file', 'permission denied', 'access denied', 'file not found']):
            return ErrorCategory.FILE_ACCESS
        
        # Model selection related
        if any(keyword in error_lower for keyword in ['model', 'model not found', 'invalid model']):
            return ErrorCategory.MODEL_SELECTION
        
        # Command syntax related
        if error_type in ['UsageError', 'BadParameter', 'MissingParameter']:
            return ErrorCategory.COMMAND_SYNTAX
        
        # Dependency related
        if any(keyword in error_lower for keyword in ['import', 'module', 'package', 'dependency']):
            return ErrorCategory.DEPENDENCY
        
        # Permissions related
        if any(keyword in error_lower for keyword in ['permission', 'access denied', 'forbidden']):
            return ErrorCategory.PERMISSIONS
        
        # Resource related
        if any(keyword in error_lower for keyword in ['memory', 'disk space', 'quota', 'limit']):
            return ErrorCategory.RESOURCE
        
        return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity"""
        if isinstance(error, (SystemExit, KeyboardInterrupt)):
            return ErrorSeverity.INFO
        
        if category in [ErrorCategory.API_KEY, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.WARNING
        
        if category in [ErrorCategory.NETWORK, ErrorCategory.DEPENDENCY]:
            return ErrorSeverity.ERROR
        
        if category in [ErrorCategory.PERMISSIONS, ErrorCategory.RESOURCE]:
            return ErrorSeverity.CRITICAL
        
        return ErrorSeverity.ERROR
    
    def _generate_suggestions(self, error_str: str, category: ErrorCategory, context: ErrorContext) -> List[str]:
        """Generate helpful suggestions based on error category"""
        suggestions = []
        
        if category == ErrorCategory.API_KEY:
            suggestions.extend([
                "Check if your OPENROUTER_API_KEY environment variable is set",
                "Verify your API key is valid and active",
                "Run 'swiss-ai config:validate' to check configuration"
            ])
        
        elif category == ErrorCategory.CONFIGURATION:
            suggestions.extend([
                "Run 'swiss-ai config:init' to create a new configuration",
                "Check your ~/.swiss-ai/config.yaml file for syntax errors",
                "Use 'swiss-ai config:validate' to identify issues"
            ])
        
        elif category == ErrorCategory.NETWORK:
            suggestions.extend([
                "Check your internet connection",
                "Try again in a few moments - the service may be temporarily unavailable",
                "Check if you're behind a firewall or proxy"
            ])
        
        elif category == ErrorCategory.FILE_ACCESS:
            suggestions.extend([
                "Check if the file path exists and is readable",
                "Ensure you have the necessary permissions",
                "Try using an absolute path instead of a relative one"
            ])
        
        elif category == ErrorCategory.MODEL_SELECTION:
            suggestions.extend([
                "Run 'swiss-ai model:list' to see available models",
                "Check if the model name is spelled correctly",
                "Try using the default model: 'swiss-ai model:select qwen3-coder'"
            ])
        
        elif category == ErrorCategory.COMMAND_SYNTAX:
            suggestions.extend([
                "Run 'swiss-ai COMMAND --help' for usage information",
                "Check the command syntax and required parameters",
                "Use quotes around arguments that contain spaces"
            ])
        
        elif category == ErrorCategory.DEPENDENCY:
            suggestions.extend([
                "Install missing dependencies with 'pip install -r requirements.txt'",
                "Check if you're in the correct Python environment",
                "Try reinstalling Swiss AI CLI: 'pip install --force-reinstall -e .'"
            ])
        
        return suggestions
    
    def _find_solutions(self, error_str: str, category: ErrorCategory, context: ErrorContext) -> List[ErrorSolution]:
        """Find specific solutions for the error"""
        solutions = []
        
        if category == ErrorCategory.API_KEY:
            solutions.append(ErrorSolution(
                title="Set up API Key",
                description="Configure your OpenRouter API key for authentication",
                commands=[
                    "export OPENROUTER_API_KEY='your-key-here'",
                    "swiss-ai config:init --wizard"
                ],
                difficulty="easy",
                success_rate=0.95
            ))
        
        elif category == ErrorCategory.CONFIGURATION:
            solutions.append(ErrorSolution(
                title="Reset Configuration",
                description="Create a fresh configuration file",
                commands=[
                    "mv ~/.swiss-ai/config.yaml ~/.swiss-ai/config.yaml.backup",
                    "swiss-ai config:init"
                ],
                difficulty="easy",
                success_rate=0.9
            ))
        
        elif category == ErrorCategory.NETWORK:
            solutions.append(ErrorSolution(
                title="Network Troubleshooting",
                description="Diagnose and fix network connectivity issues",
                commands=[
                    "ping openrouter.ai",
                    "swiss-ai doctor --check-connectivity"
                ],
                difficulty="medium",
                success_rate=0.7
            ))
        
        return solutions
    
    def _load_common_patterns(self) -> Dict[str, List[str]]:
        """Load common error patterns for pattern matching"""
        return {
            "api_key_missing": [
                "api key not found",
                "authentication failed",
                "unauthorized"
            ],
            "config_invalid": [
                "invalid configuration",
                "yaml syntax error",
                "configuration file not found"
            ],
            "network_error": [
                "connection timeout",
                "network unreachable",
                "service unavailable"
            ]
        }
    
    def _load_solution_database(self) -> Dict[str, List[ErrorSolution]]:
        """Load database of known solutions"""
        return {}  # Would be populated with known solutions
    
    def _load_troubleshooting_guides(self) -> Dict[str, str]:
        """Load troubleshooting guides for different error types"""
        return {
            "api_key": """
# API Key Troubleshooting

1. **Check Environment Variable**
   ```bash
   echo $OPENROUTER_API_KEY
   ```

2. **Set API Key**
   ```bash
   export OPENROUTER_API_KEY="your-key-here"
   ```

3. **Verify Key Validity**
   ```bash
   swiss-ai config:validate
   ```
            """,
            "configuration": """
# Configuration Troubleshooting

1. **Check Configuration File**
   ```bash
   swiss-ai config:show
   ```

2. **Validate Configuration**
   ```bash
   swiss-ai config:validate
   ```

3. **Reset Configuration**
   ```bash
   swiss-ai config:init --force
   ```
            """
        }

class ErrorFormatter:
    """Formats errors with rich console output"""
    
    def __init__(self):
        self.severity_colors = {
            ErrorSeverity.INFO: "blue",
            ErrorSeverity.WARNING: "yellow",
            ErrorSeverity.ERROR: "red",
            ErrorSeverity.CRITICAL: "bright_red"
        }
        
        self.severity_icons = {
            ErrorSeverity.INFO: "ℹ",
            ErrorSeverity.WARNING: "⚠",
            ErrorSeverity.ERROR: "✗",
            ErrorSeverity.CRITICAL: "💥"
        }
    
    def format_error(self, error: SwissAIError, show_details: bool = True) -> None:
        """Format and display error with rich formatting"""
        color = self.severity_colors[error.severity]
        icon = self.severity_icons[error.severity]
        
        # Main error message
        error_text = f"[{color} bold]{icon} {error.severity.value.title()}:[/{color} bold] {error.message}"
        console.print(error_text)
        
        if not show_details:
            return
        
        # Show suggestions if available
        if error.suggestions:
            self._show_suggestions(error.suggestions)
        
        # Show solutions if available
        if error.solutions:
            self._show_solutions(error.solutions)
        
        # Show context if available
        if error.context and error.context.command:
            self._show_context(error.context)
        
        # Show troubleshooting guide
        self._show_troubleshooting_link(error.category)
        
        # Show traceback if requested
        if error.show_traceback:
            console.print("\n[dim]Traceback:[/dim]")
            console.print_exception()
    
    def _show_suggestions(self, suggestions: List[str]) -> None:
        """Show suggestions panel"""
        suggestion_text = "\n".join(f"• {suggestion}" for suggestion in suggestions)
        console.print(Panel(
            suggestion_text,
            title="💡 Suggestions",
            border_style="yellow",
            padding=(1, 2)
        ))
    
    def _show_solutions(self, solutions: List[ErrorSolution]) -> None:
        """Show solutions with commands"""
        if not solutions:
            return
        
        console.print("\n[bold green]🔧 Possible Solutions:[/bold green]")
        
        for i, solution in enumerate(solutions, 1):
            # Solution header
            difficulty_color = {
                "easy": "green",
                "medium": "yellow", 
                "hard": "red"
            }.get(solution.difficulty, "white")
            
            success_indicator = "🟢" if solution.success_rate > 0.8 else "🟡" if solution.success_rate > 0.6 else "🔴"
            
            console.print(f"\n[bold]{i}. {solution.title}[/bold] "
                         f"[{difficulty_color}]({solution.difficulty})[/{difficulty_color}] "
                         f"{success_indicator} {solution.success_rate:.0%}")
            
            console.print(f"   [dim]{solution.description}[/dim]")
            
            # Show commands
            if solution.commands:
                console.print("   [bold]Commands:[/bold]")
                for cmd in solution.commands:
                    console.print(f"   [cyan]$ {cmd}[/cyan]")
    
    def _show_context(self, context: ErrorContext) -> None:
        """Show error context information"""
        context_items = []
        
        if context.command:
            context_items.append(f"Command: [cyan]{context.command}[/cyan]")
        
        if context.file_path:
            context_items.append(f"File: [cyan]{context.file_path}[/cyan]")
        
        if context.user_input:
            context_items.append(f"Input: [cyan]{context.user_input}[/cyan]")
        
        if context_items:
            context_text = "\n".join(context_items)
            console.print(Panel(
                context_text,
                title="📋 Context",
                border_style="blue",
                padding=(1, 2)
            ))
    
    def _show_troubleshooting_link(self, category: ErrorCategory) -> None:
        """Show link to relevant troubleshooting guide"""
        guides = {
            ErrorCategory.API_KEY: "swiss-ai config:validate --help",
            ErrorCategory.CONFIGURATION: "swiss-ai config:init --help",
            ErrorCategory.NETWORK: "swiss-ai doctor --help",
            ErrorCategory.MODEL_SELECTION: "swiss-ai model:list --help"
        }
        
        if category in guides:
            console.print(f"\n[dim]For more help: [cyan]{guides[category]}[/cyan][/dim]")

class DidYouMeanSuggester:
    """Provides 'did you mean' suggestions for command errors"""
    
    def __init__(self):
        self.commands = self._load_available_commands()
    
    def suggest_command(self, invalid_command: str) -> List[str]:
        """Suggest similar commands for invalid input"""
        from difflib import get_close_matches
        
        # Flatten all commands into a single list
        all_commands = []
        for group, commands in self.commands.items():
            all_commands.extend([f"{group}:{cmd}" for cmd in commands])
            all_commands.extend(commands)
        
        # Find close matches
        matches = get_close_matches(invalid_command, all_commands, n=3, cutoff=0.6)
        return matches
    
    def _load_available_commands(self) -> Dict[str, List[str]]:
        """Load available commands for suggestion matching"""
        return {
            "chat": ["interactive"],
            "code": ["review", "generate", "explain"],
            "research": ["analyze", "summarize"],
            "config": ["init", "show", "validate"],
            "model": ["list", "select", "test"],
            "agent": ["list", "status"]
        }

# Global instances
error_analyzer = ErrorAnalyzer()
error_formatter = ErrorFormatter()
did_you_mean = DidYouMeanSuggester()

def handle_error(error: Exception, context: Optional[ErrorContext] = None, show_details: bool = True) -> int:
    """Main error handling function"""
    try:
        # Analyze the error
        swiss_error = error_analyzer.analyze_error(error, context or ErrorContext())
        
        # Format and display the error
        error_formatter.format_error(swiss_error, show_details)
        
        return swiss_error.exit_code
        
    except Exception as handling_error:
        # Fallback if error handling itself fails
        console.print(f"[red]Error handling failed: {handling_error}[/red]")
        console.print(f"[red]Original error: {error}[/red]")
        return 1

def suggest_command_fix(invalid_command: str) -> None:
    """Suggest command fixes for invalid commands"""
    suggestions = did_you_mean.suggest_command(invalid_command)
    
    if suggestions:
        console.print(f"\n[yellow]Command '{invalid_command}' not found.[/yellow]")
        console.print("[yellow]Did you mean one of these?[/yellow]")
        
        for suggestion in suggestions:
            console.print(f"  [cyan]swiss-ai {suggestion}[/cyan]")
        
        console.print(f"\n[dim]Use [cyan]swiss-ai --help[/cyan] for all available commands.[/dim]")

def create_error_context(
    command: Optional[str] = None,
    file_path: Optional[str] = None,
    user_input: Optional[str] = None
) -> ErrorContext:
    """Helper function to create error context"""
    return ErrorContext(
        command=command,
        file_path=file_path,
        user_input=user_input,
        system_info={"platform": sys.platform, "python_version": sys.version}
    )

# Decorator for automatic error handling
def with_error_handling(show_details: bool = True):
    """Decorator to add automatic error handling to functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = create_error_context(command=func.__name__)
                exit_code = handle_error(e, context, show_details)
                sys.exit(exit_code)
        return wrapper
    return decorator

# Async version of the decorator
def with_async_error_handling(show_details: bool = True):
    """Decorator for async functions with automatic error handling"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = create_error_context(command=func.__name__)
                exit_code = handle_error(e, context, show_details)
                sys.exit(exit_code)
        return wrapper
    return decorator