# Copyright 2025 SWE Agent Contributors
# SPDX-License-Identifier: Apache-2.0

"""
Real-Time User Interface - Live visibility into SWE Agent operations
Core production feature that shows users what the agent is doing and which tools it's using in real-time.
This is not debugging - this is the main user experience feature for transparency.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.text import Text
import threading
import queue

console = Console()



class RealTimeInterface:
    """Real-time user interface that displays SWE Agent operations as they happen."""
    
    def __init__(self, no_shell_approval: bool = False):
        self.current_agent = None
        self.current_task = None
        self.tools_used = []
        self.start_time = time.time()
        self.last_activity = None
        self.step_count = 0
        self.api_calls = 0
        self.no_shell_approval = no_shell_approval

        
    def set_task(self, task: str):
        """Set the current task being worked on."""
        self.current_task = task
        self.start_time = time.time()
        self.step_count = 0
        console.print(f"\n[bold green]>>> Task:[/bold green] {task}")
        console.print("[dim]SWE Agent is analyzing the task...[/dim]\n")
    
    def set_current_agent(self, agent_name: str, description: Optional[str] = None):
        """Set the current active agent."""
        self.current_agent = agent_name
        self.step_count += 1
        
        agent_icons = {
            'software_engineer': '[*]',
            'code_analyzer': '[?]', 
            'editor': '[E]',
            'planner': '[P]'
        }
        
        icon = agent_icons.get(agent_name.lower(), '[A]')
        display_name = agent_name.replace('_', ' ').title()
        
        status_text = f"{icon} [bold cyan]{display_name}[/bold cyan]"
        if description:
            status_text += f": {description}"
        
        console.print(f"[dim]Step {self.step_count}:[/dim] {status_text}")
        self.last_activity = time.time()
    
    def log_shell_command(self, command: str) -> bool:
        """Display shell command to user and get approval."""
        console.print(f"  [yellow]>>> Shell Command:[/yellow] [bold white on_blue] {command} [/bold white on_blue]")
        
        # Get user approval
        try:
            response = console.input("    [yellow]Execute this command? [Y/n]: [/yellow]").strip().lower()
            if response in ['', 'y', 'yes']:
                console.print("  [green][OK] Command approved[/green]")
                return True
            else:
                console.print("  [red][X] Command cancelled by user[/red]")
                return False
        except (KeyboardInterrupt, EOFError):
            console.print("\n  [red][X] Command cancelled by user[/red]")
            return False
    
    def log_tool_usage(self, tool_name: str, action: str, success: bool = True, duration: float = 0):
        """Log when a tool is used."""
        self.tools_used.append({
            'tool': tool_name,
            'action': action, 
            'success': success,
            'duration': duration,
            'timestamp': time.time()
        })
        
        status = "[OK]" if success else "[X]"
        duration_text = f" ({duration:.2f}s)" if duration > 0 else ""
        
        # Clean up tool name for display
        clean_tool_name = tool_name.replace('_', ' ').title()
        
        console.print(f"  {status} [yellow]{clean_tool_name}[/yellow]: {action}{duration_text}")
        
        # Diff display temporarily disabled to prevent workflow issues
    
    def log_api_call(self, model: str = "Claude", thought_content: Optional[str] = None):
        """Log AI model API calls with actual thoughts."""
        self.api_calls += 1
        if thought_content and thought_content.strip():
            # Extract clean text from Claude's response structure
            clean_text = self._extract_text_content(thought_content)
            if clean_text:
                # Truncate very long responses for display
                if len(clean_text) > 150:
                    display_thought = clean_text[:147] + "..."
                else:
                    display_thought = clean_text
                console.print(f"  >>> [blue]{model}[/blue]: [italic]{display_thought}[/italic]")
            else:
                console.print(f"  >>> [blue]{model}[/blue]: Processing and reasoning...")
        else:
            console.print(f"  >>> [blue]{model}[/blue]: Processing and reasoning...")
    
    def _extract_text_content(self, content):
        """Extract clean text from Claude's response structure."""
        import ast
        import json
        
        if not content:
            return None
            
        content_str = str(content)
        
        # Try to parse as JSON/dict structure
        try:
            # Handle list of dicts like [{'text': '...', 'type': 'text'}]
            if content_str.startswith('[') and 'text' in content_str:
                # Use ast.literal_eval for safe parsing
                parsed = ast.literal_eval(content_str)
                if isinstance(parsed, list):
                    text_parts = []
                    for item in parsed:
                        if isinstance(item, dict) and 'text' in item:
                            text_parts.append(item['text'])
                    if text_parts:
                        return ' '.join(text_parts)
            
            # Handle single dict like {'text': '...', 'type': 'text'}
            elif content_str.startswith('{') and 'text' in content_str:
                parsed = ast.literal_eval(content_str)
                if isinstance(parsed, dict) and 'text' in parsed:
                    return parsed['text']
        except:
            # If parsing fails, return the original content if it's already clean text
            pass
        
        # Return original if it's already clean text (no brackets/JSON structure)
        if not content_str.startswith('[') and not content_str.startswith('{'):
            return content_str
            
        return None
    
    def log_thinking(self, thought: str):
        """Log agent reasoning/thinking."""
        console.print(f"  💭 [italic]{thought}[/italic]")
    
    def show_summary(self):
        """Show final summary of the workflow."""
        runtime = time.time() - self.start_time
        
        console.print(f"\n[bold]📊 Task Summary:[/bold]")
        console.print(f"Runtime: {runtime:.1f}s")
        console.print(f"Steps: {self.step_count}")
        console.print(f"API Calls: {self.api_calls}")
        console.print(f"Tools Used: {len(self.tools_used)}")
        
        if self.tools_used:
            # Show unique tools used
            unique_tools = set(tool['tool'] for tool in self.tools_used)
            console.print(f"\n[bold]🛠️ Tools Utilized:[/bold]")
            for tool in sorted(unique_tools):
                clean_name = tool.replace('_', ' ').title()
                count = len([t for t in self.tools_used if t['tool'] == tool])
                console.print(f"  • {clean_name} ({count}x)")
    
    def log_progress(self, message: str, level: str = "info"):
        """Log general progress messages."""
        colors = {
            'info': 'white',
            'success': 'green', 
            'warning': 'yellow',
            'error': 'red'
        }
        
        color = colors.get(level, 'white')
        console.print(f"  [{color}]{message}[/{color}]")

# Global real-time interface instance
realtime_interface = RealTimeInterface()

class RealTimeHandler(logging.Handler):
    """Custom logging handler for real-time UI updates."""
    
    def emit(self, record):
        try:
            msg = self.format(record)
            
            # Parse tool usage from logs
            if "tool_usage_tracker" in record.name and "completed" in msg:
                # Extract tool name and duration
                parts = msg.split("completed")
                if len(parts) > 1:
                    tool_info = parts[1].strip()
                    tool_name = tool_info.split("in")[0].strip()
                    
                    # Extract duration if present
                    duration = 0
                    if "in " in tool_info:
                        try:
                            duration_str = tool_info.split("in ")[1].split("s")[0]
                            duration = float(duration_str)
                        except:
                            pass
                    
                    success = "success: True" in msg
                    realtime_interface.log_tool_usage(tool_name, "executed", success, duration)
            
            elif "httpx" in record.name and "POST" in msg and "anthropic" in msg:
                realtime_interface.log_api_call()
                
        except Exception:
            pass

def setup_realtime_interface(no_shell_approval: bool = False):
    """Set up the real-time interface with shell approval setting."""
    global realtime_interface
    realtime_interface = RealTimeInterface(no_shell_approval)

def get_realtime_interface() -> RealTimeInterface:
    """Get the global real-time interface instance."""
    return realtime_interface