"""
Software Engineer Agent - Main orchestrator for the SWE workflow.
Responsible for task delegation, workflow initiation, and termination.
"""

import logging
from typing import Dict, Any, List
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from state.agent_state import AgentState
from tools.langraph_tools import LangGraphTools
from tools.tool_usage_tracker import get_tool_tracker
from utils.helpers import get_last_ai_message
from utils.anthropic_client import get_anthropic_client, call_claude
from pathlib import Path
from prompts.swe_prompts import SOFTWARE_ENGINEER_PROMPT

logger = logging.getLogger(__name__)

class SoftwareEngineerAgent:
    """
    Main orchestrator agent that manages the overall workflow.
    Decides when to delegate to CodeAnalyzer or Editor agents.
    """
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.name = "software_engineer"
        self.max_consecutive_visits = 3
        self.anthropic_client = get_anthropic_client()
        
        # Initialize LangGraph tools for function calls
        self.langraph_tools = LangGraphTools(str(repo_path))
        self.tools = self.langraph_tools.get_tools()
        
        # Initialize advanced tools for enhanced capabilities
        from tools.advanced_langraph_tools import AdvancedLangGraphTools
        self.advanced_tools = AdvancedLangGraphTools(str(repo_path))
        
        # Combine all tools for comprehensive functionality
        self.all_tools = self.tools + self.advanced_tools.get_all_tools()
        
        logger.info(f"[*] Software Engineer initialized with {len(self.all_tools)} tools (including advanced capabilities)")
        
    def process(self, state: AgentState) -> Dict[str, Any]:
        """
        Process the current state and determine next action.
        
        Args:
            state: Current agent state containing messages and context
            
        Returns:
            Updated state with new messages and sender information
        """
        logger.info(f">>> Software Engineer processing state with {len(state['messages'])} messages")
        
        # Debug: Print current state
        logger.debug(f"[?] Current state keys: {list(state.keys())}")
        logger.debug(f"[?] Messages: {[msg.content[:50] + '...' if hasattr(msg, 'content') else str(msg) for msg in state['messages']]}")
        
        # Check for consecutive visits to prevent loops
        consecutive_visits = state.get("consecutive_visits", {})
        visit_count = consecutive_visits.get(self.name, 0) + 1
        
        logger.debug(f"🔄 Visit count for {self.name}: {visit_count}/{self.max_consecutive_visits}")
        
        if visit_count > self.max_consecutive_visits:
            logger.warning(f"⚠️  Max consecutive visits ({self.max_consecutive_visits}) reached for {self.name}")
            return {
                **state,
                "messages": state["messages"] + [
                    AIMessage(content="PATCH COMPLETED - Maximum iterations reached")
                ],
                "sender": self.name
            }
        
        # Update visit count
        consecutive_visits[self.name] = visit_count
        
        # Get the last message to understand context
        last_message = state["messages"][-1] if state["messages"] else None
        
        # Analyze the task and determine next action
        tracker = get_tool_tracker()
        call_id = tracker.start_tool_call(self.name, "analyze_task", {"message_count": len(state["messages"])})
        
        try:
            response = self._analyze_task(state["messages"])
            success = response and len(response) > 0
            tracker.end_tool_call(call_id, self.name, "analyze_task", success,
                                None if success else "Analysis failed",
                                response[:100] if response else None)
        except Exception as e:
            tracker.end_tool_call(call_id, self.name, "analyze_task", False, str(e))
            raise
        
        logger.info(f"📝 Software Engineer decision: {response[:100]}...")
        
        # Reset visit count for other agents if we're transitioning
        if "ANALYZE CODE" in response or "EDIT FILE" in response:
            consecutive_visits = {self.name: visit_count}
            logger.debug(f"🔄 Resetting visit counts for transition")
        
        new_state = {
            **state,
            "messages": state["messages"] + [AIMessage(content=response)],
            "sender": self.name,
            "consecutive_visits": consecutive_visits
        }
        
        return new_state
    
    def _analyze_task(self, messages: List[BaseMessage]) -> str:
        """
        Analyze the current task and determine the next action using Claude Sonnet 4.
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            Response message indicating next action
        """
        logger.info(f">>> Analyzing task with {len(messages)} messages")
        
        if not messages:
            logger.debug("[P] No messages, starting with code analysis")
            return "ANALYZE CODE - Starting with codebase analysis"
        
        # Check if we have too many messages (prevent infinite loops)
        if len(messages) > 15:
            logger.warning("⚠️  Maximum message limit reached")
            return "PATCH COMPLETED - Maximum message limit reached, workflow completed"
        
        last_message = get_last_ai_message(messages)
        
        # Check if we're coming from another agent
        if last_message and hasattr(last_message, 'content'):
            content = last_message.content
            logger.debug(f"📄 Last message content: {content[:100]}...")
            
            # If code analysis is complete, move to editing
            if "ANALYSIS COMPLETE" in content:
                logger.info("[OK] Code analysis complete, moving to editing")
                return "EDIT FILE - Moving to file editing phase"
            
            # If we have an approved plan, move to implementation
            if "Plan approved" in content or "APPROVAL: approved" in content:
                logger.info("[OK] Plan approved, moving to implementation")
                # Get the original task to provide context
                original_task = None
                
                # Look for the original human message (first one)
                for msg in messages:
                    if hasattr(msg, 'content') and msg.__class__.__name__ == 'HumanMessage':
                        original_task = msg.content
                        logger.info(f"[OK] Found original task: {original_task}")
                        break
                
                # If no HumanMessage found, look for the first message that's not system-related
                if not original_task:
                    for msg in messages:
                        if hasattr(msg, 'content') and msg.content and not any(x in msg.content for x in ['APPROVAL:', 'Plan approved', 'EDIT FILE', 'ANALYZE CODE']):
                            original_task = msg.content
                            logger.info(f"[OK] Found fallback task: {original_task}")
                            break
                
                if original_task:
                    return f"EDIT FILE - Implement the approved plan for task: {original_task}"
                else:
                    logger.warning("⚠️  No original task found!")
                    return "EDIT FILE - Implement the approved plan"
            
            # If editing is complete, we're done
            if "EDITING COMPLETED" in content:
                logger.info("[OK] Editing complete, workflow finished")
                return "PATCH COMPLETED - Task completed successfully"
            
            # If we have tool calls, process them
            if "Has tool_calls" in content:
                logger.debug("[*] Processing tool calls")
                return self._process_tool_calls(content)
        
        # Use Claude to analyze the task context
        try:
            context = "\n".join([msg.content for msg in messages[-3:] if hasattr(msg, 'content')])
            
            system_prompt = SOFTWARE_ENGINEER_PROMPT
            
            claude_response = call_claude(
                self.anthropic_client,
                f"Context: {context}\n\nWhat should be the next action in this software engineering workflow?",
                system_prompt
            )
            
            logger.debug(f"[A] Claude analysis: {claude_response}")
            
            # Ensure response follows expected format
            if "ANALYZE CODE" in claude_response:
                return claude_response
            elif "EDIT FILE" in claude_response:
                return claude_response
            elif "PATCH COMPLETED" in claude_response:
                return claude_response
            else:
                logger.warning("⚠️  Claude response didn't match expected format, defaulting")
                return "ANALYZE CODE - Beginning codebase analysis"
                
        except Exception as e:
            logger.error(f"[X] Error calling Claude: {e}")
            return "ANALYZE CODE - Beginning codebase analysis"
    
    def _process_tool_calls(self, content: str) -> str:
        """
        Process tool calls and determine next action.
        
        Args:
            content: Message content containing tool call information
            
        Returns:
            Next action based on tool call results
        """
        # Check if we need to generate repository structure
        if "generate_repo_tree" in content:
            try:
                repo_tree = self.tools.generate_repo_tree()
                return f"Repository structure generated:\n{repo_tree}\n\nANALYZE CODE - Proceeding with detailed analysis"
            except Exception as e:
                logger.error(f"Error generating repo tree: {e}")
                return "ANALYZE CODE - Proceeding with analysis despite repo tree error"
        
        # Check if we need to create a patch
        if "create_patch" in content:
            try:
                patch_info = self.tools.create_patch()
                return f"Patch created:\n{patch_info}\n\nPATCH COMPLETED - Task completed"
            except Exception as e:
                logger.error(f"Error creating patch: {e}")
                return "EDIT FILE - Patch creation failed, continuing with editing"
        
        return "ANALYZE CODE - Continuing with analysis"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools for this agent."""
        return [
            "generate_repo_tree",
            "create_patch",
            "get_project_structure",
            "analyze_dependencies"
        ]
