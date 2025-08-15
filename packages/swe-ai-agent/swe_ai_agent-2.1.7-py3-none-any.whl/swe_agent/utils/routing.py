"""
Routing utilities for the SWE workflow.
Contains routing functions for state transitions between agents.
"""

import logging
from typing import Literal, Dict, Any
from state.agent_state import AgentState
from utils.helpers import get_last_ai_message

logger = logging.getLogger(__name__)

def router(state: AgentState) -> Literal["continue", "analyze_code", "edit_file", "use_swe_tools", "__end__"]:
    """
    Main router for Software Engineer agent state transitions.
    
    Args:
        state: Current agent state
        
    Returns:
        Next state to transition to
    """
    messages = state["messages"]
    if not messages:
        return "analyze_code"
    
    last_ai_message = get_last_ai_message(messages)
    if not last_ai_message:
        return "analyze_code"
    
    content = last_ai_message.content
    
    logger.info(f"Router processing message: {content[:100]}...")
    
    # Check for explicit state transitions
    if "ANALYZE CODE" in content:
        logger.info("Routing to analyze_code")
        return "analyze_code"
    
    if "EDIT FILE" in content:
        logger.info("Routing to edit_file")
        return "edit_file"
    
    if "PATCH COMPLETED" in content:
        logger.info("Routing to __end__")
        return "__end__"
    
    # Check for completion signals from other agents
    if "ANALYSIS COMPLETE" in content:
        logger.info("Analysis completed, routing to edit_file")
        return "edit_file"
    
    if "EDITING COMPLETED" in content:
        logger.info("Editing completed, routing to __end__")
        return "__end__"
    
    # Check for tool usage
    if "generate_repo_tree" in content or "create_patch" in content:
        logger.info("Routing to use_swe_tools")
        return "use_swe_tools"
    
    # Check for continuation
    if "continue" in content.lower() or "Has tool_calls" in content:
        logger.info("Routing to continue")
        return "continue"
    
    # Default behavior - if no clear signal, end the workflow
    logger.info("No clear routing signal, ending workflow")
    return "__end__"

def code_analyzer_router(state: AgentState) -> Literal["continue", "done", "edit_file", "use_analysis_tools"]:
    """
    Router for Code Analyzer agent state transitions.
    
    Args:
        state: Current agent state
        
    Returns:
        Next state to transition to
    """
    messages = state["messages"]
    if not messages:
        return "continue"
    
    last_ai_message = get_last_ai_message(messages)
    if not last_ai_message:
        return "continue"
    
    content = last_ai_message.content
    
    logger.info(f"Code Analyzer router processing: {content[:100]}...")
    
    # Check for completion
    if "ANALYSIS COMPLETE" in content:
        logger.info("Code Analyzer routing to done")
        return "done"
    
    # Check for file editing request
    if "EDIT FILE" in content:
        logger.info("Code Analyzer routing to edit_file")
        return "edit_file"
    
    # Check for tool usage
    if any(tool in content for tool in ["analyze_function", "find_references", "get_class_hierarchy"]):
        logger.info("Code Analyzer routing to use_analysis_tools")
        return "use_analysis_tools"
    
    # Check for continuation
    if "Continue analysis" in content or "Has tool_calls" in content:
        logger.info("Code Analyzer routing to continue")
        return "continue"
    
    # Default behavior
    logger.info("Code Analyzer default routing to continue")
    return "continue"

def editor_router(state: AgentState) -> Literal["continue", "done", "use_editing_tools"]:
    """
    Router for Editor agent state transitions.
    
    Args:
        state: Current agent state
        
    Returns:
        Next state to transition to
    """
    messages = state["messages"]
    if not messages:
        return "continue"
    
    last_ai_message = get_last_ai_message(messages)
    if not last_ai_message:
        return "continue"
    
    content = last_ai_message.content
    
    logger.info(f"Editor router processing: {content[:100]}...")
    
    # Check for completion
    if "EDITING COMPLETED" in content:
        logger.info("Editor routing to done")
        return "done"
    
    # Check for tool usage
    if any(tool in content for tool in ["execute_edit", "save_file", "create_backup", "validate_changes"]):
        logger.info("Editor routing to use_editing_tools")
        return "use_editing_tools"
    
    # Check for continuation
    if "Continue editing" in content or "Has tool_calls" in content:
        logger.info("Editor routing to continue")
        return "continue"
    
    # Default behavior
    logger.info("Editor default routing to continue")
    return "continue"

def get_routing_info(state: AgentState) -> Dict[str, Any]:
    """
    Get routing information for debugging.
    
    Args:
        state: Current agent state
        
    Returns:
        Routing information
    """
    messages = state["messages"]
    routing_info = {
        "message_count": len(messages),
        "sender": state["sender"],
        "consecutive_visits": state["consecutive_visits"],
        "last_message_preview": None,
        "routing_markers": []
    }
    
    if messages:
        last_ai_message = get_last_ai_message(messages)
        if last_ai_message:
            content = last_ai_message.content
            routing_info["last_message_preview"] = content[:200] + "..." if len(content) > 200 else content
            
            # Check for routing markers
            markers = [
                "ANALYZE CODE",
                "EDIT FILE", 
                "PATCH COMPLETED",
                "ANALYSIS COMPLETE",
                "EDITING COMPLETED",
                "Has tool_calls",
                "Continue analysis",
                "Continue editing"
            ]
            
            routing_info["routing_markers"] = [marker for marker in markers if marker in content]
    
    return routing_info

def validate_routing_decision(state: AgentState, decision: str) -> bool:
    """
    Validate if a routing decision is appropriate.
    
    Args:
        state: Current agent state
        decision: Routing decision to validate
        
    Returns:
        True if decision is valid, False otherwise
    """
    valid_decisions = {
        "software_engineer": ["continue", "analyze_code", "edit_file", "use_swe_tools", "__end__"],
        "code_analyzer": ["continue", "done", "edit_file", "use_analysis_tools"],
        "editor": ["continue", "done", "use_editing_tools"]
    }
    
    sender = state["sender"]
    
    # Check if decision is valid for current agent
    if sender in valid_decisions:
        return decision in valid_decisions[sender]
    
    # Default validation
    return decision in ["continue", "done", "__end__"]

def get_next_agent_prediction(state: AgentState) -> str:
    """
    Predict the next agent based on current state.
    
    Args:
        state: Current agent state
        
    Returns:
        Predicted next agent name
    """
    messages = state["messages"]
    if not messages:
        return "software_engineer"
    
    last_ai_message = get_last_ai_message(messages)
    if not last_ai_message:
        return "software_engineer"
    
    content = last_ai_message.content
    
    # Predict based on content
    if "ANALYZE CODE" in content:
        return "code_analyzer"
    elif "EDIT FILE" in content:
        return "editor"
    elif "ANALYSIS COMPLETE" in content:
        return "software_engineer"
    elif "EDITING COMPLETED" in content:
        return "software_engineer"
    elif "PATCH COMPLETED" in content:
        return "END"
    
    # Return current sender if no clear transition
    return state["sender"]

def should_end_workflow(state: AgentState) -> bool:
    """
    Determine if the workflow should end.
    
    Args:
        state: Current agent state
        
    Returns:
        True if workflow should end, False otherwise
    """
    messages = state["messages"]
    if not messages:
        return False
    
    last_ai_message = get_last_ai_message(messages)
    if not last_ai_message:
        return False
    
    content = last_ai_message.content
    
    # Check for end conditions
    end_markers = ["PATCH COMPLETED", "Task completed", "Workflow finished"]
    
    for marker in end_markers:
        if marker in content:
            return True
    
    # Check for maximum message count
    if len(messages) > 50:
        logger.warning("Maximum message count reached, ending workflow")
        return True
    
    # Check for excessive loops
    total_visits = sum(state["consecutive_visits"].values())
    if total_visits > 20:
        logger.warning("Excessive agent visits detected, ending workflow")
        return True
    
    return False
