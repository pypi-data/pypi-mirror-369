"""CLI commands for user and security management."""

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

from ...security import get_auth_manager
from ...security.permissions import Role

app = typer.Typer(help="User and security management commands")
console = Console()


@app.command()
def create_admin(
    username: str = typer.Option(..., prompt=True, help="Admin username"),
    email: str = typer.Option(..., prompt=True, help="Admin email"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Admin password"),
    full_name: Optional[str] = typer.Option(None, help="Admin full name"),
):
    """Create a new admin user."""
    async def _create_admin():
        auth_manager = get_auth_manager()
        await auth_manager.connect()
        
        try:
            # Check if user already exists
            existing_user = await auth_manager.get_user_by_username(username)
            if existing_user:
                console.print(f"[red]Error: User '{username}' already exists[/red]")
                return
            
            # Create admin user
            user = await auth_manager.create_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                roles=[Role.ADMIN]
            )
            
            console.print(f"[green]✓ Admin user '{username}' created successfully![/green]")
            console.print(f"User ID: {user.id}")
            console.print(f"Email: {user.email}")
            console.print(f"Roles: {user.roles}")
            
        except Exception as e:
            console.print(f"[red]Error creating admin user: {e}[/red]")
        finally:
            await auth_manager.disconnect()
    
    asyncio.run(_create_admin())


@app.command()
def create_user(
    username: str = typer.Option(..., prompt=True, help="Username"),
    email: str = typer.Option(..., prompt=True, help="User email"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="User password"),
    full_name: Optional[str] = typer.Option(None, help="User full name"),
    role: str = typer.Option("user", help="User role (user, developer, agent_operator, admin)"),
):
    """Create a new user."""
    async def _create_user():
        auth_manager = get_auth_manager()
        await auth_manager.connect()
        
        try:
            # Validate role
            if role not in [r.value for r in Role]:
                console.print(f"[red]Error: Invalid role '{role}'. Valid roles: {[r.value for r in Role]}[/red]")
                return
            
            # Check if user already exists
            existing_user = await auth_manager.get_user_by_username(username)
            if existing_user:
                console.print(f"[red]Error: User '{username}' already exists[/red]")
                return
            
            # Create user
            user = await auth_manager.create_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                roles=[role]
            )
            
            console.print(f"[green]✓ User '{username}' created successfully![/green]")
            console.print(f"User ID: {user.id}")
            console.print(f"Email: {user.email}")
            console.print(f"Roles: {user.roles}")
            
        except Exception as e:
            console.print(f"[red]Error creating user: {e}[/red]")
        finally:
            await auth_manager.disconnect()
    
    asyncio.run(_create_user())


@app.command()
def list_users():
    """List all users."""
    async def _list_users():
        auth_manager = get_auth_manager()
        await auth_manager.connect()
        
        try:
            # Note: This would need a method to list users in auth_manager
            console.print("[yellow]User listing functionality needs to be implemented in auth_manager[/yellow]")
            
        except Exception as e:
            console.print(f"[red]Error listing users: {e}[/red]")
        finally:
            await auth_manager.disconnect()
    
    asyncio.run(_list_users())


@app.command()
def reset_password(
    username: str = typer.Option(..., prompt=True, help="Username"),
    new_password: str = typer.Option(..., prompt=True, hide_input=True, help="New password"),
):
    """Reset a user's password."""
    async def _reset_password():
        auth_manager = get_auth_manager()
        await auth_manager.connect()
        
        try:
            # Get user
            user = await auth_manager.get_user_by_username(username)
            if not user:
                console.print(f"[red]Error: User '{username}' not found[/red]")
                return
            
            # Hash new password and update
            password_hash = auth_manager.hash_password(new_password)
            await auth_manager.redis_client.set(f"user_password:{user.id}", password_hash)
            
            console.print(f"[green]✓ Password reset for user '{username}'[/green]")
            
        except Exception as e:
            console.print(f"[red]Error resetting password: {e}[/red]")
        finally:
            await auth_manager.disconnect()
    
    asyncio.run(_reset_password())


@app.command()
def create_api_key(
    username: str = typer.Option(..., prompt=True, help="Username"),
    key_name: str = typer.Option(..., prompt=True, help="API key name"),
    permissions: str = typer.Option("", help="Comma-separated list of permissions"),
    expires_days: Optional[int] = typer.Option(None, help="Expiration in days"),
):
    """Create an API key for a user."""
    async def _create_api_key():
        auth_manager = get_auth_manager()
        await auth_manager.connect()
        
        try:
            # Get user
            user = await auth_manager.get_user_by_username(username)
            if not user:
                console.print(f"[red]Error: User '{username}' not found[/red]")
                return
            
            # Parse permissions
            permission_list = []
            if permissions:
                permission_list = [p.strip() for p in permissions.split(",")]
            
            # Create API key
            raw_key, api_key = await auth_manager.create_api_key(
                user_id=user.id,
                name=key_name,
                permissions=permission_list,
                expires_in_days=expires_days
            )
            
            console.print(f"[green]✓ API key created successfully![/green]")
            console.print(f"Key ID: {api_key.id}")
            console.print(f"Key Name: {api_key.name}")
            console.print(f"[yellow]API Key: {raw_key}[/yellow]")
            console.print("[red]⚠️  Save this key securely - it won't be shown again![/red]")
            
        except Exception as e:
            console.print(f"[red]Error creating API key: {e}[/red]")
        finally:
            await auth_manager.disconnect()
    
    asyncio.run(_create_api_key())


@app.command()
def setup():
    """Interactive setup wizard for initial system configuration."""
    console.print("[bold blue]AutoGen A2A Security Setup Wizard[/bold blue]")
    console.print("This wizard will help you create the initial admin user.\n")
    
    # Get admin user details
    username = Prompt.ask("Admin username", default="admin")
    email = Prompt.ask("Admin email")
    password = Prompt.ask("Admin password (min 8 characters)", password=True)
    
    if len(password) < 8:
        console.print("[red]Error: Password must be at least 8 characters long[/red]")
        return
    
    full_name = Prompt.ask("Admin full name (optional)", default="")
    
    # Confirm
    console.print(f"\n[yellow]Creating admin user:[/yellow]")
    console.print(f"Username: {username}")
    console.print(f"Email: {email}")
    console.print(f"Full name: {full_name or 'Not provided'}")
    
    if not Confirm.ask("Create this admin user?"):
        console.print("Setup cancelled.")
        return
    
    # Create admin user
    async def _setup():
        auth_manager = get_auth_manager()
        await auth_manager.connect()
        
        try:
            # Check if any users exist
            existing_user = await auth_manager.get_user_by_username(username)
            if existing_user:
                console.print(f"[red]Error: User '{username}' already exists[/red]")
                return
            
            # Create admin user
            user = await auth_manager.create_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name or None,
                roles=[Role.ADMIN]
            )
            
            console.print(f"\n[green]✓ Setup complete! Admin user created:[/green]")
            console.print(f"User ID: {user.id}")
            console.print(f"Username: {user.username}")
            console.print(f"Email: {user.email}")
            
            console.print(f"\n[blue]You can now start the API server and log in with these credentials.[/blue]")
            
        except Exception as e:
            console.print(f"[red]Setup failed: {e}[/red]")
        finally:
            await auth_manager.disconnect()
    
    asyncio.run(_setup())


if __name__ == "__main__":
    app()
