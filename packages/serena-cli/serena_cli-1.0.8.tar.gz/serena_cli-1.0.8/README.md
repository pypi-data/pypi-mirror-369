# 🚀 Serena CLI

[English](README.md) | [中文](README_CN.md)

A powerful CLI tool for quickly enabling and configuring Serena coding agent tools in specified projects.

## ✨ Features

- 🚀 **Quick Setup**: Enable Serena in any project with a single command
- 🔧 **Smart Detection**: Automatically detects project types and configurations
- 📁 **Project Management**: Manage multiple projects with ease
- ⚙️ **Flexible Configuration**: Global and project-specific settings
- 🎯 **MCP Integration**: Full MCP server support for IDE integration
- 🌍 **Multi-language Support**: Chinese and English documentation

## 🎯 Quick Start

### Check Environment Compatibility
```bash
serena-cli check-env
```

### Get Project Information
```bash
serena-cli info
```

### Check Serena Status
```bash
serena-cli status
```

### Enable Serena in Project
```bash
serena-cli enable
```

## 📦 Installation

### PyPI Installation (Simplest)
```bash
pip install serena-cli
```

### One-Click Installation

#### Unix/Linux/macOS
```bash
curl -fsSL https://raw.githubusercontent.com/impanda-cookie/serena-cli/main/install.sh | bash
```

#### Windows
```cmd
curl -fsSL https://raw.githubusercontent.com/impanda-cookie/serena-cli/main/install.bat | cmd
```

#### Python Script
```bash
curl -fsSL https://raw.githubusercontent.com/impanda-cookie/serena-cli/main/install.py | python3
```

### Manual Installation
```bash
git clone https://github.com/impanda-cookie/serena-cli.git
cd serena-cli
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## 🎮 Basic Usage

### Main Commands
- `serena-cli check-env` - Check environment compatibility
- `serena-cli info` - Get project information
- `serena-cli status` - Check Serena service status
- `serena-cli config` - Edit Serena configuration
- `serena-cli enable` - Enable Serena in projects
- `serena-cli mcp-tools` - Show available MCP tools

### MCP Integration
```bash
# Start MCP server
serena-cli start-mcp-server

# Start simplified MCP server (avoids TaskGroup issues)
serena-cli start-mcp-simple
```

## ⚙️ Configuration

### IDE Configuration

#### Cursor/VSCode
Add to your `settings.json`:
```json
{
  "mcp.servers": {
    "serena-cli": {
      "command": "serena-cli",
      "args": ["start-mcp-server"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

#### Vim/Neovim
Use with MCP plugins for seamless integration.

## 🏗️ Project Structure
```
serena-cli/
├── src/serena_cli/          # Core source code
├── tests/                   # Test suite
├── docs/                    # Documentation
├── examples/                # Usage examples
├── install.py               # Cross-platform installer
├── install.sh               # Unix/Linux/macOS installer
├── install.bat              # Windows installer
└── README.md                # This file
```

## 🚨 Troubleshooting

### Common Issues
1. **Python Version**: Serena requires Python 3.11-3.12
2. **MCP Server**: If MCP server fails, use CLI commands directly
3. **Dependencies**: Ensure all required packages are installed

### Environment Check
```bash
serena-cli check-env
```

## 📚 Documentation

- [Quick Start Guide](QUICK_START_EN.md) - 5-minute quick start
- [Usage Instructions](usage_instructions_EN.md) - Detailed usage guide
- [Project Status](PROJECT_STATUS.md) - Development overview

## 🛠️ Development

### Environment Setup
```bash
git clone https://github.com/impanda-cookie/serena-cli.git
cd serena-cli
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev,test]"
```

### Testing
```bash
pytest
pytest --cov=serena_cli
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI
- Enhanced with [Rich](https://rich.readthedocs.io/) for beautiful output
- Integrated with [MCP](https://modelcontextprotocol.io/) for IDE support

---

**Made with ❤️ by Panda**
