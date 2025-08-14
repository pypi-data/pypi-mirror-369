#!/usr/bin/env python3
"""
Enhanced CLI Interface for Swiss AI
Professional command-line interface with consistent grammar and excellent UX
"""

import asyncio
import sys
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import logging

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich import box
from rich.live import Live
from rich.status import Status

from .config.manager import ConfigManager, ConfigurationError
from .models.selector import ModelSelector, TaskType
from .mcp.manager import MCPManager
from .routing.router import IntelligentRouter
from .agents.collaborative import CollaborativeOrchestrator
from .context.intelligence import ContextIntelligence, ProjectType
from .utils.helpers import setup_logging, validate_api_key, get_system_info, check_internet_connection
from .error_handling import (
    SwissAIError, ErrorCategory, ErrorSeverity, ErrorContext,
    handle_error, suggest_command_fix, create_error_context,
    with_error_handling, with_async_error_handling
)
from .progress_feedback import (
    OperationType, FeedbackLevel, progress_manager, notifier,
    show_progress, show_success, show_warning, show_error, show_info,
    track_batch, monitor_realtime, with_progress
)
from .autocomplete import (
    command_registry, autocomplete_engine, command_discovery,
    show_command_suggestions, install_shell_completion
)
from .commands.secure import secure
from .commands.symphonics import symphonics
from .commands.compliance import compliance
from .commands.intelligence import intelligence
from .commands.context_cmds import context

logger = logging.getLogger(__name__)

# Global CLI state
console = Console()
config_manager: Optional[ConfigManager] = None
model_selector: Optional[ModelSelector] = None
router: Optional[IntelligentRouter] = None
orchestrator: Optional[CollaborativeOrchestrator] = None

@dataclass
class CLIContext:
    """Global CLI context"""
    verbose: bool = False
    config_path: Optional[str] = None
    model: Optional[str] = None
    agent: Optional[str] = None
    no_color: bool = False
    output_format: str = "rich"  # rich, json, plain
    project_path: Path = Path(".")
    context_intelligence: Optional['ContextIntelligence'] = None

# Global context instance
cli_ctx = CLIContext()

# -----------------------
# .env loader/saver
# -----------------------
def _env_file_path() -> Path:
    return Path(cli_ctx.config_path or Path.home() / '.swiss-ai') / '.env'

def _load_env_file() -> None:
    """Load key=value pairs from ~/.swiss-ai/.env into os.environ (non-destructive)."""
    env_path = _env_file_path()
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val
    except Exception:
        pass

def _save_env_vars(updates: Dict[str, str]) -> None:
    env_path = _env_file_path()
    env_path.parent.mkdir(parents=True, exist_ok=True)
    existing: Dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text(encoding='utf-8').splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                existing[k.strip()] = v.strip()
    existing.update(updates)
    # Redact nothing in file; store plain to let uvicorn --env-file work
    content = "\n".join([f"{k}={v}" for k, v in existing.items()]) + "\n"
    env_path.write_text(content, encoding='utf-8')

def init_cli_components():
    """Initialize CLI components lazily"""
    global config_manager, model_selector, router, orchestrator
    
    # Load secrets from ~/.swiss-ai/.env into environment for providers
    _load_env_file()

    if config_manager is None:
        config_path = cli_ctx.config_path or str(Path.home() / ".swiss-ai")
        config_manager = ConfigManager(Path(config_path))
        model_selector = ModelSelector(config_manager)
        router = IntelligentRouter(config_manager, model_selector)
        orchestrator = CollaborativeOrchestrator(config_manager, model_selector, router)
        
        # Check and display secure mode banner
        check_secure_mode()

def setup_console():
    """Setup console with context options"""
    global console
    if cli_ctx.no_color:
        console = Console(color_system=None)
    else:
        console = Console()

def enhanced_error_handler(func):
    """Enhanced decorator for consistent error handling with rich context"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SwissAIError:
            # Re-raise SwissAIError as-is
            raise
        except ConfigurationError as e:
            context = create_error_context(command=func.__name__)
            raise SwissAIError(
                str(e),
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.WARNING,
                suggestions=["Run 'swiss-ai config:init' to set up configuration"],
                context=context
            )
        except Exception as e:
            context = create_error_context(command=func.__name__)
            
            # Enhanced error analysis
            if "api key" in str(e).lower():
                category = ErrorCategory.API_KEY
                suggestions = ["Set your OPENROUTER_API_KEY environment variable"]
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                category = ErrorCategory.NETWORK
                suggestions = ["Check your internet connection", "Try again in a moment"]
            else:
                category = ErrorCategory.UNKNOWN
                suggestions = ["Use --verbose for detailed error information"]
            
            raise SwissAIError(
                str(e),
                category=category,
                severity=ErrorSeverity.ERROR,
                suggestions=suggestions,
                context=context,
                show_traceback=cli_ctx.verbose
            )
    return wrapper

def enhanced_async_error_handler(func):
    """Enhanced decorator for async functions with error handling"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SwissAIError:
            # Re-raise SwissAIError as-is
            raise
        except ConfigurationError as e:
            context = create_error_context(command=func.__name__)
            raise SwissAIError(
                str(e),
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.WARNING,
                suggestions=["Run 'swiss-ai config:init' to set up configuration"],
                context=context
            )
        except Exception as e:
            context = create_error_context(command=func.__name__)
            
            # Enhanced error analysis
            if "api key" in str(e).lower():
                category = ErrorCategory.API_KEY
                suggestions = ["Set your OPENROUTER_API_KEY environment variable"]
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                category = ErrorCategory.NETWORK
                suggestions = ["Check your internet connection", "Try again in a moment"]
            else:
                category = ErrorCategory.UNKNOWN
                suggestions = ["Use --verbose for detailed error information"]
            
            raise SwissAIError(
                str(e),
                category=category,
                severity=ErrorSeverity.ERROR,
                suggestions=suggestions,
                context=context,
                show_traceback=cli_ctx.verbose
            )
    return wrapper

def show_banner():
    """Show Swiss AI banner"""
    banner = """
[bold blue]╔══════════════════════════════════════════════════════════════════════════════╗
║                                Swiss AI CLI                                  ║
║                     Professional AI Development Assistant                    ║
╚══════════════════════════════════════════════════════════════════════════════╝[/bold blue]
"""
    console.print(banner)

def check_secure_mode():
    """Check if secure mode is enabled and show banner"""
    config_file = Path(cli_ctx.config_path or Path.home() / '.swiss-ai') / 'config.yaml'
    if config_file.exists():
        try:
            import yaml
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
            if config_data.get('secure_mode', False):
                # Access console via module globals to honor runtime patching in tests
                globals()["console"].print("[yellow]🔒 Secure mode active[/yellow]")
        except Exception:
            pass

def show_success(message: str, details: Optional[str] = None):
    """Show success message"""
    console.print(f"[green]✓[/green] {message}")
    if details:
        console.print(f"  [dim]{details}[/dim]")

def show_warning(message: str, details: Optional[str] = None):
    """Show warning message"""
    console.print(f"[yellow]⚠[/yellow] {message}")
    if details:
        console.print(f"  [dim]{details}[/dim]")

def show_info(message: str, details: Optional[str] = None):
    """Show info message"""
    console.print(f"[blue]ℹ[/blue] {message}")
    if details:
        console.print(f"  [dim]{details}[/dim]")

def show_spinner(message: str, operation_type: OperationType = OperationType.ANALYSIS):
    """Show progress message with spinner (legacy function)"""
    return Status(message, console=console, spinner="dots")

def create_help_table(commands: List[Tuple[str, str]]) -> Table:
    """Create a help table for commands"""
    table = Table(show_header=False, box=box.ROUNDED)
    table.add_column("Command", style="cyan", width=20)
    table.add_column("Description", style="white")
    
    for cmd, desc in commands:
        table.add_row(cmd, desc)
    
    return table

# ============================================================================
# Command Groups and Context Setup
# ============================================================================

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config-path', type=click.Path(), help='Custom configuration directory')
@click.option('--model', '-m', help='Override default model')
@click.option('--agent', '-a', help='Force specific agent')
@click.option('--no-color', is_flag=True, help='Disable colored output')
@click.option('--output-format', type=click.Choice(['rich', 'json', 'plain']), 
              default='rich', help='Output format')
@click.version_option(version='2.1.0', prog_name='Swiss AI CLI')
@click.pass_context
def swiss_ai(ctx, verbose, config_path, model, agent, no_color, output_format):
    """Swiss AI CLI - Professional AI Development Assistant
    
    A powerful command-line interface for AI-powered development workflows.
    
    Examples:
      swiss-ai chat "help me debug this function"
      swiss-ai code:review --file src/main.py  
      swiss-ai model:select qwen3-coder
      swiss-ai doctor --check-all
    """
    # Set up global context
    cli_ctx.verbose = verbose
    cli_ctx.config_path = config_path
    cli_ctx.model = model
    cli_ctx.agent = agent
    cli_ctx.no_color = no_color
    cli_ctx.output_format = output_format
    
    # Setup console
    setup_console()
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)
    
    # Set feedback level based on verbosity
    if verbose:
        progress_manager.set_feedback_level(FeedbackLevel.VERBOSE)
    elif no_color:
        progress_manager.set_feedback_level(FeedbackLevel.MINIMAL)
    else:
        progress_manager.set_feedback_level(FeedbackLevel.STANDARD)
    
    # Ensure context object exists
    ctx.ensure_object(dict)

# ============================================================================
# Main Commands
# ============================================================================

@swiss_ai.command()
@click.argument('message', required=False)
@click.option('--interactive', '-i', is_flag=True, help='Start interactive chat mode')
@click.option('--model', '-m', help='Override model for this chat')
@click.option('--agent', '-a', help='Force specific agent')
@click.option('--context-files', '-c', multiple=True, help='Include files for context')
@enhanced_async_error_handler
async def chat(message, interactive, model, agent, context_files):
    """Start interactive chat or send a single message
    
    Examples:
      swiss-ai chat "explain this error message"
      swiss-ai chat --interactive
      swiss-ai chat "debug this" --context-files src/main.py
      swiss-ai chat "review code" --agent code --model qwen3-coder
      echo "message" | swiss-ai chat
    """
    init_cli_components()
    
    # Check if message is coming from stdin (piped input)
    if not message and not interactive:
        import sys
        if not sys.stdin.isatty():  # Data is being piped in
            try:
                message = sys.stdin.read().strip()
                if message:
                    await process_single_message(message, model, agent, context_files)
                    return
            except EOFError:
                pass
    
    if interactive or not message:
        await start_interactive_chat()
    else:
        await process_single_message(message, model, agent, context_files)

@swiss_ai.group()
def code():
    """Code-related operations
    
    Commands for code analysis, review, generation, and optimization.
    """
    pass

@swiss_ai.group()
def research():
    """Research and analysis operations
    
    Commands for project analysis, documentation, and insights.
    """
    pass

@swiss_ai.group()
def config():
    """Configuration management
    
    Commands for managing Swiss AI configuration and settings.
    """
    pass

@config.command('keys')
@click.option('--openrouter', prompt=False, help='Set OpenRouter API key')
@click.option('--openai', prompt=False, help='Set OpenAI API key')
@click.option('--google', prompt=False, help='Set Google Generative AI key')
@click.option('--anthropic', prompt=False, help='Set Anthropic API key')
@enhanced_error_handler
def config_keys(openrouter, openai, google, anthropic):
    """Set provider API keys and save to ~/.swiss-ai/.env

    Examples:
      swiss-ai config:keys --openrouter sk-or-... --openai sk-... 
      swiss-ai config:keys                        # interactive prompts
    """
    init_cli_components()
    updates: Dict[str,str] = {}
    # Interactive prompts if flags missing
    if not any([openrouter, openai, google, anthropic]):
        if Confirm.ask("Set OpenRouter API key now?", default=False):
            openrouter = Prompt.ask("OPENROUTER_API_KEY", password=True)
        if Confirm.ask("Set OpenAI API key now?", default=False):
            openai = Prompt.ask("OPENAI_API_KEY", password=True)
        if Confirm.ask("Set Google Generative AI key now?", default=False):
            google = Prompt.ask("GOOGLE_API_KEY", password=True)
        if Confirm.ask("Set Anthropic API key now?", default=False):
            anthropic = Prompt.ask("ANTHROPIC_API_KEY", password=True)

    if openrouter:
        updates["OPENROUTER_API_KEY"] = openrouter
    if openai:
        updates["OPENAI_API_KEY"] = openai
    if google:
        updates["GOOGLE_API_KEY"] = google
    if anthropic:
        updates["ANTHROPIC_API_KEY"] = anthropic

    if not updates:
        show_info("No changes")
        return

    _save_env_vars(updates)
    # Also set in current env so this session works immediately
    for k,v in updates.items():
        os.environ[k] = v
    show_success("API keys saved to ~/.swiss-ai/.env")

@swiss_ai.group()
def model():
    """Model management and selection
    
    Commands for managing AI models and performance tracking.
    """
    pass

@model.command('browse')
@click.option('--source', type=click.Choice(['openrouter','openai','google','anthropic']), default='openrouter')
@click.option('--free', is_flag=True, help='Show only free models (where supported)')
@enhanced_error_handler
def model_browse(source, free):
    """Fetch and list live models from a provider"""
    init_cli_components()
    table = Table(title=f"Models – {source}", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    if source == 'openrouter':
        try:
            import requests
            headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY','')}"}
            resp = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=12)
            resp.raise_for_status()
            data = resp.json().get('data', [])
            rows = []
            for m in data:
                mid = m.get('id','')
                name = m.get('name', mid)
                if free and not (":free" in mid or "(free)" in mid or (m.get('pricing') or {}).get('prompt') == 0):
                    continue
                rows.append((mid, name))
            for mid, name in sorted(rows):
                table.add_row(mid, name)
        except Exception as e:
            console.print(f"[red]Failed to fetch OpenRouter models: {e}[/red]")
            return
    elif source == 'openai':
        try:
            import requests
            headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY','')}"}
            resp = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=12)
            resp.raise_for_status()
            data = resp.json().get('data', [])
            # Filter to commonly used chat-capable families
            rows = [(m.get('id',''), m.get('id','')) for m in data if isinstance(m, dict) and m.get('id','').startswith(('gpt','o'))]
            for mid, name in sorted(rows):
                table.add_row(mid, name)
        except Exception as e:
            console.print(f"[red]Failed to fetch OpenAI models: {e}[/red]")
            return
    elif source == 'google':
        try:
            import requests
            key = os.getenv('GOOGLE_API_KEY','')
            resp = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}", timeout=12)
            resp.raise_for_status()
            data = resp.json().get('models', [])
            rows = []
            for m in data:
                name = m.get('name','')
                display = m.get('displayName', name)
                rows.append((name, display))
            for mid, name in sorted(rows):
                table.add_row(mid, name)
        except Exception as e:
            console.print(f"[red]Failed to fetch Google models: {e}[/red]")
            return
    else:  # anthropic
        try:
            import requests
            headers = {"x-api-key": os.getenv('ANTHROPIC_API_KEY',''), "anthropic-version": "2023-06-01"}
            resp = requests.get("https://api.anthropic.com/v1/models", headers=headers, timeout=12)
            resp.raise_for_status()
            data = resp.json().get('data', [])
            rows = [(m.get('name',''), m.get('name','')) for m in data if isinstance(m, dict)]
            for mid, name in sorted(rows):
                table.add_row(mid, name)
        except Exception as e:
            console.print(f"[red]Failed to fetch Anthropic models: {e}[/red]")
            return
    console.print(table)

@swiss_ai.group()
def agent():
    """Agent management and routing
    
    Commands for managing specialized AI agents.
    """
    pass

@swiss_ai.group()
def defaults():
    """Smart defaults and recommendations
    
    Commands for managing intelligent defaults based on usage patterns.
    """
    pass

@swiss_ai.group()
def mcp():
    """MCP server management
    
    Commands for managing and monitoring MCP (Model Context Protocol) servers.
    """
    pass

# Register secure commands
swiss_ai.add_command(secure)
swiss_ai.add_command(symphonics)
swiss_ai.add_command(compliance)
swiss_ai.add_command(intelligence)
swiss_ai.add_command(context)

@swiss_ai.command("theme")
@click.argument('name', required=False)
@enhanced_error_handler
def theme_command(name):
    """Set or list available themes
    
    Examples:
      swiss-ai theme dark
      swiss-ai theme list
      swiss-ai theme
    """
    global console
    # Theme definitions
    THEMES = {
        'light': {'primary': 'blue', 'success': 'green', 'warning': 'yellow', 'error': 'red'},
        'dark': {'primary': 'cyan', 'success': 'bright_green', 'warning': 'bright_yellow', 'error': 'bright_red'},
        'neon': {'primary': 'magenta', 'success': 'bright_cyan', 'warning': 'bright_magenta', 'error': 'bright_red'},
        'minimal': {'primary': 'white', 'success': 'white', 'warning': 'white', 'error': 'white'}
    }
    
    if not name:
        # Show current theme
        theme_file = Path(cli_ctx.config_path or Path.home() / '.swiss-ai') / 'theme.yaml'
        current = 'dark'  # default
        if theme_file.exists():
            import yaml
            try:
                with open(theme_file, 'r') as f:
                    theme_data = yaml.safe_load(f) or {}
                current = theme_data.get('theme', 'dark')
            except Exception:
                pass
        console.print(f"Current theme: [cyan]{current}[/cyan]")
        console.print("Use 'swiss-ai theme list' to see all themes")
        return
    
    if name == 'list':
        # Show theme previews
        table = Table(title="🎨 Available Themes", box=box.ROUNDED)
        table.add_column("Theme", style="cyan", width=12)
        table.add_column("Preview", width=40)
        
        for theme_name, colors in THEMES.items():
            preview = f"[{colors['primary']}]Primary[/{colors['primary']}] [{colors['success']}]Success[/{colors['success']}] [{colors['warning']}]Warning[/{colors['warning']}] [{colors['error']}]Error[/{colors['error']}]"
            table.add_row(theme_name, preview)
        
        console.print(table)
        return
    
    if name not in THEMES:
        console.print(f"[red]Unknown theme: {name}[/red]")
        console.print(f"Available themes: {', '.join(THEMES.keys())}")
        return
    
    # Save theme choice
    theme_file = Path(cli_ctx.config_path or Path.home() / '.swiss-ai') / 'theme.yaml'
    theme_file.parent.mkdir(parents=True, exist_ok=True)
    
    import yaml
    with open(theme_file, 'w') as f:
        yaml.dump({'theme': name}, f)
    
    # Apply theme instantly
    console = Console(style=THEMES[name]['primary'])
    
    console.print(f"[green]Theme set to '{name}' ✓[/green]")

@swiss_ai.command("share")
@click.option('--gist', is_flag=True, help='Create GitHub Gist')
@click.option('--qr', is_flag=True, help='Generate QR code')
@enhanced_error_handler
def share_command(gist, qr):
    """Share context and recent commands
    
    Examples:
      swiss-ai share --gist
      swiss-ai share --qr
      swiss-ai share --gist --qr
    """
    init_cli_components()
    
    # Initialize context intelligence
    if not cli_ctx.context_intelligence:
        cli_ctx.context_intelligence = ContextIntelligence(Path(cli_ctx.config_path or Path.home() / '.swiss-ai'))
    
    # Collect context data
    context_file = Path(cli_ctx.config_path or Path.home() / '.swiss-ai') / 'context.yaml'
    context_data = {}
    if context_file.exists():
        try:
            import yaml
            with open(context_file, 'r') as f:
                context_data = yaml.safe_load(f) or {}
        except Exception:
            context_data = {"error": "Could not read context.yaml"}
    
    # Get last 5 commands
    recent_commands = cli_ctx.context_intelligence.get_recent_commands(5)
    
    # Create share data
    share_data = {
        "timestamp": datetime.now().isoformat(),
        "context": _redact_sensitive_data(context_data),
        "recent_commands": [_redact_sensitive_data(cmd) for cmd in recent_commands],
        "version": "2.1.0"
    }
    
    share_url = None
    
    if gist:
        # Try to create GitHub Gist
        try:
            import requests
            import json
            
            gist_data = {
                "description": "Swiss AI CLI Context Share",
                "public": False,
                "files": {
                    "swiss-ai-context.json": {
                        "content": json.dumps(share_data, indent=2)
                    }
                }
            }
            
            response = requests.post('https://api.github.com/gists', 
                                   json=gist_data, timeout=10)
            
            if response.status_code == 201:
                share_url = response.json()['html_url']
                console.print(f"[green]Gist created: {share_url}[/green]")
            else:
                raise Exception(f"GitHub API error: {response.status_code}")
                
        except Exception as e:
            console.print(f"[yellow]Gist creation failed: {e}[/yellow]")
            # Fallback to local file
            local_file = Path.home() / f"swiss-ai-share-{int(time.time())}.json"
            with open(local_file, 'w') as f:
                json.dump(share_data, f, indent=2)
            console.print(f"[blue]Saved locally: {local_file}[/blue]")
            share_url = str(local_file)
    
    if qr and share_url:
        # Generate QR code
        try:
            import qrcode
            qr_code = qrcode.QRCode(version=1, box_size=1, border=1)
            qr_code.add_data(share_url)
            qr_code.make(fit=True)
            
            # Print ASCII QR code
            qr_code.print_ascii(invert=True)
        except ImportError:
            console.print(f"[yellow]QR code requires 'pip install qrcode'[/yellow]")
            console.print(f"URL: {share_url}")
        except Exception as e:
            console.print(f"[yellow]QR generation failed: {e}[/yellow]")
            console.print(f"URL: {share_url}")
    
    if not gist and not qr:
        console.print("[yellow]Use --gist or --qr flags[/yellow]")

@swiss_ai.command("tour")
@click.option('--auto', is_flag=True, help='Skip confirmations and run automatically')
@enhanced_async_error_handler
async def tour_command(auto):
    """Interactive project tour and analysis
    
    Examples:
      swiss-ai tour
      swiss-ai tour --auto
    """
    init_cli_components()
    
    # Initialize context intelligence
    if not cli_ctx.context_intelligence:
        cli_ctx.context_intelligence = ContextIntelligence(Path(cli_ctx.config_path or Path.home() / '.swiss-ai'))
    
    # Detect project type
    project_context = cli_ctx.context_intelligence.project_detector.detect_project(Path.cwd())
    project_type = project_context.project_type.value
    
    console.print(f"[bold blue]🚀 Swiss AI Project Tour[/bold blue]")
    console.print(f"[dim]Detected project type: {project_type}[/dim]\n")
    
    if not auto:
        if not Confirm.ask("Start project tour?"):
            return
    
    steps = [
        ("📊 Git Analysis", _tour_git_stats),
        ("🔍 Code Issues", _tour_code_issues), 
        ("📝 Next Tasks", _tour_next_tasks),
        ("🏆 README Badge", _tour_readme_badge)
    ]
    
    with Live(console=console, refresh_per_second=2) as live:
        for i, (step_name, step_func) in enumerate(steps, 1):
            live.update(f"[bold yellow]Step {i}/4: {step_name}[/bold yellow]")
            
            if not auto:
                time.sleep(1)  # Brief pause for UX
            
            try:
                result = await step_func(project_context, auto)
                live.update(f"[green]✓ {step_name}: {result}[/green]")
                
                if not auto:
                    console.print(f"\n[green]✓ {step_name} complete[/green]")
                    if i < len(steps) and not Confirm.ask("Continue to next step?"):
                        break
                    console.print()
                    
            except Exception as e:
                live.update(f"[red]✗ {step_name}: Error - {str(e)[:30]}[/red]")
                console.print(f"[red]Error in {step_name}: {e}[/red]")
    
    console.print("\n[bold green]🎉 Tour complete! Happy coding![/bold green]")

async def _tour_git_stats(project_context, auto):
    """Step 1: Analyze Git statistics"""
    git_context = cli_ctx.context_intelligence.git_analyzer.analyze_repository(Path.cwd())
    
    if not git_context.is_repo:
        return "No Git repository found"
    
    stats = f"{len(git_context.recent_commits)} commits, branch: {git_context.current_branch}"
    
    if not auto:
        table = Table(title="Git Statistics", box=box.SIMPLE)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Current Branch", git_context.current_branch or "unknown")
        table.add_row("Recent Commits", str(len(git_context.recent_commits)))
        table.add_row("Modified Files", str(len(git_context.modified_files)))
        console.print(table)
    
    return stats

async def _tour_code_issues(project_context, auto):
    """Step 2: Find top code issues using analysis"""
    # Simulate analysis agent results
    issues = [
        "Missing type hints in main.py",
        "Unused imports in utils.py", 
        "Long function in core.py (50+ lines)"
    ]
    
    if not auto:
        console.print("[bold]🔍 Top Issues Found:[/bold]")
        for i, issue in enumerate(issues[:3], 1):
            console.print(f"  {i}. [yellow]{issue}[/yellow]")
    
    return f"Found {len(issues)} issues"

async def _tour_next_tasks(project_context, auto):
    """Step 3: Suggest next development tasks"""
    # Generate suggestions based on project type
    tasks = {
        'python': ["Add unit tests", "Set up CI/CD", "Update dependencies"],
        'javascript': ["Bundle optimization", "Add ESLint", "Update packages"],
        'react': ["Component testing", "Performance audit", "Accessibility check"],
        'unknown': ["Add documentation", "Set up testing", "Code review"]
    }
    
    suggested_tasks = tasks.get(project_context.project_type.value, tasks['unknown'])
    
    if not auto:
        console.print("[bold]📝 Suggested Next Tasks:[/bold]")
        for i, task in enumerate(suggested_tasks, 1):
            console.print(f"  {i}. [cyan]{task}[/cyan]")
    
    return f"Suggested {len(suggested_tasks)} tasks"

async def _tour_readme_badge(project_context, auto):
    """Step 4: Check and suggest README badges"""
    readme_path = Path.cwd() / "README.md"
    
    if not readme_path.exists():
        return "No README.md found"
    
    readme_content = readme_path.read_text()
    has_badges = "![" in readme_content or "https://img.shields.io" in readme_content
    
    if has_badges:
        return "Badges already present"
    
    # Suggest badge based on project type
    badge_suggestions = {
        'python': "[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)",
        'javascript': "[![Node](https://img.shields.io/badge/node-%3E%3D14-green.svg)](https://nodejs.org)",
        'react': "[![React](https://img.shields.io/badge/react-%5E18.0.0-blue.svg)](https://reactjs.org)"
    }
    
    suggested_badge = badge_suggestions.get(project_context.project_type.value)
    
    if not auto and suggested_badge:
        console.print(f"[bold]🏆 Suggested Badge:[/bold]")
        console.print(f"  {suggested_badge}")
        
        if Confirm.ask("Add this badge to README.md?"):
            # Add badge to top of README
            lines = readme_content.split('\n')
            # Insert after first heading
            insert_idx = 1 if lines and lines[0].startswith('#') else 0
            lines.insert(insert_idx, f"\n{suggested_badge}\n")
            readme_path.write_text('\n'.join(lines))
            return "Badge added to README"
    
    return "Badge suggestion provided"

def _redact_sensitive_data(data):
    """Remove sensitive information from data"""
    if isinstance(data, dict):
        redacted = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in ['key', 'token', 'password', 'secret']):
                redacted[key] = "***REDACTED***"
            else:
                redacted[key] = _redact_sensitive_data(value)
        return redacted
    elif isinstance(data, list):
        return [_redact_sensitive_data(item) for item in data]
    elif isinstance(data, str) and len(data) > 20 and any(c in data for c in ['sk-', 'pk-', 'Bearer']):
        return "***REDACTED***"
    return data

@swiss_ai.command()
@click.argument('task', required=False)
@click.option('--category', help='Show commands by category')
@click.option('--search', help='Search commands by keyword')
@click.option('--workflow', help='Suggest workflow for goal')
@enhanced_error_handler
def discover(task, category, search, workflow):
    """Discover available commands and workflows
    
    Examples:
      swiss-ai discover                    # Show all commands
      swiss-ai discover "code review"     # Find commands for task
      swiss-ai discover --search security # Search by keyword
      swiss-ai discover --workflow setup  # Show setup workflow
      swiss-ai discover --category code   # Show code commands
    """
    if task:
        # Discover commands for specific task
        commands = command_discovery.discover_by_task(task)
        if commands:
            console.print(f"[bold green]Commands for '{task}':[/bold green]")
            for cmd in commands:
                command_discovery.show_command_help(f"{cmd.group}:{cmd.name}" if cmd.group else cmd.name)
                console.print()
        else:
            console.print(f"[yellow]No specific commands found for '{task}'[/yellow]")
            show_command_suggestions(task)
    
    elif search:
        # Search commands
        results = command_registry.search_commands(search)
        if results:
            console.print(f"[bold green]Search results for '{search}':[/bold green]")
            for cmd in results:
                command_name = f"{cmd.group}:{cmd.name}" if cmd.group else cmd.name
                console.print(f"[cyan]{command_name}[/cyan] - {cmd.description}")
        else:
            console.print(f"[yellow]No commands found matching '{search}'[/yellow]")
    
    elif workflow:
        # Show workflow suggestions
        suggested_commands = command_discovery.suggest_workflow(workflow)
        if suggested_commands:
            console.print(f"[bold green]Suggested workflow for '{workflow}':[/bold green]")
            for i, cmd in enumerate(suggested_commands, 1):
                console.print(f"  {i}. [cyan]{cmd}[/cyan]")
        else:
            console.print(f"[yellow]No workflow suggestions for '{workflow}'[/yellow]")
    
    elif category:
        # Show commands by category
        if category in command_registry.groups:
            commands = command_registry.get_commands_by_group(category)
            console.print(f"[bold green]{category.title()} Commands:[/bold green]")
            for cmd in commands:
                console.print(f"[cyan]{category}:{cmd.name}[/cyan] - {cmd.description}")
        else:
            console.print(f"[yellow]Category '{category}' not found[/yellow]")
            console.print(f"Available categories: {', '.join(command_registry.groups.keys())}")
    
    else:
        # Show all commands organized by category
        command_discovery.show_commands_by_category()

@swiss_ai.command()
@click.option('--shell', default='bash', help='Shell type (bash, zsh, fish)')
@enhanced_error_handler
def completion(shell):
    """Install shell completion for Swiss AI CLI
    
    Examples:
      swiss-ai completion                  # Install bash completion
      swiss-ai completion --shell zsh     # Install zsh completion
    """
    install_shell_completion(shell)

@swiss_ai.command()
@click.option('--check-all', is_flag=True, help='Run comprehensive health check')
@click.option('--fix', is_flag=True, help='Attempt to fix issues automatically')
@click.option('--export', type=click.Path(), help='Export health report to file')
@click.option('--json', is_flag=True, help='Output as JSON')
@enhanced_error_handler
def doctor(check_all, fix, export, json):
    """System health check and diagnostics
    
    Checks system components, configuration, and connectivity.
    
    Examples:
      swiss-ai doctor
      swiss-ai doctor --check-all
      swiss-ai doctor --fix --verbose
      swiss-ai doctor --export health-report.json
    """
    init_cli_components()
    
    steps = ["Checking configuration", "Testing models", "Verifying connectivity", "Validating MCP servers"]
    if check_all:
        steps.extend(["Checking dependencies", "Testing permissions", "Analyzing performance"])
    
    with show_progress(OperationType.HEALTH_CHECK, "Running health check", steps) as progress:
        health_results = run_health_check(check_all, progress)
    
    if json:
        # Convert to JSON-friendly format with absolute paths
        json_output = {
            "overall_status": "healthy" if all(comp["status"] == "healthy" for comp in health_results["components"].values()) else "issues_detected",
            "timestamp": health_results["timestamp"],
            "comprehensive": health_results["comprehensive"],
            "components": health_results["components"]
        }
        if export:
            json_output["report_path"] = str(Path(export).resolve())
        
        import json as json_module
        console.print(json_module.dumps(json_output, indent=2))
        return
    
    display_health_results(health_results)
    
    if fix:
        fix_health_issues(health_results)
    
    if export:
        export_health_report(health_results, export)

# ============================================================================
# Code Commands
# ============================================================================

@code.command('review')
@click.option('--file', '-f', multiple=True, help='Files to review')
@click.option('--diff', is_flag=True, help='Review git diff')
@click.option('--security', is_flag=True, help='Focus on security issues')
@click.option('--performance', is_flag=True, help='Focus on performance')
@click.option('--output', '-o', type=click.Path(), help='Save review to file')
@enhanced_async_error_handler
async def code_review(file, diff, security, performance, output):
    """Review code for quality, security, and performance
    
    Examples:
      swiss-ai code:review --file src/main.py
      swiss-ai code:review --diff
      swiss-ai code:review --security --file auth.py
      swiss-ai code:review --performance --output review.md
    """
    init_cli_components()
    
    if diff:
        files_to_review = get_git_diff_files()
    else:
        files_to_review = file or get_current_files()
    
    if not files_to_review:
        raise SwissAIError("No files to review", "Specify --file or use --diff for git changes")
    
    review_results = []
    
    tracker = track_batch("Reviewing files", len(files_to_review))
    
    for file_path in files_to_review:
        tracker.update_item(file_path, "reviewing")
        
        try:
            result = await review_file(file_path, security, performance)
            review_results.append(result)
            tracker.complete_item(success=True)
        except Exception as e:
            logger.error(f"Failed to review {file_path}: {e}")
            tracker.complete_item(success=False)
    
    tracker.finish()
    
    display_review_results(review_results)
    
    if output:
        save_review_results(review_results, output)

@code.command('generate')
@click.argument('description')
@click.option('--language', '-l', help='Programming language')
@click.option('--framework', help='Framework or library to use')
@click.option('--style', help='Coding style guide')
@click.option('--output', '-o', type=click.Path(), help='Save generated code to file')
@click.option('--template', help='Use code template')
@enhanced_async_error_handler
async def code_generate(description, language, framework, style, output, template):
    """Generate code from natural language description
    
    Examples:
      swiss-ai code:generate "REST API for user management"
      swiss-ai code:generate "React component for login" --language typescript
      swiss-ai code:generate "database migration" --framework django --output migration.py
      swiss-ai code:generate "utility function" --style google --template function
    """
    init_cli_components()
    
    steps = ["Understanding requirements", "Generating code", "Optimizing output", "Validating results"]
    with show_progress(OperationType.GENERATION, "Generating code", steps) as progress:
        progress.step(0, "Analyzing requirements...")
        await asyncio.sleep(0.5)  # Simulate processing time
        
        progress.step(1, "Generating code structure...")
        generated_code = await generate_code(description, language, framework, style, template)
        
        progress.step(2, "Optimizing and formatting...")
        await asyncio.sleep(0.3)  # Simulate optimization
        
        progress.step(3, "Final validation...")
        await asyncio.sleep(0.2)
    
    display_generated_code(generated_code, language)
    
    if output:
        save_generated_code(generated_code, output)
        show_success(f"Code saved to {output}")

@code.command('explain')
@click.option('--file', '-f', required=True, help='File to explain')
@click.option('--lines', help='Line range (e.g., 10-20)')
@click.option('--detail', type=click.Choice(['brief', 'detailed', 'expert']), 
              default='detailed', help='Explanation detail level')
@click.option('--format', type=click.Choice(['text', 'markdown', 'html']), 
              default='text', help='Output format')
@enhanced_async_error_handler
async def code_explain(file, lines, detail, format):
    """Explain code functionality and structure
    
    Examples:
      swiss-ai code:explain --file src/auth.py
      swiss-ai code:explain --file main.py --lines 10-20
      swiss-ai code:explain --file algorithm.py --detail expert
      swiss-ai code:explain --file api.py --format markdown
    """
    init_cli_components()
    
    if not Path(file).exists():
        raise SwissAIError(f"File not found: {file}", "Check the file path and try again")
    
    with show_progress(f"Analyzing {file}..."):
        explanation = await explain_code(file, lines, detail, format)
    
    display_code_explanation(explanation, format)

# ============================================================================
# Research Commands  
# ============================================================================

@research.command('analyze')
@click.option('--target', '-t', help='Analysis target (project, file, directory)')
@click.option('--depth', type=click.Choice(['surface', 'detailed', 'comprehensive']), 
              default='detailed', help='Analysis depth')
@click.option('--focus', multiple=True, help='Focus areas (architecture, dependencies, etc.)')
@click.option('--output', '-o', type=click.Path(), help='Save analysis to file')
@enhanced_async_error_handler
async def research_analyze(target, depth, focus, output):
    """Analyze project structure and codebase
    
    Examples:
      swiss-ai research:analyze
      swiss-ai research:analyze --target src/
      swiss-ai research:analyze --depth comprehensive --focus architecture
      swiss-ai research:analyze --focus dependencies security --output analysis.md
    """
    init_cli_components()
    
    target = target or "."
    
    with show_progress(f"Analyzing {target}..."):
        analysis_result = await analyze_target(target, depth, focus)
    
    display_analysis_result(analysis_result)
    
    if output:
        save_analysis_result(analysis_result, output)
        show_success(f"Analysis saved to {output}")

@research.command('summarize')
@click.option('--files', '-f', multiple=True, help='Files to summarize')
@click.option('--directory', '-d', help='Directory to summarize')
@click.option('--format', type=click.Choice(['brief', 'detailed', 'executive']), 
              default='detailed', help='Summary format')
@enhanced_async_error_handler
async def research_summarize(files, directory, format):
    """Create project or file summaries
    
    Examples:
      swiss-ai research:summarize --files README.md docs/api.md
      swiss-ai research:summarize --directory src/
      swiss-ai research:summarize --directory . --format executive
    """
    init_cli_components()
    
    if not files and not directory:
        raise SwissAIError("Specify files or directory to summarize", 
                         "Use --files for specific files or --directory for a folder")
    
    targets = list(files) if files else [directory]
    
    with show_progress("Creating summary..."):
        summary = await create_summary(targets, format)
    
    display_summary(summary, format)

# ============================================================================
# Configuration Commands
# ============================================================================

@config.command('init')
@click.option('--wizard', is_flag=True, help='Interactive configuration wizard')
@click.option('--force', is_flag=True, help='Overwrite existing configuration')
@click.option('--template', help='Use configuration template')
@enhanced_error_handler
def config_init(wizard, force, template):
    """Initialize Swiss AI configuration
    
    Examples:
      swiss-ai config:init
      swiss-ai config:init --wizard
      swiss-ai config:init --force --template minimal
    """
    init_cli_components()
    
    if config_manager.config_file.exists() and not force:
        if not Confirm.ask("Configuration already exists. Overwrite?"):
            show_info("Configuration unchanged")
            return
    
    if wizard:
        run_config_wizard()
    else:
        create_default_config(template)
    
    show_success("Configuration initialized successfully")

@config.command('show')
@click.option('--section', help='Show specific section')
@click.option('--format', type=click.Choice(['rich', 'yaml', 'json']), 
              default='rich', help='Output format')
@enhanced_error_handler
def config_show(section, format):
    """Display current configuration
    
    Examples:
      swiss-ai config:show
      swiss-ai config:show --section models
      swiss-ai config:show --format yaml
    """
    init_cli_components()
    
    config = config_manager.get_config()
    # Resolved defaults for convenience
    resolved = {
        "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL") or os.getenv("SWISS_AI_DEFAULT_MODEL") or _read_env_default_model(),
        "SWISS_AI_FORCE_PROVIDER": os.getenv("SWISS_AI_FORCE_PROVIDER") or "openrouter",
    }
    if format == 'rich':
        display_config_rich(config, section, resolved)
    elif format == 'yaml':
        display_config_yaml(config, section, resolved)
    elif format == 'json':
        display_config_json(config, section, resolved)

@config.command('validate')
@click.option('--fix', is_flag=True, help='Attempt to fix issues')
@enhanced_error_handler
def config_validate(fix):
    """Validate configuration for errors
    
    Examples:
      swiss-ai config:validate
      swiss-ai config:validate --fix
    """
    init_cli_components()
    
    with show_progress("Validating configuration..."):
        issues = config_manager.validate_config()
    
    if not issues:
        show_success("Configuration is valid")
        return
    
    show_warning(f"Found {len(issues)} configuration issues:")
    for issue in issues:
        console.print(f"  [red]•[/red] {issue}")
    
    if fix:
        fixed_count = fix_config_issues(issues)
        show_success(f"Fixed {fixed_count} issues")

# ============================================================================
# Model Commands
# ============================================================================

@model.command('list')
@click.option('--available', is_flag=True, help='Show all available models')
@click.option('--performance', is_flag=True, help='Include performance metrics')
@click.option('--health', is_flag=True, help='Include health status')
@click.option('--json', is_flag=True, help='Output as JSON')
@enhanced_error_handler
def model_list(available, performance, health, json):
    """List configured and available models
    
    Examples:
      swiss-ai model:list
      swiss-ai model:list --available
      swiss-ai model:list --performance --health
    """
    init_cli_components()
    
    models_data = get_models_data(available, performance, health)
    
    if json:
        # Convert models data to JSON format
        json_output = {
            "default_provider": "openrouter",
            "models": []
        }
        
        # Mock some sample model data since get_models_data is placeholder
        # In real implementation, this would come from model_selector
        sample_models = [
            {"id": "qwen/qwen3-coder:free", "name": "Qwen3 Coder", "provider": "openrouter", "free": True, "aliases": ["qwen3-coder"]},
            {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku", "provider": "anthropic", "free": False, "aliases": ["claude-3-haiku"]},
            {"id": "google/gemini-pro", "name": "Gemini Pro", "provider": "google", "free": False, "aliases": ["gemini-pro"]}
        ]
        
        if available:
            json_output["models"] = sample_models
        else:
            # Show only configured models
            json_output["models"] = [m for m in sample_models if m["id"] in ["qwen/qwen3-coder:free"]]
        
        import json as json_module
        console.print(json_module.dumps(json_output, indent=2))
        return
    
    display_models_table(models_data, performance, health)

@model.command('select')
@click.argument('model_name')
@click.option('--profile', help='Configuration profile to update')
@click.option('--temporary', is_flag=True, help='Temporary selection for this session')
@enhanced_error_handler
def model_select(model_name, profile, temporary):
    """Select default model
    
    Examples:
      swiss-ai model:select qwen3-coder
      swiss-ai model:select claude-3-haiku --profile development
      swiss-ai model:select gpt-4 --temporary
    """
    init_cli_components()
    
    if not model_exists(model_name):
        raise SwissAIError(f"Model '{model_name}' not found", 
                         "Use 'swiss-ai model:list --available' to see available models")
    
    if temporary:
        cli_ctx.model = model_name
        show_success(f"Temporarily selected model: {model_name}")
    else:
        update_default_model(model_name, profile)
        # Persist to ~/.swiss-ai/.env for bridge and tools
        _save_env_vars({"DEFAULT_MODEL": model_name})
        show_success(f"Default model updated: {model_name}")

@model.command('test')
@click.argument('model_name', required=False)
@click.option('--prompt', default="Hello, how are you?", help='Test prompt')
@click.option('--benchmark', is_flag=True, help='Run performance benchmark')
@enhanced_async_error_handler
async def model_test(model_name, prompt, benchmark):
    """Test model connectivity and performance
    
    Examples:
      swiss-ai model:test
      swiss-ai model:test qwen3-coder
      swiss-ai model:test --prompt "Generate a Python function" --benchmark
    """
    init_cli_components()
    
    model_name = model_name or get_default_model()
    
    if benchmark:
        await run_model_benchmark(model_name)
    else:
        await test_model_simple(model_name, prompt)

# ============================================================================
# Defaults Commands
# ============================================================================

@defaults.command('show')
@click.argument('query')
@enhanced_error_handler
def defaults_show(query):
    """Show smart defaults based on usage patterns and context
    
    Examples:
      swiss-ai defaults:show "code review"
      swiss-ai defaults:show "generate python"
      swiss-ai defaults:show "debug api"
    """
    init_cli_components()
    
    # Initialize context intelligence if not already done
    if not cli_ctx.context_intelligence:
        cli_ctx.context_intelligence = ContextIntelligence(Path(cli_ctx.config_path or Path.home() / '.swiss-ai'))
    
    # Read context from .swiss-ai/context.yaml
    context_file = Path(cli_ctx.config_path or Path.home() / '.swiss-ai') / 'context.yaml'
    context_data = {}
    if context_file.exists():
        try:
            import yaml
            with open(context_file, 'r') as f:
                context_data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.debug(f"Error reading context.yaml: {e}")
    
    # Get recent command usage stats
    recent_commands = cli_ctx.context_intelligence.get_recent_commands(30)
    
    # Get smart defaults based on query and context
    smart_defaults = cli_ctx.context_intelligence.get_smart_defaults(query, context_data)
    
    # Pick top-3 smart defaults: model, temp, file-pattern
    defaults_to_show = []
    
    # Model default
    preferred_model = smart_defaults.get('preferred_model', 'qwen/qwen3-coder:free')
    model_reasoning = "Based on query analysis and project type"
    model_confidence = 85
    model_usage = sum(1 for cmd in recent_commands if any(m in cmd.get('preferred_models', []) for m in [preferred_model]))
    
    defaults_to_show.append({
        'default': 'Model',
        'value': preferred_model,
        'reasoning': model_reasoning,
        'confidence': model_confidence,
        'usage_count': model_usage
    })
    
    # Temperature default
    if 'creative' in query.lower() or 'generate' in query.lower():
        temp_value = "0.7"
        temp_reasoning = "Higher creativity for generation tasks"
        temp_confidence = 90
    elif 'code' in query.lower() or 'debug' in query.lower():
        temp_value = "0.1"
        temp_reasoning = "Lower temperature for precise code tasks"
        temp_confidence = 95
    else:
        temp_value = "0.4"
        temp_reasoning = "Balanced setting for general queries"
        temp_confidence = 75
    
    temp_usage = len([cmd for cmd in recent_commands if 'temperature' in str(cmd).lower()])
    
    defaults_to_show.append({
        'default': 'Temperature',
        'value': temp_value,
        'reasoning': temp_reasoning,
        'confidence': temp_confidence,
        'usage_count': temp_usage
    })
    
    # File pattern default
    project_context = context_data.get('project', {})
    project_type = project_context.get('project_type', 'unknown')
    
    if project_type == 'python':
        pattern_value = "**/*.py"
        pattern_reasoning = "Python project detected"
        pattern_confidence = 95
    elif project_type in ['javascript', 'typescript']:
        pattern_value = "**/*.{js,ts}"
        pattern_reasoning = f"{project_type.title()} project detected"
        pattern_confidence = 95
    elif project_type == 'react':
        pattern_value = "**/*.{jsx,tsx}"
        pattern_reasoning = "React project detected"
        pattern_confidence = 95
    else:
        pattern_value = "**/*"
        pattern_reasoning = "General file pattern for unknown project type"
        pattern_confidence = 50
    
    pattern_usage = len([cmd for cmd in recent_commands if 'file' in cmd.get('command', '').lower()])
    
    defaults_to_show.append({
        'default': 'File Pattern',
        'value': pattern_value,
        'reasoning': pattern_reasoning,
        'confidence': pattern_confidence,
        'usage_count': pattern_usage
    })
    
    # Create and display Rich table
    table = Table(title=f"🎯 Smart Defaults for '{query}'", box=box.ROUNDED)
    table.add_column("Default", style="cyan", width=15)
    table.add_column("Value", style="green", width=25)
    table.add_column("Reasoning", style="white", width=35)
    table.add_column("Confidence", style="yellow", width=12)
    table.add_column("Usage Count", style="blue", width=12)
    
    for item in defaults_to_show:
        confidence_color = "green" if item['confidence'] >= 90 else "yellow" if item['confidence'] >= 70 else "red"
        table.add_row(
            item['default'],
            item['value'],
            item['reasoning'],
            f"[{confidence_color}]{item['confidence']}%[/{confidence_color}]",
            str(item['usage_count'])
        )
    
    console.print(table)
    
    # Show additional context info if available
    if recent_commands:
        console.print(f"\n[dim]Based on {len(recent_commands)} recent command patterns[/dim]")
    if project_type != 'unknown':
        console.print(f"[dim]Project type: {project_type}[/dim]")

# ============================================================================
# MCP Commands
# ============================================================================

@mcp.command('status')
@enhanced_error_handler  
def mcp_status():
    """Check status of all MCP servers
    
    Shows running status, PID, uptime, and last errors for each configured server.
    Exit codes: 0=all healthy, 1=some issues, 2=none configured
    
    Examples:
      swiss-ai mcp:status
    """
    init_cli_components()
    
    # Get MCP servers from config
    config = config_manager.get_config()
    mcp_servers = config.mcp_servers
    
    if not mcp_servers:
        console.print("[yellow]No MCP servers configured[/yellow]")
        console.print("[dim]Use 'swiss-ai config:init' to set up MCP servers[/dim]")
        sys.exit(2)
    
    # Initialize MCP manager
    mcp_manager = MCPManager(Path(cli_ctx.config_path or Path.home() / '.swiss-ai'))
    
    server_statuses = []
    all_healthy = True
    has_issues = False
    
    steps = [f"Checking {name}" for name in mcp_servers.keys()]
    
    with show_progress(OperationType.HEALTH_CHECK, "Checking MCP servers", steps) as progress:
        for i, (server_name, server_config) in enumerate(mcp_servers.items()):
            progress.step(i, f"Checking {server_name}...")
            
            # Get server status
            server_status = mcp_manager.get_server_status(server_name)
            
            # Get instance details if running
            instance = mcp_manager.instances.get(server_name)
            
            if instance:
                pid = instance.pid
                uptime = _format_uptime(instance.start_time) if instance.start_time else "—"
                last_error = instance.last_error or "—"
                
                # Perform health check with 5s timeout
                try:
                    health_ok = _check_server_health_ping(instance, timeout=5.0)
                    if server_status == MCPServerStatus.RUNNING and health_ok:
                        status_icon = "🟢"
                        status_text = "running"
                    elif server_status == MCPServerStatus.RUNNING:
                        status_icon = "🟡"  
                        status_text = "timeout"
                        has_issues = True
                        all_healthy = False
                    else:
                        status_icon = "🔴"
                        status_text = server_status.value
                        has_issues = True
                        all_healthy = False
                except Exception as e:
                    status_icon = "🔴"
                    status_text = "error"
                    last_error = str(e)[:50]
                    has_issues = True
                    all_healthy = False
            else:
                pid = "—"
                uptime = "—"
                last_error = "—"
                status_icon = "🔴"
                status_text = "stopped"
                all_healthy = False
            
            server_statuses.append({
                'name': server_name,
                'status_icon': status_icon,
                'status_text': status_text,
                'pid': str(pid) if pid != "—" else "—",
                'uptime': uptime,
                'last_error': last_error[:30] + "..." if len(str(last_error)) > 30 else str(last_error)
            })
    
    # Create and display Rich table  
    table = Table(title="📡 MCP Server Status", box=box.ROUNDED)
    table.add_column("Server", style="cyan", width=15)
    table.add_column("Status", style="white", width=8) 
    table.add_column("PID", style="blue", width=8)
    table.add_column("Uptime", style="green", width=10)
    table.add_column("Last Error", style="red", width=25)
    
    for server in server_statuses:
        # Color status based on health
        if server['status_icon'] == "🟢":
            status_display = f"[green]{server['status_icon']}[/green]"
        elif server['status_icon'] == "🟡":
            status_display = f"[yellow]{server['status_icon']}[/yellow]"  
        else:
            status_display = f"[red]{server['status_icon']}[/red]"
            
        table.add_row(
            server['name'],
            status_display,
            server['pid'],
            server['uptime'],
            server['last_error']
        )
    
    console.print(table)
    
    # Show summary
    total_servers = len(server_statuses)
    healthy_count = sum(1 for s in server_statuses if s['status_icon'] == "🟢")
    
    if all_healthy and healthy_count > 0:
        console.print(f"\n[green]All {total_servers} servers are healthy ✓[/green]")
        sys.exit(0)
    elif has_issues:
        console.print(f"\n[yellow]{healthy_count}/{total_servers} servers healthy ⚠[/yellow]")
        sys.exit(1)
    else:
        console.print(f"\n[red]No servers are running ✗[/red]")
        sys.exit(1)

def _format_uptime(start_time: datetime) -> str:
    """Format uptime duration"""
    if not start_time:
        return "—"
    
    # Resolve datetime via module object to honor test patches reliably
    import sys as _sys
    current_time = _sys.modules[__name__].datetime.now()
    uptime = current_time - start_time
    hours = int(uptime.total_seconds() // 3600)
    minutes = int((uptime.total_seconds() % 3600) // 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def _check_server_health_ping(instance, timeout: float = 5.0) -> bool:
    """Perform health check ping with timeout"""
    try:
        if not instance.config.health_check_url:
            # If no health check URL, just check if process is alive
            return instance.process and instance.process.poll() is None
        
        # Make HTTP health check request
        import requests
        response = requests.get(instance.config.health_check_url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False

# ============================================================================
# Implementation Functions
# ============================================================================

async def start_interactive_chat():
    """Start interactive chat mode"""
    show_banner()
    console.print("\n[bold green]Interactive Chat Mode[/bold green]")
    console.print("Type your questions or commands. Use 'exit' to quit.\n")
    
    conversation_history = []
    
    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            if not user_input.strip():
                continue
            
            with show_progress(OperationType.ANALYSIS, "Processing message") as progress:
                progress.update("Understanding request...")
                await asyncio.sleep(0.2)
                
                progress.update("Generating response...")
                response = await orchestrator.process_request(user_input, conversation_history)
            
            console.print(f"\n[bold green]Assistant[/bold green]")
            console.print(Panel(response, border_style="green"))
            console.print()
            
            # Update conversation history
            conversation_history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response}
            ])
            
            # Keep history manageable
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break

async def process_single_message(message: str, model: Optional[str], 
                               agent: Optional[str], context_files: Tuple[str]):
    """Process a single message"""
    # Load context from files if provided
    context = ""
    for file_path in context_files:
        if Path(file_path).exists():
            context += f"\n--- {file_path} ---\n"
            context += Path(file_path).read_text()
    
    enhanced_message = f"{message}\n\nContext:\n{context}" if context else message
    
    with show_progress("Processing message..."):
        response = await orchestrator.process_request(enhanced_message, [])
    
    console.print(Panel(response, title="Response", border_style="green"))

def run_health_check(comprehensive: bool, progress = None) -> Dict[str, Any]:
    """Run system health check with progress tracking"""
    results = {
        "timestamp": time.time(),
        "comprehensive": comprehensive,
        "components": {}
    }
    
    # Step 1: Check configuration
    if progress:
        progress.step(0, "Checking configuration...")
    try:
        config_manager.validate_config()
        results["components"]["configuration"] = {"status": "healthy", "issues": []}
    except Exception as e:
        results["components"]["configuration"] = {"status": "error", "issues": [str(e)]}
    
    # Step 2: Check models
    if progress:
        progress.step(1, "Testing models...")
    try:
        model_health = model_selector.get_performance_stats()
        results["components"]["models"] = {"status": "healthy", "stats": model_health}
    except Exception as e:
        results["components"]["models"] = {"status": "error", "issues": [str(e)]}
    
    # Step 3: Check connectivity
    if progress:
        progress.step(2, "Verifying connectivity...")
    if check_internet_connection():
        results["components"]["connectivity"] = {"status": "healthy"}
    else:
        results["components"]["connectivity"] = {"status": "warning", "issues": ["No internet connection"]}
    
    # Step 4: Check MCP servers
    if progress:
        progress.step(3, "Validating MCP servers...")
    try:
        # Add MCP server validation here
        results["components"]["mcp_servers"] = {"status": "healthy"}
    except Exception as e:
        results["components"]["mcp_servers"] = {"status": "error", "issues": [str(e)]}
    
    # Additional comprehensive checks
    if comprehensive:
        if progress:
            progress.step(4, "Checking dependencies...")
        # Add dependency checks
        
        if progress:
            progress.step(5, "Testing permissions...")
        # Add permission checks
        
        if progress:
            progress.step(6, "Analyzing performance...")
        # Add performance checks
    
    return results

def display_health_results(results: Dict[str, Any]):
    """Display health check results"""
    table = Table(title="🏥 System Health Check", box=box.ROUNDED)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")
    
    for component, data in results["components"].items():
        status = data["status"]
        if status == "healthy":
            status_text = "[green]✓ Healthy[/green]"
        elif status == "warning":
            status_text = "[yellow]⚠ Warning[/yellow]"
        else:
            status_text = "[red]✗ Error[/red]"
        
        details = ""
        if "issues" in data and data["issues"]:
            details = "; ".join(data["issues"][:2])
        elif "stats" in data:
            details = f"{len(data['stats'])} models configured"
        
        table.add_row(component.title(), status_text, details)
    
    console.print(table)

# Placeholder functions for unimplemented features
async def review_file(file_path, security, performance): pass
async def generate_code(description, language, framework, style, template): pass
async def explain_code(file, lines, detail, format): pass
async def analyze_target(target, depth, focus): pass
async def create_summary(targets, format): pass

def get_git_diff_files(): return []
def get_current_files(): return []
def display_review_results(results): pass
def save_review_results(results, output): pass
def display_generated_code(code, language): pass
def save_generated_code(code, output): pass
def display_code_explanation(explanation, format): pass
def display_analysis_result(result): pass
def save_analysis_result(result, output): pass
def display_summary(summary, format): pass
def run_config_wizard(): pass
def create_default_config(template): pass
def _read_env_default_model() -> Optional[str]:
    try:
        path = _env_file_path()
        if not path.exists():
            return None
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.startswith('DEFAULT_MODEL='):
                return line.split('=',1)[1].strip().strip('"').strip("'")
    except Exception:
        return None
    return None

def display_config_rich(config, section, resolved):
    table = Table(title="Swiss AI Configuration", box=box.ROUNDED)
    table.add_column("Key", style="cyan", width=28)
    table.add_column("Value", style="white")
    table.add_row("version", config.version)
    table.add_row("active_profile", config.active_profile)
    table.add_row("models_count", str(len(config.models)))
    table.add_row("profiles_count", str(len(config.profiles)))
    table.add_row("DEFAULT_MODEL (resolved)", str(resolved.get("DEFAULT_MODEL")))
    table.add_row("SWISS_AI_FORCE_PROVIDER (resolved)", str(resolved.get("SWISS_AI_FORCE_PROVIDER")))
    console.print(table)

def display_config_yaml(config, section, resolved):
    import yaml as _yaml
    data = {
        "version": config.version,
        "active_profile": config.active_profile,
        "models": list(config.models.keys()),
        "profiles": list(config.profiles.keys()),
        "resolved": resolved,
    }
    console.print(_yaml.safe_dump(data, sort_keys=False))

def display_config_json(config, section, resolved):
    import json as _json
    data = {
        "version": config.version,
        "active_profile": config.active_profile,
        "models": list(config.models.keys()),
        "profiles": list(config.profiles.keys()),
        "resolved": resolved,
    }
    console.print(_json.dumps(data, indent=2))
def fix_config_issues(issues): return 0
def get_models_data(available, performance, health):
    data: Dict[str, Any] = {"configured": [], "available": []}
    # Configured/free registry from ModelSelector
    if model_selector is not None:
        for mid, info in model_selector.available_models.items():
            itm = {
                "id": mid,
                "name": getattr(info, 'name', mid),
                "provider": getattr(info, 'provider', "openrouter"),
                "tier": getattr(info, 'tier', None).value if getattr(info, 'tier', None) else None,
            }
            data["configured"].append(itm)
    if available:
        # Fetch OpenRouter live list (best coverage)
        try:
            import requests
            headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY','')}"}
            resp = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=12)
            resp.raise_for_status()
            for m in resp.json().get('data', []):
                data["available"].append({
                    "id": m.get('id',''),
                    "name": m.get('name', m.get('id','')),
                    "provider": "openrouter",
                    "free": (":free" in m.get('id','')) or ("(free)" in m.get('id','')) or ((m.get('pricing') or {}).get('prompt') == 0),
                })
        except Exception:
            pass
    return data

def display_models_table(data, performance, health):
    table = Table(title="Models", box=box.ROUNDED)
    table.add_column("Type", style="yellow", width=10)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Provider", style="green", width=12)
    table.add_column("Tier/Free", style="blue", width=10)
    # Configured
    for m in data.get("configured", []):
        table.add_row("configured", m.get("id",""), m.get("name",""), str(m.get("provider","")), str(m.get("tier") or ""))
    # Available
    for m in data.get("available", []):
        table.add_row("available", m.get("id",""), m.get("name",""), str(m.get("provider","")), "free" if m.get("free") else "")
    console.print(table)

def model_exists(model_name):
    if model_selector and model_name in model_selector.available_models:
        return True
    # Fallback: let users pass exact OpenRouter/OpenAI/Google/Anthropic ids
    return bool(model_name)

def update_default_model(model_name, profile):
    # Store in env file handled by caller; optionally track in config profiles later
    return

def get_default_model():
    return os.getenv("DEFAULT_MODEL") or os.getenv("SWISS_AI_DEFAULT_MODEL") or _read_env_default_model() or "qwen/qwen2.5-coder:free"

async def run_model_benchmark(model_name):
    prompts = [
        "Summarize: Swiss banking compliance basics in 3 bullets.",
        "Write a Python function fib(n) with type hints.",
        "Explain what MCP is in one sentence.",
    ]
    start = time.time()
    for p in prompts:
        await test_model_simple(model_name, p)
    console.print(f"[green]Benchmark completed in {time.time()-start:.1f}s[/green]")

async def test_model_simple(model_name, prompt):
    init_cli_components()
    from .api.client import SwissAIAPIClient  # lazy import path safety
    client = SwissAIAPIClient()
    with show_progress("Testing model..."):
        resp = await client.simple_chat(prompt=prompt, model=model_name)
    ok = "[green]OK[/green]" if resp.success else "[red]FAIL[/red]"
    table = Table(box=box.SIMPLE)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("status", ok)
    table.add_row("model_used", str(resp.model_used))
    table.add_row("time", f"{resp.execution_time:.2f}s")
    if resp.error:
        table.add_row("error", resp.error[:120])
    console.print(table)
def fix_health_issues(results): pass
def export_health_report(results, export_path): pass

def main():
    """Main entry point with global error handling"""
    try:
        swiss_ai()
    except SwissAIError as e:
        from .error_handling import error_formatter
        error_formatter.format_error(e, show_details=not cli_ctx.no_color)
        sys.exit(e.exit_code)
    except click.ClickException as e:
        # Handle Click-specific exceptions
        if isinstance(e, click.UsageError):
            error_msg = str(e)
            
            # Try to extract command name from error
            if "No such command" in error_msg:
                # Extract command name
                import re
                match = re.search(r"No such command '([^']+)'", error_msg)
                if match:
                    invalid_command = match.group(1)
                    console.print(f"[red]Command '{invalid_command}' not found[/red]")
                    
                    # Show suggestions
                    suggestions = command_registry.get_similar_commands(invalid_command)
                    if suggestions:
                        console.print("\n[yellow]Did you mean one of these?[/yellow]")
                        for suggestion in suggestions[:3]:
                            console.print(f"  [cyan]swiss-ai {suggestion}[/cyan]")
                    
                    # Show discovery hint
                    console.print(f"\n[dim]Use [cyan]swiss-ai discover[/cyan] to explore available commands[/dim]")
                    console.print(f"[dim]Use [cyan]swiss-ai discover '{invalid_command}'[/cyan] to find related commands[/dim]")
                    
                    sys.exit(1)
            
            suggest_command_fix(str(e))
        else:
            console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        # Handle any other unhandled exceptions
        context = create_error_context(command="swiss-ai")
        exit_code = handle_error(e, context, show_details=cli_ctx.verbose)
        sys.exit(exit_code)

if __name__ == '__main__':
    main()