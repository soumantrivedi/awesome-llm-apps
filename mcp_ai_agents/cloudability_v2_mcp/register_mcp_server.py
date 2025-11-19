#!/usr/bin/env python3
"""
Register Cloudability V2 MCP Server in Cursor IDE mcp.json
Interactively collects credentials and updates/creates the entry
"""

import json
import os
import sys
from pathlib import Path

# Default mcp.json location
MCP_JSON_PATH = Path.home() / ".cursor" / "mcp.json"

# Alternative locations to check
ALTERNATIVE_PATHS = [
    Path.home() / ".config" / "cursor" / "mcp.json",
    Path.home() / "Library" / "Application Support" / "Cursor" / "mcp.json",
]


def find_mcp_json():
    """Find the mcp.json file location"""
    if MCP_JSON_PATH.exists():
        return MCP_JSON_PATH
    
    for path in ALTERNATIVE_PATHS:
        if path.exists():
            return path
    
    # If not found, use the default location
    return MCP_JSON_PATH


def read_mcp_json(mcp_path):
    """Read mcp.json file"""
    if not mcp_path.exists():
        return {"mcpServers": {}}
    
    try:
        with open(mcp_path, 'r') as f:
            config = json.load(f)
        
        # Ensure mcpServers key exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Ensure mcpServers is a dict
        if not isinstance(config["mcpServers"], dict):
            print("⚠️  Warning: mcpServers is not a dictionary. Fixing structure...")
            config["mcpServers"] = {}
        
        return config
    except json.JSONDecodeError as e:
        print(f"✗ Error reading mcp.json: {e}")
        print("Creating backup before proceeding...")
        # Create backup
        backup_path = mcp_path.with_suffix('.json.bak')
        if mcp_path.exists():
            import shutil
            shutil.copy(mcp_path, backup_path)
            print(f"✓ Backup created at: {backup_path}")
        return {"mcpServers": {}}
    except Exception as e:
        print(f"✗ Unexpected error reading mcp.json: {e}")
        return {"mcpServers": {}}


def write_mcp_json(mcp_path, data):
    """Write mcp.json file with backup"""
    # Create backup before writing
    if mcp_path.exists():
        import shutil
        backup_path = mcp_path.with_suffix('.json.bak')
        shutil.copy(mcp_path, backup_path)
        print(f"✓ Backup created at: {backup_path}")
    
    # Ensure directory exists
    mcp_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Validate structure before writing
    if "mcpServers" not in data:
        raise ValueError("Invalid config structure: missing 'mcpServers' key")
    
    if not isinstance(data["mcpServers"], dict):
        raise ValueError("Invalid config structure: 'mcpServers' must be a dictionary")
    
    with open(mcp_path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')


def get_python_command():
    """Get Python command path"""
    # Check for venv first
    venv_python = Path.cwd() / "venv" / "bin" / "python3"
    if venv_python.exists():
        return str(venv_python.absolute())
    
    # Use system python3
    return "python3"


def get_server_path():
    """Get server script path"""
    server_path = Path.cwd() / "cloudability_v2_mcp_server.py"
    return str(server_path.absolute())


def collect_credentials():
    """Interactively collect credentials"""
    print("\n" + "=" * 80)
    print("Cloudability V2 MCP Server Registration")
    print("=" * 80 + "\n")
    
    print("Please provide your Cloudability credentials:")
    print()
    
    # Ask for authentication method
    auth_method = input("Authentication method (basic/enhanced) [basic]: ").strip().lower()
    if not auth_method:
        auth_method = "basic"
    
    env_vars = {
        "PYTHONUNBUFFERED": "1",
        "CLOUDABILITY_BASE_URL": "https://api.cloudability.com/v3"
    }
    
    if auth_method == "enhanced":
        env_vars["CLOUDABILITY_AUTH_TYPE"] = "opentoken"
        env_vars["CLOUDABILITY_PUBLIC_KEY"] = input("CLOUDABILITY_PUBLIC_KEY: ").strip()
        env_vars["CLOUDABILITY_PRIVATE_KEY"] = input("CLOUDABILITY_PRIVATE_KEY: ").strip()
        env_id = input("CLOUDABILITY_ENVIRONMENT_ID (optional): ").strip()
        if env_id:
            env_vars["CLOUDABILITY_ENVIRONMENT_ID"] = env_id
        frontdoor = input("CLOUDABILITY_FRONTDOOR_URL [https://frontdoor.apptio.com]: ").strip()
        if frontdoor:
            env_vars["CLOUDABILITY_FRONTDOOR_URL"] = frontdoor
        else:
            env_vars["CLOUDABILITY_FRONTDOOR_URL"] = "https://frontdoor.apptio.com"
    else:
        env_vars["CLOUDABILITY_AUTH_TYPE"] = "basic"
        env_vars["CLOUDABILITY_API_KEY"] = input("CLOUDABILITY_API_KEY: ").strip()
    
    # Ask for base URL
    base_url = input("CLOUDABILITY_BASE_URL [https://api.cloudability.com/v3]: ").strip()
    if base_url:
        env_vars["CLOUDABILITY_BASE_URL"] = base_url
    
    return env_vars


def register_mcp_server():
    """Main registration function"""
    mcp_path = find_mcp_json()
    
    print(f"Using mcp.json at: {mcp_path}")
    
    # Read existing configuration
    config = read_mcp_json(mcp_path)
    
    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Show existing servers (excluding cloudability-v2)
    existing_servers = [name for name in config["mcpServers"].keys() if name != "cloudability-v2"]
    if existing_servers:
        print(f"\n✓ Found {len(existing_servers)} existing MCP server(s): {', '.join(existing_servers)}")
        print("  These will be preserved.")
    else:
        print("\n✓ No other MCP servers found.")
    
    # Check if cloudability-v2 already exists
    exists = "cloudability-v2" in config["mcpServers"]
    
    if exists:
        print("\n⚠️  Found existing 'cloudability-v2' entry. It will be updated.")
        response = input("Continue? [y/N]: ").strip().lower()
        if response != 'y':
            print("Registration cancelled.")
            return False
    else:
        print("\n✓ No existing 'cloudability-v2' entry found. Creating new entry.")
    
    # Store original server count for verification
    original_count = len(config["mcpServers"])
    
    # Collect credentials
    env_vars = collect_credentials()
    
    # Build server configuration
    python_cmd = get_python_command()
    server_path = get_server_path()
    
    server_config = {
        "command": python_cmd,
        "args": [
            "-u",
            server_path
        ],
        "env": env_vars
    }
    
    # Store all existing servers (except cloudability-v2) to verify preservation
    other_servers = {k: v for k, v in config["mcpServers"].items() if k != "cloudability-v2"}
    
    # Update configuration - only modify cloudability-v2
    config["mcpServers"]["cloudability-v2"] = server_config
    
    # Verify all other servers are still present
    for server_name, server_config_orig in other_servers.items():
        if server_name not in config["mcpServers"]:
            print(f"\n✗ ERROR: Lost existing server '{server_name}'! Aborting write.")
            return False
        # Verify the config wasn't modified
        if config["mcpServers"][server_name] != server_config_orig:
            print(f"\n✗ ERROR: Existing server '{server_name}' was modified! Aborting write.")
            return False
    
    # Verify we didn't lose any servers
    if len(config["mcpServers"]) < original_count:
        print(f"\n✗ ERROR: Server count decreased from {original_count} to {len(config['mcpServers'])}! Aborting write.")
        return False
    
    # Write back to file
    try:
        write_mcp_json(mcp_path, config)
        print(f"\n✓ Successfully {'updated' if exists else 'registered'} Cloudability V2 MCP Server!")
        print(f"✓ Configuration written to: {mcp_path}")
        print(f"✓ Preserved {len(other_servers)} existing MCP server(s)")
        print("\n⚠️  Please restart Cursor IDE for changes to take effect.")
        return True
    except Exception as e:
        print(f"\n✗ Error writing to mcp.json: {e}")
        print("⚠️  Your original mcp.json should be in the .bak backup file")
        return False


if __name__ == "__main__":
    try:
        success = register_mcp_server()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nRegistration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

