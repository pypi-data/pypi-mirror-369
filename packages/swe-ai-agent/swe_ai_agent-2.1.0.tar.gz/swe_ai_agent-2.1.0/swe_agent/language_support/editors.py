"""
Language-agnostic code editors using Claude's natural understanding.
No hardcoded language rules - pure LLM-based editing capabilities.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from utils.anthropic_client import get_anthropic_client

logger = logging.getLogger(__name__)

class UniversalCodeEditor:
    """
    Universal code editor that can modify any programming language
    through Claude's natural language comprehension.
    """
    
    def __init__(self):
        self.anthropic_client = get_anthropic_client()
        logger.info("[E] Universal code editor initialized")
    
    def edit_file(self, file_path: Path, task_description: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Edit a file based on natural language description.
        
        Args:
            file_path: Path to file to edit
            task_description: Description of what to change
            context: Optional context about the project
            
        Returns:
            Edit operation result
        """
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            original_content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        prompt = f"""
        Edit this file based on the task description:

        File: {file_path.name}
        Task: {task_description}
        {f"Context: {context}" if context else ""}

        Current file content:
        {original_content}

        Please provide the complete modified file content. Make the changes requested while:
        1. Preserving existing functionality unless explicitly asked to change it
        2. Following the existing code style and patterns
        3. Ensuring syntactic correctness
        4. Adding appropriate comments if adding new functionality
        5. Maintaining proper error handling
        6. Considering edge cases and validation

        Return only the complete modified file content, no explanations.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
            system="You are an expert programmer who can edit code in any language. Return only the complete modified file content."
        )
        
        new_content = response.content.strip()
        
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        backup_path.write_text(original_content)
        
        # Write new content
        try:
            file_path.write_text(new_content)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "backup_path": str(backup_path),
                "task_description": task_description,
                "lines_changed": self._count_changes(original_content, new_content),
                "edit_type": "file_modification"
            }
        except Exception as e:
            return {"error": f"Could not write file: {e}"}
    
    def refactor_code(self, file_path: Path, refactor_type: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Refactor code based on specified type.
        
        Args:
            file_path: Path to file to refactor
            refactor_type: Type of refactoring (e.g., "extract methods", "improve performance")
            context: Optional context about the project
            
        Returns:
            Refactoring result
        """
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            original_content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        prompt = f"""
        Refactor this code with focus on: {refactor_type}

        File: {file_path.name}
        {f"Context: {context}" if context else ""}

        Current code:
        {original_content}

        Perform refactoring while:
        1. Maintaining all existing functionality
        2. Improving code quality and readability
        3. Following language-specific best practices
        4. Optimizing performance where applicable
        5. Reducing code duplication
        6. Improving maintainability
        7. Adding appropriate documentation

        Provide the complete refactored code with clear improvements.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
            system="You are an expert software engineer who can refactor code in any language while maintaining functionality."
        )
        
        new_content = response.content.strip()
        
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.refactor_backup')
        backup_path.write_text(original_content)
        
        # Write refactored content
        try:
            file_path.write_text(new_content)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "backup_path": str(backup_path),
                "refactor_type": refactor_type,
                "lines_changed": self._count_changes(original_content, new_content),
                "edit_type": "refactoring"
            }
        except Exception as e:
            return {"error": f"Could not write file: {e}"}
    
    def fix_issues(self, file_path: Path, issues: List[str], context: Optional[str] = None) -> Dict[str, Any]:
        """
        Fix specific issues in code.
        
        Args:
            file_path: Path to file to fix
            issues: List of issues to fix
            context: Optional context about the project
            
        Returns:
            Fix operation result
        """
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            original_content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        issues_text = "\n".join(f"- {issue}" for issue in issues)
        
        prompt = f"""
        Fix these specific issues in the code:

        Issues to fix:
        {issues_text}

        File: {file_path.name}
        {f"Context: {context}" if context else ""}

        Current code:
        {original_content}

        Fix all the specified issues while:
        1. Maintaining existing functionality
        2. Ensuring code correctness
        3. Following proper error handling
        4. Adding validation where needed
        5. Improving edge case handling
        6. Maintaining code style consistency

        Provide the complete fixed code.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
            system="You are an expert debugger who can fix code issues in any programming language."
        )
        
        new_content = response.content.strip()
        
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.fix_backup')
        backup_path.write_text(original_content)
        
        # Write fixed content
        try:
            file_path.write_text(new_content)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "backup_path": str(backup_path),
                "issues_fixed": issues,
                "lines_changed": self._count_changes(original_content, new_content),
                "edit_type": "bug_fix"
            }
        except Exception as e:
            return {"error": f"Could not write file: {e}"}
    
    def add_feature(self, file_path: Path, feature_description: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new feature to existing code.
        
        Args:
            file_path: Path to file to modify
            feature_description: Description of feature to add
            context: Optional context about the project
            
        Returns:
            Feature addition result
        """
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            original_content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        prompt = f"""
        Add this feature to the existing code:

        Feature: {feature_description}
        File: {file_path.name}
        {f"Context: {context}" if context else ""}

        Current code:
        {original_content}

        Add the feature while:
        1. Integrating seamlessly with existing code
        2. Following established patterns and conventions
        3. Maintaining backward compatibility
        4. Adding proper error handling
        5. Including appropriate documentation
        6. Ensuring code quality and readability
        7. Adding necessary imports or dependencies

        Provide the complete code with the new feature integrated.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
            system="You are an expert developer who can add features to code in any programming language."
        )
        
        new_content = response.content.strip()
        
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.feature_backup')
        backup_path.write_text(original_content)
        
        # Write enhanced content
        try:
            file_path.write_text(new_content)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "backup_path": str(backup_path),
                "feature_added": feature_description,
                "lines_changed": self._count_changes(original_content, new_content),
                "edit_type": "feature_addition"
            }
        except Exception as e:
            return {"error": f"Could not write file: {e}"}
    
    def create_file(self, file_path: Path, description: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new file based on description.
        
        Args:
            file_path: Path where to create the file
            description: Description of what the file should contain
            context: Optional context about the project
            
        Returns:
            File creation result
        """
        if file_path.exists():
            return {"error": f"File already exists: {file_path}"}
        
        prompt = f"""
        Create a new file with the following specification:

        File: {file_path.name}
        Description: {description}
        {f"Context: {context}" if context else ""}

        Create the file content that:
        1. Fulfills the specified requirements
        2. Follows language-specific best practices
        3. Includes proper documentation and comments
        4. Handles edge cases and errors appropriately
        5. Uses appropriate naming conventions
        6. Includes necessary imports or dependencies
        7. Is production-ready and well-structured

        Provide the complete file content.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
            system="You are an expert programmer who can create well-structured files in any programming language."
        )
        
        content = response.content.strip()
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        try:
            file_path.write_text(content)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "description": description,
                "lines_created": len(content.split('\n')),
                "edit_type": "file_creation"
            }
        except Exception as e:
            return {"error": f"Could not create file: {e}"}
    
    def optimize_performance(self, file_path: Path, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Optimize code for better performance.
        
        Args:
            file_path: Path to file to optimize
            context: Optional context about the project
            
        Returns:
            Optimization result
        """
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            original_content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        prompt = f"""
        Optimize this code for better performance:

        File: {file_path.name}
        {f"Context: {context}" if context else ""}

        Current code:
        {original_content}

        Optimize while:
        1. Maintaining all existing functionality
        2. Improving algorithmic efficiency
        3. Reducing memory usage
        4. Optimizing I/O operations
        5. Improving data structures usage
        6. Reducing computational complexity
        7. Adding performance monitoring if beneficial

        Provide the complete optimized code with performance improvements.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
            system="You are a performance optimization expert who can improve code efficiency in any programming language."
        )
        
        new_content = response.content.strip()
        
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.perf_backup')
        backup_path.write_text(original_content)
        
        # Write optimized content
        try:
            file_path.write_text(new_content)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "backup_path": str(backup_path),
                "lines_changed": self._count_changes(original_content, new_content),
                "edit_type": "performance_optimization"
            }
        except Exception as e:
            return {"error": f"Could not write file: {e}"}
    
    def _count_changes(self, original: str, new: str) -> Dict[str, int]:
        """Count changes between original and new content."""
        original_lines = original.split('\n')
        new_lines = new.split('\n')
        
        return {
            "original_lines": len(original_lines),
            "new_lines": len(new_lines),
            "lines_added": max(0, len(new_lines) - len(original_lines)),
            "lines_removed": max(0, len(original_lines) - len(new_lines))
        }


def get_language_editor() -> UniversalCodeEditor:
    """Get universal code editor instance."""
    return UniversalCodeEditor()