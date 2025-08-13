"""
Configuration management commands for IvyBloom CLI
"""

import click
import json
from rich.console import Console
from rich.table import Table

from ..utils.config import Config
from ..utils.colors import get_console, print_success, print_error, print_warning, print_info

console = get_console()

@click.group()
def config():
    """Configuration management commands"""
    pass

@config.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def set(ctx, key, value):
    """Set configuration value"""
    config_obj = ctx.obj['config']
    
    # Try to parse value as JSON for complex types
    try:
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        parsed_value = value
    
    config_obj.set(key, parsed_value)
    console.print(f"[green]✅ Set {key} = {parsed_value}[/green]")

@config.command()
@click.argument('key')
@click.pass_context
def get(ctx, key):
    """Get configuration value"""
    config_obj = ctx.obj['config']
    
    value = config_obj.get(key)
    if value is None:
        console.print(f"[red]❌ Configuration key '{key}' not found[/red]")
    else:
        console.print(f"{key} = {value}")

@config.command()
@click.pass_context
def list(ctx):
    """List all configuration values"""
    config_obj = ctx.obj['config']
    
    config_data = config_obj.show_config()
    
    table = Table(title="🔧 Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in config_data.items():
        table.add_row(key, str(value))
    
    console.print(table)

@config.command(name="show")
@click.pass_context
def show_config(ctx):
    """Show key runtime values (frontend URL, API URL, client_id)."""
    config_obj = ctx.obj['config']
    table = Table(title="🔧 IvyBloom Runtime Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("IVY_ORCHESTRATOR_URL (resolved)", config_obj.get_api_url())
    table.add_row("IVY_FRONTEND_URL (resolved)", config_obj.get_frontend_url())
    table.add_row("client_id", config_obj.get_or_create_client_id())
    console.print(table)

@config.command()
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def reset(ctx, confirm):
    """Reset configuration to defaults"""
    config_obj = ctx.obj['config']
    
    if not confirm:
        if not click.confirm("Are you sure you want to reset all configuration to defaults?"):
            console.print("Reset cancelled.")
            return
    
    config_obj.reset()
    console.print("[green]✅ Configuration reset to defaults[/green]")

@config.command()
@click.pass_context
def path(ctx):
    """Show configuration file path"""
    config_obj = ctx.obj['config']
    console.print(f"Configuration file: {config_obj.config_path}")

@config.command()
@click.argument('key')
@click.pass_context
def unset(ctx, key):
    """Remove configuration key"""
    config_obj = ctx.obj['config']
    
    config_data = config_obj.show_config()
    if key not in config_data:
        console.print(f"[red]❌ Configuration key '{key}' not found[/red]")
        return
    
    # Remove by setting to None and reloading defaults
    config_obj.config.pop(key, None)
    config_obj.save()
    console.print(f"[green]✅ Removed configuration key '{key}'[/green]")

@config.command()
@click.option('--format', default='json', type=click.Choice(['json', 'yaml']), help='Export format')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def export(ctx, format, output):
    """Export configuration to file"""
    config_obj = ctx.obj['config']
    config_data = config_obj.show_config()
    
    if format == 'json':
        content = json.dumps(config_data, indent=2)
    elif format == 'yaml':
        import yaml
        content = yaml.dump(config_data, default_flow_style=False)
    
    if output:
        with open(output, 'w') as f:
            f.write(content)
        console.print(f"[green]✅ Configuration exported to {output}[/green]")
    else:
        console.print(content)

@config.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--merge', is_flag=True, help='Merge with existing config instead of replacing')
@click.pass_context
def import_config(ctx, file_path, merge):
    """Import configuration from file"""
    config_obj = ctx.obj['config']
    
    try:
        with open(file_path, 'r') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                import yaml
                imported_config = yaml.safe_load(f)
            else:
                imported_config = json.load(f)
        
        if merge:
            # Merge with existing config
            current_config = config_obj.show_config()
            current_config.update(imported_config)
            config_obj.config = current_config
        else:
            # Replace config
            config_obj.config = imported_config
        
        config_obj.save()
        action = "merged" if merge else "imported"
        console.print(f"[green]✅ Configuration {action} from {file_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to import configuration: {e}[/red]")