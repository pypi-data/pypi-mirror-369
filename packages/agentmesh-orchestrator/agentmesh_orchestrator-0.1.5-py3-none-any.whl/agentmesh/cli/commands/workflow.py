"""Workflow management CLI commands."""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.json import JSON
    from rich.progress import Progress, SpinnerColumn, TextColumn

    console = Console()
except ImportError:
    # Fallback if rich is not available
    console = None

from ...workflows.manager import get_workflow_manager
from ...workflows.config import get_config_manager, WorkflowConfigFile
from ...orchestration.base import WorkflowStatus


def setup_parser(subparsers) -> None:
    """Setup workflow command parser."""
    workflow_parser = subparsers.add_parser(
        "workflow",
        help="Manage workflows",
        description="Create, run, and manage agent workflows",
    )

    workflow_subparsers = workflow_parser.add_subparsers(
        dest="workflow_action", help="Workflow actions"
    )

    # Create workflow command
    create_parser = workflow_subparsers.add_parser(
        "create", help="Create a new workflow from configuration"
    )
    create_parser.add_argument(
        "--config", 
        required=True, 
        help="Path to workflow configuration file (YAML/JSON)"
    )
    create_parser.add_argument(
        "--agent-mapping",
        help="JSON string mapping agent names to IDs (e.g., '{\"developer\": \"agent-123\"}')"
    )

    # List workflows command
    list_parser = workflow_subparsers.add_parser("list", help="List all workflows")
    list_parser.add_argument(
        "--status",
        choices=["pending", "running", "paused", "completed", "failed", "cancelled"],
        help="Filter by workflow status"
    )
    list_parser.add_argument(
        "--pattern",
        choices=["sequential", "round-robin", "graph", "swarm"],
        help="Filter by orchestration pattern"
    )
    list_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    # Execute workflow command
    execute_parser = workflow_subparsers.add_parser("execute", help="Execute a workflow")
    execute_parser.add_argument("workflow_id", help="Workflow ID to execute")
    execute_parser.add_argument(
        "--task", required=True, help="Task description for the workflow"
    )
    execute_parser.add_argument(
        "--parameters",
        help="JSON string of additional parameters (e.g., '{\"max_rounds\": 5}')"
    )
    execute_parser.add_argument(
        "--async",
        action="store_true",
        dest="async_run",
        help="Run workflow asynchronously",
    )

    # Get workflow command
    get_parser = workflow_subparsers.add_parser("get", help="Get workflow details")
    get_parser.add_argument("workflow_id", help="Workflow ID")

    # Cancel workflow command
    cancel_parser = workflow_subparsers.add_parser("cancel", help="Cancel a running workflow")
    cancel_parser.add_argument("workflow_id", help="Workflow ID")

    # Pause workflow command
    pause_parser = workflow_subparsers.add_parser("pause", help="Pause a running workflow")
    pause_parser.add_argument("workflow_id", help="Workflow ID to pause")

    # Resume workflow command
    resume_parser = workflow_subparsers.add_parser("resume", help="Resume a paused workflow") 
    resume_parser.add_argument("workflow_id", help="Workflow ID to resume")

    # Validate config command
    validate_parser = workflow_subparsers.add_parser("validate", help="Validate workflow configuration")
    validate_parser.add_argument("config", help="Path to workflow configuration file")

    # Templates command
    templates_parser = workflow_subparsers.add_parser("templates", help="List workflow templates")
    templates_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    # Visualize command for graph workflows
    visualize_parser = workflow_subparsers.add_parser("visualize", help="Visualize workflow graph")
    visualize_parser.add_argument("workflow_id", help="Workflow ID to visualize")
    visualize_parser.add_argument(
        "--format",
        choices=["ascii", "json", "mermaid"],
        default="ascii",
        help="Visualization format (default: ascii)",
    )
    visualize_parser.add_argument(
        "--output",
        help="Output file path (optional)",
    )


# Swarm-specific CLI commands

def add_swarm_subparser(subparsers):
    """Add swarm management subcommands."""
    swarm_parser = subparsers.add_parser(
        "swarm",
        help="Manage agent swarms"
    )
    
    swarm_subparsers = swarm_parser.add_subparsers(
        dest="swarm_action",
        help="Swarm actions"
    )
    
    # Create swarm command
    create_swarm_parser = swarm_subparsers.add_parser(
        "create",
        help="Create a new swarm"
    )
    create_swarm_parser.add_argument(
        "--config",
        required=True,
        help="Path to swarm configuration file"
    )
    create_swarm_parser.add_argument(
        "--agent-mapping",
        help="JSON mapping of agent names to implementations"
    )
    
    # Monitor swarm command
    monitor_swarm_parser = swarm_subparsers.add_parser(
        "monitor",
        help="Monitor swarm execution"
    )
    monitor_swarm_parser.add_argument(
        "--id",
        required=True,
        help="Swarm execution ID"
    )
    monitor_swarm_parser.add_argument(
        "--metrics",
        choices=["all", "participation", "handoffs", "performance"],
        default="all",
        help="Types of metrics to display"
    )
    monitor_swarm_parser.add_argument(
        "--refresh",
        type=int,
        default=5,
        help="Refresh interval in seconds"
    )
    
    # Tune swarm command
    tune_swarm_parser = swarm_subparsers.add_parser(
        "tune",
        help="Tune swarm parameters"
    )
    tune_swarm_parser.add_argument(
        "--id",
        required=True,
        help="Swarm execution ID"
    )
    tune_swarm_parser.add_argument(
        "--parameter",
        required=True,
        choices=["participation_balance", "handoff_frequency", "convergence_threshold"],
        help="Parameter to tune"
    )
    tune_swarm_parser.add_argument(
        "--value",
        type=float,
        help="New parameter value"
    )
    
    # Analytics command
    analytics_swarm_parser = swarm_subparsers.add_parser(
        "analytics",
        help="Get swarm analytics"
    )
    analytics_swarm_parser.add_argument(
        "--id",
        required=True,
        help="Swarm execution ID"
    )
    analytics_swarm_parser.add_argument(
        "--output",
        choices=["console", "json", "csv"],
        default="console",
        help="Output format"
    )


def handle_workflow_command(args) -> int:
    """Handle workflow commands."""
    try:
        if args.workflow_action == "create":
            return asyncio.run(create_workflow(args))
        elif args.workflow_action == "list":
            return asyncio.run(list_workflows(args))
        elif args.workflow_action == "execute":
            return asyncio.run(execute_workflow(args))
        elif args.workflow_action == "get":
            return asyncio.run(get_workflow(args))
        elif args.workflow_action == "cancel":
            return asyncio.run(cancel_workflow(args))
        elif args.workflow_action == "validate":
            return asyncio.run(validate_config_async(args))
        elif args.workflow_action == "templates":
            return asyncio.run(list_templates(args))
        elif args.workflow_action == "pause":
            return asyncio.run(pause_workflow(args))
        elif args.workflow_action == "resume":
            return asyncio.run(resume_workflow(args))
        elif args.workflow_action == "visualize":
            return asyncio.run(visualize_workflow(args))
        else:
            print("Unknown workflow action")
            return 1
    except Exception as e:
        if console:
            console.print(f"[red]Error: {e}[/red]")
        else:
            print(f"Error: {e}")
        return 1


async def create_workflow(args) -> int:
    """Create a new workflow."""
    try:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Configuration file not found: {config_path}")
            return 1

        # Load agent mapping if provided
        agent_mapping = None
        if args.agent_mapping:
            try:
                agent_mapping = json.loads(args.agent_mapping)
            except json.JSONDecodeError as e:
                print(f"Invalid agent mapping JSON: {e}")
                return 1

        workflow_manager = get_workflow_manager()
        
        if console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Creating workflow...", total=None)
                workflow = await workflow_manager.create_workflow_from_file(
                    config_path, agent_mapping
                )
                progress.update(task, description="Workflow created!")

            console.print(f"[green]✓[/green] Workflow created successfully!")
            console.print(f"[cyan]Workflow ID:[/cyan] {workflow.workflow_id}")
            console.print(f"[cyan]Execution ID:[/cyan] {workflow.execution_id}")
        else:
            print("Creating workflow...")
            workflow = await workflow_manager.create_workflow_from_file(
                config_path, agent_mapping
            )
            print("✓ Workflow created successfully!")
            print(f"Workflow ID: {workflow.workflow_id}")
            print(f"Execution ID: {workflow.execution_id}")

        return 0

    except Exception as e:
        if console:
            console.print(f"[red]Failed to create workflow: {e}[/red]")
        else:
            print(f"Failed to create workflow: {e}")
        return 1


async def list_workflows(args) -> int:
    """List all workflows."""
    try:
        workflow_manager = get_workflow_manager()
        
        # Parse status filter
        status_filter = None
        if args.status:
            status_filter = WorkflowStatus(args.status)
        
        workflows = await workflow_manager.list_workflows(status_filter)

        if args.format == "json":
            if console:
                console.print(JSON(json.dumps(workflows, indent=2, default=str)))
            else:
                print(json.dumps(workflows, indent=2, default=str))
        else:
            if console:
                table = Table(title="Workflows")
                table.add_column("Workflow ID", style="cyan", no_wrap=True)
                table.add_column("Execution ID", style="yellow", no_wrap=True)
                table.add_column("Pattern", style="green")
                table.add_column("Status", style="magenta")
                table.add_column("Created", style="dim")

                for workflow in workflows:
                    status_color = {
                        "pending": "yellow",
                        "running": "blue",
                        "paused": "orange",
                        "completed": "green",
                        "failed": "red",
                        "cancelled": "dim"
                    }.get(workflow["status"], "white")
                    
                    table.add_row(
                        workflow["workflow_id"],
                        workflow["execution_id"], 
                        workflow["config"].get("pattern", "unknown"),
                        f"[{status_color}]{workflow['status']}[/{status_color}]",
                        workflow["timing"]["created_at"]
                    )

                console.print(table)
            else:
                print("Workflow ID\t\tExecution ID\t\tPattern\t\tStatus\t\tCreated")
                print("-" * 80)
                for workflow in workflows:
                    print(
                        f"{workflow['workflow_id']}\t{workflow['execution_id']}\t"
                        f"{workflow['config'].get('pattern', 'unknown')}\t"
                        f"{workflow['status']}\t{workflow['timing']['created_at']}"
                    )

        return 0

    except Exception as e:
        if console:
            console.print(f"[red]Failed to list workflows: {e}[/red]")
        else:
            print(f"Failed to list workflows: {e}")
        return 1


async def execute_workflow(args) -> int:
    """Execute a workflow."""
    try:
        workflow_manager = get_workflow_manager()
        
        # Parse parameters if provided
        parameters = {}
        if args.parameters:
            try:
                parameters = json.loads(args.parameters)
            except json.JSONDecodeError as e:
                print(f"Invalid parameters JSON: {e}")
                return 1

        if args.async_run:
            # Start workflow asynchronously
            execution_id = await workflow_manager.execute_workflow(
                args.workflow_id, args.task, **parameters
            )
            
            if console:
                console.print(f"[green]✓[/green] Workflow execution started!")
                console.print(f"[cyan]Execution ID:[/cyan] {execution_id}")
                console.print(f"Use [yellow]autogen-a2a workflow get {args.workflow_id}[/yellow] to check progress")
            else:
                print("✓ Workflow execution started!")
                print(f"Execution ID: {execution_id}")
                print(f"Use 'autogen-a2a workflow get {args.workflow_id}' to check progress")
        else:
            # Execute synchronously with progress
            if console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Executing workflow...", total=None)
                    result = await workflow_manager.execute_workflow(
                        args.workflow_id, args.task, **parameters
                    )
                    progress.update(task, description="Workflow completed!")

                console.print(f"[green]✓[/green] Workflow executed successfully!")
                if result.get("result"):
                    console.print(JSON(json.dumps(result["result"], indent=2, default=str)))
            else:
                print("Executing workflow...")
                result = await workflow_manager.execute_workflow(
                    args.workflow_id, args.task, **parameters
                )
                print("✓ Workflow executed successfully!")
                if result.get("result"):
                    print(json.dumps(result["result"], indent=2, default=str))

        return 0

    except Exception as e:
        if console:
            console.print(f"[red]Failed to execute workflow: {e}[/red]")
        else:
            print(f"Failed to execute workflow: {e}")
        return 1


async def get_workflow(args) -> int:
    """Get workflow details and status."""
    try:
        workflow_manager = get_workflow_manager()
        status = await workflow_manager.get_workflow_status(args.workflow_id)
        
        if status is None:
            if console:
                console.print(f"[red]Workflow not found: {args.workflow_id}[/red]")
            else:
                print(f"Workflow not found: {args.workflow_id}")
            return 1

        if console:
            console.print(JSON(json.dumps(status, indent=2, default=str)))
        else:
            print(json.dumps(status, indent=2, default=str))

        return 0

    except Exception as e:
        if console:
            console.print(f"[red]Failed to get workflow status: {e}[/red]")
        else:
            print(f"Failed to get workflow status: {e}")
        return 1


async def cancel_workflow(args) -> int:
    """Cancel a running workflow."""
    try:
        workflow_manager = get_workflow_manager()
        success = await workflow_manager.cancel_workflow(args.workflow_id)
        
        if success:
            if console:
                console.print(f"[green]✓[/green] Workflow cancelled: {args.workflow_id}")
            else:
                print(f"✓ Workflow cancelled: {args.workflow_id}")
        else:
            if console:
                console.print(f"[red]Failed to cancel workflow: {args.workflow_id}[/red]")
            else:
                print(f"Failed to cancel workflow: {args.workflow_id}")
            return 1

        return 0

    except Exception as e:
        if console:
            console.print(f"[red]Failed to cancel workflow: {e}[/red]")
        else:
            print(f"Failed to cancel workflow: {e}")
        return 1


async def pause_workflow(args) -> int:
    """Pause a running workflow."""
    try:
        workflow_manager = get_workflow_manager()
        
        if console:
            with console.status(f"[bold blue]Pausing workflow {args.workflow_id}..."):
                success = await workflow_manager.pause_workflow(args.workflow_id)
            
            if success:
                console.print(f"[green]✅ Workflow {args.workflow_id} paused successfully[/green]")
                return 0
            else:
                console.print(f"[red]❌ Failed to pause workflow {args.workflow_id}[/red]")
                console.print("[yellow]Make sure the workflow exists and is in a running state[/yellow]")
                return 1
        else:
            print(f"Pausing workflow {args.workflow_id}...")
            success = await workflow_manager.pause_workflow(args.workflow_id)
            
            if success:
                print(f"✅ Workflow {args.workflow_id} paused successfully")
                return 0
            else:
                print(f"❌ Failed to pause workflow {args.workflow_id}")
                print("Make sure the workflow exists and is in a running state")
                return 1
                
    except Exception as e:
        if console:
            console.print(f"[red]Failed to pause workflow: {e}[/red]")
        else:
            print(f"Failed to pause workflow: {e}")
        return 1


async def resume_workflow(args) -> int:
    """Resume a paused workflow."""
    try:
        workflow_manager = get_workflow_manager()
        
        if console:
            with console.status(f"[bold blue]Resuming workflow {args.workflow_id}..."):
                success = await workflow_manager.resume_workflow(args.workflow_id)
            
            if success:
                console.print(f"[green]✅ Workflow {args.workflow_id} resumed successfully[/green]")
                return 0
            else:
                console.print(f"[red]❌ Failed to resume workflow {args.workflow_id}[/red]")
                console.print("[yellow]Make sure the workflow exists and is in a paused state[/yellow]")
                return 1
        else:
            print(f"Resuming workflow {args.workflow_id}...")
            success = await workflow_manager.resume_workflow(args.workflow_id)
            
            if success:
                print(f"✅ Workflow {args.workflow_id} resumed successfully")
                return 0
            else:
                print(f"❌ Failed to resume workflow {args.workflow_id}")
                print("Make sure the workflow exists and is in a paused state")
                return 1
                
    except Exception as e:
        if console:
            console.print(f"[red]Failed to resume workflow: {e}[/red]")
        else:
            print(f"Failed to resume workflow: {e}")
        return 1


async def validate_config_async(args) -> int:
    """Validate workflow configuration."""
    try:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Configuration file not found: {config_path}")
            return 1

        config_manager = get_config_manager()
        config = await config_manager.load_from_file(config_path)
        validation_result = await config_manager.validate_config(config)
        
        if not validation_result['valid']:
            if console:
                console.print(f"[red]Configuration validation failed:[/red]")
                for error in validation_result['errors']:
                    console.print(f"  • {error}")
                if validation_result['warnings']:
                    console.print(f"[yellow]Warnings:[/yellow]")
                    for warning in validation_result['warnings']:
                        console.print(f"  • {warning}")
            else:
                print("Configuration validation failed:")
                for error in validation_result['errors']:
                    print(f"  • {error}")
                if validation_result['warnings']:
                    print("Warnings:")
                    for warning in validation_result['warnings']:
                        print(f"  • {warning}")
            return 1
        else:
            if console:
                console.print(f"[green]✓[/green] Configuration is valid!")
                if validation_result['warnings']:
                    console.print(f"[yellow]Warnings:[/yellow]")
                    for warning in validation_result['warnings']:
                        console.print(f"  • {warning}")
            else:
                print("✓ Configuration is valid!")
                if validation_result['warnings']:
                    print("Warnings:")
                    for warning in validation_result['warnings']:
                        print(f"  • {warning}")
            return 0

    except Exception as e:
        if console:
            console.print(f"[red]Failed to validate configuration: {e}[/red]")
        else:
            print(f"Failed to validate configuration: {e}")
        return 1


def validate_config(args) -> int:
    """Validate workflow configuration."""
    try:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Configuration file not found: {config_path}")
            return 1

        config_manager = get_config_manager()
        config = config_manager.load_config(config_path)
        errors = config_manager.validate_config(config)
        
        if errors:
            if console:
                console.print(f"[red]Configuration validation failed:[/red]")
                for error in errors:
                    console.print(f"  • {error}")
            else:
                print("Configuration validation failed:")
                for error in errors:
                    print(f"  • {error}")
            return 1
        else:
            if console:
                console.print(f"[green]✓[/green] Configuration is valid!")
            else:
                print("✓ Configuration is valid!")
            return 0

    except Exception as e:
        if console:
            console.print(f"[red]Failed to validate configuration: {e}[/red]")
        else:
            print(f"Failed to validate configuration: {e}")
        return 1


async def list_templates(args) -> int:
    """List available workflow templates."""
    try:
        config_manager = get_config_manager()
        templates = await config_manager.list_templates()

        if args.format == "json":
            if console:
                console.print(JSON(json.dumps(templates, indent=2, default=str)))
            else:
                print(json.dumps(templates, indent=2, default=str))
        else:
            if console:
                table = Table(title="Workflow Templates")
                table.add_column("Template ID", style="cyan")
                table.add_column("Name", style="magenta")
                table.add_column("Category", style="green")
                table.add_column("Pattern", style="yellow")
                table.add_column("Description", style="dim")

                for template in templates:
                    table.add_row(
                        template["template_id"],
                        template["name"],
                        template["category"],
                        template["pattern"],
                        template["description"][:50] + "..." if len(template["description"]) > 50 else template["description"]
                    )

                console.print(table)
            else:
                print("Template ID\t\tName\t\tCategory\t\tPattern\t\tDescription")
                print("-" * 80)
                for template in templates:
                    desc = template["description"][:30] + "..." if len(template["description"]) > 30 else template["description"]
                    print(f"{template['template_id']}\t{template['name']}\t{template['category']}\t{template['pattern']}\t{desc}")

        return 0

    except Exception as e:
        if console:
            console.print(f"[red]Failed to list templates: {e}[/red]")
        else:
            print(f"Failed to list templates: {e}")
        return 1


async def visualize_workflow(args) -> int:
    """Visualize workflow graph structure."""
    try:
        workflow_manager = get_workflow_manager()
        
        # Get workflow status to access the graph structure
        workflow_status = await workflow_manager.get_workflow_status(args.workflow_id)
        
        if workflow_status is None:
            if console:
                console.print(f"[red]Workflow not found: {args.workflow_id}[/red]")
            else:
                print(f"Workflow not found: {args.workflow_id}")
            return 1
        
        # Check if this is a graph workflow
        pattern = workflow_status.get("config", {}).get("pattern")
        if pattern != "graph":
            if console:
                console.print(f"[yellow]Warning: Workflow {args.workflow_id} is not a graph workflow (pattern: {pattern})[/yellow]")
            else:
                print(f"Warning: Workflow {args.workflow_id} is not a graph workflow (pattern: {pattern})")
        
        # Get execution graph if available
        execution_graph = workflow_status.get("execution_graph")
        if not execution_graph:
            if console:
                console.print("[yellow]No graph structure available for this workflow[/yellow]")
            else:
                print("No graph structure available for this workflow")
            return 1
        
        if args.format == "json":
            output = json.dumps(execution_graph, indent=2, default=str)
            
        elif args.format == "mermaid":
            output = _generate_mermaid_graph(execution_graph)
            
        else:  # ascii
            output = _generate_ascii_graph(execution_graph)
        
        # Output to file or console
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            
            if console:
                console.print(f"[green]✓[/green] Graph visualization saved to: {args.output}")
            else:
                print(f"✓ Graph visualization saved to: {args.output}")
        else:
            if console:
                console.print(output)
            else:
                print(output)
        
        return 0
    
    except Exception as e:
        if console:
            console.print(f"[red]Failed to visualize workflow: {e}[/red]")
        else:
            print(f"Failed to visualize workflow: {e}")
        return 1


def _generate_ascii_graph(execution_graph: Dict[str, Any]) -> str:
    """Generate ASCII representation of workflow graph."""
    nodes = execution_graph.get("nodes", {})
    edges = execution_graph.get("edges", {})
    execution_state = execution_graph.get("execution_state", {})
    
    output = []
    output.append("Workflow Graph Visualization")
    output.append("=" * 40)
    output.append("")
    
    # Show nodes with status
    output.append("Nodes:")
    output.append("-" * 20)
    for node_id, node_info in nodes.items():
        status = node_info["status"]
        agent_id = node_info["agent_id"]
        name = node_info["name"]
        
        status_symbol = {
            "pending": "⏳",
            "ready": "🟡", 
            "running": "🔵",
            "completed": "✅",
            "failed": "❌",
            "skipped": "⏭️"
        }.get(status, "❓")
        
        output.append(f"  {status_symbol} {node_id} ({name}) -> {agent_id}")
        
        if node_info.get("error"):
            output.append(f"      Error: {node_info['error']}")
    
    output.append("")
    
    # Show edges
    output.append("Edges:")
    output.append("-" * 20)
    for edge_id, edge_info in edges.items():
        source = edge_info["source_node"]
        target = edge_info["target_node"]
        edge_type = edge_info["edge_type"]
        
        edge_symbol = {
            "sequential": "→",
            "parallel": "⇉",
            "conditional": "⟶?",
            "synchronize": "⇶"
        }.get(edge_type, "→")
        
        output.append(f"  {source} {edge_symbol} {target} ({edge_type})")
    
    output.append("")
    
    # Show execution state
    current_nodes = execution_state.get("current_nodes", [])
    completed_nodes = execution_state.get("completed_nodes", [])
    failed_nodes = execution_state.get("failed_nodes", [])
    
    if current_nodes:
        output.append(f"Currently executing: {', '.join(current_nodes)}")
    if completed_nodes:
        output.append(f"Completed: {', '.join(completed_nodes)}")
    if failed_nodes:
        output.append(f"Failed: {', '.join(failed_nodes)}")
    
    return "\n".join(output)


def _generate_mermaid_graph(execution_graph: Dict[str, Any]) -> str:
    """Generate Mermaid diagram representation of workflow graph."""
    nodes = execution_graph.get("nodes", {})
    edges = execution_graph.get("edges", {})
    
    output = []
    output.append("graph TD")
    output.append("")
    
    # Add nodes with styling based on status
    for node_id, node_info in nodes.items():
        status = node_info["status"]
        name = node_info["name"]
        
        # Create node definition
        output.append(f"    {node_id}[\"{name}\"]")
        
        # Add styling based on status
        if status == "completed":
            output.append(f"    {node_id} --> {node_id}_style{{\"fill:#90EE90\"}}")
        elif status == "running":
            output.append(f"    {node_id} --> {node_id}_style{{\"fill:#87CEEB\"}}")
        elif status == "failed":
            output.append(f"    {node_id} --> {node_id}_style{{\"fill:#FFB6C1\"}}")
    
    output.append("")
    
    # Add edges
    for edge_id, edge_info in edges.items():
        source = edge_info["source_node"]
        target = edge_info["target_node"]
        edge_type = edge_info["edge_type"]
        
        # Different arrow styles for different edge types
        if edge_type == "conditional":
            output.append(f"    {source} -.-> {target}")
        elif edge_type == "parallel":
            output.append(f"    {source} ==> {target}")
        else:
            output.append(f"    {source} --> {target}")
    
    return "\n".join(output)


async def create_swarm(args) -> int:
    """Create a new swarm from configuration."""
    try:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Configuration file not found: {config_path}")
            return 1

        # Load agent mapping if provided
        agent_mapping = None
        if args.agent_mapping:
            try:
                agent_mapping = json.loads(args.agent_mapping)
            except json.JSONDecodeError as e:
                print(f"Invalid agent mapping JSON: {e}")
                return 1

        workflow_manager = get_workflow_manager()
        
        if console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Creating swarm...", total=None)
                workflow = await workflow_manager.create_workflow_from_file(
                    config_path, agent_mapping
                )
                progress.update(task, description="Swarm created!")

            console.print(f"[green]✓[/green] Swarm created successfully!")
            console.print(f"[cyan]Swarm ID:[/cyan] {workflow.workflow_id}")
            console.print(f"[cyan]Execution ID:[/cyan] {workflow.execution_id}")
        else:
            workflow = await workflow_manager.create_workflow_from_file(
                config_path, agent_mapping
            )
            print(f"Swarm created successfully!")
            print(f"Swarm ID: {workflow.workflow_id}")
            print(f"Execution ID: {workflow.execution_id}")
            
        return 0
        
    except Exception as e:
        print(f"Failed to create swarm: {e}")
        return 1


async def monitor_swarm(args) -> int:
    """Monitor swarm execution with real-time metrics."""
    try:
        workflow_manager = get_workflow_manager()
        execution_id = args.id
        
        if console:
            console.print(f"[cyan]Monitoring swarm:[/cyan] {execution_id}")
            console.print("Press Ctrl+C to stop monitoring...")
            
            try:
                while True:
                    # Get workflow status
                    try:
                        workflow = await workflow_manager.get_workflow(execution_id)
                        if not workflow:
                            console.print(f"[red]Swarm not found: {execution_id}[/red]")
                            return 1
                            
                        orchestrator = workflow.orchestrator
                        if hasattr(orchestrator, 'get_swarm_metrics'):
                            metrics = await orchestrator.get_swarm_metrics()
                            
                            # Clear screen and display metrics
                            console.clear()
                            console.print(f"[bold cyan]Swarm Monitoring - {execution_id}[/bold cyan]")
                            console.print(f"[bold]Status:[/bold] {workflow.status.value}")
                            
                            if args.metrics in ["all", "participation"]:
                                console.print("\n[bold yellow]Agent Participation:[/bold yellow]")
                                for agent_id, rate in metrics.agent_participation_rates.items():
                                    console.print(f"  {agent_id}: {rate:.1%}")
                            
                            if args.metrics in ["all", "handoffs"]:
                                console.print(f"\n[bold yellow]Handoff Statistics:[/bold yellow]")
                                console.print(f"  Total Handoffs: {metrics.total_handoffs}")
                                console.print(f"  Autonomous Handoffs: {metrics.autonomous_handoffs}")
                                console.print(f"  Average Response Time: {metrics.avg_response_time:.2f}s")
                            
                            if args.metrics in ["all", "performance"]:
                                console.print(f"\n[bold yellow]Performance:[/bold yellow]")
                                console.print(f"  Messages Processed: {metrics.total_messages}")
                                console.print(f"  Active Agents: {len(metrics.active_agents)}")
                                console.print(f"  Convergence Score: {metrics.convergence_score:.2f}")
                            
                        else:
                            console.print("[yellow]Swarm metrics not available for this workflow type[/yellow]")
                            
                    except Exception as e:
                        console.print(f"[red]Error getting metrics: {e}[/red]")
                    
                    await asyncio.sleep(args.refresh)
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Monitoring stopped[/yellow]")
                return 0
        else:
            print(f"Monitoring swarm: {execution_id}")
            # Basic monitoring without rich console
            workflow = await workflow_manager.get_workflow(execution_id)
            if workflow:
                print(f"Status: {workflow.status.value}")
            else:
                print("Swarm not found")
                return 1
                
        return 0
        
    except Exception as e:
        print(f"Failed to monitor swarm: {e}")
        return 1


async def tune_swarm(args) -> int:
    """Tune swarm parameters during execution."""
    try:
        workflow_manager = get_workflow_manager()
        execution_id = args.id
        
        workflow = await workflow_manager.get_workflow(execution_id)
        if not workflow:
            print(f"Swarm not found: {execution_id}")
            return 1
            
        orchestrator = workflow.orchestrator
        if not hasattr(orchestrator, 'tune_parameter'):
            print("Parameter tuning not supported for this workflow type")
            return 1
            
        # Get current value if no new value provided
        if args.value is None:
            if hasattr(orchestrator, 'get_parameter'):
                current_value = await orchestrator.get_parameter(args.parameter)
                print(f"Current {args.parameter}: {current_value}")
                return 0
            else:
                print("Must provide --value for parameter tuning")
                return 1
        
        # Apply parameter tuning
        success = await orchestrator.tune_parameter(args.parameter, args.value)
        
        if console:
            if success:
                console.print(f"[green]✓[/green] Parameter tuned successfully!")
                console.print(f"[cyan]{args.parameter}[/cyan] = {args.value}")
            else:
                console.print(f"[red]Failed to tune parameter[/red]")
        else:
            if success:
                print(f"Parameter tuned successfully: {args.parameter} = {args.value}")
            else:
                print("Failed to tune parameter")
                
        return 0 if success else 1
        
    except Exception as e:
        print(f"Failed to tune swarm: {e}")
        return 1


async def swarm_analytics(args) -> int:
    """Get comprehensive swarm analytics."""
    try:
        workflow_manager = get_workflow_manager()
        execution_id = args.id
        
        workflow = await workflow_manager.get_workflow(execution_id)
        if not workflow:
            print(f"Swarm not found: {execution_id}")
            return 1
            
        orchestrator = workflow.orchestrator
        if not hasattr(orchestrator, 'get_analytics'):
            print("Analytics not supported for this workflow type")
            return 1
            
        analytics = await orchestrator.get_analytics()
        
        if args.output == "json":
            import json
            print(json.dumps(analytics, indent=2, default=str))
        elif args.output == "csv":
            # Output key metrics as CSV
            print("metric,value")
            for key, value in analytics.items():
                if isinstance(value, (int, float)):
                    print(f"{key},{value}")
        else:  # console output
            if console:
                console.print(f"[bold cyan]Swarm Analytics - {execution_id}[/bold cyan]")
                
                # Display analytics in a structured format
                for section, data in analytics.items():
                    console.print(f"\n[bold yellow]{section.replace('_', ' ').title()}:[/bold yellow]")
                    if isinstance(data, dict):
                        for key, value in data.items():
                            console.print(f"  {key}: {value}")
                    else:
                        console.print(f"  {data}")
            else:
                print(f"Swarm Analytics - {execution_id}")
                for section, data in analytics.items():
                    print(f"\n{section.replace('_', ' ').title()}:")
                    if isinstance(data, dict):
                        for key, value in data.items():
                            print(f"  {key}: {value}")
                    else:
                        print(f"  {data}")
                        
        return 0
        
    except Exception as e:
        print(f"Failed to get swarm analytics: {e}")
        return 1
