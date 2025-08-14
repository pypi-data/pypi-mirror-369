#!/usr/bin/env python3
"""
Intelligence analysis commands for code quality assessment
Integrates Bandit (security), Radon (complexity), git churn, and dependency analysis
"""

import json
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

# Scoring weights for swiss-banking rubric
SWISS_BANKING_WEIGHTS = {
    "security": 0.50,
    "complexity": 0.25, 
    "churn": 0.15,
    "dependencies": 0.10
}

def run_tool_with_timeout(cmd: List[str], timeout: int = 30, cwd: Optional[Path] = None) -> Tuple[bool, str, str]:
    """Run a subprocess command with timeout and return (success, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return False, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return False, "", str(e)

def analyze_security_with_bandit(project_path: Path) -> Dict[str, Any]:
    """Run Bandit security analysis"""
    success, stdout, stderr = run_tool_with_timeout(
        [sys.executable, "-m", "bandit", "-q", "-f", "json", "-r", str(project_path)],
        timeout=30,
        cwd=project_path
    )
    
    if not success:
        return {
            "tool_available": False,
            "error": stderr or "Bandit not installed",
            "issues": 0,
            "summary": "Security analysis unavailable"
        }
    
    try:
        bandit_result = json.loads(stdout) if stdout.strip() else {"results": []}
        issues = bandit_result.get("results", [])
        
        # Categorize by severity
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in issues:
            severity = issue.get("issue_severity", "LOW")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "tool_available": True,
            "issues": len(issues),
            "summary": f"{len(issues)} security issues found",
            "severity_breakdown": severity_counts,
            "high_risk_files": [
                issue["filename"] for issue in issues 
                if issue.get("issue_severity") == "HIGH"
            ][:5]  # Top 5 high-risk files
        }
    except json.JSONDecodeError:
        return {
            "tool_available": True,
            "error": "Failed to parse Bandit output",
            "issues": 0,
            "summary": "Security analysis failed"
        }

def analyze_complexity_with_radon(project_path: Path) -> Dict[str, Any]:
    """Run Radon complexity and maintainability analysis"""
    # Cyclomatic Complexity
    cc_success, cc_stdout, cc_stderr = run_tool_with_timeout(
        [sys.executable, "-m", "radon", "cc", "-j", str(project_path)],
        timeout=30,
        cwd=project_path
    )
    
    # Maintainability Index  
    mi_success, mi_stdout, mi_stderr = run_tool_with_timeout(
        [sys.executable, "-m", "radon", "mi", "-j", str(project_path)],
        timeout=30, 
        cwd=project_path
    )
    
    result = {"tool_available": False}
    
    if not cc_success and not mi_success:
        result.update({
            "error": cc_stderr or "Radon not installed",
            "avg_cc": 0,
            "avg_mi": 0,
            "summary": "Complexity analysis unavailable"
        })
        return result
    
    result["tool_available"] = True
    
    # Parse complexity results
    if cc_success and cc_stdout.strip():
        try:
            cc_data = json.loads(cc_stdout)
            complexities = []
            worst_files = []
            
            for file_path, methods in cc_data.items():
                for method in methods:
                    complexity = method.get("complexity", 0)
                    complexities.append(complexity)
                    if complexity > 10:  # High complexity threshold
                        worst_files.append({
                            "file": file_path,
                            "method": method.get("name", "unknown"),
                            "complexity": complexity
                        })
            
            result.update({
                "avg_cc": sum(complexities) / len(complexities) if complexities else 0,
                "max_cc": max(complexities) if complexities else 0,
                "worst_files": sorted(worst_files, key=lambda x: x["complexity"], reverse=True)[:5]
            })
        except json.JSONDecodeError:
            result.update({"avg_cc": 0, "max_cc": 0, "worst_files": []})
    else:
        result.update({"avg_cc": 0, "max_cc": 0, "worst_files": []})
    
    # Parse maintainability results
    if mi_success and mi_stdout.strip():
        try:
            mi_data = json.loads(mi_stdout)
            maintainability_scores = []
            low_mi_files = []
            
            for file_path, mi_score in mi_data.items():
                if isinstance(mi_score, (int, float)):
                    maintainability_scores.append(mi_score)
                    if mi_score < 50:  # Low maintainability threshold
                        low_mi_files.append({"file": file_path, "mi_score": mi_score})
            
            result.update({
                "avg_mi": sum(maintainability_scores) / len(maintainability_scores) if maintainability_scores else 0,
                "min_mi": min(maintainability_scores) if maintainability_scores else 0,
                "low_mi_files": sorted(low_mi_files, key=lambda x: x["mi_score"])[:5]
            })
        except json.JSONDecodeError:
            result.update({"avg_mi": 0, "min_mi": 0, "low_mi_files": []})
    else:
        result.update({"avg_mi": 0, "min_mi": 0, "low_mi_files": []})
    
    # Generate summary
    avg_cc = result.get("avg_cc", 0)
    avg_mi = result.get("avg_mi", 0)
    result["summary"] = f"Avg complexity: {avg_cc:.1f}, Avg maintainability: {avg_mi:.1f}"
    
    return result

def analyze_churn_with_git(project_path: Path, commit_limit: int = 500) -> Dict[str, Any]:
    """Analyze code churn using git log"""
    success, stdout, stderr = run_tool_with_timeout(
        ["git", "log", f"--max-count={commit_limit}", "--name-only", "--pretty=format:"],
        timeout=30,
        cwd=project_path
    )
    
    if not success:
        return {
            "tool_available": False,
            "error": stderr or "Not a git repository",
            "top_files": [],
            "summary": "Churn analysis unavailable"
        }
    
    # Count file modifications
    file_changes = {}
    lines = stdout.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            file_changes[line] = file_changes.get(line, 0) + 1
    
    # Get top churned files
    top_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "tool_available": True,
        "top_files": [{"file": f, "changes": c} for f, c in top_files],
        "total_files_touched": len(file_changes),
        "commits_analyzed": commit_limit,
        "summary": f"{len(file_changes)} files modified in last {commit_limit} commits"
    }

def analyze_dependencies_with_pipdeptree(project_path: Path) -> Dict[str, Any]:
    """Analyze dependencies with pipdeptree"""
    # Try JSON format first
    success, stdout, stderr = run_tool_with_timeout(
        [sys.executable, "-m", "pipdeptree", "--json-tree"],
        timeout=30,
        cwd=project_path
    )
    
    if not success:
        # Fallback to plain text
        success_text, stdout_text, stderr_text = run_tool_with_timeout(
            [sys.executable, "-m", "pipdeptree"],
            timeout=30,
            cwd=project_path
        )
        
        if not success_text:
            return {
                "tool_available": False,
                "error": stderr or "pipdeptree not installed",
                "count": 0,
                "summary": "Dependency analysis unavailable"
            }
        
        # Parse text output for basic info
        lines = stdout_text.strip().split('\n')
        dep_count = len([l for l in lines if l.strip() and not l.startswith(' ')])
        
        return {
            "tool_available": True,
            "format": "text",
            "count": dep_count,
            "text_output": stdout_text[:500] + "..." if len(stdout_text) > 500 else stdout_text,
            "summary": f"{dep_count} top-level dependencies found"
        }
    
    # Parse JSON output
    try:
        deps = json.loads(stdout) if stdout.strip() else []
        
        def count_deps(deps_list):
            count = 0
            for dep in deps_list:
                count += 1
                count += count_deps(dep.get("dependencies", []))
            return count
        
        total_deps = count_deps(deps)
        top_level_count = len(deps)
        
        # Identify potential risks (packages with many dependencies)
        risky_deps = []
        for dep in deps:
            dep_name = dep.get("package_name", "unknown")
            dep_count = count_deps(dep.get("dependencies", []))
            if dep_count > 5:  # Arbitrary threshold
                risky_deps.append({"name": dep_name, "dep_count": dep_count})
        
        return {
            "tool_available": True,
            "format": "json",
            "count": total_deps,
            "top_level_count": top_level_count,
            "risky_dependencies": sorted(risky_deps, key=lambda x: x["dep_count"], reverse=True)[:5],
            "summary": f"{total_deps} total dependencies ({top_level_count} top-level)"
        }
        
    except json.JSONDecodeError:
        return {
            "tool_available": True,
            "error": "Failed to parse pipdeptree JSON output",
            "count": 0,
            "summary": "Dependency analysis failed"
        }

def generate_dependency_graph(project_path: Path, output_dir: Path) -> Optional[str]:
    """Generate dependency graph files (text and optionally SVG)"""
    # Generate text graph
    success, stdout, stderr = run_tool_with_timeout(
        [sys.executable, "-m", "pipdeptree", "--graph-output", "txt"],
        timeout=30,
        cwd=project_path
    )
    
    txt_path = None
    if success and stdout.strip():
        txt_path = output_dir / "depgraph.txt"
        txt_path.write_text(stdout)
    
    # Try to generate SVG if graphviz is available
    svg_success, svg_stdout, svg_stderr = run_tool_with_timeout(
        [sys.executable, "-m", "pipdeptree", "--graph-output", "svg"],
        timeout=60,
        cwd=project_path
    )
    
    svg_path = None
    if svg_success and svg_stdout.strip():
        svg_path = output_dir / "depgraph.svg"
        svg_path.write_text(svg_stdout)
    
    return str(txt_path.resolve()) if txt_path else None

def create_reports_directory() -> Path:
    """Create timestamped reports directory"""
    base_dir = Path.home() / ".swiss-ai" / "reports" / "intelligence"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = base_dir / timestamp
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir

def generate_markdown_report(analysis_results: Dict[str, Any], output_path: Path) -> None:
    """Generate Markdown report from analysis results"""
    timestamp = analysis_results.get("timestamp", "unknown")
    
    md_content = f"""# Code Intelligence Report

**Generated:** {datetime.fromtimestamp(timestamp).isoformat() if isinstance(timestamp, (int, float)) else timestamp}

## Executive Summary

This report analyzes code quality across multiple dimensions: security vulnerabilities, complexity metrics, code churn patterns, and dependency risks.

## Security Analysis (Bandit)

"""
    
    security = analysis_results.get("security", {})
    if security.get("tool_available"):
        md_content += f"""- **Issues Found:** {security.get("issues", 0)}
- **Summary:** {security.get("summary", "N/A")}

### Severity Breakdown
"""
        for severity, count in security.get("severity_breakdown", {}).items():
            md_content += f"- {severity}: {count}\n"
        
        high_risk_files = security.get("high_risk_files", [])
        if high_risk_files:
            md_content += "\n### High Risk Files\n"
            for file in high_risk_files:
                md_content += f"- `{file}`\n"
    else:
        md_content += f"- **Status:** Tool unavailable ({security.get('error', 'Unknown error')})\n"
    
    md_content += "\n## Complexity Analysis (Radon)\n\n"
    complexity = analysis_results.get("complexity", {})
    if complexity.get("tool_available"):
        md_content += f"""- **Average Complexity:** {complexity.get("avg_cc", 0):.1f}
- **Average Maintainability:** {complexity.get("avg_mi", 0):.1f}
- **Summary:** {complexity.get("summary", "N/A")}

"""
        worst_files = complexity.get("worst_files", [])
        if worst_files:
            md_content += "### High Complexity Files\n"
            for file_info in worst_files:
                md_content += f"- `{file_info['file']}::{file_info['method']}` (CC: {file_info['complexity']})\n"
    else:
        md_content += f"- **Status:** Tool unavailable ({complexity.get('error', 'Unknown error')})\n"
    
    md_content += "\n## Code Churn Analysis (Git)\n\n"
    churn = analysis_results.get("churn", {})
    if churn.get("tool_available"):
        md_content += f"""- **Summary:** {churn.get("summary", "N/A")}
- **Files Analyzed:** {churn.get("total_files_touched", 0)}

### Most Changed Files
"""
        for file_info in churn.get("top_files", [])[:5]:
            md_content += f"- `{file_info['file']}` ({file_info['changes']} changes)\n"
    else:
        md_content += f"- **Status:** Tool unavailable ({churn.get('error', 'Unknown error')})\n"
    
    md_content += "\n## Dependency Analysis (pipdeptree)\n\n"
    deps = analysis_results.get("deps", {})
    if deps.get("tool_available"):
        md_content += f"""- **Summary:** {deps.get("summary", "N/A")}
- **Total Dependencies:** {deps.get("count", 0)}

"""
        risky_deps = deps.get("risky_dependencies", [])
        if risky_deps:
            md_content += "### Dependencies with Many Sub-dependencies\n"
            for dep in risky_deps:
                md_content += f"- `{dep['name']}` ({dep['dep_count']} dependencies)\n"
    else:
        md_content += f"- **Status:** Tool unavailable ({deps.get('error', 'Unknown error')})\n"
    
    md_content += "\n## Artifacts\n\n"
    artifacts = analysis_results.get("artifacts", {})
    for key, path in artifacts.items():
        if path:
            md_content += f"- **{key.replace('_', ' ').title()}:** `{path}`\n"
    
    output_path.write_text(md_content, encoding="utf-8")

def calculate_swiss_banking_score(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate composite score using swiss-banking rubric"""
    security = analysis_results.get("security", {})
    complexity = analysis_results.get("complexity", {})
    churn = analysis_results.get("churn", {})
    deps = analysis_results.get("deps", {})
    
    # Security score (0-100, higher is better)
    security_score = 100
    if security.get("tool_available"):
        issues = security.get("issues", 0)
        high_issues = security.get("severity_breakdown", {}).get("HIGH", 0)
        # Penalize based on issues, with extra penalty for high severity
        security_score = max(0, 100 - (issues * 5) - (high_issues * 10))
    else:
        security_score = 50  # Neutral score when tool unavailable
    
    # Complexity score (0-100, higher is better) 
    complexity_score = 100
    if complexity.get("tool_available"):
        avg_cc = complexity.get("avg_cc", 0)
        avg_mi = complexity.get("avg_mi", 100)
        # Penalize high complexity and low maintainability
        complexity_score = max(0, min(100, 100 - (avg_cc * 2) + (avg_mi - 50)))
    else:
        complexity_score = 50
    
    # Churn score (0-100, higher is better)
    churn_score = 100
    if churn.get("tool_available"):
        total_files = churn.get("total_files_touched", 0)
        top_changes = churn.get("top_files", [])
        if top_changes:
            max_changes = max(f["changes"] for f in top_changes)
            # Penalize high churn
            churn_score = max(0, 100 - (max_changes / 10) - (total_files / 50))
    else:
        churn_score = 50
    
    # Dependency risk score (0-100, higher is better)
    deps_score = 100
    if deps.get("tool_available"):
        total_deps = deps.get("count", 0)
        risky_deps = len(deps.get("risky_dependencies", []))
        # Penalize large dependency footprint and risky dependencies
        deps_score = max(0, 100 - (total_deps / 10) - (risky_deps * 5))
    else:
        deps_score = 50
    
    # Calculate weighted overall score
    overall_score = (
        security_score * SWISS_BANKING_WEIGHTS["security"] +
        complexity_score * SWISS_BANKING_WEIGHTS["complexity"] + 
        churn_score * SWISS_BANKING_WEIGHTS["churn"] +
        deps_score * SWISS_BANKING_WEIGHTS["dependencies"]
    )
    
    return {
        "overall_score": round(overall_score, 1),
        "breakdown": {
            "security": round(security_score, 1),
            "complexity": round(complexity_score, 1), 
            "churn": round(churn_score, 1),
            "dependencies": round(deps_score, 1)
        },
        "rubric": {
            "weights": SWISS_BANKING_WEIGHTS,
            "description": "Swiss banking regulatory compliance scoring"
        }
    }

@click.group()
def intelligence():
    """Code intelligence analysis and scoring commands."""
    pass

@intelligence.command("analyze")
@click.option("--json", "json_flag", is_flag=True, help="Output as JSON")
def analyze(json_flag: bool):
    """Run comprehensive code intelligence analysis
    
    Analyzes security (Bandit), complexity (Radon), churn (git log), and dependencies (pipdeptree).
    Generates JSON and Markdown reports in ~/.swiss-ai/reports/intelligence/<timestamp>/
    """
    project_path = Path.cwd()
    
    # Create reports directory
    report_dir = create_reports_directory()
    
    # Run all analyses
    with console.status("Running code intelligence analysis...", spinner="dots") as status:
        status.update("Analyzing security with Bandit...")
        security_results = analyze_security_with_bandit(project_path)
        
        status.update("Analyzing complexity with Radon...")
        complexity_results = analyze_complexity_with_radon(project_path)
        
        status.update("Analyzing code churn with git...")
        churn_results = analyze_churn_with_git(project_path)
        
        status.update("Analyzing dependencies with pipdeptree...")
        deps_results = analyze_dependencies_with_pipdeptree(project_path)
        
        status.update("Generating dependency graph...")
        depgraph_path = generate_dependency_graph(project_path, report_dir)
    
    # Compile results
    timestamp = time.time()
    analysis_results = {
        "timestamp": timestamp,
        "security": security_results,
        "complexity": complexity_results,
        "churn": churn_results,
        "deps": deps_results,
        "artifacts": {
            "json_path": str((report_dir / "summary.json").resolve()),
            "md_path": str((report_dir / "summary.md").resolve()),
            "depgraph_path": depgraph_path
        }
    }
    
    # Save JSON report
    json_path = report_dir / "summary.json"
    json_path.write_text(json.dumps(analysis_results, indent=2), encoding="utf-8")
    
    # Save Markdown report
    md_path = report_dir / "summary.md"
    generate_markdown_report(analysis_results, md_path)
    
    if json_flag:
        # Output only JSON to stdout
        console.print(json.dumps(analysis_results, indent=2))
    else:
        # Display Rich summary
        display_analysis_summary(analysis_results)

@intelligence.command("score")
@click.option("--rules", default="swiss-banking", help="Scoring rules to apply")
@click.option("--json", "json_flag", is_flag=True, help="Output as JSON") 
def score(rules: str, json_flag: bool):
    """Calculate composite code quality score using specified rules
    
    Currently supports 'swiss-banking' rules with weighted scoring:
    - Security: 50% weight
    - Complexity: 25% weight  
    - Churn: 15% weight
    - Dependencies: 10% weight
    """
    if rules != "swiss-banking":
        console.print(f"[red]Error: Unknown rules '{rules}'. Only 'swiss-banking' is supported.[/red]")
        return
    
    project_path = Path.cwd()
    
    # Run analysis (reuse analyze logic but don't save reports)
    with console.status("Analyzing code for scoring...", spinner="dots"):
        security_results = analyze_security_with_bandit(project_path)
        complexity_results = analyze_complexity_with_radon(project_path) 
        churn_results = analyze_churn_with_git(project_path)
        deps_results = analyze_dependencies_with_pipdeptree(project_path)
    
    analysis_results = {
        "security": security_results,
        "complexity": complexity_results, 
        "churn": churn_results,
        "deps": deps_results
    }
    
    # Calculate score
    score_results = calculate_swiss_banking_score(analysis_results)
    
    if json_flag:
        console.print(json.dumps(score_results, indent=2))
    else:
        display_score_summary(score_results)

def display_analysis_summary(results: Dict[str, Any]):
    """Display Rich analysis summary"""
    console.print("\n[bold blue]🧠 Code Intelligence Analysis Complete[/bold blue]")
    
    # Create summary table
    table = Table(title="Analysis Results", box=box.ROUNDED)
    table.add_column("Component", style="cyan", width=15)
    table.add_column("Status", style="green", width=12)
    table.add_column("Summary", style="white")
    
    components = ["security", "complexity", "churn", "deps"]
    component_names = ["Security", "Complexity", "Code Churn", "Dependencies"]
    
    for comp, name in zip(components, component_names):
        comp_data = results.get(comp, {})
        if comp_data.get("tool_available"):
            status = "✓ Available"
            summary = comp_data.get("summary", "No summary")
        else:
            status = "✗ Unavailable"
            summary = comp_data.get("error", "Tool not found")
        
        table.add_row(name, status, summary)
    
    console.print(table)
    
    # Show artifacts
    artifacts = results.get("artifacts", {})
    if artifacts:
        console.print(f"\n[bold green]📄 Reports Generated:[/bold green]")
        for key, path in artifacts.items():
            if path:
                console.print(f"  {key.replace('_', ' ').title()}: [cyan]{path}[/cyan]")

def display_score_summary(results: Dict[str, Any]):
    """Display Rich score summary"""
    overall = results.get("overall_score", 0)
    breakdown = results.get("breakdown", {})
    
    # Determine overall rating
    if overall >= 80:
        rating = "[green]Excellent[/green]"
        rating_icon = "🟢"
    elif overall >= 60:
        rating = "[yellow]Good[/yellow]"
        rating_icon = "🟡"
    else:
        rating = "[red]Needs Improvement[/red]"
        rating_icon = "🔴"
    
    # Create score panel
    score_text = f"""[bold]Overall Score: {overall}/100 {rating_icon}[/bold]
[bold]Rating: {rating}[/bold]

[bold yellow]Component Scores:[/bold yellow]
🔒 Security: {breakdown.get("security", 0):.1f}/100
📊 Complexity: {breakdown.get("complexity", 0):.1f}/100  
🔄 Churn: {breakdown.get("churn", 0):.1f}/100
📦 Dependencies: {breakdown.get("dependencies", 0):.1f}/100

[dim]Based on Swiss Banking regulatory compliance scoring[/dim]"""
    
    panel = Panel(score_text, title="🎯 Code Quality Score", border_style="blue")
    console.print(panel)