"""
Agent State Management - Defines the state structure for the multi-agent system.
Contains TypedDict definitions and state management utilities.
"""

from typing import TypedDict, Annotated, Sequence, Dict, Any
from langchain.schema import BaseMessage
import operator

class AgentState(TypedDict):
    """
    Core state structure for the multi-agent SWE system.
    
    This state is shared across all agents and contains:
    - Message history for conversation context
    - Current sender to track agent ownership
    - Visit counts to prevent infinite loops
    """
    
    # Message history that preserves conversation context
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Current sender identity to track which agent is active
    sender: str
    
    # Visit counts to track repeated visits and prevent loops
    consecutive_visits: Dict[str, int]

class WorkflowState(TypedDict):
    """
    Extended state for workflow management.
    
    Contains additional workflow-specific information:
    - Current phase of the workflow
    - Task description and requirements
    - Results from each agent
    """
    
    # Base agent state
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
    consecutive_visits: Dict[str, int]
    
    # Workflow-specific fields
    current_phase: str  # "planning", "analysis", "editing", "completion"
    task_description: str
    planning_results: Dict[str, Any]
    analysis_results: Dict[str, Any]
    editing_results: Dict[str, Any]
    final_output: Dict[str, Any]

class ToolState(TypedDict):
    """
    State for tool execution tracking.
    
    Contains information about tool usage:
    - Tool execution history
    - Tool results and outputs
    - Tool-specific configurations
    """
    
    # Tool execution history
    tool_calls: Sequence[Dict[str, Any]]
    tool_results: Dict[str, Any]
    tool_configs: Dict[str, Any]

def create_initial_state(task_description: str) -> AgentState:
    """
    Create an initial state for the workflow.
    
    Args:
        task_description: The task to be performed
        
    Returns:
        Initial agent state
    """
    return AgentState(
        messages=[],
        sender="system",
        consecutive_visits={}
    )

def create_workflow_state(task_description: str) -> WorkflowState:
    """
    Create an initial workflow state.
    
    Args:
        task_description: The task to be performed
        
    Returns:
        Initial workflow state
    """
    return WorkflowState(
        messages=[],
        sender="system",
        consecutive_visits={},
        current_phase="planning",
        task_description=task_description,
        planning_results={},
        analysis_results={},
        editing_results={},
        final_output={}
    )

def reset_consecutive_visits(state: AgentState, agent_name: str) -> AgentState:
    """
    Reset consecutive visits for other agents when transitioning.
    
    Args:
        state: Current agent state
        agent_name: Name of the agent that's taking control
        
    Returns:
        Updated state with reset visit counts
    """
    new_visits = {agent_name: state["consecutive_visits"].get(agent_name, 0)}
    
    return AgentState(
        messages=state["messages"],
        sender=state["sender"],
        consecutive_visits=new_visits
    )

def increment_visit_count(state: AgentState, agent_name: str) -> AgentState:
    """
    Increment visit count for an agent.
    
    Args:
        state: Current agent state
        agent_name: Name of the agent
        
    Returns:
        Updated state with incremented visit count
    """
    consecutive_visits = state["consecutive_visits"].copy()
    consecutive_visits[agent_name] = consecutive_visits.get(agent_name, 0) + 1
    
    return AgentState(
        messages=state["messages"],
        sender=state["sender"],
        consecutive_visits=consecutive_visits
    )

def get_visit_count(state: AgentState, agent_name: str) -> int:
    """
    Get the current visit count for an agent.
    
    Args:
        state: Current agent state
        agent_name: Name of the agent
        
    Returns:
        Current visit count
    """
    return state["consecutive_visits"].get(agent_name, 0)

def is_max_visits_reached(state: AgentState, agent_name: str, max_visits: int) -> bool:
    """
    Check if an agent has reached maximum consecutive visits.
    
    Args:
        state: Current agent state
        agent_name: Name of the agent
        max_visits: Maximum allowed consecutive visits
        
    Returns:
        True if max visits reached, False otherwise
    """
    return get_visit_count(state, agent_name) >= max_visits

def add_message_to_state(state: AgentState, message: BaseMessage, sender: str) -> AgentState:
    """
    Add a message to the state.
    
    Args:
        state: Current agent state
        message: Message to add
        sender: Sender of the message
        
    Returns:
        Updated state with new message
    """
    return AgentState(
        messages=state["messages"] + [message],
        sender=sender,
        consecutive_visits=state["consecutive_visits"]
    )

def get_last_message(state: AgentState) -> BaseMessage:
    """
    Get the last message from the state.
    
    Args:
        state: Current agent state
        
    Returns:
        Last message or None if no messages
    """
    if state["messages"]:
        return state["messages"][-1]
    return None

def get_messages_by_sender(state: AgentState, sender: str) -> Sequence[BaseMessage]:
    """
    Get all messages from a specific sender.
    
    Args:
        state: Current agent state
        sender: Sender to filter by
        
    Returns:
        List of messages from the sender
    """
    return [msg for msg in state["messages"] if hasattr(msg, 'sender') and msg.sender == sender]

def clear_old_messages(state: AgentState, keep_last: int = 10) -> AgentState:
    """
    Clear old messages to prevent state from growing too large.
    
    Args:
        state: Current agent state
        keep_last: Number of recent messages to keep
        
    Returns:
        Updated state with trimmed messages
    """
    if len(state["messages"]) > keep_last:
        return AgentState(
            messages=state["messages"][-keep_last:],
            sender=state["sender"],
            consecutive_visits=state["consecutive_visits"]
        )
    
    return state
