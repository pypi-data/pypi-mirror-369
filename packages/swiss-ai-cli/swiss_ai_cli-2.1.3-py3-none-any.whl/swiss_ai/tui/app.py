#!/usr/bin/env python3
"""
Minimal Textual TUI workspace for Swiss AI CLI.
Layout:
- Left: Chat panel
- Right: Context panel (files/tasks placeholder)
- Bottom: Status bar with model/agent

If Textual is not installed, a Rich fallback message is shown.
"""

from __future__ import annotations

from typing import Optional, List, Tuple

def run_tui(initial_message: Optional[str] = None) -> None:
    try:
        from textual.app import App, ComposeResult
        from textual.widgets import Header, Footer, Static, Input, Tabs
        from textual.containers import Horizontal, Vertical
        from textual.reactive import reactive

        # Lazy import command registry for palette
        try:
            from ..autocomplete import command_registry
        except Exception:
            command_registry = None

        class ChatView(Static):
            def __init__(self) -> None:
                super().__init__("", id="chat")
                self.history: list[str] = []

            def append(self, who: str, text: str) -> None:
                self.history.append(f"[bold]{who}[/bold]: {text}")
                self.update("\n".join(self.history[-200:]))

        class ContextView(Static):
            def __init__(self) -> None:
                super().__init__("(context) Press Ctrl+F for smart files, Ctrl+D for git diff\nF2 model menu; Enter to apply selection.", id="context")
                self.selected: set[str] = set()

            def set_items(self, title: str, items: List[Tuple[str, bool]]) -> None:
                lines = [f"[bold]{title}[/bold]"]
                for path, chosen in items:
                    mark = "[green]●[/green]" if chosen else "○"
                    lines.append(f" {mark} {path}")
                self.update("\n".join(lines))

        class StatusBar(Static):
            model = reactive("auto")
            agent = reactive("auto")
            def watch_model(self, v: str) -> None:
                self.update(f"Model: {v} | Agent: {self.agent}")
            def watch_agent(self, v: str) -> None:
                self.update(f"Model: {self.model} | Agent: {v}")

        class SwissAITUI(App):
            CSS = """
            #chat { border: heavy $accent; height: 1fr; }
            #context { border: heavy $secondary; height: 1fr; }
            #status { dock: bottom; height: 1; content-align: left middle; }
            #prompt { dock: bottom; height: 3; }
            """

            BINDINGS = [
                ("ctrl+k", "palette", "Command Palette"),
                ("ctrl+f", "files", "Pick Files"),
                ("ctrl+d", "diff", "Pick Git Diff"),
                ("f2", "switch_model", "Switch Model"),
                ("f4", "switch_agent", "Switch Agent"),
                ("escape", "app.quit", "Quit"),
            ]

            def compose(self) -> ComposeResult:
                yield Header(name="Swiss AI CLI")
                self.chat = ChatView()
                self.context = ContextView()
                with Horizontal():
                    with Vertical():
                        yield self.chat
                    with Vertical():
                        # Right pane tabs: Files / Diff / Models
                        self.tabs = Tabs("Files","Diff","Models", id="tabs")
                        yield self.tabs
                        yield self.context
                self.status = StatusBar(id="status")
                yield self.status
                self.input = Input(placeholder="Type message…", id="prompt")
                yield self.input
                yield Footer()
            
            def on_mount(self) -> None:
                self.chat.append("System", "Welcome to Swiss AI TUI")
                self.chat.append("System", "[dim]Ctrl+K palette, Ctrl+F files, Ctrl+D diff[/dim]")
                if initial_message:
                    self.chat.append("You", initial_message)

            def _execute_command(self, command: str) -> None:
                """Execute a swiss-ai command in background thread"""
                import threading
                import subprocess
                import sys
                import os
                
                self.chat.append("System", f"[cyan]Running:[/cyan] swiss-ai {command}")
                self.chat.append("System", "[dim]⟳ Executing...[/dim]")
                
                def run_command():
                    try:
                        # Construct command
                        cmd_parts = [sys.executable, "-m", "swiss_ai.cli_enhanced"]
                        
                        # Parse command (handle colons as separate arguments)
                        if ":" in command:
                            # Commands like "model:list" or "intelligence:analyze" 
                            cmd_parts.extend(command.split(":"))
                        else:
                            # Simple commands like "doctor"
                            cmd_parts.append(command)
                        
                        # Execute with timeout
                        result = subprocess.run(
                            cmd_parts,
                            capture_output=True,
                            text=True,
                            timeout=60,  # 60 second timeout
                            cwd=os.getcwd(),
                            env=os.environ.copy()
                        )
                        
                        # Handle results on main thread
                        self.call_from_thread(self._handle_command_result, command, result)
                        
                    except subprocess.TimeoutExpired:
                        self.call_from_thread(
                            self.chat.append,
                            "System", 
                            f"[dim red]✗ Command '{command}' timed out after 60 seconds[/dim red]"
                        )
                    except Exception as e:
                        self.call_from_thread(
                            self.chat.append,
                            "System",
                            f"[dim red]✗ Execution failed: {str(e)[:100]}[/dim red]"
                        )
                
                # Start execution in background thread
                thread = threading.Thread(target=run_command, daemon=True)
                thread.start()
            
            def _handle_command_result(self, command: str, result) -> None:
                """Handle command execution result on main thread"""
                if result.returncode == 0:
                    # Success - process stdout
                    output = result.stdout.strip()
                    if output:
                        lines = output.split('\n')
                        if len(lines) > 200:
                            # Truncate long output
                            display_lines = lines[:200]
                            truncated_output = '\n'.join(display_lines)
                            self.chat.append("System", f"[green]✓[/green] Command completed:")
                            self.chat.append("Output", truncated_output)
                            self.chat.append("System", f"[dim]… (truncated {len(lines) - 200} more lines)[/dim]")
                        else:
                            # Show full output
                            self.chat.append("System", f"[green]✓[/green] Command completed:")
                            self.chat.append("Output", output)
                    else:
                        self.chat.append("System", f"[green]✓[/green] Command '{command}' completed (no output)")
                    
                    # Show stderr if present (warnings, etc.)
                    if result.stderr.strip():
                        stderr_lines = result.stderr.strip().split('\n')[:5]  # First 5 lines only
                        stderr_text = '\n'.join(stderr_lines)
                        self.chat.append("System", f"[yellow]Warnings:[/yellow] {stderr_text}")
                        
                else:
                    # Error - show brief summary and first lines of stderr
                    stderr = result.stderr.strip() or result.stdout.strip()
                    if stderr:
                        error_lines = stderr.split('\n')[:20]  # First 20 lines
                        error_text = '\n'.join(error_lines)
                        self.chat.append("System", f"[dim red]✗ Command failed (exit code {result.returncode})[/dim red]")
                        self.chat.append("Error", f"[dim red]{error_text}[/dim red]")
                    else:
                        self.chat.append("System", f"[dim red]✗ Command failed with exit code {result.returncode}[/dim red]")

            def _search_commands(self, query: str) -> List[Tuple[str, str]]:
                # returns list of (command, description)
                results: List[Tuple[str, str]] = []
                try:
                    if not command_registry:
                        return results
                    q = query.lower()
                    # Simple contains match first
                    for name, info in command_registry.commands.items():
                        if q in name.lower() or (q and q in (info.description or "").lower()):
                            desc = info.description or ""
                            results.append((name, desc))
                    # Fallback to fuzzy
                    if not results and q:
                        from difflib import get_close_matches
                        pool = list(command_registry.commands.keys())
                        for m in get_close_matches(query, pool, n=10, cutoff=0.4):
                            desc = command_registry.commands[m].description or ""
                            results.append((m, desc))
                except Exception:
                    pass
                return results[:10]

            def action_palette(self) -> None:
                # Inline minimal palette: reuse prompt as palette with hint, output suggestions to chat
                self.chat.append("System", "Palette: type to search commands, Enter to insert, Esc to cancel.")
                # Preload a few common commands
                suggestions = self._search_commands("") if command_registry else []
                if suggestions:
                    pretty = "\n".join([f" • [cyan]{c}[/cyan] — {d}" for c, d in suggestions])
                    self.chat.append("System", pretty)
                # Set placeholder to indicate palette mode
                self.input.placeholder = "Search commands… (palette)"

            def action_switch_model(self) -> None:
                # Fetch models via bridge and show in context
                import threading, os, requests
                self.context.update("(models) Loading…")
                def fetch():
                    try:
                        key = os.getenv('SWISS_AI_BRIDGE_KEY','')
                        r = requests.get("http://127.0.0.1:8787/models", headers={"x-bridge-key": key}, timeout=6)
                        r.raise_for_status()
                        data = r.json()
                        models = data.get('available', [])
                        items = []
                        for m in models[:50]:
                            label = f"{m.get('id','')} — {m.get('name','')}"
                            items.append((label, False))
                        self.call_from_thread(self.context.set_items, "Models (Enter to set DEFAULT_MODEL)", items)
                    except Exception as e:
                        self.call_from_thread(self.context.update, f"(models) Error: {str(e)[:80]}")
                threading.Thread(target=fetch, daemon=True).start()

            def action_switch_agent(self) -> None:
                self.status.agent = "auto" if self.status.agent != "auto" else "code"

            def on_input_submitted(self, event: Input.Submitted) -> None:
                text = event.value.strip()
                if not text:
                    return
                # Detect palette mode
                if "palette" in (self.input.placeholder or "").lower():
                    results = self._search_commands(text)
                    if results:
                        chosen = results[0][0]
                        self._execute_command(chosen)
                        # Reset prompt
                        self.input.placeholder = "Type message…"
                        self.input.value = ""
                        return
                    else:
                        self.chat.append("System", "No matches.")
                        self.input.placeholder = "Type message…"
                        self.input.value = ""
                        return
                # Normal chat
                self.chat.append("You", text)
                self.input.value = ""
                self.chat.append("Assistant", "(preview) Processing…")

            # File and diff pickers (right pane)
            def action_files(self) -> None:
                try:
                    # Use smart-select for intelligent file ranking
                    from ..commands.context_cmds import smart_select_files
                    from pathlib import Path
                    
                    self.context.update("(smart-select) Analyzing files...")
                    
                    # Run smart-select in background thread to avoid blocking UI
                    import threading
                    
                    def run_smart_select():
                        try:
                            project_path = Path.cwd()
                            results = smart_select_files(project_path, limit=20)
                            
                            # Format for display
                            files_data = results.get("files", [])
                            items = []
                            
                            for file_info in files_data:
                                file_path = file_info["path"]
                                score = file_info["score"]
                                reasons = ", ".join(file_info.get("reasons", []))[:40]
                                
                                # Format: filename (score) - reasons
                                display_name = f"{file_path} ({score:.2f}) - {reasons}"
                                items.append((display_name, file_path in self.context.selected))
                            
                            # Update UI on main thread
                            self.call_from_thread(
                                self.context.set_items,
                                f"Smart Files (query: {results.get('query_used', 'auto')[:30]}...)",
                                items
                            )
                            
                        except Exception as e:
                            # Fallback to simple file listing
                            self.call_from_thread(
                                self._fallback_file_listing
                            )
                    
                    thread = threading.Thread(target=run_smart_select, daemon=True)
                    thread.start()
                    
                except Exception:
                    self._fallback_file_listing()
            
            def _fallback_file_listing(self) -> None:
                try:
                    from pathlib import Path
                    files = []
                    for p in Path('.').glob('**/*'):
                        if p.is_file() and p.stat().st_size < 2_000_000:
                            if any(p.suffix.lower() in ext for ext in ([".py",".md",".txt",".json",".yaml",".yml",".ts",".tsx",".js"])):
                                files.append(str(p))
                                if len(files) >= 50:
                                    break
                    items = [(f, f in self.context.selected) for f in files]
                    self.context.set_items("Files (first 50)", items)
                except Exception:
                    self.context.update("(files) Unable to list files")

            def action_diff(self) -> None:
                import subprocess
                try:
                    out = subprocess.run(["git","diff","--name-only"], capture_output=True, text=True, timeout=2)
                    names = [line.strip() for line in out.stdout.splitlines() if line.strip()]
                    items = [(f, f in self.context.selected) for f in names]
                    self.context.set_items("Git Diff (name-only)", items)
                except Exception:
                    self.context.update("(diff) Not a git repository or git not available")

        SwissAITUI().run()
    except Exception:
        try:
            from rich.console import Console
            from rich.panel import Panel
            c = Console()
            msg = "Textual is not installed. Install with: pip install textual\nThen run: swiss-ai ui"
            c.print(Panel(msg, title="Swiss AI TUI"))
        except Exception:
            pass


