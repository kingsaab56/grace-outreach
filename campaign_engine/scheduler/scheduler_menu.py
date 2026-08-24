"""
Smart Scheduler UI with Auto-Date, Auto-Year, Presets and Quick Custom Inputs
"""

from datetime import datetime, timedelta
from campaign_engine.scheduler.campaign_scheduler import (
    schedule_campaign,
    get_all_schedules,
    cancel_scheduled_campaign,
    run_scheduler_daemon
)
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, error, highlight


def _get_scheduled_target_interactive():
    now = datetime.now()
    cur_date_str = now.strftime("%Y-%m-%d")
    cur_time_str = now.strftime("%H:%M")
    year_str = str(now.year)

    print(f"\n{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    print(f" {Colors.BOLD}Current System Time :{Colors.RESET} {Colors.GREEN}{now.strftime('%Y-%m-%d %I:%M %p')}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    print(f" {Colors.GOLD}[1]{Colors.RESET} Quick Minutes from now   (e.g. Run in 5 or 10 mins)")
    print(f" {Colors.GOLD}[2]{Colors.RESET} Today with Auto-Date      (Default: {cur_date_str}, just enter time)")
    print(f" {Colors.GOLD}[3]{Colors.RESET} Tomorrow with Auto-Date   (Auto calculated next day)")
    print(f" {Colors.GOLD}[4]{Colors.RESET} Custom Date (Auto-Year: {year_str}) (Enter DD-MM HH:MM)")
    print(f" {Colors.GOLD}[5]{Colors.RESET} Direct Short text         (e.g. '5m', '2h', '18:30')")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")

    mode = input(f"{Colors.YELLOW}Select Timing Mode (1-5, Default 1): {Colors.RESET}").strip()
    if not mode:
        mode = "1"

    if mode == "1":
        m_in = input(f"{Colors.CYAN}Enter minutes from now (e.g. 5): {Colors.RESET}").strip()
        try:
            mins = float(m_in) if m_in else 5.0
            target = now + timedelta(minutes=mins)
            return target.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(error("Invalid minutes."))
            return None

    elif mode == "2":
        t_in = input(f"{Colors.CYAN}Enter Time for Today ({cur_date_str}) in HH:MM (e.g. 14:30 or 09:00): {Colors.RESET}").strip()
        if ":" in t_in:
            parts = t_in.split(":")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                target = now.replace(hour=int(parts[0]), minute=int(parts[1]), second=0, microsecond=0)
                return target.strftime("%Y-%m-%d %H:%M:%S")
        print(error("Invalid time format. Use HH:MM"))
        return None

    elif mode == "3":
        tom = now + timedelta(days=1)
        tom_date_str = tom.strftime("%Y-%m-%d")
        t_in = input(f"{Colors.CYAN}Enter Time for Tomorrow ({tom_date_str}) in HH:MM (e.g. 09:00): {Colors.RESET}").strip()
        if ":" in t_in:
            parts = t_in.split(":")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                target = tom.replace(hour=int(parts[0]), minute=int(parts[1]), second=0, microsecond=0)
                return target.strftime("%Y-%m-%d %H:%M:%S")
        print(error("Invalid time format. Use HH:MM"))
        return None

    elif mode == "4":
        print(f"{Colors.DIM}Year {year_str} will be auto-attached.{Colors.RESET}")
        dt_in = input(f"{Colors.CYAN}Enter Day-Month Time (e.g. 22-08 10:30): {Colors.RESET}").strip()
        try:
            full_str = f"{year_str}-{dt_in}"
            target = datetime.strptime(full_str, "%Y-%d-%m %H:%M")
            return target.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            print(error("Invalid date format. Use DD-MM HH:MM (e.g. 25-08 14:00)"))
            return None

    elif mode == "5":
        raw = input(f"{Colors.CYAN}Enter timing (e.g. '15m', '2h', '16:45'): {Colors.RESET}").strip().lower()
        if raw.endswith("m"):
            mins = float(raw[:-1])
            return (now + timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")
        if raw.endswith("h"):
            hrs = float(raw[:-1])
            return (now + timedelta(hours=hrs)).strftime("%Y-%m-%d %H:%M:%S")
        if ":" in raw:
            parts = raw.split(":")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                target = now.replace(hour=int(parts[0]), minute=int(parts[1]), second=0, microsecond=0)
                if target <= now:
                    target += timedelta(days=1)
                return target.strftime("%Y-%m-%d %H:%M:%S")
        try:
            mins = float(raw)
            return (now + timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(error("Could not parse time format."))
            return None

    return None


def scheduler_menu():
    while True:
        print_banner("CAMPAIGN SCHEDULER & AUTOMATION", "⏰")
        print(f" {Colors.GREEN}[1]{Colors.RESET}  Schedule Campaign (Smart Date/Time Presets)")
        print(f" {Colors.CYAN}[2]{Colors.RESET}  View All Scheduled Jobs")
        print(f" {Colors.RED}[3]{Colors.RESET}  Cancel a Scheduled Job")
        print(f" {Colors.GOLD}[4]{Colors.RESET}  Start Background Daemon Listener")
        print(f" {Colors.WHITE}[0]{Colors.RESET}  Back to Engine Menu")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.RESET}")

        choice = input(f"{Colors.YELLOW}Select Option: {Colors.RESET}").strip()

        if choice == "1":
            cid = input(f"{Colors.CYAN}Enter Campaign ID to Schedule: {Colors.RESET}").strip()
            if not cid.isdigit():
                print(error("Invalid Campaign ID."))
                continue

            parsed_time = _get_scheduled_target_interactive()

            if parsed_time:
                if schedule_campaign(int(cid), parsed_time):
                    print(f"\n{success(f'Campaign #{cid} scheduled successfully for:')} {Colors.BOLD}{Colors.GOLD}{parsed_time}{Colors.RESET}\n")

        elif choice == "2":
            jobs = get_all_schedules()
            print_banner("SCHEDULED CAMPAIGNS LIST", "📋")
            if not jobs:
                print(info("No scheduled jobs found."))
                continue

            print(f"{'#':<5} │ {'Camp ID':<8} │ {'Campaign Name':<22} │ {'Scheduled Time':<20} │ {'Status'}")
            print(f"{Colors.CYAN}{'─' * 80}{Colors.RESET}")
            for j in jobs:
                sid, cid, name, stime, stat, cat = j
                status_color = Colors.GREEN if stat == "Executed" else (Colors.YELLOW if stat == "Pending" else Colors.RED)
                print(f"{sid:<5} │ {cid:<8} │ {(name or 'N/A')[:20]:<22} │ {stime:<20} │ {status_color}[{stat}]{Colors.RESET}")
            print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")

        elif choice == "3":
            sid = input(f"{Colors.CYAN}Enter Schedule ID to Cancel: {Colors.RESET}").strip()
            if sid.isdigit():
                if cancel_scheduled_campaign(int(sid)):
                    print(success(f"Schedule #{sid} cancelled."))
                else:
                    print(warning(f"Schedule #{sid} not found."))
            else:
                print(error("Invalid ID."))

        elif choice == "4":
            run_scheduler_daemon()

        elif choice == "0":
            break
