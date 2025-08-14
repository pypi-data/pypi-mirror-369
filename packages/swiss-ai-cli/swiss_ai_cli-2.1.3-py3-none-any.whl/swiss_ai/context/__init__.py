#!/usr/bin/env python3
"""
Context Intelligence Module for Swiss AI CLI
Provides smart context awareness, project detection, and adaptive defaults
"""

from .intelligence import (
    ContextIntelligence,
    ProjectDetector,
    GitAnalyzer,
    ProjectType,
    ProjectContext,
    GitContext,
    UserPattern,
    SessionContext
)

__all__ = [
    "ContextIntelligence",
    "ProjectDetector", 
    "GitAnalyzer",
    "ProjectType",
    "ProjectContext",
    "GitContext",
    "UserPattern",
    "SessionContext"
]