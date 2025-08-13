"""
Project management commands for IvyBloom CLI
"""

import click
import json
from rich.console import Console
from rich.table import Table

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..client.api_client import IvyBloomAPIClient
from ..utils.colors import get_console

console = get_console()

@click.group()
def projects():
    """Project management commands"""
    pass

@projects.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def list(ctx, format):
    """List your projects"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            projects_data = client.list_projects()
        
        if format == 'json':
            console.print(json.dumps(projects_data, indent=2))
        else:
            if not projects_data:
                console.print("[yellow]No projects found[/yellow]")
                return
            
            table = Table(title=f"📁 Projects ({len(projects_data)} found)")
            table.add_column("Project ID", style="cyan")
            table.add_column("Name", style="bold")
            table.add_column("Jobs", style="green")
            table.add_column("Last Activity", style="dim")
            
            for project in projects_data:
                table.add_row(
                    project.get('project_id', '')[:8] + '...',
                    project.get('name', 'Unnamed'),
                    str(project.get('job_count', 0)),
                    project.get('last_activity', 'Never')[:16] if project.get('last_activity') else 'Never'
                )
            
            console.print(table)
    
    except Exception as e:
        console.print(f"[red]❌ Error listing projects: {e}[/red]")

@projects.command()
@click.argument('project_id')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def info(ctx, project_id, format):
    """Get project information"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            project_data = client.get_project(project_id)
        
        if format == 'json':
            console.print(json.dumps(project_data, indent=2))
        else:
            console.print(f"[bold cyan]📁 {project_data.get('name', 'Unnamed Project')}[/bold cyan]")
            console.print(f"   Project ID: {project_data.get('project_id', 'Unknown')}")
            console.print(f"   Description: {project_data.get('description', 'No description')}")
            console.print(f"   Created: {project_data.get('created_at', 'Unknown')}")
            console.print(f"   Jobs: {project_data.get('job_count', 0)}")
            console.print(f"   Last Activity: {project_data.get('last_activity', 'Never')}")
    
    except Exception as e:
        console.print(f"[red]❌ Error getting project info: {e}[/red]")

@projects.command()
@click.argument('project_id')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def jobs(ctx, project_id, format):
    """List jobs for a specific project"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            jobs_data = client.list_project_jobs(project_id)
        
        if format == 'json':
            console.print(json.dumps(jobs_data, indent=2))
        else:
            if not jobs_data:
                console.print(f"[yellow]No jobs found for project {project_id}[/yellow]")
                return
            
            table = Table(title=f"📋 Project Jobs ({len(jobs_data)} found)")
            table.add_column("Job ID", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Tool", style="green")
            table.add_column("Created", style="dim")
            
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
                    job.get('created_at', '')[:16] if job.get('created_at') else ''
                )
            
            console.print(table)
    
    except Exception as e:
        console.print(f"[red]❌ Error listing project jobs: {e}[/red]")