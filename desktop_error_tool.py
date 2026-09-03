import os
import datetime

# Get Desktop path automatically
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
LOG_FILE = os.path.join(desktop_path, "grace_error_logger.txt")

def log_error():
    print("=== Grace Outreach Assistant Error Catcher ===")
    print("Paste your error below. Type 'SAVE' on a new line and press Enter when done:\n")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "SAVE":
                break
            lines.append(line)
        except EOFError:
            break
            
    full_error = "\n".join(lines).strip()
    if full_error:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_entry = f"[{timestamp}] ERROR DETECTED:\n{full_error}\n" + "-"*50 + "\n"
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted_entry)
            
        print(f"\n✔ Error successfully saved to your Desktop file: 'grace_error_logger.txt'!")
    else:
        print("\n⚠ No error text provided.")

if __name__ == "__main__":
    log_error()
