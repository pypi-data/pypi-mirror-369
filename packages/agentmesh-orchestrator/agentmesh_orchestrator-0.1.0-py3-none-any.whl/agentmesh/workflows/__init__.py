"""Workflows package for workflow configuration and management."""

from .config import (
    WorkflowConfigFile,
    WorkflowAgentConfig,
    WorkflowTerminationConfig,
    WorkflowTemplate,
    WorkflowConfigManager,
    get_config_manager
)

from .manager import (
    WorkflowExecution,
    WorkflowManager,
    get_workflow_manager
)

__all__ = [
    # Configuration
    "WorkflowConfigFile",
    "WorkflowAgentConfig", 
    "WorkflowTerminationConfig",
    "WorkflowTemplate",
    "WorkflowConfigManager",
    "get_config_manager",
    
    # Management
    "WorkflowExecution",
    "WorkflowManager",
    "get_workflow_manager"
]
