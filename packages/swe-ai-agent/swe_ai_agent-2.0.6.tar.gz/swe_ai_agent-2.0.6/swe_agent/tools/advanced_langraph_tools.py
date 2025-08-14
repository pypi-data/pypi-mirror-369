"""
Advanced LangGraph Tool Wrappers with Shell, Git, and Enhanced Code Analysis
Integrates the uploaded tools into LangGraph callable functions.
"""

import logging
import os
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from langchain.tools import tool
from tools.file_operations import FileOperations
from tools.code_analysis import CodeAnalyzer
from tools.shell_operations import ShellOperations, GitOperations, WorkspaceManager
from tools.intelligent_code_search import FastCodeSearch
from tools.tool_usage_tracker import get_tool_tracker
from tools.security_scanner import scan_file_for_secrets, scan_directory_for_secrets, scan_recent_changes_for_secrets
from tools.web_scraper import scrape_website_content, scrape_documentation_site
from swe_agent.tools.tavily_search import search_web, search_web_news
# Direct MCP integration via langchain_mcp_adapters - no custom wrapper needed

logger = logging.getLogger(__name__)

class AdvancedLangGraphTools:
    """
    Advanced wrapper class that includes shell execution, git operations,
    and enhanced code analysis capabilities.
    """
    
    def __init__(self, repo_path: str, show_diffs: bool = True, debug_mode: bool = False):
        self.repo_path = Path(repo_path)
        self.file_ops = FileOperations(repo_path, show_diffs=show_diffs, debug_mode=debug_mode)
        self.code_analyzer = CodeAnalyzer(repo_path)
        self.shell_ops = ShellOperations(repo_path)
        self.git_ops = GitOperations(repo_path)
        self.workspace_manager = WorkspaceManager(repo_path)
        self.code_search = FastCodeSearch(repo_path)
        self.show_diffs = show_diffs
        self.debug_mode = debug_mode
        self._create_tools()
    
    def _create_tools(self):
        """Create advanced LangGraph tools."""
        file_ops = self.file_ops
        code_analyzer = self.code_analyzer
        shell_ops = self.shell_ops
        git_ops = self.git_ops
        workspace_manager = self.workspace_manager
        code_search = self.code_search
        repo_path = self.repo_path
        
        # Basic file operations (existing)
        @tool
        def create_file(filename: str, content: str) -> str:
            """
            Create a new file with the given content.
            
            Args:
                filename: Path to the file to create
                content: The complete content for the new file
                
            Example:
                create_file("hello.py", "print('Hello World')")
                
            Returns:
                Success message if file was created successfully
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "create_file", {"filename": filename})
            
            try:
                # Validate parameters explicitly
                if not filename:
                    error_msg = "[X] Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "create_file", False, error_msg)
                    return error_msg
                
                if content is None:
                    error_msg = "[X] Error: content parameter is required. Please provide the file content."
                    tracker.end_tool_call(call_id, "advanced_tools", "create_file", False, error_msg)
                    return error_msg
                
                # Show diff for new file creation if enabled
                if self.show_diffs and content:
                    from swe_agent.utils.diff_display import show_file_diff
                    from rich.console import Console
                    from rich.panel import Panel
                    
                    console = Console()
                    diff_output = show_file_diff("", content, filename)
                    console.print(f"\n[bold green]📋 File Changes: {filename}[/bold green]")
                    console.print(Panel(
                        diff_output,
                        title=f"[bold]Create: {filename}[/bold]",
                        border_style="green",
                        expand=False
                    ))
                    console.print()
                
                result = file_ops.create_file(filename, content)
                success = result["success"]
                response = f"[OK] Successfully created file: {filename}" if success else f"[X] Failed to create file: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "create_file", success, 
                                    result.get('error') if not success else None, 
                                    f"Created {filename}" if success else None)
                return response
            except Exception as e:
                error_msg = f"[X] Failed to create file {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "create_file", False, str(e))
                return error_msg
        
        @tool
        def create_new_file(filename: str, content: str = "") -> str:
            """
            Create a new file with the specified filename and optional content.
            
            Args:
                filename: Name/path for the new file (can include directories)
                content: Optional content for the file (defaults to empty string)
                
            Example:
                create_new_file("my_script.py", "print('Hello World')")
                create_new_file("docs/readme.md", "# My Project")
                create_new_file("config.json", "{}")
                
            Returns:
                Success message if file was created successfully
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "create_new_file", {"filename": filename, "content": content})
            
            try:
                # Validate parameters explicitly
                if not filename:
                    error_msg = "[X] Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "create_new_file", False, error_msg)
                    return error_msg
                
                # Content can be empty string by default
                if content is None:
                    content = ""
                
                result = file_ops.create_file(filename, content)
                success = result["success"]
                response = f"[OK] Successfully created new file: {filename}" if success else f"[X] Failed to create new file: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "create_new_file", success, 
                                    result.get('error') if not success else None, 
                                    f"Created new file {filename}" if success else None)
                return response
            except Exception as e:
                error_msg = f"[X] Failed to create new file {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "create_new_file", False, str(e))
                return error_msg
        
        @tool
        def write_complete_file(filename: str, content: str) -> str:
            """
            Write complete content to a file (creates new or completely overwrites existing).
            
            Args:
                filename: Path to the file to write (creates new or overwrites existing)
                content: Complete content to write to the file
                
            Examples:
                write_complete_file("new_app.py", "import os\nprint('Hello World')")
                write_complete_file("empty_config.json", "{}")
                write_complete_file("blank_file.txt", "")
                
            Returns:
                Success message if file was written successfully
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "write_complete_file", {"filename": filename, "content": content})
            
            try:
                # Validate parameters explicitly
                if not filename:
                    error_msg = "[X] Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "write_complete_file", False, error_msg)
                    return error_msg
                
                if content is None:
                    error_msg = "[X] Error: content parameter is required. Use empty string '' for blank files."
                    tracker.end_tool_call(call_id, "advanced_tools", "write_complete_file", False, error_msg)
                    return error_msg
                
                # Create or overwrite file with complete content
                result = file_ops.rewrite_file(filename, content)
                success = result["success"]
                
                if success:
                    file_status = "created" if not Path(filename).exists() else "overwritten"
                    response = f"[OK] Successfully wrote complete content to file: {filename} ({file_status})"
                else:
                    response = f"[X] Failed to write file: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "write_complete_file", success, 
                                    result.get('error') if not success else None, 
                                    f"Wrote complete content to {filename}" if success else None)
                return response
            except Exception as e:
                error_msg = f"[X] Failed to write complete file {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "write_complete_file", False, str(e))
                return error_msg
        
        @tool
        def search_in_file(filename: str, search_pattern: str, case_sensitive: bool = False) -> str:
            """
            Search for text patterns within a specific file and return matching lines with line numbers.
            
            Args:
                filename: Path to the file to search in
                search_pattern: Text pattern to search for (supports regex patterns)
                case_sensitive: Whether search should be case sensitive (default: False)
                
            Examples:
                search_in_file("app.py", "def main")
                search_in_file("config.json", '"port":', case_sensitive=True)
                search_in_file("README.md", "installation", case_sensitive=False)
                
            Returns:
                Matching lines with line numbers, or message if no matches found
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "search_in_file", {"filename": filename, "search_pattern": search_pattern, "case_sensitive": case_sensitive})
            
            try:
                import re
                from pathlib import Path
                
                # Validate parameters
                if not filename:
                    error_msg = "[X] Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", False, error_msg)
                    return error_msg
                
                if not search_pattern:
                    error_msg = "[X] Error: search_pattern parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", False, error_msg)
                    return error_msg
                
                file_path = Path(filename)
                if not file_path.exists():
                    error_msg = f"[X] Error: File '{filename}' does not exist"
                    tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", False, error_msg)
                    return error_msg
                
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    # Prepare regex pattern
                    flags = 0 if case_sensitive else re.IGNORECASE
                    pattern = re.compile(search_pattern, flags)
                    
                    matches = []
                    for line_num, line in enumerate(lines, 1):
                        if pattern.search(line):
                            matches.append(f"Line {line_num}: {line.rstrip()}")
                    
                    if matches:
                        result = f"[OK] Found {len(matches)} match(es) in '{filename}':\n" + "\n".join(matches)
                        success_msg = f"Found {len(matches)} matches for '{search_pattern}' in {filename}"
                    else:
                        result = f"[X] No matches found for pattern '{search_pattern}' in '{filename}'"
                        success_msg = f"No matches found for '{search_pattern}' in {filename}"
                    
                    tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", True, None, success_msg)
                    return result
                    
                except UnicodeDecodeError:
                    error_msg = f"[X] Error: Cannot read file '{filename}' - appears to be binary or has encoding issues"
                    tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", False, error_msg)
                    return error_msg
                    
            except Exception as e:
                error_msg = f"[X] Failed to search in file {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", False, str(e))
                return error_msg
        
        @tool
        def open_file(filename: str, line_number: int = 0, window_size: int = 50) -> str:
            """
            Open and read a file's content with smart defaults.
            
            Args:
                filename: Path to the file to open
                line_number: Starting line number (0 for beginning)
                window_size: Number of lines to read (50 default, -1 for entire file)
                
            Returns:
                File content with line numbers for easy reference
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "open_file", {"filename": filename, "line_number": line_number, "window_size": window_size})
            
            try:
                result = file_ops.open_file(filename, line_number, window_size)
                if result["success"]:
                    response = f"📄 File: {filename}\n{result['lines']}"
                    tracker.end_tool_call(call_id, "advanced_tools", "open_file", True, None, f"Opened {filename}")
                    return response
                else:
                    error_msg = result.get('error', 'Unknown error')
                    response = f"[X] Failed to open file: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "open_file", False, error_msg)
                    return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "open_file", False, str(e))
                raise
        
        @tool
        def edit_file(filename: str, new_content: str, line_number: int, num_lines: int = 1) -> str:
            """
            Edit a file by replacing content at specific lines.
            
            Args:
                filename: Path to the file to edit
                new_content: New content to insert
                line_number: Line number to start editing (1-based)
                num_lines: Number of lines to replace (default: 1)
                
            Returns:
                Success or error message
                
            Note: Consider using replace_in_file or rewrite_file for easier editing
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "edit_file", {"filename": filename, "line_number": line_number, "num_lines": num_lines})
            
            try:
                # Read original content for diff display
                target_path = repo_path / filename
                original_content = ""
                if target_path.exists():
                    with open(target_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                
                result = file_ops.edit_file(filename, new_content, line_number, num_lines)
                if result["success"]:
                    # Show diff after successful edit
                    if self.show_diffs:
                        try:
                            with open(target_path, 'r', encoding='utf-8') as f:
                                final_content = f.read()
                            
                            from swe_agent.utils.diff_display import show_file_diff
                            from rich.console import Console
                            from rich.panel import Panel
                            
                            console = Console()
                            diff_output = show_file_diff(original_content, final_content, filename)
                            console.print(f"\n[bold yellow]📋 File Changes: {filename}[/bold yellow]")
                            console.print(Panel(
                                diff_output,
                                title=f"[bold]Edit: {filename}[/bold]",
                                border_style="blue",
                                expand=False
                            ))
                            console.print()
                        except:
                            pass
                    
                    response = f"[OK] Successfully edited file: {filename}"
                    tracker.end_tool_call(call_id, "advanced_tools", "edit_file", True, None, f"Edited {filename}")
                    return response
                else:
                    error_msg = result.get('error', 'Unknown error')
                    response = f"[X] Failed to edit file: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "edit_file", False, error_msg)
                    return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "edit_file", False, str(e))
                raise
        
        @tool
        def replace_in_file(filename: str, old_text: str, new_text: str, max_replacements: int = -1) -> str:
            """Replace text in a file using find and replace."""
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "replace_in_file", {"filename": filename, "old_text": old_text, "new_text": new_text})
            
            try:
                target_path = repo_path / filename
                if not target_path.exists():
                    response = f"[X] File not found: {filename}"
                    tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, f"File not found: {filename}")
                    return response
                
                # Read file content
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Perform replacement
                if max_replacements == -1:
                    new_content = content.replace(old_text, new_text)
                    replacements = content.count(old_text)
                else:
                    new_content = content.replace(old_text, new_text, max_replacements)
                    replacements = min(content.count(old_text), max_replacements)
                
                if replacements == 0:
                    response = f"[X] Text '{old_text}' not found in {filename}"
                    tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, f"Text not found: {old_text}")
                    return response
                
                # Show diff before writing if enabled
                if self.show_diffs:
                    from swe_agent.utils.diff_display import show_file_diff
                    from rich.console import Console
                    from rich.panel import Panel
                    
                    console = Console()
                    diff_output = show_file_diff(content, new_content, filename)
                    console.print(f"\n[bold yellow]📋 File Changes: {filename}[/bold yellow]")
                    console.print(Panel(
                        diff_output,
                        title=f"[bold]Replace: {filename}[/bold]",
                        border_style="yellow",
                        expand=False
                    ))
                    console.print()
                
                # Write back to file
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                response = f"[OK] Successfully replaced {replacements} occurrence(s) of '{old_text}' with '{new_text}' in {filename}"
                tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", True, None, f"Replaced {replacements} occurrences in {filename}")
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, str(e))
                raise
        
        @tool
        def rewrite_file(filename: str, new_content: str) -> str:
            """
            Completely rewrite a file with new content.
            
            Args:
                filename: Path to the file to rewrite
                new_content: The complete new content for the file
                
            Example:
                rewrite_file("example.py", "print('Hello World')")
                
            Returns:
                Success message if file was rewritten successfully
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "rewrite_file", {"filename": filename})
            
            try:
                # Validate parameters explicitly
                if not filename:
                    error_msg = "[X] Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "rewrite_file", False, error_msg)
                    return error_msg
                
                if new_content is None:
                    error_msg = "[X] Error: new_content parameter is required. Please provide the complete file content."
                    tracker.end_tool_call(call_id, "advanced_tools", "rewrite_file", False, error_msg)
                    return error_msg
                
                target_path = repo_path / filename
                
                # Read original content for diff display
                original_content = ""
                if target_path.exists():
                    with open(target_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    # Create backup
                    backup_path = target_path.with_suffix(target_path.suffix + '.backup')
                    backup_path.write_text(original_content)
                
                # Show diff before writing if enabled
                if self.show_diffs:
                    from swe_agent.utils.diff_display import show_file_diff
                    from rich.console import Console
                    from rich.panel import Panel
                    
                    console = Console()
                    diff_output = show_file_diff(original_content, new_content, filename)
                    console.print(f"\n[bold yellow]📋 File Changes: {filename}[/bold yellow]")
                    console.print(Panel(
                        diff_output,
                        title=f"[bold]Rewrite: {filename}[/bold]",
                        border_style="red",
                        expand=False
                    ))
                    console.print()
                
                # Write new content
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                response = f"[OK] Successfully rewrote file: {filename}"
                tracker.end_tool_call(call_id, "advanced_tools", "rewrite_file", True, None, f"Rewrote {filename}")
                return response
            except Exception as e:
                error_msg = f"[X] Failed to rewrite file {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "rewrite_file", False, str(e))
                return error_msg
        
        @tool
        def list_files(directory: str = ".") -> str:
            """
            List files and directories in the specified directory.
            
            Args:
                directory: Directory path to list (default: current directory)
                
            Returns:
                Formatted list of files and directories with clear separation
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "list_files", {"directory": directory})
            
            try:
                result = file_ops.list_files(directory)
                if result["success"]:
                    files = result["files"]
                    if files and isinstance(files[0], dict):
                        files_str = "\n".join([f.get('name', str(f)) for f in files[:20]])
                    else:
                        files_str = "\n".join(files[:20])
                    
                    dirs = result["directories"]
                    if dirs and isinstance(dirs[0], dict):
                        dirs_str = "\n".join([d.get('name', str(d)) for d in dirs[:10]])
                    else:
                        dirs_str = "\n".join(dirs[:10])
                    
                    response = f"📁 Files:\n{files_str}\n\n📂 Directories:\n{dirs_str}"
                    tracker.end_tool_call(call_id, "advanced_tools", "list_files", True, None, f"Listed {directory}")
                    return response
                else:
                    error_msg = result.get('error', 'Unknown error')
                    response = f"[X] Failed to list files: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "list_files", False, error_msg)
                    return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "list_files", False, str(e))
                raise
        
        # Shell execution capabilities
        @tool
        def execute_shell_command(command: str, timeout: int = 30) -> str:
            """
            Execute a shell command with timeout.
            
            Args:
                command: Shell command to execute
                timeout: Timeout in seconds (default: 30)
                
            Returns:
                Command output and status
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "execute_shell_command", {"command": command, "timeout": timeout})
            
            try:
                result = shell_ops.execute_command(command, timeout)
                success = result['success']
                response = f"[OK] Command executed successfully:\n{result['stdout']}" if success else f"[X] Command failed (exit code {result['exit_code']}):\n{result['stderr']}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "execute_shell_command", success,
                                    result['stderr'] if not success else None,
                                    f"Executed: {command}" if success else None)
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "execute_shell_command", False, str(e))
                raise
        
        @tool
        def get_command_history() -> str:
            """
            Get the history of executed shell commands.
            
            Returns:
                Formatted list of recently executed commands with execution order
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "get_command_history", {})
            
            try:
                history = shell_ops.get_command_history()
                if not history:
                    response = "📜 No commands executed yet"
                else:
                    history_str = "\n".join([f"{i+1}. {cmd['command']}" for i, cmd in enumerate(history)])
                    response = f"📜 Recent command history:\n{history_str}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "get_command_history", True, None, f"Retrieved {len(history)} commands")
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "get_command_history", False, str(e))
                raise
        
        # Git operations
        @tool
        def git_status() -> str:
            """
            Get git repository status showing changes, staged files, and branch info.
            
            Returns:
                Git status information including modified files and staging area
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "git_status", {})
            
            try:
                result = git_ops.git_status()
                if result['success']:
                    if result['stdout'].strip():
                        response = f"🔄 Git status:\n{result['stdout']}"
                    else:
                        response = "[OK] Working directory clean"
                    tracker.end_tool_call(call_id, "advanced_tools", "git_status", True, None, "Retrieved git status")
                    return response
                else:
                    error_msg = result['stderr']
                    response = f"[X] Git status failed: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "git_status", False, error_msg)
                    return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "git_status", False, str(e))
                raise
        
        @tool
        def git_diff(file_path: str = None) -> str:
            """
            Get git diff for changes.
            
            Args:
                file_path: Specific file to diff (optional)
                
            Returns:
                Git diff output
            """
            result = git_ops.git_diff(file_path)
            if result['success']:
                if result['stdout'].strip():
                    return f"📝 Git diff:\n{result['stdout']}"
                else:
                    return "[OK] No changes to show"
            else:
                return f"[X] Git diff failed: {result['stderr']}"
        
        @tool
        def git_add(file_path: str) -> str:
            """
            Add file to git staging area.
            
            Args:
                file_path: Path to file to add
                
            Returns:
                Git add result
            """
            result = git_ops.git_add(file_path)
            if result['success']:
                return f"[OK] Added {file_path} to git staging area"
            else:
                return f"[X] Git add failed: {result['stderr']}"
        
        @tool
        def git_commit(message: str) -> str:
            """
            Commit staged changes.
            
            Args:
                message: Commit message
                
            Returns:
                Git commit result
            """
            result = git_ops.git_commit(message)
            if result['success']:
                return f"[OK] Committed changes: {message}"
            else:
                return f"[X] Git commit failed: {result['stderr']}"
        
        # Enhanced code analysis
        @tool
        def analyze_file_advanced(filename: str) -> str:
            """
            Advanced file analysis with detailed structure information.
            
            Args:
                filename: Path to the file to analyze
                
            Returns:
                Comprehensive analysis including language, structure, and components
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "analyze_file_advanced", {"filename": filename})
            
            try:
                result = code_analyzer.analyze_file(filename)
                if result["success"]:
                    response = f"""[?] Advanced Analysis: {filename}

Language: {result['language']}
Lines: {result['line_count']}
Functions: {len(result['functions'])}
Classes: {len(result['classes'])}
Imports: {len(result['imports'])}

[*] Functions:
{chr(10).join([f"  - {f['name']} (line {f['line_start']})" for f in result['functions'][:10]])}

[P] Classes:
{chr(10).join([f"  - {c['name']} (lines {c['line_start']}-{c['line_end']})" for c in result['classes'][:10]])}

📦 Imports:
{chr(10).join([f"  - {imp}" for imp in result['imports'][:10]])}"""
                    tracker.end_tool_call(call_id, "advanced_tools", "analyze_file_advanced", True, None, f"Analyzed {filename}")
                    return response
                else:
                    error_msg = result.get('error', 'Unknown error')
                    response = f"[X] Analysis failed: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "analyze_file_advanced", False, error_msg)
                    return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "analyze_file_advanced", False, str(e))
                raise
        
        @tool
        def search_code_semantic(query: str, file_pattern: str = "*.py") -> str:
            """
            Semantic code search using pattern matching across files.
            
            Args:
                query: Search query (can be function names, class names, or code patterns)
                file_pattern: File pattern to search in (default: *.py for Python files)
                
            Returns:
                Search results with file paths and line numbers
                
            Examples:
                - search_code_semantic("def create_file") - finds function definitions
                - search_code_semantic("class Agent", "*.py") - finds class definitions
                - search_code_semantic("import langchain", "*") - finds imports
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "search_code_semantic", {"query": query, "file_pattern": file_pattern})
            
            try:
                # Use memory-mapped FastCodeSearch for optimized performance
                results = code_search.search(query, max_results=20)
                if results:
                    formatted_results = []
                    for result in results:
                        formatted_results.append(f"📄 {result.file_path}:{result.line_number} - {result.line_content[:80]}...")
                    response = f"[?] Found {len(results)} matches for '{query}':\n" + "\n".join(formatted_results)
                    tracker.end_tool_call(call_id, "advanced_tools", "search_code_semantic", True, None, f"Found {len(results)} matches for '{query}'")
                else:
                    response = f"[?] No matches found for '{query}'"
                    tracker.end_tool_call(call_id, "advanced_tools", "search_code_semantic", True, None, f"No matches for '{query}'")
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "search_code_semantic", False, str(e))
                raise
        
        @tool
        def get_workspace_info() -> str:
            """
            Get comprehensive workspace information including files, directories, and project structure.
            
            Returns:
                Detailed workspace overview with file counts, types, and recent files
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "get_workspace_info", {})
            
            try:
                result = workspace_manager.get_workspace_info()
                if result['success']:
                    info = result['workspace_info']
                    branch_result = git_ops.git_branch()
                    branch = branch_result['stdout'].strip() if branch_result['success'] else 'Not a git repository'
                    
                    response = f"""🏢 Workspace Information:

📁 Repository: {info['repository_path']}
🌿 Git Branch: {branch}
📊 Total Files: {len(info['files'])}
📂 Directories: {len(info['directories'])}
💾 Size: {info['size_mb']:.2f} MB

🗂️ File Types:
{chr(10).join([f"  - {ext}: {count}" for ext, count in info['languages'].items()])}

📁 Recent Files:
{chr(10).join([f"  - {f['name']}" for f in info['files'][:10]])}"""
                    tracker.end_tool_call(call_id, "advanced_tools", "get_workspace_info", True, None, "Retrieved workspace info")
                    return response
                else:
                    error_msg = result['error']
                    response = f"[X] Workspace info error: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "get_workspace_info", False, error_msg)
                    return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "get_workspace_info", False, str(e))
                raise
        
        # Advanced code search tools
        @tool
        def find_function_definitions(function_name: str, language: str = "python") -> str:
            """
            Find function definitions across the codebase with file locations.
            
            Args:
                function_name: Name of the function to find (exact match or partial)
                language: Programming language (default: python, also supports: javascript, java, etc.)
                
            Returns:
                Function definition locations with file paths and line numbers
                
            Examples:
                - find_function_definitions("create_file") - finds create_file function
                - find_function_definitions("analyze", "python") - finds analyze functions
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "find_function_definitions", {"function_name": function_name, "language": language})
            
            try:
                # Use memory-mapped FastCodeSearch for optimized function search
                results = code_search.search_functions(function_name)
                if results:
                    formatted_results = []
                    for result in results:
                        formatted_results.append(f"[*] {result.file_path}:{result.line_number} - {result.line_content[:80]}...")
                    response = f"[?] Found {len(results)} function definitions for '{function_name}':\n" + "\n".join(formatted_results)
                    tracker.end_tool_call(call_id, "advanced_tools", "find_function_definitions", True, None, f"Found {len(results)} '{function_name}' functions")
                else:
                    response = f"[?] No function definitions found for '{function_name}'"
                    tracker.end_tool_call(call_id, "advanced_tools", "find_function_definitions", True, None, f"No '{function_name}' functions found")
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "find_function_definitions", False, str(e))
                raise
        
        @tool
        def find_class_definitions(class_name: str, language: str = "python") -> str:
            """
            Find class definitions across the codebase with inheritance info.
            
            Args:
                class_name: Name of the class to find (exact match or partial)
                language: Programming language (default: python, also supports: javascript, java, etc.)
                
            Returns:
                Class definition locations with file paths and line numbers
                
            Examples:
                - find_class_definitions("Agent") - finds Agent classes
                - find_class_definitions("Workflow", "python") - finds Workflow classes
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "find_class_definitions", {"class_name": class_name, "language": language})
            
            try:
                # Use memory-mapped FastCodeSearch for optimized class search  
                results = code_search.search(f"class {class_name}", max_results=20)
                if results:
                    formatted_results = []
                    for result in results:
                        formatted_results.append(f"🏗️ {result.file_path}:{result.line_number} - {result.line_content[:80]}...")
                    response = f"[?] Found {len(results)} class definitions for '{class_name}':\n" + "\n".join(formatted_results)
                    tracker.end_tool_call(call_id, "advanced_tools", "find_class_definitions", True, None, f"Found {len(results)} '{class_name}' classes")
                else:
                    response = f"[?] No class definitions found for '{class_name}'"
                    tracker.end_tool_call(call_id, "advanced_tools", "find_class_definitions", True, None, f"No '{class_name}' classes found")
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "find_class_definitions", False, str(e))
                raise
        
        @tool
        def find_imports(module_name: str, language: str = "python") -> str:
            """
            Find import statements across the codebase.
            
            Args:
                module_name: Name of the module to find imports for
                language: Programming language (default: python)
                
            Returns:
                Import statement locations
            """
            result = code_search.find_imports(module_name, language)
            if result['success']:
                if result['stdout'].strip():
                    return f"[?] Found imports for '{module_name}':\n{result['stdout']}"
                else:
                    return f"[?] No imports found for '{module_name}'"
            else:
                return f"[X] Search error: {result['stderr']}"
        
        @tool
        def get_directory_tree(max_depth: int = 3) -> str:
            """
            Get directory tree structure.
            
            Args:
                max_depth: Maximum depth to traverse (default: 3)
                
            Returns:
                Directory tree structure
            """
            result = workspace_manager.get_directory_tree(max_depth)
            if result['success']:
                return f"🌳 Directory tree:\n{result['stdout']}"
            else:
                return f"[X] Directory tree error: {result['stderr']}"
        
        @tool
        def search_files_by_name(pattern: str, file_type: str = "*") -> str:
            """
            Search for files by name pattern.
            
            Args:
                pattern: Pattern to search for in file names
                file_type: File type filter (default: all files)
                
            Returns:
                Matching file paths
            """
            result = workspace_manager.search_files(pattern, file_type)
            if result['success']:
                if result['stdout'].strip():
                    return f"[?] Found files matching '{pattern}':\n{result['stdout']}"
                else:
                    return f"[?] No files found matching '{pattern}'"
            else:
                return f"[X] File search error: {result['stderr']}"
        
        # Security scanning tools
        @tool
        def scan_file_security(filename: str) -> str:
            """
            Scan a specific file for potential secrets and security vulnerabilities.
            
            Args:
                filename: Path to the file to scan for secrets
                
            Returns:
                Security scan results showing potential secrets found
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "scan_file_security", {"filename": filename})
            
            try:
                result = scan_file_for_secrets(filename)
                success = result["success"]
                
                if success:
                    secrets_count = result["secrets_found"]
                    if secrets_count > 0:
                        response = f"🔒 Security scan of {filename}: {secrets_count} potential secrets found!\n"
                        response += "⚠️  Please review and remove any sensitive information before committing."
                    else:
                        response = f"[OK] Security scan of {filename}: No secrets detected"
                else:
                    response = f"[X] Security scan failed: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "scan_file_security", success, 
                                    result.get('error') if not success else None, 
                                    f"Scanned {filename} for secrets" if success else None)
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "scan_file_security", False, str(e))
                raise
        
        @tool
        def scan_directory_security(directory_path: str = ".", max_files: int = 50) -> str:
            """
            Scan all files in a directory for potential secrets and security vulnerabilities.
            
            Args:
                directory_path: Path to the directory to scan (default: current directory)
                max_files: Maximum number of files to scan (default: 50)
                
            Returns:
                Comprehensive security scan results for all files in directory
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "scan_directory_security", {"directory_path": directory_path})
            
            try:
                result = scan_directory_for_secrets(directory_path, max_files)
                success = result["success"]
                
                if success:
                    files_scanned = result["files_scanned"]
                    total_secrets = result["total_secrets"]
                    files_with_secrets = result["files_with_secrets"]
                    
                    response = f"🔒 Security scan of {directory_path}: {files_scanned} files scanned\n"
                    if total_secrets > 0:
                        response += f"⚠️  {total_secrets} potential secrets found in {files_with_secrets} files!\n"
                        response += "Please review and remove any sensitive information before committing."
                    else:
                        response += "[OK] No secrets detected in any files"
                else:
                    response = f"[X] Security scan failed: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "scan_directory_security", success, 
                                    result.get('error') if not success else None, 
                                    f"Scanned {directory_path} for secrets" if success else None)
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "scan_directory_security", False, str(e))
                raise
        
        @tool
        def scan_recent_changes_security() -> str:
            """
            Scan recently modified files for potential secrets and security vulnerabilities.
            
            Returns:
                Security scan results for recently modified files
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "scan_recent_changes_security", {})
            
            try:
                result = scan_recent_changes_for_secrets()
                success = result["success"]
                
                if success:
                    files_scanned = result["files_scanned"]
                    total_secrets = result["total_secrets"]
                    
                    response = f"🔒 Security scan of recent changes: {files_scanned} files scanned\n"
                    if total_secrets > 0:
                        response += f"⚠️  {total_secrets} potential secrets found in recent changes!\n"
                        response += "Please review and remove any sensitive information before committing."
                    else:
                        response += "[OK] No secrets detected in recent changes"
                else:
                    response = f"[X] Security scan failed: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "scan_recent_changes_security", success, 
                                    result.get('error') if not success else None, 
                                    "Scanned recent changes for secrets" if success else None)
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "scan_recent_changes_security", False, str(e))
                raise
        
        # Web scraping tools
        @tool
        def scrape_website(url: str, extract_links: bool = False) -> str:
            """
            Scrape content from a website URL. Optimized for documentation.
            
            Args:
                url: The website URL to scrape
                extract_links: Whether to include related documentation links (default: False)
                
            Returns:
                Formatted text content from the website
                
            Examples:
                - scrape_website("https://docs.python.org/3/") - scrape Python docs
                - scrape_website("https://api.github.com", True) - scrape with links
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "scrape_website", {"url": url, "extract_links": extract_links})
            
            try:
                if not url:
                    error_msg = "[X] Error: url parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "scrape_website", False, error_msg)
                    return error_msg
                
                result = scrape_website_content(url, extract_links)
                tracker.end_tool_call(call_id, "advanced_tools", "scrape_website", True, None, f"Scraped content from {url}")
                return result
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "scrape_website", False, str(e))
                raise
        
        @tool  
        def scrape_documentation(base_url: str, max_pages: int = 5) -> str:
            """
            Scrape a documentation site by following internal links.
            
            Args:
                base_url: The base URL of the documentation site
                max_pages: Maximum number of pages to scrape (default: 5)
                
            Returns:
                Combined content from multiple documentation pages
                
            Examples:
                - scrape_documentation("https://docs.python.org/3/") - scrape Python docs
                - scrape_documentation("https://fastapi.tiangolo.com/", 3) - scrape FastAPI docs
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "scrape_documentation", {"base_url": base_url, "max_pages": max_pages})
            
            try:
                if not base_url:
                    error_msg = "[X] Error: base_url parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "scrape_documentation", False, error_msg)
                    return error_msg
                
                result = scrape_documentation_site(base_url, max_pages)
                tracker.end_tool_call(call_id, "advanced_tools", "scrape_documentation", True, None, f"Scraped {max_pages} pages from {base_url}")
                return result
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "scrape_documentation", False, str(e))
                raise

        @tool
        def search_web_tavily(query: str, max_results: int = 5) -> str:
            """
            Search the web using Tavily's intelligent search API for comprehensive results.
            
            Args:
                query: The search query string (e.g., "Who is Leo Messi?", "Latest AI developments")
                max_results: Maximum number of search results to return (default: 5, max: 10)
                
            Returns:
                Formatted search results with AI-generated summary and source links
                
            Example:
                search_web_tavily("Leo Messi career highlights", 5)
                
            Note: Requires TAVILY_API_KEY environment variable. Get API key from https://tavily.com
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "search_web_tavily", {"query": query, "max_results": max_results})
            
            try:
                result = search_web(query, max_results)
                
                if "error" in result:
                    tracker.end_tool_call(call_id, success=False, error_message=result["error"], result_summary="Web search failed - API key required")
                    return f"❌ Web Search Error: {result['error']}\n\n📋 Setup: {result.get('setup_instructions', 'Check TAVILY_API_KEY environment variable')}"
                
                # Format results for display
                formatted_output = f"🌐 Web Search Results for: {query}\n\n"
                formatted_output += f"📊 AI Summary: {result['summary']}\n\n"
                formatted_output += f"🔍 Found {result['total_results']} results:\n\n"
                
                for i, item in enumerate(result['results'], 1):
                    formatted_output += f"{i}. **{item['title']}**\n"
                    formatted_output += f"   🔗 {item['url']}\n"
                    formatted_output += f"   📝 {item['content'][:200]}...\n"
                    if item.get('score'):
                        formatted_output += f"   ⭐ Relevance: {item['score']:.2f}\n"
                    formatted_output += "\n"
                
                # Add metadata
                if result.get('search_metadata'):
                    metadata = result['search_metadata']
                    formatted_output += f"⏱️ Search time: {metadata.get('query_time', 'unknown')}\n"
                    formatted_output += f"🔍 Search depth: {metadata.get('search_depth', 'unknown')}\n"
                
                tracker.end_tool_call(call_id, success=True, error_message="", result_summary=f"Found {result['total_results']} web search results")
                return formatted_output
                
            except Exception as e:
                tracker.end_tool_call(call_id, success=False, error_message=str(e), result_summary="Web search failed")
                return f"❌ Error during web search: {str(e)}"

        @tool
        def search_web_news_tavily(query: str, max_results: int = 5) -> str:
            """
            Search for recent news and current events using Tavily's news search capabilities.
            
            Args:
                query: The news search query (e.g., "AI latest developments", "tech news today")
                max_results: Maximum number of news articles to return (default: 5, max: 10)
                
            Returns:
                Formatted news results with recent articles and news summary
                
            Example:
                search_web_news_tavily("AI breakthroughs 2025", 3)
                
            Note: Requires TAVILY_API_KEY environment variable. Focuses on recent news and current events.
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "search_web_news_tavily", {"query": query, "max_results": max_results})
            
            try:
                result = search_web_news(query, max_results)
                
                if "error" in result:
                    tracker.end_tool_call(call_id, success=False, error_message=result["error"], result_summary="News search failed - API key required")
                    return f"❌ News Search Error: {result['error']}\n\n📋 Setup: Get API key from https://tavily.com and set TAVILY_API_KEY"
                
                # Format news results
                formatted_output = f"📰 Latest News for: {query}\n\n"
                formatted_output += f"📊 News Summary: {result['news_summary']}\n\n"
                formatted_output += f"🗞️ Found {result['total_articles']} recent articles:\n\n"
                
                for i, article in enumerate(result['articles'], 1):
                    formatted_output += f"{i}. **{article.get('title', 'No title')}**\n"
                    formatted_output += f"   🔗 {article.get('url', 'No URL')}\n"
                    formatted_output += f"   📝 {article.get('content', 'No content')[:200]}...\n"
                    if article.get('published_date'):
                        formatted_output += f"   📅 Published: {article['published_date']}\n"
                    if article.get('score'):
                        formatted_output += f"   ⭐ Relevance: {article['score']:.2f}\n"
                    formatted_output += "\n"
                
                tracker.end_tool_call(call_id, success=True, error_message="", result_summary=f"Found {result['total_articles']} news articles")
                return formatted_output
                
            except Exception as e:
                tracker.end_tool_call(call_id, success=False, error_message=str(e), result_summary="News search failed")
                return f"❌ Error during news search: {str(e)}"
        
# MCP tools are integrated directly via langchain_mcp_adapters - no management wrapper needed
        
        # Store tools as instance attributes
        self.create_file = create_file
        self.create_new_file = create_new_file
        self.write_complete_file = write_complete_file
        self.search_in_file = search_in_file
        self.open_file = open_file
        self.edit_file = edit_file
        self.replace_in_file = replace_in_file
        self.rewrite_file = rewrite_file
        self.list_files = list_files
        self.execute_shell_command = execute_shell_command
        self.get_command_history = get_command_history
        self.git_status = git_status
        self.git_diff = git_diff
        self.git_add = git_add
        self.git_commit = git_commit
        self.analyze_file_advanced = analyze_file_advanced
        self.search_code_semantic = search_code_semantic
        self.get_workspace_info = get_workspace_info
        self.find_function_definitions = find_function_definitions
        self.find_class_definitions = find_class_definitions
        self.find_imports = find_imports
        self.get_directory_tree = get_directory_tree
        self.search_files_by_name = search_files_by_name
        self.scan_file_security = scan_file_security
        self.scan_directory_security = scan_directory_security
        self.scan_recent_changes_security = scan_recent_changes_security
        self.scrape_website = scrape_website
        self.scrape_documentation = scrape_documentation
        self.search_web_tavily = search_web_tavily
        self.search_web_news_tavily = search_web_news_tavily
        
        # Netlify deployment tool for HTML/CSS/JS applications
        try:
            from .netlify_deploy import netlify_deploy_tool
            self.deploy_to_netlify = netlify_deploy_tool
        except ImportError:
            print("Warning: Netlify deployment tool not available")
            
            @tool
            def netlify_not_available(project_path: str, site_name: str = None) -> str:
                return "❌ Netlify deployment not available. Please install netlify-python library."
            
            self.deploy_to_netlify = netlify_not_available
        
        # Vision Analysis Tools for Website Screenshots
        try:
            from .pure_vision_analyzer import extract_website_info, get_component_list, get_color_palette, get_layout_info
            
            @tool
            def analyze_website_screenshot(image_path: str, context: str = "") -> str:
                """
                Analyze a website screenshot to extract design information for building similar websites.
                Use this when user provides a website screenshot or asks to recreate a website from an image.
                
                Args:
                    image_path: Path to the website screenshot image file
                    context: Optional context about the website (e.g., "e-commerce site", "dashboard")
                    
                Returns:
                    Structured analysis data including layout, components, colors, and design patterns
                """
                tracker = get_tool_tracker()
                call_id = tracker.start_tool_call("vision_tools", "analyze_website_screenshot", {"image_path": image_path})
                
                try:
                    analysis = extract_website_info(image_path, context)
                    if analysis["success"]:
                        data = analysis["analysis"]
                        
                        # Format analysis for SWE Agent
                        result = f"✅ Website Screenshot Analysis - {image_path}\n"
                        result += "=" * 60 + "\n\n"
                        
                        # Layout structure
                        layout = data.get("layout", {})
                        if layout:
                            result += "📐 LAYOUT STRUCTURE:\n"
                            for key, value in layout.items():
                                result += f"  • {key.replace('_', ' ').title()}: {value[:80]}...\n"
                            result += "\n"
                        
                        # Components found
                        components = data.get("components_observed", [])
                        if components:
                            result += f"🧩 COMPONENTS IDENTIFIED ({len(components)}):\n"
                            for i, comp in enumerate(components, 1):
                                comp_type = comp.get("type", "unknown").upper()
                                desc = comp.get("description", "")[:60]
                                location = comp.get("location", "unspecified")
                                result += f"  {i}. {comp_type} - {desc} ({location})\n"
                            result += "\n"
                        
                        # Visual elements
                        visual = data.get("visual_elements", {})
                        colors = visual.get("color_palette", [])
                        if colors:
                            result += f"🎨 COLOR PALETTE ({len(colors)} colors):\n"
                            result += f"  {', '.join(colors)}\n\n"
                        
                        # Design style
                        style = visual.get("design_style", "")
                        if style:
                            result += f"🎭 DESIGN STYLE: {style}\n\n"
                        
                        # Interactive elements
                        interactive = data.get("interactive_elements", [])
                        if interactive:
                            result += f"⚡ INTERACTIVE ELEMENTS ({len(interactive)}):\n"
                            for elem in interactive[:5]:  # Show first 5
                                elem_type = elem.get("element_type", "unknown")
                                purpose = elem.get("likely_purpose", "")[:50]
                                result += f"  • {elem_type}: {purpose}\n"
                            result += "\n"
                        
                        # Technical observations
                        tech = data.get("technical_observations", {})
                        complexity = tech.get("complexity_assessment", "unknown")
                        result += f"🔧 COMPLEXITY LEVEL: {complexity}\n\n"
                        
                        result += "💡 USE THIS DATA TO:\n"
                        result += "  • Plan HTML structure based on components\n"
                        result += "  • Create CSS using the color palette\n"
                        result += "  • Implement layout matching the structure\n"
                        result += "  • Add interactive functionality as needed\n"
                        
                        tracker.end_tool_call(call_id, True, {"components": len(components), "colors": len(colors)})
                        return result
                    else:
                        error_msg = f"❌ Vision analysis failed: {analysis.get('error', 'Unknown error')}"
                        tracker.end_tool_call(call_id, False, {"error": analysis.get('error')})
                        return error_msg
                        
                except Exception as e:
                    error_msg = f"❌ Vision tool error: {str(e)}"
                    tracker.end_tool_call(call_id, False, {"error": str(e)})
                    return error_msg
            
            self.analyze_website_screenshot = analyze_website_screenshot
            vision_tools_available = True
            print("✅ Vision analysis tool loaded successfully")
            
        except ImportError as e:
            logger.warning(f"Vision tools not available: {e}")
            print(f"❌ Vision tools import failed: {e}")
            
            @tool
            def vision_not_available(image_path: str, context: str = "") -> str:
                return f"❌ Vision analysis not available for {image_path}. Please check pure_vision_analyzer installation."
            
            self.analyze_website_screenshot = vision_not_available
            vision_tools_available = False

        # Julia Browser tools for comprehensive web browsing
        try:
            from .julia_browser_tools import (
                open_website, list_elements, click_element, type_text, 
                submit_form, follow_link, get_page_info, search_page,
                scroll_down, scroll_up, scroll_to_top, scroll_to_bottom, get_scroll_info
            )
            self.open_website = open_website
            self.list_elements = list_elements
            self.click_element = click_element
            self.type_text = type_text
            self.submit_form = submit_form
            self.follow_link = follow_link
            self.get_page_info = get_page_info
            self.search_page = search_page
            self.scroll_down = scroll_down
            self.scroll_up = scroll_up
            self.scroll_to_top = scroll_to_top
            self.scroll_to_bottom = scroll_to_bottom
            self.get_scroll_info = get_scroll_info
        except ImportError:
            print("Warning: Julia Browser tools not available")
            
            @tool
            def browser_not_available(action: str) -> str:
                return f"❌ Browser tools not available for action: {action}. Please check julia-browser installation."
            
            self.open_website = browser_not_available
            self.list_elements = browser_not_available
            self.click_element = browser_not_available
            self.type_text = browser_not_available
            self.submit_form = browser_not_available
            self.follow_link = browser_not_available
            self.get_page_info = browser_not_available
            self.search_page = browser_not_available
            self.scroll_down = browser_not_available
            self.scroll_up = browser_not_available
            self.scroll_to_top = browser_not_available
            self.scroll_to_bottom = browser_not_available
            self.get_scroll_info = browser_not_available
    
    def get_all_tools(self) -> List:
        """Get all available tools."""
        return [
            self.create_file,
            self.create_new_file,
            self.write_complete_file,
            self.search_in_file,
            self.open_file,
            self.edit_file,
            self.replace_in_file,
            self.rewrite_file,
            self.list_files,
            self.execute_shell_command,
            self.get_command_history,
            self.git_status,
            self.git_diff,
            self.git_add,
            self.git_commit,
            self.analyze_file_advanced,
            self.search_code_semantic,
            self.get_workspace_info,
            self.find_function_definitions,
            self.find_class_definitions,
            self.find_imports,
            self.get_directory_tree,
            self.search_files_by_name,
            self.scan_file_security,
            self.scan_directory_security,
            self.scan_recent_changes_security,
            self.scrape_website,
            self.scrape_documentation,
            self.search_web_tavily,
            self.search_web_news_tavily,
            # Netlify deployment tool
            self.deploy_to_netlify,
            # Vision Analysis tools
            self.analyze_website_screenshot,
            # Julia Browser tools
            self.open_website,
            self.list_elements,
            self.click_element,
            self.type_text,
            self.submit_form,
            self.follow_link,
            self.get_page_info,
            self.search_page,
            self.scroll_down,
            self.scroll_up,
            self.scroll_to_top,
            self.scroll_to_bottom,
            self.get_scroll_info
        ]