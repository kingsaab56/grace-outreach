from pathlib import Path
from datetime import datetime


LOG_FILE = Path("reports") / "activity.log"



def write_log(module, action):

    LOG_FILE.parent.mkdir(exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as file:

        file.write(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{module} -> {action}\n"
        )



def show_logs():

    if not LOG_FILE.exists():

        print("\nNo activity logs found.")

        input("\nPress Enter...")

        return


    with open(LOG_FILE, "r", encoding="utf-8") as file:

        logs = file.readlines()



    print("\n========== ACTIVITY LOG ==========\n")


    print(f"Total Logs : {len(logs)}\n")


    for log in logs:

        print(log.strip())



    input("\nPress Enter...")