"""
Job management commands for IvyBloom CLI
"""

import click
import time
import json
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.panel import Panel

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..utils.colors import get_console, get_status_color, format_status_icon, print_success, print_error, print_warning, print_info
from ..client.api_client import IvyBloomAPIClient

console = get_console()

@click.group()
def jobs():
    """Job management commands"""
    pass

@jobs.command()
@click.option('--project-id', help='Filter by project ID')
@click.option('--status', help='Filter by job status')
@click.option('--tool', help='Filter by tool name')
@click.option('--limit', default=50, help='Number of jobs to return')
@click.option('--offset', default=0, help='Number of jobs to skip')
@click.option('--created-after', help='Filter jobs created after date (ISO format)')
@click.option('--created-before', help='Filter jobs created before date (ISO format)')
@click.option('--sort-by', default='created_at', type=click.Choice(['created_at', 'status', 'tool_name']), help='Sort jobs by field')
@click.option('--sort-order', default='desc', type=click.Choice(['asc', 'desc']), help='Sort order')
@click.option('--format', default='table', type=click.Choice(['table', 'json', 'csv', 'yaml']), help='Output format')
@click.pass_context
def list(ctx, project_id, status, tool, limit, offset, created_after, created_before, sort_by, sort_order, format):
    """List jobs with filtering options"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        # Build filters
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if status:
            filters['status'] = status
        if tool:
            filters['tool_name'] = tool
        if created_after:
            filters['created_after'] = created_after
        if created_before:
            filters['created_before'] = created_before
        if limit:
            filters['limit'] = limit
        if offset:
            filters['offset'] = offset
        
        with IvyBloomAPIClient(config, auth_manager) as client:
            jobs_data = client.list_jobs(**filters)
        
        if format == 'json':
            console.print(json.dumps(jobs_data, indent=2))
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(jobs_data, default_flow_style=False))
        elif format == 'csv':
            # Simple CSV output
            if jobs_data:
                headers = jobs_data[0].keys()
                console.print(','.join(headers))
                for job in jobs_data:
                    console.print(','.join(str(job.get(h, '')) for h in headers))
        else:
            # Table format (default)
            if not jobs_data:
                console.print("[yellow]No jobs found[/yellow]")
                return
            
            table = Table(title=f"📋 Jobs ({len(jobs_data)} found)")
            table.add_column("Job ID", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Tool", style="green")
            table.add_column("Created", style="dim")
            table.add_column("Project", style="blue")
            
            for job in jobs_data:
                status_style = {
                    'completed': '[green]COMPLETED[/green]',
                    'running': '[blue]RUNNING[/blue]',
                    'failed': '[red]FAILED[/red]',
                    'pending': '[yellow]PENDING[/yellow]',
                    'cancelled': '[dim]CANCELLED[/dim]'
                }.get(job.get('status', '').lower(), job.get('status', ''))
                
                table.add_row(
                    job.get('job_id', '')[:8] + '...',
                    status_style,
                    job.get('tool_name', ''),
                    job.get('created_at', '')[:16] if job.get('created_at') else '',
                    job.get('project_id', '')[:8] + '...' if job.get('project_id') else 'None'
                )
            
            console.print(table)
    
    except Exception as e:
        console.print(f"[red]❌ Error listing jobs: {e}[/red]")

@jobs.command()
@click.argument('job_id')
@click.option('--follow', '-f', is_flag=True, help='Follow job progress')
@click.option('--logs', is_flag=True, help='Include execution logs')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def status(ctx, job_id, follow, logs, format):
    """Get job status and progress"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            if follow:
                # Follow mode - continuously update status
                with Live(console=console, refresh_per_second=2) as live:
                    while True:
                        job_data = client.get_job_status(job_id, include_logs=logs)
                        
                        # Create status display
                        status_panel = _create_status_panel(job_data)
                        live.update(status_panel)
                        
                        # Check if job is complete
                        if job_data.get('status', '').lower() in ['completed', 'failed', 'cancelled']:
                            break
                        
                        time.sleep(5)  # Wait 5 seconds before next update
            else:
                # Single status check
                job_data = client.get_job_status(job_id, include_logs=logs)
                
                if format == 'json':
                    console.print(json.dumps(job_data, indent=2))
                else:
                    status_panel = _create_status_panel(job_data)
                    console.print(status_panel)
    
    except Exception as e:
        console.print(f"[red]❌ Error getting job status: {e}[/red]")

@jobs.command()
@click.argument('job_id')
@click.option('--format', default='json', type=click.Choice(['json', 'yaml', 'csv']), help='Output format')
@click.option('--output', '-o', help='Save to file')
@click.pass_context
def results(ctx, job_id, format, output):
    """Download job results"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            results_data = client.get_job_results(job_id, format=format)
        
        if output:
            # Save to file
            with open(output, 'w') as f:
                if format == 'json':
                    json.dump(results_data, f, indent=2)
                else:
                    f.write(str(results_data))
            console.print(f"[green]✅ Results saved to {output}[/green]")
        else:
            # Print to console
            if format == 'json':
                console.print(json.dumps(results_data, indent=2))
            else:
                console.print(results_data)
    
    except Exception as e:
        console.print(f"[red]❌ Error getting job results: {e}[/red]")

@jobs.command()
@click.argument('job_id')
@click.pass_context
def cancel(ctx, job_id):
    """Cancel a running job"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    if not click.confirm(f"Are you sure you want to cancel job {job_id}?"):
        console.print("Cancelled.")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            result = client.cancel_job(job_id)
        
        console.print(f"[green]✅ Job {job_id} cancelled successfully[/green]")
    
    except Exception as e:
        console.print(f"[red]❌ Error cancelling job: {e}[/red]")

def _create_status_panel(job_data: dict) -> Panel:
    """Create a rich panel for job status display"""
    job_id = job_data.get('job_id', 'Unknown')
    status = job_data.get('status', 'Unknown')
    tool_name = job_data.get('tool_name', 'Unknown')
    progress = job_data.get('progress_percentage', 0)
    
    # Status styling
    status_styles = {
        'completed': '[green]COMPLETED ✅[/green]',
        'running': '[blue]RUNNING 🔄[/blue]',
        'failed': '[red]FAILED ❌[/red]',
        'pending': '[yellow]PENDING ⏳[/yellow]',
        'cancelled': '[dim]CANCELLED ⏹️[/dim]'
    }
    
    styled_status = status_styles.get(status.lower(), status)
    
    # Build content
    content = f"""[bold cyan]Job ID:[/bold cyan] {job_id}
[bold cyan]Tool:[/bold cyan] {tool_name}
[bold cyan]Status:[/bold cyan] {styled_status}
[bold cyan]Progress:[/bold cyan] {progress:.1f}%"""
    
    if job_data.get('started_at'):
        content += f"\n[bold cyan]Started:[/bold cyan] {job_data['started_at']}"
    
    if job_data.get('completed_at'):
        content += f"\n[bold cyan]Completed:[/bold cyan] {job_data['completed_at']}"
    
    if job_data.get('error_message'):
        content += f"\n[bold red]Error:[/bold red] {job_data['error_message']}"
    
    if job_data.get('execution_logs'):
        content += f"\n\n[bold cyan]Recent Logs:[/bold cyan]"
        for log_line in job_data['execution_logs'][-5:]:  # Last 5 log lines
            content += f"\n[dim]{log_line}[/dim]"
    
    return Panel(
        content,
        title="📊 Job Status",
        border_style="blue" if status.lower() == 'running' else "green" if status.lower() == 'completed' else "red"
    )