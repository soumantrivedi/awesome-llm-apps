#!/usr/bin/env python3
"""
Cloudability V2 MCP Server Entry Point
This script can be used as the command for MCP server registration
"""

import sys
import os

# Get the directory containing this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add project root to path so we can import from src
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Import from src package
from src.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())

