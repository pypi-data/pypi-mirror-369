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

"""
Security scanning tool for SWE Agent using detect-secrets.
Scans files for potential security vulnerabilities and secrets.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from langchain_core.tools import tool

from detect_secrets import SecretsCollection
from detect_secrets.settings import default_settings


@tool
def scan_file_for_secrets(filename: str) -> Dict[str, Any]:
    """
    Scan a specific file for potential secrets and security vulnerabilities.
    
    Args:
        filename: Path to the file to scan for secrets
        
    Returns:
        Dictionary containing scan results with found secrets and security issues
        
    Example:
        scan_file_for_secrets("config.py")
        scan_file_for_secrets("src/database/connection.py")
    """
    try:
        file_path = Path(filename)
        
        # Check if file exists
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {filename}",
                "secrets_found": 0,
                "scan_results": []
            }
        
        # Initialize secrets collection
        secrets = SecretsCollection()
        
        # Scan the file with default settings
        with default_settings():
            secrets.scan_file(str(file_path))
        
        # Convert results to JSON
        scan_results = secrets.json()
        
        # Count total secrets found
        secrets_count = len(scan_results.get('results', {}).get(str(file_path), []))
        
        return {
            "success": True,
            "file_scanned": filename,
            "secrets_found": secrets_count,
            "scan_results": scan_results,
            "summary": f"Scanned {filename}: {secrets_count} potential secrets found"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error scanning {filename}: {str(e)}",
            "secrets_found": 0,
            "scan_results": []
        }


@tool
def scan_directory_for_secrets(directory_path: str, max_files: int = 50) -> Dict[str, Any]:
    """
    Scan all files in a directory for potential secrets and security vulnerabilities.
    
    Args:
        directory_path: Path to the directory to scan
        max_files: Maximum number of files to scan (default: 50)
        
    Returns:
        Dictionary containing comprehensive scan results for all files
        
    Example:
        scan_directory_for_secrets("./src")
        scan_directory_for_secrets("./config", max_files=10)
    """
    try:
        dir_path = Path(directory_path)
        
        # Check if directory exists
        if not dir_path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {directory_path}",
                "files_scanned": 0,
                "total_secrets": 0,
                "scan_results": {}
            }
        
        # Initialize secrets collection
        secrets = SecretsCollection()
        
        # Find all files to scan (excluding common ignore patterns)
        ignore_patterns = {'.git', '__pycache__', '.pyc', '.log', '.tmp', 'node_modules', '.env.example'}
        files_to_scan = []
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and not any(pattern in str(file_path) for pattern in ignore_patterns):
                files_to_scan.append(file_path)
                if len(files_to_scan) >= max_files:
                    break
        
        # Scan all files with default settings
        with default_settings():
            for file_path in files_to_scan:
                try:
                    secrets.scan_file(str(file_path))
                except Exception as e:
                    # Continue scanning other files if one fails
                    continue
        
        # Convert results to JSON
        scan_results = secrets.json()
        
        # Count total secrets found
        total_secrets = sum(len(files) for files in scan_results.get('results', {}).values())
        
        # Create summary of files with secrets
        files_with_secrets = []
        for file_path, secret_list in scan_results.get('results', {}).items():
            if secret_list:
                files_with_secrets.append({
                    "file": file_path,
                    "secrets_count": len(secret_list),
                    "secret_types": list(set(secret.get('type', 'unknown') for secret in secret_list))
                })
        
        return {
            "success": True,
            "directory_scanned": directory_path,
            "files_scanned": len(files_to_scan),
            "total_secrets": total_secrets,
            "files_with_secrets": len(files_with_secrets),
            "scan_results": scan_results,
            "summary": files_with_secrets,
            "message": f"Scanned {len(files_to_scan)} files in {directory_path}: {total_secrets} potential secrets found in {len(files_with_secrets)} files"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error scanning directory {directory_path}: {str(e)}",
            "files_scanned": 0,
            "total_secrets": 0,
            "scan_results": {}
        }


@tool
def scan_recent_changes_for_secrets(git_diff: bool = True) -> Dict[str, Any]:
    """
    Scan recently modified files for potential secrets and security vulnerabilities.
    
    Args:
        git_diff: Whether to use git diff to identify changed files (default: True)
        
    Returns:
        Dictionary containing scan results for recently modified files
        
    Example:
        scan_recent_changes_for_secrets()
        scan_recent_changes_for_secrets(git_diff=False)
    """
    try:
        # Initialize secrets collection
        secrets = SecretsCollection()
        
        # Get list of recently modified files
        if git_diff:
            # Try to get git diff files
            try:
                import subprocess
                result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'], 
                                      capture_output=True, text=True, cwd='.')
                if result.returncode == 0:
                    modified_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
                else:
                    # Fallback to git status
                    result = subprocess.run(['git', 'status', '--porcelain'], 
                                          capture_output=True, text=True, cwd='.')
                    modified_files = [line[3:].strip() for line in result.stdout.split('\n') 
                                    if line.strip() and not line.startswith('??')]
            except Exception:
                modified_files = []
        else:
            modified_files = []
        
        # If no git files found, scan current directory recent files
        if not modified_files:
            current_dir = Path('.')
            recent_files = []
            for file_path in current_dir.rglob('*'):
                if file_path.is_file():
                    # Check if file was modified recently (within reasonable time)
                    try:
                        mtime = file_path.stat().st_mtime
                        recent_files.append((file_path, mtime))
                    except:
                        continue
            
            # Sort by modification time and take the 10 most recent
            recent_files.sort(key=lambda x: x[1], reverse=True)
            modified_files = [str(f[0]) for f in recent_files[:10]]
        
        # Scan each modified file
        files_scanned = 0
        total_secrets = 0
        
        with default_settings():
            for file_path in modified_files:
                try:
                    if Path(file_path).exists():
                        secrets.scan_file(file_path)
                        files_scanned += 1
                except Exception:
                    continue
        
        # Convert results to JSON
        scan_results = secrets.json()
        
        # Count total secrets found
        total_secrets = sum(len(files) for files in scan_results.get('results', {}).values())
        
        return {
            "success": True,
            "files_scanned": files_scanned,
            "total_secrets": total_secrets,
            "modified_files": modified_files,
            "scan_results": scan_results,
            "message": f"Scanned {files_scanned} recently modified files: {total_secrets} potential secrets found"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error scanning recent changes: {str(e)}",
            "files_scanned": 0,
            "total_secrets": 0,
            "scan_results": {}
        }


# Export the tools for use in other modules
__all__ = ['scan_file_for_secrets', 'scan_directory_for_secrets', 'scan_recent_changes_for_secrets']