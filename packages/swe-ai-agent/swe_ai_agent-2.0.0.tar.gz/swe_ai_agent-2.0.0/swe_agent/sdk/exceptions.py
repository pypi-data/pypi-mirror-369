"""
Custom exceptions for the SWE Agent SDK
"""


class SWEAgentException(Exception):
    """Base exception for SWE Agent SDK"""
    pass


class TaskExecutionException(SWEAgentException):
    """Exception raised during task execution"""
    def __init__(self, message: str, task_id: str = None, agent_type: str = None):
        super().__init__(message)
        self.task_id = task_id
        self.agent_type = agent_type


class ConnectionException(SWEAgentException):
    """Exception raised when connection to agent fails"""
    pass


class ValidationException(SWEAgentException):
    """Exception raised for validation errors"""
    pass


class TimeoutException(SWEAgentException):
    """Exception raised when task execution times out"""
    def __init__(self, message: str, timeout: int):
        super().__init__(message)
        self.timeout = timeout


class AgentNotAvailableException(SWEAgentException):
    """Exception raised when requested agent is not available"""
    def __init__(self, agent_type: str):
        super().__init__(f"Agent type '{agent_type}' is not available")
        self.agent_type = agent_type