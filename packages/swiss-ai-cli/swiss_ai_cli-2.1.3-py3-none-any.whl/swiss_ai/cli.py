#!/usr/bin/env python3
"""
Main CLI entry point for Swiss AI CLI
Professional command-line interface with intelligent routing and collaboration
"""

import asyncio
import sys
import argparse
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.live import Live
from rich import box

from .config.manager import ConfigManager, ConfigurationError
from .models.selector import ModelSelector
from .mcp.manager import MCPManager
from .routing.router import IntelligentRouter
from .agents.collaborative import CollaborativeOrchestrator
from .agents.implementations import create_all_agents
from .utils.helpers import setup_logging, validate_api_key, get_system_info, check_internet_connection
import os
from .tui.app import run_tui

logger = logging.getLogger(__name__)

class SwissAICLI:
    """Main Swiss AI CLI application"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.console = Console()
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.model_selector = ModelSelector(self.config_manager)
        self.mcp_manager = MCPManager()
        self.router = IntelligentRouter(self.config_manager, self.model_selector)
        self.orchestrator = CollaborativeOrchestrator(
            self.config_manager, self.model_selector, self.router
        )
        
        # Register all available agents
        agents = create_all_agents(self.config_manager)
        for agent in agents:
            self.orchestrator.register_agent(agent)
        
        # Runtime state
        self.conversation_history = []
        self.session_start_time = time.time()
        self.is_interactive = False
        
        logger.info(f"Swiss AI CLI initialized for project: {self.project_path}")
    
    async def run(self, args: argparse.Namespace):
        """Main run method based on arguments"""
        try:
            # Handle different command modes
            if args.command == 'init':
                await self._handle_init(args)
            elif args.command == 'config':
                await self._handle_config(args)
            elif args.command == 'models':
                await self._handle_models(args)
            elif args.command == 'mcp':
                await self._handle_mcp(args)
            elif args.command == 'stats':
                await self._handle_stats(args)
            elif args.command == 'ui':
                # Launch minimal TUI workspace; pass any message seed
                seed = " ".join(getattr(args, 'message', []) or []) or None
                run_tui(seed)
            elif args.command == 'chat' or not args.command:
                await self._handle_interactive_chat(args)
            elif args.command:
                # Direct command execution
                await self._handle_direct_command(args.command, args)
            else:
                self._show_help()
        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupted by user[/yellow]")
        except Exception as e:
            logger.error(f"Error in CLI execution: {e}")
            self.console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
        finally:
            await self._cleanup()
    
    async def _handle_init(self, args: argparse.Namespace):
        """Initialize Swiss AI CLI configuration"""
        self.console.print("[bold blue]Initializing Swiss AI CLI[/bold blue]")
        
        try:
            # Load or create configuration
            config = self.config_manager.load_config(create_if_missing=True)
            
            # Interactive setup if no API key configured
            if not any(model.api_key for model in config.models.values()) and not args.api_key:
                api_key = Prompt.ask(
                    "Enter your OpenRouter API key",
                    password=True,
                    default=""
                )
                
                if api_key and validate_api_key(api_key):
                    from .config.manager import ModelConfig
                    
                    # Add default model with API key
                    default_model = ModelConfig(
                        name="qwen/qwen3-coder:free",
                        api_key=api_key,
                        use_cases=["coding", "general"]
                    )
                    self.config_manager.add_model(default_model)
                    
                    self.console.print("[green]✓ API key configured successfully[/green]")
                else:
                    self.console.print("[yellow]⚠ No valid API key provided. You can configure it later.[/yellow]")
            
            # Auto-start MCP servers if requested
            if args.auto_mcp or Confirm.ask("Start MCP servers automatically?", default=False):
                self.mcp_manager.start_all_auto_start_servers()
            
            self.console.print("[green]✓ Swiss AI CLI initialized successfully[/green]")
            
        except ConfigurationError as e:
            self.console.print(f"[red]Configuration error: {e.message}[/red]")
            if e.suggestion:
                self.console.print(f"[yellow]Suggestion: {e.suggestion}[/yellow]")
    
    async def _handle_config(self, args: argparse.Namespace):
        """Handle configuration commands"""
        if args.config_action == 'show':
            self.config_manager.display_config()
        elif args.config_action == 'validate':
            issues = self.config_manager.validate_config()
            if issues:
                self.console.print("[red]Configuration issues found:[/red]")
                for issue in issues:
                    self.console.print(f"  • {issue}")
            else:
                self.console.print("[green]✓ Configuration is valid[/green]")
        elif args.config_action == 'reset':
            if Confirm.ask("Are you sure you want to reset configuration to defaults?"):
                self.config_manager.reset_config()
                self.console.print("[green]✓ Configuration reset to defaults[/green]")
        else:
            self.console.print("[yellow]Available config actions: show, validate, reset[/yellow]")
    
    async def _handle_models(self, args: argparse.Namespace):
        """Handle model management commands"""
        if args.model_action == 'list':
            self.model_selector.display_model_status()
        elif args.model_action == 'stats':
            stats = self.model_selector.get_performance_stats()
            self._display_model_stats(stats)
        elif args.model_action == 'reset':
            if Confirm.ask("Reset model performance data?"):
                self.model_selector.reset_performance_data()
                self.console.print("[green]✓ Model performance data reset[/green]")
        else:
            self.console.print("[yellow]Available model actions: list, stats, reset[/yellow]")
    
    async def _handle_mcp(self, args: argparse.Namespace):
        """Handle MCP server commands"""
        if args.mcp_action == 'status':
            self.mcp_manager.display_server_status()
        elif args.mcp_action == 'start':
            if args.server_name:
                success = self.mcp_manager.start_server(args.server_name)
                if success:
                    self.console.print(f"[green]✓ Started MCP server: {args.server_name}[/green]")
                else:
                    self.console.print(f"[red]✗ Failed to start MCP server: {args.server_name}[/red]")
            else:
                self.mcp_manager.start_all_auto_start_servers()
        elif args.mcp_action == 'stop':
            if args.server_name:
                success = self.mcp_manager.stop_server(args.server_name)
                if success:
                    self.console.print(f"[green]✓ Stopped MCP server: {args.server_name}[/green]")
                else:
                    self.console.print(f"[red]✗ Failed to stop MCP server: {args.server_name}[/red]")
            else:
                self.mcp_manager.stop_all_servers()
        elif args.mcp_action == 'restart':
            if args.server_name:
                success = self.mcp_manager.restart_server(args.server_name)
                if success:
                    self.console.print(f"[green]✓ Restarted MCP server: {args.server_name}[/green]")
                else:
                    self.console.print(f"[red]✗ Failed to restart MCP server: {args.server_name}[/red]")
        else:
            self.console.print("[yellow]Available MCP actions: status, start, stop, restart[/yellow]")
    
    async def _handle_stats(self, args: argparse.Namespace):
        """Display comprehensive statistics"""
        self.console.print("[bold blue]Swiss AI CLI Statistics[/bold blue]")
        
        # Collaboration stats
        collab_stats = self.orchestrator.get_collaboration_stats()
        self._display_collaboration_stats(collab_stats)
        
        # Routing stats
        self.router.display_learning_stats()
        
        # Model stats
        model_stats = self.model_selector.get_performance_stats()
        if model_stats:
            self._display_model_stats(model_stats)
        
        # System info
        if args.verbose:
            system_info = get_system_info()
            self._display_system_info(system_info)
    
    async def _handle_interactive_chat(self, args: argparse.Namespace):
        """Handle interactive chat mode"""
        # If a direct message was provided to chat, handle non-interactively
        if hasattr(args, "message") and args.message:
            user_input = " ".join(args.message).strip()
            if user_input:
                await self._process_user_request(user_input)
                return

        self.is_interactive = True
        
        # Allow forcing provider via launcher alias
        invoked = os.path.basename(sys.argv[0])
        if invoked.startswith("gemini"):
            os.environ["SWISS_AI_FORCE_PROVIDER"] = "googleai"
        elif invoked.startswith("claude"):
            os.environ["SWISS_AI_FORCE_PROVIDER"] = "anthropic"

        # Display welcome message
        self._display_welcome()
        
        # Check system readiness
        await self._check_system_readiness()
        
        # Main chat loop
        while True:
            try:
                user_input = Prompt.ask(
                    "[bold blue]swiss-ai[/bold blue]",
                    default="",
                    show_default=False
                ).strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if await self._handle_special_commands(user_input):
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                
                # Process user request
                await self._process_user_request(user_input)
                
            except KeyboardInterrupt:
                if Confirm.ask("\nDo you want to exit?"):
                    break
            except Exception as e:
                logger.error(f"Error in interactive chat: {e}")
                self.console.print(f"[red]Error: {e}[/red]")
    
    async def _handle_direct_command(self, command: str, args: argparse.Namespace):
        """Handle direct command execution"""
        self.console.print(f"[bold green]Executing:[/bold green] {command}")
        
        await self._process_user_request(command)
    
    async def _process_user_request(self, user_input: str):
        """Process a user request through the intelligent system"""
        start_time = time.time()
        
        try:
            # Show processing indicator
            with Live(Panel("[bold green]Processing...[/bold green]", title="🤖 Swiss AI"), 
                     console=self.console, refresh_per_second=4):
                
                response = await self.orchestrator.process_request(
                    user_input, self.conversation_history
                )
            
            processing_time = time.time() - start_time
            
            # Display response
            self.console.print(f"\n[bold green]Response:[/bold green]")
            self.console.print(Panel(response, border_style="green"))
            
            if self.is_interactive:
                self.console.print(f"[dim]Processed in {processing_time:.2f}s[/dim]\n")
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response}
            ])
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
        
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.console.print(f"[red]Error processing request: {e}[/red]")
    
    async def _handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands, return True if handled"""
        command = user_input.lower().strip()
        
        if command == '/help':
            self._show_interactive_help()
            return True
        elif command == '/stats':
            await self._handle_stats(argparse.Namespace(verbose=False))
            return True
        elif command == '/config':
            self.config_manager.display_config()
            return True
        elif command == '/models':
            self.model_selector.display_model_status()
            return True
        elif command == '/mcp':
            self.mcp_manager.display_server_status()
            return True
        elif command == '/routing':
            self.router.display_learning_stats()
            return True
        elif command == '/system':
            system_info = get_system_info()
            self._display_system_info(system_info)
            return True
        elif command == '/clear':
            self.conversation_history.clear()
            self.console.print("[green]✓ Conversation history cleared[/green]")
            return True
        
        return False
    
    def _display_welcome(self):
        """Display welcome message"""
        welcome_text = f"""[bold blue]Swiss AI CLI - Professional AI Assistant[/bold blue]

[green]🎯 Intelligent Routing:[/green] Automatically selects optimal agents and models
[green]🧠 Learning System:[/green] Improves performance based on usage patterns
[green]🤝 Collaborative Agents:[/green] Multiple specialized agents work together
[green]🔧 MCP Integration:[/green] Secure external tool integration
[green]⚡ Smart Models:[/green] Performance-based model selection

[bold yellow]Special Commands:[/bold yellow]
• [cyan]/help[/cyan] - Show available commands
• [cyan]/stats[/cyan] - Display system statistics
• [cyan]/config[/cyan] - Show configuration
• [cyan]/models[/cyan] - Model status and performance
• [cyan]/mcp[/cyan] - MCP server status
• [cyan]/routing[/cyan] - Routing statistics
• [cyan]/system[/cyan] - System information
• [cyan]/clear[/cyan] - Clear conversation history

[bold]Project:[/bold] {self.project_path.name}
[bold]Session:[/bold] {time.strftime('%Y-%m-%d %H:%M:%S')}"""
        
        panel = Panel(welcome_text, title="🚀 Welcome", border_style="blue")
        self.console.print(panel)
    
    def _show_interactive_help(self):
        """Show interactive help"""
        help_text = """[bold blue]Swiss AI CLI - Interactive Help[/bold blue]

[bold yellow]How to Use:[/bold yellow]
Simply type your request in natural language! The system will:
• 🎯 Analyze your request and route to the best agent
• 🧠 Select the optimal AI model for the task
• 🤝 Collaborate between agents when beneficial
• 📚 Learn from feedback to improve over time

[bold yellow]Examples:[/bold yellow]
• "debug this React component" → [green]CODE Agent[/green]
• "analyze the project structure" → [green]ANALYSIS Agent[/green]
• "read the README file" → [green]FILE Agent[/green]
• "commit my changes" → [green]GIT Agent[/green]
• "help me plan this feature" → [green]REFLECTION Agent[/green]

[bold yellow]Special Commands:[/bold yellow]
• [cyan]/stats[/cyan] - System performance statistics
• [cyan]/config[/cyan] - Configuration management
• [cyan]/models[/cyan] - AI model status and performance
• [cyan]/mcp[/cyan] - MCP server management
• [cyan]/routing[/cyan] - Routing decision statistics
• [cyan]/system[/cyan] - System information
• [cyan]/clear[/cyan] - Clear conversation history
• [cyan]/help[/cyan] - Show this help message

[bold yellow]Getting Started:[/bold yellow]
1. Ensure your API key is configured: [cyan]swiss-ai config show[/cyan]
2. Check system status: [cyan]/stats[/cyan]
3. Start asking questions or giving commands!"""
        
        panel = Panel(help_text, title="📚 Interactive Help", border_style="blue")
        self.console.print(panel)
    
    def _show_help(self):
        """Show general help"""
        help_text = """Swiss AI CLI - Professional AI Assistant

Usage:
  swiss-ai [command] [options]

Commands:
  init                 Initialize Swiss AI CLI configuration
  chat                 Start interactive chat mode (default)
  config <action>      Configuration management (show, validate, reset)
  models <action>      Model management (list, stats, reset)
  mcp <action>         MCP server management (status, start, stop, restart)
  stats                Display comprehensive statistics
  
Global Options:
  -h, --help          Show this help message
  --verbose           Enable verbose output
  --project-path PATH Set project directory (default: current directory)
  --api-key KEY       Set API key for this session

Examples:
  swiss-ai init                    # Initialize configuration
  swiss-ai chat                    # Start interactive mode
  swiss-ai "debug this function"   # Direct command
  swiss-ai config show            # Show current configuration
  swiss-ai models list            # List available models
  swiss-ai mcp status             # Show MCP server status
  swiss-ai stats --verbose       # Show detailed statistics

For more information, visit: https://github.com/swiss-ai/cli"""
        
        self.console.print(help_text)
    
    async def _check_system_readiness(self):
        """Check if system is ready for operation"""
        issues = []
        
        # Check configuration
        try:
            config_issues = self.config_manager.validate_config()
            issues.extend(config_issues)
        except Exception as e:
            issues.append(f"Configuration error: {e}")
        
        # Check internet connectivity
        if not check_internet_connection():
            issues.append("No internet connection detected")
        
        # Check MCP servers if auto-start enabled
        config = self.config_manager.get_config()
        if any(server.auto_start for server in config.mcp_servers.values()):
            # Start auto-start servers
            self.mcp_manager.start_all_auto_start_servers()
        
        # Display issues if any
        if issues:
            self.console.print("[yellow]⚠ System readiness issues detected:[/yellow]")
            for issue in issues:
                self.console.print(f"  • {issue}")
            self.console.print()
    
    def _display_collaboration_stats(self, stats: Dict[str, Any]):
        """Display collaboration statistics"""
        table = Table(title="🤝 Collaboration Statistics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Requests", str(stats['total_requests']))
        table.add_row("Success Rate", f"{stats['success_rate']:.1f}%")
        table.add_row("Active Agents", str(stats['total_agents']))
        
        if stats['agent_usage']:
            table.add_row("Most Used Agent", max(stats['agent_usage'], key=stats['agent_usage'].get))
        
        self.console.print(table)
    
    def _display_model_stats(self, stats: Dict[str, Any]):
        """Display model performance statistics"""
        if not stats:
            return
        
        table = Table(title="🤖 Model Performance", box=box.ROUNDED)
        table.add_column("Model", style="cyan")
        table.add_column("Success Rate", style="green")
        table.add_column("Avg Time", style="yellow")
        table.add_column("Requests", style="blue")
        
        for model_id, model_stats in stats.items():
            table.add_row(
                model_stats['name'],
                f"{model_stats['success_rate']:.1%}",
                f"{model_stats['avg_response_time']:.1f}s",
                str(model_stats['total_requests'])
            )
        
        self.console.print(table)
    
    def _display_system_info(self, info: Dict[str, Any]):
        """Display system information"""
        table = Table(title="💻 System Information", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in info.items():
            display_key = key.replace('_', ' ').title()
            table.add_row(display_key, str(value))
        
        self.console.print(table)
    
    async def _cleanup(self):
        """Cleanup resources"""
        try:
            # Save configuration and performance data
            self.config_manager.save_config()
            
            # Save model performance data
            data_dir = self.config_manager.config_dir / "performance"
            data_dir.mkdir(exist_ok=True)
            self.model_selector.save_performance_data(str(data_dir / "models.json"))
            
            # Shutdown MCP manager
            self.mcp_manager.shutdown()
            
            # Shutdown orchestrator
            self.orchestrator.shutdown()
            
            session_time = time.time() - self.session_start_time
            logger.info(f"Swiss AI CLI session ended after {session_time:.1f}s")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="Swiss AI CLI - Professional AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  swiss-ai init                    # Initialize configuration
  swiss-ai chat                    # Start interactive mode  
  swiss-ai "debug this function"   # Direct command
  swiss-ai config show            # Show configuration
  swiss-ai models list            # List models
  swiss-ai mcp status             # MCP server status
        """
    )
    
    # Global options
    parser.add_argument('--version', action='version', version='%(prog)s 2.1.0')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--project-path', default='.', help='Project directory path')
    parser.add_argument('--api-key', help='OpenRouter API key')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize Swiss AI CLI')
    init_parser.add_argument('--auto-mcp', action='store_true', help='Auto-start MCP servers')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Interactive chat or send a single message')
    chat_parser.add_argument('message', nargs='*', help='Optional message to send directly')

    # UI alias (same as chat)
    ui_parser = subparsers.add_parser('ui', help='Open interactive chat UI (alias of chat)')
    ui_parser.add_argument('message', nargs='*', help='Optional message to send directly')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('config_action', choices=['show', 'validate', 'reset'], 
                              help='Configuration action')
    
    # Models command
    models_parser = subparsers.add_parser('models', help='Model management')
    models_parser.add_argument('model_action', choices=['list', 'stats', 'reset'],
                              help='Model action')
    
    # MCP command
    mcp_parser = subparsers.add_parser('mcp', help='MCP server management')
    mcp_parser.add_argument('mcp_action', choices=['status', 'start', 'stop', 'restart'],
                           help='MCP action')
    mcp_parser.add_argument('--server-name', help='Specific server name')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Display statistics')
    
    # Add support for direct command as positional argument
    parser.add_argument('direct_command', nargs='?', help='Direct command to execute')
    
    return parser

async def main():
    """Main entry point for Swiss AI CLI"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Handle direct command
    if args.direct_command and not args.command:
        args.command = args.direct_command
    
    # Initialize CLI
    cli = SwissAICLI(args.project_path)
    
    # Set API key if provided
    if args.api_key:
        # TODO: Set API key in session
        pass
    
    # Run CLI
    await cli.run(args)

def cli_main():
    """Entry point for console script"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli_main()