"""REST API endpoints for workflow management."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from pydantic import BaseModel, Field

from ...orchestration.base import OrchestrationPattern, WorkflowStatus
from ...workflows.config import WorkflowConfigFile, get_config_manager
from ...workflows.manager import get_workflow_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


class CreateWorkflowRequest(BaseModel):
    """Request model for creating a workflow."""
    config: WorkflowConfigFile
    agent_mapping: Optional[Dict[str, str]] = Field(None, description="Agent name to ID mapping")


class ExecuteWorkflowRequest(BaseModel):
    """Request model for executing a workflow."""
    task: str = Field(..., description="Task description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")


class WorkflowResponse(BaseModel):
    """Response model for workflow operations."""
    workflow_id: str
    execution_id: str
    status: WorkflowStatus
    config: Dict[str, Any]
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class WorkflowListResponse(BaseModel):
    """Response model for workflow listing."""
    workflows: List[WorkflowResponse]
    total: int


class WorkflowExecutionResponse(BaseModel):
    """Response model for workflow execution."""
    execution_id: str
    workflow_id: str
    result: Optional[Dict[str, Any]] = None
    success: bool
    error: Optional[str] = None


class TemplateResponse(BaseModel):
    """Response model for workflow templates."""
    template_id: str
    name: str
    description: str
    category: str
    pattern: OrchestrationPattern
    parameters: List[Dict[str, Any]]


class TemplateListResponse(BaseModel):
    """Response model for template listing."""
    templates: List[TemplateResponse]
    total: int


class WorkflowGraphResponse(BaseModel):
    """Response model for workflow graph visualization."""
    workflow_id: str
    graph_type: str  # "sequential", "round-robin", "graph"
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    current_state: Optional[Dict[str, Any]] = None
    visualization: Dict[str, Any]  # Contains ASCII, mermaid, etc.


class WorkflowVisualizationRequest(BaseModel):
    """Request model for workflow visualization."""
    format: str = Field("ascii", description="Visualization format: ascii, json, mermaid")
    include_state: bool = Field(True, description="Include current execution state")


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Workflow",
    description="Create a new workflow from configuration"
)
async def create_workflow(
    request: CreateWorkflowRequest,
    workflow_manager = Depends(get_workflow_manager)
) -> WorkflowResponse:
    """Create a new workflow."""
    try:
        workflow = await workflow_manager.create_workflow_from_config(
            request.config,
            request.agent_mapping
        )
        
        execution_info = await workflow.get_execution_info()
        
        return WorkflowResponse(
            workflow_id=workflow.workflow_id,
            execution_id=workflow.execution_id,
            status=execution_info["status"],
            config=execution_info["config"],
            created_at=execution_info["timing"]["created_at"],
            started_at=execution_info["timing"]["started_at"],
            completed_at=execution_info["timing"]["completed_at"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while creating workflow: {str(e)}"
        )


@router.post(
    "/from-file",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Workflow from File",
    description="Create a workflow by uploading a configuration file"
)
async def create_workflow_from_file(
    file: UploadFile = File(..., description="Workflow configuration file (YAML or JSON)"),
    workflow_manager = Depends(get_workflow_manager)
) -> WorkflowResponse:
    """Create workflow from uploaded configuration file."""
    try:
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode='wb',
            suffix=Path(file.filename).suffix,
            delete=False
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Create workflow from file
            workflow = await workflow_manager.create_workflow_from_file(tmp_file_path)
            
            execution_info = await workflow.get_execution_info()
            
            return WorkflowResponse(
                workflow_id=workflow.workflow_id,
                execution_id=workflow.execution_id,
                status=execution_info["status"],
                config=execution_info["config"],
                created_at=execution_info["timing"]["created_at"],
                started_at=execution_info["timing"]["started_at"],
                completed_at=execution_info["timing"]["completed_at"]
            )
            
        finally:
            # Clean up temporary file
            Path(tmp_file_path).unlink(missing_ok=True)
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating workflow from file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while creating workflow from file: {str(e)}"
        )


@router.post(
    "/{workflow_id}/execute",
    response_model=WorkflowExecutionResponse,
    summary="Execute Workflow",
    description="Execute a workflow with a given task"
)
async def execute_workflow(
    workflow_id: str,
    request: ExecuteWorkflowRequest,
    workflow_manager = Depends(get_workflow_manager)
) -> WorkflowExecutionResponse:
    """Execute a workflow."""
    try:
        # Find workflow
        workflow = workflow_manager.active_workflows.get(workflow_id)
        if not workflow:
            # Check if it's a workflow we need to find by ID
            all_workflows = await workflow_manager.list_workflows()
            matching_workflows = [w for w in all_workflows if w["workflow_id"] == workflow_id]
            
            if not matching_workflows:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workflow {workflow_id} not found"
                )
            
            # If workflow exists but not active, it might be completed or failed
            workflow_info = matching_workflows[0]
            if workflow_info["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Workflow {workflow_id} is in {workflow_info['status']} state and cannot be executed"
                )
            
            # This shouldn't happen, but handle gracefully
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Workflow {workflow_id} found but not accessible"
            )
        
        # Execute workflow
        result = await workflow_manager.execute_workflow(
            workflow,
            request.task,
            **request.parameters
        )
        
        return WorkflowExecutionResponse(
            execution_id=workflow.execution_id,
            workflow_id=workflow.workflow_id,
            result={
                "task_id": result.task_id,
                "agent_id": result.agent_id,
                "result": result.result,
                "execution_time": result.execution_time,
                "timestamp": result.timestamp.isoformat()
            },
            success=result.success,
            error=result.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing workflow {workflow_id}: {e}")
        return WorkflowExecutionResponse(
            execution_id="error",
            workflow_id=workflow_id,
            success=False,
            error=str(e)
        )


@router.get(
    "",
    response_model=WorkflowListResponse,
    summary="List Workflows",
    description="List all workflows with optional status filtering"
)
async def list_workflows(
    status_filter: Optional[WorkflowStatus] = Query(None, description="Filter by workflow status"),
    workflow_manager = Depends(get_workflow_manager)
) -> WorkflowListResponse:
    """List workflows."""
    try:
        workflows_info = await workflow_manager.list_workflows(status_filter)
        
        workflows = [
            WorkflowResponse(
                workflow_id=info["workflow_id"],
                execution_id=info["execution_id"],
                status=info["status"],
                config=info["config"],
                created_at=info["timing"]["created_at"],
                started_at=info["timing"]["started_at"],
                completed_at=info["timing"]["completed_at"]
            )
            for info in workflows_info
        ]
        
        return WorkflowListResponse(
            workflows=workflows,
            total=len(workflows)
        )
        
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while listing workflows: {str(e)}"
        )


@router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Get Workflow",
    description="Get detailed information about a workflow"
)
async def get_workflow(
    workflow_id: str,
    workflow_manager = Depends(get_workflow_manager)
) -> WorkflowResponse:
    """Get workflow details."""
    try:
        info = await workflow_manager.get_workflow_status(workflow_id)
        
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found"
            )
        
        return WorkflowResponse(
            workflow_id=info["workflow_id"],
            execution_id=info["execution_id"],
            status=info["status"],
            config=info["config"],
            created_at=info["timing"]["created_at"],
            started_at=info["timing"]["started_at"],
            completed_at=info["timing"]["completed_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting workflow: {str(e)}"
        )


@router.get(
    "/{workflow_id}/graph",
    response_model=WorkflowGraphResponse,
    summary="Get Workflow Graph",
    description="Get the graph structure and visualization for a workflow"
)
async def get_workflow_graph(
    workflow_id: str,
    visualization_request: WorkflowVisualizationRequest = None,
    workflow_manager = Depends(get_workflow_manager)
) -> WorkflowGraphResponse:
    """Get workflow graph structure and visualization."""
    try:
        # Get workflow
        workflow_info = await workflow_manager.get_workflow_details(workflow_id)
        if not workflow_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found"
            )
        
        # Get orchestrator
        workflow = workflow_manager.active_workflows.get(workflow_id)
        if not workflow:
            # Try to reconstruct from config for visualization
            config_data = workflow_info.get("config", {})
            from ...workflows.config import WorkflowConfigFile
            config = WorkflowConfigFile(**config_data)
            workflow = await workflow_manager.create_workflow_from_config(config)
        
        orchestrator = workflow.orchestrator
        
        # Generate graph visualization
        if hasattr(orchestrator, 'visualize_graph'):
            format_type = visualization_request.format if visualization_request else "ascii"
            include_state = visualization_request.include_state if visualization_request else True
            
            visualization_data = orchestrator.visualize_graph(
                format=format_type,
                include_execution_state=include_state
            )
            
            # Extract nodes and edges information
            nodes = []
            edges = []
            current_state = None
            
            if hasattr(orchestrator, 'get_graph_structure'):
                graph_structure = orchestrator.get_graph_structure()
                nodes = graph_structure.get("nodes", [])
                edges = graph_structure.get("edges", [])
                
            if include_state and hasattr(orchestrator, 'get_execution_state'):
                current_state = orchestrator.get_execution_state()
                
            return WorkflowGraphResponse(
                workflow_id=workflow_id,
                graph_type=orchestrator.pattern.value,
                nodes=nodes,
                edges=edges,
                current_state=current_state,
                visualization=visualization_data
            )
        else:
            # Fallback for non-graph orchestrators
            agent_list = getattr(orchestrator, 'agents', orchestrator.config.agents if hasattr(orchestrator, 'config') else [])
            if not isinstance(agent_list, list):
                agent_list = list(agent_list) if agent_list else []
            
            return WorkflowGraphResponse(
                workflow_id=workflow_id,
                graph_type=orchestrator.pattern.value,
                nodes=[{"id": f"agent_{i}", "name": str(agent_name)} for i, agent_name in enumerate(agent_list)],
                edges=[],
                current_state=None,
                visualization={
                    "ascii": f"Linear workflow: {' -> '.join(str(agent) for agent in agent_list)}" if agent_list else "No agents configured",
                    "message": "Visualization not available for this workflow type"
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow graph for {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting workflow graph: {str(e)}"
        )


@router.post(
    "/{workflow_id}/pause",
    summary="Pause Workflow",
    description="Pause a running workflow"
)
async def pause_workflow(
    workflow_id: str,
    workflow_manager = Depends(get_workflow_manager)
) -> Dict[str, Any]:
    """Pause workflow execution."""
    try:
        success = await workflow_manager.pause_workflow(workflow_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot pause workflow {workflow_id} (not found or not in running state)"
            )
        
        return {"success": True, "message": f"Workflow {workflow_id} paused successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing workflow {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while pausing workflow: {str(e)}"
        )


@router.post(
    "/{workflow_id}/resume",
    summary="Resume Workflow",
    description="Resume a paused workflow"
)
async def resume_workflow(
    workflow_id: str,
    workflow_manager = Depends(get_workflow_manager)
) -> Dict[str, Any]:
    """Resume workflow execution."""
    try:
        success = await workflow_manager.resume_workflow(workflow_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot resume workflow {workflow_id} (not found or not in paused state)"
            )
        
        return {"success": True, "message": f"Workflow {workflow_id} resumed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming workflow {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while resuming workflow: {str(e)}"
        )


@router.post(
    "/{workflow_id}/cancel",
    summary="Cancel Workflow",
    description="Cancel a workflow execution"
)
async def cancel_workflow(
    workflow_id: str,
    workflow_manager = Depends(get_workflow_manager)
) -> Dict[str, Any]:
    """Cancel workflow execution."""
    try:
        success = await workflow_manager.cancel_workflow(workflow_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel workflow {workflow_id} (not found or not in cancellable state)"
            )
        
        return {"success": True, "message": f"Workflow {workflow_id} cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling workflow {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while cancelling workflow: {str(e)}"
        )


# Template endpoints
@router.get(
    "/templates",
    response_model=TemplateListResponse,
    summary="List Workflow Templates",
    description="List all available workflow templates"
)
async def list_templates(
    workflow_manager = Depends(get_workflow_manager)
) -> TemplateListResponse:
    """List workflow templates."""
    try:
        templates_info = workflow_manager.list_templates()
        
        templates = [
            TemplateResponse(**info)
            for info in templates_info
        ]
        
        return TemplateListResponse(
            templates=templates,
            total=len(templates)
        )
        
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while listing templates: {str(e)}"
        )


@router.post(
    "/from-template/{template_id}",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Workflow from Template",
    description="Create a workflow from a template with parameters"
)
async def create_workflow_from_template(
    template_id: str,
    parameters: Dict[str, Any],
    workflow_manager = Depends(get_workflow_manager)
) -> WorkflowResponse:
    """Create workflow from template."""
    try:
        workflow = await workflow_manager.create_workflow_from_template(
            template_id,
            parameters
        )
        
        execution_info = await workflow.get_execution_info()
        
        return WorkflowResponse(
            workflow_id=workflow.workflow_id,
            execution_id=workflow.execution_id,
            status=execution_info["status"],
            config=execution_info["config"],
            created_at=execution_info["timing"]["created_at"],
            started_at=execution_info["timing"]["started_at"],
            completed_at=execution_info["timing"]["completed_at"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating workflow from template {template_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while creating workflow from template: {str(e)}"
        )


@router.get(
    "/{workflow_id}/status",
    summary="Get Workflow Status",
    description="Get detailed status information for a workflow"
)
async def get_workflow_status(
    workflow_id: str,
    workflow_manager = Depends(get_workflow_manager)
) -> Dict[str, Any]:
    """Get detailed workflow status."""
    try:
        workflow_info = await workflow_manager.get_workflow_details(workflow_id)
        if not workflow_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found"
            )
        
        # Get additional runtime information if workflow is active
        workflow = workflow_manager.active_workflows.get(workflow_id)
        if workflow:
            execution_info = await workflow.get_execution_info()
            return {
                **workflow_info,
                "runtime_info": execution_info,
                "is_active": True
            }
        else:
            return {
                **workflow_info,
                "is_active": False
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow status for {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting workflow status: {str(e)}"
        )


@router.get(
    "/{workflow_id}/history",
    summary="Get Workflow Execution History",
    description="Get the execution history and message flow for a workflow"
)
async def get_workflow_history(
    workflow_id: str,
    workflow_manager = Depends(get_workflow_manager)
) -> Dict[str, Any]:
    """Get workflow execution history."""
    try:
        workflow = workflow_manager.active_workflows.get(workflow_id)
        if not workflow:
            # Try to get from completed workflows
            workflow_info = await workflow_manager.get_workflow_details(workflow_id)
            if not workflow_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workflow {workflow_id} not found"
                )
            
            return {
                "workflow_id": workflow_id,
                "history": workflow_info.get("execution_history", []),
                "message_flow": workflow_info.get("message_flow", []),
                "status": "Historical data only - workflow not active"
            }
        
        # Get execution history from active workflow
        if hasattr(workflow.orchestrator, 'get_execution_history'):
            history = workflow.orchestrator.get_execution_history()
            return {
                "workflow_id": workflow_id,
                "history": history,
                "message_flow": getattr(workflow.orchestrator, 'message_flow', []),
                "status": "Active workflow"
            }
        else:
            return {
                "workflow_id": workflow_id,
                "history": [],
                "message_flow": [],
                "status": "History not available for this workflow type"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow history for {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while getting workflow history: {str(e)}"
        )


@router.post(
    "/validate",
    summary="Validate Workflow Configuration",
    description="Validate a workflow configuration without creating it"
)
async def validate_workflow_config(
    config: WorkflowConfigFile,
    workflow_manager = Depends(get_workflow_manager)
) -> Dict[str, Any]:
    """Validate workflow configuration."""
    try:
        # Use config manager to validate
        config_manager = get_config_manager()
        validation_result = await config_manager.validate_config(config)
        
        return {
            "valid": validation_result["valid"],
            "errors": validation_result.get("errors", []),
            "warnings": validation_result.get("warnings", []),
            "config_summary": {
                "name": config.name,
                "orchestration": config.orchestration,
                "agent_count": len(config.agents),
                "has_graph": bool(getattr(config, 'graph', None))
            }
        }
        
    except Exception as e:
        logger.error(f"Error validating workflow config: {e}")
        return {
            "valid": False,
            "errors": [str(e)],
            "warnings": [],
            "config_summary": None
        }


# Swarm-specific API endpoints

class SwarmMetricsResponse(BaseModel):
    """Response model for swarm metrics."""
    execution_id: str
    agent_participation_rates: Dict[str, float]
    total_handoffs: int
    autonomous_handoffs: int
    avg_response_time: float
    total_messages: int
    active_agents: List[str]
    convergence_score: float


class SwarmAnalyticsResponse(BaseModel):
    """Response model for swarm analytics."""
    execution_id: str
    performance_metrics: Dict[str, Any]
    handoff_patterns: Dict[str, Any]
    agent_statistics: Dict[str, Any]
    efficiency_scores: Dict[str, float]


class SwarmTuneRequest(BaseModel):
    """Request model for swarm parameter tuning."""
    parameter: str = Field(..., description="Parameter name to tune")
    value: float = Field(..., description="New parameter value")


@router.get(
    "/{execution_id}/swarm/metrics",
    response_model=SwarmMetricsResponse,
    summary="Get Swarm Metrics",
    description="Get real-time metrics for a swarm execution"
)
async def get_swarm_metrics(
    execution_id: str,
    workflow_manager = Depends(get_workflow_manager)
) -> SwarmMetricsResponse:
    """Get swarm execution metrics."""
    try:
        workflow = await workflow_manager.get_workflow(execution_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow not found: {execution_id}"
            )
        
        orchestrator = workflow.orchestrator
        if not hasattr(orchestrator, 'get_swarm_metrics'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Swarm metrics not available for this workflow type"
            )
        
        metrics = await orchestrator.get_swarm_metrics()
        
        return SwarmMetricsResponse(
            execution_id=execution_id,
            agent_participation_rates=metrics.agent_participation_rates,
            total_handoffs=metrics.total_handoffs,
            autonomous_handoffs=metrics.autonomous_handoffs,
            avg_response_time=metrics.avg_response_time,
            total_messages=metrics.total_messages,
            active_agents=list(metrics.active_agents),
            convergence_score=metrics.convergence_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting swarm metrics for {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get swarm metrics: {str(e)}"
        )


@router.get(
    "/{execution_id}/swarm/analytics",
    response_model=SwarmAnalyticsResponse,
    summary="Get Swarm Analytics",
    description="Get comprehensive analytics for a swarm execution"
)
async def get_swarm_analytics(
    execution_id: str,
    workflow_manager = Depends(get_workflow_manager)
) -> SwarmAnalyticsResponse:
    """Get comprehensive swarm analytics."""
    try:
        workflow = await workflow_manager.get_workflow(execution_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow not found: {execution_id}"
            )
        
        orchestrator = workflow.orchestrator
        if not hasattr(orchestrator, 'get_analytics'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Analytics not available for this workflow type"
            )
        
        analytics = await orchestrator.get_analytics()
        
        return SwarmAnalyticsResponse(
            execution_id=execution_id,
            performance_metrics=analytics.get("performance_metrics", {}),
            handoff_patterns=analytics.get("handoff_patterns", {}),
            agent_statistics=analytics.get("agent_statistics", {}),
            efficiency_scores=analytics.get("efficiency_scores", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting swarm analytics for {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get swarm analytics: {str(e)}"
        )


@router.post(
    "/{execution_id}/swarm/tune",
    summary="Tune Swarm Parameters",
    description="Tune swarm parameters during execution"
)
async def tune_swarm_parameters(
    execution_id: str,
    tune_request: SwarmTuneRequest,
    workflow_manager = Depends(get_workflow_manager)
) -> Dict[str, Any]:
    """Tune swarm parameters during execution."""
    try:
        workflow = await workflow_manager.get_workflow(execution_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow not found: {execution_id}"
            )
        
        orchestrator = workflow.orchestrator
        if not hasattr(orchestrator, 'tune_parameter'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parameter tuning not available for this workflow type"
            )
        
        success = await orchestrator.tune_parameter(
            tune_request.parameter, 
            tune_request.value
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to tune parameter: {tune_request.parameter}"
            )
        
        return {
            "success": True,
            "parameter": tune_request.parameter,
            "new_value": tune_request.value,
            "execution_id": execution_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tuning swarm parameters for {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to tune swarm parameters: {str(e)}"
        )


@router.get(
    "/{execution_id}/swarm/handoff-graph",
    summary="Get Swarm Handoff Graph",
    description="Get visualization data for swarm handoff patterns"
)
async def get_swarm_handoff_graph(
    execution_id: str,
    workflow_manager = Depends(get_workflow_manager)
) -> Dict[str, Any]:
    """Get swarm handoff graph for visualization."""
    try:
        workflow = await workflow_manager.get_workflow(execution_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow not found: {execution_id}"
            )
        
        orchestrator = workflow.orchestrator
        if not hasattr(orchestrator, 'get_handoff_graph'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Handoff graph not available for this workflow type"
            )
        
        handoff_graph = await orchestrator.get_handoff_graph()
        
        return {
            "execution_id": execution_id,
            "nodes": handoff_graph.get("nodes", {}),
            "edges": handoff_graph.get("edges", {}),
            "metadata": handoff_graph.get("metadata", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting swarm handoff graph for {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get swarm handoff graph: {str(e)}"
        )
