# 🚀 Serena CLI 快速开始指南

[English](QUICK_START_EN.md) | [中文](QUICK_START.md)

### 安装

```bash
# 克隆仓库
git clone https://github.com/impanda-cookie/serena-cli.git
cd serena-cli

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 开发模式安装
pip install -e .
```

## ⚡ 5分钟快速上手

### 第一步：检查环境
```bash
# 激活虚拟环境（如果使用）
source venv/bin/activate

# 检查环境兼容性
serena-cli check-env
```

**预期输出**：
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

### 第二步：了解当前项目
```bash
# 获取项目信息
serena-cli info
```

**预期输出**：
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

### 第三步：查看项目状态
```bash
# 查询 Serena 状态
serena-cli status
```

**预期输出**：
```
                               Serena 状态 - your-project                               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ 项目                                                   ┃ 状态      ┃ 配置      ┃ Python 兼容性 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ /path/to/your/project                                 │ ❌ 未启用 │ ✅ 已配置 │ ⚠️ 可能不兼容  │
└────────────────────────────────────────┴───────────┴───────────┴───────────────┘
⚠️  Python 版本兼容性警告: 当前版本 3.13.2，推荐 3.11-3.12
```

### 第四步：管理配置
```bash
# 编辑项目配置
serena-cli config

# 编辑全局配置
serena-cli config --type global
```

**预期输出**：
```
✅ 配置已打开进行编辑
   配置类型: project
   项目路径: /path/to/your/project
```

### 第五步：查看可用工具
```bash
# 显示 MCP 工具信息
serena-cli mcp-tools
```

**预期输出**：
```
🔧 可用的 MCP 工具:
                                            MCP 工具列表                                             
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 工具名称           ┃ 描述                                               ┃ 使用方法                ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ serena_enable      │ 在指定或当前项目中启用 Serena                     │ @mcp serena_enable      │
│ serena_status      │ 查询 Serena 服务状态                               │ @mcp serena_status      │
│ edit_config        │ 编辑 Serena 配置                                   │ @mcp edit_config        │
└────────────────────┴────────────────────────────────────────────────────┴─────────────────────────┘
```

## 🎯 实际使用场景

### 场景 1：新项目初始化
```bash
# 进入新项目目录
cd /path/to/new-project

# 检查项目
serena-cli info

# 尝试启用 Serena（注意：Python 3.13 会失败）
serena-cli enable

# 查看详细状态
serena-cli status
```

### 场景 2：现有项目管理
```bash
# 进入现有项目
cd /path/to/existing-project

# 查看当前状态
serena-cli status

# 编辑项目配置
serena-cli config

# 查看项目信息
serena-cli info
```

### 场景 3：多项目批量检查
```bash
# 项目 1
cd /path/to/project1
serena-cli status

# 项目 2  
cd /path/to/project2
serena-cli status

# 项目 3
cd /path/to/project3
serena-cli status
```

## 🔧 故障排除

### 问题 1：命令未找到
```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 检查安装
pip list | grep serena-cli

# 重新安装
pip install -e .
```

### 问题 2：Python 版本不兼容
```bash
# 检查 Python 版本
python --version

# 运行兼容性检查
serena-cli check-env

# 考虑使用 Python 3.11 或 3.12
pyenv install 3.11.0
pyenv local 3.11.0
```

### 问题 3：配置编辑失败
```bash
# 检查编辑器设置
echo $EDITOR

# 手动编辑配置文件
ls -la .serena-cli/
cat .serena-cli/project.yml
```

## 📚 高级用法

### 批量操作脚本
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

## 🎉 成功标志

当你看到以下输出时，说明 Serena CLI 工作正常：

✅ **环境检查通过**：所有依赖库正常  
✅ **项目检测成功**：自动识别项目类型和结构  
✅ **状态查询正常**：显示详细的项目状态信息  
✅ **配置管理可用**：能够编辑和查看配置文件  
✅ **错误处理完善**：提供清晰的错误信息和解决建议  

## 🚀 下一步

1. **熟悉基本命令**：`info`, `status`, `config`
2. **了解项目结构**：查看生成的配置文件
3. **监控项目状态**：定期运行 `status` 命令
4. **自定义配置**：根据项目需求调整配置

---

**记住**：虽然 MCP 服务器有兼容性问题，但 CLI 功能完全正常，你可以立即开始使用！

**需要帮助？** 运行 `serena-cli --help` 查看所有可用命令。
