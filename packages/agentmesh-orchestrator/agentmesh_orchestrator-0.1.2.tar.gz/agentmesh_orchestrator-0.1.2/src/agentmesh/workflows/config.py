"""Workflow configuration and management."""

import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

from pydantic import BaseModel, Field, validator
from ..orchestration.base import WorkflowConfig, OrchestrationPattern

logger = logging.getLogger(__name__)


class WorkflowAgentConfig(BaseModel):
    """Configuration for an agent in a workflow."""
    
    name: str = Field(..., description="Agent name")
    type: str = Field(..., description="Agent type")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific configuration")
    id: Optional[str] = Field(None, description="Agent ID (if using existing agent)")


class WorkflowTerminationConfig(BaseModel):
    """Termination conditions for workflows."""
    
    max_rounds: Optional[int] = Field(None, description="Maximum number of rounds")
    max_messages: Optional[int] = Field(None, description="Maximum number of messages")
    timeout_seconds: Optional[int] = Field(None, description="Maximum execution time")
    custom_condition: Optional[str] = Field(None, description="Custom termination condition code")


class GraphNodeConfig(BaseModel):
    """Configuration for a node in a graph workflow."""
    
    id: str = Field(..., description="Node identifier")
    agent: str = Field(..., description="Agent name or ID")
    description: Optional[str] = Field(None, description="Node description")
    max_retries: int = Field(3, description="Maximum retry attempts")
    timeout: Optional[int] = Field(None, description="Node execution timeout")
    input_schema: Optional[Dict[str, Any]] = Field(None, description="Expected input schema")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Expected output schema")


class GraphEdgeConfig(BaseModel):
    """Configuration for an edge in a graph workflow."""
    
    id: str = Field(..., description="Edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: str = Field("sequential", description="Edge type (sequential, parallel, conditional, synchronize)")
    condition: Optional[str] = Field(None, description="Condition name for conditional edges")
    weight: float = Field(1.0, description="Edge weight")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional edge metadata")


class ParallelBranchConfig(BaseModel):
    """Configuration for parallel execution branches."""
    
    id: str = Field(..., description="Branch identifier")
    nodes: List[str] = Field(..., description="Nodes that execute in parallel")
    synchronization_node: Optional[str] = Field(None, description="Node that waits for all parallel nodes")


class ConditionConfig(BaseModel):
    """Configuration for conditional logic."""
    
    type: str = Field(..., description="Condition type (evaluation, approval, consensus)")
    criteria: Optional[List[str]] = Field(None, description="Evaluation criteria")
    required_approval: Optional[str] = Field(None, description="Required approval agent")
    required_agents: Optional[List[str]] = Field(None, description="Required consensus agents")
    timeout: Optional[int] = Field(None, description="Condition evaluation timeout")


class GraphWorkflowConfig(BaseModel):
    """Graph-specific workflow configuration."""
    
    nodes: List[GraphNodeConfig] = Field(..., description="Workflow nodes")
    edges: List[GraphEdgeConfig] = Field(..., description="Workflow edges")
    parallel_branches: Optional[List[ParallelBranchConfig]] = Field(None, description="Parallel execution branches")
    conditions: Optional[Dict[str, ConditionConfig]] = Field(None, description="Conditional logic definitions")


class SwarmParticipantConfig(BaseModel):
    """Configuration for a swarm participant."""
    
    agent_id: str = Field(..., description="Agent identifier")
    name: Optional[str] = Field(None, description="Participant display name")
    specializations: List[str] = Field(default_factory=list, description="Agent specializations")
    handoff_targets: List[str] = Field(default_factory=list, description="Allowed handoff targets")
    weight: float = Field(1.0, description="Participation weight for selection")
    max_consecutive_turns: Optional[int] = Field(None, description="Max consecutive turns")
    cooldown_seconds: int = Field(0, description="Cooldown period between activations")


class SwarmTerminationConfig(BaseModel):
    """Termination configuration for swarm workflows."""
    
    max_messages: Optional[int] = Field(None, description="Maximum messages in swarm")
    max_handoffs: Optional[int] = Field(None, description="Maximum handoffs allowed")
    timeout_seconds: Optional[int] = Field(None, description="Maximum execution time")
    convergence_threshold: Optional[float] = Field(None, description="Convergence threshold")
    min_participation: Optional[float] = Field(None, description="Minimum participation rate")


class SwarmWorkflowConfig(BaseModel):
    """Swarm-specific workflow configuration."""
    
    participants: List[SwarmParticipantConfig] = Field(..., description="Swarm participants")
    termination: Optional[SwarmTerminationConfig] = Field(None, description="Swarm termination conditions")
    handoff_strategy: str = Field("autonomous", description="Handoff strategy (autonomous, weighted, round_robin)")
    collaboration_mode: str = Field("cooperative", description="Collaboration mode (cooperative, competitive)")
    initial_agent: Optional[str] = Field(None, description="Initial agent selection")


class WorkflowConfigFile(BaseModel):
    """Complete workflow configuration from file."""
    
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    pattern: OrchestrationPattern = Field(..., description="Orchestration pattern")
    
    # Agent configuration
    agents: List[Union[str, WorkflowAgentConfig]] = Field(..., description="List of agents")
    
    # Pattern-specific configuration
    termination: Optional[WorkflowTerminationConfig] = Field(None, description="Termination conditions")
    graph: Optional[GraphWorkflowConfig] = Field(None, description="Graph workflow configuration")
    swarm: Optional[SwarmWorkflowConfig] = Field(None, description="Swarm workflow configuration")
    
    # General configuration
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Workflow parameters")
    timeout: Optional[int] = Field(None, description="Overall workflow timeout")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    failure_policy: str = Field("fail_fast", description="Failure handling policy")
    
    # Metadata
    version: str = Field("1.0", description="Configuration version")
    author: Optional[str] = Field(None, description="Workflow author")
    tags: List[str] = Field(default_factory=list, description="Workflow tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("failure_policy")
    def validate_failure_policy(cls, v):
        """Validate failure policy."""
        if v not in ["fail_fast", "continue"]:
            raise ValueError("failure_policy must be 'fail_fast' or 'continue'")
        return v

    @validator("agents", each_item=True)
    def validate_agents(cls, v):
        """Validate agent configurations."""
        if isinstance(v, str):
            return v  # Agent ID string
        elif isinstance(v, dict):
            return WorkflowAgentConfig(**v)
        else:
            return v  # Already a WorkflowAgentConfig


class WorkflowTemplate(BaseModel):
    """Workflow template for reusable configurations."""
    
    template_id: str = Field(..., description="Template identifier")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category")
    config: WorkflowConfigFile = Field(..., description="Template configuration")
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description="Template parameters")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "WorkflowTemplate":
        """Load template from file."""
        path = Path(file_path)
        with open(path, 'r') as f:
            if path.suffix.lower() in ['.yml', '.yaml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        return cls(**data)


class WorkflowConfigManager:
    """Manager for workflow configurations."""
    
    def __init__(self):
        """Initialize workflow config manager."""
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    def load_config_from_file(self, file_path: Union[str, Path]) -> WorkflowConfigFile:
        """Load workflow configuration from file.
        
        Args:
            file_path: Path to configuration file (YAML or JSON)
            
        Returns:
            WorkflowConfigFile: Parsed configuration
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        try:
            with open(path, 'r') as f:
                if path.suffix.lower() in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                    self.logger.info(f"Loaded YAML configuration from {path}")
                elif path.suffix.lower() == '.json':
                    data = json.load(f)
                    self.logger.info(f"Loaded JSON configuration from {path}")
                else:
                    raise ValueError(f"Unsupported file format: {path.suffix}")
            
            config = WorkflowConfigFile(**data)
            self.logger.info(f"Successfully parsed workflow configuration: {config.name}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {path}: {e}")
            raise

    def save_config_to_file(
        self, 
        config: WorkflowConfigFile, 
        file_path: Union[str, Path],
        format: str = "yaml"
    ) -> None:
        """Save workflow configuration to file.
        
        Args:
            config: Configuration to save
            file_path: Destination file path
            format: File format ('yaml' or 'json')
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = config.dict()
        
        try:
            with open(path, 'w') as f:
                if format.lower() == 'yaml':
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                elif format.lower() == 'json':
                    json.dump(data, f, indent=2, default=str)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Saved configuration to {path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {path}: {e}")
            raise

    async def validate_config(self, config: WorkflowConfigFile) -> Dict[str, Any]:
        """Validate workflow configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Dict[str, Any]: Validation result with errors, warnings, and status
        """
        errors = []
        warnings = []
        
        # Validate basic requirements
        if not config.agents:
            errors.append("At least one agent must be specified")
        
        # Pattern-specific validation
        if config.pattern == OrchestrationPattern.SEQUENTIAL:
            if len(config.agents) < 2:
                errors.append("Sequential workflows require at least 2 agents")
        
        elif config.pattern == OrchestrationPattern.ROUND_ROBIN:
            if len(config.agents) < 2:
                errors.append("Round-robin workflows require at least 2 agents")
            
            if config.termination is None:
                errors.append("Round-robin workflows require termination conditions")
        
        elif config.pattern == OrchestrationPattern.GRAPH:
            # Graph-specific validation
            if not config.graph:
                errors.append("Graph workflows require graph configuration")
            else:
                graph_errors, graph_warnings = self._validate_graph_config(config.graph, config.agents)
                errors.extend(graph_errors)
                warnings.extend(graph_warnings)
        
        # Validate termination conditions
        if config.termination:
            term = config.termination
            if not any([term.max_rounds, term.max_messages, term.timeout_seconds]):
                warnings.append("No termination condition specified - workflow may run indefinitely")
        
        # Validate agent names/IDs
        agent_names = set()
        for agent in config.agents:
            if isinstance(agent, str):
                if agent in agent_names:
                    warnings.append(f"Duplicate agent reference: {agent}")
                agent_names.add(agent)
            elif isinstance(agent, WorkflowAgentConfig):
                if agent.name in agent_names:
                    warnings.append(f"Duplicate agent name: {agent.name}")
                agent_names.add(agent.name)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_graph_config(self, graph: GraphWorkflowConfig, agents: List[Union[str, WorkflowAgentConfig]]) -> Tuple[List[str], List[str]]:
        """Validate graph-specific configuration."""
        errors = []
        warnings = []
        
        # Get agent names for validation
        agent_names = set()
        for agent in agents:
            if isinstance(agent, str):
                agent_names.add(agent)
            elif isinstance(agent, WorkflowAgentConfig):
                agent_names.add(agent.name)
        
        # Validate nodes
        if not graph.nodes:
            errors.append("Graph must have at least one node")
            return errors, warnings
        
        node_ids = set()
        for node in graph.nodes:
            if node.id in node_ids:
                errors.append(f"Duplicate node ID: {node.id}")
            node_ids.add(node.id)
            
            if node.agent not in agent_names:
                errors.append(f"Node {node.id} references unknown agent: {node.agent}")
        
        # Validate edges
        for edge in graph.edges:
            if edge.source not in node_ids:
                errors.append(f"Edge {edge.id} references unknown source node: {edge.source}")
            if edge.target not in node_ids:
                errors.append(f"Edge {edge.id} references unknown target node: {edge.target}")
            
            if edge.type == "conditional" and not edge.condition:
                warnings.append(f"Conditional edge {edge.id} has no condition specified")
        
        # Validate parallel branches
        if graph.parallel_branches:
            for branch in graph.parallel_branches:
                for node_id in branch.nodes:
                    if node_id not in node_ids:
                        errors.append(f"Parallel branch {branch.id} references unknown node: {node_id}")
                
                if branch.synchronization_node and branch.synchronization_node not in node_ids:
                    errors.append(f"Parallel branch {branch.id} references unknown sync node: {branch.synchronization_node}")
        
        # Check for unreachable nodes (simple check)
        reachable_nodes = set()
        source_nodes = {edge.source for edge in graph.edges}
        target_nodes = {edge.target for edge in graph.edges}
        
        # Find root nodes (nodes with no incoming edges)
        root_nodes = node_ids - target_nodes
        if not root_nodes:
            warnings.append("No root nodes found - workflow may not have a clear starting point")
        
        # Find leaf nodes (nodes with no outgoing edges)  
        leaf_nodes = node_ids - source_nodes
        if not leaf_nodes:
            warnings.append("No leaf nodes found - workflow may not have a clear ending point")
        
        return errors, warnings

    def convert_to_orchestration_config(
        self, 
        config: WorkflowConfigFile,
        agent_id_mapping: Dict[str, str]
    ) -> WorkflowConfig:
        """Convert file config to orchestration config.
        
        Args:
            config: File configuration
            agent_id_mapping: Mapping from agent names to agent IDs
            
        Returns:
            WorkflowConfig: Orchestration configuration
        """
        # Resolve agent IDs
        agent_ids = []
        for agent in config.agents:
            if isinstance(agent, str):
                # Agent ID or name
                if agent in agent_id_mapping:
                    agent_ids.append(agent_id_mapping[agent])
                else:
                    agent_ids.append(agent)  # Assume it's already an ID
            elif isinstance(agent, WorkflowAgentConfig):
                # Agent configuration object
                if agent.id:
                    agent_ids.append(agent.id)
                elif agent.name in agent_id_mapping:
                    agent_ids.append(agent_id_mapping[agent.name])
                else:
                    raise ValueError(f"Cannot resolve agent ID for: {agent.name}")
        
        return WorkflowConfig(
            name=config.name,
            pattern=config.pattern,
            agents=agent_ids,
            parameters=config.parameters,
            timeout=config.timeout,
            retry_attempts=config.retry_attempts,
            failure_policy=config.failure_policy,
            metadata=config.metadata
        )

    def create_termination_condition(
        self, 
        config: Optional[WorkflowTerminationConfig]
    ) -> Optional[Dict[str, Any]]:
        """Create termination condition from configuration.
        
        Args:
            config: Termination configuration
            
        Returns:
            Dict[str, Any]: Termination condition parameters
        """
        if not config:
            return None
        
        return {
            "max_rounds": config.max_rounds,
            "max_messages": config.max_messages,
            "timeout_seconds": config.timeout_seconds
            # Note: custom_condition would need to be evaluated from string
        }

    def load_template(self, template_path: Union[str, Path]) -> WorkflowTemplate:
        """Load workflow template from file.
        
        Args:
            template_path: Path to template file
            
        Returns:
            WorkflowTemplate: Loaded template
        """
        template = WorkflowTemplate.from_file(template_path)
        self.templates[template.template_id] = template
        self.logger.info(f"Loaded template: {template.template_id}")
        return template

    def instantiate_template(
        self,
        template_id: str,
        parameters: Dict[str, Any]
    ) -> WorkflowConfigFile:
        """Instantiate a workflow from template.
        
        Args:
            template_id: Template identifier
            parameters: Template parameters
            
        Returns:
            WorkflowConfigFile: Instantiated configuration
        """
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")
        
        template = self.templates[template_id]
        config_data = template.config.dict()
        
        # Apply parameter substitution
        config_data = self._substitute_parameters(config_data, parameters)
        
        return WorkflowConfigFile(**config_data)

    def _substitute_parameters(
        self,
        data: Any,
        parameters: Dict[str, Any]
    ) -> Any:
        """Recursively substitute template parameters."""
        if isinstance(data, str):
            # Simple string substitution
            for key, value in parameters.items():
                data = data.replace(f"${{{key}}}", str(value))
            return data
        elif isinstance(data, dict):
            return {k: self._substitute_parameters(v, parameters) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_parameters(item, parameters) for item in data]
        else:
            return data

    def load_config(self, file_path: Union[str, Path]) -> WorkflowConfigFile:
        """Load workflow configuration from file (alias for load_config_from_file).
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            WorkflowConfigFile: Parsed configuration
        """
        return self.load_config_from_file(file_path)

    async def list_templates(self) -> List[Dict[str, Any]]:
        """List all available workflow templates.
        
        Returns:
            List[Dict[str, Any]]: List of template information
        """
        # For now, return a static list of built-in templates
        # In a real implementation, this would scan a templates directory
        templates = [
            {
                "template_id": "sequential-code-review",
                "name": "Sequential Code Review",
                "description": "A workflow where agents review code sequentially",
                "category": "development",
                "pattern": "sequential",
                "parameters": [
                    {"name": "reviewer_count", "type": "int", "default": 3},
                    {"name": "review_timeout", "type": "int", "default": 600}
                ]
            },
            {
                "template_id": "roundrobin-brainstorming",
                "name": "Round-Robin Brainstorming",
                "description": "A brainstorming session using round-robin pattern",
                "category": "collaboration",
                "pattern": "round-robin",
                "parameters": [
                    {"name": "max_rounds", "type": "int", "default": 5},
                    {"name": "participant_count", "type": "int", "default": 4}
                ]
            }
        ]
        
        # Add loaded templates
        for template in self.templates.values():
            templates.append({
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "pattern": template.config.pattern,
                "parameters": template.parameters
            })
        
        return templates

    async def load_from_file(self, file_path: Union[str, Path]) -> WorkflowConfigFile:
        """Load workflow configuration from file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            WorkflowConfigFile: Loaded configuration
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif file_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            # Convert to WorkflowConfigFile
            config = WorkflowConfigFile(**data)
            self.logger.info(f"Loaded configuration from {file_path}")
            return config
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in {file_path}: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {file_path}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration from {file_path}: {e}")


# Global config manager instance
config_manager = WorkflowConfigManager()


def get_config_manager() -> WorkflowConfigManager:
    """Get the global config manager instance."""
    return config_manager
