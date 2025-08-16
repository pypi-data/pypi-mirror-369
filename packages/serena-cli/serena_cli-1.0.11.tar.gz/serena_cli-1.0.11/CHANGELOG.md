# Changelog

All notable changes to this project will be documented in this file.

## [1.0.11] - 2025-01-XX

### ✨ 新功能
- **智能 MCP 服务器启动向导**: 全新的交互式启动向导，自动检测和配置目标平台
- **智能依赖管理**: 自动检测并安装缺失的 uv、uvx、pip 等工具
- **多平台自动配置**: 支持 Claude Desktop、Cursor IDE、VSCode 和传统 MCP 服务器
- **一键完成配置**: 用户只需选择目标平台，自动完成所有配置步骤
- **自动启动 Serena Web 服务器**: 启动 MCP 服务器时自动启动 Serena Web 服务器
- **自动打开 Web Dashboard**: 自动在浏览器中打开 http://127.0.0.1:24282/dashboard/index.html
- **完整 Serena 体验**: 提供 25+ 语义代码编辑和分析工具
- **优雅关闭**: 按 Ctrl+C 时同时关闭 MCP 服务器和 Serena Web 服务器

### 🔧 技术改进
- **环境检查**: 自动检查 Python 版本、虚拟环境状态
- **依赖检查**: 智能检测缺失工具并提供多种安装方案
- **平台检测**: 自动检测可用的 AI 编程工作台
- **配置验证**: 验证配置是否成功并提供使用指导

### 📚 文档更新
- **中英文使用说明**: 更新了 `start-mcp-server` 命令的详细说明
- **快速开始指南**: 添加了 MCP 服务器启动和 Web 界面使用说明
- **功能特性说明**: 详细描述了新功能的特性和使用方法
- **智能向导说明**: 新增智能启动向导的详细使用说明

## [1.0.10] - 2025-01-XX

### ✨ 新功能
- **智能 MCP 服务器启动向导**: 全新的交互式启动向导，自动检测和配置目标平台
- **智能依赖管理**: 自动检测并安装缺失的 uv、uvx、pip 等工具
- **多平台自动配置**: 支持 Claude Desktop、Cursor IDE、VSCode 和传统 MCP 服务器
- **一键完成配置**: 用户只需选择目标平台，自动完成所有配置步骤
- **自动启动 Serena Web 服务器**: 启动 MCP 服务器时自动启动 Serena Web 服务器
- **自动打开 Web Dashboard**: 自动在浏览器中打开 http://127.0.0.1:24282/dashboard/index.html
- **完整 Serena 体验**: 提供 25+ 语义代码编辑和分析工具
- **优雅关闭**: 按 Ctrl+C 时同时关闭 MCP 服务器和 Serena Web 服务器

### 🔧 技术改进
- **环境检查**: 自动检查 Python 版本、虚拟环境状态
- **依赖检查**: 智能检测缺失工具并提供多种安装方案
- **平台检测**: 自动检测可用的 AI 编程工作台
- **配置验证**: 验证配置是否成功并提供使用指导

### 📚 文档更新
- **中英文使用说明**: 更新了 `start-mcp-server` 命令的详细说明
- **快速开始指南**: 添加了 MCP 服务器启动和 Web 界面使用说明
- **功能特性说明**: 详细描述了新功能的特性和使用方法
- **智能向导说明**: 新增智能启动向导的详细使用说明

## [1.0.9] - 2025-01-XX

### Added
- **Comprehensive MCP Server Verification**: Added built-in verification during MCP server startup
- **MCP Tools Validation**: Verify that all MCP tools are available and functional
- **Basic Functionality Testing**: Test project detection and Serena manager during startup
- **Enhanced User Experience**: Clear success confirmation and usage guidance
- **Automatic Serena Web Server**: Automatically start Serena Web server when starting MCP server
- **Web Dashboard Auto-Open**: Automatically open http://127.0.0.1:24282/dashboard/index.html in browser
- **Complete Serena Experience**: Provide 25+ semantic code editing and analysis tools

### Fixed
- **TaskGroup Error Handling**: Gracefully suppress TaskGroup error messages to console
- **MCP Server Startup Verification**: Ensure MCP server is truly running with process verification
- **User-Friendly Error Messages**: Replace technical errors with helpful guidance
- **Graceful Shutdown**: Properly close both MCP server and Serena Web server on Ctrl+C

### Changed
- **Startup Process**: Enhanced startup process with comprehensive verification steps
- **Error Suppression**: TaskGroup errors are now handled silently without user confusion
- **Verification Flow**: Added multiple verification steps to prove Serena is working

## [1.0.8] - 2025-01-XX

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Author**: Panda

## [1.0.8] - 2025-01-27

### Fixed
- **Serena Enabled Status**: Fixed `_is_serena_enabled` method to correctly check for `.serena-cli/project.yml`
- **Project Configuration Path**: Ensured `serena-cli status` accurately reflects Serena's enabled status based on the correct config file path
- **Old Naming References**: Updated all remaining references from `panda-index-helper` to `serena-cli` in MCP server output
- **Configuration Paths**: Fixed all configuration paths to use `.serena-cli` instead of `.panda-index-helper`

### Added
- **Force Enable Option**: Added `--force` option to `serena-cli enable` command to bypass Python version compatibility checks
- **Enhanced Status Display**: Added Serena configuration directory path to status output for better visibility

### Changed
- **CLI Enable Behavior**: Modified `enable` command to provide a hint to use `--force` when compatibility check fails
- **Python Version Support**: Extended Python compatibility from 3.10-3.12 to 3.10+ (only Python 3.13+ may have issues)
- **MCP Server Output**: Updated all command references in MCP server error messages to use `serena-cli`

### Technical Improvements
- **Configuration Consistency**: Aligned Serena enabled check with the actual configuration file path
- **User Control**: Provided an explicit option for users to override compatibility checks
- **Better User Experience**: More informative status output with configuration directory information

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

## [1.0.5] - 2025-01-27

### Fixed
- **Python Version References**: Updated all remaining Python version references from 3.11-3.12 to 3.10-3.12
- **Compatibility Logic**: Fixed `_check_python_compatibility` method to include Python 3.10 support
- **Template Files**: Updated configuration templates to show correct Python version recommendations

### Changed
- **Python Support Range**: Extended Python compatibility check to include Python 3.10, 3.11, and 3.12
- **Error Messages**: All error messages now consistently show Python 3.10-3.12 as recommended range

### Technical Improvements
- **Consistent Versioning**: All Python version references now consistently show 3.10-3.12
- **Better User Experience**: Users with Python 3.10 will no longer see incorrect compatibility warnings

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
