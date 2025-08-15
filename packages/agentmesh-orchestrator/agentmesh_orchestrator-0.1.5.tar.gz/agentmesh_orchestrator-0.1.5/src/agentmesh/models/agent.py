"""Agent models for AgentMesh."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Type of agent."""
    ASSISTANT = "assistant"
    USER_PROXY = "user_proxy"
    GROUP_CHAT = "group_chat"
    BEDROCK = "bedrock"


class AgentStatus(str, Enum):
    """Status of an agent."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TERMINATED = "terminated"


class ModelProvider(str, Enum):
    """Model provider for agents."""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    LOCAL = "local"
    CUSTOM = "custom"


class AgentConfig(BaseModel):
    """Configuration for creating an agent."""
    name: str = Field(..., description="Name of the agent")
    type: AgentType = Field(..., description="Type of agent")
    model: Optional[str] = Field(None, description="Model to use for the agent")
    system_message: Optional[str] = Field(None, description="System message for the agent")
    max_consecutive_auto_reply: Optional[int] = Field(None, description="Maximum consecutive auto replies")
    human_input_mode: Optional[str] = Field("NEVER", description="Human input mode")
    code_execution_config: Optional[Dict[str, Any]] = Field(None, description="Code execution configuration")
    llm_config: Optional[Dict[str, Any]] = Field(None, description="LLM configuration")
    description: Optional[str] = Field(None, description="Description of the agent")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class AgentInfo(BaseModel):
    """Information about an agent."""
    id: str = Field(..., description="Unique agent ID")
    name: str = Field(..., description="Name of the agent")
    type: AgentType = Field(..., description="Type of agent")
    status: AgentStatus = Field(..., description="Current status")
    model: Optional[str] = Field(None, description="Model being used")
    description: Optional[str] = Field(None, description="Description of the agent")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CreateAgentRequest(BaseModel):
    """Request model for creating an agent."""
    name: str = Field(..., description="Name of the agent")
    type: AgentType = Field(..., description="Type of agent")
    model: Optional[str] = Field(None, description="Model to use for the agent")
    system_message: Optional[str] = Field(None, description="System message for the agent")
    max_consecutive_auto_reply: Optional[int] = Field(None, description="Maximum consecutive auto replies")
    human_input_mode: Optional[str] = Field("NEVER", description="Human input mode")
    code_execution_config: Optional[Dict[str, Any]] = Field(None, description="Code execution configuration")
    llm_config: Optional[Dict[str, Any]] = Field(None, description="LLM configuration")
    description: Optional[str] = Field(None, description="Description of the agent")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class UpdateAgentRequest(BaseModel):
    """Request model for updating an agent."""
    name: Optional[str] = Field(None, description="Name of the agent")
    type: Optional[AgentType] = Field(None, description="Type of agent")
    model: Optional[str] = Field(None, description="Model to use for the agent")
    system_message: Optional[str] = Field(None, description="System message for the agent")
    max_consecutive_auto_reply: Optional[int] = Field(None, description="Maximum consecutive auto replies")
    human_input_mode: Optional[str] = Field(None, description="Human input mode")
    code_execution_config: Optional[Dict[str, Any]] = Field(None, description="Code execution configuration")
    llm_config: Optional[Dict[str, Any]] = Field(None, description="LLM configuration")
    description: Optional[str] = Field(None, description="Description of the agent")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AgentMessage(BaseModel):
    """Message sent by an agent."""
    id: Optional[str] = Field(None, description="Message ID")
    content: str = Field(..., description="Message content")
    role: str = Field(..., description="Role of the sender")
    name: Optional[str] = Field(None, description="Name of the sender")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentResponse(BaseModel):
    """Response from an agent."""
    agent_id: str = Field(..., description="ID of the responding agent")
    message: AgentMessage = Field(..., description="Response message")
    status: AgentStatus = Field(..., description="Agent status after response")
    execution_time: Optional[float] = Field(None, description="Time taken to generate response")


class AgentMetrics(BaseModel):
    """Metrics for an agent."""
    id: str = Field(..., description="Agent ID")
    total_messages: int = Field(0, description="Total messages processed")
    successful_responses: int = Field(0, description="Successful responses")
    failed_responses: int = Field(0, description="Failed responses")
    average_response_time: float = Field(0.0, description="Average response time in seconds")
    total_tokens_consumed: int = Field(0, description="Total tokens consumed")
    uptime_seconds: float = Field(0.0, description="Total uptime in seconds")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    error_rate: float = Field(0.0, description="Error rate percentage")
    throughput: float = Field(0.0, description="Messages per second")


def generate_agent_id() -> str:
    """Generate a unique agent ID."""
    return f"agent_{uuid4().hex[:8]}"
