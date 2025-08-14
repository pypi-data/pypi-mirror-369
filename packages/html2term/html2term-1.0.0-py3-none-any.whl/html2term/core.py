import re
import sys
import os
from typing import List, Dict, Tuple

RESET = "\033[0m"

TAGS: Dict[str, str] = {
    # Styles
    "b": "\033[1m", "strong": "\033[1m", "i": "\033[3m", "em": "\033[3m",
    "u": "\033[4m", "blink": "\033[5m", "strike": "\033[9m",
    # Foreground colors
    "black": "\033[30m", "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
    "blue": "\033[34m", "magenta": "\033[35m", "cyan": "\033[36m", "white": "\033[37m",
    "default": "\033[39m",
    # Background colors
    "bg-black": "\033[40m", "bg-red": "\033[41m", "bg-green": "\033[42m",
    "bg-yellow": "\033[43m", "bg-blue": "\033[44m", "bg-magenta": "\033[45m",
    "bg-cyan": "\033[46m", "bg-white": "\033[47m", "bg-default": "\033[49m",
}

def _enable_windows_support():
    if sys.platform == "win32":
        os.system("")

def _hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Converts a 6-digit hex color string to an (R, G, B) tuple."""
    hex_code = hex_code.lstrip('#')
    if len(hex_code) != 6:
        raise ValueError("Invalid hex code length, must be 6 characters.")
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def _get_style_code(tag_name: str) -> str:
    if tag_name in TAGS:
        return TAGS[tag_name]
    if tag_name.startswith('#'):
        try:
            r, g, b = _hex_to_rgb(tag_name)
            return f"\033[38;2;{r};{g};{b}m"
        except (ValueError, IndexError):
            return ""
    if tag_name.startswith('bg-#'):
        try:
            r, g, b = _hex_to_rgb(tag_name.lstrip('bg-'))
            return f"\033[48;2;{r};{g};{b}m"
        except (ValueError, IndexError):
            return ""
    return ""

def convert(markup: str) -> str:
    parts = re.split(r'(<[^>]+>)', markup)
    output: List[str] = []
    style_stack: List[str] = []

    for part in parts:
        if not part:
            continue
        
        match = re.match(r'<(/?)(\S+?)\s*/?>', part)
        if not match:
            output.append(part)
            continue

        is_closing, tag_name = match.groups()
        tag_name = tag_name.lower()

        if tag_name in ('br', 'tab'):
            output.append('\n' if tag_name == 'br' else '\t')
            continue

        if is_closing:
            if tag_name in style_stack:
                while style_stack:
                    if style_stack.pop() == tag_name:
                        break
                output.append(RESET)
                for open_tag in style_stack:
                    output.append(_get_style_code(open_tag))
            else:
                output.append(part)
            continue
        
        style_code = _get_style_code(tag_name)
        if style_code:
            style_stack.append(tag_name)
            output.append(style_code)
        else:
            output.append(part)

    output.append(RESET)
    return "".join(output)

def printc(markup: str, **kwargs):
    print(convert(markup), **kwargs)
