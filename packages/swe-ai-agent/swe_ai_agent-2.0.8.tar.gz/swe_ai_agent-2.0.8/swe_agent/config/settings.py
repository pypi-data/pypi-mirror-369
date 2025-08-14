"""
Settings Configuration - Manages configuration and settings for the SWE Agent system.
Contains configuration classes and environment variable handling.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)

@dataclass
class Settings:
    """
    Main configuration class for the SWE Agent system.
    
    Contains all configuration parameters and settings for the application.
    """
    
    # Core paths
    repo_path: Path
    output_dir: Path
    
    # Execution settings
    verbose: bool = False
    analyze_only: bool = False
    
    # Agent settings
    max_iterations: int = 20
    max_consecutive_visits: int = 5
    max_message_history: int = 50
    use_planner: bool = False
    enable_mcp: bool = False
    
    # Tool settings
    enable_code_analysis: bool = True
    enable_file_editing: bool = True
    enable_patch_generation: bool = True
    
    # Output settings
    save_intermediate_results: bool = True
    generate_reports: bool = True
    backup_files: bool = True
    
    # Performance settings
    timeout_seconds: int = 300
    memory_limit_mb: int = 1024
    
    # Environment variables
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    # Additional configuration
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization setup and validation."""
        # Ensure paths are Path objects
        if isinstance(self.repo_path, str):
            self.repo_path = Path(self.repo_path)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        
        # Resolve paths
        self.repo_path = self.repo_path.resolve()
        self.output_dir = self.output_dir.resolve()
        
        # Load environment variables
        self._load_environment_variables()
        
        # Validate configuration
        self._validate_configuration()
        
        # Create output directory
        self._ensure_output_directory()
    
    def _load_environment_variables(self) -> None:
        """Load relevant environment variables."""
        env_mapping = {
            "SWE_AGENT_VERBOSE": "verbose",
            "SWE_AGENT_ANALYZE_ONLY": "analyze_only",
            "SWE_AGENT_MAX_ITERATIONS": "max_iterations",
            "SWE_AGENT_MAX_VISITS": "max_consecutive_visits",
            "SWE_AGENT_TIMEOUT": "timeout_seconds",
            "SWE_AGENT_MEMORY_LIMIT": "memory_limit_mb",
            "SWE_AGENT_BACKUP_FILES": "backup_files"
        }
        
        for env_var, setting_name in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    # Convert to appropriate type
                    if setting_name in ["verbose", "analyze_only", "backup_files"]:
                        value = env_value.lower() in ["true", "1", "yes", "on"]
                    elif setting_name in ["max_iterations", "max_consecutive_visits", "timeout_seconds", "memory_limit_mb"]:
                        value = int(env_value)
                    else:
                        value = env_value
                    
                    setattr(self, setting_name, value)
                    logger.info(f"Loaded {setting_name} from environment: {value}")
                    
                except ValueError as e:
                    logger.warning(f"Invalid environment variable {env_var}: {e}")
        
        # Store all environment variables for potential use
        self.env_vars = dict(os.environ)
    
    def _validate_configuration(self) -> None:
        """Validate configuration settings."""
        validation_errors = []
        
        # Validate paths
        if not self.repo_path.exists():
            validation_errors.append(f"Repository path does not exist: {self.repo_path}")
        
        if not self.repo_path.is_dir():
            validation_errors.append(f"Repository path is not a directory: {self.repo_path}")
        
        # Validate numeric settings
        if self.max_iterations <= 0:
            validation_errors.append("max_iterations must be positive")
        
        if self.max_consecutive_visits <= 0:
            validation_errors.append("max_consecutive_visits must be positive")
        
        if self.timeout_seconds <= 0:
            validation_errors.append("timeout_seconds must be positive")
        
        if self.memory_limit_mb <= 0:
            validation_errors.append("memory_limit_mb must be positive")
        
        # Check for Python files in repository
        python_files = list(self.repo_path.rglob("*.py"))
        if not python_files:
            logger.warning(f"No Python files found in repository: {self.repo_path}")
        
        if validation_errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(validation_errors)
            raise ValueError(error_msg)
    
    def _ensure_output_directory(self) -> None:
        """Ensure output directory exists."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            subdirs = ["backups", "reports", "patches", "analysis"]
            for subdir in subdirs:
                (self.output_dir / subdir).mkdir(exist_ok=True)
                
        except Exception as e:
            logger.error(f"Failed to create output directory: {e}")
            raise
    
    @classmethod
    def from_file(cls, config_path: Path) -> "Settings":
        """
        Load settings from a configuration file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Settings instance
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Convert string paths to Path objects
            if "repo_path" in config_data:
                config_data["repo_path"] = Path(config_data["repo_path"])
            if "output_dir" in config_data:
                config_data["output_dir"] = Path(config_data["output_dir"])
            
            return cls(**config_data)
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            raise
    
    def save_to_file(self, config_path: Path) -> None:
        """
        Save settings to a configuration file.
        
        Args:
            config_path: Path to save configuration
        """
        try:
            config_data = {
                "repo_path": str(self.repo_path),
                "output_dir": str(self.output_dir),
                "verbose": self.verbose,
                "analyze_only": self.analyze_only,
                "max_iterations": self.max_iterations,
                "max_consecutive_visits": self.max_consecutive_visits,
                "max_message_history": self.max_message_history,
                "enable_code_analysis": self.enable_code_analysis,
                "enable_file_editing": self.enable_file_editing,
                "enable_patch_generation": self.enable_patch_generation,
                "save_intermediate_results": self.save_intermediate_results,
                "generate_reports": self.generate_reports,
                "backup_files": self.backup_files,
                "timeout_seconds": self.timeout_seconds,
                "memory_limit_mb": self.memory_limit_mb,
                "custom_config": self.custom_config
            }
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to: {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            raise
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Get configuration specific to an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent-specific configuration
        """
        base_config = {
            "max_consecutive_visits": self.max_consecutive_visits,
            "verbose": self.verbose,
            "timeout_seconds": self.timeout_seconds
        }
        
        # Agent-specific overrides
        agent_configs = {
            "software_engineer": {
                "enable_patch_generation": self.enable_patch_generation,
                "max_consecutive_visits": min(self.max_consecutive_visits, 3)
            },
            "code_analyzer": {
                "enable_code_analysis": self.enable_code_analysis,
                "max_consecutive_visits": min(self.max_consecutive_visits, 5)
            },
            "editor": {
                "enable_file_editing": self.enable_file_editing,
                "backup_files": self.backup_files,
                "max_consecutive_visits": min(self.max_consecutive_visits, 4)
            }
        }
        
        if agent_name in agent_configs:
            base_config.update(agent_configs[agent_name])
        
        # Add custom configuration
        if agent_name in self.custom_config:
            base_config.update(self.custom_config[agent_name])
        
        return base_config
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """
        Get configuration specific to a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool-specific configuration
        """
        base_config = {
            "repo_path": self.repo_path,
            "output_dir": self.output_dir,
            "verbose": self.verbose,
            "backup_files": self.backup_files
        }
        
        # Tool-specific overrides
        tool_configs = {
            "swe_tools": {
                "enable_patch_generation": self.enable_patch_generation,
                "save_intermediate_results": self.save_intermediate_results
            },
            "code_analysis_tools": {
                "enable_code_analysis": self.enable_code_analysis,
                "generate_reports": self.generate_reports
            },
            "editing_tools": {
                "enable_file_editing": self.enable_file_editing,
                "backup_files": self.backup_files
            }
        }
        
        if tool_name in tool_configs:
            base_config.update(tool_configs[tool_name])
        
        # Add custom configuration
        if tool_name in self.custom_config:
            base_config.update(self.custom_config[tool_name])
        
        return base_config
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """
        Get workflow-specific configuration.
        
        Returns:
            Workflow configuration
        """
        return {
            "max_iterations": self.max_iterations,
            "max_message_history": self.max_message_history,
            "timeout_seconds": self.timeout_seconds,
            "memory_limit_mb": self.memory_limit_mb,
            "analyze_only": self.analyze_only,
            "repo_path": self.repo_path,
            "output_dir": self.output_dir,
            "verbose": self.verbose
        }
    
    def update_setting(self, key: str, value: Any) -> None:
        """
        Update a specific setting.
        
        Args:
            key: Setting key
            value: New value
        """
        if hasattr(self, key):
            setattr(self, key, value)
            logger.info(f"Updated setting {key}: {value}")
        else:
            logger.warning(f"Unknown setting: {key}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific setting value.
        
        Args:
            key: Setting key
            default: Default value if setting not found
            
        Returns:
            Setting value
        """
        return getattr(self, key, default)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all settings as a dictionary.
        
        Returns:
            Dictionary of all settings
        """
        return {
            "repo_path": str(self.repo_path),
            "output_dir": str(self.output_dir),
            "verbose": self.verbose,
            "analyze_only": self.analyze_only,
            "max_iterations": self.max_iterations,
            "max_consecutive_visits": self.max_consecutive_visits,
            "max_message_history": self.max_message_history,
            "enable_code_analysis": self.enable_code_analysis,
            "enable_file_editing": self.enable_file_editing,
            "enable_patch_generation": self.enable_patch_generation,
            "save_intermediate_results": self.save_intermediate_results,
            "generate_reports": self.generate_reports,
            "backup_files": self.backup_files,
            "timeout_seconds": self.timeout_seconds,
            "memory_limit_mb": self.memory_limit_mb,
            "custom_config": self.custom_config
        }
    
    def validate_runtime_environment(self) -> bool:
        """
        Validate the runtime environment.
        
        Returns:
            True if environment is valid, False otherwise
        """
        try:
            # Check Python version
            import sys
            if sys.version_info < (3, 8):
                logger.error("Python 3.8 or higher is required")
                return False
            
            # Check required modules
            required_modules = [
                "langchain",
                "langgraph",
                "rich",
                "pathlib",
                "ast",
                "json"
            ]
            
            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    logger.error(f"Required module not found: {module}")
                    return False
            
            # Check repository accessibility
            if not os.access(self.repo_path, os.R_OK):
                logger.error(f"Repository path is not readable: {self.repo_path}")
                return False
            
            # Check output directory writability
            if not os.access(self.output_dir, os.W_OK):
                logger.error(f"Output directory is not writable: {self.output_dir}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Runtime environment validation failed: {e}")
            return False
    
    def __str__(self) -> str:
        """String representation of settings."""
        return f"Settings(repo_path={self.repo_path}, output_dir={self.output_dir}, verbose={self.verbose})"
    
    def __repr__(self) -> str:
        """Detailed string representation of settings."""
        return f"Settings({self.get_all_settings()})"
