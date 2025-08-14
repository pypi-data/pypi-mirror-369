"""
Language-agnostic code analyzers using Claude's natural understanding.
No hardcoded language rules - pure LLM-based analysis.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from utils.anthropic_client import get_anthropic_client

logger = logging.getLogger(__name__)

class UniversalCodeAnalyzer:
    """
    Universal code analyzer that understands any programming language
    through Claude's natural language comprehension.
    """
    
    def __init__(self):
        self.anthropic_client = get_anthropic_client()
        logger.info("[?] Universal code analyzer initialized")
    
    def analyze_codebase_structure(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze entire codebase structure and architecture.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Comprehensive codebase analysis
        """
        # Get project files and structure
        file_tree = self._generate_file_tree(project_path)
        key_files = self._get_key_files_content(project_path)
        
        prompt = f"""
        Analyze this codebase structure and provide a comprehensive architectural analysis:

        File Tree:
        {file_tree}

        Key Files Content:
        {key_files}

        Provide analysis covering:
        1. Overall architecture pattern (MVC, microservices, monolith, etc.)
        2. Technology stack and dependencies
        3. Code organization and module structure
        4. Data flow and component relationships
        5. Potential design patterns used
        6. Code quality and maintainability assessment
        7. Security considerations
        8. Performance implications
        9. Testing strategy and coverage
        10. Deployment and build process

        Focus on understanding the actual code structure, not just file organization.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
            system="You are a senior software architect who can analyze any codebase and provide comprehensive architectural insights."
        )
        
        return {
            "analysis": response.content,
            "project_path": str(project_path),
            "analysis_type": "codebase_structure",
            "file_count": len(file_tree.split('\n'))
        }
    
    def analyze_code_quality(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze code quality for a specific file.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            Code quality analysis
        """
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        prompt = f"""
        Analyze this code for quality, best practices, and potential improvements:

        File: {file_path.name}
        Code:
        {content}

        Provide detailed analysis including:
        1. Code quality score (1-10) with justification
        2. Best practices adherence
        3. Potential bugs or issues
        4. Performance considerations
        5. Security vulnerabilities
        6. Maintainability assessment
        7. Testing recommendations
        8. Refactoring suggestions
        9. Documentation needs
        10. Specific improvement recommendations

        Be thorough and provide actionable feedback.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
            system="You are an expert code reviewer who can analyze code quality in any programming language and provide detailed feedback."
        )
        
        return {
            "file_path": str(file_path),
            "analysis": response.content,
            "analysis_type": "code_quality",
            "file_size": len(content)
        }
    
    def analyze_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze project dependencies and their relationships.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Dependency analysis
        """
        # Look for common dependency files
        dep_files = self._find_dependency_files(project_path)
        
        prompt = f"""
        Analyze the dependencies in this project:

        Dependency Files Found:
        {dep_files}

        Provide analysis including:
        1. Direct dependencies and their purposes
        2. Transitive dependencies and potential conflicts
        3. Version compatibility issues
        4. Security vulnerabilities in dependencies
        5. Outdated packages that should be updated
        6. Unused dependencies that can be removed
        7. Missing dependencies that might be needed
        8. Dependency licensing considerations
        9. Alternative package recommendations
        10. Dependency management best practices

        Focus on understanding the actual usage patterns, not just listed dependencies.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
            system="You are a dependency management expert who can analyze package dependencies for any technology stack."
        )
        
        return {
            "analysis": response.content,
            "project_path": str(project_path),
            "analysis_type": "dependencies",
            "dependency_files": list(dep_files.keys())
        }
    
    def analyze_security(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze security aspects of the codebase.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Security analysis
        """
        # Get security-relevant files
        security_files = self._get_security_relevant_files(project_path)
        
        prompt = f"""
        Perform a security analysis of this codebase:

        Security-relevant files and content:
        {security_files}

        Provide comprehensive security analysis including:
        1. Authentication and authorization mechanisms
        2. Input validation and sanitization
        3. SQL injection vulnerabilities
        4. Cross-site scripting (XSS) risks
        5. Cross-site request forgery (CSRF) protection
        6. Sensitive data handling
        7. Cryptographic implementations
        8. API security considerations
        9. Configuration security
        10. Third-party security risks
        11. Access control implementation
        12. Security testing recommendations

        Focus on actual security implementations, not just theoretical risks.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}],
            system="You are a cybersecurity expert who can identify security vulnerabilities and provide recommendations for any codebase."
        )
        
        return {
            "analysis": response.content,
            "project_path": str(project_path),
            "analysis_type": "security",
            "files_analyzed": len(security_files)
        }
    
    def analyze_performance(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze performance characteristics of the codebase.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Performance analysis
        """
        # Get performance-critical files
        perf_files = self._get_performance_files(project_path)
        
        prompt = f"""
        Analyze the performance characteristics of this codebase:

        Performance-critical files and content:
        {perf_files}

        Provide detailed performance analysis including:
        1. Algorithmic complexity assessment
        2. Memory usage patterns
        3. I/O operations efficiency
        4. Database query optimization
        5. Caching strategies
        6. Concurrency and parallelism
        7. Network communication efficiency
        8. Resource utilization
        9. Scalability considerations
        10. Performance bottlenecks
        11. Optimization recommendations
        12. Profiling and monitoring suggestions

        Focus on actual performance implications, not just theoretical concerns.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
            system="You are a performance engineering expert who can analyze and optimize code performance for any technology stack."
        )
        
        return {
            "analysis": response.content,
            "project_path": str(project_path),
            "analysis_type": "performance",
            "files_analyzed": len(perf_files)
        }
    
    def _generate_file_tree(self, project_path: Path, max_depth: int = 3) -> str:
        """Generate a file tree structure."""
        tree_lines = []
        
        def add_tree_line(path, prefix="", is_last=True):
            if len(prefix) // 4 >= max_depth:  # Approximate depth check
                return
            
            connector = "└── " if is_last else "├── "
            tree_lines.append(f"{prefix}{connector}{path.name}")
            
            if path.is_dir():
                try:
                    children = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
                    for i, child in enumerate(children):
                        child_is_last = i == len(children) - 1
                        child_prefix = prefix + ("    " if is_last else "│   ")
                        add_tree_line(child, child_prefix, child_is_last)
                except PermissionError:
                    pass
        
        add_tree_line(project_path)
        return "\n".join(tree_lines[:100])  # Limit output
    
    def _get_key_files_content(self, project_path: Path) -> str:
        """Get content of key files for analysis."""
        key_patterns = [
            "**/main.*", "**/index.*", "**/app.*", "**/server.*",
            "**/config.*", "**/settings.*", "**/package.json",
            "**/requirements.txt", "**/go.mod", "**/Cargo.toml",
            "**/pom.xml", "**/build.gradle", "**/composer.json"
        ]
        
        key_files = []
        for pattern in key_patterns:
            try:
                for file_path in project_path.glob(pattern):
                    if file_path.is_file() and file_path.stat().st_size < 50000:
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            relative_path = file_path.relative_to(project_path)
                            key_files.append(f"=== {relative_path} ===\n{content[:2000]}\n")
                        except Exception:
                            continue
            except Exception:
                continue
        
        return "\n".join(key_files[:20])  # Limit to 20 files
    
    def _find_dependency_files(self, project_path: Path) -> Dict[str, str]:
        """Find and read dependency files."""
        dep_patterns = [
            "package.json", "requirements.txt", "go.mod", "Cargo.toml",
            "pom.xml", "build.gradle", "composer.json", "Gemfile",
            "yarn.lock", "package-lock.json", "poetry.lock"
        ]
        
        dep_files = {}
        for pattern in dep_patterns:
            try:
                for file_path in project_path.glob(f"**/{pattern}"):
                    if file_path.is_file():
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            relative_path = file_path.relative_to(project_path)
                            dep_files[str(relative_path)] = content[:5000]
                        except Exception:
                            continue
            except Exception:
                continue
        
        return dep_files
    
    def _get_security_relevant_files(self, project_path: Path) -> str:
        """Get security-relevant files content."""
        security_patterns = [
            "**/auth*", "**/login*", "**/security*", "**/crypto*",
            "**/password*", "**/token*", "**/session*", "**/oauth*",
            "**/.env*", "**/config*", "**/secrets*"
        ]
        
        security_files = []
        for pattern in security_patterns:
            try:
                for file_path in project_path.glob(pattern):
                    if file_path.is_file() and file_path.stat().st_size < 20000:
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            relative_path = file_path.relative_to(project_path)
                            security_files.append(f"=== {relative_path} ===\n{content[:1000]}\n")
                        except Exception:
                            continue
            except Exception:
                continue
        
        return "\n".join(security_files[:15])
    
    def _get_performance_files(self, project_path: Path) -> str:
        """Get performance-critical files content."""
        perf_patterns = [
            "**/database*", "**/db*", "**/cache*", "**/queue*",
            "**/worker*", "**/async*", "**/parallel*", "**/stream*",
            "**/api*", "**/service*", "**/handler*"
        ]
        
        perf_files = []
        for pattern in perf_patterns:
            try:
                for file_path in project_path.glob(pattern):
                    if file_path.is_file() and file_path.stat().st_size < 30000:
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            relative_path = file_path.relative_to(project_path)
                            perf_files.append(f"=== {relative_path} ===\n{content[:1500]}\n")
                        except Exception:
                            continue
            except Exception:
                continue
        
        return "\n".join(perf_files[:10])


def get_language_analyzer() -> UniversalCodeAnalyzer:
    """Get universal code analyzer instance."""
    return UniversalCodeAnalyzer()