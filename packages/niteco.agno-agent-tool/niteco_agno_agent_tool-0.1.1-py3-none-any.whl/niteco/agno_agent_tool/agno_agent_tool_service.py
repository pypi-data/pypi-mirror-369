"""
AgnoAgentToolService - A service that manages and executes agno agents.
"""

# Standard library imports
import logging
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

# Third-party imports
from fastapi import FastAPI, Request, HTTPException, Path, Query
from agno.agent import Agent

# OPAL SDK imports
from opal_tools_sdk import ToolsService
from opal_tools_sdk.models import Parameter, ParameterType
from pydantic import BaseModel

# Local imports


class AgentRunRequest(BaseModel):
    """Request model for running an agent."""
    message: str


class AgentToolConfig(BaseModel):
    """Configuration for AgnoAgentToolService."""
    auth_config: Optional[Dict[str, Any]] = None
    endpoint_prefix: str = "/agents"


logger = logging.getLogger(__name__)


class AgentToolRegistry:
    """Registry for managing agno agents directly."""
    
    def __init__(self):
        self._agent_instances: Dict[str, Agent] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
    
    def register_agent(self, agent: Agent, interaction_guidelines: Optional[str] = None) -> None:
        """Register an agent instance directly.
        
        Args:
            agent: The agent instance to register
            interaction_guidelines: Optional guidelines for interacting with the agent.
                                  If not provided, falls back to agent description.
        """
        self._agent_instances[agent.agent_id] = agent
        # Store interaction guidelines for later use
        if not hasattr(self, '_agent_guidelines'):
            self._agent_guidelines: Dict[str, str] = {}
        self._agent_guidelines[agent.agent_id] = interaction_guidelines or agent.description or "No interaction guidelines available"
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent."""
        if agent_id not in self._agent_instances:
            return False
        
        # Clean up running tasks
        if agent_id in self._running_tasks:
            task = self._running_tasks[agent_id]
            if not task.done():
                task.cancel()
            del self._running_tasks[agent_id]
        
        del self._agent_instances[agent_id]
        # Clean up guidelines if they exist
        if hasattr(self, '_agent_guidelines') and agent_id in self._agent_guidelines:
            del self._agent_guidelines[agent_id]
        return True
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self._agent_instances.get(agent_id)
    
    def get_agent_guidelines(self, agent_id: str) -> Optional[str]:
        """Get interaction guidelines for an agent."""
        if hasattr(self, '_agent_guidelines'):
            return self._agent_guidelines.get(agent_id)
        return None
    
    
    def list_all_agents(self) -> List[Agent]:
        """Get all registered agents."""
        return list(self._agent_instances.values())
    
    def list_all_agent_ids(self) -> List[str]:
        """Get all registered agent IDs."""
        return list(self._agent_instances.keys())
    
    def clear(self) -> None:
        """Clear all registered agents."""
        # Cancel running tasks
        for task in self._running_tasks.values():
            if not task.done():
                task.cancel()
        
        self._agent_instances.clear()
        self._running_tasks.clear()
        # Clear guidelines if they exist
        if hasattr(self, '_agent_guidelines'):
            self._agent_guidelines.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_agents": len(self._agent_instances),
            "running_tasks": len(self._running_tasks)
        }
    
    
    
    def add_running_task(self, run_id: str, task: asyncio.Task) -> None:
        """Track a running agent task."""
        self._running_tasks[run_id] = task
    
    def remove_running_task(self, run_id: str) -> Optional[asyncio.Task]:
        """Remove and return a running task."""
        return self._running_tasks.pop(run_id, None)
    


class AgnoAgentToolService(ToolsService):
    """
    Extended ToolsService that can manage and execute agno agents.
    
    Features:
    - Agent registry with discovery endpoint
    - Agent execution with run endpoint
    - Health monitoring and metrics
    """
    
    def __init__(self, app: FastAPI, config: Optional[AgentToolConfig] = None):
        """
        Initialize the Agno agent tool service.
        
        Args:
            app: FastAPI application to attach routes to
            config: Configuration object for the service
        """
        super().__init__(app)
        self.config = config or AgentToolConfig()
        self.auth_config = self.config.auth_config
        self.endpoint_prefix = self.config.endpoint_prefix.rstrip("/")  # Remove trailing slash for consistency
        self.registry = AgentToolRegistry()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._startup_time: Optional[datetime] = None
    
    
    def register_agent(self, agent: Agent, interaction_guidelines: Optional[str] = None) -> None:
        """Register a new agent.
        
        Args:
            agent: The agent instance to register
            interaction_guidelines: Optional guidelines for interacting with the agent.
                                  If not provided, falls back to agent description.
        """
        self.registry.register_agent(agent, interaction_guidelines)
        
        # Use interaction guidelines or fallback to agent description for tool description
        guidelines = interaction_guidelines or agent.description or "No description"
        
        # Register as a tool in ToolsService
        self.register_tool(
            name=f"ask_{agent.agent_id}",
            description=f"Hi, I am {agent.name}. {guidelines}",
            handler=self._create_agent_handler(agent),
            parameters=[
                Parameter(
                    name="message",
                    param_type=ParameterType.string,
                    description="Message to send to the agent",
                    required=True
                )
            ],
            endpoint=f"{self.endpoint_prefix}/{agent.agent_id}/run"
        )
        
        self.logger.info(f"Registered agent: {agent.agent_id}")
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent."""
        result = self.registry.unregister_agent(agent_id)
        if result:
            self.logger.info(f"Unregistered agent: {agent_id}")
        return result
    
    def get_agent_guidelines(self, agent_id: str) -> Optional[str]:
        """Get interaction guidelines for an agent."""
        return self.registry.get_agent_guidelines(agent_id)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health and statistics."""
        registry_stats = self.registry.get_stats()
        
        return {
            "status": "healthy",
            "startup_time": self._startup_time.isoformat() if self._startup_time else None,
            "uptime_seconds": (datetime.now() - self._startup_time).total_seconds() if self._startup_time else 0,
            "auth_enabled": self.auth_config is not None,
            "registry_stats": registry_stats
        }
    
    # Lifecycle Management
    async def startup(self) -> None:
        """Initialize service resources."""
        self._startup_time = datetime.now()
        self.logger.info("AgnoAgentToolService starting up")
        
        self.logger.info("AgnoAgentToolService startup completed")
    
    async def shutdown(self) -> None:
        """Cleanup service resources."""
        self.logger.info("AgnoAgentToolService shutting down")
        
        # Clear registry (will cancel running tasks)
        self.registry.clear()
        
        self.logger.info("AgnoAgentToolService shutdown completed")
    
    def _create_agent_handler(self, agent: Agent):
        """Create a handler function for an agent."""
        async def handler(request: AgentRunRequest) -> Dict[str, Any]:
            try:
                response = await agent.arun(request.message)
                # Extract content from RunResponse object
                content = response.content if hasattr(response, 'content') else str(response)
                return {"response": content}
            except Exception as e:
                self.logger.error(f"Error running agent {agent.agent_id}: {e}")
                return {"error": str(e)}
        
        return handler


# Factory Functions
def create_agno_agent_service(
    app: FastAPI, 
    config: Optional[AgentToolConfig] = None,
    auth_config: Optional[Dict[str, Any]] = None, 
    endpoint_prefix: str = "/agents"
) -> AgnoAgentToolService:
    """
    Create AgnoAgentToolService with configuration.
    
    Args:
        app: FastAPI application
        config: Configuration object (preferred method)
        auth_config: Optional authentication configuration (legacy, use config instead)
        endpoint_prefix: Prefix for agent endpoints (legacy, use config instead)
        
    Returns:
        Configured AgnoAgentToolService instance
    """
    # If config is provided, use it; otherwise create from legacy parameters
    if config is None:
        config = AgentToolConfig(
            auth_config=auth_config,
            endpoint_prefix=endpoint_prefix
        )
    
    service = AgnoAgentToolService(app, config)
    return service