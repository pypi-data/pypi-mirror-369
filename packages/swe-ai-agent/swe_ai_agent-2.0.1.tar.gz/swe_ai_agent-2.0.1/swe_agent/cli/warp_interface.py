# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 SWE Agent
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Warp-style terminal interface for SWE Agent.
Modern AI-powered terminal interface with integrated agent capabilities.
"""

import os
import sys
import time
import asyncio
import subprocess
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.padding import Padding
from rich.rule import Rule
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from swe_agent.workflows.clean_swe_workflow import CleanSWEWorkflow
from swe_agent.utils.helpers import display_repository_info
from swe_agent.tools.tool_usage_tracker import get_tool_tracker

# Import git-free diff utilities
from swe_agent.utils.simple_diff import get_recent_file_changes, show_file_preview, get_file_diff_simple


class WarpInterface:
    """
    Modern Warp-style terminal interface for SWE Agent.
    Provides an AI-powered terminal experience with integrated agent capabilities.
    """
    
    def __init__(self, repo_path: str = ".", output_dir: str = "output", enable_mcp: bool = False, no_shell_approval: bool = False, show_diffs: bool = True, debug_mode: bool = False):
        self.console = Console()
        self.repo_path = Path(repo_path).resolve()
        self.output_dir = Path(output_dir)
        self.enable_mcp = enable_mcp
        self.no_shell_approval = no_shell_approval
        self.show_diffs = show_diffs
        self.debug_mode = debug_mode
        self.workflow = None
        self.command_history = []
        self.ai_suggestions = []
        self.current_directory = Path.cwd()
        self.session_start = datetime.now()
        
        # Initialize workflow
        self._initialize_workflow()
        
        # Terminal state
        self.is_running = True
        self.current_input = ""
        self.ai_mode = False
        
    def _initialize_workflow(self):
        """Initialize the SWE Agent workflow."""
        try:
            self.workflow = CleanSWEWorkflow(
                repo_path=str(self.repo_path),
                output_dir=str(self.output_dir),
                use_planner=False,
                enable_mcp=self.enable_mcp,
                show_diffs=self.show_diffs,
                debug_mode=self.debug_mode
            )
        except Exception as e:
            self.console.print(f"[red]Error initializing workflow: {e}[/red]")
    
    def _get_git_status(self) -> Dict[str, Any]:
        """Get current git status."""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True, text=True, cwd=self.current_directory
            )
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "main"
            
            # Get git status
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, cwd=self.current_directory
            )
            
            changes = []
            if status_result.returncode == 0:
                for line in status_result.stdout.strip().split('\n'):
                    if line.strip():
                        status_code = line[:2]
                        filename = line[3:].strip()
                        changes.append({"status": status_code, "file": filename})
            
            return {
                "branch": branch,
                "changes": changes,
                "clean": len(changes) == 0
            }
        except Exception:
            return {"branch": "unknown", "changes": [], "clean": True}
    
    def _show_code_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> str:
        """Show code changes without showing diff content."""
        try:
            # Use git-free approach to detect recent changes
            recent_changes = get_recent_file_changes(str(self.current_directory), minutes=1)
            
            if not recent_changes:
                return ""
            
            changes_output = []
            changes_output.append("📝 Code Changes:")
            changes_output.append("=" * 50)
            
            for file_path, status, info in recent_changes:
                changes_output.append(f"🔄 Modified: {file_path}")
                changes_output.append(f"  [dim]{info}[/dim]")
                changes_output.append("")  # Add spacing between files
            
            return "\n".join(changes_output)
        except Exception as e:
            return f"Could not detect changes: {str(e)}"
    
    def _create_header(self) -> Panel:
        """Create the header panel with session info."""
        session_time = datetime.now() - self.session_start
        hours, remainder = divmod(int(session_time.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        git_info = self._get_git_status()
        
        header_content = Table.grid(padding=1)
        header_content.add_column(justify="left")
        header_content.add_column(justify="center")
        header_content.add_column(justify="right")
        
        # Left: Directory and Git info
        left_info = Text()
        left_info.append("📁 ", style="bright_blue")
        left_info.append(str(self.current_directory.name), style="bright_white")
        left_info.append(" on ", style="dim")
        left_info.append(f"🌿 {git_info['branch']}", style="bright_green")
        # Use git-free change detection
        recent_changes = get_recent_file_changes(str(self.current_directory), minutes=10)
        if recent_changes:
            left_info.append(f" ({len(recent_changes)} changes)", style="bright_yellow")
        
        # Center: SWE Agent title
        center_info = Text("SWE Agent", style="bold bright_magenta")
        center_info.append(" • ", style="dim")
        center_info.append("AI Terminal", style="bright_cyan")
        
        # Right: Session time
        right_info = Text()
        right_info.append("⏱️ ", style="bright_blue")
        right_info.append(f"{hours:02d}:{minutes:02d}:{seconds:02d}", style="bright_white")
        
        header_content.add_row(left_info, center_info, right_info)
        
        return Panel(
            header_content,
            style="bright_black on grey11",
            height=3
        )
    
    def _create_ai_panel(self) -> Panel:
        """Create the AI suggestions panel."""
        if not self.ai_suggestions:
            content = Text("💡 AI suggestions will appear here", style="dim italic")
        else:
            content = Text()
            for i, suggestion in enumerate(self.ai_suggestions[-3:], 1):
                content.append(f"{i}. ", style="bright_blue")
                content.append(suggestion, style="bright_white")
                content.append("\n")
        
        return Panel(
            content,
            title="[A] AI Assistant",
            title_align="left",
            style="bright_blue",
            height=8
        )
    
    def _create_command_panel(self) -> Panel:
        """Create the command input panel."""
        prompt_text = Text()
        prompt_text.append("➜ ", style="bright_green")
        prompt_text.append(str(self.current_directory.name), style="bright_blue")
        prompt_text.append(" ", style="dim")
        
        if self.ai_mode:
            prompt_text.append("[A] AI: ", style="bright_magenta")
        else:
            prompt_text.append("$ ", style="bright_white")
        
        prompt_text.append(self.current_input, style="bright_white")
        prompt_text.append("▊", style="bright_white blink")
        
        return Panel(
            prompt_text,
            style="bright_black on grey7",
            height=3
        )
    
    def _create_history_panel(self) -> Panel:
        """Create the command history panel."""
        if not self.command_history:
            content = Text("Command history will appear here", style="dim italic")
        else:
            content = Text()
            for cmd in self.command_history[-10:]:
                timestamp = cmd.get('timestamp', '')
                command = cmd.get('command', '')
                output = cmd.get('output', '')
                success = cmd.get('success', True)
                
                # Add timestamp
                content.append(f"[{timestamp}] ", style="dim")
                
                # Add command with status indicator
                if success:
                    content.append("[OK] ", style="bright_green")
                else:
                    content.append("[ERR] ", style="bright_red")
                
                content.append(command, style="bright_white")
                content.append("\n")
                
                # Add output preview if available
                if output and len(output) > 0:
                    preview = output[:100] + "..." if len(output) > 100 else output
                    content.append(f"   {preview}", style="dim")
                    content.append("\n")
        
        return Panel(
            content,
            title="[History] Command History",
            title_align="left",
            style="bright_yellow",
            height=15
        )
    
    def _create_layout(self) -> Layout:
        """Create the main layout."""
        layout = Layout()
        
        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        
        # Split body into main and sidebar
        layout["body"].split_row(
            Layout(name="main", ratio=2),
            Layout(name="sidebar", ratio=1)
        )
        
        # Split main into AI panel and command area
        layout["main"].split_column(
            Layout(name="ai_panel", size=8),
            Layout(name="command_area")
        )
        
        # Update panels
        layout["header"].update(self._create_header())
        layout["ai_panel"].update(self._create_ai_panel())
        layout["command_area"].update(self._create_command_panel())
        layout["sidebar"].update(self._create_history_panel())
        
        return layout
    
    def _execute_shell_command(self, command: str) -> Dict[str, Any]:
        """Execute a shell command and return results."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.current_directory,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout + result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "Command timed out after 30 seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Error executing command: {str(e)}",
                "returncode": -1
            }
    
    async def _execute_ai_command(self, task: str) -> Dict[str, Any]:
        """Execute an AI task using the SWE Agent workflow."""
        try:
            if not self.workflow:
                return {
                    "success": False,
                    "output": "SWE Agent workflow not initialized"
                }
            
            # Get git status before execution to track changes
            git_status_before = self._get_git_status()
            
            # Execute the task using the workflow's run_workflow method
            result = self.workflow.run_workflow(task)
            
            # Get git status after execution
            git_status_after = self._get_git_status()
            
            # Check for file changes and show diffs
            changes_output = self._show_code_changes(git_status_before, git_status_after)
            
            output = f"AI Task: {task}\nResult: Task completed successfully"
            if changes_output:
                output += f"\n\n{changes_output}"
            
            return {
                "success": True,
                "output": output
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"AI task failed: {str(e)}"
            }
    
    def _add_to_history(self, command: str, output: str, success: bool):
        """Add command to history."""
        self.command_history.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "command": command,
            "output": output,
            "success": success
        })
        
        # Keep only last 50 commands
        if len(self.command_history) > 50:
            self.command_history = self.command_history[-50:]
    
    def _generate_ai_suggestions(self, current_input: str):
        """Generate AI suggestions based on current input."""
        suggestions = []
        
        # Basic suggestions based on input
        if current_input.startswith("git"):
            suggestions.extend([
                "git status - Check repository status",
                "git add . - Stage all changes",
                "git commit -m 'message' - Commit changes"
            ])
        elif current_input.startswith("cd"):
            suggestions.extend([
                "cd .. - Go to parent directory",
                "cd ~ - Go to home directory",
                "cd / - Go to root directory"
            ])
        elif current_input.startswith("ls"):
            suggestions.extend([
                "ls -la - List all files with details",
                "ls -lh - List files with human-readable sizes",
                "ls -t - List files by modification time"
            ])
        elif "create" in current_input.lower() or "make" in current_input.lower():
            suggestions.extend([
                "Use AI mode to create files with intelligent content",
                "mkdir new_directory - Create a new directory",
                "touch filename.txt - Create an empty file"
            ])
        else:
            suggestions.extend([
                "Type 'ai:' to enter AI mode for intelligent assistance",
                "Use Tab for command completion",
                "Press Ctrl+C to cancel current command"
            ])
        
        self.ai_suggestions = suggestions
    
    def _handle_special_commands(self, command: str) -> Optional[Dict[str, Any]]:
        """Handle special commands like cd, exit, etc."""
        if command.strip() == "exit" or command.strip() == "quit":
            self.is_running = False
            return {"success": True, "output": "Goodbye! 👋"}
        
        elif command.strip() == "clear":
            self.command_history = []
            return {"success": True, "output": "Terminal cleared"}
        
        elif command.startswith("cd "):
            path = command[3:].strip()
            try:
                if path == "~":
                    new_path = Path.home()
                elif path == "..":
                    new_path = self.current_directory.parent
                else:
                    new_path = Path(path)
                    if not new_path.is_absolute():
                        new_path = self.current_directory / new_path
                
                if new_path.exists() and new_path.is_dir():
                    self.current_directory = new_path.resolve()
                    return {"success": True, "output": f"Changed to {self.current_directory}"}
                else:
                    return {"success": False, "output": f"Directory not found: {path}"}
            except Exception as e:
                return {"success": False, "output": f"Error changing directory: {str(e)}"}
        
        elif command.strip() == "pwd":
            return {"success": True, "output": str(self.current_directory)}
        
        return None
    
    async def _process_command(self, command: str):
        """Process a single command."""
        if not command.strip():
            return
        
        # Handle special commands
        special_result = self._handle_special_commands(command)
        if special_result:
            self._add_to_history(command, special_result["output"], special_result["success"])
            return
        
        # Check if it's an AI command
        if command.startswith("ai:"):
            ai_task = command[3:].strip()
            result = await self._execute_ai_command(ai_task)
        else:
            # Execute as shell command
            result = self._execute_shell_command(command)
        
        # Add to history
        self._add_to_history(command, result["output"], result["success"])
    
    def _show_welcome_message(self):
        """Show welcome message."""
        welcome_panel = Panel(
            Text.assemble(
                (">>> Welcome to SWE Agent Warp Interface\n\n", "bold bright_magenta"),
                ("Modern AI-powered terminal experience\n", "bright_cyan"),
                ("• Type commands normally or use ", "bright_white"),
                ("ai:", "bright_magenta"),
                (" prefix for AI assistance\n", "bright_white"),
                ("• Use ", "bright_white"),
                ("Tab", "bright_yellow"),
                (" for suggestions and ", "bright_white"),
                ("Ctrl+C", "bright_yellow"),
                (" to cancel\n", "bright_white"),
                ("• Type ", "bright_white"),
                ("exit", "bright_red"),
                (" to quit\n", "bright_white"),
            ),
            title="[A] SWE Agent",
            title_align="center",
            style="bright_blue"
        )
        
        self.console.print(welcome_panel)
        self.console.print()
    
    async def run(self):
        """Run the Warp interface."""
        self._show_welcome_message()
        
        try:
            while self.is_running:
                # Display the current layout
                self._display_interface()
                
                # Get user input with custom prompt
                try:
                    git_info = self._get_git_status()
                    prompt_text = f"➜ {self.current_directory.name}"
                    if not git_info['clean']:
                        prompt_text += f" ({len(git_info['changes'])} changes)"
                    prompt_text += " $ "
                    
                    command = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: input(prompt_text)
                    )
                    
                    if command:
                        # Generate AI suggestions
                        self._generate_ai_suggestions(command)
                        
                        # Process command
                        await self._process_command(command)
                        
                        # Clear screen and redraw (optional)
                        # self.console.clear()
                        
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Command cancelled[/yellow]")
                    continue
                except EOFError:
                    break
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Exiting...[/yellow]")
        
        self.console.print("[green]Session ended. Goodbye! 👋[/green]")
    
    def _display_interface(self):
        """Display the current interface state."""
        # Clear screen
        self.console.clear()
        
        # Display header
        self.console.print(self._create_header())
        
        # Display AI suggestions if available
        if self.ai_suggestions:
            self.console.print(self._create_ai_panel())
        
        # Display recent history
        if self.command_history:
            self.console.print(self._create_history_panel())
    



async def main():
    """Main entry point for the Warp interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SWE Agent Warp Interface")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    
    args = parser.parse_args()
    
    interface = WarpInterface(args.repo_path, args.output_dir)
    await interface.run()


if __name__ == "__main__":
    asyncio.run(main())