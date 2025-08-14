"""
Enhanced pair programming interface for SWE Agent
Inspired by Aider's conversational terminal UI
"""

import os
import sys
import time
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.columns import Columns
from pathlib import Path
import subprocess
import json
import threading
import queue
from datetime import datetime

from swe_agent.workflows.clean_swe_workflow import CleanSWEWorkflow
from swe_agent.tools.tool_usage_tracker import ToolUsageTracker

class PairProgrammingInterface:
    def __init__(self, repo_path: str = ".", output_dir: str = "output", enable_mcp: bool = False, no_shell_approval: bool = False, show_diffs: bool = True, debug_mode: bool = False):
        self.console = Console(highlight=False)
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.show_diffs = show_diffs
        self.debug_mode = debug_mode
        self.workflow = CleanSWEWorkflow(repo_path, output_dir, use_planner=False, enable_mcp=enable_mcp, show_diffs=show_diffs, debug_mode=debug_mode)
        self.tool_tracker = ToolUsageTracker()
        self.session_history = []
        self.current_files = set()
        self.git_repo = self._check_git_repo()
        
        # UI state
        self.show_model_info = True
        self.show_git_info = True
        self.last_task_result = None
        
    def _check_git_repo(self) -> bool:
        """Check if we're in a git repository"""
        try:
            subprocess.run(["git", "status"], capture_output=True, check=True, cwd=self.repo_path)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_git_status(self) -> Dict:
        """Get git repository status"""
        if not self.git_repo:
            return {"status": "none", "branch": None, "changed_files": []}
        
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"], 
                capture_output=True, text=True, cwd=self.repo_path
            )
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            # Get changed files
            status_result = subprocess.run(
                ["git", "status", "--porcelain"], 
                capture_output=True, text=True, cwd=self.repo_path
            )
            changed_files = []
            if status_result.returncode == 0:
                for line in status_result.stdout.strip().split('\n'):
                    if line.strip():
                        status_char = line[:2]
                        filename = line[3:].strip()
                        changed_files.append((status_char, filename))
            
            return {
                "status": "clean" if not changed_files else "dirty",
                "branch": branch,
                "changed_files": changed_files
            }
        except Exception:
            return {"status": "error", "branch": None, "changed_files": []}
    
    def _display_header(self):
        """Display the header with model and git info"""
        # Model information
        model_info = Text()
        model_info.append("SWE Agent ", style="bold cyan")
        model_info.append("v1.0.0-dev\n", style="dim")
        model_info.append("Main model: ", style="dim")
        model_info.append("claude-sonnet-4-20250514", style="yellow")
        model_info.append(" with unified tool access\n", style="dim")
        model_info.append("Weak model: ", style="dim")
        model_info.append("claude-sonnet-4-mini", style="yellow")
        
        # Git information
        git_status = self._get_git_status()
        git_info = Text()
        if git_status["status"] == "none":
            git_info.append("Git repo: ", style="dim")
            git_info.append("none", style="red")
        else:
            git_info.append("Git repo: ", style="dim")
            git_info.append(git_status["branch"] or "unknown", style="green")
            if git_status["changed_files"]:
                git_info.append(f" ({len(git_status['changed_files'])} changed)", style="yellow")
        
        git_info.append("\nRepo-map: ", style="dim")
        git_info.append("enabled", style="green")
        
        # Help text
        help_text = Text()
        help_text.append('Use /help <question> for help, run "swe --help" to see cmd line args', style="dim")
        
        # Combine all info
        header_text = Text()
        header_text.append(model_info)
        header_text.append("\n")
        header_text.append(git_info)
        header_text.append("\n")
        header_text.append(help_text)
        
        self.console.print(header_text)
        self.console.print()
    
    def _display_file_context(self):
        """Display current file context"""
        if not self.current_files:
            return
            
        files_text = Text("Files in context: ", style="dim")
        for i, file_path in enumerate(sorted(self.current_files)):
            if i > 0:
                files_text.append(", ", style="dim")
            files_text.append(str(file_path), style="blue")
        
        self.console.print(files_text)
        self.console.print()
    
    def _display_git_changes(self):
        """Display recent git changes"""
        git_status = self._get_git_status()
        if git_status["status"] == "dirty" and git_status["changed_files"]:
            table = Table(title="Git Changes", show_header=True, header_style="bold magenta")
            table.add_column("Status", style="yellow", width=8)
            table.add_column("File", style="blue")
            
            for status_char, filename in git_status["changed_files"]:
                status_desc = {
                    "M ": "Modified",
                    "A ": "Added",
                    "D ": "Deleted",
                    "R ": "Renamed",
                    "C ": "Copied",
                    "?? ": "Untracked"
                }.get(status_char, status_char.strip())
                
                table.add_row(status_desc, filename)
            
            self.console.print(table)
            self.console.print()
    
    def _get_user_input(self) -> str:
        """Get user input with rich prompt"""
        try:
            prompt_text = Text()
            prompt_text.append("> ", style="bold green")
            
            # Use Rich's prompt with the styled text
            user_input = Prompt.ask(prompt_text, console=self.console)
            return user_input.strip()
        except KeyboardInterrupt:
            return "/exit"
        except EOFError:
            return "/exit"
    
    def _handle_command(self, command: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        if command.startswith("/"):
            cmd_parts = command[1:].split()
            cmd = cmd_parts[0].lower()
            
            if cmd == "help":
                self._show_help()
                return True
            elif cmd == "exit" or cmd == "quit":
                return self._handle_exit()
            elif cmd == "status":
                self._show_status()
                return True
            elif cmd == "files":
                self._show_files()
                return True
            elif cmd == "git":
                self._show_git_status()
                return True
            elif cmd == "clear":
                self.console.clear()
                self._display_header()
                return True
            elif cmd == "add":
                if len(cmd_parts) > 1:
                    self._add_file_to_context(cmd_parts[1])
                else:
                    self.console.print("Usage: /add <filename>", style="yellow")
                return True
            elif cmd == "remove":
                if len(cmd_parts) > 1:
                    self._remove_file_from_context(cmd_parts[1])
                else:
                    self.console.print("Usage: /remove <filename>", style="yellow")
                return True
            elif cmd == "tools":
                self._show_tool_usage()
                return True
            else:
                self.console.print(f"Unknown command: {command}", style="red")
                return True
        
        return False
    
    def _show_help(self):
        """Show help information"""
        # Create help content with proper text formatting
        help_content = []
        
        # Title
        help_content.append(Text("SWE Agent Pair Programming Interface", style="bold cyan"))
        help_content.append(Text(""))
        
        # Commands section
        help_content.append(Text("Commands:", style="bold yellow"))
        commands = [
            ("  /help", "Show this help message"),
            ("  /status", "Show system status"),
            ("  /files", "Show files in context"),
            ("  /git", "Show git status"),
            ("  /tools", "Show tool usage statistics"),
            ("  /add <file>", "Add file to context"),
            ("  /remove <file>", "Remove file from context"),
            ("  /clear", "Clear screen"),
            ("  /exit", "Exit the interface")
        ]
        
        for cmd, desc in commands:
            line = Text()
            line.append(cmd, style="cyan")
            line.append(f"    {desc}")
            help_content.append(line)
        
        help_content.append(Text(""))
        
        # Usage section
        help_content.append(Text("Usage:", style="bold yellow"))
        help_content.append(Text("  Simply type your request and the SWE Agent will help you implement it."))
        help_content.append(Text("  The agent can create, edit, and analyze files across all programming languages."))
        help_content.append(Text(""))
        
        # Examples section
        help_content.append(Text("Examples:", style="bold yellow"))
        examples = [
            "  • \"Create a Python calculator with GUI\"",
            "  • \"Fix the bug in main.py line 42\"",
            "  • \"Refactor the database connection code\"",
            "  • \"Add error handling to the API endpoints\"",
            "  • \"Create unit tests for the User class\""
        ]
        for example in examples:
            help_content.append(Text(example))
        
        help_content.append(Text(""))
        
        # Features section
        help_content.append(Text("Features:", style="bold yellow"))
        features = [
            "  ✓ Universal language support (Python, JavaScript, Go, Rust, etc.)",
            "  ✓ Intelligent code analysis and suggestions",
            "  ✓ Git integration and change tracking",
            "  ✓ File context management",
            "  ✓ Tool usage analytics"
        ]
        for feature in features:
            help_content.append(Text(feature, style="green"))
        
        # Create and display the panel
        help_panel = Panel(
            Text("\n").join(help_content),
            title="Help",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(help_panel)
    
    def _show_status(self):
        """Show system status"""
        # Get basic repo info
        python_files = list(self.repo_path.glob("**/*.py"))
        total_size = sum(f.stat().st_size for f in python_files if f.is_file())
        
        table = Table(title="System Status", show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")
        
        table.add_row("Repository", "Active", str(self.repo_path))
        table.add_row("Python Files", str(len(python_files)), f"Total size: {total_size:,} bytes")
        table.add_row("Git Repository", "Yes" if self.git_repo else "No", "")
        table.add_row("Files in Context", str(len(self.current_files)), ", ".join(map(str, list(self.current_files)[:3])))
        table.add_row("Tool Tracking", "Enabled", f"{len(self.tool_tracker.usage_stats)} tools tracked")
        
        self.console.print(table)
    
    def _show_files(self):
        """Show files in context"""
        if not self.current_files:
            self.console.print("No files in context", style="yellow")
            return
        
        table = Table(title="Files in Context", show_header=True, header_style="bold magenta")
        table.add_column("File", style="blue")
        table.add_column("Status", style="green")
        
        for file_path in sorted(self.current_files):
            if file_path.exists():
                size = file_path.stat().st_size
                status = f"{size:,} bytes"
            else:
                status = "Not found"
            table.add_row(str(file_path), status)
        
        self.console.print(table)
    
    def _show_git_status(self):
        """Show detailed git status"""
        git_status = self._get_git_status()
        
        if git_status["status"] == "none":
            self.console.print("Not a git repository", style="yellow")
            return
        
        self.console.print(f"Branch: {git_status['branch']}", style="green")
        self.console.print(f"Status: {git_status['status']}", style="green" if git_status['status'] == "clean" else "yellow")
        
        if git_status["changed_files"]:
            self._display_git_changes()
        else:
            self.console.print("Working directory clean", style="green")
    
    def _show_tool_usage(self):
        """Show tool usage statistics"""
        if not self.tool_tracker.usage_stats:
            self.console.print("No tool usage data available", style="yellow")
            return
        
        table = Table(title="Tool Usage Statistics", show_header=True, header_style="bold magenta")
        table.add_column("Tool", style="cyan")
        table.add_column("Uses", style="green")
        table.add_column("Avg Time", style="blue")
        table.add_column("Success Rate", style="yellow")
        
        for tool_name, stats in self.tool_tracker.usage_stats.items():
            success_rate = (stats['success_count'] / stats['total_count']) * 100 if stats['total_count'] > 0 else 0
            avg_time = stats['total_time'] / stats['total_count'] if stats['total_count'] > 0 else 0
            
            table.add_row(
                tool_name,
                str(stats['total_count']),
                f"{avg_time:.2f}s",
                f"{success_rate:.1f}%"
            )
        
        self.console.print(table)
    
    def _add_file_to_context(self, filename: str):
        """Add file to context"""
        file_path = Path(filename)
        if not file_path.is_absolute():
            file_path = self.repo_path / file_path
        
        if file_path.exists():
            self.current_files.add(file_path)
            self.console.print(f"Added {filename} to context", style="green")
        else:
            self.console.print(f"File not found: {filename}", style="red")
    
    def _remove_file_from_context(self, filename: str):
        """Remove file from context"""
        file_path = Path(filename)
        if not file_path.is_absolute():
            file_path = self.repo_path / file_path
        
        if file_path in self.current_files:
            self.current_files.remove(file_path)
            self.console.print(f"Removed {filename} from context", style="green")
        else:
            self.console.print(f"File not in context: {filename}", style="yellow")
    
    def _handle_exit(self) -> bool:
        """Handle exit command"""
        if Confirm.ask("Are you sure you want to exit?"):
            self.console.print("Thank you for using SWE Agent Pair Programming Interface!", style="bold green")
            return True
        return False
    
    def _execute_task(self, task: str) -> Dict:
        """Execute a task using the SWE workflow with real-time interface"""
        # The real-time interface is built into run_workflow - no need for separate progress display
        try:
            result = self.workflow.run_workflow(task)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task_description": task
            }
    
    def _display_task_result(self, result: Dict):
        """Display task execution result"""
        if not result:
            return
        
        # Show execution summary
        final_state = result.get("final_state", {})
        messages = final_state.get("messages", [])
        
        if messages:
            # Show the last AI message (result)
            last_message = messages[-1]
            if hasattr(last_message, 'content') and last_message.content:
                content = str(last_message.content)
                
                # Ensure content is not empty and is a string
                if content and content.strip():
                    # Display the response in a panel
                    panel = Panel(
                        Text(content),
                        title="SWE Agent Response",
                        title_align="left",
                        border_style="green"
                    )
                    self.console.print(panel)
                else:
                    self.console.print("Task completed successfully", style="green")
        
        # Show task statistics
        stats_text = Text()
        stats_text.append(f"Messages: {result.get('message_count', 0)}", style="dim")
        stats_text.append(f" | Final sender: {result.get('final_sender', 'Unknown')}", style="dim")
        self.console.print(stats_text)
        self.console.print()
    
    def run(self):
        """Run the pair programming interface"""
        self.console.clear()
        self._display_header()
        
        self.console.print("Welcome to SWE Agent Pair Programming Interface!", style="bold green")
        self.console.print("Type your request or use /help for commands.", style="dim")
        self.console.print()
        
        while True:
            try:
                # Display context information
                self._display_file_context()
                
                # Get user input
                user_input = self._get_user_input()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if self._handle_command(user_input):
                    if user_input.startswith("/exit"):
                        break
                    continue
                
                # Execute the task
                self.console.print()
                try:
                    result = self._execute_task(user_input)
                    self._display_task_result(result)
                    self.last_task_result = result
                    
                    # Add to session history
                    self.session_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "input": user_input,
                        "result": result
                    })
                    
                except Exception as e:
                    self.console.print(f"Error executing task: {str(e)}", style="red")
                    self.console.print()
                
                # Show git changes if any
                self._display_git_changes()
                
            except KeyboardInterrupt:
                self.console.print("\nUse /exit to quit gracefully", style="yellow")
                continue
            except Exception as e:
                self.console.print(f"Unexpected error: {str(e)}", style="red")
                continue

def main():
    """Main entry point for pair programming interface"""
    interface = PairProgrammingInterface()
    interface.run()

if __name__ == "__main__":
    main()