#!/usr/bin/env python3
"""
Serena CLI - Command line interface for managing Serena coding agent tools.
"""

import asyncio
import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .serena_manager import SerenaManager
from .project_detector import ProjectDetector
from .config_manager import ConfigManager

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="1.0.0", prog_name="serena-cli")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose):
    """Serena CLI - 快速启用和配置 Serena 编码代理工具"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.option("--project", "-p", help="项目路径，留空则使用当前目录")
@click.option("--context", "-c", default="ide-assistant", help="Serena 上下文")
@click.option("--force", "-f", is_flag=True, help="强制重新安装")
def enable(project, context, force):
    """在指定或当前项目中启用 Serena"""
    asyncio.run(_enable_serena(project, context, force))


@cli.command()
@click.option("--project", "-p", help="项目路径")
def status(project):
    """查询 Serena 服务状态"""
    asyncio.run(_get_status(project))


@cli.command()
@click.option("--type", "-t", "config_type", default="project", type=click.Choice(["global", "project"]), help="配置类型")
@click.option("--project", "-p", help="项目路径")
def config(config_type, project):
    """编辑 Serena 配置"""
    _edit_config(config_type, project)


@cli.command()
@click.option("--project", "-p", help="项目路径")
def info(project):
    """获取项目信息"""
    _get_project_info(project)


@cli.command()
def start_mcp_server():
    """启动 MCP 服务器"""
    asyncio.run(_start_mcp_server())


@cli.command()
def start_mcp_simple():
    """启动简化的 MCP 服务器（避免 TaskGroup 问题）"""
    console.print("[green]启动简化的 Serena CLI MCP 服务器...[/green]")
    asyncio.run(_start_mcp_simple())


@cli.command()
def mcp_tools():
    """显示可用的 MCP 工具信息"""
    _show_mcp_tools()


@cli.command()
def check_env():
    """检查环境兼容性"""
    _check_environment()


async def _enable_serena(project_path, context, force):
    """Enable Serena in project."""
    try:
        serena_manager = SerenaManager()
        
        if not project_path:
            detector = ProjectDetector()
            project_path = detector.detect_current_project()
        
        if not project_path:
            console.print("[red]❌ 无法检测到项目路径[/red]")
            return
        
        console.print(f"[blue]🔧 在项目 {project_path} 中启用 Serena...[/blue]")
        
        result = await serena_manager.enable_in_project(
            project_path=project_path,
            context=context,
            force=force
        )
        
        if result.get("success"):
            console.print(f"[green]✅ Serena 启用成功！[/green]")
            console.print(f"   项目: {project_path}")
            console.print(f"   上下文: {context}")
            
            # Show Python compatibility info
            if "python_compatibility" in result:
                compat = result["python_compatibility"]
                if not compat.get("compatible"):
                    console.print(f"[yellow]⚠️  Python 版本兼容性警告: {compat.get('warning', '')}[/yellow]")
        else:
            console.print(f"[red]❌ Serena 启用失败: {result.get('error', '未知错误')}[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ 启用失败: {e}[/red]")
        logger.error(f"Error enabling Serena: {e}")


async def _get_status(project_path):
    """Get Serena status."""
    try:
        serena_manager = SerenaManager()
        
        if not project_path:
            detector = ProjectDetector()
            project_path = detector.detect_current_project()
        
        if not project_path:
            console.print("[red]❌ 无法检测到项目路径[/red]")
            return
        
        status = await serena_manager.get_status(project_path)
        
        if "error" in status:
            console.print(f"[red]❌ 获取状态失败: {status['error']}[/red]")
            return
        
        # Create status table
        table = Table(title=f"Serena 状态 - {Path(project_path).name}")
        table.add_column("项目", style="cyan")
        table.add_column("状态", style="green")
        table.add_column("配置", style="blue")
        table.add_column("Python 兼容性", style="yellow")
        
        # status is directly the status object, not wrapped in {"status": ...}
        table.add_row(
            str(project_path),
            "✅ 已启用" if status["serena_enabled"] else "❌ 未启用",
            "✅ 已配置" if status["config_exists"] else "❌ 未配置",
            "✅ 兼容" if status["python_compatibility"]["compatible"] else "⚠️ 可能不兼容"
        )
        
        console.print(table)
        
        # Show additional info
        if not status["python_compatibility"]["compatible"]:
            console.print(f"[yellow]⚠️  Python 版本兼容性警告: 当前版本 {status['python_compatibility']['version']}，推荐 {status['python_compatibility']['recommended']}[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ 获取状态失败: {e}[/red]")
        logger.error(f"Error getting status: {e}")
        # Add more detailed error information
        import traceback
        console.print(f"[yellow]详细错误信息: {traceback.format_exc()}[/yellow]")


def _edit_config(config_type, project_path):
    """Edit configuration."""
    try:
        config_manager = ConfigManager()
        
        if config_type == "project" and not project_path:
            detector = ProjectDetector()
            project_path = detector.detect_current_project()
        
        result = config_manager.edit_config(config_type, project_path)
        
        if result.get("success"):
            console.print(f"[green]✅ 配置已打开进行编辑[/green]")
            console.print(f"   配置类型: {config_type}")
            if project_path:
                console.print(f"   项目路径: {project_path}")
        else:
            console.print(f"[red]❌ 编辑配置失败: {result.get('error', '未知错误')}[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ 编辑配置失败: {e}[/red]")
        logger.error(f"Error editing config: {e}")


def _get_project_info(project_path):
    """Get project information."""
    try:
        detector = ProjectDetector()
        
        if not project_path:
            project_path = detector.detect_current_project()
        
        if not project_path:
            console.print("[red]❌ 无法检测到项目路径[/red]")
            return
        
        project_info = detector.get_project_info(project_path)
        
        if not project_info:
            console.print("[red]❌ 无法获取项目信息[/red]")
            return
        
        # Create info table
        table = Table(title=f"项目信息 - {project_info['name']}")
        table.add_column("属性", style="cyan")
        table.add_column("值", style="green")
        
        table.add_row("项目路径", str(project_path))
        table.add_row("项目类型", project_info["type"])
        table.add_row("编程语言", ", ".join(project_info["languages"]))
        table.add_row("文件数量", str(project_info["size"]["total_files"]))
        table.add_row("项目大小", f"{project_info['size']['total_size_mb']:.2f} MB")
        table.add_row("Serena 配置", "✅ 已配置" if project_info["has_serena"] else "❌ 未配置")
        table.add_row("Panda 配置", "✅ 已配置" if project_info["has_panda_config"] else "❌ 未配置")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ 获取项目信息失败: {e}[/red]")
        logger.error(f"Error getting project info: {e}")


async def _start_mcp_server():
    """Start MCP server."""
    try:
        from .mcp_server import SerenaCLIMCPServer
        
        server = SerenaCLIMCPServer()
        
        if not server.is_mcp_available():
            console.print("[red]❌ MCP 库不可用[/red]")
            console.print("[yellow]💡 你可以直接使用 CLI 命令:[/yellow]")
            console.print("   serena-cli enable     # 启用 Serena")
            console.print("   serena-cli status     # 查询状态")
            console.print("   serena-cli config     # 编辑配置")
            return
        
        console.print("[green]🚀 启动 Serena CLI MCP 服务器...[/green]")
        await server.run()
        
    except Exception as e:
        console.print(f"[red]❌ 启动服务器失败: {e}[/red]")
        logger.error(f"Error starting MCP server: {e}")
        
        if "TaskGroup" in str(e):
            console.print("[yellow]⚠️  这是已知的 MCP 库兼容性问题[/yellow]")
            console.print("[yellow]💡 你可以直接使用 CLI 命令:[/yellow]")
            console.print("   serena-cli enable     # 启用 Serena")
            console.print("   serena-cli status     # 查询状态")
            console.print("   serena-cli config     # 编辑配置")


async def _start_mcp_simple():
    """Start simplified MCP server."""
    try:
        from .mcp_server import SerenaCLIMCPServer
        
        server = SerenaCLIMCPServer()
        console.print(f"[blue]📊 MCP 可用性: {'✅ 可用' if server.is_mcp_available() else '❌ 不可用'}[/blue]")
        
        tools = server.get_tools_info()
        console.print(f"[blue]🔧 可用工具数量: {len(tools)}[/blue]")
        
        for tool in tools:
            console.print(f"   - {tool['name']}: {tool['description']}")
        
        console.print("\n[green]✅ 简化 MCP 服务器启动完成！[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ 启动简化服务器失败: {e}[/red]")
        logger.error(f"Error starting simplified MCP server: {e}")


def _show_mcp_tools():
    """Show MCP tools information."""
    try:
        from .mcp_server import SerenaCLIMCPServer
        
        server = SerenaCLIMCPServer()
        
        console.print(f"\n🔧 可用的 MCP 工具:")
        
        table = Table(title="MCP 工具列表")
        table.add_column("工具名称", style="cyan")
        table.add_column("描述", style="green")
        table.add_column("使用方法", style="blue")
        
        for tool in server.get_tools_info():
            table.add_row(
                tool["name"],
                tool["description"],
                f"@mcp {tool['name']}"
            )
        
        console.print(table)
        
        console.print(f"\n💡 如果 MCP 服务器不可用，你可以使用以下 CLI 命令:")
        console.print("  serena-cli enable     # 启用 Serena")
        console.print("  serena-cli status     # 查询状态")
        console.print("  serena-cli config     # 编辑配置")
        console.print("  serena-cli info       # 项目信息")
        
    except Exception as e:
        console.print(f"[red]❌ 显示 MCP 工具失败: {e}[/red]")
        logger.error(f"Error showing MCP tools: {e}")


def _check_environment():
    """Check environment compatibility."""
    try:
        serena_manager = SerenaManager()
        
        console.print("[blue]🔍 检查环境兼容性...[/blue]")
        
        # Check Python version
        python_version = serena_manager.python_version
        is_compatible = serena_manager.is_python_compatible
        
        console.print(f"🐍 Python 版本: {python_version}")
        
        if is_compatible:
            console.print("[green]✅ Python 版本兼容[/green]")
        else:
            console.print("[yellow]⚠️  Python 版本可能不兼容[/yellow]")
            console.print(f"   推荐版本: 3.11-3.12")
        
        # Check dependencies
        dependencies = ["mcp", "yaml", "click", "rich", "psutil"]
        for dep in dependencies:
            try:
                __import__(dep)
                console.print(f"✅ {dep}: 已安装")
            except ImportError:
                console.print(f"❌ {dep}: 未安装")
        
        # Show Serena compatibility info
        guide = serena_manager.get_installation_guide()
        console.print(f"\n📊 Serena 兼容性:")
        console.print(f"   当前版本: {guide['python_version']}")
        console.print(f"   推荐版本: {guide['recommended_version']}")
        console.print(f"   兼容性: {'✅ 兼容' if guide['compatible'] else '⚠️ 可能不兼容'}")
        
        if not guide['compatible']:
            console.print(f"\n⚠️  兼容性警告:")
            for warning in guide.get('warnings', []):
                console.print(f"   - {warning}")
        
        console.print(f"\n[green]✅ 环境检查完成！[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ 环境检查失败: {e}[/red]")
        logger.error(f"Error checking environment: {e}")


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
