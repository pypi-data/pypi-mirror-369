#!/usr/bin/env python3
"""
IvyBloom CLI - Main entry point
"""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich.align import Align

try:
    from . import __version__
    from .utils.config import Config
    from .utils.welcome import show_welcome_screen
    from .utils.colors import get_console
    from .commands.auth import auth
    from .commands.jobs import jobs
    from .commands.projects import projects
    from .commands.tools import tools, run
    from .commands.account import account
    from .commands.config import config
    from .commands.workflows import workflows
    from .commands.batch import batch
    from .commands.data import data
except ImportError:
    # Direct execution - use absolute imports
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from __init__ import __version__
    from utils.config import Config
    from utils.welcome import show_welcome_screen
    from commands.auth import auth
    from commands.jobs import jobs
    from commands.projects import projects
    from commands.tools import tools, run
    from commands.account import account
    from commands.config import config
    from commands.workflows import workflows
    from commands.batch import batch
    from commands.data import data
    from utils.colors import get_console

console = get_console()

@click.group(invoke_without_command=True)
@click.option('--config-file', type=click.Path(), help='Path to configuration file')
@click.option('--api-url', help='API base URL (overrides config)')
@click.option('--debug', is_flag=True, help='Enable debug output')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output-format', default='table', type=click.Choice(['json', 'yaml', 'table', 'csv']), help='Output format')
@click.option('--timeout', default=30, type=int, help='Request timeout in seconds')
@click.option('--retries', default=3, type=int, help='Number of retry attempts')
@click.option('--quiet', '-q', is_flag=True, help='Suppress non-essential output')
@click.option('--no-progress', is_flag=True, help='Disable progress bars and spinners')
@click.option('--offline', is_flag=True, help='Enable offline mode (use cached data)')
@click.option('--profile', is_flag=True, help='Enable performance profiling')
@click.version_option(version=__version__, prog_name='ivybloom')
@click.pass_context
def cli(ctx, config_file, api_url, debug, verbose, output_format, timeout, retries, quiet, no_progress, offline, profile):
    """
    🌿 IvyBloom CLI - Ivy Biosciences Platform
    
    Computational Biology & Drug Discovery Tools
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Initialize configuration
    config = Config(config_file)
    if api_url:
        config.set('api_url', api_url)
    if debug:
        config.set('debug', True)
    if verbose:
        config.set('verbose', True)
    if output_format:
        config.set('output_format', output_format)
    if timeout:
        config.set('timeout', timeout)
    if retries:
        config.set('retries', retries)
    if quiet:
        config.set('quiet', True)
    if no_progress:
        config.set('no_progress', True)
    if offline:
        config.set('offline', True)
    if profile:
        config.set('profile', True)
    
    ctx.obj['config'] = config
    ctx.obj['debug'] = debug
    ctx.obj['verbose'] = verbose
    ctx.obj['output_format'] = output_format
    ctx.obj['quiet'] = quiet
    ctx.obj['no_progress'] = no_progress
    ctx.obj['offline'] = offline
    ctx.obj['profile'] = profile

    # Show welcome screen if no subcommand was invoked
    if ctx.invoked_subcommand is None:
        show_welcome_screen(__version__)
        click.echo(ctx.get_help())
        return

@cli.command()
@click.pass_context
def version(ctx):
    """Show version information with welcome screen"""
    show_welcome_screen(__version__)

# Add command groups
cli.add_command(auth)
cli.add_command(jobs)
cli.add_command(projects) 
cli.add_command(tools)
cli.add_command(account)
cli.add_command(config)
cli.add_command(workflows)
cli.add_command(batch)
cli.add_command(data)

# Add the run command as a top-level command
cli.add_command(run)

def main():
    """Main CLI entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()