"""
SPDX-License-Identifier: Apache-2.0

Direct Netlify API client using requests library.
Replaces the problematic netlify-python SDK.
"""

import os
import json
import zipfile
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()

class NetlifyAPIClient:
    """Direct Netlify API client using HTTP requests."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.netlify.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "SWE-Agent (swe-agent@replit.com)",
            "Content-Type": "application/json"
        }
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user information."""
        response = requests.get(f"{self.base_url}/user", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def list_sites(self) -> list:
        """List all sites for the user."""
        response = requests.get(f"{self.base_url}/sites", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_site(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new site."""
        data = {}
        if name:
            data["name"] = name
            
        response = requests.post(
            f"{self.base_url}/sites", 
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def deploy_zip_to_site(self, site_id: str, zip_path: str) -> Dict[str, Any]:
        """Deploy a ZIP file to an existing site."""
        zip_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "SWE-Agent (swe-agent@replit.com)",
            "Content-Type": "application/zip"
        }
        
        with open(zip_path, 'rb') as zip_file:
            response = requests.post(
                f"{self.base_url}/sites/{site_id}/deploys",
                headers=zip_headers,
                data=zip_file.read()
            )
        response.raise_for_status()
        return response.json()
    
    def create_and_deploy_zip(self, zip_path: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new site and deploy ZIP file in one request."""
        zip_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "SWE-Agent (swe-agent@replit.com)",
            "Content-Type": "application/zip"
        }
        
        url = f"{self.base_url}/sites"
        if name:
            url += f"?name={name}"
            
        with open(zip_path, 'rb') as zip_file:
            response = requests.post(
                url,
                headers=zip_headers,
                data=zip_file.read()
            )
        response.raise_for_status()
        return response.json()
    
    def get_deploy_status(self, site_id: str, deploy_id: str) -> Dict[str, Any]:
        """Get deployment status."""
        response = requests.get(
            f"{self.base_url}/sites/{site_id}/deploys/{deploy_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


def deploy_to_netlify_direct(project_path: str, site_name: Optional[str] = None) -> str:
    """
    Deploy project to Netlify using direct API calls.
    
    Args:
        project_path: Path to the project directory
        site_name: Optional name for the site
        
    Returns:
        Deployment result message
    """
    # Check for access token
    access_token = os.getenv('NETLIFY_ACCESS_TOKEN')
    if not access_token:
        return """❌ Error: NETLIFY_ACCESS_TOKEN environment variable not set.

To deploy to Netlify:
1. Go to https://app.netlify.com/user/applications  
2. Create a Personal Access Token
3. Set the environment variable: NETLIFY_ACCESS_TOKEN=your_token_here
4. Try deployment again"""

    project_path_obj = Path(project_path).resolve()
    if not project_path_obj.exists():
        return f"❌ Error: Project path '{project_path}' does not exist."
        
    if not project_path_obj.is_dir():
        return f"❌ Error: '{project_path}' is not a directory."

    try:
        # Create Netlify API client
        client = NetlifyAPIClient(access_token)
        
        # Get current user information
        user_info = client.get_current_user()
        console.print(f"✅ Authenticated as: {user_info.get('email', 'Unknown')}")
        
        # Create deployment zip
        zip_path = f"{project_path_obj.name}_deploy.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in project_path_obj.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    arc_name = file_path.relative_to(project_path_obj)
                    zip_file.write(file_path, arc_name)
                    
        console.print(f"📦 Created deployment package: {zip_path}")
        
        try:
            # Try to create new site and deploy in one request
            if site_name:
                console.print(f"🚀 Creating new site: {site_name}")
                deploy_result = client.create_and_deploy_zip(zip_path, site_name)
            else:
                console.print("🚀 Creating new site with auto-generated name")
                deploy_result = client.create_and_deploy_zip(zip_path)
                
            # Extract URLs and info
            site_url = deploy_result.get('ssl_url') or deploy_result.get('url', 'Unknown')
            deploy_url = deploy_result.get('deploy_ssl_url') or deploy_result.get('deploy_url', site_url)
            site_id = deploy_result.get('site_id', 'Unknown')
            deploy_id = deploy_result.get('id', 'Unknown')
            actual_name = deploy_result.get('name', site_name or 'auto-generated')
            
            return f"""✅ Successfully deployed to Netlify!

🌐 Live URL: {site_url}
🔗 Deploy URL: {deploy_url}
📦 Site ID: {site_id}
📝 Site Name: {actual_name}
👤 Deployed by: {user_info.get('full_name', user_info.get('email', 'Unknown'))}
📁 Project: {project_path_obj.name}
🚀 Deploy ID: {deploy_id}

Your HTML/CSS/JS application is now live and accessible worldwide!"""
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # Fallback to existing site approach
                console.print("⚠️ Site creation failed, using existing site...")
                sites = client.list_sites()
                if sites:
                    existing_site = sites[0]
                    console.print(f"📝 Using existing site: {existing_site['name']}")
                    
                    deploy_result = client.deploy_zip_to_site(existing_site['id'], zip_path)
                    
                    site_url = existing_site.get('ssl_url') or existing_site.get('url', 'Unknown')
                    deploy_url = deploy_result.get('deploy_ssl_url') or deploy_result.get('deploy_url', site_url)
                    
                    return f"""✅ Successfully deployed to Netlify!

🌐 Live URL: {site_url}
🔗 Deploy URL: {deploy_url}
📦 Site ID: {existing_site['id']}
📝 Site Name: {existing_site['name']}
👤 Deployed by: {user_info.get('full_name', user_info.get('email', 'Unknown'))}
📁 Project: {project_path_obj.name}
🚀 Deploy ID: {deploy_result['id']}

Your HTML/CSS/JS application is now live and accessible worldwide!"""
                else:
                    raise Exception("Cannot create new site and no existing sites available")
            else:
                raise
                
    except Exception as e:
        error_msg = str(e)
        if "500" in error_msg or "Internal Server Error" in error_msg:
            return f"""❌ Netlify API Error: Server error - this may be a temporary issue.

Solutions:
1. Wait a few minutes and try again
2. Check Netlify Status: https://www.netlifystatus.com/
3. Your token is valid, so this is not an authentication issue

Technical details: {type(e).__name__}: {error_msg}"""
        else:
            return f"""❌ Deployment failed: {error_msg}

Common solutions:
1. Verify NETLIFY_ACCESS_TOKEN is correct
2. Check network connection
3. Try again with a different site name
4. Check Netlify Status: https://www.netlifystatus.com/

Error details: {type(e).__name__}: {error_msg}"""
    finally:
        # Clean up zip file
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.unlink(zip_path)