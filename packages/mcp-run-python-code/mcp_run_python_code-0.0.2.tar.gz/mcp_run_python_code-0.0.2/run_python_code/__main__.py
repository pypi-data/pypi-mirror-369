# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: weather tool
CLI entry point for the MCP Weather Server.
"""
from loguru import logger
import sys
from run_python_code.server import run_server


def main():
    """Main entry point for the RunPythonCode MCP Server."""
    logger.info("RunPythonCode MCP Server running...")
    try:
        run_server()
    except KeyboardInterrupt:
        logger.info("Server interrupted, shutting down...")
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
