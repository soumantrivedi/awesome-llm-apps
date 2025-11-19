"""
Custom MCP Server Wrapper for Atlassian (Jira & Confluence) using API Tokens
Implements MCP protocol following official standards for enterprise environments
where OAuth app creation is not allowed.

This wrapper provides MCP-compatible tools for Jira and Confluence using API token authentication.
"""

import json
import sys
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Import tools directly (not from futuristic_pm package to avoid re-executing st.set_page_config)
try:
    from tools import JiraTools
    from confluence_tools import ConfluenceTools
except ImportError:
    # Fallback: add current directory to path and try again
    import sys
    from pathlib import Path
    tools_path = Path(__file__).parent
    if str(tools_path) not in sys.path:
        sys.path.insert(0, str(tools_path))
    try:
        from tools import JiraTools
        from confluence_tools import ConfluenceTools
    except ImportError as e:
        logger.error(f"Failed to import JiraTools and ConfluenceTools: {e}")
        raise

# MCP Protocol Constants
MCP_VERSION = "2024-11-05"


class CustomAtlassianMCPServer:
    """
    Custom MCP Server for Atlassian Jira and Confluence
    Implements MCP protocol over stdio following official MCP standards
    """
    
    def __init__(self):
        self.jira_tools = None
        self.confluence_tools = None
        self.initialized = False
        
    def initialize_tools(self, config: Dict):
        """Initialize Jira and Confluence tools from configuration"""
        try:
            # Initialize Jira tools if config provided
            if config.get('jira_url') and config.get('jira_email') and config.get('jira_token'):
                self.jira_tools = JiraTools(
                    jira_url=config['jira_url'],
                    email=config['jira_email'],
                    api_token=config['jira_token']
                )
                logger.info("Jira tools initialized successfully")
            
            # Initialize Confluence tools if config provided
            if config.get('confluence_url') and config.get('confluence_email') and config.get('confluence_token'):
                self.confluence_tools = ConfluenceTools(
                    confluence_url=config['confluence_url'],
                    email=config['confluence_email'],
                    api_token=config['confluence_token']
                )
                logger.info("Confluence tools initialized successfully")
            
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            return False
    
    def get_tools(self) -> List[Dict]:
        """Return list of available MCP tools"""
        tools = []
        
        # Jira Tools
        if self.jira_tools:
            tools.extend([
                {
                    "name": "jira_create_story",
                    "description": "Create a new Jira story with natural language description and acceptance criteria",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_key": {"type": "string", "description": "Jira project key"},
                            "summary": {"type": "string", "description": "Story summary"},
                            "description": {"type": "string", "description": "Detailed story description"},
                            "acceptance_criteria": {"type": "string", "description": "Acceptance criteria (optional)"},
                            "story_points": {"type": "integer", "description": "Story points estimate (optional)"},
                            "issue_type": {"type": "string", "description": "Issue type (Story, Bug, Task, etc.)", "default": "Story"}
                        },
                        "required": ["project_key", "summary", "description"]
                    }
                },
                {
                    "name": "jira_create_epic",
                    "description": "Create a new Jira epic with natural language description",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_key": {"type": "string", "description": "Jira project key"},
                            "summary": {"type": "string", "description": "Epic summary"},
                            "description": {"type": "string", "description": "Detailed epic description"},
                            "epic_name": {"type": "string", "description": "Epic name (optional)"}
                        },
                        "required": ["project_key", "summary", "description"]
                    }
                },
                {
                    "name": "jira_create_release",
                    "description": "Create a new Jira release/version",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_key": {"type": "string", "description": "Jira project key"},
                            "name": {"type": "string", "description": "Release name"},
                            "description": {"type": "string", "description": "Release description"},
                            "release_date": {"type": "string", "description": "Release date (YYYY-MM-DD, optional)"}
                        },
                        "required": ["project_key", "name", "description"]
                    }
                },
                {
                    "name": "jira_get_issue",
                    "description": "Get details of a Jira issue by key",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Jira issue key (e.g., PROJ-123)"}
                        },
                        "required": ["issue_key"]
                    }
                },
                {
                    "name": "jira_add_comment",
                    "description": "Add a comment to a Jira issue",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Jira issue key"},
                            "comment": {"type": "string", "description": "Comment text"}
                        },
                        "required": ["issue_key", "comment"]
                    }
                },
                {
                    "name": "jira_update_issue",
                    "description": "Update a Jira issue",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Jira issue key"},
                            "summary": {"type": "string", "description": "Updated summary (optional)"},
                            "description": {"type": "string", "description": "Updated description (optional)"},
                            "fields": {"type": "object", "description": "Additional fields to update (optional)"}
                        },
                        "required": ["issue_key"]
                    }
                },
                {
                    "name": "jira_search_issues",
                    "description": "Search for Jira issues using JQL",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "jql": {"type": "string", "description": "JQL query string"},
                            "max_results": {"type": "integer", "description": "Maximum number of results", "default": 50}
                        },
                        "required": ["jql"]
                    }
                },
                {
                    "name": "jira_create_sprint",
                    "description": "Create a new sprint in Jira",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "board_id": {"type": "integer", "description": "Jira board ID"},
                            "name": {"type": "string", "description": "Sprint name"},
                            "goal": {"type": "string", "description": "Sprint goal (optional)"},
                            "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD, optional)"},
                            "end_date": {"type": "string", "description": "End date (YYYY-MM-DD, optional)"}
                        },
                        "required": ["board_id", "name"]
                    }
                }
            ])
        
        # Confluence Tools
        if self.confluence_tools:
            tools.extend([
                {
                    "name": "confluence_create_page",
                    "description": "Create a new Confluence page",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "space_key": {"type": "string", "description": "Confluence space key"},
                            "title": {"type": "string", "description": "Page title"},
                            "content": {"type": "string", "description": "Page content (HTML or markdown)"},
                            "parent_id": {"type": "string", "description": "Parent page ID (optional)"}
                        },
                        "required": ["space_key", "title", "content"]
                    }
                },
                {
                    "name": "confluence_update_page",
                    "description": "Update an existing Confluence page",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "Confluence page ID"},
                            "title": {"type": "string", "description": "Updated title (optional)"},
                            "content": {"type": "string", "description": "Updated content (HTML or markdown)"},
                            "version": {"type": "integer", "description": "Page version number (required for update)"}
                        },
                        "required": ["page_id", "content", "version"]
                    }
                },
                {
                    "name": "confluence_get_page",
                    "description": "Get details of a Confluence page",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "Confluence page ID"}
                        },
                        "required": ["page_id"]
                    }
                },
                {
                    "name": "confluence_search_pages",
                    "description": "Search for Confluence pages",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query (CQL)"},
                            "space_key": {"type": "string", "description": "Space key to search in (optional)"},
                            "limit": {"type": "integer", "description": "Maximum number of results", "default": 25}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "confluence_get_comments",
                    "description": "Get comments for a Confluence page",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "Confluence page ID"}
                        },
                        "required": ["page_id"]
                    }
                },
                {
                    "name": "confluence_add_comment",
                    "description": "Add a comment to a Confluence page",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "Confluence page ID"},
                            "comment": {"type": "string", "description": "Comment text"}
                        },
                        "required": ["page_id", "comment"]
                    }
                }
            ])
        
        return tools
    
    async def handle_request(self, request: Dict) -> Dict:
        """Handle MCP protocol request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": MCP_VERSION,
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "custom-atlassian-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                tools = self.get_tools()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = await self.call_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call a specific tool with arguments"""
        try:
            # Jira Tools
            if tool_name == "jira_create_story" and self.jira_tools:
                result = self.jira_tools.create_story(
                    project_key=arguments["project_key"],
                    summary=arguments["summary"],
                    description=arguments["description"],
                    acceptance_criteria=arguments.get("acceptance_criteria"),
                    story_points=arguments.get("story_points"),
                    issue_type=arguments.get("issue_type", "Story")
                )
                return {"success": True, "data": result}
            
            elif tool_name == "jira_create_epic" and self.jira_tools:
                result = self.jira_tools.create_epic(
                    project_key=arguments["project_key"],
                    summary=arguments["summary"],
                    description=arguments["description"],
                    epic_name=arguments.get("epic_name")
                )
                return {"success": True, "data": result}
            
            elif tool_name == "jira_create_release" and self.jira_tools:
                result = self.jira_tools.create_release(
                    project_key=arguments["project_key"],
                    name=arguments["name"],
                    description=arguments["description"],
                    release_date=arguments.get("release_date")
                )
                return {"success": True, "data": result}
            
            elif tool_name == "jira_get_issue" and self.jira_tools:
                result = self.jira_tools.get_story(arguments["issue_key"])
                return {"success": True, "data": result}
            
            elif tool_name == "jira_add_comment" and self.jira_tools:
                result = self.jira_tools.add_comment(
                    issue_key=arguments["issue_key"],
                    comment=arguments["comment"]
                )
                return {"success": True, "data": result}
            
            elif tool_name == "jira_update_issue" and self.jira_tools:
                result = self.jira_tools.update_story(
                    issue_key=arguments["issue_key"],
                    summary=arguments.get("summary"),
                    description=arguments.get("description"),
                    **arguments.get("fields", {})
                )
                return {"success": True, "data": result}
            
            elif tool_name == "jira_search_issues" and self.jira_tools:
                # Build JQL with max results
                jql = arguments["jql"]
                max_results = arguments.get("max_results", 50)
                result = self.jira_tools.search_stories(jql)
                # Limit results
                if isinstance(result, list) and len(result) > max_results:
                    result = result[:max_results]
                return {"success": True, "data": result}
            
            elif tool_name == "jira_create_sprint" and self.jira_tools:
                result = self.jira_tools.create_sprint(
                    board_id=arguments["board_id"],
                    name=arguments["name"],
                    goal=arguments.get("goal"),
                    start_date=arguments.get("start_date"),
                    end_date=arguments.get("end_date")
                )
                return {"success": True, "data": result}
            
            # Confluence Tools
            elif tool_name == "confluence_create_page" and self.confluence_tools:
                result = self.confluence_tools.create_page(
                    space_key=arguments["space_key"],
                    title=arguments["title"],
                    content=arguments["content"],
                    parent_id=arguments.get("parent_id")
                )
                return {"success": True, "data": result}
            
            elif tool_name == "confluence_update_page" and self.confluence_tools:
                # update_page handles version retrieval internally if not provided
                result = self.confluence_tools.update_page(
                    page_id=arguments["page_id"],
                    title=arguments.get("title"),
                    content=arguments["content"],
                    version=arguments.get("version")
                )
                return {"success": True, "data": result}
            
            elif tool_name == "confluence_get_page" and self.confluence_tools:
                # Get page by ID using Confluence API
                try:
                    import requests
                    page_id = arguments["page_id"]
                    confluence_url = self.confluence_tools.confluence_url
                    headers = self.confluence_tools.headers
                    auth = self.confluence_tools.auth
                    
                    url = f"{confluence_url}/rest/api/content/{page_id}"
                    response = requests.get(
                        url,
                        headers=headers,
                        auth=auth,
                        params={"expand": "body.storage,version,space"}
                    )
                    response.raise_for_status()
                    result = response.json()
                    return {"success": True, "data": result}
                except Exception as e:
                    logger.error(f"Error getting Confluence page: {e}")
                    return {"success": False, "error": f"Failed to get page: {str(e)}"}
            
            elif tool_name == "confluence_search_pages" and self.confluence_tools:
                space_key = arguments.get("space_key")
                query = arguments["query"]
                limit = arguments.get("limit", 25)
                result = self.confluence_tools.search_pages(
                    space_key=space_key if space_key else "",
                    query=query,
                    limit=limit
                )
                return {"success": True, "data": result}
            
            elif tool_name == "confluence_get_comments" and self.confluence_tools:
                result = self.confluence_tools.get_page_comments(arguments["page_id"])
                return {"success": True, "data": result}
            
            elif tool_name == "confluence_add_comment" and self.confluence_tools:
                # Note: ConfluenceTools.get_page_comments exists but add_comment may need to be added
                # For now, we'll return a helpful error message
                return {
                    "success": False,
                    "error": "add_comment method needs to be implemented in ConfluenceTools class",
                    "message": "This functionality can be added to the ConfluenceTools class"
                }
            
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


async def main():
    """Main entry point for MCP server (stdio-based)"""
    server = CustomAtlassianMCPServer()
    
    # Read configuration from environment variables
    config = {
        "jira_url": os.getenv("JIRA_URL"),
        "jira_email": os.getenv("JIRA_EMAIL"),
        "jira_token": os.getenv("JIRA_API_TOKEN"),
        "confluence_url": os.getenv("CONFLUENCE_URL"),
        "confluence_email": os.getenv("CONFLUENCE_EMAIL"),
        "confluence_token": os.getenv("CONFLUENCE_API_TOKEN"),
    }
    
    # Initialize tools
    if not server.initialize_tools(config):
        logger.error("Failed to initialize tools")
        # Don't exit immediately - allow MCP client to handle initialization errors
        # sys.exit(1)
    
    # Read from stdin, write to stdout (MCP stdio protocol)
    # Use unbuffered I/O for real-time communication
    try:
        sys.stdin.reconfigure(encoding='utf-8')
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7 doesn't have reconfigure
        pass
    
    loop = asyncio.get_event_loop()
    
    while True:
        try:
            # Read line from stdin (blocking) - use executor to avoid blocking event loop
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            request = json.loads(line)
            response = await server.handle_request(request)
            
            # Write response to stdout
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error",
                    "data": str(e)
                }
            }
            print(json.dumps(error_response, ensure_ascii=False))
            sys.stdout.flush()
        
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
            break
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
            print(json.dumps(error_response, ensure_ascii=False))
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())

