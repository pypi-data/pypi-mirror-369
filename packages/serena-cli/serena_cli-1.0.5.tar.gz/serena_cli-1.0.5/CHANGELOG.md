# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Author**: Panda

## [Unreleased]

### Added
- Initial project setup
- Core CLI functionality
- MCP server support
- Project detection and management
- Configuration management
- Comprehensive documentation in Chinese and English
- One-click installation scripts for multiple platforms

### Changed
- Project renamed from "panda-index-helper" to "serena-cli"
- Improved error handling and user feedback
- Enhanced compatibility checks

### Fixed
- TaskGroup compatibility issues with Python 3.13
- Python version compatibility warnings
- Configuration path issues

## [1.0.4] - 2025-01-27

### Fixed
- **Missing Method**: Added missing `enable_serena` method to `SerenaManager` class
- **Python Compatibility**: Extended Python version support to include Python 3.10-3.12
- **Project Validation**: Added `_is_valid_project` method for better project detection

### Changed
- **Python Version Range**: Updated recommended Python version from 3.11-3.12 to 3.10-3.12
- **Quick Solutions**: Updated installation guides to include Python 3.10 options

### Added
- **Synchronous Enable Method**: Added `enable_serena` method for CLI usage
- **Project Validation**: Added project validation logic to ensure valid project paths
- **Better Error Handling**: Improved error messages for project validation and Python compatibility

### Technical Improvements
- **Method Consistency**: Ensured all CLI commands have corresponding methods in `SerenaManager`
- **Python Support**: Extended compatibility to cover Python 3.10, 3.11, and 3.12
- **Code Structure**: Better organization of project validation and Serena enabling logic

## [1.0.3] - 2025-01-27

### Changed
- **CLI Output Language**: Changed CLI commands output from Chinese to English priority
- **Project Name Display**: Updated project information display to use English terminology
- **Python Compatibility**: Enhanced Python version compatibility warnings with actionable quick solutions

### Added
- **Quick Solutions**: Added practical solutions for Python compatibility issues:
  - pyenv installation guide for Python 3.11-3.12
  - conda environment creation
  - Docker container usage
  - Continue with current version option
- **Synchronous Status Method**: Added `get_status_sync` method to avoid async/await issues in CLI

### Fixed
- **CLI Entry Point**: Fixed CLI entry point configuration in pyproject.toml
- **MCP Tools Display**: Added missing `get_tools` method to MCP server class
- **Project Config Paths**: Updated configuration paths from `.panda-index-helper` to `.serena-cli`
- **Status Command**: Fixed status command to work properly without async/await errors

### Technical Improvements
- **Error Handling**: Improved error handling and user feedback for compatibility issues
- **Code Structure**: Better separation between async and sync methods
- **User Experience**: More informative and actionable error messages

## [1.0.2] - 2025-01-27

### Changed
- Updated GitHub repository URLs to use correct repository: impanda-cookie/serena-cli
- Fixed all documentation links to point to the correct GitHub repository
- Enhanced installation instructions with correct repository URLs

### Fixed
- Corrected GitHub repository references in all documentation files
- Updated installation scripts and manual installation instructions

## [1.0.1] - 2025-01-27

### Changed
- Updated author information from "Your Name" to "Panda"
- Added bilingual navigation links between Chinese and English documentation
- Set English as default language for documentation
- Enhanced cross-language document linking

### Fixed
- Improved documentation consistency across languages
- Better user experience for international users

## [1.0.0] - 2025-01-27

### Added
- **Core Features**
  - `serena-cli check-env` - Environment compatibility check
  - `serena-cli info` - Project information display
  - `serena-cli status` - Serena service status query
  - `serena-cli config` - Configuration management
  - `serena-cli enable` - Enable Serena in projects
  - `serena-cli mcp-tools` - MCP tools information

- **MCP Integration**
  - `serena_enable` tool for enabling Serena via MCP
  - `serena_status` tool for status queries via MCP
  - `edit_config` tool for configuration editing via MCP

- **Project Management**
  - Intelligent project detection
  - Multi-language project support
  - Automatic configuration generation
  - Global and project-level settings

- **Installation & Deployment**
  - Cross-platform installation scripts
  - Virtual environment management
  - Dependency auto-installation
  - PyPI package distribution support

- **Documentation**
  - Comprehensive README in Chinese and English
  - Quick start guides for both languages
  - Detailed usage instructions
  - Troubleshooting guides
  - API documentation

### Technical Details
- **Python Support**: 3.8+
- **Dependencies**: mcp, pyyaml, click, rich, psutil
- **Architecture**: Modular design with clear separation of concerns
- **Testing**: Comprehensive test suite with pytest
- **Code Quality**: Black, isort, flake8, mypy integration
- **CI/CD**: GitHub Actions ready

### Known Issues
- MCP server has compatibility issues with Python 3.13.2
- Serena requires Python 3.11-3.12 for full functionality
- CLI functions work normally despite MCP server issues

---

## Version History

- **1.0.0** - Initial release with full CLI functionality
- **Unreleased** - Development version with latest features

## Release Notes

### Version 1.0.0
This is the initial release of Serena CLI, providing a complete solution for managing Serena coding agent tools. While the MCP server has some compatibility limitations, all CLI functions work perfectly and provide immediate value to users.

**Key Benefits:**
- 🚀 One-command Serena management
- 🔍 Intelligent project detection
- ⚙️ Flexible configuration management
- 📚 Comprehensive documentation
- 🌍 Bilingual support (Chinese/English)
- 🖥️ Cross-platform compatibility

**Getting Started:**
```bash
# Install from PyPI
pip install serena-cli

# Or use one-click installation
git clone <repository>
cd serena-cli
./install.sh  # Unix/Linux/macOS
# or
install.bat   # Windows
# or
python install.py  # Cross-platform
```

**Quick Usage:**
```bash
serena-cli check-env    # Check environment
serena-cli info         # Get project info
serena-cli status       # Check Serena status
serena-cli config       # Edit configuration
serena-cli enable       # Enable Serena
```
