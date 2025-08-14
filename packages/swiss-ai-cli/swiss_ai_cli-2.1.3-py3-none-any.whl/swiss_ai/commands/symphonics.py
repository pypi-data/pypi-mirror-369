#!/usr/bin/env python3
"""
Symphonics command suite: operationalize Aurequest → Fracturemap → Chordcraft → Reverline → Archivista

Lightweight session management stored under ~/.swiss-ai/symphonics/<session_id>.json
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from ..api.client import SwissAIAPIClient
from ..config.manager import ConfigManager

console = Console()


def _store_dir() -> Path:
    d = Path.home() / ".swiss-ai" / "symphonics"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _session_path(session_id: str) -> Path:
    return _store_dir() / f"{session_id}.json"


def _load_session(session_id: str) -> Dict[str, Any]:
    p = _session_path(session_id)
    if not p.exists():
        raise click.ClickException(f"Session not found: {session_id}")
    return json.loads(p.read_text(encoding="utf-8") or "{}")


def _save_session(session_id: str, data: Dict[str, Any]) -> None:
    p = _session_path(session_id)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _new_session(title: str, tags: Optional[List[str]] = None) -> str:
    session_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    data = {
        "id": session_id,
        "title": title,
        "tags": tags or [],
        "created_at": int(time.time()),
        "movements": [],
        "roles": {},
        "status": "active",
    }
    _save_session(session_id, data)
    return session_id


def _append_movement(session_id: str, movement: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = _load_session(session_id)
    entry = {"movement": movement, "timestamp": int(time.time()), **payload}
    data.setdefault("movements", []).append(entry)
    _save_session(session_id, data)
    return data


def _ensure_api() -> SwissAIAPIClient:
    # Lazy create API client with config
    cfg = ConfigManager()
    return SwissAIAPIClient(cfg)


@click.group()
def symphonics():
    """Symphonics: run Aurequest → Fracturemap → Chordcraft → Reverline → Archivista."""
    pass


@symphonics.command("start")
@click.option("--title", required=True, help="Session title")
@click.option("--tag", multiple=True, help="Optional tags")
def start_session(title: str, tag: List[str]):
    """Start a new Symphonics session and return its session id."""
    sid = _new_session(title, list(tag))
    console.print(Panel(f"Session started: [cyan]{sid}[/cyan]", title="Symphonics", border_style="blue"))


@symphonics.command("list")
def list_sessions():
    """List existing Symphonics sessions."""
    rows = []
    for p in sorted(_store_dir().glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            d = json.loads(p.read_text(encoding="utf-8") or "{}")
            rows.append((d.get("id", p.stem), d.get("title", ""), d.get("status", ""), len(d.get("movements", []))))
        except Exception:
            continue
    table = Table(title="Symphonics Sessions", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Status", style="yellow")
    table.add_column("Steps", style="green")
    for r in rows:
        table.add_row(*map(str, r))
    console.print(table)


@symphonics.command("aurequest")
@click.option("--session-id", required=True)
@click.option("--what", required=True, help="Intent / purpose")
@click.option("--why", default="", help="Desired feeling / goal")
def aurequest(session_id: str, what: str, why: str):
    """Record the initial intent (Aurequest)."""
    data = _append_movement(session_id, "Aurequest", {"what": what, "why": why})
    console.print(Panel(f"Aurequest captured for [cyan]{session_id}[/cyan]", title="Aurequest", border_style="green"))


@symphonics.command("fracturemap")
@click.option("--session-id", required=True)
@click.option("--hint", default="", help="Context or constraints to guide the split")
@click.option("--auto", is_flag=True, help="Use AI to propose sub-tasks")
def fracturemap(session_id: str, hint: str, auto: bool):
    """Split the intent into harmonized sub-tasks."""
    tasks: List[str]
    if auto:
        prompt = (
            "You are Strucynth. Split the user's intent into 3-7 harmonized sub-tasks for diverse AI agents.\n"
            "Guidelines: concise task names, include purpose in parentheses, and ask 2 clarifying questions if useful.\n"
            f"Context hint: {hint or '—'}\n"
            "Return as a bullet list (e.g., '- Task (purpose)') without prose."
        )
        try:
            api = _ensure_api()
            # Non-async path: use simple_chat synchronously by running event loop internally if needed
            # Fallback: if event loop cannot be used here, return a sensible default
            import asyncio
            async def _call():
                return await api.simple_chat(prompt, model="deepseek/deepseek-r1:free")
            try:
                res = asyncio.run(_call())
                text = res.content if res and res.success else ""
            except RuntimeError:
                # If already in a running loop (rare in CLI), skip
                text = ""
            lines = [l.strip("- ") for l in (text or "").splitlines() if l.strip()]
            tasks = lines[:7] or ["Draft flow", "Create exercises", "Clarity check"]
        except Exception:
            tasks = ["Draft flow", "Create exercises", "Clarity check"]
    else:
        tasks = [s.strip() for s in hint.split(";") if s.strip()] or ["Draft flow", "Create exercises", "Clarity check"]

    data = _append_movement(session_id, "Fracturemap", {"tasks": tasks})
    table = Table(title="Fracturemap", box=box.ROUNDED)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Task", style="white")
    for i, t in enumerate(tasks, 1):
        table.add_row(str(i), t)
    console.print(table)


@symphonics.command("chordcraft")
@click.option("--session-id", required=True)
@click.option("--notes", default="", help="Notes for weaving outputs")
def chordcraft(session_id: str, notes: str):
    """Record integration step and notes (Chordcraft)."""
    _append_movement(session_id, "Chordcraft", {"notes": notes})
    console.print(Panel("Integration recorded", title="Chordcraft", border_style="magenta"))


@symphonics.command("reverline")
@click.option("--session-id", required=True)
@click.option("--auto", is_flag=True, help="Ask AI to critique and suggest improvements")
def reverline(session_id: str, auto: bool):
    """Feedback loop — optionally use AI to critique and synthesize improvements."""
    critique = ""
    if auto:
        data = _load_session(session_id)
        recent = data.get("movements", [])[-5:]
        transcript = json.dumps(recent, indent=2)
        prompt = (
            "You are Resonara. Critique and suggest improvements to the current work-in-progress.\n"
            "Return a prioritized list of 3-5 improvements and a one-paragraph synthesis.\n"
            f"Transcript:\n{transcript}\n"
        )
        try:
            import asyncio
            api = _ensure_api()
            async def _call():
                return await api.simple_chat(prompt, model="deepseek/deepseek-r1:free")
            try:
                res = asyncio.run(_call())
                if res and res.success:
                    critique = res.content
                else:
                    critique = "(ai) Consider clarity, examples, and alignment to goals; provide a brief synthesis."
            except RuntimeError:
                critique = "(ai) Clarity, examples, alignment; short synthesis."
        except Exception:
            critique = "(local) Provide clearer structure; add tests; reduce redundancy."
    _append_movement(session_id, "Reverline", {"critique": critique})
    console.print(Panel(critique or "Reverline recorded", title="Reverline", border_style="yellow"))


@symphonics.command("archivista")
@click.option("--session-id", required=True)
@click.option("--export", type=click.Path(), help="Optional export path (JSON)")
def archivista(session_id: str, export: Optional[str]):
    """Close session and optionally export the score."""
    data = _load_session(session_id)
    data["status"] = "archived"
    _save_session(session_id, data)
    if export:
        Path(export).write_text(json.dumps(data, indent=2), encoding="utf-8")
        console.print(f"Exported to [green]{export}[/green]")
    else:
        console.print(Panel("Session archived", title="Archivista", border_style="green"))


