"""
Code Analysis Tools - Specialized tools for code analysis and FQDN mapping.
Contains tools for analyzing code structure, dependencies, and generating insights.
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
import re

logger = logging.getLogger(__name__)

class CodeAnalysisTools:
    """
    Specialized tools for code analysis tasks.
    Used by the Code Analyzer agent for detailed code insights.
    """
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.output_dir = repo_path / "output"
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_fqdn_mappings(self) -> str:
        """
        Generate Fully Qualified Domain Name mappings for code elements.
        
        Returns:
            String representation of FQDN mappings
        """
        try:
            fqdn_mappings = {}
            
            for py_file in self.repo_path.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue
                    
                try:
                    content = py_file.read_text()
                    tree = ast.parse(content)
                    
                    # Get relative path for module name
                    rel_path = py_file.relative_to(self.repo_path)
                    module_name = str(rel_path.with_suffix('')).replace('/', '.')
                    
                    # Extract classes and functions
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            fqdn = f"{module_name}.{node.name}"
                            fqdn_mappings[fqdn] = {
                                "type": "class",
                                "file": str(rel_path),
                                "line": node.lineno,
                                "methods": []
                            }
                            
                            # Extract methods
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    method_fqdn = f"{fqdn}.{item.name}"
                                    fqdn_mappings[method_fqdn] = {
                                        "type": "method",
                                        "file": str(rel_path),
                                        "line": item.lineno,
                                        "parent_class": fqdn
                                    }
                                    fqdn_mappings[fqdn]["methods"].append(method_fqdn)
                                    
                        elif isinstance(node, ast.FunctionDef):
                            fqdn = f"{module_name}.{node.name}"
                            fqdn_mappings[fqdn] = {
                                "type": "function",
                                "file": str(rel_path),
                                "line": node.lineno
                            }
                            
                except Exception as e:
                    logger.warning(f"Error analyzing {py_file}: {e}")
                    continue
            
            # Save mappings to file
            mappings_file = self.output_dir / "fqdn_mappings.json"
            with open(mappings_file, 'w') as f:
                json.dump(fqdn_mappings, f, indent=2)
            
            # Return summary
            summary = f"Generated FQDN mappings for {len(fqdn_mappings)} code elements:\n"
            summary += f"- Classes: {len([k for k, v in fqdn_mappings.items() if v['type'] == 'class'])}\n"
            summary += f"- Functions: {len([k for k, v in fqdn_mappings.items() if v['type'] == 'function'])}\n"
            summary += f"- Methods: {len([k for k, v in fqdn_mappings.items() if v['type'] == 'method'])}\n"
            summary += f"Mappings saved to: {mappings_file}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating FQDN mappings: {e}")
            return f"Error generating FQDN mappings: {str(e)}"
    
    def analyze_code_structure(self) -> str:
        """
        Analyze the overall code structure.
        
        Returns:
            String representation of code structure analysis
        """
        try:
            structure_info = {
                "modules": [],
                "classes": [],
                "functions": [],
                "imports": set(),
                "complexity_metrics": {}
            }
            
            for py_file in self.repo_path.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue
                    
                try:
                    content = py_file.read_text()
                    tree = ast.parse(content)
                    
                    rel_path = py_file.relative_to(self.repo_path)
                    module_name = str(rel_path.with_suffix('')).replace('/', '.')
                    
                    structure_info["modules"].append(module_name)
                    
                    # Analyze complexity
                    complexity = self._calculate_complexity(tree)
                    structure_info["complexity_metrics"][module_name] = complexity
                    
                    # Extract imports
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                structure_info["imports"].add(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                structure_info["imports"].add(node.module)
                        elif isinstance(node, ast.ClassDef):
                            structure_info["classes"].append(f"{module_name}.{node.name}")
                        elif isinstance(node, ast.FunctionDef):
                            structure_info["functions"].append(f"{module_name}.{node.name}")
                            
                except Exception as e:
                    logger.warning(f"Error analyzing structure of {py_file}: {e}")
                    continue
            
            # Convert set to list for JSON serialization
            structure_info["imports"] = list(structure_info["imports"])
            
            # Save structure info
            structure_file = self.output_dir / "code_structure.json"
            with open(structure_file, 'w') as f:
                json.dump(structure_info, f, indent=2)
            
            # Return summary
            summary = f"Code Structure Analysis:\n"
            summary += f"- Modules: {len(structure_info['modules'])}\n"
            summary += f"- Classes: {len(structure_info['classes'])}\n"
            summary += f"- Functions: {len(structure_info['functions'])}\n"
            summary += f"- Unique imports: {len(structure_info['imports'])}\n"
            summary += f"Structure saved to: {structure_file}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error analyzing code structure: {e}")
            return f"Error analyzing code structure: {str(e)}"
    
    def find_dependencies(self) -> str:
        """
        Find and analyze dependencies in the codebase.
        
        Returns:
            String representation of dependency analysis
        """
        try:
            dependencies = {
                "internal_imports": [],
                "external_imports": [],
                "dependency_graph": {},
                "circular_dependencies": []
            }
            
            # Get all Python files
            py_files = list(self.repo_path.rglob("*.py"))
            module_names = set()
            
            for py_file in py_files:
                if py_file.name.startswith('.'):
                    continue
                rel_path = py_file.relative_to(self.repo_path)
                module_name = str(rel_path.with_suffix('')).replace('/', '.')
                module_names.add(module_name)
            
            # Analyze imports
            for py_file in py_files:
                if py_file.name.startswith('.'):
                    continue
                    
                try:
                    content = py_file.read_text()
                    tree = ast.parse(content)
                    
                    rel_path = py_file.relative_to(self.repo_path)
                    module_name = str(rel_path.with_suffix('')).replace('/', '.')
                    
                    dependencies["dependency_graph"][module_name] = []
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                if alias.name in module_names:
                                    dependencies["internal_imports"].append(f"{module_name} -> {alias.name}")
                                    dependencies["dependency_graph"][module_name].append(alias.name)
                                else:
                                    dependencies["external_imports"].append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module and node.module in module_names:
                                dependencies["internal_imports"].append(f"{module_name} -> {node.module}")
                                dependencies["dependency_graph"][module_name].append(node.module)
                            elif node.module:
                                dependencies["external_imports"].append(node.module)
                                
                except Exception as e:
                    logger.warning(f"Error analyzing dependencies in {py_file}: {e}")
                    continue
            
            # Find circular dependencies
            dependencies["circular_dependencies"] = self._find_circular_dependencies(
                dependencies["dependency_graph"]
            )
            
            # Remove duplicates
            dependencies["external_imports"] = list(set(dependencies["external_imports"]))
            
            # Save dependencies
            deps_file = self.output_dir / "dependencies.json"
            with open(deps_file, 'w') as f:
                json.dump(dependencies, f, indent=2)
            
            # Return summary
            summary = f"Dependency Analysis:\n"
            summary += f"- Internal imports: {len(dependencies['internal_imports'])}\n"
            summary += f"- External imports: {len(dependencies['external_imports'])}\n"
            summary += f"- Circular dependencies: {len(dependencies['circular_dependencies'])}\n"
            summary += f"Dependencies saved to: {deps_file}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error finding dependencies: {e}")
            return f"Error finding dependencies: {str(e)}"
    
    def analyze_function(self, function_name: Optional[str] = None) -> str:
        """
        Analyze a specific function or all functions.
        
        Args:
            function_name: Name of function to analyze (optional)
            
        Returns:
            Function analysis results
        """
        try:
            function_info = {}
            
            for py_file in self.repo_path.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue
                    
                try:
                    content = py_file.read_text()
                    tree = ast.parse(content)
                    
                    rel_path = py_file.relative_to(self.repo_path)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if function_name and node.name != function_name:
                                continue
                                
                            func_info = {
                                "file": str(rel_path),
                                "line": node.lineno,
                                "args": [arg.arg for arg in node.args.args],
                                "returns": ast.unparse(node.returns) if node.returns else None,
                                "decorators": [ast.unparse(dec) for dec in node.decorator_list],
                                "docstring": ast.get_docstring(node),
                                "complexity": self._calculate_function_complexity(node)
                            }
                            
                            function_info[node.name] = func_info
                            
                except Exception as e:
                    logger.warning(f"Error analyzing functions in {py_file}: {e}")
                    continue
            
            if function_name and function_name not in function_info:
                return f"Function '{function_name}' not found"
            
            # Save function analysis
            func_file = self.output_dir / "function_analysis.json"
            with open(func_file, 'w') as f:
                json.dump(function_info, f, indent=2)
            
            summary = f"Function Analysis:\n"
            summary += f"- Functions analyzed: {len(function_info)}\n"
            summary += f"Analysis saved to: {func_file}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error analyzing function: {e}")
            return f"Error analyzing function: {str(e)}"
    
    def find_references(self, identifier: Optional[str] = None) -> str:
        """
        Find references to a specific identifier.
        
        Args:
            identifier: Identifier to find references for
            
        Returns:
            Reference analysis results
        """
        try:
            if not identifier:
                return "No identifier specified for reference search"
            
            references = []
            
            for py_file in self.repo_path.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue
                    
                try:
                    content = py_file.read_text()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines):
                        if identifier in line:
                            references.append({
                                "file": str(py_file.relative_to(self.repo_path)),
                                "line": i + 1,
                                "context": line.strip()
                            })
                            
                except Exception as e:
                    logger.warning(f"Error searching references in {py_file}: {e}")
                    continue
            
            # Save references
            ref_file = self.output_dir / f"references_{identifier}.json"
            with open(ref_file, 'w') as f:
                json.dump(references, f, indent=2)
            
            summary = f"Reference Search for '{identifier}':\n"
            summary += f"- References found: {len(references)}\n"
            summary += f"References saved to: {ref_file}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error finding references: {e}")
            return f"Error finding references: {str(e)}"
    
    def get_class_hierarchy(self) -> str:
        """
        Get class hierarchy information.
        
        Returns:
            Class hierarchy analysis
        """
        try:
            hierarchy = {}
            
            for py_file in self.repo_path.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue
                    
                try:
                    content = py_file.read_text()
                    tree = ast.parse(content)
                    
                    rel_path = py_file.relative_to(self.repo_path)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            bases = [ast.unparse(base) for base in node.bases]
                            hierarchy[node.name] = {
                                "file": str(rel_path),
                                "line": node.lineno,
                                "bases": bases,
                                "methods": [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
                            }
                            
                except Exception as e:
                    logger.warning(f"Error analyzing class hierarchy in {py_file}: {e}")
                    continue
            
            # Save hierarchy
            hierarchy_file = self.output_dir / "class_hierarchy.json"
            with open(hierarchy_file, 'w') as f:
                json.dump(hierarchy, f, indent=2)
            
            summary = f"Class Hierarchy Analysis:\n"
            summary += f"- Classes found: {len(hierarchy)}\n"
            summary += f"Hierarchy saved to: {hierarchy_file}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting class hierarchy: {e}")
            return f"Error getting class hierarchy: {str(e)}"
    
    def get_additional_insights(self) -> str:
        """
        Get additional code insights and metrics.
        
        Returns:
            Additional insights
        """
        try:
            insights = {
                "code_quality": {},
                "patterns": [],
                "potential_issues": []
            }
            
            total_lines = 0
            total_functions = 0
            total_classes = 0
            
            for py_file in self.repo_path.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue
                    
                try:
                    content = py_file.read_text()
                    tree = ast.parse(content)
                    
                    lines = len(content.split('\n'))
                    total_lines += lines
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            total_functions += 1
                            # Check for long functions
                            if hasattr(node, 'end_lineno') and node.end_lineno:
                                func_lines = node.end_lineno - node.lineno
                                if func_lines > 50:
                                    insights["potential_issues"].append(
                                        f"Long function: {node.name} ({func_lines} lines)"
                                    )
                        elif isinstance(node, ast.ClassDef):
                            total_classes += 1
                            
                except Exception as e:
                    logger.warning(f"Error getting insights from {py_file}: {e}")
                    continue
            
            insights["code_quality"] = {
                "total_lines": total_lines,
                "total_functions": total_functions,
                "total_classes": total_classes,
                "avg_lines_per_function": total_lines / max(total_functions, 1)
            }
            
            # Save insights
            insights_file = self.output_dir / "code_insights.json"
            with open(insights_file, 'w') as f:
                json.dump(insights, f, indent=2)
            
            summary = f"Additional Code Insights:\n"
            summary += f"- Total lines: {total_lines}\n"
            summary += f"- Total functions: {total_functions}\n"
            summary += f"- Total classes: {total_classes}\n"
            summary += f"- Potential issues: {len(insights['potential_issues'])}\n"
            summary += f"Insights saved to: {insights_file}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting additional insights: {e}")
            return f"Error getting additional insights: {str(e)}"
    
    def _calculate_complexity(self, tree: ast.AST) -> Dict:
        """Calculate complexity metrics for an AST tree."""
        complexity = {
            "cyclomatic": 1,  # Base complexity
            "nodes": 0,
            "functions": 0,
            "classes": 0
        }
        
        for node in ast.walk(tree):
            complexity["nodes"] += 1
            
            if isinstance(node, ast.FunctionDef):
                complexity["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                complexity["classes"] += 1
            elif isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                complexity["cyclomatic"] += 1
        
        return complexity
    
    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
        
        return complexity
    
    def _find_circular_dependencies(self, dep_graph: Dict[str, List[str]]) -> List[str]:
        """Find circular dependencies in the dependency graph."""
        circular_deps = []
        
        def has_cycle(node: str, visited: Set[str], path: List[str]) -> bool:
            if node in path:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                circular_deps.append(" -> ".join(cycle))
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            path.append(node)
            
            for neighbor in dep_graph.get(node, []):
                if has_cycle(neighbor, visited, path):
                    return True
            
            path.pop()
            return False
        
        visited = set()
        for node in dep_graph:
            if node not in visited:
                has_cycle(node, visited, [])
        
        return circular_deps
