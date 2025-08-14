#!/usr/bin/env python3
"""
Rich Help System for Swiss AI CLI
Beautiful, context-aware help with examples and progressive disclosure
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import box

console = Console()

@dataclass
class CommandExample:
    """Command example with description"""
    command: str
    description: str
    advanced: bool = False

@dataclass
class CommandTip:
    """Helpful tip for command usage"""
    tip: str
    level: str = "beginner"  # beginner, intermediate, advanced

class SwissAIHelpFormatter:
    """Enhanced help formatter for Swiss AI CLI"""
    
    def __init__(self):
        self.examples = self._load_examples()
        self.tips = self._load_tips()
        self.common_mistakes = self._load_common_mistakes()
    
    def format_command_help(self, ctx: click.Context, show_advanced: bool = False) -> None:
        """Format help for a specific command"""
        command_name = ctx.info_name
        command_path = self._get_command_path(ctx)
        
        # Main help panel
        self._show_main_help(ctx, command_path)
        
        # Examples section
        self._show_examples(command_path, show_advanced)
        
        # Tips and tricks
        self._show_tips(command_path, show_advanced)
        
        # Common mistakes
        self._show_common_mistakes(command_path)
        
        # Related commands
        self._show_related_commands(command_path)
    
    def format_group_help(self, ctx: click.Context) -> None:
        """Format help for command groups"""
        group_name = ctx.info_name
        
        # Group overview
        self._show_group_overview(ctx, group_name)
        
        # Command listing with descriptions
        self._show_command_listing(ctx, group_name)
        
        # Quick start examples
        self._show_quick_start(group_name)
        
        # Workflow examples
        self._show_workflows(group_name)
    
    def _show_main_help(self, ctx: click.Context, command_path: str):
        """Show main command help"""
        cmd = ctx.command
        
        # Build help content
        help_text = f"[bold cyan]{command_path}[/bold cyan]"
        if cmd.short_help:
            help_text += f"\n{cmd.short_help}"
        
        if cmd.help:
            help_text += f"\n\n{cmd.help}"
        
        # Usage patterns
        usage = self._build_usage_string(ctx)
        help_text += f"\n\n[bold]Usage:[/bold]\n  {usage}"
        
        # Options table
        if cmd.params:
            options_table = self._build_options_table(cmd.params)
            help_text += f"\n\n[bold]Options:[/bold]"
            console.print(Panel(help_text, title="📖 Command Help", border_style="blue"))
            console.print(options_table)
        else:
            console.print(Panel(help_text, title="📖 Command Help", border_style="blue"))
    
    def _show_examples(self, command_path: str, show_advanced: bool):
        """Show command examples"""
        examples = self.examples.get(command_path, [])
        
        if not examples:
            return
        
        # Filter examples by level
        basic_examples = [ex for ex in examples if not ex.advanced]
        advanced_examples = [ex for ex in examples if ex.advanced]
        
        if basic_examples:
            console.print("\n[bold green]📚 Examples:[/bold green]")
            for example in basic_examples:
                console.print(f"  [cyan]{example.command}[/cyan]")
                console.print(f"    {example.description}")
        
        if show_advanced and advanced_examples:
            console.print("\n[bold yellow]🔧 Advanced Examples:[/bold yellow]")
            for example in advanced_examples:
                console.print(f"  [cyan]{example.command}[/cyan]")
                console.print(f"    {example.description}")
    
    def _show_tips(self, command_path: str, show_advanced: bool):
        """Show helpful tips"""
        tips = self.tips.get(command_path, [])
        
        if not tips:
            return
        
        relevant_tips = tips
        if not show_advanced:
            relevant_tips = [tip for tip in tips if tip.level in ["beginner", "intermediate"]]
        
        if relevant_tips:
            console.print("\n[bold blue]💡 Tips:[/bold blue]")
            for tip in relevant_tips:
                level_emoji = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
                emoji = level_emoji.get(tip.level, "🔵")
                console.print(f"  {emoji} {tip.tip}")
    
    def _show_common_mistakes(self, command_path: str):
        """Show common mistakes and corrections"""
        mistakes = self.common_mistakes.get(command_path, [])
        
        if mistakes:
            console.print("\n[bold red]⚠ Common Mistakes:[/bold red]")
            for mistake, correction in mistakes:
                console.print(f"  [red]✗[/red] {mistake}")
                console.print(f"  [green]✓[/green] {correction}")
    
    def _show_related_commands(self, command_path: str):
        """Show related commands"""
        related = self._get_related_commands(command_path)
        
        if related:
            console.print("\n[bold magenta]🔗 Related Commands:[/bold magenta]")
            for cmd, desc in related:
                console.print(f"  [cyan]{cmd}[/cyan] - {desc}")
    
    def _show_group_overview(self, ctx: click.Context, group_name: str):
        """Show command group overview"""
        group = ctx.command
        
        # Group description
        overview = f"[bold cyan]{group_name}[/bold cyan]"
        if group.short_help:
            overview += f"\n{group.short_help}"
        if group.help:
            overview += f"\n\n{group.help}"
        
        console.print(Panel(overview, title=f"📋 {group_name.title()} Commands", border_style="blue"))
    
    def _show_command_listing(self, ctx: click.Context, group_name: str):
        """Show formatted command listing"""
        group = ctx.command
        
        if not hasattr(group, 'commands') or not group.commands:
            return
        
        table = Table(title="Available Commands", box=box.ROUNDED)
        table.add_column("Command", style="cyan", width=20)
        table.add_column("Description", style="white")
        
        for cmd_name, cmd in sorted(group.commands.items()):
            desc = cmd.short_help or cmd.help or "No description available"
            if len(desc) > 60:
                desc = desc[:57] + "..."
            table.add_row(f"{group_name}:{cmd_name}", desc)
        
        console.print(table)
    
    def _show_quick_start(self, group_name: str):
        """Show quick start examples for the group"""
        quick_starts = {
            "code": [
                ("swiss-ai code:review --file src/main.py", "Review a specific file"),
                ("swiss-ai code:generate 'REST API for users'", "Generate code from description"),
                ("swiss-ai code:explain --file complex.py", "Explain complex code")
            ],
            "research": [
                ("swiss-ai research:analyze", "Analyze current project"),
                ("swiss-ai research:summarize --directory src/", "Summarize source code"),
                ("swiss-ai research:analyze --focus architecture", "Focus on architecture")
            ],
            "config": [
                ("swiss-ai config:init --wizard", "Interactive setup"),
                ("swiss-ai config:show", "View current settings"),
                ("swiss-ai config:validate", "Check configuration")
            ],
            "model": [
                ("swiss-ai model:list", "See available models"),
                ("swiss-ai model:select qwen3-coder", "Switch default model"),
                ("swiss-ai model:test", "Test current model")
            ]
        }
        
        examples = quick_starts.get(group_name, [])
        if examples:
            console.print("\n[bold green]🚀 Quick Start:[/bold green]")
            for cmd, desc in examples:
                console.print(f"  [cyan]{cmd}[/cyan]")
                console.print(f"    {desc}")
    
    def _show_workflows(self, group_name: str):
        """Show common workflows"""
        workflows = {
            "code": [
                {
                    "name": "Code Review Workflow",
                    "steps": [
                        "swiss-ai code:review --diff",
                        "swiss-ai code:explain --file changed_file.py", 
                        "swiss-ai code:generate 'unit tests' --template test"
                    ]
                }
            ],
            "research": [
                {
                    "name": "Project Analysis Workflow", 
                    "steps": [
                        "swiss-ai research:analyze --depth comprehensive",
                        "swiss-ai research:summarize --format executive",
                        "swiss-ai code:review --security"
                    ]
                }
            ]
        }
        
        group_workflows = workflows.get(group_name, [])
        if group_workflows:
            console.print("\n[bold magenta]🔄 Common Workflows:[/bold magenta]")
            for workflow in group_workflows:
                console.print(f"  [bold]{workflow['name']}:[/bold]")
                for i, step in enumerate(workflow['steps'], 1):
                    console.print(f"    {i}. [cyan]{step}[/cyan]")
    
    def _build_usage_string(self, ctx: click.Context) -> str:
        """Build usage string for command"""
        pieces = []
        cmd = ctx.command
        
        if ctx.parent:
            pieces.append(ctx.parent.info_name)
        pieces.append(ctx.info_name)
        
        # Add parameters
        for param in cmd.params:
            if isinstance(param, click.Option):
                if param.required:
                    pieces.append(f"--{param.name} VALUE")
                else:
                    pieces.append(f"[--{param.name} VALUE]")
            elif isinstance(param, click.Argument):
                if param.required:
                    pieces.append(f"{param.name.upper()}")
                else:
                    pieces.append(f"[{param.name.upper()}]")
        
        return " ".join(pieces)
    
    def _build_options_table(self, params) -> Table:
        """Build options table"""
        table = Table(box=box.ROUNDED)
        table.add_column("Option", style="cyan", width=25)
        table.add_column("Description", style="white")
        table.add_column("Default", style="yellow", width=15)
        
        for param in params:
            if isinstance(param, click.Option):
                # Option names
                option_names = []
                if param.opts:
                    option_names.extend(param.opts)
                if param.secondary_opts:
                    option_names.extend(param.secondary_opts)
                
                option_str = ", ".join(option_names)
                if param.type.name != "flag":
                    option_str += f" {param.type.name.upper()}"
                
                # Description
                desc = param.help or "No description"
                if param.required:
                    desc = f"[red]*[/red] {desc}"
                
                # Default value
                default = str(param.default) if param.default is not None else ""
                if param.type.name == "flag":
                    default = "False"
                
                table.add_row(option_str, desc, default)
        
        return table
    
    def _get_command_path(self, ctx: click.Context) -> str:
        """Get full command path"""
        path_parts = []
        current = ctx
        while current:
            if current.info_name:
                path_parts.append(current.info_name)
            current = current.parent
        return ":".join(reversed(path_parts))
    
    def _load_examples(self) -> Dict[str, List[CommandExample]]:
        """Load command examples"""
        return {
            "swiss-ai": [
                CommandExample("swiss-ai chat 'help me debug this'", "Quick chat message"),
                CommandExample("swiss-ai doctor", "System health check"),
                CommandExample("swiss-ai --verbose config:show", "Verbose configuration display", advanced=True)
            ],
            "swiss-ai:chat": [
                CommandExample("swiss-ai chat 'explain this error'", "Get help with an error"),
                CommandExample("swiss-ai chat --interactive", "Start interactive mode"),
                CommandExample("swiss-ai chat 'review code' --context-files src/main.py", "Chat with file context", advanced=True)
            ],
            "swiss-ai:code:review": [
                CommandExample("swiss-ai code:review --file main.py", "Review single file"),
                CommandExample("swiss-ai code:review --diff", "Review git changes"),
                CommandExample("swiss-ai code:review --security --performance", "Focused security and performance review", advanced=True)
            ],
            "swiss-ai:code:generate": [
                CommandExample("swiss-ai code:generate 'REST API endpoint'", "Generate REST API code"),
                CommandExample("swiss-ai code:generate 'React login form' --language typescript", "Generate TypeScript React component"),
                CommandExample("swiss-ai code:generate 'database model' --framework django --output models.py", "Generate and save Django model", advanced=True)
            ],
            "swiss-ai:research:analyze": [
                CommandExample("swiss-ai research:analyze", "Analyze current project"),
                CommandExample("swiss-ai research:analyze --target src/", "Analyze specific directory"),
                CommandExample("swiss-ai research:analyze --depth comprehensive --focus architecture security", "Deep analysis with multiple focus areas", advanced=True)
            ],
            "swiss-ai:config:init": [
                CommandExample("swiss-ai config:init", "Quick configuration setup"),
                CommandExample("swiss-ai config:init --wizard", "Interactive configuration wizard"),
                CommandExample("swiss-ai config:init --template minimal --force", "Force minimal configuration", advanced=True)
            ],
            "swiss-ai:model:list": [
                CommandExample("swiss-ai model:list", "List configured models"),
                CommandExample("swiss-ai model:list --available", "Show all available models"),
                CommandExample("swiss-ai model:list --performance --health", "Detailed model information", advanced=True)
            ]
        }
    
    def _load_tips(self) -> Dict[str, List[CommandTip]]:
        """Load helpful tips"""
        return {
            "swiss-ai:chat": [
                CommandTip("Use quotes around messages with spaces", "beginner"),
                CommandTip("Include file context with --context-files for better responses", "intermediate"),
                CommandTip("Use --agent to force a specific agent type", "advanced")
            ],
            "swiss-ai:code:review": [
                CommandTip("Use --diff to review only changed files in git", "beginner"),
                CommandTip("Combine --security and --performance for comprehensive review", "intermediate"),
                CommandTip("Save reviews with --output for documentation", "intermediate")
            ],
            "swiss-ai:config:init": [
                CommandTip("Use --wizard for interactive setup if you're new", "beginner"),
                CommandTip("Configuration is stored in ~/.swiss-ai/config.yaml", "intermediate"),
                CommandTip("Use --template for predefined configurations", "advanced")
            ],
            "swiss-ai:model:select": [
                CommandTip("Use --temporary to test a model without changing defaults", "intermediate"),
                CommandTip("Different profiles can have different default models", "advanced")
            ]
        }
    
    def _load_common_mistakes(self) -> Dict[str, List[Tuple[str, str]]]:
        """Load common mistakes and corrections"""
        return {
            "swiss-ai:chat": [
                ("swiss-ai chat hello world", "swiss-ai chat 'hello world'"),
                ("swiss-ai chat --file main.py", "swiss-ai chat 'review this' --context-files main.py")
            ],
            "swiss-ai:code:review": [
                ("swiss-ai code:review main.py", "swiss-ai code:review --file main.py"),
                ("swiss-ai code:review --all", "swiss-ai code:review --diff")
            ],
            "swiss-ai:config:init": [
                ("swiss-ai init", "swiss-ai config:init"),
                ("swiss-ai config init", "swiss-ai config:init")
            ]
        }
    
    def _get_related_commands(self, command_path: str) -> List[Tuple[str, str]]:
        """Get related commands"""
        relations = {
            "swiss-ai:code:review": [
                ("swiss-ai code:explain", "Understand code before reviewing"),
                ("swiss-ai code:generate", "Generate improved code"),
                ("swiss-ai research:analyze", "Broader project analysis")
            ],
            "swiss-ai:code:generate": [
                ("swiss-ai code:review", "Review generated code"),
                ("swiss-ai code:explain", "Understand generated code")
            ],
            "swiss-ai:config:init": [
                ("swiss-ai config:show", "View configuration"),
                ("swiss-ai config:validate", "Validate configuration"),
                ("swiss-ai doctor", "Check system health")
            ],
            "swiss-ai:model:select": [
                ("swiss-ai model:list", "See available models"),
                ("swiss-ai model:test", "Test selected model")
            ]
        }
        
        return relations.get(command_path, [])

# Create global help formatter instance
help_formatter = SwissAIHelpFormatter()

def show_command_help(ctx: click.Context, show_advanced: bool = False):
    """Show help for a command with rich formatting"""
    if isinstance(ctx.command, click.Group):
        help_formatter.format_group_help(ctx)
    else:
        help_formatter.format_command_help(ctx, show_advanced)

def show_suggestion(message: str, suggestions: List[str]):
    """Show command suggestions"""
    console.print(f"\n[yellow]💡 {message}[/yellow]")
    for suggestion in suggestions:
        console.print(f"  [cyan]{suggestion}[/cyan]")

def show_did_you_mean(command: str, similar_commands: List[str]):
    """Show 'did you mean' suggestions"""
    if similar_commands:
        console.print(f"\n[yellow]Did you mean one of these?[/yellow]")
        for cmd in similar_commands[:3]:
            console.print(f"  [cyan]{cmd}[/cyan]")

def show_quick_help():
    """Show quick help overview"""
    quick_help = """
[bold blue]Swiss AI CLI - Quick Help[/bold blue]

[bold]Most Common Commands:[/bold]
  [cyan]swiss-ai chat 'your message'[/cyan]     Chat with AI assistant
  [cyan]swiss-ai code:review --diff[/cyan]      Review your code changes
  [cyan]swiss-ai doctor[/cyan]                  Check system health
  [cyan]swiss-ai config:init --wizard[/cyan]    Set up configuration

[bold]Get More Help:[/bold]
  [cyan]swiss-ai COMMAND --help[/cyan]          Detailed help for any command
  [cyan]swiss-ai --help[/cyan]                  Full command reference

[bold]Examples:[/bold]
  [cyan]swiss-ai chat 'explain this error message'[/cyan]
  [cyan]swiss-ai code:generate 'user authentication system'[/cyan]
  [cyan]swiss-ai research:analyze --target src/[/cyan]

Use [cyan]--verbose[/cyan] with any command for detailed output.
"""
    
    console.print(Panel(quick_help, title="🚀 Quick Help", border_style="blue"))