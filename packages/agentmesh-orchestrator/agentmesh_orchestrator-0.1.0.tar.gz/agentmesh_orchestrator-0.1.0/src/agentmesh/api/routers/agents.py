"""Agent management API endpoints."""

from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ...core.agent_manager import AgentManager, get_agent_manager
from ...models.agent import (
    AgentConfig,
    AgentInfo,
    AgentStatus,
    AgentType,
    CreateAgentRequest,
    UpdateAgentRequest,
)

router = APIRouter()


class AgentListResponse(BaseModel):
    """Response model for agent list."""
    
    agents: List[AgentInfo]
    total: int
    page: int
    size: int


class AgentResponse(BaseModel):
    """Response model for single agent."""
    
    agent: AgentInfo


@router.post(
    "",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Agent",
    description="Create a new agent in the system"
)
async def create_agent(
    request: CreateAgentRequest,
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgentResponse:
    """Create a new agent."""
    try:
        agent_id = await agent_manager.create_agent(request.to_config())
        agent_info = await agent_manager.get_agent(agent_id)
        if not agent_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent created but could not be retrieved"
            )
        return AgentResponse(agent=agent_info)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get(
    "",
    response_model=AgentListResponse,
    summary="List Agents",
    description="List all agents with optional filtering"
)
async def list_agents(
    status_filter: Optional[AgentStatus] = Query(None, description="Filter by agent status"),
    agent_type: Optional[AgentType] = Query(None, description="Filter by agent type"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgentListResponse:
    """List agents with optional filtering and pagination."""
    try:
        agents = await agent_manager.list_agents(
            status_filter=status_filter,
            agent_type=agent_type,
            page=page,
            size=size
        )
        
        total = await agent_manager.count_agents(
            status_filter=status_filter,
            agent_type=agent_type
        )
        
        return AgentListResponse(
            agents=agents,
            total=total,
            page=page,
            size=size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Get Agent",
    description="Get information about a specific agent"
)
async def get_agent(
    agent_id: UUID,
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgentResponse:
    """Get agent by ID."""
    try:
        agent_info = await agent_manager.get_agent(agent_id)
        if not agent_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        return AgentResponse(agent=agent_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}"
        )


@router.put(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Update Agent",
    description="Update an existing agent's configuration"
)
async def update_agent(
    agent_id: UUID,
    request: UpdateAgentRequest,
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgentResponse:
    """Update agent configuration."""
    try:
        agent_info = await agent_manager.update_agent(agent_id, request.to_config())
        if not agent_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        return AgentResponse(agent=agent_info)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}"
        )


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Agent",
    description="Delete an agent from the system"
)
async def delete_agent(
    agent_id: UUID,
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> None:
    """Delete agent by ID."""
    try:
        success = await agent_manager.delete_agent(agent_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )


@router.post(
    "/{agent_id}/start",
    response_model=AgentResponse,
    summary="Start Agent",
    description="Start an agent"
)
async def start_agent(
    agent_id: UUID,
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgentResponse:
    """Start an agent."""
    try:
        agent_info = await agent_manager.start_agent(agent_id)
        if not agent_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        return AgentResponse(agent=agent_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start agent: {str(e)}"
        )


@router.post(
    "/{agent_id}/stop",
    response_model=AgentResponse,
    summary="Stop Agent",
    description="Stop a running agent"
)
async def stop_agent(
    agent_id: UUID,
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgentResponse:
    """Stop an agent."""
    try:
        agent_info = await agent_manager.stop_agent(agent_id)
        if not agent_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        return AgentResponse(agent=agent_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop agent: {str(e)}"
        )


@router.get(
    "/{agent_id}/status",
    response_model=Dict[str, str],
    summary="Get Agent Status",
    description="Get the current status of an agent"
)
async def get_agent_status(
    agent_id: UUID,
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> Dict[str, str]:
    """Get agent status."""
    try:
        status_info = await agent_manager.get_agent_status(agent_id)
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        return status_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )
