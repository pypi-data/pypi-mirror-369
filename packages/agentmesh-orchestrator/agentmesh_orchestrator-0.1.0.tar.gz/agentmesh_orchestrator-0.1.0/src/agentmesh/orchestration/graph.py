"""Graph-based workflow orchestration implementation."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field

from .base import (
    BaseOrchestrator,
    WorkflowConfig,
    WorkflowStatus,
    TaskResult,
    AgentExecutionError
)
from ..models.message import BaseChatMessage, TextMessage, SystemMessage

logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    """Status of a workflow node."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class EdgeType(Enum):
    """Type of workflow edge."""
    SEQUENTIAL = "sequential"  # Simple sequential execution
    CONDITIONAL = "conditional"  # Based on condition evaluation
    PARALLEL = "parallel"  # Parallel execution trigger
    SYNCHRONIZE = "synchronize"  # Wait for multiple paths


@dataclass
class WorkflowNode:
    """Represents a node in the workflow graph."""
    node_id: str
    agent_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    status: NodeStatus = NodeStatus.PENDING
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowEdge:
    """Represents an edge in the workflow graph."""
    edge_id: str
    source_node: str
    target_node: str
    edge_type: EdgeType = EdgeType.SEQUENTIAL
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    condition_data: Optional[Dict[str, Any]] = None
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParallelExecution:
    """Tracks parallel execution branches."""
    branch_id: str
    nodes: List[str]
    synchronization_node: Optional[str] = None
    completed_nodes: Set[str] = field(default_factory=set)
    failed_nodes: Set[str] = field(default_factory=set)


class GraphOrchestrator(BaseOrchestrator):
    """
    Graph-based workflow orchestrator with conditional branching and parallel execution.
    
    Supports:
    - Conditional branching based on message content or agent responses
    - Parallel execution of independent workflow paths
    - Synchronization points for parallel paths
    - Dynamic workflow modification during execution
    - Complex dependency management
    """

    def __init__(self, config: WorkflowConfig):
        """Initialize graph orchestrator.
        
        Args:
            config: Workflow configuration
        """
        super().__init__(config)
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: Dict[str, WorkflowEdge] = {}
        self.execution_graph: Dict[str, List[str]] = {}  # adjacency list
        self.reverse_graph: Dict[str, List[str]] = {}  # reverse adjacency list
        self.parallel_executions: Dict[str, ParallelExecution] = {}
        self.current_nodes: Set[str] = set()  # currently executing nodes
        self.completed_nodes: Set[str] = set()
        self.failed_nodes: Set[str] = set()
        self.execution_context: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    def add_node(
        self,
        node_id: str,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        max_retries: int = 3
    ) -> WorkflowNode:
        """Add a node to the workflow graph.
        
        Args:
            node_id: Unique node identifier
            agent_id: ID of the agent to execute this node
            name: Human-readable node name
            description: Node description
            max_retries: Maximum retry attempts
            
        Returns:
            WorkflowNode: Created node
        """
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists")
        
        node = WorkflowNode(
            node_id=node_id,
            agent_id=agent_id,
            name=name or node_id,
            description=description,
            max_retries=max_retries
        )
        
        self.nodes[node_id] = node
        self.execution_graph[node_id] = []
        self.reverse_graph[node_id] = []
        
        self.logger.info(f"Added node: {node_id} -> {agent_id}")
        return node

    def add_edge(
        self,
        edge_id: str,
        source_node: str,
        target_node: str,
        edge_type: EdgeType = EdgeType.SEQUENTIAL,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        condition_data: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowEdge:
        """Add an edge to the workflow graph.
        
        Args:
            edge_id: Unique edge identifier
            source_node: Source node ID
            target_node: Target node ID
            edge_type: Type of edge (sequential, conditional, etc.)
            condition: Condition function for conditional edges
            condition_data: Data for condition evaluation
            weight: Edge weight for priority
            metadata: Additional edge metadata
            
        Returns:
            WorkflowEdge: Created edge
        """
        if edge_id in self.edges:
            raise ValueError(f"Edge {edge_id} already exists")
        
        if source_node not in self.nodes:
            raise ValueError(f"Source node {source_node} does not exist")
        
        if target_node not in self.nodes:
            raise ValueError(f"Target node {target_node} does not exist")
        
        edge = WorkflowEdge(
            edge_id=edge_id,
            source_node=source_node,
            target_node=target_node,
            edge_type=edge_type,
            condition=condition,
            condition_data=condition_data or {},
            weight=weight,
            metadata=metadata or {}
        )
        
        self.edges[edge_id] = edge
        self.execution_graph[source_node].append(target_node)
        self.reverse_graph[target_node].append(source_node)
        
        self.logger.info(f"Added edge: {source_node} -> {target_node} ({edge_type.value})")
        return edge

    def add_parallel_branch(
        self,
        branch_id: str,
        nodes: List[str],
        synchronization_node: Optional[str] = None
    ) -> ParallelExecution:
        """Add a parallel execution branch.
        
        Args:
            branch_id: Unique branch identifier
            nodes: List of nodes that can execute in parallel
            synchronization_node: Optional node that waits for all parallel nodes
            
        Returns:
            ParallelExecution: Created parallel execution
        """
        if branch_id in self.parallel_executions:
            raise ValueError(f"Parallel branch {branch_id} already exists")
        
        # Validate nodes exist
        for node_id in nodes:
            if node_id not in self.nodes:
                raise ValueError(f"Node {node_id} does not exist")
        
        if synchronization_node and synchronization_node not in self.nodes:
            raise ValueError(f"Synchronization node {synchronization_node} does not exist")
        
        parallel_exec = ParallelExecution(
            branch_id=branch_id,
            nodes=nodes,
            synchronization_node=synchronization_node
        )
        
        self.parallel_executions[branch_id] = parallel_exec
        
        self.logger.info(f"Added parallel branch: {branch_id} with {len(nodes)} nodes")
        return parallel_exec

    def get_ready_nodes(self) -> List[str]:
        """Get nodes that are ready to execute.
        
        Returns:
            List[str]: List of node IDs ready for execution
        """
        ready_nodes = []
        
        for node_id, node in self.nodes.items():
            if node.status != NodeStatus.PENDING:
                continue
            
            # Check if all dependencies are satisfied
            dependencies = self.reverse_graph.get(node_id, [])
            if not dependencies:
                # No dependencies, ready to start
                ready_nodes.append(node_id)
                continue
            
            # Check conditional and parallel dependencies
            can_execute = True
            for dep_node_id in dependencies:
                dep_node = self.nodes[dep_node_id]
                
                # Find the edge between dependency and this node
                edge = self._find_edge(dep_node_id, node_id)
                if not edge:
                    continue
                
                if edge.edge_type == EdgeType.SEQUENTIAL:
                    # Sequential dependency must be completed
                    if dep_node.status != NodeStatus.COMPLETED:
                        can_execute = False
                        break
                
                elif edge.edge_type == EdgeType.CONDITIONAL:
                    # Conditional dependency must be completed and condition satisfied
                    if dep_node.status != NodeStatus.COMPLETED:
                        can_execute = False
                        break
                    
                    if edge.condition and not self._evaluate_condition(edge, dep_node.output_data):
                        can_execute = False
                        break
                
                elif edge.edge_type == EdgeType.PARALLEL:
                    # For parallel edges, dependency should be completed or running
                    if dep_node.status not in [NodeStatus.COMPLETED, NodeStatus.RUNNING]:
                        can_execute = False
                        break
            
            if can_execute:
                ready_nodes.append(node_id)
        
        return ready_nodes

    def _find_edge(self, source_node: str, target_node: str) -> Optional[WorkflowEdge]:
        """Find edge between two nodes."""
        for edge in self.edges.values():
            if edge.source_node == source_node and edge.target_node == target_node:
                return edge
        return None

    def _evaluate_condition(self, edge: WorkflowEdge, output_data: Optional[Dict[str, Any]]) -> bool:
        """Evaluate edge condition."""
        if not edge.condition:
            return True
        
        try:
            # Prepare condition data
            condition_input = {
                "output_data": output_data or {},
                "condition_data": edge.condition_data or {},
                "execution_context": self.execution_context
            }
            
            return edge.condition(condition_input)
        
        except Exception as e:
            self.logger.error(f"Condition evaluation failed for edge {edge.edge_id}: {e}")
            return False

    async def execute(self, task: str, **kwargs) -> TaskResult:
        """Execute the graph workflow.
        
        Args:
            task: Task description
            **kwargs: Additional execution parameters
            
        Returns:
            TaskResult: Execution result
        """
        self.logger.info(f"Starting graph workflow execution: {self.config.name}")
        
        start_time = datetime.now()
        messages: List[BaseChatMessage] = []
        
        try:
            # Initialize execution context
            self.execution_context.update({
                "task": task,
                "start_time": start_time,
                "parameters": kwargs
            })
            
            # Add initial system message
            messages.append(SystemMessage(
                content=f"Starting graph workflow: {self.config.name}",
                sender="system",
                metadata={"task": task}
            ))
            
            # Reset node statuses
            for node in self.nodes.values():
                node.status = NodeStatus.PENDING
                node.retry_count = 0
                node.started_at = None
                node.completed_at = None
                node.error = None
            
            self.current_nodes.clear()
            self.completed_nodes.clear()
            self.failed_nodes.clear()
            
            # Execute workflow
            while True:
                ready_nodes = self.get_ready_nodes()
                
                if not ready_nodes and not self.current_nodes:
                    # No more nodes to execute
                    break
                
                # Start ready nodes
                for node_id in ready_nodes:
                    if node_id not in self.current_nodes:
                        await self._start_node_execution(node_id, task, messages)
                
                # Wait for at least one node to complete
                if self.current_nodes:
                    await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                    await self._check_running_nodes(messages)
            
            # Check final status
            if self.failed_nodes:
                error_msg = f"Workflow failed. Failed nodes: {', '.join(self.failed_nodes)}"
                self.logger.error(error_msg)
                
                return TaskResult(
                    success=False,
                    messages=messages,
                    error=error_msg,
                    metadata={
                        "completed_nodes": list(self.completed_nodes),
                        "failed_nodes": list(self.failed_nodes),
                        "execution_time": (datetime.now() - start_time).total_seconds()
                    }
                )
            
            self.logger.info(f"Graph workflow completed successfully. Nodes: {len(self.completed_nodes)}")
            
            return TaskResult(
                success=True,
                messages=messages,
                metadata={
                    "completed_nodes": list(self.completed_nodes),
                    "execution_time": (datetime.now() - start_time).total_seconds(),
                    "final_context": self.execution_context
                }
            )
        
        except Exception as e:
            error_msg = f"Graph workflow execution failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return TaskResult(
                success=False,
                messages=messages,
                error=error_msg,
                metadata={
                    "completed_nodes": list(self.completed_nodes),
                    "failed_nodes": list(self.failed_nodes),
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            )

    async def _start_node_execution(
        self,
        node_id: str,
        task: str,
        messages: List[BaseChatMessage]
    ) -> None:
        """Start execution of a node."""
        node = self.nodes[node_id]
        node.status = NodeStatus.RUNNING
        node.started_at = datetime.now()
        
        self.current_nodes.add(node_id)
        
        self.logger.info(f"Starting node execution: {node_id} ({node.agent_id})")
        
        # Create node-specific task based on dependencies
        node_task = self._prepare_node_task(node_id, task)
        
        # Start async execution (simulation for now)
        asyncio.create_task(self._execute_node(node_id, node_task, messages))

    def _prepare_node_task(self, node_id: str, original_task: str) -> str:
        """Prepare task for specific node based on dependencies and context."""
        node = self.nodes[node_id]
        
        # Collect input from dependency nodes
        dependency_outputs = []
        dependencies = self.reverse_graph.get(node_id, [])
        
        for dep_node_id in dependencies:
            dep_node = self.nodes[dep_node_id]
            if dep_node.status == NodeStatus.COMPLETED and dep_node.output_data:
                dependency_outputs.append(f"Output from {dep_node.name}: {dep_node.output_data}")
        
        # Prepare contextualized task
        if dependency_outputs:
            contextualized_task = f"{original_task}\n\nPrevious outputs:\n" + "\n".join(dependency_outputs)
        else:
            contextualized_task = original_task
        
        return contextualized_task

    async def _execute_node(
        self,
        node_id: str,
        task: str,
        messages: List[BaseChatMessage]
    ) -> None:
        """Execute a single node (simulated for now)."""
        node = self.nodes[node_id]
        
        try:
            # Simulate agent execution
            await asyncio.sleep(1)  # Simulate processing time
            
            # Simulate different outcomes based on node name
            if "fail" in node.name.lower():
                raise Exception(f"Simulated failure in node {node_id}")
            
            # Simulate successful execution
            output_data = {
                "result": f"Completed task: {task}",
                "node_id": node_id,
                "agent_id": node.agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            node.output_data = output_data
            node.status = NodeStatus.COMPLETED
            node.completed_at = datetime.now()
            
            # Add to messages
            messages.append(TextMessage(
                content=f"Node {node.name} completed: {output_data['result']}",
                sender=node.agent_id,
                metadata={"node_id": node_id, "output_data": output_data}
            ))
            
            self.completed_nodes.add(node_id)
            self.current_nodes.discard(node_id)
            
            self.logger.info(f"Node completed: {node_id}")
        
        except Exception as e:
            await self._handle_node_failure(node_id, str(e), messages)

    async def _handle_node_failure(
        self,
        node_id: str,
        error: str,
        messages: List[BaseChatMessage]
    ) -> None:
        """Handle node execution failure."""
        node = self.nodes[node_id]
        node.retry_count += 1
        node.error = error
        
        self.logger.warning(f"Node {node_id} failed (attempt {node.retry_count}): {error}")
        
        if node.retry_count < node.max_retries:
            # Retry the node
            self.logger.info(f"Retrying node {node_id} (attempt {node.retry_count + 1})")
            await asyncio.sleep(1)  # Brief delay before retry
            await self._execute_node(node_id, self._prepare_node_task(node_id, self.execution_context.get("task", "")), messages)
        else:
            # Mark as failed
            node.status = NodeStatus.FAILED
            node.completed_at = datetime.now()
            
            messages.append(TextMessage(
                content=f"Node {node.name} failed after {node.max_retries} attempts: {error}",
                sender="system",
                metadata={"node_id": node_id, "error": error}
            ))
            
            self.failed_nodes.add(node_id)
            self.current_nodes.discard(node_id)

    async def _check_running_nodes(self, messages: List[BaseChatMessage]) -> None:
        """Check status of running nodes and update parallel executions."""
        # Check parallel execution synchronization
        for parallel_exec in self.parallel_executions.values():
            if parallel_exec.synchronization_node:
                sync_node = self.nodes[parallel_exec.synchronization_node]
                
                # Check if all parallel nodes are completed
                all_completed = all(
                    node_id in self.completed_nodes or node_id in self.failed_nodes
                    for node_id in parallel_exec.nodes
                )
                
                if all_completed and sync_node.status == NodeStatus.PENDING:
                    # Mark synchronization node as ready
                    sync_node.status = NodeStatus.READY

    async def pause(self) -> bool:
        """Pause workflow execution."""
        self.status = WorkflowStatus.PAUSED
        # In a real implementation, this would pause all running nodes
        self.logger.info("Graph workflow paused")
        return True

    async def resume(self) -> bool:
        """Resume workflow execution."""
        self.status = WorkflowStatus.RUNNING
        # In a real implementation, this would resume all paused nodes
        self.logger.info("Graph workflow resumed")
        return True

    async def cancel(self) -> bool:
        """Cancel workflow execution."""
        self.status = WorkflowStatus.CANCELLED
        # Cancel all running nodes
        for node_id in list(self.current_nodes):
            node = self.nodes[node_id]
            node.status = NodeStatus.FAILED
            node.error = "Workflow cancelled"
            self.current_nodes.discard(node_id)
            self.failed_nodes.add(node_id)
        
        self.logger.info("Graph workflow cancelled")
        return True

    def get_execution_graph(self) -> Dict[str, Any]:
        """Get current execution graph state.
        
        Returns:
            Dict with nodes, edges, and current execution state
        """
        return {
            "nodes": {
                node_id: {
                    "agent_id": node.agent_id,
                    "name": node.name,
                    "status": node.status.value,
                    "started_at": node.started_at.isoformat() if node.started_at else None,
                    "completed_at": node.completed_at.isoformat() if node.completed_at else None,
                    "retry_count": node.retry_count,
                    "error": node.error
                }
                for node_id, node in self.nodes.items()
            },
            "edges": {
                edge_id: {
                    "source_node": edge.source_node,
                    "target_node": edge.target_node,
                    "edge_type": edge.edge_type.value,
                    "weight": edge.weight,
                    "metadata": edge.metadata
                }
                for edge_id, edge in self.edges.items()
            },
            "parallel_executions": {
                branch_id: {
                    "nodes": parallel_exec.nodes,
                    "synchronization_node": parallel_exec.synchronization_node,
                    "completed_nodes": list(parallel_exec.completed_nodes),
                    "failed_nodes": list(parallel_exec.failed_nodes)
                }
                for branch_id, parallel_exec in self.parallel_executions.items()
            },
            "execution_state": {
                "current_nodes": list(self.current_nodes),
                "completed_nodes": list(self.completed_nodes),
                "failed_nodes": list(self.failed_nodes),
                "status": self.status.value
            }
        }

    def get_graph_structure(self) -> Dict[str, Any]:
        """Get the graph structure in a format suitable for visualization."""
        nodes = [
            {
                "id": node.node_id,
                "agent_id": node.agent_id,
                "name": node.name or node.agent_id,
                "description": node.description,
                "status": node.status.value,
                "position": self._calculate_node_position(node.node_id),
                "metadata": {
                    "retry_count": node.retry_count,
                    "max_retries": node.max_retries,
                    "started_at": node.started_at.isoformat() if node.started_at else None,
                    "completed_at": node.completed_at.isoformat() if node.completed_at else None
                }
            }
            for node in self.nodes.values()
        ]
        
        edges = [
            {
                "id": edge.edge_id,
                "source": edge.source_node,
                "target": edge.target_node,
                "type": edge.edge_type.value,
                "weight": edge.weight,
                "metadata": edge.metadata,
                "condition": str(edge.condition.__name__) if edge.condition else None
            }
            for edge in self.edges.values()
        ]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "parallel_branches": [
                {
                    "id": branch_id,
                    "nodes": branch.nodes,
                    "sync_node": branch.synchronization_node,
                    "completed": list(branch.completed_nodes),
                    "failed": list(branch.failed_nodes)
                }
                for branch_id, branch in self.parallel_executions.items()
            ]
        }
    
    def get_execution_state(self) -> Dict[str, Any]:
        """Get current execution state for monitoring."""
        return {
            "workflow_id": self.config.name,
            "status": self.status.value,
            "current_nodes": [
                {
                    "node_id": node_id,
                    "agent_id": self.nodes[node_id].agent_id,
                    "status": self.nodes[node_id].status.value,
                    "started_at": self.nodes[node_id].started_at.isoformat() if self.nodes[node_id].started_at else None
                }
                for node_id in self.current_nodes
            ],
            "progress": {
                "total_nodes": len(self.nodes),
                "completed_nodes": len(self.completed_nodes),
                "failed_nodes": len(self.failed_nodes),
                "pending_nodes": len([n for n in self.nodes.values() if n.status == NodeStatus.PENDING]),
                "progress_percentage": (len(self.completed_nodes) / len(self.nodes) * 100) if self.nodes else 0
            },
            "parallel_executions": {
                branch_id: {
                    "active": len(branch.nodes) > len(branch.completed_nodes) + len(branch.failed_nodes),
                    "progress": len(branch.completed_nodes) / len(branch.nodes) * 100 if branch.nodes else 0
                }
                for branch_id, branch in self.parallel_executions.items()
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history for analysis."""
        history = []
        
        # Add node execution history
        for node in self.nodes.values():
            if node.started_at:
                history.append({
                    "timestamp": node.started_at.isoformat(),
                    "event_type": "node_started",
                    "node_id": node.node_id,
                    "agent_id": node.agent_id,
                    "data": {
                        "input_data": node.input_data,
                        "retry_count": node.retry_count
                    }
                })
            
            if node.completed_at:
                history.append({
                    "timestamp": node.completed_at.isoformat(),
                    "event_type": "node_completed" if node.status == NodeStatus.COMPLETED else "node_failed",
                    "node_id": node.node_id,
                    "agent_id": node.agent_id,
                    "data": {
                        "output_data": node.output_data,
                        "error": node.error,
                        "duration": (node.completed_at - node.started_at).total_seconds() if node.started_at else None
                    }
                })
        
        # Add parallel execution events
        for branch_id, branch in self.parallel_executions.items():
            if branch.completed_nodes:
                history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": "parallel_branch_progress",
                    "branch_id": branch_id,
                    "data": {
                        "completed_nodes": list(branch.completed_nodes),
                        "failed_nodes": list(branch.failed_nodes),
                        "progress": len(branch.completed_nodes) / len(branch.nodes) * 100
                    }
                })
        
        # Sort by timestamp
        history.sort(key=lambda x: x["timestamp"])
        return history
    
    def _calculate_node_position(self, node_id: str) -> Dict[str, float]:
        """Calculate node position for visualization (simplified layout)."""
        # Simple grid layout - in a real implementation, you'd use a proper graph layout algorithm
        nodes_list = list(self.nodes.keys())
        if node_id not in nodes_list:
            return {"x": 0, "y": 0}
        
        index = nodes_list.index(node_id)
        cols = max(3, int(len(nodes_list) ** 0.5))
        
        return {
            "x": (index % cols) * 150,
            "y": (index // cols) * 100
        }
