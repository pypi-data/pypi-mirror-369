# SPDX-License-Identifier: Apache-2.0

"""
Simple diff utilities for git-free file change tracking.
Provides fallback diff functionality when git is not available.
"""

import os
import time
import difflib
from typing import List, Tuple


def get_recent_file_changes(directory: str = ".", minutes: int = 10) -> List[Tuple[str, str, str]]:
    """
    Get list of recently modified files.
    
    Args:
        directory: Directory to scan
        minutes: Files modified within this many minutes
    
    Returns:
        List of (filepath, status, info) tuples
    """
    changes = []
    current_time = time.time()
    cutoff_time = current_time - (minutes * 60)
    
    try:
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git']]
            
            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue
                
                file_path = os.path.join(root, file)
                try:
                    stat_info = os.stat(file_path)
                    
                    if stat_info.st_mtime > cutoff_time:
                        rel_path = os.path.relpath(file_path, directory)
                        file_size = stat_info.st_size
                        mod_time = time.strftime("%H:%M:%S", time.localtime(stat_info.st_mtime))
                        changes.append((rel_path, 'modified', f"{file_size} bytes, {mod_time}"))
                except:
                    continue
    except:
        pass
    
    return changes


def show_file_preview(file_path: str, max_lines: int = 10) -> List[str]:
    """
    Show preview of file content with line numbers.
    
    Args:
        file_path: Path to the file
        max_lines: Maximum lines to show
    
    Returns:
        List of formatted lines for display
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        preview_lines = []
        total_lines = len(lines)
        
        if total_lines <= max_lines:
            # Show all lines
            for i, line in enumerate(lines, 1):
                preview_lines.append(f"[cyan]{i:3d}:[/cyan] {line.rstrip()}")
        else:
            # Show first few and last few lines
            show_count = max_lines // 2
            
            # First lines
            for i in range(show_count):
                preview_lines.append(f"[cyan]{i+1:3d}:[/cyan] {lines[i].rstrip()}")
            
            # Separator
            preview_lines.append("[dim]...[/dim]")
            
            # Last lines
            for i in range(total_lines - show_count, total_lines):
                preview_lines.append(f"[cyan]{i+1:3d}:[/cyan] {lines[i].rstrip()}")
        
        return preview_lines
        
    except Exception as e:
        return [f"[dim]Error reading file: {str(e)}[/dim]"]


def get_file_diff_simple(file_path: str, before_content: str = None) -> List[str]:
    """
    Get diff between before_content and current file content.
    
    Args:
        file_path: Path to the file
        before_content: Previous content (if None, treats as new file)
    
    Returns:
        List of colored diff lines for Rich console
    """
    try:
        # Read current content
        with open(file_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # Split into lines
        current_lines = current_content.splitlines(keepends=True)
        before_lines = before_content.splitlines(keepends=True) if before_content else []
        
        # Generate diff
        diff = difflib.unified_diff(
            before_lines,
            current_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=""
        )
        
        # Color the diff for Rich console
        colored_lines = []
        for line in diff:
            if line.startswith('+++'):
                colored_lines.append(f"[blue]{line}[/blue]")
            elif line.startswith('---'):
                colored_lines.append(f"[blue]{line}[/blue]")
            elif line.startswith('@@'):
                colored_lines.append(f"[blue]{line}[/blue]")
            elif line.startswith('+'):
                colored_lines.append(f"[green]{line}[/green]")
            elif line.startswith('-'):
                colored_lines.append(f"[red]{line}[/red]")
            else:
                colored_lines.append(line)
        
        return colored_lines
        
    except Exception as e:
        return [f"[dim]Error generating diff: {str(e)}[/dim]"]