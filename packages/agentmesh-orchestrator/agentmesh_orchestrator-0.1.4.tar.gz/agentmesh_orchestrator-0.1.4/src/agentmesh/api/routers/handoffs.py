"""REST API router for handoff management functionality."""

import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status, Query, Path
from pydantic import BaseModel

from ...core.handoff_manager import (
    get_handoff_manager,
    HandoffRequest,
    HandoffResponse,
    HandoffSummary,
    HandoffAuditEntry,
    HandoffReason
)
from ...core.agent_manager import get_agent_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/handoffs", tags=["Handoffs"])


class InitiateHandoffRequest(BaseModel):
    """Request model for initiating a handoff."""
    to_agent_id: str
    reason: str
    message: str
    conversation_id: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    priority: int = 0
    expires_in_minutes: int = 60


class RespondToHandoffRequest(BaseModel):
    """Request model for responding to a handoff."""
    accepted: bool
    message: Optional[str] = None


class HandoffRequestResponse(BaseModel):
    """Response model for handoff requests."""
    handoff: HandoffRequest


class HandoffResponseModel(BaseModel):
    """Response model for handoff responses."""
    response: HandoffResponse


class HandoffListResponse(BaseModel):
    """Response model for handoff lists."""
    handoffs: List[HandoffRequest]
    count: int


class HandoffHistoryResponse(BaseModel):
    """Response model for handoff history."""
    history: List[HandoffSummary]
    count: int


class HandoffAuditResponse(BaseModel):
    """Response model for handoff audit trail."""
    audit_entries: List[HandoffAuditEntry]
    count: int


class OperationResponse(BaseModel):
    """Response model for simple operations."""
    success: bool
    message: str


@router.post("/initiate", response_model=HandoffRequestResponse)
async def initiate_handoff(
    from_agent_id: str = Query(..., description="ID of the agent initiating the handoff"),
    request: InitiateHandoffRequest = ...,
):
    """Initiate a handoff request."""
    handoff_manager = get_handoff_manager()
    agent_manager = get_agent_manager()
    
    # Verify initiating agent exists
    from_agent = await agent_manager.get_agent(from_agent_id)
    if not from_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Initiating agent {from_agent_id} not found"
        )
    
    # Verify target agent exists
    to_agent = await agent_manager.get_agent(request.to_agent_id)
    if not to_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target agent {request.to_agent_id} not found"
        )
    
    # Validate reason
    valid_reasons = [
        HandoffReason.TASK_COMPLETION,
        HandoffReason.EXPERTISE_REQUIRED,
        HandoffReason.WORKLOAD_DISTRIBUTION,
        HandoffReason.ERROR_ESCALATION,
        HandoffReason.USER_REQUEST,
        HandoffReason.TIMEOUT,
        HandoffReason.MANUAL
    ]
    
    if request.reason not in valid_reasons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid handoff reason: {request.reason}"
        )
    
    try:
        handoff = await handoff_manager.initiate_handoff(
            from_agent_id=from_agent_id,
            to_agent_id=request.to_agent_id,
            reason=request.reason,
            message=request.message,
            conversation_id=request.conversation_id,
            context_data=request.context_data,
            metadata=request.metadata,
            priority=request.priority,
            expires_in_minutes=request.expires_in_minutes
        )
        
        return HandoffRequestResponse(handoff=handoff)
        
    except Exception as e:
        logger.error(f"Error initiating handoff from {from_agent_id} to {request.to_agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while initiating handoff: {str(e)}"
        )


@router.post("/respond/{handoff_id}", response_model=HandoffResponseModel)
async def respond_to_handoff(
    handoff_id: str = Path(..., description="ID of the handoff to respond to"),
    agent_id: str = Query(..., description="ID of the responding agent"),
    request: RespondToHandoffRequest = ...,
):
    """Respond to a handoff request."""
    handoff_manager = get_handoff_manager()
    agent_manager = get_agent_manager()
    
    # Verify responding agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Responding agent {agent_id} not found"
        )
    
    try:
        response = await handoff_manager.respond_to_handoff(
            handoff_id=handoff_id,
            agent_id=agent_id,
            accepted=request.accepted,
            message=request.message
        )
        
        return HandoffResponseModel(response=response)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error responding to handoff {handoff_id} by agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while responding to handoff: {str(e)}"
        )


@router.post("/cancel/{handoff_id}", response_model=OperationResponse)
async def cancel_handoff(
    handoff_id: str = Path(..., description="ID of the handoff to cancel"),
    agent_id: str = Query(..., description="ID of the agent cancelling the handoff"),
    reason: Optional[str] = Query(None, description="Reason for cancellation"),
):
    """Cancel a handoff request."""
    handoff_manager = get_handoff_manager()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        success = await handoff_manager.cancel_handoff(
            handoff_id=handoff_id,
            agent_id=agent_id,
            reason=reason
        )
        
        if success:
            return OperationResponse(
                success=True,
                message=f"Handoff {handoff_id} cancelled successfully"
            )
        else:
            return OperationResponse(
                success=False,
                message="Failed to cancel handoff - not found or already processed"
            )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error cancelling handoff {handoff_id} by agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while cancelling handoff: {str(e)}"
        )


@router.get("/pending", response_model=HandoffListResponse)
async def get_pending_handoffs(
    agent_id: str = Query(..., description="ID of the agent"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of handoffs to return"),
):
    """Get pending handoff requests for an agent."""
    handoff_manager = get_handoff_manager()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        handoffs = await handoff_manager.get_pending_handoffs(
            agent_id=agent_id,
            limit=limit
        )
        
        return HandoffListResponse(
            handoffs=handoffs,
            count=len(handoffs)
        )
        
    except Exception as e:
        logger.error(f"Error getting pending handoffs for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting pending handoffs: {str(e)}"
        )


@router.get("/history", response_model=HandoffHistoryResponse)
async def get_handoff_history(
    agent_id: str = Query(..., description="ID of the agent"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of handoffs to return"),
):
    """Get handoff history for an agent."""
    handoff_manager = get_handoff_manager()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        history = await handoff_manager.get_handoff_history(
            agent_id=agent_id,
            limit=limit
        )
        
        return HandoffHistoryResponse(
            history=history,
            count=len(history)
        )
        
    except Exception as e:
        logger.error(f"Error getting handoff history for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting handoff history: {str(e)}"
        )


@router.get("/audit/{handoff_id}", response_model=HandoffAuditResponse)
async def get_handoff_audit(
    handoff_id: str = Path(..., description="ID of the handoff"),
    agent_id: str = Query(..., description="ID of the requesting agent"),
):
    """Get audit trail for a handoff."""
    handoff_manager = get_handoff_manager()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        audit_entries = await handoff_manager.get_handoff_audit(handoff_id)
        
        # Basic access control - only agents involved in the handoff can see audit
        if audit_entries:
            # Check if agent was involved in the handoff
            involved = any(
                entry.agent_id == agent_id or 
                (entry.event_type == "created" and entry.details.get("to_agent_id") == agent_id)
                for entry in audit_entries
            )
            
            if not involved:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied - agent not involved in this handoff"
                )
        
        return HandoffAuditResponse(
            audit_entries=audit_entries,
            count=len(audit_entries)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting handoff audit for {handoff_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting handoff audit: {str(e)}"
        )


@router.get("/reasons")
async def get_handoff_reasons():
    """Get list of valid handoff reasons."""
    return {
        "reasons": [
            {"value": HandoffReason.TASK_COMPLETION, "description": "Task has been completed"},
            {"value": HandoffReason.EXPERTISE_REQUIRED, "description": "Specialized expertise is required"},
            {"value": HandoffReason.WORKLOAD_DISTRIBUTION, "description": "Distribute workload across agents"},
            {"value": HandoffReason.ERROR_ESCALATION, "description": "Escalate due to error or issue"},
            {"value": HandoffReason.USER_REQUEST, "description": "User requested specific agent"},
            {"value": HandoffReason.TIMEOUT, "description": "Previous agent timed out"},
            {"value": HandoffReason.MANUAL, "description": "Manual handoff by administrator"}
        ]
    }
