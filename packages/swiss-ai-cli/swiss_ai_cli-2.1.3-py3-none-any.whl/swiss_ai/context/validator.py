#!/usr/bin/env python3
"""
Context YAML Validator for Swiss AI CLI
Validates context configuration files against JSON schema
"""

import json
from pathlib import Path
import jsonschema
import yaml
from rich.console import Console

console = Console()

# Load schema from schema.json
_schema_path = Path(__file__).parent / "schema.json"
with open(_schema_path, 'r') as f:
    SCHEMA = json.load(f)

def validate_context_yaml(path: Path) -> tuple[bool, list[str]]:
    """Validate context YAML file against schema
    
    Args:
        path: Path to the YAML file to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    try:
        if not path.exists():
            return False, [f"File not found: {path}"]
        
        data = yaml.safe_load(path.read_text())
        if data is None:
            return False, ["Empty or invalid YAML file"]
        
        jsonschema.validate(data, schema=SCHEMA)
        return True, []
    except yaml.YAMLError as e:
        return False, [f"YAML parsing error: {str(e)}"]
    except jsonschema.ValidationError as e:
        path = ".".join([str(p) for p in e.path])
        return False, [f"Schema validation error at '{path}': {e.message}"]
    except Exception as e:
        return False, [str(e)]

def validate_and_report(path: Path) -> bool:
    """Validate and print results to console"""
    is_valid, errors = validate_context_yaml(path)
    
    if is_valid:
        console.print(f"[green]✓[/green] {path} is valid")
        return True
    else:
        console.print(f"[red]✗[/red] {path} validation failed:")
        for error in errors:
            console.print(f"  [red]•[/red] {error}")
        return False