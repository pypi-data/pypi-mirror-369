# 📚 Serena CLI 使用说明

[English](usage_instructions_EN.md) | [中文](usage_instructions.md)

## 🎯 概述

Serena CLI 是一个强大的命令行工具，用于快速启用和配置 Serena 编码代理工具。它提供了完整的项目管理和配置功能，支持 MCP 协议和直接的 CLI 命令。

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd serena-cli

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -e .
```

### 基本使用

```bash
# 检查环境
serena-cli check-env

# 查看项目信息
serena-cli info

# 查看状态
serena-cli status

# 编辑配置
serena-cli config

# 查看帮助
serena-cli --help
```

## 🔧 CLI 命令详解

### 基础命令

#### `serena-cli --version`
显示工具版本信息。

#### `serena-cli --help`
显示完整的帮助信息，包括所有可用命令。

#### `serena-cli -v, --verbose`
启用详细日志输出。

### 核心功能命令

#### `serena-cli check-env`
检查环境兼容性，包括：
- Python 版本检查
- 依赖库检查
- Serena 兼容性验证

**示例输出**：
```
🔍 检查环境兼容性...
🐍 Python 版本: 3.13.2
✅ MCP 库: 已安装
✅ yaml: 已安装
✅ click: 已安装
✅ rich: 已安装
✅ psutil: 已安装

📊 Serena 兼容性:
   当前版本: 3.13.2
   推荐版本: 3.11-3.12
   兼容性: ⚠️ 可能不兼容
```

#### `serena-cli info [--project PATH]`
获取项目信息，包括：
- 项目路径和名称
- 项目类型和编程语言
- 文件数量和大小
- 配置状态

**示例输出**：
```
                   项目信息 - your-project                    
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 属性        ┃ 值                                                     ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 项目路径    │ /path/to/your/project                                 │
│ 项目类型    │ python                                                 │
│ 编程语言    │ Python                                                 │
│ 文件数量    │ 3274                                                   │
│ 项目大小    │ 42.02 MB                                               │
│ Serena 配置 │ ❌ 未配置                                              │
│ Panda 配置  │ ✅ 已配置                                              │
└─────────────┴────────────────────────────────────────────────────────┘
```

#### `serena-cli status [--project PATH]`
查询 Serena 服务状态，包括：
- 项目路径
- Serena 启用状态
- 配置存在状态
- Python 兼容性

**示例输出**：
```
                               Serena 状态 - your-project                               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ 项目                                                   ┃ 状态      ┃ 配置      ┃ Python 兼容性 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ /path/to/your/project                                 │ ❌ 未启用 │ ✅ 已配置 │ ⚠️ 可能不兼容  │
└────────────────────────────────────────┴───────────┴───────────┴───────────────┘
⚠️  Python 版本兼容性警告: 当前版本 3.13.2，推荐 3.11-3.12
```

#### `serena-cli config [--type TYPE] [--project PATH]`
编辑 Serena 配置，支持：
- `--type global`: 编辑全局配置
- `--type project`: 编辑项目配置（默认）
- `--project PATH`: 指定项目路径

**示例输出**：
```
✅ 配置已打开进行编辑
   配置类型: project
   项目路径: /path/to/your/project
```

#### `serena-cli enable [--project PATH] [--context CONTEXT] [--force]`
在指定或当前项目中启用 Serena，支持：
- `--project PATH`: 指定项目路径
- `--context CONTEXT`: 指定 Serena 上下文（默认：ide-assistant）
- `--force`: 强制重新安装

**示例输出**：
```
🔧 在项目 /path/to/your/project 中启用 Serena...
✅ Serena 启用成功！
   项目: /path/to/your/project
   上下文: ide-assistant
```

### 高级功能命令

#### `serena-cli mcp-tools`
显示可用的 MCP 工具信息，包括：
- 工具名称和描述
- MCP 调用方法
- CLI 命令替代方案

**示例输出**：
```
🔧 可用的 MCP 工具:
                             MCP 工具列表                             
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 工具名称    ┃ 描述                                               ┃ 使用方法                ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ serena_enable │ 在指定或当前项目中启用 Serena                     │ @mcp serena_enable      │
│ serena_status │ 查询 Serena 服务状态                               │ @mcp serena_status      │
│ edit_config   │ 编辑 Serena 配置                                   │ @mcp edit_config        │
└────────────────────┴────────────────────────────────────────────────────┴─────────────────────────┘

💡 如果 MCP 服务器不可用，你可以使用以下 CLI 命令:
  serena-cli enable     # 启用 Serena
  serena-cli status     # 查询状态
  serena-cli config     # 编辑配置
  serena-cli info       # 项目信息
```

#### `serena-cli start-mcp-server`
启动智能 MCP 服务器向导，自动检测环境、安装依赖、配置目标平台，提供完整的用户体验。

**🚀 智能向导功能：**
- ✅ **环境检查**: 自动检查 Python 版本和虚拟环境
- ✅ **依赖管理**: 智能检测并安装缺失的 uv、uvx、pip 等工具
- ✅ **平台选择**: 支持 Claude Desktop、Cursor IDE、VSCode、传统 MCP 服务器
- ✅ **自动配置**: 根据选择自动配置相应平台的 MCP 设置
- ✅ **配置验证**: 验证配置是否成功并提供使用指导
- ✅ **Web 服务器**: 自动启动 Serena Web 服务器并打开 Dashboard

**🎯 支持的平台：**
1. **Claude Desktop** ⭐ - 官方 Serena 集成 (推荐)
2. **Cursor IDE** 💡 - MCP 协议集成
3. **VSCode** 💡 - MCP 协议集成  
4. **传统 MCP 服务器** 💡 - 标准 MCP 协议

**示例输出：**
```
🚀 Serena CLI 智能 MCP 服务器启动向导
==================================================
🔍 第一步：环境检查...
✅ Python 版本: 3.13.2
✅ 虚拟环境已激活

🔍 第二步：依赖检查...
✅ uv 已安装
✅ uvx 已安装
✅ pip 已安装
✅ 所有依赖检查通过！

🔍 第三步：选择目标平台...
请选择目标 AI 编程工作台:
1. ✅ Claude - 官方 Serena 集成 (推荐) ⭐
2. ✅ Cursor - MCP 协议集成 💡
3. ✅ Vscode - MCP 协议集成 💡
4. ✅ Traditional - 标准 MCP 协议 💡

请输入选择 (1-4): 1
✅ 已选择: Claude

🔧 第四步：配置 Claude...
🤖 配置 Claude Desktop...
✅ 成功添加到 Claude MCP!
   Context: ide-assistant
   Project: /Users/panda/Code/toy/AI/mylibs/panda-index-helper-mcp
🔄 请重启 Claude 以使用新工具

🔍 第五步：验证 Claude 配置...
✅ Claude MCP 配置验证通过!

📚 第六步：Claude 使用指导
==================================================
🤖 Claude Desktop 使用说明:
1. 重启 Claude Desktop
2. 在对话中使用: @mcp serena
3. 享受 18 个 Serena 工具!

🎉 配置完成！现在你可以开始使用 Serena 了!
💡 如有问题，请查看文档或联系技术支持
```

#### `serena-cli start-mcp-simple`
启动简化的 MCP 服务器，避免 TaskGroup 问题（已弃用，推荐使用 `start-mcp-server`）。

## 🎮 MCP 工具使用

### 在 Cursor 中使用

```python
# 启用 Serena
@mcp serena_enable

# 查询状态
@mcp serena_status

# 编辑配置
@mcp edit_config
```

### 在 VSCode 中使用

```python
# 启用 Serena
@mcp serena_enable

# 查询状态
@mcp serena_status

# 编辑配置
@mcp edit_config
```

## ⚙️ 配置管理

### 全局配置

全局配置文件位置：`~/.serena-cli/config.yml`

**默认配置**：
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

### 项目配置

项目配置文件位置：`.serena-cli/project.yml`

**默认配置**：
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

## 🔍 故障排除

### 常见问题

#### 1. 命令未找到
```bash
# 检查安装
pip list | grep serena-cli

# 重新安装
pip install -e .

# 检查虚拟环境
source venv/bin/activate
```

#### 2. Python 版本不兼容
```bash
# 检查版本
python --version

# 运行兼容性检查
serena-cli check-env

# 考虑降级 Python 版本
pyenv install 3.11.0
pyenv local 3.11.0
```

#### 3. MCP 服务器启动失败
```bash
# 使用简化启动
serena-cli start-mcp-simple

# 直接使用 CLI 命令
serena-cli enable
serena-cli status
serena-cli config
```

#### 4. 配置编辑失败
```bash
# 检查编辑器设置
echo $EDITOR

# 手动编辑配置文件
ls -la .serena-cli/
cat .serena-cli/project.yml
```

### 日志和调试

```bash
# 启用详细日志
serena-cli -v check-env

# 查看日志文件
tail -f ~/.serena-cli/logs/serena-cli.log
```

## 📚 高级用法

### 批量项目管理

```bash
#!/bin/bash
# 批量检查多个项目

projects=(
    "/path/to/project1"
    "/path/to/project2"
    "/path/to/project3"
)

for project in "${projects[@]}"; do
    echo "=== 检查项目: $project ==="
    cd "$project"
    serena-cli status
    echo ""
done
```

### 自动化配置

```bash
# 创建项目配置模板
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

### 集成到 CI/CD

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

## 🎯 最佳实践

### 1. 项目初始化
```bash
# 进入新项目
cd /path/to/new-project

# 检查环境
serena-cli check-env

# 查看项目信息
serena-cli info

# 配置项目
serena-cli config
```

### 2. 日常维护
```bash
# 定期检查状态
serena-cli status

# 监控环境变化
serena-cli check-env

# 更新配置
serena-cli config
```

### 3. 团队协作
```bash
# 共享配置模板
cp .serena-cli/project.yml template.yml

# 批量应用配置
for project in */; do
    cd "$project"
    cp ../template.yml .serena-cli/project.yml
    cd ..
done
```

## 🚀 扩展和定制

### 自定义工具配置

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
    - "你是一个专业的 Python 开发者"
    - "请遵循 PEP 8 代码规范"
  language_servers:
    - "python-lsp-server"
    - "typescript-language-server"
```

### 环境变量配置

```bash
# 设置默认编辑器
export EDITOR="code"

# 设置日志级别
export SERENA_LOG_LEVEL="DEBUG"

# 设置配置目录
export SERENA_CONFIG_DIR="/custom/config/path"
```

## 📞 支持和反馈

### 获取帮助
```bash
# 查看帮助
serena-cli --help

# 查看特定命令帮助
serena-cli enable --help
```

### 报告问题
- 检查日志文件：`~/.serena-cli/logs/serena-cli.log`
- 运行诊断命令：`serena-cli check-env`
- 提供错误信息和环境详情

### 贡献代码
- Fork 项目仓库
- 创建功能分支
- 提交 Pull Request

---

**Serena CLI** - 让 Serena 管理变得简单高效！ 🚀
