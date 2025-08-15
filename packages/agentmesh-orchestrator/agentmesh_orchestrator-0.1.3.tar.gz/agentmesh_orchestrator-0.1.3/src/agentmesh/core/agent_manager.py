"""Agent manager for creating and managing AutoGen agents."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

try:
    from autogen_core import MessageContext
    from autogen_agentchat import ChatAgent, AssistantAgent, UserProxyAgent
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    AUTOGEN_AVAILABLE = True
except ImportError:
    # Fallback for when AutoGen is not available
    AUTOGEN_AVAILABLE = False
    MessageContext = None
    ChatAgent = None
    AssistantAgent = None
    UserProxyAgent = None
    OpenAIChatCompletionClient = None

# AWS Bedrock support
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    boto3 = None
    BotoCoreError = None
    ClientError = None

from ..models.agent import (
    AgentConfig,
    AgentInfo,
    AgentType,
    AgentStatus,
    ModelProvider,
    AgentMetrics,
    generate_agent_id,
)

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages AutoGen agents with lifecycle operations."""

    def __init__(self):
        """Initialize the agent manager."""
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._metrics: Dict[str, AgentMetrics] = {}

    async def create_agent(self, config: AgentConfig) -> str:
        """Create a new agent with the given configuration.

        Args:
            config: Agent configuration

        Returns:
            Agent ID

        Raises:
            ValueError: If agent name already exists or configuration is invalid
        """
        # Validate configuration
        await self._validate_agent_config(config)

        # Check if agent name already exists
        for agent_id, agent_data in self.agents.items():
            if agent_data["info"].name == config.name:
                raise ValueError(f"Agent with name '{config.name}' already exists")

        # Generate unique agent ID
        agent_id = generate_agent_id()

        # Create agent info
        agent_info = AgentInfo(
            id=agent_id,
            name=config.name,
            type=config.type,
            status=AgentStatus.CREATED,
            model=config.model,
            provider=config.provider,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            config=config.config,
        )

        # Initialize metrics
        metrics = AgentMetrics(agent_id=agent_id)

        # Create the actual agent instance
        agent_instance = None
        if AUTOGEN_AVAILABLE:
            try:
                agent_instance = await self._create_autogen_agent(config)
            except Exception as e:
                logger.warning(f"Failed to create AutoGen agent: {e}")
                agent_instance = None

        # Store agent data
        self.agents[agent_id] = {
            "info": agent_info,
            "config": config,
            "instance": agent_instance,
            "metrics": metrics,
            "start_time": None,
        }

        self._metrics[agent_id] = metrics

        logger.info(f"Created agent {agent_id} ({config.name}) of type {config.type}")
        return agent_id

    async def _validate_agent_config(self, config: AgentConfig) -> None:
        """Validate agent configuration.

        Args:
            config: Agent configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate basic fields
        if not config.name or not config.name.strip():
            raise ValueError("Agent name cannot be empty")

        if len(config.name) > 100:
            raise ValueError("Agent name cannot exceed 100 characters")

        # Validate model provider specific requirements
        if config.provider == ModelProvider.OPENAI:
            if not config.model:
                raise ValueError("Model is required for OpenAI provider")
            
        elif config.provider == ModelProvider.BEDROCK:
            if not BEDROCK_AVAILABLE:
                raise ValueError("Bedrock is not available - boto3 not installed")
            if not config.model:
                raise ValueError("Model is required for Bedrock provider")
            # Could add more specific Bedrock model validation here
            
        elif config.provider == ModelProvider.AZURE_OPENAI:
            if not config.model:
                raise ValueError("Model is required for Azure OpenAI provider")
            # Could add Azure-specific validation here

        # Validate temperature range
        if config.temperature is not None and (config.temperature < 0 or config.temperature > 2):
            raise ValueError("Temperature must be between 0 and 2")

        # Validate max_tokens
        if config.max_tokens is not None and config.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

    async def _create_autogen_agent(self, config: AgentConfig) -> Optional[Any]:
        """Create an AutoGen agent instance.

        Args:
            config: Agent configuration

        Returns:
            AutoGen agent instance or None if creation fails
        """
        if not AUTOGEN_AVAILABLE:
            return None

        try:
            # Create model client
            model_client = None
            if config.provider == ModelProvider.OPENAI:
                model_client = OpenAIChatCompletionClient(
                    model=config.model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )
            elif config.provider == ModelProvider.BEDROCK and BEDROCK_AVAILABLE:
                model_client = await self._create_bedrock_client(config)
            elif config.provider == ModelProvider.AZURE_OPENAI:
                # TODO: Implement Azure OpenAI client
                logger.warning("Azure OpenAI not yet implemented")
                model_client = None
            else:
                logger.warning(f"Unsupported model provider: {config.provider}")

            # Create agent based on type
            if config.type == AgentType.ASSISTANT:
                agent = AssistantAgent(
                    name=config.name,
                    model_client=model_client,
                    system_message=config.system_message
                    or f"You are {config.name}, a helpful assistant.",
                )
            elif config.type == AgentType.USER_PROXY:
                agent = UserProxyAgent(
                    name=config.name,
                    system_message=config.system_message
                    or f"You are {config.name}, a user proxy agent.",
                )
            else:
                raise ValueError(f"Unsupported agent type: {config.type}")

            return agent

        except Exception as e:
            logger.error(f"Failed to create AutoGen agent: {e}")
            return None

    async def _create_bedrock_client(self, config: AgentConfig) -> Optional[Any]:
        """Create a Bedrock model client.

        Args:
            config: Agent configuration

        Returns:
            Bedrock client or None if creation fails
        """
        if not BEDROCK_AVAILABLE:
            logger.error("Bedrock is not available - boto3 not installed")
            return None

        try:
            # Create Bedrock client
            bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=config.config.get('aws_region', 'us-east-1'),
                aws_access_key_id=config.config.get('aws_access_key_id'),
                aws_secret_access_key=config.config.get('aws_secret_access_key'),
            )

            # TODO: Implement Bedrock model client wrapper for AutoGen
            # This would need to be implemented as a custom model client
            # that follows AutoGen's model client interface
            logger.warning("Bedrock model client wrapper not yet implemented")
            return None

        except Exception as e:
            logger.error(f"Failed to create Bedrock client: {e}")
            return None

    async def start_agent(self, agent_id: Union[str, UUID]) -> Optional[AgentInfo]:
        """Start an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Updated agent info or None if not found or failed

        Raises:
            ValueError: If agent not found
        """
        agent_id = self._normalize_agent_id(agent_id)
        if agent_id not in self.agents:
            return None

        agent_data = self.agents[agent_id]
        agent_info = agent_data["info"]

        if agent_info.status == AgentStatus.ACTIVE:
            return agent_info  # Already active

        # Update status
        agent_info.status = AgentStatus.STARTING
        agent_info.updated_at = datetime.now()

        try:
            # Start the agent (placeholder for actual start logic)
            await asyncio.sleep(0.1)  # Simulate startup time

            # Update status to active
            agent_info.status = AgentStatus.ACTIVE
            agent_info.last_active = datetime.now()
            agent_data["start_time"] = datetime.now()

            logger.info(f"Started agent {agent_id} ({agent_info.name})")
            return agent_info

        except Exception as e:
            agent_info.status = AgentStatus.ERROR
            logger.error(f"Failed to start agent {agent_id}: {e}")
            return None

    async def stop_agent(self, agent_id: Union[str, UUID]) -> Optional[AgentInfo]:
        """Stop an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Updated agent info or None if not found or failed

        Raises:
            ValueError: If agent not found
        """
        agent_id = self._normalize_agent_id(agent_id)
        if agent_id not in self.agents:
            return None

        agent_data = self.agents[agent_id]
        agent_info = agent_data["info"]

        if agent_info.status in [AgentStatus.STOPPED, AgentStatus.CREATED]:
            return agent_info  # Already stopped

        # Update status
        agent_info.status = AgentStatus.STOPPING
        agent_info.updated_at = datetime.now()

        try:
            # Stop the agent (placeholder for actual stop logic)
            await asyncio.sleep(0.1)  # Simulate shutdown time

            # Update status to stopped
            agent_info.status = AgentStatus.STOPPED

            # Update uptime if agent was running
            if agent_data["start_time"]:
                uptime = (datetime.now() - agent_data["start_time"]).total_seconds()
                agent_info.uptime_seconds += uptime
                agent_data["start_time"] = None

            logger.info(f"Stopped agent {agent_id} ({agent_info.name})")
            return agent_info

        except Exception as e:
            agent_info.status = AgentStatus.ERROR
            logger.error(f"Failed to stop agent {agent_id}: {e}")
            return None

    async def delete_agent(self, agent_id: Union[str, UUID]) -> bool:
        """Delete an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If agent not found
        """
        agent_id = self._normalize_agent_id(agent_id)
        if agent_id not in self.agents:
            return False

        agent_data = self.agents[agent_id]
        agent_info = agent_data["info"]

        # Stop agent first if running
        if agent_info.status == AgentStatus.ACTIVE:
            await self.stop_agent(agent_id)

        # Remove from storage
        del self.agents[agent_id]
        if agent_id in self._metrics:
            del self._metrics[agent_id]

        logger.info(f"Deleted agent {agent_id} ({agent_info.name})")
        return True

    async def get_agent(self, agent_id: Union[str, UUID]) -> AgentInfo:
        """Get agent information.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent information

        Raises:
            ValueError: If agent not found
        """
        agent_id = self._normalize_agent_id(agent_id)
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent_data = self.agents[agent_id]
        agent_info = agent_data["info"]

        # Update uptime for active agents
        if agent_info.status == AgentStatus.ACTIVE and agent_data["start_time"]:
            current_uptime = (datetime.now() - agent_data["start_time"]).total_seconds()
            agent_info.uptime_seconds = current_uptime

        return agent_info

    async def list_agents(
        self, 
        status_filter: Optional[AgentStatus] = None,
        agent_type: Optional[AgentType] = None,
        page: int = 1,
        size: int = 10
    ) -> List[AgentInfo]:
        """List agents with optional filtering and pagination.

        Args:
            status_filter: Optional status filter
            agent_type: Optional type filter
            page: Page number (1-based)
            size: Page size

        Returns:
            List of agent information
        """
        agents = []
        for agent_id, agent_data in self.agents.items():
            agent_info = agent_data["info"]

            # Update uptime for active agents
            if agent_info.status == AgentStatus.ACTIVE and agent_data["start_time"]:
                current_uptime = (
                    datetime.now() - agent_data["start_time"]
                ).total_seconds()
                agent_info.uptime_seconds = current_uptime

            # Apply filters
            if status_filter is not None and agent_info.status != status_filter:
                continue
            if agent_type is not None and agent_info.type != agent_type:
                continue

            agents.append(agent_info)

        # Sort by creation time
        agents = sorted(agents, key=lambda x: x.created_at)
        
        # Apply pagination
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        return agents[start_idx:end_idx]

    async def get_agent_by_name(self, name: str) -> Optional[AgentInfo]:
        """Get agent by name.

        Args:
            name: Agent name

        Returns:
            Agent information or None if not found
        """
        for agent_data in self.agents.values():
            if agent_data["info"].name == name:
                return agent_data["info"]
        return None

    async def get_agent_metrics(self, agent_id: str) -> AgentMetrics:
        """Get agent performance metrics.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent metrics

        Raises:
            ValueError: If agent not found
        """
        if agent_id not in self._metrics:
            raise ValueError(f"Agent {agent_id} not found")

        return self._metrics[agent_id]

    async def update_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update agent status.

        Args:
            agent_id: Agent identifier
            status: New status

        Raises:
            ValueError: If agent not found
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent_info = self.agents[agent_id]["info"]
        agent_info.status = status
        agent_info.updated_at = datetime.now()

        if status == AgentStatus.ACTIVE:
            agent_info.last_active = datetime.now()

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents.

        Returns:
            Health check results
        """
        total_agents = len(self.agents)
        active_agents = len(
            [a for a in self.agents.values() if a["info"].status == AgentStatus.ACTIVE]
        )
        error_agents = len(
            [a for a in self.agents.values() if a["info"].status == AgentStatus.ERROR]
        )

        return {
            "status": "healthy" if error_agents == 0 else "degraded",
            "total_agents": total_agents,
            "active_agents": active_agents,
            "error_agents": error_agents,
            "autogen_available": AUTOGEN_AVAILABLE,
            "bedrock_available": BEDROCK_AVAILABLE,
            "timestamp": datetime.now().isoformat(),
        }

    async def count_agents(
        self, 
        status_filter: Optional[AgentStatus] = None,
        agent_type: Optional[AgentType] = None
    ) -> int:
        """Count agents with optional filters.

        Args:
            status_filter: Optional status filter
            agent_type: Optional type filter

        Returns:
            Number of matching agents
        """
        count = 0
        for agent_data in self.agents.values():
            agent_info = agent_data["info"]
            
            # Apply filters
            if status_filter is not None and agent_info.status != status_filter:
                continue
            if agent_type is not None and agent_info.type != agent_type:
                continue
                
            count += 1
        return count

    async def update_agent(self, agent_id: Union[str, UUID], config: AgentConfig) -> Optional[AgentInfo]:
        """Update an agent's configuration.

        Args:
            agent_id: Agent identifier
            config: New configuration

        Returns:
            Updated agent info or None if not found
        """
        agent_id = self._normalize_agent_id(agent_id)
        if agent_id not in self.agents:
            return None

        agent_data = self.agents[agent_id]
        agent_info = agent_data["info"]

        # Update fields from config
        agent_info.name = config.name
        agent_info.type = config.type
        agent_info.model = config.model
        agent_info.provider = config.provider
        agent_info.config = config.config
        agent_info.updated_at = datetime.now()

        # Update the stored config
        agent_data["config"] = config

        # Recreate agent instance if needed
        if AUTOGEN_AVAILABLE:
            try:
                new_instance = await self._create_autogen_agent(config)
                agent_data["instance"] = new_instance
            except Exception as e:
                logger.warning(f"Failed to recreate AutoGen agent after update: {e}")

        return agent_info

    async def get_agent_status(self, agent_id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """Get detailed agent status information.

        Args:
            agent_id: Agent identifier

        Returns:
            Status information or None if not found
        """
        agent_id = self._normalize_agent_id(agent_id)
        if agent_id not in self.agents:
            return None

        agent_data = self.agents[agent_id]
        agent_info = agent_data["info"]

        # Update uptime for active agents
        current_uptime = 0
        if agent_info.status == AgentStatus.ACTIVE and agent_data["start_time"]:
            current_uptime = (datetime.now() - agent_data["start_time"]).total_seconds()

        return {
            "id": agent_info.id,
            "status": agent_info.status.value,
            "last_activity": agent_info.last_active.isoformat() if agent_info.last_active else None,
            "uptime_seconds": current_uptime,
            "created_at": agent_info.created_at.isoformat(),
            "updated_at": agent_info.updated_at.isoformat(),
        }

    def _normalize_agent_id(self, agent_id: Union[str, UUID]) -> str:
        """Normalize agent ID to string format."""
        if isinstance(agent_id, UUID):
            return str(agent_id)
        return agent_id

# Global agent manager instance
_agent_manager: Optional[AgentManager] = None


def get_agent_manager() -> AgentManager:
    """Get or create the global agent manager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager
