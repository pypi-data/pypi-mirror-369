"""
Serena manager for handling installation and configuration.
"""

import asyncio
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SerenaManager:
    """Manages Serena installation and configuration."""

    def __init__(self):
        """Initialize the Serena manager."""
        self.config_dir = Path.home() / ".serena-cli"
        self.config_dir.mkdir(exist_ok=True)
        
        # Check Python version compatibility
        self.python_version = self._get_python_version()
        self.is_python_compatible = self._check_python_compatibility()
        
        if not self.is_python_compatible:
            logger.warning(f"Python {self.python_version} may not be compatible with Serena. "
                          f"Recommended: Python 3.10+")

    def _get_python_version(self) -> str:
        """Get current Python version."""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def _check_python_compatibility(self) -> bool:
        """Check if Python version is compatible with Serena."""
        # Serena currently supports Python 3.10+ (only Python 3.13+ may have issues)
        major, minor = sys.version_info.major, sys.version_info.minor
        return major == 3 and minor >= 10

    async def enable_in_project(
        self, 
        project_path: str, 
        context: str = "ide-assistant",
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Enable Serena in the specified project.
        
        Args:
            project_path: Path to the project
            context: Serena context (e.g., 'ide-assistant')
            force: Force reinstallation
            
        Returns:
            Dictionary with operation results
        """
        try:
            project_path = Path(project_path).resolve()
            
            # Check if Serena is already enabled
            if not force and self._is_serena_enabled(project_path):
                return {
                    "status": "already_enabled",
                    "message": "Serena 已经在此项目中启用"
                }
            
            # Check Python compatibility
            if not self.is_python_compatible:
                logger.warning("Python 版本可能不兼容 Serena，但将继续尝试安装")
            
            # Install Serena if needed
            install_result = await self._install_serena(force)
            if not install_result["success"]:
                return install_result
            
            # Generate project configuration
            config_result = self._generate_project_config(project_path, context)
            if not config_result["success"]:
                return config_result
            
            return {
                "success": True,
                "install_result": install_result,
                "config_result": config_result,
                "message": "Serena 项目配置完成",
                "python_compatibility": {
                    "version": self.python_version,
                    "compatible": self.is_python_compatible,
                    "warning": "Python 版本可能不兼容，建议使用 Python 3.10+" if not self.is_python_compatible else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error enabling Serena in project: {e}")
            return {"success": False, "error": str(e)}

    def enable_serena(self, project_path: str, force: bool = False) -> dict:
        """
        Enable Serena in the specified project (synchronous version).
        
        Args:
            project_path: Path to the project
            force: Force enable even if Python version may not be compatible
            
        Returns:
            Dictionary with operation results
        """
        try:
            project_path = Path(project_path).resolve()
            
            # Check if project is valid
            if not self._is_valid_project(project_path):
                return {
                    "success": False,
                    "error": "Invalid project path or not a recognized project"
                }
            
            # Check Python compatibility (unless forced)
            if not force:
                python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                is_compatible = (
                    sys.version_info.major == 3 and 
                    sys.version_info.minor >= 10
                )
                
                if not is_compatible:
                    return {
                        "success": False,
                        "error": f"Python version {python_version} may not be compatible with Serena. Recommended: Python 3.10+"
                    }
            else:
                logger.warning("⚠️  Force mode: Skipping Python version compatibility check")
            
            # Check if Serena is already enabled
            if self._is_serena_enabled(project_path):
                return {
                    "success": True,
                    "message": "Serena is already enabled in this project",
                    "project_path": str(project_path),
                    "context": "ide-assistant"
                }
            
            # Create project configuration
            config = self._generate_project_config(project_path, "ide-assistant")
            
            if config:
                return {
                    "success": True,
                    "message": "Serena enabled successfully",
                    "project_path": str(project_path),
                    "context": "ide-assistant",
                    "config": config
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create project configuration"
                }
                
        except Exception as e:
            logger.error(f"Error enabling Serena: {e}")
            return {"success": False, "error": str(e)}

    def get_status_sync(self, project_path: str) -> dict:
        """
        Get Serena status for the specified project (synchronous version).
        
        Args:
            project_path: Path to the project
            
        Returns:
            Dictionary with status information
        """
        try:
            project_path = Path(project_path).resolve()
            
            # Check if Serena is enabled
            serena_enabled = self._is_serena_enabled(project_path)
            
            # Get project configuration
            project_config = self._get_project_config(project_path)
            
            # Check if Serena is installed
            serena_installed = self._is_serena_installed()
            
            # Get Python version
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            
            status = {
                "project_path": str(project_path),
                "serena_enabled": serena_enabled,
                "config_exists": bool(project_config),
                "serena_installed": serena_installed,
                "python_version": python_version,
                "installation_method": "Not installed",
                "serena_context": "Not configured"
            }
            
            if serena_enabled and project_config:
                status["installation_method"] = project_config.get("installation_method", "Unknown")
                status["serena_context"] = project_config.get("serena_context", "Not specified")
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting Serena status: {e}")
            return {"error": str(e)}

    async def get_status(self, project_path: str) -> Dict[str, Any]:
        """
        Get Serena status for the specified project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Dictionary with status information
        """
        try:
            project_path = Path(project_path).resolve()
            
            status = {
                "project_path": str(project_path),
                "serena_enabled": self._is_serena_enabled(project_path),
                "config_exists": self._has_project_config(project_path),
                "serena_installed": self._is_serena_installed(),
                "project_config": self._get_project_config(project_path),
                "python_compatibility": {
                    "version": self.python_version,
                    "compatible": self.is_python_compatible,
                    "recommended": "3.10+"
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting Serena status: {e}")
            return {"error": str(e)}

    async def _install_serena(self, force: bool = False) -> Dict[str, Any]:
        """
        Install or update Serena.
        
        Args:
            force: Force reinstallation
            
        Returns:
            Dictionary with installation results
        """
        try:
            if not force and self._is_serena_installed():
                return {"success": True, "message": "Serena 已安装"}
            
            # Try to install using uv first
            if self._is_uv_available():
                result = await self._install_with_uv()
                if result["success"]:
                    return result
            
            # Fallback to pip
            result = await self._install_with_pip()
            return result
            
        except Exception as e:
            logger.error(f"Error installing Serena: {e}")
            return {"success": False, "error": str(e)}

    def _is_serena_enabled(self, project_path: Path) -> bool:
        """Check if Serena is enabled in the project."""
        project_config = project_path / ".serena-cli" / "project.yml"
        return project_config.exists()

    def _has_project_config(self, project_path: Path) -> bool:
        """Check if project has Serena configuration."""
        serena_config = project_path / ".serena-cli" / "project.yml"
        return serena_config.exists()

    def _is_serena_installed(self) -> bool:
        """Check if Serena is installed."""
        try:
            # Try to import serena
            import serena
            return True
        except ImportError:
            return False

    def _is_uv_available(self) -> bool:
        """Check if uv is available."""
        try:
            result = subprocess.run(
                ["uv", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def _install_with_uv(self) -> Dict[str, Any]:
        """Install Serena using uv."""
        try:
            cmd = [
                "uv", "pip", "install", "--from", 
                "git+https://github.com/oraios/serena"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            if process.returncode == 0:
                return {"success": True, "message": "Serena 通过 uv 安装成功"}
            else:
                error_msg = stderr.decode() if stderr else "未知错误"
                return {
                    "success": False, 
                    "error": f"uv 安装失败: {error_msg}",
                    "fallback": "将尝试使用 pip 安装"
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False, 
                "error": "uv 安装超时",
                "fallback": "将尝试使用 pip 安装"
            }
        except Exception as e:
            return {
                "success": False, 
                "error": f"uv 安装异常: {str(e)}",
                "fallback": "将尝试使用 pip 安装"
            }

    async def _install_with_pip(self) -> Dict[str, Any]:
        """Install Serena using pip."""
        try:
            # Try different installation methods
            install_methods = [
                # Method 1: Direct git install
                [sys.executable, "-m", "pip", "install", "git+https://github.com/oraios/serena"],
                # Method 2: With --user flag
                [sys.executable, "-m", "pip", "install", "--user", "git+https://github.com/oraios/serena"],
                # Method 3: With --break-system-packages (for newer Python versions)
                [sys.executable, "-m", "pip", "install", "--break-system-packages", "git+https://github.com/oraios/serena"]
            ]
            
            for i, cmd in enumerate(install_methods, 1):
                try:
                    logger.info(f"尝试安装方法 {i}: {' '.join(cmd)}")
                    
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
                    
                    if process.returncode == 0:
                        return {
                            "success": True, 
                            "message": f"Serena 通过 pip 安装成功 (方法 {i})",
                            "method": f"pip method {i}"
                        }
                    else:
                        error_msg = stderr.decode() if stderr else "未知错误"
                        logger.warning(f"安装方法 {i} 失败: {error_msg}")
                        
                except asyncio.TimeoutError:
                    logger.warning(f"安装方法 {i} 超时")
                except Exception as e:
                    logger.warning(f"安装方法 {i} 异常: {e}")
            
            # All methods failed
            return {
                "success": False, 
                "error": "所有安装方法都失败了",
                "suggestions": [
                    "检查网络连接",
                    "确保 Python 版本兼容 (推荐 3.10+)",
                    "尝试手动安装: pip install git+https://github.com/oraios/serena",
                    "检查是否有权限问题"
                ]
            }
                
        except Exception as e:
            logger.error(f"Error in pip installation: {e}")
            return {"success": False, "error": f"pip 安装异常: {str(e)}"}

    def _generate_project_config(self, project_path: Path, context: str) -> Dict[str, Any]:
        """Generate project configuration."""
        try:
            # Create .serena-cli directory
            serena_dir = project_path / ".serena-cli"
            serena_dir.mkdir(exist_ok=True)
            
            # Create project configuration file
            config_file = serena_dir / "project.yml"
            config_content = self._get_project_config_template(project_path, context)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            return {"success": True, "config_file": str(config_file)}
            
        except Exception as e:
            logger.error(f"Error generating project config: {e}")
            return {"success": False, "error": str(e)}


    def _get_project_config_template(self, project_path: Path, context: str) -> str:
        """Get project configuration template."""
        return f"""# Serena CLI 项目配置
# 项目: {project_path.name}
# 路径: {project_path}
# 生成时间: {self._get_current_timestamp()}
# Python 版本: {self.python_version}
# 兼容性: {'✅ 兼容' if self.is_python_compatible else '⚠️ 可能不兼容'}

project_name: "{project_path.name}"
serena_context: "{context}"
read_only: false
auto_start: true

# 包含的工具
included_tools:
  - find_symbol
  - read_file
  - execute_shell_command
  - list_dir
  - get_symbols_overview
  - search_for_pattern

# 排除的工具
excluded_tools: []

# 项目特定设置
project_settings:
  language_servers: []
  custom_prompts: []
  memory_enabled: true

# Python 兼容性信息
python_compatibility:
  version: "{self.python_version}"
  compatible: {str(self.is_python_compatible).lower()}
  recommended: "3.10+"
  warning: "{'Python 版本可能不兼容 Serena，建议使用 Python 3.10+' if not self.is_python_compatible else 'Python 版本兼容'}"
"""



    def _get_project_config(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Get existing project configuration."""
        try:
            config_file = project_path / ".serena-cli" / "project.yml"
            if config_file.exists():
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            return None
        except Exception:
            return None

    def _get_current_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_installation_guide(self) -> dict:
        """Get installation guide with compatibility information."""
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        recommended_version = "3.10+"
        
        # Check if current Python version is compatible
        is_compatible = (
            sys.version_info.major == 3 and 
            sys.version_info.minor >= 10
        )
        
        guide = {
            "python_version": python_version,
            "recommended_version": recommended_version,
            "compatible": is_compatible,
            "warnings": [],
            "quick_solutions": []
        }
        
        if not is_compatible:
            guide["warnings"].append(
                f"Current Python version {python_version} may not be compatible with Serena"
            )
            guide["warnings"].append(
                f"Recommended: Python {recommended_version}"
            )
            
            # Add quick solutions
            guide["quick_solutions"] = [
                {
                    "title": "Use pyenv to install Python 3.10+",
                    "commands": [
                        "pyenv install 3.10.12",
                        "pyenv local 3.10.12",
                        "python -m venv venv",
                        "source venv/bin/activate"
                    ]
                },
                {
                    "title": "Use conda to create a compatible environment",
                    "commands": [
                        "conda create -n serena python=3.10",
                        "conda activate serena"
                    ]
                },
                {
                    "title": "Use Docker with Python 3.10",
                    "commands": [
                        "docker run -it python:3.10-slim bash"
                    ]
                },
                {
                    "title": "Continue with current version (may have issues)",
                    "commands": [
                        "pip install serena-agent"
                    ]
                }
            ]
        
        return guide

    def _is_valid_project(self, project_path: Path) -> bool:
        """Check if the path is a valid project."""
        # Check for common project indicators
        indicators = [
            ".git",
            "package.json",
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "README.md",
            "src/",
            "lib/",
            "app/"
        ]
        
        for indicator in indicators:
            if (project_path / indicator).exists():
                return True
        return False
