"""
Tool execution commands for IvyBloom CLI
"""

import click
import json
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..utils.colors import get_console, get_tool_color, print_success, print_error, print_warning, print_info
from ..client.api_client import IvyBloomAPIClient

console = get_console()

@click.group()
def tools():
    """Tool execution and discovery commands"""
    pass

@tools.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def list(ctx, format):
    """List available tools"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            tools_data = client.list_tools()
        
        if format == 'json':
            console.print(json.dumps(tools_data, indent=2))
        else:
            if not tools_data:
                console.print("[yellow]No tools available[/yellow]")
                return
            
            console.print(f"[bold cyan]🧬 Available Tools ({len(tools_data)} found)[/bold cyan]\n")
            
            for tool in sorted(tools_data):
                console.print(f"  • [green]{tool}[/green]")
            
            console.print(f"\nUse 'ivybloom tools info <tool_name>' for details")
            console.print(f"Use 'ivybloom run <tool_name>' to execute a tool")
    
    except Exception as e:
        console.print(f"[red]❌ Error listing tools: {e}[/red]")

@tools.command()
@click.argument('tool_name')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def info(ctx, tool_name, format):
    """Get detailed information about a tool"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            schema_data = client.get_tool_schema(tool_name)
        
        if format == 'json':
            console.print(json.dumps(schema_data, indent=2))
        else:
            console.print(f"[bold cyan]🧬 {tool_name.title()}[/bold cyan]")
            console.print(f"   {schema_data.get('description', 'No description available')}")
            console.print()
            
            parameters = schema_data.get('parameters', {})
            if parameters:
                console.print("[bold]Parameters:[/bold]")
                for param_name, param_info in parameters.items():
                    param_type = param_info.get('type', 'unknown')
                    description = param_info.get('description', 'No description')
                    console.print(f"  • [green]{param_name}[/green] ({param_type}): {description}")
                console.print()
            
            required = schema_data.get('required_fields', [])
            if required:
                console.print(f"[bold]Required:[/bold] {', '.join(required)}")
            
            optional = schema_data.get('optional_fields', [])
            if optional:
                console.print(f"[bold]Optional:[/bold] {', '.join(optional)}")
            
            examples = schema_data.get('examples', [])
            if examples:
                console.print("\n[bold]Examples:[/bold]")
                for example in examples:
                    console.print(f"  [dim]{example.get('cli_command', 'No example')}[/dim]")
    
    except Exception as e:
        console.print(f"[red]❌ Error getting tool info: {e}[/red]")

@click.command()
@click.argument('tool_name')
@click.option('--project-id', help='Project ID to associate with job')
@click.option('--job-title', help='Custom job title')
@click.option('--wait', is_flag=True, help='Wait for job completion')
@click.option('--params-file', type=click.File('r'), help='JSON file with parameters')
@click.argument('params', nargs=-1)
@click.pass_context
def run(ctx, tool_name, project_id, job_title, wait, params_file, params):
    """Run a computational tool"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        # Build parameters
        parameters = {}
        
        # Load from file if provided
        if params_file:
            parameters = json.load(params_file)
        
        # Parse command line parameters (key=value format)
        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                # Try to parse as JSON for complex values
                try:
                    parameters[key] = json.loads(value)
                except json.JSONDecodeError:
                    parameters[key] = value
            else:
                console.print(f"[red]Invalid parameter format: {param}[/red]")
                console.print("Use key=value format, e.g., protein_sequence=MKLLVL...")
                return
        
        if not parameters and not params_file:
            # Interactive parameter collection
            console.print(f"[cyan]🧬 Setting up {tool_name} job[/cyan]")
            console.print("Enter parameters (press Enter with empty value to finish):")
            
            while True:
                key = Prompt.ask("Parameter name", default="")
                if not key:
                    break
                value = Prompt.ask(f"Value for {key}")
                if value:
                    try:
                        parameters[key] = json.loads(value)
                    except json.JSONDecodeError:
                        parameters[key] = value
        
        # Create job request
        job_request = {
            "tool_name": tool_name,
            "parameters": parameters,
            "project_id": project_id,
            "job_title": job_title,
            "wait_for_completion": wait
        }
        
        console.print(f"🚀 Submitting {tool_name} job...")
        
        with IvyBloomAPIClient(config, auth_manager) as client:
            job_response = client.create_job(job_request)
        
        job_id = job_response.get('job_id')
        console.print(f"[green]✅ Job created successfully[/green]")
        console.print(f"   Job ID: [cyan]{job_id}[/cyan]")
        console.print(f"   Status: {job_response.get('status', 'Unknown')}")
        
        if job_response.get('estimated_duration'):
            duration = job_response['estimated_duration']
            console.print(f"   Estimated duration: {duration}s")
        
        console.print(f"\nUse 'ivybloom jobs status {job_id}' to check progress")
        console.print(f"Use 'ivybloom jobs results {job_id}' to get results when complete")
    
    except Exception as e:
        console.print(f"[red]❌ Error running tool: {e}[/red]")

# Add the run command to the CLI (not as a subcommand of tools)
# This will be imported in main.py