# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description:
RunPythonCode MCP Server implementation.
This module provides Python code execution tools via MCP (Model Context Protocol).
"""
from typing import Optional
from mcp.server.fastmcp import FastMCP
import tempfile
from run_python_code.code import RunPythonCode

# Create MCP server instance
mcp = FastMCP(
    name="RunPythonCodeServer",
    instructions="Execute Python code, install python packages, and run Python files",
)
# Initialize the RunPythonCode tool
python_runner = RunPythonCode(base_dir=tempfile.mkdtemp())


@mcp.tool()
def run_python_code(code: str, variable_to_return: Optional[str] = None) -> str:
    """
    Run Python code in the current environment.

    Parameters:
        code: The Python code to execute
        variable_to_return: Optional variable name to return its value

    Returns:
        str: The value of variable_to_return if provided, otherwise success message or error
    """
    return python_runner.run_python_code(code, variable_to_return)


@mcp.tool()
def save_to_file_and_run(
        file_name: str,
        code: str,
        variable_to_return: Optional[str] = None,
        overwrite: bool = True
) -> str:
    """
    Save Python code to a file and run it.

    Parameters:
        file_name: Name of the file to save (e.g., "script.py")
        code: Python code to save and execute
        variable_to_return: Optional variable name to return its value
        overwrite: Whether to overwrite existing file

    Returns:
        str: The value of variable_to_return if provided, otherwise success message or error
    """
    return python_runner.save_to_file_and_run(file_name, code, variable_to_return, overwrite)


@mcp.tool()
def pip_install_package(package_name: str) -> str:
    """
    Install a Python package using pip.

    Parameters:
        package_name: Name of the package to install

    Returns:
        str: Success message or error information
    """
    return python_runner.pip_install_package(package_name)


@mcp.tool()
def run_python_file(file_name: str, variable_to_return: Optional[str] = None) -> str:
    """
    Run an existing Python file.

    Parameters:
        file_name: Name of the Python file to run
        variable_to_return: Optional variable name to return its value

    Returns:
        str: The value of variable_to_return if provided, otherwise success message or error
    """
    return python_runner.run_python_file_return_variable(file_name, variable_to_return)


def run_server():
    """
    Run the MCP server with the specified transport.
    """
    mcp.run(transport='stdio')
