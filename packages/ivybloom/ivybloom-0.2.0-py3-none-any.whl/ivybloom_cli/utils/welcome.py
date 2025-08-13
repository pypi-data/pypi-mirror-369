"""
Welcome screen display for ivybloom CLI
"""

import shutil
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich import box
from .colors import get_console

console = get_console()

def get_terminal_width() -> int:
    """Get current terminal width"""
    return shutil.get_terminal_size().columns

def load_ivy_leaf_art() -> str:
    """Load simple ivy leaf design"""
    return """🌿 ivybloom"""

def load_compact_art() -> str:
    """Load compact version for narrow terminals"""
    return """🌿 ivybloom"""

def show_welcome_screen(version: str = "0.2.0", force_compact: bool = False) -> None:
    """Display welcome screen with simplified content"""
    
    # Create compact welcome content with proper line breaks
    welcome_text = (
        f"🌿 [cli.title]ivybloom CLI v{version}[/cli.title]\n"
        "[welcome.text]Computational Biology & Drug Discovery[/welcome.text]\n\n"
        "[cli.bright]Getting started:[/cli.bright]\n"
        "[cli.accent]ivybloom --help[/cli.accent]\n\n"
        "[cli.bright]Authenticate:[/cli.bright] 🔐\n"
        "[cli.accent]ivybloom auth login[/cli.accent]\n\n"
        "[cli.bright]Explore tools:[/cli.bright] 🧰\n"
        "[cli.accent]ivybloom tools list[/cli.accent]\n\n"
        "[cli.bright]Docs:[/cli.bright] 📘\n"
        "[cli.accent]docs.ivybiosciences.com/cli[/cli.accent]"
    )
    
    # Create a simple centered panel
    panel = Panel(
        Text.from_markup(welcome_text),
        title="🌿 ivybloom",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2),
        width=min(50, get_terminal_width() - 4)  # Ensure it fits with margin
    )
    
    console.print()
    console.print(Align.center(panel))
    console.print()

def show_welcome_panel(version: str = "0.2.0") -> None:
    """Show welcome screen in a bordered panel"""
    
    welcome_text = (
        f"🌿 ivybloom CLI v{version}\n"
        "Computational Biology & Drug Discovery\n\n"
        "Run 'ivybloom --help' to get started\n"
        "Visit docs.ivybiosciences.com/cli"
    )
    
    # Create simple panel with proper width constraints
    panel = Panel(
        Align.center(Text(welcome_text, style="green")),
        title="🌿 ivybloom CLI",
        title_align="center",
        border_style="green",
        padding=(1, 2),
        width=min(45, get_terminal_width() - 4)  # Prevent wrapping
    )
    
    console.print()
    console.print(Align.center(panel))
    console.print()