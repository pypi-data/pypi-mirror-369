"""
Editing Tools - Specialized tools for file editing and navigation.
Contains tools for navigating codebases, editing files, and managing changes.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import shutil
import difflib
from datetime import datetime
from tools.file_operations import FileOperations
from tools.code_analysis import CodeAnalyzer

logger = logging.getLogger(__name__)

class EditingTools:
    """
    Specialized tools for file editing and navigation tasks.
    Used by the Editor agent for file modifications.
    """
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.output_dir = repo_path / "output"
        self.backup_dir = repo_path / "output" / "backups"
        self.output_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        self.current_file = None
        self.file_content = None
        self.changes_made = []
        
        # Initialize standalone file operations (no composio dependency)
        self.file_ops = FileOperations(str(repo_path))
        self.code_analyzer = CodeAnalyzer(str(repo_path))
        
    def navigate_codebase(self) -> str:
        """
        Navigate through the codebase to identify files for editing.
        
        Returns:
            Navigation results and file recommendations
        """
        try:
            navigation_info = {
                "python_files": [],
                "config_files": [],
                "recently_modified": [],
                "large_files": [],
                "recommendations": []
            }
            
            # Get all Python files
            for py_file in self.repo_path.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue
                    
                stat = py_file.stat()
                file_info = {
                    "path": str(py_file.relative_to(self.repo_path)),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "lines": len(py_file.read_text().split('\n')) if stat.st_size < 1000000 else 0
                }
                navigation_info["python_files"].append(file_info)
                
                # Identify large files
                if stat.st_size > 10000:  # Files larger than 10KB
                    navigation_info["large_files"].append(file_info)
            
            # Get config files
            config_patterns = ["*.json", "*.yaml", "*.yml", "*.toml", "*.cfg", "*.ini"]
            for pattern in config_patterns:
                for config_file in self.repo_path.rglob(pattern):
                    if config_file.name.startswith('.'):
                        continue
                    navigation_info["config_files"].append(
                        str(config_file.relative_to(self.repo_path))
                    )
            
            # Sort by modification time to find recently modified files
            navigation_info["python_files"].sort(key=lambda x: x["modified"], reverse=True)
            navigation_info["recently_modified"] = navigation_info["python_files"][:5]
            
            # Generate recommendations
            if navigation_info["python_files"]:
                navigation_info["recommendations"].append(
                    f"Found {len(navigation_info['python_files'])} Python files"
                )
                navigation_info["recommendations"].append(
                    f"Most recently modified: {navigation_info['recently_modified'][0]['path']}"
                )
            
            # Save navigation info
            nav_file = self.output_dir / "navigation_info.json"
            with open(nav_file, 'w') as f:
                json.dump(navigation_info, f, indent=2)
            
            summary = f"Codebase Navigation:\n"
            summary += f"- Python files: {len(navigation_info['python_files'])}\n"
            summary += f"- Config files: {len(navigation_info['config_files'])}\n"
            summary += f"- Large files: {len(navigation_info['large_files'])}\n"
            summary += f"Navigation info saved to: {nav_file}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error navigating codebase: {e}")
            return f"Error navigating codebase: {str(e)}"
    
    def open_file_for_editing(self, file_path: Optional[str] = None) -> str:
        """
        Open a file for editing.
        
        Args:
            file_path: Path to the file to open (optional)
            
        Returns:
            File content or selection prompt
        """
        try:
            if not file_path:
                # Select a file automatically
                py_files = list(self.repo_path.rglob("*.py"))
                if py_files:
                    file_path = str(py_files[0].relative_to(self.repo_path))
                else:
                    return "No Python files found in the repository"
            
            target_file = self.repo_path / file_path
            
            if not target_file.exists():
                return f"File not found: {file_path}"
            
            # Read file content
            self.file_content = target_file.read_text()
            self.current_file = target_file
            
            # Create backup
            backup_path = self.backup_dir / f"{target_file.name}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(target_file, backup_path)
            
            # Return file preview
            lines = self.file_content.split('\n')
            preview = '\n'.join(lines[:20])  # First 20 lines
            
            summary = f"Opened file for editing: {file_path}\n"
            summary += f"- Lines: {len(lines)}\n"
            summary += f"- Size: {len(self.file_content)} characters\n"
            summary += f"- Backup created: {backup_path}\n\n"
            summary += f"File preview:\n{preview}"
            
            if len(lines) > 20:
                summary += f"\n... ({len(lines) - 20} more lines)"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return f"Error opening file: {str(e)}"
    
    def perform_edit(self, edit_type: str = "sample", target_line: Optional[int] = None, 
                    new_content: Optional[str] = None) -> str:
        """
        Perform an edit operation on the current file.
        
        Args:
            edit_type: Type of edit to perform
            target_line: Line number to edit (optional)
            new_content: New content to insert (optional)
            
        Returns:
            Edit operation results
        """
        try:
            if not self.current_file or not self.file_content:
                return "No file currently open for editing"
            
            lines = self.file_content.split('\n')
            original_content = self.file_content
            
            if edit_type == "sample":
                # Perform a sample edit - add a comment
                if lines:
                    # Find a good place to add a comment
                    insert_line = min(5, len(lines))
                    lines.insert(insert_line, "# SWE Agent: Code analysis and editing completed")
                    edit_description = f"Added comment at line {insert_line + 1}"
                else:
                    lines.append("# SWE Agent: New file created")
                    edit_description = "Added comment to new file"
                    
            elif edit_type == "function_docstring":
                # Add docstrings to functions without them
                edit_description = self._add_function_docstrings(lines)
                
            elif edit_type == "import_optimization":
                # Optimize imports
                edit_description = self._optimize_imports(lines)
                
            elif edit_type == "custom" and target_line and new_content:
                # Custom edit at specific line
                if 0 <= target_line - 1 < len(lines):
                    lines[target_line - 1] = new_content
                    edit_description = f"Modified line {target_line}"
                else:
                    return f"Invalid line number: {target_line}"
            else:
                # Default: add improvement comment
                lines.insert(0, "# SWE Agent: File processed for improvements")
                edit_description = "Added processing comment"
            
            # Update file content
            self.file_content = '\n'.join(lines)
            
            # Track changes
            change_record = {
                "timestamp": datetime.now().isoformat(),
                "file": str(self.current_file.relative_to(self.repo_path)),
                "edit_type": edit_type,
                "description": edit_description,
                "lines_before": len(original_content.split('\n')),
                "lines_after": len(lines)
            }
            self.changes_made.append(change_record)
            
            # Generate diff
            diff = list(difflib.unified_diff(
                original_content.split('\n'),
                self.file_content.split('\n'),
                fromfile=f"a/{self.current_file.name}",
                tofile=f"b/{self.current_file.name}",
                lineterm=''
            ))
            
            newline = '\n'
            summary = f"Edit operation completed:{newline}"
            summary += f"- Type: {edit_type}{newline}"
            summary += f"- Description: {edit_description}{newline}"
            orig_lines = len(original_content.split('\n'))
            new_lines = len(lines)
            summary += f"- Lines changed: {orig_lines} -> {new_lines}{newline}"
            
            if diff:
                summary += f"\nDiff preview:\n" + '\n'.join(diff[:10])
                if len(diff) > 10:
                    summary += f"\n... ({len(diff) - 10} more diff lines)"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error performing edit: {e}")
            return f"Error performing edit: {str(e)}"
    
    def execute_edit(self) -> str:
        """
        Execute the edit by saving changes to the file.
        
        Returns:
            Execution results
        """
        try:
            if not self.current_file or not self.file_content:
                return "No file currently open for editing"
            
            # Write changes to file
            self.current_file.write_text(self.file_content)
            
            summary = f"Edit executed successfully:\n"
            summary += f"- File: {self.current_file.relative_to(self.repo_path)}\n"
            summary += f"- Changes applied: {len(self.changes_made)}\n"
            summary += f"- Final size: {len(self.file_content)} characters\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error executing edit: {e}")
            return f"Error executing edit: {str(e)}"
    
    def save_file(self, file_path: Optional[str] = None) -> str:
        """
        Save the current file or a specific file.
        
        Args:
            file_path: Path to save file (optional)
            
        Returns:
            Save operation results
        """
        try:
            if file_path:
                target_file = self.repo_path / file_path
                if self.file_content:
                    target_file.write_text(self.file_content)
                    return f"File saved: {file_path}"
                else:
                    return f"No content to save to {file_path}"
            else:
                return self.execute_edit()
                
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return f"Error saving file: {str(e)}"
    
    def create_backup(self, file_path: Optional[str] = None) -> str:
        """
        Create a backup of the current or specified file.
        
        Args:
            file_path: Path to backup (optional)
            
        Returns:
            Backup creation results
        """
        try:
            if file_path:
                source_file = self.repo_path / file_path
            else:
                source_file = self.current_file
            
            if not source_file or not source_file.exists():
                return "No file to backup"
            
            backup_name = f"{source_file.name}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(source_file, backup_path)
            
            return f"Backup created: {backup_path}"
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return f"Error creating backup: {str(e)}"
    
    def validate_changes(self) -> str:
        """
        Validate the changes made to the file.
        
        Returns:
            Validation results
        """
        try:
            if not self.current_file or not self.file_content:
                return "No file currently open for validation"
            
            validation_results = {
                "syntax_valid": True,
                "syntax_errors": [],
                "warnings": [],
                "changes_summary": self.changes_made
            }
            
            # Check Python syntax
            if self.current_file.suffix == '.py':
                try:
                    compile(self.file_content, str(self.current_file), 'exec')
                    validation_results["syntax_valid"] = True
                except SyntaxError as e:
                    validation_results["syntax_valid"] = False
                    validation_results["syntax_errors"].append(str(e))
            
            # Check for potential issues
            lines = self.file_content.split('\n')
            for i, line in enumerate(lines):
                if len(line) > 100:
                    validation_results["warnings"].append(f"Line {i+1}: Long line ({len(line)} chars)")
                if line.strip().startswith('print(') and not line.strip().startswith('# print('):
                    validation_results["warnings"].append(f"Line {i+1}: Debug print statement")
            
            # Save validation results
            validation_file = self.output_dir / "validation_results.json"
            with open(validation_file, 'w') as f:
                json.dump(validation_results, f, indent=2)
            
            summary = f"Validation Results:\n"
            summary += f"- Syntax valid: {validation_results['syntax_valid']}\n"
            summary += f"- Syntax errors: {len(validation_results['syntax_errors'])}\n"
            summary += f"- Warnings: {len(validation_results['warnings'])}\n"
            summary += f"- Changes made: {len(self.changes_made)}\n"
            
            if validation_results["syntax_errors"]:
                summary += f"\nSyntax errors:\n" + '\n'.join(validation_results["syntax_errors"])
            
            return summary
            
        except Exception as e:
            logger.error(f"Error validating changes: {e}")
            return f"Error validating changes: {str(e)}"
    
    def perform_additional_edits(self) -> str:
        """
        Perform additional editing operations.
        
        Returns:
            Additional editing results
        """
        try:
            if not self.current_file or not self.file_content:
                return "No file currently open for additional editing"
            
            additional_edits = []
            lines = self.file_content.split('\n')
            
            # Add type hints where missing
            for i, line in enumerate(lines):
                if line.strip().startswith('def ') and '-> ' not in line and ':' in line:
                    # This is a simplified type hint addition
                    if line.strip().endswith(':'):
                        lines[i] = line.rstrip(':') + ' -> None:'
                        additional_edits.append(f"Added return type hint at line {i+1}")
            
            # Add TODO comments for complex functions
            for i, line in enumerate(lines):
                if line.strip().startswith('def ') and len(line) > 50:
                    # Insert TODO comment before complex function
                    lines.insert(i, '    # TODO: Consider breaking down this complex function')
                    additional_edits.append(f"Added TODO comment before line {i+1}")
                    break  # Only add one TODO per session
            
            # Update file content
            self.file_content = '\n'.join(lines)
            
            # Track additional changes
            for edit in additional_edits:
                change_record = {
                    "timestamp": datetime.now().isoformat(),
                    "file": str(self.current_file.relative_to(self.repo_path)),
                    "edit_type": "additional_edit",
                    "description": edit
                }
                self.changes_made.append(change_record)
            
            summary = f"Additional editing completed:\n"
            summary += f"- Additional edits: {len(additional_edits)}\n"
            summary += f"- Total changes: {len(self.changes_made)}\n"
            
            if additional_edits:
                summary += f"\nEdits made:\n" + '\n'.join(additional_edits)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error performing additional edits: {e}")
            return f"Error performing additional edits: {str(e)}"
    
    def _add_function_docstrings(self, lines: List[str]) -> str:
        """Add docstrings to functions that don't have them."""
        edits = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            if line.strip().startswith('def '):
                # Check if next non-empty line is a docstring
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                
                if j < len(lines) and not lines[j].strip().startswith('"""') and not lines[j].strip().startswith("'''"):
                    # Add docstring
                    indent = ' ' * (len(line) - len(line.lstrip()) + 4)
                    docstring = f'{indent}"""Function docstring added by SWE Agent."""'
                    lines.insert(i + 1, docstring)
                    edits.append(f"Added docstring to function at line {i+1}")
                    i += 1  # Skip the inserted line
            i += 1
        
        return f"Added {len(edits)} docstrings"
    
    def _optimize_imports(self, lines: List[str]) -> str:
        """Optimize import statements."""
        import_lines = []
        other_lines = []
        
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_lines.append(line)
            else:
                other_lines.append(line)
        
        # Sort imports
        import_lines.sort()
        
        # Reconstruct lines
        lines[:] = import_lines + [''] + other_lines
        
        return f"Optimized {len(import_lines)} import statements"
    
    # Enhanced file operations using standalone tools
    def create_file_standalone(self, file_path: str, content: str = "", is_directory: bool = False) -> str:
        """
        Create a new file or directory using standalone file operations.
        
        Args:
            file_path: Path for the new file/directory
            content: Initial content for the file
            is_directory: Whether to create a directory
            
        Returns:
            Creation results
        """
        try:
            result = self.file_ops.create_file(file_path, content, is_directory)
            if result["success"]:
                return f"[OK] {result['message']}"
            else:
                return f"[X] {result['message']}: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"[X] Error creating {'directory' if is_directory else 'file'}: {str(e)}"
    
    def edit_file_standalone(self, file_path: str, text: str, start_line: int = 1, end_line: int = None) -> str:
        """
        Edit a file using standalone file operations.
        
        Args:
            file_path: Path to the file to edit
            text: New text content
            start_line: Starting line number (1-based)
            end_line: Ending line number (1-based, inclusive)
            
        Returns:
            Edit results
        """
        try:
            result = self.file_ops.edit_file(file_path, text, start_line, end_line)
            if result["success"]:
                return f"[OK] {result['message']}\n📝 Modified lines: {result['lines_modified']}"
            else:
                return f"[X] {result['message']}: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"[X] Error editing file: {str(e)}"
    
    def search_in_files_standalone(self, query: str, file_pattern: str = "*.py", case_sensitive: bool = False) -> str:
        """
        Search for text within files using standalone operations.
        
        Args:
            query: Text to search for
            file_pattern: Pattern for files to search in
            case_sensitive: Whether to use case-sensitive search
            
        Returns:
            Search results
        """
        try:
            result = self.file_ops.search_in_files(query, file_pattern, ".", case_sensitive)
            if result["success"]:
                if result["total_matches"] == 0:
                    return f"[?] No matches found for '{query}'"
                
                summary = f"[?] Found {result['total_matches']} matches in {result['files_with_matches']} files:\n\n"
                
                for file_match in result["matches"][:5]:  # Show first 5 files
                    summary += f"📄 {file_match['file']}:\n"
                    for match in file_match["matches"][:3]:  # Show first 3 matches per file
                        summary += f"  Line {match['line_number']}: {match['line_content']}\n"
                    if len(file_match["matches"]) > 3:
                        summary += f"  ... and {len(file_match['matches']) - 3} more matches\n"
                    summary += "\n"
                
                if len(result["matches"]) > 5:
                    summary += f"... and {len(result['matches']) - 5} more files with matches\n"
                
                return summary
            else:
                return f"[X] {result['message']}: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"[X] Error searching files: {str(e)}"
    
    def analyze_code_standalone(self, file_path: str = None) -> str:
        """
        Analyze code structure using standalone code analysis.
        
        Args:
            file_path: Specific file to analyze (optional)
            
        Returns:
            Code analysis results
        """
        try:
            if file_path:
                # Analyze specific file
                result = self.code_analyzer.analyze_file(file_path)
                if result["success"]:
                    summary = f"📊 Code Analysis: {file_path}\n\n"
                    summary += f"Language: {result['language']}\n"
                    summary += f"Lines: {result['line_count']}\n"
                    summary += f"Functions: {len(result.get('functions', []))}\n"
                    summary += f"Classes: {len(result.get('classes', []))}\n"
                    summary += f"Imports: {len(result.get('imports', []))}\n"
                    
                    if result.get('classes'):
                        summary += f"\n[P] Classes:\n"
                        for cls in result['classes'][:3]:  # Show first 3 classes
                            summary += f"  - {cls['name']} (line {cls['line_start']})\n"
                    
                    if result.get('functions'):
                        summary += f"\n[*] Functions:\n"
                        for func in result['functions'][:5]:  # Show first 5 functions
                            summary += f"  - {func['name']} (line {func['line_start']})\n"
                    
                    return summary
                else:
                    return f"[X] {result['message']}: {result.get('error', 'Unknown error')}"
            else:
                # Analyze entire directory
                result = self.code_analyzer.analyze_directory()
                if result["success"]:
                    summary = f"📊 Directory Analysis: {result['directory']}\n\n"
                    summary += f"Total files: {result['summary']['total_files']}\n"
                    summary += f"Total lines: {result['summary']['total_lines']}\n"
                    summary += f"Total functions: {result['summary']['total_functions']}\n"
                    summary += f"Total classes: {result['summary']['total_classes']}\n"
                    
                    summary += f"\n🗂️ Languages:\n"
                    for lang, count in result['summary']['languages'].items():
                        summary += f"  - {lang}: {count} files\n"
                    
                    return summary
                else:
                    return f"[X] {result['message']}: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"[X] Error analyzing code: {str(e)}"
