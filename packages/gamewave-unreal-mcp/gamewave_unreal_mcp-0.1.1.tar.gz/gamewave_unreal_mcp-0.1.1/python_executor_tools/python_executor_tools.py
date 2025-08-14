"""
Blueprint Action Tools - Dynamically discover available Blueprint actions

This module provides tools for discovering Blueprint actions using the FBlueprintActionDatabase,
allowing dynamic exploration of what nodes and functions are available for different pin types,
classes, and class hierarchies.
"""

import logging
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP, Context
from utils.python_executor.python_executor_operations import (
    execute_python_code as execute_python_code_impl
)

# Get logger
logger = logging.getLogger("UnrealMCP")

def register_python_executor_tools(mcp: FastMCP):
    """Register ptython executor tools with the MCP server."""

    @mcp.tool()
    def execute_python_code(
        ctx: Context,
        code: str
    ) -> Dict[str, Any]:
        """
        Execute python code in unreal engine.
        
        This tool uses Unreal's IPythonScriptPlugin plugin to execute python code in unreal engine.

        Args:
            code: python code to execute in unreal engine. This argument type is string.
        
        Returns:
            Dict containing:
                - success: Boolean indicating if the python code was executed. The executed code may have run succesfully or unsuccesfully.
                - result: Result of the python code execution.
        
        Examples:
            # Code to create a new level in Unreal Engine.
            execute_python_code(code="import unreal\nunreal.EditorLevelLibrary.new_level('level_name')")
            
            # Code to Get the Unreal Engine version.
            execute_python_code(code="import unreal\nversion = unreal.SystemLibrary.get_engine_version()\nprint(version)")
            
            # Code to import an asset into Unreal Engine.
            execute_python_code(pin_type="import unreal\nimport os\nfile_path = 'file_path'\ndestination_path = 'destination_path'\ntask = unreal.AssetImportTask()\ntask.filename = file_path\ntask.destination_path = destination_path\ntask.automated = True\ntask.save = True\nunreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])")
        """
        return execute_python_code_impl(ctx, code)
