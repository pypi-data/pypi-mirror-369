"""
LangGraph Tool Wrappers for Standalone Tools
Converts standalone file operations and code analysis tools into LangGraph callable functions.
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
from langchain.tools import tool
from tools.file_operations import FileOperations
from tools.code_analysis import CodeAnalyzer

logger = logging.getLogger(__name__)

class LangGraphTools:
    """
    Wrapper class that converts standalone tools into LangGraph callable functions.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.file_ops = FileOperations(repo_path)
        self.code_analyzer = CodeAnalyzer(repo_path)
        self._create_tools()
    
    def _create_tools(self):
        """Create LangGraph tools from standalone tools."""
        # Store references to self for closure
        file_ops = self.file_ops
        code_analyzer = self.code_analyzer
        
        @tool
        def create_file(filename: str, content: str) -> str:
            """
            Create a new file with the given content.
            
            Args:
                filename: Name of the file to create
                content: Content to write to the file
                
            Returns:
                Result message
            """
            result = file_ops.create_file(filename, content)
            if result["success"]:
                return f"[OK] Successfully created file: {filename}"
            else:
                return f"[X] Failed to create file: {result.get('error', 'Unknown error')}"
        
        @tool
        def open_file(filename: str, line_number: int = 0, window_size: int = 50) -> str:
            """
            Open and read a file's content.
            
            Args:
                filename: Name of the file to open
                line_number: Starting line number (0-based)
                window_size: Number of lines to read
                
            Returns:
                File content or error message
            """
            result = file_ops.open_file(filename, line_number, window_size)
            if result["success"]:
                return f"📄 File: {filename}\n{result['lines']}"
            else:
                return f"[X] Failed to open file: {result.get('error', 'Unknown error')}"
        
        @tool
        def edit_file(filename: str, new_content: str, line_number: int, num_lines: int = 1) -> str:
            """
            Edit a file by replacing content at specific lines.
            
            Args:
                filename: Name of the file to edit
                new_content: New content to insert
                line_number: Line number to start editing (1-based)
                num_lines: Number of lines to replace
                
            Returns:
                Result message
            """
            result = file_ops.edit_file(filename, new_content, line_number, num_lines)
            if result["success"]:
                return f"[OK] Successfully edited file: {filename}"
            else:
                return f"[X] Failed to edit file: {result.get('error', 'Unknown error')}"
        
        @tool
        def list_files(directory: str = ".") -> str:
            """
            List files and directories in the specified directory.
            
            Args:
                directory: Directory to list (default: current directory)
                
            Returns:
                List of files and directories
            """
            result = file_ops.list_files(directory)
            if result["success"]:
                # Handle both string and dict formats
                files = result["files"]
                if files and isinstance(files[0], dict):
                    files_str = "\n".join([f.get('name', str(f)) for f in files[:20]])
                else:
                    files_str = "\n".join(files[:20])
                
                dirs = result["directories"]
                if dirs and isinstance(dirs[0], dict):
                    dirs_str = "\n".join([d.get('name', str(d)) for d in dirs[:10]])
                else:
                    dirs_str = "\n".join(dirs[:10])
                
                return f"📁 Files:\n{files_str}\n\n📂 Directories:\n{dirs_str}"
            else:
                return f"[X] Failed to list files: {result.get('error', 'Unknown error')}"
        
        @tool
        def search_in_files(pattern: str, file_pattern: str = "*") -> str:
            """
            Search for a pattern in files.
            
            Args:
                pattern: Pattern to search for
                file_pattern: File pattern to search in (default: all files)
                
            Returns:
                Search results
            """
            result = file_ops.search_in_files(pattern, file_pattern)
            if result["success"]:
                return f"[?] Found {result['total_matches']} matches in {result['files_with_matches']} files"
            else:
                return f"[X] Search failed: {result.get('error', 'Unknown error')}"
        
        @tool
        def analyze_file(filename: str) -> str:
            """
            Analyze a code file and extract its structure.
            
            Args:
                filename: Name of the file to analyze
                
            Returns:
                Analysis results
            """
            result = code_analyzer.analyze_file(filename)
            if result["success"]:
                return f"""📊 Code Analysis: {filename}

Language: {result['language']}
Lines: {result['line_count']}
Functions: {len(result['functions'])}
Classes: {len(result['classes'])}
Imports: {len(result['imports'])}

[*] Functions:
{chr(10).join([f"  - {f['name']} (line {f['line_start']})" for f in result['functions'][:10]])}

[P] Classes:
{chr(10).join([f"  - {c['name']} (lines {c['line_start']}-{c['line_end']})" for c in result['classes'][:10]])}"""
            else:
                return f"[X] Analysis failed: {result.get('error', 'Unknown error')}"
        
        @tool
        def analyze_directory(path: str = ".") -> str:
            """
            Analyze the entire directory structure and code.
            
            Args:
                path: Directory path to analyze (default: current directory)
            
            Returns:
                Directory analysis results
            """
            result = code_analyzer.analyze_directory()
            if result["success"]:
                summary = result['summary']
                return f"""📊 Directory Analysis:

Total files: {summary['total_files']}
Total lines: {summary['total_lines']}
Total functions: {summary['total_functions']}
Total classes: {summary['total_classes']}

🗂️ Languages:
{chr(10).join([f"  - {lang}: {count}" for lang, count in summary['languages'].items()])}"""
            else:
                return f"[X] Directory analysis failed: {result.get('error', 'Unknown error')}"
        
        @tool
        def get_class_info(class_name: str) -> str:
            """
            Get detailed information about a specific class.
            
            Args:
                class_name: Name of the class to analyze
                
            Returns:
                Class information
            """
            result = code_analyzer.get_class_info(class_name)
            if result["success"]:
                class_info = result['class_info']
                return f"""[P] Class: {class_info['name']}

File: {result['file_path']}
Lines: {class_info['line_start']}-{class_info['line_end']}

Methods: {len(class_info['methods'])}
{chr(10).join([f"  - {m['name']} (line {m['line_start']})" for m in class_info['methods'][:10]])}"""
            else:
                return f"[X] Class not found: {result.get('error', 'Unknown error')}"
        
        @tool
        def get_function_info(function_name: str) -> str:
            """
            Get detailed information about a specific function.
            
            Args:
                function_name: Name of the function to analyze
                
            Returns:
                Function information
            """
            result = code_analyzer.get_function_info(function_name)
            if result["success"]:
                func_info = result['function_info']
                return f"""[*] Function: {func_info['name']}

File: {result['file_path']}
Lines: {func_info['line_start']}-{func_info['line_end']}
Arguments: {func_info.get('args', 'None')}"""
            else:
                return f"[X] Function not found: {result.get('error', 'Unknown error')}"
        
        # Store tools as instance variables
        self.create_file = create_file
        self.open_file = open_file
        self.edit_file = edit_file
        self.list_files = list_files
        self.search_in_files = search_in_files
        self.analyze_file = analyze_file
        self.analyze_directory = analyze_directory
        self.get_class_info = get_class_info
        self.get_function_info = get_function_info
    
    def get_tools(self) -> List:
        """
        Get all available tools for LangGraph agents.
        
        Returns:
            List of tool functions
        """
        return [
            self.create_file,
            self.open_file,
            self.edit_file,
            self.list_files,
            self.search_in_files,
            self.analyze_file,
            self.analyze_directory,
            self.get_class_info,
            self.get_function_info
        ]
    
    def get_tool_names(self) -> List[str]:
        """
        Get names of all available tools.
        
        Returns:
            List of tool names
        """
        return [
            "create_file",
            "open_file", 
            "edit_file",
            "list_files",
            "search_in_files",
            "analyze_file",
            "analyze_directory",
            "get_class_info",
            "get_function_info"
        ]