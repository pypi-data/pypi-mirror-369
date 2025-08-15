"""Agent management CLI commands."""

import json
import asyncio

try:
    from rich.console import Console
    from rich.table import Table
    from rich.json import JSON

    console = Console()
except ImportError:
    # Fallback if rich is not available
    console = None

# Import our models and manager
from agentmesh.models.agent import AgentConfig, AgentType
from agentmesh.core.agent_manager import AgentManager

# Global agent manager instance
agent_manager = AgentManager()


def setup_parser(subparsers) -> None:
    """Setup agent command parser."""
    agent_parser = subparsers.add_parser(
        "agent",
        help="Manage agents",
        description="Create, list, start, stop and manage agents",
    )

    agent_subparsers = agent_parser.add_subparsers(
        dest="agent_action", help="Agent actions"
    )

    # Create agent command
    create_parser = agent_subparsers.add_parser("create", help="Create a new agent")
    create_parser.add_argument("--name", required=True, help="Agent name")
    create_parser.add_argument(
        "--type", required=True, choices=["assistant", "user_proxy"], help="Agent type"
    )
    create_parser.add_argument(
        "--model", default="gpt-4o", help="Model to use (default: gpt-4o)"
    )
    create_parser.add_argument("--system-message", help="System message for the agent")
    create_parser.add_argument("--config", help="Path to agent configuration file")

    # List agents command
    list_parser = agent_subparsers.add_parser("list", help="List all agents")
    list_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    list_parser.add_argument(
        "--status",
        choices=["active", "inactive", "all"],
        default="all",
        help="Filter by status (default: all)",
    )

    # Get agent command
    get_parser = agent_subparsers.add_parser("get", help="Get agent details")
    get_parser.add_argument("agent_id", help="Agent ID or name")

    # Start agent command
    start_parser = agent_subparsers.add_parser("start", help="Start an agent")
    start_parser.add_argument("agent_id", help="Agent ID or name")

    # Stop agent command
    stop_parser = agent_subparsers.add_parser("stop", help="Stop an agent")
    stop_parser.add_argument("agent_id", help="Agent ID or name")

    # Delete agent command
    delete_parser = agent_subparsers.add_parser("delete", help="Delete an agent")
    delete_parser.add_argument("agent_id", help="Agent ID or name")
    delete_parser.add_argument(
        "--force", action="store_true", help="Force delete without confirmation"
    )


def handle_agent_command(args) -> int:
    """Handle agent commands."""
    try:
        if args.agent_action == "create":
            return create_agent(args)
        elif args.agent_action == "list":
            return list_agents(args)
        elif args.agent_action == "get":
            return get_agent(args)
        elif args.agent_action == "start":
            return start_agent(args)
        elif args.agent_action == "stop":
            return stop_agent(args)
        elif args.agent_action == "delete":
            return delete_agent(args)
        else:
            console.print("[red]Unknown agent action[/red]")
            return 1
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


def create_agent(args) -> int:
    """Create a new agent."""
    if console:
        console.print("[yellow]Creating agent...[/yellow]")
    else:
        print("Creating agent...")

    try:
        # Build agent configuration
        config = AgentConfig(
            name=args.name,
            type=AgentType(args.type),
            model=args.model,
            system_message=args.system_message,
        )

        # Load from config file if provided
        if args.config:
            try:
                import yaml

                with open(args.config, "r") as f:
                    file_config = yaml.safe_load(f)
                    # Update config with file values
                    for key, value in file_config.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
            except Exception as e:
                if console:
                    console.print(f"[red]Error loading config file: {e}[/red]")
                else:
                    print(f"Error loading config file: {e}")
                return 1

        # Create agent using AgentManager
        agent_id = asyncio.run(agent_manager.create_agent(config))

        if console:
            console.print("[green]✓[/green] Agent configuration:")
            console.print(
                JSON(
                    json.dumps(
                        {
                            "id": agent_id,
                            "name": config.name,
                            "type": config.type,
                            "model": config.model,
                            "system_message": config.system_message,
                        },
                        indent=2,
                    )
                )
            )
            console.print(
                f"[green]✓[/green] Agent created with ID: [cyan]{agent_id}[/cyan]"
            )
        else:
            print("✓ Agent configuration:")
            print(
                json.dumps(
                    {
                        "id": agent_id,
                        "name": config.name,
                        "type": config.type,
                        "model": config.model,
                        "system_message": config.system_message,
                    },
                    indent=2,
                )
            )
            print(f"✓ Agent created with ID: {agent_id}")

        return 0

    except Exception as e:
        if console:
            console.print(f"[red]Error creating agent: {e}[/red]")
        else:
            print(f"Error creating agent: {e}")
        return 1


def list_agents(args) -> int:
    """List all agents."""
    try:
        # Get agents from AgentManager
        agents = asyncio.run(agent_manager.list_agents())

        # Filter by status if specified
        if args.status != "all":
            from agentmesh.models.agent import AgentStatus

            status_filter = AgentStatus(args.status)
            agents = [a for a in agents if a.status == status_filter]

        if args.format == "json":
            agents_data = [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "type": agent.type,
                    "status": agent.status,
                    "model": agent.model,
                    "created": agent.created_at.isoformat(),
                    "message_count": agent.message_count,
                }
                for agent in agents
            ]
            if console:
                console.print(JSON(json.dumps(agents_data, indent=2)))
            else:
                print(json.dumps(agents_data, indent=2))
        else:
            if console:
                table = Table(title="Agents")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="magenta")
                table.add_column("Type", style="green")
                table.add_column("Status", style="yellow")
                table.add_column("Model", style="blue")
                table.add_column("Messages", style="white")

                for agent in agents:
                    status_style = (
                        "green"
                        if agent.status == "active"
                        else "red" if agent.status == "error" else "yellow"
                    )
                    table.add_row(
                        agent.id,
                        agent.name,
                        agent.type,
                        f"[{status_style}]{agent.status}[/{status_style}]",
                        agent.model,
                        str(agent.message_count),
                    )

                console.print(table)
            else:
                print("ID\t\tName\t\tType\t\tStatus\t\tModel\t\tMessages")
                print("-" * 80)
                for agent in agents:
                    print(
                        f"{agent.id}\t{agent.name}\t{agent.type}\t{agent.status}\t{agent.model}\t{agent.message_count}"
                    )

        return 0

    except Exception as e:
        if console:
            console.print(f"[red]Error listing agents: {e}[/red]")
        else:
            print(f"Error listing agents: {e}")
        return 1


def get_agent(args) -> int:
    """Get agent details."""
    try:
        if console:
            console.print(f"[yellow]Getting agent: {args.agent_id}[/yellow]")
        else:
            print(f"Getting agent: {args.agent_id}")

        # Try to get agent by ID first, then by name
        try:
            agent = asyncio.run(agent_manager.get_agent(args.agent_id))
        except ValueError:
            # Try by name
            agent = asyncio.run(agent_manager.get_agent_by_name(args.agent_id))
            if not agent:
                raise ValueError(f"Agent '{args.agent_id}' not found")

        agent_data = {
            "id": agent.id,
            "name": agent.name,
            "type": agent.type,
            "status": agent.status,
            "model": agent.model,
            "provider": agent.provider,
            "created": agent.created_at.isoformat(),
            "updated": agent.updated_at.isoformat(),
            "last_active": agent.last_active.isoformat() if agent.last_active else None,
            "message_count": agent.message_count,
            "conversation_count": agent.conversation_count,
            "uptime_seconds": agent.uptime_seconds,
            "config": agent.config,
        }

        if console:
            console.print(JSON(json.dumps(agent_data, indent=2)))
        else:
            print(json.dumps(agent_data, indent=2))

        return 0

    except Exception as e:
        if console:
            console.print(f"[red]Error getting agent: {e}[/red]")
        else:
            print(f"Error getting agent: {e}")
        return 1


def start_agent(args) -> int:
    """Start an agent."""
    try:
        if console:
            console.print(f"[yellow]Starting agent: {args.agent_id}[/yellow]")
        else:
            print(f"Starting agent: {args.agent_id}")

        success = asyncio.run(agent_manager.start_agent(args.agent_id))

        if success:
            if console:
                console.print(
                    f"[green]✓[/green] Agent {args.agent_id} started successfully"
                )
            else:
                print(f"✓ Agent {args.agent_id} started successfully")
            return 0
        else:
            if console:
                console.print(f"[red]✗[/red] Failed to start agent {args.agent_id}")
            else:
                print(f"✗ Failed to start agent {args.agent_id}")
            return 1

    except Exception as e:
        if console:
            console.print(f"[red]Error starting agent: {e}[/red]")
        else:
            print(f"Error starting agent: {e}")
        return 1


def stop_agent(args) -> int:
    """Stop an agent."""
    try:
        if console:
            console.print(f"[yellow]Stopping agent: {args.agent_id}[/yellow]")
        else:
            print(f"Stopping agent: {args.agent_id}")

        success = asyncio.run(agent_manager.stop_agent(args.agent_id))

        if success:
            if console:
                console.print(
                    f"[green]✓[/green] Agent {args.agent_id} stopped successfully"
                )
            else:
                print(f"✓ Agent {args.agent_id} stopped successfully")
            return 0
        else:
            if console:
                console.print(f"[red]✗[/red] Failed to stop agent {args.agent_id}")
            else:
                print(f"✗ Failed to stop agent {args.agent_id}")
            return 1

    except Exception as e:
        if console:
            console.print(f"[red]Error stopping agent: {e}[/red]")
        else:
            print(f"Error stopping agent: {e}")
        return 1


def delete_agent(args) -> int:
    """Delete an agent."""
    try:
        if not args.force:
            if console:
                response = console.input(
                    f"Are you sure you want to delete agent {args.agent_id}? [y/N]: "
                )
            else:
                response = input(
                    f"Are you sure you want to delete agent {args.agent_id}? [y/N]: "
                )

            if response.lower() not in ["y", "yes"]:
                print("Operation cancelled")
                return 0

        if console:
            console.print(f"[yellow]Deleting agent: {args.agent_id}[/yellow]")
        else:
            print(f"Deleting agent: {args.agent_id}")

        success = asyncio.run(agent_manager.delete_agent(args.agent_id))

        if success:
            if console:
                console.print(
                    f"[green]✓[/green] Agent {args.agent_id} deleted successfully"
                )
            else:
                print(f"✓ Agent {args.agent_id} deleted successfully")
            return 0
        else:
            if console:
                console.print(f"[red]✗[/red] Failed to delete agent {args.agent_id}")
            else:
                print(f"✗ Failed to delete agent {args.agent_id}")
            return 1

    except Exception as e:
        if console:
            console.print(f"[red]Error deleting agent: {e}[/red]")
        else:
            print(f"Error deleting agent: {e}")
        return 1
