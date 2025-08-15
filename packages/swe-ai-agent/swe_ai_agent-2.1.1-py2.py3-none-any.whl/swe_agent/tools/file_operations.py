"""
Standalone file operations tools for the SWE Agent system.
Extracted from the composio file tools without dependencies.
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class FileOperations:
    """
    Standalone file operations class providing comprehensive file management capabilities.
    """
    
    def __init__(self, base_path: str = None, show_diffs: bool = True, debug_mode: bool = False):
        """
        Initialize file operations with a base working directory.
        
        Args:
            base_path: Base directory for file operations (default: current directory)
            show_diffs: Enable diff visualization for file operations
            debug_mode: Enable debug mode with variable dumps
        """
        self.base_path = Path(base_path or os.getcwd()).resolve()
        self.current_file = None
        self.file_history = []
        self.show_diffs = show_diffs
        self.debug_mode = debug_mode
        
    def create_file(self, file_path: str, content: str = "", is_directory: bool = False) -> Dict[str, Any]:
        """
        Create a new file or directory.
        
        Args:
            file_path: Path to create (relative to base_path)
            content: Initial content for the file (ignored for directories)
            is_directory: Whether to create a directory instead of a file
            
        Returns:
            Dict with 'success', 'path', 'message', and optional 'error'
        """
        try:
            full_path = self.base_path / file_path
            
            if is_directory:
                full_path.mkdir(parents=True, exist_ok=True)
                return {
                    "success": True,
                    "path": str(full_path),
                    "message": f"Directory created: {file_path}"
                }
            else:
                # Create parent directories if they don't exist
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create the file with content
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "success": True,
                    "path": str(full_path),
                    "message": f"File created: {file_path}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "path": file_path,
                "message": f"Failed to create {'directory' if is_directory else 'file'}: {file_path}",
                "error": str(e)
            }
    
    def open_file(self, file_path: str, line_number: int = 0, window_size: int = 100) -> Dict[str, Any]:
        """
        Open a file and return its content with line numbers.
        
        Args:
            file_path: Path to the file (relative to base_path)
            line_number: Starting line number (0-based)
            window_size: Number of lines to return
            
        Returns:
            Dict with 'success', 'content', 'lines', 'message', and optional 'error'
        """
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "error": "FileNotFoundError"
                }
            
            if full_path.is_dir():
                return {
                    "success": False,
                    "message": f"Cannot open directory: {file_path}",
                    "error": "IsADirectoryError"
                }
            
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Set current file for editing
            self.current_file = full_path
            
            # Calculate line range
            start_line = max(0, line_number)
            end_line = min(len(lines), start_line + window_size)
            
            # Format lines with line numbers
            formatted_lines = []
            for i, line in enumerate(lines[start_line:end_line], start=start_line + 1):
                formatted_lines.append(f"{i:4d}: {line.rstrip()}")
            
            return {
                "success": True,
                "content": ''.join(lines),
                "lines": '\n'.join(formatted_lines),
                "total_lines": len(lines),
                "showing_lines": f"{start_line + 1}-{end_line}",
                "message": f"File opened: {file_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error opening file: {file_path}",
                "error": str(e)
            }
    
    def edit_file(self, file_path: str = None, text: str = "", start_line: int = 1, 
                  end_line: int = None) -> Dict[str, Any]:
        """
        Edit a file by replacing content at specific line numbers.
        
        Args:
            file_path: Path to file (if None, uses current file)
            text: New text content
            start_line: Starting line number (1-based)
            end_line: Ending line number (1-based, inclusive)
            
        Returns:
            Dict with 'success', 'old_text', 'new_text', 'message', and optional 'error'
        """
        try:
            if file_path:
                target_path = self.base_path / file_path
                self.current_file = target_path
            elif self.current_file:
                target_path = self.current_file
            else:
                return {
                    "success": False,
                    "message": "No file specified and no current file open",
                    "error": "NoFileError"
                }
            
            if not target_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {target_path}",
                    "error": "FileNotFoundError"
                }
            
            # Read current content
            with open(target_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Convert to 0-based indexing
            start_idx = start_line - 1
            end_idx = end_line - 1 if end_line else start_idx
            
            # Validate line numbers
            if start_idx < 0 or start_idx >= len(lines):
                return {
                    "success": False,
                    "message": f"Invalid start line: {start_line}",
                    "error": "InvalidLineNumber"
                }
            
            if end_idx < start_idx:
                return {
                    "success": False,
                    "message": f"End line {end_line} cannot be before start line {start_line}",
                    "error": "InvalidLineRange"
                }
            
            # Store old text
            old_text = ''.join(lines[start_idx:end_idx + 1])
            
            # Apply edit
            new_lines = lines[:start_idx] + [text + '\n'] + lines[end_idx + 1:]
            
            # Write back to file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            return {
                "success": True,
                "old_text": old_text.rstrip(),
                "new_text": text,
                "message": f"File edited: {target_path.name}",
                "lines_modified": f"{start_line}-{end_line or start_line}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error editing file: {str(e)}",
                "error": str(e)
            }
    
    def write_file(self, file_path: str, content: str, append: bool = False) -> Dict[str, Any]:
        """
        Write content to a file, completely replacing or appending.
        
        Args:
            file_path: Path to the file
            content: Content to write
            append: Whether to append to existing content
            
        Returns:
            Dict with 'success', 'message', and optional 'error'
        """
        try:
            full_path = self.base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(full_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"Content {'appended to' if append else 'written to'} file: {file_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error writing file: {file_path}",
                "error": str(e)
            }
    
    def list_files(self, directory: str = ".", pattern: str = None, 
                   include_hidden: bool = False) -> Dict[str, Any]:
        """
        List files and directories in a given directory.
        
        Args:
            directory: Directory to list (relative to base_path)
            pattern: File pattern to match (e.g., "*.py")
            include_hidden: Whether to include hidden files
            
        Returns:
            Dict with 'success', 'files', 'directories', 'message', and optional 'error'
        """
        try:
            full_path = self.base_path / directory
            
            if not full_path.exists():
                return {
                    "success": False,
                    "message": f"Directory not found: {directory}",
                    "error": "DirectoryNotFoundError"
                }
            
            if not full_path.is_dir():
                return {
                    "success": False,
                    "message": f"Not a directory: {directory}",
                    "error": "NotADirectoryError"
                }
            
            files = []
            directories = []
            
            for item in full_path.iterdir():
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                if pattern and not item.match(pattern):
                    continue
                
                if item.is_dir():
                    directories.append(item.name)
                else:
                    files.append({
                        "name": item.name,
                        "size": item.stat().st_size,
                        "modified": item.stat().st_mtime
                    })
            
            return {
                "success": True,
                "files": sorted(files, key=lambda x: x['name']),
                "directories": sorted(directories),
                "message": f"Listed {len(files)} files and {len(directories)} directories"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error listing directory: {directory}",
                "error": str(e)
            }
    
    def find_files(self, pattern: str, directory: str = ".", case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Find files matching a pattern recursively.
        
        Args:
            pattern: Pattern to search for
            directory: Directory to search in
            case_sensitive: Whether to use case-sensitive matching
            
        Returns:
            Dict with 'success', 'matches', 'message', and optional 'error'
        """
        try:
            full_path = self.base_path / directory
            
            if not full_path.exists():
                return {
                    "success": False,
                    "message": f"Directory not found: {directory}",
                    "error": "DirectoryNotFoundError"
                }
            
            matches = []
            
            for item in full_path.rglob(pattern):
                if item.is_file():
                    relative_path = item.relative_to(self.base_path)
                    matches.append(str(relative_path))
            
            return {
                "success": True,
                "matches": sorted(matches),
                "count": len(matches),
                "message": f"Found {len(matches)} files matching pattern '{pattern}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error finding files: {pattern}",
                "error": str(e)
            }
    
    def search_in_files(self, query: str, file_pattern: str = "*.py", 
                       directory: str = ".", case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search for text within files.
        
        Args:
            query: Text to search for
            file_pattern: Pattern for files to search in
            directory: Directory to search in
            case_sensitive: Whether to use case-sensitive search
            
        Returns:
            Dict with 'success', 'matches', 'message', and optional 'error'
        """
        try:
            full_path = self.base_path / directory
            matches = []
            
            for file_path in full_path.rglob(file_pattern):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        file_matches = []
                        for line_num, line in enumerate(lines, 1):
                            search_line = line if case_sensitive else line.lower()
                            search_query = query if case_sensitive else query.lower()
                            
                            if search_query in search_line:
                                file_matches.append({
                                    "line_number": line_num,
                                    "line_content": line.rstrip(),
                                    "match_start": search_line.find(search_query)
                                })
                        
                        if file_matches:
                            relative_path = file_path.relative_to(self.base_path)
                            matches.append({
                                "file": str(relative_path),
                                "matches": file_matches
                            })
                    
                    except (UnicodeDecodeError, PermissionError):
                        # Skip files that can't be read
                        continue
            
            total_matches = sum(len(file_match["matches"]) for file_match in matches)
            
            return {
                "success": True,
                "matches": matches,
                "files_with_matches": len(matches),
                "total_matches": total_matches,
                "message": f"Found {total_matches} matches in {len(matches)} files"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error searching in files: {query}",
                "error": str(e)
            }
    
    def rename_file(self, old_path: str, new_path: str) -> Dict[str, Any]:
        """
        Rename or move a file/directory.
        
        Args:
            old_path: Current path
            new_path: New path
            
        Returns:
            Dict with 'success', 'message', and optional 'error'
        """
        try:
            old_full_path = self.base_path / old_path
            new_full_path = self.base_path / new_path
            
            if not old_full_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {old_path}",
                    "error": "FileNotFoundError"
                }
            
            # Create parent directories if needed
            new_full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Rename/move the file
            old_full_path.rename(new_full_path)
            
            return {
                "success": True,
                "message": f"Renamed {old_path} to {new_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error renaming file: {old_path} to {new_path}",
                "error": str(e)
            }
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file or directory.
        
        Args:
            file_path: Path to delete
            
        Returns:
            Dict with 'success', 'message', and optional 'error'
        """
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "error": "FileNotFoundError"
                }
            
            if full_path.is_dir():
                shutil.rmtree(full_path)
                return {
                    "success": True,
                    "message": f"Directory deleted: {file_path}"
                }
            else:
                full_path.unlink()
                return {
                    "success": True,
                    "message": f"File deleted: {file_path}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error deleting file: {file_path}",
                "error": str(e)
            }
    
    def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """
        Copy a file or directory.
        
        Args:
            source: Source path
            destination: Destination path
            
        Returns:
            Dict with 'success', 'message', and optional 'error'
        """
        try:
            source_path = self.base_path / source
            dest_path = self.base_path / destination
            
            if not source_path.exists():
                return {
                    "success": False,
                    "message": f"Source not found: {source}",
                    "error": "FileNotFoundError"
                }
            
            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                return {
                    "success": True,
                    "message": f"Directory copied: {source} to {destination}"
                }
            else:
                shutil.copy2(source_path, dest_path)
                return {
                    "success": True,
                    "message": f"File copied: {source} to {destination}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error copying: {source} to {destination}",
                "error": str(e)
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file or directory.
        
        Args:
            file_path: Path to analyze
            
        Returns:
            Dict with file information and optional 'error'
        """
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "error": "FileNotFoundError"
                }
            
            stat = full_path.stat()
            
            return {
                "success": True,
                "path": str(full_path),
                "name": full_path.name,
                "size": stat.st_size,
                "is_directory": full_path.is_dir(),
                "is_file": full_path.is_file(),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "permissions": oct(stat.st_mode)[-3:],
                "message": f"File info retrieved for: {file_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting file info: {file_path}",
                "error": str(e)
            }