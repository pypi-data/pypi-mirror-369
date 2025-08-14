"""
CLI Interface - Main command-line interface for the SWE Agent system.
Handles interactive mode, task execution, and user interaction.
"""

import logging
import sys
from typing import Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.tree import Tree
import time
import json

from swe_agent.workflows.clean_swe_workflow import CleanSWEWorkflow
from swe_agent.config.settings import Settings
from swe_agent.cli.tool_usage_display import ToolUsageDisplay
from swe_agent.utils.helpers import (
    display_workflow_status, display_agent_transition, display_tool_execution,
    display_results_summary, save_workflow_results, format_message_history,
    get_python_files_count, get_repository_size, truncate_text
)

logger = logging.getLogger(__name__)
console = Console()

class SWEInterface:
    """
    Main CLI interface for the SWE Agent system.
    Handles user interaction, task execution, and workflow management.
    """
    
    def __init__(self, settings: Settings, enable_mcp: bool = False, no_shell_approval: bool = False, show_diffs: bool = True, debug_mode: bool = False):
        self.settings = settings
        self.enable_mcp = enable_mcp
        self.no_shell_approval = no_shell_approval
        self.show_diffs = show_diffs
        self.debug_mode = debug_mode
        self.workflow = CleanSWEWorkflow(str(settings.repo_path), str(settings.output_dir), settings.use_planner, enable_mcp, show_diffs, debug_mode)
        self.session_history = []
        self.running = True
        self.tool_display = ToolUsageDisplay(console)
        
    def start_interactive_mode(self) -> None:
        """
        Start the interactive CLI mode for continuous task input.
        """
        console.print(Panel(
            Text(">>> SWE Agent Interactive Mode", style="bold blue"),
            title="Welcome",
            border_style="blue"
        ))
        
        # Display repository information
        self._display_repository_info()
        
        # Display workflow status
        workflow_status = {"status": "Clean workflow initialized"}
        display_workflow_status(workflow_status)
        
        # Display available commands
        self._display_help()
        
        # Main interactive loop
        while self.running:
            try:
                command = Prompt.ask(
                    "[bold green]SWE Agent[/bold green]",
                    choices=["task", "status", "history", "tools", "help", "exit"],
                    default="task"
                )
                
                if command == "task":
                    self._handle_task_command()
                elif command == "status":
                    self._handle_status_command()
                elif command == "history":
                    self._handle_history_command()
                elif command == "tools":
                    self._handle_tools_command()
                elif command == "help":
                    self._display_help()
                elif command == "exit":
                    self._handle_exit_command()
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' command to quit gracefully[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                if self.settings.verbose:
                    import traceback
                    console.print(traceback.format_exc())
    
    def execute_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute a single task using the SWE workflow.
        
        Args:
            task_description: Description of the task to perform
            
        Returns:
            Task execution results
        """
        console.print(Panel(
            Text(f"Executing Task: {task_description}", style="bold cyan"),
            title="Task Execution",
            border_style="cyan"
        ))
        
        # Display repository information
        self._display_repository_info()
        
        # Execute the workflow with progress tracking
        results = self._execute_workflow_with_progress(task_description)
        
        # Display results
        display_results_summary(results)
        
        # Save results
        if results.get("success", False):
            results_file = save_workflow_results(results, self.settings.output_dir)
            if results_file:
                console.print(f"[green]Results saved to: {results_file}[/green]")
        
        # Add to session history
        self.session_history.append({
            "task": task_description,
            "results": results,
            "timestamp": time.time()
        })
        
        return results
    
    def _display_repository_info(self) -> None:
        """Display information about the repository being analyzed."""
        info_table = Table(title="Repository Information")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="green")
        
        info_table.add_row("Path", str(self.settings.repo_path))
        info_table.add_row("Python Files", str(get_python_files_count(self.settings.repo_path)))
        info_table.add_row("Size", get_repository_size(self.settings.repo_path))
        info_table.add_row("Output Directory", str(self.settings.output_dir))
        info_table.add_row("Mode", "Analysis Only" if self.settings.analyze_only else "Full Workflow")
        
        console.print(info_table)
    
    def _display_help(self) -> None:
        """Display help information and available commands."""
        help_text = Text()
        help_text.append("Available Commands:\n\n", style="bold")
        help_text.append("• task    - Execute a new SWE task\n", style="green")
        help_text.append("• status  - Show workflow and system status\n", style="blue")
        help_text.append("• history - View session history\n", style="yellow")
        help_text.append("• tools   - View tool usage statistics and analysis\n", style="magenta")
        help_text.append("• help    - Show this help message\n", style="cyan")
        help_text.append("• exit    - Exit the application\n", style="red")
        
        help_text.append("\nAgent Workflow:\n", style="bold")
        help_text.append("1. Software Engineer - Task delegation and workflow control\n", style="white")
        help_text.append("2. Code Analyzer - Code analysis and FQDN mapping\n", style="white")
        help_text.append("3. Editor - File editing and modifications\n", style="white")
        
        console.print(Panel(help_text, title="Help", border_style="green"))
    
    def _handle_task_command(self) -> None:
        """Handle the task command for executing new tasks."""
        task_description = Prompt.ask("Enter task description")
        
        if not task_description.strip():
            console.print("[red]Task description cannot be empty[/red]")
            return
        
        # Confirm task execution
        if not Confirm.ask(f"Execute task: '{task_description}'?"):
            console.print("[yellow]Task cancelled[/yellow]")
            return
        
        # Execute the task
        results = self.execute_task(task_description)
        
        # Offer to view detailed results
        if results.get("success", False) and Confirm.ask("View detailed results?"):
            self._display_detailed_results(results)
    
    def _handle_status_command(self) -> None:
        """Handle the status command for displaying system status."""
        console.print(Panel(
            Text("System Status", style="bold blue"),
            title="Status Check",
            border_style="blue"
        ))
        
        # Display workflow status
        workflow_status = {"status": "Clean workflow initialized"}
        display_workflow_status(workflow_status)
        
        # Display available actions
        actions = ["task", "status", "history", "tools", "help", "exit"]
        self._display_available_actions(actions)
        
        # Display session statistics
        self._display_session_stats()
    
    def _handle_history_command(self) -> None:
        """Handle the history command for viewing session history."""
        if not self.session_history:
            console.print("[yellow]No tasks executed in this session[/yellow]")
            return
        
        history_table = Table(title="Session History")
        history_table.add_column("Task", style="cyan")
        history_table.add_column("Status", style="green")
        history_table.add_column("Messages", style="blue")
        history_table.add_column("Time", style="yellow")
        
        for entry in self.session_history:
            task = truncate_text(entry["task"], 50)
            status = "✓ Success" if entry["results"].get("success", False) else "✗ Failed"
            messages = str(entry["results"].get("message_count", 0))
            timestamp = time.strftime("%H:%M:%S", time.localtime(entry["timestamp"]))
            
            history_table.add_row(task, status, messages, timestamp)
        
        console.print(history_table)
        
        # Offer to view detailed results for a specific task
        if len(self.session_history) > 1:
            if Confirm.ask("View detailed results for a specific task?"):
                self._select_and_display_history_entry()
    
    def _handle_tools_command(self) -> None:
        """Handle the tools command for viewing tool usage statistics."""
        console.print(Panel(
            Text("Tool Usage Analysis", style="bold blue"),
            title="Tool Statistics",
            border_style="blue"
        ))
        
        # Sub-command menu
        tool_command = Prompt.ask(
            "What tool information would you like to see?",
            choices=["overall", "agent", "tool", "live", "clear", "back"],
            default="overall"
        )
        
        if tool_command == "overall":
            self.tool_display.display_overall_usage()
        elif tool_command == "agent":
            agent_name = Prompt.ask(
                "Which agent?",
                choices=["software_engineer", "code_analyzer", "editor", "planner"],
                default="software_engineer"
            )
            self.tool_display.display_agent_usage(agent_name)
        elif tool_command == "tool":
            tool_name = Prompt.ask("Enter tool name (e.g., 'create_file', 'execute_shell_command')")
            self.tool_display.display_tool_details(tool_name)
        elif tool_command == "live":
            self.tool_display.display_live_usage()
        elif tool_command == "clear":
            if Confirm.ask("Clear all tool usage history?"):
                self.tool_display.clear_usage_history()
        elif tool_command == "back":
            return
    
    def _handle_exit_command(self) -> None:
        """Handle the exit command for graceful shutdown."""
        if self.session_history:
            console.print(f"[blue]Executed {len(self.session_history)} tasks this session[/blue]")
        
        if Confirm.ask("Are you sure you want to exit?"):
            console.print("[green]Thank you for using SWE Agent![/green]")
            self.running = False
        else:
            console.print("[yellow]Continuing session...[/yellow]")
    
    def _execute_workflow_with_progress(self, task_description: str) -> Dict[str, Any]:
        """
        Execute workflow with progress tracking and live updates.
        
        Args:
            task_description: Task description
            
        Returns:
            Workflow execution results
        """
        # Show basic task start message
        console.print(f"[blue]>>> Starting task...[/blue]")
        
        start_time = time.time()
        
        try:
            # Real-time interface is built into run_workflow - shows detailed progress
            results = self.workflow.run_workflow(task_description)
            
            # Check if workflow is waiting for approval
            if results.get("final_sender") == "planner":
                # Look for approval signal in the final state messages
                final_state = results.get("final_state", {})
                messages = final_state.get("messages", [])
                
                needs_approval = False
                for message in reversed(messages):
                    if hasattr(message, 'content') and "AWAITING_HUMAN_APPROVAL" in message.content:
                        needs_approval = True
                        break
                
                if needs_approval:
                    approval_results = self._handle_approval_workflow(results)
                    if approval_results:
                        results = approval_results
            
            execution_time = time.time() - start_time
            results["execution_time"] = execution_time
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            results = {
                "task_description": task_description,
                "error": str(e),
                "success": False,
                "execution_time": time.time() - start_time
            }
        
        return results
    
    def _handle_approval_workflow(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the approval workflow when the planner is waiting for human approval.
        
        Args:
            results: Current workflow results
            
        Returns:
            Updated results after approval process
        """
        # Extract the plan from the messages
        final_state = results.get("final_state", {})
        messages = final_state.get("messages", [])
        plan_content = None
        
        # Find the plan in the messages
        for message in reversed(messages):
            if hasattr(message, 'content') and ("PROJECT PLAN" in message.content.upper() or "AWAITING_HUMAN_APPROVAL" in message.content):
                plan_content = message.content
                break
        
        if not plan_content:
            console.print("[red]No plan found in workflow results![/red]")
            return results
        
        # Display the plan
        console.print(Panel(
            Text("Project Plan Generated", style="bold cyan"),
            title="Planning Complete",
            border_style="cyan"
        ))
        
        # Clean up the plan content for display
        plan_display = plan_content.replace("AWAITING_HUMAN_APPROVAL", "").strip()
        console.print(Panel(
            Text(plan_display, style="white"),
            title="Detailed Plan",
            border_style="blue"
        ))
        
        # Get user approval
        console.print("[bold yellow]Please review the plan above.[/bold yellow]")
        approval_choice = Prompt.ask(
            "Do you approve this plan?",
            choices=["approve", "modify", "reject"],
            default="approve"
        )
        
        if approval_choice == "approve":
            console.print("[green]Plan approved! Proceeding with implementation...[/green]")
            # Continue workflow with approval
            return self._continue_workflow_with_approval(results, "approved")
        elif approval_choice == "modify":
            modification_request = Prompt.ask("What changes would you like to make?")
            console.print("[yellow]Requesting plan modifications...[/yellow]")
            return self._continue_workflow_with_approval(results, f"modify: {modification_request}")
        else:
            console.print("[red]Plan rejected. Task cancelled.[/red]")
            results["success"] = False
            results["error"] = "Plan rejected by user"
            return results
    
    def _continue_workflow_with_approval(self, results: Dict[str, Any], approval_response: str) -> Dict[str, Any]:
        """
        Continue the workflow with the user's approval response.
        
        Args:
            results: Current workflow results
            approval_response: User's approval response
            
        Returns:
            Updated workflow results
        """
        try:
            # Extract the original task from the results
            original_task = results.get("task_description", "")
            
            # Continue the workflow with approval and original task context
            continued_results = self.workflow.continue_workflow_with_approval(approval_response, original_task)
            
            # Merge results
            if continued_results:
                results.update(continued_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to continue workflow with approval: {e}")
            results["error"] = str(e)
            results["success"] = False
            return results
    
    def _display_available_actions(self, actions: Dict[str, Any]) -> None:
        """Display available actions for each agent."""
        actions_table = Table(title="Available Agent Actions")
        actions_table.add_column("Agent", style="cyan")
        actions_table.add_column("Available Tools", style="green")
        
        for agent_name, tools in actions.items():
            tools_str = ", ".join(tools) if tools else "No tools"
            actions_table.add_row(agent_name.replace("_", " ").title(), tools_str)
        
        console.print(actions_table)
    
    def _display_session_stats(self) -> None:
        """Display session statistics."""
        if not self.session_history:
            return
        
        successful_tasks = sum(1 for entry in self.session_history if entry["results"].get("success", False))
        failed_tasks = len(self.session_history) - successful_tasks
        
        stats_table = Table(title="Session Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Tasks", str(len(self.session_history)))
        stats_table.add_row("Successful", str(successful_tasks))
        stats_table.add_row("Failed", str(failed_tasks))
        
        if successful_tasks > 0:
            success_rate = (successful_tasks / len(self.session_history)) * 100
            stats_table.add_row("Success Rate", f"{success_rate:.1f}%")
        
        console.print(stats_table)
    
    def _display_detailed_results(self, results: Dict[str, Any]) -> None:
        """Display detailed results for a task."""
        details_text = Text()
        details_text.append("Task Results:\n\n", style="bold")
        details_text.append(f"Description: {results.get('task_description', 'N/A')}\n", style="white")
        details_text.append(f"Success: {results.get('success', False)}\n", style="green" if results.get("success") else "red")
        details_text.append(f"Messages: {results.get('message_count', 0)}\n", style="blue")
        details_text.append(f"Final Agent: {results.get('final_sender', 'N/A')}\n", style="cyan")
        
        if results.get("execution_time"):
            details_text.append(f"Execution Time: {results['execution_time']:.2f}s\n", style="yellow")
        
        if results.get("visit_counts"):
            details_text.append(f"Agent Visits: {results['visit_counts']}\n", style="magenta")
        
        if results.get("error"):
            details_text.append(f"Error: {results['error']}\n", style="red")
        
        console.print(Panel(details_text, title="Detailed Results", border_style="green"))
        
        # Offer to view message history
        if results.get("final_state") and Confirm.ask("View message history?"):
            self._display_message_history(results["final_state"])
    
    def _display_message_history(self, final_state: Dict[str, Any]) -> None:
        """Display message history from the final state."""
        if "messages" not in final_state:
            console.print("[yellow]No message history available[/yellow]")
            return
        
        messages = final_state["messages"]
        formatted_history = format_message_history(messages)
        
        console.print(Panel(
            Text(formatted_history, style="white"),
            title="Message History",
            border_style="blue"
        ))
    
    def _select_and_display_history_entry(self) -> None:
        """Allow user to select and view a specific history entry."""
        try:
            choices = [str(i) for i in range(1, len(self.session_history) + 1)]
            selection = Prompt.ask(
                "Select task number",
                choices=choices,
                default="1"
            )
            
            index = int(selection) - 1
            entry = self.session_history[index]
            
            console.print(f"[blue]Task: {entry['task']}[/blue]")
            self._display_detailed_results(entry["results"])
            
        except (ValueError, IndexError):
            console.print("[red]Invalid selection[/red]")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session.
        
        Returns:
            Session summary information
        """
        return {
            "total_tasks": len(self.session_history),
            "successful_tasks": sum(1 for entry in self.session_history if entry["results"].get("success", False)),
            "failed_tasks": sum(1 for entry in self.session_history if not entry["results"].get("success", False)),
            "settings": {
                "repo_path": str(self.settings.repo_path),
                "output_dir": str(self.settings.output_dir),
                "analyze_only": self.settings.analyze_only,
                "verbose": self.settings.verbose
            }
        }
    
    def export_session_report(self, output_path: Optional[Path] = None) -> str:
        """
        Export session report to a file.
        
        Args:
            output_path: Optional output path for the report
            
        Returns:
            Path to the exported report
        """
        if not output_path:
            output_path = self.settings.output_dir / "session_report.json"
        
        report_data = {
            "session_summary": self.get_session_summary(),
            "task_history": self.session_history,
            "workflow_status": self.workflow.get_workflow_status(),
            "export_timestamp": time.time()
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            console.print(f"[green]Session report exported to: {output_path}[/green]")
            return str(output_path)
            
        except Exception as e:
            console.print(f"[red]Failed to export session report: {e}[/red]")
            return ""
