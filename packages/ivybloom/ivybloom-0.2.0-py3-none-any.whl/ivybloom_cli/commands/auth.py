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
        pair_url = f"{resolved_frontend.rstrip('/')}/cli/link?client_id={client_id}"
        
        console.print()
        console.print(f"🔗 [welcome.text]Linking this CLI installation to your account[/welcome.text]")
        console.print(f"   Client ID: [cli.accent]{client_id}[/cli.accent]")
        console.print(f"   Link: [cli.bright]{pair_url}[/cli.bright]")
        console.print()
        
        # Open browser automatically
        try:
            webbrowser.open(pair_url)
            print_success("Browser opened successfully")
        except Exception as e:
            print_error(f"Failed to open browser: {e}")
            console.print(f"Please manually visit: {pair_url}")
        
        console.print()
        console.print("🔄 [yellow]Waiting for you to complete linking in your browser...[/yellow]")
        console.print("   Press Ctrl+C to cancel")
        console.print()
        
        # Poll for linking completion
        success = _wait_for_cli_linking(config, auth_manager, client_id)
        
        if success:
            console.print()
            print_success("🎉 CLI successfully linked to your account!")
            console.print("✨ [green]Ready to go! Try these commands:[/green]")
            console.print("   [cli.accent]ivybloom tools list[/cli.accent]     - Browse available tools")
            console.print("   [cli.accent]ivybloom projects list[/cli.accent]  - View your projects") 
            console.print("   [cli.accent]ivybloom --help[/cli.accent]         - See all commands")
            console.print()
        else:
            print_error("CLI linking failed or was cancelled.")
            console.print("💡 [yellow]Troubleshooting tips:[/yellow]")
            console.print("   • Make sure you're logged in to the web app")
            console.print("   • Try the linking process again")
            console.print("   • Use 'ivybloom auth login --browser' as an alternative")
        
        return

    # Handle browser/device authentication
    if browser or device:
        api_url = config.get_api_url()
        
        if browser:
            console.print()
            console.print("🌐 [bold cyan]Browser Authentication[/bold cyan]")
            console.print("   Starting secure OAuth flow via your default browser...")
            console.print()
            auth_result = browser_login(api_url)
        else:  # device flow
            console.print()
            console.print("📱 [bold cyan]Device Authentication[/bold cyan]")
            console.print("   Starting device flow for headless environments...")
            console.print()
            auth_result = device_flow_login(api_url)
        
        if 'error' in auth_result:
            print_error(f"Authentication failed: {auth_result['error']}")
            console.print()
            console.print("💡 [yellow]Troubleshooting tips:[/yellow]")
            console.print("   • Check your internet connection")
            console.print("   • Try running the command again")
            console.print("   • Use --device flag if browser issues persist")
            console.print("   • Contact support if problems continue")
            return
        
        # Store tokens
        auth_manager.store_oauth_tokens(auth_result)
        console.print()
        print_success("🎉 Successfully authenticated with IvyBloom!")
        
        # Show user info
        try:
            with IvyBloomAPIClient(config, auth_manager) as client:
                user_info = client.get_account_info()
                console.print(f"   Logged in as: [cli.accent]{user_info.get('email', 'Unknown')}[/cli.accent]")
                console.print(f"   User ID: [cli.dim]{user_info.get('user_id', 'Unknown')}[/cli.dim]")
        except Exception as e:
            print_info("Authentication successful, but couldn't fetch user info")
        
        console.print()
        console.print("✨ [green]Ready to go! Try these commands:[/green]")
        console.print("   [cli.accent]ivybloom tools list[/cli.accent]     - Browse available tools")
        console.print("   [cli.accent]ivybloom projects list[/cli.accent]  - View your projects") 
        console.print("   [cli.accent]ivybloom --help[/cli.accent]         - See all commands")
        console.print()
        
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
@click.option('--open', 'open_browser', is_flag=True, help='Open link in default browser (default: true)')
@click.option('--frontend-url', help='Override frontend URL for link flow (e.g., https://app.example.com)')
@click.option('--no-wait', is_flag=True, help='Don\'t wait for linking completion')
@click.pass_context
def link(ctx, open_browser, frontend_url, no_wait):
    """🔗 Link this CLI installation to your IvyBloom account
    
    This creates a secure connection between this CLI and your web account
    without requiring an API key. Perfect for personal use!
    
    USAGE:
      ivybloom auth link                    # Auto-open browser and wait
      ivybloom auth link --no-wait          # Generate link only, don't wait
    
    PROCESS:
      1. CLI generates a unique pairing code
      2. Browser opens automatically (or you visit the link)
      3. Login to your IvyBloom account
      4. Approve the CLI connection
      5. CLI automatically detects completion and is ready to use!
    
    💡 TIP: This is more convenient than API keys for interactive use.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if auth_manager.is_authenticated():
        print_info("You are already authenticated.")
        console.print("Use 'ivybloom auth logout' first if you want to re-link.")
        return
    
    resolved_frontend = (frontend_url or config.get_frontend_url())
    if not resolved_frontend:
        console.print("[red]Error: Frontend URL not configured.[/red]")
        console.print("Set IVY_FRONTEND_URL or run: ivybloom config set frontend_url https://your-frontend-host")
        return
    
    client_id = config.get_or_create_client_id()
    pair_url = f"{resolved_frontend.rstrip('/')}/cli/link?client_id={client_id}"

    console.print()
    console.print(f"🔗 [welcome.text]Link this CLI installation to your IvyBloom account[/welcome.text]")
    console.print(f"   Client ID: [cli.accent]{client_id}[/cli.accent]")
    console.print(f"   Link: [cli.bright]{pair_url}[/cli.bright]")
    console.print()

    # Auto-open browser by default (unless explicitly disabled)
    if open_browser is not False:
        try:
            webbrowser.open(pair_url)
            print_success("Browser opened successfully")
        except Exception as e:
            print_error(f"Failed to open browser: {e}")
            console.print(f"Please manually visit: {pair_url}")
    
    if not no_wait:
        console.print()
        console.print("🔄 [yellow]Waiting for you to complete linking in your browser...[/yellow]")
        console.print("   Press Ctrl+C to cancel")
        console.print()
        
        # Poll for linking completion
        success = _wait_for_cli_linking(config, auth_manager, client_id)
        
        if success:
            console.print()
            print_success("🎉 CLI successfully linked to your account!")
            console.print("✨ [green]Ready to go! Try these commands:[/green]")
            console.print("   [cli.accent]ivybloom tools list[/cli.accent]     - Browse available tools")
            console.print("   [cli.accent]ivybloom projects list[/cli.accent]  - View your projects") 
            console.print("   [cli.accent]ivybloom --help[/cli.accent]         - See all commands")
            console.print()
        else:
            print_error("CLI linking failed or was cancelled.")
            console.print("💡 [yellow]Troubleshooting tips:[/yellow]")
            console.print("   • Make sure you're logged in to the web app")
            console.print("   • Try the linking process again")
            console.print("   • Use 'ivybloom auth login --browser' as an alternative")
    else:
        console.print("🔄 [yellow]Linking URL generated. Complete the process in your browser.[/yellow]")
        console.print("   Run 'ivybloom auth status' to check if linking was successful.")

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
            
            # Show token expiration info if available
            oauth_tokens = auth_manager.get_oauth_tokens()
            if oauth_tokens and 'expires_at' in oauth_tokens:
                try:
                    from datetime import datetime
                    expires_at = datetime.fromisoformat(oauth_tokens['expires_at'])
                    time_left = expires_at - datetime.now()
                    
                    if time_left.total_seconds() > 0:
                        hours = int(time_left.total_seconds() // 3600)
                        minutes = int((time_left.total_seconds() % 3600) // 60)
                        table.add_row("Token Expires", f"In {hours}h {minutes}m")
                    else:
                        table.add_row("Token Status", "🔄 Auto-refreshing expired token")
                except Exception:
                    pass
            
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

def _wait_for_cli_linking(config: Config, auth_manager: AuthManager, client_id: str, timeout: int = 300) -> bool:
    """Wait for CLI linking to complete with polling and loading indicator"""
    import time
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    
    # Create a loading indicator with progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        TextColumn("• Timeout in {task.fields[remaining]:.0f}s"),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task(
            "Waiting for linking completion...", 
            total=timeout,
            remaining=timeout
        )
        
        start_time = time.time()
        poll_interval = 3  # Poll every 3 seconds
        
        while time.time() - start_time < timeout:
            elapsed = time.time() - start_time
            remaining = timeout - elapsed
            
            # Update progress
            progress.update(task, completed=elapsed, remaining=remaining)
            
            try:
                # Check linking status (this endpoint doesn't require auth)
                import httpx
                api_url = config.get_api_url()
                status_url = f"{api_url.rstrip('/')}/cli/link-status/{client_id}"
                
                with httpx.Client() as client:
                    response = client.get(status_url)
                    
                    if response.status_code == 200:
                        status_data = response.json()
                        
                        if status_data.get('linked', False):
                            # Linking completed! Now verify and get credentials
                            progress.update(task, description="✅ Linking completed! Verifying...")
                            time.sleep(0.5)
                            
                            # Use the API client to verify and get auth token/credentials
                            try:
                                with IvyBloomAPIClient(config, auth_manager) as api_client:
                                    verify_result = api_client.verify_cli_linking(client_id)
                                    
                                    if verify_result.get('success'):
                                        # Store any returned credentials
                                        if 'auth_token' in verify_result:
                                            auth_manager.store_auth_token(verify_result['auth_token'])
                                        
                                        return True
                                    else:
                                        progress.update(task, description="❌ Verification failed!")
                                        time.sleep(1)
                                        return False
                                        
                            except Exception as e:
                                progress.update(task, description=f"❌ Verification error: {e}")
                                time.sleep(1)
                                return False
                
            except KeyboardInterrupt:
                progress.update(task, description="❌ Cancelled by user!")
                time.sleep(0.5)
                return False
            except Exception:
                # Network error or other issue - continue polling
                pass
            
            # Wait before next poll
            time.sleep(poll_interval)
        
        # Timeout reached
        progress.update(task, description="⏰ Linking timeout!")
        time.sleep(0.5)
    
    return False