"""REST API router for messaging functionality."""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status, Query, Path
from pydantic import BaseModel

from ...messaging.message_bus import get_message_bus, Message, MessageResult, MessageType
from ...models.agent import AgentInfo
from ...core.agent_manager import get_agent_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messaging", tags=["Messaging"])


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""
    receiver_id: str
    content: str
    message_type: str = MessageType.CHAT
    metadata: Optional[Dict[str, Any]] = None
    reply_to: Optional[str] = None


class BroadcastMessageRequest(BaseModel):
    """Request model for broadcasting a message."""
    group_id: str
    content: str
    message_type: str = MessageType.BROADCAST
    metadata: Optional[Dict[str, Any]] = None


class GroupMembershipRequest(BaseModel):
    """Request model for group membership operations."""
    group_id: str


class MessageResponse(BaseModel):
    """Response model for message operations."""
    message: Message


class MessagesResponse(BaseModel):
    """Response model for multiple messages."""
    messages: List[Message]
    count: int


class GroupOperationResponse(BaseModel):
    """Response model for group operations."""
    success: bool
    message: str


@router.post("/send", response_model=MessageResult)
async def send_message(
    sender_id: str = Query(..., description="ID of the sending agent"),
    request: SendMessageRequest = ...,
):
    """Send a message from one agent to another."""
    message_bus = get_message_bus()
    agent_manager = get_agent_manager()
    
    # Verify sender exists
    sender = await agent_manager.get_agent(sender_id)
    if not sender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sender agent {sender_id} not found"
        )
    
    # Verify receiver exists
    receiver = await agent_manager.get_agent(request.receiver_id)
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Receiver agent {request.receiver_id} not found"
        )
    
    try:
        result = await message_bus.send_message(
            sender_id=sender_id,
            receiver_id=request.receiver_id,
            content=request.content,
            message_type=request.message_type,
            metadata=request.metadata,
            reply_to=request.reply_to
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message: {result.error}"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending message from {sender_id} to {request.receiver_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while sending message: {str(e)}"
        )


@router.post("/broadcast", response_model=List[MessageResult])
async def broadcast_message(
    sender_id: str = Query(..., description="ID of the sending agent"),
    request: BroadcastMessageRequest = ...,
):
    """Broadcast a message to all agents in a group."""
    message_bus = get_message_bus()
    agent_manager = get_agent_manager()
    
    # Verify sender exists
    sender = await agent_manager.get_agent(sender_id)
    if not sender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sender agent {sender_id} not found"
        )
    
    try:
        results = await message_bus.broadcast_message(
            sender_id=sender_id,
            group_id=request.group_id,
            content=request.content,
            message_type=request.message_type,
            metadata=request.metadata
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error broadcasting message from {sender_id} to group {request.group_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while broadcasting message: {str(e)}"
        )


@router.get("/conversation/{agent1_id}/{agent2_id}", response_model=MessagesResponse)
async def get_conversation_history(
    agent1_id: str = Path(..., description="ID of the first agent"),
    agent2_id: str = Path(..., description="ID of the second agent"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of messages to return"),
):
    """Get conversation history between two agents."""
    message_bus = get_message_bus()
    agent_manager = get_agent_manager()
    
    # Verify both agents exist
    agent1 = await agent_manager.get_agent(agent1_id)
    if not agent1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent1_id} not found"
        )
    
    agent2 = await agent_manager.get_agent(agent2_id)
    if not agent2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent2_id} not found"
        )
    
    try:
        messages = await message_bus.get_conversation_history(
            agent1_id=agent1_id,
            agent2_id=agent2_id,
            limit=limit
        )
        
        return MessagesResponse(
            messages=messages,
            count=len(messages)
        )
        
    except Exception as e:
        logger.error(f"Error getting conversation history between {agent1_id} and {agent2_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting conversation history: {str(e)}"
        )


@router.get("/agent/{agent_id}/messages", response_model=MessagesResponse)
async def get_agent_messages(
    agent_id: str = Path(..., description="ID of the agent"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of messages to return"),
):
    """Get all messages for a specific agent."""
    message_bus = get_message_bus()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        messages = await message_bus.get_agent_messages(
            agent_id=agent_id,
            limit=limit
        )
        
        return MessagesResponse(
            messages=messages,
            count=len(messages)
        )
        
    except Exception as e:
        logger.error(f"Error getting messages for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting agent messages: {str(e)}"
        )


@router.post("/groups/join", response_model=GroupOperationResponse)
async def join_group(
    agent_id: str = Query(..., description="ID of the agent"),
    request: GroupMembershipRequest = ...,
):
    """Add an agent to a group."""
    message_bus = get_message_bus()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        success = await message_bus.add_agent_to_group(agent_id, request.group_id)
        
        if success:
            return GroupOperationResponse(
                success=True,
                message=f"Agent {agent_id} successfully joined group {request.group_id}"
            )
        else:
            return GroupOperationResponse(
                success=False,
                message=f"Failed to add agent {agent_id} to group {request.group_id}"
            )
        
    except Exception as e:
        logger.error(f"Error adding agent {agent_id} to group {request.group_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while joining group: {str(e)}"
        )


@router.post("/groups/leave", response_model=GroupOperationResponse)
async def leave_group(
    agent_id: str = Query(..., description="ID of the agent"),
    request: GroupMembershipRequest = ...,
):
    """Remove an agent from a group."""
    message_bus = get_message_bus()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        success = await message_bus.remove_agent_from_group(agent_id, request.group_id)
        
        if success:
            return GroupOperationResponse(
                success=True,
                message=f"Agent {agent_id} successfully left group {request.group_id}"
            )
        else:
            return GroupOperationResponse(
                success=False,
                message=f"Failed to remove agent {agent_id} from group {request.group_id}"
            )
        
    except Exception as e:
        logger.error(f"Error removing agent {agent_id} from group {request.group_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while leaving group: {str(e)}"
        )


@router.get("/groups/{group_id}/members")
async def get_group_members(
    group_id: str = Path(..., description="ID of the group"),
):
    """Get members of a group."""
    message_bus = get_message_bus()
    
    try:
        # This is a private method, but we can access it for the API
        members = await message_bus._get_group_members(group_id)
        
        return {
            "group_id": group_id,
            "members": members,
            "count": len(members)
        }
        
    except Exception as e:
        logger.error(f"Error getting members for group {group_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting group members: {str(e)}"
        )
