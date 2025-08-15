"""
Direct OpenRouter API client for proper tool calling support.
Based on OpenRouter's official documentation and specifications.
"""

import json
import requests
import os
from typing import List, Dict, Any, Optional


class OpenRouterClient:
    """Direct OpenRouter client that implements proper tool calling protocol."""
    
    def __init__(self, api_key: str = None, model: str = "anthropic/claude-sonnet-4", 
                 site_url: str = None, site_name: str = None):
        self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Optional headers for OpenRouter rankings
        if site_url:
            self.headers["HTTP-Referer"] = site_url
        if site_name:
            self.headers["X-Title"] = site_name
    
    def _convert_langchain_tools_to_openrouter(self, langchain_tools: List) -> List[Dict]:
        """Convert LangChain tools to OpenRouter tool schema format."""
        openrouter_tools = []
        
        for tool in langchain_tools:
            # Extract tool information from LangChain tool
            tool_schema = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            
            # Convert args_schema to OpenRouter parameters format
            if hasattr(tool, 'args_schema') and tool.args_schema:
                try:
                    schema_dict = tool.args_schema.schema()
                    if 'properties' in schema_dict:
                        tool_schema["function"]["parameters"]["properties"] = schema_dict["properties"]
                    if 'required' in schema_dict:
                        tool_schema["function"]["parameters"]["required"] = schema_dict["required"]
                except Exception as e:
                    print(f"Warning: Could not extract schema for tool {tool.name}: {e}")
                    # Fallback to basic schema
                    tool_schema["function"]["parameters"] = {
                        "type": "object",
                        "properties": {"input": {"type": "string", "description": "Input for the tool"}},
                        "required": []
                    }
            
            openrouter_tools.append(tool_schema)
        
        return openrouter_tools
    
    def chat_with_tools(self, messages: List[Dict], tools: List = None) -> Dict:
        """
        Make a chat completion request with tools using OpenRouter's format.
        Follows the 3-step OpenRouter protocol.
        """
        # Convert LangChain tools to OpenRouter format
        openrouter_tools = self._convert_langchain_tools_to_openrouter(tools) if tools else []
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 4096
        }
        
        # Add tools if provided
        if openrouter_tools:
            payload["tools"] = openrouter_tools
        
        print(f"🔧 OpenRouter Direct: Making request to {self.model}")
        print(f"🔧 OpenRouter Direct: {len(openrouter_tools)} tools available")
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"❌ OpenRouter API error: {response.status_code} - {response.text}")
                return {"error": f"API error: {response.status_code}"}
            
            result = response.json()
            print(f"✅ OpenRouter Direct: Response received")
            
            return result
            
        except Exception as e:
            print(f"❌ OpenRouter Direct: Request failed: {e}")
            return {"error": str(e)}
    
    def execute_tool_workflow(self, user_message: str, tools: List, max_iterations: int = 3) -> str:
        """
        Execute the complete OpenRouter tool calling workflow with loop prevention:
        1. Send request with tools
        2. Execute any requested tools
        3. Send results back for final response
        """
        # Create tool mapping for execution
        tool_mapping = {tool.name: tool for tool in tools}
        
        # Step 1: Initial request with tools
        messages = [
            {"role": "user", "content": user_message}
        ]
        
        iteration = 0
        executed_tools = set()  # Track executed tools to prevent infinite loops
        
        while iteration < max_iterations:
            iteration += 1
            print(f"🔧 Step {iteration}: Sending request with {len(tools)} tools")
            response = self.chat_with_tools(messages, tools)
            
            if "error" in response:
                return f"Error: {response['error']}"
            
            # Get the assistant's response
            assistant_message = response["choices"][0]["message"]
            messages.append(assistant_message)
            
            # Check if there are tool calls
            if "tool_calls" in assistant_message and assistant_message["tool_calls"]:
                print(f"🔧 Found {len(assistant_message['tool_calls'])} tool calls")
                
                has_new_tools = False
                # Execute each tool call
                for tool_call in assistant_message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_call_id = tool_call["id"]
                    
                    # Handle arguments - could be string or dict
                    arguments = tool_call["function"]["arguments"]
                    if isinstance(arguments, str):
                        try:
                            tool_args = json.loads(arguments) if arguments.strip() else {}
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON decode error for tool {tool_name}: {e}")
                            tool_args = {}
                    else:
                        tool_args = arguments if arguments else {}
                    
                    # Create a unique identifier for this tool call
                    tool_signature = f"{tool_name}:{str(sorted(tool_args.items()) if tool_args else '')}"
                    
                    # Check if we've already executed this exact tool call
                    if tool_signature in executed_tools:
                        print(f"🔄 Skipping duplicate tool call: {tool_name}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "name": tool_name,
                            "content": "Tool already executed in this workflow"
                        })
                        continue
                    
                    executed_tools.add(tool_signature)
                    has_new_tools = True
                    
                    print(f"🔧 Executing tool: {tool_name} with args: {tool_args}")
                    
                    try:
                        if tool_name in tool_mapping:
                            # Execute the tool
                            result = tool_mapping[tool_name].invoke(tool_args)
                            
                            # Add tool result to messages
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "name": tool_name,
                                "content": json.dumps(result) if not isinstance(result, str) else str(result)
                            })
                            
                            print(f"✅ Tool {tool_name} executed successfully")
                        else:
                            print(f"❌ Tool {tool_name} not found")
                            messages.append({
                                "role": "tool", 
                                "tool_call_id": tool_call_id,
                                "name": tool_name,
                                "content": f"Error: Tool {tool_name} not found"
                            })
                            
                    except Exception as e:
                        print(f"❌ Tool execution error: {e}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call_id, 
                            "name": tool_name,
                            "content": f"Error executing tool: {str(e)}"
                        })
                
                # If no new tools were executed, break the loop
                if not has_new_tools:
                    print("🔧 No new tools to execute, completing workflow")
                    break
                    
            else:
                # No tool calls, return the direct response
                print("🔧 No tool calls found, completing workflow")
                return assistant_message["content"]
        
        # After the loop, check if we have a response to return
        if messages and len(messages) > 1:
            # Look for the most recent assistant message
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get("role") == "assistant" and msg.get("content"):
                    print(f"🔧 Workflow completed with {len(executed_tools)} tools executed")
                    return msg["content"]
                elif hasattr(msg, 'content') and hasattr(msg, 'role') and msg.content:
                    print(f"🔧 Workflow completed with {len(executed_tools)} tools executed")
                    return msg.content
        
        # If no suitable response found, get a final completion
        print(f"🔧 Final Step: Getting completion response (iteration {iteration})")
        
        # Force a final response by asking for completion
        messages.append({
            "role": "user", 
            "content": "Please provide your final response based on the tool results above. Do not call any more tools."
        })
        
        final_response = self.chat_with_tools(messages, [])  # No tools for final response
        
        if "error" in final_response:
            return f"Error in final response: {final_response['error']}"
        
        return final_response["choices"][0]["message"]["content"]