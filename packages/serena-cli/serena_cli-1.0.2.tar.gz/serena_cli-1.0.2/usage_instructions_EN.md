# 📚 Serena CLI Usage Instructions

[English](usage_instructions_EN.md) | [中文](usage_instructions.md)

## 🎯 Overview

Serena CLI is a powerful command-line tool for quickly enabling and configuring Serena coding agent tools. It provides complete project management and configuration functionality, supporting both MCP protocol and direct CLI commands.

## 🚀 Quick Start

### Installation

```bash
# Clone project
git clone <repository-url>
cd serena-cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .
```

### Basic Usage

```bash
# Check environment
serena-cli check-env

# View project information
serena-cli info

# View status
serena-cli status

# Edit configuration
serena-cli config

# View help
serena-cli --help
```

## 🔧 CLI Commands Detailed

### Basic Commands

#### `serena-cli --version`
Display tool version information.

#### `serena-cli --help`
Display complete help information, including all available commands.

#### `serena-cli -v, --verbose`
Enable detailed log output.

### Core Function Commands

#### `serena-cli check-env`
Check environment compatibility, including:
- Python version check
- Dependency library check
- Serena compatibility verification

**Example Output**:
```
🔍 Checking environment compatibility...
🐍 Python version: 3.13.2
✅ MCP library: Installed
✅ yaml: Installed
✅ click: Installed
✅ rich: Installed
✅ psutil: Installed

📊 Serena compatibility:
   Current version: 3.13.2
   Recommended version: 3.11-3.12
   Compatibility: ⚠️ May not be compatible
```

#### `serena-cli info [--project PATH]`
Get project information, including:
- Project path and name
- Project type and programming language
- File count and size
- Configuration status

**Example Output**:
```
                    Project Information - your-project                    
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property     ┃ Value                                                 ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Project Path │ /path/to/your/project                                │
│ Project Type │ python                                                │
│ Language     │ Python                                                │
│ File Count   │ 3274                                                  │
│ Project Size │ 42.02 MB                                              │
│ Serena Config│ ❌ Not configured                                     │
│ Panda Config │ ✅ Configured                                         │
└─────────────┴────────────────────────────────────────────────────────┘
```

#### `serena-cli status [--project PATH]`
Query Serena service status, including:
- Project path
- Serena enable status
- Configuration existence status
- Python compatibility

**Example Output**:
```
                               Serena Status - your-project                               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Project                                                ┃ Status    ┃ Config    ┃ Python Comp.   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ /path/to/your/project                                 │ ❌ Disabled│ ✅ Config │ ⚠️ May not comp.│
└────────────────────────────────────────┴───────────┴───────────┴───────────────┘
⚠️  Python version compatibility warning: Current version 3.13.2, recommended 3.11-3.12
```

#### `serena-cli config [--type TYPE] [--project PATH]`
Edit Serena configuration, supporting:
- `--type global`: Edit global configuration
- `--type project`: Edit project configuration (default)
- `--project PATH`: Specify project path

**Example Output**:
```
✅ Configuration opened for editing
   Config type: project
   Project path: /path/to/your/project
```

#### `serena-cli enable [--project PATH] [--context CONTEXT] [--force]`
Enable Serena in specified or current project, supporting:
- `--project PATH`: Specify project path
- `--context CONTEXT`: Specify Serena context (default: ide-assistant)
- `--force`: Force reinstallation

**Example Output**:
```
🔧 Enabling Serena in project /path/to/your/project...
✅ Serena enabled successfully!
   Project: /path/to/your/project
   Context: ide-assistant
```

### Advanced Function Commands

#### `serena-cli mcp-tools`
Display available MCP tools information, including:
- Tool names and descriptions
- MCP calling methods
- CLI command alternatives

**Example Output**:
```
🔧 Available MCP tools:
                             MCP Tools List                             
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Tool Name   ┃ Description                                            ┃ Usage Method            ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ serena_enable │ Enable Serena in specified or current project       │ @mcp serena_enable      │
│ serena_status │ Query Serena service status                          │ @mcp serena_status      │
│ edit_config   │ Edit Serena configuration                            │ @mcp edit_config        │
└────────────────────┴────────────────────────────────────────────────────┴─────────────────────────┘

💡 If MCP server is unavailable, you can use the following CLI commands:
  serena-cli enable     # Enable Serena
  serena-cli status     # Query status
  serena-cli config     # Edit configuration
  serena-cli info       # Project information
```

#### `serena-cli start-mcp-server`
Start MCP server (Note: Current version may have compatibility issues).

#### `serena-cli start-mcp-simple`
Start simplified MCP server, avoiding TaskGroup issues.

## 🎮 MCP Tools Usage

### In Cursor

```python
# Enable Serena
@mcp serena_enable

# Query status
@mcp serena_status

# Edit configuration
@mcp edit_config
```

### In VSCode

```python
# Enable Serena
@mcp serena_enable

# Query status
@mcp serena_status

# Edit configuration
@mcp edit_config
```

## ⚙️ Configuration Management

### Global Configuration

Global configuration file location: `~/.serena-cli/config.yml`

**Default Configuration**:
```yaml
default_context: "ide-assistant"
install_method: "uv"
log_level: "INFO"
auto_start: true
port: 24282
dashboard:
  enabled: true
  port: 24282
  auto_open: true
logging:
  level: "INFO"
  file: "~/.serena-cli/logs/serena-cli.log"
  max_size: "10MB"
  backup_count: 5
serena:
  default_context: "ide-assistant"
  auto_install: true
  preferred_installer: "uv"
```

### Project Configuration

Project configuration file location: `.serena-cli/project.yml`

**Default Configuration**:
```yaml
project_name: "your-project"
serena_context: "ide-assistant"
read_only: false
auto_start: true
included_tools:
  - find_symbol
  - read_file
  - execute_shell_command
  - list_dir
  - get_symbols_overview
  - search_for_pattern
excluded_tools: []
project_settings:
  memory_enabled: true
  language_servers: []
  custom_prompts: []
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Command Not Found
```bash
# Check installation
pip list | grep serena-cli

# Reinstall
pip install -e .

# Check virtual environment
source venv/bin/activate
```

#### 2. Python Version Incompatibility
```bash
# Check version
python --version

# Run compatibility check
serena-cli check-env

# Consider downgrading Python version
pyenv install 3.11.0
pyenv local 3.11.0
```

#### 3. MCP Server Startup Failure
```bash
# Use simplified startup
serena-cli start-mcp-simple

# Use CLI commands directly
serena-cli enable
serena-cli status
serena-cli config
```

#### 4. Configuration Edit Failure
```bash
# Check editor settings
echo $EDITOR

# Manually edit configuration files
ls -la .serena-cli/
cat .serena-cli/project.yml
```

### Logging and Debugging

```bash
# Enable detailed logging
serena-cli -v check-env

# View log files
tail -f ~/.serena-cli/logs/serena-cli.log
```

## 📚 Advanced Usage

### Batch Project Management

```bash
#!/bin/bash
# Batch check multiple projects

projects=(
    "/path/to/project1"
    "/path/to/project2"
    "/path/to/project3"
)

for project in "${projects[@]}"; do
    echo "=== Checking project: $project ==="
    cd "$project"
    serena-cli status
    echo ""
done
```

### Automated Configuration

```bash
# Create project configuration template
mkdir -p .serena-cli
cat > .serena-cli/project.yml << EOF
project_name: "my-project"
serena_context: "ide-assistant"
read_only: false
included_tools:
  - find_symbol
  - read_file
  - execute_shell_command
EOF
```

### CI/CD Integration

```yaml
# .github/workflows/serena-check.yml
name: Serena Status Check
on: [push, pull_request]
jobs:
  check-serena:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.11'
      - name: Install Serena CLI
        run: |
          pip install -e .
      - name: Check Serena Status
        run: |
          serena-cli check-env
          serena-cli status
```

## 🎯 Best Practices

### 1. Project Initialization
```bash
# Enter new project
cd /path/to/new-project

# Check environment
serena-cli check-env

# View project information
serena-cli info

# Configure project
serena-cli config
```

### 2. Daily Maintenance
```bash
# Regularly check status
serena-cli status

# Monitor environment changes
serena-cli check-env

# Update configuration
serena-cli config
```

### 3. Team Collaboration
```bash
# Share configuration templates
cp .serena-cli/project.yml template.yml

# Batch apply configuration
for project in */; do
    cd "$project"
    cp ../template.yml .serena-cli/project.yml
    cd ..
done
```

## 🚀 Extension and Customization

### Custom Tool Configuration

```yaml
# .serena-cli/project.yml
included_tools:
  - find_symbol
  - read_file
  - execute_shell_command
  - custom_tool_1
  - custom_tool_2

excluded_tools:
  - unwanted_tool

project_settings:
  custom_prompts:
    - "You are a professional Python developer"
    - "Please follow PEP 8 code standards"
  language_servers:
    - "python-lsp-server"
    - "typescript-language-server"
```

### Environment Variable Configuration

```bash
# Set default editor
export EDITOR="code"

# Set log level
export SERENA_LOG_LEVEL="DEBUG"

# Set configuration directory
export SERENA_CONFIG_DIR="/custom/config/path"
```

## 📞 Support and Feedback

### Getting Help
```bash
# View help
serena-cli --help

# View specific command help
serena-cli enable --help
```

### Reporting Issues
- Check log files: `~/.serena-cli/logs/serena-cli.log`
- Run diagnostic commands: `serena-cli check-env`
- Provide error information and environment details

### Contributing Code
- Fork project repository
- Create feature branch
- Submit Pull Request

---

**Serena CLI** - Making Serena management simple and efficient! 🚀
