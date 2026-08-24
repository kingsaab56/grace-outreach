import os
import sys
import ctypes

# Force Enable Virtual Terminal ANSI Sequences on Windows Console
if os.name == 'nt':
    try:
        kernel32 = ctypes.windll.kernel32
        hStdOut = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
        kernel32.SetConsoleMode(hStdOut, mode.value | 0x0004 | 0x0008)
    except Exception:
        pass
    os.system('')

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from campaign_engine.campaign_menu import campaign_engine_menu
from campaign_engine.ui_theme import Colors

def main():
    while True:
        print(f"""
{Colors.CYAN}========================================================={Colors.RESET}
            {Colors.BOLD}{Colors.GOLD}Grace Outreach Assistant V1.0{Colors.RESET}
                {Colors.DIM}Developed by King Saab{Colors.RESET}
{Colors.CYAN}========================================================={Colors.RESET}

 {Colors.GREEN}[1]{Colors.RESET} Email Collector (DB)
 {Colors.GREEN}[2]{Colors.RESET} Email Cleaner (DB)
 {Colors.CYAN}[3]{Colors.RESET} Campaign Manager
 {Colors.YELLOW}[4]{Colors.RESET} Spam Checker
 {Colors.BLUE}[5]{Colors.RESET} CRM Dashboard
 {Colors.GOLD}[6]{Colors.RESET} Lead Scoring
 {Colors.MAGENTA}[7]{Colors.RESET} AI Template Analyzer
 {Colors.MAGENTA}[8]{Colors.RESET} Subject Analyzer
 {Colors.CYAN}[9]{Colors.RESET} Template Manager
 {Colors.WHITE}[10]{Colors.RESET} Reports
 {Colors.WHITE}[11]{Colors.RESET} Activity Logs
 {Colors.GOLD}[12]{Colors.RESET} Personalized Campaign
 {Colors.CYAN}[13]{Colors.RESET} Campaign Progress
 {Colors.DIM}[14]{Colors.RESET} System Settings
 {Colors.GREEN}[15]{Colors.RESET} Gmail Draft Assistant
 {Colors.BLUE}[16]{Colors.RESET} Gmail Profile Manager
 {Colors.YELLOW}[17]{Colors.RESET} Follow-up Manager
 {Colors.RED}[18]{Colors.RESET} Suppression Manager
 {Colors.GREEN}[19]{Colors.RESET} Reply Manager
 {Colors.BLUE}[20]{Colors.RESET} Gmail Account Manager
 {Colors.GOLD}[21]{Colors.RESET} Draft Queue Manager
 {Colors.CYAN}{Colors.BOLD}[22] Campaign Engine V2{Colors.RESET}
 {Colors.RED}[0] Exit{Colors.RESET}
{Colors.CYAN}========================================================={Colors.RESET}
""")
        choice = input(f"{Colors.YELLOW}Select Option: {Colors.RESET}").strip()

        if choice == "22":
            try:
                campaign_engine_menu()
            except Exception as e:
                print(f"\n{Colors.RED}[Error executing option 22]: {e}{Colors.RESET}\n")
                input("Press Enter to return to main menu...")
        elif choice == "0":
            print(f"\n{Colors.GREEN}Exiting Grace Outreach Assistant. Goodbye!{Colors.RESET}")
            sys.exit(0)
        else:
            print(f"\nFeature [{choice}] selected. Returning to menu...\n")

if __name__ == "__main__":
    main()
