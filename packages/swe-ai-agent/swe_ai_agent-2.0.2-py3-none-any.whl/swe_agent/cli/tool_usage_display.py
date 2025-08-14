"""
Tool Usage Display - CLI interface for displaying tool usage statistics
Provides rich console output for tool usage tracking and analysis.
"""

import logging
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text
from rich.align import Align
from tools.tool_usage_tracker import get_tool_tracker

logger = logging.getLogger(__name__)

class ToolUsageDisplay:
    """Rich console interface for displaying tool usage statistics."""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.tracker = get_tool_tracker()
    
    def display_agent_usage(self, agent_name: str) -> None:
        """Display tool usage for a specific agent."""
        usage = self.tracker.get_agent_usage_summary(agent_name)
        
        if usage['total_calls'] == 0:
            self.console.print(f"[yellow]No tool usage recorded for {agent_name}[/yellow]")
            return
        
        # Create agent summary table
        table = Table(title=f"[Agent] {agent_name.title()} Agent - Tool Usage", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Calls", str(usage['total_calls']))
        table.add_row("Success Rate", f"{usage['success_rate']:.1f}%")
        table.add_row("Total Duration", f"{usage['total_duration']:.2f}s")
        table.add_row("Avg Duration", f"{usage['avg_duration']:.2f}s")
        
        # Most used tools
        if usage['most_used_tools']:
            tools_text = ", ".join([f"{tool}: {count}" for tool, count in usage['most_used_tools'].items()])
            table.add_row("Top Tools", tools_text)
        
        self.console.print(table)
        
        # Recent activity
        if usage['recent_usage']:
            recent_table = Table(title="[Time] Recent Activity", show_header=True)
            recent_table.add_column("Tool", style="cyan")
            recent_table.add_column("Time", style="yellow")
            recent_table.add_column("Duration", style="white")
            recent_table.add_column("Status", style="green")
            
            for activity in usage['recent_usage']:
                status = "[OK]" if activity['success'] else "[ERR]"
                recent_table.add_row(
                    activity['tool'],
                    activity['time'],
                    activity['duration'],
                    status
                )
            
            self.console.print(recent_table)
    
    def display_overall_usage(self) -> None:
        """Display overall tool usage across all agents."""
        usage = self.tracker.get_overall_usage_summary()
        
        if usage['total_calls'] == 0:
            self.console.print("[yellow]No tool usage recorded yet[/yellow]")
            return
        
        # Header with overall stats
        header_table = Table(title="[Tools] Overall Tool Usage Statistics", show_header=True)
        header_table.add_column("Metric", style="cyan")
        header_table.add_column("Value", style="white")
        
        header_table.add_row("Total Calls", str(usage['total_calls']))
        header_table.add_row("Total Duration", f"{usage['total_duration']:.2f}s")
        header_table.add_row("Avg Duration", f"{usage['avg_duration']:.2f}s")
        header_table.add_row("Active Agents", str(usage['active_agents']))
        
        self.console.print(header_table)
        
        # Popular tools
        if usage['most_popular_tools']:
            tools_table = Table(title="[Popular] Most Popular Tools", show_header=True)
            tools_table.add_column("Tool", style="cyan")
            tools_table.add_column("Usage", style="white")
            
            for tool, count in usage['most_popular_tools'].items():
                tools_table.add_row(tool, str(count))
            
            self.console.print(tools_table)
        
        # Agent activity
        if usage['agent_activity']:
            agents_table = Table(title="👥 Agent Activity", show_header=True)
            agents_table.add_column("Agent", style="cyan")
            agents_table.add_column("Calls", style="white")
            agents_table.add_column("Success Rate", style="green")
            
            for agent, calls in usage['agent_activity'].items():
                agent_summary = self.tracker.get_agent_usage_summary(agent)
                agents_table.add_row(
                    agent,
                    str(calls),
                    f"{agent_summary['success_rate']:.1f}%"
                )
            
            self.console.print(agents_table)
        
        # Footer
        footer_text = Text("Use 'tools agent <name>' to see detailed agent usage", style="dim")
        self.console.print(Align.center(footer_text))
    
    def display_tool_details(self, tool_name: str) -> None:
        """Display detailed usage information for a specific tool."""
        usage = self.tracker.get_tool_usage_details(tool_name)
        
        if usage['usage_count'] == 0:
            self.console.print(f"[yellow]No usage recorded for tool: {tool_name}[/yellow]")
            return
        
        # Tool details table
        table = Table(title=f"[Tool] {tool_name} - Detailed Usage", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Usage Count", str(usage['usage_count']))
        table.add_row("Success Rate", f"{usage['success_rate']:.1f}%")
        table.add_row("Total Duration", f"{usage['total_duration']:.2f}s")
        table.add_row("Avg Duration", f"{usage['avg_duration']:.2f}s")
        
        # Agents using this tool
        if usage['agents_using']:
            agents_text = ", ".join([f"{agent}: {count}" for agent, count in usage['agents_using'].items()])
            table.add_row("Agents Using", agents_text)
        
        self.console.print(table)
        
        # Recent usage
        if usage['recent_usage']:
            recent_table = Table(title="[Time] Recent Usage", show_header=True)
            recent_table.add_column("Agent", style="cyan")
            recent_table.add_column("Time", style="yellow")
            recent_table.add_column("Duration", style="white")
            recent_table.add_column("Status", style="green")
            
            for activity in usage['recent_usage']:
                status = "[OK]" if activity['success'] else "[ERR]"
                recent_table.add_row(
                    activity['agent'],
                    activity['time'],
                    activity['duration'],
                    status
                )
            
            self.console.print(recent_table)
    
    def display_live_usage(self) -> None:
        """Display live tool usage updates."""
        self.console.print("[bold green][LIVE] Tool Usage Monitor[/bold green]")
        self.console.print("[dim]Press Ctrl+C to exit[/dim]")
        
        try:
            while True:
                usage = self.tracker.get_overall_usage_summary()
                
                # Clear and display updated stats
                self.console.clear()
                self.console.print(f"[bold]Live Stats - Total Calls: {usage['total_calls']}[/bold]")
                
                if usage['agent_activity']:
                    for agent, calls in usage['agent_activity'].items():
                        agent_summary = self.tracker.get_agent_usage_summary(agent)
                        recent = agent_summary['recent_usage'][-1] if agent_summary['recent_usage'] else None
                        
                        if recent:
                            self.console.print(f"[Agent] {agent}: {calls} calls (Last: {recent['tool']} at {recent['time']})")
                        else:
                            self.console.print(f"[Agent] {agent}: {calls} calls")
                
                import time
                time.sleep(2)  # Update every 2 seconds
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Live monitor stopped[/yellow]")
    
    def display_usage_report(self) -> None:
        """Display a comprehensive usage report."""
        report = self.tracker.format_usage_report()
        
        panel = Panel(
            report,
            title="[Tools] Tool Usage Report",
            border_style="blue",
            expand=False
        )
        
        self.console.print(panel)
    
    def clear_usage_history(self) -> None:
        """Clear all usage history."""
        self.tracker.clear_history()
        self.console.print("[green][OK] Tool usage history cleared[/green]")