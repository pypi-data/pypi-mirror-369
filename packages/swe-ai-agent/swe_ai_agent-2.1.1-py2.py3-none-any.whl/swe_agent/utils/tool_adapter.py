"""
Tool Adapter for unified tool calling across different AI providers.
Handles protocol differences between Anthropic and OpenRouter/OpenAI tool calling formats.
"""

import json
import logging
from typing import List, Dict, Any, Union
from langchain_core.tools import StructuredTool
from langchain_core.messages import AIMessage, ToolMessage

logger = logging.getLogger(__name__)

class ToolCallAdapter:
    """
    Adapts tool calling between different AI providers to handle protocol differences.
    """
    
    def __init__(self, provider: str):
        """
        Initialize tool adapter for specific provider.
        
        Args:
            provider: "anthropic" or "openrouter"
        """
        self.provider = provider.lower()
    
    def normalize_tool_response(self, response: AIMessage) -> AIMessage:
        """
        Normalize tool calling response format between providers.
        
        Args:
            response: AI response with potential tool calls
            
        Returns:
            Normalized AIMessage with consistent tool call format
        """
        if not hasattr(response, 'tool_calls') or not response.tool_calls:
            return response
            
        # Handle OpenRouter tool call format differences
        if self.provider == "openrouter":
            return self._normalize_openrouter_response(response)
        else:
            return response
    
    def should_wait_for_tool_result(self, response: AIMessage) -> bool:
        """
        Check if the response contains tool calls that need results.
        
        Args:
            response: AI response to check
            
        Returns:
            True if tool calls need results, False otherwise
        """
        return (hasattr(response, 'tool_calls') and 
                response.tool_calls and 
                len(response.tool_calls) > 0)
    
    def _normalize_openrouter_response(self, response: AIMessage) -> AIMessage:
        """
        Normalize OpenRouter tool call response to match expected format.
        
        Args:
            response: OpenRouter AIMessage with tool calls
            
        Returns:
            Normalized AIMessage
        """
        try:
            normalized_tool_calls = []
            
            for tool_call in response.tool_calls:
                # Ensure tool call has required fields
                normalized_call = {
                    "id": getattr(tool_call, "id", f"call_{len(normalized_tool_calls)}"),
                    "name": getattr(tool_call, "name", "unknown_tool"),
                    "args": getattr(tool_call, "args", {}),
                    "type": "tool_use"
                }
                normalized_tool_calls.append(normalized_call)
            
            # Create new response with normalized tool calls
            normalized_response = AIMessage(
                content=response.content or "",
                tool_calls=normalized_tool_calls,
                name=getattr(response, "name", None),
                id=getattr(response, "id", None)
            )
            
            return normalized_response
            
        except Exception as e:
            logger.warning(f"Failed to normalize OpenRouter tool response: {e}")
            return response
    
    def create_tool_result_message(self, tool_call_id: str, tool_name: str, 
                                 result: str, success: bool = True) -> ToolMessage:
        """
        Create a standardized tool result message.
        
        Args:
            tool_call_id: ID of the tool call
            tool_name: Name of the tool that was called
            result: Result of the tool execution
            success: Whether the tool call was successful
            
        Returns:
            ToolMessage with standardized format
        """
        return ToolMessage(
            content=result,
            tool_call_id=tool_call_id,
            name=tool_name,
            additional_kwargs={"success": success}
        )
    
    def validate_tool_call(self, tool_call: Dict[str, Any]) -> bool:
        """
        Validate that a tool call has the required format.
        
        Args:
            tool_call: Tool call dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["name"]
        
        if self.provider == "openrouter":
            required_fields.extend(["id"])
        
        return all(field in tool_call for field in required_fields)

def create_tool_adapter(provider: str) -> ToolCallAdapter:
    """
    Factory function to create appropriate tool adapter.
    
    Args:
        provider: "anthropic" or "openrouter"
        
    Returns:
        Configured ToolCallAdapter
    """
    return ToolCallAdapter(provider)