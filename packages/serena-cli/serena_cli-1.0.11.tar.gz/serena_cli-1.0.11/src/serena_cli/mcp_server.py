"""
Serena CLI MCP Server

A powerful MCP server for quickly enabling and configuring Serena coding agent tools in specified projects.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

# Try to import MCP library
try:
    from mcp.server import Server
    from mcp import stdio_server
    from mcp.types import Tool
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    Tool = None

from .serena_manager import SerenaManager
from .project_detector import ProjectDetector
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


class SerenaCLIMCPServer:
    """Serena CLI MCP Server for managing Serena coding agent tools."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.mcp_available = MCP_AVAILABLE
        self.server = None
        
        # Initialize managers
        self.serena_manager = SerenaManager()
        self.project_detector = ProjectDetector()
        self.config_manager = ConfigManager()
        
        # Define available tools
        self.tools = [
            {
                "name": "serena_enable",
                "description": "在指定或当前项目中启用 Serena",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "项目路径，留空则使用当前目录"
                        },
                        "context": {
                            "type": "string",
                            "description": "Serena 上下文，如 'ide-assistant'",
                            "default": "ide-assistant"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "强制重新安装",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "serena_status",
                "description": "查询 Serena 服务状态",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "项目路径"
                        }
                    }
                }
            },
            {
                "name": "edit_config",
                "description": "编辑 Serena 配置",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "项目路径"
                        },
                        "config_type": {
                            "type": "string",
                            "description": "配置类型：global 或 project",
                            "enum": ["global", "project"]
                        }
                    }
                }
            }
        ]
        
        if self.mcp_available:
            self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP handlers."""
        try:
            logger.info("Creating MCP Server instance...")
            self.server = Server("serena-cli")
            logger.info("MCP Server instance created successfully")
            
            logger.info("Registering list_tools handler...")
            @self.server.list_tools()
            async def handle_list_tools() -> List[Tool]:
                """List available tools."""
                return [Tool(**tool) for tool in self.tools]
            logger.info("list_tools handler registered successfully")
            
            logger.info("Registering call_tool handler...")
            @self.server.call_tool()
            async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
                """Handle tool calls."""
                return await self.execute_tool(name, arguments)
            logger.info("call_tool handler registered successfully")
            
            logger.info("All MCP handlers registered successfully")
                
        except Exception as e:
            logger.error(f"Failed to register MCP handlers: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.server = None
    
    def is_mcp_available(self) -> bool:
        """Check if MCP is available and properly initialized."""
        if not self.mcp_available:
            return False
        
        # Check if server was successfully created
        if self.server is None:
            logger.warning("MCP library available but server not initialized")
            return False
            
        return True
    
    def get_tools(self) -> dict:
        """Get available MCP tools information."""
        tools_dict = {}
        for tool in self.tools:
            tools_dict[tool["name"]] = {
                "description": tool["description"],
                "inputSchema": tool.get("inputSchema", {})
            }
        return tools_dict

    def get_tools_info(self) -> List[Dict[str, Any]]:
        """Get detailed tools information for CLI display."""
        return self.tools
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments."""
        try:
            if tool_name == "serena_enable":
                return await self._handle_serena_enable(arguments)
            elif tool_name == "serena_status":
                return await self._handle_serena_status(arguments)
            elif tool_name == "edit_config":
                return await self._handle_edit_config(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def _handle_serena_enable(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Serena enable tool."""
        project_path = arguments.get("project_path")
        context = arguments.get("context", "ide-assistant")
        force = arguments.get("force", False)
        
        if not project_path:
            project_path = self.project_detector.detect_current_project()
        
        if not project_path:
            return {"error": "无法检测到项目路径"}
        
        result = await self.serena_manager.enable_in_project(
            project_path=project_path,
            context=context,
            force=force
        )
        
        return result
    
    async def _handle_serena_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Serena status tool."""
        project_path = arguments.get("project_path")
        
        if not project_path:
            project_path = self.project_detector.detect_current_project()
        
        if not project_path:
            return {"error": "无法检测到项目路径"}
        
        status = await self.serena_manager.get_status(project_path)
        return status
    
    async def _handle_edit_config(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle edit config tool."""
        project_path = arguments.get("project_path")
        config_type = arguments.get("config_type", "project")
        
        if config_type == "project" and not project_path:
            project_path = self.project_detector.detect_current_project()
        
        result = self.config_manager.edit_config(config_type, project_path)
        return result
    
    async def run(self, stdio: bool = True):
        """Run the MCP server."""
        if not self.mcp_available or not self.server:
            logger.warning("MCP not available, server cannot run")
            return
        
        try:
            if stdio:
                # For stdio mode, use stdio_server as context manager
                async with stdio_server() as (read_stream, write_stream):
                    await self.server.run(
                        read_stream,
                        write_stream
                    )
            else:
                # Add other server parameters as needed
                pass
        except Exception as e:
            if "TaskGroup" in str(e):
                # Suppress TaskGroup error messages to console
                logger.debug(f"TaskGroup error encountered: {e}")
                logger.info("This is a known compatibility issue with MCP library 1.13.0 and Python 3.13.2")
                logger.info("CLI functionality remains fully operational")
                # Don't raise TaskGroup errors, just log them
                return
            else:
                logger.error(f"Server run error: {e}")
                raise


async def main():
    """Main entry point."""
    try:
        server = SerenaCLIMCPServer()
        
        if server.is_mcp_available():
            logger.info("Starting MCP server...")
            await server.run()
        else:
            logger.warning("MCP server not available, running in test mode")
            # Test mode - show available tools
            tools = server.get_tools_info()
            print("Available tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            print("\nMCP server not available. You can still use CLI commands:")
            print("  serena-cli enable")
            print("  serena-cli status")
            print("  serena-cli config")
            
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        # Provide helpful error information
        if "TaskGroup" in str(e):
            print("\n⚠️  MCP 服务器启动失败，但核心功能仍然可用")
            print("你可以使用以下命令直接操作：")
            print("  serena-cli enable")
            print("  serena-cli status")
            print("  serena-cli config")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
