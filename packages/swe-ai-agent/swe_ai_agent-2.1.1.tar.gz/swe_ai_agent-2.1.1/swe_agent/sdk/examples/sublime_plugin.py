"""
Sublime Text Plugin Example for SWE Agent Integration

This example demonstrates how to integrate SWE Agent into Sublime Text
using the SWE Agent SDK.

Installation:
1. Copy this file to your Sublime Text Packages/User directory
2. Install the SWE Agent SDK in your Sublime Text Python environment
3. Configure the plugin settings in Preferences > Package Settings > SWE Agent

Usage:
- Ctrl+Shift+P -> "SWE Agent: Execute Task"
- Right-click context menu -> "SWE Agent: Fix This"
- Command palette -> "SWE Agent: Analyze Code"
"""

import sublime
import sublime_plugin
import threading
import os
import sys
from pathlib import Path

# Add the SWE Agent SDK to the Python path
# Adjust this path to where your SWE Agent SDK is installed
SDK_PATH = os.path.expanduser("~/swe-agent-sdk")
if SDK_PATH not in sys.path:
    sys.path.append(SDK_PATH)

try:
    from sdk import SWEAgentClient, TaskRequest, TaskStatus
    from sdk.exceptions import SWEAgentException
    SDK_AVAILABLE = True
except ImportError as e:
    print(f"SWE Agent SDK not available: {e}")
    SDK_AVAILABLE = False


class SweAgentExecuteTaskCommand(sublime_plugin.TextCommand):
    """Command to execute a custom task with SWE Agent"""
    
    def run(self, edit):
        if not SDK_AVAILABLE:
            sublime.error_message("SWE Agent SDK is not installed or not accessible")
            return
        
        # Get task from user input
        self.view.window().show_input_panel(
            "Enter task description:",
            "",
            self.on_task_entered,
            None,
            None
        )
    
    def on_task_entered(self, task_text):
        if not task_text.strip():
            return
        
        # Get current file context
        context_files = []
        current_file = self.view.file_name()
        if current_file:
            context_files.append(current_file)
        
        # Create task request
        request = TaskRequest(
            task=task_text,
            context_files=context_files,
            working_directory=self._get_working_directory()
        )
        
        # Execute task in background
        self._execute_task_async(request)
    
    def _execute_task_async(self, request):
        """Execute task asynchronously to avoid blocking UI"""
        def run_task():
            try:
                client = SWEAgentClient(
                    working_directory=request.working_directory,
                    log_level="INFO"
                )
                
                # Show progress in status bar
                sublime.status_message("SWE Agent: Executing task...")
                
                response = client.execute_task(request)
                
                # Handle response
                if response.status == TaskStatus.COMPLETED:
                    sublime.status_message("SWE Agent: Task completed successfully")
                    self._show_result(response)
                else:
                    sublime.status_message(f"SWE Agent: Task failed - {response.error}")
                    sublime.error_message(f"Task failed: {response.error}")
                    
            except SWEAgentException as e:
                sublime.status_message("SWE Agent: Task failed")
                sublime.error_message(f"SWE Agent error: {str(e)}")
            except Exception as e:
                sublime.status_message("SWE Agent: Unexpected error")
                sublime.error_message(f"Unexpected error: {str(e)}")
        
        thread = threading.Thread(target=run_task)
        thread.daemon = True
        thread.start()
    
    def _show_result(self, response):
        """Show task result in a new tab"""
        window = self.view.window()
        result_view = window.new_file()
        result_view.set_name(f"SWE Agent Result - {response.task_id[:8]}")
        result_view.set_scratch(True)
        
        # Format result content
        content = f"""SWE Agent Task Result
====================
Task ID: {response.task_id}
Status: {response.status.value}
Execution Time: {response.execution_time:.2f}s
Timestamp: {response.timestamp}

Result:
{response.result or 'No result content'}

Tools Used:
{', '.join(response.tools_used) if response.tools_used else 'None'}

Files Modified:
{', '.join(response.files_modified) if response.files_modified else 'None'}

Agent Visits:
{response.agent_visits if response.agent_visits else 'None'}
"""
        
        result_view.run_command('append', {'characters': content})
        result_view.set_read_only(True)
    
    def _get_working_directory(self):
        """Get the working directory for the current project"""
        window = self.view.window()
        if window.project_data():
            folders = window.project_data().get('folders', [])
            if folders:
                return folders[0].get('path', os.getcwd())
        
        current_file = self.view.file_name()
        if current_file:
            return os.path.dirname(current_file)
        
        return os.getcwd()


class SweAgentFixThisCommand(sublime_plugin.TextCommand):
    """Command to fix code issues at cursor position"""
    
    def run(self, edit):
        if not SDK_AVAILABLE:
            sublime.error_message("SWE Agent SDK is not installed")
            return
        
        # Get current selection or line
        selection = self.view.sel()[0]
        if selection.empty():
            # If no selection, use current line
            line = self.view.line(selection)
            code_text = self.view.substr(line)
            line_number = self.view.rowcol(line.begin())[0] + 1
        else:
            code_text = self.view.substr(selection)
            line_number = self.view.rowcol(selection.begin())[0] + 1
        
        current_file = self.view.file_name()
        if not current_file:
            sublime.error_message("Please save the file first")
            return
        
        # Create task to fix the code
        task = f"Fix the following code issue in {os.path.basename(current_file)} at line {line_number}:\n\n{code_text}"
        
        request = TaskRequest(
            task=task,
            context_files=[current_file],
            working_directory=self._get_working_directory()
        )
        
        self._execute_task_async(request)
    
    def _execute_task_async(self, request):
        """Execute fix task asynchronously"""
        def run_task():
            try:
                client = SWEAgentClient(
                    working_directory=request.working_directory,
                    log_level="INFO"
                )
                
                sublime.status_message("SWE Agent: Analyzing and fixing code...")
                
                response = client.execute_task(request)
                
                if response.status == TaskStatus.COMPLETED:
                    sublime.status_message("SWE Agent: Code fix completed")
                    # The file should be automatically updated by the agent
                    # Refresh the view
                    sublime.set_timeout(lambda: self.view.run_command('revert'), 1000)
                else:
                    sublime.status_message(f"SWE Agent: Fix failed - {response.error}")
                    sublime.error_message(f"Fix failed: {response.error}")
                    
            except Exception as e:
                sublime.status_message("SWE Agent: Fix failed")
                sublime.error_message(f"Error: {str(e)}")
        
        thread = threading.Thread(target=run_task)
        thread.daemon = True
        thread.start()
    
    def _get_working_directory(self):
        """Get the working directory for the current project"""
        window = self.view.window()
        if window.project_data():
            folders = window.project_data().get('folders', [])
            if folders:
                return folders[0].get('path', os.getcwd())
        
        current_file = self.view.file_name()
        if current_file:
            return os.path.dirname(current_file)
        
        return os.getcwd()


class SweAgentAnalyzeCodeCommand(sublime_plugin.TextCommand):
    """Command to analyze code quality and structure"""
    
    def run(self, edit):
        if not SDK_AVAILABLE:
            sublime.error_message("SWE Agent SDK is not installed")
            return
        
        current_file = self.view.file_name()
        if not current_file:
            sublime.error_message("Please save the file first")
            return
        
        # Create analysis task
        task = f"Analyze the code in {os.path.basename(current_file)} and provide insights on code quality, structure, potential issues, and improvement suggestions"
        
        request = TaskRequest(
            task=task,
            context_files=[current_file],
            working_directory=self._get_working_directory()
        )
        
        self._execute_task_async(request)
    
    def _execute_task_async(self, request):
        """Execute analysis task asynchronously"""
        def run_task():
            try:
                client = SWEAgentClient(
                    working_directory=request.working_directory,
                    log_level="INFO"
                )
                
                sublime.status_message("SWE Agent: Analyzing code...")
                
                response = client.execute_task(request)
                
                if response.status == TaskStatus.COMPLETED:
                    sublime.status_message("SWE Agent: Code analysis completed")
                    self._show_analysis_result(response)
                else:
                    sublime.status_message(f"SWE Agent: Analysis failed - {response.error}")
                    sublime.error_message(f"Analysis failed: {response.error}")
                    
            except Exception as e:
                sublime.status_message("SWE Agent: Analysis failed")
                sublime.error_message(f"Error: {str(e)}")
        
        thread = threading.Thread(target=run_task)
        thread.daemon = True
        thread.start()
    
    def _show_analysis_result(self, response):
        """Show analysis result in a new tab"""
        window = self.view.window()
        result_view = window.new_file()
        result_view.set_name("SWE Agent - Code Analysis")
        result_view.set_scratch(True)
        
        # Format analysis content
        content = f"""SWE Agent Code Analysis
=====================
File: {self.view.file_name()}
Analysis Time: {response.timestamp}
Execution Time: {response.execution_time:.2f}s

{response.result or 'No analysis result'}

Tools Used: {', '.join(response.tools_used) if response.tools_used else 'None'}
"""
        
        result_view.run_command('append', {'characters': content})
        result_view.set_read_only(True)
        result_view.set_syntax_file("Packages/Markdown/Markdown.sublime-syntax")
    
    def _get_working_directory(self):
        """Get the working directory for the current project"""
        window = self.view.window()
        if window.project_data():
            folders = window.project_data().get('folders', [])
            if folders:
                return folders[0].get('path', os.getcwd())
        
        current_file = self.view.file_name()
        if current_file:
            return os.path.dirname(current_file)
        
        return os.getcwd()


class SweAgentStatusCommand(sublime_plugin.ApplicationCommand):
    """Command to show SWE Agent status"""
    
    def run(self):
        if not SDK_AVAILABLE:
            sublime.error_message("SWE Agent SDK is not installed")
            return
        
        try:
            client = SWEAgentClient()
            status = client.get_agent_status()
            
            status_text = f"""SWE Agent Status
===============
Running: {status.is_running}
Uptime: {status.uptime:.2f}s
Total Tasks: {status.total_tasks}
Successful: {status.successful_tasks}
Failed: {status.failed_tasks}
Available Agents: {[agent.value for agent in status.agents_available]}
"""
            
            sublime.message_dialog(status_text)
            
        except Exception as e:
            sublime.error_message(f"Error getting status: {str(e)}")


# Add context menu items
class SweAgentContextMenu(sublime_plugin.EventListener):
    """Add SWE Agent options to context menu"""
    
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "swe_agent_available":
            return SDK_AVAILABLE
        return None