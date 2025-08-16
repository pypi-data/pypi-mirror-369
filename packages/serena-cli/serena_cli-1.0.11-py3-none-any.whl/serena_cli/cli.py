#!/usr/bin/env python3
"""
Serena CLI - Command Line Interface
A powerful CLI tool for quickly enabling and configuring Serena coding agent tools.
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .serena_manager import SerenaManager
from .project_detector import ProjectDetector
from .config_manager import ConfigManager
from .mcp_server import SerenaCLIMCPServer

console = Console()

@click.group(invoke_without_command=True)
@click.version_option(version="1.0.11", prog_name="serena-cli")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, verbose):
    """Serena CLI - Quickly enable and configure Serena coding agent tools"""
    if ctx.invoked_subcommand is None:
        # Show help if no subcommand is provided
        click.echo(ctx.get_help())
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

@cli.command()
@click.option("--project", help="Project path (leave blank to use current directory)")
def check_env(project):
    """Check environment compatibility"""
    project_path = project or os.getcwd()
    
    console.print("\n🔍 Checking environment compatibility...")
    
    # Check Python version
    python_version = sys.version_info
    console.print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check Python compatibility
    if python_version.major == 3 and python_version.minor >= 10 and python_version.minor <= 12:
        console.print("✅ Python version is compatible with Serena")
    else:
        console.print("⚠️  Python version may not be compatible with Serena")
        console.print("   Recommended: Python 3.10-3.12")
    
    # Check dependencies
    dependencies = ["mcp", "yaml", "click", "rich", "psutil"]
    for dep in dependencies:
        try:
            __import__(dep)
            console.print(f"✅ {dep}: Installed")
        except ImportError:
            console.print(f"❌ {dep}: Not installed")
    
    # Serena compatibility assessment
    console.print("\n📊 Serena compatibility:")
    if python_version.major == 3 and python_version.minor >= 10 and python_version.minor <= 12:
        console.print("   Current version: {}.{}.{}".format(python_version.major, python_version.minor, python_version.micro))
        console.print("   Recommended version: 3.10-3.12")
        console.print("   Compatibility: ✅ Compatible")
    else:
        console.print("   Current version: {}.{}.{}".format(python_version.major, python_version.minor, python_version.micro))
        console.print("   Recommended version: 3.10-3.12")
        console.print("   Compatibility: ⚠️  May not be compatible")
        
        console.print("\n⚠️  Compatibility warning:")
        console.print("   - Current Python version {}.{}.{} may not be compatible with Serena".format(
            python_version.major, python_version.minor, python_version.micro))
        console.print("   - Recommended: Python 3.10, 3.11 or 3.12")
        console.print("   - If installation fails, consider downgrading Python version or wait for Serena update")
        
        # Provide quick solutions
        console.print("\n🚀 Quick solutions:")
        console.print("   1. Use pyenv to install Python 3.10, 3.11 or 3.12:")
        console.print("      pyenv install 3.10.12")
        console.print("      pyenv local 3.10.12")
        console.print("   2. Use conda to create a compatible environment:")
        console.print("      conda create -n serena python=3.10")
        console.print("      conda activate serena")
        console.print("   3. Use Docker with Python 3.10:")
        console.print("      docker run -it python:3.10-slim bash")
        console.print("   4. Continue with current version (may have issues)")
    
    console.print("\n✅ Environment check completed!")

@cli.command()
@click.option("--project", help="Project path (leave blank to use current directory)")
def info(project):
    """Get project information"""
    project_path = project or os.getcwd()
    
    try:
        detector = ProjectDetector()
        project_info = detector.get_project_info(project_path)
        
        if project_info:
            console.print(f"\n📁 Project: {project_info['name']}")
            console.print(f"📍 Path: {project_info['path']}")
            console.print(f"🔧 Type: {project_info['type']}")
            console.print(f"📊 Status: {'✅ Enabled' if project_info['enabled'] else '❌ Not enabled'}")
            
            if project_info['config']:
                console.print(f"⚙️  Config: {project_info['config']}")
        else:
            console.print("❌ No project detected at the specified path")
            
    except Exception as e:
        console.print(f"❌ Error getting project info: {e}")

@cli.command()
@click.option("--project", help="Project path (leave blank to use current directory)")
def status(project):
    """Query Serena service status"""
    project_path = project or os.getcwd()
    
    try:
        serena_manager = SerenaManager()
        status = serena_manager.get_status_sync(project_path)
        
        console.print(f"\n📊 Serena Status for: {os.path.basename(project_path)}")
        console.print(f"🔧 Enabled: {'✅ Yes' if status['serena_enabled'] else '❌ No'}")
        console.print(f"📁 Project: {status['project_path']}")
        console.print(f"🐍 Python: {status['python_version']}")
        
        if status['serena_enabled']:
            console.print(f"📦 Installation: {status['installation_method']}")
            console.print(f"⚙️  Context: {status['serena_context']}")
        
    except Exception as e:
        console.print(f"❌ Error getting status: {e}")

@cli.command()
@click.argument("config_type", type=click.Choice(["global", "project"]))
@click.option("--project", help="Project path (leave blank to use current directory)")
def config(config_type, project):
    """Edit Serena configuration"""
    project_path = project or os.getcwd()
    
    try:
        config_manager = ConfigManager()
        
        if config_type == "global":
            config_manager.edit_global_config()
        else:
            config_manager.edit_project_config(project_path)
            
    except Exception as e:
        console.print(f"❌ Error editing config: {e}")

@cli.command()
@click.option("--project", help="Project path (leave blank to use current directory)")
def enable(project):
    """Enable Serena in specified or current project"""
    project_path = project or os.getcwd()
    
    try:
        serena_manager = SerenaManager()
        result = serena_manager.enable_serena(project_path)
        
        if result['success']:
            console.print("✅ Serena enabled successfully!")
            console.print(f"📁 Project: {result['project_path']}")
            console.print(f"⚙️  Context: {result['context']}")
        else:
            console.print("❌ Failed to enable Serena")
            console.print(f"📝 Reason: {result['error']}")
            
    except Exception as e:
        console.print(f"❌ Error enabling Serena: {e}")

@cli.command()
def mcp_tools():
    """Show available MCP tools information"""
    try:
        server = SerenaCLIMCPServer()
        tools = server.get_tools()
        
        table = Table(title="Available MCP Tools")
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="green")
        
        for tool_name, tool_info in tools.items():
            table.add_row(tool_name, tool_info.get('description', 'No description'))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error getting MCP tools: {e}")

@cli.command()
def start_mcp_server():
    """Start MCP server"""
    console.print("🚀 Starting Serena CLI MCP server...")
    console.print("📡 Server will be available for MCP clients")
    console.print("⚠️  Note: If you encounter TaskGroup errors, use 'start-mcp-simple' instead")
    
    try:
        _start_mcp_server()
    except Exception as e:
        console.print(f"❌ Failed to start server: {e}")
        console.print("💡 Try using 'serena-cli start-mcp-simple' for a simplified version")

@cli.command()
def start_mcp_simple():
    """Start simplified MCP server (avoids TaskGroup issues)"""
    console.print("🚀 Starting Serena CLI simplified MCP server...")
    console.print("📡 This version avoids known TaskGroup compatibility issues")
    
    try:
        _start_mcp_simple()
    except Exception as e:
        console.print(f"❌ Failed to start simplified server: {e}")
        console.print("💡 You can still use all CLI commands directly")

def _start_mcp_server():
    """Start the MCP server with smart wizard"""
    try:
        # 启动智能 MCP 服务器向导
        console.print("\n🚀 启动智能 MCP 服务器向导...")
        try:
            start_smart_mcp_wizard()
        except Exception as e:
            console.print(f"⚠️  智能向导启动失败: {e}")
            console.print("💡 回退到传统模式...")
            start_traditional_serena_web_server()
        
        # 启动 MCP 服务器
        server = SerenaCLIMCPServer()
        server.run()
    except Exception as e:
        console.print(f"❌ Server startup failed: {e}")
        console.print("💡 CLI functionality remains fully operational")

def _start_mcp_simple():
    """Start a simplified MCP server"""
    try:
        # Import here to avoid circular imports
        from .mcp_server import SerenaCLIMCPServer
        server = SerenaCLIMCPServer()
        server.run()
    except Exception as e:
        console.print(f"❌ Simplified server startup failed: {e}")
        console.print("💡 CLI functionality remains fully operational")

def _show_mcp_tools():
    """Show available MCP tools"""
    try:
        server = SerenaCLIMCPServer()
        tools = server.get_tools()
        
        console.print("\n🔧 Available MCP Tools:")
        for tool_name, tool_info in tools.items():
            console.print(f"  • {tool_name}: {tool_info.get('description', 'No description')}")
            
    except Exception as e:
        console.print(f"❌ Error getting MCP tools: {e}")

def _check_environment():
    """Check environment compatibility"""
    console.print("\n🔍 Checking environment...")
    
    # Check Python version
    python_version = sys.version_info
    console.print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check dependencies
    dependencies = ["mcp", "yaml", "click", "rich", "psutil"]
    for dep in dependencies:
        try:
            __import__(dep)
            console.print(f"✅ {dep}: Installed")
        except ImportError:
            console.print(f"❌ {dep}: Not installed")
    
    # Serena compatibility
    if python_version.major == 3 and python_version.minor >= 10 and python_version.minor <= 12:
        console.print("✅ Python version is compatible with Serena")
    else:
        console.print("⚠️  Python version may not be compatible with Serena")
        console.print("   Recommended: Python 3.10-3.12")
        console.print("   Continuing with installation attempt...")

def _get_status(project_path: str) -> dict:
    """Get project status"""
    try:
        serena_manager = SerenaManager()
        return serena_manager.get_status(project_path)
    except Exception as e:
        return {"error": str(e)}

def start_smart_mcp_wizard():
    """启动智能 MCP 服务器向导"""
    console.print("🚀 Serena CLI 智能 MCP 服务器启动向导")
    console.print("=" * 50)
    
    # 第一步：环境检查
    if not check_environment():
        console.print("❌ 环境检查失败，无法继续")
        return False
    
    # 第二步：依赖检查
    if not check_dependencies():
        console.print("❌ 依赖检查失败，无法继续")
        return False
    
    # 第三步：平台选择
    platform = select_target_platform()
    if not platform:
        console.print("❌ 平台选择失败，无法继续")
        return False
    
    # 第四步：配置目标平台
    if not configure_target_platform(platform):
        console.print("❌ 平台配置失败，无法继续")
        return False
    
    # 第五步：配置验证
    if not verify_configuration(platform):
        console.print("⚠️  配置验证失败，但可能仍可使用")
    
    # 第六步：使用指导
    show_usage_guide(platform)
    
    return True

def check_environment():
    """检查 Python 环境"""
    console.print("🔍 第一步：环境检查...")
    
    # 检查 Python 版本
    python_version = sys.version_info
    if python_version < (3, 10):
        console.print(f"❌ Python 版本过低: {python_version.major}.{python_version.minor}")
        console.print("💡 需要 Python 3.10+")
        console.print("   建议使用: pyenv install 3.11.0")
        return False
    
    console.print(f"✅ Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查虚拟环境
    venv_active = os.environ.get('VIRTUAL_ENV') is not None
    if venv_active:
        console.print("✅ 虚拟环境已激活")
    else:
        console.print("⚠️  未检测到虚拟环境")
        console.print("💡 建议创建虚拟环境以获得最佳体验")
    
    return True

def check_dependencies():
    """检查依赖工具"""
    console.print("\n🔍 第二步：依赖检查...")
    
    missing_tools = []
    
    # 检查 uv
    if not shutil.which("uv"):
        missing_tools.append("uv")
        console.print("❌ uv 未安装")
    else:
        console.print("✅ uv 已安装")
    
    # 检查 uvx
    if not shutil.which("uvx"):
        missing_tools.append("uvx")
        console.print("❌ uvx 未安装")
    else:
        console.print("✅ uvx 已安装")
    
    # 检查 pip (备用方案)
    if not shutil.which("pip"):
        missing_tools.append("pip")
        console.print("❌ pip 未安装")
    else:
        console.print("✅ pip 已安装")
    
    # 安装缺失的工具
    if missing_tools:
        console.print(f"\n🔧 正在安装缺失依赖: {', '.join(missing_tools)}...")
        if not install_missing_tools(missing_tools):
            console.print("❌ 依赖安装失败")
            return False
    
    console.print("✅ 所有依赖检查通过！")
    return True

def install_missing_tools(tools):
    """安装缺失的工具"""
    for tool in tools:
        if tool == "uv":
            if not install_uv():
                return False
        elif tool == "uvx":
            if not install_uvx():
                return False
        elif tool == "pip":
            if not install_pip():
                return False
    
    return True

def install_uv():
    """安装 uv 工具"""
    console.print("📦 正在安装 uv...")
    
    # 方法 1: 官方安装脚本
    try:
        result = subprocess.run([
            "curl", "-LsSf", "https://astral.sh/uv/install.sh", "|", "sh"
        ], shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            console.print("✅ uv 安装成功 (官方脚本)")
            return True
    except:
        pass
    
    # 方法 2: pip 安装
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "uv"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            console.print("✅ uv 安装成功 (pip)")
            return True
    except:
        pass
    
    # 方法 3: 手动指导
    console.print("❌ 自动安装失败")
    console.print("💡 请手动安装 uv:")
    console.print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
    return False

def install_uvx():
    """安装 uvx 工具"""
    console.print("📦 正在安装 uvx...")
    
    try:
        result = subprocess.run(["uv", "pip", "install", "uvx"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            console.print("✅ uvx 安装成功")
            return True
    except:
        pass
    
    console.print("❌ uvx 安装失败")
    console.print("💡 请手动安装: uv pip install uvx")
    return False

def install_pip():
    """安装 pip 工具"""
    console.print("📦 正在安装 pip...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            console.print("✅ pip 安装成功")
            return True
    except:
        pass
    
    console.print("❌ pip 安装失败")
    console.print("💡 请手动安装 pip")
    return False

def select_target_platform():
    """选择目标平台"""
    console.print("\n🔍 第三步：选择目标平台...")
    
    # 检测可用平台
    platforms = detect_available_platforms()
    
    if not platforms:
        console.print("❌ 未检测到可用的 AI 工作台")
        return None
    
    # 显示平台选项
    console.print("请选择目标 AI 编程工作台:\n")
    
    platform_options = []
    for i, (name, info) in enumerate(platforms.items(), 1):
        status_icon = "✅" if info["status"] == "available" else "❌"
        priority_icon = "⭐" if info["priority"] == "high" else "💡"
        console.print(f"{i}. {status_icon} {name.title()} - {info['description']} {priority_icon}")
        platform_options.append(name)
    
    # 用户选择
    while True:
        try:
            choice = input(f"\n请输入选择 (1-{len(platforms)}): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(platforms):
                selected_platform = platform_options[choice_num - 1]
                console.print(f"✅ 已选择: {selected_platform.title()}")
                return selected_platform
            else:
                console.print(f"❌ 请输入 1-{len(platforms)} 之间的数字")
        except ValueError:
            console.print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            console.print("\n❌ 用户取消选择")
            return None

def detect_available_platforms():
    """检测可用的平台"""
    platforms = {}
    
    # 检测 Claude
    if os.path.exists(os.path.expanduser("~/.claude.json")):
        platforms["claude"] = {
            "status": "available",
            "priority": "high",
            "description": "官方 Serena 集成 (推荐)"
        }
    
    # 检测 Cursor
    if os.path.exists(os.path.expanduser("~/.cursor")):
        platforms["cursor"] = {
            "status": "available", 
            "priority": "medium",
            "description": "MCP 协议集成"
        }
    
    # 检测 VSCode
    if os.path.exists(os.path.expanduser("~/.vscode")):
        platforms["vscode"] = {
            "status": "available",
            "priority": "medium", 
            "description": "MCP 协议集成"
        }
    
    # 添加传统 MCP 服务器选项
    platforms["traditional"] = {
        "status": "available",
        "priority": "low",
        "description": "标准 MCP 协议"
    }
    
    return platforms

def configure_target_platform(platform):
    """配置目标平台"""
    console.print(f"\n🔧 第四步：配置 {platform.title()}...")
    
    if platform == "claude":
        return configure_claude()
    elif platform == "cursor":
        return configure_cursor()
    elif platform == "vscode":
        return configure_vscode()
    elif platform == "traditional":
        return configure_traditional()
    else:
        console.print(f"❌ 未知平台: {platform}")
        return False

def configure_claude():
    """配置 Claude Desktop"""
    console.print("🤖 配置 Claude Desktop...")
    
    try:
        # 获取当前目录
        current_project = os.getcwd()
        context = "ide-assistant"
        
        # 执行 Claude MCP 命令
        command = [
            "claude", "mcp", "add", "serena", "--",
            "uvx", "--from", "git+https://github.com/oraios/serena",
            "serena", "start-mcp-server", "--context", context, "--project", current_project
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("✅ 成功添加到 Claude MCP!")
            console.print(f"   Context: {context}")
            console.print(f"   Project: {current_project}")
            console.print("🔄 请重启 Claude 以使用新工具")
            return True
        else:
            console.print("❌ Claude MCP 配置失败")
            console.print(f"   错误: {result.stderr}")
            return False
            
    except Exception as e:
        console.print(f"❌ Claude 配置异常: {e}")
        return False

def configure_cursor():
    """配置 Cursor IDE"""
    console.print("️ 配置 Cursor IDE...")
    
    try:
        # 创建配置目录
        config_dir = Path.home() / ".cursor"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "mcp.json"
        
        # 读取现有配置或创建新配置
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {"mcpServers": {}}
        
        # 添加 serena-cli 配置
        config["mcpServers"]["serena-cli"] = {
            "command": "serena-cli",
            "args": ["start-mcp-server"],
            "env": {}
        }
        
        # 写入配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        console.print("✅ 成功配置 Cursor MCP!")
        console.print(f"   配置文件: {config_file}")
        console.print("🔄 请重启 Cursor 以使用新工具")
        return True
        
    except Exception as e:
        console.print(f"❌ Cursor 配置异常: {e}")
        return False

def configure_vscode():
    """配置 VSCode"""
    console.print(" 配置 VSCode...")
    
    try:
        # 创建项目级配置
        config_dir = Path.cwd() / ".vscode"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "settings.json"
        
        # 读取现有配置或创建新配置
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        # 添加 MCP 配置
        if "mcp.servers" not in config:
            config["mcp.servers"] = {}
        
        config["mcp.servers"]["serena-cli"] = {
            "command": "serena-cli",
            "args": ["start-mcp-server"],
            "env": {}
        }
        
        # 写入配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        console.print("✅ 成功配置 VSCode MCP!")
        console.print(f"   配置文件: {config_file}")
        console.print("💡 需要安装 MCP 扩展才能使用")
        console.print("🔄 请重启 VSCode 以使用新工具")
        return True
        
    except Exception as e:
        console.print(f"❌ VSCode 配置异常: {e}")
        return False

def configure_traditional():
    """配置传统 MCP 服务器"""
    console.print("🌐 配置传统 MCP 服务器...")
    
    try:
        # 启动传统 MCP 服务器
        start_traditional_serena_web_server()
        return True
    except Exception as e:
        console.print(f"❌ 传统 MCP 服务器配置异常: {e}")
        return False

def start_traditional_serena_web_server():
    """启动传统 Serena Web 服务器"""
    console.print("🌐 启动传统 Serena Web 服务器...")
    
    try:
        import webbrowser
        import time
        import socket
        
        # 检查端口是否被占用
        def is_port_open(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('127.0.0.1', port))
                    return result == 0
            except:
                return False
        
        # 检查端口 24282
        if is_port_open(24282):
            console.print("✅ Serena Web 服务器已在运行!")
            console.print("🌐 Web Dashboard: http://127.0.0.1:24282/dashboard/index.html")
            console.print("🔧 提供 25+ 语义代码编辑和分析工具")
            
            try:
                webbrowser.open("http://127.0.0.1:24282/dashboard/index.html")
                console.print("🚀 Web dashboard 已在浏览器中打开!")
            except Exception as e:
                console.print(f"💡 请手动打开: http://127.0.0.1:24282/dashboard/index.html")
        else:
            # 启动 Serena Web 服务器
            serena_web_cmd = [
                "uvx", "--from", "git+https://github.com/oraios/serena", 
                "serena", "start-mcp-server"
            ]
            
            serena_process = subprocess.Popen(
                serena_web_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(3)
            
            if serena_process.poll() is None:
                console.print("✅ Serena Web 服务器启动成功!")
                console.print("🌐 Web Dashboard: http://127.0.0.1:24282/dashboard/index.html")
                console.print("🔧 提供 25+ 语义代码编辑和分析工具")
                
                try:
                    webbrowser.open("http://127.0.0.1:24282/dashboard/index.html")
                    console.print("🚀 Web dashboard 已在浏览器中打开!")
                except Exception as e:
                    console.print(f"💡 请手动打开: http://127.0.0.1:24282/dashboard/index.html")
            else:
                console.print("⚠️  Serena Web 服务器可能未正确启动")
                console.print("💡 可以手动运行: uvx --from git+https://github.com/oraios/serena serena start-mcp-server")
                
    except Exception as e:
        console.print(f"⚠️  无法启动 Serena Web 服务器: {e}")
        console.print("💡 可以手动运行: uvx --from git+https://github.com/oraios/serena serena start-mcp-server")

def verify_configuration(platform):
    """验证配置"""
    console.print(f"\n🔍 第五步：验证 {platform.title()} 配置...")
    
    if platform == "claude":
        return verify_claude_config()
    elif platform == "cursor":
        return verify_cursor_config()
    elif platform == "vscode":
        return verify_vscode_config()
    elif platform == "traditional":
        return verify_traditional_config()
    
    return False

def verify_claude_config():
    """验证 Claude 配置"""
    try:
        result = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True)
        if result.returncode == 0 and "serena" in result.stdout:
            console.print("✅ Claude MCP 配置验证通过!")
            return True
        else:
            console.print("⚠️  Claude MCP 配置验证失败")
            return False
    except:
        console.print("⚠️  无法验证 Claude MCP 配置")
        return False

def verify_cursor_config():
    """验证 Cursor 配置"""
    config_file = Path.home() / ".cursor" / "mcp.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if "serena-cli" in config.get("mcpServers", {}):
                console.print("✅ Cursor MCP 配置验证通过!")
                return True
        except:
            pass
    
    console.print("⚠️  Cursor MCP 配置验证失败")
    return False

def verify_vscode_config():
    """验证 VSCode 配置"""
    config_file = Path.cwd() / ".vscode" / "settings.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if "serena-cli" in config.get("mcp.servers", {}):
                console.print("✅ VSCode MCP 配置验证通过!")
                return True
        except:
            pass
    
    console.print("⚠️  VSCode MCP 配置验证失败")
    return False

def verify_traditional_config():
    """验证传统 MCP 配置"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', 24282))
            if result == 0:
                console.print("✅ 传统 MCP 服务器验证通过!")
                return True
    except:
        pass
    
    console.print("⚠️  传统 MCP 服务器验证失败")
    return False

def show_usage_guide(platform):
    """显示使用指导"""
    console.print(f"\n📚 第六步：{platform.title()} 使用指导")
    console.print("=" * 50)
    
    if platform == "claude":
        console.print("🤖 Claude Desktop 使用说明:")
        console.print("1. 重启 Claude Desktop")
        console.print("2. 在对话中使用: @mcp serena")
        console.print("3. 享受 18 个 Serena 工具!")
        
    elif platform == "cursor":
        console.print("️ Cursor IDE 使用说明:")
        console.print("1. 重启 Cursor")
        console.print("2. 在聊天中使用: @mcp serena-cli")
        console.print("3. 使用我们的 MCP 工具!")
        
    elif platform == "vscode":
        console.print(" VSCode 使用说明:")
        console.print("1. 安装 MCP 扩展")
        console.print("2. 重启 VSCode")
        console.print("3. 使用 MCP 工具!")
        
    elif platform == "traditional":
        console.print("🌐 传统 MCP 服务器使用说明:")
        console.print("1. 服务器已在后台运行")
        console.print("2. Web Dashboard: http://127.0.0.1:24282/dashboard/index.html")
        console.print("3. 在支持 MCP 的 IDE 中配置服务器地址")
    
    console.print("\n🎉 配置完成！现在你可以开始使用 Serena 了!")
    console.print("💡 如有问题，请查看文档或联系技术支持")

if __name__ == "__main__":
    cli()
