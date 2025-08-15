"""
Diff Display Utilities for SWE Agent Package
Enhanced diff visualization for file operations with Rich console formatting.
"""

import difflib
from typing import Optional


def show_file_diff(original_content: str, new_content: str, filename: str) -> str:
    """
    Generate a unified diff display between original and new content.
    
    Args:
        original_content: Original file content (empty string for new files)
        new_content: New file content
        filename: Name of the file being modified
        
    Returns:
        Formatted diff output as string with Rich markup
    """
    if original_content == new_content:
        return "[dim]No changes detected[/dim]"
    
    # Split content into lines for diff
    original_lines = original_content.splitlines(keepends=True) if original_content else []
    new_lines = new_content.splitlines(keepends=True) if new_content else []
    
    # Generate unified diff
    diff_lines = list(difflib.unified_diff(
        original_lines,
        new_lines,
        fromfile=f"{filename} original",
        tofile=f"{filename} updated",
        lineterm='',
        n=3  # 3 lines of context
    ))
    
    if not diff_lines:
        return "[dim]No changes detected[/dim]"
    
    # Format the diff output with syntax highlighting
    formatted_lines = []
    for line in diff_lines:
        if line.startswith('+++') or line.startswith('---'):
            formatted_lines.append(f"[bold]{line}[/bold]")
        elif line.startswith('@@'):
            formatted_lines.append(f"[blue]{line}[/blue]")
        elif line.startswith('+'):
            formatted_lines.append(f"[green]{line}[/green]")
        elif line.startswith('-'):
            formatted_lines.append(f"[red]{line}[/red]")
        else:
            formatted_lines.append(line)
    
    # Join and format as code block
    diff_content = '\n'.join(formatted_lines)
    return f"```diff\n{diff_content}\n```"


def show_simple_diff(original_content: str, new_content: str, max_lines: int = 50) -> str:
    """
    Generate a simple line-by-line diff for quick viewing.
    
    Args:
        original_content: Original file content
        new_content: New file content  
        max_lines: Maximum lines to show in diff
        
    Returns:
        Simple formatted diff output
    """
    if original_content == new_content:
        return "No changes"
    
    original_lines = original_content.splitlines()
    new_lines = new_content.splitlines()
    
    # Simple line count comparison
    if len(original_lines) == 0:
        return f"New file created with {len(new_lines)} lines"
    elif len(new_lines) == 0:
        return f"File deleted (was {len(original_lines)} lines)"
    else:
        return f"File modified: {len(original_lines)} → {len(new_lines)} lines"