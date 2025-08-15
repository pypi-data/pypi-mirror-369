"""Database models for AutoGen A2A Communication System."""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .database import Base


class Agent(Base):
    """Database model for agents."""
    
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="created")
    model = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    system_message = Column(Text)
    temperature = Column(Integer)  # Store as integer (temperature * 100)
    max_tokens = Column(Integer)
    config = Column(JSON)  # JSON field for additional configuration
    capabilities = Column(JSON)  # JSON field for agent capabilities
    uptime_seconds = Column(Integer, default=0)
    last_active = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    workflow_memberships = relationship("WorkflowMember", back_populates="agent")
    team_memberships = relationship("TeamMember", back_populates="agent")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "model": self.model,
            "provider": self.provider,
            "system_message": self.system_message,
            "temperature": self.temperature / 100.0 if self.temperature is not None else None,
            "max_tokens": self.max_tokens,
            "config": self.config or {},
            "capabilities": self.capabilities or [],
            "uptime_seconds": self.uptime_seconds,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Workflow(Base):
    """Database model for workflows."""
    
    __tablename__ = "workflows"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default="created")
    config = Column(JSON)  # JSON field for workflow configuration
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    members = relationship("WorkflowMember", back_populates="workflow", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "config": self.config or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WorkflowMember(Base):
    """Database model for workflow membership."""
    
    __tablename__ = "workflow_members"
    
    id = Column(String(36), primary_key=True, index=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    role = Column(String(50))  # Optional role within the workflow
    order = Column(Integer, default=0)  # Execution order
    config = Column(JSON)  # Member-specific configuration
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="members")
    agent = relationship("Agent", back_populates="workflow_memberships")


class Team(Base):
    """Database model for teams."""
    
    __tablename__ = "teams"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default="created")
    config = Column(JSON)  # JSON field for team configuration
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "config": self.config or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TeamMember(Base):
    """Database model for team membership."""
    
    __tablename__ = "team_members"
    
    id = Column(String(36), primary_key=True, index=True)
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=False)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    role = Column(String(50))  # Optional role within the team
    is_leader = Column(Boolean, default=False)
    config = Column(JSON)  # Member-specific configuration
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    team = relationship("Team", back_populates="members")
    agent = relationship("Agent", back_populates="team_memberships")


class ExecutionLog(Base):
    """Database model for execution logs."""
    
    __tablename__ = "execution_logs"
    
    id = Column(String(36), primary_key=True, index=True)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=True)
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=True)
    event_type = Column(String(50), nullable=False)  # start, stop, message, error, etc.
    message = Column(Text)
    data = Column(JSON)  # Additional event data
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "workflow_id": self.workflow_id,
            "team_id": self.team_id,
            "event_type": self.event_type,
            "message": self.message,
            "data": self.data or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
