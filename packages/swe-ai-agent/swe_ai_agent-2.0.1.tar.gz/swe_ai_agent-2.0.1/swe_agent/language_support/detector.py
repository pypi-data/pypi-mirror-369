"""
Language-agnostic detector using Claude's natural language understanding.
No hardcoded language rules - leverages LLM's inherent language comprehension.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from utils.anthropic_client import get_anthropic_client

logger = logging.getLogger(__name__)

class LanguageDetector:
    """
    Language detector that uses Claude's natural understanding 
    instead of hardcoded patterns or extensions.
    """
    
    def __init__(self):
        self.anthropic_client = get_anthropic_client()
        logger.info("🌍 Language detector initialized with Claude comprehension")
    
    def detect_project_languages(self, project_path: Path) -> Dict[str, any]:
        """
        Analyze entire project to understand all languages and technologies used.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Comprehensive language analysis
        """
        # Get file structure and sample contents
        file_info = self._gather_project_files(project_path)
        
        prompt = f"""
        Analyze this project structure and file contents to identify all programming languages, 
        frameworks, and technologies used. Don't rely on file extensions alone - examine the 
        actual code content.

        Project files and sample contents:
        {file_info}

        Provide a comprehensive analysis including:
        1. Primary programming languages (with confidence levels)
        2. Frameworks and libraries detected
        3. Build systems and tooling
        4. Database technologies
        5. Configuration formats
        6. Development environment setup
        7. Suggested development workflow

        Focus on what the code actually does, not just file extensions.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
            system="You are an expert polyglot developer who can understand any programming language and technology stack by examining code content."
        )
        
        return {
            "analysis": response.content,
            "project_path": str(project_path),
            "file_count": len(file_info),
            "detection_method": "claude_analysis"
        }
    
    def detect_file_language(self, file_path: Path) -> Dict[str, any]:
        """
        Detect language and provide analysis for a specific file.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            File language analysis
        """
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')[:5000]  # First 5K chars
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        prompt = f"""
        Analyze this file to determine its programming language, purpose, and characteristics:

        File: {file_path.name}
        Content preview:
        {content}

        Provide:
        1. Programming language (with confidence level)
        2. File purpose and functionality
        3. Code quality assessment
        4. Dependencies and imports used
        5. Suggested improvements or patterns
        6. How this file fits into a larger project

        Focus on understanding the actual code, not just file extension.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
            system="You are an expert code analyst who can understand any programming language and provide detailed technical analysis."
        )
        
        return {
            "file_path": str(file_path),
            "analysis": response.content,
            "content_preview": content[:500],
            "detection_method": "claude_analysis"
        }
    
    def suggest_development_environment(self, project_path: Path) -> Dict[str, any]:
        """
        Analyze project and suggest optimal development environment setup.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Development environment recommendations
        """
        project_analysis = self.detect_project_languages(project_path)
        
        prompt = f"""
        Based on this project analysis, suggest the optimal development environment setup:

        {project_analysis['analysis']}

        Provide specific recommendations for:
        1. Required runtime environments and versions
        2. Package managers and dependency installation
        3. Build tools and compilation steps
        4. Testing frameworks and commands
        5. Development server setup
        6. IDE/editor configurations
        7. Debugging tools and techniques
        8. Deployment considerations

        Make recommendations practical and actionable for a headless development environment.
        """
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
            system="You are a DevOps expert who can recommend optimal development environments for any technology stack."
        )
        
        return {
            "project_path": str(project_path),
            "recommendations": response.content,
            "based_on_analysis": project_analysis['analysis']
        }
    
    def _gather_project_files(self, project_path: Path, max_files: int = 50) -> str:
        """
        Gather representative files from project for analysis.
        
        Args:
            project_path: Path to project
            max_files: Maximum number of files to include
            
        Returns:
            Formatted string with file information
        """
        files_info = []
        file_count = 0
        
        # Common patterns to prioritize
        priority_patterns = [
            "README", "package.json", "requirements.txt", "Cargo.toml", 
            "go.mod", "build.gradle", "pom.xml", "composer.json",
            "main.", "index.", "app.", "server.", "client."
        ]
        
        # Get all files
        all_files = []
        for pattern in ["**/*"]:
            try:
                for file_path in project_path.glob(pattern):
                    if file_path.is_file() and file_count < max_files:
                        all_files.append(file_path)
                        file_count += 1
            except Exception as e:
                logger.warning(f"Error accessing files: {e}")
        
        # Sort by priority and size
        def file_priority(file_path):
            name = file_path.name.lower()
            # Higher priority for important files
            for pattern in priority_patterns:
                if pattern.lower() in name:
                    return 0
            # Medium priority for smaller files
            try:
                size = file_path.stat().st_size
                if size < 10000:  # Files under 10KB
                    return 1
                elif size < 100000:  # Files under 100KB
                    return 2
                else:
                    return 3
            except:
                return 3
        
        all_files.sort(key=file_priority)
        
        # Gather file information
        for file_path in all_files[:max_files]:
            try:
                size = file_path.stat().st_size
                relative_path = file_path.relative_to(project_path)
                
                # Get file content sample
                content_sample = ""
                if size < 50000:  # Only read files under 50KB
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        content_sample = content[:1000]  # First 1K chars
                    except:
                        content_sample = "[binary or unreadable file]"
                
                files_info.append(f"""
File: {relative_path}
Size: {size} bytes
Content sample:
{content_sample}
---""")
                
            except Exception as e:
                logger.warning(f"Error reading file {file_path}: {e}")
        
        return "\n".join(files_info)