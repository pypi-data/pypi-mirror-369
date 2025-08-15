"""WebSocket router for real-time agent communication."""

import asyncio
import json
import logging
from typing import Dict, Set, Optional
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from pydantic import BaseModel, ValidationError

from ...messaging.message_bus import get_message_bus, Message, MessageType
from ...models.agent import AgentInfo
from ...core.agent_manager import get_agent_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


class WebSocketMessage(BaseModel):
    """WebSocket message structure."""
    type: str  # 'message', 'join_group', 'leave_group', 'status', 'heartbeat'
    data: Dict = {}


class ConnectionManager:
    """Manages WebSocket connections for agents."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.agent_connections: Dict[str, str] = {}  # agent_id -> connection_id
        self.connection_agents: Dict[str, str] = {}  # connection_id -> agent_id
        self.agent_groups: Dict[str, Set[str]] = {}  # agent_id -> set of group_ids
        
    async def connect(self, websocket: WebSocket, agent_id: str) -> str:
        """Accept a new WebSocket connection for an agent."""
        await websocket.accept()
        
        connection_id = str(uuid4())
        self.active_connections[connection_id] = websocket
        
        # Disconnect existing connection for this agent if any
        if agent_id in self.agent_connections:
            old_connection_id = self.agent_connections[agent_id]
            await self.disconnect(old_connection_id)
        
        self.agent_connections[agent_id] = connection_id
        self.connection_agents[connection_id] = agent_id
        self.agent_groups[agent_id] = set()
        
        logger.info(f"Agent {agent_id} connected via WebSocket {connection_id}")
        return connection_id
        
    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            agent_id = self.connection_agents.get(connection_id)
            
            try:
                await websocket.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket {connection_id}: {e}")
            
            # Clean up mappings
            del self.active_connections[connection_id]
            
            if agent_id:
                if agent_id in self.agent_connections:
                    del self.agent_connections[agent_id]
                if agent_id in self.agent_groups:
                    del self.agent_groups[agent_id]
                logger.info(f"Agent {agent_id} disconnected from WebSocket {connection_id}")
            
            if connection_id in self.connection_agents:
                del self.connection_agents[connection_id]
    
    async def send_personal_message(self, message: str, agent_id: str):
        """Send a message to a specific agent."""
        if agent_id in self.agent_connections:
            connection_id = self.agent_connections[agent_id]
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_text(message)
                    return True
                except Exception as e:
                    logger.error(f"Error sending message to agent {agent_id}: {e}")
                    await self.disconnect(connection_id)
        return False
    
    async def broadcast_to_group(self, message: str, group_id: str, exclude_agent: Optional[str] = None):
        """Broadcast a message to all agents in a group."""
        sent_count = 0
        for agent_id, groups in self.agent_groups.items():
            if group_id in groups and agent_id != exclude_agent:
                if await self.send_personal_message(message, agent_id):
                    sent_count += 1
        return sent_count
    
    def add_agent_to_group(self, agent_id: str, group_id: str):
        """Add an agent to a group for broadcasting."""
        if agent_id in self.agent_groups:
            self.agent_groups[agent_id].add(group_id)
            return True
        return False
    
    def remove_agent_from_group(self, agent_id: str, group_id: str):
        """Remove an agent from a group."""
        if agent_id in self.agent_groups:
            self.agent_groups[agent_id].discard(group_id)
            return True
        return False
    
    def get_connected_agents(self) -> Set[str]:
        """Get list of currently connected agents."""
        return set(self.agent_connections.keys())


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/agent/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent real-time communication."""
    message_bus = get_message_bus()
    agent_manager = get_agent_manager()
    
    # Verify agent exists
    try:
        agent_info = await agent_manager.get_agent(agent_id)
        if not agent_info:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Agent not found")
            return
    except Exception as e:
        logger.error(f"Error verifying agent {agent_id}: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Internal error")
        return
    
    connection_id = await manager.connect(websocket, agent_id)
    
    # Start listening to messages from the message bus
    async def message_listener():
        """Listen for messages from the message bus and forward to WebSocket."""
        try:
            await message_bus.subscribe_to_messages(
                agent_id,
                lambda msg: manager.send_personal_message(
                    json.dumps({
                        "type": "message",
                        "data": msg.model_dump(mode='json')  # Use JSON mode for proper serialization
                    }),
                    agent_id
                )
            )
        except Exception as e:
            logger.error(f"Message listener error for agent {agent_id}: {e}")
    
    # Start message listener task
    listener_task = asyncio.create_task(message_listener())
    
    try:
        while True:
            # Receive message from WebSocket
            data = await websocket.receive_text()
            
            try:
                ws_message = WebSocketMessage(**json.loads(data))
            except (json.JSONDecodeError, ValidationError) as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": f"Invalid message format: {e}"}
                }))
                continue
            
            # Handle different message types
            if ws_message.type == "message":
                await handle_message(ws_message, agent_id, message_bus)
            elif ws_message.type == "join_group":
                await handle_join_group(ws_message, agent_id, message_bus)
            elif ws_message.type == "leave_group":
                await handle_leave_group(ws_message, agent_id, message_bus)
            elif ws_message.type == "status":
                await handle_status_update(ws_message, agent_id, agent_manager)
            elif ws_message.type == "heartbeat":
                await websocket.send_text(json.dumps({"type": "heartbeat_ack", "data": {}}))
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": f"Unknown message type: {ws_message.type}"}
                }))
                
    except WebSocketDisconnect:
        logger.info(f"Agent {agent_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for agent {agent_id}: {e}")
    finally:
        # Cancel message listener task
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            pass
        
        # Disconnect
        await manager.disconnect(connection_id)


async def handle_message(ws_message: WebSocketMessage, sender_id: str, message_bus):
    """Handle incoming message from WebSocket."""
    data = ws_message.data
    
    required_fields = ["receiver_id", "content"]
    if not all(field in data for field in required_fields):
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "data": {"message": "Missing required fields: receiver_id, content"}
            }),
            sender_id
        )
        return
    
    try:
        result = await message_bus.send_message(
            sender_id=sender_id,
            receiver_id=data["receiver_id"],
            content=data["content"],
            message_type=data.get("message_type", MessageType.CHAT),
            metadata=data.get("metadata", {}),
            reply_to=data.get("reply_to")
        )
        
        # Send result back to sender
        await manager.send_personal_message(
            json.dumps({
                "type": "message_result",
                "data": result.model_dump(mode='json')  # Use JSON mode for proper serialization
            }),
            sender_id
        )
        
    except Exception as e:
        logger.error(f"Error sending message from {sender_id}: {e}")
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "data": {"message": f"Failed to send message: {e}"}
            }),
            sender_id
        )


async def handle_join_group(ws_message: WebSocketMessage, agent_id: str, message_bus):
    """Handle agent joining a group."""
    data = ws_message.data
    group_id = data.get("group_id")
    
    if not group_id:
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "data": {"message": "Missing group_id"}
            }),
            agent_id
        )
        return
    
    try:
        # Add to message bus group
        success = await message_bus.add_agent_to_group(agent_id, group_id)
        
        if success:
            # Add to WebSocket group for real-time updates
            manager.add_agent_to_group(agent_id, group_id)
            
            await manager.send_personal_message(
                json.dumps({
                    "type": "group_joined",
                    "data": {"group_id": group_id}
                }),
                agent_id
            )
        else:
            await manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "data": {"message": f"Failed to join group {group_id}"}
                }),
                agent_id
            )
            
    except Exception as e:
        logger.error(f"Error joining group {group_id} for agent {agent_id}: {e}")
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "data": {"message": f"Failed to join group: {e}"}
            }),
            agent_id
        )


async def handle_leave_group(ws_message: WebSocketMessage, agent_id: str, message_bus):
    """Handle agent leaving a group."""
    data = ws_message.data
    group_id = data.get("group_id")
    
    if not group_id:
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "data": {"message": "Missing group_id"}
            }),
            agent_id
        )
        return
    
    try:
        # Remove from message bus group
        success = await message_bus.remove_agent_from_group(agent_id, group_id)
        
        if success:
            # Remove from WebSocket group
            manager.remove_agent_from_group(agent_id, group_id)
            
            await manager.send_personal_message(
                json.dumps({
                    "type": "group_left",
                    "data": {"group_id": group_id}
                }),
                agent_id
            )
        else:
            await manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "data": {"message": f"Failed to leave group {group_id}"}
                }),
                agent_id
            )
            
    except Exception as e:
        logger.error(f"Error leaving group {group_id} for agent {agent_id}: {e}")
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "data": {"message": f"Failed to leave group: {e}"}
            }),
            agent_id
        )


async def handle_status_update(ws_message: WebSocketMessage, agent_id: str, agent_manager):
    """Handle agent status update."""
    data = ws_message.data
    status = data.get("status")
    
    if not status:
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "data": {"message": "Missing status"}
            }),
            agent_id
        )
        return
    
    try:
        # Update agent status
        # This could be extended to update agent metadata or status in the database
        await manager.send_personal_message(
            json.dumps({
                "type": "status_updated",
                "data": {"status": status}
            }),
            agent_id
        )
        
        logger.info(f"Agent {agent_id} status updated to: {status}")
        
    except Exception as e:
        logger.error(f"Error updating status for agent {agent_id}: {e}")
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "data": {"message": f"Failed to update status: {e}"}
            }),
            agent_id
        )


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    return manager
