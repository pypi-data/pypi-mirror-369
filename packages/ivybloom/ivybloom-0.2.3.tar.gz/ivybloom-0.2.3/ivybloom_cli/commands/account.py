"""
Account and usage commands for IvyBloom CLI
"""

import click
import json
from rich.console import Console
from rich.table import Table

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..client.api_client import IvyBloomAPIClient
from ..utils.colors import get_console, print_success, print_error, print_warning, print_info

console = get_console()

@click.group()
def account():
    """Account and usage management commands"""
    pass

@account.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def info(ctx, format):
    """Show account information"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            account_data = client.get_account_info()
        
        if format == 'json':
            console.print(json.dumps(account_data, indent=2))
        else:
            console.print(f"[bold cyan]👤 Account Information[/bold cyan]")
            console.print(f"   Email: {account_data.get('email', 'Unknown')}")
            console.print(f"   User ID: {account_data.get('user_id', 'Unknown')}")
            console.print(f"   Plan: {account_data.get('plan', 'Unknown')}")
            console.print(f"   API Keys: {account_data.get('api_keys_count', 0)}/{account_data.get('api_keys_limit', 'Unknown')}")
            
            usage = account_data.get('usage_current_month', {})
            if usage:
                console.print(f"\n[bold cyan]📊 Current Month Usage[/bold cyan]")
                for tool, count in usage.items():
                    console.print(f"   {tool}: {count}")
            
            limits = account_data.get('usage_limits', {})
            if limits:
                console.print(f"\n[bold cyan]📈 Usage Limits[/bold cyan]")
                for tool, limit in limits.items():
                    current = usage.get(tool, 0)
                    percentage = (current / limit * 100) if limit > 0 else 0
                    console.print(f"   {tool}: {current}/{limit} ({percentage:.1f}%)")
    
    except Exception as e:
        console.print(f"[red]❌ Error getting account info: {e}[/red]")

@account.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def usage(ctx, format):
    """Show detailed usage statistics"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            usage_data = client.get_usage_stats()
        
        if format == 'json':
            console.print(json.dumps(usage_data, indent=2))
        else:
            console.print("[bold cyan]📊 Usage Statistics[/bold cyan]")
            
            # Current month
            current_month = usage_data.get('current_month', {})
            if current_month:
                console.print("\n[bold]Current Month:[/bold]")
                table = Table()
                table.add_column("Tool", style="cyan")
                table.add_column("Jobs", style="green")
                
                for tool, count in current_month.items():
                    table.add_row(tool, str(count))
                
                console.print(table)
            
            # Last 30 days
            last_30_days = usage_data.get('last_30_days', {})
            if last_30_days:
                console.print("\n[bold]Last 30 Days:[/bold]")
                table = Table()
                table.add_column("Tool", style="cyan")
                table.add_column("Jobs", style="green")
                
                for tool, count in last_30_days.items():
                    table.add_row(tool, str(count))
                
                console.print(table)
            
            # Summary stats
            total_jobs = usage_data.get('total_jobs', 0)
            total_api_calls = usage_data.get('total_api_calls', 0)
            console.print(f"\n[bold]Summary:[/bold]")
            console.print(f"   Total Jobs: {total_jobs}")
            console.print(f"   Total API Calls: {total_api_calls}")
            
            # Rate limit status
            rate_limit = usage_data.get('rate_limit_status', {})
            if rate_limit:
                console.print(f"\n[bold]Rate Limit Status:[/bold]")
                for limit_type, info in rate_limit.items():
                    console.print(f"   {limit_type}: {info}")
    
    except Exception as e:
        console.print(f"[red]❌ Error getting usage stats: {e}[/red]")