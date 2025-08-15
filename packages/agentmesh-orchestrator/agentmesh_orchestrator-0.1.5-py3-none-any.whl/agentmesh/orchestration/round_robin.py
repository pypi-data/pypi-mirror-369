"""Round-robin orchestration implementation."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable

from ..core.agent_manager import get_agent_manager
from ..models.message import BaseChatMessage, TextMessage
from .base import (
    BaseOrchestrator,
    TaskResult,
    WorkflowConfig,
    WorkflowStatus,
    OrchestrationError,
    AgentExecutionError
)

logger = logging.getLogger(__name__)


class TerminationCondition:
    """Termination condition for round-robin orchestration."""
    
    def __init__(
        self,
        max_rounds: Optional[int] = None,
        max_messages: Optional[int] = None,
        timeout_seconds: Optional[int] = None,
        custom_condition: Optional[Callable[[List[TaskResult]], bool]] = None
    ):
        """Initialize termination condition.
        
        Args:
            max_rounds: Maximum number of complete rounds
            max_messages: Maximum total messages
            timeout_seconds: Maximum execution time
            custom_condition: Custom termination function
        """
        self.max_rounds = max_rounds
        self.max_messages = max_messages
        self.timeout_seconds = timeout_seconds
        self.custom_condition = custom_condition

    def should_terminate(
        self, 
        current_round: int, 
        message_count: int, 
        execution_time: float,
        history: List[TaskResult]
    ) -> bool:
        """Check if orchestration should terminate."""
        if self.max_rounds and current_round >= self.max_rounds:
            return True
        
        if self.max_messages and message_count >= self.max_messages:
            return True
        
        if self.timeout_seconds and execution_time >= self.timeout_seconds:
            return True
        
        if self.custom_condition and self.custom_condition(history):
            return True
        
        return False


class RoundRobinOrchestrator(BaseOrchestrator):
    """Round-robin orchestration following AutoGen's RoundRobinGroupChat pattern.
    
    Executes agents in a cyclic manner, where each agent can contribute
    to the conversation. This pattern is useful for collaborative tasks
    where multiple agents need to discuss and refine solutions.
    """

    def __init__(
        self, 
        config: WorkflowConfig,
        termination_condition: Optional[TerminationCondition] = None
    ):
        """Initialize round-robin orchestrator.
        
        Args:
            config: Workflow configuration
            termination_condition: Termination conditions for the orchestration
        """
        super().__init__(config)
        self.agent_manager = get_agent_manager()
        self.termination_condition = termination_condition or TerminationCondition(
            max_rounds=5,  # Default to 5 rounds
            max_messages=20  # Default to 20 messages
        )
        self._execution_task: Optional[asyncio.Task] = None
        self._current_speaker_index = 0
        self._round_count = 0
        self._message_count = 0
        self._start_time: Optional[datetime] = None

    async def execute(self, task: str, **kwargs) -> TaskResult:
        """Execute agents in round-robin fashion.
        
        Args:
            task: Initial task description
            **kwargs: Additional parameters
            
        Returns:
            TaskResult: Final aggregated result
        """
        if self.context.status == WorkflowStatus.RUNNING:
            raise OrchestrationError("Workflow is already running")

        self.logger.info(f"Starting round-robin workflow with {len(self.config.agents)} agents")
        self.context.status = WorkflowStatus.RUNNING
        self._start_time = datetime.now()
        
        try:
            # Create execution task for cancellation support
            self._execution_task = asyncio.create_task(
                self._execute_round_robin_workflow(task, **kwargs)
            )
            
            result = await self._execution_task
            self.context.status = WorkflowStatus.COMPLETED
            return result
            
        except asyncio.CancelledError:
            self.context.status = WorkflowStatus.CANCELLED
            self.logger.info("Round-robin workflow cancelled")
            raise
        except Exception as e:
            self.context.status = WorkflowStatus.FAILED
            self.logger.error(f"Round-robin workflow failed: {e}")
            raise

    async def _execute_round_robin_workflow(self, initial_task: str, **kwargs) -> TaskResult:
        """Execute the round-robin workflow logic."""
        conversation_history = [initial_task]
        last_result = None
        
        while True:
            # Check termination conditions
            execution_time = (datetime.now() - self._start_time).total_seconds()
            if self.termination_condition.should_terminate(
                self._round_count,
                self._message_count,
                execution_time,
                self.context.history
            ):
                self.logger.info(
                    f"Round-robin terminated after {self._round_count} rounds, "
                    f"{self._message_count} messages, {execution_time:.2f}s"
                )
                break
            
            # Select next speaker
            current_agent_id = await self._select_next_speaker()
            self.logger.info(
                f"Round {self._round_count + 1}, Message {self._message_count + 1}: "
                f"Agent {current_agent_id}"
            )
            
            # Prepare context for current agent
            agent_context = {
                "round": self._round_count + 1,
                "message_number": self._message_count + 1,
                "conversation_history": conversation_history[-10:],  # Last 10 messages
                "all_participants": self.config.agents,
                "shared_data": self.context.shared_data,
                **kwargs
            }
            
            # Create conversation context for the agent
            conversation_context = self._build_conversation_context(conversation_history)
            
            # Execute current agent
            result = await self._execute_agent_with_retry(
                current_agent_id,
                conversation_context,
                agent_context
            )
            
            # Update tracking
            self._update_context(result)
            self._message_count += 1
            
            if not result.success:
                if self.config.failure_policy == "fail_fast":
                    raise AgentExecutionError(f"Agent {current_agent_id} failed: {result.error}")
                else:
                    self.logger.warning(f"Agent {current_agent_id} failed, continuing: {result.error}")
                    conversation_history.append(f"[Error from {current_agent_id}: {result.error}]")
            else:
                # Add agent's response to conversation
                if result.result:
                    if isinstance(result.result, str):
                        conversation_history.append(f"{current_agent_id}: {result.result}")
                    else:
                        conversation_history.append(f"{current_agent_id}: {str(result.result)}")
                
                last_result = result
            
            # Update speaker index
            self._current_speaker_index = (self._current_speaker_index + 1) % len(self.config.agents)
            
            # Check if we completed a round
            if self._current_speaker_index == 0:
                self._round_count += 1
                self.logger.info(f"Completed round {self._round_count}")

        if not last_result:
            raise OrchestrationError("No agents executed successfully")
        
        # Create final aggregated result
        return await self._create_final_result(conversation_history)

    async def _select_next_speaker(self) -> str:
        """Select the next speaker in round-robin fashion.
        
        This is a simple round-robin implementation, but could be enhanced
        with more sophisticated speaker selection logic.
        """
        return self.config.agents[self._current_speaker_index]

    def _build_conversation_context(self, conversation_history: List[str]) -> str:
        """Build conversation context for the current agent."""
        if len(conversation_history) <= 1:
            return conversation_history[0] if conversation_history else ""
        
        # Include recent conversation history
        context_parts = [
            "=== Conversation History ===",
            *conversation_history[-5:],  # Last 5 messages
            "=== Your Turn ===",
            "Please continue the conversation based on the above context."
        ]
        
        return "\n".join(context_parts)

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
                    sender="round_robin_orchestrator",
                    metadata={
                        "workflow_id": self.workflow_id,
                        "context": context
                    }
                )
                
                # Execute agent
                result = await self._simulate_agent_execution(agent_id, task_message, context)
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return TaskResult(
                    task_id=f"{self.workflow_id}-{agent_id}-{self._message_count}",
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
                    task_id=f"{self.workflow_id}-{agent_id}-{self._message_count}",
                    agent_id=agent_id,
                    success=False,
                    error=str(e),
                    execution_time=execution_time
                )
        
        raise OrchestrationError(f"Unexpected error in agent execution: {agent_id}")

    async def _simulate_agent_execution(
        self,
        agent_id: str,
        message: BaseChatMessage,
        context: Dict[str, Any]
    ) -> str:
        """Simulate agent execution for testing/demo purposes."""
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        round_num = context.get("round", 1)
        message_num = context.get("message_number", 1)
        
        # Simulate different agent behaviors in round-robin
        if "analyst" in agent_id.lower():
            return f"Analysis from {agent_id} (Round {round_num}): Based on the discussion, I see several key patterns..."
        elif "designer" in agent_id.lower():
            return f"Design perspective from {agent_id} (Round {round_num}): From a UX standpoint, we should consider..."
        elif "developer" in agent_id.lower():
            return f"Technical input from {agent_id} (Round {round_num}): The implementation approach could be..."
        elif "manager" in agent_id.lower():
            return f"Project view from {agent_id} (Round {round_num}): Let's align on priorities and next steps..."
        else:
            return f"Contribution from {agent_id} (Round {round_num}): {message.content[:50]}..."

    async def _create_final_result(self, conversation_history: List[str]) -> TaskResult:
        """Create the final aggregated result from the conversation."""
        # Summarize the conversation
        summary = f"Round-robin conversation completed with {len(self.config.agents)} agents over {self._round_count} rounds.\n"
        summary += f"Total messages: {self._message_count}\n"
        summary += f"Participants: {', '.join(self.config.agents)}\n\n"
        summary += "Key outcomes:\n"
        
        # Extract key points from the last few messages
        if len(conversation_history) > 3:
            summary += "- " + "\n- ".join(conversation_history[-3:])
        
        return TaskResult(
            task_id=f"{self.workflow_id}-final",
            agent_id="round_robin_orchestrator",
            success=True,
            result=summary,
            execution_time=(datetime.now() - self._start_time).total_seconds()
        )

    async def pause(self) -> bool:
        """Pause the round-robin workflow execution."""
        if self.context.status != WorkflowStatus.RUNNING:
            return False
        
        self.context.status = WorkflowStatus.PAUSED
        self.logger.info("Round-robin workflow paused")
        return True

    async def resume(self) -> bool:
        """Resume the paused round-robin workflow execution."""
        if self.context.status != WorkflowStatus.PAUSED:
            return False
        
        self.context.status = WorkflowStatus.RUNNING
        self.logger.info("Round-robin workflow resumed")
        return True

    async def cancel(self) -> bool:
        """Cancel the round-robin workflow execution."""
        if self._execution_task and not self._execution_task.done():
            self._execution_task.cancel()
            
        self.context.status = WorkflowStatus.CANCELLED
        self.logger.info("Round-robin workflow cancelled")
        return True

    async def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state."""
        return {
            "workflow_id": self.workflow_id,
            "current_round": self._round_count,
            "current_speaker_index": self._current_speaker_index,
            "current_speaker": self.config.agents[self._current_speaker_index] if self.config.agents else None,
            "message_count": self._message_count,
            "status": self.context.status,
            "participants": self.config.agents,
            "termination_condition": {
                "max_rounds": self.termination_condition.max_rounds,
                "max_messages": self.termination_condition.max_messages,
                "timeout_seconds": self.termination_condition.timeout_seconds
            }
        }
