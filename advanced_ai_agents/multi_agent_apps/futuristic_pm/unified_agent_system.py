"""
Unified Multi-Agent System for FuturisticPM
Integrates all agents (MCP, Self-Evolving, Agile Coach) with orchestration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from mcp_agents import MCPAgentManager, SelfEvolvingAgent, AgileCoachAgent
    from agent_orchestrator import AgentOrchestrator
    AGENTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Agent modules not available: {e}")
    AGENTS_AVAILABLE = False
    MCPAgentManager = None
    SelfEvolvingAgent = None
    AgileCoachAgent = None
    AgentOrchestrator = None


class UnifiedAgentSystem:
    """Unified system managing all agents and their interactions"""
    
    def __init__(self, openai_api_key: str):
        if not AGENTS_AVAILABLE:
            raise ImportError("Agent modules required")
        
        self.openai_api_key = openai_api_key
        self.orchestrator = AgentOrchestrator(openai_api_key)
        self.mcp_manager = None
        self.self_evolving_agent = None
        self.agile_coach_agent = None
        self.initialized = False
    
    async def initialize(self, config: Dict):
        """Initialize all agents"""
        try:
            # Initialize MCP agents
            if config.get('github_token') or config.get('jira_config') or config.get('confluence_config') or config.get('slack_config'):
                self.mcp_manager = MCPAgentManager(self.openai_api_key)
                mcp_config = {
                    'github_token': config.get('github_token'),
                    'jira_config': config.get('jira_config'),
                    'confluence_config': config.get('confluence_config'),
                    'slack_config': config.get('slack_config')
                }
                await self.mcp_manager.initialize_all_agents(mcp_config)
                
                # Register MCP agents with orchestrator
                for name, agent in self.mcp_manager.agents.items():
                    capabilities = self._get_agent_capabilities(name)
                    self.orchestrator.register_agent(name, agent, capabilities)
            
            # Initialize Self-Evolving Agent
            self.self_evolving_agent = SelfEvolvingAgent(self.openai_api_key)
            self.orchestrator.register_agent(
                'self_evolving',
                self.self_evolving_agent.agent,
                ['learning', 'adaptation', 'optimization', 'reflection']
            )
            
            # Initialize Agile Coach Agent
            self.agile_coach_agent = AgileCoachAgent(self.openai_api_key)
            self.orchestrator.register_agent(
                'agile_coach',
                self.agile_coach_agent.agent,
                ['sprint_planning', 'retrospectives', 'backlog_grooming', 'velocity_tracking', 'agile_metrics']
            )
            
            # Set up coordination rules
            self._setup_coordination_rules()
            
            self.initialized = True
            logger.info("Unified agent system initialized")
            
        except Exception as e:
            logger.error(f"Error initializing unified agent system: {e}")
            raise
    
    def _get_agent_capabilities(self, agent_name: str) -> List[str]:
        """Get capabilities for an agent"""
        capabilities_map = {
            'github': ['repository_management', 'issue_tracking', 'pull_requests', 'code_analysis'],
            'jira': ['epic_management', 'story_creation', 'sprint_planning', 'release_planning'],
            'confluence': ['page_creation', 'documentation', 'report_publishing', 'content_organization'],
            'slack': ['messaging', 'notifications', 'team_communication']
        }
        return capabilities_map.get(agent_name, [])
    
    def _setup_coordination_rules(self):
        """Set up agent coordination rules"""
        # Strategy agent -> Research agent
        self.orchestrator.add_coordination_rule('strategy', 'research')
        
        # Research agent -> Roadmap agent
        self.orchestrator.add_coordination_rule('research', 'roadmap')
        
        # Roadmap agent -> Metrics agent
        self.orchestrator.add_coordination_rule('roadmap', 'metrics')
        
        # Metrics agent -> Stakeholder agent
        self.orchestrator.add_coordination_rule('metrics', 'stakeholder')
        
        # Stakeholder agent -> Execution agent
        self.orchestrator.add_coordination_rule('stakeholder', 'execution')
        
        # Execution agent -> Jira agent (if available)
        if 'jira' in self.orchestrator.agents:
            self.orchestrator.add_coordination_rule('execution', 'jira')
        
        # Jira agent -> Confluence agent (if available)
        if 'jira' in self.orchestrator.agents and 'confluence' in self.orchestrator.agents:
            self.orchestrator.add_coordination_rule('jira', 'confluence')
        
        # Any agent can request agile coaching
        for agent_name in self.orchestrator.agents.keys():
            if agent_name != 'agile_coach':
                self.orchestrator.add_coordination_rule(
                    agent_name,
                    'agile_coach',
                    condition=lambda result, context: 'sprint' in result.lower() or 'agile' in result.lower() or 'scrum' in result.lower()
                )
    
    async def run_workflow_step(self, step_name: str, task: str, context: Dict = None) -> Dict:
        """Run a workflow step with agent coordination"""
        context = context or {}
        
        # Map step names to initial agents
        step_agent_map = {
            'Strategy': 'strategy',
            'Research': 'research',
            'Roadmap': 'roadmap',
            'Metrics': 'metrics',
            'Stakeholder': 'stakeholder',
            'Execution': 'execution'
        }
        
        initial_agent = step_agent_map.get(step_name)
        if not initial_agent or initial_agent not in self.orchestrator.agents:
            # Fallback: use first available agent
            initial_agent = list(self.orchestrator.agents.keys())[0] if self.orchestrator.agents else None
        
        if not initial_agent:
            raise ValueError("No agents available")
        
        # Coordinate agents for this step
        result = await self.orchestrator.coordinate_agents(initial_agent, task, context)
        
        return result
    
    async def get_agile_coaching(self, question: str, context: Dict = None) -> str:
        """Get agile coaching from Agile Coach Agent"""
        if not self.agile_coach_agent:
            return "Agile Coach Agent not available"
        
        return await self.agile_coach_agent.coach(question, context)
    
    async def evolve_from_feedback(self, feedback: str, context: Dict) -> str:
        """Evolve system based on feedback"""
        if not self.self_evolving_agent:
            return "Self-Evolving Agent not available"
        
        return await self.self_evolving_agent.evolve(feedback, context)
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        return self.orchestrator.get_agent_status()
    
    def get_interaction_history(self, limit: int = 20) -> List[Dict]:
        """Get recent interaction history"""
        return self.orchestrator.get_interaction_history(limit)
    
    async def close(self):
        """Close all agent connections"""
        if self.mcp_manager:
            await self.mcp_manager.close_all()
        self.initialized = False

