#!/usr/bin/env python3
from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


DEFAULT_RULES: Dict[str, Any] = {
    "sections": [
        "Data protection & secrecy",
        "Key & credential management",
        "Logging & auditability",
        "Secure configuration",
    ],
    "patterns": {
        "SECRET_KEY": r"(?i)(secret_key|api_key|apikey|access_key|secret)[\s:=\"]+[A-Za-z0-9_\-]{12,}",
        "PRIVATE_KEY": r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----",
        "HARDCODED_TOKEN": r"(?i)(bearer|token|auth)[\s:=\"]+[A-Za-z0-9_\-]{12,}",
        "PII_LOG": r"(?i)log\(.*(email|ssn|social|credit|iban|passport)",
        "DEBUG_TRUE": r"(?i)(debug\s*=\s*true|DEBUG\s*=\s*1)",
        "PLAIN_HTTP": r"(?i)http://[a-z0-9]",
    },
}


def _load_rules(name: str, rules_path: Optional[Path] = None) -> Dict[str, Any]:
    try:
        if rules_path:
            if rules_path.exists():
                import yaml
                return yaml.safe_load(rules_path.read_text(encoding="utf-8")) or DEFAULT_RULES
            return DEFAULT_RULES
        base = Path(__file__).resolve().parent.parent / "compliance" / "rules"
        path = base / f"{name}.yaml"
        if path.exists():
            import yaml
            return yaml.safe_load(path.read_text(encoding="utf-8")) or DEFAULT_RULES
        return DEFAULT_RULES
    except Exception:
        return DEFAULT_RULES


def _scan_repo(patterns: Dict[str, str], target_dir: Path) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    root = target_dir if target_dir else Path.cwd()
    code_ext = {".py", ".js", ".ts", ".tsx", ".json", ".yaml", ".yml", ".env", ".ini"}
    compiled = {k: re.compile(v, re.I | re.M) for k, v in patterns.items()}
    for p in root.rglob("**/*"):
        try:
            if not p.is_file():
                continue
            if p.suffix.lower() not in code_ext:
                continue
            if p.stat().st_size > 2_000_000:
                continue
            text = p.read_text(errors="ignore", encoding="utf-8")
            for key, rgx in compiled.items():
                for m in rgx.finditer(text):
                    issues.append({"rule": key, "file": str(p), "excerpt": m.group(0)[:120]})
        except Exception:
            continue
    return issues


def _render_table(title: str, findings: List[Dict[str, Any]]) -> None:
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("Rule", style="yellow", width=22)
    table.add_column("File", style="cyan")
    table.add_column("Excerpt", style="white")
    for f in findings[:200]:
        table.add_row(f.get("rule", ""), f.get("file", ""), f.get("excerpt", ""))
    console.print(table)


def _traffic_light(count: int) -> str:
    if count == 0:
        return "🟢 OK"
    if count <= 3:
        return "🟡 Attention"
    return "🔴 Risk"


async def run_finma_scan(target: str = ".", report: Optional[str] = None, rules: Optional[str] = None) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """Programmatic FINMA scan used by the web bridge.
    Returns (ok, report_path, summary_dict).
    """
    ruleset = _load_rules("finma", Path(rules) if rules else None)
    patterns = ruleset.get("patterns", {})
    sections = ruleset.get("sections", [])
    findings = _scan_repo(patterns, Path(target))
    status = _traffic_light(len(findings))
    summary = {"status": status, "count": len(findings), "sections": sections, "findings": findings}
    out_path = None
    if report:
        lines = ["# FINMA Compliance Report", "", f"Overall: {status}", ""]
        if sections:
            lines.append("## Areas Covered")
            for s in sections:
                lines.append(f"- {s}")
            lines.append("")
        if findings:
            lines.append("## Findings")
            for f in findings:
                lines.append(f"- {f['rule']}: {f['file']} — `{f['excerpt']}`")
        Path(report).write_text("\n".join(lines), encoding="utf-8")
        out_path = str(Path(report).resolve())
    return (len(findings) == 0, out_path, summary)


@click.group()
def compliance():
    """Swiss compliance checks and reporting."""
    pass


@compliance.command("finma")
@click.option("--report", type=click.Path(), help="Export markdown report path")
@click.option("--target", type=click.Path(), default=".", help="Target directory to scan")
@click.option("--rules", "rules_file", type=click.Path(), help="Path to custom FINMA rules YAML")
@click.option("--json", "json_flag", is_flag=True, help="Output as JSON")
def finma(report: Optional[str], target: str, rules_file: Optional[str], json_flag: bool):
    """Run FINMA-style baseline checks and produce a compliance summary."""
    # Load rules
    rules = _load_rules("finma", Path(rules_file) if rules_file else None)
    patterns = rules.get("patterns", {})
    sections = rules.get("sections", [])

    findings = _scan_repo(patterns, Path(target))
    status = _traffic_light(len(findings))

    # Create JSON output if requested
    if json_flag:
        json_output = {
            "status": status,
            "count": len(findings),
            "sections": sections,
            "findings": findings
        }
        
        # Handle report generation and add absolute path
        if report:
            out = ["# FINMA Compliance Report", "", f"Overall: {status}", ""]
            if sections:
                out.append("## Areas Covered")
                for s in sections:
                    out.append(f"- {s}")
                out.append("")
            if findings:
                out.append("## Findings")
                for f in findings:
                    out.append(f"- {f['rule']}: {f['file']} — `{f['excerpt']}`")
            Path(report).write_text("\n".join(out), encoding="utf-8")
            json_output["report_path"] = str(Path(report).resolve())
        
        console.print(json.dumps(json_output, indent=2))
        return

    console.print(Panel(f"FINMA baseline: {status} — {len(findings)} potential findings", title="Compliance", border_style="blue"))
    if findings:
        _render_table("Findings", findings)

    if report:
        out = ["# FINMA Compliance Report", "", f"Overall: {status}", ""]
        if sections:
            out.append("## Areas Covered")
            for s in sections:
                out.append(f"- {s}")
            out.append("")
        if findings:
            out.append("## Findings")
            for f in findings:
                out.append(f"- {f['rule']}: {f['file']} — `{f['excerpt']}`")
        Path(report).write_text("\n".join(out), encoding="utf-8")
        console.print(f"Saved report to [green]{report}[/green]")


