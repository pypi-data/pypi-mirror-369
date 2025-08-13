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

# UI compatibility aliases mapping
TOOL_ALIASES = {
    'proteinfolding': 'esmfold',
    'moleculardocking': 'diffdock', 
    'denovodesign': 'reinvent',
    'fragmentsearch': 'fragment_library',
    'aianalysis': 'biobert'
}

def resolve_tool_name(tool_name):
    """Resolve tool aliases to actual tool names"""
    return TOOL_ALIASES.get(tool_name.lower(), tool_name)

# Estimated durations for each tool (in minutes)
TOOL_DURATIONS = {
    'esmfold': 5,
    'blast': 2,
    'xtalnet': 15,
    'xtalnet_csp': 240,  # 4 hours
    'diffdock': 30,
    'reinvent': 60,      # 1 hour
    'fragment_growing': 120,  # 2 hours
    'fragment_library': 10,
    'aizynthfinder': 150,     # 2.5 hours
    'frogs': 60,             # 1 hour
    'graphsol': 10,
    'admetlab3': 10,
    'protox3': 15,
    'molport': 25,
    'zinc': 25,
    'pubchem': 20,
    'biobert': 40,
    'deeppurpose': 90        # 1.5 hours
}

def get_tool_duration(tool_name):
    """Get estimated duration for a tool in minutes"""
    return TOOL_DURATIONS.get(tool_name, 30)  # Default 30 min

def format_duration(minutes):
    """Format duration in a human-readable way"""
    if minutes < 60:
        return f"{minutes} min"
    elif minutes < 1440:  # Less than 24 hours
        hours = minutes / 60
        if hours == int(hours):
            return f"{int(hours)} hour{'s' if hours != 1 else ''}"
        else:
            return f"{hours:.1f} hours"
    else:
        days = minutes / 1440
        return f"{days:.1f} days"

@click.group()
def tools():
    """🧬 Computational biology tool discovery and management
    
    Explore and learn about available computational tools for drug discovery,
    molecular modeling, and bioinformatics analysis.
    
    DISCOVERY WORKFLOW:
    
      1. List tools:         ivybloom tools list
      2. Get tool info:      ivybloom tools info <tool_name>
      3. See parameters:     ivybloom tools schema <tool_name> --examples
      4. Run the tool:       ivybloom run <tool_name> [parameters...]
    
    AVAILABLE TOOL CATEGORIES (20 tools total):
    
      🧪 Protein & Structure:     esmfold, blast, xtalnet, xtalnet_csp
      🔬 Molecular Design:        diffdock, reinvent, fragment_growing, fragment_library  
      🧬 Chemical Synthesis:      aizynthfinder, frogs, graphsol
      📊 ADMET & Toxicity:        admetlab3, protox3
      🔍 Database Search:         molport, zinc, pubchem
      🤖 AI & Literature:         biobert, deeppurpose
      📱 UI Aliases:              proteinfolding, moleculardocking, denovodesign, etc.
    
    💡 TIP: Start with 'ivybloom tools list' to see what's available!
    
    Run 'ivybloom tools <command> --help' for detailed help on each command.
    """
    pass

@tools.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def list(ctx, format):
    """📋 List all available computational tools
    
    Discover the computational biology and drug discovery tools available
    through the IvyBloom platform.
    
    USAGE:
      ivybloom tools list                   # Table format (default)
      ivybloom tools list --format json    # JSON output for scripts
    
    NEXT STEPS:
      • Get tool details:    ivybloom tools info <tool_name>
      • See parameters:      ivybloom tools schema <tool_name>
      • Run a tool:          ivybloom run <tool_name> --show-schema
    
    💡 TIP: Each tool has detailed parameter schemas and examples available.
    """
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
    """ℹ️  Get detailed information about a specific tool
    
    Learn about a tool's purpose, capabilities, and basic parameter info.
    
    USAGE:
      ivybloom tools info esmfold          # Human-readable info
      ivybloom tools info esmfold --format json  # JSON for scripts
    
    SHOWS:
      • Tool description and purpose
      • Parameter overview (types and descriptions)  
      • Required vs optional parameters
      • Usage examples (if available)
    
    FOR MORE DETAILS:
      • Full parameter schema:  ivybloom tools schema {tool_name}
      • Usage examples:         ivybloom tools schema {tool_name} --examples
      • Quick help:             ivybloom run {tool_name} --show-schema
    
    💡 TIP: Use this to understand what a tool does before diving into parameters.
    """.format(tool_name=tool_name)
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # Resolve tool aliases
    resolved_tool_name = resolve_tool_name(tool_name)
    if resolved_tool_name != tool_name:
        console.print(f"[dim]Using alias: {tool_name} → {resolved_tool_name}[/dim]")
        tool_name = resolved_tool_name
    
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

@tools.command()
@click.argument('tool_name')
@click.option('--examples', is_flag=True, help='Include usage examples')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def schema(ctx, tool_name, examples, format):
    """Get parameter schema for a tool"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # Resolve tool aliases
    resolved_tool_name = resolve_tool_name(tool_name)
    if resolved_tool_name != tool_name:
        console.print(f"[dim]Using alias: {tool_name} → {resolved_tool_name}[/dim]")
        tool_name = resolved_tool_name
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            schema_data = client.get_tool_schema(tool_name)
        
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
                console.print("[bold]Parameters:[/bold]")
                
                # Show required parameters first
                if required_fields:
                    console.print("\n  [bold red]Required Parameters:[/bold red]")
                    for param_name in required_fields:
                        if param_name in properties:
                            param_info = properties[param_name]
                            param_type = param_info.get('type', 'unknown')
                            description = param_info.get('description', 'No description')
                            default = param_info.get('default')
                            minimum = param_info.get('minimum')
                            maximum = param_info.get('maximum')
                            
                            console.print(f"    • [red]{param_name}[/red] ([yellow]{param_type}[/yellow]) - {description}")
                            if default is not None:
                                console.print(f"      Default: [dim]{default}[/dim]")
                            if minimum is not None or maximum is not None:
                                range_info = f"Range: {minimum or '∞'} - {maximum or '∞'}"
                                console.print(f"      {range_info}")
                
                # Show optional parameters
                optional_params = [p for p in properties.keys() if p not in required_fields]
                if optional_params:
                    console.print("\n  [bold green]Optional Parameters:[/bold green]")
                    for param_name in optional_params:
                        param_info = properties[param_name]
                        param_type = param_info.get('type', 'unknown')
                        description = param_info.get('description', 'No description')
                        default = param_info.get('default')
                        minimum = param_info.get('minimum')
                        maximum = param_info.get('maximum')
                        
                        console.print(f"    • [green]{param_name}[/green] ([yellow]{param_type}[/yellow]) - {description}")
                        if default is not None:
                            console.print(f"      Default: [dim]{default}[/dim]")
                        if minimum is not None or maximum is not None:
                            range_info = f"Range: {minimum or '∞'} - {maximum or '∞'}"
                            console.print(f"      {range_info}")
                
                console.print()
            
            # Show examples if requested
            if examples:
                example_data = schema_data.get('examples', [])
                if example_data:
                    console.print("[bold]Usage Examples:[/bold]")
                    for i, example in enumerate(example_data, 1):
                        console.print(f"\n  [bold cyan]Example {i}:[/bold cyan]")
                        if isinstance(example, dict):
                            # Build CLI command from example
                            params = []
                            for key, value in example.items():
                                if isinstance(value, str):
                                    params.append(f'{key}="{value}"')
                                else:
                                    params.append(f'{key}={value}')
                            cli_cmd = f"ivybloom run {tool_name} {' '.join(params)}"
                            console.print(f"    [dim]{cli_cmd}[/dim]")
                        else:
                            console.print(f"    [dim]{example}[/dim]")
                else:
                    console.print("\n[dim]No examples available[/dim]")
            
            console.print(f"\n[cyan]Usage:[/cyan]")
            console.print(f"  ivybloom run {tool_name} [parameters...]")
            console.print(f"  ivybloom run {tool_name} --help")
    
    except Exception as e:
        console.print(f"[red]❌ Error getting tool schema: {e}[/red]")

@click.command()
@click.argument('tool_name')
@click.option('--project-id', help='Project ID to associate with job')
@click.option('--job-title', help='Custom job title')
@click.option('--wait', is_flag=True, help='Wait for job completion')
@click.option('--params-file', type=click.File('r'), help='JSON file with parameters')
@click.option('--dry-run', is_flag=True, help='Validate parameters without executing')
@click.option('--show-schema', is_flag=True, help='Show parameter schema for this tool')
@click.argument('params', nargs=-1)
@click.pass_context
def run(ctx, tool_name, project_id, job_title, wait, params_file, dry_run, show_schema, params):
    """Run a computational tool
    
    \b
    Parameters are passed as key=value pairs:
      ivybloom run esmfold protein_sequence=MKLLVL num_recycles=3
    
    \b
    Use --show-schema to see all available parameters:
      ivybloom run esmfold --show-schema
    
    \b
    Or use the dedicated schema command:
      ivybloom tools schema esmfold --examples
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        # Resolve tool aliases
        resolved_tool_name = resolve_tool_name(tool_name)
        if resolved_tool_name != tool_name:
            console.print(f"[dim]Using alias: {tool_name} → {resolved_tool_name}[/dim]")
            tool_name = resolved_tool_name
        
        # If --show-schema is requested, show schema and exit
        if show_schema:
            with IvyBloomAPIClient(config, auth_manager) as client:
                schema_data = client.get_tool_schema(tool_name)
            
            duration = get_tool_duration(tool_name)
            duration_str = format_duration(duration)
            
            console.print(f"[bold cyan]📋 {tool_name.title()} Parameters[/bold cyan]")
            console.print(f"   {schema_data.get('description', 'No description available')}")
            console.print(f"   [dim]⏱️  Estimated duration: {duration_str}[/dim]\n")
            
            parameters = schema_data.get('parameters', {})
            properties = parameters.get('properties', {}) if parameters else {}
            required_fields = parameters.get('required', []) if parameters else []
            
            if properties:
                if required_fields:
                    console.print("[bold red]Required:[/bold red]")
                    for param_name in required_fields:
                        if param_name in properties:
                            param_info = properties[param_name]
                            param_type = param_info.get('type', 'unknown')
                            description = param_info.get('description', 'No description')
                            console.print(f"  • [red]{param_name}[/red] ({param_type}) - {description}")
                
                optional_params = [p for p in properties.keys() if p not in required_fields]
                if optional_params:
                    console.print("\n[bold green]Optional:[/bold green]")
                    for param_name in optional_params:
                        param_info = properties[param_name]
                        param_type = param_info.get('type', 'unknown')
                        description = param_info.get('description', 'No description')
                        default = param_info.get('default')
                        console.print(f"  • [green]{param_name}[/green] ({param_type}) - {description}")
                        if default is not None:
                            console.print(f"    Default: [dim]{default}[/dim]")
                
                console.print(f"\n[cyan]Usage:[/cyan]")
                console.print(f"  ivybloom run {tool_name} param1=value1 param2=value2")
            else:
                console.print("[yellow]No parameters found for this tool[/yellow]")
            
            return
        
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
        
        # If no parameters provided, show help
        if not parameters and not params_file and not params:
            console.print(f"[yellow]No parameters provided for {tool_name}[/yellow]")
            console.print(f"Use [green]ivybloom run {tool_name} --show-schema[/green] to see available parameters")
            console.print(f"Or use [green]ivybloom tools schema {tool_name} --examples[/green] for detailed help")
            return
        
        # Validate parameters against schema if dry-run is requested
        if dry_run:
            console.print(f"[blue]🔍 Validating parameters for {tool_name}...[/blue]")
            
            with IvyBloomAPIClient(config, auth_manager) as client:
                schema_data = client.get_tool_schema(tool_name)
            
            schema_params = schema_data.get('parameters', {})
            properties = schema_params.get('properties', {})
            required_fields = schema_params.get('required', [])
            
            # Check required parameters
            missing_required = [field for field in required_fields if field not in parameters]
            if missing_required:
                console.print(f"[red]❌ Missing required parameters: {', '.join(missing_required)}[/red]")
                return
            
            # Check parameter types and ranges
            validation_errors = []
            for param_name, param_value in parameters.items():
                if param_name in properties:
                    param_schema = properties[param_name]
                    param_type = param_schema.get('type')
                    
                    # Basic type validation
                    if param_type == 'integer' and not isinstance(param_value, int):
                        try:
                            parameters[param_name] = int(param_value)
                        except ValueError:
                            validation_errors.append(f"{param_name} must be an integer")
                    
                    elif param_type == 'number' and not isinstance(param_value, (int, float)):
                        try:
                            parameters[param_name] = float(param_value)
                        except ValueError:
                            validation_errors.append(f"{param_name} must be a number")
                    
                    # Range validation
                    if param_type in ['integer', 'number'] and isinstance(parameters[param_name], (int, float)):
                        minimum = param_schema.get('minimum')
                        maximum = param_schema.get('maximum')
                        value = parameters[param_name]
                        
                        if minimum is not None and value < minimum:
                            validation_errors.append(f"{param_name} must be >= {minimum}")
                        if maximum is not None and value > maximum:
                            validation_errors.append(f"{param_name} must be <= {maximum}")
            
            if validation_errors:
                console.print("[red]❌ Validation errors:[/red]")
                for error in validation_errors:
                    console.print(f"  • {error}")
                return
            
            console.print("[green]✅ Parameters are valid![/green]")
            console.print(f"[dim]Job would be created with parameters: {json.dumps(parameters, indent=2)}[/dim]")
            return
        
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
        
        # Handle both job_id (API response) and id (database field) for flexibility
        job_id = job_response.get('job_id') or job_response.get('id')
        tool_name_display = job_response.get('tool_name') or job_response.get('job_type') or tool_name
        
        console.print(f"[green]✅ Job created successfully[/green]")
        console.print(f"   Job ID: [cyan]{job_id}[/cyan]")
        console.print(f"   Tool: [blue]{tool_name_display}[/blue]")
        console.print(f"   Status: [yellow]{job_response.get('status', 'PENDING')}[/yellow]")
        
        # Show estimated duration (convert from seconds or use our mapping)
        estimated_duration = job_response.get('estimated_duration')
        if estimated_duration:
            # API returns seconds, convert to minutes for display
            duration_minutes = estimated_duration // 60
            console.print(f"   Estimated duration: [dim]{format_duration(duration_minutes)}[/dim]")
        else:
            # Use our mapping if API doesn't provide duration
            duration_minutes = get_tool_duration(tool_name)
            console.print(f"   Estimated duration: [dim]{format_duration(duration_minutes)}[/dim]")
        
        if job_response.get('created_at'):
            console.print(f"   Created: [dim]{job_response['created_at']}[/dim]")
        
        console.print(f"\n[cyan]Next steps:[/cyan]")
        console.print(f"   Check progress: [green]ivybloom jobs status {job_id}[/green]")
        console.print(f"   Get results: [green]ivybloom jobs results {job_id}[/green]")
        if duration_minutes > 10:
            console.print(f"   Live monitor: [green]ivybloom jobs status {job_id} --follow[/green]")
        
        # If wait flag is set, monitor the job
        if wait:
            console.print(f"\n[blue]⏳ Waiting for job completion...[/blue]")
            _wait_for_job_completion(client, job_id)
    
    except Exception as e:
        console.print(f"[red]❌ Error running tool: {e}[/red]")

def _wait_for_job_completion(client: 'IvyBloomAPIClient', job_id: str) -> None:
    """Wait for job completion and show progress"""
    import time
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text
    
    with Live(console=console, refresh_per_second=2) as live:
        while True:
            try:
                job_data = client.get_job_status(job_id, include_logs=False)
                status = job_data.get('status', 'Unknown')
                progress = job_data.get('progress_percent', 0)
                current_phase = job_data.get('current_phase', 'N/A')
                
                # Create progress display
                status_text = Text()
                status_text.append(f"Job: {job_id[:8]}...\n")
                status_text.append(f"Status: {status}\n")
                status_text.append(f"Progress: {progress}%\n")
                status_text.append(f"Phase: {current_phase}")
                
                panel = Panel(status_text, title="🔄 Job Progress", border_style="blue")
                live.update(panel)
                
                # Check if job is complete
                if status.upper() in ['COMPLETED', 'SUCCESS', 'FAILURE', 'FAILED', 'CANCELLED', 'ARCHIVED']:
                    break
                    
                time.sleep(3)  # Wait 3 seconds before next update
                
            except Exception as e:
                console.print(f"[red]❌ Error monitoring job: {e}[/red]")
                break
    
    # Final status
    try:
        final_job_data = client.get_job_status(job_id, include_logs=True)
        final_status = final_job_data.get('status', 'Unknown')
        
        if final_status.upper() in ['COMPLETED', 'SUCCESS']:
            console.print(f"[green]✅ Job completed successfully![/green]")
            console.print(f"   Use 'ivybloom jobs results {job_id}' to get results")
        elif final_status.upper() in ['FAILURE', 'FAILED']:
            console.print(f"[red]❌ Job failed[/red]")
            if final_job_data.get('error_message'):
                console.print(f"   Error: {final_job_data['error_message']}")
        else:
            console.print(f"[yellow]⚠️ Job ended with status: {final_status}[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error getting final status: {e}[/red]")

# Add the run command to the CLI (not as a subcommand of tools)
# This will be imported in main.py

# Note: result_callback is only available on groups, not commands
# If we need post-processing, it should be done within the run command itself

# Add help for common usage patterns
def show_run_help():
    """Show help for the run command"""
    console.print("[bold cyan]🚀 ivybloom run - Execute computational tools[/bold cyan]")
    console.print()
    console.print("[bold]Usage:[/bold]")
    console.print("  ivybloom run <tool_name> [parameters...]")
    console.print("  ivybloom run <tool_name> --show-schema")
    console.print("  ivybloom run <tool_name> --dry-run param1=value1")
    console.print()
    console.print("[bold]Examples:[/bold]")
    console.print("  ivybloom run esmfold sequence=MKWVTFISLLFLFSSAYSRGVFRRD")
    console.print("  ivybloom run diffdock protein_file=protein.pdb ligand_smiles=CCO")
    console.print("  ivybloom run reinvent target_smiles='CC(=O)OC1=CC=CC=C1C(=O)O'")
    console.print("  ivybloom run admetlab3 smiles=CCO properties='solubility,toxicity'")
    console.print("  ivybloom run blast sequence=MKWVTFISLLFLFSSAYS database=nr")
    console.print()
    console.print("[bold]Get available tools:[/bold]")
    console.print("  ivybloom tools list")
    console.print()
    console.print("[bold]Get tool-specific help:[/bold]")
    console.print("  ivybloom tools schema <tool_name> --examples")