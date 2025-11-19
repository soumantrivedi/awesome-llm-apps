#!/usr/bin/env python3
"""
Cloudability V2 MCP Server Entry Point
This script can be used as the command for MCP server registration
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())

