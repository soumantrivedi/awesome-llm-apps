"""
MCP Agent Implementations for FuturisticPM
Based on patterns from mcp_ai_agents/ folder
Uses Agno Agent framework with MCP tools for Jira, Confluence, GitHub, and Slack
"""

import asyncio
import os
import json
import logging
from typing import Dict, List, Optional, Any
from textwrap import dedent

logger = logging.getLogger(__name__)

# Try to import Agno Agent framework
try:
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    from agno.tools.mcp import MCPTools, MultiMCPTools
    from agno.db.sqlite import SqliteDb
    from mcp import StdioServerParameters
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False
    Agent = None
    OpenAIChat = None
    MCPTools = None
    MultiMCPTools = None
    SqliteDb = None
    StdioServerParameters = None
    logger.warning("Agno framework not available. Install: pip install agno")


class MCPAgentManager:
    """Manages MCP-based agents for Jira, Confluence, GitHub, and Slack"""
    
    def __init__(self, openai_api_key: str, db_file: str = "futuristic_pm_agents.db"):
        if not AGNO_AVAILABLE:
            raise ImportError("Agno framework required for MCP agents")
        
        self.openai_api_key = openai_api_key
        self.db = SqliteDb(db_file=db_file) if SqliteDb else None
        self.agents = {}
        self.mcp_tools = {}
        self._initialized = False
    
    async def initialize_github_agent(self, github_token: str, toolsets: str = "repos,issues,pull_requests"):
        """Initialize GitHub MCP agent"""
        try:
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={
                    **os.environ,
                    "GITHUB_PERSONAL_ACCESS_TOKEN": github_token,
                    "GITHUB_TOOLSETS": toolsets
                }
            )
            
            mcp_tools = MCPTools(server_params=server_params)
            await mcp_tools.__aenter__()
            self.mcp_tools['github'] = mcp_tools
            
            agent = Agent(
                name="GitHubAgent",
                model=OpenAIChat(id="gpt-4o", api_key=self.openai_api_key),
                tools=[mcp_tools],
                description="GitHub integration agent for repository management, issues, and pull requests",
                instructions=dedent("""
                    You are a GitHub expert agent with direct access to GitHub repositories through MCP tools.
                    
                    Your capabilities:
                    - Repository management: search, create, clone, fork repositories
                    - Issue management: create, update, comment on, and close issues
                    - Pull request workflow: create, review, merge PRs
                    - Code analysis: search code, review diffs, analyze commits
                    - Branch management: create, switch, merge branches
                    - Collaboration: manage teams, reviews, project workflows
                    
                    Always use MCP tools for GitHub operations. Provide clear, actionable insights.
                    Format responses in markdown with links to relevant GitHub pages.
                """),
                markdown=True,
                retries=3,
                db=self.db,
                enable_user_memories=True,
                add_history_to_context=True,
                num_history_runs=10
            )
            
            self.agents['github'] = agent
            logger.info("GitHub MCP agent initialized")
            return agent
        except Exception as e:
            logger.error(f"Failed to initialize GitHub agent: {e}")
            raise
    
    async def initialize_jira_agent(self, jira_config: Dict):
        """Initialize Jira MCP agent using official Atlassian Remote MCP Server (SSE/OAuth 2.0)"""
        try:
            # Official Atlassian Remote MCP Server uses SSE (Server-Sent Events)
            # Endpoint: https://mcp.atlassian.com/v1/sse
            # Authentication: OAuth 2.0
            
            oauth_access_token = jira_config.get('oauth_access_token')
            oauth_client_id = jira_config.get('oauth_client_id')
            oauth_client_secret = jira_config.get('oauth_client_secret')
            
            has_mcp = False
            
            if oauth_access_token:
                # Use official Atlassian Remote MCP Server (SSE)
                # Note: SSE-based MCP servers require special client implementation
                # For now, we'll prepare the configuration
                # The actual SSE connection will be handled by the MCP client library
                try:
                    # Store OAuth credentials
                    env = {
                        **os.environ,
                        "ATLASSIAN_ACCESS_TOKEN": oauth_access_token,
                        "ATLASSIAN_CLIENT_ID": oauth_client_id or '',
                        "ATLASSIAN_CLIENT_SECRET": oauth_client_secret or '',
                        "ATLASSIAN_SITE_URL": jira_config.get('url', '').replace('https://', '').replace('.atlassian.net', ''),
                    }
                    
                    # For SSE-based remote MCP servers, we need to use a different approach
                    # The MCP client should support SSE endpoints
                    # This is a placeholder - actual implementation depends on MCP client library support
                    logger.info("Atlassian Remote MCP Server (SSE) configured - OAuth token provided")
                    has_mcp = True
                    self.mcp_tools['jira'] = None  # Will be initialized when SSE support is available
                except Exception as e:
                    logger.warning(f"Atlassian Remote MCP Server setup failed: {e}")
                    has_mcp = False
            else:
                # Fallback: Use API token credentials (direct API, not MCP)
                env = {
                    **os.environ,
                    "JIRA_URL": jira_config.get('url', ''),
                    "JIRA_EMAIL": jira_config.get('email', ''),
                    "JIRA_API_TOKEN": jira_config.get('token', ''),
                    "JIRA_PROJECT_KEY": jira_config.get('project_key', ''),
                }
                has_mcp = False
                logger.info("Using direct API fallback for Jira (OAuth token not provided)")
            
            # Prepare tools list
            tools_list = []
            if has_mcp and self.mcp_tools.get('jira'):
                tools_list.append(self.mcp_tools['jira'])
            elif has_mcp:
                # SSE-based MCP server - tools will be available via remote connection
                # Note: This requires MCP client library support for SSE
                pass
            
            agent = Agent(
                name="JiraAgent",
                model=OpenAIChat(id="gpt-4o", api_key=self.openai_api_key),
                tools=tools_list,
                description="Jira integration agent for epics, stories, sprints, and releases using official Atlassian Remote MCP Server",
                instructions=dedent(f"""
                    You are a Jira expert agent for product management.
                    
                    **MCP Integration**: You have access to Jira through the official Atlassian Remote MCP Server.
                    This server uses OAuth 2.0 authentication and provides secure access to Jira operations.
                    
                    Your capabilities:
                    - Epic management: create, update, link epics
                    - Story creation: create user stories with natural, conversational acceptance criteria
                    - Sprint planning: create sprints, manage capacity, assign stories
                    - Release planning: create releases and link stories
                    - Issue tracking: update status, add comments, modify scope
                    - Search and query: search issues, filter by criteria
                    
                    **CRITICAL**: Write all content in natural, easy-to-understand language.
                    Avoid AI-generated sounding text. Make acceptance criteria clear and actionable.
                    
                    Project: {jira_config.get('project_key', 'N/A')}
                    Board ID: {jira_config.get('board_id', 'N/A')}
                    Site: {jira_config.get('url', 'N/A')}
                """),
                markdown=True,
                retries=3,
                db=self.db,
                enable_user_memories=True,
                add_history_to_context=True,
                num_history_runs=10
            )
            
            self.agents['jira'] = agent
            logger.info("Jira agent initialized")
            return agent
        except Exception as e:
            logger.error(f"Failed to initialize Jira agent: {e}")
            raise
    
    async def initialize_confluence_agent(self, confluence_config: Dict):
        """Initialize Confluence MCP agent using official Atlassian Remote MCP Server (SSE/OAuth 2.0)"""
        try:
            # Official Atlassian Remote MCP Server uses SSE (Server-Sent Events)
            # Same server handles both Jira and Confluence
            # Endpoint: https://mcp.atlassian.com/v1/sse
            # Authentication: OAuth 2.0
            
            oauth_access_token = confluence_config.get('oauth_access_token')
            oauth_client_id = confluence_config.get('oauth_client_id')
            oauth_client_secret = confluence_config.get('oauth_client_secret')
            
            has_mcp = False
            
            if oauth_access_token:
                # Use official Atlassian Remote MCP Server (SSE)
                try:
                    env = {
                        **os.environ,
                        "ATLASSIAN_ACCESS_TOKEN": oauth_access_token,
                        "ATLASSIAN_CLIENT_ID": oauth_client_id or '',
                        "ATLASSIAN_CLIENT_SECRET": oauth_client_secret or '',
                        "ATLASSIAN_SITE_URL": confluence_config.get('url', '').replace('https://', '').replace('.atlassian.net/wiki', '').replace('.atlassian.net', ''),
                        "CONFLUENCE_SPACE": confluence_config.get('space', ''),
                    }
                    
                    logger.info("Atlassian Remote MCP Server (SSE) configured for Confluence - OAuth token provided")
                    has_mcp = True
                    self.mcp_tools['confluence'] = None  # Will be initialized when SSE support is available
                except Exception as e:
                    logger.warning(f"Atlassian Remote MCP Server setup failed: {e}")
                    has_mcp = False
            else:
                # Fallback: Use API token credentials (direct API, not MCP)
                env = {
                    **os.environ,
                    "CONFLUENCE_URL": confluence_config.get('url', ''),
                    "CONFLUENCE_EMAIL": confluence_config.get('email', ''),
                    "CONFLUENCE_API_TOKEN": confluence_config.get('token', ''),
                    "CONFLUENCE_SPACE": confluence_config.get('space', ''),
                }
                has_mcp = False
                logger.info("Using direct API fallback for Confluence (OAuth token not provided)")
            
            # Prepare tools list
            tools_list = []
            if has_mcp and self.mcp_tools.get('confluence'):
                tools_list.append(self.mcp_tools['confluence'])
            elif has_mcp:
                # SSE-based MCP server - tools will be available via remote connection
                pass
            
            agent = Agent(
                name="ConfluenceAgent",
                model=OpenAIChat(id="gpt-4o", api_key=self.openai_api_key),
                tools=tools_list,
                description="Confluence integration agent for publishing documents and reports using official Atlassian Remote MCP Server",
                instructions=dedent(f"""
                    You are a Confluence expert agent for documentation and knowledge management.
                    
                    **MCP Integration**: You have access to Confluence through the official Atlassian Remote MCP Server.
                    This server uses OAuth 2.0 authentication and provides secure access to Confluence operations.
                    
                    Your capabilities:
                    - Page creation: create well-structured wiki pages
                    - Nested structures: organize content hierarchically
                    - Formatting: use Confluence wiki markup effectively
                    - Content organization: create index pages, link related content
                    - Report publishing: publish sprint reports, retrospectives, planning docs
                    - Search and query: search pages, find content
                    - Comments: add comments to pages, respond to feedback
                    
                    Space: {confluence_config.get('space', 'N/A')}
                    Site: {confluence_config.get('url', 'N/A')}
                    
                    Always create clear, well-organized documentation that's easy to navigate.
                """),
                markdown=True,
                retries=3,
                db=self.db,
                enable_user_memories=True,
                add_history_to_context=True,
                num_history_runs=10
            )
            
            self.agents['confluence'] = agent
            logger.info("Confluence agent initialized")
            return agent
        except Exception as e:
            logger.error(f"Failed to initialize Confluence agent: {e}")
            raise
    
    async def initialize_slack_agent(self, slack_config: Dict):
        """Initialize Slack MCP agent"""
        try:
            if not slack_config.get('bot_token'):
                logger.warning("Slack bot token not provided, skipping Slack MCP agent")
                return None
            
            env = {
                **os.environ,
                "SLACK_BOT_TOKEN": slack_config.get('bot_token', ''),
                "SLACK_TEAM_ID": slack_config.get('team_id', ''),
            }
            
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-slack"],
                env=env
            )
            
            mcp_tools = MCPTools(server_params=server_params)
            await mcp_tools.__aenter__()
            self.mcp_tools['slack'] = mcp_tools
            
            agent = Agent(
                name="SlackAgent",
                model=OpenAIChat(id="gpt-4o", api_key=self.openai_api_key),
                tools=[mcp_tools],
                description="Slack integration agent for team communication and notifications",
                instructions=dedent("""
                    You are a Slack expert agent for team communication.
                    
                    Your capabilities:
                    - Channel messaging: send messages to channels
                    - Direct messages: send DMs to users
                    - User management: get user information
                    - Channel management: list channels, get channel info
                    - Notifications: send important updates and alerts
                    
                    Always be professional and concise in communications.
                    Use appropriate formatting and mentions when needed.
                """),
                markdown=True,
                retries=3,
                db=self.db,
                enable_user_memories=True,
                add_history_to_context=True,
                num_history_runs=10
            )
            
            self.agents['slack'] = agent
            logger.info("Slack MCP agent initialized")
            return agent
        except Exception as e:
            logger.error(f"Failed to initialize Slack agent: {e}")
            return None
    
    async def initialize_all_agents(self, config: Dict):
        """Initialize all configured MCP agents"""
        tasks = []
        
        if config.get('github_token'):
            tasks.append(self.initialize_github_agent(config['github_token']))
        
        if config.get('jira_config'):
            tasks.append(self.initialize_jira_agent(config['jira_config']))
        
        if config.get('confluence_config'):
            tasks.append(self.initialize_confluence_agent(config['confluence_config']))
        
        if config.get('slack_config'):
            tasks.append(self.initialize_slack_agent(config['slack_config']))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            self._initialized = True
            logger.info(f"Initialized {len(self.agents)} MCP agents")
    
    async def close_all(self):
        """Close all MCP connections"""
        for name, mcp_tool in self.mcp_tools.items():
            if mcp_tool:
                try:
                    await mcp_tool.__aexit__(None, None, None)
                except Exception as e:
                    logger.error(f"Error closing {name} MCP connection: {e}")
        self.agents = {}
        self.mcp_tools = {}
        self._initialized = False
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    async def run_agent(self, agent_name: str, message: str, user_id: str = None, session_id: str = None) -> str:
        """Run an agent with a message"""
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")
        
        if user_id is None:
            import uuid
            user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        if session_id is None:
            import uuid
            session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        try:
            response = await agent.arun(message)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error running agent {agent_name}: {e}")
            raise


class SelfEvolvingAgent:
    """Self-evolving agent that learns and improves from interactions"""
    
    def __init__(self, openai_api_key: str, db_file: str = "futuristic_pm_evolution.db"):
        if not AGNO_AVAILABLE:
            raise ImportError("Agno framework required")
        
        self.openai_api_key = openai_api_key
        self.db = SqliteDb(db_file=db_file) if SqliteDb else None
        
        self.agent = Agent(
            name="SelfEvolvingAgent",
            model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
            description="Self-evolving agent that learns and improves from interactions",
            instructions=dedent("""
                You are a self-evolving AI agent that learns and improves from every interaction.
                
                Your core capabilities:
                1. **Learning**: Analyze past interactions to identify patterns and improvements
                2. **Adaptation**: Adjust your approach based on feedback and outcomes
                3. **Optimization**: Continuously refine your strategies and methods
                4. **Reflection**: Critically evaluate your own performance
                5. **Evolution**: Propose and implement improvements to your own capabilities
                
                Learning principles:
                - Track what works well and what doesn't
                - Identify common patterns in successful interactions
                - Learn from user feedback and corrections
                - Adapt communication style to user preferences
                - Improve accuracy and relevance over time
                
                Always reflect on your responses and suggest improvements.
                Be proactive in learning from each interaction.
            """),
            markdown=True,
            retries=3,
            db=self.db,
            enable_user_memories=True,
            add_history_to_context=True,
            num_history_runs=20  # More history for learning
        )
    
    async def evolve(self, feedback: str, context: Dict) -> str:
        """Evolve based on feedback"""
        evolution_prompt = f"""
        Based on the following feedback and context, analyze how to improve:
        
        Feedback: {feedback}
        Context: {json.dumps(context, indent=2)}
        
        Provide:
        1. Analysis of what went well and what didn't
        2. Specific improvements to make
        3. Updated approach for future interactions
        """
        
        response = await self.agent.arun(evolution_prompt)
        return response.content if hasattr(response, 'content') else str(response)


class AgileCoachAgent:
    """Specialized agile coach agent for Scrum, Kanban, and agile practices"""
    
    def __init__(self, openai_api_key: str, db_file: str = "futuristic_pm_agile.db"):
        if not AGNO_AVAILABLE:
            raise ImportError("Agno framework required")
        
        self.openai_api_key = openai_api_key
        self.db = SqliteDb(db_file=db_file) if SqliteDb else None
        
        self.agent = Agent(
            name="AgileCoachAgent",
            model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
            description="Agile coach agent specializing in Scrum, Kanban, and agile methodologies",
            instructions=dedent("""
                You are an expert Agile Coach with deep knowledge of Scrum, Kanban, SAFe, and other agile frameworks.
                
                Your expertise includes:
                1. **Sprint Planning**: Facilitate effective sprint planning sessions
                2. **Daily Standups**: Guide daily scrum meetings and identify blockers
                3. **Sprint Reviews**: Help conduct meaningful sprint reviews
                4. **Retrospectives**: Facilitate productive retrospectives with actionable insights
                5. **Backlog Grooming**: Guide backlog refinement and prioritization
                6. **Velocity Tracking**: Analyze team velocity and capacity
                7. **Agile Metrics**: Track and interpret agile metrics (burndown, velocity, etc.)
                8. **Team Coaching**: Help teams improve their agile practices
                9. **Scaling Agile**: Guide scaling efforts for larger organizations
                
                Best practices you promote:
                - User story format (As a... I want... So that...)
                - INVEST criteria for user stories
                - Definition of Done
                - Sprint goals and objectives
                - Continuous improvement mindset
                - Cross-functional collaboration
                
                Always provide practical, actionable advice based on agile principles.
            """),
            markdown=True,
            retries=3,
            db=self.db,
            enable_user_memories=True,
            add_history_to_context=True,
            num_history_runs=15
        )
    
    async def coach(self, question: str, context: Dict = None) -> str:
        """Provide agile coaching"""
        context_str = json.dumps(context, indent=2) if context else "No additional context"
        
        coaching_prompt = f"""
        As an agile coach, provide guidance on:
        
        Question/Topic: {question}
        Context: {context_str}
        
        Provide:
        1. Direct answer to the question
        2. Best practices and principles
        3. Practical examples or templates
        4. Common pitfalls to avoid
        5. Actionable next steps
        """
        
        response = await self.agent.arun(coaching_prompt)
        return response.content if hasattr(response, 'content') else str(response)

