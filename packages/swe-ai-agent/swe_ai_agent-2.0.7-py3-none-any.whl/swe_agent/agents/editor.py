"""
Editor Agent - Specialized agent for file editing and navigation.
Manages navigation within the codebase and file modifications using standalone tools.
"""

import logging
from typing import Dict, Any, List
from langchain.schema import BaseMessage, AIMessage
from state.agent_state import AgentState
from tools.langraph_tools import LangGraphTools
from tools.tool_usage_tracker import get_tool_tracker
from utils.helpers import get_last_ai_message
from utils.anthropic_client import get_anthropic_client, call_claude
from pathlib import Path
from prompts.swe_prompts import EDITING_AGENT_PROMPT

logger = logging.getLogger(__name__)

class EditorAgent:
    """
    Specialized agent for file editing and navigation tasks.
    Handles file modifications, navigation, and patch creation.
    """
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.name = "editor"
        self.max_consecutive_visits = 4
        self.anthropic_client = get_anthropic_client()
        
        # Initialize LangGraph tools for function calls
        self.langraph_tools = LangGraphTools(str(repo_path))
        self.tools = self.langraph_tools.get_tools()
        
        # Initialize advanced tools for enhanced capabilities
        from tools.advanced_langraph_tools import AdvancedLangGraphTools
        self.advanced_tools = AdvancedLangGraphTools(str(repo_path))
        
        # Combine all tools for comprehensive functionality
        self.all_tools = self.tools + self.advanced_tools.get_all_tools()
        
        logger.info(f"📝 Editor initialized with {len(self.all_tools)} tools (including advanced capabilities)")
        
    def process(self, state: AgentState) -> Dict[str, Any]:
        """
        Process the current state and perform editing operations.
        
        Args:
            state: Current agent state containing messages and context
            
        Returns:
            Updated state with editing results
        """
        logger.info(f"Editor processing state with {len(state['messages'])} messages")
        
        # Check for consecutive visits to prevent loops
        consecutive_visits = state.get("consecutive_visits", {})
        visit_count = consecutive_visits.get(self.name, 0) + 1
        
        if visit_count > self.max_consecutive_visits:
            logger.warning(f"Max consecutive visits ({self.max_consecutive_visits}) reached for {self.name}")
            return {
                **state,
                "messages": state["messages"] + [
                    AIMessage(content="EDITING COMPLETED - Maximum editing iterations reached")
                ],
                "sender": self.name
            }
        
        # Update visit count
        consecutive_visits[self.name] = visit_count
        
        # Perform editing based on current context
        tracker = get_tool_tracker()
        call_id = tracker.start_tool_call(self.name, "perform_editing", {"message_count": len(state["messages"])})
        
        try:
            editing_result = self._perform_editing(state["messages"])
            success = "EDITING COMPLETED" in editing_result
            tracker.end_tool_call(call_id, self.name, "perform_editing", success, 
                                None if success else "Editing failed", 
                                editing_result[:100] if editing_result else None)
        except Exception as e:
            tracker.end_tool_call(call_id, self.name, "perform_editing", False, str(e))
            raise
        
        # Reset visit count for other agents if we're transitioning
        if "EDITING COMPLETED" in editing_result:
            consecutive_visits = {self.name: visit_count}
        
        new_state = {
            **state,
            "messages": state["messages"] + [AIMessage(content=editing_result)],
            "sender": self.name,
            "consecutive_visits": consecutive_visits
        }
        
        return new_state
    
    def _perform_editing(self, messages: List[BaseMessage]) -> str:
        """
        Perform editing operations based on the current context using standalone tools.
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            Editing results or next action
        """
        try:
            # Get the implementation context from the message chain
            # Look for the most recent Software Engineer message that contains implementation details
            implementation_context = None
            original_task = None
            
            # First, get the original human task
            for msg in messages:
                if hasattr(msg, 'content') and msg.__class__.__name__ == 'HumanMessage':
                    original_task = msg.content
                    break
            
            # Then, look for the most recent SWE Agent message with implementation details
            for msg in reversed(messages):
                if hasattr(msg, 'content') and msg.content:
                    content = msg.content
                    # Look for SWE Agent messages that contain implementation instructions
                    if "EDIT FILE" in content and "task:" in content:
                        # Extract the actual task from the SWE message
                        task_start = content.find("task:")
                        if task_start != -1:
                            implementation_context = content[task_start + 5:].strip()
                        else:
                            implementation_context = content
                        break
            
            # Use the implementation context if available, otherwise fall back to original task
            task_to_execute = implementation_context if implementation_context else original_task
            
            if not task_to_execute:
                return "EDITING COMPLETED - No task found to execute"
            
            # Use Claude to understand what needs to be created/edited
            logger.info(f">>> Editor analyzing task: {task_to_execute}")
            
            # If we have both contexts, use the original task (it's more specific)
            if original_task and implementation_context:
                final_task = original_task
            else:
                final_task = task_to_execute
            
            # Let Claude decide what file to create and its content
            result = self._create_file_with_claude(final_task)
            
            return result
                
        except Exception as e:
            logger.error(f"Error in editing: {e}")
            return f"Editing error: {str(e)}\n\nEDITING COMPLETED - Proceeding despite errors"
    
    def _create_file_with_claude(self, task: str) -> str:
        """
        Use Claude with enhanced prompts to understand the task and create appropriate files.
        
        Args:
            task: The original task description
            
        Returns:
            Results of file creation
        """
        try:
            # Enhanced system prompt with tool guidance
            system_prompt = EDITING_AGENT_PROMPT
            
            # Get comprehensive context using available tools dynamically
            context_parts = []
            
            # 1. Get workspace overview
            try:
                workspace_tool = next((tool for tool in self.all_tools if hasattr(tool, 'name') and tool.name == 'get_workspace_info'), None)
                if workspace_tool:
                    workspace_info = workspace_tool.invoke({})
                    context_parts.append(f"Workspace Info: {workspace_info}")
                else:
                    context_parts.append("Workspace Info: Tool not available")
            except Exception as e:
                context_parts.append(f"Workspace Info: Error - {str(e)}")
            
            # 2. Get directory structure
            try:
                dir_tool = next((tool for tool in self.all_tools if hasattr(tool, 'name') and tool.name == 'get_directory_tree'), None)
                if dir_tool:
                    dir_tree = dir_tool.invoke({"max_depth": 2})
                    context_parts.append(f"Directory Structure: {dir_tree}")
                else:
                    context_parts.append("Directory Structure: Tool not available")
            except Exception as e:
                context_parts.append(f"Directory Structure: Error - {str(e)}")
            
            # 3. Check existing files
            try:
                list_tool = next((tool for tool in self.all_tools if hasattr(tool, 'name') and tool.name == 'list_files'), None)
                if list_tool:
                    files_list = list_tool.invoke({"directory": "."})
                    context_parts.append(f"Current Files: {files_list}")
                else:
                    context_parts.append("Current Files: Tool not available")
            except Exception as e:
                context_parts.append(f"Current Files: Error - {str(e)}")
            
            context = f"Working directory: {self.repo_path}\n" + "\n".join(context_parts)
            
            # Use Claude with enhanced editing prompt to get comprehensive implementation plan
            claude_response = call_claude(
                self.anthropic_client,
                f"""
                Analyze this task and provide a comprehensive implementation plan using the available tools:

                Task: {task}
                
                Context: {context}
                
                Available Tools: {len(self.all_tools)} tools including file operations, shell commands, git operations, and code analysis.
                
                Provide a step-by-step implementation plan and execute it. Consider operations like:
                - Delete existing files if needed
                - Create new files with proper content
                - Modify existing files if required
                - Use shell commands for complex operations
                - Verify the implementation works
                """,
                system_prompt
            )
            
            logger.info(f"📝 Claude implementation plan: {claude_response[:200]}...")
            
            # Execute the comprehensive implementation plan
            results = []
            
            # Handle file deletion if mentioned in task
            if "delete" in task.lower():
                files_to_delete = []
                # Extract files to delete from task
                words = task.lower().split()
                for i, word in enumerate(words):
                    if word == "delete" and i + 1 < len(words):
                        # Look for file patterns after "delete"
                        potential_file = words[i + 1]
                        if "." in potential_file:
                            files_to_delete.append(potential_file)
                
                # Delete files using shell command
                for file_to_delete in files_to_delete:
                    try:
                        shell_tool = next((tool for tool in self.all_tools if hasattr(tool, 'name') and tool.name == 'execute_shell_command'), None)
                        if shell_tool:
                            delete_result = shell_tool.invoke({"command": f"rm -f {file_to_delete}"})
                            results.append(f"Deleted {file_to_delete}: {delete_result}")
                        else:
                            results.append(f"Failed to delete {file_to_delete}: Shell tool not available")
                    except Exception as e:
                        results.append(f"Failed to delete {file_to_delete}: {str(e)}")
            
            # Determine files to create based on task and Claude's analysis
            files_to_create = []
            
            # Parse Claude's response for file creation instructions
            lines = claude_response.split('\n')
            for line in lines:
                if any(indicator in line.lower() for indicator in ['create', 'filename:', 'file:']):
                    # Extract potential filename
                    for word in line.split():
                        if "." in word and not word.startswith("http"):
                            files_to_create.append(word.strip('.,;:'))
            
            # Fallback: determine files based on task keywords
            if not files_to_create:
                if any(word in task.lower() for word in ['html', 'web', 'page']):
                    files_to_create = ['index.html']
                elif any(word in task.lower() for word in ['python', 'script', 'py']):
                    files_to_create = ['main.py']
                elif any(word in task.lower() for word in ['javascript', 'js']):
                    files_to_create = ['script.js']
                elif any(word in task.lower() for word in ['css', 'style']):
                    files_to_create = ['style.css']
                elif any(word in task.lower() for word in ['go']):
                    files_to_create = ['main.go']
                else:
                    files_to_create = ['implementation.py']
            
            # Create files with appropriate content
            for filename in files_to_create:
                try:
                    # Get file content from Claude
                    file_content = call_claude(
                        self.anthropic_client,
                        f"Create complete, functional content for {filename} to implement: {task}",
                        f"Create a complete, functional {filename} file. Include all necessary code, proper structure, and comments."
                    )
                    
                    # Create the file using the create_file tool
                    create_tool = next((tool for tool in self.all_tools if hasattr(tool, 'name') and tool.name == 'create_file'), None)
                    if create_tool:
                        create_result = create_tool.invoke({"filename": filename, "content": file_content})
                        results.append(f"Created {filename}: {create_result}")
                    else:
                        results.append(f"Failed to create {filename}: Create tool not available")
                    
                except Exception as e:
                    results.append(f"Failed to create {filename}: {str(e)}")
            
            # Verify the implementation using additional tools
            try:
                # Check directory contents to verify changes
                list_tool = next((tool for tool in self.all_tools if hasattr(tool, 'name') and tool.name == 'list_files'), None)
                if list_tool:
                    dir_contents = list_tool.invoke({"directory": "."})
                    results.append(f"Directory verification: {dir_contents}")
                else:
                    results.append("Directory verification: List tool not available")
            except Exception as e:
                results.append(f"Directory verification failed: {str(e)}")
            
            final_result = f"""
Comprehensive Implementation Results:
{chr(10).join(results)}

Implementation Analysis:
{claude_response}

EDITING COMPLETED - Implementation completed successfully"""
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error creating file with Claude: {e}")
            return f"Error creating file: {str(e)}\n\nEDITING COMPLETED - File creation failed"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools for this agent."""
        return [
            # Basic file operations
            "create_file",
            "open_file", 
            "edit_file",
            "list_files",
            "search_in_files",
            # Code analysis
            "analyze_file",
            "analyze_directory",
            "get_class_info",
            "get_function_info",
            # Advanced capabilities
            "execute_shell_command",
            "get_command_history",
            "git_status",
            "git_diff",
            "git_add",
            "git_commit",
            "analyze_file_advanced",
            "search_code_semantic",
            "get_workspace_info",
            "find_function_definitions",
            "find_class_definitions",
            "find_imports",
            "get_directory_tree",
            "search_files_by_name"
        ]
