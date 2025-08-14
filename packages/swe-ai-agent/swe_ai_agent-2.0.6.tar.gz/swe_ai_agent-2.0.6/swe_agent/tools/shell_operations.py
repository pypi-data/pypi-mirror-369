"""
Standalone Shell Operations
Provides shell execution, git operations, and workspace management without composio dependencies.
"""

import os
import subprocess
import threading
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ShellOperations:
    """Standalone shell operations class."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.command_history = []
        self.active_shells = {}
        self.shell_counter = 0
    
    def execute_command(self, command: str, timeout: int = 30, shell_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a shell command with timeout and capture output.
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
            shell_id: Optional shell ID for session management
            
        Returns:
            Dictionary with success, stdout, stderr, exit_code
        """
        try:
            # Show command to user and get approval via real-time interface
            try:
                from swe_agent.utils.progress_tracker import get_realtime_interface
                realtime_interface = get_realtime_interface()
                if not realtime_interface.log_shell_command(command):
                    return {
                        'success': False,
                        'stdout': '',
                        'stderr': 'Command cancelled by user',
                        'exit_code': -2,
                        'current_shell_pwd': str(self.repo_path)
                    }
            except:
                # Fallback if real-time interface not available
                pass
            
            # Add to command history
            self.command_history.append({
                'command': command,
                'timestamp': time.time(),
                'shell_id': shell_id or 'default'
            })
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.repo_path)
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode,
                'current_shell_pwd': str(self.repo_path)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'exit_code': -1,
                'current_shell_pwd': str(self.repo_path)
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'exit_code': -1,
                'current_shell_pwd': str(self.repo_path)
            }
    
    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent command history."""
        return self.command_history[-limit:]
    
    def clear_history(self) -> Dict[str, Any]:
        """Clear command history."""
        self.command_history.clear()
        return {'success': True, 'message': 'Command history cleared'}

class GitOperations:
    """Git operations wrapper."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.shell_ops = ShellOperations(repo_path)
    
    def git_status(self) -> Dict[str, Any]:
        """Get git repository status."""
        return self.shell_ops.execute_command("git status --porcelain")
    
    def git_diff(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get git diff for changes."""
        cmd = "git diff"
        if file_path:
            cmd += f" {file_path}"
        return self.shell_ops.execute_command(cmd)
    
    def git_add(self, file_path: str) -> Dict[str, Any]:
        """Add file to git staging area."""
        return self.shell_ops.execute_command(f"git add {file_path}")
    
    def git_commit(self, message: str) -> Dict[str, Any]:
        """Commit staged changes."""
        return self.shell_ops.execute_command(f'git commit -m "{message}"')
    
    def git_log(self, limit: int = 10) -> Dict[str, Any]:
        """Get git log."""
        return self.shell_ops.execute_command(f"git log --oneline -n {limit}")
    
    def git_branch(self) -> Dict[str, Any]:
        """Get current branch."""
        return self.shell_ops.execute_command("git branch --show-current")
    
    def git_remote(self) -> Dict[str, Any]:
        """Get remote information."""
        return self.shell_ops.execute_command("git remote -v")

class WorkspaceManager:
    """Workspace management operations."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.shell_ops = ShellOperations(repo_path)
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """Get comprehensive workspace information."""
        try:
            info = {
                'repository_path': str(self.repo_path),
                'exists': self.repo_path.exists(),
                'is_git_repo': (self.repo_path / '.git').exists(),
                'files': [],
                'directories': [],
                'size_mb': 0,
                'languages': {}
            }
            
            if info['exists']:
                # Get files and directories
                for item in self.repo_path.iterdir():
                    if item.is_file():
                        info['files'].append({
                            'name': item.name,
                            'size': item.stat().st_size,
                            'extension': item.suffix
                        })
                    elif item.is_dir() and not item.name.startswith('.'):
                        info['directories'].append(item.name)
                
                # Calculate total size
                total_size = sum(f.stat().st_size for f in self.repo_path.rglob('*') if f.is_file())
                info['size_mb'] = total_size / (1024 * 1024)
                
                # Language detection
                extensions = {}
                for file in info['files']:
                    ext = file['extension']
                    if ext:
                        extensions[ext] = extensions.get(ext, 0) + 1
                
                info['languages'] = extensions
            
            return {'success': True, 'workspace_info': info}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_files(self, pattern: str, file_type: str = "*") -> Dict[str, Any]:
        """Search for files matching a pattern."""
        cmd = f"find . -name '{file_type}' -type f | grep -i '{pattern}'"
        return self.shell_ops.execute_command(cmd)
    
    def get_directory_tree(self, max_depth: int = 3) -> Dict[str, Any]:
        """Get directory tree structure."""
        cmd = f"find . -maxdepth {max_depth} -type d | sort"
        return self.shell_ops.execute_command(cmd)

# Import Whoosh-based search to replace hardcoded patterns
try:
    from swe_agent.tools.intelligent_code_search import WhooshCodeSearch
    WHOOSH_AVAILABLE = True
except ImportError:
    try:
        # Try importing from parent directory
        from tools.intelligent_code_search import WhooshCodeSearch
        WHOOSH_AVAILABLE = True
    except ImportError:
        WHOOSH_AVAILABLE = False

class AdvancedCodeSearch:
    """Advanced code search capabilities using Whoosh full-text search."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.shell_ops = ShellOperations(repo_path)
        
        # Use Whoosh-based search if available, fallback to grep
        if WHOOSH_AVAILABLE:
            self.whoosh_search = WhooshCodeSearch(repo_path)
        else:
            self.whoosh_search = None
    
    def search_code(self, query: str, file_pattern: str = "*.py", context_lines: int = 3) -> Dict[str, Any]:
        """Search for code patterns with context using Whoosh or fallback to grep."""
        if self.whoosh_search:
            return self.whoosh_search.search_code(query, file_pattern, context_lines)
        else:
            # Fallback to grep
            cmd = f"grep -r -n -C {context_lines} --include='{file_pattern}' '{query}' ."
            return self.shell_ops.execute_command(cmd)
    
    def find_function_definitions(self, function_name: str, language: str = "python") -> Dict[str, Any]:
        """Find function definitions using Whoosh or fallback to grep."""
        if self.whoosh_search:
            return self.whoosh_search.find_function_definitions(function_name, language)
        else:
            # Fallback to hardcoded grep patterns
            if language == "python":
                cmd = f"grep -r -n 'def {function_name}' --include='*.py' ."
            elif language == "javascript":
                cmd = f"grep -r -n 'function {function_name}' --include='*.js' ."
            else:
                cmd = f"grep -r -n '{function_name}' --include='*.{language}' ."
            
            return self.shell_ops.execute_command(cmd)
    
    def find_class_definitions(self, class_name: str, language: str = "python") -> Dict[str, Any]:
        """Find class definitions using Whoosh or fallback to grep."""
        if self.whoosh_search:
            return self.whoosh_search.find_class_definitions(class_name, language)
        else:
            # Fallback to hardcoded grep patterns
            if language == "python":
                cmd = f"grep -r -n 'class {class_name}' --include='*.py' ."
            elif language == "javascript":
                cmd = f"grep -r -n 'class {class_name}' --include='*.js' ."
            else:
                cmd = f"grep -r -n '{class_name}' --include='*.{language}' ."
            
            return self.shell_ops.execute_command(cmd)
    
    def find_imports(self, module_name: str, language: str = "python") -> Dict[str, Any]:
        """Find import statements using Whoosh or fallback to grep."""
        if self.whoosh_search:
            return self.whoosh_search.find_imports(module_name, language)
        else:
            # Fallback to hardcoded grep patterns
            if language == "python":
                cmd = f"grep -r -n 'import {module_name}\\|from {module_name}' --include='*.py' ."
            elif language == "javascript":
                cmd = f"grep -r -n 'import.*{module_name}\\|require.*{module_name}' --include='*.js' ."
            else:
                cmd = f"grep -r -n '{module_name}' --include='*.{language}' ."
            
            return self.shell_ops.execute_command(cmd)