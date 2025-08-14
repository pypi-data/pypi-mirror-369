"""
Software Engineering Tools - General purpose tools for the SWE workflow.
Contains tools for repository management, patch creation, and project structure analysis.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
import json
import subprocess
from tools.file_operations import FileOperations
from tools.code_analysis import CodeAnalyzer

logger = logging.getLogger(__name__)

class SWETools:
    """
    General purpose software engineering tools.
    Used by the Software Engineer agent for high-level operations.
    """
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.output_dir = repo_path / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize standalone file operations (no composio dependency)
        self.file_ops = FileOperations(str(repo_path))
        self.code_analyzer = CodeAnalyzer(str(repo_path))
        
    def generate_repo_tree(self) -> str:
        """
        Generate a tree structure of the repository.
        
        Returns:
            String representation of the repository tree
        """
        try:
            tree_lines = []
            
            def add_tree_lines(path: Path, prefix: str = "", is_last: bool = True):
                if path.name.startswith('.'):
                    return
                
                connector = "└── " if is_last else "├── "
                tree_lines.append(f"{prefix}{connector}{path.name}")
                
                if path.is_dir():
                    children = [p for p in path.iterdir() if not p.name.startswith('.')]
                    children.sort(key=lambda x: (x.is_file(), x.name))
                    
                    for i, child in enumerate(children):
                        is_last_child = i == len(children) - 1
                        extension = "    " if is_last else "│   "
                        add_tree_lines(child, prefix + extension, is_last_child)
            
            tree_lines.append(f"{self.repo_path.name}/")
            children = [p for p in self.repo_path.iterdir() if not p.name.startswith('.')]
            children.sort(key=lambda x: (x.is_file(), x.name))
            
            for i, child in enumerate(children):
                is_last_child = i == len(children) - 1
                add_tree_lines(child, "", is_last_child)
            
            return "\n".join(tree_lines)
            
        except Exception as e:
            logger.error(f"Error generating repository tree: {e}")
            return f"Error generating tree: {str(e)}"
    
    def get_project_structure(self) -> Dict:
        """
        Get detailed project structure information.
        
        Returns:
            Dictionary containing project structure details
        """
        try:
            structure = {
                "root_path": str(self.repo_path),
                "python_files": [],
                "directories": [],
                "config_files": [],
                "total_files": 0,
                "total_directories": 0
            }
            
            for item in self.repo_path.rglob("*"):
                if item.name.startswith('.'):
                    continue
                    
                if item.is_file():
                    structure["total_files"] += 1
                    
                    if item.suffix == ".py":
                        structure["python_files"].append(str(item.relative_to(self.repo_path)))
                    elif item.name in ["requirements.txt", "setup.py", "pyproject.toml", ".gitignore"]:
                        structure["config_files"].append(str(item.relative_to(self.repo_path)))
                        
                elif item.is_dir():
                    structure["total_directories"] += 1
                    structure["directories"].append(str(item.relative_to(self.repo_path)))
            
            return structure
            
        except Exception as e:
            logger.error(f"Error getting project structure: {e}")
            return {"error": str(e)}
    
    def analyze_dependencies(self) -> Dict:
        """
        Analyze project dependencies.
        
        Returns:
            Dictionary containing dependency information
        """
        try:
            dependencies = {
                "requirements_txt": [],
                "imports": [],
                "setup_py": [],
                "pyproject_toml": []
            }
            
            # Check requirements.txt
            req_file = self.repo_path / "requirements.txt"
            if req_file.exists():
                dependencies["requirements_txt"] = req_file.read_text().strip().split("\n")
            
            # Check setup.py
            setup_file = self.repo_path / "setup.py"
            if setup_file.exists():
                content = setup_file.read_text()
                # Simple regex to find install_requires
                if "install_requires" in content:
                    dependencies["setup_py"] = ["Found install_requires in setup.py"]
            
            # Analyze Python imports
            for py_file in self.repo_path.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue
                try:
                    content = py_file.read_text()
                    for line in content.split("\n"):
                        line = line.strip()
                        if line.startswith("import ") or line.startswith("from "):
                            dependencies["imports"].append(line)
                except Exception:
                    continue
            
            # Limit imports to unique and first 20
            dependencies["imports"] = list(set(dependencies["imports"]))[:20]
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}")
            return {"error": str(e)}
    
    def create_patch(self, changes: Optional[List[Dict]] = None) -> str:
        """
        Create a patch file for the changes made.
        
        Args:
            changes: List of changes to include in the patch
            
        Returns:
            Path to the created patch file or error message
        """
        try:
            patch_file = self.output_dir / "swe_agent_patch.patch"
            
            if changes:
                patch_content = "# SWE Agent Generated Patch\n\n"
                for change in changes:
                    patch_content += f"File: {change.get('file', 'unknown')}\n"
                    patch_content += f"Operation: {change.get('operation', 'unknown')}\n"
                    patch_content += f"Description: {change.get('description', 'No description')}\n"
                    patch_content += "---\n\n"
            else:
                # Try to generate patch using git if available
                try:
                    result = subprocess.run(
                        ["git", "diff", "--no-index", "/dev/null", "."],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True
                    )
                    patch_content = result.stdout if result.stdout else "No changes detected"
                except Exception:
                    patch_content = "# SWE Agent Patch\n# No specific changes recorded\n"
            
            patch_file.write_text(patch_content)
            return f"Patch created: {patch_file}"
            
        except Exception as e:
            logger.error(f"Error creating patch: {e}")
            return f"Error creating patch: {str(e)}"
    
    def save_analysis_report(self, analysis_data: Dict) -> str:
        """
        Save analysis report to a JSON file.
        
        Args:
            analysis_data: Analysis data to save
            
        Returns:
            Path to the saved report
        """
        try:
            report_file = self.output_dir / "analysis_report.json"
            
            with open(report_file, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            return f"Analysis report saved: {report_file}"
            
        except Exception as e:
            logger.error(f"Error saving analysis report: {e}")
            return f"Error saving report: {str(e)}"
    
    def get_file_stats(self) -> Dict:
        """
        Get statistics about files in the repository.
        
        Returns:
            Dictionary containing file statistics
        """
        try:
            stats = {
                "total_files": 0,
                "python_files": 0,
                "total_lines": 0,
                "python_lines": 0,
                "largest_file": "",
                "largest_file_size": 0
            }
            
            for file_path in self.repo_path.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    stats["total_files"] += 1
                    
                    try:
                        file_size = file_path.stat().st_size
                        if file_size > stats["largest_file_size"]:
                            stats["largest_file_size"] = file_size
                            stats["largest_file"] = str(file_path.relative_to(self.repo_path))
                        
                        if file_path.suffix == ".py":
                            stats["python_files"] += 1
                            content = file_path.read_text()
                            lines = len(content.split("\n"))
                            stats["python_lines"] += lines
                            stats["total_lines"] += lines
                        else:
                            # Estimate lines for non-Python files
                            try:
                                content = file_path.read_text()
                                stats["total_lines"] += len(content.split("\n"))
                            except Exception:
                                pass
                    except Exception:
                        continue
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting file stats: {e}")
            return {"error": str(e)}
