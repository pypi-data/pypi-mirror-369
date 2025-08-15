"""REST API router for context management functionality."""

import logging
from datetime import timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status, Query, Path
from pydantic import BaseModel

from ...core.context_manager import (
    get_context_manager, 
    ContextEntry, 
    ContextVersion,
    ContextScope,
    AccessLevel
)
from ...core.agent_manager import get_agent_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/context", tags=["Context Management"])


class SetContextRequest(BaseModel):
    """Request model for setting context."""
    key: str
    value: Any
    scope: str
    scope_id: str
    metadata: Optional[Dict[str, Any]] = None
    expires_in_hours: Optional[int] = None
    change_reason: Optional[str] = None


class ContextResponse(BaseModel):
    """Response model for context operations."""
    entry: ContextEntry


class ContextListResponse(BaseModel):
    """Response model for context listing."""
    entries: List[ContextEntry]
    count: int


class ContextHistoryResponse(BaseModel):
    """Response model for context history."""
    versions: List[ContextVersion]
    count: int


class GrantAccessRequest(BaseModel):
    """Request model for granting context access."""
    key: str
    scope: str
    scope_id: str
    target_agent_id: str
    access_level: str


class AccessOperationResponse(BaseModel):
    """Response model for access operations."""
    success: bool
    message: str


@router.post("/set", response_model=ContextResponse)
async def set_context(
    agent_id: str = Query(..., description="ID of the agent setting context"),
    request: SetContextRequest = ...,
):
    """Set a context entry."""
    context_manager = get_context_manager()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    # Validate scope
    if request.scope not in [ContextScope.AGENT, ContextScope.CONVERSATION, ContextScope.GROUP, ContextScope.GLOBAL]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scope: {request.scope}"
        )
    
    try:
        expires_in = timedelta(hours=request.expires_in_hours) if request.expires_in_hours else None
        
        entry = await context_manager.set_context(
            key=request.key,
            value=request.value,
            scope=request.scope,
            scope_id=request.scope_id,
            created_by=agent_id,
            metadata=request.metadata,
            expires_in=expires_in,
            change_reason=request.change_reason
        )
        
        return ContextResponse(entry=entry)
        
    except Exception as e:
        logger.error(f"Error setting context by agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while setting context: {str(e)}"
        )


@router.get("/get/{scope}/{scope_id}/{key}", response_model=ContextResponse)
async def get_context(
    scope: str = Path(..., description="Context scope"),
    scope_id: str = Path(..., description="Scope identifier"),
    key: str = Path(..., description="Context key"),
    agent_id: str = Query(..., description="ID of the requesting agent"),
    version: Optional[int] = Query(None, description="Specific version to retrieve"),
):
    """Get a context entry."""
    context_manager = get_context_manager()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        entry = await context_manager.get_context(
            key=key,
            scope=scope,
            scope_id=scope_id,
            requester_id=agent_id,
            version=version
        )
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Context entry not found or access denied"
            )
        
        return ContextResponse(entry=entry)
        
    except Exception as e:
        logger.error(f"Error getting context by agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting context: {str(e)}"
        )


@router.delete("/delete/{scope}/{scope_id}/{key}")
async def delete_context(
    scope: str = Path(..., description="Context scope"),
    scope_id: str = Path(..., description="Scope identifier"),
    key: str = Path(..., description="Context key"),
    agent_id: str = Query(..., description="ID of the requesting agent"),
):
    """Delete a context entry."""
    context_manager = get_context_manager()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        success = await context_manager.delete_context(
            key=key,
            scope=scope,
            scope_id=scope_id,
            requester_id=agent_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied or context entry not found"
            )
        
        return {"success": True, "message": "Context entry deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting context by agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while deleting context: {str(e)}"
        )


@router.get("/list/{scope}/{scope_id}", response_model=ContextListResponse)
async def list_context(
    scope: str = Path(..., description="Context scope"),
    scope_id: str = Path(..., description="Scope identifier"),
    agent_id: str = Query(..., description="ID of the requesting agent"),
    key_pattern: Optional[str] = Query(None, description="Filter by key pattern"),
):
    """List context entries in a scope."""
    context_manager = get_context_manager()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        entries = await context_manager.list_context(
            scope=scope,
            scope_id=scope_id,
            requester_id=agent_id,
            key_pattern=key_pattern
        )
        
        return ContextListResponse(
            entries=entries,
            count=len(entries)
        )
        
    except Exception as e:
        logger.error(f"Error listing context by agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while listing context: {str(e)}"
        )


@router.get("/history/{scope}/{scope_id}/{key}", response_model=ContextHistoryResponse)
async def get_context_history(
    scope: str = Path(..., description="Context scope"),
    scope_id: str = Path(..., description="Scope identifier"),
    key: str = Path(..., description="Context key"),
    agent_id: str = Query(..., description="ID of the requesting agent"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of versions to return"),
):
    """Get version history for a context entry."""
    context_manager = get_context_manager()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        versions = await context_manager.get_context_history(
            key=key,
            scope=scope,
            scope_id=scope_id,
            requester_id=agent_id,
            limit=limit
        )
        
        return ContextHistoryResponse(
            versions=versions,
            count=len(versions)
        )
        
    except Exception as e:
        logger.error(f"Error getting context history by agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting context history: {str(e)}"
        )


@router.post("/access/grant", response_model=AccessOperationResponse)
async def grant_context_access(
    agent_id: str = Query(..., description="ID of the agent granting access"),
    request: GrantAccessRequest = ...,
):
    """Grant access to a context entry."""
    context_manager = get_context_manager()
    agent_manager = get_agent_manager()
    
    # Verify granting agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    # Verify target agent exists
    target_agent = await agent_manager.get_agent(request.target_agent_id)
    if not target_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target agent {request.target_agent_id} not found"
        )
    
    # Validate access level
    if request.access_level not in [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid access level: {request.access_level}"
        )
    
    try:
        success = await context_manager.grant_access(
            key=request.key,
            scope=request.scope,
            scope_id=request.scope_id,
            agent_id=request.target_agent_id,
            access_level=request.access_level,
            granted_by=agent_id
        )
        
        if success:
            return AccessOperationResponse(
                success=True,
                message=f"Access granted to {request.target_agent_id} for {request.key}"
            )
        else:
            return AccessOperationResponse(
                success=False,
                message="Failed to grant access - insufficient permissions"
            )
        
    except Exception as e:
        logger.error(f"Error granting context access by agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while granting access: {str(e)}"
        )


@router.post("/access/revoke", response_model=AccessOperationResponse)
async def revoke_context_access(
    agent_id: str = Query(..., description="ID of the agent revoking access"),
    request: GrantAccessRequest = ...,  # Reuse same model, just ignore access_level
):
    """Revoke access to a context entry."""
    context_manager = get_context_manager()
    agent_manager = get_agent_manager()
    
    # Verify revoking agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    # Verify target agent exists
    target_agent = await agent_manager.get_agent(request.target_agent_id)
    if not target_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target agent {request.target_agent_id} not found"
        )
    
    try:
        success = await context_manager.revoke_access(
            key=request.key,
            scope=request.scope,
            scope_id=request.scope_id,
            agent_id=request.target_agent_id,
            revoked_by=agent_id
        )
        
        if success:
            return AccessOperationResponse(
                success=True,
                message=f"Access revoked from {request.target_agent_id} for {request.key}"
            )
        else:
            return AccessOperationResponse(
                success=False,
                message="Failed to revoke access - insufficient permissions"
            )
        
    except Exception as e:
        logger.error(f"Error revoking context access by agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while revoking access: {str(e)}"
        )
