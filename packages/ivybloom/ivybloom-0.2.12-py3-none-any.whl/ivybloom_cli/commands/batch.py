"""
Batch operations for IvyBloom CLI
"""

import click
import json
import yaml
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from ..client.api_client import IvyBloomAPIClient
from ..utils.config import Config
from ..utils.auth import AuthManager
from ..utils.colors import get_console, print_success, print_error, print_warning, print_info

console = get_console()

@click.group()
@click.pass_context
def batch(ctx):
    """Batch operations for multiple jobs"""
    pass

@batch.command()
@click.argument('job_file', type=click.Path(exists=True))
@click.option('--project-id', help='Project ID for all jobs')
@click.option('--batch-title', help='Title for the batch')
@click.option('--dry-run', is_flag=True, help='Show what would be submitted without actually submitting')
@click.pass_context
def submit(ctx, job_file: str, project_id: str, batch_title: str, dry_run: bool):
    """Submit multiple jobs from a YAML/JSON file"""
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # Load job definitions
    try:
        with open(job_file, 'r') as f:
            if job_file.endswith('.yaml') or job_file.endswith('.yml'):
                jobs_data = yaml.safe_load(f)
            else:
                jobs_data = json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading job file: {e}[/red]")
        return
    
    # Validate job structure
    if not isinstance(jobs_data, dict) or 'jobs' not in jobs_data:
        console.print("[red]Error: Job file must contain a 'jobs' array[/red]")
        return
    
    jobs = jobs_data['jobs']
    if not isinstance(jobs, list):
        console.print("[red]Error: 'jobs' must be an array[/red]")
        return
    
    # Show what will be submitted
    console.print(f"\n[bold cyan]Batch Job Submission[/bold cyan]")
    console.print(f"Jobs to submit: {len(jobs)}")
    if batch_title:
        console.print(f"Batch title: {batch_title}")
    if project_id:
        console.print(f"Project ID: {project_id}")
    
    # Show job details
    table = Table(title="Jobs to Submit")
    table.add_column("Index", style="cyan")
    table.add_column("Tool", style="green")
    table.add_column("Title", style="yellow")
    table.add_column("Parameters", style="dim")
    
    for i, job in enumerate(jobs):
        tool_name = job.get('tool_name', 'Unknown')
        job_title = job.get('job_title', f'Batch job {i+1}')
        params = str(job.get('parameters', {}))[:50] + '...' if len(str(job.get('parameters', {}))) > 50 else str(job.get('parameters', {}))
        table.add_row(str(i+1), tool_name, job_title, params)
    
    console.print(table)
    
    if dry_run:
        console.print("\n[yellow]Dry run mode - no jobs were submitted[/yellow]")
        return
    
    # Confirm submission
    if not Confirm.ask(f"\nSubmit {len(jobs)} jobs?"):
        console.print("[yellow]Batch submission cancelled[/yellow]")
        return
    
    # Submit jobs
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            submitted_jobs = []
            failed_jobs = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Submitting jobs...", total=len(jobs))
                
                for i, job in enumerate(jobs):
                    try:
                        # Prepare job request
                        job_request = {
                            'tool_name': job['tool_name'],
                            'parameters': job['parameters'],
                            'project_id': job.get('project_id') or project_id,
                            'job_title': job.get('job_title') or f'Batch job {i+1}'
                        }
                        
                        # Submit job
                        result = client.create_job(job_request)
                        submitted_jobs.append({
                            'index': i+1,
                            'job_id': result['job_id'],
                            'tool_name': job['tool_name'],
                            'title': job_request['job_title']
                        })
                        
                        progress.update(task, advance=1, description=f"Submitted job {i+1}/{len(jobs)}")
                        
                    except Exception as e:
                        failed_jobs.append({
                            'index': i+1,
                            'error': str(e),
                            'tool_name': job.get('tool_name', 'Unknown')
                        })
                        progress.update(task, advance=1, description=f"Failed job {i+1}/{len(jobs)}")
            
            # Show results
            console.print(f"\n[bold green]Batch submission completed[/bold green]")
            console.print(f"Successfully submitted: {len(submitted_jobs)}")
            console.print(f"Failed: {len(failed_jobs)}")
            
            if submitted_jobs:
                success_table = Table(title="Successfully Submitted Jobs")
                success_table.add_column("Index", style="cyan")
                success_table.add_column("Job ID", style="green")
                success_table.add_column("Tool", style="yellow")
                success_table.add_column("Title", style="dim")
                
                for job in submitted_jobs:
                    success_table.add_row(
                        str(job['index']),
                        job['job_id'],
                        job['tool_name'],
                        job['title']
                    )
                
                console.print(success_table)
            
            if failed_jobs:
                console.print(f"\n[bold red]Failed Jobs:[/bold red]")
                for job in failed_jobs:
                    console.print(f"  {job['index']}: {job['tool_name']} - {job['error']}")
    
    except Exception as e:
        console.print(f"[red]Error during batch submission: {e}[/red]")

@batch.command()
@click.argument('job_ids', nargs=-1, required=True)
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def cancel(ctx, job_ids: tuple, confirm: bool):
    """Cancel multiple jobs by ID"""
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    console.print(f"\n[bold yellow]Batch Job Cancellation[/bold yellow]")
    console.print(f"Jobs to cancel: {len(job_ids)}")
    
    # Show jobs to cancel
    for job_id in job_ids:
        console.print(f"  - {job_id}")
    
    if not confirm and not Confirm.ask(f"\nCancel {len(job_ids)} jobs?"):
        console.print("[yellow]Batch cancellation cancelled[/yellow]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            cancelled_jobs = []
            failed_jobs = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Cancelling jobs...", total=len(job_ids))
                
                for i, job_id in enumerate(job_ids):
                    try:
                        client.cancel_job(job_id)
                        cancelled_jobs.append(job_id)
                        progress.update(task, advance=1, description=f"Cancelled {i+1}/{len(job_ids)}")
                        
                    except Exception as e:
                        failed_jobs.append({'job_id': job_id, 'error': str(e)})
                        progress.update(task, advance=1, description=f"Failed {i+1}/{len(job_ids)}")
            
            # Show results
            console.print(f"\n[bold green]Batch cancellation completed[/bold green]")
            console.print(f"Successfully cancelled: {len(cancelled_jobs)}")
            console.print(f"Failed: {len(failed_jobs)}")
            
            if failed_jobs:
                console.print(f"\n[bold red]Failed Cancellations:[/bold red]")
                for job in failed_jobs:
                    console.print(f"  {job['job_id']}: {job['error']}")
    
    except Exception as e:
        console.print(f"[red]Error during batch cancellation: {e}[/red]")

@batch.command()
@click.argument('job_ids', nargs=-1, required=True)
@click.option('--format', default='json', type=click.Choice(['json', 'yaml', 'table']), help='Output format')
@click.option('--output-dir', help='Directory to save results')
@click.pass_context
def results(ctx, job_ids: tuple, format: str, output_dir: str):
    """Download results for multiple jobs"""
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    console.print(f"\n[bold cyan]Batch Results Download[/bold cyan]")
    console.print(f"Jobs to download: {len(job_ids)}")
    
    if output_dir:
        import os
        os.makedirs(output_dir, exist_ok=True)
        console.print(f"Output directory: {output_dir}")
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            results = []
            failed_jobs = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Downloading results...", total=len(job_ids))
                
                for i, job_id in enumerate(job_ids):
                    try:
                        result = client.get_job_results(job_id, format=format)
                        results.append({'job_id': job_id, 'result': result})
                        
                        # Save to file if output directory specified
                        if output_dir:
                            import os
                            filename = f"job_{job_id}_results.{format}"
                            filepath = os.path.join(output_dir, filename)
                            
                            with open(filepath, 'w') as f:
                                if format == 'json':
                                    json.dump(result, f, indent=2)
                                elif format == 'yaml':
                                    yaml.dump(result, f, default_flow_style=False)
                                else:
                                    f.write(str(result))
                        
                        progress.update(task, advance=1, description=f"Downloaded {i+1}/{len(job_ids)}")
                        
                    except Exception as e:
                        failed_jobs.append({'job_id': job_id, 'error': str(e)})
                        progress.update(task, advance=1, description=f"Failed {i+1}/{len(job_ids)}")
            
            # Show results
            console.print(f"\n[bold green]Batch download completed[/bold green]")
            console.print(f"Successfully downloaded: {len(results)}")
            console.print(f"Failed: {len(failed_jobs)}")
            
            if not output_dir and results:
                # Display results inline
                for result in results:
                    console.print(f"\n[bold]Job {result['job_id']}:[/bold]")
                    if format == 'json':
                        console.print(json.dumps(result['result'], indent=2))
                    elif format == 'yaml':
                        console.print(yaml.dump(result['result'], default_flow_style=False))
                    else:
                        console.print(str(result['result']))
            
            if failed_jobs:
                console.print(f"\n[bold red]Failed Downloads:[/bold red]")
                for job in failed_jobs:
                    console.print(f"  {job['job_id']}: {job['error']}")
    
    except Exception as e:
        console.print(f"[red]Error during batch download: {e}[/red]")