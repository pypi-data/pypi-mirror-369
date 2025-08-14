#!/usr/bin/env python3
import os, sys, platform
from pathlib import Path
from typing import Tuple
import click
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def detect_debugger() -> Tuple[str, str]:
    """Detect debugger using platform-specific methods"""
    system = platform.system().lower()
    try:
        if system == "windows":
            import ctypes
            return ("🔴 Risk", "Debugger detected") if ctypes.windll.kernel32.IsDebuggerPresent() else ("🟢 OK", "None detected")
        elif system == "linux":
            with open('/proc/self/status', 'r') as f:
                for line in f:
                    if line.startswith('TracerPid:'):
                        pid = int(line.split(':')[1].strip())
                        return ("🔴 Risk", f"Traced by PID {pid}") if pid != 0 else ("🟢 OK", "None detected")
        elif system == "darwin":
            import subprocess
            result = subprocess.run(['sysctl', '-n', f'kern.proc.pid.{os.getpid()}'], capture_output=True, text=True, timeout=2)
            return ("🔴 Risk", "Process traced") if 'P_TRACED' in result.stdout else ("🟢 OK", "None detected")
        return "🟡 Unknown", "Unsupported platform"
    except Exception as e:
        return "🟡 Unknown", f"Error: {str(e)[:20]}"

def check_preload_libraries() -> Tuple[str, str]:
    """Check for suspicious preloaded libraries"""
    suspicious = []
    system = platform.system().lower()
    if system == "linux":
        libs = os.environ.get('LD_PRELOAD', '').split(':')
        suspicious = [lib for lib in libs if lib.strip() and ('/tmp/' in lib or '/dev/shm/' in lib or not lib.startswith('/usr/'))]
    elif system == "darwin":
        libs = os.environ.get('DYLD_INSERT_LIBRARIES', '').split(':')
        suspicious = [lib for lib in libs if lib.strip() and ('/tmp/' in lib or not (lib.startswith('/System/') or lib.startswith('/usr/')))]
    if suspicious:
        # Return full path for clearer mitigation (tests expect full string)
        return "🔴 Risk", f"Remove {suspicious[0]}"
    elif os.environ.get('LD_PRELOAD') or os.environ.get('DYLD_INSERT_LIBRARIES'):
        return "🟡 Warning", "Preload detected"
    return "🟢 OK", "None detected"

@click.group() 
def secure():
    """Security monitoring and threat detection"""
    pass

@secure.command('check')
@click.option('--strict', is_flag=True, help='Enable strict security checks')
def secure_check(strict):
    """Check for security threats"""
    checks = [("Debugger", detect_debugger()), ("Preload Libs", check_preload_libraries())]
    table = Table(title="Security Status", box=box.ROUNDED)
    table.add_column("Threat", style="cyan", width=15)
    table.add_column("Status", style="white", width=10) 
    table.add_column("Mitigation", style="yellow", width=25)
    
    has_risks = any("🔴" in status for _, (status, _) in checks)
    for threat, (status, mitigation) in checks:
        table.add_row(threat, status, mitigation)
    console.print(table)
    
    if has_risks and strict:
        console.print("\n[red]Strict mode: Exiting due to security risks[/red]")
        sys.exit(1)