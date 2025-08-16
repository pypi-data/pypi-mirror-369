"""
Project detection and validation utilities.
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class ProjectDetector:
    """Detects and validates projects."""

    def __init__(self):
        """Initialize the project detector."""
        # Common project indicators
        self.project_indicators = [
            # Version control
            ".git",
            ".svn",
            ".hg",
            
            # Package managers
            "package.json",      # Node.js
            "pyproject.toml",    # Python
            "requirements.txt",  # Python
            "Cargo.toml",        # Rust
            "go.mod",           # Go
            "pom.xml",          # Java Maven
            "build.gradle",      # Java Gradle
            "composer.json",     # PHP
            "Gemfile",          # Ruby
            
            # Project files
            "README.md",
            "README.txt",
            "CHANGELOG.md",
            "LICENSE",
            "Makefile",
            "CMakeLists.txt",
            
            # IDE/Editor
            ".vscode",
            ".idea",
            ".cursor",
            
            # Build tools
            "Makefile",
            "Dockerfile",
            "docker-compose.yml",
            ".github",
            ".gitlab-ci.yml",
            "Jenkinsfile",
            
            # Documentation
            "docs/",
            "documentation/",
            "api/",
            
            # Source code directories
            "src/",
            "lib/",
            "app/",
            "main/",
            "source/",
        ]

    def detect_current_project(self) -> Optional[str]:
        """
        Detect the current project from the current working directory.
        
        Returns:
            Project path if detected, None otherwise
        """
        try:
            current_dir = Path.cwd()
            return self._find_project_root(current_dir)
        except Exception as e:
            logger.error(f"Error detecting current project: {e}")
            return None

    def detect_project_from_path(self, path: str) -> Optional[str]:
        """
        Detect project from a specific path.
        
        Args:
            path: Path to check
            
        Returns:
            Project path if detected, None otherwise
        """
        try:
            path = Path(path).resolve()
            return self._find_project_root(path)
        except Exception as e:
            logger.error(f"Error detecting project from path {path}: {e}")
            return None

    def validate_project(self, project_path: str) -> bool:
        """
        Validate if a path is a valid project.
        
        Args:
            project_path: Path to validate
            
        Returns:
            True if valid project, False otherwise
        """
        try:
            project_path = Path(project_path).resolve()
            
            # Check if path exists and is a directory
            if not project_path.exists() or not project_path.is_dir():
                return False
            
            # Check if it's a project by looking for indicators
            return self._has_project_indicators(project_path)
            
        except Exception as e:
            logger.error(f"Error validating project {project_path}: {e}")
            return False

    def get_project_info(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Dictionary with project information
        """
        try:
            project_path = Path(project_path).resolve()
            
            if not self.validate_project(project_path):
                return None
            
            info = {
                "path": str(project_path),
                "name": project_path.name,
                "type": self._detect_project_type(project_path),
                "indicators": self._get_project_indicators(project_path),
                "size": self._get_project_size(project_path),
                "languages": self._detect_languages(project_path),
                "has_serena": self._has_serena_config(project_path),
                "has_panda_config": self._has_panda_config(project_path)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting project info for {project_path}: {e}")
            return None

    def list_projects_in_directory(self, directory: str) -> List[str]:
        """
        List all projects in a directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of project paths
        """
        try:
            directory = Path(directory).resolve()
            projects = []
            
            if not directory.exists() or not directory.is_dir():
                return projects
            
            # Look for immediate subdirectories that are projects
            for item in directory.iterdir():
                if item.is_dir() and self.validate_project(item):
                    projects.append(str(item))
            
            return projects
            
        except Exception as e:
            logger.error(f"Error listing projects in {directory}: {e}")
            return []

    def _find_project_root(self, start_path: Path) -> Optional[str]:
        """
        Find the project root starting from a given path.
        
        Args:
            start_path: Starting path for search
            
        Returns:
            Project root path if found, None otherwise
        """
        try:
            current = start_path
            
            # Search upwards through parent directories
            while current != current.parent:
                if self._has_project_indicators(current):
                    return str(current)
                current = current.parent
            
            # Check the starting path itself
            if self._has_project_indicators(start_path):
                return str(start_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding project root from {start_path}: {e}")
            return None

    def _has_project_indicators(self, path: Path) -> bool:
        """
        Check if a path has project indicators.
        
        Args:
            path: Path to check
            
        Returns:
            True if has indicators, False otherwise
        """
        try:
            # Count how many indicators are present
            indicator_count = 0
            
            for indicator in self.project_indicators:
                indicator_path = path / indicator
                if indicator_path.exists():
                    indicator_count += 1
                    # If we find enough indicators, consider it a project
                    if indicator_count >= 2:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking project indicators for {path}: {e}")
            return False

    def _get_project_indicators(self, path: Path) -> List[str]:
        """
        Get list of project indicators present in a path.
        
        Args:
            path: Path to check
            
        Returns:
            List of found indicators
        """
        try:
            found_indicators = []
            
            for indicator in self.project_indicators:
                indicator_path = path / indicator
                if indicator_path.exists():
                    found_indicators.append(indicator)
            
            return found_indicators
            
        except Exception as e:
            logger.error(f"Error getting project indicators for {path}: {e}")
            return []

    def _detect_project_type(self, path: Path) -> str:
        """
        Detect the type of project.
        
        Args:
            path: Project path
            
        Returns:
            Project type string
        """
        try:
            # Check for specific project types
            if (path / "package.json").exists():
                return "nodejs"
            elif (path / "pyproject.toml").exists() or (path / "requirements.txt").exists():
                return "python"
            elif (path / "Cargo.toml").exists():
                return "rust"
            elif (path / "go.mod").exists():
                return "go"
            elif (path / "pom.xml").exists():
                return "java-maven"
            elif (path / "build.gradle").exists():
                return "java-gradle"
            elif (path / "composer.json").exists():
                return "php"
            elif (path / "Gemfile").exists():
                return "ruby"
            elif (path / "Makefile").exists():
                return "c-cpp"
            elif (path / "CMakeLists.txt").exists():
                return "cmake"
            else:
                return "generic"
                
        except Exception as e:
            logger.error(f"Error detecting project type for {path}: {e}")
            return "unknown"

    def _get_project_size(self, path: Path) -> Dict[str, Any]:
        """
        Get project size information.
        
        Args:
            path: Project path
            
        Returns:
            Dictionary with size information
        """
        try:
            total_files = 0
            total_size = 0
            
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    total_files += 1
                    try:
                        total_size += file_path.stat().st_size
                    except OSError:
                        pass
            
            return {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting project size for {path}: {e}")
            return {"total_files": 0, "total_size_bytes": 0, "total_size_mb": 0}

    def _detect_languages(self, path: Path) -> List[str]:
        """
        Detect programming languages used in the project.
        
        Args:
            path: Project path
            
        Returns:
            List of detected languages
        """
        try:
            language_extensions = {
                ".py": "Python",
                ".js": "JavaScript",
                ".ts": "TypeScript",
                ".java": "Java",
                ".cpp": "C++",
                ".c": "C",
                ".rs": "Rust",
                ".go": "Go",
                ".php": "PHP",
                ".rb": "Ruby",
                ".cs": "C#",
                ".swift": "Swift",
                ".kt": "Kotlin",
                ".scala": "Scala",
                ".clj": "Clojure",
                ".hs": "Haskell",
                ".ml": "OCaml",
                ".fs": "F#",
                ".dart": "Dart",
                ".lua": "Lua"
            }
            
            detected_languages = set()
            
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    suffix = file_path.suffix.lower()
                    if suffix in language_extensions:
                        detected_languages.add(language_extensions[suffix])
            
            return sorted(list(detected_languages))
            
        except Exception as e:
            logger.error(f"Error detecting languages for {path}: {e}")
            return []

    def _has_serena_config(self, path: Path) -> bool:
        """Check if project has Serena configuration."""
        return (path / ".serena" / "project.yml").exists()

    def _has_panda_config(self, project_path: Path) -> bool:
        """Check if project has Panda configuration."""
        panda_config = project_path / ".serena-cli" / "project.yml"
        return panda_config.exists()
