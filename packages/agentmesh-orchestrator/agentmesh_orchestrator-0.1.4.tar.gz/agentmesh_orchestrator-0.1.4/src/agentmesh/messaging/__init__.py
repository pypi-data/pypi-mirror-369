"""Message bus implementation for agent communication."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4

import redis.asyncio as redis
from pydantic import BaseModel

from ..core.config import get_settings
from ..models.agent import AgentInfo

logger = logging.getLogger(__name__)


class MessageType(str):
    """Message type constants."""
    CHAT = "chat"
    HANDOFF = "handoff"
    SYSTEM = "system"
    BROADCAST = "broadcast"
    STATUS = "status"


class Message(BaseModel):
    """Base message model."""
    id: str
    sender_id: str
    receiver_id: Optional[str] = None
    group_id: Optional[str] = None
    message_type: str
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime
    reply_to: Optional[str] = None


class MessageResult(BaseModel):
    """Result of message sending operation."""
    message_id: str
    success: bool
    delivered_at: Optional[datetime] = None
    error: Optional[str] = None


class MessageBus:
    """Redis-based message bus for agent communication."""

    def __init__(self):
        """Initialize the message bus."""
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        self.subscribers: Dict[str, set] = {}
        self.message_handlers: Dict[str, List] = {}
        
    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                db=self.settings.redis_db,
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis message bus")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis message bus")

    async def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        content: str,
        message_type: str = MessageType.CHAT,
        metadata: Optional[Dict[str, Any]] = None,
        reply_to: Optional[str] = None
    ) -> MessageResult:
        """Send a message to a specific agent."""
        if not self.redis_client:
            await self.connect()

        message = Message(
            id=str(uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.utcnow(),
            reply_to=reply_to
        )

        try:
            # Store message in Redis
            await self._store_message(message)
            
            # Publish to receiver's channel
            channel = f"agent:{receiver_id}"
            await self.redis_client.publish(channel, message.model_dump_json())
            
            # Store in conversation history
            await self._store_conversation_message(sender_id, receiver_id, message)
            
            logger.debug(f"Message sent from {sender_id} to {receiver_id}")
            
            return MessageResult(
                message_id=message.id,
                success=True,
                delivered_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return MessageResult(
                message_id=message.id,
                success=False,
                error=str(e)
            )

    async def broadcast_message(
        self,
        sender_id: str,
        group_id: str,
        content: str,
        message_type: str = MessageType.BROADCAST,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[MessageResult]:
        """Broadcast a message to all agents in a group."""
        if not self.redis_client:
            await self.connect()

        message = Message(
            id=str(uuid4()),
            sender_id=sender_id,
            group_id=group_id,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.utcnow()
        )

        try:
            # Store message in Redis
            await self._store_message(message)
            
            # Get group members
            group_members = await self._get_group_members(group_id)
            
            results = []
            for member_id in group_members:
                if member_id != sender_id:  # Don't send to self
                    result = await self.send_message(
                        sender_id=sender_id,
                        receiver_id=member_id,
                        content=content,
                        message_type=message_type,
                        metadata={**(metadata or {}), "broadcast_id": message.id}
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to broadcast message: {e}")
            return [MessageResult(
                message_id=message.id,
                success=False,
                error=str(e)
            )]

    async def subscribe_to_messages(
        self,
        agent_id: str,
        callback
    ) -> None:
        """Subscribe an agent to receive messages."""
        if not self.redis_client:
            await self.connect()

        channel = f"agent:{agent_id}"
        pubsub = self.redis_client.pubsub()
        
        try:
            await pubsub.subscribe(channel)
            logger.info(f"Agent {agent_id} subscribed to messages")
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        msg_data = json.loads(message['data'])
                        parsed_message = Message(**msg_data)
                        await callback(parsed_message)
                    except Exception as e:
                        logger.error(f"Error processing message for {agent_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Subscription error for {agent_id}: {e}")
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

    async def get_conversation_history(
        self,
        agent1_id: str,
        agent2_id: str,
        limit: int = 50
    ) -> List[Message]:
        """Get conversation history between two agents."""
        if not self.redis_client:
            await self.connect()

        # Create conversation key (sorted to ensure consistency)
        conv_key = f"conversation:{':'.join(sorted([agent1_id, agent2_id]))}"
        
        try:
            # Get message IDs from conversation list
            message_ids = await self.redis_client.lrange(conv_key, 0, limit-1)
            
            messages = []
            for msg_id in message_ids:
                msg_data = await self.redis_client.hget("messages", msg_id)
                if msg_data:
                    messages.append(Message(**json.loads(msg_data)))
            
            return list(reversed(messages))  # Most recent first
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []

    async def get_agent_messages(
        self,
        agent_id: str,
        limit: int = 50
    ) -> List[Message]:
        """Get all messages for an agent."""
        if not self.redis_client:
            await self.connect()

        try:
            # Get message IDs for the agent
            message_ids = await self.redis_client.lrange(
                f"agent_messages:{agent_id}", 0, limit-1
            )
            
            messages = []
            for msg_id in message_ids:
                msg_data = await self.redis_client.hget("messages", msg_id)
                if msg_data:
                    messages.append(Message(**json.loads(msg_data)))
            
            return list(reversed(messages))  # Most recent first
            
        except Exception as e:
            logger.error(f"Failed to get agent messages: {e}")
            return []

    async def _store_message(self, message: Message) -> None:
        """Store message in Redis."""
        if not self.redis_client:
            return

        # Store in messages hash
        await self.redis_client.hset(
            "messages",
            message.id,
            message.model_dump_json()
        )
        
        # Add to sender's message list
        await self.redis_client.lpush(
            f"agent_messages:{message.sender_id}",
            message.id
        )
        
        # Add to receiver's message list (if not broadcast)
        if message.receiver_id:
            await self.redis_client.lpush(
                f"agent_messages:{message.receiver_id}",
                message.id
            )

    async def _store_conversation_message(
        self,
        agent1_id: str,
        agent2_id: str,
        message: Message
    ) -> None:
        """Store message in conversation history."""
        if not self.redis_client:
            return

        # Create conversation key (sorted to ensure consistency)
        conv_key = f"conversation:{':'.join(sorted([agent1_id, agent2_id]))}"
        
        # Add message to conversation
        await self.redis_client.lpush(conv_key, message.id)
        
        # Keep only recent messages (configurable limit)
        await self.redis_client.ltrim(conv_key, 0, 999)  # Keep last 1000 messages

    async def _get_group_members(self, group_id: str) -> List[str]:
        """Get members of a group."""
        if not self.redis_client:
            return []

        try:
            members = await self.redis_client.smembers(f"group:{group_id}:members")
            return list(members) if members else []
        except Exception as e:
            logger.error(f"Failed to get group members: {e}")
            return []

    async def add_agent_to_group(self, agent_id: str, group_id: str) -> bool:
        """Add an agent to a group."""
        if not self.redis_client:
            await self.connect()

        try:
            await self.redis_client.sadd(f"group:{group_id}:members", agent_id)
            await self.redis_client.sadd(f"agent:{agent_id}:groups", group_id)
            return True
        except Exception as e:
            logger.error(f"Failed to add agent to group: {e}")
            return False

    async def remove_agent_from_group(self, agent_id: str, group_id: str) -> bool:
        """Remove an agent from a group."""
        if not self.redis_client:
            await self.connect()

        try:
            await self.redis_client.srem(f"group:{group_id}:members", agent_id)
            await self.redis_client.srem(f"agent:{agent_id}:groups", group_id)
            return True
        except Exception as e:
            logger.error(f"Failed to remove agent from group: {e}")
            return False


# Global message bus instance
_message_bus: Optional[MessageBus] = None


def get_message_bus() -> MessageBus:
    """Get or create the global message bus instance."""
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus
