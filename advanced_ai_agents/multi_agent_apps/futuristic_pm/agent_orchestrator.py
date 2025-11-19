"""
Agent Orchestrator for FuturisticPM
Manages multi-agent interactions and coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from agno.agent import Agent  # type: ignore
    from agno.models.openai import OpenAIChat  # type: ignore
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False
    Agent = None  # type: ignore
    OpenAIChat = None  # type: ignore


class AgentOrchestrator:
    """Orchestrates interactions between multiple agents"""
    
    def __init__(self, openai_api_key: str):
        if not AGNO_AVAILABLE:
            raise ImportError("Agno framework required")
        
        self.openai_api_key = openai_api_key
        self.agents = {}
        self.interaction_history = []
        self.coordination_rules = {}
    
    def register_agent(self, name: str, agent: Agent, capabilities: List[str] = None):
        """Register an agent with the orchestrator"""
        self.agents[name] = {
            'agent': agent,
            'capabilities': capabilities or [],
            'status': 'idle',
            'interactions': 0
        }
        logger.info(f"Registered agent: {name}")
    
    def add_coordination_rule(self, trigger_agent: str, target_agent: str, condition: Callable = None):
        """Add a rule for agent coordination"""
        if trigger_agent not in self.coordination_rules:
            self.coordination_rules[trigger_agent] = []
        
        self.coordination_rules[trigger_agent].append({
            'target': target_agent,
            'condition': condition
        })
    
    async def coordinate_agents(self, initial_agent: str, message: str, context: Dict = None) -> Dict:
        """Coordinate multiple agents to solve a task"""
        if initial_agent not in self.agents:
            raise ValueError(f"Agent '{initial_agent}' not registered")
        
        context = context or {}
        results = {}
        visited_agents = set()
        agent_queue = [(initial_agent, message, context)]
        
        while agent_queue:
            agent_name, task, current_context = agent_queue.pop(0)
            
            if agent_name in visited_agents:
                continue
            
            visited_agents.add(agent_name)
            agent_info = self.agents[agent_name]
            agent = agent_info['agent']
            
            # Update agent status
            agent_info['status'] = 'working'
            agent_info['interactions'] += 1
            
            try:
                # Run agent
                full_task = f"{task}\n\nContext: {self._format_context(current_context)}"
                response = await agent.arun(full_task)
                result = response.content if hasattr(response, 'content') else str(response)
                
                results[agent_name] = {
                    'result': result,
                    'timestamp': datetime.now().isoformat(),
                    'context_used': current_context
                }
                
                # Log interaction
                self.interaction_history.append({
                    'from': None,
                    'to': agent_name,
                    'message': task,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Check coordination rules
                if agent_name in self.coordination_rules:
                    for rule in self.coordination_rules[agent_name]:
                        should_coordinate = True
                        if rule['condition']:
                            should_coordinate = rule['condition'](result, current_context)
                        
                        if should_coordinate and rule['target'] not in visited_agents:
                            # Prepare handoff message
                            handoff_message = f"""
                            Previous agent ({agent_name}) completed their task:
                            
                            Result: {result[:500]}
                            
                            Please continue with the next phase of work.
                            """
                            agent_queue.append((rule['target'], handoff_message, {
                                **current_context,
                                f'{agent_name}_result': result
                            }))
                
                agent_info['status'] = 'idle'
                
            except Exception as e:
                logger.error(f"Error running agent {agent_name}: {e}")
                results[agent_name] = {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                agent_info['status'] = 'error'
        
        return {
            'results': results,
            'interaction_history': self.interaction_history[-10:],  # Last 10 interactions
            'agents_used': list(visited_agents)
        }
    
    def _format_context(self, context: Dict) -> str:
        """Format context for agent consumption"""
        if not context:
            return "No additional context"
        
        formatted = []
        for key, value in context.items():
            if isinstance(value, str):
                formatted.append(f"{key}: {value[:200]}")
            else:
                formatted.append(f"{key}: {value}")
        
        return "\n".join(formatted)
    
    async def parallel_agent_execution(self, tasks: Dict[str, str], context: Dict = None) -> Dict:
        """Execute multiple agents in parallel"""
        context = context or {}
        
        async def run_agent_task(agent_name, task):
            if agent_name not in self.agents:
                return agent_name, {'error': f"Agent '{agent_name}' not found"}
            
            agent_info = self.agents[agent_name]
            agent = agent_info['agent']
            agent_info['status'] = 'working'
            
            try:
                full_task = f"{task}\n\nContext: {self._format_context(context)}"
                response = await agent.arun(full_task)
                result = response.content if hasattr(response, 'content') else str(response)
                agent_info['status'] = 'idle'
                return agent_name, {'result': result, 'timestamp': datetime.now().isoformat()}
            except Exception as e:
                agent_info['status'] = 'error'
                return agent_name, {'error': str(e), 'timestamp': datetime.now().isoformat()}
        
        # Run all agents in parallel
        tasks_list = [run_agent_task(name, task) for name, task in tasks.items()]
        results = await asyncio.gather(*tasks_list)
        
        return {name: result for name, result in results}
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        return {
            name: {
                'status': info['status'],
                'interactions': info['interactions'],
                'capabilities': info['capabilities']
            }
            for name, info in self.agents.items()
        }
    
    def get_interaction_history(self, limit: int = 20) -> List[Dict]:
        """Get recent interaction history"""
        return self.interaction_history[-limit:]

