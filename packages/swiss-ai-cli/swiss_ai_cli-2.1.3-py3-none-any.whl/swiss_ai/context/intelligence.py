#!/usr/bin/env python3
"""
Context Intelligence System for Swiss AI CLI
Provides smart context awareness, project detection, and adaptive defaults
"""

import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

logger = logging.getLogger(__name__)

class ProjectType(Enum):
    """Detected project types"""
    PYTHON = "python"
    JAVASCRIPT = "javascript" 
    TYPESCRIPT = "typescript"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NODE = "node"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    PHP = "php"
    RUBY = "ruby"
    UNKNOWN = "unknown"

class ContextType(Enum):
    """Types of context information"""
    PROJECT = "project"
    GIT = "git"
    FILES = "files"
    WORKFLOW = "workflow"
    USER_PATTERNS = "user_patterns"

@dataclass
class ProjectContext:
    """Project-specific context information"""
    project_type: ProjectType
    root_path: Path
    main_files: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    build_tools: List[str] = field(default_factory=list)
    test_frameworks: List[str] = field(default_factory=list)
    structure: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GitContext:
    """Git repository context"""
    is_repo: bool = False
    current_branch: str = ""
    recent_commits: List[Dict[str, str]] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    staged_files: List[str] = field(default_factory=list)
    untracked_files: List[str] = field(default_factory=list)
    remote_url: str = ""
    last_commit_time: Optional[datetime] = None

@dataclass
class UserPattern:
    """User behavior patterns for adaptation"""
    command: str
    frequency: int = 1
    last_used: datetime = field(default_factory=datetime.now)
    success_rate: float = 1.0
    avg_execution_time: float = 0.0
    preferred_models: List[str] = field(default_factory=list)
    context_tags: List[str] = field(default_factory=list)

@dataclass
class SessionContext:
    """Current session context and memory"""
    session_start: datetime = field(default_factory=datetime.now)
    commands_executed: List[Dict[str, Any]] = field(default_factory=list)
    current_workflow: Optional[str] = None
    recent_files: List[str] = field(default_factory=list)
    active_models: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)

class ProjectDetector:
    """Intelligent project type detection"""
    
    def __init__(self):
        self.detection_patterns = {
            ProjectType.PYTHON: {
                'files': ['requirements.txt', 'pyproject.toml', 'setup.py', 'setup.cfg', 'Pipfile'],
                'extensions': ['.py'],
                'indicators': ['__init__.py', 'main.py', 'app.py']
            },
            ProjectType.JAVASCRIPT: {
                'files': ['package.json', 'yarn.lock', 'package-lock.json'],
                'extensions': ['.js', '.mjs'],
                'indicators': ['index.js', 'app.js', 'server.js']
            },
            ProjectType.TYPESCRIPT: {
                'files': ['tsconfig.json', 'package.json'],
                'extensions': ['.ts', '.tsx'],
                'indicators': ['index.ts', 'main.ts', 'app.ts']
            },
            ProjectType.REACT: {
                'files': ['package.json'],
                'extensions': ['.jsx', '.tsx'],
                'indicators': ['App.jsx', 'App.tsx', 'index.jsx'],
                'keywords': ['react', 'react-dom', 'react-scripts']
            },
            ProjectType.VUE: {
                'files': ['package.json', 'vue.config.js'],
                'extensions': ['.vue'],
                'indicators': ['App.vue', 'main.js'],
                'keywords': ['vue', '@vue/cli']
            },
            ProjectType.ANGULAR: {
                'files': ['angular.json', 'package.json'],
                'extensions': ['.ts'],
                'indicators': ['app.module.ts', 'main.ts'],
                'keywords': ['@angular/core', '@angular/cli']
            },
            ProjectType.GO: {
                'files': ['go.mod', 'go.sum'],
                'extensions': ['.go'],
                'indicators': ['main.go', 'cmd/']
            },
            ProjectType.RUST: {
                'files': ['Cargo.toml', 'Cargo.lock'],
                'extensions': ['.rs'],
                'indicators': ['main.rs', 'lib.rs', 'src/']
            },
            ProjectType.JAVA: {
                'files': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
                'extensions': ['.java'],
                'indicators': ['Main.java', 'Application.java', 'src/main/']
            },
            ProjectType.CSHARP: {
                'files': ['*.csproj', '*.sln', 'project.json'],
                'extensions': ['.cs'],
                'indicators': ['Program.cs', 'Startup.cs']
            }
        }
    
    def detect_project(self, path: Path) -> ProjectContext:
        """Detect project type and gather context"""
        
        # Check for project indicators
        detected_type = ProjectType.UNKNOWN
        confidence_scores = {}
        
        for project_type, patterns in self.detection_patterns.items():
            score = self._calculate_project_score(path, patterns)
            confidence_scores[project_type] = score
        
        # Select highest confidence project type
        if confidence_scores:
            detected_type = max(confidence_scores.items(), key=lambda x: x[1])[0]
            if confidence_scores[detected_type] < 0.3:  # Low confidence threshold
                detected_type = ProjectType.UNKNOWN
        
        # Gather project context
        context = ProjectContext(
            project_type=detected_type,
            root_path=path,
            main_files=self._find_main_files(path, detected_type),
            config_files=self._find_config_files(path, detected_type),
            dependencies=self._extract_dependencies(path, detected_type),
            build_tools=self._detect_build_tools(path, detected_type),
            test_frameworks=self._detect_test_frameworks(path, detected_type),
            structure=self._analyze_structure(path)
        )
        
        return context
    
    def _calculate_project_score(self, path: Path, patterns: Dict[str, List[str]]) -> float:
        """Calculate confidence score for project type"""
        score = 0.0
        
        # Check for project files
        for file_pattern in patterns.get('files', []):
            if '*' in file_pattern:
                # Wildcard matching
                import glob
                matches = list(path.glob(file_pattern))
                if matches:
                    score += 0.4
            else:
                if (path / file_pattern).exists():
                    score += 0.4
        
        # Check for file extensions
        extensions = patterns.get('extensions', [])
        if extensions:
            found_files = []
            for ext in extensions:
                found_files.extend(path.rglob(f"*{ext}"))
            if found_files:
                score += 0.3
        
        # Check for indicator files
        for indicator in patterns.get('indicators', []):
            if (path / indicator).exists():
                score += 0.2
        
        # Check package.json for keywords (for JS frameworks)
        keywords = patterns.get('keywords', [])
        if keywords and (path / 'package.json').exists():
            try:
                with open(path / 'package.json', 'r') as f:
                    package_data = json.load(f)
                    deps = {**package_data.get('dependencies', {}), 
                           **package_data.get('devDependencies', {})}
                    
                    for keyword in keywords:
                        if keyword in deps:
                            score += 0.3
            except:
                pass
        
        return min(score, 1.0)
    
    def _find_main_files(self, path: Path, project_type: ProjectType) -> List[str]:
        """Find main entry point files"""
        main_files = []
        
        common_main_files = {
            ProjectType.PYTHON: ['main.py', 'app.py', '__main__.py', 'run.py'],
            ProjectType.JAVASCRIPT: ['index.js', 'app.js', 'server.js', 'main.js'],
            ProjectType.TYPESCRIPT: ['index.ts', 'app.ts', 'main.ts'],
            ProjectType.REACT: ['App.jsx', 'App.tsx', 'index.jsx', 'index.tsx'],
            ProjectType.GO: ['main.go'],
            ProjectType.RUST: ['main.rs', 'lib.rs'],
            ProjectType.JAVA: ['Main.java', 'Application.java']
        }
        
        candidates = common_main_files.get(project_type, [])
        for candidate in candidates:
            file_path = path / candidate
            if file_path.exists():
                main_files.append(str(file_path.relative_to(path)))
        
        return main_files
    
    def _find_config_files(self, path: Path, project_type: ProjectType) -> List[str]:
        """Find configuration files"""
        config_files = []
        
        config_patterns = {
            ProjectType.PYTHON: ['.env', 'config.py', 'settings.py', 'pyproject.toml'],
            ProjectType.JAVASCRIPT: ['.env', 'webpack.config.js', '.babelrc', 'jest.config.js'],
            ProjectType.TYPESCRIPT: ['tsconfig.json', '.env'],
            ProjectType.REACT: ['.env', 'public/manifest.json'],
            ProjectType.GO: ['config.yaml', 'config.json', '.env'],
            ProjectType.RUST: ['Cargo.toml', 'config.toml']
        }
        
        patterns = config_patterns.get(project_type, [])
        for pattern in patterns:
            file_path = path / pattern
            if file_path.exists():
                config_files.append(str(file_path.relative_to(path)))
        
        return config_files
    
    def _extract_dependencies(self, path: Path, project_type: ProjectType) -> Dict[str, str]:
        """Extract project dependencies"""
        dependencies = {}
        
        try:
            if project_type in [ProjectType.JAVASCRIPT, ProjectType.TYPESCRIPT, ProjectType.REACT, ProjectType.VUE, ProjectType.ANGULAR]:
                package_json = path / 'package.json'
                if package_json.exists():
                    with open(package_json, 'r') as f:
                        data = json.load(f)
                        dependencies.update(data.get('dependencies', {}))
                        dependencies.update(data.get('devDependencies', {}))
            
            elif project_type == ProjectType.PYTHON:
                # Try requirements.txt first
                req_file = path / 'requirements.txt'
                if req_file.exists():
                    with open(req_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if '==' in line:
                                    name, version = line.split('==', 1)
                                    dependencies[name] = version
                                else:
                                    dependencies[line] = "latest"
                
                # Also check pyproject.toml
                pyproject = path / 'pyproject.toml'
                if pyproject.exists():
                    try:
                        import toml
                        with open(pyproject, 'r') as f:
                            data = toml.load(f)
                            deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
                            dependencies.update(deps)
                    except ImportError:
                        pass  # toml not available
        except Exception as e:
            logger.debug(f"Error extracting dependencies: {e}")
        
        return dependencies
    
    def _detect_build_tools(self, path: Path, project_type: ProjectType) -> List[str]:
        """Detect build tools and task runners"""
        build_tools = []
        
        tool_indicators = {
            'webpack': ['webpack.config.js', 'webpack.config.ts'],
            'vite': ['vite.config.js', 'vite.config.ts'],
            'rollup': ['rollup.config.js'],
            'parcel': ['.parcelrc'],
            'make': ['Makefile'],
            'cmake': ['CMakeLists.txt'],
            'gradle': ['build.gradle', 'gradlew'],
            'maven': ['pom.xml'],
            'cargo': ['Cargo.toml'],
            'npm': ['package.json'],
            'yarn': ['yarn.lock'],
            'poetry': ['pyproject.toml'],
            'pip': ['requirements.txt']
        }
        
        for tool, indicators in tool_indicators.items():
            for indicator in indicators:
                if (path / indicator).exists():
                    build_tools.append(tool)
                    break
        
        return build_tools
    
    def _detect_test_frameworks(self, path: Path, project_type: ProjectType) -> List[str]:
        """Detect testing frameworks"""
        test_frameworks = []
        
        # Check dependencies for test frameworks
        dependencies = self._extract_dependencies(path, project_type)
        
        test_framework_patterns = {
            'jest': ['jest'],
            'mocha': ['mocha'],
            'chai': ['chai'],
            'jasmine': ['jasmine'],
            'pytest': ['pytest'],
            'unittest': ['unittest2'],
            'nose': ['nose', 'nose2'],
            'go-test': [],  # Built into Go
            'cargo-test': []  # Built into Rust
        }
        
        for framework, patterns in test_framework_patterns.items():
            if any(pattern in dependencies for pattern in patterns):
                test_frameworks.append(framework)
        
        # Special cases for built-in test frameworks
        if project_type == ProjectType.GO and any(path.rglob('*_test.go')):
            test_frameworks.append('go-test')
        
        if project_type == ProjectType.RUST and any(path.rglob('tests/')):
            test_frameworks.append('cargo-test')
        
        return test_frameworks
    
    def _analyze_structure(self, path: Path) -> Dict[str, Any]:
        """Analyze project structure"""
        structure = {
            'total_files': 0,
            'directories': [],
            'file_types': {},
            'size_mb': 0.0
        }
        
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    structure['total_files'] += 1
                    ext = item.suffix.lower()
                    structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
                    
                    try:
                        structure['size_mb'] += item.stat().st_size / (1024 * 1024)
                    except:
                        pass
                elif item.is_dir() and item != path:
                    rel_path = str(item.relative_to(path))
                    if not any(part.startswith('.') for part in item.parts):
                        structure['directories'].append(rel_path)
        except Exception as e:
            logger.debug(f"Error analyzing structure: {e}")
        
        return structure

class GitAnalyzer:
    """Git repository analysis and context extraction"""
    
    def __init__(self):
        self.console = Console()
    
    def analyze_repository(self, path: Path) -> GitContext:
        """Analyze Git repository context"""
        context = GitContext()
        
        git_dir = path / '.git'
        if not git_dir.exists():
            return context
        
        context.is_repo = True
        
        try:
            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  cwd=path, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                context.current_branch = result.stdout.strip()
            
            # Get recent commits
            result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                                  cwd=path, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(' ', 1)
                        if len(parts) == 2:
                            commits.append({
                                'hash': parts[0],
                                'message': parts[1]
                            })
                context.recent_commits = commits
            
            # Get file status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  cwd=path, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        status = line[:2]
                        filename = line[3:].strip()
                        
                        if status.strip() == 'M':
                            context.modified_files.append(filename)
                        elif status.strip() in ['A', 'M']:
                            context.staged_files.append(filename)
                        elif status.strip() == '??':
                            context.untracked_files.append(filename)
            
            # Get remote URL
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  cwd=path, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                context.remote_url = result.stdout.strip()
            
            # Get last commit time
            result = subprocess.run(['git', 'log', '-1', '--format=%ct'], 
                                  cwd=path, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                timestamp = int(result.stdout.strip())
                context.last_commit_time = datetime.fromtimestamp(timestamp)
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError) as e:
            logger.debug(f"Git analysis error: {e}")
        
        return context

class ContextIntelligence:
    """Main context intelligence system"""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path.home() / '.swiss-ai'
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        self.console = Console()
        self.project_detector = ProjectDetector()
        self.git_analyzer = GitAnalyzer()
        
        # State management
        self.session_context = SessionContext()
        self.user_patterns: Dict[str, UserPattern] = {}
        self.cache: Dict[str, Any] = {}
        
        # Load persistent data
        self._load_user_patterns()
    
    def analyze_context(self, working_directory: Path = None) -> Dict[str, Any]:
        """Comprehensive context analysis"""
        if working_directory is None:
            working_directory = Path.cwd()
        
        cache_key = f"context_{working_directory}_{int(time.time() // 300)}"  # 5-minute cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        context = {}
        
        # Project context
        project_context = self.project_detector.detect_project(working_directory)
        try:
            context['project'] = asdict(project_context)
        except TypeError:
            # In test environments where detector is mocked to return non-dataclass
            context['project'] = project_context if isinstance(project_context, dict) else {}
        
        # Git context
        git_context = self.git_analyzer.analyze_repository(working_directory)
        try:
            context['git'] = asdict(git_context)
        except TypeError:
            context['git'] = git_context if isinstance(git_context, dict) else {}
        
        # Session context
        context['session'] = asdict(self.session_context)
        
        # User patterns
        context['user_patterns'] = {k: asdict(v) for k, v in self.user_patterns.items()}
        
        # Smart recommendations
        context['recommendations'] = self._generate_recommendations(project_context, git_context)
        
        # Cache the result
        self.cache[cache_key] = context
        
        return context
    
    def update_session(self, command: str, result: Dict[str, Any]):
        """Update session context with command execution"""
        
        command_record = {
            'command': command,
            'timestamp': datetime.now().isoformat(),
            'success': result.get('success', True),
            'execution_time': result.get('execution_time', 0.0),
            'model_used': result.get('model_used'),
            'agent_used': result.get('agent_used')
        }
        
        self.session_context.commands_executed.append(command_record)
        
        # Update user patterns
        self._update_user_patterns(command, result)
        
        # Trim session history to last 50 commands
        if len(self.session_context.commands_executed) > 50:
            self.session_context.commands_executed = self.session_context.commands_executed[-50:]
    
    def get_smart_defaults(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get intelligent defaults based on context"""
        if context is None:
            context = self.analyze_context()
        
        defaults = {}
        
        project_type = context.get('project', {}).get('project_type', 'unknown')
        
        # Model selection based on project type and task
        if 'code' in user_input.lower() or 'debug' in user_input.lower():
            if project_type in ['python', 'javascript', 'typescript']:
                defaults['preferred_model'] = 'qwen/qwen3-coder:free'
            else:
                defaults['preferred_model'] = 'anthropic/claude-3-haiku'
        elif 'analyze' in user_input.lower() or 'explain' in user_input.lower():
            defaults['preferred_model'] = 'deepseek/deepseek-v3:free'
        
        # Agent selection based on context
        if context.get('git', {}).get('modified_files'):
            defaults['suggested_workflow'] = 'review_then_commit'
        
        if project_type != 'unknown':
            defaults['project_aware'] = True
            defaults['context_files'] = context.get('project', {}).get('main_files', [])
        
        # User pattern-based defaults
        similar_commands = self._find_similar_commands(user_input)
        if similar_commands:
            defaults['similar_commands'] = similar_commands[:3]
        
        return defaults
    
    def _generate_recommendations(self, project_context: ProjectContext, git_context: GitContext) -> List[str]:
        """Generate smart recommendations based on context"""
        recommendations = []
        
        # Project-based recommendations
        if project_context.project_type != ProjectType.UNKNOWN:
            if not project_context.main_files:
                recommendations.append(f"No main entry files detected for {project_context.project_type.value} project")
            
            if not project_context.test_frameworks:
                recommendations.append("Consider setting up automated testing")
        
        # Git-based recommendations
        if git_context.is_repo:
            if git_context.modified_files:
                recommendations.append(f"You have {len(git_context.modified_files)} modified files")
            
            if git_context.untracked_files:
                recommendations.append(f"You have {len(git_context.untracked_files)} untracked files")
        
        # Session-based recommendations
        if len(self.session_context.commands_executed) > 5:
            recent_commands = [cmd['command'] for cmd in self.session_context.commands_executed[-5:]]
            if len(set(recent_commands)) < len(recent_commands):
                recommendations.append("Consider creating a workflow for repeated commands")
        
        return recommendations
    
    def _update_user_patterns(self, command: str, result: Dict[str, Any]):
        """Update user behavior patterns"""
        pattern_key = command.split()[0] if command.split() else command
        
        if pattern_key in self.user_patterns:
            pattern = self.user_patterns[pattern_key]
            pattern.frequency += 1
            pattern.last_used = datetime.now()
            
            # Update success rate
            success = result.get('success', True)
            pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1) + (1.0 if success else 0.0)) / pattern.frequency
            
            # Update execution time
            exec_time = result.get('execution_time', 0.0)
            if exec_time > 0:
                pattern.avg_execution_time = (pattern.avg_execution_time * (pattern.frequency - 1) + exec_time) / pattern.frequency
        else:
            self.user_patterns[pattern_key] = UserPattern(
                command=pattern_key,
                frequency=1,
                last_used=datetime.now(),
                success_rate=1.0 if result.get('success', True) else 0.0,
                avg_execution_time=result.get('execution_time', 0.0)
            )
        
        # Save patterns periodically
        if len(self.user_patterns) % 10 == 0:
            self._save_user_patterns()
    
    def _find_similar_commands(self, user_input: str) -> List[str]:
        """Find similar commands from user patterns"""
        similar = []
        input_words = set(user_input.lower().split())
        
        for pattern_key, pattern in self.user_patterns.items():
            pattern_words = set(pattern_key.lower().split())
            overlap = len(input_words.intersection(pattern_words))
            
            if overlap > 0:
                similar.append({
                    'command': pattern_key,
                    'frequency': pattern.frequency,
                    'success_rate': pattern.success_rate,
                    'overlap': overlap
                })
        
        # Sort by relevance (overlap * frequency * success_rate)
        similar.sort(key=lambda x: x['overlap'] * x['frequency'] * x['success_rate'], reverse=True)
        
        return [cmd['command'] for cmd in similar]
    
    def _load_user_patterns(self):
        """Load user patterns from disk"""
        patterns_file = self.config_path / 'user_patterns.json'
        
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                    
                    for key, pattern_data in data.items():
                        # Convert datetime strings back to datetime objects
                        if 'last_used' in pattern_data:
                            pattern_data['last_used'] = datetime.fromisoformat(pattern_data['last_used'])
                        
                        self.user_patterns[key] = UserPattern(**pattern_data)
                        
            except Exception as e:
                logger.debug(f"Error loading user patterns: {e}")
    
    def _save_user_patterns(self):
        """Save user patterns to disk"""
        patterns_file = self.config_path / 'user_patterns.json'
        
        try:
            # Convert to serializable format
            data = {}
            for key, pattern in self.user_patterns.items():
                pattern_dict = asdict(pattern)
                # Convert datetime to string
                pattern_dict['last_used'] = pattern.last_used.isoformat()
                data[key] = pattern_dict
            
            with open(patterns_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.debug(f"Error saving user patterns: {e}")
    
    def get_recent_commands(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get recent command usage statistics"""
        # Sort user patterns by frequency and last used time
        recent_patterns = []
        
        for pattern_key, pattern in self.user_patterns.items():
            recent_patterns.append({
                'command': pattern.command,
                'frequency': pattern.frequency,
                'success_rate': pattern.success_rate,
                'last_used': pattern.last_used,
                'avg_execution_time': pattern.avg_execution_time,
                'preferred_models': pattern.preferred_models,
                'context_tags': pattern.context_tags
            })
        
        # Sort by frequency * success_rate * recency score
        def score_pattern(p):
            days_ago = (datetime.now() - p['last_used']).days
            recency_score = max(0.1, 1.0 - (days_ago / 30))  # Decay over 30 days
            return p['frequency'] * p['success_rate'] * recency_score
        
        recent_patterns.sort(key=score_pattern, reverse=True)
        return recent_patterns[:limit]

    def display_context_summary(self, context: Dict[str, Any] = None):
        """Display beautiful context summary"""
        if context is None:
            context = self.analyze_context()
        
        # Project information
        project = context.get('project', {})
        project_type = project.get('project_type', 'unknown')
        
        if project_type != 'unknown':
            # Project panel
            project_info = f"""[bold cyan]Type:[/bold cyan] {project_type.title()}
[bold cyan]Files:[/bold cyan] {project.get('structure', {}).get('total_files', 0)}
[bold cyan]Size:[/bold cyan] {project.get('structure', {}).get('size_mb', 0):.1f} MB"""

            if project.get('dependencies'):
                dep_count = len(project['dependencies'])
                project_info += f"\n[bold cyan]Dependencies:[/bold cyan] {dep_count}"
            
            project_panel = Panel(
                project_info,
                title="🏗️ Project Context",
                border_style="blue"
            )
            self.console.print(project_panel)
        
        # Git information
        git = context.get('git', {})
        if git.get('is_repo'):
            git_info = f"[bold green]Branch:[/bold green] {git.get('current_branch', 'unknown')}"
            
            if git.get('modified_files'):
                git_info += f"\n[bold yellow]Modified:[/bold yellow] {len(git['modified_files'])} files"
            
            if git.get('recent_commits'):
                git_info += f"\n[bold blue]Recent:[/bold blue] {git['recent_commits'][0]['message'][:50]}..."
            
            git_panel = Panel(
                git_info,
                title="🔧 Git Status", 
                border_style="green"
            )
            self.console.print(git_panel)
        
        # Recommendations
        recommendations = context.get('recommendations', [])
        if recommendations:
            rec_text = "\n".join(f"• {rec}" for rec in recommendations[:3])
            rec_panel = Panel(
                rec_text,
                title="💡 Smart Recommendations",
                border_style="yellow"
            )
            self.console.print(rec_panel)