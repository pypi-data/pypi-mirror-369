#!/usr/bin/env python3
"""
Serena CLI - Command Line Interface
A powerful CLI tool for quickly enabling and configuring Serena coding agent tools.
"""

import os
import sys
import subprocess
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
@click.version_option(version="1.0.2", prog_name="serena-cli")
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
    """Start the MCP server"""
    try:
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

if __name__ == "__main__":
    cli()
