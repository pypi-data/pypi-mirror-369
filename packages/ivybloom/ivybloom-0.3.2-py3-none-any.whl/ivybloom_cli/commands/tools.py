"""
Tool execution commands for IvyBloom CLI
"""

import click
import json
from rich.console import Console
from rich.table import Table

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..utils.colors import get_console, get_tool_color, print_success, print_error, print_warning, print_info
from ..utils.schema_loader import get_tool_schema, get_available_tools, resolve_tool_name as resolve_schema_tool_name
from ..client.api_client import IvyBloomAPIClient

console = get_console()

@click.group()
def tools():
    """🧬 Tool discovery and execution commands
    
    Explore computational biology tools, view schemas, and execute analyses.
    """
    pass

@tools.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def list(ctx, format):
    """🧬 List all available computational tools
    
    Browse the complete catalog of scientific tools available on the IvyBloom platform.
    Authentication is required to access the current tool catalog.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # All tools list access now requires authentication
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            tools_list = get_available_tools(client)
            
        if format == 'table':
            table = Table(title="🧬 Available Tools", show_header=True, header_style="bold cyan")
            table.add_column("Tool", style="green", width=20)
            table.add_column("Status", style="blue", width=15)
            
            for tool_name in tools_list:
                table.add_row(tool_name, "Available")
            
            console.print(table)
            console.print(f"\n[dim]💡 Total: {len(tools_list)} tools available[/dim]")
            console.print("[dim]📖 Run 'ivybloom tools info <tool_name>' for detailed parameter information[/dim]")
        
        elif format == 'json':
            console.print(json.dumps(tools_list, indent=2))
            
    except Exception as e:
        console.print(f"[red]❌ Error fetching tools: {e}[/red]")

@tools.command()
@click.argument('tool_name')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def info(ctx, tool_name, format):
    """📋 Get detailed information about a specific tool
    
    Shows comprehensive parameter information for the specified tool.
    Authentication is required to access tool schemas.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # Resolve tool aliases
    resolved_tool_name = resolve_schema_tool_name(tool_name)
    if resolved_tool_name != tool_name:
        console.print(f"[dim]Using alias: {tool_name} → {resolved_tool_name}[/dim]")
        tool_name = resolved_tool_name
    
    # All schema access now requires authentication
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            schema_data = get_tool_schema(tool_name, client)
            
        if not schema_data:
            console.print(f"[red]❌ Tool '{tool_name}' not found or schema not available[/red]")
            return
            
        if format == 'json':
            console.print(json.dumps(schema_data, indent=2))
            return
            
        # Table format display
        console.print(f"[bold cyan]🧬 {tool_name.title()}[/bold cyan]")
        console.print(f"   {schema_data.get('description', 'No description available')}")
        console.print()
        
        # Extract schema parameters
        parameters = schema_data.get('parameters', {})
        properties = parameters.get('properties', {}) if parameters else {}
        required_fields = parameters.get('required', []) if parameters else []
        
        if properties:
            console.print("[bold]Parameters:[/bold]")
            
            # Show required parameters first
            if required_fields:
                console.print("\n  [bold red]Required Parameters:[/bold red]")
                for param_name in required_fields:
                    param_info = properties.get(param_name, {})
                    param_type = param_info.get('type', 'unknown')
                    description = param_info.get('description', 'No description')
                    console.print(f"    • [green]{param_name}[/green] ({param_type}): {description}")
                    if 'default' in param_info:
                        console.print(f"      [dim]Default: {param_info['default']}[/dim]")
            
            # Show optional parameters
            optional_fields = [name for name in properties.keys() if name not in required_fields]
            if optional_fields:
                console.print("\n  [bold yellow]Optional Parameters:[/bold yellow]")
                for param_name in optional_fields:
                    param_info = properties.get(param_name, {})
                    param_type = param_info.get('type', 'unknown')
                    description = param_info.get('description', 'No description')
                    console.print(f"    • [green]{param_name}[/green] ({param_type}): {description}")
                    if 'default' in param_info:
                        console.print(f"      [dim]Default: {param_info['default']}[/dim]")
            
            console.print()
            console.print(f"[bold]Summary:[/bold] {len(required_fields)} required, {len(optional_fields)} optional parameters")
        else:
            console.print("[yellow]No parameter information available[/yellow]")
            
        console.print()
        console.print(f"[dim]💡 Run 'ivybloom run {tool_name} --help' to execute this tool[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error getting tool info: {e}[/red]")

@tools.command()
@click.argument('tool_name')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def schema(ctx, tool_name, format):
    """📋 Get comprehensive parameter schema for a tool
    
    Display detailed parameter schema from the authenticated API.
    Authentication is required to access tool schemas.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # Resolve tool aliases
    resolved_tool_name = resolve_schema_tool_name(tool_name)
    if resolved_tool_name != tool_name:
        console.print(f"[dim]Using alias: {tool_name} → {resolved_tool_name}[/dim]")
        tool_name = resolved_tool_name
    
    # All schema access now requires authentication
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            schema_data = get_tool_schema(tool_name, client)
            
        if not schema_data:
            console.print(f"[red]❌ Schema for '{tool_name}' not found[/red]")
            return
            
        if format == 'json':
            console.print(json.dumps(schema_data, indent=2))
        else:
            console.print(f"[bold cyan]📋 {tool_name.title()} Parameter Schema[/bold cyan]")
            console.print(f"   {schema_data.get('description', 'No description available')}")
            console.print()
            
            # Show parameters with detailed information
            parameters = schema_data.get('parameters', {})
            properties = parameters.get('properties', {}) if parameters else {}
            required_fields = parameters.get('required', []) if parameters else []
            
            if properties:
                table = Table(title="Parameters", show_header=True, header_style="bold cyan")
                table.add_column("Parameter", style="green")
                table.add_column("Type", style="blue")
                table.add_column("Required", style="red")
                table.add_column("Description", style="white")
                table.add_column("Default", style="dim")
                
                for param_name, param_info in properties.items():
                    param_type = param_info.get('type', 'unknown')
                    description = param_info.get('description', 'No description')
                    is_required = "Yes" if param_name in required_fields else "No"
                    default = str(param_info.get('default', '')) if 'default' in param_info else ''
                    
                    table.add_row(param_name, param_type, is_required, description, default)
                
                console.print(table)
                console.print(f"\n[dim]💡 Total: {len(properties)} parameters ({len(required_fields)} required)[/dim]")
            else:
                console.print("[yellow]No parameter information available[/yellow]")
                
    except Exception as e:
        console.print(f"[red]❌ Error getting tool schema: {e}[/red]")
