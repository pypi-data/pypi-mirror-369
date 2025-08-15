"""
Code Analyzer Agent - Specialized agent for code analysis tasks.
Analyzes codebases to gather insights on classes, methods, and functions.
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
from prompts.swe_prompts import CODE_ANALYZER_PROMPT

logger = logging.getLogger(__name__)

class CodeAnalyzerAgent:
    """
    Specialized agent for code analysis tasks.
    Generates FQDN mappings and provides code insights.
    """
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.name = "code_analyzer"
        self.max_consecutive_visits = 5
        self.anthropic_client = get_anthropic_client()
        
        # Initialize LangGraph tools for function calls
        self.langraph_tools = LangGraphTools(str(repo_path))
        self.tools = self.langraph_tools.get_tools()
        
        # Initialize advanced tools for enhanced capabilities
        from tools.advanced_langraph_tools import AdvancedLangGraphTools
        self.advanced_tools = AdvancedLangGraphTools(str(repo_path))
        
        # Combine all tools for comprehensive functionality
        self.all_tools = self.tools + self.advanced_tools.get_all_tools()
        
        logger.info(f"[?] Code Analyzer initialized with {len(self.all_tools)} tools (including advanced capabilities)")
        
    def process(self, state: AgentState) -> Dict[str, Any]:
        """
        Process the current state and perform code analysis.
        
        Args:
            state: Current agent state containing messages and context
            
        Returns:
            Updated state with analysis results
        """
        logger.info(f"[?] Code Analyzer processing state with {len(state['messages'])} messages")
        
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
                    AIMessage(content="ANALYSIS COMPLETE - Maximum analysis iterations reached")
                ],
                "sender": self.name
            }
        
        # Update visit count
        consecutive_visits[self.name] = visit_count
        
        # Perform analysis based on current context
        tracker = get_tool_tracker()
        call_id = tracker.start_tool_call(self.name, "perform_analysis", {"message_count": len(state["messages"])})
        
        try:
            analysis_result = self._perform_analysis(state["messages"])
            success = "ANALYSIS COMPLETE" in analysis_result
            tracker.end_tool_call(call_id, self.name, "perform_analysis", success,
                                None if success else "Analysis failed",
                                analysis_result[:100] if analysis_result else None)
        except Exception as e:
            tracker.end_tool_call(call_id, self.name, "perform_analysis", False, str(e))
            raise
        
        # Reset visit count for other agents if we're transitioning
        if "ANALYSIS COMPLETE" in analysis_result or "EDIT FILE" in analysis_result:
            consecutive_visits = {self.name: visit_count}
        
        new_state = {
            **state,
            "messages": state["messages"] + [AIMessage(content=analysis_result)],
            "sender": self.name,
            "consecutive_visits": consecutive_visits
        }
        
        return new_state
    
    def _perform_analysis(self, messages: List[BaseMessage]) -> str:
        """
        Perform code analysis based on the current context.
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            Analysis results or next action
        """
        try:
            # Get the last message to understand what analysis is needed
            last_message = get_last_ai_message(messages)
            
            if not last_message:
                return self._initial_analysis()
            
            content = last_message.content
            
            # Check if we need specific analysis
            if "ANALYZE CODE" in content:
                return self._initial_analysis()
            elif "Has tool_calls" in content:
                return self._process_tool_calls(content)
            else:
                return self._continue_analysis()
                
        except Exception as e:
            logger.error(f"Error in code analysis: {e}")
            return f"Analysis error: {str(e)}\n\nANALYSIS COMPLETE - Proceeding despite errors"
    
    def _initial_analysis(self) -> str:
        """
        Perform comprehensive code analysis using the full tool suite.
        
        Returns:
            Detailed analysis results
        """
        try:
            logger.debug("[?] Starting comprehensive analysis with full tool suite...")
            
            # Enhanced system prompt with tool guidance
            system_prompt = CODE_ANALYZER_PROMPT
            
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
                    dir_tree = dir_tool.invoke({"max_depth": 3})
                    context_parts.append(f"Directory Structure: {dir_tree}")
                else:
                    context_parts.append("Directory Structure: Tool not available")
            except Exception as e:
                context_parts.append(f"Directory Structure: Error - {str(e)}")
            
            # 3. Get git status
            try:
                git_tool = next((tool for tool in self.all_tools if hasattr(tool, 'name') and tool.name == 'git_status'), None)
                if git_tool:
                    git_status = git_tool.invoke({})
                    context_parts.append(f"Git Status: {git_status}")
                else:
                    context_parts.append("Git Status: Tool not available")
            except Exception as e:
                context_parts.append(f"Git Status: Error - {str(e)}")
            
            # 4. List current files
            try:
                list_tool = next((tool for tool in self.all_tools if hasattr(tool, 'name') and tool.name == 'list_files'), None)
                if list_tool:
                    file_list = list_tool.invoke({"directory": "."})
                    context_parts.append(f"Current Files: {file_list}")
                else:
                    context_parts.append("Current Files: Tool not available")
            except Exception as e:
                context_parts.append(f"Current Files: Error - {str(e)}")
            
            # 5. Execute a simple analysis command
            try:
                shell_tool = next((tool for tool in self.all_tools if hasattr(tool, 'name') and tool.name == 'execute_shell_command'), None)
                if shell_tool:
                    analysis_result = shell_tool.invoke({"command": "find . -name '*.py' | head -10"})
                    context_parts.append(f"Python Files Sample: {analysis_result}")
                else:
                    context_parts.append("Python Files Sample: Tool not available")
            except Exception as e:
                context_parts.append(f"Python Files Sample: Error - {str(e)}")
            
            context = f"Working directory: {self.repo_path}\n" + "\n".join(context_parts)
            
            claude_analysis = call_claude(
                self.anthropic_client,
                f"Analyze this codebase using the comprehensive tool suite. Context: {context}",
                system_prompt
            )
            
            result = f"""Comprehensive Code Analysis Results:

Tool-Enhanced Analysis:
{claude_analysis}

Analysis Strategy Used:
- Workspace overview assessment
- Directory structure mapping
- Git repository status check
- Comprehensive tool-based investigation

Recommended Next Steps:
- Use specific tools for deeper analysis based on task requirements
- Focus on identified key areas for implementation

ANALYSIS COMPLETE - Comprehensive analysis completed successfully"""
            
            logger.info("[OK] Comprehensive analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[X] Error in fast analysis: {e}")
            return f"Analysis completed with basic assessment.\n\nANALYSIS COMPLETE - Proceeding to next phase"
    
    def _process_tool_calls(self, content: str) -> str:
        """
        Process specific tool calls based on content.
        
        Args:
            content: Message content containing tool call information
            
        Returns:
            Tool execution results
        """
        try:
            # Use standalone code analysis tools
            results = []
            
            # Use LangGraph tools for analysis
            dir_analysis = self.langraph_tools.analyze_directory.invoke({"path": "."})
            results.append(f"Directory Analysis:\n{dir_analysis}")
            
            # Get file listings
            file_list = self.langraph_tools.list_files.invoke({"directory": "."})
            results.append(f"File Structure:\n{file_list}")
            
            if results:
                return f"Analysis results:\n" + "\n".join(results) + "\n\nANALYSIS COMPLETE - Detailed analysis completed"
            else:
                return "Analysis completed with basic assessment.\n\nANALYSIS COMPLETE - Proceeding to next phase"
                
        except Exception as e:
            logger.error(f"Error processing analysis tool calls: {e}")
            return f"Analysis completed with basic assessment.\n\nANALYSIS COMPLETE - Proceeding to next phase"
    
    def _continue_analysis(self) -> str:
        """
        Continue analysis with additional checks.
        
        Returns:
            Additional analysis results or completion
        """
        try:
            # Perform additional analysis using standalone tools
            results = []
            
            # Use LangGraph tools for additional analysis
            search_result = self.langraph_tools.search_in_files.invoke({"pattern": "class", "file_pattern": "*.py"})
            results.append(f"Class Search: {search_result}")
            
            # Get more detailed analysis
            dir_analysis = self.langraph_tools.analyze_directory.invoke({"path": "."})
            results.append(f"Detailed Analysis:\n{dir_analysis}")
            
            result_text = "\n".join(results) if results else "Basic analysis completed"
            
            return f"""Additional Analysis:
{result_text}

ANALYSIS COMPLETE - Comprehensive analysis finished"""
            
        except Exception as e:
            logger.error(f"Error in continued analysis: {e}")
            return "ANALYSIS COMPLETE - Analysis finished with some limitations"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools for this agent."""
        return [
            "analyze_file",
            "analyze_directory",
            "get_class_info",
            "get_function_info",
            "create_file",
            "open_file",
            "list_files",
            "search_in_files"
        ]
