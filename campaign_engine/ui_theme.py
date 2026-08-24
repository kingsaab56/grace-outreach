"""
Windows Safe UI Theme & Terminal Color Controller
Ensures UTF-8 encoding, ANSI compatibility, and full color attributes.
"""

import os
import sys

if sys.platform == "win32":
    os.system("")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GOLD = "\033[33m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"


def print_banner(title, icon="🚀"):
    width = 74
    print("\n" + Colors.CYAN + "=" * width + Colors.RESET)
    content = f"  {icon}  {title}  {icon}"
    print(Colors.BOLD + content.center(width) + Colors.RESET)
    print(Colors.CYAN + "=" * width + Colors.RESET + "\n")


def info(msg):
    return f"{Colors.CYAN}ℹ {msg}{Colors.RESET}"


def success(msg):
    return f"{Colors.GREEN}✔ {msg}{Colors.RESET}"


def warning(msg):
    return f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}"


def error(msg):
    return f"{Colors.RED}✖ {msg}{Colors.RESET}"


def highlight(msg):
    return f"{Colors.BOLD}{Colors.WHITE}{msg}{Colors.RESET}"
