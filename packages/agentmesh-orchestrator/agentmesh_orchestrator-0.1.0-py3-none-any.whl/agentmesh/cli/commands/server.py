"""Server management CLI commands."""

import argparse
import asyncio
import signal
import sys
from typing import Optional

try:
    from rich.console import Console

    console = Console()
except ImportError:
    console = None


def setup_parser(subparsers) -> None:
    """Setup server command parser."""
    server_parser = subparsers.add_parser(
        "server",
        help="Manage the API server",
        description="Start, stop, and manage the AutoGen A2A API server",
    )

    server_subparsers = server_parser.add_subparsers(
        dest="server_action", help="Server actions"
    )

    # Start server command
    start_parser = server_subparsers.add_parser("start", help="Start the API server")
    start_parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    start_parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
    )
    start_parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )
    start_parser.add_argument(
        "--workers", type=int, default=1, help="Number of worker processes (default: 1)"
    )

    # Status command
    status_parser = server_subparsers.add_parser("status", help="Check server status")
    status_parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Server URL to check (default: http://localhost:8000)",
    )


def handle_server_command(args) -> int:
    """Handle server commands."""
    try:
        if args.server_action == "start":
            return start_server(args)
        elif args.server_action == "status":
            return check_server_status(args)
        else:
            print("Unknown server action")
            return 1
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def start_server(args) -> int:
    """Start the API server."""
    if console:
        console.print(f"[yellow]Starting AutoGen A2A API server...[/yellow]")
        console.print(f"[cyan]Host:[/cyan] {args.host}")
        console.print(f"[cyan]Port:[/cyan] {args.port}")
        console.print(f"[cyan]Reload:[/cyan] {args.reload}")
        console.print(f"[cyan]Workers:[/cyan] {args.workers}")
    else:
        print(f"Starting AutoGen A2A API server...")
        print(f"Host: {args.host}")
        print(f"Port: {args.port}")
        print(f"Reload: {args.reload}")
        print(f"Workers: {args.workers}")

    try:
        # Try to import uvicorn and start the server
        import uvicorn

        # TODO: Replace with actual FastAPI app import
        # from agentmesh.api.main import app

        # For now, create a simple placeholder app
        try:
            from fastapi import FastAPI

            app = FastAPI(title="AutoGen A2A API", version="0.1.0")

            @app.get("/")
            async def root():
                return {"message": "AutoGen A2A API is running", "version": "0.1.0"}

            @app.get("/health")
            async def health():
                return {"status": "healthy"}

        except ImportError:
            print(
                "FastAPI not available. Please install it with: pip install fastapi uvicorn"
            )
            return 1

        if console:
            console.print(
                f"[green]✓[/green] Server starting at [cyan]http://{args.host}:{args.port}[/cyan]"
            )
            console.print("[yellow]Press Ctrl+C to stop the server[/yellow]")
        else:
            print(f"✓ Server starting at http://{args.host}:{args.port}")
            print("Press Ctrl+C to stop the server")

        # Configure uvicorn
        config = uvicorn.Config(
            app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=(
                args.workers if not args.reload else 1
            ),  # reload doesn't work with multiple workers
            log_level="info",
        )

        server = uvicorn.Server(config)

        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            if console:
                console.print("\n[yellow]Shutting down server gracefully...[/yellow]")
            else:
                print("\nShutting down server gracefully...")
            server.should_exit = True

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Run the server
        asyncio.run(server.serve())

    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages: pip install uvicorn fastapi")
        return 1
    except Exception as e:
        print(f"Failed to start server: {e}")
        return 1

    return 0


def check_server_status(args) -> int:
    """Check server status."""
    import httpx

    try:
        if console:
            console.print(f"[yellow]Checking server status at {args.url}...[/yellow]")
        else:
            print(f"Checking server status at {args.url}...")

        response = httpx.get(f"{args.url}/health", timeout=5.0)

        if response.status_code == 200:
            data = response.json()
            if console:
                console.print(f"[green]✓[/green] Server is healthy")
                console.print(f"[cyan]Status:[/cyan] {data.get('status', 'unknown')}")
            else:
                print("✓ Server is healthy")
                print(f"Status: {data.get('status', 'unknown')}")
            return 0
        else:
            if console:
                console.print(
                    f"[red]✗[/red] Server returned status code: {response.status_code}"
                )
            else:
                print(f"✗ Server returned status code: {response.status_code}")
            return 1

    except httpx.ConnectError:
        if console:
            console.print(f"[red]✗[/red] Cannot connect to server at {args.url}")
        else:
            print(f"✗ Cannot connect to server at {args.url}")
        return 1
    except Exception as e:
        if console:
            console.print(f"[red]✗[/red] Error checking server status: {e}")
        else:
            print(f"✗ Error checking server status: {e}")
        return 1
