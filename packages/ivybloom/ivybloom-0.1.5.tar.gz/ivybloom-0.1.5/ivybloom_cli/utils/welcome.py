"""
Welcome screen display for ivybloom CLI
"""

import shutil
from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.columns import Columns
from rich import box
from .colors import get_console

console = get_console()

def get_terminal_width() -> int:
    """Get current terminal width"""
    return shutil.get_terminal_size().columns

def load_ivy_leaf_art() -> str:
    """Load the elegant text-based ivy leaf design"""
    return """                  `    `  `          `            
 ¨¨¨¨¨¨¨¨¨…¨¨…¨¨¨¨¨¨¨¨¨¨¨¨¨   ›Æ…¨x  ¨¨¨¨¨¨¨¨¨¨¨¨ 
 ¨¨¨¨¨¸¨¨¸¨¨¨¨¨ˆ¨¨¨¨¨¨¨     ’Æ+ | ì“ `¨¨¨¨¨¨¨¨¨¨¨ 
`¨·¨¨¨…¸¨¨¸¨¨¨¨¨¨¨¨…    ­ÝFâ—  †¨  t  ¨¨ˆ·¨¨¨…ˆ¨¨ 
 ¨¨¨¨¨¨¨ˆ¨…¨¨…¨¨…ˆ`` ÆÆ `  `¿``—h;+/  ´¨¨¨¨¨¨¨´¨¨ 
`¨¨¨´´``´´´¨¨¨¨¨´  f¡ ¹ ›¡:›| < ·%…:t  ¨¨¨¨¨¨¨¨…¨ 
 ¨¨¨   `     ``¨  Æ  ·¹· J ‚’`8¸`  †Æ¸ `¨¨¨ˆ¨¨¨¨´ 
 ¨¨¨ ;—¬×aé&©    o‘`º/;×  µ  ¾; ä``  1  ´¨¨¨¨¨¨¨¨ 
 ¨¨´ ë¸}‰` {z¨Æ‰ ç …`~’÷r‘t~G   ·D‰/…¥Ì  ¨¨¨¨¨¨¨¨ 
 ¨·  è‹ `n¹ ¯`•  c 7·2  » `}`£0   ˆ`:*`Æ ¨¨¨¨¨¨¨¨`
 ¨¨ í  ‰7…9  ¨ í¸…¸˜ j¹‚ ’·O  ¸7i… ù˜ w  ¨¨¨¨¨¨ˆ¨`
 ¨¨ û;‚    ~·  <)` “ˆ †˜ ­Ï  %’ ˆž  tÍ­ `¨ˆ·¨ˆ¨¨¨ 
 ˆ¨ z )`· ˆ’7C`+“ˆ ” ’? `J  `º?x `·¢Y   ¨¨¨¨¨¨¨¨¨ 
 ´¨  ý  âÝßµ¤’|ï•  I‚ × á ˜é´  • ¨:²          `¨¨ 
`¨…  yˆˆ `     «ú  ì­²·ö½‘ ¸»¸“ ?{¸ûpD¬±yÐF§u   ´ 
 ¨` ùº˜˜ ‚  ` ` `^5´ `ü` °*`  4L`¸`   ˆ  ÷ `¹´Ý`` 
`¨ °ò /i“¢Ï±4—%òˆ` J ƒ `   ˆI¸ ` ¹•~Ìh{ƒ¡l  ´86 ` 
`¨  Ý?~˜     ÷¦i   Jv±hÿ×º¬=³¬‰‹„` ˜ª     %Á“   ``
`¨´   `{g|  ¨  ¨¹Mc †~ {´  ’   ´¼ º  [<J»ôY   ¨¨´`
 ¨¨·´`    Æ$fäÆî   ˆ`ò ) U¨``s`…^’L|›´ `D   ´´…¨¨ 
 ¨¨¨·¨¨¨´  ` `    ±: æ  ª`in¿ º¨L  ¿¿Æá``  ´…´¨´¨ 
 ¨¨¨¨¨¨¨¨´¨´…¸¨  (< `‚ƒ ˜ ¦`©`÷í¨3S`    `´…´¨¨¨¨¨ 
 ´ˆ¨¨¨·¨¨¨…´¨`  <@    ì–`± · ˜ ‘I    ¨¨¨…´¨¨¨¨¨¨¨ 
 ¨¨¨¨¨¨¨¨¨´´   xi  ¨´  ·hV”˜ r`(° ´¨ˆ¨¨¨¨¨ˆ¨¨¨¨¨¨ 
 ¨¨¨ˆ¨…¨¨    xÚ`  …¨¨¨`    ”Æø#   ¨¨¨¨·¨¨¨¨¨¨¨ˆ¨´ 
 ¨¨¨¨¨¨¨  ˜èQº  `¨¨¨¨¨¨¨¨´`   ` `¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨ 
 `        ``    `             `   `       ``      
"""

def load_compact_art() -> str:
    """Load compact version for narrow terminals"""
    return """  🌿
 🌿🌿
🌿🌿🌿
  ║"""

def show_welcome_screen(version: str = "0.1.5", force_compact: bool = False) -> None:
    """Display welcome screen with ASCII art"""
    
    width = get_terminal_width()
    
    # Choose art based on terminal width
    if force_compact or width < 80:
        ascii_art = load_compact_art()
    else:
        ascii_art = load_ivy_leaf_art()

    # Normalize ASCII: strip common leading indentation and trailing spaces
    def _dedent_ascii(art: str) -> str:
        lines = art.splitlines()
        # Compute minimum leading spaces among non-empty lines
        leading_spaces = [len(line) - len(line.lstrip(" ")) for line in lines if line.strip()]
        common_indent = min(leading_spaces) if leading_spaces else 0
        trimmed = [line[common_indent:].rstrip() for line in lines]
        return "\n".join(trimmed)

    ascii_art_trimmed = _dedent_ascii(ascii_art)
    
    # Create welcome text content with a bit more color and guidance
    welcome_text = (
        f"🌿 [cli.title]ivybloom CLI v{version}[/cli.title]\n"
        "[welcome.text]Computational Biology & Drug Discovery[/welcome.text]\n\n"
        "[cli.bright]Getting started[/cli.bright]: run [cli.accent]ivybloom --help[/cli.accent]\n"
        "[cli.bright]Authenticate[/cli.bright]: [cli.accent]ivybloom auth login[/cli.accent]  🔐\n"
        "[cli.bright]Explore tools[/cli.bright]: [cli.accent]ivybloom tools list[/cli.accent]  🧰\n"
        "[cli.bright]Docs[/cli.bright]: [cli.accent]docs.ivybiosciences.com/cli[/cli.accent]  📘\n"
    )
    
    # Compute layout feasibility for side-by-side rendering
    ascii_lines = ascii_art_trimmed.splitlines()
    left_width = max((len(line.rstrip()) for line in ascii_lines), default=0)
    spacing = 4  # gap between columns managed by Columns
    available_for_right = width - left_width - spacing

    # Build right panel
    right_panel = Panel(
        Text.from_markup(welcome_text),
        title=Text("🌿 ivybloom", style="cli.title"),
        border_style="welcome.border",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    console.print()

    # If there is sufficient width, render side-by-side; otherwise fall back to stacked
    if available_for_right >= 30:
        # Attempt to constrain right panel width for better wrapping
        desired_right_width = min(60, max(40, available_for_right))
        right_panel.width = desired_right_width

        columns = Columns(
            [
                Align.left(Text(ascii_art_trimmed, style="welcome.art")),
                right_panel,
            ],
            expand=False,
            equal=False,
            padding=(0, 4),
        )
        console.print(Align.center(columns))
    else:
        # Stacked layout: art centered, then panel centered
        console.print(Align.center(Text(ascii_art_trimmed, style="welcome.art")))
        console.print()
        console.print(Align.center(right_panel))

    console.print()

def show_welcome_panel(version: str = "0.1.5") -> None:
    """Show welcome screen in a bordered panel"""
    
    width = get_terminal_width()
    
    if width < 80:
        ascii_art = load_compact_art()
    else:
        ascii_art = load_ivy_leaf_art()
    
    welcome_text = f"""🌿 ivybloom CLI v{version} - Ivy Biosciences Platform
   Computational Biology & Drug Discovery

   Run 'ivybloom --help' to get started
   Visit docs.ivybiosciences.com/cli for documentation"""
    
    # Combine art and text
    full_content = f"{ascii_art}\n\n{welcome_text}"
    
    # Create panel
    panel = Panel(
        Align.center(Text(full_content, style="green")),
        title="🌿 ivybloom CLI",
        title_align="center",
        border_style="green",
        padding=(1, 2)
    )
    
    console.print()
    console.print(Align.center(panel))
    console.print()