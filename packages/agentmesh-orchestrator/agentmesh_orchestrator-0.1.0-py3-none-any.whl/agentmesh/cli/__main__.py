"""CLI main entry point for AgentMesh system."""

import argparse
import asyncio
import sys
from typing import List, Optional

from rich.console import Console
from rich.table import Table

from agentmesh.cli.commands import agent, workflow, server

console = Console()


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="agentmesh",
        description="AgentMesh - Multi-Agent Orchestration Platform CLI",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("--version", action="version", version="agentmesh 0.1.0")

    parser.add_argument(
        "--server",
        type=str,
        default="http://localhost:8000",
        help="API server URL (default: http://localhost:8000)",
    )

    parser.add_argument("--api-key", type=str, help="API key for authentication")

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", metavar="COMMAND"
    )

    # Setup command parsers
    agent.setup_parser(subparsers)
    workflow.setup_parser(subparsers)
    workflow.add_swarm_subparser(subparsers)  # Add swarm commands
    server.setup_parser(subparsers)

    return parser


def print_help():
    """Print help information with examples."""
    console.print("[bold]AgentMesh CLI[/bold] - Multi-Agent Orchestration Platform")
    console.print()

    # Create examples table
    table = Table(title="Common Commands")
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    table.add_column("Example", style="green")

    table.add_row(
        "agent create",
        "Create a new agent",
        "agentmesh agent create --name architect --type assistant",
    )
    table.add_row("agent list", "List all agents", "agentmesh agent list")
    table.add_row(
        "workflow create",
        "Create a workflow",
        "agentmesh workflow create --config workflow.yaml",
    )
    table.add_row(
        "workflow run", "Run a workflow", "agentmesh workflow run --id workflow-123"
    )
    table.add_row(
        "swarm create", "Create a swarm", "agentmesh swarm create --config swarm.yaml"
    )
    table.add_row(
        "swarm monitor", "Monitor a swarm", "agentmesh swarm monitor --id swarm-123"
    )
    table.add_row(
        "server start", "Start the API server", "agentmesh server start --port 8000"
    )

    console.print(table)
    console.print()
    console.print(
        "Use [cyan]agentmesh COMMAND --help[/cyan] for more information about a command."
    )


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()

    if args is None:
        args = sys.argv[1:]

    # If no arguments provided, show help
    if not args:
        print_help()
        return 0

    parsed_args = parser.parse_args(args)

    try:
        # Route to appropriate command handler
        if parsed_args.command == "agent":
            from agentmesh.cli.commands.agent import handle_agent_command

            return handle_agent_command(parsed_args)
        elif parsed_args.command == "workflow":
            from agentmesh.cli.commands.workflow import handle_workflow_command

            return handle_workflow_command(parsed_args)
        elif parsed_args.command == "swarm":
            from agentmesh.cli.commands.workflow import handle_swarm_command
            
            return asyncio.run(handle_swarm_command(parsed_args))
        elif parsed_args.command == "server":
            from agentmesh.cli.commands.server import handle_server_command

            return handle_server_command(parsed_args)
        else:
            console.print(f"[red]Unknown command: {parsed_args.command}[/red]")
            print_help()
            return 1

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        return 130
    except Exception as e:
        if parsed_args.verbose:
            console.print_exception()
        else:
            console.print(f"[red]Error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
