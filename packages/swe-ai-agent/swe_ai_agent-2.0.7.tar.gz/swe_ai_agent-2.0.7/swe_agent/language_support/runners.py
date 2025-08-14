"""
Language-agnostic code runners using Claude's natural understanding.
No hardcoded language rules - pure LLM-based execution and testing.
"""

import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from utils.anthropic_client import get_anthropic_client

logger = logging.getLogger(__name__)

class UniversalCodeRunner:
    """
    Universal code runner that can execute and test code in any language
    through Claude's natural language comprehension.
    """
    
    def __init__(self):
        self.anthropic_client = get_anthropic_client()
        logger.info(">>> Universal code runner initialized")
    
    def analyze_execution_requirements(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze project to determine execution requirements.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Execution requirements analysis
        """
        # Get project structure and key files
        key_files = self._get_execution_relevant_files(project_path)
        
        prompt = f"""
        Analyze this project to determine how to run, test, and deploy it:

        Project files and content:
        {key_files}

        Provide comprehensive execution analysis including:
        1. Required runtime environments (versions, dependencies)
        2. Build commands and compilation steps
        3. How to run the application (entry points, commands)
        4. Testing framework and test execution commands
        5. Development server setup and configuration
        6. Environment variables and configuration needed
        7. Database setup and migration commands
        8. Deployment process and requirements
        9. Monitoring and logging setup
        10. Performance testing approaches

        Focus on practical, actionable commands that can be executed.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}],
            system="You are a DevOps expert who can analyze any project and provide comprehensive execution instructions."
        )
        
        return {
            "analysis": response.content,
            "project_path": str(project_path),
            "analysis_type": "execution_requirements"
        }
    
    def generate_run_commands(self, project_path: Path, task_type: str) -> Dict[str, Any]:
        """
        Generate specific run commands for different tasks.
        
        Args:
            project_path: Path to project directory
            task_type: Type of task (run, test, build, deploy, etc.)
            
        Returns:
            Generated run commands
        """
        execution_analysis = self.analyze_execution_requirements(project_path)
        
        prompt = f"""
        Based on this execution analysis, generate specific commands for: {task_type}

        Execution Analysis:
        {execution_analysis['analysis']}

        Generate specific, executable commands for the task type: {task_type}
        
        Provide:
        1. Step-by-step commands to execute
        2. Required environment setup
        3. Pre-requisites and dependencies
        4. Expected output or success indicators
        5. Common issues and troubleshooting
        6. Alternative approaches if main approach fails

        Format as actionable shell commands that can be executed directly.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
            system="You are a command-line expert who can generate executable commands for any development task."
        )
        
        return {
            "commands": response.content,
            "task_type": task_type,
            "project_path": str(project_path),
            "based_on_analysis": execution_analysis['analysis']
        }
    
    def execute_command(self, command: str, project_path: Path, timeout: int = 300) -> Dict[str, Any]:
        """
        Execute a command and capture results.
        
        Args:
            command: Command to execute
            project_path: Working directory for command
            timeout: Command timeout in seconds
            
        Returns:
            Execution result
        """
        logger.info(f"Executing command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": timeout,  # Approximate
                "working_directory": str(project_path)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "command": command,
                "error": f"Command timed out after {timeout} seconds",
                "working_directory": str(project_path)
            }
        except Exception as e:
            return {
                "success": False,
                "command": command,
                "error": str(e),
                "working_directory": str(project_path)
            }
    
    def run_tests(self, project_path: Path) -> Dict[str, Any]:
        """
        Run tests for the project.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Test execution results
        """
        test_commands = self.generate_run_commands(project_path, "test")
        
        # Extract commands from the analysis
        commands_text = test_commands['commands']
        
        prompt = f"""
        Extract the specific test commands from this analysis:

        {commands_text}

        Provide just the shell commands to run tests, one per line.
        Include setup commands if needed.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
            system="Extract only the executable shell commands from the analysis."
        )
        
        # Execute test commands
        test_results = []
        for command in response.content.strip().split('\n'):
            if command.strip():
                result = self.execute_command(command.strip(), project_path)
                test_results.append(result)
        
        return {
            "test_commands": test_commands,
            "execution_results": test_results,
            "overall_success": all(r.get("success", False) for r in test_results),
            "project_path": str(project_path)
        }
    
    def build_project(self, project_path: Path) -> Dict[str, Any]:
        """
        Build the project.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Build execution results
        """
        build_commands = self.generate_run_commands(project_path, "build")
        
        # Extract commands from the analysis
        commands_text = build_commands['commands']
        
        prompt = f"""
        Extract the specific build commands from this analysis:

        {commands_text}

        Provide just the shell commands to build the project, one per line.
        Include setup commands if needed.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
            system="Extract only the executable shell commands from the analysis."
        )
        
        # Execute build commands
        build_results = []
        for command in response.content.strip().split('\n'):
            if command.strip():
                result = self.execute_command(command.strip(), project_path)
                build_results.append(result)
        
        return {
            "build_commands": build_commands,
            "execution_results": build_results,
            "overall_success": all(r.get("success", False) for r in build_results),
            "project_path": str(project_path)
        }
    
    def run_application(self, project_path: Path) -> Dict[str, Any]:
        """
        Run the main application.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Application run results
        """
        run_commands = self.generate_run_commands(project_path, "run")
        
        # Extract commands from the analysis
        commands_text = run_commands['commands']
        
        prompt = f"""
        Extract the specific run commands from this analysis:

        {commands_text}

        Provide just the shell commands to run the application, one per line.
        Include setup commands if needed.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
            system="Extract only the executable shell commands from the analysis."
        )
        
        # Execute run commands (with shorter timeout for long-running apps)
        run_results = []
        for command in response.content.strip().split('\n'):
            if command.strip():
                result = self.execute_command(command.strip(), project_path, timeout=30)
                run_results.append(result)
        
        return {
            "run_commands": run_commands,
            "execution_results": run_results,
            "project_path": str(project_path)
        }
    
    def debug_execution_issues(self, project_path: Path, error_details: str) -> Dict[str, Any]:
        """
        Debug execution issues and provide solutions.
        
        Args:
            project_path: Path to project directory
            error_details: Details of the error encountered
            
        Returns:
            Debug analysis and solutions
        """
        execution_analysis = self.analyze_execution_requirements(project_path)
        
        prompt = f"""
        Debug these execution issues:

        Error Details:
        {error_details}

        Project Execution Analysis:
        {execution_analysis['analysis']}

        Provide debugging help including:
        1. Root cause analysis of the error
        2. Step-by-step troubleshooting approach
        3. Specific commands to diagnose the issue
        4. Multiple solution approaches
        5. Environment setup fixes
        6. Dependency resolution steps
        7. Configuration corrections
        8. Prevention strategies for future

        Focus on practical, actionable solutions.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
            system="You are a debugging expert who can troubleshoot execution issues for any technology stack."
        )
        
        return {
            "debug_analysis": response.content,
            "error_details": error_details,
            "project_path": str(project_path),
            "analysis_type": "debug_execution"
        }
    
    def _get_execution_relevant_files(self, project_path: Path) -> str:
        """Get files relevant to execution analysis."""
        exec_patterns = [
            "package.json", "requirements.txt", "go.mod", "Cargo.toml",
            "pom.xml", "build.gradle", "composer.json", "Gemfile",
            "Makefile", "Dockerfile", "docker-compose.yml",
            "main.*", "index.*", "app.*", "server.*", "run.*",
            "test.*", "spec.*", "*.config.*", "*.env*"
        ]
        
        exec_files = []
        for pattern in exec_patterns:
            try:
                for file_path in project_path.glob(f"**/{pattern}"):
                    if file_path.is_file() and file_path.stat().st_size < 50000:
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            relative_path = file_path.relative_to(project_path)
                            exec_files.append(f"=== {relative_path} ===\n{content[:2000]}\n")
                        except Exception:
                            continue
            except Exception:
                continue
        
        return "\n".join(exec_files[:25])  # Limit to 25 files


def get_language_runner() -> UniversalCodeRunner:
    """Get universal code runner instance."""
    return UniversalCodeRunner()