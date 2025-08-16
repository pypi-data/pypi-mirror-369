# Panda Index Helper 使用说明

## 🚀 快速开始

### 1. 安装

```bash
pip install serena-cli
```

### 2. 配置 MCP 客户端

#### Cursor
编辑 `~/.cursor/mcp.json`：
```json
{
  "mcpServers": {
    "serena-cli": {
      "command": "serena-cli",
      "args": ["start-mcp-server"]
    }
  }
}
```

#### VSCode
在设置中添加：
```json
{
  "mcp.servers": {
    "serena-cli": {
      "command": "serena-cli",
      "args": ["start-mcp-server"]
    }
  }
}
```

### 3. 重启 IDE
重启你的 IDE 以加载新的 MCP 配置。

### 4. 使用
在项目中使用 `@mcp serena-cli` 来启用 Serena。

## 🎯 核心功能

### 启用 Serena
```
@mcp serena-cli
```

### 查询状态
```
@mcp serena-cli --status
```

### 编辑配置
```
@mcp serena-cli --config
```

## 🔧 命令行工具

### 启用 Serena
```bash
# 在当前项目中启用
serena-cli enable

# 在指定项目中启用
serena-cli enable --project /path/to/project

# 强制重新安装
serena-cli enable --force

# 指定上下文
serena-cli enable --context ide-assistant
```

### 查询状态
```bash
# 查询当前项目状态
serena-cli status

# 查询指定项目状态
serena-cli status --project /path/to/project
```

### 编辑配置
```bash
# 编辑项目配置
serena-cli config

# 编辑全局配置
serena-cli config --type global

# 编辑指定项目配置
serena-cli config --project /path/to/project
```

### 获取项目信息
```bash
# 获取当前项目信息
serena-cli info

# 获取指定项目信息
serena-cli info --project /path/to/project
```

### 启动 MCP 服务器
```bash
serena-cli start-mcp-server
```

## ⚙️ 配置选项

### 全局配置
位置：`~/.serena-cli/config.yml`

```yaml
# 默认 Serena 上下文
default_context: "ide-assistant"

# 默认安装方式
install_method: "uv"  # 可选: "uv", "pip"

# 日志级别
log_level: "INFO"

# 自动启动服务
auto_start: true

# 端口配置
port: 24282

# 仪表板配置
dashboard:
  enabled: true
  port: 24282
  auto_open: true

# 日志配置
logging:
  level: "INFO"
  file: "~/.serena-cli/logs/serena-cli.log"
  max_size: "10MB"
  backup_count: 5

# Serena 配置
serena:
  default_context: "ide-assistant"
  auto_install: true
  preferred_installer: "uv"
```

### 项目配置
位置：`.serena-cli/project.yml`

```yaml
project_name: "my-project"
serena_context: "ide-assistant"
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
```

## 🔍 故障排除

### 常见问题

#### 1. Python 版本不兼容
**问题**：Serena 要求 Python 3.11-3.12，但当前版本是 3.13
**解决方案**：
- 使用 Python 3.11 或 3.12 创建虚拟环境
- 或者等待 Serena 更新支持 Python 3.13

#### 2. 安装失败
**问题**：无法安装 Serena
**解决方案**：
- 检查网络连接
- 尝试使用 `--force` 参数
- 检查 Python 版本兼容性

#### 3. MCP 服务器启动失败
**问题**：MCP 服务器无法启动
**解决方案**：
- 检查端口是否被占用
- 查看日志文件
- 重启 IDE 客户端

#### 4. 项目检测失败
**问题**：无法检测到项目结构
**解决方案**：
- 确保在正确的项目目录中
- 检查项目是否包含必要的文件
- 手动指定项目路径

### 日志查看

```bash
# 查看最新日志
tail -f ~/.serena-cli/logs/latest.log

# 查看错误日志
grep "ERROR" ~/.serena-cli/logs/latest.log

# 查看调试日志
grep "DEBUG" ~/.serena-cli/logs/latest.log
```

### 调试模式

```bash
# 启用详细日志
serena-cli --verbose enable

# 查看详细输出
serena-cli --verbose status
```

## 🚀 高级用法

### 批量操作
```bash
# 批量启用多个项目
for project in /path/to/projects/*; do
  serena-cli enable --project "$project"
done
```

### 自动化脚本
```bash
#!/bin/bash
# 自动启用所有 Python 项目

find /path/to/projects -name "pyproject.toml" -type f | while read -r file; do
  project_dir=$(dirname "$file")
  echo "启用项目: $project_dir"
  serena-cli enable --project "$project_dir"
done
```

### CI/CD 集成
```yaml
# GitHub Actions 示例
name: Enable Serena
on: [push, pull_request]
jobs:
  enable-serena:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Serena CLI
        run: pip install serena-cli
      - name: Enable Serena
        run: serena-cli enable --force
```

## 📚 更多资源

- [Serena 官方文档](https://github.com/oraios/serena)
- [MCP 协议文档](https://modelcontextprotocol.io/)
- [Cursor 文档](https://cursor.sh/docs)
- [问题反馈](https://github.com/impanda-cookie/serena-cli/issues)

## 🤝 获取帮助

如果你遇到问题或需要帮助：

1. 查看本文档的故障排除部分
2. 检查日志文件获取详细错误信息
3. 在 GitHub 上提交 issue
4. 查看常见问题解答

---

**版本**：1.0.0  
**最后更新**：2025-01-27
