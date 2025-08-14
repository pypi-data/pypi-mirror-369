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
Simple Warp-style terminal interface for SWE Agent.
Optimized for terminal environments with clean, functional design.
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.live import Live
from rich.layout import Layout

# Import SWE Agent components
from swe_agent.workflows.clean_swe_workflow import CleanSWEWorkflow
from swe_agent.utils.helpers import display_repository_info
from swe_agent.tools.tool_usage_tracker import get_tool_tracker


class SimpleWarpInterface:
    """
    Simple Warp-style terminal interface for SWE Agent.
    Optimized for terminal environments.
    """
    
    def __init__(self, repo_path: str = ".", output_dir: str = "output"):
        self.console = Console()
        self.repo_path = Path(repo_path).resolve()
        self.output_dir = Path(output_dir)
        self.workflow = None
        self.command_history = []
        self.current_directory = Path.cwd()
        self.session_start = datetime.now()
        self.is_running = True
        
        # Initialize workflow
        self._initialize_workflow()
        
    def _initialize_workflow(self):
        """Initialize the SWE Agent workflow."""
        try:
            self.workflow = CleanSWEWorkflow(
                repo_path=str(self.repo_path),
                output_dir=str(self.output_dir)
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
                        changes.append(line.strip())
            
            return {
                "branch": branch,
                "changes": changes,
                "clean": len(changes) == 0
            }
        except Exception:
            return {"branch": "unknown", "changes": [], "clean": True}
    
    def _show_code_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> str:
        """Show code changes with diffs."""
        try:
            # Find new or modified files
            before_changes = set(before.get("changes", []))
            after_changes = set(after.get("changes", []))
            
            # Get new changes
            new_changes = after_changes - before_changes
            
            if not new_changes:
                return ""
            
            changes_output = []
            changes_output.append("📝 Code Changes:")
            changes_output.append("=" * 50)
            
            for change in new_changes:
                # Parse git status line (format: XY filename)
                if len(change) < 3:
                    continue
                    
                status_code = change[:2]
                filename = change[3:]
                
                if status_code.startswith('A'):
                    changes_output.append(f"[OK] Created: {filename}")
                elif status_code.startswith('M'):
                    changes_output.append(f"📝 Modified: {filename}")
                elif status_code.startswith('D'):
                    changes_output.append(f"🗑️ Deleted: {filename}")
                else:
                    changes_output.append(f"🔄 Changed: {filename}")
                
                # Try to show diff for the file
                try:
                    if status_code.startswith('A'):
                        # For new files, show first few lines
                        file_path = Path(self.current_directory) / filename
                        if file_path.exists():
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()[:10]
                                for i, line in enumerate(lines, 1):
                                    changes_output.append(f"  + {i:3d}: {line.rstrip()}")
                                if len(lines) == 10:
                                    changes_output.append("  ... (truncated)")
                    else:
                        # For modified files, show git diff
                        diff_result = subprocess.run(
                            ['git', 'diff', 'HEAD', filename],
                            capture_output=True, text=True, cwd=self.current_directory
                        )
                        
                        if diff_result.stdout:
                            diff_lines = diff_result.stdout.split('\n')
                            line_count = 0
                            for line in diff_lines:
                                if line.startswith('+++') or line.startswith('---'):
                                    continue
                                elif line.startswith('+'):
                                    changes_output.append(f"  + {line[1:]}")
                                    line_count += 1
                                elif line.startswith('-'):
                                    changes_output.append(f"  - {line[1:]}")
                                    line_count += 1
                                elif line.startswith('@@'):
                                    changes_output.append(f"  {line}")
                                
                                # Limit output to prevent overwhelming the terminal
                                if line_count > 15:
                                    changes_output.append("  ... (truncated)")
                                    break
                        
                except Exception:
                    # If diff fails, just show that the file changed
                    changes_output.append(f"  Changes detected but diff unavailable")
                
                changes_output.append("")  # Add spacing between files
            
            return "\n".join(changes_output)
            
        except Exception as e:
            return f"Could not generate diff: {str(e)}"
    
    def _show_status_bar(self):
        """Show the status bar with current info."""
        git_info = self._get_git_status()
        session_time = datetime.now() - self.session_start
        minutes = int(session_time.total_seconds() // 60)
        
        # Create status table
        status_table = Table.grid(padding=1)
        status_table.add_column()
        status_table.add_column(justify="right")
        
        # Left side: Directory and git info
        left_info = Text()
        left_info.append("📁 ", style="bright_blue")
        left_info.append(str(self.current_directory.name), style="bright_white")
        left_info.append(" on ", style="dim")
        left_info.append(f"🌿 {git_info['branch']}", style="bright_green")
        if not git_info['clean']:
            left_info.append(f" ({len(git_info['changes'])} changes)", style="bright_yellow")
        
        # Right side: Session time
        right_info = Text()
        right_info.append(f"Session: {minutes}m", style="bright_cyan")
        
        status_table.add_row(left_info, right_info)
        
        self.console.print(Panel(status_table, style="bright_black", height=3))
    
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
    
    def _execute_ai_command(self, task: str) -> Dict[str, Any]:
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
    
    def _handle_special_commands(self, command: str) -> Optional[Dict[str, Any]]:
        """Handle special commands like cd, exit, etc."""
        if command.strip() in ["exit", "quit", "q"]:
            self.is_running = False
            return {"success": True, "output": "Goodbye! 👋"}
        
        elif command.strip() == "clear":
            self.console.clear()
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
        
        elif command.strip() == "help":
            help_text = """
[A] SWE Agent Warp Interface - Available Commands:

• Basic Commands:
  - exit/quit/q    : Exit the interface
  - clear          : Clear the terminal
  - pwd            : Show current directory
  - cd <path>      : Change directory
  - help           : Show this help message

• AI Commands (use 'ai:' prefix):
  - ai: create a Python calculator
  - ai: analyze the codebase
  - ai: refactor this file
  - ai: add tests for the main function

• Shell Commands:
  - Any regular shell command (ls, git, python, etc.)
  - Commands run in the current directory
  - Output is displayed with success/failure indicators

• Tips:
  - Use 'ai:' prefix for intelligent code assistance
  - Tab completion works for file paths
  - Ctrl+C to cancel current command
            """
            return {"success": True, "output": help_text}
        
        return None
    
    def _add_to_history(self, command: str, output: str, success: bool):
        """Add command to history."""
        self.command_history.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "command": command,
            "success": success,
            "output_preview": output[:100] + "..." if len(output) > 100 else output
        })
        
        # Keep only last 20 commands
        if len(self.command_history) > 20:
            self.command_history = self.command_history[-20:]
    
    def _show_command_result(self, command: str, result: Dict[str, Any]):
        """Show command result with nice formatting."""
        if result["success"]:
            self.console.print(f"[green][OK][/green] {command}")
        else:
            self.console.print(f"[red][X][/red] {command}")
        
        if result["output"].strip():
            # Show output in a panel
            self.console.print(Panel(
                result["output"],
                title="Output" if result["success"] else "Error",
                title_align="left",
                border_style="green" if result["success"] else "red"
            ))
        
        self.console.print()  # Add spacing
    
    def _process_command(self, command: str):
        """Process a single command."""
        if not command.strip():
            return
        
        # Handle special commands
        special_result = self._handle_special_commands(command)
        if special_result:
            self._show_command_result(command, special_result)
            self._add_to_history(command, special_result["output"], special_result["success"])
            return
        
        # Check if it's an AI command
        if command.startswith("ai:"):
            ai_task = command[3:].strip()
            self.console.print(f"[magenta][A] Processing AI task:[/magenta] {ai_task}")
            result = self._execute_ai_command(ai_task)
        else:
            # Execute as shell command
            result = self._execute_shell_command(command)
        
        # Show result and add to history
        self._show_command_result(command, result)
        self._add_to_history(command, result["output"], result["success"])
    
    def run(self):
        """Run the Simple Warp interface."""
        # Show welcome message
        welcome_panel = Panel(
            Text.assemble(
                (">>> SWE Agent Warp Interface\n", "bold bright_magenta"),
                ("Modern AI-powered terminal experience\n\n", "bright_cyan"),
                ("Commands:\n", "bold bright_white"),
                ("• Regular shell commands (ls, git, python, etc.)\n", "bright_white"),
                ("• AI commands: ", "bright_white"),
                ("ai: <task>", "bright_magenta"),
                (" - for intelligent assistance\n", "bright_white"),
                ("• Built-in: ", "bright_white"),
                ("help", "bright_yellow"),
                (", ", "bright_white"),
                ("exit", "bright_red"),
                (", ", "bright_white"),
                ("clear", "bright_green"),
                (", ", "bright_white"),
                ("pwd", "bright_blue"),
                ("\n", "bright_white"),
            ),
            title="[A] Welcome",
            title_align="center",
            style="bright_blue"
        )
        
        self.console.print(welcome_panel)
        self.console.print()
        
        try:
            while self.is_running:
                # Show status bar
                self._show_status_bar()
                
                # Get user input
                try:
                    git_info = self._get_git_status()
                    prompt_text = f"➜ {self.current_directory.name}"
                    if not git_info['clean']:
                        prompt_text += f" ({len(git_info['changes'])})"
                    prompt_text += f" [{git_info['branch']}] $ "
                    
                    command = Prompt.ask(
                        prompt_text,
                        console=self.console,
                        show_default=False
                    )
                    
                    if command:
                        self._process_command(command)
                        
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Command cancelled[/yellow]")
                    continue
                except EOFError:
                    break
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Exiting...[/yellow]")
        
        self.console.print("[green]Session ended. Goodbye! 👋[/green]")


def main():
    """Main entry point for the Simple Warp interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SWE Agent Simple Warp Interface")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    
    args = parser.parse_args()
    
    interface = SimpleWarpInterface(args.repo_path, args.output_dir)
    interface.run()


if __name__ == "__main__":
    main()