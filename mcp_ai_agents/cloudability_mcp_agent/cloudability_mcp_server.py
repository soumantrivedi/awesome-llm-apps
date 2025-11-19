#!/usr/bin/env python3
"""
Cloudability MCP Server - Backward Compatible Entry Point
This file maintains backward compatibility while using the new modular architecture.
"""

# Import from new modular structure
from src.main import CloudabilityMCPServer, main
from src.config import Config
import asyncio
import sys

# Re-export for backward compatibility
__all__ = ['CloudabilityMCPServer', 'main', 'Config']

# Main entry point for backward compatibility
if __name__ == "__main__":
    asyncio.run(main())
