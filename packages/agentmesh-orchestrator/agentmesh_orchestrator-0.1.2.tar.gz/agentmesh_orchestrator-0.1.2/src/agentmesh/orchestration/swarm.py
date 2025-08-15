"""Swarm orchestration implementation for autonomous agent coordination."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
import random
from collections import defaultdict

from .base import (
    BaseOrchestrator,
    WorkflowConfig,
    WorkflowStatus,
    TaskResult,
    AgentExecutionError
)
from ..models.message import BaseChatMessage, TextMessage, SystemMessage

logger = logging.getLogger(__name__)


class SwarmStatus(Enum):
    """Status of the swarm coordination."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    CONVERGING = "converging"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


class HandoffType(Enum):
    """Type of agent handoff in swarm."""
    AUTONOMOUS = "autonomous"  # Agent decides to handoff
    BROADCAST = "broadcast"    # Message to all agents
    TARGETED = "targeted"      # Specific agent selection
    RANDOM = "random"          # Random agent selection


@dataclass
class SwarmParticipant:
    """Represents a participant in the swarm."""
    agent_id: str
    name: str
    specializations: List[str] = field(default_factory=list)
    handoff_targets: List[str] = field(default_factory=list)
    participation_weight: float = 1.0
    max_consecutive_turns: Optional[int] = None
    cool_down_period: Optional[timedelta] = None
    last_active: Optional[datetime] = None
    total_messages: int = 0
    successful_handoffs: int = 0
    failed_handoffs: int = 0


@dataclass
class HandoffDecision:
    """Represents a handoff decision made by an agent."""
    from_agent: str
    to_agent: Optional[str]
    handoff_type: HandoffType
    reason: str
    confidence: float
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SwarmMetrics:
    """Metrics for swarm performance analysis."""
    total_messages: int = 0
    total_handoffs: int = 0
    active_participants: int = 0
    avg_response_time: float = 0.0
    participation_distribution: Dict[str, float] = field(default_factory=dict)
    handoff_success_rate: float = 0.0
    convergence_score: float = 0.0
    collaboration_efficiency: float = 0.0


class SwarmOrchestrator(BaseOrchestrator):
    """
    Swarm orchestration engine for autonomous agent coordination.
    
    Implements self-organizing agent behavior where agents autonomously decide
    when and to whom to handoff tasks based on their capabilities and the
    current context.
    """

    def __init__(self, config: WorkflowConfig):
        """Initialize swarm orchestrator.
        
        Args:
            config: Workflow configuration with swarm participants
        """
        super().__init__(config)
        self.participants: Dict[str, SwarmParticipant] = {}
        self.handoff_history: List[HandoffDecision] = []
        self.current_agent: Optional[str] = None
        self.message_count: int = 0
        self.swarm_status: SwarmStatus = SwarmStatus.INITIALIZING
        self.termination_condition: Dict[str, Any] = config.parameters.get('termination', {})
        self.collaboration_graph: Dict[str, Set[str]] = defaultdict(set)
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{self.workflow_id[:8]}")
        
        # Initialize participants from config
        self._initialize_participants()

    def _initialize_participants(self):
        """Initialize swarm participants from configuration."""
        swarm_config = self.config.parameters.get('swarm', {})
        participants_config = swarm_config.get('participants', [])
        
        for participant in participants_config:
            if isinstance(participant, dict):
                agent_id = participant.get('agent_id') or participant.get('name')
                self.participants[agent_id] = SwarmParticipant(
                    agent_id=agent_id,
                    name=participant.get('name', agent_id),
                    specializations=participant.get('specializations', []),
                    handoff_targets=participant.get('handoff_targets', []),
                    participation_weight=participant.get('weight', 1.0),
                    max_consecutive_turns=participant.get('max_consecutive_turns'),
                    cool_down_period=timedelta(seconds=participant.get('cooldown_seconds', 0))
                )
        
        # If no explicit participants, use agents from config
        if not self.participants:
            for agent_id in self.config.agents:
                self.participants[agent_id] = SwarmParticipant(
                    agent_id=agent_id,
                    name=agent_id
                )
        
        self.logger.info(f"Initialized swarm with {len(self.participants)} participants")

    async def execute(self, task: str, **kwargs) -> TaskResult:
        """Execute task using swarm coordination.
        
        Args:
            task: The task to execute
            **kwargs: Additional execution parameters
            
        Returns:
            TaskResult: Result of the swarm execution
        """
        self.logger.info(f"Starting swarm execution for task: {task[:100]}...")
        self.swarm_status = SwarmStatus.ACTIVE
        
        messages = []
        start_time = datetime.utcnow()
        
        try:
            # Initialize with task message
            initial_message = SystemMessage(content=f"Swarm Task: {task}")
            messages.append(initial_message)
            
            # Select initial agent
            self.current_agent = self._select_initial_agent()
            self.logger.info(f"Initial agent selected: {self.current_agent}")
            
            # Execute swarm coordination loop
            while self._should_continue():
                # Get current agent and execute
                agent_result = await self._execute_agent_turn(
                    self.current_agent, 
                    task, 
                    messages
                )
                
                if agent_result.success:
                    messages.extend(agent_result.messages or [])
                    self.message_count += len(agent_result.messages or [])
                    
                    # Update participant stats
                    if self.current_agent in self.participants:
                        self.participants[self.current_agent].total_messages += 1
                        self.participants[self.current_agent].last_active = datetime.utcnow()
                    
                    # Decide on handoff
                    handoff_decision = await self._make_handoff_decision(
                        self.current_agent,
                        agent_result,
                        messages
                    )
                    
                    if handoff_decision:
                        self.handoff_history.append(handoff_decision)
                        
                        if handoff_decision.to_agent:
                            # Successful handoff
                            self._update_collaboration_graph(
                                handoff_decision.from_agent,
                                handoff_decision.to_agent
                            )
                            self.current_agent = handoff_decision.to_agent
                            self.participants[handoff_decision.from_agent].successful_handoffs += 1
                            self.logger.info(
                                f"Handoff: {handoff_decision.from_agent} -> {handoff_decision.to_agent} "
                                f"({handoff_decision.reason})"
                            )
                        else:
                            # Termination requested
                            self.logger.info(f"Termination requested by {handoff_decision.from_agent}")
                            break
                else:
                    # Agent execution failed
                    self.logger.warning(f"Agent {self.current_agent} execution failed: {agent_result.error}")
                    
                    # Try to recover by selecting another agent
                    recovery_agent = self._select_recovery_agent()
                    if recovery_agent and recovery_agent != self.current_agent:
                        self.current_agent = recovery_agent
                        self.logger.info(f"Recovered with agent: {recovery_agent}")
                    else:
                        self.logger.error("No recovery agent available, terminating swarm")
                        break
            
            # Determine final status
            if self._check_success_conditions(messages):
                self.swarm_status = SwarmStatus.COMPLETED
                success = True
                error = None
            else:
                self.swarm_status = SwarmStatus.FAILED
                success = False
                error = "Swarm failed to reach successful conclusion"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Generate swarm metrics
            metrics = self._calculate_swarm_metrics(execution_time)
            
            return TaskResult(
                success=success,
                messages=messages,
                error=error,
                metadata={
                    "swarm_metrics": metrics,
                    "execution_time": execution_time,
                    "total_handoffs": len(self.handoff_history),
                    "participants": list(self.participants.keys()),
                    "final_status": self.swarm_status.value
                }
            )
            
        except Exception as e:
            self.logger.error(f"Swarm execution error: {e}")
            self.swarm_status = SwarmStatus.FAILED
            
            return TaskResult(
                success=False,
                messages=messages,
                error=str(e),
                metadata={
                    "swarm_status": self.swarm_status.value,
                    "handoffs_completed": len(self.handoff_history)
                }
            )

    def _select_initial_agent(self) -> str:
        """Select the initial agent to start the swarm."""
        # Use weighted random selection based on participation weights
        agents = list(self.participants.keys())
        weights = [self.participants[agent].participation_weight for agent in agents]
        
        if weights:
            return random.choices(agents, weights=weights)[0]
        else:
            return agents[0] if agents else self.config.agents[0]

    def _select_recovery_agent(self) -> Optional[str]:
        """Select an agent for error recovery."""
        available_agents = [
            agent_id for agent_id in self.participants.keys()
            if agent_id != self.current_agent and self._is_agent_available(agent_id)
        ]
        
        if available_agents:
            # Select agent with highest participation weight
            return max(available_agents, key=lambda a: self.participants[a].participation_weight)
        
        return None

    def _is_agent_available(self, agent_id: str) -> bool:
        """Check if an agent is available for execution."""
        participant = self.participants.get(agent_id)
        if not participant:
            return False
        
        # Check cooldown period
        if participant.cool_down_period and participant.last_active:
            time_since_active = datetime.utcnow() - participant.last_active
            if time_since_active < participant.cool_down_period:
                return False
        
        return True

    async def _execute_agent_turn(
        self, 
        agent_id: str, 
        task: str, 
        messages: List[BaseChatMessage]
    ) -> TaskResult:
        """Execute a single agent turn."""
        # This is a placeholder - in real implementation, this would
        # interface with actual agents
        self.logger.info(f"Executing agent turn: {agent_id}")
        
        # Simulate agent execution
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Create mock response
        response_message = TextMessage(
            content=f"Agent {agent_id} processed the task",
            source=agent_id
        )
        
        return TaskResult(
            success=True,
            messages=[response_message],
            metadata={"agent_id": agent_id}
        )

    async def _make_handoff_decision(
        self,
        current_agent: str,
        agent_result: TaskResult,
        messages: List[BaseChatMessage]
    ) -> Optional[HandoffDecision]:
        """Make autonomous handoff decision."""
        # Check termination conditions first
        if self._check_termination_conditions():
            return HandoffDecision(
                from_agent=current_agent,
                to_agent=None,
                handoff_type=HandoffType.AUTONOMOUS,
                reason="Termination condition met",
                confidence=1.0
            )
        
        # Simple handoff logic - in real implementation, this would be more sophisticated
        participant = self.participants[current_agent]
        
        # Check if agent wants to continue or handoff
        should_handoff = (
            len(participant.handoff_targets) > 0 and
            random.random() < 0.3  # 30% chance of handoff
        )
        
        if should_handoff:
            # Select target agent
            available_targets = [
                target for target in participant.handoff_targets
                if self._is_agent_available(target)
            ]
            
            if available_targets:
                target_agent = random.choice(available_targets)
                return HandoffDecision(
                    from_agent=current_agent,
                    to_agent=target_agent,
                    handoff_type=HandoffType.AUTONOMOUS,
                    reason="Autonomous handoff decision",
                    confidence=0.7
                )
        
        return None

    def _should_continue(self) -> bool:
        """Check if swarm should continue execution."""
        return (
            self.swarm_status == SwarmStatus.ACTIVE and
            not self._check_termination_conditions()
        )

    def _check_termination_conditions(self) -> bool:
        """Check if any termination conditions are met."""
        if not self.termination_condition:
            return self.message_count >= 10  # Default limit
        
        max_messages = self.termination_condition.get('max_messages')
        if max_messages and self.message_count >= max_messages:
            return True
        
        max_handoffs = self.termination_condition.get('max_handoffs')
        if max_handoffs and len(self.handoff_history) >= max_handoffs:
            return True
        
        timeout = self.termination_condition.get('timeout_seconds')
        if timeout:
            elapsed = (datetime.utcnow() - self.context.created_at).total_seconds()
            if elapsed >= timeout:
                return True
        
        return False

    def _check_success_conditions(self, messages: List[BaseChatMessage]) -> bool:
        """Check if swarm execution was successful."""
        # Simple success check - at least some messages and no critical errors
        return len(messages) > 1 and self.message_count > 0

    def _update_collaboration_graph(self, from_agent: str, to_agent: str):
        """Update the collaboration graph with handoff information."""
        self.collaboration_graph[from_agent].add(to_agent)

    def _calculate_swarm_metrics(self, execution_time: float) -> SwarmMetrics:
        """Calculate comprehensive swarm metrics."""
        total_messages = sum(p.total_messages for p in self.participants.values())
        total_handoffs = len(self.handoff_history)
        active_participants = len([p for p in self.participants.values() if p.total_messages > 0])
        
        # Calculate participation distribution
        participation_dist = {}
        if total_messages > 0:
            for agent_id, participant in self.participants.items():
                participation_dist[agent_id] = participant.total_messages / total_messages
        
        # Calculate handoff success rate
        successful_handoffs = sum(p.successful_handoffs for p in self.participants.values())
        total_handoff_attempts = successful_handoffs + sum(p.failed_handoffs for p in self.participants.values())
        handoff_success_rate = successful_handoffs / total_handoff_attempts if total_handoff_attempts > 0 else 0.0
        
        # Simple collaboration efficiency metric
        collaboration_efficiency = min(1.0, active_participants / len(self.participants)) if self.participants else 0.0
        
        return SwarmMetrics(
            total_messages=total_messages,
            total_handoffs=total_handoffs,
            active_participants=active_participants,
            avg_response_time=execution_time / max(1, total_messages),
            participation_distribution=participation_dist,
            handoff_success_rate=handoff_success_rate,
            convergence_score=0.8 if self.swarm_status == SwarmStatus.COMPLETED else 0.3,
            collaboration_efficiency=collaboration_efficiency
        )

    def get_swarm_state(self) -> Dict[str, Any]:
        """Get current swarm state for monitoring."""
        return {
            "status": self.swarm_status.value,
            "current_agent": self.current_agent,
            "message_count": self.message_count,
            "handoff_count": len(self.handoff_history),
            "participants": {
                agent_id: {
                    "messages": participant.total_messages,
                    "successful_handoffs": participant.successful_handoffs,
                    "last_active": participant.last_active.isoformat() if participant.last_active else None
                }
                for agent_id, participant in self.participants.items()
            },
            "collaboration_graph": {
                agent: list(targets) for agent, targets in self.collaboration_graph.items()
            }
        }

    def get_handoff_patterns(self) -> Dict[str, Any]:
        """Analyze handoff patterns in the swarm."""
        handoff_matrix = defaultdict(lambda: defaultdict(int))
        
        for handoff in self.handoff_history:
            if handoff.to_agent:
                handoff_matrix[handoff.from_agent][handoff.to_agent] += 1
        
        return {
            "handoff_matrix": dict(handoff_matrix),
            "most_active_handoffers": sorted(
                self.participants.items(),
                key=lambda x: x[1].successful_handoffs,
                reverse=True
            )[:3],
            "handoff_frequency": len(self.handoff_history) / max(1, self.message_count)
        }

    async def get_swarm_metrics(self) -> SwarmMetrics:
        """Get current swarm metrics."""
        if not self.metrics:
            return SwarmMetrics()
        return self.metrics
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive swarm analytics."""
        metrics = await self.get_swarm_metrics()
        handoff_patterns = self.get_handoff_patterns()
        
        # Calculate efficiency scores
        efficiency_scores = {}
        if metrics.total_messages > 0:
            efficiency_scores["messages_per_handoff"] = metrics.total_messages / max(metrics.total_handoffs, 1)
        if metrics.agent_participation_rates:
            efficiency_scores["participation_balance"] = (
                1.0 - (max(metrics.agent_participation_rates.values()) - 
                       min(metrics.agent_participation_rates.values()))
            )
        
        return {
            "performance_metrics": {
                "total_messages": metrics.total_messages,
                "total_handoffs": metrics.total_handoffs,
                "autonomous_handoffs": metrics.autonomous_handoffs,
                "avg_response_time": metrics.avg_response_time,
                "convergence_score": metrics.convergence_score
            },
            "handoff_patterns": handoff_patterns,
            "agent_statistics": {
                "participation_rates": metrics.agent_participation_rates,
                "active_agents": list(metrics.active_agents),
                "agent_count": len(self.participants)
            },
            "efficiency_scores": efficiency_scores
        }
    
    async def tune_parameter(self, parameter: str, value: float) -> bool:
        """Tune swarm parameters during execution."""
        try:
            if parameter == "participation_balance":
                # Adjust participation weights to balance load
                if self.participants:
                    avg_weight = sum(p.participation_weight for p in self.participants) / len(self.participants)
                    for participant in self.participants:
                        if participant.participation_weight < avg_weight:
                            participant.participation_weight = min(participant.participation_weight * (1 + value), 2.0)
                        else:
                            participant.participation_weight = max(participant.participation_weight * (1 - value), 0.5)
                return True
                
            elif parameter == "handoff_frequency":
                # Adjust handoff threshold - affects when agents decide to hand off
                self._handoff_threshold = max(0.1, min(1.0, value))
                return True
                
            elif parameter == "convergence_threshold":
                # Adjust convergence detection threshold
                self._convergence_threshold = max(0.1, min(1.0, value))
                return True
                
            else:
                logger.warning(f"Unknown parameter for tuning: {parameter}")
                return False
                
        except Exception as e:
            logger.error(f"Error tuning parameter {parameter}: {e}")
            return False
    
    async def get_parameter(self, parameter: str) -> Optional[float]:
        """Get current value of a tunable parameter."""
        try:
            if parameter == "participation_balance":
                if not self.participants:
                    return None
                weights = [p.participation_weight for p in self.participants]
                return 1.0 - (max(weights) - min(weights)) if weights else None
                
            elif parameter == "handoff_frequency":
                return getattr(self, '_handoff_threshold', 0.5)
                
            elif parameter == "convergence_threshold":
                return getattr(self, '_convergence_threshold', 0.8)
                
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting parameter {parameter}: {e}")
            return None
    
    async def get_handoff_graph(self) -> Dict[str, Any]:
        """Get handoff graph for visualization."""
        nodes = {}
        edges = {}
        
        # Create nodes for each participant
        for participant in self.participants:
            nodes[participant.agent_id] = {
                "id": participant.agent_id,
                "name": participant.name,
                "specializations": participant.specializations,
                "participation_rate": self.metrics.agent_participation_rates.get(participant.agent_id, 0.0) if self.metrics else 0.0,
                "is_active": participant.agent_id in (self.metrics.active_agents if self.metrics else set())
            }
        
        # Create edges from handoff patterns
        handoff_patterns = self.get_handoff_patterns()
        edge_id = 0
        for source_agent, targets in handoff_patterns.get("direct_handoffs", {}).items():
            for target_agent, count in targets.items():
                edge_id += 1
                edges[f"edge_{edge_id}"] = {
                    "id": f"edge_{edge_id}",
                    "source": source_agent,
                    "target": target_agent,
                    "weight": count,
                    "type": "handoff"
                }
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_participants": len(self.participants),
                "total_handoffs": self.metrics.total_handoffs if self.metrics else 0,
                "last_updated": datetime.now().isoformat()
            }
        }

    async def cancel(self) -> bool:
        """Cancel the swarm execution."""
        try:
            self.status = SwarmStatus.TERMINATED
            logger.info(f"Swarm {self.execution_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling swarm: {e}")
            return False
    
    async def pause(self) -> bool:
        """Pause the swarm execution."""
        try:
            if self.status == SwarmStatus.ACTIVE:
                self._paused = True
                logger.info(f"Swarm {self.execution_id} paused")
                return True
            return False
        except Exception as e:
            logger.error(f"Error pausing swarm: {e}")
            return False
    
    async def resume(self) -> bool:
        """Resume the swarm execution."""
        try:
            if getattr(self, '_paused', False):
                self._paused = False
                logger.info(f"Swarm {self.execution_id} resumed")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resuming swarm: {e}")
            return False
