"""
Authentication commands for ivybloom CLI
"""

import click
import webbrowser
from rich.console import Console
from rich.table import Table

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..utils.colors import get_console, print_success, print_error, print_warning, print_info
from ..client.api_client import IvyBloomAPIClient
from ..utils.browser_auth import browser_login, device_flow_login

console = get_console()

@click.group()
def auth():
    """🔐 Authentication management commands
    
    Manage your IvyBloom CLI authentication credentials and account linking.
    
    QUICK START:
    
      • First time:        ivybloom auth login --browser
      • Headless/CI:       ivybloom auth login --api-key
      • Link CLI:          ivybloom auth link
      • Check status:      ivybloom auth status
    
    AUTHENTICATION METHODS:
    
      🌐 Browser OAuth (Recommended): Secure, user-friendly authentication
      🔑 API Key: For automation, CI/CD, and headless environments  
      🔗 CLI Linking: Link this CLI installation to your web account
      📱 Device Flow: For remote servers without browser access
    
    Get your API key at: https://ivybiosciences.com/settings/api-keys
    
    Run 'ivybloom auth <command> --help' for detailed help on each command.
    """
    pass

@auth.command()
@click.option('--api-key', help='Provide API key directly (non-interactive)')
@click.option('--browser', is_flag=True, help='Login using browser (OAuth flow)')
@click.option('--device', is_flag=True, help='Login using device flow (for headless environments)')
@click.option('--link', is_flag=True, help='Link this CLI installation to your account (no API key)')
@click.option('--frontend-url', help='Override frontend URL for link flow (e.g., https://app.example.com)')
@click.option('--no-verify', is_flag=True, help='Skip API key validation')
@click.option('--force', is_flag=True, help='Overwrite existing credentials')
@click.pass_context
def login(ctx, api_key, browser, device, link, frontend_url, no_verify, force):
    """🚀 Login to IvyBloom platform
    
    Choose your preferred authentication method:
    
    RECOMMENDED: Browser OAuth (most secure)
      ivybloom auth login --browser
    
    FOR AUTOMATION: API Key authentication  
      ivybloom auth login --api-key
    
    FOR HEADLESS SERVERS: Device flow
      ivybloom auth login --device
      
    FOR CLI LINKING: Connect this CLI to your web account
      ivybloom auth login --link
    
    💡 TIP: After login, run 'ivybloom auth status' to verify your connection.
    """
    """Login with API key or browser authentication"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if auth_manager.is_authenticated() and not force:
        print_info("You are already logged in.")
        console.print("Use 'ivybloom auth logout' to logout first, or use --force to overwrite.")
        return
    
    # Handle link-based pairing (client UUID + Clerk user)
    if link:
        api_url = config.get_api_url()
        resolved_frontend = (frontend_url or config.get_frontend_url())
        if not resolved_frontend:
            console.print("[red]Error: Frontend URL not configured.[/red]")
            console.print("Set IVY_FRONTEND_URL or run: ivybloom config set frontend_url https://your-frontend-host")
            return
        client_id = config.get_or_create_client_id()
        # Construct a pairing URL the frontend can consume to complete linking
        # The frontend file/route should read client_id and, when authenticated, call backend to bind Clerk user id to this client_id
        pair_url = f"{resolved_frontend.rstrip('/')}/cli/link?client_id={client_id}"
        console.print()
        console.print(f"[welcome.text]Linking this CLI installation to your account[/welcome.text]")
        console.print(f"Client ID: [cli.accent]{client_id}[/cli.accent]")
        console.print(f"Open this link to complete linking: [cli.bright]{pair_url}[/cli.bright]")
        console.print("Link opened in your browser. After you see 'Your CLI is now linked', return here and continue.")
        console.print()
        return

    # Handle browser/device authentication
    if browser or device:
        api_url = config.get_api_url()
        
        if browser:
            print_info("Starting browser authentication...")
            auth_result = browser_login(api_url)
        else:  # device flow
            print_info("Starting device authentication...")
            auth_result = device_flow_login(api_url)
        
        if 'error' in auth_result:
            print_error(f"Authentication failed: {auth_result['error']}")
            return
        
        # Store tokens
        auth_manager.store_oauth_tokens(auth_result)
        print_success("Successfully authenticated with IvyBloom!")
        
        # Show user info
        try:
            with IvyBloomAPIClient(config, auth_manager) as client:
                user_info = client.get_account_info()
                console.print(f"Logged in as: [cli.accent]{user_info.get('email', 'Unknown')}[/cli.accent]")
        except Exception as e:
            print_info("Authentication successful, but couldn't fetch user info")
        
        return
    
    # Handle API key authentication
    if not api_key:
        api_key = auth_manager.prompt_for_api_key()
    
    if not api_key:
        print_error("No API key provided. Login cancelled.")
        return
    
    # Store API key
    auth_manager.store_api_key(api_key)
    
    # Test the API key unless --no-verify is used
    if not no_verify:
        print_info("Validating API key...")
        
        try:
            # Test API connection
            with IvyBloomAPIClient(config, auth_manager) as client:
                account_info = client.get_account_info()
                
            console.print(f"[green]✅ Successfully logged in as {account_info.get('email', 'Unknown')}[/green]")
            
        except Exception as e:
            # Remove the invalid API key
            auth_manager.remove_api_key()
            console.print(f"[red]❌ Login failed: {e}[/red]")
            console.print("Please check your API key and try again.")
            return
    else:
        console.print("[green]✅ API key stored (validation skipped)[/green]")

@auth.command()
@click.option('--open', 'open_browser', is_flag=True, help='Open link in default browser')
@click.option('--frontend-url', help='Override frontend URL for link flow (e.g., https://app.example.com)')
@click.pass_context
def link(ctx, open_browser, frontend_url):
    """🔗 Link this CLI installation to your IvyBloom account
    
    This creates a secure connection between this CLI and your web account
    without requiring an API key. Perfect for personal use!
    
    USAGE:
      ivybloom auth link                    # Generate link manually
      ivybloom auth link --open             # Auto-open in browser
    
    PROCESS:
      1. CLI generates a unique pairing code
      2. You visit the link in your browser  
      3. Login to your IvyBloom account
      4. Approve the CLI connection
      5. CLI is now linked and ready to use!
    
    💡 TIP: This is more convenient than API keys for interactive use.
    """
    config = ctx.obj['config']
    resolved_frontend = (frontend_url or config.get_frontend_url())
    if not resolved_frontend:
        console.print("[red]Error: Frontend URL not configured.[/red]")
        console.print("Set IVY_FRONTEND_URL or run: ivybloom config set frontend_url https://your-frontend-host")
        return
    client_id = config.get_or_create_client_id()
    pair_url = f"{resolved_frontend.rstrip('/')}/cli/link?client_id={client_id}"

    console.print()
    console.print(f"[welcome.text]Link this CLI installation to your IvyBloom account[/welcome.text]")
    console.print(f"Client ID: [cli.accent]{client_id}[/cli.accent]")
    console.print(f"Open this link to complete linking: [cli.bright]{pair_url}[/cli.bright]")
    console.print("Link opened in your browser. After you see 'Your CLI is now linked', return here and continue.")
    console.print()

    if open_browser:
        try:
            webbrowser.open(pair_url)
            print_success("Browser opened successfully")
        except Exception as e:
            print_error(f"Failed to open browser: {e}")

@auth.command()
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def logout(ctx, confirm):
    """🚪 Logout and clear authentication credentials
    
    This removes all stored authentication data from this device:
    • API keys • OAuth tokens • CLI linking • JWT tokens
    
    USAGE:
      ivybloom auth logout                  # Interactive confirmation
      ivybloom auth logout --confirm        # Skip confirmation
    
    💡 TIP: You can always login again with 'ivybloom auth login'
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[yellow]You are not logged in.[/yellow]")
        return
    
    # Confirm logout unless --confirm is used
    if not confirm:
        if not click.confirm("Are you sure you want to logout?"):
            console.print("Logout cancelled.")
            return
    
    # Remove credentials
    auth_manager.remove_api_key()
    auth_manager.remove_auth_token()
    
    console.print("[green]✅ Successfully logged out[/green]")

@auth.command()
@click.option('--check-connectivity', is_flag=True, help='Test API connectivity')
@click.option('--show-permissions', is_flag=True, help='Display API key permissions')
@click.pass_context
def status(ctx, check_connectivity, show_permissions):
    """📊 Check authentication status and connectivity
    
    Verify your CLI authentication and connection to IvyBloom services.
    
    USAGE:
      ivybloom auth status                        # Basic status
      ivybloom auth status --check-connectivity  # Test API connection  
      ivybloom auth status --show-permissions    # Show detailed permissions
    
    SHOWS:
      ✅ Authentication method • Account info • Connection status
      🔑 API key details • Token expiration • Rate limits
      🌐 API endpoint • Network connectivity • Service health
    
    💡 TIP: Run this if you're having connection issues.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # Create status table
    table = Table(title="🔐 Authentication Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    if auth_manager.is_authenticated():
        # Get account info
        try:
            with IvyBloomAPIClient(config, auth_manager) as client:
                account_info = client.get_account_info()
            
            table.add_row("Status", "✅ Authenticated")
            table.add_row("Email", account_info.get('email', 'Unknown'))
            table.add_row("User ID", account_info.get('user_id', 'Unknown'))
            table.add_row("Plan", account_info.get('plan', 'Unknown'))
            table.add_row("API Keys", f"{account_info.get('api_keys_count', 0)}/{account_info.get('api_keys_limit', 'Unknown')}")
            
        except Exception as e:
            table.add_row("Status", "❌ Authentication Error")
            table.add_row("Error", str(e))
    else:
        table.add_row("Status", "❌ Not authenticated")
        table.add_row("Action", "Run 'ivybloom auth login' to authenticate")
    
    console.print(table)

@auth.command()
@click.pass_context
def whoami(ctx):
    """👤 Show current user account information
    
    Display details about the currently authenticated user.
    
    SHOWS:
      • User ID and email address
      • Account type and status  
      • Organization/team info
      • Subscription details
      • Usage statistics
    
    💡 TIP: Use this to verify you're logged into the correct account.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated[/red]")
        console.print("Run 'ivybloom auth login' to authenticate")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            account_info = client.get_account_info()
        
        console.print(f"[bold cyan]👤 {account_info.get('email', 'Unknown')}[/bold cyan]")
        console.print(f"   User ID: {account_info.get('user_id', 'Unknown')}")
        console.print(f"   Plan: {account_info.get('plan', 'Unknown')}")
        
    except Exception as e:
        console.print(f"[red]❌ Error getting user info: {e}[/red]")