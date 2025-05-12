"""
Persistence Mechanism Simulation - FOR EDUCATIONAL PURPOSES ONLY
This module simulates malware persistence techniques in Windows environments
"""
import os
import sys
import logging
import winreg
import subprocess
import datetime
import time
import ctypes
import json

# Constants 
APP_NAME = "UniProjectDemo"
SAFE_REGISTRY_KEY = f"Software\\{APP_NAME}_Test"
STARTUP_ENTRY_NAME = f"{APP_NAME}_Startup"
TASK_NAME = f"{APP_NAME}_Task"
LOG_DIR = os.path.join(os.environ["TEMP"], f"{APP_NAME}_Logs")

# Ensure log directory exists BEFORE logging is configured
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "persistence_demo.log")),
        logging.StreamHandler()
    ]
)

def is_admin():
    """Check if running as admin (required for some tasks)."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def confirm_action():
    """Ask for user confirmation before making changes."""
    response = input("Continue? (y/n): ").strip().lower()
    return response == "y"

class PersistenceDemo:
    def __init__(self):
        self.script_path = os.path.abspath(sys.argv[0])
        os.makedirs(LOG_DIR, exist_ok=True)

    def log_action(self, action, details):
        """Log actions to a JSON file for later cleanup."""
        log_file = os.path.join(LOG_DIR, "actions.json")
        actions = []
        
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                actions = json.load(f)
        
        actions.append({"action": action, "details": details, "timestamp": str(datetime.datetime.now())})
        
        with open(log_file, "w") as f:
            json.dump(actions, f, indent=4)

    def add_registry_persistence(self):
        """Adds a safe registry entry (HKCU)."""
        try:
            key_path = f"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, STARTUP_ENTRY_NAME, 0, winreg.REG_SZ, self.script_path)
            
            self.log_action("registry", {"key": f"HKCU\\{key_path}", "value": STARTUP_ENTRY_NAME})
            logging.info(f"Added registry entry: HKCU\\{key_path}\\{STARTUP_ENTRY_NAME}")
            return True
        except Exception as e:
            logging.error(f"Registry error: {e}")
            return False

    def add_startup_folder_persistence(self):
        """Adds a harmless .bat file to Startup (asks for confirmation)."""
        try:
            startup_folder = os.path.join(
                os.environ["APPDATA"],
                "Microsoft\\Windows\\Start Menu\\Programs\\Startup"
            )
            bat_path = os.path.join(startup_folder, f"{APP_NAME}.bat")
            
            # Create a harmless script that just logs
            bat_content = f"@echo off\necho {APP_NAME} Demo >> \"{os.path.join(LOG_DIR, 'startup_log.txt')}\""
            
            with open(bat_path, "w") as f:
                f.write(bat_content)
            
            self.log_action("startup", {"path": bat_path})
            logging.info(f"Added to Startup: {bat_path}")
            return True
        except Exception as e:
            logging.error(f"Startup folder error: {e}")
            return False

    def add_scheduled_task(self):
        """Creates a scheduled task that logs timestamps (harmless)."""
        try:
            task_command = (
                f'schtasks /create /tn "{TASK_NAME}" /tr "python \"{self.script_path}\" --log" '
                f'/sc ONLOGON /rl HIGHEST /F'
            )
            subprocess.run(task_command, shell=True, check=True)
            
            self.log_action("scheduled_task", {"task_name": TASK_NAME})
            logging.info(f"Created scheduled task: {TASK_NAME}")
            return True
        except Exception as e:
            logging.error(f"Scheduled task error: {e}")
            return False

    def cleanup(self):
        """Removes all persistence mechanisms."""
        try:
            # Remove registry entry
            try:
                key_path = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.DeleteValue(key, STARTUP_ENTRY_NAME)
                logging.info(f"Removed registry entry: HKCU\\{key_path}\\{STARTUP_ENTRY_NAME}")
            except Exception as e:
                logging.error(f"Registry cleanup failed: {e}")

            # Remove startup file
            try:
                startup_folder = os.path.join(
                    os.environ["APPDATA"],
                    "Microsoft\\Windows\\Start Menu\\Programs\\Startup"
                )
                bat_path = os.path.join(startup_folder, f"{APP_NAME}.bat")
                if os.path.exists(bat_path):
                    os.remove(bat_path)
                    logging.info(f"Removed startup file: {bat_path}")
            except Exception as e:
                logging.error(f"Startup cleanup failed: {e}")

            # Remove scheduled task
            try:
                subprocess.run(f'schtasks /delete /tn "{TASK_NAME}" /F', shell=True, check=True)
                logging.info(f"Removed scheduled task: {TASK_NAME}")
            except Exception as e:
                logging.error(f"Task cleanup failed: {e}")

            logging.info("Cleanup complete!")
            return True
        except Exception as e:
            logging.error(f"Cleanup error: {e}")
            return False

if __name__ == "__main__":
    if not is_admin():
        logging.warning("Some features require Admin (e.g., scheduled tasks). Re-run as Admin if needed.")
    
    demo = PersistenceDemo()
    
    if "--cleanup" in sys.argv:
        demo.cleanup()
    elif "--log" in sys.argv:
        # This is called by the scheduled task (just logs)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(os.path.join(LOG_DIR, "task_log.txt"), "a") as f:
            f.write(f"{timestamp} - Task ran\n")
    else:
        print(f"\n=== {APP_NAME} - Safe Persistence Demo ===")
        print("This will demonstrate real persistence techniques but is SAFE.")
        print("All changes can be undone with: python script.py --cleanup\n")
        
        if confirm_action():
            demo.add_registry_persistence()
            demo.add_startup_folder_persistence()
            demo.add_scheduled_task()
            print("\nDemo complete! Check logs in:", LOG_DIR)
        else:
            print("Cancelled.")