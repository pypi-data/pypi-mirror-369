"""
SWE Agent SDK Client - Main interface for external integrations
"""

import asyncio
import json
import logging
import os
import subprocess
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Union

from .exceptions import (
    SWEAgentException,
    TaskExecutionException,
    ConnectionException,
    ValidationException,
    TimeoutException
)
from .models import (
    TaskRequest,
    TaskResponse,
    TaskStatus,
    AgentStatus,
    AgentType,
    FileContext,
    GitStatus,
    ToolUsageStats,
    WorkflowResult
)


class SWEAgentClient:
    """
    Main client for interacting with the SWE Agent system
    
    This client provides a high-level interface for IDE integrations and external tools
    to interact with the SWE Agent. It handles task execution, status monitoring,
    and result retrieval.
    """
    
    def __init__(self, 
                 working_directory: str = ".",
                 log_level: str = "INFO",
                 timeout: int = 300,
                 max_retries: int = 3):
        """
        Initialize the SWE Agent client
        
        Args:
            working_directory: Base directory for agent operations
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            timeout: Default timeout for tasks in seconds
            max_retries: Maximum number of retry attempts
        """
        self.working_directory = Path(working_directory).resolve()
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = self._setup_logging(log_level)
        
        # Task tracking
        self.active_tasks: Dict[str, TaskResponse] = {}
        self.task_history: List[TaskResponse] = []
        
        # Agent status
        self._agent_status = AgentStatus(
            is_running=False,
            agents_available=[AgentType.SOFTWARE_ENGINEER, AgentType.CODE_ANALYZER, AgentType.EDITOR]
        )
        
        # Event callbacks
        self.task_callbacks: Dict[str, Callable] = {}
        
        self.logger.info(f"SWE Agent Client initialized with working directory: {self.working_directory}")
    
    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("swe_agent_sdk")
        logger.setLevel(getattr(logging, log_level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def execute_task(self, request: TaskRequest) -> TaskResponse:
        """
        Execute a task synchronously
        
        Args:
            request: Task request object
            
        Returns:
            TaskResponse object with results
            
        Raises:
            TaskExecutionException: If task execution fails
            TimeoutException: If task execution times out
            ValidationException: If request validation fails
        """
        self.logger.info(f"Executing task: {request.task}")
        
        # Validate request
        self._validate_request(request)
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create initial response
        response = TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            timestamp=datetime.now()
        )
        
        self.active_tasks[task_id] = response
        
        try:
            # Update status to running
            response.status = TaskStatus.RUNNING
            
            # Execute the task
            start_time = time.time()
            result = self._execute_workflow(request)
            execution_time = time.time() - start_time
            
            # Update response with results
            response.status = TaskStatus.COMPLETED
            response.result = result.get("result", "Task completed successfully")
            response.execution_time = execution_time
            response.messages = result.get("messages", [])
            response.agent_visits = result.get("agent_visits", {})
            response.tools_used = result.get("tools_used", [])
            response.files_modified = result.get("files_modified", [])
            
            self.logger.info(f"Task {task_id} completed successfully in {execution_time:.2f}s")
            
        except Exception as e:
            response.status = TaskStatus.FAILED
            response.error = str(e)
            self.logger.error(f"Task {task_id} failed: {str(e)}")
            
            if isinstance(e, (TaskExecutionException, TimeoutException, ValidationException)):
                raise
            else:
                raise TaskExecutionException(f"Task execution failed: {str(e)}", task_id)
        
        finally:
            # Move to history and cleanup
            self.task_history.append(response)
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
        
        return response
    
    def execute_task_async(self, request: TaskRequest, callback: Callable = None) -> str:
        """
        Execute a task asynchronously
        
        Args:
            request: Task request object
            callback: Optional callback function to call when task completes
            
        Returns:
            Task ID for tracking
        """
        task_id = str(uuid.uuid4())
        
        if callback:
            self.task_callbacks[task_id] = callback
        
        def run_task():
            try:
                response = self.execute_task(request)
                if callback:
                    callback(response)
            except Exception as e:
                error_response = TaskResponse(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error=str(e)
                )
                if callback:
                    callback(error_response)
            finally:
                self.task_callbacks.pop(task_id, None)
        
        thread = threading.Thread(target=run_task)
        thread.daemon = True
        thread.start()
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[TaskResponse]:
        """Get status of a specific task"""
        # Check active tasks first
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check history
        for task in self.task_history:
            if task.task_id == task_id:
                return task
        
        return None
    
    def get_agent_status(self) -> AgentStatus:
        """Get current agent system status"""
        self._agent_status.uptime = time.time() - getattr(self, '_start_time', time.time())
        self._agent_status.total_tasks = len(self.task_history)
        self._agent_status.successful_tasks = sum(1 for t in self.task_history if t.status == TaskStatus.COMPLETED)
        self._agent_status.failed_tasks = sum(1 for t in self.task_history if t.status == TaskStatus.FAILED)
        self._agent_status.is_running = len(self.active_tasks) > 0
        
        return self._agent_status
    
    def get_file_context(self, filepath: str) -> FileContext:
        """Get context information for a file"""
        file_path = Path(filepath)
        if not file_path.is_absolute():
            file_path = self.working_directory / file_path
        
        context = FileContext(filepath=str(file_path))
        
        if file_path.exists():
            context.size = file_path.stat().st_size
            context.last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Detect language based on extension
            context.language = self._detect_language(file_path)
            
            # Check git status
            git_status = self.get_git_status()
            if git_status.is_repo:
                context.is_in_git = True
                # Check if file is tracked/modified
                rel_path = str(file_path.relative_to(self.working_directory))
                if rel_path in git_status.modified_files:
                    context.git_status = "modified"
                elif rel_path in git_status.staged_files:
                    context.git_status = "staged"
                elif rel_path in git_status.untracked_files:
                    context.git_status = "untracked"
                else:
                    context.git_status = "tracked"
        
        return context
    
    def get_git_status(self) -> GitStatus:
        """Get git repository status"""
        git_status = GitStatus(is_repo=False)
        
        try:
            # Check if it's a git repository
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.working_directory,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                git_status.is_repo = True
                
                # Get current branch
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.working_directory,
                    capture_output=True,
                    text=True
                )
                if branch_result.returncode == 0:
                    git_status.current_branch = branch_result.stdout.strip()
                
                # Get status
                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=self.working_directory,
                    capture_output=True,
                    text=True
                )
                
                if status_result.returncode == 0:
                    lines = status_result.stdout.strip().split('\n')
                    for line in lines:
                        if not line:
                            continue
                        
                        status_code = line[:2]
                        filename = line[3:]
                        
                        if status_code[0] != ' ':  # Staged
                            git_status.staged_files.append(filename)
                        if status_code[1] != ' ':  # Modified
                            git_status.modified_files.append(filename)
                        if status_code == '??':  # Untracked
                            git_status.untracked_files.append(filename)
                
                git_status.has_changes = bool(git_status.staged_files or git_status.modified_files or git_status.untracked_files)
                
                # Get last commit
                commit_result = subprocess.run(
                    ["git", "log", "-1", "--format=%H %s"],
                    cwd=self.working_directory,
                    capture_output=True,
                    text=True
                )
                if commit_result.returncode == 0:
                    git_status.last_commit = commit_result.stdout.strip()
                
                # Get remote URL
                remote_result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=self.working_directory,
                    capture_output=True,
                    text=True
                )
                if remote_result.returncode == 0:
                    git_status.remote_url = remote_result.stdout.strip()
        
        except Exception as e:
            self.logger.warning(f"Error getting git status: {e}")
        
        return git_status
    
    def get_tool_usage_stats(self) -> List[ToolUsageStats]:
        """Get tool usage statistics"""
        # This would typically load from a persistent store
        # For now, return empty list as placeholder
        return []
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            self.logger.info(f"Task {task_id} cancelled")
            return True
        return False
    
    def _validate_request(self, request: TaskRequest):
        """Validate task request"""
        if not request.task or not request.task.strip():
            raise ValidationException("Task description cannot be empty")
        
        if request.timeout <= 0:
            raise ValidationException("Timeout must be positive")
        
        # Validate context files exist
        for filepath in request.context_files:
            file_path = Path(filepath)
            if not file_path.is_absolute():
                file_path = self.working_directory / file_path
            
            if not file_path.exists():
                raise ValidationException(f"Context file not found: {filepath}")
    
    def _execute_workflow(self, request: TaskRequest) -> Dict[str, Any]:
        """Execute the actual workflow"""
        # Import here to avoid circular imports
        from workflows.clean_swe_workflow import CleanSWEWorkflow
        from config.settings import Settings
        
        # Create workflow instance
        settings = Settings()
        workflow = CleanSWEWorkflow(
            settings=settings,
            use_planner=request.use_planner
        )
        
        # Prepare initial state
        initial_state = {
            "messages": [],
            "sender": "user",
            "task": request.task,
            "context_files": request.context_files,
            "working_directory": str(self.working_directory)
        }
        
        # Execute workflow
        try:
            result = workflow.run_workflow(request.task)
            
            # Extract useful information
            final_state = result.get("final_state", {})
            messages = final_state.get("messages", [])
            
            return {
                "result": self._extract_result_from_messages(messages),
                "messages": [self._serialize_message(msg) for msg in messages],
                "agent_visits": final_state.get("agent_visits", {}),
                "tools_used": self._extract_tools_used(messages),
                "files_modified": self._extract_files_modified(messages)
            }
            
        except Exception as e:
            raise TaskExecutionException(f"Workflow execution failed: {str(e)}")
    
    def _extract_result_from_messages(self, messages: List) -> str:
        """Extract result from message chain"""
        if not messages:
            return "Task completed successfully"
        
        # Get the last AI message
        for message in reversed(messages):
            if hasattr(message, 'content') and message.content:
                return str(message.content)
        
        return "Task completed successfully"
    
    def _serialize_message(self, message) -> Dict[str, Any]:
        """Serialize message object to dictionary"""
        return {
            "type": type(message).__name__,
            "content": str(getattr(message, 'content', '')),
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_tools_used(self, messages: List) -> List[str]:
        """Extract tools used from messages"""
        tools = set()
        for message in messages:
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    if hasattr(tool_call, 'name'):
                        tools.add(tool_call.name)
        return list(tools)
    
    def _extract_files_modified(self, messages: List) -> List[str]:
        """Extract files that were modified"""
        files = set()
        # This would need to be implemented based on tool call analysis
        return list(files)
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.rs': 'rust',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.sh': 'bash',
            '.sql': 'sql'
        }
        
        return extension_map.get(file_path.suffix.lower())