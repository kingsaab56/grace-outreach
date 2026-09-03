import os
import datetime

LOG_FILE = "error_capture_log.txt"

def log_error(error_text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_entry = f"[{timestamp}] ERROR DETECTED:\n{error_text.strip()}\n" + "-"*50 + "\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_entry)
    
    print(f"✔ Error successfully captured and saved to '{LOG_FILE}'!")

if __name__ == "__main__":
    print("=== Grace Outreach Assistant Error Catcher ===")
    print("Paste your error below. Press Enter twice (or type 'SAVE') when done:")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "SAVE":
                break
            lines.append(line)
        except EOFError:
            break
            
    full_error = "\n".join(lines)
    if full_error.strip():
        log_error(full_error)
    else:
        print("⚠ No error text provided.")
