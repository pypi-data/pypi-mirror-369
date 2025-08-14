"""
SWE Agent SDK - A comprehensive SDK for integrating SWE Agent into IDEs and external tools
"""

from .client import SWEAgentClient
from .models import (
    TaskRequest,
    TaskResponse,
    AgentStatus,
    FileContext,
    GitStatus,
    ToolUsageStats
)
from .exceptions import (
    SWEAgentException,
    TaskExecutionException,
    ConnectionException,
    ValidationException
)

__version__ = "1.0.0"
__all__ = [
    "SWEAgentClient",
    "TaskRequest",
    "TaskResponse", 
    "AgentStatus",
    "FileContext",
    "GitStatus",
    "ToolUsageStats",
    "SWEAgentException",
    "TaskExecutionException",
    "ConnectionException",
    "ValidationException"
]