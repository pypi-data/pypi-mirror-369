#!/usr/bin/env python3
"""
SWE Agent - Headless Agentic IDE
Main entry point for the SWE Agent package
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# Add the package directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from .workflows.clean_swe_workflow import CleanSWEWorkflow
from .config.settings import Settings
from .cli.interface import SWEInterface
from .cli.pair_programming_interface import PairProgrammingInterface
from .cli.warp_interface import WarpInterface
from .utils.helpers import display_repository_info, display_help
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    """Main entry point for SWE Agent"""
    parser = argparse.ArgumentParser(
        description="SWE Agent - Headless Agentic IDE with comprehensive tool support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    swe-agent --interactive                 # Start interactive mode
    swe-agent --pair                        # Start pair programming interface (like Aider)
    swe-agent --task "create a calculator"  # Execute specific task
    swe-agent --help                        # Show this help message
    swe-agent --status                      # Show current workflow status
        """
    )
    
    # Command options
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode for continuous task input")
    parser.add_argument("--task", type=str, help="Execute a specific task")
    parser.add_argument("--status", action="store_true", help="Show current workflow status")
    parser.add_argument("--repo-path", type=str, default=".", help="Path to the repository to analyze (default: current directory)")
    parser.add_argument("--output-dir", type=str, default="output", help="Output directory for results (default: output)")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Set logging level (default: INFO)")
    parser.add_argument("--use-planner", action="store_true", help="Enable planner agent for complex task planning (default: disabled)")
    parser.add_argument("--enable-mcp", action="store_true", help="Enable MCP integration for DeepWiki and Semgrep servers (default: disabled)")
    parser.add_argument("--pair", action="store_true", help="Start pair programming interface (interactive with enhanced UI)")
    parser.add_argument("--warp", action="store_true", help="Start Warp-style AI terminal interface")
    parser.add_argument("--no-shell-approval", action="store_true", help="Disable shell command approval - agent will execute shell commands autonomously (default: requires approval)")
    parser.add_argument("--show-diffs", action="store_true", default=True, help="Enable diff visualization for file operations (shows before/after comparisons)")
    parser.add_argument("--debug-mode", action="store_true", help="Enable debug mode with variable dumps and detailed operation logs")
    
    args = parser.parse_args()
    
    # Set up configuration
    settings = Settings(
        repo_path=Path(args.repo_path),
        output_dir=Path(args.output_dir),
        verbose=(args.log_level == "DEBUG"),
        use_planner=args.use_planner,
        enable_mcp=args.enable_mcp
    )
    settings.no_shell_approval = getattr(args, 'no_shell_approval', False)
    
    try:
        # Show status
        if args.status:
            display_repository_info(settings.repo_path, settings.output_dir)
            return
        
        # Execute specific task
        if args.task:
            execute_single_task(args.task, settings, args.use_planner, args.enable_mcp, settings.no_shell_approval, args.show_diffs, args.debug_mode)
            return
        
        # Start pair programming interface
        if args.pair:
            start_pair_programming(settings, args.enable_mcp, settings.no_shell_approval, args.show_diffs, args.debug_mode)
            return
        
        # Start Warp interface
        if args.warp:
            start_warp_interface(settings, args.enable_mcp, settings.no_shell_approval, args.show_diffs, args.debug_mode)
            return
        
        # Start interactive mode
        if args.interactive:
            start_interactive_mode(settings, args.enable_mcp, settings.no_shell_approval, args.show_diffs, args.debug_mode)
            return
        
        # Default: show help
        display_help()
        parser.print_help()
        
    except KeyboardInterrupt:
        console.print("\n[!] SWE Agent interrupted by user", style="yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[X] Error: {str(e)}", style="red")
        sys.exit(1)


def execute_single_task(task: str, settings: Settings, use_planner: bool = False, enable_mcp: bool = False, no_shell_approval: bool = False, show_diffs: bool = True, debug_mode: bool = False):
    """Execute a single task"""
    console.print(Panel(f"Executing Task: {task}", title="SWE Agent", style="blue"))
    
    # Initialize workflow
    workflow = CleanSWEWorkflow(str(settings.repo_path), str(settings.output_dir), use_planner=use_planner, enable_mcp=enable_mcp, show_diffs=show_diffs, debug_mode=debug_mode)
    
    # Prepare initial state
    initial_state = {
        "messages": [],
        "sender": "user",
        "task": task
    }
    
    # Execute workflow
    result = workflow.run_workflow(task)
    
    # Display result
    if result.get("success", True):
        console.print(Panel("Task completed successfully", title="Result", style="green"))
    else:
        console.print(Panel(f"Task failed: {result.get('error', 'Unknown error')}", title="Result", style="red"))


def start_interactive_mode(settings: Settings, enable_mcp: bool = False, no_shell_approval: bool = False, show_diffs: bool = True, debug_mode: bool = False):
    """Start interactive CLI mode"""
    cli = SWEInterface(settings, enable_mcp, no_shell_approval, show_diffs, debug_mode)
    cli.start_interactive_mode()


def start_pair_programming(settings: Settings, enable_mcp: bool = False, no_shell_approval: bool = False, show_diffs: bool = True, debug_mode: bool = False):
    """Start pair programming interface"""
    interface = PairProgrammingInterface(str(settings.repo_path), str(settings.output_dir), enable_mcp, no_shell_approval, show_diffs, debug_mode)
    interface.run()


def start_warp_interface(settings: Settings, enable_mcp: bool = False, no_shell_approval: bool = False, show_diffs: bool = True, debug_mode: bool = False):
    """Start Warp-style AI terminal interface"""
    import asyncio
    interface = WarpInterface(str(settings.repo_path), str(settings.output_dir), enable_mcp, no_shell_approval, show_diffs, debug_mode)
    asyncio.run(interface.run())


if __name__ == "__main__":
    main()