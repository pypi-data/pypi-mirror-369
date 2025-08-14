#!/usr/bin/env python3
"""
Command Autocomplete and Discovery for Swiss AI CLI
Intelligent command completion, suggestions, and discovery features
"""

import os
import sys
import click
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path
from dataclasses import dataclass
from difflib import get_close_matches
import re

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich import box

console = Console()

@dataclass
class CommandInfo:
    """Information about a CLI command"""
    name: str
    group: Optional[str] = None
    description: str = ""
    aliases: List[str] = None
    parameters: List[str] = None
    examples: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.parameters is None:
            self.parameters = []
        if self.examples is None:
            self.examples = []
        if self.tags is None:
            self.tags = []

class CommandRegistry:
    """Registry of all available CLI commands"""
    
    def __init__(self):
        self.commands: Dict[str, CommandInfo] = {}
        self.groups: Dict[str, List[str]] = {}
        self.aliases: Dict[str, str] = {}
        self.tags: Dict[str, List[str]] = {}
        self._initialize_commands()
    
    def _initialize_commands(self):
        """Initialize the command registry with all available commands"""
        
        # Main commands
        self.register_command(CommandInfo(
            name="chat",
            description="Interactive chat with AI assistant",
            parameters=["message", "--interactive", "--model", "--agent", "--context-files"],
            examples=[
                "swiss-ai chat 'explain this error'",
                "swiss-ai chat --interactive",
                "swiss-ai chat 'debug this' --context-files main.py"
            ],
            tags=["interactive", "conversation", "help"]
        ))
        
        self.register_command(CommandInfo(
            name="doctor",
            description="System health check and diagnostics",
            parameters=["--check-all", "--fix", "--export"],
            examples=[
                "swiss-ai doctor",
                "swiss-ai doctor --check-all",
                "swiss-ai doctor --fix"
            ],
            tags=["health", "diagnostics", "troubleshooting"]
        ))
        
        # Code commands
        code_commands = [
            CommandInfo(
                name="review",
                group="code",
                description="Review code for quality, security, and performance",
                parameters=["--file", "--diff", "--security", "--performance", "--output"],
                examples=[
                    "swiss-ai code:review --file main.py",
                    "swiss-ai code:review --diff",
                    "swiss-ai code:review --security --file auth.py"
                ],
                tags=["code", "review", "quality", "security"]
            ),
            CommandInfo(
                name="generate",
                group="code",
                description="Generate code from natural language description",
                parameters=["description", "--language", "--framework", "--style", "--output", "--template"],
                examples=[
                    "swiss-ai code:generate 'REST API for users'",
                    "swiss-ai code:generate 'React component' --language typescript",
                    "swiss-ai code:generate 'utility function' --style google"
                ],
                tags=["code", "generation", "creation"]
            ),
            CommandInfo(
                name="explain",
                group="code",
                description="Explain code functionality and structure",
                parameters=["--file", "--lines", "--detail", "--format"],
                examples=[
                    "swiss-ai code:explain --file algorithm.py",
                    "swiss-ai code:explain --file main.py --lines 10-20",
                    "swiss-ai code:explain --file api.py --detail expert"
                ],
                tags=["code", "explanation", "documentation"]
            )
        ]
        
        for cmd in code_commands:
            self.register_command(cmd)
        
        # Research commands
        research_commands = [
            CommandInfo(
                name="analyze",
                group="research",
                description="Analyze project structure and codebase",
                parameters=["--target", "--depth", "--focus", "--output"],
                examples=[
                    "swiss-ai research:analyze",
                    "swiss-ai research:analyze --target src/",
                    "swiss-ai research:analyze --depth comprehensive --focus architecture"
                ],
                tags=["research", "analysis", "project"]
            ),
            CommandInfo(
                name="summarize",
                group="research",
                description="Create project or file summaries",
                parameters=["--files", "--directory", "--format"],
                examples=[
                    "swiss-ai research:summarize --files README.md",
                    "swiss-ai research:summarize --directory src/",
                    "swiss-ai research:summarize --directory . --format executive"
                ],
                tags=["research", "summary", "documentation"]
            )
        ]
        
        for cmd in research_commands:
            self.register_command(cmd)
        
        # Config commands
        config_commands = [
            CommandInfo(
                name="init",
                group="config",
                description="Initialize Swiss AI configuration",
                parameters=["--wizard", "--force", "--template"],
                examples=[
                    "swiss-ai config:init",
                    "swiss-ai config:init --wizard",
                    "swiss-ai config:init --force --template minimal"
                ],
                tags=["config", "setup", "initialization"]
            ),
            CommandInfo(
                name="show",
                group="config",
                description="Display current configuration",
                parameters=["--section", "--format"],
                examples=[
                    "swiss-ai config:show",
                    "swiss-ai config:show --section models",
                    "swiss-ai config:show --format yaml"
                ],
                tags=["config", "display", "information"]
            ),
            CommandInfo(
                name="validate",
                group="config",
                description="Validate configuration for errors",
                parameters=["--fix"],
                examples=[
                    "swiss-ai config:validate",
                    "swiss-ai config:validate --fix"
                ],
                tags=["config", "validation", "troubleshooting"]
            )
        ]
        
        for cmd in config_commands:
            self.register_command(cmd)
        
        # Model commands
        model_commands = [
            CommandInfo(
                name="list",
                group="model",
                description="List configured and available models",
                parameters=["--available", "--performance", "--health"],
                examples=[
                    "swiss-ai model:list",
                    "swiss-ai model:list --available",
                    "swiss-ai model:list --performance --health"
                ],
                tags=["model", "list", "information"]
            ),
            CommandInfo(
                name="select",
                group="model",
                description="Select default model",
                parameters=["model_name", "--profile", "--temporary"],
                examples=[
                    "swiss-ai model:select qwen3-coder",
                    "swiss-ai model:select claude-3-haiku --profile development",
                    "swiss-ai model:select gpt-4 --temporary"
                ],
                tags=["model", "selection", "configuration"]
            ),
            CommandInfo(
                name="test",
                group="model",
                description="Test model connectivity and performance",
                parameters=["model_name", "--prompt", "--benchmark"],
                examples=[
                    "swiss-ai model:test",
                    "swiss-ai model:test qwen3-coder",
                    "swiss-ai model:test --prompt 'Generate a function' --benchmark"
                ],
                tags=["model", "testing", "diagnostics"]
            )
        ]
        
        for cmd in model_commands:
            self.register_command(cmd)
    
    def register_command(self, command: CommandInfo):
        """Register a command in the registry"""
        # Full command name
        if command.group:
            full_name = f"{command.group}:{command.name}"
            
            # Add to group
            if command.group not in self.groups:
                self.groups[command.group] = []
            self.groups[command.group].append(command.name)
        else:
            full_name = command.name
        
        self.commands[full_name] = command
        
        # Register aliases
        for alias in command.aliases:
            self.aliases[alias] = full_name
        
        # Register tags
        for tag in command.tags:
            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(full_name)
    
    def get_command(self, name: str) -> Optional[CommandInfo]:
        """Get command by name or alias"""
        if name in self.commands:
            return self.commands[name]
        elif name in self.aliases:
            return self.commands[self.aliases[name]]
        return None
    
    def search_commands(self, query: str) -> List[CommandInfo]:
        """Search commands by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for command in self.commands.values():
            # Check name match
            if query_lower in command.name.lower():
                results.append(command)
                continue
            
            # Check description match
            if query_lower in command.description.lower():
                results.append(command)
                continue
            
            # Check tag match
            if any(query_lower in tag.lower() for tag in command.tags):
                results.append(command)
                continue
        
        return results
    
    def get_similar_commands(self, invalid_command: str) -> List[str]:
        """Get similar commands for 'did you mean' suggestions"""
        all_commands = list(self.commands.keys()) + list(self.aliases.keys())
        matches = get_close_matches(invalid_command, all_commands, n=5, cutoff=0.6)
        return matches
    
    def get_commands_by_group(self, group: str) -> List[CommandInfo]:
        """Get all commands in a group"""
        return [self.commands[f"{group}:{cmd}"] for cmd in self.groups.get(group, [])]
    
    def get_commands_by_tag(self, tag: str) -> List[CommandInfo]:
        """Get all commands with a specific tag"""
        return [self.commands[cmd_name] for cmd_name in self.tags.get(tag, [])]

class AutocompleteEngine:
    """Engine for providing intelligent autocompletion"""
    
    def __init__(self, registry: CommandRegistry):
        self.registry = registry
        self.context_aware = True
    
    def complete_command(self, partial: str, context: Optional[str] = None) -> List[Tuple[str, str]]:
        """Complete a partial command with descriptions"""
        completions = []
        
        # Direct command matches
        for cmd_name, cmd_info in self.registry.commands.items():
            if cmd_name.startswith(partial):
                completions.append((cmd_name, cmd_info.description))
        
        # Alias matches
        for alias, cmd_name in self.registry.aliases.items():
            if alias.startswith(partial):
                cmd_info = self.registry.commands[cmd_name]
                completions.append((alias, f"Alias for {cmd_name}: {cmd_info.description}"))
        
        # Context-aware completions
        if context and self.context_aware:
            context_completions = self._get_context_completions(partial, context)
            completions.extend(context_completions)
        
        # Sort by relevance
        completions.sort(key=lambda x: (len(x[0]), x[0]))
        
        return completions[:10]  # Limit to top 10
    
    def complete_parameter(self, command: str, partial_param: str) -> List[Tuple[str, str]]:
        """Complete command parameters"""
        cmd_info = self.registry.get_command(command)
        if not cmd_info:
            return []
        
        completions = []
        
        for param in cmd_info.parameters:
            if param.startswith(partial_param):
                # Extract parameter description from help text
                description = self._get_parameter_description(param)
                completions.append((param, description))
        
        return completions
    
    def _get_context_completions(self, partial: str, context: str) -> List[Tuple[str, str]]:
        """Get context-aware completions based on current directory/files"""
        completions = []
        
        # File-based completions
        if "file" in context.lower():
            for file_path in self._get_relevant_files():
                if str(file_path).startswith(partial):
                    completions.append((str(file_path), f"File: {file_path}"))
        
        # Directory-based completions
        if "directory" in context.lower() or "dir" in context.lower():
            for dir_path in self._get_relevant_directories():
                if str(dir_path).startswith(partial):
                    completions.append((str(dir_path), f"Directory: {dir_path}"))
        
        return completions
    
    def _get_relevant_files(self) -> List[Path]:
        """Get relevant files in current directory"""
        try:
            current_dir = Path(".")
            relevant_extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".md", ".txt"}
            
            files = []
            for file_path in current_dir.iterdir():
                if file_path.is_file() and file_path.suffix in relevant_extensions:
                    files.append(file_path)
            
            return sorted(files)[:20]  # Limit to 20 files
        except:
            return []
    
    def _get_relevant_directories(self) -> List[Path]:
        """Get relevant directories"""
        try:
            current_dir = Path(".")
            dirs = []
            
            for dir_path in current_dir.iterdir():
                if dir_path.is_dir() and not dir_path.name.startswith("."):
                    dirs.append(dir_path)
            
            return sorted(dirs)[:10]  # Limit to 10 directories
        except:
            return []
    
    def _get_parameter_description(self, param: str) -> str:
        """Get description for a parameter"""
        descriptions = {
            "--file": "Specify input file path",
            "--output": "Specify output file path",
            "--model": "Override default model",
            "--agent": "Force specific agent",
            "--verbose": "Enable verbose output",
            "--help": "Show help message",
            "--format": "Specify output format",
            "--diff": "Review git changes",
            "--security": "Focus on security issues",
            "--performance": "Focus on performance",
            "--interactive": "Start interactive mode",
            "--wizard": "Use interactive wizard",
            "--force": "Force operation",
            "--check-all": "Run comprehensive check"
        }
        
        return descriptions.get(param, "Command parameter")

class CommandDiscovery:
    """System for discovering and learning about commands"""
    
    def __init__(self, registry: CommandRegistry):
        self.registry = registry
    
    def discover_by_task(self, task_description: str) -> List[CommandInfo]:
        """Discover commands based on task description"""
        task_lower = task_description.lower()
        
        # Task keywords to command mapping
        task_mappings = {
            "review": ["code:review"],
            "analyze": ["research:analyze", "code:review"],
            "generate": ["code:generate"],
            "create": ["code:generate"],
            "explain": ["code:explain"],
            "help": ["chat"],
            "debug": ["chat", "code:review"],
            "fix": ["doctor", "config:validate"],
            "setup": ["config:init"],
            "configure": ["config:init", "config:show"],
            "test": ["model:test", "doctor"],
            "check": ["doctor", "config:validate"],
            "summarize": ["research:summarize"],
            "document": ["code:explain", "research:summarize"]
        }
        
        suggested_commands = []
        
        # Find matching commands
        for keyword, commands in task_mappings.items():
            if keyword in task_lower:
                for cmd_name in commands:
                    cmd_info = self.registry.get_command(cmd_name)
                    if cmd_info and cmd_info not in suggested_commands:
                        suggested_commands.append(cmd_info)
        
        return suggested_commands
    
    def show_command_help(self, command_name: str):
        """Show detailed help for a command"""
        cmd_info = self.registry.get_command(command_name)
        if not cmd_info:
            console.print(f"[red]Command '{command_name}' not found[/red]")
            return
        
        # Create help display
        help_content = []
        
        # Command name and description
        if cmd_info.group:
            title = f"swiss-ai {cmd_info.group}:{cmd_info.name}"
        else:
            title = f"swiss-ai {cmd_info.name}"
        
        help_content.append(f"[bold cyan]{title}[/bold cyan]")
        help_content.append(f"{cmd_info.description}")
        
        # Parameters
        if cmd_info.parameters:
            help_content.append("\n[bold]Parameters:[/bold]")
            for param in cmd_info.parameters:
                help_content.append(f"  [cyan]{param}[/cyan]")
        
        # Examples
        if cmd_info.examples:
            help_content.append("\n[bold green]Examples:[/bold green]")
            for example in cmd_info.examples:
                help_content.append(f"  [dim]$[/dim] [cyan]{example}[/cyan]")
        
        # Tags
        if cmd_info.tags:
            help_content.append(f"\n[bold]Tags:[/bold] {', '.join(cmd_info.tags)}")
        
        console.print(Panel(
            "\n".join(help_content),
            title="Command Help",
            border_style="blue"
        ))
    
    def show_commands_by_category(self):
        """Show all commands organized by category"""
        console.print(Panel(
            "[bold blue]Swiss AI CLI Command Reference[/bold blue]",
            title="📚 Command Discovery"
        ))
        
        # Show groups
        for group_name, commands in self.registry.groups.items():
            console.print(f"\n[bold yellow]{group_name.title()} Commands:[/bold yellow]")
            
            table = Table(show_header=False, box=box.SIMPLE)
            table.add_column("Command", style="cyan", width=25)
            table.add_column("Description", style="white")
            
            for cmd_name in commands:
                full_name = f"{group_name}:{cmd_name}"
                cmd_info = self.registry.commands[full_name]
                table.add_row(full_name, cmd_info.description)
            
            console.print(table)
        
        # Show standalone commands
        standalone_commands = [cmd for cmd in self.registry.commands.values() if not cmd.group]
        if standalone_commands:
            console.print(f"\n[bold yellow]Main Commands:[/bold yellow]")
            
            table = Table(show_header=False, box=box.SIMPLE)
            table.add_column("Command", style="cyan", width=25)
            table.add_column("Description", style="white")
            
            for cmd in standalone_commands:
                table.add_row(cmd.name, cmd.description)
            
            console.print(table)
    
    def suggest_workflow(self, goal: str) -> List[str]:
        """Suggest a workflow of commands for a goal"""
        goal_lower = goal.lower()
        
        workflows = {
            "code review": [
                "swiss-ai code:review --diff",
                "swiss-ai code:explain --file changed_file.py",
                "swiss-ai doctor --check-all"
            ],
            "project analysis": [
                "swiss-ai research:analyze",
                "swiss-ai research:summarize --directory src/",
                "swiss-ai code:review --security"
            ],
            "setup": [
                "swiss-ai config:init --wizard",
                "swiss-ai doctor",
                "swiss-ai model:list"
            ],
            "generate code": [
                "swiss-ai code:generate 'your description'",
                "swiss-ai code:review --file generated_file.py",
                "swiss-ai code:explain --file generated_file.py"
            ]
        }
        
        # Find matching workflow
        for workflow_name, commands in workflows.items():
            if any(keyword in goal_lower for keyword in workflow_name.split()):
                return commands
        
        return []

# Global instances
command_registry = CommandRegistry()
autocomplete_engine = AutocompleteEngine(command_registry)
command_discovery = CommandDiscovery(command_registry)

# Shell completion functions
def generate_bash_completion():
    """Generate bash completion script"""
    return '''
_swiss_ai_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Command completion
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        opts="chat doctor code:review code:generate code:explain research:analyze research:summarize config:init config:show config:validate model:list model:select model:test"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
    
    # Parameter completion
    case "${prev}" in
        --file|--output)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --model)
            opts="qwen3-coder claude-3-haiku gpt-4"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        --format)
            opts="json yaml rich plain"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
    esac
}

complete -F _swiss_ai_completion swiss-ai
complete -F _swiss_ai_completion swissai
'''

def install_shell_completion(shell: str = "bash"):
    """Install shell completion"""
    if shell == "bash":
        completion_script = generate_bash_completion()
        
        # Try to find bash completion directory
        completion_dirs = [
            Path.home() / ".bash_completion.d",
            Path("/etc/bash_completion.d"),
            Path("/usr/local/etc/bash_completion.d")
        ]
        
        for comp_dir in completion_dirs:
            if comp_dir.exists():
                comp_file = comp_dir / "swiss-ai"
                try:
                    comp_file.write_text(completion_script)
                    console.print(f"[green]✓[/green] Bash completion installed to {comp_file}")
                    console.print("[dim]Restart your shell or run: source ~/.bashrc[/dim]")
                    return
                except PermissionError:
                    continue
        
        # Fallback: add to .bashrc
        bashrc = Path.home() / ".bashrc"
        if bashrc.exists():
            with open(bashrc, "a") as f:
                f.write(f"\n# Swiss AI CLI completion\n{completion_script}\n")
            console.print("[green]✓[/green] Bash completion added to ~/.bashrc")
            console.print("[dim]Restart your shell to enable completion[/dim]")
        else:
            console.print("[yellow]⚠[/yellow] Could not install bash completion automatically")
            console.print("Add the following to your shell configuration:")
            console.print(Panel(completion_script, title="Bash Completion Script"))

def show_command_suggestions(partial_command: str):
    """Show command suggestions for partial input"""
    suggestions = autocomplete_engine.complete_command(partial_command)
    
    if not suggestions:
        # Try fuzzy matching
        similar = command_registry.get_similar_commands(partial_command)
        if similar:
            console.print(f"[yellow]No exact matches for '{partial_command}'[/yellow]")
            console.print("[yellow]Did you mean:[/yellow]")
            for cmd in similar:
                console.print(f"  [cyan]{cmd}[/cyan]")
        else:
            console.print(f"[red]No commands found matching '{partial_command}'[/red]")
        return
    
    console.print(f"[bold]Command suggestions for '[cyan]{partial_command}[/cyan]':[/bold]")
    
    table = Table(show_header=False, box=box.ROUNDED)
    table.add_column("Command", style="cyan", width=25)
    table.add_column("Description", style="white")
    
    for cmd, desc in suggestions:
        table.add_row(cmd, desc)
    
    console.print(table)