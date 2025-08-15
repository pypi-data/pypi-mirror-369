"""Base orchestration classes and interfaces."""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class OrchestrationPattern(str, Enum):
    """Orchestration pattern types."""
    SEQUENTIAL = "sequential"
    ROUND_ROBIN = "round_robin"
    GRAPH = "graph"
    SWARM = "swarm"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskResult(BaseModel):
    """Result of a task execution."""
    task_id: str
    agent_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.now)


class WorkflowConfig(BaseModel):
    """Configuration for workflow orchestration."""
    name: str
    pattern: OrchestrationPattern
    agents: List[str]  # Agent IDs
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[int] = None  # Timeout in seconds
    retry_attempts: int = 3
    failure_policy: str = "fail_fast"  # "fail_fast" or "continue"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowContext(BaseModel):
    """Context shared across workflow execution."""
    workflow_id: str
    current_step: int = 0
    shared_data: Dict[str, Any] = Field(default_factory=dict)
    history: List[TaskResult] = Field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.CREATED
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class BaseOrchestrator(ABC):
    """Base class for all orchestration patterns."""

    def __init__(self, config: WorkflowConfig):
        """Initialize orchestrator with configuration."""
        self.config = config
        self.workflow_id = str(uuid4())
        self.context = WorkflowContext(workflow_id=self.workflow_id)
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{self.workflow_id[:8]}")

    @abstractmethod
    async def execute(self, task: str, **kwargs) -> TaskResult:
        """Execute the workflow with the given task.
        
        Args:
            task: The task description or prompt
            **kwargs: Additional parameters for execution
            
        Returns:
            TaskResult: The final result of workflow execution
        """
        pass

    @abstractmethod
    async def pause(self) -> bool:
        """Pause the workflow execution.
        
        Returns:
            bool: True if successfully paused
        """
        pass

    @abstractmethod
    async def resume(self) -> bool:
        """Resume the paused workflow execution.
        
        Returns:
            bool: True if successfully resumed
        """
        pass

    @abstractmethod
    async def cancel(self) -> bool:
        """Cancel the workflow execution.
        
        Returns:
            bool: True if successfully cancelled
        """
        pass

    async def get_status(self) -> WorkflowStatus:
        """Get current workflow status."""
        return self.context.status

    async def get_progress(self) -> Dict[str, Any]:
        """Get workflow progress information."""
        total_steps = len(self.config.agents)
        current_step = self.context.current_step
        
        return {
            "workflow_id": self.workflow_id,
            "status": self.context.status,
            "progress": {
                "current_step": current_step,
                "total_steps": total_steps,
                "percentage": (current_step / total_steps * 100) if total_steps > 0 else 0
            },
            "history": [
                {
                    "task_id": result.task_id,
                    "agent_id": result.agent_id,
                    "success": result.success,
                    "timestamp": result.timestamp.isoformat()
                }
                for result in self.context.history
            ],
            "created_at": self.context.created_at.isoformat(),
            "updated_at": self.context.updated_at.isoformat()
        }

    def _update_context(self, result: TaskResult) -> None:
        """Update workflow context with task result."""
        self.context.history.append(result)
        if result.success:
            self.context.current_step += 1
        self.context.updated_at = datetime.now()

    async def _handle_error(self, error: Exception, agent_id: str, attempt: int) -> bool:
        """Handle execution errors with retry logic.
        
        Args:
            error: The exception that occurred
            agent_id: ID of the agent that failed
            attempt: Current attempt number
            
        Returns:
            bool: True if should retry, False otherwise
        """
        self.logger.error(f"Error in agent {agent_id} (attempt {attempt}): {error}")
        
        if attempt < self.config.retry_attempts:
            self.logger.info(f"Retrying agent {agent_id} (attempt {attempt + 1})")
            return True
        
        if self.config.failure_policy == "fail_fast":
            self.context.status = WorkflowStatus.FAILED
            return False
        
        # Continue with next agent if failure_policy is "continue"
        return False

    async def _execute_with_timeout(self, coro, timeout: Optional[int] = None) -> Any:
        """Execute coroutine with optional timeout.
        
        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds
            
        Returns:
            Any: Result of coroutine execution
            
        Raises:
            asyncio.TimeoutError: If execution exceeds timeout
        """
        if timeout:
            return await asyncio.wait_for(coro, timeout=timeout)
        else:
            return await coro


class OrchestrationError(Exception):
    """Base exception for orchestration errors."""
    pass


class WorkflowTimeoutError(OrchestrationError):
    """Raised when workflow execution exceeds timeout."""
    pass


class AgentExecutionError(OrchestrationError):
    """Raised when agent execution fails."""
    pass


class WorkflowConfigurationError(OrchestrationError):
    """Raised when workflow configuration is invalid."""
    pass
