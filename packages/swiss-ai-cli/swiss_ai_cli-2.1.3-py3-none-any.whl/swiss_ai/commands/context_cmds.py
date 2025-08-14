#!/usr/bin/env python3
"""
Context management commands for intelligent file selection and compression
Implements TF-IDF ranking, AST-based chunking, and token-budgeted context creation
"""

import ast
import json
import math
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

# File type weights for path heuristics
PATH_WEIGHTS = {
    "src": 1.5,
    "app": 1.4,
    "core": 1.3,
    "lib": 1.2,
    "main": 1.2,
    "test": 0.8,
    "tests": 0.7,
    "spec": 0.7,
    "docs": 0.6,
    "doc": 0.6,
    "__pycache__": 0.1,
    "node_modules": 0.1,
    ".git": 0.1
}

def estimate_tokens(text: str) -> int:
    """Simple token estimation: ~4 characters per token"""
    return max(1, len(text) // 4)

def load_symphonics_query() -> Optional[str]:
    """Load recent Symphonics movements to derive query"""
    try:
        symphonics_dir = Path.home() / ".swiss-ai" / "symphonics"
        if not symphonics_dir.exists():
            return None
        
        # Look for recent session files
        json_files = list(symphonics_dir.glob("*.json"))
        if not json_files:
            return None
        
        # Get most recent file
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract query from recent movements
        movements = data.get("movements", [])
        if not movements:
            return None
        
        # Combine last few movement payloads
        query_parts = []
        for movement in movements[-5:]:  # Last 5 movements
            movement_type = movement.get("type", "")
            payload = movement.get("payload", {})
            
            if movement_type in ["Aurequest", "Fracturemap", "Reverline"]:
                # Extract meaningful text from payload
                if isinstance(payload, dict):
                    for key, value in payload.items():
                        if isinstance(value, str) and len(value.strip()) > 10:
                            query_parts.append(value.strip())
                elif isinstance(payload, str) and len(payload.strip()) > 10:
                    query_parts.append(payload.strip())
        
        return " ".join(query_parts) if query_parts else None
        
    except Exception:
        return None

def get_git_churn_scores(project_path: Path) -> Dict[str, float]:
    """Get file modification frequency from git history"""
    import subprocess
    
    try:
        result = subprocess.run(
            ["git", "log", "--max-count=500", "--name-only", "--pretty=format:"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=project_path
        )
        
        if result.returncode != 0:
            return {}
        
        file_counts = Counter()
        lines = result.stdout.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                file_counts[line] += 1
        
        # Normalize to 0-1 scale
        max_count = max(file_counts.values()) if file_counts else 1
        return {f: count / max_count for f, count in file_counts.items()}
        
    except Exception:
        return {}

def calculate_path_score(file_path: Path) -> float:
    """Calculate heuristic score based on path components"""
    parts = file_path.parts
    score = 1.0
    
    for part in parts:
        part_lower = part.lower()
        for keyword, weight in PATH_WEIGHTS.items():
            if keyword in part_lower:
                score *= weight
                break
    
    return score

def build_tfidf_scorer(documents: List[Tuple[Path, str]]) -> 'TFIDFScorer':
    """Build TF-IDF scorer from documents"""
    try:
        # Try to use sklearn if available
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        class SklearnTFIDFScorer:
            def __init__(self, documents):
                self.file_paths = [doc[0] for doc in documents]
                texts = [doc[1] for doc in documents]
                
                self.vectorizer = TfidfVectorizer(
                    stop_words='english',
                    max_features=1000,
                    ngram_range=(1, 2)
                )
                self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            def score_query(self, query: str) -> List[Tuple[Path, float]]:
                query_vector = self.vectorizer.transform([query])
                similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
                
                scores = []
                for i, sim in enumerate(similarities):
                    if sim > 0:
                        scores.append((self.file_paths[i], float(sim)))
                
                return sorted(scores, key=lambda x: x[1], reverse=True)
        
        return SklearnTFIDFScorer(documents)
        
    except ImportError:
        # Fallback to manual implementation
        class ManualTFIDFScorer:
            def __init__(self, documents):
                self.documents = documents
                self.file_paths = [doc[0] for doc in documents]
                
                # Build vocabulary and document frequencies
                self.vocab = set()
                self.doc_freqs = defaultdict(int)
                self.term_docs = []
                
                for file_path, text in documents:
                    words = self._tokenize(text.lower())
                    unique_words = set(words)
                    self.vocab.update(unique_words)
                    self.term_docs.append(Counter(words))
                    
                    for word in unique_words:
                        self.doc_freqs[word] += 1
                
                self.num_docs = len(documents)
            
            def _tokenize(self, text: str) -> List[str]:
                import re
                return re.findall(r'\b\w+\b', text)
            
            def _tf_idf(self, term: str, doc_counter: Counter) -> float:
                tf = doc_counter.get(term, 0) / max(len(doc_counter), 1)
                idf = math.log(self.num_docs / max(self.doc_freqs[term], 1))
                return tf * idf
            
            def score_query(self, query: str) -> List[Tuple[Path, float]]:
                query_terms = self._tokenize(query.lower())
                query_counter = Counter(query_terms)
                
                scores = []
                for i, doc_counter in enumerate(self.term_docs):
                    score = 0.0
                    for term in query_terms:
                        if term in self.vocab:
                            doc_tfidf = self._tf_idf(term, doc_counter)
                            query_tfidf = self._tf_idf(term, query_counter)
                            score += doc_tfidf * query_tfidf
                    
                    if score > 0:
                        scores.append((self.file_paths[i], score))
                
                return sorted(scores, key=lambda x: x[1], reverse=True)
        
        return ManualTFIDFScorer(documents)

def collect_project_files(project_path: Path, max_size_mb: float = 2.0) -> List[Path]:
    """Collect relevant project files for analysis"""
    files = []
    max_size_bytes = int(max_size_mb * 1024 * 1024)
    
    # File extensions to include
    include_extensions = {
        '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.h',
        '.md', '.txt', '.yaml', '.yml', '.json', '.xml', '.html', '.css',
        '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala'
    }
    
    try:
        for file_path in project_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            # Skip large files
            if file_path.stat().st_size > max_size_bytes:
                continue
            
            # Include files with relevant extensions
            if file_path.suffix.lower() in include_extensions:
                files.append(file_path)
            
            # Limit total files to prevent performance issues
            if len(files) >= 1000:
                break
                
    except Exception:
        pass
    
    return files

def smart_select_files(project_path: Path, query: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    """Smart file selection using TF-IDF and heuristics"""
    timestamp = time.time()
    
    # Derive query from symphonics if not provided
    if not query:
        query = load_symphonics_query()
    
    if not query:
        query = "main core app"  # Fallback default
    
    # Collect project files
    files = collect_project_files(project_path)
    
    if not files:
        return {
            "timestamp": timestamp,
            "query_used": query,
            "files": [],
            "artifacts": {"json_path": None}
        }
    
    # Load file contents for TF-IDF
    documents = []
    for file_path in files:
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            # Include filename in content for better matching
            content_with_filename = f"{file_path.name} {content}"
            documents.append((file_path, content_with_filename))
        except Exception:
            continue
    
    if not documents:
        return {
            "timestamp": timestamp,
            "query_used": query,
            "files": [],
            "artifacts": {"json_path": None}
        }
    
    # Build TF-IDF scorer
    tfidf_scorer = build_tfidf_scorer(documents)
    
    # Score files with TF-IDF
    tfidf_scores = dict(tfidf_scorer.score_query(query))
    
    # Get git churn scores
    churn_scores = get_git_churn_scores(project_path)
    
    # Combine scores
    file_results = []
    for file_path in files:
        if file_path not in tfidf_scores:
            continue
        
        tfidf_score = tfidf_scores[file_path]
        path_score = calculate_path_score(file_path)
        churn_score = churn_scores.get(str(file_path.relative_to(project_path)), 0.0)
        
        # Weighted combination
        combined_score = (
            tfidf_score * 0.6 +      # TF-IDF relevance
            path_score * 0.25 +      # Path heuristics  
            churn_score * 0.15       # Git churn
        )
        
        reasons = []
        if tfidf_score > 0.1:
            reasons.append(f"Content relevance: {tfidf_score:.2f}")
        if path_score != 1.0:
            reasons.append(f"Path importance: {path_score:.2f}")
        if churn_score > 0:
            reasons.append(f"Recent activity: {churn_score:.2f}")
        if not reasons:
            reasons.append("Filename match")
        
        file_results.append({
            "path": str(file_path.relative_to(project_path)),
            "score": round(combined_score, 3),
            "reasons": reasons
        })
    
    # Sort and limit results
    file_results.sort(key=lambda x: x["score"], reverse=True)
    file_results = file_results[:limit]
    
    return {
        "timestamp": timestamp,
        "query_used": query,
        "files": file_results,
        "artifacts": {"json_path": None}
    }

def chunk_python_file(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Chunk Python file using AST"""
    chunks = []
    
    try:
        tree = ast.parse(content)
        
        # Sort nodes by line number
        nodes = []
        for node in ast.walk(tree):
            if hasattr(node, 'lineno') and isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                nodes.append(node)
        
        nodes.sort(key=lambda x: x.lineno)
        
        lines = content.split('\n')
        last_end = 0
        
        for node in nodes:
            start_line = node.lineno - 1  # Convert to 0-based
            
            # Estimate end line
            end_line = start_line + 20  # Default chunk size
            if hasattr(node, 'end_lineno') and node.end_lineno:
                end_line = node.end_lineno - 1
            else:
                # Find next node or reasonable end
                for other_node in nodes:
                    if other_node.lineno > node.lineno:
                        end_line = min(end_line, other_node.lineno - 2)
                        break
            
            end_line = min(end_line, len(lines) - 1)
            
            if start_line >= last_end:
                chunk_content = '\n'.join(lines[start_line:end_line + 1])
                chunks.append({
                    "file": str(file_path),
                    "start": start_line + 1,  # Convert back to 1-based
                    "end": end_line + 1,
                    "tokens_est": estimate_tokens(chunk_content),
                    "content": chunk_content
                })
                last_end = end_line + 1
        
        # Add remaining content if any
        if last_end < len(lines):
            remaining_content = '\n'.join(lines[last_end:])
            if remaining_content.strip():
                chunks.append({
                    "file": str(file_path),
                    "start": last_end + 1,
                    "end": len(lines),
                    "tokens_est": estimate_tokens(remaining_content),
                    "content": remaining_content
                })
    
    except SyntaxError:
        # Fallback to line-based chunking
        chunks = chunk_file_by_lines(file_path, content)
    
    return chunks

def chunk_file_by_lines(file_path: Path, content: str, chunk_size: int = 50) -> List[Dict[str, Any]]:
    """Fallback chunking by fixed line ranges"""
    lines = content.split('\n')
    chunks = []
    
    for i in range(0, len(lines), chunk_size):
        end_line = min(i + chunk_size, len(lines))
        chunk_content = '\n'.join(lines[i:end_line])
        
        chunks.append({
            "file": str(file_path),
            "start": i + 1,
            "end": end_line,
            "tokens_est": estimate_tokens(chunk_content),
            "content": chunk_content
        })
    
    return chunks

def compress_files(file_paths: List[Path], target_tokens: int = 128000) -> Dict[str, Any]:
    """Compress files into token-budgeted context"""
    timestamp = time.time()
    all_chunks = []
    total_tokens = 0
    
    for file_path in file_paths:
        if not file_path.exists():
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Choose chunking strategy based on file type
            if file_path.suffix == '.py':
                chunks = chunk_python_file(file_path, content)
            else:
                chunks = chunk_file_by_lines(file_path, content)
            
            # Add chunks while respecting token budget
            for chunk in chunks:
                if total_tokens + chunk["tokens_est"] <= target_tokens:
                    all_chunks.append(chunk)
                    total_tokens += chunk["tokens_est"]
                else:
                    break
            
            # Stop if we're close to budget
            if total_tokens >= target_tokens * 0.9:
                break
                
        except Exception:
            continue
    
    return {
        "timestamp": timestamp,
        "target_tokens": target_tokens,
        "total_tokens": total_tokens,
        "chunks": [
            {
                "file": chunk["file"],
                "start": chunk["start"], 
                "end": chunk["end"],
                "tokens_est": chunk["tokens_est"]
            } for chunk in all_chunks
        ],
        "artifacts": {"json_path": None, "txt_path": None}
    }

def create_context_reports_directory() -> Path:
    """Create timestamped context reports directory"""
    base_dir = Path.home() / ".swiss-ai" / "reports" / "context"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = base_dir / timestamp
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir

@click.group()
def context():
    """Context management commands for intelligent file selection and compression."""
    pass

@context.command("smart-select")
@click.option("--limit", default=20, help="Maximum number of files to return")
@click.option("--query", help="Search query (if omitted, derives from recent Symphonics)")
@click.option("--json", is_flag=True, help="Output as JSON")
def smart_select(limit: int, query: Optional[str], json: bool):
    """Rank repository files by relevance to recent work
    
    Uses TF-IDF scoring combined with git churn analysis and path heuristics
    to identify the most relevant files for context inclusion.
    """
    project_path = Path.cwd()
    
    # Create reports directory
    report_dir = create_context_reports_directory()
    
    with console.status("Analyzing files for relevance...", spinner="dots") as status:
        status.update("Collecting project files...")
        results = smart_select_files(project_path, query, limit)
    
    # Save JSON report
    json_path = report_dir / "smart_select.json"
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    results["artifacts"]["json_path"] = str(json_path.resolve())
    
    if json:
        console.print(json.dumps(results, indent=2))
    else:
        display_smart_select_results(results)

@context.command("compress")
@click.option("--files", multiple=True, help="Files to include in context")
@click.option("--from-smart", type=int, help="Use smart-select to get N files")
@click.option("--target", default=128000, help="Target token budget")
@click.option("--json", is_flag=True, help="Output as JSON")
def compress(files: Tuple[str], from_smart: Optional[int], target: int, json: bool):
    """Produce token-budgeted context from a set of files
    
    Chunks files using AST analysis (Python) or line-based splitting,
    respecting the specified token budget.
    """
    project_path = Path.cwd()
    
    # Determine files to compress
    if from_smart:
        with console.status("Running smart-select...", spinner="dots"):
            smart_results = smart_select_files(project_path, limit=from_smart)
            file_paths = [project_path / f["path"] for f in smart_results["files"]]
    else:
        file_paths = [Path(f) for f in files]
        file_paths = [f if f.is_absolute() else project_path / f for f in file_paths]
    
    if not file_paths:
        console.print("[red]Error: No files specified. Use --files or --from-smart.[/red]")
        return
    
    # Create reports directory
    report_dir = create_context_reports_directory()
    
    with console.status("Compressing files into context...", spinner="dots") as status:
        status.update("Chunking files and estimating tokens...")
        results = compress_files(file_paths, target)
    
    # Save JSON report
    json_path = report_dir / "compress.json"  
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    results["artifacts"]["json_path"] = str(json_path.resolve())
    
    # Create text context file
    txt_path = report_dir / "context.txt"
    context_lines = []
    for file_path in file_paths:
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            context_lines.append(f"=== {file_path} ===\n{content}\n")
        except Exception:
            continue
    
    txt_content = "\n".join(context_lines)
    txt_path.write_text(txt_content, encoding="utf-8")
    results["artifacts"]["txt_path"] = str(txt_path.resolve())
    
    if json:
        console.print(json.dumps(results, indent=2))
    else:
        display_compress_results(results)

def display_smart_select_results(results: Dict[str, Any]):
    """Display Rich smart-select results"""
    query = results.get("query_used", "N/A")
    files = results.get("files", [])
    
    console.print(f"\n[bold blue]🧠 Smart File Selection[/bold blue]")
    console.print(f"[dim]Query: {query}[/dim]")
    
    if not files:
        console.print("[yellow]No relevant files found.[/yellow]")
        return
    
    # Create results table
    table = Table(title=f"Top {len(files)} Files by Relevance", box=box.ROUNDED)
    table.add_column("Rank", style="cyan", width=4)
    table.add_column("File", style="green")
    table.add_column("Score", style="yellow", width=8)
    table.add_column("Reasons", style="white")
    
    for i, file_info in enumerate(files, 1):
        reasons_text = ", ".join(file_info.get("reasons", []))[:50] + "..."
        if len(file_info.get("reasons", [])) <= 2:
            reasons_text = ", ".join(file_info.get("reasons", []))
        
        table.add_row(
            str(i),
            file_info["path"],
            f'{file_info["score"]:.3f}',
            reasons_text
        )
    
    console.print(table)
    
    # Show artifacts
    artifacts = results.get("artifacts", {})
    if artifacts.get("json_path"):
        console.print(f"\n[bold green]📄 Report saved:[/bold green] [cyan]{artifacts['json_path']}[/cyan]")

def display_compress_results(results: Dict[str, Any]):
    """Display Rich compress results"""
    target = results.get("target_tokens", 0)
    total = results.get("total_tokens", 0)
    chunks = results.get("chunks", [])
    
    console.print(f"\n[bold blue]🗜️ Context Compression[/bold blue]")
    
    # Summary panel
    usage_pct = (total / target * 100) if target > 0 else 0
    color = "green" if usage_pct <= 90 else "yellow" if usage_pct <= 100 else "red"
    
    summary_text = f"""[bold]Token Budget:[/bold] {total:,} / {target:,} ({usage_pct:.1f}%)
[bold]Chunks Created:[/bold] {len(chunks)}
[bold]Files Processed:[/bold] {len(set(chunk['file'] for chunk in chunks))}"""
    
    panel = Panel(summary_text, title="Compression Summary", border_style=color)
    console.print(panel)
    
    # Show sample chunks
    if chunks:
        console.print("\n[bold yellow]Sample Chunks:[/bold yellow]")
        for chunk in chunks[:5]:  # Show first 5 chunks
            file_name = Path(chunk["file"]).name
            lines = f'L{chunk["start"]}-{chunk["end"]}'
            tokens = chunk["tokens_est"]
            console.print(f"  [cyan]{file_name}[/cyan] {lines} ({tokens} tokens)")
        
        if len(chunks) > 5:
            console.print(f"  [dim]... and {len(chunks) - 5} more chunks[/dim]")
    
    # Show artifacts
    artifacts = results.get("artifacts", {})
    if artifacts.get("json_path") or artifacts.get("txt_path"):
        console.print(f"\n[bold green]📄 Artifacts created:[/bold green]")
        if artifacts.get("json_path"):
            console.print(f"  JSON: [cyan]{artifacts['json_path']}[/cyan]")
        if artifacts.get("txt_path"):
            console.print(f"  Context: [cyan]{artifacts['txt_path']}[/cyan]")