#!/usr/bin/env python3
"""
CBT Query MCP Server Entry Point

Simple entry point for the CBT Query MCP server.
"""

import sys
import logging
from pathlib import Path

# add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from cbt_query.server import mcp, logger


def setup_logging():
    """setup simple logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )


def main():
    """main entry point for CBT Query MCP server"""
    try:
        setup_logging()
        logger.info("Starting CBT Query MCP Server")
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
