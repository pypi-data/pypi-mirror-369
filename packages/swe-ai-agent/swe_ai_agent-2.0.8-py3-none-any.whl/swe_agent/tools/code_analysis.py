"""
Standalone code analysis tools for the SWE Agent system.
Provides comprehensive code understanding without external dependencies.
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """
    Comprehensive code analysis tool that can understand code structure,
    extract classes, functions, and provide insights across multiple languages.
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize code analyzer.
        
        Args:
            base_path: Base directory for analysis (default: current directory)
        """
        self.base_path = Path(base_path or os.getcwd()).resolve()
        self.cache = {}
        
    def analyze_file(self, file_path: str, language: str = None) -> Dict[str, Any]:
        """
        Analyze a single file for code structure and elements.
        
        Args:
            file_path: Path to file to analyze
            language: Programming language (auto-detected if None)
            
        Returns:
            Dict with analysis results including classes, functions, imports, etc.
        """
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "error": "FileNotFoundError"
                }
            
            # Read file content
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                return {
                    "success": False,
                    "message": f"Cannot read file (binary?): {file_path}",
                    "error": "UnicodeDecodeError"
                }
            
            # Detect language if not provided
            if not language:
                language = self._detect_language(file_path, content)
            
            # Analyze based on language
            if language == "python":
                analysis = self._analyze_python_file(content, file_path)
            elif language == "javascript":
                analysis = self._analyze_javascript_file(content, file_path)
            elif language == "java":
                analysis = self._analyze_java_file(content, file_path)
            elif language == "cpp":
                analysis = self._analyze_cpp_file(content, file_path)
            elif language == "go":
                analysis = self._analyze_go_file(content, file_path)
            else:
                analysis = self._analyze_generic_file(content, file_path, language)
            
            analysis.update({
                "success": True,
                "file_path": str(file_path),
                "language": language,
                "file_size": len(content),
                "line_count": len(content.splitlines()),
                "message": f"Analysis complete for {file_path}"
            })
            
            return analysis
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error analyzing file: {file_path}",
                "error": str(e)
            }
    
    def _detect_language(self, file_path: str, content: str) -> str:
        """
        Detect programming language from file extension and content.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Detected language name
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Extension-based detection
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'matlab',
            '.pl': 'perl',
            '.sh': 'bash',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.tex': 'latex'
        }
        
        if extension in extension_map:
            return extension_map[extension]
        
        # Content-based detection for files without extensions
        if content.strip().startswith('#!/'):
            shebang = content.splitlines()[0].lower()
            if 'python' in shebang:
                return 'python'
            elif 'node' in shebang or 'javascript' in shebang:
                return 'javascript'
            elif 'bash' in shebang or 'sh' in shebang:
                return 'bash'
        
        # Basic pattern matching
        if re.search(r'\bdef\s+\w+\s*\(', content) and 'import ' in content:
            return 'python'
        elif re.search(r'\bfunction\s+\w+\s*\(', content) and 'var ' in content:
            return 'javascript'
        elif re.search(r'\bclass\s+\w+\s*\{', content) and 'public static void main' in content:
            return 'java'
        elif re.search(r'\bfunc\s+\w+\s*\(', content) and 'package ' in content:
            return 'go'
        
        return 'unknown'
    
    def _analyze_python_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Python file using AST parsing.
        
        Args:
            content: File content
            file_path: File path
            
        Returns:
            Analysis results
        """
        try:
            tree = ast.parse(content)
            
            classes = []
            functions = []
            imports = []
            global_vars = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno,
                        "methods": [],
                        "attributes": [],
                        "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                        "bases": [self._get_name(base) for base in node.bases],
                        "docstring": ast.get_docstring(node)
                    }
                    
                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                "name": item.name,
                                "line_start": item.lineno,
                                "line_end": item.end_lineno,
                                "args": [arg.arg for arg in item.args.args],
                                "returns": self._get_name(item.returns) if item.returns else None,
                                "is_async": isinstance(item, ast.AsyncFunctionDef),
                                "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in item.decorator_list],
                                "docstring": ast.get_docstring(item)
                            }
                            class_info["methods"].append(method_info)
                    
                    classes.append(class_info)
                
                elif isinstance(node, ast.FunctionDef) and not self._is_in_class(node, tree):
                    func_info = {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "returns": self._get_name(node.returns) if node.returns else None,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                        "docstring": ast.get_docstring(node)
                    }
                    functions.append(func_info)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append({
                                "type": "import",
                                "module": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno
                            })
                    else:
                        for alias in node.names:
                            imports.append({
                                "type": "from_import",
                                "module": node.module,
                                "name": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno
                            })
                
                elif isinstance(node, ast.Assign) and self._is_global_assignment(node, tree):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            global_vars.append({
                                "name": target.id,
                                "line": node.lineno,
                                "type": self._infer_type(node.value)
                            })
            
            return {
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "global_variables": global_vars,
                "complexity": self._calculate_complexity(tree),
                "syntax_errors": []
            }
            
        except SyntaxError as e:
            return {
                "classes": [],
                "functions": [],
                "imports": [],
                "global_variables": [],
                "complexity": 0,
                "syntax_errors": [str(e)]
            }
    
    def _analyze_javascript_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze JavaScript file using regex patterns.
        
        Args:
            content: File content
            file_path: File path
            
        Returns:
            Analysis results
        """
        classes = []
        functions = []
        imports = []
        
        # Find classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        for match in re.finditer(class_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            classes.append({
                "name": match.group(1),
                "extends": match.group(2),
                "line_start": line_num,
                "methods": []
            })
        
        # Find functions
        func_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*\(',
            r'let\s+(\w+)\s*=\s*\(',
            r'var\s+(\w+)\s*=\s*\(',
            r'(\w+):\s*function\s*\(',
            r'(\w+)\s*\([^)]*\)\s*=>'
        ]
        
        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                functions.append({
                    "name": match.group(1),
                    "line_start": line_num,
                    "type": "function"
                })
        
        # Find imports
        import_patterns = [
            r'import\s+(.+?)\s+from\s+["\'](.+?)["\']',
            r'const\s+(.+?)\s*=\s*require\(["\'](.+?)["\']\)',
            r'import\s*\*\s*as\s+(\w+)\s+from\s+["\'](.+?)["\']'
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                imports.append({
                    "imported": match.group(1),
                    "module": match.group(2),
                    "line": line_num
                })
        
        return {
            "classes": classes,
            "functions": functions,
            "imports": imports,
            "global_variables": [],
            "complexity": len(functions) + len(classes),
            "syntax_errors": []
        }
    
    def _analyze_java_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Java file using regex patterns.
        
        Args:
            content: File content
            file_path: File path
            
        Returns:
            Analysis results
        """
        classes = []
        functions = []
        imports = []
        
        # Find package declaration
        package_match = re.search(r'package\s+([\w\.]+);', content)
        package = package_match.group(1) if package_match else None
        
        # Find imports
        import_pattern = r'import\s+(?:static\s+)?([\w\.\*]+);'
        for match in re.finditer(import_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            imports.append({
                "import": match.group(1),
                "line": line_num
            })
        
        # Find classes
        class_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+|final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w\s,]+))?\s*\{'
        for match in re.finditer(class_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            classes.append({
                "name": match.group(1),
                "extends": match.group(2),
                "implements": match.group(3),
                "line_start": line_num,
                "methods": []
            })
        
        # Find methods
        method_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:final\s+)?(\w+)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{'
        for match in re.finditer(method_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            functions.append({
                "name": match.group(2),
                "return_type": match.group(1),
                "line_start": line_num
            })
        
        return {
            "package": package,
            "classes": classes,
            "functions": functions,
            "imports": imports,
            "global_variables": [],
            "complexity": len(functions) + len(classes),
            "syntax_errors": []
        }
    
    def _analyze_cpp_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze C++ file using regex patterns.
        
        Args:
            content: File content
            file_path: File path
            
        Returns:
            Analysis results
        """
        classes = []
        functions = []
        includes = []
        
        # Find includes
        include_pattern = r'#include\s*[<"]([^>"]+)[>"]'
        for match in re.finditer(include_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            includes.append({
                "include": match.group(1),
                "line": line_num
            })
        
        # Find classes
        class_pattern = r'class\s+(\w+)(?:\s*:\s*(?:public\s+|private\s+|protected\s+)?(\w+))?\s*\{'
        for match in re.finditer(class_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            classes.append({
                "name": match.group(1),
                "inherits": match.group(2),
                "line_start": line_num,
                "methods": []
            })
        
        # Find functions
        func_pattern = r'(?:inline\s+)?(?:virtual\s+)?(?:static\s+)?(\w+(?:\s*\*)?)\s+(\w+)\s*\([^)]*\)\s*(?:const\s*)?(?:override\s*)?[{;]'
        for match in re.finditer(func_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            functions.append({
                "name": match.group(2),
                "return_type": match.group(1),
                "line_start": line_num
            })
        
        return {
            "classes": classes,
            "functions": functions,
            "includes": includes,
            "global_variables": [],
            "complexity": len(functions) + len(classes),
            "syntax_errors": []
        }
    
    def _analyze_go_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Go file using regex patterns.
        
        Args:
            content: File content
            file_path: File path
            
        Returns:
            Analysis results
        """
        functions = []
        imports = []
        structs = []
        
        # Find package declaration
        package_match = re.search(r'package\s+(\w+)', content)
        package = package_match.group(1) if package_match else None
        
        # Find imports
        import_pattern = r'import\s+(?:\(\s*([^)]+)\s*\)|"([^"]+)"|\s+(\w+)\s+"([^"]+)")'
        for match in re.finditer(import_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            imports.append({
                "import": match.group(1) or match.group(2) or match.group(4),
                "alias": match.group(3),
                "line": line_num
            })
        
        # Find functions
        func_pattern = r'func\s+(?:\(\s*\w+\s+\*?\w+\s*\)\s+)?(\w+)\s*\([^)]*\)(?:\s*\([^)]*\))?(?:\s*\w+)?\s*\{'
        for match in re.finditer(func_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            functions.append({
                "name": match.group(1),
                "line_start": line_num
            })
        
        # Find structs
        struct_pattern = r'type\s+(\w+)\s+struct\s*\{'
        for match in re.finditer(struct_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            structs.append({
                "name": match.group(1),
                "line_start": line_num
            })
        
        return {
            "package": package,
            "functions": functions,
            "structs": structs,
            "imports": imports,
            "global_variables": [],
            "complexity": len(functions) + len(structs),
            "syntax_errors": []
        }
    
    def _analyze_generic_file(self, content: str, file_path: str, language: str) -> Dict[str, Any]:
        """
        Generic analysis for unknown file types.
        
        Args:
            content: File content
            file_path: File path
            language: Detected language
            
        Returns:
            Basic analysis results
        """
        lines = content.splitlines()
        
        # Count comment lines
        comment_lines = 0
        for line in lines:
            line = line.strip()
            if line.startswith('#') or line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                comment_lines += 1
        
        # Count blank lines
        blank_lines = sum(1 for line in lines if not line.strip())
        
        # Basic word count
        words = len(content.split())
        
        return {
            "language": language,
            "total_lines": len(lines),
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,
            "code_lines": len(lines) - comment_lines - blank_lines,
            "words": words,
            "characters": len(content),
            "functions": [],
            "classes": [],
            "imports": [],
            "global_variables": [],
            "complexity": 0,
            "syntax_errors": []
        }
    
    def analyze_directory(self, directory: str = ".", patterns: List[str] = None) -> Dict[str, Any]:
        """
        Analyze all files in a directory matching given patterns.
        
        Args:
            directory: Directory to analyze
            patterns: List of file patterns to match (default: common code files)
            
        Returns:
            Comprehensive directory analysis
        """
        if patterns is None:
            patterns = ["*.py", "*.js", "*.java", "*.cpp", "*.go", "*.rs", "*.rb", "*.php"]
        
        try:
            full_path = self.base_path / directory
            
            if not full_path.exists():
                return {
                    "success": False,
                    "message": f"Directory not found: {directory}",
                    "error": "DirectoryNotFoundError"
                }
            
            files_analyzed = {}
            summary = {
                "total_files": 0,
                "languages": defaultdict(int),
                "total_lines": 0,
                "total_functions": 0,
                "total_classes": 0,
                "errors": []
            }
            
            # Find all matching files
            for pattern in patterns:
                for file_path in full_path.rglob(pattern):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(self.base_path)
                        
                        # Analyze the file
                        analysis = self.analyze_file(str(relative_path))
                        
                        if analysis["success"]:
                            files_analyzed[str(relative_path)] = analysis
                            
                            # Update summary
                            summary["total_files"] += 1
                            summary["languages"][analysis["language"]] += 1
                            summary["total_lines"] += analysis.get("line_count", 0)
                            summary["total_functions"] += len(analysis.get("functions", []))
                            summary["total_classes"] += len(analysis.get("classes", []))
                        else:
                            summary["errors"].append({
                                "file": str(relative_path),
                                "error": analysis.get("error", "Unknown error")
                            })
            
            return {
                "success": True,
                "directory": directory,
                "files": files_analyzed,
                "summary": dict(summary),
                "message": f"Analyzed {summary['total_files']} files in {directory}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error analyzing directory: {directory}",
                "error": str(e)
            }
    
    def get_class_info(self, class_name: str, file_path: str = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific class.
        
        Args:
            class_name: Name of the class to find
            file_path: Specific file to search in (optional)
            
        Returns:
            Detailed class information
        """
        try:
            if file_path:
                # Search in specific file
                analysis = self.analyze_file(file_path)
                if analysis["success"]:
                    for cls in analysis.get("classes", []):
                        if cls["name"] == class_name:
                            return {
                                "success": True,
                                "class_info": cls,
                                "file_path": file_path,
                                "message": f"Found class {class_name} in {file_path}"
                            }
            else:
                # Search in all files
                dir_analysis = self.analyze_directory()
                if dir_analysis["success"]:
                    for filepath, analysis in dir_analysis["files"].items():
                        for cls in analysis.get("classes", []):
                            if cls["name"] == class_name:
                                return {
                                    "success": True,
                                    "class_info": cls,
                                    "file_path": filepath,
                                    "message": f"Found class {class_name} in {filepath}"
                                }
            
            return {
                "success": False,
                "message": f"Class {class_name} not found",
                "error": "ClassNotFoundError"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error searching for class {class_name}",
                "error": str(e)
            }
    
    def get_function_info(self, function_name: str, file_path: str = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific function.
        
        Args:
            function_name: Name of the function to find
            file_path: Specific file to search in (optional)
            
        Returns:
            Detailed function information
        """
        try:
            if file_path:
                # Search in specific file
                analysis = self.analyze_file(file_path)
                if analysis["success"]:
                    for func in analysis.get("functions", []):
                        if func["name"] == function_name:
                            return {
                                "success": True,
                                "function_info": func,
                                "file_path": file_path,
                                "message": f"Found function {function_name} in {file_path}"
                            }
            else:
                # Search in all files
                dir_analysis = self.analyze_directory()
                if dir_analysis["success"]:
                    for filepath, analysis in dir_analysis["files"].items():
                        for func in analysis.get("functions", []):
                            if func["name"] == function_name:
                                return {
                                    "success": True,
                                    "function_info": func,
                                    "file_path": filepath,
                                    "message": f"Found function {function_name} in {filepath}"
                                }
            
            return {
                "success": False,
                "message": f"Function {function_name} not found",
                "error": "FunctionNotFoundError"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error searching for function {function_name}",
                "error": str(e)
            }
    
    # Helper methods
    def _get_name(self, node) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return str(node)
    
    def _is_in_class(self, node, tree) -> bool:
        """Check if a node is inside a class definition."""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                if node in parent.body:
                    return True
        return False
    
    def _is_global_assignment(self, node, tree) -> bool:
        """Check if an assignment is at global scope."""
        for parent in ast.walk(tree):
            if isinstance(parent, (ast.FunctionDef, ast.ClassDef)):
                if node in ast.walk(parent):
                    return False
        return True
    
    def _infer_type(self, node) -> str:
        """Infer type from assignment value."""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.List):
            return 'list'
        elif isinstance(node, ast.Dict):
            return 'dict'
        elif isinstance(node, ast.Set):
            return 'set'
        elif isinstance(node, ast.Tuple):
            return 'tuple'
        elif isinstance(node, ast.Call):
            return 'call_result'
        else:
            return 'unknown'
    
    def _calculate_complexity(self, tree) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity