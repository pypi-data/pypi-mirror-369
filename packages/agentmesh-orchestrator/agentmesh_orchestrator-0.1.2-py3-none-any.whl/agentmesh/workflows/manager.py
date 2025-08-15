"""Workflow management and execution."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from uuid import uuid4

from ..core.agent_manager import get_agent_manager
from ..orchestration.base import (
    BaseOrchestrator,
    OrchestrationPattern,
    WorkflowConfig,
    WorkflowStatus,
    TaskResult
)
from ..orchestration.sequential import SequentialOrchestrator
from ..orchestration.round_robin import RoundRobinOrchestrator
from ..orchestration.graph import GraphOrchestrator
from ..orchestration.swarm import SwarmOrchestrator
from .config import (
    WorkflowConfigFile,
    WorkflowConfigManager,
    get_config_manager
)

logger = logging.getLogger(__name__)


class WorkflowExecution(BaseOrchestrator):
    """Workflow execution wrapper that delegates to specific orchestrators."""
    
    def __init__(
        self,
        config: WorkflowConfig,
        orchestrator: BaseOrchestrator
    ):
        """Initialize workflow execution.
        
        Args:
            config: Workflow configuration
            orchestrator: Specific orchestrator implementation
        """
        super().__init__(config)
        self.orchestrator = orchestrator
        self.execution_id = str(uuid4())
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    async def execute(self, task: str, **kwargs) -> TaskResult:
        """Execute the workflow."""
        self.started_at = datetime.now()
        try:
            result = await self.orchestrator.execute(task, **kwargs)
            self.completed_at = datetime.now()
            return result
        except Exception as e:
            self.completed_at = datetime.now()
            raise

    async def pause(self) -> bool:
        """Pause workflow execution."""
        return await self.orchestrator.pause()

    async def resume(self) -> bool:
        """Resume workflow execution."""
        return await self.orchestrator.resume()

    async def cancel(self) -> bool:
        """Cancel workflow execution."""
        return await self.orchestrator.cancel()

    async def get_execution_info(self) -> Dict[str, Any]:
        """Get detailed execution information."""
        progress = await self.orchestrator.get_progress()
        
        execution_info = {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "config": self.config.dict(),
            "status": await self.orchestrator.get_status(),
            "progress": progress,
            "timing": {
                "created_at": self.created_at.isoformat(),
                "started_at": self.started_at.isoformat() if self.started_at else None,
                "completed_at": self.completed_at.isoformat() if self.completed_at else None,
                "duration_seconds": (
                    (self.completed_at - self.started_at).total_seconds()
                    if self.started_at and self.completed_at
                    else None
                )
            }
        }
        
        # Add graph-specific information for graph workflows
        if hasattr(self.orchestrator, 'get_execution_graph'):
            execution_info["execution_graph"] = self.orchestrator.get_execution_graph()
        
        return execution_info


class WorkflowManager:
    """Manager for workflow creation and execution."""
    
    def __init__(self):
        """Initialize workflow manager."""
        self.config_manager = get_config_manager()
        self.agent_manager = get_agent_manager()
        self.active_workflows: Dict[str, WorkflowExecution] = {}
        self.completed_workflows: Dict[str, WorkflowExecution] = {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    async def create_workflow_from_config(
        self,
        config_file: WorkflowConfigFile,
        agent_id_mapping: Optional[Dict[str, str]] = None
    ) -> WorkflowExecution:
        """Create workflow from configuration file.
        
        Args:
            config_file: Workflow configuration
            agent_id_mapping: Optional mapping from agent names to IDs
            
        Returns:
            WorkflowExecution: Created workflow execution
        """
        # Validate configuration
        errors = self.config_manager.validate_config(config_file)
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        # Resolve agent IDs
        if agent_id_mapping is None:
            agent_id_mapping = await self._build_agent_id_mapping()
        
        # Convert to orchestration config
        orchestration_config = self.config_manager.convert_to_orchestration_config(
            config_file, agent_id_mapping
        )
        
        # Create appropriate orchestrator
        orchestrator = await self._create_orchestrator(config_file, orchestration_config)
        
        # Create workflow execution
        workflow = WorkflowExecution(orchestration_config, orchestrator)
        
        self.logger.info(f"Created workflow: {workflow.workflow_id} ({config_file.pattern})")
        return workflow

    async def create_workflow_from_file(
        self,
        file_path: Union[str, Path],
        agent_id_mapping: Optional[Dict[str, str]] = None
    ) -> WorkflowExecution:
        """Create workflow from configuration file.
        
        Args:
            file_path: Path to configuration file
            agent_id_mapping: Optional mapping from agent names to IDs
            
        Returns:
            WorkflowExecution: Created workflow execution
        """
        config_file = self.config_manager.load_config_from_file(file_path)
        return await self.create_workflow_from_config(config_file, agent_id_mapping)

    async def execute_workflow(
        self,
        workflow: WorkflowExecution,
        task: str,
        **kwargs
    ) -> TaskResult:
        """Execute a workflow.
        
        Args:
            workflow: Workflow to execute
            task: Task description
            **kwargs: Additional parameters
            
        Returns:
            TaskResult: Execution result
        """
        # Register workflow
        self.active_workflows[workflow.workflow_id] = workflow
        
        try:
            self.logger.info(f"Starting workflow execution: {workflow.workflow_id}")
            result = await workflow.execute(task, **kwargs)
            
            # Move to completed workflows
            self.completed_workflows[workflow.workflow_id] = workflow
            del self.active_workflows[workflow.workflow_id]
            
            self.logger.info(f"Completed workflow execution: {workflow.workflow_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {workflow.workflow_id}: {e}")
            # Keep in active workflows for potential retry/inspection
            raise

    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow."""
        if workflow_id in self.active_workflows:
            return await self.active_workflows[workflow_id].pause()
        return False

    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        if workflow_id in self.active_workflows:
            return await self.active_workflows[workflow_id].resume()
        return False

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if workflow_id in self.active_workflows:
            success = await self.active_workflows[workflow_id].cancel()
            if success:
                # Move to completed workflows
                workflow = self.active_workflows[workflow_id]
                self.completed_workflows[workflow_id] = workflow
                del self.active_workflows[workflow_id]
            return success
        return False

    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status and progress."""
        workflow = (
            self.active_workflows.get(workflow_id) or
            self.completed_workflows.get(workflow_id)
        )
        
        if workflow:
            return await workflow.get_execution_info()
        
        return None

    async def list_workflows(
        self,
        status_filter: Optional[WorkflowStatus] = None
    ) -> List[Dict[str, Any]]:
        """List all workflows with optional status filter."""
        workflows = []
        
        # Add active workflows
        for workflow in self.active_workflows.values():
            info = await workflow.get_execution_info()
            if status_filter is None or info["status"] == status_filter:
                workflows.append(info)
        
        # Add completed workflows
        for workflow in self.completed_workflows.values():
            info = await workflow.get_execution_info()
            if status_filter is None or info["status"] == status_filter:
                workflows.append(info)
        
        return workflows

    async def _create_orchestrator(
        self,
        config_file: WorkflowConfigFile,
        orchestration_config: WorkflowConfig
    ) -> BaseOrchestrator:
        """Create the appropriate orchestrator for the workflow pattern."""
        pattern = config_file.pattern
        
        if pattern == OrchestrationPattern.SEQUENTIAL:
            return SequentialOrchestrator(orchestration_config)
        
        elif pattern == OrchestrationPattern.ROUND_ROBIN:
            termination_condition = self.config_manager.create_termination_condition(
                config_file.termination
            )
            return RoundRobinOrchestrator(orchestration_config, termination_condition)
        
        elif pattern == OrchestrationPattern.GRAPH:
            # Create graph orchestrator and configure it
            orchestrator = GraphOrchestrator(orchestration_config)
            await self._configure_graph_orchestrator(orchestrator, config_file)
            return orchestrator
        
        elif pattern == OrchestrationPattern.SWARM:
            # Create swarm orchestrator with participant configuration
            orchestrator = SwarmOrchestrator(orchestration_config)
            await self._configure_swarm_orchestrator(orchestrator, config_file)
            return orchestrator
        
        else:
            raise ValueError(f"Unsupported orchestration pattern: {pattern}")

    async def _configure_graph_orchestrator(
        self,
        orchestrator: GraphOrchestrator,
        config_file: WorkflowConfigFile
    ) -> None:
        """Configure graph orchestrator with nodes and edges from config."""
        from ..orchestration.graph import EdgeType
        
        if config_file.graph and config_file.graph.nodes:
            # Configure from explicit graph structure
            self.logger.info("Configuring graph from explicit structure")
            
            # Add nodes from graph config
            for node_config in config_file.graph.nodes:
                orchestrator.add_node(
                    node_id=node_config.id,
                    agent_id=node_config.agent,
                    name=node_config.id,
                    description=node_config.description,
                    max_retries=node_config.max_retries
                )
            
            # Add edges from graph config
            for edge_config in config_file.graph.edges:
                edge_type_map = {
                    "sequential": EdgeType.SEQUENTIAL,
                    "parallel": EdgeType.PARALLEL,
                    "conditional": EdgeType.CONDITIONAL,
                    "synchronize": EdgeType.SYNCHRONIZE
                }
                
                edge_type = edge_type_map.get(edge_config.type, EdgeType.SEQUENTIAL)
                
                # Create condition function if needed
                condition_func = None
                if edge_type == EdgeType.CONDITIONAL and edge_config.condition:
                    condition_func = self._create_condition_function(
                        edge_config.condition, 
                        config_file.graph.conditions
                    )
                
                orchestrator.add_edge(
                    edge_id=edge_config.id,
                    source_node=edge_config.source,
                    target_node=edge_config.target,
                    edge_type=edge_type,
                    condition=condition_func,
                    weight=edge_config.weight,
                    metadata=edge_config.metadata
                )
            
            # Add parallel branches if specified
            if config_file.graph.parallel_branches:
                for branch_config in config_file.graph.parallel_branches:
                    orchestrator.add_parallel_branch(
                        branch_id=branch_config.id,
                        nodes=branch_config.nodes,
                        synchronization_node=branch_config.synchronization_node
                    )
        
        else:
            # Default to sequential configuration for backwards compatibility
            self.logger.info("No explicit graph structure found, using sequential default")
            
            # Add nodes for each agent
            for i, agent_config in enumerate(config_file.agents):
                if isinstance(agent_config, str):
                    # Simple agent ID/name
                    node_id = f"node_{i}"
                    agent_id = agent_config
                    name = agent_config
                else:
                    # Agent configuration object
                    node_id = f"node_{i}"
                    agent_id = agent_config.id or agent_config.name
                    name = agent_config.name
                
                orchestrator.add_node(
                    node_id=node_id,
                    agent_id=agent_id,
                    name=name,
                    description=f"Agent node for {name}"
                )
            
            # Add sequential edges
            for i in range(len(config_file.agents) - 1):
                source_node = f"node_{i}"
                target_node = f"node_{i + 1}"
                orchestrator.add_edge(
                    edge_id=f"edge_{i}",
                    source_node=source_node,
                    target_node=target_node,
                    edge_type=EdgeType.SEQUENTIAL
                )

    async def _configure_swarm_orchestrator(
        self,
        orchestrator: SwarmOrchestrator,
        config_file: WorkflowConfigFile
    ) -> None:
        """Configure swarm orchestrator with participant settings."""
        self.logger.info("Configuring swarm orchestrator")
        
        # Swarm configuration is handled during orchestrator initialization
        # via the config.parameters.swarm settings
        swarm_config = config_file.parameters.get('swarm', {})
        
        self.logger.info(f"Swarm configuration: {len(orchestrator.participants)} participants")
        
        # Log participant information
        for agent_id, participant in orchestrator.participants.items():
            self.logger.debug(
                f"Participant {agent_id}: specializations={participant.specializations}, "
                f"handoffs={participant.handoff_targets}, weight={participant.participation_weight}"
            )

    def _create_condition_function(
        self,
        condition_name: str,
        conditions_config: Optional[Dict[str, Any]]
    ) -> Optional[Callable[[Dict[str, Any]], bool]]:
        """Create a condition function from configuration."""
        if not conditions_config or condition_name not in conditions_config:
            self.logger.warning(f"Condition '{condition_name}' not found in configuration")
            return None
        
        condition_config = conditions_config[condition_name]
        condition_type = condition_config.get("type", "evaluation")
        
        if condition_type == "evaluation":
            # Simple evaluation based on criteria
            criteria = condition_config.get("criteria", [])
            
            def evaluation_condition(input_data: Dict[str, Any]) -> bool:
                output_data = input_data.get("output_data", {})
                
                # Simple criteria checking
                for criterion in criteria:
                    if criterion == "all_tests_pass":
                        if not output_data.get("tests_passed", False):
                            return False
                    elif criterion == "no_critical_bugs":
                        if output_data.get("critical_bugs", 0) > 0:
                            return False
                    elif criterion == "performance_acceptable":
                        if not output_data.get("performance_ok", False):
                            return False
                    elif criterion == "security_issues_found":
                        if output_data.get("security_issues", 0) > 0:
                            return True  # This condition triggers on issues found
                
                return True
            
            return evaluation_condition
        
        elif condition_type == "approval":
            # Approval-based condition (simplified)
            def approval_condition(input_data: Dict[str, Any]) -> bool:
                output_data = input_data.get("output_data", {})
                return output_data.get("approved", False)
            
            return approval_condition
        
        elif condition_type == "consensus":
            # Consensus-based condition (simplified)
            def consensus_condition(input_data: Dict[str, Any]) -> bool:
                output_data = input_data.get("output_data", {})
                return output_data.get("consensus_reached", False)
            
            return consensus_condition
        
        else:
            self.logger.warning(f"Unknown condition type: {condition_type}")
            return None

    async def _build_agent_id_mapping(self) -> Dict[str, str]:
        """Build mapping from agent names to agent IDs."""
        agents = await self.agent_manager.list_agents()
        return {agent.name: agent.id for agent in agents}

    # Template management methods
    async def create_workflow_from_template(
        self,
        template_id: str,
        parameters: Dict[str, Any],
        agent_id_mapping: Optional[Dict[str, str]] = None
    ) -> WorkflowExecution:
        """Create workflow from template.
        
        Args:
            template_id: Template identifier
            parameters: Template parameters
            agent_id_mapping: Optional mapping from agent names to IDs
            
        Returns:
            WorkflowExecution: Created workflow execution
        """
        config_file = self.config_manager.instantiate_template(template_id, parameters)
        return await self.create_workflow_from_config(config_file, agent_id_mapping)

    def load_template(self, template_path: Union[str, Path]) -> None:
        """Load workflow template."""
        self.config_manager.load_template(template_path)

    def list_templates(self) -> List[Dict[str, Any]]:
        """List available workflow templates."""
        return [
            {
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "pattern": template.config.pattern,
                "parameters": template.parameters
            }
            for template in self.config_manager.templates.values()
        ]


# Global workflow manager instance
workflow_manager = WorkflowManager()


def get_workflow_manager() -> WorkflowManager:
    """Get the global workflow manager instance."""
    return workflow_manager
