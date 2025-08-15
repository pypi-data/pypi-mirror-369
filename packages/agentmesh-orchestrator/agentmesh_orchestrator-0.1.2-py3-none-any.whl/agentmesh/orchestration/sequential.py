"""Sequential orchestration implementation."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.agent_manager import get_agent_manager
from ..models.message import BaseChatMessage, TextMessage
from .base import (
    BaseOrchestrator,
    TaskResult,
    WorkflowConfig,
    WorkflowStatus,
    OrchestrationError,
    WorkflowTimeoutError,
    AgentExecutionError
)

logger = logging.getLogger(__name__)


class SequentialOrchestrator(BaseOrchestrator):
    """Sequential workflow orchestration following AutoGen patterns.
    
    Executes agents in a predefined sequence, where each agent processes
    the result from the previous agent. This pattern is useful for
    pipeline-style workflows where tasks build upon each other.
    """

    def __init__(self, config: WorkflowConfig):
        """Initialize sequential orchestrator."""
        super().__init__(config)
        self.agent_manager = get_agent_manager()
        self._execution_task: Optional[asyncio.Task] = None

    async def execute(self, task: str, **kwargs) -> TaskResult:
        """Execute agents sequentially.
        
        Args:
            task: Initial task description
            **kwargs: Additional parameters
            
        Returns:
            TaskResult: Final result from the last agent
        """
        if self.context.status == WorkflowStatus.RUNNING:
            raise OrchestrationError("Workflow is already running")

        self.logger.info(f"Starting sequential workflow with {len(self.config.agents)} agents")
        self.context.status = WorkflowStatus.RUNNING
        
        try:
            # Create execution task for cancellation support
            self._execution_task = asyncio.create_task(
                self._execute_sequential_workflow(task, **kwargs)
            )
            
            result = await self._execution_task
            self.context.status = WorkflowStatus.COMPLETED
            return result
            
        except asyncio.CancelledError:
            self.context.status = WorkflowStatus.CANCELLED
            self.logger.info("Sequential workflow cancelled")
            raise
        except Exception as e:
            self.context.status = WorkflowStatus.FAILED
            self.logger.error(f"Sequential workflow failed: {e}")
            raise

    async def _execute_sequential_workflow(self, initial_task: str, **kwargs) -> TaskResult:
        """Execute the sequential workflow logic."""
        current_message = initial_task
        last_result = None
        
        for i, agent_id in enumerate(self.config.agents):
            self.logger.info(f"Executing step {i + 1}/{len(self.config.agents)}: agent {agent_id}")
            
            # Create task context for this step
            step_context = {
                "step": i + 1,
                "total_steps": len(self.config.agents),
                "previous_results": [r.result for r in self.context.history if r.success],
                "shared_data": self.context.shared_data,
                **kwargs
            }
            
            # Execute agent with retry logic
            result = await self._execute_agent_with_retry(
                agent_id, current_message, step_context
            )
            
            # Update context and prepare for next iteration
            self._update_context(result)
            
            if not result.success:
                if self.config.failure_policy == "fail_fast":
                    raise AgentExecutionError(f"Agent {agent_id} failed: {result.error}")
                else:
                    self.logger.warning(f"Agent {agent_id} failed, continuing: {result.error}")
                    continue
            
            # Use the result as input for the next agent
            if result.result:
                if isinstance(result.result, str):
                    current_message = result.result
                elif hasattr(result.result, 'content'):
                    current_message = result.result.content
                else:
                    current_message = str(result.result)
            
            last_result = result
            
            # Update shared data if agent provided any
            if hasattr(result, 'shared_data') and result.shared_data:
                self.context.shared_data.update(result.shared_data)

        if not last_result:
            raise OrchestrationError("No agents executed successfully")
        
        return last_result

    async def _execute_agent_with_retry(
        self, 
        agent_id: str, 
        message: str, 
        context: Dict[str, Any]
    ) -> TaskResult:
        """Execute a single agent with retry logic."""
        start_time = datetime.now()
        
        for attempt in range(1, self.config.retry_attempts + 1):
            try:
                self.logger.debug(f"Executing agent {agent_id}, attempt {attempt}")
                
                # Get agent from manager
                agent_info = await self.agent_manager.get_agent(agent_id)
                if not agent_info:
                    raise AgentExecutionError(f"Agent {agent_id} not found")
                
                # Create message for agent
                task_message = TextMessage(
                    content=message,
                    sender="workflow_orchestrator",
                    metadata={
                        "workflow_id": self.workflow_id,
                        "context": context
                    }
                )
                
                # Execute agent (this would integrate with actual agent execution)
                # For now, we'll simulate execution
                result = await self._simulate_agent_execution(agent_id, task_message, context)
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return TaskResult(
                    task_id=f"{self.workflow_id}-{agent_id}-{attempt}",
                    agent_id=agent_id,
                    success=True,
                    result=result,
                    execution_time=execution_time
                )
                
            except Exception as e:
                if await self._handle_error(e, agent_id, attempt):
                    continue
                
                execution_time = (datetime.now() - start_time).total_seconds()
                return TaskResult(
                    task_id=f"{self.workflow_id}-{agent_id}-{attempt}",
                    agent_id=agent_id,
                    success=False,
                    error=str(e),
                    execution_time=execution_time
                )
        
        # This should never be reached due to retry logic
        raise OrchestrationError(f"Unexpected error in agent execution: {agent_id}")

    async def _simulate_agent_execution(
        self, 
        agent_id: str, 
        message: BaseChatMessage, 
        context: Dict[str, Any]
    ) -> str:
        """Simulate agent execution for testing/demo purposes.
        
        In a real implementation, this would:
        1. Get the actual agent instance
        2. Send the message to the agent
        3. Wait for response
        4. Return the agent's response
        """
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Simulate agent response based on agent type/name
        if "architect" in agent_id.lower():
            return f"Architecture plan created for: {message.content}"
        elif "developer" in agent_id.lower():
            return f"Code implementation for: {message.content}"
        elif "tester" in agent_id.lower():
            return f"Test suite created for: {message.content}"
        elif "reviewer" in agent_id.lower():
            return f"Code review completed for: {message.content}"
        else:
            return f"Task processed by {agent_id}: {message.content}"

    async def pause(self) -> bool:
        """Pause the sequential workflow execution."""
        if self.context.status != WorkflowStatus.RUNNING:
            return False
        
        self.context.status = WorkflowStatus.PAUSED
        self.logger.info("Sequential workflow paused")
        return True

    async def resume(self) -> bool:
        """Resume the paused sequential workflow execution."""
        if self.context.status != WorkflowStatus.PAUSED:
            return False
        
        self.context.status = WorkflowStatus.RUNNING
        self.logger.info("Sequential workflow resumed")
        return True

    async def cancel(self) -> bool:
        """Cancel the sequential workflow execution."""
        if self._execution_task and not self._execution_task.done():
            self._execution_task.cancel()
            
        self.context.status = WorkflowStatus.CANCELLED
        self.logger.info("Sequential workflow cancelled")
        return True

    async def get_execution_plan(self) -> List[Dict[str, Any]]:
        """Get the execution plan for this sequential workflow."""
        plan = []
        for i, agent_id in enumerate(self.config.agents):
            agent_info = await self.agent_manager.get_agent(agent_id)
            plan.append({
                "step": i + 1,
                "agent_id": agent_id,
                "agent_name": agent_info.name if agent_info else f"Unknown({agent_id})",
                "status": "completed" if i < self.context.current_step else 
                         "running" if i == self.context.current_step else "pending"
            })
        
        return plan
