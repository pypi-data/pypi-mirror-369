"""
Helper utilities for the SWE Agent system.
Contains utility functions for message handling, logging, and general operations.
"""

import logging
import os
import sys
from typing import List, Optional, Dict, Any
from pathlib import Path
from langchain.schema import BaseMessage, AIMessage, HumanMessage
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from datetime import datetime

console = Console()

def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration with rich formatting.
    
    Args:
        verbose: Enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                show_time=True,
                show_path=verbose,
                rich_tracebacks=True
            )
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    if verbose:
        logging.getLogger("swe_agent").setLevel(logging.DEBUG)

def get_last_ai_message(messages: List[BaseMessage]) -> Optional[AIMessage]:
    """
    Get the last AI message from a list of messages.
    
    Args:
        messages: List of messages to search
        
    Returns:
        Last AI message or None if not found
    """
    if not messages:
        return None
    
    # Iterate backwards to find the last AI message
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            return message
    
    return None

def get_last_human_message(messages: List[BaseMessage]) -> Optional[HumanMessage]:
    """
    Get the last human message from a list of messages.
    
    Args:
        messages: List of messages to search
        
    Returns:
        Last human message or None if not found
    """
    if not messages:
        return None
    
    # Iterate backwards to find the last human message
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return message
    
    return None

def format_message_history(messages: List[BaseMessage], max_messages: int = 10) -> str:
    """
    Format message history for display.
    
    Args:
        messages: List of messages to format
        max_messages: Maximum number of messages to display
        
    Returns:
        Formatted message history string
    """
    if not messages:
        return "No messages in history"
    
    # Get last N messages
    recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
    
    formatted = []
    for i, msg in enumerate(recent_messages, 1):
        msg_type = "Human" if isinstance(msg, HumanMessage) else "AI"
        content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
        formatted.append(f"{i}. [{msg_type}] {content}")
    
    return "\n".join(formatted)

def display_workflow_status(workflow_status: Dict[str, Any]) -> None:
    """
    Display workflow status in a formatted table.
    
    Args:
        workflow_status: Workflow status information
    """
    table = Table(title="SWE Workflow Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    # Add agents
    for agent_name, agent_class in workflow_status.get("agents", {}).items():
        table.add_row(f"Agent: {agent_name}", agent_class)
    
    # Add tools
    for tool_name, tool_class in workflow_status.get("tools", {}).items():
        table.add_row(f"Tool: {tool_name}", tool_class)
    
    # Add paths
    table.add_row("Repository Path", str(workflow_status.get("repo_path", "N/A")))
    table.add_row("Output Directory", str(workflow_status.get("output_dir", "N/A")))
    
    console.print(table)

def display_agent_transition(from_agent: str, to_agent: str, reason: str) -> None:
    """
    Display agent transition information.
    
    Args:
        from_agent: Source agent name
        to_agent: Target agent name
        reason: Reason for transition
    """
    transition_text = Text()
    transition_text.append(f"{from_agent}", style="red")
    transition_text.append(" → ", style="yellow")
    transition_text.append(f"{to_agent}", style="green")
    transition_text.append(f"\nReason: {reason}", style="white")
    
    console.print(Panel(transition_text, title="Agent Transition", border_style="blue"))

def display_tool_execution(tool_name: str, result: str) -> None:
    """
    Display tool execution results.
    
    Args:
        tool_name: Name of the executed tool
        result: Tool execution result
    """
    tool_text = Text()
    tool_text.append(f"Tool: {tool_name}", style="cyan bold")
    tool_text.append(f"\nResult: {result[:300]}...", style="white")
    
    console.print(Panel(tool_text, title="Tool Execution", border_style="green"))

def validate_repository_path(repo_path: Path) -> bool:
    """
    Validate if a repository path is valid.
    
    Args:
        repo_path: Path to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not repo_path.exists():
        console.print(f"[red]Repository path does not exist: {repo_path}[/red]")
        return False
    
    if not repo_path.is_dir():
        console.print(f"[red]Repository path is not a directory: {repo_path}[/red]")
        return False
    
    # Check for Python files
    py_files = list(repo_path.rglob("*.py"))
    if not py_files:
        console.print(f"[yellow]Warning: No Python files found in {repo_path}[/yellow]")
    
    return True

def create_output_directory(output_dir: Path) -> bool:
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_dir: Output directory path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        console.print(f"[red]Failed to create output directory: {e}[/red]")
        return False

def save_workflow_results(results: Dict[str, Any], output_dir: Path) -> str:
    """
    Save workflow results to a JSON file.
    
    Args:
        results: Workflow results to save
        output_dir: Output directory path
        
    Returns:
        Path to saved file
    """
    import json
    from langchain_core.messages import BaseMessage
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"workflow_results_{timestamp}.json"
    
    def serialize_value(value):
        """Recursively serialize complex objects."""
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, BaseMessage):
            return {
                "type": type(value).__name__,
                "content": value.content,
                "role": getattr(value, 'role', 'unknown')
            }
        elif isinstance(value, list):
            return [serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: serialize_value(v) for k, v in value.items()}
        else:
            return str(value)
    
    try:
        # Convert non-serializable objects properly
        serializable_results = serialize_value(results)
        
        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        return str(results_file)
    except Exception as e:
        console.print(f"[red]Failed to save results: {e}[/red]")
        return ""

def display_results_summary(results: Dict[str, Any]) -> None:
    """
    Display a summary of workflow results.
    
    Args:
        results: Workflow results to display
    """
    if results.get("success", False):
        status_color = "green"
        status_text = "SUCCESS"
    else:
        status_color = "red"
        status_text = "FAILED"
    
    summary_text = Text()
    summary_text.append(f"Status: {status_text}", style=f"{status_color} bold")
    summary_text.append(f"\nTask: {results.get('task_description', 'N/A')}", style="white")
    summary_text.append(f"\nMessages: {results.get('message_count', 0)}", style="cyan")
    summary_text.append(f"\nFinal Agent: {results.get('final_sender', 'N/A')}", style="blue")
    
    if results.get("error"):
        summary_text.append(f"\nError: {results['error']}", style="red")
    
    console.print(Panel(summary_text, title="Workflow Results", border_style=status_color))

def get_python_files_count(repo_path: Path) -> int:
    """
    Get the count of Python files in a repository.
    
    Args:
        repo_path: Repository path
        
    Returns:
        Number of Python files
    """
    try:
        return len(list(repo_path.rglob("*.py")))
    except Exception:
        return 0

def get_repository_size(repo_path: Path) -> str:
    """
    Get the size of a repository in human-readable format.
    
    Args:
        repo_path: Repository path
        
    Returns:
        Repository size as string
    """
    try:
        total_size = 0
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        # Convert to human-readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0
        
        return f"{total_size:.1f} TB"
    except Exception:
        return "Unknown"

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def display_progress_bar(current: int, total: int, description: str = "Processing") -> None:
    """
    Display a simple progress indicator.
    
    Args:
        current: Current progress
        total: Total items
        description: Progress description
    """
    percentage = (current / total) * 100 if total > 0 else 0
    bar_length = 30
    filled_length = int(bar_length * current // total) if total > 0 else 0
    
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    
    console.print(f"\r{description}: |{bar}| {percentage:.1f}% ({current}/{total})", end="")
    
    if current == total:
        console.print()  # New line when complete

def get_file_extension_stats(repo_path: Path) -> Dict[str, int]:
    """
    Get statistics about file extensions in the repository.
    
    Args:
        repo_path: Repository path
        
    Returns:
        Dictionary of extension counts
    """
    extension_stats = {}
    
    try:
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext:
                    extension_stats[ext] = extension_stats.get(ext, 0) + 1
                else:
                    extension_stats["<no extension>"] = extension_stats.get("<no extension>", 0) + 1
    except Exception:
        pass
    
    return extension_stats

def is_text_file(file_path: Path) -> bool:
    """
    Check if a file is a text file.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if text file, False otherwise
    """
    text_extensions = {'.py', '.txt', '.md', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini'}
    
    if file_path.suffix.lower() in text_extensions:
        return True
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Read first 1KB
        return True
    except (UnicodeDecodeError, IOError):
        return False

def extract_function_names(file_path: Path) -> List[str]:
    """
    Extract function names from a Python file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        List of function names
    """
    function_names = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import ast
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_names.append(node.name)
    except Exception:
        pass
    
    return function_names

def extract_class_names(file_path: Path) -> List[str]:
    """
    Extract class names from a Python file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        List of class names
    """
    class_names = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import ast
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_names.append(node.name)
    except Exception:
        pass
    
    return class_names

def display_repository_info(repo_path: Path, output_dir: Path, mode: str = "Full Workflow") -> None:
    """
    Display repository information in a formatted table.
    
    Args:
        repo_path: Path to the repository
        output_dir: Output directory path
        mode: Workflow mode
    """
    python_files = get_python_files_count(repo_path)
    repo_size = get_repository_size(repo_path)
    
    # Repository Information Table
    info_table = Table(title="Repository Information")
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="green")
    
    info_table.add_row("Path", str(repo_path))
    info_table.add_row("Python Files", str(python_files))
    info_table.add_row("Size", str(repo_size))
    info_table.add_row("Output Directory", str(output_dir))
    info_table.add_row("Mode", mode)
    
    console.print(info_table)

def display_help() -> None:
    """
    Display help information for the SWE Agent system.
    """
    help_panel = Panel(
        """Available Commands:

• task    - Execute a new SWE task
• status  - Show workflow and system status
• history - View session history
• tools   - View tool usage statistics and analysis
• help    - Show this help message
• exit    - Exit the application

Agent Workflow:
1. Software Engineer - Task delegation and workflow control
2. Code Analyzer - Code analysis and FQDN mapping
3. Editor - File editing and modifications
""",
        title="Help",
        border_style="blue"
    )
    console.print(help_panel)
