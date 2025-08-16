"""
Configuration management for Serena CLI.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .project_detector import ProjectDetector


class ConfigManager:
    """Manage global and project-specific configurations."""
    
    def __init__(self):
        """Initialize configuration manager."""
        # Global config directory
        self.global_config_dir = Path.home() / ".serena-cli"
        self.global_config_file = self.global_config_dir / "config.yml"
        self.logs_dir = self.global_config_dir / "logs"
        
        # Ensure directories exist
        self.global_config_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize default config if needed
        if not self.global_config_file.exists():
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default global configuration."""
        default_config = self._get_default_config()
        self._write_yaml(self.global_config_file, default_config)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default global configuration."""
        return {
            "default_context": "ide-assistant",
            "install_method": "uv",
            "log_level": "INFO",
            "auto_start": True,
            "port": 24282,
            "dashboard": {
                "enabled": True,
                "port": 24282,
                "auto_open": True
            },
            "logging": {
                "level": "INFO",
                "file": str(self.logs_dir / "serena-cli.log"),
                "max_size": "10MB",
                "backup_count": 5
            },
            "serena": {
                "default_context": "ide-assistant",
                "auto_install": True,
                "preferred_installer": "uv"
            }
        }
    
    def get_config(self, config_type: str = "global", project_path: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration."""
        if config_type == "global":
            return self._read_yaml(self.global_config_file) or {}
        elif config_type == "project":
            if not project_path:
                detector = ProjectDetector()
                project_path = detector.detect_current_project()
            
            if not project_path:
                return {}
            
            project_config_dir = Path(project_path) / ".serena-cli"
            project_config_file = project_config_dir / "project.yml"
            
            if project_config_file.exists():
                return self._read_yaml(project_config_file) or {}
            else:
                return self._create_project_config(project_path)
        
        return {}
    
    def _create_project_config(self, project_path: str) -> Dict[str, Any]:
        """Create default project configuration."""
        project_path = Path(project_path)
        project_config_dir = project_path / ".serena-cli"
        project_config_file = project_config_dir / "project.yml"
        
        # Ensure project config directory exists
        project_config_dir.mkdir(exist_ok=True)
        
        # Create default project config
        default_project_config = {
            "project_name": project_path.name,
            "serena_context": "ide-assistant",
            "read_only": False,
            "auto_start": True,
            "included_tools": [
                "find_symbol",
                "read_file",
                "execute_shell_command",
                "list_dir",
                "get_symbols_overview",
                "search_for_pattern"
            ],
            "excluded_tools": [],
            "project_settings": {
                "memory_enabled": True,
                "language_servers": [],
                "custom_prompts": []
            }
        }
        
        self._write_yaml(project_config_file, default_project_config)
        return default_project_config
    
    def update_config(self, config_type: str, updates: Dict[str, Any], project_path: Optional[str] = None) -> bool:
        """Update configuration."""
        try:
            if config_type == "global":
                config = self._read_yaml(self.global_config_file) or {}
                config.update(updates)
                self._write_yaml(self.global_config_file, config)
                return True
            
            elif config_type == "project":
                if not project_path:
                    detector = ProjectDetector()
                    project_path = detector.detect_current_project()
                
                if not project_path:
                    return False
                
                project_config_dir = Path(project_path) / ".serena-cli"
                project_config_file = project_config_dir / "project.yml"
                
                if not project_config_file.exists():
                    self._create_project_config(project_path)
                
                config = self._read_yaml(project_config_file) or {}
                config.update(updates)
                self._write_yaml(project_config_file, config)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    def edit_config(self, config_type: str, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Open configuration file for editing."""
        try:
            if config_type == "global":
                config_file = self.global_config_file
                if not config_file.exists():
                    self._create_default_config()
            elif config_type == "project":
                if not project_path:
                    detector = ProjectDetector()
                    project_path = detector.detect_current_project()
                
                if not project_path:
                    return {"success": False, "error": "无法检测到项目路径"}
                
                project_config_dir = Path(project_path) / ".serena-cli"
                project_config_file = project_config_dir / "project.yml"
                
                if not project_config_file.exists():
                    self._create_project_config(project_path)
                
                config_file = project_config_file
            else:
                return {"success": False, "error": f"不支持的配置类型: {config_type}"}
            
            # Open file in default editor
            self._open_file_in_editor(config_file)
            
            return {
                "success": True,
                "message": "配置已打开进行编辑",
                "config_file": str(config_file)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _open_file_in_editor(self, file_path: Path):
        """Open file in default system editor."""
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", file_path])
            else:
                subprocess.run(["xdg-open", file_path])
        except Exception:
            # Fallback to default editor
            editor = os.environ.get("EDITOR", "nano")
            subprocess.run([editor, file_path])
    
    def _read_yaml(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Read YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return None
    
    def _write_yaml(self, file_path: Path, data: Dict[str, Any]):
        """Write YAML file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
        except Exception as e:
            print(f"Error writing YAML file: {e}")
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration structure."""
        required_keys = ["default_context", "install_method"]
        return all(key in config for key in required_keys)
