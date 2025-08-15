"""
Interactive utilities for IvyBloom CLI
"""

import sys
from typing import List, Dict, Any, Optional, Callable
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def select_from_list(
    items: List[Dict[str, Any]], 
    title: str,
    display_key: str = 'name',
    id_key: str = 'id',
    description_key: Optional[str] = None,
    max_display: int = 10,
    allow_cancel: bool = True
) -> Optional[str]:
    """
    Interactive selection from a list using arrow keys (fallback to number selection)
    
    Args:
        items: List of dictionaries containing selectable items
        title: Title to display above the selection
        display_key: Key to use for display text
        id_key: Key to use for return value
        description_key: Optional key for additional description
        max_display: Maximum items to display at once
        allow_cancel: Whether to allow canceling selection
    
    Returns:
        Selected item ID or None if cancelled
    """
    if not items:
        console.print(f"[yellow]No items available for selection.[/yellow]")
        return None
    
    # For now, implement a simple numbered selection
    # TODO: Add proper arrow key navigation with a library like inquirer
    return _numbered_selection(items, title, display_key, id_key, description_key, max_display, allow_cancel)

def _numbered_selection(
    items: List[Dict[str, Any]], 
    title: str,
    display_key: str,
    id_key: str,
    description_key: Optional[str],
    max_display: int,
    allow_cancel: bool
) -> Optional[str]:
    """Numbered selection interface"""
    
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print()
    
    # Display items with numbers
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Number", style="cyan", width=4)
    table.add_column("Item", style="white")
    if description_key:
        table.add_column("Description", style="dim")
    
    display_items = items[:max_display]
    
    for i, item in enumerate(display_items, 1):
        display_text = str(item.get(display_key, 'Unknown'))
        row = [f"{i}.", display_text]
        
        if description_key:
            desc = str(item.get(description_key, ''))
            if len(desc) > 50:
                desc = desc[:47] + "..."
            row.append(desc)
        
        table.add_row(*row)
    
    console.print(table)
    
    if len(items) > max_display:
        console.print(f"[dim]... and {len(items) - max_display} more items[/dim]")
    
    console.print()
    
    # Get user selection
    while True:
        if allow_cancel:
            prompt_text = f"Select an item (1-{len(display_items)}) or 'q' to quit: "
        else:
            prompt_text = f"Select an item (1-{len(display_items)}): "
        
        try:
            response = input(prompt_text).strip().lower()
            
            if allow_cancel and response in ['q', 'quit', 'cancel', '']:
                return None
            
            selection = int(response)
            if 1 <= selection <= len(display_items):
                selected_item = display_items[selection - 1]
                return str(selected_item.get(id_key))
            else:
                console.print(f"[red]Please enter a number between 1 and {len(display_items)}[/red]")
                
        except (ValueError, KeyboardInterrupt):
            if allow_cancel:
                return None
            console.print("[red]Please enter a valid number[/red]")

def select_job_action(job_data: Dict[str, Any]) -> Optional[str]:
    """
    Select an action to perform on a job
    
    Args:
        job_data: Job information dictionary
        
    Returns:
        Selected action or None if cancelled
    """
    job_id = job_data.get('job_id') or job_data.get('id', 'Unknown')
    job_title = job_data.get('job_title', 'Untitled')
    job_type = job_data.get('job_type') or job_data.get('tool_name', 'Unknown')
    status = job_data.get('status', 'Unknown')
    
    # Show job info
    console.print(f"\n[bold cyan]Job Actions for:[/bold cyan]")
    console.print(f"  [cyan]ID:[/cyan] {job_id}")
    console.print(f"  [cyan]Title:[/cyan] {job_title}")
    console.print(f"  [cyan]Type:[/cyan] {job_type}")
    console.print(f"  [cyan]Status:[/cyan] {status}")
    console.print()
    
    # Available actions based on job status
    actions = []
    
    # Always available
    actions.append({
        'id': 'status',
        'name': '📊 View Status',
        'description': 'Show detailed job status and progress'
    })
    
    # For completed jobs
    if status.upper() in ['COMPLETED', 'SUCCESS']:
        actions.extend([
            {
                'id': 'results',
                'name': '📄 View Results',
                'description': 'Show job results and metadata'
            },
            {
                'id': 'download',
                'name': '📥 Download Files',
                'description': 'Download result files and artifacts'
            }
        ])
    
    # For running jobs
    if status.upper() in ['PENDING', 'PROCESSING', 'STARTED']:
        actions.extend([
            {
                'id': 'follow',
                'name': '👁️  Monitor Live',
                'description': 'Watch job progress in real-time'
            },
            {
                'id': 'cancel',
                'name': '❌ Cancel Job',
                'description': 'Cancel the running job'
            }
        ])
    
    return select_from_list(
        items=actions,
        title="Available Actions",
        display_key='name',
        id_key='id',
        description_key='description',
        allow_cancel=True
    )

def select_project_action(project_data: Dict[str, Any]) -> Optional[str]:
    """
    Select an action to perform on a project
    
    Args:
        project_data: Project information dictionary
        
    Returns:
        Selected action or None if cancelled
    """
    project_id = project_data.get('project_id') or project_data.get('id', 'Unknown')
    project_name = project_data.get('name', 'Untitled')
    
    # Show project info
    console.print(f"\n[bold cyan]Project Actions for:[/bold cyan]")
    console.print(f"  [cyan]ID:[/cyan] {project_id}")
    console.print(f"  [cyan]Name:[/cyan] {project_name}")
    console.print()
    
    actions = [
        {
            'id': 'info',
            'name': 'ℹ️  View Details',
            'description': 'Show detailed project information'
        },
        {
            'id': 'jobs',
            'name': '📋 View Jobs',
            'description': 'List all jobs in this project'
        },
        {
            'id': 'create_job',
            'name': '🚀 Create Job',
            'description': 'Run a new job in this project'
        }
    ]
    
    return select_from_list(
        items=actions,
        title="Available Actions",
        display_key='name',
        id_key='id',
        description_key='description',
        allow_cancel=True
    )

def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask for confirmation with y/n prompt
    
    Args:
        message: Confirmation message
        default: Default value if user just presses enter
        
    Returns:
        True if confirmed, False otherwise
    """
    default_text = "Y/n" if default else "y/N"
    prompt = f"{message} ({default_text}): "
    
    try:
        response = input(prompt).strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'true', '1']
        
    except KeyboardInterrupt:
        return False
