#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""
Netlify Deployment Tool for SWE Agent

Provides deployment capabilities for HTML, CSS, and JavaScript applications to Netlify.
Uses direct HTTP API calls instead of netlify-python SDK to avoid backend bugs.
Only supports static web applications (HTML/CSS/JS) - does not support server-side applications.
"""

import os
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from .netlify_api import deploy_to_netlify_direct


class NetlifyDeployInput(BaseModel):
    """Input for Netlify deployment tool."""
    project_path: str = Field(description="Path to the HTML/CSS/JS project directory to deploy")
    site_name: Optional[str] = Field(default=None, description="Optional site name for the deployment")


class NetlifyDeployTool(BaseTool):
    """
    Deploy HTML, CSS, and JavaScript applications to Netlify.
    
    This tool:
    - Only works with static web applications (HTML, CSS, JavaScript)
    - Creates a zip file of the project
    - Deploys to Netlify using direct API calls
    - Returns the live URL of the deployed site
    
    Requirements:
    - NETLIFY_ACCESS_TOKEN environment variable must be set
    - Project must contain HTML files (index.html preferred)
    - Only static files are supported (no server-side code)
    """
    
    name: str = "deploy_to_netlify"
    description: str = """Deploy applications to Netlify hosting when explicitly requested.
    
    Use this tool ONLY when user specifically asks to:
    - "Deploy to Netlify"
    - "Deploy this app" 
    - "Host on Netlify"
    
    DO NOT use automatically - only when deployment is explicitly requested.
    
    The tool will:
    1. Create a deployment package from any project directory
    2. Deploy to Netlify using direct API calls
    3. Return the live URL
    
    Parameters:
    - project_path: Path to the directory to deploy
    - site_name: (Optional) Name for the Netlify site
    
    Example usage:
    deploy_to_netlify(project_path="./my-app", site_name="my-site")
    """
    args_schema: type = NetlifyDeployInput

    def _run(self, project_path: str, site_name: Optional[str] = None) -> str:
        """Execute Netlify deployment using direct API calls."""
        return deploy_to_netlify_direct(project_path, site_name)


# Create tool instance
netlify_deploy_tool = NetlifyDeployTool()