# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 SWE Agent
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# MCP Server Integration Examples

This document provides examples for integrating Model Context Protocol (MCP) servers with SWE Agent to extend its capabilities with external services.

## Overview

MCP (Model Context Protocol) allows SWE Agent to connect to external servers that provide specialized capabilities like:
- Mathematical computations
- Weather information
- File system access
- Database operations
- API integrations
- Custom business logic

## Configuration

### 1. Default Configuration

SWE Agent comes with DeepWiki MCP server pre-configured for GitHub repository documentation access. The `.swe_mcp_config.json` file includes:

```json
{
  "_description": "MCP Server Configuration for SWE Agent",
  "deepwiki": {
    "url": "https://mcp.deepwiki.com/sse",
    "transport": "streamable_http",
    "description": "DeepWiki MCP server for GitHub repository documentation and AI-powered search capabilities"
  },
  "_examples": {
    "math_server": {
      "command": "python",
      "args": ["/path/to/math_server.py"],
      "transport": "stdio",
      "description": "Math computation server"
    },
    "weather_server": {
      "url": "http://localhost:8000/mcp",
      "transport": "streamable_http",
      "description": "Weather information server"
    },
    "file_server": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/path/to/allowed/directory"],
      "transport": "stdio",
      "description": "Filesystem access server"
    }
  }
}
```

### 2. DeepWiki MCP Server (Default)

The DeepWiki server provides three main capabilities:
- **`ask_question`**: Ask questions about GitHub repositories with AI-powered responses
- **`read_wiki_contents`**: Retrieve formatted documentation content
- **`read_wiki_structure`**: Get repository structure and navigation

This server requires no authentication and works with public GitHub repositories through deepwiki.com.

### 2. Active Server Configuration

Remove the `_` prefix to activate servers:

```json
{
  "math_server": {
    "command": "python",
    "args": ["/home/user/servers/math_server.py"],
    "transport": "stdio",
    "description": "Math computation server"
  },
  "weather_server": {
    "url": "http://localhost:8000/mcp",
    "transport": "streamable_http",
    "description": "Weather information server"
  }
}
```

## Usage Examples

### 1. Managing MCP Servers

```python
# List configured servers
result = manage_mcp_servers("list")

# Get integration status
result = manage_mcp_servers("info")

# List available tools from MCP servers
result = manage_mcp_servers("tools")

# Add a new server
config = {
    "command": "python",
    "args": ["/path/to/math_server.py"],
    "transport": "stdio",
    "description": "Math computation server"
}
result = manage_mcp_servers("add", name="math", config=config)

# Remove a server
result = manage_mcp_servers("remove", name="math")
```

### 2. SWE Agent Task Examples

**GitHub Repository Documentation (Default):**
```
User: Create documentation for this repository based on its structure

SWE Agent will:
1. Use DeepWiki MCP server to analyze repository structure
2. Ask questions about code patterns and architecture
3. Generate comprehensive documentation from repository knowledge
```

**Code Learning and Analysis:**
```
User: Help me understand how React hooks work by finding examples

SWE Agent will:
1. Use DeepWiki to search React repository documentation
2. Find relevant hook implementations and examples
3. Create educational examples based on official patterns
```

**Mathematical Computation:**
```
User: Create a calculator that can compute complex mathematical expressions

SWE Agent will:
1. Check available MCP tools for math capabilities
2. Use math server tools for complex calculations
3. Implement calculator using external math services
```

**Weather-Aware Applications:**
```
User: Build a weather dashboard that shows current conditions

SWE Agent will:
1. Configure weather MCP server
2. Use weather tools to fetch current conditions
3. Create dashboard displaying real-time weather data
```

**File System Integration:**
```
User: Create a file browser with search capabilities

SWE Agent will:
1. Set up filesystem MCP server
2. Use file system tools for directory traversal
3. Implement search using MCP file operations
```

## Common MCP Server Types

### 1. Mathematical Computation Server

```python
# Example math_server.py
import json
import sys
from typing import Any, Dict

def handle_math_request(operation: str, operands: list) -> Dict[str, Any]:
    if operation == "add":
        return {"result": sum(operands)}
    elif operation == "multiply":
        return {"result": operands[0] * operands[1] if len(operands) >= 2 else 0}
    elif operation == "factorial":
        import math
        return {"result": math.factorial(operands[0]) if operands else 0}
    else:
        return {"error": "Unknown operation"}

# MCP server implementation would handle the protocol details
```

### 2. Weather Information Server

```python
# Example weather server integration
import requests

def get_weather(location: str) -> Dict[str, Any]:
    # Integrate with weather API
    api_key = "your_weather_api_key"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    response = requests.get(url)
    return response.json()
```

### 3. Database Integration Server

```python
# Example database MCP server
import sqlite3

def query_database(query: str) -> Dict[str, Any]:
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return {"data": results}
```

## Best Practices

### 1. Security Considerations

- **Limit File Access**: Configure filesystem servers with restricted directory access
- **API Key Management**: Store API keys securely, not in configuration files
- **Network Security**: Use HTTPS for HTTP-based MCP servers
- **Input Validation**: Validate all inputs to MCP servers

### 2. Performance Optimization

- **Connection Pooling**: Reuse MCP connections when possible
- **Caching**: Implement caching for frequently requested data
- **Timeouts**: Set appropriate timeouts for MCP operations
- **Error Handling**: Gracefully handle MCP server failures

### 3. Development Workflow

1. **Start Simple**: Begin with basic MCP servers (math, file access)
2. **Test Incrementally**: Test each MCP server independently
3. **Monitor Performance**: Track MCP tool usage and performance
4. **Document APIs**: Document custom MCP server capabilities

## Troubleshooting

### Common Issues

1. **Server Not Starting**
   - Check server command and arguments
   - Verify file paths and permissions
   - Review server logs for errors

2. **Connection Failures**
   - Verify network connectivity for HTTP servers
   - Check port availability
   - Validate server configuration

3. **Tool Not Available**
   - Confirm server initialization completed
   - Check MCP client connection status
   - Verify tool registration

### Debugging Commands

```python
# Check MCP integration status
manage_mcp_servers("info")

# List configured servers
manage_mcp_servers("list")

# View available tools
manage_mcp_servers("tools")
```

## Advanced Integration

### Custom MCP Server Development

For complex integrations, you can develop custom MCP servers:

1. **Follow MCP Protocol**: Implement the standard MCP protocol
2. **Define Tools**: Specify available tools and their schemas
3. **Handle Requests**: Process tool invocation requests
4. **Return Results**: Provide structured responses

### Integration with SWE Workflows

MCP servers can be integrated into complex SWE workflows:

```python
# Example: Weather-aware deployment script
def deploy_with_weather_check():
    # Check weather conditions
    weather = manage_mcp_servers("invoke_tool", 
                                server="weather", 
                                tool="get_weather", 
                                location="production_center")
    
    # Deploy only if weather is favorable
    if weather.get("condition") == "clear":
        # Proceed with deployment
        execute_shell_command("./deploy.sh")
    else:
        # Delay deployment
        print("Deployment delayed due to weather conditions")
```

This integration allows SWE Agent to make intelligent decisions based on external data and services, significantly expanding its capabilities beyond traditional code analysis and editing.