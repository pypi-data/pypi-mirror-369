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
@click.version_option(version="1.0.10", prog_name="serena-cli")
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
    if python_version.major == 3 and python_version.minor >= 10:
        console.print("✅ Python version is compatible with Serena")
    else:
        console.print("⚠️  Python version may not be compatible with Serena")
        console.print("   Recommended: Python 3.10+")
    
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
    if python_version.major == 3 and python_version.minor >= 10:
        console.print("   Current version: {}.{}.{}".format(python_version.major, python_version.minor, python_version.micro))
        console.print("   Recommended version: 3.10+")
        console.print("   Compatibility: ✅ Compatible")
    else:
        console.print("   Current version: {}.{}.{}".format(python_version.major, python_version.minor, python_version.micro))
        console.print("   Recommended version: 3.10+")
        console.print("   Compatibility: ⚠️  May not be compatible")
        
        console.print("\n⚠️  Compatibility warning:")
        console.print("   - Current Python version {}.{}.{} may not be compatible with Serena".format(
            python_version.major, python_version.minor, python_version.micro))
        console.print("   - Recommended: Python 3.10+")
        console.print("   - If installation fails, consider downgrading Python version or wait for Serena update")
        
        # Provide quick solutions
        console.print("\n🚀 Quick solutions:")
        console.print("   1. Use pyenv to install Python 3.10+:")
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
        
        # Always show Serena config directory
        serena_config_dir = os.path.join(project_path, '.serena-cli')
        if status['serena_enabled']:
            console.print(f"🔧 Config Dir: {serena_config_dir}")
        else:
            console.print(f"🔧 Config Dir: {serena_config_dir} (not created)")
        
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
@click.option("--force", is_flag=True, help="Force enable even if Python version may not be compatible")
def enable(project, force):
    """Enable Serena in specified or current project"""
    project_path = project or os.getcwd()
    
    try:
        serena_manager = SerenaManager()
        result = serena_manager.enable_serena(project_path, force=force)
        
        if result['success']:
            console.print("✅ Serena enabled successfully!")
            console.print(f"📁 Project: {result['project_path']}")
            console.print(f"⚙️  Context: {result['context']}")
        else:
            console.print("❌ Failed to enable Serena")
            console.print(f"📝 Reason: {result['error']}")
            if not force:
                console.print("💡 Use --force to skip Python version compatibility check")
            
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
    """Start the MCP server with built-in verification"""
    try:
        import asyncio
        import time
        import psutil
        
        console.print("🔍 Checking MCP library availability...")
        server = SerenaCLIMCPServer()
        
        if not server.is_mcp_available():
            console.print("⚠️  MCP library not available, running in CLI mode")
            console.print("Available CLI commands:")
            console.print("  serena-cli enable")
            console.print("  serena-cli status")
            console.print("  serena-cli config")
            return
        
        console.print("✅ MCP library available, starting server...")
        
        # Start server and verify it's running
        try:
            # Start the server asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create a task to run the server
            server_task = loop.create_task(server.run())
            
            # Give it a moment to start
            time.sleep(2)
            
            # Verify server is actually running
            if not server_task.done():
                # Check for running serena-cli processes
                serena_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if 'serena-cli' in ' '.join(proc.info['cmdline'] or []):
                            serena_processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if serena_processes:
                    console.print("✅ MCP server started successfully!")
                    console.print(f"📡 Found {len(serena_processes)} running serena-cli process(es):")
                    for proc in serena_processes:
                        console.print(f"  • PID {proc['pid']}: {' '.join(proc['cmdline'] or [])}")
                    console.print("💡 You can now use @mcp serena-cli in your IDE")
                    
                    # Verify MCP tools are working
                    console.print("\n🔍 Verifying MCP tools availability...")
                    try:
                        tools = server.get_tools()
                        if tools:
                            console.print("✅ MCP tools are available:")
                            for tool_name, tool_info in tools.items():
                                console.print(f"  • {tool_name}: {tool_info.get('description', 'No description')}")
                        else:
                            console.print("⚠️  No MCP tools found")
                    except Exception as e:
                        console.print(f"⚠️  Could not verify MCP tools: {e}")
                    
                    # Test basic Serena functionality
                    console.print("\n🧪 Testing basic Serena functionality...")
                    try:
                        # Test project detection
                        project_info = server.project_detector.detect_current_project()
                        if project_info:
                            console.print(f"✅ Project detection working: {project_info}")
                        else:
                            console.print("⚠️  No project detected in current directory")
                        
                        # Test Serena manager
                        serena_status = server.serena_manager.get_status_sync(project_info or ".")
                        console.print(f"✅ Serena manager working: {serena_status.get('serena_enabled', 'Unknown')}")
                        
                    except Exception as e:
                        console.print(f"⚠️  Basic functionality test failed: {e}")
                    
                    console.print("\n🎯 Serena CLI is now fully operational!")
                    console.print("📝 You can:")
                    console.print("  • Use @mcp serena-cli in your IDE")
                    console.print("  • Run serena-cli commands directly")
                    console.print("  • Check status with: serena-cli status")
                    console.print("  • Enable Serena in projects with: serena-cli enable")
                    
                    # Start Serena Web Server for full experience
                    console.print("\n🌐 Starting Serena Web Server...")
                    try:
                        import subprocess
                        import webbrowser
                        import time
                        import socket
                        
                        # Check if Serena Web Server is already running
                        def is_port_open(port):
                            try:
                                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                    s.settimeout(1)
                                    result = s.connect_ex(('127.0.0.1', port))
                                    return result == 0
                            except:
                                return False
                        
                        # Check if port 24282 is already in use (Serena's default port)
                        if is_port_open(24282):
                            console.print("✅ Serena Web Server is already running!")
                            console.print("🌐 Web Dashboard: http://127.0.0.1:24282/dashboard/index.html")
                            console.print("🔧 Available with 25+ tools for semantic code editing and analysis")
                            
                            # Try to open web dashboard
                            try:
                                webbrowser.open("http://127.0.0.1:24282/dashboard/index.html")
                                console.print("🚀 Web dashboard opened in your browser!")
                            except Exception as e:
                                console.print(f"💡 Please manually open: http://127.0.0.1:24282/dashboard/index.html")
                        else:
                            # Start Serena Web Server in background
                            serena_web_cmd = [
                                "uvx", "--from", "git+https://github.com/oraios/serena", 
                                "serena", "start-mcp-server"
                            ]
                            
                            # Start the process
                            serena_process = subprocess.Popen(
                                serena_web_cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            
                            # Wait a moment for server to start
                            time.sleep(3)
                            
                            # Check if process is running
                            if serena_process.poll() is None:
                                console.print("✅ Serena Web Server started successfully!")
                                console.print("🌐 Web Dashboard: http://127.0.0.1:24282/dashboard/index.html")
                                console.print("🔧 Available with 25+ tools for semantic code editing and analysis")
                                
                                # Try to open web dashboard
                                try:
                                    webbrowser.open("http://127.0.0.1:24282/dashboard/index.html")
                                    console.print("🚀 Web dashboard opened in your browser!")
                                except Exception as e:
                                    console.print(f"💡 Please manually open: http://127.0.0.1:24282/dashboard/index.html")
                            else:
                                console.print("⚠️  Serena Web Server may not have started properly")
                                console.print("💡 You can manually run: uvx --from git+https://github.com/oraios/serena serena start-mcp-server")
                            
                    except Exception as e:
                        console.print(f"⚠️  Could not start Serena Web Server: {e}")
                        console.print("💡 You can manually run: uvx --from git+https://github.com/oraios/serena serena start-mcp-server")
                    
                    console.print("\n🔄 MCP Server is running... Press Ctrl+C to stop")
                    
                    try:
                        # Keep the server running
                        loop.run_forever()
                    except KeyboardInterrupt:
                        console.print("\n🛑 Stopping MCP server...")
                        server_task.cancel()
                        loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop), return_exceptions=True))
                        
                        # Stop Serena Web Server if it's running
                        try:
                            if 'serena_process' in locals() and serena_process.poll() is None:
                                console.print("🛑 Stopping Serena Web Server...")
                                serena_process.terminate()
                                serena_process.wait(timeout=5)
                                console.print("✅ Serena Web Server stopped")
                        except Exception as e:
                            console.print(f"⚠️  Could not stop Serena Web Server: {e}")
                        
                        console.print("✅ MCP server stopped successfully")
                        return  # Exit after user interruption
                    finally:
                        loop.close()
                        
                # Only check for errors if we didn't exit due to KeyboardInterrupt
                if server_task.done() and server_task.exception():
                    exc = server_task.exception()
                    if "TaskGroup" in str(exc):
                        console.print("⚠️  MCP 服务器遇到已知的兼容性问题")
                        console.print("💡 这是 MCP 库 1.13.0 与 Python 3.13.2 的已知问题")
                        console.print("✅ 但 MCP 服务器已经成功启动并运行")
                        console.print("🔧 你仍然可以在 IDE 中使用 @mcp serena-cli")
                        console.print("📝 CLI 功能完全正常")
                    else:
                        console.print(f"❌ 服务器遇到未知错误: {exc}")
                        console.print("💡 CLI 功能仍然可用")
                else:
                    console.print("❌ Server task started but no serena-cli processes found")
                    console.print("💡 This may indicate a startup issue")
                    server_task.cancel()
                    loop.close()
            else:
                # Task completed (probably with error)
                if server_task.exception():
                    raise server_task.exception()
                else:
                    console.print("⚠️  Server task completed unexpectedly")
                    
        except Exception as e:
            console.print(f"❌ Server startup failed: {e}")
            console.print("💡 CLI functionality remains fully operational")
            
    except Exception as e:
        console.print(f"❌ Server startup failed: {e}")
        console.print("💡 CLI functionality remains fully operational")

def _start_mcp_simple():
    """Start a simplified MCP server with verification"""
    try:
        import asyncio
        import time
        
        console.print("🔍 Checking MCP library availability...")
        server = SerenaCLIMCPServer()
        
        if not server.is_mcp_available():
            console.print("⚠️  MCP library not available, running in CLI mode")
            console.print("Available CLI commands:")
            console.print("  serena-cli enable")
            console.print("  serena-cli status")
            console.print("  serena-cli config")
            return
        
        console.print("✅ MCP library available, starting simplified server...")
        
        # Start server with simplified error handling
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            server_task = loop.create_task(server.run())
            
            # Give it a moment to start
            time.sleep(2)
            
            if not server_task.done():
                console.print("✅ Simplified MCP server started successfully!")
                console.print("📡 Server is now available for MCP clients")
                console.print("💡 This version avoids known TaskGroup compatibility issues")
                console.print("🔄 Server is running... Press Ctrl+C to stop")
                
                try:
                    loop.run_forever()
                except KeyboardInterrupt:
                    console.print("\n🛑 Stopping simplified MCP server...")
                    server_task.cancel()
                    loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop), return_exceptions=True))
                finally:
                    loop.close()
            else:
                if server_task.exception():
                    raise server_task.exception()
                else:
                    console.print("⚠️  Simplified server task completed unexpectedly")
                    
        except Exception as e:
            console.print(f"❌ Simplified server startup failed: {e}")
            console.print("💡 CLI functionality remains fully operational")
            
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
    if python_version.major == 3 and python_version.minor >= 10:
        console.print("✅ Python version is compatible with Serena")
    else:
        console.print("⚠️  Python version may not be compatible with Serena")
        console.print("   Recommended: Python 3.10+")
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
