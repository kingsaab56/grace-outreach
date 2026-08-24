import sys
import os

C_TITLE = "\033[38;5;141m"  # Purple
C_INFO  = "\033[38;5;220m"  # Gold
C_PROMPT= "\033[38;5;51m"   # Aqua
C_WARN  = "\033[38;5;208m"  # Orange
C_STAT  = "\033[38;5;46m"   # Neon Green
C_RST   = "\033[0m"
C_BOLD  = "\033[1m"

SPAM_WORDS = [
    "free", "guarantee", "100%", "win", "winner", "cash", "money", 
    "no risk", "act now", "urgent", "credit card", "billion", "prize"
]


def start_spam_checker():
    print(f"\n{C_TITLE}{C_BOLD}========== SPAM TRIGGER KEYWORD CHECKER =========={C_RST}\n")
    text = input(f"{C_PROMPT}Enter Subject or Body to check: {C_RST}").strip().lower()
    
    if not text:
        return

    found = [w for w in SPAM_WORDS if w in text]
    
    if found:
        print(f"\n{C_WARN}{C_BOLD} Spam Triggers Found ({len(found)}):{C_RST} {', '.join(found)}")
    else:
        print(f"\n{C_STAT}{C_BOLD} Clean! No common spam words detected.{C_RST}")
    
    input(f"\n{C_INFO}Press Enter to return...{C_RST}")
