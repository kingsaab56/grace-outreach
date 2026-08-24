import sys
import os

if sys.platform == "win32":
    os.system("")

class UI:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    ORANGE  = "\033[38;5;208m"
    GOLD    = "\033[38;5;220m"
    PURPLE  = "\033[38;5;141m"
    PINK    = "\033[38;5;213m"
    LIME    = "\033[38;5;118m"
    AQUA    = "\033[38;5;51m"
    CORAL   = "\033[38;5;203m"


def print_welcome_avatar_banner():
    rockstar_art = r"""
                  👑  KING SAAB  👑
             ╔═════════════════════════╗
             ║   (•‿•)   ROCK STAR !   ║
             ║  <)  )╯  GRACE ASSIST   ║
             ║   /  \    EST. 2026     ║
             ╚═════════════════════════╝"""

    print(f"\n{UI.PINK}  ★  *  *  ★  *  *  ★  *  *  ★  *  *  ★  *  *  ★  *  *  ★  *  *  ★  *  *  ★  *  *  ★{UI.RESET}")
    print(f"{UI.AQUA}          🎈  🌟  🎈                               🎈  🌟  🎈{UI.RESET}")
    print(f"{UI.GOLD}{UI.BOLD}{rockstar_art}{UI.RESET}")
    print(f"{UI.PINK}          🎈  ✨  🎈                               🎈  ✨  🎈{UI.RESET}")
    print(f"{UI.CYAN}{UI.BOLD}═════════════════════════════════════════════════════════════════════════════════{UI.RESET}")
    print(f"{UI.LIME}{UI.BOLD}             🌟 WELCOME TO GRACE OUTREACH ASSISTANT 🌟{UI.RESET}")
    print(f"{UI.ORANGE}{UI.BOLD}                   Developed by: King Saab (Pro AI Engine){UI.RESET}")
    print(f"{UI.CYAN}{UI.BOLD}═════════════════════════════════════════════════════════════════════════════════{UI.RESET}\n")


def show_main_menu():
    print(f"""
{UI.GOLD}{UI.BOLD}╔═══════════════════════════════════════════════════════════════════════════════╗
║                      💎 MASTER SYSTEM CONTROLLER 💎                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝{UI.RESET}

 {UI.LIME}{UI.BOLD}[22]{UI.RESET} 🚀 {UI.LIME}CAMPAIGN ENGINE V2{UI.RESET} {UI.DIM}── (AI Scorer, Multi-Accounts, Schedulers & Quotas){UI.RESET}

 {UI.CYAN}{UI.BOLD}[1]{UI.RESET}  🏢 {UI.CYAN}Company & Project Info Setup{UI.RESET}
 {UI.AQUA}{UI.BOLD}[2]{UI.RESET}  👥 {UI.AQUA}Lead Management & Contacts Importer{UI.RESET}
 {UI.PURPLE}{UI.BOLD}[3]{UI.RESET}  ✉️  {UI.PURPLE}Email Template Designer & Personalizer{UI.RESET}
 {UI.PINK}{UI.BOLD}[4]{UI.RESET}  🤖 {UI.PINK}AI Outreach Generator & Assistant{UI.RESET}
 {UI.ORANGE}{UI.BOLD}[5]{UI.RESET}  🛡️  {UI.ORANGE}Gmail Accounts Health & OAuth Center{UI.RESET}
 {UI.YELLOW}{UI.BOLD}[6]{UI.RESET}  📥 {UI.YELLOW}Reply Tracker & Sentiment Analyzer{UI.RESET}
 {UI.GOLD}{UI.BOLD}[7]{UI.RESET}  ⏰ {UI.GOLD}Automated Follow-up Sequences{UI.RESET}
 {UI.BLUE}{UI.BOLD}[8]{UI.RESET}  📊 {UI.BLUE}Analytics & Conversion Reports{UI.RESET}
 {UI.GREEN}{UI.BOLD}[9]{UI.RESET}  ⚙️  {UI.GREEN}System Database & Settings Backup{UI.RESET}

 {UI.RED}{UI.BOLD}[0]{UI.RESET}  🚪 {UI.RED}Exit Grace Outreach Assistant{UI.RESET}
{UI.CYAN}───────────────────────────────────────────────────────────────────────────────{UI.RESET}""")
