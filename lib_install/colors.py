import os

COLORS = {
    "BLUE": "\033[34m",
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[33m",
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
}

ICONS = {
    "info": "\u2139",
    "error": "\u274C",
    "warning": "\u26A0",
    "success": "\u2705"
}

def colorText(text, color, bold=False):
    """Apply color and optional bold to text."""
    color_code = COLORS.get(color, '')
    if bold:
        color_code = COLORS["BOLD"] + color_code
    return f"{color_code}{text}{COLORS['RESET']}"

def printColored(message, color="RESET", bold=False):
    """Print a message with optional color and bold formatting."""
    print(colorText(message, color, bold))
    

def printLogo():
    logo_path = f"/home/{os.environ.get('SUDO_USER')}/install/lib_install/logo.txt"
   
    with open(logo_path, "r") as file:
        ascii_art = file.read()
        print(ascii_art)
    printColored("License Creative Commons CC BY-NC 4.0 Utilisation non commerciale 4.0 International","YELLOW")