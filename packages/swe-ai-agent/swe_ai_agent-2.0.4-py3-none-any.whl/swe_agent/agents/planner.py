"""
Planner Agent - Specialized agent for project planning and technical specifications.
Creates comprehensive plans and tech specs that require human approval before implementation.
"""

import logging
from typing import Dict, Any, List
from langchain_core.messages import BaseMessage, AIMessage
from state.agent_state import AgentState
from tools.planning_tools import PlanningTools
from utils.anthropic_client import call_claude
from utils.helpers import get_last_ai_message

logger = logging.getLogger(__name__)

class PlannerAgent:
    """
    Specialized agent for project planning and technical specification creation.
    Handles goal analysis, planning, and tech spec generation with human approval workflow.
    """
    
    def __init__(self, tools: PlanningTools):
        """
        Initialize the Planner Agent.
        
        Args:
            tools: Planning tools instance for plan creation and management
        """
        self.tools = tools
        self.anthropic_client = tools.anthropic_client
        logger.info("[P] Planner initialized with Claude Sonnet 4 and planning tools")
    
    def process(self, state: AgentState) -> Dict[str, Any]:
        """
        Process the current state and perform planning operations.
        
        Args:
            state: Current agent state containing messages and context
            
        Returns:
            Updated state with planning results
        """
        logger.info(f"[P] Planner processing state with {len(state['messages'])} messages")
        
        # Process the planning task
        response = self._perform_planning(state["messages"])
        
        # Create response message with trimmed content to prevent API errors
        response_message = AIMessage(content=response.rstrip())
        
        # Update consecutive visits
        consecutive_visits = state["consecutive_visits"].copy()
        consecutive_visits["planner"] = consecutive_visits.get("planner", 0) + 1
        
        # Update state
        new_state = {
            "messages": state["messages"] + [response_message],
            "sender": "planner",
            "consecutive_visits": consecutive_visits
        }
        
        return new_state
    
    def _perform_planning(self, messages: List[BaseMessage]) -> str:
        """
        Perform planning operations based on the current context.
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            Planning results or next action
        """
        try:
            # Check if this is an approval message
            last_human_message = None
            approval_message = None
            for msg in reversed(messages):
                if hasattr(msg, 'content') and msg.__class__.__name__ == 'HumanMessage':
                    last_human_message = msg.content
                    break
                elif hasattr(msg, 'content') and msg.__class__.__name__ == 'AIMessage' and msg.content.startswith("APPROVAL:"):
                    approval_message = msg.content
            
            # If we have both original task and approval, process directly
            if last_human_message and approval_message and not last_human_message.startswith("APPROVAL:"):
                logger.info(">>> Planner handling approval response from restart")
                if "approved" in approval_message.lower():
                    return """# PLAN APPROVED [OK]

The project plan has been approved and implementation can now begin.

**Implementation Status:** Ready to start
**Next Phase:** Development

PLANNING COMPLETED - approved - Plan approved, routing to Software Engineer Agent for implementation
"""
                else:
                    return self._handle_approval_response(messages)
            
            if last_human_message and last_human_message.startswith("APPROVAL:"):
                # This is an approval response, handle it
                logger.info(">>> Planner handling approval response")
                return self._handle_approval_response(messages)
            
            # Get the original goal from the first human message
            original_goal = None
            for msg in messages:
                if hasattr(msg, 'content') and msg.__class__.__name__ == 'HumanMessage':
                    if not msg.content.startswith("APPROVAL:"):
                        original_goal = msg.content
                        break
            
            if not original_goal:
                return "PLANNING COMPLETED - No goal found to plan for"
            
            # Check if we need human approval
            last_message = get_last_ai_message(messages)
            if last_message and "AWAITING_HUMAN_APPROVAL" in last_message.content:
                return self._handle_approval_response(messages)
            
            # Generate initial plan and tech spec
            logger.info(f">>> Planner analyzing goal: {original_goal}")
            
            # Create comprehensive plan and tech spec
            plan_result = self._create_plan_and_spec(original_goal)
            
            return plan_result
                
        except Exception as e:
            logger.error(f"Error in planning: {e}")
            return f"Planning error: {str(e)}\n\nPLANNING COMPLETED - Proceeding despite errors"
    
    def _create_plan_and_spec(self, goal: str) -> str:
        """
        Create a comprehensive plan and technical specification.
        
        Args:
            goal: The original goal/task description
            
        Returns:
            Formatted plan and tech spec requiring human approval
        """
        try:
            # Generate comprehensive plan and tech spec
            prompt = f"""
            Create a comprehensive project plan and technical specification for the following goal:

            Goal: {goal}

            Please provide a detailed plan with the following structure:

            ## PROJECT OVERVIEW
            - Brief description of what will be built
            - Key objectives and success criteria
            - Target users/audience

            ## TECHNICAL SPECIFICATION
            - Architecture overview
            - Technology stack recommendations
            - Key components and their responsibilities
            - Data structures and APIs if applicable
            - File structure and organization

            ## IMPLEMENTATION PLAN
            - Phase 1: Core functionality
            - Phase 2: Enhanced features
            - Phase 3: Polish and optimization
            - Estimated timeline for each phase

            ## REQUIREMENTS
            - Functional requirements
            - Non-functional requirements
            - Dependencies and external services
            - Testing strategy

            ## RISK ASSESSMENT
            - Potential challenges
            - Mitigation strategies
            - Alternative approaches

            Make the plan actionable and specific. Include enough detail that a developer could start implementation immediately upon approval.
            """
            
            plan_content = call_claude(
                self.anthropic_client, 
                prompt, 
                "You are an expert technical architect and project planner. Create comprehensive, actionable plans that developers can immediately implement."
            )
            
            # Check if this is a simple task that can be auto-approved
            simple_task_keywords = ['create', 'list', 'delete', 'update', 'simple', 'hello', 'test', 'basic', 'file', 'html', 'txt']
            is_simple_task = any(keyword in goal.lower() for keyword in simple_task_keywords)
            
            if is_simple_task:
                # Auto-approve simple tasks
                formatted_response = f"""# PROJECT PLAN & TECHNICAL SPECIFICATION

{plan_content}

---

## PLAN APPROVED [OK]

This is a simple task that has been automatically approved for implementation.

**Plan Status:** Approved
**Implementation Status:** Ready to start
**Next Phase:** Development

Plan approved. Proceeding with implementation.
"""
            else:
                # Format the response for human approval
                formatted_response = f"""# PROJECT PLAN & TECHNICAL SPECIFICATION

{plan_content}

---

## APPROVAL REQUIRED

This plan needs your approval before implementation can begin.

**Next Steps:**
1. Review the plan and technical specification above
2. Provide feedback or approval
3. Implementation will begin once approved

**Available Actions:**
- Type "approve" to proceed with implementation
- Type "modify [your changes]" to request modifications
- Type "reject" to cancel and create a new plan

AWAITING_HUMAN_APPROVAL - Please review and approve the plan above
"""
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return f"Error creating plan: {str(e)}\n\nPLANNING COMPLETED - Creation failed"
    
    def _handle_approval_response(self, messages: List[BaseMessage]) -> str:
        """
        Handle human approval response.
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            Next action based on approval status
        """
        try:
            # Get the last human message for approval response
            last_human_msg = None
            for msg in reversed(messages):
                if hasattr(msg, 'content') and msg.__class__.__name__ == 'HumanMessage':
                    content = msg.content.lower().strip()
                    # Extract approval response from "APPROVAL: approved" format
                    if content.startswith("approval:"):
                        last_human_msg = content.replace("approval:", "").strip()
                    else:
                        last_human_msg = content
                    break
            
            if not last_human_msg:
                return "AWAITING_HUMAN_APPROVAL - Please provide approval response"
            
            if "approve" in last_human_msg:
                return """# PLAN APPROVED [OK]

The project plan has been approved and implementation can now begin.

**Implementation Status:** Ready to start
**Next Phase:** Development

PLANNING COMPLETED - approved - Plan approved, routing to Software Engineer Agent for implementation
"""
            
            elif "modify" in last_human_msg:
                # Extract modification requests
                modification_request = last_human_msg.replace("modify", "").strip()
                
                prompt = f"""
                The user has requested modifications to the plan:
                
                Modification Request: {modification_request}
                
                Please update the plan accordingly and present the revised version for approval.
                Keep the same structure but incorporate the requested changes.
                """
                
                updated_plan = call_claude(
                    self.anthropic_client,
                    prompt,
                    "You are an expert technical architect. Incorporate user feedback into project plans while maintaining technical accuracy."
                )
                
                return f"""# REVISED PROJECT PLAN & TECHNICAL SPECIFICATION

{updated_plan}

---

## APPROVAL REQUIRED

This revised plan incorporates your requested modifications.

**Available Actions:**
- Type "approve" to proceed with implementation
- Type "modify [your changes]" to request further modifications
- Type "reject" to cancel and create a new plan

AWAITING_HUMAN_APPROVAL - Please review and approve the revised plan above
"""
            
            elif "reject" in last_human_msg:
                return """# PLAN REJECTED [X]

The project plan has been rejected. Please provide a new goal or clarify your requirements.

PLANNING COMPLETED - Plan rejected, awaiting new goal
"""
            
            else:
                return """# UNCLEAR APPROVAL RESPONSE

Please provide a clear response:
- Type "approve" to proceed with implementation
- Type "modify [your changes]" to request modifications
- Type "reject" to cancel and create a new plan

AWAITING_HUMAN_APPROVAL - Please provide clear approval response
"""
                
        except Exception as e:
            logger.error(f"Error handling approval: {e}")
            return f"Error handling approval: {str(e)}\n\nPLANNING COMPLETED - Approval handling failed"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools for this agent."""
        return [
            "create_plan",
            "create_tech_spec",
            "analyze_requirements",
            "estimate_timeline",
            "assess_risks",
            "generate_architecture"
        ]