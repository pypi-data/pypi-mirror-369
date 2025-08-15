"""
Authentication commands for Darkfield CLI
Production-ready API key authentication only
"""

import click
import webbrowser
import keyring
import sys
from rich.console import Console
from rich.table import Table
from ..config import DARKFIELD_API_URL, DARKFIELD_WEB_URL

console = Console()

@click.group()
def auth():
    """Manage authentication and API keys"""
    pass

@auth.command()
@click.option('--api-key', help='API key for authentication')
@click.option('--no-browser', is_flag=True, help='Do not open a browser automatically')
def login(api_key, no_browser):
    """Authenticate with Darkfield using API key."""
    console.print("\n[cyan]Darkfield Authentication[/cyan]")
    console.print("\nAPI keys are required for CLI access.")
    console.print("[dim]• New user? Run: darkfield auth signup[/dim]")
    console.print("[dim]• Have an account? Get your key at: darkfield.ai/dashboard/api-keys[/dim]")
    
    import requests

    # If API key supplied via flag, verify directly
    if api_key:
        console.print("\nAuthenticating with provided API key...")
    else:
        interactive = sys.stdin.isatty() and sys.stdout.isatty()
        # Default: open browser when interactive and not suppressed
        if interactive and not no_browser:
            console.print("\n[yellow]Opening browser to dashboard API keys page...[/yellow]")
            try:
                webbrowser.open(f"{DARKFIELD_WEB_URL}/dashboard/api-keys")
                console.print("Generate an API key in the dashboard, then paste it here.")
            except Exception:
                console.print(f"Open this URL to manage API keys: {DARKFIELD_WEB_URL}/dashboard/api-keys")
            api_key = click.prompt("\nAPI key", type=str, hide_input=True)
        elif interactive:
            console.print(f"\nVisit: [cyan]{DARKFIELD_WEB_URL}/dashboard/api-keys[/cyan]")
            api_key = click.prompt("API key", type=str, hide_input=True)
        else:
            console.print(f"\nOpen this URL to manage API keys: {DARKFIELD_WEB_URL}/dashboard/api-keys")
            console.print("Then set: export DARKFIELD_API_KEY=df_live_...")
            return

    # Validate API key format
    if not api_key.startswith(("df_live_", "df_test_")):
        console.print("\n[red]✗[/red] Invalid API key format. Keys should start with 'df_live_' or 'df_test_'")
        return

    # Verify credentials with the API
    try:
        verify_url = f"{DARKFIELD_API_URL}/api/v1/auth/verify"
        response = requests.get(
            verify_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            
            # Store credentials securely
            keyring.set_password("darkfield-cli", "api_key", api_key)
            keyring.set_password("darkfield-cli", "user_email", data.get("email", ""))
            keyring.set_password("darkfield-cli", "user_id", data.get("user_id", ""))
            keyring.set_password("darkfield-cli", "account_status", data.get("account_status", "active"))
            
            console.print(f"\n[green]✓[/green] Successfully authenticated")
            console.print(f"Email: {data.get('email', 'N/A')}")
            console.print(f"Tier: {data.get('tier','free').upper()}")
            console.print(f"Organization: {data.get('organization', 'Personal')}")
            
            # Check if this is a CLI-only account
            if data.get('account_status') == 'cli_only':
                console.print("\n[yellow]ℹ[/yellow] CLI-only account detected")
                console.print("To access the web dashboard, run: [bold]darkfield auth link-account[/bold]")
                
        elif response.status_code == 401:
            console.print("\n[red]✗[/red] Invalid API key. Please check your credentials.")
        else:
            console.print(f"\n[red]✗[/red] Authentication failed: {response.status_code}")
            if response.text:
                console.print(f"Details: {response.text}")
    except requests.exceptions.RequestException as e:
        console.print(f"\n[red]✗[/red] Network error: {e}")

@auth.command()
def logout():
    """Log out from Darkfield (clears local credentials only)"""
    try:
        # Get current user for confirmation
        email = keyring.get_password("darkfield-cli", "user_email")
        
        if email:
            if click.confirm(f"Log out from {email}?"):
                # Note: We don't revoke the API key server-side 
                # Users should revoke keys manually in the dashboard for security
                
                # Clear local credentials
                for key in ["api_key", "user_email", "user_id", "account_status"]:
                    try:
                        keyring.delete_password("darkfield-cli", key)
                    except:
                        pass
                
                console.print("[green]✓[/green] Successfully logged out (local credentials cleared)")
                console.print("[dim]Note: API key remains valid. Revoke it at darkfield.ai/dashboard/api-keys[/dim]")
            else:
                console.print("[yellow]Logout cancelled[/yellow]")
        else:
            console.print("[yellow]Not currently logged in[/yellow]")
            
    except Exception:
        console.print("[yellow]Not currently logged in[/yellow]")

@auth.command()
def status():
    """Show current authentication status"""
    try:
        email = keyring.get_password("darkfield-cli", "user_email")
        api_key = keyring.get_password("darkfield-cli", "api_key")
        account_status = keyring.get_password("darkfield-cli", "account_status")
        
        if email and api_key:
            # Verify credentials are still valid
            import requests
            
            response = requests.get(
                f"{DARKFIELD_API_URL}/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                console.print(f"[green]✓[/green] Authenticated as: {email}")
                console.print(f"User ID: {data.get('user_id', 'N/A')}")
                console.print(f"Tier: {data.get('tier', 'free').upper()}")
                console.print(f"Organization: {data.get('organization', 'Personal')}")
                
                # Show API key preview (last 4 chars only for security)
                key_preview = f"df_{'*' * 8}...{api_key[-4:]}"
                console.print(f"API Key: {key_preview}")
                
                # Show account status warnings
                if data.get('account_status') == 'cli_only':
                    console.print("\n[yellow]⚠ CLI-only account[/yellow]")
                    console.print("To access the web dashboard, run: [bold]darkfield auth link-account[/bold]")
                elif data.get('account_status') == 'pending_verification':
                    console.print("\n[yellow]⚠ Email verification pending[/yellow]")
                    console.print("Check your email to verify your account")
                    
                # Show usage stats if available
                if 'usage' in data:
                    console.print("\n[bold]Usage this month:[/bold]")
                    console.print(f"API calls: {data['usage'].get('api_calls', 0):,}")
                    console.print(f"Vectors extracted: {data['usage'].get('vectors', 0):,}")
            else:
                console.print("[red]✗[/red] Authentication is no longer valid")
                console.print("Please run: [bold]darkfield auth login[/bold]")
        else:
            console.print("[yellow]Not authenticated[/yellow]")
            console.print("\nTo get started:")
            console.print("• New user: [bold]darkfield auth signup[/bold]")
            console.print("• Existing user: [bold]darkfield auth login[/bold]")
            
    except Exception as e:
        console.print(f"[red]Error checking auth status: {e}[/red]")

@auth.command()
@click.option('--email', prompt=True, help='Email address for your account')
@click.option('--organization', default='', help='Organization name (optional)')
def signup(email, organization):
    """Sign up for a Darkfield account and get your first API key."""
    console.print("\n[cyan]Creating Darkfield account...[/cyan]")
    
    import requests
    try:
        # Try CLI signup endpoint
        response = requests.post(
            f"{DARKFIELD_API_URL}/api/v1/auth/register",
            json={
                "email": email,
                "organization": organization or None,
                "source": "cli"  # Track that this came from CLI
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            api_key = data.get("api_key")
            
            if not api_key:
                console.print("[red]Registration failed: no API key received[/red]")
                return
                
            # Save credentials
            console.print("\n[green]✓[/green] Account created successfully!")
            console.print(f"\n[yellow]Your API key (save this!):[/yellow]")
            console.print(f"[bold]{api_key}[/bold]")
            
            if click.confirm("\nSave API key to system keychain?", default=True):
                keyring.set_password("darkfield-cli", "api_key", api_key)
                keyring.set_password("darkfield-cli", "user_email", email)
                keyring.set_password("darkfield-cli", "account_status", "cli_only")
                console.print("[green]✓[/green] Credentials saved")
            
            console.print("\n[bold]Next steps:[/bold]")
            console.print("1. Check your email for verification link")
            console.print("2. Run: [cyan]darkfield analyze demo[/cyan] to try it out")
            console.print("3. Visit: [cyan]darkfield.ai/dashboard[/cyan] to access web features")
            
            # Check if this is a CLI-only account
            if data.get('account_status') == 'cli_only':
                console.print("\n[dim]Note: This is a CLI-only account. To enable web dashboard access,[/dim]")
                console.print("[dim]run: darkfield auth link-account[/dim]")
                
        elif response.status_code == 403:
            # Open signup disabled, redirect to web
            console.print("\n[yellow]Direct CLI signup is disabled.[/yellow]")
            console.print("Opening web signup page...")
            webbrowser.open(f"{DARKFIELD_WEB_URL}/sign-up?source=cli&email={email}")
            console.print("\nAfter signing up on the web:")
            console.print("1. Go to dashboard.darkfield.ai/api-keys")
            console.print("2. Generate an API key")
            console.print("3. Run: [cyan]darkfield auth login --api-key YOUR_KEY[/cyan]")
            
        elif response.status_code == 409:
            console.print("\n[yellow]Account already exists with this email.[/yellow]")
            console.print("Please run: [bold]darkfield auth login[/bold]")
            
        else:
            console.print(f"[red]Registration failed: {response.status_code}[/red]")
            if response.text:
                console.print(f"Details: {response.text}")
                
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Network error during signup: {e}[/red]")
        console.print("\nYou can also sign up at: [cyan]darkfield.ai/sign-up[/cyan]")

@auth.command()
def link_account():
    """Link your CLI account to enable web dashboard access."""
    email = keyring.get_password("darkfield-cli", "user_email")
    account_status = keyring.get_password("darkfield-cli", "account_status")
    
    if not email:
        console.print("[red]Not authenticated. Please login first.[/red]")
        return
        
    if account_status == "active":
        console.print("[green]✓[/green] Your account is already fully activated")
        console.print(f"Access the dashboard at: [cyan]{DARKFIELD_WEB_URL}/dashboard[/cyan]")
        return
        
    console.print("\n[cyan]Linking CLI account to web dashboard...[/cyan]")
    console.print(f"Email: {email}")
    console.print("\nThis will create a Clerk account for web dashboard access.")
    console.print("You'll receive a magic link to set up your dashboard password.")
    
    if click.confirm("\nProceed with account linking?"):
        # Generate unique linking token
        import requests
        api_key = keyring.get_password("darkfield-cli", "api_key")
        
        try:
            response = requests.post(
                f"{DARKFIELD_API_URL}/api/v1/auth/link-account",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"email": email},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                link_url = data.get("link_url")
                
                console.print("\n[green]✓[/green] Account linking initiated")
                console.print("\nOpening browser to complete setup...")
                webbrowser.open(link_url)
                
                console.print("\n[bold]Next steps:[/bold]")
                console.print("1. Check your email for the magic link")
                console.print("2. Complete web dashboard setup")
                console.print("3. Your API keys will work for both CLI and web")
                
                # Update local status
                keyring.set_password("darkfield-cli", "account_status", "pending_verification")
                
            else:
                console.print(f"[red]Account linking failed: {response.status_code}[/red]")
                if response.text:
                    console.print(f"Details: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Network error: {e}[/red]")
    else:
        console.print("[yellow]Account linking cancelled[/yellow]")

@auth.command()
@click.option('--name', required=True, help='Name for this API key')
@click.option('--expires-days', default=90, help='Days until expiration (0 for no expiration)')
def create_key(name, expires_days):
    """Create a new API key (requires web dashboard access)."""
    api_key = keyring.get_password("darkfield-cli", "api_key")
    if not api_key:
        console.print("[red]Not authenticated. Please login first.[/red]")
        return
    
    # For security, key creation should be done via web dashboard
    console.print("\n[yellow]For security, new API keys must be created via the web dashboard.[/yellow]")
    console.print(f"\nOpening: [cyan]{DARKFIELD_WEB_URL}/dashboard/api-keys[/cyan]")
    webbrowser.open(f"{DARKFIELD_WEB_URL}/dashboard/api-keys")
    
    console.print("\n[dim]This ensures proper audit logging and key management.[/dim]")

@auth.command()
def list_keys():
    """List all API keys for your account."""
    api_key = keyring.get_password("darkfield-cli", "api_key")
    if not api_key:
        console.print("[red]Not authenticated. Please login first.[/red]")
        return
    
    import requests
    
    try:
        response = requests.get(
            f"{DARKFIELD_API_URL}/api/v1/api-keys",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        
        if response.status_code == 200:
            keys = response.json().get("keys", [])
            
            if not keys:
                console.print("[yellow]No API keys found[/yellow]")
                console.print("\nCreate new keys at: [cyan]darkfield.ai/dashboard/api-keys[/cyan]")
                return
            
            table = Table(title="Your API Keys", show_header=True)
            table.add_column("Name", style="cyan")
            table.add_column("Key Preview", style="dim")
            table.add_column("Status")
            table.add_column("Created", style="dim")
            table.add_column("Last Used")
            table.add_column("Expires")
            
            for key in keys:
                status = "[green]Active[/green]" if key.get("is_active") else "[red]Revoked[/red]"
                last_used = key.get("last_used_at", "Never")
                if last_used != "Never":
                    last_used = last_used[:10]  # Just date
                created = key["created_at"][:10]  # Just date
                expires = key.get("expires_at")
                if expires:
                    expires = expires[:10]
                else:
                    expires = "Never"
                    
                table.add_row(
                    key["name"],
                    key.get("preview", "df_****..."),
                    status,
                    created,
                    last_used,
                    expires
                )
            
            console.print(table)
            console.print(f"\nTotal keys: {len(keys)}")
            console.print("\nManage keys at: [cyan]darkfield.ai/dashboard/api-keys[/cyan]")
            
        else:
            console.print(f"[red]Failed to list keys: {response.status_code}[/red]")
            
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Network error: {e}[/red]")

@auth.command()
def rotate_key():
    """Rotate your current API key (generate new, revoke old)."""
    current_key = keyring.get_password("darkfield-cli", "api_key")
    if not current_key:
        console.print("[red]Not authenticated. Please login first.[/red]")
        return
    
    console.print("\n[yellow]⚠ Key rotation will:[/yellow]")
    console.print("• Generate a new API key")
    console.print("• Revoke the current key after 5 minutes")
    console.print("• Require updating any scripts using the old key")
    
    if not click.confirm("\nProceed with key rotation?"):
        console.print("[yellow]Key rotation cancelled[/yellow]")
        return
    
    import requests
    try:
        response = requests.post(
            f"{DARKFIELD_API_URL}/api/v1/api-keys/rotate",
            headers={"Authorization": f"Bearer {current_key}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            new_key = data["api_key"]
            
            console.print("\n[green]✓[/green] New API key generated")
            console.print(f"\n[yellow]New API key (save this!):[/yellow]")
            console.print(f"[bold]{new_key}[/bold]")
            
            # Update stored credentials
            keyring.set_password("darkfield-cli", "api_key", new_key)
            console.print("\n[green]✓[/green] Local credentials updated")
            console.print("[dim]Old key will be revoked in 5 minutes[/dim]")
            
        else:
            console.print(f"[red]Key rotation failed: {response.status_code}[/red]")
            
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Network error: {e}[/red]")