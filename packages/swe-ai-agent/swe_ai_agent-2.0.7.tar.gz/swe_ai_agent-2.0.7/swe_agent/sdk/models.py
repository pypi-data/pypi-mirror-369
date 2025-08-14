"""
Data models for the SWE Agent SDK
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Status of a task execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(Enum):
    """Types of agents available"""
    PLANNER = "planner"
    SOFTWARE_ENGINEER = "software_engineer"
    CODE_ANALYZER = "code_analyzer"
    EDITOR = "editor"


@dataclass
class TaskRequest:
    """Request object for task execution"""
    task: str
    use_planner: bool = False
    context_files: List[str] = field(default_factory=list)
    working_directory: str = "."
    timeout: int = 300  # 5 minutes default
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResponse:
    """Response object for task execution"""
    task_id: str
    status: TaskStatus
    result: Optional[str] = None
    error: Optional[str] = None
    messages: List[Dict[str, Any]] = field(default_factory=list)
    execution_time: float = 0.0
    agent_visits: Dict[str, int] = field(default_factory=dict)
    tools_used: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentStatus:
    """Status information for the agent system"""
    is_running: bool
    current_task: Optional[str] = None
    uptime: float = 0.0
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    agents_available: List[AgentType] = field(default_factory=list)
    system_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileContext:
    """File context information"""
    filepath: str
    content: Optional[str] = None
    language: Optional[str] = None
    size: int = 0
    last_modified: Optional[datetime] = None
    is_in_git: bool = False
    git_status: Optional[str] = None


@dataclass
class GitStatus:
    """Git repository status"""
    is_repo: bool
    current_branch: Optional[str] = None
    has_changes: bool = False
    staged_files: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    untracked_files: List[str] = field(default_factory=list)
    last_commit: Optional[str] = None
    remote_url: Optional[str] = None


@dataclass
class ToolUsageStats:
    """Tool usage statistics"""
    tool_name: str
    usage_count: int
    success_rate: float
    average_execution_time: float
    last_used: Optional[datetime] = None
    agent_usage: Dict[str, int] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result from workflow execution"""
    final_state: Dict[str, Any]
    message_count: int
    final_sender: str
    execution_time: float
    success: bool = True
    error: Optional[str] = None