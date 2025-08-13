"""
Welcome screen display for IvyBloom CLI
"""

import shutil
from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from .colors import get_console

console = get_console()

def get_terminal_width() -> int:
    """Get current terminal width"""
    return shutil.get_terminal_size().columns

def load_ivy_leaf_art() -> str:
    """Load the elegant text-based ivy leaf design"""
    return """           `          `  `     `                               `                                    
               `         ``                  `                  ùÆãÆ    `                           
                  `  `    `    `                              oÆ~˜ ¸f                               
                  `                       ` `               ›Æs …&  Æ                 `             
                                                           ÆÏ  `b Ï  Å                              
              `          `                               ÆÙ  '¤´˜  Ò{[²  `                          
                              `                      ªÆÆº ³£:· Î¢ê ``vÆ                 `           
            `                 `                 `ŸÆÆÆ' 65  ·³  2   ‡ `<Ë                            
               `    `       `   `           TÆÆÆ`       ……    &t·‹'¨ ¹ Æ `                          
                          `              ¥ÆF«   ¦ v  ;¨ ª'¨²  Ø  `  yù ­¤                `    `     
                                    `  ÇÆ  ` ž    £ "¯  ·Y…  Á     ¿¸   Ý                        `  
`                                     Æî }­…L+ îÿ 'I ­÷`  © þ˜  {ÆÍvÉ;´ t                 ` `  `    
                `                    X ›  }h     ´ ©   ²¨¨·`j ê`'      Q Æ                  `       
                                    ÃT0 ¨  ™¨Úv''´×š ^¹1r  ixÉ   LÏˆ ú ‹‚šÐ                         
    `      ÕZ|ÆÆÆÆÆÆU              s^   p  O      ´ ¶  ~  ô«   u4   ¨ îg‰É°'                        
     `     ¢     `  eÏÐÁÆ¢‹        X›×' :v'6 'Óÿ    ¼7    d` <· Æ;f  L…    Æ      `              `  
           Æ ´  ë  ·   ï( áÆÆ  `   Ÿ '  `` t    nmÄ› © ·`®:´Aü     ´éú‚¦Ì<  #                `      
        `  M Nl ³Ì&` "   †  `ÈÆo"¸Wú 8¿ : ¨ö˜'³ˆ     à` fL       Œ^Ÿ    … Æ¬OO `                    
          ë    ˜  ¹O•Ÿ''þ ··ˆ  ?`` º      ×} }…‹¸`:   ÷p'  ` û@Æè  ¨jª'É    — Æ       `    `   `  ` 
          Æ ?='ˆ;¬T°e   ?‹´ ¦v‚   7ñ'ïi†S ˜¡    >ú ¯› ‹û  3ÌT‹    ·…  `  ¥Y…° Æ¯                    
         ›&´ä¬      ×¥ /`r ¹ ˆë 3`      …5IÍ`˜'­`¦·  '7 Ùo¬½ç åÒøa  "Yí õÓ'!…¬Ë    `                
         #   `ŒMþ3Sn'L   :  : ¸o' ^– Ò¼° ¨ 8 `´ˆ` ­{ –Ð      ‡^/¦/¿   ç¹†    ø`                     
         ž  u `      …q™  ö" 3 ï `‚¥n*     ›x <' '  ÏÎˆ ' ¨ ˆ  ´  0 M¯`ã  ‹·öä              `       
         Ø b' ‚;;  `   Cs ¨`˜` ÒL      —¦–' ‡>‚ …  /O`    ¤¯O ¸  'šc ¨  í· Ñ­           ` `         
         È ¸ˆ·` = §Å¨(„ m¬ ·   y^  ·ƒ³ú‚ˆ¨· ˆÌ ‹   P I•ÖoöÏ ¢· Qžÿ ' …  ¨ðÆ                         
   `     È ´•*  ´ˆ —     cÊ ¸  ®/ s†` / ` ¹c`L ' ¸M›       ´!½—      ¸C ß'        ` `           `   
         h3¸ âê‚        ÷ 7@:  97   ) · ˜!   4¸² ¦² ¾›  Oýôm`"Ì23'af×„4Æ        `    `              
          Æ` `  FÈ Nppñü$†t`+¼ ù*     ï†×· ˜¸j­ b5   ¬€™¯`    `~ '–  rƒ                             
          žcz…´    º     `   ÜzÒ× öò·`óï  ¸ˆ  `M   Ã?Ì ¸ …› Æ`ˆo` ê wtÞ 'ˆ„ÆÆÆÆÆÆÆÆ          `      
 `         Ý ¯»:˜…¨     'ˆ`:    6•  ` —z­' '  ·‡—T¡  º´‚‹õ'‹"    ¬   `            tj$ÆÆW[           
       `  †á ¨ `  ´ …ñ& `: ­'  …`m&2 ` u `û  ÕÊ¹ ` ¨´  ~  ´   ¸5tdß3tþKxßêÏ'…´swV   '  xrýÆ˜ `      
         #ù´`Ã›` ‹&ˆ˜  ~?·  ´º*    sñ  ½  7 ff   ²÷‹ x      ¡Û©‚    ·       ;o… ˆ ¾ù  c    !Æ›      
     `  Æ      ™`     ´    '   ó |' pà'  §'ºÆ` ×˜ˆ …<ˆ…¼ ú÷Åg `¸… ·ˆº` '  sH   Z´ ` ÑÆ‚'<¨›# °Æ     
       Æ •nuFTD›6 øèÙ$445ë¯GøæaÏ      °Ð  —ç  ·' ¨ '    Pz‹       ¨ ' ``¯o¿¢¼ZhL~PY‹  „    ŸÆh`     
       Èâ   ~ ' ¨ `    G`       kÆÆ­›É`ér¹‰          ÖÆ      óÆÆÆ›ª²–˜XÆ           CZ `  Æp         
 `      ;Æ$  ‚õ »¹ˆ›' ˆi:'ÝîI—F;        &¨„°ÚRŒÆ$+/•"·–°»/{ù³         ` r  ·¸‡n  ¹‹ ´ò'Æm       `   
           ÅÆz     ®¨'     …é¸ ( vÌ–¬ ŽÆ  ©–¯!     `´ `     ·O½  ~…'nî V 5½    +‹   ¤ìþ            `
              &Æâ/`   ```i@'      ‹ÇÆ¶   â'' +àú·  … ˆ"§ ›¨ ´ ;'Ì`   :˜‚ˆ Í9†´ ' —±`Æª    ``        
                 €Æ¨ 'ÂqÙ `   ˜ ÄÆg    o ¬ w ^× NÆ · ˜   ^ '2`&'7éÆl  ·     ô …  —`Æ            `   
                    ÆÆðoSGQÆÆÆD† `    –' ­Å '  ù  Zµ  …Ì' È`     á  æ‚N òœÎ     ~Æ¨                 
          `     `                     |'  Æ ¿'&'`; tEˆ     ‹%  Æ    â´ `  ~ˆÂV†Æ¬                `  
      `                           `  ¥–­  R ³  ‚²…' `æŒ …8 ' › ³¸      Å‚ ×9Æ¶´                     
`                                   ‰     'Ì> ¨      `›Ü  ˆ; `  *­Lÿ:T}rÆÖU       `                 
         `                         |"Y     é u  Ì›(`è¨ ¹µ–    äà‚  ãÑÜ´ ` `      `                  
 `                          `     C‡­      ³Ã  '      ´  S ÑÆ?   Ûe                                 
`                                µ'a     ``  Æ´lº¿¤æ …'~·¥    Ý›ƒs                   `              
                             `  Žþ°` ``    `  Ê¸  `¼  ­¨» Z˜'`÷`T          `          `             
             `                ^ív‚    `        3Ær  ¸/`   Y    ¨&           `                       
                     ``  `   ã;Æ                 "ÆÆ¿!j •U»ñyC·Æ `                  `               
    `                   `  ³};y    ``   `            !èÆÊ0 ´ ¶a    `           `                    
`   `               `    ¸Æ´Æ…                           ´‚‹¸       ` ``                   `        
      ` ` `            yL=Æ… `                   `       `                                ` `       
                    …ÆfïÆ`              `   `                                                  `    
            `      UNýÆ `     `               `             ``      `   `  `                        
               `       `                                      `                                   `"""

def load_compact_art() -> str:
    """Load compact version for narrow terminals"""
    return """  🌿
 🌿🌿
🌿🌿🌿
  ║"""

def show_welcome_screen(version: str = "1.0.0", force_compact: bool = False) -> None:
    """Display welcome screen with ASCII art"""
    
    width = get_terminal_width()
    
    # Choose art based on terminal width
    if force_compact or width < 80:
        ascii_art = load_compact_art()
    else:
        ascii_art = load_ivy_leaf_art()
    
    # Create welcome text with left-justified opening lines
    welcome_text = f"""🌿 IvyBloom CLI v{version} - Ivy Biosciences Platform
Computational Biology & Drug Discovery Tools

Run 'ivybloom --help' to get started
Visit docs.ivybiosciences.com/cli for documentation"""
    
    # Display with proper alignment using themed colors
    console.print()
    console.print(Align.center(Text(ascii_art, style="welcome.art")))
    console.print()
    console.print(Text(welcome_text, style="welcome.text"))  # Left-justified welcome text
    console.print()

def show_welcome_panel(version: str = "1.0.0") -> None:
    """Show welcome screen in a bordered panel"""
    
    width = get_terminal_width()
    
    if width < 80:
        ascii_art = load_compact_art()
    else:
        ascii_art = load_ivy_leaf_art()
    
    welcome_text = f"""🌿 IvyBloom CLI v{version} - Ivy Biosciences Platform
   Computational Biology & Drug Discovery Tools

   Run 'ivybloom --help' to get started
   Visit docs.ivybiosciences.com/cli for documentation"""
    
    # Combine art and text
    full_content = f"{ascii_art}\n\n{welcome_text}"
    
    # Create panel
    panel = Panel(
        Align.center(Text(full_content, style="green")),
        title="🌿 IvyBloom CLI",
        title_align="center",
        border_style="green",
        padding=(1, 2)
    )
    
    console.print()
    console.print(Align.center(panel))
    console.print()