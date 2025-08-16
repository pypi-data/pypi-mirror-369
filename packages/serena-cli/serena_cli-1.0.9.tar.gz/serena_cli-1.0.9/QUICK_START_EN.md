# 🚀 Serena CLI Quick Start Guide

[English](QUICK_START_EN.md) | [中文](QUICK_START.md)

### Installation

```bash
# Clone the repository
git clone https://github.com/impanda-cookie/serena-cli.git
cd serena-cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## ⚡ 5-Minute Quick Start

### Step 1: Check Environment
```bash
# Activate virtual environment (if using)
source venv/bin/activate

# Check environment compatibility
serena-cli check-env
```

**Expected Output**:
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

### Step 2: Understand Current Project
```bash
# Get project information
serena-cli info
```

**Expected Output**:
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

### Step 3: Check Project Status
```bash
# Query Serena status
serena-cli status
```

**Expected Output**:
```
                               Serena Status - your-project                               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Project                                                ┃ Status    ┃ Config    ┃ Python Comp.   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ /path/to/your/project                                 │ ❌ Disabled│ ✅ Config │ ⚠️ May not comp.│
└────────────────────────────────────────┴───────────┴───────────┴───────────────┘
⚠️  Python version compatibility warning: Current version 3.13.2, recommended 3.11-3.12
```

### Step 4: Manage Configuration
```bash
# Edit project configuration
serena-cli config

# Edit global configuration
serena-cli config --type global
```

**Expected Output**:
```
✅ Configuration opened for editing
   Config type: project
   Project path: /path/to/your/project
```

### Step 5: View Available Tools
```bash
# Show MCP tools information
serena-cli mcp-tools
```

**Expected Output**:
```
🔧 Available MCP tools:
                                            MCP Tools List                                             
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Tool Name          ┃ Description                                        ┃ Usage Method            ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ serena_enable      │ Enable Serena in specified or current project     │ @mcp serena_enable      │
│ serena_status      │ Query Serena service status                       │ @mcp serena_status      │
│ edit_config        │ Edit Serena configuration                         │ @mcp edit_config        │
└────────────────────┴────────────────────────────────────────────────────┴─────────────────────────┘
```

## 🎯 Real-World Usage Scenarios

### Scenario 1: New Project Initialization
```bash
# Enter new project directory
cd /path/to/new-project

# Check project
serena-cli info

# Try to enable Serena (Note: Python 3.13 will fail)
serena-cli enable

# View detailed status
serena-cli status
```

### Scenario 2: Existing Project Management
```bash
# Enter existing project
cd /path/to/existing-project

# View current status
serena-cli status

# Edit project configuration
serena-cli config

# View project information
serena-cli info
```

### Scenario 3: Multi-Project Batch Check
```bash
# Project 1
cd /path/to/project1
serena-cli status

# Project 2  
cd /path/to/project2
serena-cli status

# Project 3
cd /path/to/project3
serena-cli status
```

## 🔧 Troubleshooting

### Problem 1: Command Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Check installation
pip list | grep serena-cli

# Reinstall
pip install -e .
```

### Problem 2: Python Version Incompatibility
```bash
# Check Python version
python --version

# Run compatibility check
serena-cli check-env

# Consider using Python 3.11 or 3.12
pyenv install 3.11.0
pyenv local 3.11.0
```

### Problem 3: Configuration Edit Failure
```bash
# Check editor settings
echo $EDITOR

# Manually edit configuration files
ls -la .serena-cli/
cat .serena-cli/project.yml
```

## 📚 Advanced Usage

### Batch Operations Script
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

## 🎉 Success Indicators

When you see the following output, Serena CLI is working correctly:

✅ **Environment check passed**: All dependency libraries are normal  
✅ **Project detection successful**: Automatically identifies project type and structure  
✅ **Status query normal**: Displays detailed project status information  
✅ **Configuration management available**: Can edit and view configuration files  
✅ **Error handling complete**: Provides clear error information and solution suggestions  

## 🚀 Next Steps

1. **Familiarize with basic commands**: `info`, `status`, `config`
2. **Understand project structure**: View generated configuration files
3. **Monitor project status**: Regularly run `status` command
4. **Customize configuration**: Adjust settings according to project needs

---

**Remember**: Although the MCP server has compatibility issues, all CLI functions work normally and you can start using them immediately!

**Need help?** Run `serena-cli --help` to see all available commands.
